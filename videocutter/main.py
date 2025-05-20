# videocutter/main.py
# Main orchestrator for the VideoCutter pipeline.

import os
import shutil # For potential cleanup
from datetime import datetime

# Import a load_config function (assuming it's defined in config_manager.py)
from .config_manager import load_config 

# Import utility modules
from .utils import file_utils
from .utils import font_utils # Though font_utils might be used more by overlay_compositor

# Import processing modules
from .processing import video_processor
from .processing import depth_processor
from .processing import slideshow_generator
from .processing import audio_processor
from .processing import subtitle_generator
from .processing import overlay_compositor

def run_pipeline(config_path: str = None, gui_settings: dict = None):
    """
    Runs the full VideoCutter processing pipeline.

    Args:
        config_path (str, optional): Path to a JSON configuration file.
        gui_settings (dict, optional): Dictionary of settings from the GUI to override/supplement config file.
    """
    start_time_pipeline = datetime.now()
    print(f"VideoCutter Pipeline Started at: {start_time_pipeline.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Load Configuration
    # -------------------------------------------------------------------------
    cfg = load_config(config_path=config_path, initial_data=gui_settings)
    print("Configuration loaded successfully.")
    # print(f"Effective Config: {cfg}") # For debugging

    # 2. Setup Project Directories & Initial File Handling
    # -------------------------------------------------------------------------
    print("\n--- Phase 1: Initial Setup & File Preparation ---")
    # Ensure base input folder exists
    if not os.path.isdir(cfg.input_folder):
        print(f"Error: Base input folder '{cfg.input_folder}' does not exist. Aborting.")
        return

    # Setup standard subdirectories (RESULT, SOURCE/timestamp)
    # result_base_folder is INPUT/RESULT
    # run_source_backup_folder is INPUT/SOURCE/datetime_str
    # work_datetime_folder is INPUT/RESULT/datetime_str (where processing happens)
    result_base_folder, _, run_source_backup_folder, run_datetime_str = \
        file_utils.setup_project_directories(cfg.input_folder)
    
    # This will be the main working directory for this run's intermediate and final files
    work_datetime_folder = os.path.join(result_base_folder, run_datetime_str)
    os.makedirs(work_datetime_folder, exist_ok=True)
    print(f"Working directory for this run: {work_datetime_folder}")

    # Collect initial media files from cfg.input_folder (not result_base_folder)
    initial_media_files = []
    for ext_list in [['.mp4', '.mov', '.avi'], ['.jpg', '.jpeg', '.png'], ['.mp3']]: # Video, Image, Audio
        initial_media_files.extend(file_utils.find_files_by_extension(cfg.input_folder, ext_list))
    
    # Backup and move initial files to the working directory
    # This step needs careful thought: original scripts moved files.
    # We need to decide if we process in-place in input_folder then move, or move to work_dir then process.
    # Let's adopt: backup, then copy to work_dir, then process in work_dir.
    
    processed_raw_media_paths_in_work_dir = [] # Paths to files copied into work_datetime_folder

    for original_path in initial_media_files:
        if os.path.basename(original_path).lower() == 'voiceover.mp3': # Special handling for voiceover
            file_utils.backup_original_file(original_path, run_source_backup_folder)
            shutil.copy(original_path, os.path.join(work_datetime_folder, 'voiceover.mp3'))
            print(f"Copied voiceover.mp3 to {work_datetime_folder}")
            # Voiceover is not part of the visual slideshow items initially
            continue # Don't add to processed_raw_media_paths_in_work_dir yet

        file_utils.backup_original_file(original_path, run_source_backup_folder)
        
        # Copy to work_datetime_folder for processing
        filename = os.path.basename(original_path)
        path_in_work_dir = os.path.join(work_datetime_folder, filename)
        shutil.copy(original_path, path_in_work_dir)
        processed_raw_media_paths_in_work_dir.append(path_in_work_dir)
        
        # Remove from original input_folder after backup and copy
        try:
            os.remove(original_path)
            print(f"Removed original from input: {original_path}")
        except OSError as e:
            print(f"Error removing original file {original_path}: {e}")


    # 3. Initial Video & Image Processing (in work_datetime_folder)
    # -------------------------------------------------------------------------
    print("\n--- Phase 2: Initial Media Processing ---")
    # video_processor.process_raw_media was a placeholder. We need to call specific functions.
    
    # Process Videos (split, orientation)
    video_segments_for_slideshow = []
    images_for_slideshow = []

    temp_video_files_to_remove = [] # Store paths of intermediate full-length processed videos

    for media_path_in_work_dir in processed_raw_media_paths_in_work_dir:
        filename = os.path.basename(media_path_in_work_dir)
        if any(filename.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi']):
            print(f"Processing video: {media_path_in_work_dir}")
            
            # Handle orientation (e.g., vertical to horizontal with blur)
            # This function modifies in-place or creates a new file.
            # Let's assume it modifies in-place or we handle the output path.
            # For now, let's assume convert_to_horizontal_with_blur_bg saves to a new path if conversion happens
            
            converted_video_path = media_path_in_work_dir # Assume no conversion initially
            if cfg.video_orientation == 'horizontal': # Only convert if target is horizontal
                # convert_to_horizontal_with_blur_bg expects output_path.
                # Let's make it save with a suffix, then rename, or use the same path.
                # The current video_processor.convert_to_horizontal_with_blur_bg saves to output_path.
                # We need to ensure it doesn't overwrite before splitting if it's the same file.
                # Let's assume it processes and replaces media_path_in_work_dir if conversion occurs.
                
                # A safer pattern:
                temp_converted_path = os.path.join(work_datetime_folder, f"converted_{filename}")
                if video_processor.convert_to_horizontal_with_blur_bg(media_path_in_work_dir, temp_converted_path, cfg.get('target_resolution.horizontal_height', 1080)):
                    # If conversion happened, the original (media_path_in_work_dir) is now the converted one for splitting
                    # No, the function saves to temp_converted_path. So use that.
                    converted_video_path = temp_converted_path
                    # The original media_path_in_work_dir might be kept or removed depending on flow.
                    # For now, let's assume we use the converted_video_path for splitting.
                    # And we might want to remove the original media_path_in_work_dir if it was different.
                    if media_path_in_work_dir != converted_video_path:
                         temp_video_files_to_remove.append(media_path_in_work_dir) # Mark original for removal
                else: # No conversion happened or failed
                    if os.path.exists(temp_converted_path): os.remove(temp_converted_path) # cleanup if temp was made but failed

            # Split video
            segment_output_prefix = os.path.join(work_datetime_folder, os.path.splitext(filename)[0] + "_seg")
            video_processor.split_video_into_segments(converted_video_path, segment_output_prefix, cfg.segment_duration)
            
            # Collect new segment files (they end with %03d.mp4)
            # This requires listing directory, more robust than assuming names.
            # For now, assume segments are created and will be picked up by file_utils.find_files_by_extension later.
            # Or, split_video_into_segments could return a list of created segments.
            # Let's assume for now they are in work_datetime_folder.
            if converted_video_path != media_path_in_work_dir and os.path.exists(converted_video_path): # if temp_converted_path was used
                temp_video_files_to_remove.append(converted_video_path)


        elif any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            print(f"Processing image: {media_path_in_work_dir}")
            target_h = cfg.get('target_resolution.vertical_height', 1920) if cfg.video_orientation == 'vertical' else cfg.get('target_resolution.horizontal_height', 1080)
            video_processor.process_image_for_video(media_path_in_work_dir, target_h, cfg.video_orientation)
            images_for_slideshow.append(media_path_in_work_dir) # Add processed image path

    # Clean up intermediate full videos that were converted before splitting
    for f_path in temp_video_files_to_remove:
        if os.path.exists(f_path):
            os.remove(f_path)
            print(f"Removed intermediate processed video: {f_path}")

    # At this point, work_datetime_folder contains processed images and video segments.
    # Clean short video segments
    video_processor.clean_short_video_segments(work_datetime_folder, cfg.segment_duration - 0.5) # Allow slight variation

    # 4. Media List Preparation for Slideshow (after initial processing and cleaning)
    # -------------------------------------------------------------------------
    print("\n--- Phase 3: Preparing Media List for Slideshow ---")
    # Files are already in work_datetime_folder and named with original names (images) or _seg%03d.mp4 (videos)
    # The sorter.py logic (renaming to 001.ext, 002.ext) is applied *after* this initial processing
    # and *before* DepthFlow/Slideshow in the original flow.
    # Let's call the sorter logic now (which is in file_utils)
    # The sorter moves files from work_datetime_folder into work_datetime_folder/run_datetime_str_sorted
    # This seems redundant. Let's assume sorter renames IN PLACE in work_datetime_folder.
    # The original sorter.py created a subfolder named datetime_str *inside* the output_folder (which was result_folder).
    # So, if result_folder is INPUT/RESULT, sorter made INPUT/RESULT/datetime_str.
    # Our work_datetime_folder is already INPUT/RESULT/datetime_str.
    # So, the sorter should operate on work_datetime_folder and rename files within it.
    
    # The `organize_files_to_timestamped_folder` moves files. We need a version that renames in place
    # or we adjust the workflow. For now, let's assume we list files after cleaning.
    
    current_media_for_slideshow = file_utils.find_files_by_extension(
        work_datetime_folder, 
        ['.mp4', '.jpg', '.jpeg', '.png']
    )
    # Filter out voiceover.mp3 if it was copied there by mistake or for other reasons
    current_media_for_slideshow = [p for p in current_media_for_slideshow if os.path.basename(p).lower() != 'voiceover.mp3']
    
    # Limit media files by duration (from depth.py logic)
    # Note: original depth.py used (segment_duration - 1) as divisor.
    # This might be because transitions effectively shorten usable time.
    # Using cfg.slide_duration which defaults to segment_duration.
    effective_segment_duration_for_limit = cfg.slide_duration
    if cfg.get('depthflow.enabled', False) or len(cfg.transitions) > 0 : # If depthflow or transitions, account for potential shortening
         effective_segment_duration_for_limit = max(1, cfg.slide_duration -1) # Ensure at least 1

    kept_filenames_after_limit = file_utils.limit_media_files_by_duration(
        work_datetime_folder, 
        cfg.time_limit - cfg.outro_duration, # Time available before outro
        effective_segment_duration_for_limit 
    )
    # Update media list to only include kept files
    current_media_for_slideshow = [os.path.join(work_datetime_folder, fname) for fname in kept_filenames_after_limit]
    current_media_for_slideshow.sort() # Ensure sorted order for slideshow

    # 5. DepthFlow Processing (Conditional)
    # -------------------------------------------------------------------------
    if cfg.depthflow.enabled:
        print("\n--- Phase 4: DepthFlow Processing ---")
        images_to_depthflow = [p for p in current_media_for_slideshow if any(p.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])]
        videos_from_depthflow = depth_processor.apply_depth_effects(images_to_depthflow, cfg.toDict()) # Pass full config as dict
        
        # Replace original images with their depthflowed video counterparts in the list
        temp_media_list = [p for p in current_media_for_slideshow if not any(p.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])] # Keep existing videos
        temp_media_list.extend(videos_from_depthflow)
        current_media_for_slideshow = sorted(temp_media_list)
        
        # Delete original images that were processed by DepthFlow
        for img_path in images_to_depthflow:
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f"Removed original image after DepthFlow: {img_path}")
    
    # 6. Generate Base Slideshow (Video only, with transitions)
    # -------------------------------------------------------------------------
    print("\n--- Phase 5: Generating Base Slideshow ---")
    slideshow_base_path = os.path.join(work_datetime_folder, "slideshow_base.mp4")
    
    # Add outro video path to the list for slideshow generation
    # The slideshow_generator expects the full path to the outro.
    outro_template_name = 'outro_vertical.mp4' if cfg.video_orientation == 'vertical' else 'outro_horizontal.mp4'
    outro_video_full_path = os.path.join(cfg.template_folder, outro_template_name)
    
    if not os.path.exists(outro_video_full_path):
        print(f"Error: Outro template video not found at {outro_video_full_path}. Cannot generate slideshow.")
        return

    media_for_ffmpeg_slideshow = current_media_for_slideshow + [outro_video_full_path]

    slideshow_base_path = slideshow_generator.generate_base_slideshow(
        media_for_ffmpeg_slideshow, 
        slideshow_base_path, 
        cfg.toDict() # Pass full config
    )
    if not slideshow_base_path:
        print("Error: Base slideshow generation failed. Aborting.")
        return

    # 7. Generate Subtitles (Conditional)
    # -------------------------------------------------------------------------
    generated_srt_path = None
    if cfg.subtitles.enabled and os.path.exists(os.path.join(work_datetime_folder, 'voiceover.mp3')):
        print("\n--- Phase 6: Generating Subtitles ---")
        srt_output_target_path = os.path.join(work_datetime_folder, "subs", "voiceover.srt")
        # Ensure subs directory exists
        os.makedirs(os.path.join(work_datetime_folder, "subs"), exist_ok=True)
        
        generated_srt_path = subtitle_generator.generate_srt_from_audio_file(
            os.path.join(work_datetime_folder, 'voiceover.mp3'),
            srt_output_target_path,
            cfg.toDict() # Pass full config
        )
        if generated_srt_path:
            print(f"Subtitles generated: {generated_srt_path}")
        else:
            print("Subtitle generation failed or was skipped.")
    elif cfg.subtitles.enabled:
        print("Subtitle generation enabled in config, but voiceover.mp3 not found in working directory. Skipping SRT generation.")


    # 8. Audio Processing
    # -------------------------------------------------------------------------
    print("\n--- Phase 7: Audio Processing ---")
    video_with_audio_path = os.path.join(work_datetime_folder, "slideshow_with_audio.mp4")
    video_with_audio_path = audio_processor.process_audio(
        slideshow_base_path, 
        video_with_audio_path, 
        cfg.toDict(), # Pass full config
        work_datetime_folder # For voiceover.mp3 and intermediate files
    )
    if not video_with_audio_path:
        print("Error: Audio processing failed. Aborting.")
        return

    # 9. Final Overlay Composition (Title, Subscribe, Effects, Rendered Subtitles)
    # -------------------------------------------------------------------------
    print("\n--- Phase 8: Final Overlay Composition ---")
    final_output_video_name = f"{cfg.title.replace(' ', '_')}_{run_datetime_str}.mp4"
    final_output_video_path = os.path.join(work_datetime_folder, final_output_video_name)
    
    final_video_actual_path = overlay_compositor.apply_final_overlays(
        video_with_audio_path,
        final_output_video_path,
        cfg.toDict(), # Pass full config
        work_datetime_folder, # For resolving srt_file path if needed by compositor
        generated_srt_path if cfg.subtitles.enabled else None
    )

    if not final_video_actual_path:
        print("Error: Final overlay composition failed.")
        return

    # 10. Cleanup (Optional: remove intermediate files like slideshow_base.mp4, slideshow_with_audio.mp4 if different from final)
    # -------------------------------------------------------------------------
    print("\n--- Phase 9: Cleanup ---")
    if slideshow_base_path != final_video_actual_path and os.path.exists(slideshow_base_path):
        os.remove(slideshow_base_path)
        print(f"Cleaned up: {slideshow_base_path}")
    if video_with_audio_path != final_video_actual_path and os.path.exists(video_with_audio_path):
        os.remove(video_with_audio_path)
        print(f"Cleaned up: {video_with_audio_path}")
    
    # Remove original processed segments/images from work_datetime_folder if they are not the final output
    # This needs careful handling to not delete the final video or essential logs.
    # For now, we'll leave the contents of work_datetime_folder as is, besides the final video.

    end_time_pipeline = datetime.now()
    print(f"\nVideoCutter Pipeline Finished at: {end_time_pipeline.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total processing time: {end_time_pipeline - start_time_pipeline}")
    print(f"Final video output: {final_video_actual_path}")


if __name__ == "__main__":
    print("VideoCutter main orchestrator starting (direct execution)...")
    # Example: Run with default config if it exists
    # This assumes 'config/default_config.json' is in the parent directory of 'videocutter' package
    project_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_cfg_path = os.path.join(project_root_dir, "config", "default_config.json")
    
    if os.path.exists(default_cfg_path):
        # For testing, you might want to copy some files into an 'INPUT_test_main' folder
        # and pass that as part of gui_settings to override 'input_folder'
        # test_input_dir = "INPUT_test_main"
        # os.makedirs(test_input_dir, exist_ok=True)
        # # Copy some test media into test_input_dir
        # # ... 
        # test_gui_settings = {"input_folder": test_input_dir, "title": "Main Test Run"}
        # run_pipeline(config_path=default_cfg_path, gui_settings=test_gui_settings)
        
        # For a simple run with existing INPUT folder:
        run_pipeline(config_path=default_cfg_path)
    else:
        print(f"Default config not found at {default_cfg_path}. Cannot run test pipeline.")
    
    print("VideoCutter main orchestrator finished (direct execution).")
