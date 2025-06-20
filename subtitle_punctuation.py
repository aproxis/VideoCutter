import whisperx
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from deepmultilingualpunctuation import PunctuationModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TranscriptionConfig:
    """Configuration class for transcription parameters"""
    source_file: str
    model_size: str = "distil-large-v3"
    device: str = "cuda"
    compute_type: str = "float16"
    batch_size: int = 16
    language: Optional[str] = None  # Auto-detect if None
    max_chars_per_line: int = 42
    max_lines_per_subtitle: int = 2
    min_duration: float = 1.5
    max_duration: float = 7.0
    min_gap: float = 0.3
    output_formats: List[str] = None
    
    # ASS styling options
    ass_style_name: str = "Default"
    ass_font_name: str = "Arial"
    ass_font_size: int = 20
    ass_primary_color: str = "&H00FFFFFF"  # White
    ass_secondary_color: str = "&H000000FF"  # Red
    ass_outline_color: str = "&H00000000"  # Black
    ass_back_color: str = "&H80000000"  # Semi-transparent black
    ass_bold: bool = False
    ass_italic: bool = False
    ass_border_style: int = 1  # 1=Outline+drop shadow, 3=Opaque box
    ass_outline: float = 2.0
    ass_shadow: float = 0.0
    ass_alignment: int = 2  # 2=Bottom center
    ass_margin_l: int = 10
    ass_margin_r: int = 10
    ass_margin_v: int = 30
    
    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ["srt"]

