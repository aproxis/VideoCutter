# VideoCutter - Refactoring Overview (Branch: refactor/core-modules)

This document outlines the significant refactoring effort undertaken to restructure the VideoCutter application into a more modular, maintainable, and scalable system. All work described here is on the `refactor/core-modules` Git branch.

## 1. Rationale for Refactoring

The original VideoCutter application, while functional, consisted of several large Python scripts (`cutter.py`, `slideshow.py`, `subscribe_new.py`, etc.) with overlapping responsibilities and tight coupling. This led to challenges in:

*   **Maintainability**: Modifying one part of the system could have unintended consequences elsewhere.
*   **Readability**: Large scripts with complex conditional logic, especially for FFmpeg command generation, were difficult to follow.
*   **Testability**: Unit testing individual components was challenging.
*   **Configuration Management**: Settings were primarily passed via extensive command-line arguments between scripts.
*   **Scalability**: Adding new features or significantly altering existing ones was becoming increasingly complex.

The refactoring aims to address these issues by introducing a clear separation of concerns through a modular package structure.

## 2. New Architecture Overview

The application has been reorganized into a Python package named `videocutter`. This package encapsulates all core logic, orchestrated by a central `main.py` script.

### Key Components:

*   **`videocutter/main.py`**: The main orchestrator of the pipeline. It initializes configuration and calls processing modules in sequence.
*   **`videocutter/config_manager.py`**: Handles loading, parsing, and providing access to application settings (from JSON files and potentially GUI overrides).
*   **`videocutter/utils/`**: A sub-package for shared utility functions:
    *   `file_utils.py`: File/directory operations, sorting, media limiting.
    *   `font_utils.py`: Font name extraction and path resolution.
*   **`videocutter/processing/`**: A sub-package containing modules for each distinct stage of the video processing pipeline:
    *   `video_processor.py`: Initial video/image preparation (splitting, orientation, effects, cleaning short segments).
    *   `depth_processor.py`: Applies DepthFlow parallax effects to images.
    *   `slideshow_generator.py`: Creates the base video slideshow with transitions (video track only).
    *   `audio_processor.py`: Handles all audio mixing (soundtrack, voiceover, transitions, sidechain compression).
    *   `subtitle_generator.py`: Transcribes audio to generate SRT subtitle files using WhisperX.
    *   `overlay_compositor.py`: Applies final visual overlays (title, subscribe animation, effects) and renders subtitles onto the video.
*   **`gui.py` (Modified)**: The Tkinter GUI now interacts with `videocutter/main.py` by passing a configuration dictionary, instead of calling the old `cutter.py` script via subprocess.

### ASCII Diagram of Package Structure:

```
VideoCutter_Project_Root/
├── videocutter/                  <-- New Main Package
│   ├── __init__.py
│   ├── main.py                   <-- Orchestrator
│   ├── config_manager.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   └── font_utils.py
│   └── processing/
│       ├── __init__.py
│       ├── video_processor.py
│       ├── depth_processor.py
│       ├── slideshow_generator.py
│       ├── audio_processor.py
│       ├── subtitle_generator.py
│       └── overlay_compositor.py
├── gui.py                        <-- Modified GUI
├── config/
│   └── default_config.json
├── fonts/
├── TEMPLATE/
├── INPUT/
├── effects/
├── memory-bank/
├── README.md                     <-- Main Project README
├── README_refactor.md            <-- This Document
└── ... (other project files)
```

## 3. Workflow Overview

The refactored pipeline, orchestrated by `videocutter/main.py`, generally follows these steps:

1.  **Configuration Loading**: `config_manager.py` loads settings from a JSON file and merges any overrides (e.g., from `gui.py`).
2.  **Initial Setup**: `file_utils.py` sets up working directories and backs up original source media. Input files are copied to a timestamped working directory.
3.  **Media Preparation**:
    *   `video_processor.py` processes raw videos (splitting, orientation changes) and images (resizing, effects) within the working directory.
    *   `video_processor.py` also cleans (deletes) any video segments shorter than a configured duration.
