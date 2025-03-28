# Configuration Directory for VideoCutter

This directory contains configuration presets for the VideoCutter processing pipeline. These JSON files store settings that can be loaded, saved, and managed through the GUI interface.

## Configuration File Format

Configuration files are stored in JSON format with the following structure:

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

## Configuration Parameters

### Required Parameters

- **model_name**: Name displayed in the output video
- **watermark**: Text watermark displayed on the slideshow
- **font_size**: Size of the model name text (or 0 for auto-calculation)
- **segment_duration**: Duration of each video segment in seconds
- **input_folder**: Directory containing input files
- **depthflow**: Enable/disable 3D parallax effects (0/1)
- **time_limit**: Maximum duration of the final video in seconds
- **video_orientation**: Output video orientation ("vertical" or "horizontal")
- **blur**: Enable/disable blur effects for horizontal videos (0/1)

## Usage

### Through the GUI

1. **Load Configuration**:
   - Select a configuration from the dropdown menu
   - Click "Load" to apply the settings

2. **Save Configuration**:
   - Adjust settings as needed
   - Click "Save" to update the current configuration
   - Or enter a new name and click "Save As" to create a new configuration

3. **Delete Configuration**:
   - Select a configuration from the dropdown menu
   - Click "Delete" to remove it

### Default Configuration

If no configuration files exist, a default configuration will be automatically created with the following settings:

```json
{
  "model_name": "Model Name",
  "watermark": "Today is a\n Plus Day",
  "font_size": 90,
  "segment_duration": 6,
  "input_folder": "INPUT",
  "depthflow": 0,
  "time_limit": 600,
  "video_orientation": "vertical",
  "blur": 0
}
```

## Best Practices

1. **Create Multiple Presets**:
   - Create different presets for different types of content
   - Use descriptive names for easy identification

2. **Font Size Management**:
   - Leave font_size at 0 to use automatic calculation based on model name length
   - Or set a specific value for consistent sizing

3. **Time Management**:
   - Adjust segment_duration based on content type (shorter for fast-paced, longer for detailed)
   - Set time_limit according to platform requirements (e.g., 60 seconds for Instagram)

4. **Orientation Settings**:
   - Use "vertical" for mobile-focused content (9:16 aspect ratio)
   - Use "horizontal" for traditional video platforms (16:9 aspect ratio)
   - Enable blur for horizontal videos with vertical source material

## Troubleshooting

- **Missing Configuration**: If the dropdown is empty, a default configuration will be created automatically
- **Invalid JSON**: If a configuration file is corrupted, it may not appear in the list
- **Parameter Changes**: If new parameters are added to the system, older configuration files will use default values for those parameters
