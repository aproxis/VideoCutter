# VideoCutter: Automated Video Creation Toolkit

## Project Overview
VideoCutter is a comprehensive video processing toolkit designed to automate the creation of professional slideshows from images and videos. It incorporates depth effects, audio processing, and custom overlays to produce engaging content for social media platforms. It aims to streamline the video creation workflow for content creators, reduce manual editing time, and maintain high-quality output.

## Features

### Core Functionality
*   **Video Processing**: Splits videos into configurable segments, processes input videos and images into standardized formats, and supports both vertical (9:16) and horizontal (16:9) video formats.
*   **Image Processing**: Resizes images to target dimensions, applies gradient and blur effects for background enhancement, and includes enhanced `zoompan` effects with dynamic zooming.
*   **DepthFlow Integration**: Generates 3D parallax effects from static images with multiple animation types and randomized parameters.
*   **Slideshow Creation**: Combines processed media into cohesive slideshows with random transition effects and configurable slide duration.
*   **Audio Processing**: Integrates soundtracks with fade in/out, mixes voiceovers with sidechain compression, adds transition sound effects, and synchronizes audio with video.
*   **Branding & Overlays**: Adds model name overlays, subscribe/like overlays, customizable colors and positioning, and integrates outro videos.
*   **File Management**: Organizes output in date-time based folders, automatically backs up source files, and maintains consistent file naming.
*   **Configuration System**: Provides a GUI for parameter configuration, supports JSON-based configuration presets, and includes save/load/delete functionality.

### Advanced Subtitle System
*   **SRT/ASS Integration**: Generates and integrates SRT/ASS subtitles with videos.
*   **Custom Font Support**: Allows selection of custom fonts from the `fonts/` directory.
*   **Advanced Styling**: Supports full ASS styling with configurable font, size, colors, outline, shadow effects, and precise positioning.
*   **Real-time Preview**: Offers a real-time subtitle preview in the GUI for accurate visual feedback.

## Why VideoCutter? (Problem Solved)
VideoCutter addresses the time-consuming and technical challenges faced by content creators in producing professional-quality video content. It automates the process of video editing, reducing the need for extensive technical knowledge and manual intervention.

*   **Time Efficiency**: Automates tasks that previously took hours, processing entire batches in minutes.
*   **Technical Barrier Reduction**: Provides a simple GUI that handles complex technical details.
*   **Consistency**: Ensures consistent branding, timing, and visual style across all content.
*   **Resource Management**: Automatically backs up original files, preventing data loss.
*   **Platform Optimization**: Supports both vertical and horizontal formats for various platforms.

## System Architecture

VideoCutter follows a modular architecture with a clear separation of concerns, transitioning from older monolithic scripts to a new, modular `videocutter` package. `videocutter/main.py` serves as the central orchestrator.

### Component Architecture
```
┌─────────────────────┐       ┌─────────────────────────┐
│ GUI Interface       │       │ videocutter/main.py     │
│ (gui.py)            │──────►│ (Main Orchestrator)     │
│ ├─ MainSettingsFrame│       └───────────┬─────────────┘
│ ├─ TitleSettingsFrame│                  │
│ ├─ SubtitleSettingsFrame│               ▼
│ ├─ OverlayEffectsFrame│      ┌─────────────────────────┐
│ └─ DepthflowSettingsFrame│    │ videocutter/config_     │
└──────────┬──────────┘       │ manager.py              │
           │                  │ (Configuration Manager) │
           │                  └───────────┬─────────────┘
           │                               │
           ▼                               ▼
┌─────────────────────┐       ┌─────────────────────────┐
│ videocutter/utils/  │       │ videocutter/processing/ │
│ gui_config_         │       │ video_processor.py      │
│ manager.py          │       │ (Video Processor)       │
└─────────────────────┘       └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ videocutter/processing/ │
                               │ depth_processor.py      │
                               │ (Depth Processor)       │
                               └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ videocutter/processing/ │
                               │ slideshow_generator.py  │
                               │ (Slideshow Generator)   │
                               └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ videocutter/processing/ │
                               │ audio_processor.py      │
                               │ (Audio Processor)       │
                               └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ videocutter/processing/ │
                               │ subtitle_generator.py   │
                               │ (Subtitle Generator)    │
                               └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ videocutter/processing/ │
                               │ overlay_compositor.py   │
                               │ (Overlay Compositor)    │
                               └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ Final Video Output      │
                               └─────────────────────────┘
```

### Supporting Utilities
```
┌─────────────────────┐       ┌─────────────────────────┐
│ videocutter/utils/  │       │ videocutter/utils/      │
│ file_utils.py       │◄──────┤ font_utils.py           │
│ (File Utilities)    │       │ (Font Utilities)        │
└─────────────────────┘       └─────────────────────────┘
           ▲                               ▲
           │                               │
           ▼                               ▼
┌─────────────────────┐       ┌─────────────────────────┐
│ videocutter/gui/    │       │ videocutter/gui/        │
│ gui_utils.py        │◄──────┤ title_settings_frame.py │
│ (GUI Utilities)     │       │ (Title Settings Frame)  │
└─────────────────────┘       └─────────────────────────┘
```

