# videocutter/processing/subtitle_generator.py
# Enhanced version with line length control for ASS and text correction functionality

import os
import re
import whisperx
import certifi
from mutagen.mp3 import MP3
from dotmap import DotMap
from videocutter.utils.font_utils import get_font_name
from videocutter.utils.punctuation_utils import apply_punctuation_fix
from videocutter.utils.subtitle_processing_utils import (
    format_timestamp_ass, split_at_sentence_boundaries,
    merge_short_subtitles, split_subtitle_text_ass
)
import difflib

# Set up SSL for HTTPS requests
if "SSL_CERT_FILE" not in os.environ:
    os.environ["SSL_CERT_FILE"] = certifi.where()

# Set number of threads for math libraries
if "OMP_NUM_THREADS" not in os.environ:
    os.environ["OMP_NUM_THREADS"] = "6"
if "MKL_NUM_THREADS" not in os.environ:
    os.environ["MKL_NUM_THREADS"] = "6"

import logging
logger = logging.getLogger(__name__)

def _get_audio_duration(file_path: str) -> float:
    """Determine the duration of an MP3 file using mutagen."""
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        logger.error(f"Could not determine audio duration for {file_path}: {e}")
        return 0.0

def _transcribe_with_whisperx(audio_path: str, language: str, model_name: str, device: str, compute_type: str, initial_prompt: str = None) -> dict:
    """Transcribe and perform forced alignment with WhisperX."""
    logger.debug(f"Entering _transcribe_with_whisperx with: audio_path='{audio_path}', language='{language}', model_name='{model_name}', device='{device}', compute_type='{compute_type}'")
    logger.info(f"Running WhisperX (model: {model_name}, device: {device}, lang: {language}) for file: {audio_path}")
    
    asr_options = {}
    if initial_prompt:
        asr_options["initial_prompt"] = initial_prompt

    model = whisperx.load_model(model_name, device=device, language=language, compute_type=compute_type, asr_options=asr_options)
    result = model.transcribe(audio_path)
    
    logger.info("Loading alignment model...")
    alignment_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    logger.info("Performing alignment...")
    aligned_result = whisperx.align(result["segments"], alignment_model, metadata, audio_path, device)
    num_segments = len(aligned_result.get('segments', []))
    logger.debug(f"Exiting _transcribe_with_whisperx. Aligned result has {num_segments} segments.")
    return aligned_result

def _find_best_match_segment(transcribed_word: str, original_words_list: list, start_idx: int) -> tuple:
    """
    Finds the best matching word in the original_words_list starting from start_idx.
    Returns the index of the best match and its similarity score.
    """
    best_match_idx = start_idx
    max_similarity = 0.0

    # Search a small window around the current original_idx
    search_window = 5 # Look 5 words ahead
    end_idx = min(start_idx + search_window, len(original_words_list))

    for i in range(start_idx, end_idx):
        original_word = original_words_list[i]
        similarity = difflib.SequenceMatcher(None, transcribed_word, original_word).ratio()
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_idx = i
    return best_match_idx, max_similarity

