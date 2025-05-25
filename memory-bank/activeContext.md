# Active Context: VideoCutter

## Current Work Focus

The primary focus for VideoCutter is now shifting towards a significant **refactoring of core scripts** (`cutter.py`, `sorter.py`, `cleaner.py`, `slideshow.py`, `subscribe.py`, `depth.py`, and `audio.py`) to improve modularity, maintainability, and scalability. This will involve creating a central controller and breaking down existing scripts into more specialized modules.

Alongside this, ongoing work includes documentation updates and potential further enhancements to subtitle functionality and user experience as identified.

### Subtitle Enhancement Priorities

1.  **Subtitle Rendering Improvements**
    - Fixing color format conversion for ASS subtitles
    - Implementing proper shadow rendering with opacity control
    - Ensuring correct layer ordering (shadow → outline → text)
    - Improving preview accuracy in the GUI

2.  **Font Management**
    - Enhancing font detection from the fonts/ directory
    - Implementing better fallback mechanisms
    - Supporting custom fonts for subtitles
    - Fixing font path handling

3.  **GUI Enhancements**
    - Improving subtitle preview rendering
    - Adding real-time parameter updates
    - Implementing numeric formatting for slider values
    - Enhancing control state management

4.  **FFmpeg Integration**
    - Optimizing subtitle styling parameters
    - Fixing color conversion for ASS format
    - Implementing proper opacity handling
    - Ensuring consistent parameter passing between components

## Recent Changes

### Subtitle Rendering Improvements

- Fixed RGB to BGR color conversion for ASS subtitle format
- Corrected opacity handling by inverting values for ASS format
- Implemented proper shadow rendering with opacity control
- Fixed the drawing order to ensure shadows appear behind text with outlines
- Enhanced preview rendering to match the final video output

### GUI Enhancements

- Improved the subtitle preview with proper layer management
- Added formatting for float values to limit them to 2 decimal places
- Fixed shadow controls state management
- Enhanced preview rendering with alpha compositing
- Implemented proper masking for complex text shapes with outlines
- **Reorganized GUI layout for better user experience:**
    - Increased window size to 1400x900.
    - Restructured tabs into "Main Settings", "Subtitles", and "Overlay Effects" (renamed from "Advanced Effects").
    - Relocated settings to more logical tabs:
        - "Generate Subtitles .srt" and "Characters per line (max)" moved to "Subtitles" tab.
        - "Effect Overlay" and "Chromakey Settings" moved to "Overlay Effects" tab.
    - Adjusted internal frame parenting to match new tab structure.
    - Added separate controls for title video chromakey color, similarity, and blend, and moved them to a dedicated section.
    - Added a checkbox to enable/disable title background with configurable color and opacity.
    - Implemented new overlay directory structure (`effects/overlays`, `effects/subscribe`, `effects/title`).
    - Added dropdowns in GUI for selecting subscribe and title video overlay files from their respective directories.
    - Added an "Enable" checkbox for Effect Overlay in GUI, with state saving/loading and control enabling/disabling.
    - Implemented GUI control disabling (greying out) for Watermark, Subscribe Overlay, and Title Overlay sections based on their respective "Enable" checkboxes, ensuring all relevant widgets are correctly enabled/disabled.
    - Centralized default GUI values in `videocutter/utils/gui_config_manager.py`.
    - Implemented threading for `start_process` to keep the GUI responsive during video processing.
    - **Fixed `KeyError: 'gui_utils'` by ensuring `gui_utils` module is correctly passed to `gui_config_manager` via the `gui_elements` dictionary.**

### FFmpeg Integration

- Updated subtitle styling parameters to use proper ASS format
- Fixed opacity handling in the ASS style string
- Implemented proper color ordering for ASS format
- Enhanced font path resolution for custom fonts

## Next Steps

### Immediate Priority: Core Script Refactoring

1.  **Detailed Analysis of Core Scripts**:
    *   Thoroughly examine `cutter.py`, `sorter.py`, `cleaner.py`, `slideshow.py`, `subscribe.py`, `depth.py`, and `audio.py`.
    *   Identify current responsibilities, functions, classes, and dependencies.
    *   Pinpoint areas with mixed concerns, high complexity, or potential for generalization.
