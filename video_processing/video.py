import os
import shutil
import json
from datetime import datetime
from typing import List
from .config import VideoConfig
from .utils import (
    run_ffmpeg_command,
    ensure_directory,
    get_media_files,
    validate_aspect_ratio
)

class VideoProcessor:
    """Handles all video processing operations"""
    
    def __init__(self, config: VideoConfig):
        self.config = config
        self.result_folder = os.path.join(config.input_folder, 'RESULT')
        self.source_folder = os.path.join(config.input_folder, 'SOURCE')
        self.current_datetime = datetime.now()
        self.datetime_str = self.current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        self.source_date_folder = os.path.join(self.source_folder, self.datetime_str)

    def split_video(self, input_file: str, output_prefix: str) -> bool:
        """
        Split a video into segments of configured duration.
        
        Args:
            input_file: Path to input video file
            output_prefix: Prefix for output segments
            
        Returns:
            bool: True if successful, False if failed
        """
        cmd = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'error',
            '-i', input_file,
            '-c:v', 'libx264',
            '-crf', '22',
            '-g', '30',
            '-r', '30',
            '-an',  # Remove audio
            '-map', '0',
            '-segment_time', str(self.config.segment_duration),
            '-g', str(self.config.segment_duration),
            '-sc_threshold', '0',
            '-force_key_frames', f'expr:gte(t,n_forced*{self.config.segment_duration})',
            '-f', 'segment',
            '-reset_timestamps', '1',
            f'{output_prefix}%d.mp4'
        ]
        
        return run_ffmpeg_command(
            cmd,
            description=f"Splitting video {input_file} into segments"
        )

    def process_videos(self) -> None:
        """Process all videos in the input folder"""
        # Ensure directories exist
        ensure_directory(self.result_folder)
        ensure_directory(self.source_date_folder)

        # Get video files
        video_files = get_media_files(self.config.input_folder, ['.mp4'])
        if not video_files:
            return

        print('##### Video splitting')
        
        for video_file in video_files:
            input_path = os.path.join(self.config.input_folder, video_file)
            
            # Validate aspect ratio
            if not validate_aspect_ratio(input_path):
                print(f"Deleting {input_path} - invalid aspect ratio")
                os.remove(input_path)
                continue

            output_prefix = os.path.splitext(os.path.basename(video_file))[0] + '_'
            
            # Split video
            if self.split_video(input_path, os.path.join(self.result_folder, output_prefix)):
                # Move original to source folder
                shutil.move(input_path, os.path.join(self.source_date_folder, video_file))

        print(f'##### Videos moved to {self.result_folder}')

    def run_cleaner(self) -> None:
        """Run the cleaner script to remove short videos"""
        cleaner_script = 'cleaner.py'
        cleaner_args = [
            '--i', self.result_folder,
            '--m', str(self.config.segment_duration)
        ]
        cmd = ['python3', cleaner_script] + cleaner_args
        subprocess.run(cmd)
        print(f'##### Cleaned videos shorter than {self.config.segment_duration}s')

    def run_sorter(self) -> None:
        """Run the sorter script to organize files"""
        sorter_script = 'sorter.py'
        sorter_args = [
            '--o', self.result_folder,
            '--d', self.datetime_str
        ]
        cmd = ['python3', sorter_script] + sorter_args
        subprocess.run(cmd)
        print(f'##### Files organized in {self.result_folder}/{self.datetime_str}')
