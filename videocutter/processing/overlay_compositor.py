# videocutter/processing/overlay_compositor.py
# Handles applying final overlays (title, subscribe, effects) and rendering subtitles.

import subprocess
import os
import random
import json # For ffprobe
import glob # For font fallback
import tempfile # For creating temporary files
from typing import Optional # For Optional type hint
from dotmap import DotMap # Import DotMap
import shutil # Import shutil for file copying

# Assuming font_utils is in videocutter.utils
from videocutter.utils.font_utils import get_font_name
# Assuming video_processor has get_video_duration or similar
from .video_processor import get_video_duration


def _get_overlay_video_duration(overlay_video_path: str) -> float:
    """Gets overlay video duration using ffprobe."""
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", overlay_video_path]
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True, check=True)
        json_data = json.loads(result.stdout)
        return float(json_data['format']['duration'])
    except Exception as e:
        print(f"Error getting overlay video duration for {overlay_video_path}: {e}. Defaulting to 23s.")
        return 23.0 # Fallback from original script

def apply_final_overlays(
    input_video_path: str, 
    output_video_path: str, 
    config: DotMap, # Changed to DotMap
    working_directory: str, # For resolving subtitle_file path
    subtitle_file_path: str | None = None # Optional path to subtitle file (SRT or ASS)
    ):
    """
    Applies final overlays (title, subscribe, effects) and renders subtitles.

    Args:
        input_video_path (str): Path to the video with audio (e.g., slideshow_with_audio.mp4).
        output_video_path (str): Path for the final output video.
        config (dict): Configuration dictionary. Expected keys:
            'title_overlay': { 'text', 'font_file', 'font_size', 'font_color', 
                               'start_delay', 'appearance_delay', 'visible_time', 
                               'x_offset', 'y_offset' }
            'subscribe_overlay': { 'chromakey_color', 'similarity', 'blend', 'start_delay' }
            'video_orientation': str ('vertical' or 'horizontal')
            'template_folder': str
            'effects': { 'overlay_file', 'opacity', 'blend_mode' } (optional)
            'subtitles': { 'enabled', 'font_name', 'font_size', 'font_color_hex', 
                           'outline_color_hex', 'outline_thickness', 'shadow_color_hex', 
                           'shadow_opacity', 'shadow_enabled', 'position_ass' } (optional)
        working_directory (str): Base directory for the current run (e.g., INPUT/RESULT/datetime_folder)
        subtitle_file_path (str | None): Absolute path to the subtitle file (SRT or ASS) if subtitles are enabled.
    
    Returns:
        str | None: Path to the final video, or None on failure.
    """
    print(f"Applying final overlays to {input_video_path}...")

    title_cfg = config.get('title_overlay', {})
    sub_ov_cfg = config.get('subscribe_overlay', {})
    effects_cfg = config.get('effects', {})
    subtitle_cfg = config.get('subtitles', {})
    video_orientation = config.get('video_orientation', 'vertical')
    template_folder = config.get('template_folder', 'TEMPLATE')
    
    # Title properties
    title_text_val = title_cfg.get('text', 'Model Name').strip('"')
    title_font_filename = title_cfg.get('font_file', 'Montserrat-SemiBold.otf')
    # Resolve title font path (checking 'fonts/' then system) - this could use font_utils more extensively
    title_font_path = os.path.join('fonts', title_font_filename)
    if not os.path.exists(title_font_path):
        title_font_path = title_cfg.get('system_font_fallback_path', '/Users/a/Library/Fonts/Montserrat-SemiBold.otf') # Example fallback
        if not os.path.exists(title_font_path):
             print(f"Warning: Title font {title_font_filename} not found in fonts/ or as fallback. FFmpeg might fail or use default.")
             title_font_path = title_font_filename # Let ffmpeg try to find it

    title_font_size = title_cfg.get('font_size', 90)
    title_font_color_hex = title_cfg.get('font_color', 'FFFFFF')
    if title_font_color_hex.lower() == 'random':
        title_font_color_hex = random.choice(['FF00B4', 'ff6600', '0b4178'])
    
    # Title text timing properties
    title_appearance_delay = title_cfg.get('appearance_delay', 1)
    title_visible_time = title_cfg.get('visible_time', 5)
    title_x_offset = title_cfg.get('x_offset', 110)
    title_y_offset = title_cfg.get('y_offset', -35)
    enable_title = title_cfg.get('enable_title', True) # Get enable status
    title_opacity = title_cfg.get('opacity', 1.0) # Get title opacity
    enable_title_background = title_cfg.get('enable_background', False) # New: Get enable status for background
    title_background_color = title_cfg.get('background_color', '000000') # New: Get background color
    title_background_opacity = title_cfg.get('background_opacity', 0.5) # New: Get background opacity

    print(f"DEBUG: enable_title_background: {enable_title_background}")
    print(f"DEBUG: title_background_color: {title_background_color}")
    print(f"DEBUG: title_background_opacity: {title_background_opacity}")

    # Subscribe overlay properties
    enable_subscribe_overlay = sub_ov_cfg.get('enabled', True) # New: Get enable status
    subscribe_appearance_delay = sub_ov_cfg.get('subscribe_delay', 21) # New: Separate delay for subscribe
    chromakey_color_hex = sub_ov_cfg.get('chromakey_color', '65db41')
    chromakey_similarity = sub_ov_cfg.get('similarity', 0.18)
    chromakey_blend = sub_ov_cfg.get('blend', 0.0)
    
    # Title Video Overlay properties
    title_video_overlay_cfg = config.get('title_video_overlay', {})
    enable_title_video_overlay = title_video_overlay_cfg.get('enabled', False)
    title_video_overlay_file = title_video_overlay_cfg.get('overlay_file')
    title_video_overlay_delay = title_video_overlay_cfg.get('appearance_delay', 0)
    title_video_chromakey_color = title_video_overlay_cfg.get('chromakey_color', '65db41')
    title_video_chromakey_similarity = title_video_overlay_cfg.get('chromakey_similarity', 0.18)
    title_video_chromakey_blend = title_video_overlay_cfg.get('chromakey_blend', 0.0)

    main_video_duration = get_video_duration(input_video_path)
    if main_video_duration is None:
        print(f"Could not get duration for main video {input_video_path}. Aborting.")
        return None

    # --- Build Filter Complex ---
    filter_complex_parts = []
    ffmpeg_inputs = ['-i', input_video_path]
    input_stream_indices = {"main_video": 0}
    next_input_idx = 1 # For optional subscribe/effect/title_video overlay

    # Conditionally add subscribe overlay input and filters
    subscribe_overlay_file = sub_ov_cfg.get('overlay_file')
    print(f"DEBUG: enable_subscribe_overlay: {enable_subscribe_overlay}")
    print(f"DEBUG: subscribe_overlay_file: {subscribe_overlay_file}")

    if enable_subscribe_overlay and subscribe_overlay_file:
        subscribe_video_full_path = os.path.join(config.get('subscribe_folder', 'effects/subscribe'), subscribe_overlay_file)
        print(f"DEBUG: subscribe_video_full_path: {subscribe_video_full_path}")
        print(f"DEBUG: os.path.exists(subscribe_video_full_path): {os.path.exists(subscribe_video_full_path)}")

        if os.path.exists(subscribe_video_full_path):
            ffmpeg_inputs.extend(['-i', subscribe_video_full_path])
            subscribe_input_idx = input_stream_indices["subscribe_overlay"] = next_input_idx
            next_input_idx += 1
            
            subscribe_overlay_duration = _get_overlay_video_duration(subscribe_video_full_path)
            
            # 1. Audio Mix (main video audio + subscribe overlay audio)
            audio_mix = (
                f"[{subscribe_input_idx}:a]adelay={subscribe_appearance_delay*1000}|{subscribe_appearance_delay*1000},"
                f"volume=0.5[a_sub];"
                f"[{input_stream_indices['main_video']}:a]volume=1.0[a_main];"
                f"[a_main][a_sub]amix=inputs=2:normalize=0[aout]"
            )
            filter_complex_parts.append(audio_mix)

            # 2. Video Base (main video + chromakeyed subscribe overlay)
            video_base = (
                f"[{input_stream_indices['main_video']}:v]setpts=PTS-STARTPTS[v_main];"
                f"[{subscribe_input_idx}:v]setpts=PTS-STARTPTS+{subscribe_appearance_delay}/TB,"
                f"chromakey=color=0x{chromakey_color_hex}:similarity={chromakey_similarity}:blend={chromakey_blend}[v_sub_ck];"
                f"[v_main][v_sub_ck]overlay=enable='between(t,{subscribe_appearance_delay},{subscribe_appearance_delay+subscribe_overlay_duration})'[v_with_sub]"
            )
            filter_complex_parts.append(video_base)
            current_video_stream = "v_with_sub"
        else:
            print(f"Warning: Subscribe overlay file '{subscribe_video_full_path}' not found. Skipping subscribe overlay.")
            filter_complex_parts.append(f"[{input_stream_indices['main_video']}:a]volume=1.0[aout]")
            filter_complex_parts.append(f"[{input_stream_indices['main_video']}:v]setpts=PTS-STARTPTS[v_main]")
            current_video_stream = "v_main"
    else:
        print(f"Info: Subscribe overlay disabled or no file selected. Skipping subscribe overlay.")
        # If subscribe overlay is disabled, audio is just main video's audio, and video stream is just main video
        filter_complex_parts.append(f"[{input_stream_indices['main_video']}:a]volume=1.0[aout]")
        filter_complex_parts.append(f"[{input_stream_indices['main_video']}:v]setpts=PTS-STARTPTS[v_main]")
        current_video_stream = "v_main"

    # 3. Optional Effect Overlay
    effect_overlay_file = effects_cfg.get('overlay_file')
    enable_effect_overlay = effects_cfg.get('enabled', False) # Get enable status
    has_effect = False
    if enable_effect_overlay and effect_overlay_file: # Check enable flag
        effect_path = os.path.join(config.get('effects_folder', 'effects/overlays'), effect_overlay_file) # Use new effects_folder
        if os.path.exists(effect_path):
            has_effect = True
            ffmpeg_inputs.extend(['-i', effect_path])
            effect_input_idx = input_stream_indices["effect_overlay"] = next_input_idx
            next_input_idx +=1
            
            effect_opacity = effects_cfg.get('opacity', 0.2)
            effect_blend_mode = effects_cfg.get('blend_mode', 'overlay').lower()
            
            effect_stream_label = "v_effect_processed"
            if effect_blend_mode in ["normal", "overlay", "over"]:
                filter_complex_parts.append(
                    f"[{effect_input_idx}:v]format=rgba,colorchannelmixer=aa={effect_opacity},"
                    f"setpts=PTS-STARTPTS,scale=iw:ih,setsar=1[effect_alpha];"
                    f"[{current_video_stream}][effect_alpha]overlay=shortest=1[{effect_stream_label}]"
                )
            else: # Other blend modes
                filter_complex_parts.append(
                    f"[{current_video_stream}]format=rgba,scale=iw:ih,setsar=1,format=rgb24[v_rgb_for_blend];"
                    f"[{effect_input_idx}:v]format=rgba,trim=duration={main_video_duration},setpts=PTS-STARTPTS,"
                    f"scale=iw:ih,setsar=1,format=rgb24[effect_rgb];"
                    f"[v_rgb_for_blend][effect_rgb]blend=all_mode={effect_blend_mode}:all_opacity={effect_opacity}[blended_effect];"
                    f"[blended_effect]format=yuv420p[{effect_stream_label}]"
                )
            current_video_stream = effect_stream_label
        else:
            print(f"Warning: Effect overlay file '{effect_path}' not found. Skipping effect overlay.")
    else:
        print(f"Info: Effect overlay disabled or no file selected. Skipping effect overlay.")

    # 4. Title Video Overlay (Conditional)
    temp_title_video_overlay_file: Optional[str] = None
    try:
        if enable_title_video_overlay and title_video_overlay_file:
            title_video_overlay_full_path = os.path.join(config.get('title_folder', 'effects/title'), title_video_overlay_file) # Use new title_folder
            if os.path.exists(title_video_overlay_full_path):
                ffmpeg_inputs.extend(['-i', title_video_overlay_full_path])
                title_video_input_idx = input_stream_indices["title_video_overlay"] = next_input_idx
                next_input_idx += 1

                title_video_overlay_duration = _get_overlay_video_duration(title_video_overlay_full_path)

                title_video_base = (
                    f"[{current_video_stream}]setpts=PTS-STARTPTS[v_prev];"
                    f"[{title_video_input_idx}:v]setpts=PTS-STARTPTS+{title_video_overlay_delay}/TB,"
                    f"chromakey=color=0x{title_video_chromakey_color}:similarity={title_video_chromakey_similarity}:blend={title_video_chromakey_blend}[v_title_ov_ck];"
                    f"[v_prev][v_title_ov_ck]overlay=enable='between(t,{title_video_overlay_delay},{title_video_overlay_delay+title_video_overlay_duration})'[v_with_title_video_ov]"
                )
                filter_complex_parts.append(title_video_base)
                current_video_stream = "v_with_title_video_ov"
            else:
                print(f"Warning: Title video overlay file '{title_video_overlay_full_path}' not found.")
        
        # 5. Title Text Overlay (Conditional)
        temp_title_file: Optional[str] = None
        if enable_title:
            # Determine title text start time based on title video overlay
            if enable_title_video_overlay:
                title_text_start_time = title_video_overlay_delay + title_appearance_delay
            else:
                title_text_start_time = title_appearance_delay

            # Ensure title_font_path is correctly escaped for ffmpeg if it contains spaces or special chars
            escaped_title_font_path = title_font_path.replace("\\", "/") # Basic normalization
            
            # Write title text to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
                f.write(title_text_val)
                temp_title_file = f.name

            # Base drawtext options
            drawtext_options = [
                f"textfile='{temp_title_file}'",
                f"x=((w-tw)/2+{title_x_offset})",
                f"y=((h/2)+{title_y_offset})",
                f"enable='between(t,{title_text_start_time},{title_text_start_time+title_visible_time})'",
                f"fontfile='{escaped_title_font_path}'",
                f"fontsize={title_font_size}",
                f"fontcolor=0x{title_font_color_hex}",
                f"alpha={title_opacity}",
                f"shadowcolor=black",
                f"shadowx=4",
                f"shadowy=2"
            ]

            if enable_title_background:
                # Add background color and opacity
                drawtext_options.append(f"box=1")
                drawtext_options.append(f"boxcolor=0x{title_background_color}@{title_background_opacity}")
                drawtext_options.append(f"boxborderw=30") # Add some padding around the text

            title_drawtext = f"drawtext={':'.join(drawtext_options)}"
            filter_complex_parts.append(f"[{current_video_stream}]{title_drawtext}[v_with_title]")
            current_video_stream = "v_with_title"
        # If title is not enabled, current_video_stream remains unchanged, effectively skipping this overlay.

        # 6. Subtitle Rendering
        if subtitle_cfg.get('enabled', False) and subtitle_file_path and os.path.exists(subtitle_file_path):
            print(f"Preparing subtitle styling for {subtitle_file_path}...")
            
            # Define temp_dir for overlay_compositor
            package_root_dir = os.path.dirname(os.path.abspath(__file__)) # videocutter/processing/
            videocutter_root_dir = os.path.dirname(package_root_dir) # videocutter/
            project_root_dir = os.path.dirname(videocutter_root_dir) # One level up to VideoCutter/
            temp_dir = os.path.join(project_root_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True) # Ensure temp directory exists

            # Copy subtitle file to temp_dir and use that path
            subtitle_extension = os.path.splitext(subtitle_file_path)[1].lstrip('.')
            temp_subtitle_path_in_temp_dir = os.path.join(temp_dir, f"voiceover.{subtitle_extension}")
            shutil.copy(subtitle_file_path, temp_subtitle_path_in_temp_dir)
            print(f"Copied subtitle to temp directory for overlay_compositor: {temp_subtitle_path_in_temp_dir}")

            # Resolve subtitle font name (using font_utils if available, or simple name)
            sub_font_name_arg = subtitle_cfg.get('font_name', 'Arial')
            sub_font_path_local = os.path.join(config.get('fonts_folder','fonts'), sub_font_name_arg) # Check local 'fonts'
            
            actual_sub_font_name = sub_font_name_arg # Default to arg
            if os.path.exists(sub_font_path_local):
                actual_sub_font_name = get_font_name(sub_font_path_local) # From font_utils
            # Add more robust system font path resolution here if needed via font_utils

            fc_bgr = subtitle_cfg.get('font_color_hex', 'FFFFFF')[4:6] + subtitle_cfg.get('font_color_hex', 'FFFFFF')[2:4] + subtitle_cfg.get('font_color_hex', 'FFFFFF')[0:2]
            oc_bgr = subtitle_cfg.get('outline_color_hex', '000000')[4:6] + subtitle_cfg.get('outline_color_hex', '000000')[2:4] + subtitle_cfg.get('outline_color_hex', '000000')[0:2]
            sc_bgr = subtitle_cfg.get('shadow_color_hex', '000000')[4:6] + subtitle_cfg.get('shadow_color_hex', '000000')[2:4] + subtitle_cfg.get('shadow_color_hex', '000000')[0:2]
            
            style_parts = [
                f"FontName={actual_sub_font_name}",
                f"Fontsize={subtitle_cfg.get('font_size', 24)}",
                f"PrimaryColour=&H00{fc_bgr}",
                f"OutlineColour=&H00{oc_bgr}",
                f"Outline={subtitle_cfg.get('outline_thickness', 1)}",
                f"Alignment={subtitle_cfg.get('position_ass', 2)}"
            ]
            if subtitle_cfg.get('shadow_enabled', True):
                opacity_val = int((1.0 - subtitle_cfg.get('shadow_opacity', 0.5)) * 255)
                opacity_hex = format(opacity_val, '02X')
                style_parts.append(f"BackColour=&H{opacity_hex}{sc_bgr}")
                style_parts.append("Shadow=2") # Use a more visible shadow distance
            else:
                style_parts.append("Shadow=0")
            
            ass_style = ",".join(style_parts)
            abs_fonts_dir = os.path.abspath(config.get('fonts_folder','fonts'))
            
            # Use the copied file in temp_dir for FFmpeg
            ffmpeg_safe_subtitle_path = temp_subtitle_path_in_temp_dir
            ffmpeg_safe_fonts_dir = abs_fonts_dir # No escaping needed for fontsdir if it's absolute and simple

            filter_complex_parts.append(
                f"[{current_video_stream}]subtitles='{ffmpeg_safe_subtitle_path}':fontsdir='{ffmpeg_safe_fonts_dir}'[v_final]"
            )
            current_video_stream = "v_final" # Update current_video_stream after applying subtitles
        else:
            # If subtitles are not enabled/applied, the stream before this block is effectively the final one for mapping.
            # However, to ensure the -map directive always uses [v_final], we create a null filter to [v_final].
            filter_complex_parts.append(f"[{current_video_stream}]null[v_final]") 
            current_video_stream = "v_final" # Explicitly set current_video_stream to "v_final"

        # --- Execute FFmpeg Command ---
        final_filter_complex_str = ";".join(filter_complex_parts)
        
        ffmpeg_cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'debug']
        ffmpeg_cmd.extend(ffmpeg_inputs)
        ffmpeg_cmd.extend([
            '-filter_complex', final_filter_complex_str,
            '-map', '[v_final]', # Explicitly map [v_final] as it's always the last video stream label
            '-map', '[aout]', # From audio_mix
            '-c:v', 'libx264', '-crf', str(config.get('video_crf', 22)), '-preset', config.get('video_preset', 'medium'),
            '-c:a', 'aac', '-b:a', config.get('audio_bitrate', '192k'),
            output_video_path
        ])

        print(f"Executing final overlay composition: {' '.join(ffmpeg_cmd)}")
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Final video saved: {output_video_path}")
            return output_video_path
        except subprocess.CalledProcessError as e:
            print(f"Error during final overlay composition: {e}")
            print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")
            return None
    finally:
        if temp_title_file and os.path.exists(temp_title_file):
            os.remove(temp_title_file)
            print(f"Cleaned up temporary title file: {temp_title_file}")

