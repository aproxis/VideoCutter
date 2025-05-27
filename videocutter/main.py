# videocutter/main.py
# Main orchestrator for the VideoCutter pipeline.

import os
import shutil # For potential cleanup
from datetime import datetime
from dotmap import DotMap # Import DotMap for type hinting
import json

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

# Renamed original run_pipeline to specify it's for a single project
def run_pipeline_for_project(project_name: str, project_input_folder: str, cfg: DotMap):
    """
    Runs the full VideoCutter processing pipeline for a single project.

    Args:
        project_name (str): Name of the project (e.g., subfolder name).
        project_input_folder (str): Path to the specific project's input files.
        cfg (DotMap): The fully resolved configuration object for this project.
    """
    start_time_project = datetime.now()
    print(f"\n{'='*20} Starting Project: {project_name} at {start_time_project.strftime('%Y-%m-%d %H:%M:%S')} {'='*20}")
    print(f"Using Input Folder: {project_input_folder}")
    # print(f"Effective Config for {project_name}: {cfg}") # For debugging

    # Define a temporary directory within the project root for intermediate files
    project_root_dir = os.path.dirname(os.path.abspath(__file__)) # videocutter/
    project_root_dir = os.path.dirname(project_root_dir) # One level up to VideoCutter/
    temp_dir = os.path.join(project_root_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True) # Ensure temp directory exists

    # 2. Setup Project-Specific Directories & Initial File Handling
    # Directories (RESULT, SOURCE/timestamp) are now created *inside* the project_input_folder
    # The `base_input_folder` for setup_project_directories is now the project_input_folder itself.
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 1: Initial Setup & File Preparation ---")
    
    # result_base_folder becomes project_input_folder/RESULT
    # run_source_backup_folder becomes project_input_folder/SOURCE/datetime_str
    # work_datetime_folder becomes project_input_folder/RESULT/datetime_str
    result_in_project_folder, _, run_source_backup_folder, run_datetime_str = \
        file_utils.setup_project_directories(project_input_folder) 
        # setup_project_directories creates RESULT and SOURCE/datetime inside project_input_folder
    
    work_datetime_folder = os.path.join(result_in_project_folder, run_datetime_str)
    # This was created by setup_project_directories if result_in_project_folder was its output
    # Let's adjust setup_project_directories to return the work_datetime_folder directly or ensure it's clear.
    # For now, assuming work_datetime_folder is correctly project_input_folder/RESULT/datetime_str
    # The current file_utils.setup_project_directories returns:
    # result_folder (e.g. project_input_folder/RESULT)
    # source_folder (e.g. project_input_folder/SOURCE)
    # run_specific_source_folder (e.g. project_input_folder/SOURCE/datetime_str)
    # datetime_str
    # So, work_datetime_folder needs to be constructed:
    work_datetime_folder = os.path.join(result_in_project_folder, run_datetime_str) # This is correct.
    os.makedirs(work_datetime_folder, exist_ok=True) # Ensure this specific folder is created

    print(f"Working directory for {project_name}: {work_datetime_folder}")

    # Collect initial media files from project_input_folder (top level of it)
    initial_media_files = []
    for ext_list in [['.mp4', '.mov', '.avi'], ['.jpg', '.jpeg', '.png'], ['.mp3'], ['.txt']]: # Added .txt
        initial_media_files.extend(file_utils.find_files_by_extension(project_input_folder, ext_list))
    
    # Collect initial media files from project_input_folder (top level of it)
    # and copy them to the work_datetime_folder for processing.
    # The file_utils.organize_files_to_timestamped_folder will handle renaming.
    
    # First, find all relevant files in the project_input_folder
    all_files_in_input = []
    for ext_list in [['.mp4', '.mov', '.avi'], ['.jpg', '.jpeg', '.png'], ['.mp3'], ['.txt']]:
        all_files_in_input.extend(file_utils.find_files_by_extension(project_input_folder, ext_list))
    
    # Filter out files that are already in RESULT or SOURCE subdirs of the project folder
    # and the project config file itself.
    files_to_process_and_move = []
    for original_path in all_files_in_input:
        filename = os.path.basename(original_path)
        if os.path.dirname(original_path).endswith(os.path.sep + "RESULT") or \
           os.path.dirname(original_path).endswith(os.path.sep + "SOURCE") or \
           filename.lower() == cfg.get('project_specific_config_filename', '_project_config.json'):
            continue
        files_to_process_and_move.append(original_path)

    # Copy files to a temporary staging area within work_datetime_folder
    # before calling organize_files_to_timestamped_folder
    staging_dir = os.path.join(work_datetime_folder, "staging")
    os.makedirs(staging_dir, exist_ok=True)

    for original_path in files_to_process_and_move:
        filename = os.path.basename(original_path)
        destination_path = os.path.join(staging_dir, filename)
        
        file_utils.backup_original_file(original_path, run_source_backup_folder)
        shutil.copy(original_path, destination_path)
        print(f"Copied '{original_path}' to staging area '{destination_path}'")
        
        # Remove from original project_input_folder (top-level) after backup and copy
        try:
            if os.path.dirname(original_path) == project_input_folder: # Only remove if it's at the root of project folder
                os.remove(original_path)
                print(f"Removed original from {project_input_folder}: {original_path}")
        except OSError as e:
            print(f"Error removing original file {original_path} from {project_input_folder}: {e}")

    # Now, organize and rename files from the staging directory into the work_datetime_folder
    # This will apply the renaming rules (001.jpg, voiceover.mp3, original_text.txt etc.)
    file_utils.organize_files_to_timestamped_folder(staging_dir, "") # Pass empty string for datetime_string as it's already a timestamped folder
    
    # Move the renamed files from staging_dir to work_datetime_folder
    for filename in os.listdir(staging_dir):
        shutil.move(os.path.join(staging_dir, filename), os.path.join(work_datetime_folder, filename))
    
    # Clean up the staging directory
    shutil.rmtree(staging_dir)
    print(f"Cleaned up staging directory: {staging_dir}")

    # 3. Initial Video & Image Processing (in work_datetime_folder for the current project)
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 2: Initial Media Processing ---")
    
    temp_video_files_to_remove = [] 

    # Re-scan work_datetime_folder for files after organization
    processed_raw_media_paths_in_work_dir = file_utils.find_files_by_extension(
        work_datetime_folder, 
        ['.mp4', '.mov', '.avi', '.jpg', '.jpeg', '.png'] # Only process media files
    )

    for media_path_in_work_dir in processed_raw_media_paths_in_work_dir:
        filename = os.path.basename(media_path_in_work_dir)
        if any(filename.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi']):
            print(f"Processing video for {project_name}: {media_path_in_work_dir}")
            
            converted_video_path = media_path_in_work_dir 
            if cfg.video_orientation == 'horizontal':
                temp_converted_path = os.path.join(work_datetime_folder, f"converted_{filename}")
                apply_blur_for_video = cfg.get('image_options', {}).get('apply_side_blur', False)
                if video_processor.convert_to_horizontal_with_blur_bg(
                    media_path_in_work_dir, 
                    temp_converted_path, 
                    cfg.get('target_resolution',{}).get('horizontal_height', 1080),
                    apply_blur_for_video
                    ):
                    converted_video_path = temp_converted_path
                    if media_path_in_work_dir != converted_video_path:
                         temp_video_files_to_remove.append(media_path_in_work_dir) 
                else: 
                    if os.path.exists(temp_converted_path): os.remove(temp_converted_path)

            segment_output_prefix = os.path.join(work_datetime_folder, os.path.splitext(filename)[0] + "_seg")
            video_processor.split_video_into_segments(converted_video_path, segment_output_prefix, cfg.segment_duration)
            
            if converted_video_path != media_path_in_work_dir and os.path.exists(converted_video_path): 
                temp_video_files_to_remove.append(converted_video_path)

        elif any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            print(f"Processing image for {project_name}: {media_path_in_work_dir}")
            target_h = cfg.get('target_resolution',{}).get('vertical_height', 1920) if cfg.video_orientation == 'vertical' \
                else cfg.get('target_resolution',{}).get('horizontal_height', 1080)
            apply_blur_for_image = cfg.get('image_options', {}).get('apply_side_blur', False)
            video_processor.process_image_for_video(
                media_path_in_work_dir, 
                target_h, 
                cfg.video_orientation,
                apply_blur_for_image
            )

    for f_path in temp_video_files_to_remove:
        if os.path.exists(f_path):
            os.remove(f_path)
            print(f"Removed intermediate processed video for {project_name}: {f_path}")

    video_processor.clean_short_video_segments(work_datetime_folder, cfg.segment_duration - 0.5)

    # 4. Media List Preparation for Slideshow
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 3: Preparing Media List for Slideshow ---")
    
    current_media_for_slideshow = file_utils.find_files_by_extension(
        work_datetime_folder, 
        ['.mp4', '.jpg', '.jpeg', '.png']
    )
    current_media_for_slideshow = [p for p in current_media_for_slideshow if os.path.basename(p).lower() != 'voiceover.mp3']

    # Determine actual outro duration
    outro_template_name = 'outro_vertical.mp4' if cfg.video_orientation == 'vertical' else 'outro_horizontal.mp4'
    outro_video_full_path = os.path.join(cfg.template_folder, outro_template_name)
    actual_outro_duration = 0
    if os.path.exists(outro_video_full_path):
        actual_outro_duration = video_processor.get_video_duration(outro_video_full_path)
        if actual_outro_duration is None or actual_outro_duration <= 0:
            print(f"Warning: Could not get valid duration for outro video {outro_video_full_path}. Using config default: {cfg.outro_duration}s")
            actual_outro_duration = cfg.outro_duration # Fallback to config if ffprobe fails
        else:
            print(f"Actual outro video duration: {actual_outro_duration:.2f}s")
            # Update cfg.outro_duration so slideshow_generator uses the actual value
            cfg.outro_duration = actual_outro_duration 
    else:
        print(f"Warning: Outro video {outro_video_full_path} not found. Using config default for outro_duration: {cfg.outro_duration}s")
        actual_outro_duration = cfg.outro_duration # Use config default if file not found
    
    # Use cfg.slide_duration (which defaults to segment_duration - 1) for limiting media files.
    # This is the effective display time per item before transitions.
    effective_display_time_per_item = cfg.slide_duration
    if effective_display_time_per_item <= 0: 
        effective_display_time_per_item = 1 # Avoid division by zero or negative
        print(f"Warning: Calculated effective_display_time_per_item was <=0, defaulting to 1s. Check slide_duration and segment_duration config.")

    # Time available for main content (before outro)
    time_for_main_content = cfg.time_limit - actual_outro_duration # Use actual_outro_duration
    if time_for_main_content < 0: time_for_main_content = 0
        
    kept_filenames_after_limit = file_utils.limit_media_files_by_duration(
        work_datetime_folder, 
        time_for_main_content,
        effective_display_time_per_item 
    )
    current_media_for_slideshow = [os.path.join(work_datetime_folder, fname) for fname in kept_filenames_after_limit]
    current_media_for_slideshow.sort()

    # 5. DepthFlow Processing (Conditional)
    # -------------------------------------------------------------------------
    if cfg.depthflow.enabled:
        print(f"\n--- {project_name} - Phase 4: DepthFlow Processing ---")
        # Ensure output_datetime_folder is set in cfg for depth_processor logging
        cfg.output_datetime_folder = work_datetime_folder # Pass the current working folder for logs
        
        images_to_depthflow = [p for p in current_media_for_slideshow if any(p.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])]
        if images_to_depthflow:
            videos_from_depthflow = depth_processor.apply_depth_effects(images_to_depthflow, cfg)
            
            new_media_list = [p for p in current_media_for_slideshow if not p in images_to_depthflow]
            new_media_list.extend(videos_from_depthflow)
            current_media_for_slideshow = sorted(new_media_list)
            
            for img_path in images_to_depthflow: # Remove original images that were depthflowed
                if os.path.exists(img_path):
                    os.remove(img_path)
                    print(f"Removed original image after DepthFlow for {project_name}: {img_path}")
        else:
            print(f"No images found for DepthFlow processing in {project_name}.")
    
    # 6. Generate Base Slideshow
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 5: Generating Base Slideshow ---")
    slideshow_base_path = os.path.join(work_datetime_folder, "slideshow_base.mp4")
    
    outro_template_name = 'outro_vertical.mp4' if cfg.video_orientation == 'vertical' else 'outro_horizontal.mp4'
    outro_video_full_path = os.path.join(cfg.template_folder, outro_template_name)
    
    if not os.path.exists(outro_video_full_path):
        print(f"Error for {project_name}: Outro template video not found at {outro_video_full_path}. Cannot generate slideshow.")
        return # Skip this project

    if not current_media_for_slideshow:
        print(f"Error for {project_name}: No media files available for slideshow after filtering/DepthFlow. Skipping.")
        return

    media_for_ffmpeg_slideshow = current_media_for_slideshow + [outro_video_full_path]

    slideshow_base_path = slideshow_generator.generate_base_slideshow(
        media_for_ffmpeg_slideshow, slideshow_base_path, cfg
    )
    if not slideshow_base_path:
        print(f"Error for {project_name}: Base slideshow generation failed. Aborting project.")
        return

    # Read original text for correction if available
    original_text_content = None
    # Read from the work_datetime_folder where it was copied
    original_text_file_path_in_work_dir = os.path.join(work_datetime_folder, 'original_text.txt')
    print(f"DEBUG: Checking for original_text.txt at: {original_text_file_path_in_work_dir}")
    if os.path.exists(original_text_file_path_in_work_dir):
        print(f"DEBUG: original_text.txt exists: {os.path.exists(original_text_file_path_in_work_dir)}")
        try:
            with open(original_text_file_path_in_work_dir, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"DEBUG: Raw content read from original_text.txt (first 100 chars): '{content[:100]}...' (length: {len(content)})")
                # Clean content: replace newlines with spaces, remove extra whitespace
                cleaned_content = ' '.join(content.split()).strip()
                print(f"DEBUG: Cleaned content (first 100 chars): '{cleaned_content[:100]}...' (length: {len(cleaned_content)})")
                if cleaned_content:
                    original_text_content = cleaned_content
                    print(f"Found original_text.txt for {project_name}. Content loaded and cleaned for subtitle correction.")
                else:
                    print(f"original_text.txt for {project_name} is empty or contains only whitespace. Skipping subtitle correction.")
        except Exception as e:
            print(f"Error reading original_text.txt for {project_name}: {e}. Skipping subtitle correction.")
    else:
        print(f"original_text.txt not found in work directory for {project_name}. Skipping subtitle correction.")

    # 7. Generate Subtitles (Conditional)
    # -------------------------------------------------------------------------
    generated_subtitle_path = None
    project_voiceover_path = os.path.join(work_datetime_folder, 'voiceover.mp3')

    if cfg.subtitles.enabled and os.path.exists(project_voiceover_path):
        print(f"\n--- {project_name} - Phase 6: Generating Subtitles ---")
        
        subtitle_format = cfg.subtitles.get('format', 'ass').lower() # Get format from config, default to 'ass'
        subtitle_extension = "ass" if subtitle_format == "ass" else "srt"
        subtitle_output_target_path = os.path.join(work_datetime_folder, "subs", f"voiceover.{subtitle_extension}")
        os.makedirs(os.path.join(work_datetime_folder, "subs"), exist_ok=True)
        
        vo_delay_from_config_audio_dict = cfg.get('audio', {}).get('vo_delay', "NOT_IN_AUDIO_DICT_USING_0_DEFAULT")
        # Ensure vo_delay_for_srt is correctly fetched and converted
        try:
            # cfg.audio.vo_delay should be an int due to ConfigManager's processing
            vo_delay_for_srt = float(cfg.audio.vo_delay) 
        except (TypeError, ValueError):
            print(f"Warning: Could not convert cfg.audio.vo_delay ('{cfg.audio.get('vo_delay')}') to float. Defaulting to 0 for subtitle offset.")
            vo_delay_for_srt = 0.0
            
        print(f"Debug Subtitle offset: cfg.audio.vo_delay = {cfg.audio.get('vo_delay')}, vo_delay_for_srt = {vo_delay_for_srt}")
        # Removed the problematic print statement here

        generated_subtitle_path = subtitle_generator.generate_subtitles_from_audio_file(
            project_voiceover_path, 
            subtitle_output_target_path, 
            cfg,
            subtitle_format=subtitle_format, # Pass the format
            time_offset_seconds=vo_delay_for_srt, # Pass the delay
            original_text=original_text_content # Pass the original text content
        )
        if generated_subtitle_path: 
            print(f"Subtitles generated for {project_name}: {generated_subtitle_path}")
        else: print(f"Subtitle generation failed or was skipped for {project_name}.")
    elif cfg.subtitles.enabled:
        print(f"Subtitle generation enabled for {project_name}, but voiceover.mp3 not found. Skipping.")

    # 8. Audio Processing
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 7: Audio Processing ---")
    video_with_audio_path = os.path.join(work_datetime_folder, "slideshow_with_audio.mp4")
    video_with_audio_path = audio_processor.process_audio(
        slideshow_base_path, video_with_audio_path, cfg, work_datetime_folder
    )
    if not video_with_audio_path:
        print(f"Error for {project_name}: Audio processing failed. Aborting project.")
        return

    # 9. Final Overlay Composition
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 8: Final Overlay Composition ---")
    # Use project_name in the final output, placed inside work_datetime_folder
    final_output_video_name = f"{project_name.replace(' ', '_')}_{cfg.title.replace(' ', '_')}_{run_datetime_str}.mp4"
    final_output_video_path = os.path.join(work_datetime_folder, final_output_video_name)
    
    final_video_actual_path = overlay_compositor.apply_final_overlays(
        video_with_audio_path, final_output_video_path, cfg, 
        work_datetime_folder, generated_subtitle_path if cfg.subtitles.enabled else None
    )

    if not final_video_actual_path:
        print(f"Error for {project_name}: Final overlay composition failed.")
        return

    # 10. Cleanup
    # -------------------------------------------------------------------------
    print(f"\n--- {project_name} - Phase 9: Cleanup ---")
    if slideshow_base_path != final_video_actual_path and os.path.exists(slideshow_base_path):
        os.remove(slideshow_base_path); print(f"Cleaned up for {project_name}: {slideshow_base_path}")
    if video_with_audio_path != final_video_actual_path and os.path.exists(video_with_audio_path):
        os.remove(video_with_audio_path); print(f"Cleaned up for {project_name}: {video_with_audio_path}")
    
    # Clean up the temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Cleaned up temporary directory: {temp_dir}")

    end_time_project = datetime.now()
    print(f"\nProject {project_name} Finished at: {end_time_project.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total processing time for {project_name}: {end_time_project - start_time_project}")
    print(f"Final video output for {project_name}: {final_video_actual_path}")


