import os
import argparse
import whisperx
import certifi
from mutagen.mp3 import MP3

# Set up SSL for HTTPS requests
os.environ["SSL_CERT_FILE"] = certifi.where()
# Set number of threads for math libraries
os.environ["OMP_NUM_THREADS"] = "6"
os.environ["MKL_NUM_THREADS"] = "6"

def get_audio_duration(file_path):
    """Determine the duration of an MP3 file using mutagen."""
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        print(f"Could not determine audio duration for {file_path}: {e}")
        return 0

def format_time(seconds):
    """Convert time in seconds to SRT format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    millis = int((secs - int(secs)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(secs):02},{millis:03}"

def transcribe_with_whisperx(audio_path, language="en", model_name="base", device="cpu"):
    """Transcribe and perform forced alignment with WhisperX."""
    print(f"Running WhisperX for file: {audio_path}")
    # Load Whisper model with int8 compute type for stability
    model = whisperx.load_model(model_name, device=device, language=language, compute_type="int8")
    result = model.transcribe(audio_path)
    # Load model for forced alignment
    alignment_model, metadata = whisperx.load_align_model(language_code=language, device=device)
    aligned_result = whisperx.align(result["segments"], alignment_model, metadata, audio_path, device)
    return aligned_result

def whisperx_result_to_srt(aligned_result, max_width=21):
    """Convert WhisperX result to SRT format."""
    srt_lines = []
    segments = aligned_result["segments"]
    subtitle_index = 0
    
    block_text = ""
    block_start = 0.0
    block_end = 0.0
    
    for seg in segments:
        for w in seg["words"]:
            word = w["word"].strip()
            if not word:
                continue
            
            if not block_text:
                block_text = word
                block_start = w["start"]
                block_end = w["end"]
            else:
                test_len = len(block_text) + 1 + len(word)  # +1 for space
                if test_len <= max_width:
                    block_text += " " + word
                    block_end = w["end"]
                else:
                    subtitle_index += 1
                    srt_lines.append(str(subtitle_index))
                    srt_lines.append(f"{format_time(block_start)} --> {format_time(block_end)}")
                    srt_lines.append(block_text)
                    srt_lines.append("")
                    block_text = word
                    block_start = w["start"]
                    block_end = w["end"]
    
    if block_text:
        subtitle_index += 1
        srt_lines.append(str(subtitle_index))
        srt_lines.append(f"{format_time(block_start)} --> {format_time(block_end)}")
        srt_lines.append(block_text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)

def generate_srt(directory, generate_srt=False, max_width=21):
    """Generate SRT subtitles for the adjusted_voiceover.mp3 file."""
    if not generate_srt:
        return
    
    print("###### GENERATING SUBTITLES ######")
    
    # Find the adjusted_voiceover.mp3 file in the directory
    voiceover_path = os.path.join(directory, 'adjusted_voiceover.mp3')
    
    if os.path.exists(voiceover_path):
        try:
            # Create a directory for subtitles if it doesn't exist
            subs_dir = os.path.join(directory, 'subs')
            os.makedirs(subs_dir, exist_ok=True)
            
            # Generate the output path for the SRT file
            srt_output_path = os.path.join(subs_dir, 'voiceover.srt')
            
            # Skip if the SRT file already exists
            if os.path.exists(srt_output_path):
                print(f"Subtitles already exist at {srt_output_path}. Skipping.")
                return
            
            print(f"Transcribing audio file: {voiceover_path}")
            
            # Transcribe the audio
            aligned_result = transcribe_with_whisperx(voiceover_path)
            
            # Convert to SRT format
            srt_text = whisperx_result_to_srt(aligned_result, max_width)
            
            # Save the SRT file
            with open(srt_output_path, "w", encoding="utf-8") as f_out:
                f_out.write(srt_text)
            
            print(f"Subtitles saved to: {srt_output_path}")
        except Exception as e:
            print(f"Error generating subtitles: {e}")
    else:
        print(f"Voiceover file not found at {voiceover_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SRT subtitles from an audio file.")
    parser.add_argument('--i', type=str, required=True, dest='directory', help='Directory containing the adjusted_voiceover.mp3 file')
    parser.add_argument('--srt', type=str, default='1', dest='generate_srt', help='Generate SRT subtitles? 0/1')
    parser.add_argument('--smaxw', type=int, default=21, dest='subtitle_max_width', help='Maximum characters in one line of subtitles')
    
    args = parser.parse_args()
    
    generate_srt(args.directory, args.generate_srt == '1', args.subtitle_max_width)
