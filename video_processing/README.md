# Video Processing Package

This package contains the core modules for the VideoCutter application. It provides functionality for video processing, image manipulation, audio processing, and slideshow creation.

## Modules

### `__init__.py`

Package initialization file that defines the package version and provides a brief description.

### `config.py`

Configuration module that provides:
- `VideoConfig` class for managing all settings
- `parse_arguments()` function for parsing command-line arguments

### `utils.py`

Utility functions used across the application:
- File operations (finding videos, creating directories)
- Video analysis (duration, dimensions, aspect ratio)
- Timestamp folder creation

### `video.py`

Video processing functionality:
- `VideoProcessor` class for processing videos
- Methods for splitting videos into segments
- Integration with cleaner, sorter, and depth processor

### `image.py`

Image processing functionality:
- `ImageProcessor` class for processing images
- Methods for resizing, cropping, and applying effects
- Support for different image orientations and aspect ratios

### `audio.py`

Audio processing functionality:
- `AudioProcessor` class for processing audio
- Methods for adding audio to videos
- Audio mixing, compression, and effects

### `slideshow.py`

Slideshow creation functionality:
- `SlideshowCreator` class for creating slideshows
- Methods for combining images and videos with transitions
- Integration with audio processing and overlay addition

### `gui.py`

Graphical user interface:
- `VideoCutterGUI` class for the application GUI
- Configuration management (loading, saving)
- User interface elements and event handling

## Usage

The modules in this package are designed to be used together to create a complete video processing pipeline. The typical workflow is:

1. Parse configuration from command line or GUI
2. Process videos (split into segments)
3. Process images (resize, crop, apply effects)
4. Create slideshow with transitions
5. Add audio and overlays

Example:

```python
from video_processing.config import parse_arguments
from video_processing.video import VideoProcessor
from video_processing.image import ImageProcessor
from video_processing.slideshow import SlideshowCreator

# Parse configuration
config = parse_arguments()

# Initialize processors
video_processor = VideoProcessor(config)
image_processor = ImageProcessor(config)
slideshow_creator = SlideshowCreator(config)

# Process videos and images
video_processor.process_videos()
image_processor.process_images(config.input_folder, config.result_folder, video_processor.source_date_folder)

# Create slideshow
slideshow_creator.process_all_folders()
```

## Extension

To extend the functionality of this package:

1. Add new methods to existing classes for related functionality
2. Create new modules for entirely new features
3. Update the main entry points (`main.py` and `gui_main.py`) to use the new functionality
