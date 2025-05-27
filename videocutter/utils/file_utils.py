# videocutter/utils/file_utils.py
# Utility functions for file and directory operations.

import os
import shutil
from datetime import datetime

def setup_project_directories(base_input_folder: str) -> tuple[str, str, str, str]:
    """
    Sets up the necessary RESULT and SOURCE directories for a processing run.
    A unique timestamped subfolder is created within the SOURCE directory.

    Args:
        base_input_folder (str): The main input folder (e.g., 'INPUT').

    Returns:
        tuple[str, str, str, str]: Paths to result_folder, source_folder, 
                                   run_specific_source_folder, and the datetime_str.
    """
    result_folder = os.path.join(base_input_folder, 'RESULT')
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
        print(f"Created result folder: {result_folder}")

    source_folder = os.path.join(base_input_folder, 'SOURCE')
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
        print(f"Created source folder: {source_folder}")

    current_datetime = datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    run_specific_source_folder = os.path.join(source_folder, datetime_str)
    os.makedirs(run_specific_source_folder, exist_ok=True)
    print(f"Created run-specific source folder: {run_specific_source_folder}")

    return result_folder, source_folder, run_specific_source_folder, datetime_str

def backup_original_file(original_file_path: str, run_specific_source_folder: str):
    """
    Copies an original file to the run-specific source backup folder.

    Args:
        original_file_path (str): Path to the original file.
        run_specific_source_folder (str): Path to the backup folder for the current run.
    """
    if not os.path.isfile(original_file_path):
        print(f"Warning: Original file not found for backup: {original_file_path}")
        return
    
    try:
        base_filename = os.path.basename(original_file_path)
        backup_path = os.path.join(run_specific_source_folder, base_filename)
        shutil.copy(original_file_path, backup_path)
        print(f"Backed up '{original_file_path}' to '{backup_path}'")
    except Exception as e:
        print(f"Error backing up file {original_file_path}: {e}")

def find_files_by_extension(directory: str, extensions: list[str]) -> list[str]:
    """
    Finds all files with specified extensions under the given directory, recursively.

    Args:
        directory (str): The directory to search in.
        extensions (list[str]): A list of file extensions to find (e.g., ['.mp4', '.jpg']).
                               Extensions should include the dot.

    Returns:
        list[str]: A list of absolute paths to the found files.
    """
    found_files = []
    normalized_extensions = [ext.lower() for ext in extensions]
    for dirpath, dirnames, filenames in os.walk(directory):
        for f_name in filenames:
            if os.path.splitext(f_name)[1].lower() in normalized_extensions:
                found_files.append(os.path.join(dirpath, f_name))
    return found_files

def organize_files_to_timestamped_folder(source_directory: str, datetime_string: str) -> str:
    """
    Moves and renames files from a source directory into a new timestamped subfolder
    within that source directory. MP3 files are renamed to 'voiceover.mp3'.
    Other files are renamed sequentially (001.ext, 002.ext, etc.) per extension.

    Args:
        source_directory (str): The directory containing files to be sorted.
        datetime_string (str): The name for the timestamped subfolder (e.g., "YYYY-MM-DD_HH-MM-SS").

    Returns:
        str: The path to the created timestamped_folder.
    """
    timestamped_folder_path = os.path.join(source_directory, datetime_string)
    os.makedirs(timestamped_folder_path, exist_ok=True)
    print(f"Ensured timestamped folder exists: {timestamped_folder_path}")

    files_in_source = sorted(os.listdir(source_directory)) # Sort to ensure consistent numbering
    counters = {} # To keep track of renaming sequence per extension
    
    image_extensions = ['.jpg', '.jpeg', '.png']
    txt_extensions = ['.txt']
    
    voiceover_found = False
    original_text_found = False

    for filename in files_in_source:
        # Skip the newly created timestamped folder itself and any files without extensions
        if filename == datetime_string or not os.path.splitext(filename)[1]:
            continue

        original_filepath = os.path.join(source_directory, filename)
        if not os.path.isfile(original_filepath): # Skip if it's a directory
            continue

        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        new_filename = filename # Default to original filename

        if ext_lower == '.mp3':
            if not voiceover_found:
                new_filename = 'voiceover.mp3'
                voiceover_found = True
            else:
                # Handle multiple mp3s if needed, e.g., rename sequentially
                current_counter = counters.get(ext_lower, 0) + 1
                counters[ext_lower] = current_counter
                new_filename = f"voiceover_{str(current_counter).zfill(3)}.mp3"
        elif ext_lower in [f".{e}" for e in image_extensions]: # Check against normalized image extensions
            current_counter = counters.get('.jpg', 0) + 1 # Use .jpg counter for all images
            counters['.jpg'] = current_counter
            new_filename = f"{str(current_counter).zfill(3)}.jpg" # Force .jpg extension
        elif ext_lower in txt_extensions:
            if not original_text_found:
                new_filename = 'original_text.txt'
                original_text_found = True
            else:
                current_counter = counters.get(ext_lower, 0) + 1
                counters[ext_lower] = current_counter
                new_filename = f"original_text_{str(current_counter).zfill(3)}.txt"
        else:
            # For other file types, continue sequential renaming based on their original extension
            current_counter = counters.get(ext_lower, 0) + 1
            counters[ext_lower] = current_counter
            new_filename = f"{str(current_counter).zfill(3)}{ext}" # Preserve original extension case

        new_filepath = os.path.join(timestamped_folder_path, new_filename)
        
        try:
            shutil.move(original_filepath, new_filepath)
            print(f"Moved and renamed '{original_filepath}' to '{new_filepath}'")
        except Exception as e:
            print(f"Error moving file {original_filepath} to {new_filepath}: {e}")
            # If it's a duplicate voiceover.mp3, we might want to handle it (e.g., rename uniquely or skip)
            if new_filename == 'voiceover.mp3' and os.path.exists(new_filepath):
                print(f"Warning: '{new_filepath}' already exists. Original '{original_filepath}' was not moved.")


    return timestamped_folder_path