2.  **Design New Modular Architecture**:
    *   Define logical modules/components to be extracted from the existing scripts.
    *   Propose a new directory structure if necessary (e.g., `videocutter_core/`, `videocutter_utils/`).
    *   Outline the responsibilities of a new central `main.py` (or a heavily refactored `cutter.py`) orchestrator.
3.  **Define Interfaces and Data Flow**:
    *   Specify how modules will communicate with the main controller and each other.
    *   Plan how configuration data and application state will be managed and passed.
4.  **Develop Implementation Plan**:
    *   Break down the refactoring process into smaller, manageable steps.
    *   Consider the impact on `gui.py` and how it will interact with the new structure.
    *   Establish a testing strategy for the refactored components.

### Short-term Tasks (Post-Refactoring Planning / Parallel if possible)

1.  **Subtitle Feature Expansion**
    *   Add support for multiple subtitle tracks
    *   Implement subtitle timing adjustment
    *   Add more positioning options
    *   Enhance text formatting options (bold, italic, etc.)

2.  **Preview Enhancements**
    *   Add video-based subtitle preview
    *   Implement timeline-based subtitle editing
    *   Add real-time preview updates during typing
    *   Enhance preview scaling for different resolutions

3.  **Configuration Management**
    *   Add subtitle preset management
    *   Implement style templates for quick application
    *   Enhance parameter validation
    *   Add more detailed tooltips and help text

### Medium-term Tasks

1.  **Subtitle Generation**
    - Enhance automatic subtitle generation
    - Implement subtitle timing correction
    - Add support for subtitle translation
    - Implement subtitle formatting suggestions

2.  **Performance Optimization**
    - Optimize subtitle rendering for speed
    - Reduce memory usage during processing
    - Implement more efficient preview rendering
    - Optimize font loading and caching

3.  **User Experience Improvements**
    - Add drag-and-drop subtitle file import
    - Implement subtitle editor with syntax highlighting
    - Add waveform visualization for timing
    - Enhance error reporting for subtitle issues

### Long-term Vision

1.  **Advanced Subtitle Features**
    - Add animated subtitle effects
    - Implement karaoke-style text animation
    - Add support for graphic subtitles
    - Implement subtitle templates for different content types

2.  **Integration Enhancements**
    - Add support for more subtitle formats
    - Implement direct subtitle download from services
    - Add subtitle extraction from video files
    - Implement subtitle synchronization tools

3.  **Accessibility Improvements**
    - Add high-contrast subtitle options
    - Implement screen reader compatibility
    - Add support for closed captioning standards
    - Implement subtitle accessibility validation

## Active Decisions and Considerations

### Subtitle Rendering Approach

**Decision**: Use ASS format for subtitle styling with FFmpeg and implement a custom preview renderer using PIL/Pillow.

**Considerations**:
- ASS provides rich styling options not available in SRT
- FFmpeg has good support for ASS subtitle rendering
- Custom preview renderer ensures WYSIWYG experience
- Layer management is critical for proper visual appearance

### Color Handling Strategy

**Decision**: Implement proper RGB to BGR conversion for ASS format and handle opacity inversion.

**Considerations**:
- ASS uses BGR color ordering instead of RGB
- Opacity in ASS is inverted (00=opaque, FF=transparent)
- Consistent color representation is critical for user experience
- Preview must match final output exactly

### Font Management

**Decision**: Prioritize fonts from the fonts/ directory with fallback to system fonts.

**Considerations**:
- Custom fonts provide consistent appearance across systems
- Fallback mechanism ensures functionality even if fonts are missing
- Font discovery needs to be robust and user-friendly
- Preview must use the same fonts as the final output

### Preview Rendering

**Decision**: Implement sophisticated layer management with alpha compositing for accurate preview.

**Considerations**:
- Preview must match final output exactly
- Layer ordering is critical for proper visual appearance
- Alpha compositing provides accurate shadow and outline effects
- Real-time updates enhance user experience

### Refactoring Core Scripts