### Data Flow Pipeline
```
┌─────────────┐    ┌─────────────┐    ┌────────────────┐
│ Input Files │───►│ FileUtils   │───►│ Processed Media│
└─────────────┘    └─────────────┘    └────────┬───────┘
                                               │
                                               ▼
┌─────────────┐    ┌─────────────┐    ┌────────────────┐
│VideoProcessor│◄───┤DepthProcessor│◄──┤SlideshowGenerator│
└──────┬──────┘    └─────────────┘    └────────────────┘
       │                                      │
       ▼                                      ▼
┌─────────────┐    ┌─────────────┐    ┌────────────────┐
│AudioProcessor│───►│SubtitleGen  │───►│OverlayCompositor│
└─────────────┘    └─────────────┘    └────────┬───────┘
                                               │
                                               ▼
                                    ┌─────────────┐
                                    │ Final Video │
                                    └─────────────┘
```

### Configuration Flow Hierarchy
```
┌─────────────────────────────────┐
│ Global Config                   │
│ (default_config.json)           │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ Project Config                  │
│ (_project_config.json)          │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ Runtime Settings (GUI)          │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ ConfigManager                   │
│ (Unified Processing)            │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ Unified Config (DotMap)         │
│ ├─ Main Orchestrator            │
│ ├─ VideoProcessor               │
│ ├─ DepthProcessor               │
│ ├─ SlideshowGenerator           │
│ ├─ AudioProcessor               │
│ ├─ SubtitleGenerator            │
│ ├─ OverlayCompositor            │
│ ├─ GUIConfigManager             │
│ └─ TitleSettingsFrame           │
└─────────────────────────────────┘

## Content Module Architecture

This section details the architecture of the `content/` module, which focuses on YouTube video processing, transcript handling, image searching, and voiceover generation.

```
+-----------------------------------------------------------------+
| content/main.py                                                 |
| (Orchestrates video processing pipeline: fetches videos,        |
|  rewrites transcripts, finds images, generates voiceovers)      |
+-----------------------------------------------------------------+
             |
             | Calls methods from:
             v
+-----------------------------------------------------------------+
| content/youtube_handler.py                                      |
| (Handles YouTube video search, channel video retrieval,         |
|  and transcript fetching using Selenium and YouTube Transcript API) |
+-----------------------------------------------------------------+
             |
             | Passes data to:
             v
+-----------------------------------------------------------------+
| content/transcript_processor.py                                 |
| (Rewrites video transcripts using AI and extracts keywords      |
|  for image searching)                                           |
+-----------------------------------------------------------------+
             |
             | Passes keywords to:
             v
+-----------------------------------------------------------------+
| content/image_searcher.py                                       |
| (Searches and downloads relevant images and short videos        |
|  based on extracted keywords)                                   |
+-----------------------------------------------------------------+
             |
             | Passes rewritten text to:
             v
+-----------------------------------------------------------------+
| content/voice_generator.py                                      |
| (Generates natural-sounding voiceovers from rewritten text)     |
+-----------------------------------------------------------------+
             |
             | Utilizes:
             v
+-----------------------------------------------------------------+
| content/config.py                                               |
| (Manages application-wide configuration settings and paths)     |
+-----------------------------------------------------------------+
             |
             | Utilizes:
             v
+-----------------------------------------------------------------+
| content/utils/logger_config.py                                  |
| (Sets up and configures logging for the entire application)     |
+-----------------------------------------------------------------+
```
```

## Key Technologies

*   **Python 3.x**: Primary programming language.
*   **FFmpeg**: Core video and audio processing engine.
*   **Tkinter**: GUI framework for the configuration interface.
*   **PIL/Pillow**: Image processing library, also used for subtitle preview rendering.
*   **DepthFlow**: Library for 3D parallax effects.
*   **JSON**: Configuration file format.
*   **Subprocess**: Manages external process execution.
*   **DotMap**: Provides dot notation access to dictionaries for configuration.
*   **WhisperX**: For audio transcription and alignment (used by `subtitle_generator`).
*   **Mutagen**: For audio metadata (duration).
*   **FontTools**: For font file inspection.

## Installation & Setup