def limit_media_files_by_duration(directory: str, total_time_limit_seconds: int, segment_duration_seconds: int, image_extensions: list[str] = None, video_extensions: list[str] = None) -> list[str]:
    """
    Limits the number of media files in a directory to fit a total time limit,
    by deleting surplus files. Files are sorted alphabetically before limiting.

    Args:
        directory (str): The directory containing media files.
        total_time_limit_seconds (int): The total desired duration for all media.
        segment_duration_seconds (int): The duration each media item is expected to occupy.
                                        Note: The original logic used (segment_duration - 1)
                                        for the limit calculation, which might be specific
                                        to slideshow transition handling. This function uses
                                        the direct segment_duration for a more general limit.
                                        Adjust divisor if needed for specific use cases.
        image_extensions (list[str], optional): List of image extensions. 
                                                Defaults to ['.jpg', '.jpeg', '.png'].
        video_extensions (list[str], optional): List of video extensions. 
                                                Defaults to ['.mp4'].
    Returns:
        list[str]: A list of filenames (not full paths) that were kept.
    """
    if image_extensions is None:
        image_extensions = ['.jpg', '.jpeg', '.png']
    if video_extensions is None:
        video_extensions = ['.mp4']

    all_media_filenames = []
    original_image_filenames = []
    original_video_filenames = []

    for f_name in os.listdir(directory):
        full_path = os.path.join(directory, f_name)
        if os.path.isfile(full_path):
            ext = os.path.splitext(f_name)[1].lower()
            if ext in image_extensions:
                all_media_filenames.append(f_name)
                original_image_filenames.append(f_name)
            elif ext in video_extensions:
                all_media_filenames.append(f_name)
                original_video_filenames.append(f_name)
    
    sorted_media_filenames = sorted(all_media_filenames, key=lambda x: x.lower())

    if segment_duration_seconds <= 0:
        print("Warning: segment_duration_seconds must be positive. Skipping file limiting.")
        return sorted_media_filenames

    # Calculate the limit. Consider if a -1 is needed in the divisor for specific contexts
    # like slideshows where transitions might effectively shorten usable segment time.
    # For a general utility, using segment_duration_seconds directly is clearer.
    # The original depth.py used (args.segment_duration - 1).
    # If this function is used before DepthFlow, that -1 might still be relevant.
    # For now, using segment_duration_seconds directly.
    limit = int(total_time_limit_seconds / segment_duration_seconds)
    if limit <= 0 : limit = 1 # Ensure at least one file can be kept if time limit allows

    print(f"Original media count in '{directory}': {len(sorted_media_filenames)}")
    print(f"Calculated limit based on time_limit ({total_time_limit_seconds}s) and segment_duration ({segment_duration_seconds}s): {limit} files")

    kept_filenames = sorted_media_filenames[:limit]
    files_to_delete = set(sorted_media_filenames) - set(kept_filenames)

    for filename_to_delete in files_to_delete:
        try:
            file_path_to_delete = os.path.join(directory, filename_to_delete)
            os.remove(file_path_to_delete)
            print(f"Deleted surplus file: {file_path_to_delete}")
        except Exception as e:
            print(f"Error deleting file {file_path_to_delete}: {e}")
            
    print(f"Kept {len(kept_filenames)} files in '{directory}'.")
    return kept_filenames


