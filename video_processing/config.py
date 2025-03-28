"""
Configuration module for VideoCutter.

This module provides a centralized configuration class for managing all settings
and command-line arguments used throughout the application.
"""

import argparse
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VideoConfig:
    """Configuration class for video processing settings."""
    
    # Video segmentation settings
    segment_duration: int = 6
    time_limit: int = 595
    
    # Input/output settings
    input_folder: str = 'INPUT'
    
    # Model and text settings
    model_name: str = 'Model Name'
    fontsize: int = 90
    watermark: str = 'Today is a\n Plus Day'
    
    # Processing options
    depthflow: str = '0'
    video_orientation: str = 'vertical'
    blur: str = '0'
    
    # Derived settings
    result_folder: Optional[str] = None
    source_folder: Optional[str] = None
    datetime_str: Optional[str] = None
    
    def __post_init__(self):
        """Initialize derived settings after initialization."""
        if not self.result_folder:
            self.result_folder = os.path.join(self.input_folder, 'RESULT')
        
        if not self.source_folder:
            self.source_folder = os.path.join(self.input_folder, 'SOURCE')


def parse_arguments() -> VideoConfig:
    """Parse command-line arguments and return a VideoConfig object.
    
    Returns:
        VideoConfig: Configuration object with all settings.
    """
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
    
    args = parser.parse_args()
    
    # Create and return the config object
    config = VideoConfig(
        segment_duration=args.segment_duration,
        time_limit=args.time_limit,
        input_folder=args.input_folder,
        model_name=args.model_name,
        fontsize=args.fontsize,
        watermark=args.watermark.replace('\\n', '\n'),
        depthflow=args.depthflow,
        video_orientation=args.video_orientation,
        blur=args.blur
    )
    
    return config
