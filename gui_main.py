#!/usr/bin/env python3
"""
VideoCutter GUI - Main entry point for the GUI application.

This script launches the graphical user interface for the VideoCutter application.
"""

from video_processing.gui import VideoCutterGUI


def main():
    """Main entry point for the GUI application."""
    gui = VideoCutterGUI()
    gui.run()


if __name__ == "__main__":
    main()
