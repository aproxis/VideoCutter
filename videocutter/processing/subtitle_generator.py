# videocutter/processing/subtitle_generator.py
# Enhanced version with line length control for ASS and text correction functionality

import os
import re
import whisperx
import certifi
from mutagen.mp3 import MP3
from dotmap import DotMap
from videocutter.utils.font_utils import get_font_name
from difflib import SequenceMatcher

# Set up SSL for HTTPS requests
if "SSL_CERT_FILE" not in os.environ:
    os.environ["SSL_CERT_FILE"] = certifi.where()

# Set number of threads for math libraries
if "OMP_NUM_THREADS" not in os.environ:
    os.environ["OMP_NUM_THREADS"] = "6"
if "MKL_NUM_THREADS" not in os.environ:
    os.environ["MKL_NUM_THREADS"] = "6"

def _get_audio_duration(file_path: str) -> float:
    """Determine the duration of an MP3 file using mutagen."""
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        print(f"Could not determine audio duration for {file_path}: {e}")
        return 0.0

def _format_time(seconds: float) -> str:
    """Convert time in seconds to SRT format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs_val = seconds % 60
    millis = int((secs_val - int(secs_val)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(secs_val):02},{millis:03}"

def _format_ass_time(seconds: float) -> str:
    """Format seconds to ASS time format: H:MM:SS.cs"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"

def _transcribe_with_whisperx(audio_path: str, language: str, model_name: str, device: str, compute_type: str, initial_prompt: str = None) -> dict:
    """Transcribe and perform forced alignment with WhisperX."""
    print(f"Running WhisperX (model: {model_name}, device: {device}, lang: {language}) for file: {audio_path}")
    
    asr_options = {}
    if initial_prompt:
        asr_options["initial_prompt"] = initial_prompt

    model = whisperx.load_model(model_name, device=device, language=language, compute_type=compute_type, asr_options=asr_options)
    result = model.transcribe(audio_path)
    
    print("Loading alignment model...")
    alignment_model, metadata = whisperx.load_align_model(language_code=language, device=device)
    print("Performing alignment...")
    aligned_result = whisperx.align(result["segments"], alignment_model, metadata, audio_path, device)
    return aligned_result

