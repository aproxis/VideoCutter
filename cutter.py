#!/usr/bin/env python3
"""
Video processing pipeline main script.
Uses the video_processing package for modular functionality.
"""

import argparse
from video_processing import VideoConfig, VideoPipeline

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', type=int, default=6, dest='segment_duration', 
                      help='Duration of each segment (in seconds)')
    parser.add_argument('--tl', type=int, default=595, dest='time_limit', 
                      help='Duration of clip')
    parser.add_argument('--i', type=str, default='INPUT', dest='input_folder', 
                      help='Input folder')
    parser.add_argument('--n', type=str, default='Model Name', dest='model_name', 
                      help='Model name')
    parser.add_argument('--f', type=int, default=90, dest='fontsize', 
                      help='Font size')
    parser.add_argument('--w', type=str, default='Today is a\\n Plus Day', 
                      dest='watermark', help='Watermark text')
    parser.add_argument('--z', type=str, default='0', dest='depthflow', 
                      help='Use DepthFlow for images? 0/1')
    parser.add_argument('--o', type=str, default='vertical', 
                      dest='video_orientation', help='Video orientation (vertical|horizontal)')
    parser.add_argument('--b', type=str, default='0', dest='blur', 
                      help='Add blur? 0/1')

    args = parser.parse_args()
    
    # Initialize configuration
    config = VideoConfig()
    config.update_from_args(args)
    
    # Run the pipeline
    pipeline = VideoPipeline(config)
    pipeline.run()

if __name__ == '__main__':
    main()