### Required Software
1.  **Python 3.x**: Minimum 3.6, recommended 3.8+.
2.  **FFmpeg**: Minimum 4.0, recommended 4.4+ with libx264 support.
3.  **DepthFlow**: Custom package for depth effects, requires PyTorch backend.

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
    sudo apt-get install ffmpeg
    
    # Windows
    # Download from ffmpeg.org and add to PATH
    ```

3.  **DepthFlow Setup**
    ```bash
    # DepthFlow is typically installed via pip as part of requirements.txt
    # Ensure PyTorch is installed with appropriate CUDA support if using GPU
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 # Example for CUDA 11.8
    ```

### Directory Structure
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
│   │   ├── depthflow_settings_frame.py
│   │   ├── main_settings_frame.py
│   │   ├── overlay_effects_frame.py
│   │   ├── subtitle_settings_frame.py
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

### Template Files
Required template files in `TEMPLATE` directory:
*   `soundtrack.mp3`: Background music
*   `transition.mp3`: Transition sound effect
*   `transition_long.mp3`: Extended transition sound
*   `voiceover_end.mp3`: Ending voiceover
*   `outro_vertical.mp4`: Vertical outro video
*   `outro_horizontal.mp4`: Horizontal outro video
*   `name_subscribe_like.mp4`: Vertical subscription overlay
*   `name_subscribe_like_horizontal.mp4`: Horizontal subscription overlay

## Usage

The workflow for VideoCutter is designed to be straightforward and efficient:

1.  **Input Preparation**:
    *   Place media files (images, videos) in the `INPUT` folder.
    *   Optional voiceover file (`voiceover.mp3`) can be added to the `INPUT` folder.

2.  **Configuration**:
    *   Launch the GUI (`python gui.py`).
    *   Select or create a configuration preset via the GUI.
    *   Set basic parameters like model name, watermark text, and video orientation.
    *   Enable/disable advanced options like depth effects, title overlays, and subtitle styling.

3.  **Processing**:
    *   Click the "START" button in the GUI to initiate the entire pipeline.
    *   Progress will be displayed in the terminal.
    *   No further user intervention is required during processing.

4.  **Output**:
    *   The completed video will be saved in a date-time stamped folder within `INPUT/RESULT/`.
    *   Original files are preserved in `INPUT/SOURCE/`.
    *   The final video is ready for direct upload to social media platforms.

## Current Status & Progress

### Project Status: Beta (Major Refactoring Underway)
VideoCutter is currently in a functional beta state. The core functionality is complete and working, with a usable GUI interface and configuration system, including recently enhanced subtitle features.

A **major refactoring is actively underway**, transitioning from a collection of monolithic scripts to a modular Python package (`videocutter`). The new `videocutter/main.py` now orchestrates the pipeline, utilizing specialized modules for each processing step. The old scripts are being superseded.

### Recent Progress
*   **Core Refactoring**: Established new `videocutter` package structure with `main.py` as orchestrator, and migrated core functionalities into modular components (`config_manager`, `processing/` modules, `utils/` modules). `gui.py` has been updated to interact with this new modular backend.
*   **GUI Reorganization**: Increased window size, restructured GUI tabs ("Main Settings", "Title Settings", "Subtitles", "Overlay Effects", "DepthFlow"), relocated settings for improved user experience, implemented new overlay directory structure, and enhanced control disabling for various sections.
*   **Subtitle System Enhancements**: Implemented full ASS style parameter support, fixed color conversion and opacity handling, enhanced preview accuracy, and integrated new subtitle parameters into the GUI and configuration system.

## Future Enhancements

### Immediate Priority: Core Script Refactoring Completion
*   Formally deprecate and remove old monolithic scripts (`cutter.py`, `sorter.py`, `cleaner.py`, `slideshow.py`, `subscribe.py`, `depth.py`, `audio.py`, `srt_generator.py`) once the new modular pipeline is fully stable.

### Short-term Tasks
*   **Subtitle Feature Expansion**: Add support for multiple subtitle tracks, timing adjustment, more positioning options, and enhanced text formatting.
*   **Preview Enhancements**: Implement video-based subtitle preview, timeline-based editing, and real-time preview updates.
*   **Configuration Management**: Add subtitle preset management, style templates, and enhanced parameter validation.

### Medium-term Tasks
*   **Subtitle Generation**: Enhance automatic subtitle generation, implement timing correction, and add support for translation.
*   **Performance Optimization**: Optimize subtitle rendering, reduce memory usage, and improve overall processing efficiency.
*   **User Experience Improvements**: Add drag-and-drop subtitle file import, implement a subtitle editor, and enhance error reporting.

### Long-term Vision
*   **Advanced Subtitle Features**: Add animated subtitle effects, karaoke-style text animation, and graphic subtitle support.
*   **Integration Enhancements**: Support more subtitle formats, direct subtitle download from services, and subtitle extraction from video files.
*   **Accessibility Improvements**: Add high-contrast subtitle options and screen reader compatibility.

## Contributing
Contributions are welcome! Please refer to the `memory-bank/` documentation for detailed project context, system patterns, and technical insights.

## Contact
For questions or support, please open an issue on the project's GitHub repository.
