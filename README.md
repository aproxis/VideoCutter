# VideoCutter

A comprehensive video processing toolkit for creating professional slideshows from images and videos with depth effects, audio processing, and custom overlays.

## Overview

VideoCutter automates the process of creating engaging video content from images and video clips. It provides a complete pipeline from processing raw media to producing polished slideshows with depth effects, transitions, audio mixing, and custom branding.

![VideoCutter GUI](https://via.placeholder.com/800x500?text=VideoCutter+GUI)

## Features

- **Video Processing**
  - Split videos into segments of configurable duration
  - Filter videos based on aspect ratio and minimum duration
  - Process both vertical (9:16) and horizontal (16:9) content

- **Image Enhancement**
  - Resize and crop images to target dimensions
  - Apply blur effects and gradients for professional look
  - Support for both vertical and horizontal orientations

- **DepthFlow Integration**
  - Create 3D parallax effects from static images
  - Configurable animations (Circle, Orbital, Dolly, Horizontal)
  - Customizable depth parameters

- **Slideshow Creation**
  - Smooth transitions between media elements
  - Random transition effects for visual variety
  - Configurable slide duration and watermarks

- **Audio Processing**
  - Mix soundtrack, voiceover, and transition sounds
  - Sidechain compression for professional audio quality
  - Automatic audio timing and synchronization

- **Branding & Customization**
  - Add model name and custom watermarks
  - Configurable font sizes and colors
  - Subscribe/like overlays for social media engagement

- **User-Friendly Interface**
  - Graphical user interface for easy configuration
  - Save and load configuration presets
  - Real-time font size calculation based on text length

## Directory Structure

```
VideoCutter/
├── config/                  # Configuration presets
├── INPUT/                   # Input media files
│   ├── DEPTH/               # Images for depth processing
│   ├── RESULT/              # Processed output (date-time folders)
│   └── SOURCE/              # Original files backup
├── TEMPLATE/                # Template files for overlays and audio
├── memory-bank/             # Project documentation and context
├── *.py                     # Python scripts
└── README.md                # This documentation
```

## Requirements

### Software Dependencies

- Python 3.x
- FFmpeg (for video and audio processing)
- PIL/Pillow (for image processing)
- DepthFlow (for depth effects)
- Tkinter (for GUI)

### Python Packages

See `requirements.txt` for a complete list of dependencies. Key packages include:

```
pillow>=10.4.0
numpy>=1.26.4
opencv-contrib-python>=4.10.0
pydub>=0.25.1
tqdm>=4.66.6
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/aproxis/VideoCutter.git
   cd VideoCutter
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg:
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

4. Install DepthFlow (if using depth effects):
   ```
   pip install DepthFlow
   ```

5. Set up directory structure:
   ```
   mkdir -p config INPUT/DEPTH TEMPLATE
   ```

6. Add required template files to the TEMPLATE directory (see TEMPLATE/README.md for details)

## Core Components

### 1. GUI Interface (`gui.py`)
The graphical user interface for configuring and starting the processing pipeline. Features include:
- Configuration preset management (save, load, delete)
- Model name and watermark text input
- Font size calculation and customization
- Segment duration and time limit settings
- Video orientation selection (vertical/horizontal)
- DepthFlow and blur effect toggles

### 2. Video Processing (`cutter.py`)
The main entry point that orchestrates the entire workflow:
- Splits videos into segments of specified duration
- Processes images for the target aspect ratio
- Organizes files into date-time folders
- Calls subsequent scripts in the pipeline

### 3. Quality Control (`cleaner.py`)
Ensures quality by removing videos that don't meet requirements:
- Removes videos shorter than specified duration
- Validates video formats and properties

### 4. File Organization (`sorter.py`)
Manages file organization and naming:
- Creates date-time stamped folders
- Renames files for consistent processing
- Backs up original files

### 5. Depth Effects (`depth.py`)
Applies 3D parallax effects to static images:
- Creates depth maps from 2D images
- Applies various animation patterns
- Processes in parallel for performance

### 6. Slideshow Creation (`slideshow.py`)
Combines processed media into a cohesive slideshow:
- Adds transitions between segments
- Applies watermark and text overlays
- Creates the base slideshow structure

### 7. Audio Processing (`audio.py`)
Handles all audio-related processing:
- Mixes soundtrack with voiceover
- Adds transition sound effects
- Applies audio effects and normalization

### 8. Branding (`subscribe.py`)
Adds final branding and subscription overlays:
- Integrates model name overlay
- Adds subscribe/like animations
- Finalizes the video for distribution

## Usage

### Quick Start

1. Set up your environment:
   ```
   # Clone the repository
   git clone https://github.com/aproxis/VideoCutter.git
   cd VideoCutter
   
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create necessary directories
   mkdir -p INPUT/DEPTH INPUT/RESULT INPUT/SOURCE
   ```

2. Prepare your media:
   - Place images and videos in the `INPUT` folder
   - Add background music as `TEMPLATE/music.mp3` (optional)
   - Add voiceover as `INPUT/voiceover.mp3` (optional)

3. Launch the application:
   ```
   python gui.py
   ```

### GUI Mode

1. Configure your settings:
   - Set model name and watermark text
   - Adjust font size and segment duration
   - Choose video orientation (vertical/horizontal)
   - Enable/disable depth effects
   - Set time limits

2. Click "START" to begin processing

3. Find your results in the `INPUT/RESULT/[datetime]/` folder

### Command Line Mode

For batch processing or automation, you can use the command line interface:

```
python cutter.py --n "Model Name" --w "Your Watermark" --d 6 --o vertical --z 1
```

#### Parameters:

- `--d`: Segment duration in seconds (default: 6)
- `--tl`: Time limit in seconds (default: 595)
- `--i`: Input folder (default: 'INPUT')
- `--n`: Model name (default: 'Model Name')
- `--f`: Font size (default: 90)
- `--w`: Watermark text (default: 'Today is a\n Plus Day')
- `--z`: Use DepthFlow (0/1, default: 0)
- `--o`: Video orientation (vertical/horizontal, default: vertical)
- `--b`: Add blur (0/1, default: 0)

## Workflow

1. **Input Preparation**:
   - Place your images and videos in the `INPUT` folder
   - Add voiceover as `voiceover.mp3` (optional)

2. **Processing Pipeline**:
   - Videos are split into segments of specified duration
   - Images are processed and resized
   - Files are organized into date-time folders
   - Depth effects are applied (if enabled)
   - Slideshow is created with transitions
   - Audio is added and mixed
   - Subscription overlays are added

3. **Output**:
   - Final videos are saved in `INPUT/RESULT/[datetime]/`
   - Original files are backed up in `INPUT/SOURCE/[datetime]/`

## Configuration Files

The `config/` directory contains JSON configuration presets that can be loaded and saved from the GUI:

```json
{
  "model_name": "Model Name",
  "watermark": "Your Watermark Text",
  "font_size": 90,
  "segment_duration": 6,
  "input_folder": "INPUT",
  "depthflow": 0,
  "time_limit": 600,
  "video_orientation": "vertical",
  "blur": 0
}
```

## Advanced Features

### DepthFlow Animations

When enabled, DepthFlow creates 3D parallax effects from static images with randomly selected animations:

- **Circle**: Camera moves in a circular pattern
- **Orbital**: Camera orbits around the subject
- **Dolly**: Camera moves forward/backward
- **Horizontal**: Camera pans horizontally

Parameters like isometric view, height, and zoom are randomized for variety.

### Image Processing

The image processing pipeline includes:

1. Aspect ratio detection and appropriate resizing
2. Gradient edge effects for smooth transitions
3. Blur effects for background enhancement
4. Orientation-specific processing for vertical/horizontal output

### Audio Processing

The audio pipeline includes:

1. Soundtrack processing with fade in/out
2. Transition sound mixing
3. Voiceover integration with 5-second lead-in
4. Sidechain compression for clear voiceover
5. Final audio mixing and normalization

### Custom Overlays

The subscribe overlay adds:

- Model name with configurable font size
- Subscribe/like buttons
- Custom colors and animations

## Troubleshooting

### Common Issues

- **FFmpeg errors**: Ensure FFmpeg is properly installed and in your PATH
- **Missing files**: Check that all template files exist in the TEMPLATE directory
- **Processing errors**: Verify input files are in supported formats (MP4, JPG)
- **Audio sync issues**: Check that voiceover.mp3 exists in the INPUT folder

### Logs

Check the terminal output for detailed processing logs and error messages. The depth processing also creates a `_depth_log.txt` file in the output directory.

## Performance Considerations

- **Memory Usage**: DepthFlow processing requires significant RAM (8GB+ recommended)
- **Processing Time**: Typical processing takes 2-5 minutes per minute of output video
- **Storage**: Ensure at least 10GB of free space for temporary files and outputs
- **GPU Acceleration**: DepthFlow benefits from GPU acceleration if available

## Future Development

Planned enhancements include:

- Comprehensive error handling throughout the pipeline
- Progress indicators during processing
- Additional transition types and effects
- Direct social media publishing integration
- Batch processing capabilities

## License

[MIT License](LICENSE)

## Credits

- FFmpeg for video and audio processing
- DepthFlow for 3D parallax effects
- All contributors to this project
