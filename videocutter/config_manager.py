# videocutter/config_manager.py
# Handles loading, validation, and access to configuration.

import json
import os
from dotmap import DotMap # For easy dictionary access, similar to original argparse 'args'

class ConfigManager:
    def __init__(self, default_config_path: str = None, config_data: dict = None):
        self.config = DotMap()
        self._default_config_path = default_config_path
        
        if default_config_path and os.path.exists(default_config_path):
            try:
                with open(default_config_path, 'r') as f:
                    defaults = json.load(f)
                self.config.update(defaults)
                print(f"Loaded default configuration from: {default_config_path}")
            except Exception as e:
                print(f"Warning: Could not load default config from {default_config_path}: {e}")
        
        if config_data: # For direct initialization, e.g., from GUI
            self.config.update(config_data)
            print("Configuration updated with provided data.")
            
        self._apply_type_conversions_and_defaults()

    def _apply_type_conversions_and_defaults(self):
        """
        Ensures critical config values have correct types and applies defaults
        if values are missing or invalid.
        This is important because JSON loads numbers as int/float but sometimes
        they are stored as strings in the config file.
        """
        # General settings
        self.config.title = str(self.config.get('title', 'Default Model Name'))
        self.config.input_folder = str(self.config.get('input_folder', 'INPUT'))
        self.config.template_folder = str(self.config.get('template_folder', 'TEMPLATE'))
        self.config.fonts_folder = str(self.config.get('fonts_folder', 'fonts')) # New, useful for utils
        self.config.effects_folder = str(self.config.get('effects_folder', 'effects')) # New

        # Video processing
        self.config.video_orientation = str(self.config.get('video_orientation', 'vertical')).lower()
        self.config.segment_duration = int(self.config.get('segment_duration', 6))
        self.config.time_limit = int(self.config.get('time_limit', 595)) # Total clip duration
        self.config.fps = int(self.config.get('fps', 25))
        self.config.video_crf = int(self.config.get('video_crf', 22))
        self.config.video_preset = str(self.config.get('video_preset', 'medium'))
        self.config.audio_bitrate = str(self.config.get('audio_bitrate', '192k'))


        # Slideshow specific
        self.config.slide_duration = int(self.config.get('slide_duration', self.config.segment_duration)) # Default to segment_duration
        self.config.outro_duration = int(self.config.get('outro_duration', 14)) # Duration of the outro video itself
        self.config.transition_duration = float(self.config.get('transition_duration', 0.5))
        self.config.transitions = list(self.config.get('transitions', ['hblur', 'smoothup', 'horzopen', 'circleopen', 'diagtr', 'diagbl']))


        # DepthFlow
        self.config.depthflow.enabled = bool(self.config.get('depthflow', False)) # 'depthflow' in JSON was boolean
        self.config.depthflow.segment_duration = int(self.config.get('depthflow_segment_duration', self.config.segment_duration))
        self.config.depthflow.render_height = int(self.config.get('depthflow_render_height', 1920))
        self.config.depthflow.render_fps = int(self.config.get('depthflow_render_fps', self.config.fps))
        # Add other depthflow specific params from depth_processor.py defaults if needed

        # Title Overlay
        self.config.title_overlay.text = str(self.config.get('title', 'Model Name')) # Reuse 'title' for text
        self.config.title_overlay.font_file = str(self.config.get('title_font', 'Montserrat-SemiBold.otf'))
        self.config.title_overlay.font_size = int(self.config.get('title_font_size', 90))
        self.config.title_overlay.font_color = str(self.config.get('title_fontcolor', 'FFFFFF')) # Was '000000' in default_config, but 'random' in cutter.py
        self.config.title_overlay.start_delay = int(self.config.get('overlay_start_delay', 21)) # 'delay' in default_config was 1, but osd in cutter.py was 21
        self.config.title_overlay.appearance_delay = int(self.config.get('title_appearance_delay', 1))
        self.config.title_overlay.visible_time = int(self.config.get('title_visible_time', 5))
        self.config.title_overlay.x_offset = int(self.config.get('title_x_offset', 110))
        self.config.title_overlay.y_offset = int(self.config.get('title_y_offset', -35))

        # Watermark (during slideshow transitions)
        self.config.watermark.text = str(self.config.get('watermark', 'Today is a\\n Plus Day')).replace('\\n', '\n')
        self.config.watermark.type = str(self.config.get('watermark_type', 'random'))
        self.config.watermark.speed_frames = int(self.config.get('watermark_speed', 50))
        self.config.watermark.font_file_path = str(self.config.get('watermark_font', 'Nexa Bold.otf')) # Will need resolving to full path
        self.config.watermark.font_size = int(self.config.get('watermark_font_size', 40)) # Default from slideshow.py
        self.config.watermark.opacity = float(self.config.get('watermark_opacity', 0.7)) # Default from slideshow.py
        
        # Subscribe Overlay (final overlay)
        self.config.subscribe_overlay.chromakey_color = str(self.config.get('chromakey_color', '65db41'))
        self.config.subscribe_overlay.similarity = float(self.config.get('chromakey_similarity', 0.18))
        self.config.subscribe_overlay.blend = float(self.config.get('chromakey_blend', 0.0))
        self.config.subscribe_overlay.start_delay = int(self.config.get('overlay_start_delay', 21)) # Same as title_overlay.start_delay

        # Effects Overlay
        self.config.effects.overlay_file = self.config.get('effect_overlay') # Can be None
        if isinstance(self.config.effects.overlay_file, str) and self.config.effects.overlay_file.lower() == 'none':
            self.config.effects.overlay_file = None
        self.config.effects.opacity = float(self.config.get('effect_opacity', 0.2))
        self.config.effects.blend_mode = str(self.config.get('effect_blend', 'overlay'))

        # Audio processing
        self.config.audio.outro_duration = int(self.config.get('outro_duration', 14)) # From audio.py args
        self.config.audio.vo_delay = int(self.config.get('vo_delay', 5)) # From audio.py args
        # Add other audio specific params from audio_processor.py defaults if needed

        # Subtitles
        self.config.subtitles.enabled = str(self.config.get('generate_srt', '0')) == '1' # from cutter.py args
        self.config.subtitles.max_line_width = int(self.config.get('subtitle_max_width', 42)) # from srt_generator.py
        self.config.subtitles.font_name = str(self.config.get('subtitle_font', 'Arial'))
        self.config.subtitles.font_size = int(self.config.get('subtitle_fontsize', 24))
        self.config.subtitles.font_color_hex = str(self.config.get('subtitle_fontcolor', 'FFFFFF'))
        self.config.subtitles.shadow_color_hex = str(self.config.get('subtitle_bgcolor', '000000')) # 'bgcolor' in JSON
        self.config.subtitles.shadow_opacity = float(self.config.get('subtitle_bgopacity', 0.5)) # 'bgopacity' in JSON
        self.config.subtitles.shadow_enabled = bool(self.config.get('subtitle_shadow', True)) # 'shadow' in JSON
        self.config.subtitles.position_ass = int(self.config.get('subtitle_position', 2))
        self.config.subtitles.outline_thickness = float(self.config.get('subtitle_outline', 1.0))
        self.config.subtitles.outline_color_hex = str(self.config.get('subtitle_outlinecolor', '000000'))
        # WhisperX specific settings
        self.config.subtitles.language = str(self.config.get('subtitle_language', 'en'))
        self.config.subtitles.whisper_model = str(self.config.get('subtitle_whisper_model', 'base'))
        self.config.subtitles.device = str(self.config.get('subtitle_device', 'cpu'))
        self.config.subtitles.compute_type = str(self.config.get('subtitle_compute_type', 'float32'))


    def get(self, key, default=None):
        return self.config.get(key, default)

    def __getitem__(self, key):
        return self.config[key]

    def __str__(self):
        return str(self.config.toDict()) # Pretty print if needed

