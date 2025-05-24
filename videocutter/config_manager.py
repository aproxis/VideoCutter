# videocutter/config_manager.py
# Handles loading, validation, and access to configuration.

import json
import os
from dotmap import DotMap # For easy dictionary access, similar to original argparse 'args'

class ConfigManager:
    def __init__(self, 
                 global_default_config_path: str = None, 
                 project_specific_config_path: str = None, # New: path to _project_config.json
                 runtime_overrides: dict = None): # New: for GUI/CLI overrides
        
        self.config = DotMap()
        self._global_default_config_path = global_default_config_path
        self._project_specific_config_path = project_specific_config_path
        
        # 1. Load global default config
        if global_default_config_path and os.path.exists(global_default_config_path):
            try:
                with open(global_default_config_path, 'r') as f:
                    global_defaults = json.load(f)
                self.config.update(global_defaults)
                print(f"Loaded global default configuration from: {global_default_config_path}")
            except Exception as e:
                print(f"Warning: Could not load global default config from {global_default_config_path}: {e}")
        else:
            print(f"Info: Global default config path not provided or not found: {global_default_config_path}")

        # 2. Load project-specific config (overrides global defaults)
        if project_specific_config_path and os.path.exists(project_specific_config_path):
            try:
                with open(project_specific_config_path, 'r') as f:
                    project_cfg_data = json.load(f)
                self.config.update(project_cfg_data) # Merge, project specifics take precedence
                print(f"Loaded and merged project-specific configuration from: {project_specific_config_path}")
            except Exception as e:
                print(f"Warning: Could not load project-specific config from {project_specific_config_path}: {e}")
        else:
            if project_specific_config_path: # Path was given but file not found
                 print(f"Info: Project-specific config file not found at: {project_specific_config_path}")

        # 3. Apply runtime overrides (e.g., from GUI, highest precedence)
        if runtime_overrides:
            print(f"Runtime overrides provided: {runtime_overrides.get('generate_srt', 'Not in runtime_overrides')}")
            self.config.update(runtime_overrides)
            print("Configuration updated with runtime overrides.")
            
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
        self.config.effects_folder = str(self.config.get('effects_folder', os.path.join('effects', 'overlays'))) # Updated default
        self.config.subscribe_folder = str(self.config.get('subscribe_folder', os.path.join('effects', 'subscribe'))) # New
        self.config.title_folder = str(self.config.get('title_folder', os.path.join('effects', 'title'))) # New

        # Video processing
        self.config.video_orientation = str(self.config.get('video_orientation', 'vertical')).lower()
        self.config.segment_duration = int(self.config.get('segment_duration', 6))
        self.config.time_limit = int(self.config.get('time_limit', 595)) # Total clip duration
        self.config.fps = int(self.config.get('fps', 25))
        self.config.video_crf = int(self.config.get('video_crf', 22))
        self.config.video_preset = str(self.config.get('video_preset', 'medium'))
        self.config.audio_bitrate = str(self.config.get('audio_bitrate', '192k'))

        # Image/Video processing options
        if not isinstance(self.config.get('image_options'), (dict, DotMap)): self.config.image_options = DotMap()
        self.config.image_options.apply_side_blur = bool(self.config.get('blur', False)) # From JSON 'blur' or gui_settings['blur']


        # Slideshow specific
        # slide_duration is the effective time each main segment/image is shown *before* transition starts eating into it.
        # Original slideshow.py used segment_duration - 1 for this.
        default_slide_duration = self.config.segment_duration - 1 if self.config.segment_duration > 1 else 1
        self.config.slide_duration = int(self.config.get('slide_duration', default_slide_duration))
        self.config.outro_duration = int(self.config.get('outro_duration', 14)) # Duration of the outro video itself
        self.config.transition_duration = float(self.config.get('transition_duration', 0.5))
        self.config.transitions = list(self.config.get('transitions', ['hblur', 'smoothup', 'horzopen', 'circleopen', 'diagtr', 'diagbl']))


        # DepthFlow
        depthflow_config_source = self.config.get('depthflow')
        if not isinstance(depthflow_config_source, (dict, DotMap)):
            # If 'depthflow' was a boolean (e.g., from JSON) or not present, initialize as DotMap
            self.config.depthflow = DotMap()
            self.config.depthflow.enabled = bool(depthflow_config_source) # Use the boolean if it was one
        else: # It was already a dict/DotMap, ensure it's a DotMap
            self.config.depthflow = DotMap(depthflow_config_source)
        
        self.config.depthflow.enabled = bool(self.config.depthflow.get('enabled', depthflow_config_source if isinstance(depthflow_config_source, bool) else False))
        self.config.depthflow.segment_duration = int(self.config.depthflow.get('segment_duration', self.config.segment_duration))
        self.config.depthflow.render_height = int(self.config.depthflow.get('render_height', 1920))
        self.config.depthflow.render_fps = int(self.config.depthflow.get('render_fps', self.config.fps))
        # Add other depthflow specific params from depth_processor.py defaults if needed

        # Title Overlay
        if not isinstance(self.config.get('title_overlay'), (dict, DotMap)): self.config.title_overlay = DotMap()
        self.config.title_overlay.text = str(self.config.get('title', self.config.title_overlay.get('text', 'Model Name')))
        self.config.title_overlay.font_file = str(self.config.title_overlay.get('font_file', self.config.get('title_font', 'Montserrat-SemiBold.otf')))
        self.config.title_overlay.font_size = int(self.config.title_overlay.get('font_size', self.config.get('title_font_size', 90)))
        self.config.title_overlay.font_color = str(self.config.title_overlay.get('font_color', self.config.get('title_fontcolor', 'FFFFFF')))
        self.config.title_overlay.appearance_delay = int(self.config.title_overlay.get('appearance_delay', self.config.get('title_appearance_delay', 1)))
        self.config.title_overlay.visible_time = int(self.config.title_overlay.get('visible_time', self.config.get('title_visible_time', 5)))
        self.config.title_overlay.x_offset = int(self.config.title_overlay.get('x_offset', self.config.get('title_x_offset', 110)))
        self.config.title_overlay.y_offset = int(self.config.title_overlay.get('y_offset', self.config.get('title_y_offset', -35)))
        self.config.title_overlay.enabled = bool(self.config.title_overlay.get('enabled', self.config.get('enable_title', True)))
        self.config.title_overlay.opacity = float(self.config.title_overlay.get('opacity', self.config.get('title_opacity', 1.0)))
        self.config.title_overlay.enable_background = bool(self.config.title_overlay.get('enable_background', self.config.get('enable_title_background', False)))
        self.config.title_overlay.background_color = str(self.config.title_overlay.get('background_color', self.config.get('title_background_color', '000000')))
        self.config.title_overlay.background_opacity = float(self.config.title_overlay.get('background_opacity', self.config.get('title_background_opacity', 0.5)))

        # Watermark (during slideshow transitions)
        if not isinstance(self.config.get('watermark_settings'), (dict, DotMap)): self.config.watermark_settings = DotMap() # Changed key to avoid conflict if 'watermark' is just text
        self.config.watermark_settings.text = str(self.config.get('watermark', self.config.watermark_settings.get('text', 'Today is a\\n Plus Day'))).replace('\\n', '\n')
        self.config.watermark_settings.type = str(self.config.watermark_settings.get('type', self.config.get('watermark_type', 'random')))
        self.config.watermark_settings.speed_frames = int(self.config.watermark_settings.get('speed_frames', self.config.get('watermark_speed', 50)))
        self.config.watermark_settings.font_file_path = str(self.config.watermark_settings.get('font_file_path', self.config.get('watermark_font', 'Nexa Bold.otf')))
        self.config.watermark_settings.font_size = int(self.config.watermark_settings.get('font_size', 40))
        self.config.watermark_settings.opacity = float(self.config.watermark_settings.get('opacity', 0.7))
        
        # Subscribe Overlay (final overlay)
        if not isinstance(self.config.get('subscribe_overlay'), (dict, DotMap)): self.config.subscribe_overlay = DotMap()
        self.config.subscribe_overlay.enabled = bool(self.config.subscribe_overlay.get('enabled', self.config.get('enable_subscribe_overlay', True)))
        self.config.subscribe_overlay.overlay_file = str(self.config.subscribe_overlay.get('overlay_file', self.config.get('subscribe_overlay_file', 'None'))) # New: overlay file selection
        if self.config.subscribe_overlay.overlay_file.lower() == 'none':
            self.config.subscribe_overlay.overlay_file = None
        self.config.subscribe_overlay.appearance_delay = int(self.config.subscribe_overlay.get('appearance_delay', self.config.get('subscribe_delay', 21)))
        self.config.subscribe_overlay.chromakey_color = str(self.config.subscribe_overlay.get('chromakey_color', self.config.get('chromakey_color', '65db41')))
        self.config.subscribe_overlay.similarity = float(self.config.subscribe_overlay.get('similarity', self.config.get('chromakey_similarity', 0.18)))
        self.config.subscribe_overlay.blend = float(self.config.subscribe_overlay.get('blend', self.config.get('chromakey_blend', 0.0)))

        # Title Video Overlay (new section)
        if not isinstance(self.config.get('title_video_overlay'), (dict, DotMap)): self.config.title_video_overlay = DotMap()
        self.config.title_video_overlay.enabled = bool(self.config.title_video_overlay.get('enabled', self.config.get('enable_title_video_overlay', False)))
        self.config.title_video_overlay.overlay_file = str(self.config.title_video_overlay.get('overlay_file', self.config.get('title_video_overlay_file', 'None')))
        if self.config.title_video_overlay.overlay_file.lower() == 'none':
            self.config.title_video_overlay.overlay_file = None
        self.config.title_video_overlay.appearance_delay = int(self.config.title_video_overlay.get('appearance_delay', self.config.get('title_video_overlay_delay', 0)))
        self.config.title_video_overlay.chromakey_color = str(self.config.title_video_overlay.get('chromakey_color', self.config.get('title_video_chromakey_color', '65db41')))
        self.config.title_video_overlay.similarity = float(self.config.title_video_overlay.get('similarity', self.config.get('title_video_chromakey_similarity', 0.18)))
        self.config.title_video_overlay.blend = float(self.config.title_video_overlay.get('blend', self.config.get('title_video_chromakey_blend', 0.0)))

        # Effects Overlay
        if not isinstance(self.config.get('effects'), (dict, DotMap)): self.config.effects = DotMap()
        self.config.effects.overlay_file = self.config.effects.get('overlay_file', self.config.get('effect_overlay'))
        if isinstance(self.config.effects.overlay_file, str) and self.config.effects.overlay_file.lower() == 'none':
            self.config.effects.overlay_file = None
        self.config.effects.opacity = float(self.config.effects.get('opacity', self.config.get('effect_opacity', 0.2)))
        self.config.effects.blend_mode = str(self.config.effects.get('blend_mode', self.config.get('effect_blend', 'overlay')))
        self.config.effects.enabled = bool(self.config.effects.get('enabled', self.config.get('enable_effect_overlay', True))) # New

        # Audio processing
        if not isinstance(self.config.get('audio'), (dict, DotMap)): self.config.audio = DotMap()
        self.config.audio.outro_duration = int(self.config.get('outro_duration', self.config.audio.get('outro_duration', 14))) # Prioritize top-level if it exists
        self.config.audio.vo_delay = int(self.config.get('vo_delay', self.config.audio.get('vo_delay', 5))) # Prioritize top-level 'vo_delay' (from GUI)
        # Add other audio specific params from audio_processor.py defaults if needed

        # Subtitles
        if not isinstance(self.config.get('subtitles'), (dict, DotMap)): self.config.subtitles = DotMap()
        
        # Determine the source for 'enabled' state: runtime 'generate_srt', then config 'generate_srt', then config 'subtitles.enabled'
        # Default to '0' (string false) if none are found.
        generate_srt_val = self.config.get('generate_srt', '0') # Check top-level first (from runtime or merged JSON)
        
        # If 'subtitles' dict exists and has 'enabled', it might take precedence if 'generate_srt' wasn't from runtime
        # However, the current DotMap update order should mean runtime 'generate_srt' wins.
        # Let's simplify: if 'generate_srt' (bool from GUI) is in self.config, use it. Otherwise, check 'subtitles.enabled'.
        
        if 'generate_srt' in self.config and isinstance(self.config.generate_srt, bool):
            self.config.subtitles.enabled = self.config.generate_srt
            print(f"Subtitle enabled status from top-level 'generate_srt' (bool): {self.config.subtitles.enabled}")
        else:
            # Fallback to checking string '0'/'1' or a nested 'enabled'
            enabled_source_val = self.config.subtitles.get('enabled', self.config.get('generate_srt', '0'))
            self.config.subtitles.enabled = str(enabled_source_val).lower() in ['true', '1']
            print(f"Subtitle enabled status from string/nested (source: '{enabled_source_val}'): {self.config.subtitles.enabled}")

        self.config.subtitles.max_line_width = int(self.config.subtitles.get('max_line_width', self.config.get('subtitle_max_width', self.config.get('subtitle_maxwidth', 42))))
        self.config.subtitles.font_name = str(self.config.subtitles.get('font_name', self.config.get('subtitle_font', 'Arial')))
        self.config.subtitles.font_size = int(self.config.subtitles.get('font_size', self.config.get('subtitle_fontsize', 24)))
        self.config.subtitles.font_color_hex = str(self.config.subtitles.get('font_color_hex', self.config.get('subtitle_fontcolor', 'FFFFFF')))
        self.config.subtitles.shadow_color_hex = str(self.config.subtitles.get('shadow_color_hex', self.config.get('subtitle_bgcolor', '000000')))
        self.config.subtitles.shadow_opacity = float(self.config.subtitles.get('shadow_opacity', self.config.get('subtitle_bgopacity', 0.5)))
        self.config.subtitles.shadow_enabled = bool(self.config.subtitles.get('shadow_enabled', self.config.get('subtitle_shadow', True)))
        self.config.subtitles.position_ass = int(self.config.subtitles.get('position_ass', self.config.get('subtitle_position', 2)))
        self.config.subtitles.outline_thickness = float(self.config.subtitles.get('outline_thickness', self.config.get('subtitle_outline', 1.0)))
        self.config.subtitles.outline_color_hex = str(self.config.subtitles.get('outline_color_hex', self.config.get('subtitle_outlinecolor', '000000')))
        # WhisperX specific settings
        self.config.subtitles.language = str(self.config.subtitles.get('language', self.config.get('subtitle_language', 'en')))
        self.config.subtitles.whisper_model = str(self.config.subtitles.get('whisper_model', self.config.get('subtitle_whisper_model', 'base')))
        self.config.subtitles.device = str(self.config.subtitles.get('device', self.config.get('subtitle_device', 'cpu')))
        self.config.subtitles.compute_type = str(self.config.subtitles.get('compute_type', self.config.get('subtitle_compute_type', 'float32')))


    def get(self, key, default=None): # Keep this simple get for direct access
        return self.config.get(key, default)

    def __getitem__(self, key):
        return self.config[key]

    def __str__(self):
        return str(self.config.toDict())