class SubtitleGenerator:
    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.punct_model = None
        self.load_punctuation_model()
    
    def load_punctuation_model(self):
        """Load punctuation model with error handling"""
        try:
            self.punct_model = PunctuationModel()
            logger.info("Punctuation model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load punctuation model: {e}")
            self.punct_model = None
    
    def format_timestamp(self, seconds: Optional[float]) -> str:
        """Format timestamp for SRT format"""
        if seconds is None:
            return "00:00:00,000"
        
        # Ensure non-negative timestamp
        seconds = max(0, seconds)
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')
    
    def format_timestamp_ass(self, seconds: Optional[float]) -> str:
        """Format timestamp for ASS format (centiseconds)"""
        if seconds is None:
            return "0:00:00.00"
        
        seconds = max(0, seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def format_timestamp_vtt(self, seconds: Optional[float]) -> str:
        """Format timestamp for WebVTT format"""
        if seconds is None:
            return "00:00:00.000"
        
        seconds = max(0, seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def split_subtitle_text(self, text: str) -> str:
        """Enhanced text splitting with better line breaking"""
        words = text.split()
        if not words:
            return text
        
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # Check if adding this word would exceed line length
            if (current_length + word_length + len(current_line)) > self.config.max_chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
                
                # Limit number of lines per subtitle
                if len(lines) >= self.config.max_lines_per_subtitle:
                    break
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line and len(lines) < self.config.max_lines_per_subtitle:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def split_subtitle_text_ass(self, text: str) -> str:
        """Split text for ASS format (uses \\N for line breaks)"""
        words = text.split()
        if not words:
            return text
        
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            if (current_length + word_length + len(current_line)) > self.config.max_chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
                
                if len(lines) >= self.config.max_lines_per_subtitle:
                    break
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line and len(lines) < self.config.max_lines_per_subtitle:
            lines.append(' '.join(current_line))
        
        return '\\N'.join(lines)  # ASS uses \N for line breaks
    
    def split_at_sentence_boundaries(self, text: str, word_data: List[Dict]) -> List[Dict]:
        """Split text at sentence boundaries with improved timing"""
        # Enhanced sentence splitting pattern
        sentence_pattern = r'(?<=[.!?])\s+|(?<=[.!?]")[\s]*|(?<=Mr\.|Mrs\.|Dr\.|Prof\.)\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        result = []
        current_word_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_words = sentence.split()
            sentence_word_count = len(sentence_words)
            
            if current_word_index + sentence_word_count <= len(word_data):
                sentence_word_data = word_data[current_word_index:current_word_index + sentence_word_count]
                
                # Find start and end times with better error handling
                start_time = None
                end_time = None
                
                for word in sentence_word_data:
                    if 'start' in word and word['start'] is not None:
                        start_time = word['start']
                        break
                
                for word in reversed(sentence_word_data):
                    if 'end' in word and word['end'] is not None:
                        end_time = word['end']
                        break
                
                # Fallback timing if not available
                if start_time is None or end_time is None:
                    if result:
                        prev_end = result[-1]['end']
                        start_time = prev_end + 0.1
                        end_time = start_time + max(1.0, len(sentence) * 0.05)
                    else:
                        start_time = 0
                        end_time = max(1.0, len(sentence) * 0.05)
                
                result.append({
                    'text': sentence,
                    'start': start_time,
                    'end': end_time
                })
                
                current_word_index += sentence_word_count
            else:
                # Handle edge case where word count doesn't match
                logger.warning(f"Word count mismatch for sentence: {sentence}")
                break
        
        return result
    
    def merge_short_subtitles(self, cues: List[Dict]) -> List[Dict]:
        """Merge short subtitles with improved logic"""
        if not cues:
            return cues
        
        merged_cues = []
        current_cue = None
        
        for cue in cues:
            duration = cue['end'] - cue['start']
            
            if current_cue is None:
                current_cue = cue.copy()
            else:
                # Check if should merge based on duration and gap
                gap = cue['start'] - current_cue['end']
                combined_duration = cue['end'] - current_cue['start']
                
                should_merge = (
                    duration < self.config.min_duration or
                    (gap < self.config.min_gap and combined_duration < self.config.max_duration)
                )
                
                if should_merge:
                    current_cue['text'] += ' ' + cue['text']
                    current_cue['end'] = cue['end']
                else:
                    merged_cues.append(current_cue)
                    current_cue = cue.copy()
        
        if current_cue:
            merged_cues.append(current_cue)
        
        return merged_cues
    
    def generate_srt(self, cues: List[Dict], output_path: str):
        """Generate SRT subtitle file"""
        try:
            with open(output_path, "w", encoding="utf-8") as srt_file:
                for i, cue in enumerate(cues, 1):
                    formatted_text = self.split_subtitle_text(cue['text'])
                    
                    srt_file.write(f"{i}\n")
                    srt_file.write(f"{self.format_timestamp(cue['start'])} --> {self.format_timestamp(cue['end'])}\n")
                    srt_file.write(f"{formatted_text}\n\n")
            
            logger.info(f"SRT file saved: {output_path}")
        except Exception as e:
            logger.error(f"Error generating SRT file: {e}")
            raise
    
    def generate_vtt(self, cues: List[Dict], output_path: str):
        """Generate WebVTT subtitle file"""
        try:
            with open(output_path, "w", encoding="utf-8") as vtt_file:
                vtt_file.write("WEBVTT\n\n")
                
                for cue in cues:
                    formatted_text = self.split_subtitle_text(cue['text'])
                    
                    vtt_file.write(f"{self.format_timestamp_vtt(cue['start'])} --> {self.format_timestamp_vtt(cue['end'])}\n")
                    vtt_file.write(f"{formatted_text}\n\n")
            
            logger.info(f"VTT file saved: {output_path}")
        except Exception as e:
            logger.error(f"Error generating VTT file: {e}")
            raise
    
    def generate_ass(self, cues: List[Dict], output_path: str):
        """Generate ASS (Advanced SubStation Alpha) subtitle file"""
        try:
            with open(output_path, "w", encoding="utf-8") as ass_file:
                # Write ASS header
                ass_file.write("[Script Info]\n")
                ass_file.write("Title: WhisperX Generated Subtitles\n")
                ass_file.write("ScriptType: v4.00+\n")
                ass_file.write("WrapStyle: 0\n")
                ass_file.write("ScaledBorderAndShadow: yes\n")
                ass_file.write("YCbCr Matrix: TV.709\n")
                ass_file.write("PlayResX: 1920\n")
                ass_file.write("PlayResY: 1080\n\n")
                
                # Write styles section
                ass_file.write("[V4+ Styles]\n")
                ass_file.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
                
                style_line = (
                    f"Style: {self.config.ass_style_name},"
                    f"{self.config.ass_font_name},"
                    f"{self.config.ass_font_size},"
                    f"{self.config.ass_primary_color},"
                    f"{self.config.ass_secondary_color},"
                    f"{self.config.ass_outline_color},"
                    f"{self.config.ass_back_color},"
                    f"{-1 if self.config.ass_bold else 0},"
                    f"{-1 if self.config.ass_italic else 0},"
                    f"0,0,100,100,0,0,"
                    f"{self.config.ass_border_style},"
                    f"{self.config.ass_outline},"
                    f"{self.config.ass_shadow},"
                    f"{self.config.ass_alignment},"
                    f"{self.config.ass_margin_l},"
                    f"{self.config.ass_margin_r},"
                    f"{self.config.ass_margin_v},"
                    f"1\n"
                )
                ass_file.write(style_line)
                ass_file.write("\n")
                
                # Write events section
                ass_file.write("[Events]\n")
                ass_file.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
                
                for cue in cues:
                    formatted_text = self.split_subtitle_text_ass(cue['text'])
                    # Escape special characters for ASS
                    formatted_text = formatted_text.replace("{", "\\{").replace("}", "\\}")
                    
                    event_line = (
                        f"Dialogue: 0,"
                        f"{self.format_timestamp_ass(cue['start'])},"
                        f"{self.format_timestamp_ass(cue['end'])},"
                        f"{self.config.ass_style_name},,0,0,0,,"
                        f"{formatted_text}\n"
                    )
                    ass_file.write(event_line)
            
            logger.info(f"ASS file saved: {output_path}")
        except Exception as e:
            logger.error(f"Error generating ASS file: {e}")
            raise
    
    def generate_json(self, cues: List[Dict], output_path: str):
        """Generate JSON transcript file"""
        try:
            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump(cues, json_file, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON file saved: {output_path}")
        except Exception as e:
            logger.error(f"Error generating JSON file: {e}")
            raise

def validate_config(config: TranscriptionConfig) -> bool:
    """Validate configuration parameters"""
    if not os.path.exists(config.source_file):
        logger.error(f"Source file not found: {config.source_file}")
        return False
    
    if config.device == "cuda":
        try:
            import torch
            if not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                config.device = "cpu"
        except ImportError:
            logger.warning("PyTorch not available, using CPU")
            config.device = "cpu"
    
    return True

def transcribe_audio(config: TranscriptionConfig) -> Dict:
    """Main transcription function with error handling"""
    try:
        logger.info(f"Loading WhisperX model: {config.model_size}")
        model = whisperx.load_model(
            config.model_size, 
            config.device, 
            compute_type=config.compute_type
        )
        
        logger.info(f"Loading audio: {config.source_file}")
        audio = whisperx.load_audio(config.source_file)
        
        logger.info("Starting transcription...")
        result = model.transcribe(
            audio, 
            batch_size=config.batch_size,
            language=config.language,
            print_progress=True
        )
        
        logger.info("Aligning transcription...")
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], 
            device=config.device
        )
        result = whisperx.align(
            result["segments"], 
            model_a, 
            metadata, 
            audio, 
            config.device, 
            return_char_alignments=True
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Enhanced WhisperX Transcription with ASS Support")
    parser.add_argument("source_file", help="Path to audio/video file")
    parser.add_argument("--model", default="distil-large-v3", help="WhisperX model size")
    parser.add_argument("--device", default="cuda", help="Device to use (cuda/cpu)")
    parser.add_argument("--language", help="Language code (auto-detect if not specified)")
    parser.add_argument("--formats", nargs="+", default=["srt"], 
                       choices=["srt", "vtt", "json", "ass"], help="Output formats")
    parser.add_argument("--max-chars", type=int, default=42, help="Max characters per line")
    parser.add_argument("--min-duration", type=float, default=1.5, help="Minimum subtitle duration")
    parser.add_argument("--max-duration", type=float, default=7.0, help="Maximum subtitle duration")
    
    # ASS-specific arguments
    parser.add_argument("--ass-font", default="Arial", help="ASS font name")
    parser.add_argument("--ass-size", type=int, default=20, help="ASS font size")
    parser.add_argument("--ass-color", default="&H00FFFFFF", help="ASS primary color (hex)")
    parser.add_argument("--ass-bold", action="store_true", help="ASS bold text")
    parser.add_argument("--ass-italic", action="store_true", help="ASS italic text")
    
    args = parser.parse_args()
    
    # Create configuration
    config = TranscriptionConfig(
        source_file=args.source_file,
        model_size=args.model,
        device=args.device,
        language=args.language,
        output_formats=args.formats,
        max_chars_per_line=args.max_chars,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        ass_font_name=args.ass_font,
        ass_font_size=args.ass_size,
        ass_primary_color=args.ass_color,
        ass_bold=args.ass_bold,
        ass_italic=args.ass_italic
    )
    
    if not validate_config(config):
        return
    
    try:
        # Transcribe audio
        result = transcribe_audio(config)
        
        # Generate subtitles
        generator = SubtitleGenerator(config)
        
        all_cues = []
        for segment in result["segments"]:
            text = segment['text']
            
            # Apply punctuation restoration if available
            if generator.punct_model:
                try:
                    text = generator.punct_model.restore_punctuation(text)
                except Exception as e:
                    logger.warning(f"Punctuation restoration failed: {e}")
            
            word_data = segment.get('words', [])
            sentences = generator.split_at_sentence_boundaries(text, word_data)
            all_cues.extend(sentences)
        
        # Merge short subtitles
        merged_cues = generator.merge_short_subtitles(all_cues)
        
        # Generate output files
        base_name = os.path.splitext(config.source_file)[0]
        
        for format_type in config.output_formats:
            output_path = f"{base_name}.{format_type}"
            
            if format_type == "srt":
                generator.generate_srt(merged_cues, output_path)
            elif format_type == "vtt":
                generator.generate_vtt(merged_cues, output_path)
            elif format_type == "json":
                generator.generate_json(merged_cues, output_path)
            elif format_type == "ass":
                generator.generate_ass(merged_cues, output_path)
        
        logger.info(f"Transcription completed successfully. Generated {len(merged_cues)} subtitles.")
        
        # Validation check
        original_text = " ".join([segment["text"] for segment in result["segments"]])
        final_text = " ".join([cue["text"] for cue in merged_cues])
        
        original_words = set(re.findall(r'\b[\w\']+\b', original_text.lower()))
        final_words = set(re.findall(r'\b[\w\']+\b', final_text.lower()))
        
        missing_words = original_words - final_words
        if missing_words:
            logger.warning(f"Missing words detected: {', '.join(list(missing_words)[:10])}")
        else:
            logger.info("No words lost during processing")
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    # For direct execution without command line args, modify this section:
    USE_COMMAND_LINE = True
    
    if USE_COMMAND_LINE:
        main()
    else:
        # Example configuration for direct execution
        config = TranscriptionConfig(
            source_file=r"PATH_TO_YOUR_FILE",  # Update this path
            model_size="distil-large-v3",
            device="cuda",
            language="en",
            output_formats=["srt", "vtt", "json", "ass"],
            max_chars_per_line=42,
            min_duration=1.5,
            max_duration=7.0,
            # ASS styling
            ass_font_name="Arial",
            ass_font_size=20,
            ass_primary_color="&H00FFFFFF",
            ass_bold=False,
            ass_italic=False
        )
        
        if validate_config(config):
            try:
                result = transcribe_audio(config)
                generator = SubtitleGenerator(config)
                
                all_cues = []
                for segment in result["segments"]:
                    text = segment['text']
                    if generator.punct_model:
                        try:
                            text = generator.punct_model.restore_punctuation(text)
                        except Exception as e:
                            logger.warning(f"Punctuation restoration failed: {e}")
                    
                    word_data = segment.get('words', [])
                    sentences = generator.split_at_sentence_boundaries(text, word_data)
                    all_cues.extend(sentences)
                
                merged_cues = generator.merge_short_subtitles(all_cues)
                
                base_name = os.path.splitext(config.source_file)[0]
                for format_type in config.output_formats:
                    output_path = f"{base_name}.{format_type}"
                    
                    if format_type == "srt":
                        generator.generate_srt(merged_cues, output_path)
                    elif format_type == "vtt":
                        generator.generate_vtt(merged_cues, output_path)
                    elif format_type == "json":
                        generator.generate_json(merged_cues, output_path)
                    elif format_type == "ass":
                        generator.generate_ass(merged_cues, output_path)
                
                print(f"Transcription completed. Generated {len(merged_cues)} subtitles.")
                
            except Exception as e:
                print(f"Error: {e}")