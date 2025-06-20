# videocutter/processing/audio_processor.py
# Handles all audio mixing and processing tasks.

import subprocess
import os
import shutil # For cleaning up temp files
import json
import logging

logger = logging.getLogger(__name__)

# Assuming video_processor contains get_video_duration or similar
from .video_processor import get_video_duration # This is for VIDEO duration

# For audio duration, mutagen is more direct for mp3
from mutagen.mp3 import MP3
from dotmap import DotMap


def get_mp3_duration(file_path: str) -> float | None:
    """Determine the duration of an MP3 file using mutagen."""
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        logger.error(f"Could not determine audio duration for {file_path} using mutagen: {e}")
        # Fallback to ffprobe format duration if mutagen fails
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout:
                metadata = json.loads(result.stdout)
                if metadata.get("format", {}).get("duration"):
                    return float(metadata["format"]["duration"])
            logger.error(f"ffprobe fallback for duration of {file_path} also failed.")
        except Exception as fe:
            logger.error(f"ffprobe fallback for duration of {file_path} failed: {fe}")
        return None

def process_audio(
    base_video_path: str, 
    output_video_with_audio_path: str, 
    config: DotMap,
    working_directory: str, # Directory to store intermediate files and find voiceover.mp3
    num_slides: int, # New: Number of slides/segments in the video
    slide_duration: int # New: Duration of each slide/segment
    ):
    """
    Adds a complete audio mix (soundtrack, voiceover, transitions) to a base video.
    Dynamically generates transition audio based on the number of slides.

    Args:
        base_video_path (str): Path to the input video (e.g., slideshow_base.mp4).
        output_video_with_audio_path (str): Path for the final video with audio.
        config (dict): Configuration dictionary. Expected keys:
            'audio': {
                'outro_duration': int,
                'vo_delay': int,
                'soundtrack_volume': float (e.g., 1.0),
                'transition_volume': float (e.g., 1.6),
                'sidechain_ratio': int (e.g., 3),
                'sidechain_threshold': float (e.g., 0.02),
                'sidechain_attack': int (e.g., 20),
                'sidechain_release': int (e.g., 500),
                'final_mix_main_volume': float (e.g., 2.0),
                'final_mix_transition_volume': float (e.g., 2.0)
            },
            'template_folder': str (path to template folder for audio files)
        working_directory (str): Directory where voiceover.mp3 is located and
                                 where intermediate audio files will be created.
    Returns:
        str | None: Path to the output video with audio, or None on failure.
    """
    logger.info(f"Processing audio for {base_video_path}...")
    logger.info(f"Working directory for audio processing: {working_directory}")
    
    audio_cfg = config.get('audio', {})
    # Resolve template_folder to an absolute path if it's relative
    # Assuming config.template_folder is relative to project root if not absolute
    # For robustness, main.py should resolve this and pass an absolute path in cfg.
    # For now, let's assume it's either absolute or correctly relative.
    template_folder_path = config.get('template_folder', 'TEMPLATE')
    if not os.path.isabs(template_folder_path):
        # This assumes audio_processor.py is in videocutter/processing/
        # Project root is two levels up from videocutter/processing/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_folder_path = os.path.join(project_root, template_folder_path)
    
    logger.info(f"Using template folder for audio: {template_folder_path}")

    soundtrack_path = os.path.join(template_folder_path, 'soundtrack.mp3')
    base_transition_500ms_path = os.path.join(template_folder_path, 'transition_500ms.mp3') # New base transition sound
    voiceover_end_path = os.path.join(template_folder_path, 'voiceover_end.mp3')
    voiceover_path = os.path.join(working_directory, 'voiceover.mp3')

    # Intermediate file paths
    soundtrack_adj_path = os.path.join(working_directory, 'adjusted_soundtrack.mp3')
    # Dynamically generated transition sound path
    dynamic_transitions_path = os.path.join(working_directory, 'dynamic_transitions.mp3') 
    transitions_adj_path = os.path.join(working_directory, 'adjusted_transitions.mp3')
    vo_adj_path = os.path.join(working_directory, 'adjusted_voiceover.mp3')
    vo_long_adj_path = os.path.join(working_directory, 'adjusted_long_voiceover.mp3')
    compressed_main_soundtrack_path = os.path.join(working_directory, 'compressed_main_soundtrack.mp3')
    vo_end_long_path = os.path.join(working_directory, 'voiceover_end_long.mp3')
    compressed_final_soundtrack_path = os.path.join(working_directory, 'compressed_final_soundtrack.mp3')
    mixed_final_audio_path = os.path.join(working_directory, 'mixed_final_audio.mp3')

    intermediate_files = [
        soundtrack_adj_path, dynamic_transitions_path, transitions_adj_path, 
        vo_adj_path, vo_long_adj_path, compressed_main_soundtrack_path, 
        vo_end_long_path, compressed_final_soundtrack_path, mixed_final_audio_path
    ]

    try:
        video_duration = get_video_duration(base_video_path)
        if video_duration is None or video_duration <= 0: # Added check for <= 0
            logger.error(f"Could not get valid duration for {base_video_path} (duration: {video_duration}). Aborting audio processing.")
            return None
        logger.info(f"Base video duration for audio processing: {video_duration:.2f}s")

        # Verify template files exist
        required_templates = [soundtrack_path, base_transition_500ms_path, voiceover_end_path]
        for t_path in required_templates:
            if not os.path.exists(t_path):
                logger.error(f"Error: Required audio template not found: {t_path}. Aborting audio processing.")
                return None

        # 1. Prepare Soundtrack
        cmd_soundtrack = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', soundtrack_path, '-ss', '0', '-t', str(video_duration),
            '-af', f"afade=t=in:st=0:d=3,afade=t=out:st={video_duration - 3}:d=3,volume={audio_cfg.get('soundtrack_volume', 1.0)}",
            '-q:a', '0', '-ac', '2', soundtrack_adj_path
        ]
        subprocess.run(cmd_soundtrack, check=True)
        logger.info(f"1. Soundtrack prepared: {soundtrack_adj_path}")

        # 2. Prepare Individual Transition Sounds and Calculate their Offsets
        num_transitions_needed = max(0, num_slides - 1)
        transition_duration = config.get('transition_duration', 0.5) # Default from config_manager.py
        actual_outro_duration = config.get('outro_duration', 14) # Get the actual duration

        transition_audio_inputs = [] # List of (input_path, offset_seconds)
        
        # Replicate the video transition timing logic from slideshow_generator.py
        current_cumulative_duration = slide_duration # Duration of the first segment
        
        for i in range(num_transitions_needed):
            # Calculate offset for the transition
            # The offset is where the next_stream starts to fade in on the current_stream
            # It should be the duration of the current_stream minus the transition duration
            offset = current_cumulative_duration - transition_duration
            
            # Add this transition sound input and its offset
            transition_audio_inputs.append((base_transition_500ms_path, offset))
            
            # Update cumulative duration for the next iteration
            # The output duration of xfade is (duration of first input) + (duration of second input) - (transition duration)
            # Here, duration of first input is current_cumulative_duration
            # Duration of second input is slide_duration (for all non-outro segments)
            # For the outro, its actual duration should be used.
            
            # Check if this is the transition to the outro
            if i == num_transitions_needed - 1: # This is the last transition, leading to the outro
                # The second input is the outro video, use its actual duration
                current_cumulative_duration = current_cumulative_duration + actual_outro_duration - transition_duration
            else:
                # For all other segments, assume slide_duration
                current_cumulative_duration = current_cumulative_duration + slide_duration - transition_duration
        
        logger.info(f"2. Calculated {len(transition_audio_inputs)} transition audio offsets.")

        if not os.path.exists(voiceover_path):
            logger.info(f"Voiceover file not found at {voiceover_path}. Proceeding without voiceover.")
            # If no voiceover, the compressed soundtrack is just the adjusted soundtrack
            shutil.copy(soundtrack_adj_path, compressed_final_soundtrack_path)
            logger.info("Skipped voiceover processing steps as voiceover.mp3 not found.")
        else:
            # 3. Prepare Main Voiceover (add initial delay)
            cmd_vo_delay = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-f', 'lavfi', '-t', str(audio_cfg.get('vo_delay', 5)), '-i', 'anullsrc=r=44100:cl=stereo',
                '-i', voiceover_path,
                '-filter_complex', '[0][1]concat=n=2:v=0:a=1[a]', '-map', '[a]',
                '-ac', '2', vo_adj_path
            ]
            subprocess.run(cmd_vo_delay, check=True)
            logger.info(f"3. Main voiceover initial delay added: {vo_adj_path}")

            # 4. Pad Main Voiceover with silence at the end
            vo_adj_duration = get_mp3_duration(vo_adj_path) # Use get_mp3_duration for audio file
            if vo_adj_duration is None: 
                logger.error(f"Error: Could not get duration for adjusted voiceover {vo_adj_path}. Aborting audio processing for voiceover.")
                # Fallback: treat as if no voiceover, copy soundtrack_adj to compressed_final_soundtrack
                shutil.copy(soundtrack_adj_path, compressed_final_soundtrack_path)
                logger.info("Skipped further voiceover processing due to duration error.")
                # Jump to step 8 (mix with transitions)
            else:
                main_vo_silence_needed = video_duration - vo_adj_duration
            if main_vo_silence_needed < 0: main_vo_silence_needed = 0 # Ensure not negative

            cmd_vo_pad = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-i', vo_adj_path,
                '-f', 'lavfi', '-t', str(main_vo_silence_needed), '-i', 'anullsrc=r=44100:cl=stereo',
                '-filter_complex', '[0][1]concat=n=2:v=0:a=1[a]', '-map', '[a]',
                '-ac', '2', vo_long_adj_path
            ]
            subprocess.run(cmd_vo_pad, check=True)
            logger.info(f"4. Main voiceover padded: {vo_long_adj_path}")

            # 5. Sidechain Compress Soundtrack with Main Voiceover
            sc_ratio = audio_cfg.get('sidechain_ratio', 3)
            sc_thresh = audio_cfg.get('sidechain_threshold', 0.02)
            sc_attack = audio_cfg.get('sidechain_attack', 20)
            sc_release = audio_cfg.get('sidechain_release', 500)
            cmd_sc_main = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-i', soundtrack_adj_path, '-i', vo_long_adj_path,
                '-filter_complex', f"[1:a]asplit=2[sc][mix];[0:a][sc]sidechaincompress=ratio={sc_ratio}:threshold={sc_thresh}:attack={sc_attack}:release={sc_release}[compr];[compr][mix]amix=normalize=0[aout]",
                '-map', '[aout]', '-q:a', '0', '-ac', '2', compressed_main_soundtrack_path
            ]
            subprocess.run(cmd_sc_main, check=True)
            logger.info(f"5. Soundtrack compressed with main voiceover: {compressed_main_soundtrack_path}")

            # 6. Prepare End Voiceover (add initial silence)
            vo_end_silence_needed = video_duration - audio_cfg.get('outro_duration', 14) 
            if vo_end_silence_needed < 0: vo_end_silence_needed = 0

            cmd_vo_end_delay = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-f', 'lavfi', '-t', str(vo_end_silence_needed), '-i', 'anullsrc=r=44100:cl=stereo',
                '-i', voiceover_end_path,
                '-filter_complex', '[0][1]concat=n=2:v=0:a=1[a]', '-map', '[a]',
                '-ac', '2', vo_end_long_path
            ]
            subprocess.run(cmd_vo_end_delay, check=True)
            logger.info(f"6. End voiceover prepared: {vo_end_long_path}")

            # 7. Sidechain Compress (Main Compressed) Soundtrack with End Voiceover
            cmd_sc_end = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-i', compressed_main_soundtrack_path, '-i', vo_end_long_path,
                '-filter_complex', f"[1:a]asplit=2[sc][mix];[0:a][sc]sidechaincompress=ratio={sc_ratio}:threshold={sc_thresh}:attack={sc_attack}:release={sc_release}[compr];[compr][mix]amix=normalize=0[aout]",
                '-map', '[aout]', '-q:a', '0', '-ac', '2', compressed_final_soundtrack_path
            ]
            subprocess.run(cmd_sc_end, check=True)
            logger.info(f"7. Soundtrack compressed with end voiceover: {compressed_final_soundtrack_path}")
        # End of "if os.path.exists(voiceover_path):" else block
        
        # 8. Mix Final Compressed Soundtrack with Transitions
        # Ensure compressed_final_soundtrack_path exists (it would if voiceover processing was skipped)
        if not os.path.exists(compressed_final_soundtrack_path):
            logger.error(f"Error: {compressed_final_soundtrack_path} not found before final mix. This shouldn't happen.")
            # As a fallback, try to use the adjusted_soundtrack if voiceover processing failed catastrophically
            if os.path.exists(soundtrack_adj_path):
                compressed_final_soundtrack_path = soundtrack_adj_path
                logger.warning(f"Fallback: Using {soundtrack_adj_path} for final mix.")
            else:
                logger.error("Cannot proceed with final audio mix, essential soundtrack component missing.")
                return None

        vol_main = audio_cfg.get('final_mix_main_volume', 2.0)
        vol_trans = audio_cfg.get('final_mix_transition_volume', 2.0)
        
        # Build the filter complex for mixing main soundtrack with individual transition sounds
        audio_filter_complex_parts = []
        audio_inputs_for_ffmpeg = ['-i', compressed_final_soundtrack_path] # Main soundtrack is the first input (index 0)
        
        current_audio_stream = "[0:a]" # Start with the main soundtrack stream
        
        for i, (trans_sound_path, offset) in enumerate(transition_audio_inputs):
            # Add each transition sound as a new input to FFmpeg
            audio_inputs_for_ffmpeg.extend(['-i', trans_sound_path])
            
            # The index of the current transition sound input in FFmpeg command
            # It will be 1, 2, 3... after the main soundtrack at 0
            trans_input_idx = i + 1 
            
            # Trim the transition sound to transition_duration and apply volume
            # Then apply adelay to shift it to the correct offset
            # Finally, mix it with the current main audio stream
            
            # Stream for the processed transition sound
            processed_trans_stream = f"[trans_proc{i}]"
            audio_filter_complex_parts.append(
                f"[{trans_input_idx}:a]atrim=duration={transition_duration},volume={vol_trans},adelay={int(offset*1000)}|{int(offset*1000)}{processed_trans_stream}"
            )
            
            # Mix the current main audio stream with the processed transition sound
            mixed_output_stream = f"[mixed_audio{i}]"
            audio_filter_complex_parts.append(
                f"{current_audio_stream}{processed_trans_stream}amix=inputs=2:normalize=0{mixed_output_stream}"
            )
            current_audio_stream = mixed_output_stream # Update current_audio_stream for next iteration

        final_audio_mix_stream = current_audio_stream # The last mixed stream is the final output
        
        # If there are no transitions, the final audio mix stream is just the main soundtrack
        if not transition_audio_inputs:
            final_audio_mix_stream = "[0:a]" # Map directly to the main soundtrack

        final_audio_filter_complex = ";".join(audio_filter_complex_parts)

        cmd_mix_final = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            *audio_inputs_for_ffmpeg, # All audio inputs (main soundtrack + individual transitions)
            '-filter_complex', final_audio_filter_complex,
            '-map', final_audio_mix_stream,
            mixed_final_audio_path
        ]
        subprocess.run(cmd_mix_final, check=True)
        logger.info(f"8. Final audio mixed: {mixed_final_audio_path}")

        # 9. Combine Video with Final Mixed Audio
        cmd_combine = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', base_video_path, '-i', mixed_final_audio_path,
            '-map', '0:v', '-map', '1:a',
            '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', '-shortest',
            output_video_with_audio_path
        ]
        subprocess.run(cmd_combine, check=True)
        logger.info(f"9. Final video with audio created: {output_video_with_audio_path}")
        
        return output_video_with_audio_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during audio processing: {e}")
        logger.error(f"Command that failed: {' '.join(e.cmd)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during audio processing: {e}")
        return None
    finally:
        # Clean up intermediate files
        for f_path in intermediate_files:
            if os.path.exists(f_path):
                try:
                    # os.remove(f_path)
                    logger.info(f"Cleaned up intermediate file: {f_path}")
                except OSError as e:
                    logger.error(f"Error cleaning up intermediate file {f_path}: {e}")


