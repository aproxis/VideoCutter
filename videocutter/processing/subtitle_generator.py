# videocutter/processing/subtitle_generator.py
# Handles transcribing audio and generating SRT subtitle files using WhisperX.

import os
import whisperx
import certifi
from mutagen.mp3 import MP3 # For get_audio_duration, though not directly used in main srt flow
from dotmap import DotMap
from videocutter.utils.font_utils import get_font_name # Import for font resolution

# Set up SSL for HTTPS requests - should ideally be done once at application startup
if "SSL_CERT_FILE" not in os.environ:
    os.environ["SSL_CERT_FILE"] = certifi.where()

# Set number of threads for math libraries - might be better configured globally or via config
# For now, keeping them as they were in the original script.
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

def _transcribe_with_whisperx(audio_path: str, language: str, model_name: str, device: str, compute_type: str) -> dict:
    """Transcribe and perform forced alignment with WhisperX."""
    print(f"Running WhisperX (model: {model_name}, device: {device}, lang: {language}) for file: {audio_path}")
    model = whisperx.load_model(model_name, device=device, language=language, compute_type=compute_type)
    result = model.transcribe(audio_path) # Returns dict with 'segments'
    
    print("Loading alignment model...")
    alignment_model, metadata = whisperx.load_align_model(language_code=language, device=device)
    print("Performing alignment...")
    aligned_result = whisperx.align(result["segments"], alignment_model, metadata, audio_path, device)
    return aligned_result # This dict also has 'segments' key with word timings

def _whisperx_result_to_srt(aligned_result: dict, max_width: int, time_offset: float = 0.0) -> str: # Re-add time_offset
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

            if not current_line_text: # Starting a new line
                current_line_text = word
                current_line_start_time = word_start
                current_line_end_time = word_end
            else:
                # Check if adding the new word exceeds max_width
                if len(current_line_text) + 1 + len(word) <= max_width:
                    current_line_text += " " + word
                    current_line_end_time = word_end # Extend current line's end time
                else:
                    # Finalize current line
                    subtitle_index += 1
                    srt_lines.append(str(subtitle_index))
                    # Use current_line_start_time and current_line_end_time, add offset
                    srt_lines.append(f"{_format_time(current_line_start_time + time_offset)} --> {_format_time(current_line_end_time + time_offset)}")
                    srt_lines.append(current_line_text)
                    srt_lines.append("")
                    
                    # Start new line with current word
                    current_line_text = word
                    current_line_start_time = word_start
                    current_line_end_time = word_end
    
    # Add the last accumulated line if any
    if current_line_text:
        subtitle_index += 1
        srt_lines.append(str(subtitle_index))
        # Use current_line_start_time and current_line_end_time, add offset
        srt_lines.append(f"{_format_time(current_line_start_time + time_offset)} --> {_format_time(current_line_end_time + time_offset)}")
        srt_lines.append(current_line_text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)

def _whisperx_result_to_ass(aligned_result: dict, time_offset: float = 0.0, config: DotMap = None) -> str:
    """Convert WhisperX aligned result to ASS subtitle format."""
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
        else:  # horizontal
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
    
    # Dynamically generate the style string
    sub_cfg = config.get('subtitles', {})
    
    # Resolve subtitle font name
    sub_font_name_arg = sub_cfg.get('font_name', 'Arial')
    # Assuming fonts are in a 'fonts' folder relative to the project root
    # This path needs to be absolute for get_font_name to work correctly
    # For now, let's assume config.fonts_folder is correctly set up in config_manager.py
    fonts_folder = config.get('fonts_folder', 'fonts')
    sub_font_path_local = os.path.join(fonts_folder, sub_font_name_arg)
    
    actual_sub_font_name = sub_font_name_arg # Default to arg
    if os.path.exists(sub_font_path_local):
        actual_sub_font_name = get_font_name(sub_font_path_local) # From font_utils
    else:
        print(f"Warning: Subtitle font {sub_font_name_arg} not found at {sub_font_path_local}. Using raw font name.")

    # Color conversions (RRGGBB to BBGGRR)
    fc_bgr = sub_cfg.get('font_color_hex', 'FFFFFF')[4:6] + sub_cfg.get('font_color_hex', 'FFFFFF')[2:4] + sub_cfg.get('font_color_hex', 'FFFFFF')[0:2]
    # SecondaryColour (default to white)
    secondary_color_bgr = sub_cfg.get('secondary_color_hex', '00FFFFFF')[4:6] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[2:4] + sub_cfg.get('secondary_color_hex', '00FFFFFF')[0:2]
    # OutlineColour (default to black)
    oc_bgr = sub_cfg.get('outline_color_hex', '000000')[4:6] + sub_cfg.get('outline_color_hex', '000000')[2:4] + sub_cfg.get('outline_color_hex', '000000')[0:2]
    # BackColour (default to black)
    sc_bgr = sub_cfg.get('shadow_color_hex', '000000')[4:6] + sub_cfg.get('shadow_color_hex', '000000')[2:4] + sub_cfg.get('shadow_color_hex', '000000')[0:2]

    # Style definition
    ass_style_definition = (
        f"Style: Default,{actual_sub_font_name},"
        f"{sub_cfg.get('font_size', 24)}," # Fontsize
        f"&H00{fc_bgr}," # PrimaryColour
        f"&H00{secondary_color_bgr}," # SecondaryColour
        f"&H00{oc_bgr}," # OutlineColour
        f"&H00{sc_bgr}," # BackColour
        f"{sub_cfg.get('bold', -1)}," # Bold
        f"{sub_cfg.get('italic', 0)}," # Italic
        f"{sub_cfg.get('underline', 0)}," # Underline
        f"{sub_cfg.get('strikeout', 0)}," # StrikeOut
        f"{sub_cfg.get('scale_x', 100)}," # ScaleX
        f"{sub_cfg.get('scale_y', 100)}," # ScaleY
        f"{sub_cfg.get('spacing', 0.0)}," # Spacing
        f"{sub_cfg.get('angle', 0)}," # Angle
        f"{sub_cfg.get('border_style', 1)}," # BorderStyle
        f"{sub_cfg.get('outline_thickness', 1.0)}," # Outline
        f"{sub_cfg.get('shadow_distance', 1.0)}," # Shadow
        f"{sub_cfg.get('position_ass', 2)}," # Alignment
        f"{sub_cfg.get('margin_l', 10)}," # MarginL
        f"{sub_cfg.get('margin_r', 10)}," # MarginR
        f"{sub_cfg.get('margin_v', 10)}," # MarginV
        f"{sub_cfg.get('encoding', 1)}" # Encoding
    )
    
    ass_header += ass_style_definition + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    
    ass_events = []
    
    for segment in segments:
        for word_info in segment.get("words", []):
            text = word_info.get("word", "").strip()
            if not text:
                continue

            start = word_info.get("start", 0.0) + time_offset
            end = word_info.get("end", start) + time_offset

            start_ass = _format_ass_time(start)
            end_ass = _format_ass_time(end)

            ass_line = f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}"
            ass_events.append(ass_line)

    return ass_header + "\n".join(ass_events)

