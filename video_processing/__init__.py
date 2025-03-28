"""
VideoCutter - A modular video processing package for cutting, processing, and creating slideshows.

This package provides a comprehensive toolkit for video processing, image manipulation,
audio processing, and slideshow creation. It is designed to automate the creation of
professional-quality slideshows from images and videos with minimal user intervention.

Key Features:
- Video cutting and segmentation (split videos into configurable segments)
- Image processing and manipulation (resize, crop, apply effects)
- Audio processing and mixing (soundtrack, voiceover, transitions)
- Slideshow creation with transitions and effects
- 3D parallax effects for static images (via DepthFlow)
- Branding and subscription overlays
- Support for both vertical (9:16) and horizontal (16:9) video formats
- Configuration management via GUI or command line

Module Structure:
- config.py: Configuration management and command-line parsing
- utils.py: Utility functions for file operations and common tasks
- video.py: Video processing functionality (cutting, cleaning, sorting)
- image.py: Image processing functionality (resizing, formatting, effects)
- audio.py: Audio processing functionality (mixing, effects)
- slideshow.py: Slideshow creation functionality (transitions, effects)
- gui.py: Graphical user interface for configuration and execution

The package is designed to be used either through the command-line interface
(main.py) or the graphical user interface (gui_main.py).

Example Usage:
    from video_processing.config import parse_arguments
    from video_processing.video import VideoProcessor
    
    config = parse_arguments()
    processor = VideoProcessor(config)
    processor.process_videos()
"""

__version__ = "1.0.0"
__author__ = "VideoCutter Team"
__license__ = "Proprietary"
__copyright__ = "Copyright 2025"
