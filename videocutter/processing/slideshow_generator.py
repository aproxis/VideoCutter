# videocutter/processing/slideshow_generator.py
# Handles creating the base video slideshow from media items with transitions.

import subprocess
import os
import random

# PIL Image is imported in the original slideshow.py but not directly used for manipulation
# in the core slideshow generation part. Keeping it commented for now.
# from PIL import Image 

def _get_video_dimensions(config: dict, video_orientation: str) -> tuple[int, int]:
    """
    Determines target video width and height based on orientation and configuration.
    """
    target_resolution = config.get('target_resolution', {})
    if video_orientation == 'vertical':
        target_height = target_resolution.get('vertical_height', 1920)
        target_width = target_resolution.get('vertical_width', 1080)
    else:  # horizontal
        target_height = target_resolution.get('horizontal_height', 1080)
        target_width = target_resolution.get('horizontal_width', 1920)
    return target_width, target_height

def generate_base_slideshow(
    media_file_paths: list[str], 
    output_path: str, 
    config: dict # Expects a dictionary-like config object
    ):
    """
    Generates a base slideshow video from a list of media files with transitions.
    This function focuses on the video track only. Audio and final overlays
    are handled by other modules.

    Args:
        media_file_paths (list[str]): A list of absolute paths to media files (images/videos).
                                      The last item is expected to be the outro video.
        output_path (str): The full path for the output slideshow.mp4.
        config (dict): Configuration dictionary containing necessary parameters like:
            - slide_duration (int): Duration for each image/segment.
            - video_orientation (str): 'vertical' or 'horizontal'.
            - watermark (dict, optional): { 
                'text': str, 'type': str ('ccw', 'random'), 
                'speed_frames': int, 'font_file_path': str, 
                'font_size': int, 'opacity': float 
              }
            - outro_duration (int): Duration of the outro video.
            - (Other params like fps, target_width, target_height will be derived or set to defaults)
    """
    print(f"Generating base slideshow: {output_path}")
    
    # Use slide_duration from config (which defaults to segment_duration - 1)
    # This is the effective display time for each item before transition.
    slide_duration = config.get('slide_duration', 5) 
    if slide_duration <= 0: slide_duration = 1 # Ensure positive
    
    video_orientation = config.get('video_orientation', 'vertical')
    target_width, target_height = _get_video_dimensions(config, video_orientation)

    fps = config.get('fps', 25)
    watermark_config = config.get('watermark_settings') # Use 'watermark_settings' to get the dict
    outro_duration = config.get('outro_duration', 14) # Duration of the actual outro clip

    # Retrieve new watermark settings
    watermark_font_size = config.get('watermark_font_size', 40)
    watermark_opacity = config.get('watermark_opacity', 0.7)
    watermark_fontcolor = config.get('watermark_fontcolor', 'random')

    ffmpeg_cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error']
    filter_complex_parts = []
    inputs = []

    def _prepare_media_input(
        idx: int, 
        media_path: str, 
        is_outro: bool, 
        slide_duration: int, 
        fps: int, 
        target_width: int, 
        target_height: int
    ) -> tuple[list[str], str]:
        """
        Prepares FFmpeg input arguments and filter complex part for a single media item.
        Returns (input_args, filter_part).
        """
        file_extension = os.path.splitext(media_path)[1].lower()
        input_args = []
        filter_part = ""

        if file_extension in ['.jpg', '.jpeg', '.png']:
            input_args.extend(['-loop', '1', '-t', str(slide_duration), '-framerate', str(fps)])
            input_args.extend(['-i', media_path])
            zoompan_duration_frames = int(fps * slide_duration) 
            
            # Define dynamic positions for zoompan
            positions_zoom_in = [
                ("0", "0"),                                    # top-left
                ("iw-(iw/zoom)", "0"),                         # top-right
                ("0", "ih-(ih/zoom)"),                         # bottom-left
                ("iw-(iw/zoom)", "ih-(ih/zoom)"),              # bottom-right
                ("(iw-iw/zoom)/2", "(ih-ih/zoom)/2"),          # center
            ]

            zoom_speed = round(random.uniform(0.0005, 0.002), 6)
            
            # Randomly choose between zoom-in and zoom-out
            zoom_direction = random.choice(['in', 'out'])

            if zoom_direction == 'in':
                x_expr, y_expr = random.choice(positions_zoom_in)
                zoom_expr = f"1+{zoom_speed}*on"
            else: # zoom_direction == 'out'
                # Zoom out always from center
                x_expr, y_expr = ("(iw-iw/zoom)/2", "(ih-ih/zoom)/2")
                zoom_expr = f"if(lte(zoom,1.0),1.5,max(1.001,zoom-{zoom_speed}))" # Use random speed for zoom out

            # Apply pre-scaling and then zoompan
            filter_part = (
                f"[{idx}:v]scale=8000:-1[scaled_img{idx}];"  # Pre-scale to 8000px width
                f"[scaled_img{idx}]zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={zoompan_duration_frames}:s={target_width}x{target_height}:fps={fps}[zp{idx}];"
                f"[zp{idx}]format=yuv420p[v{idx}]"
            )
        elif file_extension == '.mp4':
            input_args.extend(['-i', media_path])
            scale_filter = f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
            
            if is_outro:
                filter_part = (
                    f"[{idx}:v]setpts=PTS-STARTPTS,fps={fps},setsar=1,{scale_filter},format=yuv420p[v{idx}]"
                )
            else:
                filter_part = (
                    f"[{idx}:v]setpts=PTS-STARTPTS,fps={fps},{scale_filter},format=yuv420p[v{idx}]"
                )
        else:
            print(f"Skipping unsupported file type: {media_path}")
            return [], "" # Return empty if unsupported

        return input_args, filter_part

    # Prepare input arguments and initial filter parts for each media item
    for i, media_path in enumerate(media_file_paths):
        is_outro = (i == len(media_file_paths) - 1) # Assuming last file is always outro
        
        item_inputs, item_filter_part = _prepare_media_input(
            i, media_path, is_outro, slide_duration, fps, target_width, target_height
        )
        inputs.extend(item_inputs)
        if item_filter_part: # Only add if not empty (i.e., not skipped)
            filter_complex_parts.append(item_filter_part)
            
    # Build transition chain
    current_stream = "v0"
    for i in range(len(media_file_paths) - 1):
        next_stream = f"v{i+1}"
        output_stream_label = f"f{i}"
        
        transition_type = random.choice(config.get('transitions', ['hblur', 'smoothup', 'horzopen', 'circleopen', 'diagtr', 'diagbl']))
        transition_duration = config.get('transition_duration', 0.5) # seconds
        
        # Calculate offset for the transition
        # If current item is an image, its duration is slide_duration.
        # If it's a video, its actual duration should be used (this needs ffprobe if segments vary)
        # For now, assuming all non-outro segments effectively run for slide_duration in the slideshow context
        item_effective_duration = slide_duration
        if i == len(media_file_paths) - 2: # Transitioning to the outro
             # The item before the outro runs for its full slide_duration
            pass


        offset = (i + 1) * slide_duration - transition_duration 
        
        filter_part = f"[{current_stream}][{next_stream}]xfade=transition={transition_type}:duration={transition_duration}:offset={offset}[{output_stream_label}]"
        
        # Apply watermark if configured, enabled, and not the transition to the very last (outro) clip
        enable_watermark = config.get('enable_watermark', True) # Get enable_watermark setting
        if enable_watermark and watermark_config and (i < len(media_file_paths) - 2): # Don't watermark over the outro transition
            new_current_stream, watermark_filter_part = _apply_watermark_filter(
                output_stream_label, 
                watermark_config,
                watermark_font_size, # Pass new argument
                watermark_opacity,   # Pass new argument
                watermark_fontcolor  # Pass new argument
            )
            if watermark_filter_part:
                filter_part += watermark_filter_part
                current_stream = new_current_stream
            else:
                current_stream = output_stream_label
        else:
            current_stream = output_stream_label
            
        filter_complex_parts.append(filter_part)

    final_filter_complex = ";".join(filter_complex_parts)
    
    # Calculate total duration for -frames:v or -t
    # Number of image/video segments (excluding outro) * slide_duration + actual_outro_duration
    num_main_segments = len(media_file_paths) -1 
    # cfg.outro_duration should now hold the actual duration of the outro file (set in main.py)
    actual_outro_duration = config.get('outro_duration', 14) # Get the actual duration
    total_video_duration = (num_main_segments * slide_duration) + actual_outro_duration
    
    print(f"Slideshow Generator: num_main_segments={num_main_segments}, slide_duration={slide_duration}, actual_outro_duration={actual_outro_duration}, total_video_duration={total_video_duration}")


    ffmpeg_cmd.extend(inputs)
    ffmpeg_cmd.extend([
        '-filter_complex', final_filter_complex,
        '-map', f"[{current_stream}]", # Map the final chained stream
        '-pix_fmt', 'yuv420p',
        '-vcodec', 'libx264',
        '-crf', str(config.get('video_crf', 22)),
        '-preset', config.get('video_preset', 'medium'),
        '-r', str(fps),
        '-t', str(total_video_duration), # Use -t for total duration
        output_path
    ])

    print(f"Executing slideshow generation: {' '.join(ffmpeg_cmd)}")
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Base slideshow saved: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error generating base slideshow: {e}")
        print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")
        return None

