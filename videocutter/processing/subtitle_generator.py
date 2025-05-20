# videocutter/processing/subtitle_generator.py
# Handles transcribing audio and generating SRT subtitle files using WhisperX.

import os
import whisperx
import certifi
from mutagen.mp3 import MP3 # For get_audio_duration, though not directly used in main srt flow

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

def _whisperx_result_to_srt(aligned_result: dict, max_width: int) -> str:
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
                    srt_lines.append(f"{_format_time(current_line_start_time)} --> {_format_time(current_line_end_time)}")
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
        srt_lines.append(f"{_format_time(current_line_start_time)} --> {_format_time(current_line_end_time)}")
        srt_lines.append(current_line_text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)

def generate_srt_from_audio_file(
    audio_file_path: str, 
    output_srt_path: str, 
    config: dict
    ) -> str | None:
    """
    Generates an SRT subtitle file from an audio file using WhisperX.

    Args:
        audio_file_path (str): Path to the input audio file (e.g., voiceover.mp3).
        output_srt_path (str): Path where the generated SRT file should be saved.
        config (dict): Configuration dictionary. Expected keys:
            'subtitles': {
                'language': str (e.g., 'en'),
                'whisper_model': str (e.g., 'base'),
                'device': str (e.g., 'cpu' or 'cuda'),
                'compute_type': str (e.g., 'float32'),
                'max_line_width': int (e.g., 21)
            }
    Returns:
        str | None: Path to the generated SRT file, or None on failure.
    """
    print("###### GENERATING SUBTITLES ######")
    
    sub_cfg = config.get('subtitles', {})
    language = sub_cfg.get('language', 'en')
    model_name = sub_cfg.get('whisper_model', 'base') # e.g., "base", "small", "medium", "large-v2"
    device = sub_cfg.get('device', 'cpu') 
    compute_type = sub_cfg.get('compute_type', 'float32') # "int8", "float16", "float32"
    max_width = sub_cfg.get('max_line_width', 42) # Increased default based on common practice

    if not os.path.exists(audio_file_path):
        print(f"Audio file not found at {audio_file_path}. Cannot generate SRT.")
        return None
            
    # Skip if the SRT file already exists
    if os.path.exists(output_srt_path):
        print(f"Subtitles already exist at {output_srt_path}. Skipping generation.")
        return output_srt_path
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_srt_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created subtitle output directory: {output_dir}")

    try:
        print(f"Transcribing audio file: {audio_file_path}")
        aligned_result = _transcribe_with_whisperx(audio_file_path, language, model_name, device, compute_type)
        
        print("Converting transcription to SRT format...")
        srt_text = _whisperx_result_to_srt(aligned_result, max_width)
        
        with open(output_srt_path, "w", encoding="utf-8") as f_out:
            f_out.write(srt_text)
        
        print(f"Subtitles saved to: {output_srt_path}")
        return output_srt_path
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
