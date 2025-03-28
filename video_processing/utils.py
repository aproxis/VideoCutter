"""
Utility functions for VideoCutter.

This module provides common utility functions used across the application.
"""

import os
import subprocess
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


def find_video_files(directory: str) -> List[str]:
    """Find all video files under the given directory.
    
    Args:
        directory: The directory to search for video files.
        
    Returns:
        A list of paths to video files.
    """
    result = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in [f for f in filenames if f.lower().endswith('.mp4')]:
            result.append(os.path.join(dirpath, f))
    return result


def get_video_duration(filename: str) -> Optional[float]:
    """Get the duration of the video in seconds.
    
    Args:
        filename: Path to the video file.
        
    Returns:
        The duration in seconds, or None if the duration could not be determined.
    """
    try:
        p = subprocess.Popen(["ffprobe",
                             "-loglevel",
                             "error",
                             "-select_streams",
                             "v:0",
                             "-show_entries",
                             "format=duration",
                             "-of",
                             "default=noprint_wrappers=1:nokey=1",
                             "-sexagesimal",
                             filename], stdout=subprocess.PIPE)
        (out, err) = p.communicate()
        retval = p.wait()
        if retval != 0:
            print(f"Failed to determine duration of {filename}. Skipping.")
            return None
        
        # Decode the bytes-like object into a string using UTF-8 encoding
        duration_str = out.decode('utf-8').strip()
        duration_parts = duration_str.split(":")
        if len(duration_parts) == 3:
            hours, minutes, seconds = map(float, duration_parts)
        else:
            minutes, seconds = map(float, duration_parts)
            hours = 0
        duration_in_seconds = hours * 3600 + minutes * 60 + seconds
        return duration_in_seconds
    except Exception as e:
        print(f"Error while getting duration of {filename}: {e}")
        return None


def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """Get the width and height of a video.
    
    Args:
        video_path: Path to the video file.
        
    Returns:
        A tuple of (width, height).
        
    Raises:
        subprocess.CalledProcessError: If ffprobe fails.
        json.JSONDecodeError: If the output cannot be parsed as JSON.
    """
    cmd = f"ffprobe -v error -show_entries stream=width,height -of json {video_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    json_data = json.loads(result.stdout)
    width = json_data['streams'][0]['width']
    height = json_data['streams'][0]['height']
    return width, height


def check_aspect_ratio(video_path: str, target_ratio: float = 16/9, tolerance: float = 0.01) -> bool:
    """Check if a video has the specified aspect ratio.
    
    Args:
        video_path: Path to the video file.
        target_ratio: The target aspect ratio (default: 16/9).
        tolerance: The allowed deviation from the target ratio.
        
    Returns:
        True if the video has the specified aspect ratio, False otherwise.
    """
    width, height = get_video_dimensions(video_path)
    aspect_ratio = height / width
    return abs(aspect_ratio - target_ratio) <= tolerance


def create_timestamp_folder(base_folder: str) -> str:
    """Create a timestamped folder within the base folder.
    
    Args:
        base_folder: The base folder path.
        
    Returns:
        The path to the created timestamp folder.
    """
    # Get the current date and time
    current_datetime = datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create the subfolder for the date-time
    timestamp_folder = os.path.join(base_folder, datetime_str)
    os.makedirs(timestamp_folder, exist_ok=True)
    
    return timestamp_folder, datetime_str


def ensure_directory(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path to ensure exists.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
