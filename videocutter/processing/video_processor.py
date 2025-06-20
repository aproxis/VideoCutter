# videocutter/processing/video_processor.py
# Handles initial video and image processing tasks.

import os
import shutil
import subprocess
import json
from PIL import Image, ImageFilter, ImageDraw

# --- Video Utilities ---

import logging
logger = logging.getLogger(__name__)

def get_video_metadata(video_path: str) -> dict | None:
    """Gets video metadata (width, height, duration) using ffprobe, focusing on stream data."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0", # Explicitly select the first video stream
            "-show_entries", "stream=width,height,duration,r_frame_rate,avg_frame_rate", # Get duration from stream
            "-of", "json", video_path
        ]
        # logger.debug(f"Executing ffprobe for metadata: {' '.join(cmd)}") # For debugging
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"ffprobe for {video_path} failed with exit code {result.returncode}")
            logger.error(f"ffprobe stderr: {result.stderr}")
            return None
        
        if not result.stdout:
            logger.error(f"ffprobe for {video_path} produced no output.")
            return None
            
        metadata = json.loads(result.stdout)
        
        if not metadata.get("streams") or not metadata["streams"][0]:
            logger.error(f"No video stream data found in ffprobe JSON output for {video_path}")
            # Fallback: try to get format duration if stream duration is missing
            cmd_format_duration = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json", video_path
            ]
            result_format = subprocess.run(cmd_format_duration, capture_output=True, text=True, check=False)
            if result_format.returncode == 0 and result_format.stdout:
                format_meta = json.loads(result_format.stdout)
                if format_meta.get("format", {}).get("duration"):
                     logger.info(f"Using format duration for {video_path} as stream duration was not found.")
                     # We don't have width/height here, so this is only partial.
                     # This function primarily needs width/height for video processing.
                     # For now, if stream info is missing, we can't proceed with width/height dependent ops.
                     # Let's return at least duration if found this way.
                     # However, the caller (convert_to_horizontal_with_blur_bg) needs width/height.
                     # So, if primary stream info fails, it's better to return None or incomplete.
                     # For now, let's stick to requiring stream info for width/height.
                     return {"duration": float(format_meta["format"]["duration"])} # No width/height
            return None

        video_stream_data = metadata["streams"][0]
        
        duration_str = video_stream_data.get("duration")
        if duration_str is None: # Duration might be in format section for some containers
            duration_str = metadata.get("format", {}).get("duration", "0")

        # Frame rate can be 'num/den' or a float string
        r_frame_rate_str = video_stream_data.get("r_frame_rate", "0/1")
        avg_frame_rate_str = video_stream_data.get("avg_frame_rate", "0/1")
        
        def parse_frame_rate(fr_str):
            if "/" in fr_str:
                num, den = map(float, fr_str.split('/'))
                return num / den if den else 0
            return float(fr_str)

        r_frame_rate = parse_frame_rate(r_frame_rate_str)
        avg_frame_rate = parse_frame_rate(avg_frame_rate_str)

        return {
            "width": int(video_stream_data.get("width", 0)),
            "height": int(video_stream_data.get("height", 0)),
            "duration": float(duration_str),
            "r_frame_rate": r_frame_rate,
            "avg_frame_rate": avg_frame_rate
        }
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from ffprobe output for {video_path}. Output: {result.stdout}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting metadata for {video_path}: {e}")
    return None

def get_video_duration(video_path: str) -> float | None:
    """Get the duration of the video in seconds using ffprobe, preferring stream duration."""
    metadata = get_video_metadata(video_path)
    return metadata["duration"] if metadata else None

def split_video_into_segments(input_file: str, output_prefix: str, segment_duration: int):
    """Splits a video into segments of specified duration using FFmpeg."""
    try:
        # Note: Original command from cutter.py used -an to remove audio.
        # This might be desired if audio is handled entirely separately later.
        cmd = (
            f"ffmpeg -hide_banner -loglevel error -i \"{input_file}\" "
            f"-c:v libx264 -crf 22 -g 30 -r 30 -an " 
            f"-map 0 -segment_time {segment_duration} -g {segment_duration} "
            f"-sc_threshold 0 -force_key_frames expr:gte\(t,n_forced*{segment_duration}\) "
            f"-f segment -reset_timestamps 1 \"{output_prefix}%03d.mp4\""  # Using %03d for 3-digit padding
        )
        logger.debug(f"Executing split: {cmd}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, b''):
            logger.debug(line.decode().strip())
        process.wait()
        if process.returncode != 0:
            raise Exception(f"FFmpeg split failed for {input_file} with exit code {process.returncode}")
        logger.info(f"Successfully split {input_file} into segments with prefix {output_prefix}")
    except Exception as e:
        logger.error(f"Failed to split video {input_file}: {e}")

def convert_to_horizontal_with_blur_bg(input_path: str, output_path: str, target_output_height: int = 1080, apply_blur: bool = True):
    """
    Converts a vertical video to a horizontal 16:9 format.
    If apply_blur is True, it adds a blurred background of the video itself.
    If apply_blur is False, it scales the video to fit and pads with black.
    """
    metadata = get_video_metadata(input_path)
    if not metadata or not metadata.get("width") or not metadata.get("height"):
        logger.warning(f"Could not get dimensions for {input_path}. Skipping conversion.")
        return False

    original_width = metadata["width"]
    original_height = metadata["height"]

    if not original_width or not original_height:
        logger.warning(f"Invalid dimensions from metadata for {input_path}. Skipping conversion.")
        return False

    if original_height <= original_width:
        logger.info(f"{input_path} is not a vertical video. Skipping conversion to horizontal.")
        if input_path != output_path:
            try:
                shutil.copy(input_path, output_path)
                logger.info(f"Copied {input_path} to {output_path} as no conversion needed.")
            except Exception as e:
                logger.error(f"Error copying {input_path} to {output_path}: {e}")
                return False
        return False

    target_output_width = target_output_height * 16 // 9
    scaled_fg_width = int(original_width * target_output_height / original_height)
    scaled_fg_height = target_output_height
    
    filter_complex_parts = []
    filter_complex_parts.append(f"[0:v]scale={scaled_fg_width}:{scaled_fg_height}[fg]")

    if apply_blur:
        logger.info(f"Processing vertical video {input_path} to horizontal format with blur.")
        filter_complex_parts.insert(0, f"[0:v]scale={target_output_width}:{target_output_height},boxblur=20:5[bg]")
        filter_complex_parts.append(f"[bg][fg]overlay=(W-w)/2:(H-h)/2:format=auto[outv]")
    else:
        logger.info(f"Processing vertical video {input_path} to horizontal format with black padding.")
        # Pad the 'fg' stream directly
        filter_complex_parts.append(f"[fg]pad={target_output_width}:{target_output_height}:(ow-iw)/2:(oh-ih)/2:color=black[outv]")

    final_filter_complex = ";".join(filter_complex_parts)
    
    temp_output = os.path.join(os.path.dirname(output_path), "temp_conversion_" + os.path.basename(output_path))
    
    ffmpeg_cmd_parts = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", input_path,
        "-filter_complex", final_filter_complex,
        "-map", "[outv]", "-c:v", "libx264", "-crf", "22", "-preset", "medium",
        "-r", "30", "-an", temp_output
    ]
    logger.debug(f"Executing conversion: {' '.join(ffmpeg_cmd_parts)}")
    try:
        subprocess.run(ffmpeg_cmd_parts, shell=False, check=True)
        shutil.move(temp_output, output_path)
        logger.info(f"Successfully converted {input_path} to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting {input_path}: {e}")
        if os.path.exists(temp_output):
            os.remove(temp_output)
    except Exception as e:
        logger.error(f"An unexpected error occurred during conversion of {input_path}: {e}")
        if os.path.exists(temp_output):
            os.remove(temp_output)
    return False

# --- Image Utilities ---

def process_image_for_video(image_path: str, target_final_height: int, target_video_orientation: str, apply_blur: bool):
    """
    Processes an image to fit the target video orientation and dimensions,
    applying blur and gradient effects as needed if apply_blur is True.
    The processed image overwrites the original image_path.
    """
    try:
        original_image = Image.open(image_path)
        original_width, original_height = original_image.size
        logger.info(f"Processing image: {image_path} ({original_width}x{original_height}) for {target_video_orientation} output ({target_final_height}p), Blur: {apply_blur}")

        is_vertical_image = original_height > original_width
        final_image = None

        if target_video_orientation == 'vertical': # Target is 9:16
            target_final_width = target_final_height * 9 // 16
            
            if is_vertical_image: 
                scaled_to_width = original_image.resize(
                    (target_final_width, int(original_height * target_final_width / original_width)), 
                    Image.Resampling.LANCZOS
                )
                if scaled_to_width.height >= target_final_height: 
                    top = (scaled_to_width.height - target_final_height) // 2
                    final_image = scaled_to_width.crop((0, top, target_final_width, top + target_final_height))
                elif apply_blur: # Vertical image for vertical video, smaller height (letterbox with blur and gradients)
                    bg = original_image.resize((target_final_width, target_final_height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=20))
                    fg_w, fg_h = scaled_to_width.size
                    
                    # Add top and bottom gradients (letterbox effect)
                    border_fraction = int(fg_h * 0.1) # Fade 10% of the image height from top and bottom
                    gradient = Image.new('L', (fg_w, fg_h), color=255)
                    draw = ImageDraw.Draw(gradient)
                    for y_coord in range(border_fraction):
                        alpha = int(255 * (y_coord / border_fraction))
                        draw.line([(0, y_coord), (fg_w - 1, y_coord)], fill=alpha)  # Top fade
                        draw.line([(0, fg_h - 1 - y_coord), (fg_w - 1, fg_h - 1 - y_coord)], fill=alpha)  # Bottom fade
                    
                    scaled_to_width.putalpha(gradient)
                    x_offset = (target_final_width - fg_w) // 2 # Center horizontally
                    y_offset = (target_final_height - fg_h) // 2 
                    bg.paste(scaled_to_width, (x_offset, y_offset), mask=scaled_to_width)
                    final_image = bg
                else: # No blur, just scale and pad with black (or center)
                    final_image = Image.new('RGB', (target_final_width, target_final_height), (0,0,0))
                    y_offset = (target_final_height - scaled_to_width.height) // 2
                    final_image.paste(scaled_to_width, (0, y_offset))

            else: # Horizontal image for vertical video
                scaled_to_height = original_image.resize(
                    (int(original_width * target_final_height / original_height), target_final_height),
                    Image.Resampling.LANCZOS
                )
                if apply_blur: # Horizontal image for vertical video (pillarbox with blur)
                    bg = original_image.resize((target_final_width, target_final_height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=20))
                    fg_w, fg_h = scaled_to_height.size
                    # CORRECTED: Gradient on TOP and BOTTOM for pillarbox
                    border_fraction = int(fg_h * 0.1) 
                    gradient = Image.new('L', (fg_w, fg_h), color=255)
                    draw = ImageDraw.Draw(gradient)
                    for y_coord in range(border_fraction):
                        alpha = int(255 * (y_coord / border_fraction))
                        draw.line([(0, y_coord), (fg_w - 1, y_coord)], fill=alpha)  # Top fade
                        draw.line([(0, fg_h - 1 - y_coord), (fg_w - 1, fg_h - 1 - y_coord)], fill=alpha)  # Bottom fade
                    scaled_to_height.putalpha(gradient)
                    x_offset = (target_final_width - fg_w) // 2
                    y_offset = (target_final_height - fg_h) // 2 # Center vertically too
                    bg.paste(scaled_to_height, (x_offset, y_offset), mask=scaled_to_height)
                    final_image = bg
                else: # No blur, just scale and pad with black (or center)
                    final_image = Image.new('RGB', (target_final_width, target_final_height), (0,0,0))
                    x_offset = (target_final_width - scaled_to_height.width) // 2
                    final_image.paste(scaled_to_height, (x_offset, 0))


        elif target_video_orientation == 'horizontal': # Target is 16:9
            target_final_width = target_final_height * 16 // 9

            if not is_vertical_image: 
                scaled_to_height = original_image.resize(
                    (int(original_width * target_final_height / original_height), target_final_height),
                    Image.Resampling.LANCZOS
                )
                if scaled_to_height.width >= target_final_width: 
                    left = (scaled_to_height.width - target_final_width) // 2
                    final_image = scaled_to_height.crop((left, 0, left + target_final_width, target_final_height))
                elif apply_blur: # Horizontal image for horizontal video, smaller width (pillarbox with blur and gradients)
                    bg = original_image.resize((target_final_width, target_final_height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=20))
                    fg_w, fg_h = scaled_to_height.size
                    
                    # Add side gradients (pillarbox effect)
                    border_fraction = int(fg_w * 0.1) # Fade 10% of the image width from left and right
                    gradient = Image.new('L', (fg_w, fg_h), color=255) 
                    draw = ImageDraw.Draw(gradient)
                    for x_coord in range(border_fraction):
                        alpha = int(255 * (x_coord / border_fraction))
                        draw.line([(x_coord, 0), (x_coord, fg_h - 1)], fill=alpha)  # Left fade
                        draw.line([(fg_w - 1 - x_coord, 0), (fg_w - 1 - x_coord, fg_h - 1)], fill=alpha)  # Right fade
                    
                    scaled_to_height.putalpha(gradient)
                    x_offset = (target_final_width - fg_w) // 2 
                    y_offset = (target_final_height - fg_h) // 2 # Center vertically
                    bg.paste(scaled_to_height, (x_offset, y_offset), mask=scaled_to_height)
                    final_image = bg
                else: # No blur, just scale and pad with black (or center)
                    final_image = Image.new('RGB', (target_final_width, target_final_height), (0,0,0))
                    x_offset = (target_final_width - scaled_to_height.width) // 2
                    final_image.paste(scaled_to_height, (x_offset, 0))
            else: # Vertical image for horizontal video
                scaled_to_width = original_image.resize( # This was scaled_to_width in original, but logic implies scaling to fit width of horizontal frame
                    (target_final_width, int(original_height * target_final_width / original_width)), # This seems wrong, should be scaled to fit height first
                    Image.Resampling.LANCZOS
                )
                # Corrected logic for vertical image in horizontal frame:
                # Scale to fit height of horizontal frame first
                scaled_to_fit_height = original_image.resize(
                    (int(original_width * target_final_height / original_height), target_final_height),
                    Image.Resampling.LANCZOS
                )
                if apply_blur: # Vertical image in horizontal frame (letterbox with blur)
                    bg = original_image.resize((target_final_width, target_final_height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=20))
                    fg_w, fg_h = scaled_to_fit_height.size 
                    
                    # CORRECTED: Gradient should be on LEFT and RIGHT for a vertical image being letterboxed
                    border_fraction = int(fg_w * 0.1) # Fade 10% of the image width from left and right
                    gradient = Image.new('L', (fg_w, fg_h), color=255) 
                    draw = ImageDraw.Draw(gradient)
                    for x_coord in range(border_fraction):
                        alpha = int(255 * (x_coord / border_fraction))
                        draw.line([(x_coord, 0), (x_coord, fg_h - 1)], fill=alpha)  # Left fade
                        draw.line([(fg_w - 1 - x_coord, 0), (fg_w - 1 - x_coord, fg_h - 1)], fill=alpha)  # Right fade
                    
                    scaled_to_fit_height.putalpha(gradient)
                    x_offset = (target_final_width - fg_w) // 2 
                    y_offset = (target_final_height - fg_h) // 2 # Center vertically
                    bg.paste(scaled_to_fit_height, (x_offset, y_offset), mask=scaled_to_fit_height)
                    final_image = bg
                else: # No blur, just scale and pad with black (or center)
                    final_image = Image.new('RGB', (target_final_width, target_final_height), (0,0,0))
                    x_offset = (target_final_width - scaled_to_fit_height.width) // 2
                    final_image.paste(scaled_to_fit_height, (x_offset, 0))
        else:
            logger.error(f"Unsupported target_video_orientation: {target_video_orientation}")
            return

        if final_image:
            final_image.save(image_path)
            logger.info(f"Processed and saved image: {image_path}")
        else:
            logger.warning(f"Image processing resulted in no final image for {image_path}")


    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")


# --- Main processing loop (example, to be called by orchestrator) ---

def process_initial_media(config, input_files_list, work_folder):
    """
    Processes a list of raw media files (videos and images).
    - Backs up originals.
    - Processes videos (orientation, splitting).
    - Processes images.
    - Removes original files from the initial input location after processing and backup.
    - Returns a list of paths to processed segment files in the work_folder.
    """
    # This function will be more elaborate, using the config object
    # For now, this is a conceptual placeholder.
    
    # Example:
    # for file_path in input_files_list:
    #     backup_original_file(file_path, config.run_specific_source_folder)
    #     if file_is_video(file_path):
    #         # handle video: convert_to_horizontal_with_blur_bg if needed, then split_video_into_segments
    #         # add segment paths to a list
    #     elif file_is_image(file_path):
    #         # copy to work_folder, then process_image_for_video
    #         # add processed image path to a list
    #     os.remove(file_path) # remove original from input after backup and processing
    pass

def clean_short_video_segments(directory_to_clean: str, min_duration_seconds: float, video_extensions: list[str] = None, is_dry_run: bool = False):
    """
    Deletes video files in a directory that are shorter than a specified minimum duration.
    Optionally, can remove the parent directory if it becomes empty after deletions.
    (Directory removal logic from original cleaner.py was based on os.access, which is not
    a reliable check for emptiness; this version omits that specific directory removal logic
    for simplicity, focusing on file deletion. Directory cleanup can be handled separately if needed.)

    Args:
        directory_to_clean (str): The directory to scan for video files.
        min_duration_seconds (float): Minimum duration for a video to be kept.
        video_extensions (list[str], optional): List of video extensions. Defaults to ['.mp4'].
        is_dry_run (bool, optional): If True, only print actions. Defaults to False.
    """
    if video_extensions is None:
        video_extensions = ['.mp4']

    # We need find_files_by_extension from file_utils.
    # This creates a temporary circular dependency if called directly from here during module loading.
    # For a cleaner design, file_utils should not import from processing modules.
    # Assuming find_files_by_extension will be available in the calling scope or imported carefully.
    # For now, we'll assume it's accessible. A better approach might be to pass it as an argument
    # or have the main orchestrator provide the list of files.
    # To make this self-contained for now, let's temporarily redefine a local version
    # or expect it to be imported from videocutter.utils import file_utils.
    
    # For direct execution/testing, this import is fine.
    # In the final refactored system, the orchestrator would likely get the file list.
    from videocutter.utils.file_utils import find_files_by_extension

    logger.info(f"Cleaning short videos in: {directory_to_clean}, min duration: {min_duration_seconds}s")
    
    video_files_to_check = find_files_by_extension(directory_to_clean, video_extensions)
    files_to_delete = set()

    for video_file_path in video_files_to_check:
        duration = get_video_duration(video_file_path) # Already in this module
        if duration is not None and duration < min_duration_seconds:
            files_to_delete.add(video_file_path)
            if is_dry_run:
                logger.info(f"[Dry Run] Would delete: {video_file_path} (Duration: {duration:.2f}s)")
        elif duration is None:
            logger.warning(f"Could not determine duration for {video_file_path}. Skipping.")

    if not files_to_delete:
        logger.info("No video files found shorter than the minimum duration.")
        return

    if is_dry_run:
        logger.info(f"\n[Dry Run] Total files that would be deleted: {len(files_to_delete)}")
    else:
        logger.info(f"\nDeleting {len(files_to_delete)} video files shorter than {min_duration_seconds}s...")
        for file_path in sorted(list(files_to_delete)):
            try:
                os.unlink(file_path)
                logger.info(f"Deleted: {file_path}")
                # Original cleaner.py had logic to remove parent dir if empty.
                # This can be complex and risky (e.g. if dir is not exclusively for these segments).
                # Omitting that part for now. Parent directory cleanup can be a separate step if needed.
                # parent_dir = os.path.dirname(file_path)
                # if not os.listdir(parent_dir): # Check if directory is empty
                #     try:
                #         os.rmdir(parent_dir)
                #         logger.error(f"Removed empty directory: {parent_dir}") # Changed to logger.error for consistency
                #     except OSError as e:
                #         logger.error(f"Error removing directory {parent_dir}: {e}")
            except OSError as e:
                logger.error(f"Error deleting file {file_path}: {e}")
        logger.info("Deletion complete.")


if __name__ == "__main__":
    logger.info("video_processor.py executed directly (for testing).")
    logger.info("video_processor.py executed directly (for testing).")
    
    # Setup a test directory for clean_short_video_segments
    test_clean_dir = "temp_clean_test_dir"
    if not os.path.exists(test_clean_dir):
        os.makedirs(test_clean_dir)

    # Create dummy video files for testing (need actual mp4s for duration check)
    # For simplicity, we'll just test the dry run path without real ffprobe calls here
    # as creating valid short/long mp4s programmatically is complex.
    # Assume get_video_duration and find_files_by_extension are tested elsewhere or mocked.
    
    # To truly test, you'd copy some short and long mp4s into test_clean_dir
    # For now, let's simulate by creating empty files and assuming get_video_duration works
    dummy_short_vid = os.path.join(test_clean_dir, "short_vid.mp4")
    dummy_long_vid = os.path.join(test_clean_dir, "long_vid.mp4")
    with open(dummy_short_vid, "w") as f: f.write("dummy")
    with open(dummy_long_vid, "w") as f: f.write("dummy")

    logger.info(f"\n--- Testing clean_short_video_segments (Dry Run) ---")
    # Mocking get_video_duration for this test block
    original_get_video_duration = get_video_duration
    def mock_get_video_duration(file_path):
        if "short_vid.mp4" in file_path: return 2.0
        if "long_vid.mp4" in file_path: return 10.0
        return None
    
    # global get_video_duration # This is not how you rebind in Python
    # get_video_duration = mock_get_video_duration # This rebinds the local name, not the module's
    # Instead, we'd typically use unittest.mock.patch for proper mocking in tests.
    # For this simple __main__, we'll rely on the print statements.
    # The test below will use the actual get_video_duration which will fail on dummy files.
    # A more robust test would involve creating actual short video files.

    # The following call will likely print errors for get_video_duration because files are not real videos
    # but it will demonstrate the dry_run logic flow.
    clean_short_video_segments(test_clean_dir, min_duration_seconds=5.0, is_dry_run=True)

    # logger.info(f"\n--- Testing clean_short_video_segments (Actual Deletion) ---")
    # logger.info("Note: This would delete files if get_video_duration could parse them.")
    # clean_short_video_segments(test_clean_dir, min_duration_seconds=5.0, is_dry_run=False)
    
    # Restore original function if it was truly patched (not done effectively here)
    # get_video_duration = original_get_video_duration

    # Clean up
    if os.path.exists(dummy_short_vid): os.remove(dummy_short_vid)
    if os.path.exists(dummy_long_vid): os.remove(dummy_long_vid)
    if os.path.exists(test_clean_dir): os.rmdir(test_clean_dir)
    
    logger.info("\nVideo_processor.py testing finished.")