**Decision**: Undertake a significant refactoring of core processing scripts to improve modularity, maintainability, and prepare for future scalability. A central controller will orchestrate more specialized modules.

**Rationale**:
-   **Maintainability**: Smaller, focused modules are easier to understand, debug, and modify.
-   **Testability**: Independent modules can be unit-tested more effectively.
-   **Scalability**: A modular design makes it easier to add new features or modify existing ones without impacting unrelated parts of the system.
-   **Usability/Reusability**: Well-defined modules can potentially be reused in other contexts or by other tools.
-   **Reduced Technical Debt**: Addresses current complexities and mixed concerns in scripts like `cutter.py`.

**Key Architectural Considerations**:
-   **Module Granularity**: Finding the right balance for the size and scope of new modules.
-   **Inter-Module Communication**: Defining clear and efficient interfaces (e.g., function calls, data objects).
-   **Configuration Management**: How global and module-specific configurations will be handled and passed.
-   **State Management**: How state is maintained and shared (or isolated) across the pipeline.
-   **Impact on GUI**: Ensuring `gui.py` can seamlessly integrate with the new backend structure.

## Current Challenges

1.  **ASS Format Complexity**
    - ASS format has complex parameter requirements
    - Color ordering and opacity handling are counterintuitive
    - Documentation for ASS format is limited
    - Testing requires rendering to verify appearance

2.  **Preview Accuracy**
    - Ensuring preview matches final output exactly
    - Handling different rendering engines (PIL vs. FFmpeg)
    - Managing layer ordering consistently
    - Implementing proper alpha compositing

3.  **Font Compatibility**
    - Ensuring fonts work across different platforms
    - Handling missing fonts gracefully
    - Managing font paths correctly
    - Supporting various font formats

4.  **Parameter Validation**
    - Ensuring valid parameter ranges
    - Providing meaningful error messages
    - Preventing invalid combinations
    - Maintaining backward compatibility

5.  **Refactoring Complexity**:
    *   Managing dependencies between newly created modules.
    *   Ensuring backward compatibility of existing configuration files if possible, or providing a clear migration path.
    *   Thoroughly testing the refactored system to ensure no regressions in functionality.
    *   Potential for unforeseen complexities when untangling existing script logic.

## Recent Insights

1.  **GUI Reorganization Benefits**:
    - The new tab structure ("Main Settings", "Subtitles", "Overlay Effects") provides a clearer separation of concerns.
    - Grouping related settings (e.g., all subtitle-specific options under the "Subtitles" tab, and visual effects under "Overlay Effects") improves navigability and reduces clutter in each tab.
    - This reorganization is expected to make the GUI more intuitive for users.
    - The addition of dedicated controls for title video chromakey and title background further enhances user control and customization.
    - The new overlay directory structure and GUI dropdowns provide more organized and flexible management of visual effects.
    - Added an "Enable" checkbox for the Effect Overlay, allowing users to easily toggle its application and manage associated settings.
    - Implemented GUI control disabling (greying out) for Watermark, Subscribe Overlay, and Title Overlay sections based on their respective "Enable" checkboxes, ensuring all relevant widgets are correctly enabled/disabled, improving usability and clarity.
    - Centralized default GUI values in `videocutter/utils/gui_config_manager.py`.
    - Implemented threading for `start_process` to keep the GUI responsive during video processing.

2.  **Layer Management Importance**
    - Proper layer ordering is critical for subtitle appearance
    - Shadow must appear behind text with outline
    - Alpha compositing is necessary for accurate preview
    - Z-ordering must be consistent between preview and final output

2.  **Color Conversion Complexity**
    - ASS format uses BGR instead of RGB
    - Opacity handling is inverted in ASS format
    - Hex color codes need careful conversion
    - Preview and final output must use the same color conversion

3.  **Preview Rendering Techniques**
    - Multiple image layers with alpha channels provide accurate preview
    - Mask-based shadow rendering improves appearance
    - Separate rendering passes for each effect improve control
    - Composite images provide better results than direct drawing

4.  **FFmpeg Parameter Optimization**
    - ASS style string format is highly specific
    - Parameter ordering affects rendering
    - Escaping special characters is necessary
    - Testing with various parameter combinations is essential