if __name__ == "__main__":
    print("overlay_compositor.py executed directly (for testing).")
    # Example usage (requires a video with audio, templates, fonts, and a config dict)
    # mock_config_overlay = {
    #     'title_overlay': { 'text': 'Awesome Title', 'font_file': 'Montserrat-SemiBold.otf', 
    #                        'font_size': 70, 'font_color': 'FFF000', 'start_delay': 5, 
    #                        'appearance_delay': 1, 'visible_time': 4, 'x_offset': 0, 'y_offset': 100 },
    #     'subscribe_overlay': { 'chromakey_color': '00FF00', 'similarity': 0.1, 'blend': 0.05, 'start_delay': 5 },
    #     'video_orientation': 'horizontal',
    #     'template_folder': '../../TEMPLATE', # Adjust path
    #     'fonts_folder': '../../fonts',     # Adjust path
    #     'effects_folder': '../../effects', # Adjust path
    #     'effects': { 'overlay_file': 'film_grain.mp4', 'opacity': 0.1, 'blend_mode': 'overlay' }, # Optional
    #     'subtitles': { 'enabled': True, 'font_name': 'Arial', 'font_size': 28, 
    #                    'font_color_hex': 'FFFFFF', 'outline_color_hex': '000000', 
    #                    'outline_thickness': 1.5, 'shadow_color_hex': '333333', 
    #                    'shadow_opacity': 0.6, 'shadow_enabled': True, 'position_ass': 2 },
    #     'video_crf': 23, 'video_preset': 'fast', 'audio_bitrate': '160k'
    # }
    # test_input_video = "path/to/slideshow_with_audio.mp4"
    # test_srt = "path/to/subs/voiceover.srt" # Create a dummy srt
    # test_output_final = "output/final_video_test.mp4"
    # test_working_dir = "path/to/working_dir" # Where srt might be relative to if not absolute

    # if not os.path.exists("output"): os.makedirs("output")
    # if os.path.exists(test_input_video) and (not subtitle_cfg.get('enabled') or os.path.exists(test_srt)):
    #     apply_final_overlays(test_input_video, test_output_final, mock_config_overlay, test_working_dir, test_srt if subtitle_cfg.get('enabled') else None)
    # else:
    #     print("Test files not found for overlay_compositor.")
    print("Overlay compositor test placeholder finished.")