def _correct_transcription_with_original_text(aligned_result: dict, original_text: str, audio_duration: float = None) -> dict:
    """
    Correct the transcribed text using the original text with proper punctuation.
    
    Args:
        aligned_result: WhisperX result with word-level timing
        original_text: Original text with proper punctuation
        
    Returns:
        Corrected aligned_result with original text and preserved timing
    """
    num_segments = len(aligned_result['segments']) if aligned_result and 'segments' in aligned_result else 0
    logger.debug(f"Entering _correct_transcription_with_original_text. Original text (first 100 chars): '{original_text[:100]}', Aligned result segments: {num_segments}")
    logger.info("Correcting transcription with original text...")
    
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
                logger.debug(f"Audio end detected. Transcribed word start time ({transcribed_word_start_time:.2f}s) exceeds audio duration ({audio_duration:.2f}s) + threshold.")
            
            if audio_has_ended:
                # If audio has ended, just use the transcribed word (which will likely be empty/short)
                # and do not attempt to match against original_text.
                corrected_word = transcribed_word
                logger.debug(f"Audio ended. Keeping transcribed word: '{transcribed_word}'")
            else:
                # Normal correction logic if audio has not ended
                cleaned_transcribed_word = re.sub(r'[^\w\s]', '', transcribed_word).lower()

                if not cleaned_transcribed_word or original_idx >= len(cleaned_original_words):
                    logger.debug(f"Skipping word '{transcribed_word}' (original_idx: {original_idx}, len(original_words): {len(cleaned_original_words)})")
                    corrected_word = transcribed_word # Keep transcribed if no original words left or empty
                    original_idx += 1 # Still advance to avoid getting stuck
                else:
                    # Find best match in cleaned original text
                    match_idx, similarity = _find_best_match_segment(cleaned_transcribed_word, cleaned_original_words, original_idx)
                    
                    # Use original word (with punctuation) if similarity is reasonable, otherwise keep transcribed
                    if similarity > 0.6:  # Threshold for accepting match
                        corrected_word = original_words_with_punctuation[match_idx]
                        logger.debug(f"Matched '{transcribed_word}' to '{corrected_word}' (sim: {similarity:.2f}). original_idx: {original_idx} -> {match_idx + 1}")
                    else:
                        corrected_word = transcribed_word
                        logger.debug(f"No good match for '{transcribed_word}' (sim: {similarity:.2f}). Keeping transcribed. original_idx: {original_idx} -> {original_idx + 1}")
                    logger.debug(f"Comparing: transcribed_word='{transcribed_word}', cleaned_transcribed_word='{cleaned_transcribed_word}', original_word='{original_words_with_punctuation[match_idx] if match_idx < len(original_words_with_punctuation) else 'N/A'}', similarity={similarity:.2f}. Decision: {'Matched' if similarity > 0.6 else 'Kept transcribed'}")
                    original_idx = match_idx + 1 if similarity > 0.6 else original_idx + 1
            
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
    
    num_segments_corrected = len(corrected_result['segments']) if corrected_result and 'segments' in corrected_result else 0
    logger.debug(f"Exiting _correct_transcription_with_original_text. Corrected result has {num_segments_corrected} segments.")
    logger.info(f"Corrected transcription: matched {len(corrected_segments)} segments")
    return corrected_result


