#!/usr/bin/env python3
"""
VideoCutter - Main entry point for the video processing application.

This script orchestrates the entire video processing pipeline, from raw input files
to the final slideshow with audio, transitions, and effects. It follows a sequential
workflow that processes videos and images, applies effects, creates a slideshow,
and adds audio and overlays.

The workflow consists of the following steps:
1. Parse command-line arguments for configuration
2. Process videos (split into segments)
3. Process images (resize, format)
4. Handle audio files (copy to source and result folders)
5. Run cleaner to remove short videos
6. Run sorter to organize files into date-time folders
7. Run depth processor to apply 3D effects (if enabled)
8. Create slideshow with transitions and effects
9. Add audio and overlays to create the final video

Usage:
    python main.py [options]

Options:
    --n MODEL_NAME      Model name for the video
    --w WATERMARK       Watermark text
    --f FONT_SIZE       Font size for text
    --d DURATION        Segment duration in seconds
    --tl TIME_LIMIT     Maximum time limit in seconds
    --z DEPTHFLOW       Use DepthFlow for images (0/1)
    --i INPUT_FOLDER    Input folder path
    --o ORIENTATION     Video orientation (vertical/horizontal)
    --b BLUR            Add blur effect (0/1)
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
    """
    Main entry point for the application.
    
    This function orchestrates the entire video processing pipeline:
    1. Parses command-line arguments
    2. Initializes processors
    3. Processes videos and images
    4. Handles audio files
    5. Runs cleaner, sorter, and depth processor
    6. Creates the final slideshow
    
    The function times the entire process and prints progress messages
    to keep the user informed about the current stage of processing.
    """
    # Start timing the entire process for performance tracking
    start_time = time.time()
    
    # Parse command-line arguments to get configuration settings
    # This includes model name, watermark, font size, segment duration, etc.
    config = parse_arguments()
    
    # Initialize the video processor with the configuration
    # This processor handles video splitting, cleaning, sorting, and depth effects
    video_processor = VideoProcessor(config)
    
    # Process videos in the input folder
    # This splits videos into segments of the specified duration
    # and backs up original files to the SOURCE folder
    print("##### Processing videos...")
    video_processor.process_videos()
    
    # Initialize the image processor with the configuration
    # This processor handles image resizing, formatting, and effects
    image_processor = ImageProcessor(config)
    
    # Process images in the input folder
    # This resizes images to the target dimensions and applies formatting
    # based on the selected orientation (vertical/horizontal)
    print("##### Processing images...")
    image_processor.process_images(config.input_folder, config.result_folder, video_processor.source_date_folder)
    
    # Process audio files (typically voiceover)
    # This copies the original audio to the source folder for backup
    # and moves the audio to the result folder for processing
    print("##### Processing audio files...")
    audio_files = [f for f in os.listdir(config.input_folder) if f.endswith('.mp3')]
    for audio_file in audio_files:
        input_path = os.path.join(config.input_folder, audio_file)
        
        # Copy original audio to the source folder for backup
        shutil.copy(input_path, os.path.join(video_processor.source_date_folder, audio_file))
        
        # Move the audio to the result folder for processing
        shutil.move(input_path, os.path.join(config.result_folder, audio_file))
    
    print(f'##### Voiceover moved to {config.result_folder}')
    
    # Run cleaner to remove videos shorter than the specified duration
    # This ensures quality control by removing segments that are too short
    print(f'##### Delete videos shorter than {config.segment_duration}s')
    video_processor.run_cleaner()
    
    # Run sorter to organize files into date-time folders
    # This renames files for consistency and moves them to the appropriate folders
    print(f'##### Rename and move to {config.result_folder}/{config.datetime_str}')
    video_processor.run_sorter()
    
    # Run depth processor if enabled (config.depthflow = 1)
    # This applies 3D parallax effects to static images
    print(f'##### Create slideshow {str(config.segment_duration - 1)}s per frame')
    video_processor.run_depth_processor()
    
    # Create slideshow from processed media
    # This combines images and videos with transitions and effects
    # and adds audio and overlays to create the final video
    print("##### Creating slideshow...")
    slideshow_creator = SlideshowCreator(config)
    slideshow_creator.process_all_folders()
    
    # Print completion message with total processing time
    elapsed_time = time.time() - start_time
    print(f"Slideshow creation complete: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes).")
    print("###### SLIDESHOW READY ######")


if __name__ == "__main__":
    main()