def _similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings, ignoring punctuation."""
    # Remove punctuation and convert to lowercase for comparison
    a_cleaned = re.sub(r'[^\w\s]', '', a).lower()
    b_cleaned = re.sub(r'[^\w\s]', '', b).lower()
    if not a_cleaned and not b_cleaned: # Handle cases where both are empty after cleaning
        return 1.0
    return SequenceMatcher(None, a_cleaned, b_cleaned).ratio()

def _find_best_match_segment(word: str, original_words: list, start_idx: int = 0) -> tuple:
    """Find the best matching word in the original text starting from start_idx."""
    # Prioritize sequential matching within a small look-ahead window
    # This prevents large, incorrect jumps in the original text
    look_ahead_window = 20 # Search up to 5 words ahead
    
    best_match_idx_in_window = start_idx
    best_similarity_in_window = 0.0
    
    # Iterate through a small window starting from start_idx
    for i in range(start_idx, min(len(original_words), start_idx + look_ahead_window)):
        current_original_word = original_words[i]
        similarity = _similarity(word, current_original_word)
        # print(f"DEBUG_FBM: word='{word}', original_words[{i}]='{current_original_word}', sim={similarity:.2f}, best_sim_win={best_similarity_in_window:.2f}, best_idx_win={best_match_idx_in_window}")
        
        if similarity > best_similarity_in_window:
            best_similarity_in_window = similarity
            best_match_idx_in_window = i
            # print(f"DEBUG_FBM:   -> NEW BEST IN WINDOW: best_sim_win={best_similarity_in_window:.2f}, best_idx_win={best_match_idx_in_window}")
    
    # print(f"DEBUG_FBM: Final for word='{word}' (start_idx={start_idx}): returning best_idx={best_match_idx_in_window}, best_sim={best_similarity_in_window:.2f}")
    return best_match_idx_in_window, best_similarity_in_window

def _correct_transcription_with_original_text(aligned_result: dict, original_text: str, audio_duration: float = None) -> dict:
    """
    Correct the transcribed text using the original text with proper punctuation.
    
    Args:
        aligned_result: WhisperX result with word-level timing
        original_text: Original text with proper punctuation
        
    Returns:
        Corrected aligned_result with original text and preserved timing
    """
    print("Correcting transcription with original text...")
    
    # Split original text into words, preserving punctuation context for final output
    original_words_with_punctuation = re.findall(r'\S+', original_text)
    
    # Create a cleaned version of original words for comparison purposes
    cleaned_original_words = [re.sub(r'[^\w\s]', '', word).lower() for word in original_words_with_punctuation]

    transcribed_segments = aligned_result.get("segments", [])
    
    corrected_segments = []
    original_idx = 0 # Pointer for original_words_with_punctuation
    audio_has_ended = False
    audio_end_threshold_seconds = 1.0 # If transcribed word starts this much after audio_duration, assume end

    for segment in transcribed_segments:
        words_in_segment = segment.get("words", [])
        if not words_in_segment:
            continue
            
        corrected_words = []
        
        for word_info in words_in_segment:
            transcribed_word = word_info.get("word", "").strip()
            transcribed_word_start_time = word_info.get("start", 0.0)

            # Check if audio has ended based on transcribed word's start time
            if audio_duration is not None and transcribed_word_start_time > (audio_duration + audio_end_threshold_seconds):
                audio_has_ended = True
                print(f"DEBUG: Audio end detected. Transcribed word start time ({transcribed_word_start_time:.2f}s) exceeds audio duration ({audio_duration:.2f}s) + threshold.")
            
            if audio_has_ended:
                # If audio has ended, just use the transcribed word (which will likely be empty/short)
                # and do not attempt to match against original_text.
                corrected_word = transcribed_word
                print(f"DEBUG: Audio ended. Keeping transcribed word: '{transcribed_word}'")
            else:
                # Normal correction logic if audio has not ended
                cleaned_transcribed_word = re.sub(r'[^\w\s]', '', transcribed_word).lower()

                if not cleaned_transcribed_word or original_idx >= len(cleaned_original_words):
                    print(f"DEBUG: Skipping word '{transcribed_word}' (original_idx: {original_idx}, len(original_words): {len(cleaned_original_words)})")
                    corrected_word = transcribed_word # Keep transcribed if no original words left or empty
                    original_idx += 1 # Still advance to avoid getting stuck
                else:
                    # Find best match in cleaned original text
                    match_idx, similarity = _find_best_match_segment(cleaned_transcribed_word, cleaned_original_words, original_idx)
                    
                    # Use original word (with punctuation) if similarity is reasonable, otherwise keep transcribed
                    if similarity > 0.6:  # Threshold for accepting match
                        corrected_word = original_words_with_punctuation[match_idx]
                        print(f"DEBUG: Matched '{transcribed_word}' to '{corrected_word}' (sim: {similarity:.2f}). original_idx: {original_idx} -> {match_idx + 1}")
                        original_idx = match_idx + 1
                    else:
                        corrected_word = transcribed_word
                        print(f"DEBUG: No good match for '{transcribed_word}' (sim: {similarity:.2f}). Keeping transcribed. original_idx: {original_idx} -> {original_idx + 1}")
                        original_idx += 1
            
            # Preserve timing information
            corrected_word_info = word_info.copy()
            corrected_word_info["word"] = corrected_word
            corrected_words.append(corrected_word_info)
        
        if corrected_words:
            corrected_segment = segment.copy()
            corrected_segment["words"] = corrected_words
            corrected_segments.append(corrected_segment)
    
    corrected_result = aligned_result.copy()
    corrected_result["segments"] = corrected_segments
    
    print(f"Corrected transcription: matched {len(corrected_segments)} segments")
    return corrected_result

def _whisperx_result_to_srt(aligned_result: dict, max_width: int, time_offset: float = 0.0) -> str:
    """Convert WhisperX aligned result to SRT format."""
    srt_lines = []
    segments = aligned_result.get("segments", [])
    subtitle_index = 0
    
    current_line_text = ""
    current_line_start_time = 0.0
    current_line_end_time = 0.0
    
    for segment in segments:
        words_in_segment = segment.get("words", [])
        if not words_in_segment:
            continue

        for word_info in words_in_segment:
            word = word_info.get("word", "").strip()
            if not word:
                continue

            word_start = word_info.get("start", current_line_end_time)
            word_end = word_info.get("end", word_start)

            if not current_line_text:
                current_line_text = word
                current_line_start_time = word_start
                current_line_end_time = word_end
            else:
                if len(current_line_text) + 1 + len(word) <= max_width:
                    current_line_text += " " + word
                    current_line_end_time = word_end
                else:
                    subtitle_index += 1
                    srt_lines.append(str(subtitle_index))
                    srt_lines.append(f"{_format_time(current_line_start_time + time_offset)} --> {_format_time(current_line_end_time + time_offset)}")
                    srt_lines.append(current_line_text)
                    srt_lines.append("")
                    
                    current_line_text = word
                    current_line_start_time = word_start
                    current_line_end_time = word_end
    
    if current_line_text:
        subtitle_index += 1
        srt_lines.append(str(subtitle_index))
        srt_lines.append(f"{_format_time(current_line_start_time + time_offset)} --> {_format_time(current_line_end_time + time_offset)}")
        srt_lines.append(current_line_text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)

def _whisperx_result_to_ass(aligned_result: dict, max_width: int, time_offset: float = 0.0, config: DotMap = None) -> str:
    """
    Convert WhisperX aligned result to ASS subtitle format with line length control.
    
    Args:
        aligned_result: WhisperX result with word-level timing
        max_width: Maximum characters per line
        time_offset: Time offset in seconds
        config: Configuration object
        
    Returns:
        ASS formatted subtitle string
    """
    segments = aligned_result.get("segments", [])
    
    # Determine PlayResX and PlayResY based on video orientation from config
    play_res_x = 1920
    play_res_y = 1080
    if config:
        video_orientation = config.get('video_orientation', 'vertical')
        target_resolution = config.get('target_resolution', {})
        if video_orientation == 'vertical':
            play_res_x = target_resolution.get('vertical_width', 1080)
            play_res_y = target_resolution.get('vertical_height', 1920)
        else:
            play_res_x = target_resolution.get('horizontal_width', 1920)
            play_res_y = target_resolution.get('horizontal_height', 1080)

    # Basic header
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
    
    # Generate style string (same as original)
    sub_cfg = config.get('subtitles', {}) if config else {}
    
    sub_font_name_arg = sub_cfg.get('font_name', 'Arial')
    fonts_folder = config.get('fonts_folder', 'fonts') if config else 'fonts'
    sub_font_path_local = os.path.join(fonts_folder, sub_font_name_arg)
    
    actual_sub_font_name = sub_font_name_arg
    if os.path.exists(sub_font_path_local):
        actual_sub_font_name = get_font_name(sub_font_path_local)
    else:
        print(f"Warning: Subtitle font {sub_font_name_arg} not found at {sub_font_path_local}. Using raw font name.")

    # Color conversions (RRGGBB to BBGGRR)
    fc_bgr = sub_cfg.get('font_color_hex', 'FFFFFF')[4:6] + sub_cfg.get('font_color_hex', 'FFFFFF')[2:4] + sub_cfg.get('font_color_hex', 'FFFFFF')[0:2]
    secondary_color_bgr = sub_cfg.get('secondary_color_hex', '00FFFFFF')[4:6] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[2:4] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[0:2]
    oc_bgr = sub_cfg.get('outline_color_hex', '000000')[4:6] + sub_cfg.get('outline_color_hex', '000000')[2:4] + sub_cfg.get('outline_color_hex', '000000')[0:2]
    sc_bgr = sub_cfg.get('shadow_color_hex', '000000')[4:6] + sub_cfg.get('shadow_color_hex', '000000')[2:4] + sub_cfg.get('shadow_color_hex', '000000')[0:2]

    # Style definition
    ass_style_definition = (
        f"Style: Default,{actual_sub_font_name},"
        f"{sub_cfg.get('font_size', 24)},"
        f"&H00{fc_bgr},"
        f"&H00{secondary_color_bgr},"
        f"&H00{oc_bgr},"
        f"&H00{sc_bgr},"
        f"{sub_cfg.get('bold', -1)},"
        f"{sub_cfg.get('italic', 0)},"
        f"{sub_cfg.get('underline', 0)},"
        f"{sub_cfg.get('strikeout', 0)},"
        f"{sub_cfg.get('scale_x', 100)},"
        f"{sub_cfg.get('scale_y', 100)},"
        f"{sub_cfg.get('spacing', 0.0)},"
        f"{sub_cfg.get('angle', 0)},"
        f"{sub_cfg.get('border_style', 1)},"
        f"{sub_cfg.get('outline_thickness', 1.0)},"
        f"{sub_cfg.get('shadow_distance', 1.0)},"
        f"{sub_cfg.get('position_ass', 2)},"
        f"{sub_cfg.get('margin_l', 10)},"
        f"{sub_cfg.get('margin_r', 10)},"
        f"{sub_cfg.get('margin_v', 10)},"
        f"{sub_cfg.get('encoding', 1)}"
    )
    
    ass_header += ass_style_definition + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    
    ass_events = []
    
    # Group words into lines based on max_width
    current_line_text = ""
    current_line_start_time = 0.0
    current_line_end_time = 0.0
    
    for segment in segments:
        words_in_segment = segment.get("words", [])
        if not words_in_segment:
            continue

        for word_info in words_in_segment:
            word = word_info.get("word", "").strip()
            if not word:
                continue

            word_start = word_info.get("start", current_line_end_time) + time_offset
            word_end = word_info.get("end", word_start) + time_offset

            if not current_line_text:  # Starting a new line
                current_line_text = word
                current_line_start_time = word_start
                current_line_end_time = word_end
            else:
                # Check if adding the new word exceeds max_width
                if len(current_line_text) + 1 + len(word) <= max_width:
                    current_line_text += " " + word
                    current_line_end_time = word_end
                else:
                    # Finalize current line
                    start_ass = _format_ass_time(current_line_start_time)
                    end_ass = _format_ass_time(current_line_end_time)
                    ass_line = f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{current_line_text}"
                    ass_events.append(ass_line)
                    
                    # Start new line with current word
                    current_line_text = word
                    current_line_start_time = word_start
                    current_line_end_time = word_end
    
    # Add the last accumulated line if any
    if current_line_text:
        start_ass = _format_ass_time(current_line_start_time)
        end_ass = _format_ass_time(current_line_end_time)
        ass_line = f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{current_line_text}"
        ass_events.append(ass_line)

    return ass_header + "\n".join(ass_events)

def generate_subtitles_from_audio_file(
    audio_file_path: str, 
    output_path: str,
    config: DotMap,
    subtitle_format: str = 'srt',
    time_offset_seconds: float = 0.0,
    original_text: str = None,
    audio_duration: float = None
    ) -> str | None:
    """
    Generates a subtitle file (SRT or ASS) from an audio file using WhisperX.

    Args:
        audio_file_path (str): Path to the input audio file
        output_path (str): Path where the generated subtitle file should be saved
        config (DotMap): Configuration dictionary
        subtitle_format (str): Desired subtitle format ('srt' or 'ass')
        time_offset_seconds (float): Time offset in seconds
        original_text (str): Original text with punctuation for correction (optional)
        
    Returns:
        str | None: Path to the generated subtitle file, or None on failure
    """
    print("###### GENERATING SUBTITLES ######")
    print(f"DEBUG: subtitle_generator.py received original_text: '{original_text[:100] if original_text else 'None'}...' (length: {len(original_text) if original_text else 0})")
    
    sub_cfg = config.get('subtitles', {})
    language = sub_cfg.get('language', 'en')
    model_name = sub_cfg.get('whisper_model', 'base')
    device = sub_cfg.get('device', 'cpu') 
    compute_type = sub_cfg.get('compute_type', 'int8')
    max_width = sub_cfg.get('max_line_width', 42)

    if not os.path.exists(audio_file_path):
        print(f"Audio file not found at {audio_file_path}. Cannot generate subtitles.")
        return None
            
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created subtitle output directory: {output_dir}")

    try:
        # Get actual audio duration
        actual_audio_duration = _get_audio_duration(audio_file_path)
        print(f"DEBUG: Actual audio duration: {actual_audio_duration:.2f} seconds")

        print(f"Transcribing audio file: {audio_file_path}")
        # As per user request, testing without initial_prompt to see if it's causing issues.
        # The original_text will still be used for post-transcription correction.
        aligned_result = _transcribe_with_whisperx(audio_file_path, language, model_name, device, compute_type, initial_prompt=None)
        
        # Save uncorrected ASS as debug backup if original_text is provided and format is ASS
        if original_text and subtitle_format == 'ass':
            uncorrected_ass_text = _whisperx_result_to_ass(aligned_result, max_width, time_offset=time_offset_seconds, config=config)
            uncorrected_output_path = os.path.join(output_dir, "voiceover_uncorrected.ass")
            try:
                with open(uncorrected_output_path, "w", encoding="utf-8") as f_uncorrected:
                    f_uncorrected.write(uncorrected_ass_text)
                print(f"Uncorrected ASS subtitles saved to: {uncorrected_output_path}")
            except Exception as e:
                print(f"Error saving uncorrected ASS subtitles: {e}")

        # Apply text correction if original text is provided
        if original_text:
            aligned_result = _correct_transcription_with_original_text(aligned_result, original_text, actual_audio_duration)
        
        subtitle_text = ""
        if subtitle_format == 'srt':
            print(f"Converting transcription to SRT format with time offset: {time_offset_seconds}s...")
            subtitle_text = _whisperx_result_to_srt(aligned_result, max_width, time_offset=time_offset_seconds)
        elif subtitle_format == 'ass':
            print(f"Converting transcription to ASS format with time offset: {time_offset_seconds}s...")
            subtitle_text = _whisperx_result_to_ass(aligned_result, max_width, time_offset=time_offset_seconds, config=config)
        else:
            print(f"Unsupported subtitle format: {subtitle_format}. Only 'srt' and 'ass' are supported.")
            return None
        
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(subtitle_text)
        
        print(f"Subtitles saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating subtitles for {audio_file_path}: {e}")
        return None

if __name__ == "__main__":
    print("Enhanced subtitle generator ready for testing.")