def generate_subtitles_from_audio_file(
    audio_file_path: str, 
    output_path: str,
    config: DotMap,
    subtitle_format: str = 'srt',
    time_offset_seconds: float = 0.0,
    original_text: str = None,
    audio_duration: float = None,
    apply_punctuation_fix_enabled: bool = False
    ) -> str | None:
    logger.debug(f"DEBUG: generate_subtitles_from_audio_file called with apply_punctuation_fix_enabled={apply_punctuation_fix_enabled}")
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
    logger.info("###### GENERATING SUBTITLES ######")
    logger.debug(f"Starting transcription for audio: {audio_file_path}")
    logger.debug(f"Transcription parameters: language='{config.subtitles.language}', model='{config.subtitles.whisper_model}', device='{config.subtitles.device}', compute_type='{config.subtitles.compute_type}'")
    
    sub_cfg = config.get('subtitles', {})

    logger.debug(f"DEBUG: Before punctuation fix block: apply_punctuation_fix_enabled={apply_punctuation_fix_enabled}, original_text_length={len(original_text) if original_text else 0}")
    # Apply punctuation fix to original_text if enabled
    if apply_punctuation_fix_enabled and original_text:
        logger.info("Applying punctuation fix to original text...")
        logger.debug(f"DEBUG: Entering punctuation fix block. Original text (first 50 chars): '{original_text[:50]}'")
        original_text = apply_punctuation_fix(original_text)
        logger.debug(f"DEBUG: After punctuation fix. Original text (first 50 chars): '{original_text[:50]}'")
        logger.debug(f"Original text after punctuation fix: '{original_text[:100]}...'")

    language = sub_cfg.get('language', 'en')
    model_name = sub_cfg.get('whisper_model', 'base')
    device = sub_cfg.get('device', 'cpu') 
    compute_type = sub_cfg.get('compute_type', 'int8')
    max_width = sub_cfg.get('max_line_width', 42)
    max_lines = sub_cfg.get('max_lines_per_subtitle', 2) # Assuming this config exists or will be added

    if not os.path.exists(audio_file_path):
        logger.error(f"Audio file not found at {audio_file_path}. Cannot generate subtitles.")
        return None
            
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created subtitle output directory: {output_dir}")

    try:
        # Get actual audio duration
        actual_audio_duration = _get_audio_duration(audio_file_path)
        logger.debug(f"Actual audio duration: {actual_audio_duration:.2f} seconds")

        logger.info(f"Transcribing audio file: {audio_file_path}")
        # As per user request, testing without initial_prompt to see if it's causing issues.
        # The original_text will still be used for post-transcription correction.
        aligned_result = _transcribe_with_whisperx(audio_file_path, language, model_name, device, compute_type, initial_prompt=None)
        
        num_segments = len(aligned_result['segments']) if aligned_result and 'segments' in aligned_result else 0
        first_segment_text = aligned_result['segments'][0]['text'][:50] + '...' if num_segments > 0 else 'N/A'
        logger.debug(f"Raw transcription complete. Segments: {num_segments}, First segment: '{first_segment_text}'")

        # Save uncorrected ASS as debug backup if original_text is provided and format is ASS
        if original_text and subtitle_format == 'ass':
            uncorrected_output_path = os.path.join(os.path.dirname(output_path), "_uncorrected_voiceover.ass")
            # Reconstructing _whisperx_result_to_ass logic here for the uncorrected backup
            segments = aligned_result.get("segments", [])
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

            ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
            sub_cfg = config.get('subtitles', {})
            sub_font_name_arg = sub_cfg.get('font_name', 'Arial')
            fonts_folder = config.get('fonts_folder', 'fonts')
            sub_font_path_local = os.path.join(fonts_folder, sub_font_name_arg)
            actual_sub_font_name = sub_font_name_arg
            if os.path.exists(sub_font_path_local):
                actual_sub_font_name = get_font_name(sub_font_path_local)
            
            fc_bgr = sub_cfg.get('font_color_hex', 'FFFFFF')[4:6] + sub_cfg.get('font_color_hex', 'FFFFFF')[2:4] + sub_cfg.get('font_color_hex', 'FFFFFF')[0:2]
            secondary_color_bgr = sub_cfg.get('secondary_color_hex', '00FFFFFF')[4:6] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[2:4] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[0:2]
            oc_bgr = sub_cfg.get('outline_color_hex', '000000')[4:6] + sub_cfg.get('outline_color_hex', '000000')[2:4] + sub_cfg.get('outline_color_hex', '000000')[0:2]
            sc_bgr = sub_cfg.get('shadow_color_hex', '000000')[4:6] + sub_cfg.get('shadow_color_hex', '000000')[2:4] + sub_cfg.get('shadow_color_hex', '000000')[0:2]

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
            for segment in segments:
                words_in_segment = segment.get("words", [])
                if not words_in_segment:
                    continue
                
                current_line_text = ""
                current_line_start_time = 0.0
                current_line_end_time = 0.0

                for word_info in words_in_segment:
                    word = word_info.get("word", "").strip()
                    if not word:
                        continue
                    word_start = word_info.get("start", current_line_end_time) + time_offset_seconds
                    word_end = word_info.get("end", word_start) + time_offset_seconds

                    if not current_line_text:
                        current_line_text = word
                        current_line_start_time = word_start
                        current_line_end_time = word_end
                    else:
                        if len(current_line_text) + 1 + len(word) <= max_width:
                            current_line_text += " " + word
                            current_line_end_time = word_end
                        else:
                            start_ass = format_timestamp_ass(current_line_start_time)
                            end_ass = format_timestamp_ass(current_line_end_time)
                            ass_line = f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{split_subtitle_text_ass(current_line_text, max_width, max_lines)}" # Use split_subtitle_text_ass
                            ass_events.append(ass_line)
                            current_line_text = word
                            current_line_start_time = word_start
                            current_line_end_time = word_end
                if current_line_text:
                    start_ass = format_timestamp_ass(current_line_start_time)
                    end_ass = format_timestamp_ass(current_line_end_time)
                    ass_line = f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{split_subtitle_text_ass(current_line_text, max_width, max_lines)}" # Use split_subtitle_text_ass
                    ass_events.append(ass_line)
                
                current_line_text = "" # Reset for next segment
            uncorrected_ass_text = ass_header + "\n".join(ass_events)

            try:
                with open(uncorrected_output_path, "w", encoding="utf-8") as f_uncorrected:
                    f_uncorrected.write(uncorrected_ass_text)
                logger.info(f"Uncorrected ASS subtitles saved to: {uncorrected_output_path}")
            except Exception as e:
                logger.error(f"Error saving uncorrected ASS subtitles: {e}")

        # Apply text correction if original text is provided (ALWAYS if original_text exists)
        if original_text:
            logger.debug(f"Original text for correction (first 100 chars): '{original_text[:100]}'")
            aligned_result = _correct_transcription_with_original_text(aligned_result, original_text, actual_audio_duration)
            num_segments_corrected = len(aligned_result['segments']) if aligned_result and 'segments' in aligned_result else 0
            first_segment_text_corrected = aligned_result['segments'][0]['text'][:50] + '...' if num_segments_corrected > 0 else 'N/A'
            logger.debug(f"Transcription corrected. Segments: {num_segments_corrected}, First segment: '{first_segment_text_corrected}'")
        
        # Extract word-level data for sentence splitting and merging
        all_words_data = []
        for segment in aligned_result.get("segments", []):
            all_words_data.extend(segment.get("words", []))

        logger.debug(f"Punctuation fix enabled: {apply_punctuation_fix_enabled}")
        logger.debug(f"All words data summary: {len(all_words_data)} words, first 5: {[w['word'] for w in all_words_data[:5]]}")
        # Conditionally apply sentence splitting and merging based on punctuation_fix_enabled
        if apply_punctuation_fix_enabled and all_words_data:
            logger.debug("Applying splitting/merging based on punctuation fix.")
            logger.info("Punctuation fix enabled. Applying sentence boundary splitting and merging short subtitles.")
            
            # Step 1: Split into sentence boundaries
            sentence_cues = split_at_sentence_boundaries(all_words_data)
            logger.debug(f"Split into {len(sentence_cues)} sentence cues.")

            # Step 2: Merge short subtitles
            min_subtitle_duration = sub_cfg.get('min_subtitle_duration', 0.5) # Example config value
            max_subtitle_duration = sub_cfg.get('max_subtitle_duration', 6.0) # Example config value
            min_subtitle_gap = sub_cfg.get('min_subtitle_gap', 0.1) # Example config value
            
            processed_cues = merge_short_subtitles(sentence_cues, min_subtitle_duration, max_subtitle_duration, min_subtitle_gap)
            logger.debug(f"Merged into {len(processed_cues)} processed cues.")
        else:
            logger.debug("Skipping splitting/merging (punctuation fix not enabled or no word data).")
            logger.info("Punctuation fix disabled. Skipping sentence boundary splitting and merging short subtitles.")
            # If punctuation fix is disabled, use the raw segments directly for cues
            processed_cues = []
            for segment in aligned_result.get("segments", []):
                # Create a simple cue from each segment, preserving original text and timing
                processed_cues.append({
                    'text': segment.get('text', ''),
                    'start': segment.get('start', 0.0),
                    'end': segment.get('end', 0.0)
                })
            logger.debug(f"Using raw segments as cues. Total cues: {len(processed_cues)}")

        subtitle_text = ""
        if subtitle_format == 'ass':
            logger.info(f"Converting processed cues to ASS format with time offset: {time_offset_seconds}s...")
            
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

            ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
            sub_cfg = config.get('subtitles', {})
            sub_font_name_arg = sub_cfg.get('font_name', 'Arial')
            fonts_folder = config.get('fonts_folder', 'fonts')
            sub_font_path_local = os.path.join(fonts_folder, sub_font_name_arg)
            actual_sub_font_name = sub_font_name_arg
            if os.path.exists(sub_font_path_local):
                actual_sub_font_name = get_font_name(sub_font_path_local)
            
            fc_bgr = sub_cfg.get('font_color_hex', 'FFFFFF')[4:6] + sub_cfg.get('font_color_hex', 'FFFFFF')[2:4] + sub_cfg.get('font_color_hex', 'FFFFFF')[0:2]
            secondary_color_bgr = sub_cfg.get('secondary_color_hex', '00FFFFFF')[4:6] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[2:4] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[0:2]
            oc_bgr = sub_cfg.get('outline_color_hex', '000000')[4:6] + sub_cfg.get('outline_color_hex', '000000')[2:4] + sub_cfg.get('outline_color_hex', '000000')[0:2]
            sc_bgr = sub_cfg.get('shadow_color_hex', '000000')[4:6] + sub_cfg.get('shadow_color_hex', '000000')[2:4] + sub_cfg.get('shadow_color_hex', '000000')[0:2]

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
            for cue in processed_cues: # Iterate over processed cues
                start_ass = format_timestamp_ass(cue['start'] + time_offset_seconds)
                end_ass = format_timestamp_ass(cue['end'] + time_offset_seconds)
                # Use the text from the processed cue
                ass_line = f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{split_subtitle_text_ass(cue['text'], max_width, max_lines)}"
                ass_events.append(ass_line)
            
            subtitle_text = ass_header + "\n".join(ass_events)
        else:
            logger.error(f"Unsupported subtitle format: {subtitle_format}. Only 'ass' is supported.")
            return None
        
        logger.debug(f"Final processed cues summary: {len(processed_cues)} cues, first cue text: '{processed_cues[0]['text'][:50]}...'")
        logger.debug(f"Subtitle text to be written (first 100 chars): '{subtitle_text[:100]}'")
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(subtitle_text)
        
        logger.info(f"Subtitles saved to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating subtitles for {audio_file_path}: {e}")
        return None

if __name__ == "__main__":
    logger.info("Enhanced subtitle generator ready for testing.")
