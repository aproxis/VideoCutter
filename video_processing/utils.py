import subprocess
import os
from typing import List, Optional
from .config import VideoConfig
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_ffmpeg_command(
    command: List[str],
    description: str = "",
    suppress_output: bool = True
) -> bool:
    """
    Execute an FFmpeg command with error handling and logging.
    
    Args:
        command: List of command arguments
        description: Description of the operation for logging
        suppress_output: Whether to suppress FFmpeg output
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        logger.info(f"Starting FFmpeg operation: {description}")
        
        kwargs = {'check': True}
        if suppress_output:
            kwargs.update({
                'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT
            })
            
        subprocess.run(command, **kwargs)
        logger.info(f"Successfully completed: {description}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {description}")
        if not suppress_output and e.stdout:
            logger.error(e.stdout.decode())
        return False
    except Exception as e:
        logger.error(f"Unexpected error during {description}: {str(e)}")
        return False

def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Path to directory
        
    Returns:
        bool: True if directory exists (or was created), False if failed
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {str(e)}")
        return False

def get_media_files(
    directory: str,
    extensions: List[str]
) -> List[str]:
    """
    Get media files with specified extensions from a directory.
    
    Args:
        directory: Path to search
        extensions: List of file extensions to include
        
    Returns:
        List of matching file paths
    """
    try:
        return [
            f for f in os.listdir(directory)
            if os.path.splitext(f)[1].lower() in extensions
        ]
    except Exception as e:
        logger.error(f"Failed to list files in {directory}: {str(e)}")
        return []

def validate_aspect_ratio(
    video_path: str,
    target_ratio: float = 16/9,
    tolerance: float = 0.01
) -> bool:
    """
    Validate a video's aspect ratio using ffprobe.
    
    Args:
        video_path: Path to video file
        target_ratio: Target aspect ratio (width/height)
        tolerance: Allowed deviation from target
        
    Returns:
        bool: True if aspect ratio is within tolerance
    """
    try:
        cmd = f"ffprobe -v error -show_entries stream=width,height -of json {video_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        width = int(json.loads(result.stdout)['streams'][0]['width'])
        height = int(json.loads(result.stdout)['streams'][0]['height'])
        ratio = width / height
        return abs(ratio - target_ratio) <= tolerance
    except Exception as e:
        logger.error(f"Failed to validate aspect ratio for {video_path}: {str(e)}")
        return False
