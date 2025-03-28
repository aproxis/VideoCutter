# Configuration Files

This directory contains configuration files for the VideoCutter application. These files store settings that can be loaded and saved through the GUI.

## File Format

Configuration files are in JSON format and contain the following settings:

```json
{
  "model_name": "Model Name",
  "watermark": "Watermark Text",
  "font_size": 90,
  "segment_duration": 6,
  "input_folder": "INPUT",
  "depthflow": 0,
  "time_limit": 600,
  "video_orientation": "vertical",
  "blur": 0
}
```

## Settings

- `model_name`: The name of the model to display in the video
- `watermark`: Text to display as a watermark (use \n for line breaks)
- `font_size`: Font size for the model name
- `segment_duration`: Duration of each video segment in seconds
- `input_folder`: Folder containing input videos and images
- `depthflow`: Whether to use DepthFlow for images (0 = off, 1 = on)
- `time_limit`: Maximum duration of the final video in seconds
- `video_orientation`: Orientation of the video ("vertical" or "horizontal")
- `blur`: Whether to add blur effect (0 = off, 1 = on)

## Included Configurations

- `vertical_config.json`: Configuration for vertical videos (9:16 aspect ratio)
- `horizontal_config.json`: Configuration for horizontal videos (16:9 aspect ratio) with blur effect enabled

## Creating New Configurations

You can create new configurations in two ways:

1. Through the GUI:
   - Set your desired parameters
   - Enter a filename in the "Save as" field
   - Click the "Save As" button

2. Manually:
   - Create a new JSON file in this directory
   - Follow the format shown above
   - The file will be automatically detected by the application

## Loading Configurations

To load a configuration:
1. Start the GUI application
2. Select the configuration from the dropdown menu at the top
3. The settings will be automatically loaded
