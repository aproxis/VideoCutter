#!/usr/bin/env python3
"""
VideoCutter - Main entry point for the video processing application.

This script processes videos and images to create slideshows with audio and effects.
"""

import os
import shutil
import time
from datetime import datetime

from video_processing.config import parse_arguments, VideoConfig
from video_processing.video import VideoProcessor
from video_processing.image import ImageProcessor
from video_processing.slideshow import SlideshowCreator


def main():
    """Main entry point for the application."""
    # Start timing the entire process
    start_time = time.time()
    
    # Parse command-line arguments
    config = parse_arguments()
    
    # Initialize processors
    video_processor = VideoProcessor(config)
    
    # Process videos
    video_processor.process_videos()
    
    # Process images
    image_processor = ImageProcessor(config)
    image_processor.process_images(config.input_folder, config.result_folder, video_processor.source_date_folder)
    
    # Process audio files
    audio_files = [f for f in os.listdir(config.input_folder) if f.endswith('.mp3')]
    for audio_file in audio_files:
        input_path = os.path.join(config.input_folder, audio_file)
        
        # Copy original audio to the source folder
        shutil.copy(input_path, os.path.join(video_processor.source_date_folder, audio_file))
        
        # Move the audio to the result folder
        shutil.move(input_path, os.path.join(config.result_folder, audio_file))
    
    print(f'##### Voiceover moved to {config.result_folder}')
    
    # Run cleaner to remove short videos
    print(f'##### Delete videos shorter than {config.segment_duration}s')
    video_processor.run_cleaner()
    
    # Run sorter to organize files
    print(f'##### Rename and move to {config.result_folder}/{config.datetime_str}')
    video_processor.run_sorter()
    
    # Run depth processor if enabled
    print(f'##### Create slideshow {str(config.segment_duration - 1)}s per frame')
    video_processor.run_depth_processor()
    
    # Create slideshow
    slideshow_creator = SlideshowCreator(config)
    slideshow_creator.process_all_folders()
    
    # Print completion message
    print(f"Slideshow creation complete: {time.time() - start_time:.2f} seconds.")
    print("###### SLIDESHOW READY ######")


if __name__ == "__main__":
    main()
