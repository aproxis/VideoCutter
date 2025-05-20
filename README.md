# VideoCutter

A comprehensive video processing toolkit for creating professional slideshows from images and videos with depth effects, audio processing, custom overlays, and advanced subtitle support.

## Overview

VideoCutter automates the process of creating engaging video content from images and video clips. It provides a complete pipeline from processing raw media to producing polished slideshows with depth effects, transitions, audio mixing, custom branding, and professional subtitles. The project is currently in a functional beta state and is preparing for a significant refactoring of its core scripts to enhance modularity and maintainability.

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

- **Advanced Subtitle System**
  - SRT subtitle integration with videos
  - Custom font selection from fonts/ directory
  - Advanced styling with shadow and outline effects
  - Real-time preview in GUI
  - Configurable positioning and colors

- **User-Friendly Interface**
  - Graphical user interface for easy configuration
  - Save and load configuration presets
  - Real-time font size calculation based on text length
  - Live subtitle preview with accurate rendering

## Directory Structure

```
VideoCutter/
├── config/                  # Configuration presets
├── fonts/                   # Custom fonts for text and subtitles
├── INPUT/                   # Input media files
│   ├── RESULT/              # Processed output (date-time folders)
│   ├── SOURCE/              # Original files backup
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
curl -L https://evermeet.cx/ffmpeg/ffmpeg-7.1.1.zip -o ffmpeg.zip
curl -L https://evermeet.cx/ffmpeg/getrelease/ffprobe/7.0 -o ffprobe.zip
unzip ffmpeg.zip
unzip ffprobe.zip
sudo mv ffmpeg /usr/local/bin/
sudo mv ffprobe /usr/local/bin/
sudo chmod +x /usr/local/bin/ffmpeg
sudo chmod +x /usr/local/bin/ffprobe

brew install python-tk@3.11
brew install python@3.11 

python3.11 -m venv venv
source venv/bin/activate

pip install Pillow
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1
pip install transformers==4.47.0
pip install depthflow==0.8.0
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
   mkdir -p config INPUT/DEPTH INPUT/subs TEMPLATE fonts
   ```

6. Add required template files to the TEMPLATE directory (see TEMPLATE/README.md for details)

7. Add custom fonts to the fonts directory (optional, for subtitle and text styling)

## Core Components

### 1. GUI Interface (`gui.py`)
The graphical user interface for configuring and starting the processing pipeline. Features include:
- Configuration preset management (save, load, delete)
- Model name and watermark text input
- Font size calculation and customization
- Segment duration and time limit settings
- Video orientation selection (vertical/horizontal)
- DepthFlow and blur effect toggles
- Subtitle styling and preview

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