def _apply_watermark_filter(
    stream_label: str, 
    watermark_config: dict,
    wm_font_size: int,
    wm_opacity: float,
    wm_fontcolor: str
) -> tuple[str, str]:
    """
    Generates the FFmpeg drawtext filter for watermarking.
    Returns (modified_stream_label, watermark_filter_part).
    """
    wm_text = watermark_config.get('text', '').replace("'", "\\\\'") # Escape single quotes for ffmpeg
    wm_type = watermark_config.get('type', 'random')
    wm_speed_frames = watermark_config.get('speed_frames', 50)
    wm_font_file = watermark_config.get('font_file_path', 'Arial.ttf') # Ensure this path is valid for ffmpeg
    
    # Determine font color expression
    fontcolor_expr = f"random@{wm_opacity}" if wm_fontcolor == "random" else f"{wm_fontcolor}@{wm_opacity}"
    
    watermark_drawtext = ""
    if wm_type == 'ccw':
        watermark_drawtext = (
            f"drawtext=text='{wm_text}':fontfile='{wm_font_file}':fontsize={wm_font_size}:fontcolor={fontcolor_expr}:"
            f"x='if(lt(mod(n/{wm_speed_frames},4),1),15+mod(n/{wm_speed_frames},1)*(w-text_w-30),if(lt(mod(n/{wm_speed_frames},4),2),w-text_w-15,if(lt(mod(n/{wm_speed_frames},4),3),w-text_w-15-(mod(n/{wm_speed_frames},1)*(w-text_w-30)),15)))':"
            f"y='if(lt(mod(n/{wm_speed_frames},4),1),15,if(lt(mod(n/{wm_speed_frames},4),2),15+mod(n/{wm_speed_frames},1)*(h-text_h-30),if(lt(mod(n/{wm_speed_frames},4),3),h-text_h-15,h-text_h-15-(mod(n/{wm_speed_frames},1)*(h-text_h-30)))))'"
        )
    elif wm_type == 'random':
        watermark_drawtext = (
            f"drawtext=text='{wm_text}':fontfile='{wm_font_file}':fontsize={wm_font_size}:fontcolor={fontcolor_expr}:"
            f"x='if(eq(mod(n\\,{wm_speed_frames})\\,0)\\,random(1)*w\\,x)':y='if(eq(mod(n\\,{wm_speed_frames})\\,0)\\,random(1)*h\\,y)'"
        )
    
    if watermark_drawtext:
        new_stream_label = f"{stream_label}w"
        watermark_filter_part = f";[{stream_label}]{watermark_drawtext}[{new_stream_label}]"
        return new_stream_label, watermark_filter_part
    return stream_label, "" # No watermark applied

if __name__ == "__main__":
    print("slideshow_generator.py executed directly (for testing).")
    # Example usage (requires actual media files and a config dict)
    # mock_media_files = ["path/to/image1.jpg", "path/to/video1.mp4", "path/to/outro.mp4"]
    # mock_config = {
    #     'slide_duration': 5,
    #     'video_orientation': 'vertical',
    #     'target_resolution': {'vertical_height': 1920, 'vertical_width': 1080},
    #     'fps': 25,
    #     'outro_duration': 10,
    #     'watermark': {
    #         'text': 'Test Watermark', 'type': 'random', 
    #         'speed_frames': 50, 'font_file_path': 'Arial.ttf', # Ensure Arial.ttf is accessible
    #         'font_size': 30, 'opacity': 0.7
    #     },
    #    'transitions': ['diagtl', 'circlecrop'],
    #    'transition_duration': 0.7,
    #    'video_crf': 23,
    #    'video_preset': 'fast'
    # }
    # if not os.path.exists("output"): os.makedirs("output")
    # generate_base_slideshow(mock_media_files, "output/test_slideshow_base.mp4", mock_config)
