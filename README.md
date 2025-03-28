# VideoCutter

A comprehensive video processing tool for cutting, processing, and creating slideshows from videos and images.

## Features

- Split videos into segments of specified duration
- Process images for slideshows
- Create slideshows with transitions and effects
- Add audio and overlays to slideshows
- Support for both vertical and horizontal video orientations
- Optional depth flow effects
- Configurable settings via GUI or command line

## Project Structure

```
VideoCutter/
├── config/                  # Configuration files
│   ├── vertical_config.json   # Configuration for vertical videos
│   └── horizontal_config.json # Configuration for horizontal videos
├── docs/                    # Documentation
├── INPUT/                   # Input folder for videos and images
│   ├── RESULT/              # Processed videos and images
│   └── SOURCE/              # Original files backup
├── TEMPLATE/                # Template files for overlays and audio
├── tests/                   # Test suite
│   └── unit/                # Unit tests
├── video_processing/        # Core processing modules
│   ├── audio.py             # Audio processing functionality
│   ├── config.py            # Configuration management
│   ├── gui.py               # Graphical user interface
│   ├── image.py             # Image processing functionality
│   ├── slideshow.py         # Slideshow creation functionality
│   ├── utils.py             # Utility functions
│   └── video.py             # Video processing functionality
├── gui_main.py              # GUI entry point
├── main.py                  # Command line entry point
└── pytest.ini               # Pytest configuration
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/VideoCutter.git
   cd VideoCutter
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode

To use the graphical user interface:

```
python gui_main.py
```

The GUI allows you to:
- Select configuration files
- Set model name and watermark text
- Configure segment duration and time limits
- Choose between vertical and horizontal video orientations
- Enable/disable depth flow and blur effects
- Save and load configurations

### Command Line Mode

To use the command line interface:

```
python main.py [options]
```

Available options:
- `--n`: Model name
- `--w`: Watermark text
- `--f`: Font size
- `--d`: Segment duration (in seconds)
- `--tl`: Time limit (in seconds)
- `--z`: Use DepthFlow for images (0/1)
- `--i`: Input folder
- `--o`: Video orientation (vertical/horizontal)
- `--b`: Add blur (0/1)

Example:
```
python main.py --n "Model Name" --w "Watermark Text" --f 90 --d 6 --o horizontal
```

## Testing

Run the test suite with:

```
pytest
```

For test coverage report:

```
pytest --cov
```

## Workflow

1. Place videos and images in the `INPUT` folder
2. Run the application (GUI or command line)
3. The application will:
   - Split videos into segments
   - Process images
   - Create a slideshow with transitions
   - Add audio and overlays
4. The final video will be saved in the `INPUT/RESULT/[timestamp]` folder

## License

[Your License Here]
