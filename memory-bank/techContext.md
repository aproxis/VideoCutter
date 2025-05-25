# Technical Context: VideoCutter

## Technologies Used

### Core Technologies

1.  **Python 3.x**
    - Primary programming language
    - Used for all script components
    - Provides cross-platform compatibility
    - Extensive library ecosystem

2.  **FFmpeg**
    - Core video and audio processing engine
    - Handles video splitting, merging, and effects
    - Manages audio mixing and synchronization
    - Provides format conversion and optimization
    - Renders subtitles with ASS styling

3.  **Tkinter**
    - GUI framework for the configuration interface
    - Native integration with Python
    - Cross-platform compatibility
    - Lightweight and simple implementation

4.  **PIL/Pillow**
    - Image processing library
    - Handles image resizing, cropping, and effects
    - Manages watermark application
    - Provides format conversion
    - Used for subtitle preview rendering

5.  **DepthFlow**
    - 3D parallax effect generation
    - Creates depth maps from 2D images
    - Applies motion effects to static images
    - Integrates with PyTorch for ML-based depth estimation

### Supporting Technologies

1.  **JSON**
    - Configuration file format
    - Stores preset parameters
    - Enables easy serialization/deserialization
    - Human-readable format

2.  **Subprocess**
    - Manages external process execution
    - Handles FFmpeg command execution
    - Provides process monitoring and control
    - Used by modular components for external calls.

3.  **OS/Shutil**
    - File system operations
    - Directory management
    - File moving and copying
    - Path manipulation
    - Used extensively by `videocutter/utils/file_utils.py` and other processing modules.

4.  **Argparse**
    - Command-line argument parsing
    - Used by the main `gui.py` and `videocutter/main.py` for initial setup. Older monolithic scripts also used it.

5.  **PyTorch** (via DepthFlow)
    - Machine learning framework
    - Powers depth estimation models
    - GPU acceleration support
    - Tensor operations for image processing

6.  **Advanced SubStation Alpha (ASS)**
    - Subtitle format for advanced styling
    - Supports rich text formatting
    - Enables shadow and outline effects
    - Provides precise positioning control

7.  **DotMap**
    - Provides dot notation access to dictionaries.
    - Used by `videocutter/config_manager.py` to provide flexible access to configuration parameters.

## Development Setup

### Required Software

1.  **Python 3.x**
    - Minimum version: 3.6
    - Recommended version: 3.8+
    - Required packages: see requirements section

2.  **FFmpeg**
    - Minimum version: 4.0
    - Recommended version: 4.4+
    - Required with libx264 support

3.  **DepthFlow**
    - Custom package for depth effects
    - Requires PyTorch backend
    - GPU support recommended but not required

### Environment Setup

1.  **Python Environment**
    ```bash
    # Create virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```

2.  **FFmpeg Installation**
    ```bash
    # macOS
    brew install ffmpeg
    
    # Ubuntu/Debian
    apt-get install ffmpeg
    
    # Windows
    # Download from ffmpeg.org and add to PATH
    ```

3.  **DepthFlow Setup**
    ```bash
    # DepthFlow is typically installed via pip as part of requirements.txt
    # Ensure PyTorch is installed with appropriate CUDA support if using GPU
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 # Example for CUDA 11.8
    ```

4.  **Directory Structure**
    ```
    VideoCutter/
    ├── config/                  # Configuration presets
    ├── fonts/                   # Custom fonts for text and subtitles
    ├── INPUT/                   # Input directory for media
    │   ├── DEPTH/               # Processed depth files
    │   ├── RESULT/              # Final output videos
    │   └── SOURCE/              # Backup of source files
    ├── TEMPLATE/                # Template files for overlays and audio
    ├── memory-bank/             # Project documentation
    ├── videocutter/             # Modular Python package
    │   ├── config_manager.py
    │   ├── main.py
    │   ├── gui/
    │   │   ├── gui_utils.py
    │   │   └── title_settings_frame.py
    │   ├── processing/
    │   │   ├── audio_processor.py
    │   │   ├── depth_processor.py
    │   │   ├── overlay_compositor.py
    │   │   ├── slideshow_generator.py
    │   │   ├── subtitle_generator.py
    │   │   └── video_processor.py
    │   └── utils/
    │       ├── file_utils.py
    │       ├── font_utils.py
    │       └── gui_config_manager.py
    ├── gui.py                   # Main GUI entry point
    ├── requirements.txt         # Python dependencies
    └── *.py                     # Older monolithic scripts (to be deprecated)
    ```

5.  **Template Files**
    - Required template files in TEMPLATE directory:
        - `soundtrack.mp3`: Background music
        - `transition.mp3`: Transition sound effect
        - `transition_long.mp3`: Extended transition sound
        - `voiceover_end.mp3`: Ending voiceover
        - `outro_vertical.mp4`: Vertical outro video
        - `outro_horizontal.mp4`: Horizontal outro video
        - `name_subscribe_like.mp4`: Vertical subscription overlay
        - `name_subscribe_like_horizontal.mp4`: Horizontal subscription overlay

## Technical Constraints

### Performance Constraints

