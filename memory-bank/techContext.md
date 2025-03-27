# Technical Context: VideoCutter

## Technologies Used

### Core Technologies

1. **Python 3.x**
   - Primary programming language
   - Used for all script components
   - Provides cross-platform compatibility
   - Extensive library ecosystem

2. **FFmpeg**
   - Core video and audio processing engine
   - Handles video splitting, merging, and effects
   - Manages audio mixing and synchronization
   - Provides format conversion and optimization

3. **Tkinter**
   - GUI framework for the configuration interface
   - Native integration with Python
   - Cross-platform compatibility
   - Lightweight and simple implementation

4. **PIL/Pillow**
   - Image processing library
   - Handles image resizing, cropping, and effects
   - Manages watermark application
   - Provides format conversion

5. **DepthFlow**
   - 3D parallax effect generation
   - Creates depth maps from 2D images
   - Applies motion effects to static images
   - Integrates with PyTorch for ML-based depth estimation

### Supporting Technologies

1. **JSON**
   - Configuration file format
   - Stores preset parameters
   - Enables easy serialization/deserialization
   - Human-readable format

2. **Subprocess**
   - Manages external process execution
   - Handles FFmpeg command execution
   - Provides process monitoring and control
   - Enables inter-script communication

3. **OS/Shutil**
   - File system operations
   - Directory management
   - File moving and copying
   - Path manipulation

4. **Argparse**
   - Command-line argument parsing
   - Enables script parameterization
   - Provides help documentation
   - Validates input parameters

5. **PyTorch** (via DepthFlow)
   - Machine learning framework
   - Powers depth estimation models
   - GPU acceleration support
   - Tensor operations for image processing

## Development Setup

### Required Software

1. **Python 3.x**
   - Minimum version: 3.6
   - Recommended version: 3.8+
   - Required packages: see requirements section

2. **FFmpeg**
   - Minimum version: 4.0
   - Recommended version: 4.4+
   - Required with libx264 support

3. **DepthFlow**
   - Custom package for depth effects
   - Requires PyTorch backend
   - GPU support recommended but not required

### Environment Setup

1. **Python Environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install pillow numpy click attr dotmap
   ```

2. **FFmpeg Installation**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   apt-get install ffmpeg
   
   # Windows
   # Download from ffmpeg.org and add to PATH
   ```

3. **DepthFlow Setup**
   ```bash
   # Install DepthFlow
   pip install DepthFlow
   
   # Install PyTorch (with CUDA if GPU available)
   pip install torch torchvision
   ```

4. **Directory Structure**
   ```
   VideoCutter/
   ├── config/                  # Create this directory
   ├── INPUT/                   # Create this directory
   │   ├── DEPTH/               # Create this directory
   │   ├── RESULT/              # Auto-created
   │   └── SOURCE/              # Auto-created
   ├── TEMPLATE/                # Create this directory
   └── *.py                     # Python scripts
   ```

5. **Template Files**
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

1. **Memory Usage**
   - High memory consumption during video processing
   - DepthFlow requires significant RAM for depth estimation
   - Parallel processing increases memory requirements
   - Recommended minimum: 8GB RAM, 16GB+ preferred

2. **Processing Time**
   - Video processing is CPU-intensive
   - DepthFlow benefits from GPU acceleration
   - Processing time scales with video resolution and duration
   - Typical processing: 2-5 minutes per minute of output video

3. **Storage Requirements**
   - Temporary files created during processing
   - Source backups increase storage needs
   - Multiple output versions stored in date-time folders
   - Recommended free space: 10GB minimum

### Compatibility Constraints

1. **Video Format Constraints**
   - Input videos must be MP4 format
   - 16:9 aspect ratio required for input videos
   - Output formats: vertical (9:16) or horizontal (16:9)
   - H.264 codec used for compatibility

2. **Image Format Constraints**
   - Supported formats: JPG, JPEG
   - No specific aspect ratio requirements (auto-processed)
   - Recommended resolution: 1080p or higher

3. **Audio Format Constraints**
   - Voiceover must be MP3 format
   - Template audio files must be MP3 format
   - Stereo audio output (2 channels)
   - AAC codec used for output

## Dependencies

### Python Package Dependencies

```
pillow>=9.0.0          # Image processing
numpy>=1.20.0          # Numerical operations
click>=8.0.0           # Command-line interface
attr>=21.2.0           # Class attribute management
dotmap>=1.3.0          # Dot notation access to dictionaries
```

### External Dependencies

1. **FFmpeg**
   - Required for all video and audio processing
   - Must be available in system PATH
   - Required codecs: libx264, aac

2. **System Fonts**
   - Required fonts:
     - Montserrat-SemiBold.otf
     - Nexa.otf
   - Must be installed in system font directory or specified path

## Integration Points

1. **Input Integration**
   - Manual file placement in INPUT directory
   - No direct API for file ingestion
   - Potential for future automation via watched folders

2. **Output Integration**
   - Files saved to local filesystem
   - No direct publishing to platforms
   - Manual upload to social media required

3. **Configuration Integration**
   - JSON configuration files
   - Manual creation/editing via GUI
   - No external configuration API

4. **Process Integration**
   - Command-line execution
   - GUI-triggered processing
   - No scheduling or automation built-in