def load_config(config_path: str = None, initial_data: dict = None) -> DotMap:
    """
    Loads configuration from a JSON file and merges with initial_data.
    If config_path is None, tries to load from 'config/default_config.json'.
    """
    if config_path is None:
        # Try a default path relative to the project root
        # This assumes the script is run from project root or config_manager.py is in a known location
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # videocutter/ -> project root
        default_path = os.path.join(project_root, "config", "default_config.json")
        if os.path.exists(default_path):
            config_path = default_path
        else:
            print("Warning: Default config path not found, using empty base config.")
            
    manager = ConfigManager(default_config_path=config_path, config_data=initial_data)
    return manager.config


if __name__ == "__main__":
    print("Testing ConfigManager...")
    
    # Test loading default (assuming config/default_config.json exists relative to project root)
    # For this test to run standalone, ensure path is correct or provide one.
    # Let's assume a test config for this example
    test_config_dir = "temp_config_test"
    os.makedirs(test_config_dir, exist_ok=True)
    test_config_path = os.path.join(test_config_dir, "test_cfg.json")
    
    sample_data = {
        "title": "My Test Video", 
        "segment_duration": "7",
        "depthflow": "true", # Test string to bool conversion
        "watermark_speed": 60
    }
    with open(test_config_path, 'w') as f:
        json.dump(sample_data, f)

    cfg = load_config(config_path=test_config_path)
    print("\nLoaded Config:")
    print(f"Title: {cfg.title} (type: {type(cfg.title)})")
    print(f"Segment Duration: {cfg.segment_duration} (type: {type(cfg.segment_duration)})")
    print(f"Depthflow Enabled: {cfg.depthflow.enabled} (type: {type(cfg.depthflow.enabled)})")
    print(f"Watermark Speed: {cfg.watermark.speed_frames} (type: {type(cfg.watermark.speed_frames)})")
    print(f"Input Folder: {cfg.input_folder}") # Should come from internal defaults

    # Test with initial_data overriding file
    gui_settings = {"title": "GUI Overridden Title", "time_limit": "300"}
    cfg_merged = load_config(config_path=test_config_path, initial_data=gui_settings)
    print("\nMerged Config (GUI override):")
    print(f"Title: {cfg_merged.title}")
    print(f"Time Limit: {cfg_merged.time_limit} (type: {type(cfg_merged.time_limit)})")
    print(f"Segment Duration: {cfg_merged.segment_duration}") # From file

    # Clean up
    os.remove(test_config_path)
    os.rmdir(test_config_dir)
    print("\nConfigManager test complete.")