1.  **Memory Usage**
    - High memory consumption during video processing
    - DepthFlow requires significant RAM for depth estimation
    - Parallel processing increases memory requirements
    - Recommended minimum: 8GB RAM, 16GB+ preferred

2.  **Processing Time**
    - Video processing is CPU-intensive
    - DepthFlow benefits from GPU acceleration
    - Processing time scales with video resolution and duration
    - Typical processing: 2-5 minutes per minute of output video

3.  **Storage Requirements**
    - Temporary files created during processing
    - Source backups increase storage needs
    - Multiple output versions stored in date-time folders
    - Recommended free space: 10GB minimum

### Compatibility Constraints

1.  **Video Format Constraints**
    - Input videos must be MP4 format
    - 16:9 aspect ratio required for input videos
    - Output formats: vertical (9:16) or horizontal (16:9)
    - H.264 codec used for compatibility

2.  **Image Format Constraints**
    - Supported formats: JPG, JPEG
    - No specific aspect ratio requirements (auto-processed)
    - Recommended resolution: 1080p or higher

3.  **Audio Format Constraints**
    - Voiceover must be MP3 format
    - Template audio files must be MP3 format
    - Stereo audio output (2 channels)
    - AAC codec used for output

4.  **Subtitle Format Constraints**
    - Input subtitles in SRT format
    - Output subtitles rendered using ASS format
    - Custom fonts must be in TTF or OTF format
    - Font files must be in the fonts/ directory or system fonts

## Dependencies

### Python Package Dependencies

```
# From requirements.txt
pillow>=9.0.0          # Image processing
numpy>=1.20.0          # Numerical operations
click>=8.0.0           # Command-line interface
attr>=21.2.0           # Class attribute management
dotmap>=1.3.0          # Dot notation access to dictionaries
whisperx             # Audio transcription and alignment
mutagen              # Audio metadata (duration)
fonttools            # Font file inspection
```

### External Dependencies

1.  **FFmpeg**
    - Required for all video and audio processing
    - Must be available in system PATH
    - Required codecs: libx264, aac

2.  **System Fonts**
    - Required fonts:
        - Montserrat-SemiBold.otf
        - Nexa.otf
        - Arial.ttf (for subtitles)
    - Must be installed in system font directory or specified path

## Integration Points

1.  **Input Integration**
    - Manual file placement in INPUT directory
    - No direct API for file ingestion
    - Potential for future automation via watched folders

2.  **Output Integration**
    - Files saved to local filesystem
    - No direct publishing to platforms
    - Manual upload to social media required

3.  **Configuration Integration**
    - JSON configuration files
    - Managed by `videocutter/config_manager.py` and `videocutter/utils/gui_config_manager.py`.
    - GUI provides interface for creation/editing.

4.  **Process Integration**
    - GUI-triggered processing via `gui.py` calling `videocutter/main.py`.
    - No scheduling or automation built-in.

## Subtitle Processing

### Subtitle Workflow

1.  **SRT/ASS Generation**
    - `videocutter/processing/subtitle_generator.py` transcribes audio and generates SRT/ASS files.
    - Output files are used by `videocutter/processing/overlay_compositor.py`.

2.  **Styling Parameters**
    - Font selection from `fonts/` directory.
    - Font size, color, and position.
    - Outline thickness and color.
    - Shadow toggle and opacity.
    - Position using ASS alignment (1-9).

3.  **Color Handling**
    - RGB to BGR conversion for ASS format.
    - Opacity handling for shadow effects.
    - Hex color codes without # prefix.

4.  **Preview Rendering**
    - Real-time preview in GUI (`videocutter/gui/gui_utils.py`).
    - PIL/Pillow for rendering.
    - Alpha compositing for shadow effects.
    - Layer management for proper z-ordering.

5.  **FFmpeg Integration**
    - ASS style string generation by `videocutter/processing/subtitle_generator.py`.
    - Subtitle filter application by `videocutter/processing/overlay_compositor.py`.
    - Hardcoded subtitle rendering.
    - Font path resolution.

### ASS Format Specifics

The ASS subtitle format uses specific color ordering and parameters:

1.  **Color Format**: BGR (not RGB) in hexadecimal
2.  **Opacity**: Inverted scale (00=fully opaque, FF=fully transparent)
3.  **Style Parameters**:
    - `FontName`: Font to use
    - `FontSize`: Size in pixels
    - `PrimaryColour`: Text color (&H00BBGGRR)
    - `OutlineColour`: Outline color (&H00BBGGRR)
    - `BackColour`: Shadow color (&HAABBGGRR where AA is opacity)
    - `Outline`: Outline thickness
    - `Shadow`: Shadow presence (0/1)
    - `Alignment`: Position (1-9)

### Font Management

1.  **Font Discovery**
    - Searches `fonts/` directory for TTF/OTF files.
    - Falls back to system fonts if not found.
    - Provides dropdown selection in GUI.

2.  **Font Rendering**
    - PIL/Pillow for preview rendering.
    - FFmpeg for final video rendering.
    - Consistent appearance between preview and final output.

3.  **Font Fallbacks**
    - Default to Arial if specified font not found.
    - Graceful degradation to system fonts.
    - Error logging for missing fonts.