4.  **Media List Finalization**:
    *   `file_utils.py` lists all processed media in the working directory.
    *   `file_utils.py` limits this list based on total desired video duration and segment duration to prevent overly long outputs.
5.  **DepthFlow (Conditional)**: If enabled, `depth_processor.py` converts prepared images from the list into video segments with parallax effects. The media list is updated.
6.  **Base Slideshow Generation**: `slideshow_generator.py` takes the final list of media (image-videos or depth-videos, and original video segments) and creates a base video track (`slideshow_base.mp4`) with transitions.
7.  **Subtitle Generation (Conditional)**: If enabled and a voiceover file exists, `subtitle_generator.py` transcribes the voiceover audio to an SRT file.
8.  **Audio Processing**: `audio_processor.py` takes `slideshow_base.mp4`, the voiceover, and template audio files to produce a video with a complete audio mix (`slideshow_with_audio.mp4`).
9.  **Final Composition**: `overlay_compositor.py` takes `slideshow_with_audio.mp4` and applies:
    *   Title text.
    *   Subscribe/like animation overlay (with chromakey).
    *   Optional visual effect overlays.
    *   Renders subtitles from the SRT file (if generated) onto the video.
    *   Produces the final output video.
10. **Cleanup**: Intermediate files (like `slideshow_base.mp4`) are removed.

### Mermaid Diagram of Refactored Workflow:

```mermaid
graph TD
    A[User Config (GUI/JSON)] --> B(videocutter.config_manager.load_config);
    B -- Configuration Object --> C(videocutter.main.run_pipeline);

    C --> D(utils.file_utils.setup_project_directories);
    D --> E{Copy Media to WorkDir};
    E --> F(processing.video_processor: Initial Video/Image Prep);
    F --> G(processing.video_processor.clean_short_video_segments);
    G --> H(utils.file_utils.limit_media_files_by_duration);
    
    H -- Media List --> I{DepthFlow Enabled?};
    I -- Yes --> J(processing.depth_processor.apply_depth_effects);
    J -- Depth Videos & Other Media --> K;
    I -- No --> K(processing.slideshow_generator.generate_base_slideshow);
    
    K -- Base Slideshow (Video Only) --> L;
    C -- Voiceover Path & Config --> M{Generate SRT?};
    M -- Yes --> N(processing.subtitle_generator.generate_srt_from_audio_file);
    
    L --> O(processing.audio_processor.process_audio);
    N -- SRT File Path (Optional) --> P;
    O -- Video with Audio --> P(processing.overlay_compositor.apply_final_overlays);
    
    P --> Q[Final Output Video];

    subgraph Utilities
        U1(utils.font_utils)
    end
    P --> U1;
```

## 4. Benefits of Refactoring

*   **Improved Modularity**: Each component now has a well-defined, single responsibility.
*   **Enhanced Readability & Maintainability**: Smaller, focused modules are easier to understand, debug, and update. FFmpeg command generation, while still complex, is localized within specific processing steps.
*   **Increased Testability**: Individual functions and modules can be unit-tested more effectively.
*   **Centralized Configuration**: `config_manager.py` provides a unified way to handle settings, reducing reliance on long CLI argument chains.
*   **Reduced Code Duplication**: Utility functions (file operations, font handling) are centralized.
*   **Better Scalability**: The clear structure makes it easier to add new features or modify existing steps in the pipeline without broad side effects.

## 5. Next Steps (Post-Initial Refactoring)

1.  **Thorough Testing**:
    *   Unit tests for utility functions and critical logic within processing modules.
    *   Integration tests for each processing module.
    *   End-to-end testing via `gui.py` and potentially a CLI for `main.py`.
2.  **Refinement**: Based on testing, refine error handling, logging, intermediate file management, and FFmpeg command precision.
3.  **GUI Threading**: Implement threading in `gui.py` when calling `run_pipeline` to prevent the UI from freezing during processing.
4.  **Cleanup**: Remove the old, now redundant, scripts from the project root.
5.  **Documentation**: Update all relevant Memory Bank files and the main `README.md` to reflect the finalized new architecture.

This refactoring lays a strong foundation for the future development and enhancement of VideoCutter.
