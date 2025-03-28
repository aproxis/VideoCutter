"""
Video processing module for VideoCutter.

This module provides functions for processing videos, including splitting,
cleaning, and sorting.
"""

import os
import subprocess
import shutil
from typing import List, Optional

from .config import VideoConfig
from .utils import find_video_files, get_video_duration, check_aspect_ratio, create_timestamp_folder, ensure_directory


class VideoProcessor:
    """Class for processing videos."""
    
    def __init__(self, config: VideoConfig):
        """Initialize the VideoProcessor.
        
        Args:
            config: The configuration object.
        """
        self.config = config
        
        # Ensure output directories exist
        ensure_directory(config.result_folder)
        ensure_directory(config.source_folder)
        
        # Create timestamp folder for source files
        self.source_date_folder, self.config.datetime_str = create_timestamp_folder(config.source_folder)
    
    def split_video(self, input_file: str, output_prefix: str) -> None:
        """Split a video into segments of specified duration.
        
        Args:
            input_file: Path to the input video file.
            output_prefix: Prefix for the output files.
        """
        try:
            cmd = (
                f"ffmpeg -hide_banner -loglevel error -i {input_file} -c:v libx264 -crf 22 -g 30 -r 30 -an "
                f"-map 0 -segment_time {self.config.segment_duration} -g {self.config.segment_duration} "
                f"-sc_threshold 0 -force_key_frames expr:gte\(t,n_forced*{self.config.segment_duration}\) "
                f"-f segment -reset_timestamps 1 {output_prefix}%d.mp4"
            )
            
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = p.stdout.readline()
                if not line:
                    break
                print(line.decode().strip())
            p.wait()
            
            if p.returncode != 0:
                raise Exception(f"FFmpeg failed with exit code {p.returncode}")
        
        except Exception as e:
            print(f"Failed to process {input_file}: {e}")
    
    def process_videos(self) -> None:
        """Process all videos in the input folder."""
        # List all video files in the input folder
        video_files = [f for f in os.listdir(self.config.input_folder) if f.endswith('.mp4')]
        
        print('##### Video splitting')
        
        # Split each video file into segments
        for video_file in video_files:
            input_path = os.path.join(self.config.input_folder, video_file)
            
            # Check if the video has the correct aspect ratio
            if not check_aspect_ratio(input_path):
                print(f"Deleting {input_path} as it's not 16:9 aspect ratio")
                os.remove(input_path)  # Delete the file
                continue
            
            output_prefix = os.path.splitext(os.path.basename(video_file))[0] + '_'
            
            # Split the video
            self.split_video(input_path, os.path.join(self.config.result_folder, output_prefix))
            
            # Move original video to the source folder
            shutil.move(input_path, os.path.join(self.source_date_folder, video_file))
        
        print(f'##### Videos moved to {self.config.result_folder}')
    
    def run_cleaner(self) -> None:
        """Run the cleaner to remove short videos."""
        cleaner_script = 'cleaner.py'
        cleaner_args = ['--i', self.config.result_folder, '--m', str(self.config.segment_duration)]
        
        # Construct the full command to run cleaner.py with arguments
        cleaner_command = ['python3', cleaner_script] + cleaner_args
        
        # Run the cleaner.py script with arguments
        subprocess.run(cleaner_command)
    
    def run_sorter(self) -> None:
        """Run the sorter to organize files."""
        sorter_script = 'sorter.py'
        sorter_args = ['--o', self.config.result_folder, '--d', self.config.datetime_str]
        
        # Construct the full command to run sorter.py with arguments
        sorter_command = ['python3', sorter_script] + sorter_args
        
        # Run the sorter.py script with arguments
        subprocess.run(sorter_command)
    
    def run_depth_processor(self) -> None:
        """Run the depth processor if enabled."""
        if self.config.depthflow == '1':
            print("DepthFlow is True")
            depth_script = 'depth.py'
            depth_args = [
                '--o', self.config.result_folder,
                '--d', self.config.datetime_str,
                '--t', str(self.config.segment_duration - 1),
                '--tl', str(self.config.time_limit)
            ]
            
            # Construct the full command to run depth.py with arguments
            depth_command = ['python3', depth_script] + depth_args
            
            # Run the depth.py script with arguments
            subprocess.run(depth_command)
    
    def run_slideshow_creator(self) -> None:
        """Run the slideshow creator."""
        slideshow_script = 'slideshow.py'
        slideshow_args = [
            '--t', str(self.config.segment_duration - 1),
            '--tl', str(self.config.time_limit),
            '--n', self.config.model_name,
            '--w', self.config.watermark.replace('\n', '\\n'),
            '--f', str(self.config.fontsize),
            '--z', str(self.config.depthflow),
            '--o', str(self.config.video_orientation)
        ]
        
        print(slideshow_args)
        
        # Construct the full command to run slideshow.py with arguments
        slideshow_command = ['python3', slideshow_script] + slideshow_args
        
        # Run the slideshow.py script with arguments
        subprocess.run(slideshow_command)
        
        print("###### SLIDESHOW READY ######")
    
    def process_all(self) -> None:
        """Process all videos and create slideshow."""
        # Process videos
        self.process_videos()
        
        # Run cleaner to remove short videos
        print(f'##### Delete videos shorter than {self.config.segment_duration}s')
        self.run_cleaner()
        
        # Run sorter to organize files
        print(f'##### Rename and move to {self.config.result_folder}/{self.config.datetime_str}')
        self.run_sorter()
        
        # Run depth processor if enabled
        print(f'##### Create slideshow {str(self.config.segment_duration - 1)}s per frame')
        self.run_depth_processor()
        
        # Run slideshow creator
        self.run_slideshow_creator()