def load_config(
    global_config_path: str = None, 
    project_folder_path: str = None, # New: For batch mode, path to the specific project's folder
    runtime_settings: dict = None,   # New: For GUI/CLI overrides
    project_config_filename: str = "_project_config.json" # Standard name for project-local config
    ) -> DotMap:
    """
    Loads configuration with a hierarchical approach:
    1. Global default config file (e.g., 'config/default_config.json' or path from GUI).
    2. Project-specific config file (e.g., 'BATCH_INPUTS/Project_Alpha/_project_config.json').
    3. Runtime settings (e.g., from GUI or CLI).
    Later sources override earlier ones.
    """
    
    # Determine global_config_path if not provided
    if global_config_path is None:
        # Assuming videocutter package is one level down from project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        default_global_path = os.path.join(project_root, "config", "default_config.json")
        if os.path.exists(default_global_path):
            global_config_path = default_global_path
            print(f"Using default global config: {global_config_path}")
        else:
            print("Warning: No global_config_path provided and default_config.json not found. Starting with empty base config.")

    project_specific_cfg_path = None
    if project_folder_path and project_config_filename:
        path_to_check = os.path.join(project_folder_path, project_config_filename)
        if os.path.exists(path_to_check):
            project_specific_cfg_path = path_to_check
            print(f"Found project-specific config: {project_specific_cfg_path}")
        else:
            print(f"No project-specific config '{project_config_filename}' found in {project_folder_path}.")
            
    manager = ConfigManager(
        global_default_config_path=global_config_path,
        project_specific_config_path=project_specific_cfg_path,
        runtime_overrides=runtime_settings
    )
    return manager.config