def _format_ass_time(seconds: float) -> str:
    """Format seconds to ASS time format: H:MM:SS.cs"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"

def generate_subtitles_from_audio_file(
    audio_file_path: str, 
    output_path: str, # Changed from output_srt_path
    config: DotMap,
    subtitle_format: str = 'srt', # New parameter
    time_offset_seconds: float = 0.0
    ) -> str | None:
    """
    Generates a subtitle file (SRT or ASS) from an audio file using WhisperX.

    Args:
        audio_file_path (str): Path to the input audio file (e.g., voiceover.mp3).
        output_path (str): Path where the generated subtitle file should be saved.
        config (dict): Configuration dictionary. Expected keys:
            'subtitles': {
                'language': str (e.g., 'en'),
                'whisper_model': str (e.g., 'base'),
                'device': str (e.g., 'cpu' or 'cuda'),
                'compute_type': str (e.g., 'float32'),
                'max_line_width': int (e.g., 21)
            }
        subtitle_format (str): Desired subtitle format ('srt' or 'ass').
    Returns:
        str | None: Path to the generated subtitle file, or None on failure.
    """
    print("###### GENERATING SUBTITLES ######")
    
    sub_cfg = config.get('subtitles', {})
    language = sub_cfg.get('language', 'en')
    model_name = sub_cfg.get('whisper_model', 'base')
    device = sub_cfg.get('device', 'cpu') 
    compute_type = sub_cfg.get('compute_type', 'float32')
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
        print(f"Transcribing audio file: {audio_file_path}")
        aligned_result = _transcribe_with_whisperx(audio_file_path, language, model_name, device, compute_type)
        
        subtitle_text = ""
        if subtitle_format == 'srt':
            print(f"Converting transcription to SRT format with time offset: {time_offset_seconds}s...")
            subtitle_text = _whisperx_result_to_srt(aligned_result, max_width, time_offset=time_offset_seconds)
        elif subtitle_format == 'ass':
            print(f"Converting transcription to ASS format with time offset: {time_offset_seconds}s...")
            subtitle_text = _whisperx_result_to_ass(aligned_result, time_offset=time_offset_seconds, config=config)
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
    print("subtitle_generator.py executed directly (for testing).")
    # Example usage (requires an audio file and WhisperX setup)
    # mock_config_srt = {
    #     'subtitles': {
    #         'language': 'en',
    #         'whisper_model': 'tiny', # Use tiny for faster testing
    #         'device': 'cpu',
    #         'compute_type': 'float32',
    #         'max_line_width': 30
    #     }
    # }
    # test_audio_file = "path/to/your/test_audio.mp3" # Replace with actual audio
    # test_srt_output = "output/test_audio.srt"
    
    # if os.path.exists(test_audio_file):
    #     if not os.path.exists("output"): os.makedirs("output")
    #     generated_srt = generate_srt_from_audio_file(test_audio_file, test_srt_output, mock_config_srt)
    #     if generated_srt:
    #         print(f"SRT generation test successful: {generated_srt}")
    #     else:
    #         print("SRT generation test failed.")
    # else:
    #     print(f"Test audio file not found: {test_audio_file}")
    print("Subtitle generator test placeholder finished.")
