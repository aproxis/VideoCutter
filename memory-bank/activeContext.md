# Active Context: VideoCutter

## Current Work Focus

The current focus for VideoCutter is on enhancing subtitle functionality and improving the user experience. Recent work has centered on optimizing subtitle rendering, fixing color conversion issues, and ensuring consistent appearance between preview and final output.

### Subtitle Enhancement Priorities

1. **Subtitle Rendering Improvements**
   - Fixing color format conversion for ASS subtitles
   - Implementing proper shadow rendering with opacity control
   - Ensuring correct layer ordering (shadow → outline → text)
   - Improving preview accuracy in the GUI

2. **Font Management**
   - Enhancing font detection from the fonts/ directory
   - Implementing better fallback mechanisms
   - Supporting custom fonts for subtitles
   - Fixing font path handling

3. **GUI Enhancements**
   - Improving subtitle preview rendering
   - Adding real-time parameter updates
   - Implementing numeric formatting for slider values
   - Enhancing control state management

4. **FFmpeg Integration**
   - Optimizing subtitle styling parameters
   - Fixing color conversion for ASS format
   - Implementing proper opacity handling
   - Ensuring consistent parameter passing between components

## Recent Changes

### Subtitle Rendering Improvements

- Fixed RGB to BGR color conversion for ASS subtitle format
- Corrected opacity handling by inverting values for ASS format
- Implemented proper alpha compositing for shadow effects
- Fixed the drawing order to ensure shadows appear behind text with outlines
- Enhanced preview rendering to match the final video output

### GUI Enhancements

- Improved the subtitle preview with proper layer management
- Added formatting for float values to limit them to 2 decimal places
- Fixed shadow controls state management
- Enhanced preview rendering with alpha compositing
- Implemented proper masking for complex text shapes with outlines

### FFmpeg Integration

- Updated subtitle styling parameters to use proper ASS format
- Fixed opacity handling in the ASS style string
- Implemented proper color ordering for ASS format
- Enhanced font path resolution for custom fonts

## Next Steps

### Short-term Tasks

1. **Subtitle Feature Expansion**
   - Add support for multiple subtitle tracks
   - Implement subtitle timing adjustment
   - Add more positioning options
   - Enhance text formatting options (bold, italic, etc.)

2. **Preview Enhancements**
   - Add video-based subtitle preview
   - Implement timeline-based subtitle editing
   - Add real-time preview updates during typing
   - Enhance preview scaling for different resolutions

3. **Configuration Management**
   - Add subtitle preset management
   - Implement style templates for quick application
   - Enhance parameter validation
   - Add more detailed tooltips and help text

### Medium-term Tasks

1. **Subtitle Generation**
   - Enhance automatic subtitle generation
   - Implement subtitle timing correction
   - Add support for subtitle translation
   - Implement subtitle formatting suggestions

2. **Performance Optimization**
   - Optimize subtitle rendering for speed
   - Reduce memory usage during processing
   - Implement more efficient preview rendering
   - Optimize font loading and caching

3. **User Experience Improvements**
   - Add drag-and-drop subtitle file import
   - Implement subtitle editor with syntax highlighting
   - Add waveform visualization for timing
   - Enhance error reporting for subtitle issues

### Long-term Vision

1. **Advanced Subtitle Features**
   - Add animated subtitle effects
   - Implement karaoke-style text animation
   - Add support for graphic subtitles
   - Implement subtitle templates for different content types

2. **Integration Enhancements**
   - Add support for more subtitle formats
   - Implement direct subtitle download from services
   - Add subtitle extraction from video files
   - Implement subtitle synchronization tools

3. **Accessibility Improvements**
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
- ASS format uses BGR color ordering instead of RGB
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

## Current Challenges

1. **ASS Format Complexity**
   - ASS format has complex parameter requirements
   - Color ordering and opacity handling are counterintuitive
   - Documentation for ASS format is limited
   - Testing requires rendering to verify appearance

2. **Preview Accuracy**
   - Ensuring preview matches final output exactly
   - Handling different rendering engines (PIL vs. FFmpeg)
   - Managing layer ordering consistently
   - Implementing proper alpha compositing

3. **Font Compatibility**
   - Ensuring fonts work across different platforms
   - Handling missing fonts gracefully
   - Managing font paths correctly
   - Supporting various font formats

4. **Parameter Validation**
   - Ensuring valid parameter ranges
   - Providing meaningful error messages
   - Preventing invalid combinations
   - Maintaining backward compatibility

## Recent Insights

1. **Layer Management Importance**
   - Proper layer ordering is critical for subtitle appearance
   - Shadow must appear behind text with outline
   - Alpha compositing is necessary for accurate preview
   - Z-ordering must be consistent between preview and final output

2. **Color Conversion Complexity**
   - ASS format uses BGR instead of RGB
   - Opacity handling is inverted in ASS format
   - Hex color codes need careful conversion
   - Preview and final output must use the same color conversion

3. **Preview Rendering Techniques**
   - Multiple image layers with alpha channels provide accurate preview
   - Mask-based shadow rendering improves appearance
   - Separate rendering passes for each effect improve control
   - Composite images provide better results than direct drawing

4. **FFmpeg Parameter Optimization**
   - ASS style string format is highly specific
   - Parameter ordering affects rendering
   - Escaping special characters is necessary
   - Testing with various parameter combinations is essential
