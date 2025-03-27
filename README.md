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

```
pillow
numpy
click
attr
dotmap
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/VideoCutter.git
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

## Usage

### GUI Mode

1. Launch the GUI:
   ```
   python gui.py
   ```

2. Configure your settings:
   - Set model name and watermark text
   - Adjust font size and segment duration
   - Choose video orientation (vertical/horizontal)
   - Enable/disable depth effects
   - Set time limits

3. Click "START" to begin processing

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

Check the terminal output for detailed processing logs and error messages.

## License

[MIT License](LICENSE)

## Credits

- FFmpeg for video and audio processing
- DepthFlow for 3D parallax effects
- All contributors to this project
