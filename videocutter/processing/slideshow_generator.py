# videocutter/processing/slideshow_generator.py
# Handles creating the base video slideshow from media items with transitions.

import subprocess
import os
import random

# PIL Image is imported in the original slideshow.py but not directly used for manipulation
# in the core slideshow generation part. Keeping it commented for now.
# from PIL import Image 

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
    
    slide_duration = config.get('slide_duration', 5)
    video_orientation = config.get('video_orientation', 'vertical')
    
    if video_orientation == 'vertical':
        target_height = config.get('target_resolution', {}).get('vertical_height', 1920)
        target_width = config.get('target_resolution', {}).get('vertical_width', 1080)
    else: # horizontal
        target_height = config.get('target_resolution', {}).get('horizontal_height', 1080)
        target_width = config.get('target_resolution', {}).get('horizontal_width', 1920)

    fps = config.get('fps', 25)
    watermark_config = config.get('watermark')
    outro_duration = config.get('outro_duration', 14) # Duration of the actual outro clip

    ffmpeg_cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error']
    filter_complex_parts = []
    inputs = []

    # Prepare input arguments and initial filter parts for each media item
    for i, media_path in enumerate(media_file_paths):
        file_extension = os.path.splitext(media_path)[1].lower()
        is_outro = (i == len(media_file_paths) - 1) # Assuming last file is always outro

        if file_extension in ['.jpg', '.jpeg', '.png']:
            inputs.extend(['-loop', '1', '-t', str(slide_duration), '-framerate', str(fps)])
            inputs.extend(['-i', media_path])
            # Zoom-pan effect for images
            filter_complex_parts.append(
                f"[{i}:v]zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={fps*slide_duration}:s={target_width}x{target_height},format=yuv420p[v{i}]"
            )
        elif file_extension == '.mp4':
            inputs.extend(['-i', media_path])
            if is_outro:
                # Outro video might not need scaling if pre-rendered to target, but ensure PTS is reset
                filter_complex_parts.append(
                    f"[{i}:v]setpts=PTS-STARTPTS,fps={fps},setsar=1,scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[v{i}]"
                )
            else:
                # Scale video segments to target, reset PTS
                filter_complex_parts.append(
                    f"[{i}:v]setpts=PTS-STARTPTS,fps={fps},scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[v{i}]"
                )
        else:
            print(f"Skipping unsupported file type: {media_path}")
            continue
            
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
        
        # Apply watermark if configured and not the transition to the very last (outro) clip
        if watermark_config and (i < len(media_file_paths) - 2): # Don't watermark over the outro transition
            wm_text = watermark_config.get('text', '').replace("'", "\\\\'") # Escape single quotes for ffmpeg
            wm_type = watermark_config.get('type', 'random')
            wm_speed_frames = watermark_config.get('speed_frames', 50)
            wm_font_file = watermark_config.get('font_file_path', 'Arial.ttf') # Ensure this path is valid for ffmpeg
            wm_font_size = watermark_config.get('font_size', 40)
            wm_opacity = watermark_config.get('opacity', 0.7)
            
            # Ensure font path is absolute or discoverable by ffmpeg
            # This might need adjustment if font_utils.py is used to resolve paths first
            # For now, assuming wm_font_file is a path ffmpeg can use.
            
            watermark_drawtext = ""
            if wm_type == 'ccw':
                watermark_drawtext = (
                    f"drawtext=text='{wm_text}':fontfile='{wm_font_file}':fontsize={wm_font_size}:fontcolor_expr=random@{wm_opacity}:"
                    f"x='if(lt(mod(n/{wm_speed_frames},4),1),15+mod(n/{wm_speed_frames},1)*(w-text_w-30),if(lt(mod(n/{wm_speed_frames},4),2),w-text_w-15,if(lt(mod(n/{wm_speed_frames},4),3),w-text_w-15-(mod(n/{wm_speed_frames},1)*(w-text_w-30)),15)))':"
                    f"y='if(lt(mod(n/{wm_speed_frames},4),1),15,if(lt(mod(n/{wm_speed_frames},4),2),15+mod(n/{wm_speed_frames},1)*(h-text_h-30),if(lt(mod(n/{wm_speed_frames},4),3),h-text_h-15,h-text_h-15-(mod(n/{wm_speed_frames},1)*(h-text_h-30)))))'"
                )
            elif wm_type == 'random':
                watermark_drawtext = (
                    f"drawtext=text='{wm_text}':fontfile='{wm_font_file}':fontsize={wm_font_size}:fontcolor_expr=random@{wm_opacity}:"
                    f"x='if(eq(mod(n\\,{wm_speed_frames})\\,0)\\,random(1)*w\\,x)':y='if(eq(mod(n\\,{wm_speed_frames})\\,0)\\,random(1)*h\\,y)'"
                )
            
            if watermark_drawtext:
                filter_part += f";[{output_stream_label}]{watermark_drawtext}[{output_stream_label}w]"
                current_stream = f"{output_stream_label}w" # Continue with watermarked stream
            else:
                current_stream = output_stream_label
        else:
            current_stream = output_stream_label
            
        filter_complex_parts.append(filter_part)

    final_filter_complex = ";".join(filter_complex_parts)
    
    # Calculate total duration for -frames:v or -t
    # Number of image/video segments (excluding outro) * slide_duration + outro_duration
    num_main_segments = len(media_file_paths) -1 
    total_video_duration = (num_main_segments * slide_duration) + outro_duration
    # max_frames = int(total_video_duration * fps) # This can be an alternative to -t

    ffmpeg_cmd.extend(inputs)
    ffmpeg_cmd.extend([
        '-filter_complex', final_filter_complex,
        '-map', f"[{current_stream}]", # Map the final chained stream
        '-pix_fmt', 'yuv420p',
        # '-color_range', 'jpeg', # This might be problematic, often not needed for yuv420p
        '-vcodec', 'libx264',
        '-crf', str(config.get('video_crf', 22)),
        '-preset', config.get('video_preset', 'medium'),
        '-r', str(fps),
        '-t', str(total_video_duration), # Use -t for total duration
        # '-frames:v', str(max_frames), # Alternative to -t
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