### 8. Branding & Subtitles (`subscribe.py`)
Adds final branding, subscription overlays, and subtitles:
- Integrates model name overlay
- Adds subscribe/like animations
- Applies subtitles with advanced styling
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
   mkdir -p INPUT/DEPTH INPUT/RESULT INPUT/SOURCE INPUT/subs fonts
   ```

2. Prepare your media:
   - Place images and videos in the `INPUT` folder
   - Add custom fonts to the `fonts` directory

3. Launch the application:
   ```
   python gui.py
   ```

### GUI Mode

1. Configure your settings:
   - Set title and watermark text
   - Adjust font size and segment duration
   - Choose video orientation (vertical/horizontal)
   - Enable/disable depth effects
   - Set time limits
   - Configure subtitle styling (if using subtitles)

2. Click "START" to begin processing

3. Find your results in the `INPUT/RESULT/[datetime]/` folder

### Command Line Mode

For batch processing or automation, you can use the command line interface:

```
python cutter.py --n "Model Name" --w "Your Watermark" --d 6 --o vertical --z 1 --srt 1
```

#### Basic Parameters:

- `--d`: Segment duration in seconds (default: 6)
- `--tl`: Time limit in seconds (default: 595)
- `--i`: Input folder (default: 'INPUT')
- `--n`: Model name (default: 'Model Name')
- `--f`: Font size (default: 90)
- `--w`: Watermark text (default: 'Today is a\n Plus Day')
- `--z`: Use DepthFlow (0/1, default: 0)
- `--o`: Video orientation (vertical/horizontal, default: vertical)
- `--b`: Add blur (0/1, default: 0)

#### Subtitle Parameters:

- `--srt`: Add SRT subtitles (0/1, default: 0)
- `--sf`: Font for subtitles (default: 'Arial')
- `--sfs`: Subtitle font size (default: 24)
- `--sfc`: Subtitle font color (hex without #, default: 'FFFFFF')
- `--sbc`: Subtitle shadow color (hex without #, default: '000000')
- `--sbo`: Subtitle shadow opacity (0-1, default: 0.5)
- `--spos`: Subtitle position (1-9, ASS alignment, default: 2)
- `--sout`: Subtitle outline thickness (default: 1)
- `--soutc`: Subtitle outline color (hex without #, default: '000000')
- `--shadow`: Enable subtitle shadow (0/1, default: 1)
- `--smaxw`: Maximum characters per subtitle line (default: 21)

## Workflow

1. **Input Preparation**:
   - Place your images and videos in the `INPUT` folder
   - Add voiceover as `voiceover.mp3` (optional)
   - Add subtitle file as `subs/voiceover.srt` (optional)
   - Add custom fonts to the `fonts` directory (optional)

2. **Processing Pipeline**:
   - Videos are split into segments of specified duration
   - Images are processed and resized
   - Files are organized into date-time folders
   - Depth effects are applied (if enabled)
   - Slideshow is created with transitions
   - Audio is added and mixed
   - Subscription overlays are added
   - Subtitles are rendered with styling (if enabled)

3. **Output**:
   - Final videos are saved in `INPUT/RESULT/[datetime]/`
   - Original files are backed up in `INPUT/SOURCE/[datetime]/`

## Configuration Files

The `config/` directory contains JSON configuration presets that can be loaded and saved from the GUI:

```json
{
  "title": "Model Name",
  "watermark": "Your Watermark Text",
  "title_font_size": 90,
  "segment_duration": 6,
  "input_folder": "INPUT",
  "depthflow": 0,
  "time_limit": 600,
  "video_orientation": "vertical",
  "blur": 0,
  "generate_srt": false,
  "subtitle_font": "Arial",
  "subtitle_fontsize": 24,
  "subtitle_fontcolor": "FFFFFF",
  "subtitle_bgcolor": "000000",
  "subtitle_bgopacity": 0.5,
  "subtitle_position": 2,
  "subtitle_outline": 1,
  "subtitle_outlinecolor": "000000",
  "subtitle_shadow": true
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

### Subtitle System

The subtitle system provides advanced styling options:

1. **Font Selection**: Choose from custom fonts in the fonts/ directory
2. **Color Customization**: Set text, outline, and shadow colors
3. **Shadow Effects**: Add drop shadows with configurable opacity
4. **Outline Effects**: Add text outlines with configurable thickness
5. **Positioning**: 9-point positioning system (1-9 ASS alignment)
6. **Real-time Preview**: See exactly how subtitles will appear in the final video
7. **SRT Integration**: Use standard SRT files for subtitle content

## Subtitle Format

The system uses SRT files for subtitle content:

```
1
00:00:01,000 --> 00:00:04,000
This is a subtitle

2
00:00:05,000 --> 00:00:08,000
With multiple lines
```

SRT file will be generated in `INPUT/{datetime_folder}/subs/voiceover.srt` for automatic integration.

## Troubleshooting

### Common Issues

- **FFmpeg errors**: Ensure FFmpeg is properly installed and in your PATH
- **Missing files**: Check that all template files exist in the TEMPLATE directory
- **Processing errors**: Verify input files are in supported formats (MP4, JPG)
- **Audio sync issues**: Check that voiceover.mp3 exists in the INPUT folder
- **Subtitle issues**: Verify SRT file format and placement in INPUT/subs directory
- **Font issues**: Ensure custom fonts are in the fonts/ directory and in TTF or OTF format

### Logs

Check the terminal output for detailed processing logs and error messages. The depth processing also creates a `_depth_log.txt` file in the output directory.

## Performance Considerations

- **Memory Usage**: DepthFlow processing requires significant RAM (8GB+ recommended)
- **Processing Time**: Typical processing takes 2-5 minutes per minute of output video
- **Storage**: Ensure at least 10GB of free space for temporary files and outputs
- **GPU Acceleration**: DepthFlow benefits from GPU acceleration if available

## Future Development

The immediate next major step is a **Core Script Refactoring** to improve modularity, maintainability, and scalability by breaking down main processing scripts into smaller, specialized modules managed by a central controller.

Planned enhancements also include:

- Comprehensive error handling throughout the pipeline
- Progress indicators during processing
- Additional transition types and effects
- Direct social media publishing integration
- Batch processing capabilities
- Multiple subtitle track support
- Subtitle timing adjustment
- Advanced text formatting options
- Subtitle editor with timeline

## License

[MIT License](LICENSE)

## Credits

- FFmpeg for video and audio processing
- DepthFlow for 3D parallax effects
- All contributors to this project