if __name__ == "__main__":
    print("Testing file_utils.py...")
    # Create a dummy INPUT folder for testing
    if not os.path.exists("INPUT_test"):
        os.makedirs("INPUT_test")
    
    res_folder, src_folder, run_src_folder, dt_str = setup_project_directories("INPUT_test")
    print(f"Result Folder: {res_folder}")
    print(f"Source Folder: {src_folder}")
    print(f"Run Source Folder: {run_src_folder}")
    print(f"Datetime String: {dt_str}")

    # Create a dummy file to backup
    dummy_file_path = os.path.join("INPUT_test", "dummy.txt")
    with open(dummy_file_path, "w") as f:
        f.write("This is a test file.")
    
    backup_original_file(dummy_file_path, run_src_folder)
    
    # Clean up dummy test files/folders
    if os.path.exists(dummy_file_path):
        os.remove(dummy_file_path)
    
    # Test find_files_by_extension
    print("\nTesting find_files_by_extension...")
    dummy_mp4_path_in_result = os.path.join(res_folder, "test_in_result.mp4") 
    dummy_jpg_path_in_result = os.path.join(res_folder, "test_in_result.jpg")
    if not os.path.exists(res_folder): os.makedirs(res_folder)
    with open(dummy_mp4_path_in_result, "w") as f: f.write("dummy mp4")
    with open(dummy_jpg_path_in_result, "w") as f: f.write("dummy jpg")
    
    found_videos = find_files_by_extension(res_folder, [".mp4"])
    print(f"Found videos in {res_folder}: {found_videos}")
    found_media_in_input_test = find_files_by_extension("INPUT_test", [".mp4", ".jpg", ".txt"])
    print(f"Found media in INPUT_test: {found_media_in_input_test}")

    if os.path.exists(dummy_mp4_path_in_result): os.remove(dummy_mp4_path_in_result)
    if os.path.exists(dummy_jpg_path_in_result): os.remove(dummy_jpg_path_in_result)

    print("\nTesting organize_files_to_timestamped_folder...")
    org_test_files_dir = res_folder 
    if not os.path.exists(org_test_files_dir): os.makedirs(org_test_files_dir)
    test_files_for_org = {
        "video1.MP4": "v1", "imageA.JPG": "iA", 
        "audio_track.mp3": "aT", "video2.mp4": "v2"
    }
    for fname, content in test_files_for_org.items():
        with open(os.path.join(org_test_files_dir, fname), "w") as f: f.write(content)

    org_datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_orgtest")
    organized_folder = organize_files_to_timestamped_folder(org_test_files_dir, org_datetime_str)
    print(f"Files organized into: {organized_folder}")
    if os.path.exists(organized_folder):
        print(f"Contents of {organized_folder}: {os.listdir(organized_folder)}")
        shutil.rmtree(organized_folder, ignore_errors=True)
    # Clean up original files left by organize function if any (should be moved)
    for fname in test_files_for_org.keys():
        if os.path.exists(os.path.join(org_test_files_dir, fname)):
             os.remove(os.path.join(org_test_files_dir, fname))

    print("\nTesting limit_media_files_by_duration...")
    limit_test_dir = os.path.join(res_folder, "limit_test")
    if not os.path.exists(limit_test_dir): os.makedirs(limit_test_dir)
    test_files_for_limit = [f"file{i:02d}.jpg" for i in range(10)] + [f"vid{i:02d}.mp4" for i in range(5)]
    for fname in test_files_for_limit:
        with open(os.path.join(limit_test_dir, fname), "w") as f: f.write("limit_test_content")
    
    kept_files = limit_media_files_by_duration(limit_test_dir, total_time_limit_seconds=30, segment_duration_seconds=6)
    print(f"Kept files after limiting: {kept_files}")
    print(f"Remaining files in {limit_test_dir}: {os.listdir(limit_test_dir)}")
    shutil.rmtree(limit_test_dir, ignore_errors=True)


    # General cleanup of dummy test files/folders
    if os.path.exists(run_src_folder): 
        if not os.listdir(run_src_folder): 
            os.rmdir(run_src_folder)
    if os.path.exists(os.path.join("INPUT_test", "SOURCE")):
         if not os.listdir(os.path.join("INPUT_test", "SOURCE")): 
            os.rmdir(os.path.join("INPUT_test", "SOURCE"))
    if os.path.exists(res_folder): # INPUT_test/RESULT
        # Remove any remaining files/dirs before trying to rmdir res_folder
        for item in os.listdir(res_folder):
            item_path = os.path.join(res_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path): # like limit_test_dir if not cleaned properly
                shutil.rmtree(item_path, ignore_errors=True)
        if not os.listdir(res_folder): 
            os.rmdir(res_folder)
    if os.path.exists("INPUT_test"):
        if not os.listdir("INPUT_test"): 
            os.rmdir("INPUT_test")
    print("Test complete.")