if __name__ == "__main__":
    logger.info("audio_processor.py executed directly (for testing).")
    # Example usage (requires a base video, template audio files, and a config dict)
    # mock_config_audio = {
    #     'audio': {
    #         'outro_duration': 14, 'vo_delay': 5, 'soundtrack_volume': 0.8,
    #         'transition_volume': 1.5, 'sidechain_ratio': 4, 'sidechain_threshold': 0.025,
    #         'sidechain_attack': 25, 'sidechain_release': 600,
    #         'final_mix_main_volume': 1.0, 'final_mix_transition_volume': 1.0
    #     },
    #     'template_folder': '../../TEMPLATE' # Adjust path relative to this test
    # }
    # test_work_dir = "temp_audio_test_work_dir"
    # if not os.path.exists(test_work_dir): os.makedirs(test_work_dir)
    # # Create/copy a dummy slideshow_base.mp4 and voiceover.mp3 into test_work_dir
    # # Create/copy dummy template audio files into ../../TEMPLATE
    
    # # result = process_audio(
    # #     os.path.join(test_work_dir, "slideshow_base.mp4"),
    # #     os.path.join(test_work_dir, "slideshow_with_audio.mp4"),
    # #     mock_config_audio,
    # #     test_work_dir
    # # )
    # # if result:
    # #     logger.info(f"Audio processing test successful: {result}")
    # # else:
    # #     logger.info("Audio processing test failed.")
    # # if os.path.exists(test_work_dir): shutil.rmtree(test_work_dir)
    logger.info("Audio processor test placeholder finished.")
