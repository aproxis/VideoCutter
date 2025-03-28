#!/usr/bin/env python3
"""
VideoCutter GUI - Main entry point for the GUI application.

This script launches the graphical user interface for the VideoCutter application.
It provides a user-friendly interface for configuring and running the video processing
pipeline without needing to use command-line arguments.

The GUI allows users to:
1. Select or create configuration presets
2. Set model name, watermark text, and font size
3. Configure segment duration and time limits
4. Choose between vertical and horizontal video orientations
5. Enable/disable depth flow and blur effects
6. Save and load configurations
7. Start the video processing pipeline with a single click

Usage:
    python gui_main.py

The GUI is implemented using Tkinter and provides a simple, intuitive interface
for users who prefer not to use the command line. It offers the same functionality
as the command-line interface but with visual controls and configuration management.
"""

from video_processing.gui import VideoCutterGUI


def main():
    """
    Main entry point for the GUI application.
    
    This function initializes the VideoCutterGUI class and starts the main event loop.
    The GUI provides a user-friendly interface for configuring and running the
    video processing pipeline.
    
    The GUI allows users to:
    - Select configuration presets from dropdown menu
    - Configure all processing parameters through form fields
    - Save, load, and delete configuration presets
    - Start the processing pipeline with a single button click
    
    No command-line arguments are needed as all configuration is done through the GUI.
    """
    # Initialize the GUI
    gui = VideoCutterGUI()
    
    # Start the main event loop
    # This will display the GUI and handle user interactions
    gui.run()


if __name__ == "__main__":
    main()