if __name__ == "__main__":
    print("Testing ConfigManager...")
    
    # Create dummy config files for testing
    test_project_root = "temp_test_project_root"
    os.makedirs(os.path.join(test_project_root, "config"), exist_ok=True)
    os.makedirs(os.path.join(test_project_root, "batch_projects", "ProjectA"), exist_ok=True)

    default_global_cfg_path = os.path.join(test_project_root, "config", "global.json")
    project_a_cfg_path = os.path.join(test_project_root, "batch_projects", "ProjectA", "_project_config.json")

    with open(default_global_cfg_path, 'w') as f:
        json.dump({"title": "Global Title", "segment_duration": "5", "global_setting": True, "depthflow": False}, f)
    
    with open(project_a_cfg_path, 'w') as f:
        json.dump({"title": "ProjectA Title", "segment_duration": "8", "project_setting": "AlphaValue", "depthflow": True}, f)

    print("\n--- Test 1: Loading Global Default Only ---")
    # Mock __file__ to be inside a 'videocutter' subdirectory for project_root calculation
    original_file_attr = __file__
    __file__ = os.path.join(test_project_root, "videocutter", "config_manager.py") # Mock path
    cfg1 = load_config(global_config_path=default_global_cfg_path)
    __file__ = original_file_attr # Restore
    print(f"Title: {cfg1.title}, Seg Dur: {cfg1.segment_duration}, Global: {cfg1.global_setting}, DepthFlow Enabled: {cfg1.depthflow.enabled}")

    print("\n--- Test 2: Loading Global + Project Specific ---")
    __file__ = os.path.join(test_project_root, "videocutter", "config_manager.py") # Mock path
    cfg2 = load_config(global_config_path=default_global_cfg_path, 
                       project_folder_path=os.path.join(test_project_root, "batch_projects", "ProjectA"))
    __file__ = original_file_attr # Restore
    print(f"Title: {cfg2.title}, Seg Dur: {cfg2.segment_duration}, Global: {cfg2.global_setting}, Project: {cfg2.project_setting}, DepthFlow Enabled: {cfg2.depthflow.enabled}")

    print("\n--- Test 3: Loading Global + Project Specific + Runtime Overrides ---")
    runtime_settings = {"title": "Runtime Title", "segment_duration": "10", "runtime_setting": "XYZ"}
    __file__ = os.path.join(test_project_root, "videocutter", "config_manager.py") # Mock path
    cfg3 = load_config(global_config_path=default_global_cfg_path, 
                       project_folder_path=os.path.join(test_project_root, "batch_projects", "ProjectA"),
                       runtime_settings=runtime_settings)
    __file__ = original_file_attr # Restore
    print(f"Title: {cfg3.title}, Seg Dur: {cfg3.segment_duration}, Global: {cfg3.global_setting}, Project: {cfg3.project_setting}, Runtime: {cfg3.runtime_setting}, DepthFlow Enabled: {cfg3.depthflow.enabled}")
    
    print(f"\n--- Test 4: Referencing a nested attribute from JSON (depthflow: true) ---")
    test_config_dir_bool = "temp_config_test_bool"
    os.makedirs(test_config_dir_bool, exist_ok=True)
    test_config_path_bool = os.path.join(test_config_dir_bool, "test_cfg_bool.json")
    sample_data_bool = {"depthflow": True, "segment_duration": "7"} # depthflow is a boolean
    with open(test_config_path_bool, 'w') as f: json.dump(sample_data_bool, f)
    
    __file__ = os.path.join(test_project_root, "videocutter", "config_manager.py") # Mock path
    cfg4 = load_config(global_config_path=test_config_path_bool)
    __file__ = original_file_attr # Restore
    print(f"Depthflow Enabled: {cfg4.depthflow.enabled} (type: {type(cfg4.depthflow.enabled)})")
    print(f"Segment Duration: {cfg4.segment_duration} (type: {type(cfg4.segment_duration)})")


    # Clean up
    shutil.rmtree(test_project_root, ignore_errors=True)
    shutil.rmtree(test_config_dir_bool, ignore_errors=True)
    print("\nConfigManager test complete.")
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