def run_batch_pipeline(batch_root_folder: str, global_config_path: str = None, gui_settings: dict = None):
    """
    Runs the VideoCutter pipeline for all subfolders (projects) in a given batch root folder.
    """
    print(f"Starting Batch Processing for directory: {batch_root_folder}")
    if not os.path.isdir(batch_root_folder):
        print(f"Error: Batch root folder '{batch_root_folder}' does not exist. Aborting.")
        return

    for project_folder_name in os.listdir(batch_root_folder):
        project_folder_full_path = os.path.join(batch_root_folder, project_folder_name)
        if os.path.isdir(project_folder_full_path):
            print(f"\n{'-'*30}\nProcessing Project Folder: {project_folder_full_path}\n{'-'*30}")
            
            # Load config: global -> project-specific -> runtime (GUI)
            # The 'input_folder' in the config will be overridden to be the project_folder_full_path
            # The 'title' might also be overridden by the project_folder_name if not in project_config
            
            project_specific_gui_settings = (gui_settings or {}).copy()
            project_specific_gui_settings['input_folder'] = project_folder_full_path # Crucial override
            
            # Try to derive a title from folder name if not set by GUI/project_config
            # This logic will be handled by ConfigManager's defaults if 'title' isn't found
            # in project_config or gui_settings.
            
            cfg = load_config(
                global_config_path=global_config_path,
                project_folder_path=project_folder_full_path, # For _project_config.json
                runtime_settings=project_specific_gui_settings
            )
            
            # If title is still default after all merges, use project folder name
            if cfg.title == 'Default Model Name' or cfg.title == '':
                 cfg.title = project_folder_name
                 # Ensure title_overlay.text is also updated for consistency
                 cfg.title_overlay.text = project_folder_name

            run_pipeline_for_project(project_folder_name, project_folder_full_path, cfg)
        else:
            print(f"Skipping '{project_folder_full_path}', not a directory.")
    print(f"\nBatch Processing Finished for directory: {batch_root_folder}")


