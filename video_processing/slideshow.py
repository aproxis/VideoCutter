"""
Slideshow creation module for VideoCutter.

This module provides functions for creating slideshows from images and videos.
"""

import os
import subprocess
import random
import time
from typing import List, Optional, Tuple

from .config import VideoConfig
from .audio import AudioProcessor


class SlideshowCreator:
    """Class for creating slideshows."""
    
    def __init__(self, config: VideoConfig):
        """Initialize the SlideshowCreator.
        
        Args:
            config: The configuration object.
        """
        self.config = config
        
        # Set target dimensions based on orientation
        if config.video_orientation == 'vertical':
            self.target_height = 1920
            self.target_width = 1080
            self.outro_video_path = os.path.join('TEMPLATE', 'outro_vertical.mp4')
        else:
            self.target_height = 1080
            self.target_width = 1920
            self.outro_video_path = os.path.join('TEMPLATE', 'outro_horizontal.mp4')
        
        # Set frame rate
        self.fps = 25
        
        # Set font settings
        self.fontfile = '/Users/a/Library/Fonts/Nexa.otf'
        self.fontsize = 40
        
        # Set watermark settings
        self.watermark_text = config.watermark
        self.watermark_opacity = 0.7
        self.wmTimer = 50  # every half-slide move watermark
    
    def create_slideshow(self, folder_path: str) -> None:
        """Create a slideshow from images and videos in a folder.
        
        Args:
            folder_path: Path to the folder containing images and videos.
        """
        print(f"+++++ Processing folder: {folder_path}")
        print(f"Using outro video path: {os.path.abspath(self.outro_video_path)}")
        
        # Get the list of image and video files in the folder
        image_paths = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg'))]
        
        # If depthflow is enabled, don't use regular images
        if self.config.depthflow == '1':
            image_paths = []
            print(f"***** Not using JPG files, using DepthFlow. {folder_path}")
        
        video_paths = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
        
        # Sort the image and video paths alphabetically
        merged_paths = sorted(image_paths + video_paths, key=lambda x: x.lower())
        merged_paths_orig = merged_paths
        
        # Limit number of values in "merged_paths"
        limit = int(self.config.time_limit / self.config.segment_duration - 3)
        merged_paths = merged_paths[:limit]
        
        # Show difference between "merged_paths" and "merged_paths_limit"
        print(f"***** Number of values in merged_paths: {len(merged_paths)}")
        print(f"***** Number of values in merged_paths_orig: {len(merged_paths_orig)}")
        
        # Add outro.mp4 to the end of the list
        if not os.path.isfile(self.outro_video_path):
            print(f"***** Error: Outro video file does not exist at {self.outro_video_path}. Skipping slideshow creation.")
            return
        else:
            merged_paths.append(self.outro_video_path)
            print(merged_paths)
        
        # Check if there are any files to process
        if not merged_paths:
            print(f"***** No files found in {folder_path}")
            return
        
        # Set up FFMPEG command
        command = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error']
        
        # Build the filter complex argument
        filter_arg = self._build_filter_complex(merged_paths)
        
        # Set framerate of output video
        command.extend(['-r', str(self.fps)])
        
        # Add input arguments
        command = self._add_input_arguments(command, merged_paths, folder_path)
        
        # Calculate maximum duration
        max_duration = len(merged_paths) * self.config.segment_duration + (14 - self.config.segment_duration)
        max_frames = max_duration * self.fps
        
        # Add output arguments
        command.extend([
            '-filter_complex', filter_arg,
            '-pix_fmt', 'yuv420p',
            '-color_range', 'jpeg',
            '-vcodec', 'libx264',
            '-frames:v', str(max_frames),
            '-b:v', '2000k',
            os.path.join(folder_path, 'slideshow.mp4')
        ])
        
        try:
            print(f"##### Creating slideshow")
            subprocess.run(command, check=True)
            print(f"+++++ Slideshow saved: {folder_path}/slideshow.mp4")
            
            # Add audio
            print(f"##### Adding audio")
            audio_processor = AudioProcessor(self.config)
            audio_processor.process_audio(folder_path)
            
            # Add subscribe overlay
            print(f"##### Adding name, watermark, subscribe overlay")
            self._add_subscribe_overlay(folder_path)
            
            print(f"+++++ Subscribe overlay added.")
        
        except subprocess.CalledProcessError:
            print("***** Error executing FFmpeg command")
    
    def _build_filter_complex(self, merged_paths: List[str]) -> str:
        """Build the filter complex argument for FFmpeg.
        
        Args:
            merged_paths: List of paths to images and videos.
            
        Returns:
            The filter complex argument string.
        """
        filter_arg = ""
        
        # Add zoompan effect for images and setpts for videos
        for j, media_path in enumerate(merged_paths):
            if media_path.endswith('.jpg'):
                filter_arg += f'[{j}]zoompan=z=\'zoom+0.001\':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=30*{self.config.segment_duration}:s={self.target_width}x{self.target_height}[z{j}];'
            
            if media_path.endswith('.mp4'):
                if "outro.mp4" in media_path.lower():
                    filter_arg += f'[{j}]settb=AVTB,setpts=PTS-STARTPTS,fps={self.fps}/1,setsar=1:1[z{j}];'
                else:
                    filter_arg += f'[{j}]settb=AVTB,setpts=PTS-STARTPTS,fps={self.fps}/1,scale={self.target_width}:{self.target_height},setsar=1:1[z{j}];'
        
        # Add transitions between media
        for i, media_path in enumerate(merged_paths[:-1]):
            # Choose a random transition type
            transition_type = random.choice(['hblur', 'smoothup', 'horzopen', 'circleopen', 'diagtr', 'diagbl'])
            
            # Calculate offset for transitions
            offset = (i+1) * self.config.segment_duration - 0.5
            
            if i == 0:
                # Crossfade effect between the first two images
                filter_arg += f'[z{i}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset}[f{i}];'
            
            elif i == len(merged_paths[:-1]) - 1:
                # No chaining for last image in sequence - no semicolon in the end!!!
                filter_arg += f'[f{i-1}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset}'
            
            else:
                # Crossfade effect between intermediate media and watermark
                filter_arg += f'[f{i-1}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset},drawtext=text=\'{self.watermark_text}\':x=if(eq(mod(n\,{self.wmTimer})\,0)\,random(1)*w\,x):y=if(eq(mod(n\,{self.wmTimer})\,0)\,random(1)*h\,y):fontfile={self.fontfile}:fontsize={self.fontsize}:fontcolor_expr=random@{self.watermark_opacity}[f{i}];'
        
        return filter_arg
    
    def _add_input_arguments(self, command: List[str], merged_paths: List[str], folder_path: str) -> List[str]:
        """Add input arguments to the FFmpeg command.
        
        Args:
            command: The FFmpeg command list.
            merged_paths: List of paths to images and videos.
            folder_path: Path to the folder containing the files.
            
        Returns:
            The updated command list.
        """
        image_extensions = ['.jpg', '.jpeg']
        video_extensions = ['.mp4']
        
        for i, file_path in enumerate(merged_paths):
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Check if the file is named "outro.mp4" and has a video extension
            if "outro.mp4" in file_path.lower() and file_extension in video_extensions:
                # Add input arguments for the "outro.mp4" video
                command.extend(['-i', file_path])
            else:
                # Check if the file has an image extension
                if file_extension in image_extensions:
                    # Add input arguments for an image
                    command.extend([
                        '-loop', '1',
                        '-t', str(self.config.segment_duration),
                        '-color_range', 'jpeg',
                        '-i', os.path.join(folder_path, file_path)
                    ])
                
                # Check if the file has a video extension
                elif file_extension in video_extensions:
                    # Add input arguments for a video
                    command.extend(['-i', os.path.join(folder_path, file_path)])
                
                # Handle other file types or unsupported extensions
                else:
                    print(f"Skipping file {file_path} with unsupported extension")
        
        return command
    
    def _add_subscribe_overlay(self, folder_path: str) -> None:
        """Add subscribe overlay to the video.
        
        Args:
            folder_path: Path to the folder containing the slideshow.
        """
        subscribe_script = 'subscribe.py'
        subscribe_args = [
            '--i', folder_path,
            '--n', f'"{self.config.model_name}"',
            '--f', str(self.config.fontsize),
            '--o', str(self.config.video_orientation)
        ]
        
        # Construct the full command to run subscribe.py with arguments
        subscribe_command = ['python3', subscribe_script] + subscribe_args
        
        # Run the subscribe.py script with arguments
        subprocess.run(subscribe_command, check=True)
    
    def process_all_folders(self) -> None:
        """Process all folders in the result directory."""
        root_folder = os.path.join(self.config.input_folder, 'RESULT')
        
        for folder_name in os.listdir(root_folder):
            folder_path = os.path.join(root_folder, folder_name)
            
            # If there is slideshow.mp4 file, skip it
            if os.path.isfile(os.path.join(folder_path, 'slideshow.mp4')):
                print(f"----- Slideshow already exists in {folder_path}")
                continue
            elif os.path.isdir(folder_path):
                self.create_slideshow(folder_path)
