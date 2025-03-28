"""
Utility functions for VideoCutter.

This module provides common utility functions used across the application for tasks such as:
- Finding video files in directories
- Getting video duration and dimensions
- Checking video aspect ratios
- Creating timestamp-based folders
- Ensuring directories exist

These functions abstract common operations and provide a consistent interface
for working with files, directories, and video properties throughout the application.
"""

import os
import subprocess
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


def find_video_files(directory: str) -> List[str]:
    """
    Find all video files under the given directory.
    
    This function recursively searches the specified directory and its subdirectories
    for files with the .mp4 extension (case-insensitive). It returns a list of full
    paths to all matching files.
    
    Args:
        directory: The directory to search for video files.
        
    Returns:
        A list of absolute paths to video files found in the directory.
    
    Example:
        ```python
        videos = find_video_files('INPUT')
        for video in videos:
            print(f"Found video: {video}")
        ```
    """
    result = []
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(directory):
        # Filter for .mp4 files (case-insensitive)
        for f in [f for f in filenames if f.lower().endswith('.mp4')]:
            # Add the full path to the result list
            result.append(os.path.join(dirpath, f))
    return result


def get_video_duration(filename: str) -> Optional[float]:
    """
    Get the duration of the video in seconds.
    
    This function uses ffprobe to determine the duration of a video file.
    It returns the duration in seconds as a float, or None if the duration
    could not be determined (e.g., if the file is not a valid video or ffprobe fails).
    
    Args:
        filename: Path to the video file.
        
    Returns:
        The duration in seconds as a float, or None if the duration could not be determined.
    
    Example:
        ```python
        duration = get_video_duration('video.mp4')
        if duration is not None:
            print(f"Video duration: {duration:.2f} seconds")
        else:
            print("Could not determine video duration")
        ```
    """
    try:
        # Run ffprobe to get the duration in sexagesimal format (HH:MM:SS.ms)
        p = subprocess.Popen([
            "ffprobe",
            "-loglevel", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            "-sexagesimal",
            filename
        ], stdout=subprocess.PIPE)
        
        # Get the output and return code
        (out, err) = p.communicate()
        retval = p.wait()
        
        # Check if ffprobe succeeded
        if retval != 0:
            print(f"Failed to determine duration of {filename}. Skipping.")
            return None
        
        # Decode the bytes-like object into a string using UTF-8 encoding
        duration_str = out.decode('utf-8').strip()
        
        # Parse the duration string (HH:MM:SS.ms or MM:SS.ms)
        duration_parts = duration_str.split(":")
        if len(duration_parts) == 3:
            # Format is HH:MM:SS.ms
            hours, minutes, seconds = map(float, duration_parts)
        else:
            # Format is MM:SS.ms
            minutes, seconds = map(float, duration_parts)
            hours = 0
            
        # Calculate the total duration in seconds
        duration_in_seconds = hours * 3600 + minutes * 60 + seconds
        return duration_in_seconds
    except Exception as e:
        # Handle any exceptions that might occur
        print(f"Error while getting duration of {filename}: {e}")
        return None


def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """
    Get the width and height of a video.
    
    This function uses ffprobe to determine the dimensions (width and height)
    of a video file. It returns a tuple of (width, height) as integers.
    
    Args:
        video_path: Path to the video file.
        
    Returns:
        A tuple of (width, height) as integers.
        
    Raises:
        subprocess.CalledProcessError: If ffprobe fails.
        json.JSONDecodeError: If the output cannot be parsed as JSON.
    
    Example:
        ```python
        try:
            width, height = get_video_dimensions('video.mp4')
            print(f"Video dimensions: {width}x{height}")
        except Exception as e:
            print(f"Error: {e}")
        ```
    """
    # Run ffprobe to get the width and height in JSON format
    cmd = f"ffprobe -v error -show_entries stream=width,height -of json {video_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    
    # Parse the JSON output
    json_data = json.loads(result.stdout)
    
    # Extract the width and height
    width = json_data['streams'][0]['width']
    height = json_data['streams'][0]['height']
    
    return width, height


def check_aspect_ratio(video_path: str, target_ratio: float = 16/9, tolerance: float = 0.01) -> bool:
    """
    Check if a video has the specified aspect ratio.
    
    This function checks if the aspect ratio of a video is within a specified
    tolerance of the target ratio. The aspect ratio is calculated as height/width.
    
    Args:
        video_path: Path to the video file.
        target_ratio: The target aspect ratio (default: 16/9).
        tolerance: The allowed deviation from the target ratio.
        
    Returns:
        True if the video has the specified aspect ratio (within tolerance), False otherwise.
    
    Example:
        ```python
        # Check if video has a 16:9 aspect ratio
        if check_aspect_ratio('video.mp4'):
            print("Video has a 16:9 aspect ratio")
        else:
            print("Video does not have a 16:9 aspect ratio")
            
        # Check if video has a 9:16 aspect ratio (vertical)
        if check_aspect_ratio('video.mp4', target_ratio=9/16):
            print("Video has a 9:16 aspect ratio")
        else:
            print("Video does not have a 9:16 aspect ratio")
        ```
    """
    # Get the video dimensions
    width, height = get_video_dimensions(video_path)
    
    # Calculate the actual aspect ratio (height/width)
    aspect_ratio = width / height
    
    # Check if the aspect ratio is within tolerance of the target ratio
    return abs(aspect_ratio - target_ratio) <= tolerance


def create_timestamp_folder(base_folder: str) -> Tuple[str, str]:
    """
    Create a timestamped folder within the base folder.
    
    This function creates a subfolder within the specified base folder,
    with a name based on the current date and time in the format
    "YYYY-MM-DD_HH-MM-SS". It returns the path to the created folder
    and the timestamp string.
    
    Args:
        base_folder: The base folder path.
        
    Returns:
        A tuple of (timestamp_folder_path, timestamp_string).
    
    Example:
        ```python
        folder_path, timestamp = create_timestamp_folder('OUTPUT')
        print(f"Created folder: {folder_path}")
        print(f"Timestamp: {timestamp}")
        ```
    """
    # Get the current date and time
    current_datetime = datetime.now()
    
    # Format the date and time as a string (YYYY-MM-DD_HH-MM-SS)
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create the subfolder for the date-time
    timestamp_folder = os.path.join(base_folder, datetime_str)
    os.makedirs(timestamp_folder, exist_ok=True)
    
    return timestamp_folder, datetime_str


def ensure_directory(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    This function checks if the specified directory exists, and creates it
    (including any necessary parent directories) if it does not.
    
    Args:
        directory: The directory path to ensure exists.
    
    Example:
        ```python
        # Ensure the output directory exists
        ensure_directory('OUTPUT/processed')
        
        # Now we can safely write to files in this directory
        with open('OUTPUT/processed/result.txt', 'w') as f:
            f.write('Processing complete')
        ```
    """
    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory)
