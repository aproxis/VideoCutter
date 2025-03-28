"""
Configuration module for VideoCutter.

This module provides a centralized configuration class for managing all settings
and command-line arguments used throughout the application. It defines the VideoConfig
dataclass that holds all configuration parameters and provides a function to parse
command-line arguments into a VideoConfig object.

The configuration parameters include:
- Video segmentation settings (duration, time limit)
- Input/output folder paths
- Model and text settings (name, font size, watermark)
- Processing options (depth flow, orientation, blur)

This module serves as the single source of truth for configuration across the application,
ensuring consistency and making it easier to add new configuration options in the future.
"""

import argparse
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VideoConfig:
    """
    Configuration class for video processing settings.
    
    This dataclass holds all configuration parameters used throughout the application.
    It provides default values for all parameters and initializes derived settings
    in the __post_init__ method.
    
    Attributes:
        segment_duration (int): Duration of each video segment in seconds.
            Default is 6 seconds.
        time_limit (int): Maximum duration of the final video in seconds.
            Default is 595 seconds (just under 10 minutes).
        input_folder (str): Path to the folder containing input files.
            Default is 'INPUT'.
        model_name (str): Name of the model to display in the video.
            Default is 'Model Name'.
        fontsize (int): Font size for the model name text.
            Default is 90.
        watermark (str): Text to display as a watermark.
            Default is 'Today is a\n Plus Day'.
        depthflow (str): Whether to use DepthFlow for images ('0' or '1').
            Default is '0' (disabled).
        video_orientation (str): Orientation of the video ('vertical' or 'horizontal').
            Default is 'vertical'.
        blur (str): Whether to add blur effect ('0' or '1').
            Default is '0' (disabled).
        result_folder (Optional[str]): Path to the folder for processed results.
            Derived from input_folder if not provided.
        source_folder (Optional[str]): Path to the folder for source file backups.
            Derived from input_folder if not provided.
        datetime_str (Optional[str]): Timestamp string for folder organization.
            Set by the video processor during execution.
    """
    
    # Video segmentation settings
    segment_duration: int = 6  # Duration of each segment in seconds
    time_limit: int = 595      # Maximum duration of the final video (just under 10 minutes)
    
    # Input/output settings
    input_folder: str = 'INPUT'  # Folder containing input files
    
    # Model and text settings
    model_name: str = 'Model Name'  # Name to display in the video
    fontsize: int = 90              # Font size for the model name
    watermark: str = 'Today is a\n Plus Day'  # Watermark text (supports newlines)
    
    # Processing options
    depthflow: str = '0'  # Use DepthFlow for images? '0' = No, '1' = Yes
    video_orientation: str = 'vertical'  # 'vertical' (9:16) or 'horizontal' (16:9)
    blur: str = '0'  # Add blur effect? '0' = No, '1' = Yes
    
    # Derived settings (set during initialization or processing)
    result_folder: Optional[str] = None  # Folder for processed results
    source_folder: Optional[str] = None  # Folder for source file backups
    datetime_str: Optional[str] = None   # Timestamp for folder organization
    
    def __post_init__(self):
        """
        Initialize derived settings after initialization.
        
        This method is automatically called after the dataclass is initialized.
        It sets up the result_folder and source_folder paths based on the input_folder
        if they weren't explicitly provided.
        """
        # Set up result folder path if not provided
        if not self.result_folder:
            self.result_folder = os.path.join(self.input_folder, 'RESULT')
        
        # Set up source folder path if not provided
        if not self.source_folder:
            self.source_folder = os.path.join(self.input_folder, 'SOURCE')


def parse_arguments() -> VideoConfig:
    """
    Parse command-line arguments and return a VideoConfig object.
    
    This function sets up an argument parser with all the configuration options
    and their default values. It then parses the command-line arguments and
    creates a VideoConfig object with the parsed values.
    
    The argument names follow a consistent pattern:
    - --d: Duration-related parameters
    - --i: Input-related parameters
    - --n: Name-related parameters
    - --f: Font-related parameters
    - --w: Watermark-related parameters
    - --z: DepthFlow-related parameters
    - --o: Orientation-related parameters
    - --b: Blur-related parameters
    - --tl: Time limit parameters
    
    Returns:
        VideoConfig: Configuration object with all settings from command-line arguments.
    
    Example:
        To use this function:
        ```python
        config = parse_arguments()
        print(f"Processing videos with segment duration: {config.segment_duration}s")
        ```
    """
    # Create argument parser with description
    parser = argparse.ArgumentParser(description="Video processing tool for cutting and creating slideshows.")
    
    # Video segmentation settings
    parser.add_argument('--d', type=int, default=6, dest='segment_duration', 
                        help='Duration of each segment (in seconds)')
    parser.add_argument('--tl', type=int, default=595, dest='time_limit', 
                        help='Duration of clip')
    
    # Input/output settings
    parser.add_argument('--i', type=str, default='INPUT', dest='input_folder', 
                        help='Input folder')
    
    # Model and text settings
    parser.add_argument('--n', type=str, default='Model Name', dest='model_name', 
                        help='Model name')
    parser.add_argument('--f', type=int, default=90, dest='fontsize', 
                        help='Font size')
    parser.add_argument('--w', type=str, default='Today is a\\n Plus Day', dest='watermark', 
                        help='Watermark text')
    
    # Processing options
    parser.add_argument('--z', type=str, default='0', dest='depthflow', 
                        help='Use DepthFlow for images? 0/1')
    parser.add_argument('--o', type=str, default='vertical', dest='video_orientation', 
                        help='Video orientation (vertical|horizontal)')
    parser.add_argument('--b', type=str, default='0', dest='blur', 
                        help='Add blur? 0/1')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Create and return the config object
    # Note: We replace the escaped newlines in the watermark with actual newlines
    config = VideoConfig(
        segment_duration=args.segment_duration,
        time_limit=args.time_limit,
        input_folder=args.input_folder,
        model_name=args.model_name,
        fontsize=args.fontsize,
        watermark=args.watermark.replace('\\n', '\n'),  # Convert escaped newlines to actual newlines
        depthflow=args.depthflow,
        video_orientation=args.video_orientation,
        blur=args.blur
    )
    
    return config