if __name__ == "__main__":
    print("VideoCutter main orchestrator starting (direct execution)...")
    
    # Determine the global default config path relative to this file's package root
    package_root_dir = os.path.dirname(os.path.abspath(__file__)) # videocutter/
    project_root_dir = os.path.dirname(package_root_dir) # One level up
    default_global_cfg_path = os.path.join(project_root_dir, "config", "default_config.json")

    # --- Example: Single Project Run (like original run_pipeline) ---
    # This requires an INPUT folder at project_root_dir with media files.
    # And config/default_config.json to exist.
    # single_project_input_folder = os.path.join(project_root_dir, "INPUT")
    # if os.path.exists(default_global_cfg_path) and os.path.isdir(single_project_input_folder):
    #     print("\n--- TESTING SINGLE PROJECT RUN ---")
    #     single_run_settings = {"input_folder": single_project_input_folder, "title": "Single Run Test"}
    #     cfg_single = load_config(global_config_path=default_global_cfg_path, runtime_settings=single_run_settings)
    #     if cfg_single.title == 'Default Model Name': cfg_single.title = "SingleProjectFromMain"
    #     run_pipeline_for_project("SingleTest", single_project_input_folder, cfg_single)
    # else:
    #     print("Skipping single project run test: Default config or INPUT folder not found.")

    # --- Example: Batch Project Run ---
    # Create a dummy batch structure for testing
    batch_test_root = os.path.join(project_root_dir, "BATCH_INPUTS_test")
    projectA_path = os.path.join(batch_test_root, "ProjectA_CoolVideo")
    projectB_path = os.path.join(batch_test_root, "ProjectB_AnotherOne")
    
    os.makedirs(projectA_path, exist_ok=True)
    os.makedirs(projectB_path, exist_ok=True)

    # Create dummy media for ProjectA
    with open(os.path.join(projectA_path, "image1.jpg"), "w") as f: f.write("dummy")
    with open(os.path.join(projectA_path, "vid1.mp4"), "w") as f: f.write("dummy")
    with open(os.path.join(projectA_path, "voiceover.mp3"), "w") as f: f.write("dummy")
    with open(os.path.join(projectA_path, "_project_config.json"), "w") as f:
        json.dump({"title": "Project Alpha Custom Title", "segment_duration": 7, "depthflow": True}, f)

    # Create dummy media for ProjectB
    with open(os.path.join(projectB_path, "photo_x.png"), "w") as f: f.write("dummy")
    
    if os.path.exists(default_global_cfg_path):
         print("\n--- TESTING BATCH PROJECT RUN ---")
         # GUI settings could provide a global override for the batch
         batch_gui_settings = {"time_limit": 300} # Example global override for the batch
         run_batch_pipeline(batch_test_root, global_config_path=default_global_cfg_path, gui_settings=batch_gui_settings)
    else:
         print("Skipping batch project run test: Default global config not found.")

    # Clean up dummy batch structure
    # shutil.rmtree(batch_test_root, ignore_errors=True)
    
    print("\nVideoCutter main orchestrator finished (direct execution).")
