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

6. **Pytest**
   - Testing framework
   - Unit and integration testing
   - Test fixtures and mocks
   - Coverage reporting

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
   pip install -r requirements.txt
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
   ├── config/                  # Configuration files
   │   ├── vertical_config.json   # Configuration for vertical videos
   │   └── horizontal_config.json # Configuration for horizontal videos
   ├── docs/                    # Documentation
   ├── INPUT/                   # Input folder for videos and images
   │   ├── DEPTH/               # Depth processing folder
   │   ├── RESULT/              # Auto-created for processed files
   │   └── SOURCE/              # Auto-created for original files backup
   ├── TEMPLATE/                # Template files for overlays and audio
   ├── tests/                   # Test suite
   │   └── unit/                # Unit tests
   ├── video_processing/        # Core processing modules
   │   ├── __init__.py          # Package initialization
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
pytest>=7.0.0          # Testing framework
pytest-cov>=4.0.0      # Test coverage reporting
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

## Documentation Standards

### Code Documentation

The project follows a comprehensive documentation approach:

1. **Module Docstrings**
   - Brief description of the module
   - Detailed explanation of purpose and functionality
   - Key features or components listed
   - Usage examples where appropriate

2. **Class Docstrings**
   - Brief description of the class
   - Detailed explanation of purpose and functionality
   - Attributes listed with types and descriptions
   - Usage examples where appropriate

3. **Function Docstrings**
   - Brief description of the function
   - Detailed explanation of purpose and functionality
   - Parameters listed with types and descriptions
   - Return values listed with types and descriptions
   - Exceptions listed with conditions
   - Usage examples where appropriate

4. **Type Hints**
   - All function parameters include type hints
   - Return values include type hints
   - Complex types use typing module (List, Dict, Optional, etc.)
   - Improves code understanding and IDE support

5. **README Files**
   - Each major directory includes a README.md file
   - Explains purpose and contents of the directory
   - Provides usage examples and guidance
   - Lists dependencies and requirements

### Documentation Tools

1. **Docstrings**
   - Google-style docstrings for readability
   - Consistent formatting across all modules
   - Examples included where appropriate
   - Type information included in parameter descriptions

2. **Markdown**
   - README files use Markdown format
   - Consistent structure across all files
   - Code blocks with syntax highlighting
   - Lists, tables, and headings for organization

3. **Memory Bank**
   - Project-level documentation in memory-bank directory
   - Captures high-level architecture and decisions
   - Records project context and progress
   - Documents technical constraints and requirements

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

## Testing Framework

### Test Structure

1. **Unit Tests**
   - Located in tests/unit directory
   - Test individual components in isolation
   - Mock external dependencies
   - Focus on function and class behavior

2. **Test Configuration**
   - pytest.ini defines test configuration
   - Coverage reporting enabled
   - Test discovery patterns defined
   - Verbose output for clarity

3. **Test Fixtures**
   - Common test data and setup
   - Mock objects and functions
   - Environment configuration
   - Temporary file handling

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=video_processing

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test
pytest tests/unit/test_config.py::TestVideoConfig::test_default_values
```

### Test Coverage

- Current coverage: ~50%
- Unit tests for core components
- Limited integration testing
- Focus on critical functionality
- Ongoing expansion of test suite
