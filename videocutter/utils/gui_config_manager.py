import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
import glob
import logging
from videocutter.gui.logging_settings_frame import LoggingSettingsFrame

logger = logging.getLogger("videocutter.utils.gui_config_manager")

# Default values for GUI elements
# These are now the single source of truth for default settings
debug_logging_enabled = False # New: Default for debug logging
title = 'Model Name'
watermark = 'Today is a\n Plus Day'
watermark_type = 'random'
watermark_speed = 50 # This is the FFmpeg speed, not intuitive
title_font_size = 90
segment_duration = 6
input_folder = 'INPUT'
template_folder = 'TEMPLATE'
depthflow = 0 # Boolean 0 or 1
time_limit = 600
watermark_font = 'Nexa Bold.otf'
enable_watermark = True
watermark_font_size = 40
watermark_opacity = 0.7
watermark_fontcolor = 'random'
watermark_speed_intuitive = 5 # Intuitive speed 1-10
transition_duration = 0.5 # New: Default transition duration in seconds
fps = 30 # New: Default frames per second
subscribe_delay = 21
title_fontcolor = 'random'
title_font = 'Montserrat-Semi-Bold.otf'
voiceover_delay = 5
title_appearance_delay = 1
title_visible_time = 5
title_x_offset = 110
title_y_offset = -35
enable_title = True
title_opacity = 1.0
enable_title_background = False
title_background_color = '000000'
title_background_opacity = 0.5
enable_subscribe_overlay = True
title_video_overlay_file = 'None'
enable_title_video_overlay = False
title_video_overlay_delay = 0
title_video_chromakey_color = '65db41'
title_video_chromakey_similarity = 0.18
title_video_chromakey_blend = 0
chromakey_color = '65db41'
chromakey_similarity = 0.18
chromakey_blend = 0
enable_subtitles = False # Renamed from generate_srt
subtitle_maxwidth = 21
subtitle_font = "Arial"
subtitle_fontsize = 48
subtitle_fontcolor = "FFFFFF"
subtitle_bgcolor = "000000"
subtitle_bgopacity = 0.5
subtitle_position = 2
subtitle_outline = 1
subtitle_outlinecolor = "000000"
subtitle_shadow = True
subtitle_format = 'ass' # New: Default subtitle format is now ASS
punctuation_fix_enabled = False # New: Enable/disable punctuation fix

# New ASS subtitle style parameters
subtitle_secondary_color = "00FFFFFF" # Default to white (BBGGRR)
subtitle_bold = -1 # -1 for bold, 0 for normal
subtitle_italic = 0 # 0 for normal, -1 for italic
subtitle_underline = 0 # 0 for normal, -1 for underlined
subtitle_strikeout = 0 # 0 for normal, -1 for strikeout
subtitle_scale_x = 100 # Percentage
subtitle_scale_y = 100 # Percentage
subtitle_spacing = 0.0 # Pixels
subtitle_angle = 0 # Degrees
subtitle_border_style = 1 # 1 for outline+shadow, 3 for opaque box
subtitle_shadow_distance = 1.0 # Pixels
subtitle_margin_l = 10 # Left margin
subtitle_margin_r = 10 # Right margin
subtitle_margin_v = 10 # Vertical margin
subtitle_encoding = 1 # Character set (1 for ANSI, 0 for default)

effect_overlay = 'None'
effect_opacity = 0.2
effect_blend = 'overlay'
enable_effect_overlay = True # Added this line
video_orientation = 'vertical' # Default video orientation
blur = 0 # Default blur setting
batch_input_folder = '' # New: Default for batch input folder

# DepthFlow settings
enable_depthflow = False
depthflow_vignette_enable = True
depthflow_dof_enable = True
depthflow_isometric_min = 0.4
depthflow_isometric_max = 0.5
depthflow_height_min = 0.1
depthflow_height_max = 0.15
depthflow_zoom_min = 0.65
depthflow_zoom_max = 0.75
depthflow_min_effects_per_image = 2 # Updated default
depthflow_max_effects_per_image = 4 # Updated default
depthflow_base_zoom_loops = False
depthflow_workers = 1

# New DepthFlow parameters
depthflow_height = 0.3
depthflow_offset_x = 0.0
depthflow_offset_y = 0.0
depthflow_steady = 0.0
depthflow_isometric = 0.5
depthflow_dolly = 0.0
depthflow_focus = 0.0
depthflow_zoom = 1.0
depthflow_invert = 0.0
depthflow_center_x = 0.0
depthflow_center_y = 0.0
depthflow_origin_x = 0.0
depthflow_origin_y = 0.0
depthflow_zoom_probability = 0.3 # New

# Define watermark types
watermark_types = ['ccw', 'random']

# Define font color options
font_colors = ['random', 'FF00B4', 'ff6600', '0b4178', 'FFFFFF', '000000', '00FF00', '0000FF', 'FFFF00']

# Define supported blend modes for effects
SUPPORTED_BLEND_MODES = [
    'normal',
    'overlay',
]

# Get available fonts from the fonts directory
fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts')
available_fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
if not available_fonts:
    available_fonts = ['Nexa Bold.otf']

# Define overlay directories
overlays_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'effects', 'overlays')
subscribe_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'effects', 'subscribe')
title_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'effects', 'title')

# Get available effect files (general overlays)
if not os.path.exists(overlays_dir):
    os.makedirs(overlays_dir)
effect_files = ["None"] + [f for f in os.listdir(overlays_dir) if f.endswith('.mp4')]

# Get available subscribe overlay files
if not os.path.exists(subscribe_dir):
    os.makedirs(subscribe_dir)
subscribe_overlay_files = ["None"] + [f for f in os.listdir(subscribe_dir) if f.endswith('.mp4')]

# Get available title video overlay files
if not os.path.exists(title_dir):
    os.makedirs(title_dir)
title_video_overlay_files = ["None"] + [f for f in os.listdir(title_dir) if f.endswith('.mp4')]


config_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]

def create_default_config():
    default_config = {
        'debug_logging_enabled': debug_logging_enabled, # New
        'title': title,
        'watermark': watermark,
        'watermark_type': watermark_type,
        'watermark_speed': watermark_speed,
        'title_font_size': title_font_size,
        'segment_duration': segment_duration,
        'input_folder': input_folder,
        'template_folder': template_folder,
        'depthflow': depthflow,
        'time_limit': time_limit,
        'video_orientation': video_orientation,
        'blur': blur,
        'watermark_font': watermark_font,
        'enable_watermark': enable_watermark,
        'watermark_font_size': watermark_font_size,
        'watermark_opacity': watermark_opacity,
        'watermark_fontcolor': watermark_fontcolor,
        'watermark_speed_intuitive': watermark_speed_intuitive,
        'transition_duration': transition_duration, # New
        'fps': fps, # New
        'subscribe_delay': subscribe_delay,
        'title_fontcolor': title_fontcolor,
        'title_font': title_font,
        'voiceover_delay': voiceover_delay,
        'title_appearance_delay': title_appearance_delay,
        'title_visible_time': title_visible_time,
        'title_x_offset': title_x_offset,
        'title_y_offset': title_y_offset,
        'enable_title': enable_title,
        'title_opacity': title_opacity,
        'enable_title_background': enable_title_background,
        'title_background_color': title_background_color,
        'title_background_opacity': title_background_opacity,
        'enable_subscribe_overlay': enable_subscribe_overlay,
        'subscribe_overlay_file': "None", # Default for subscribe overlay file
        'title_video_overlay_file': title_video_overlay_file,
        'enable_title_video_overlay': enable_title_video_overlay,
        'title_video_overlay_delay': title_video_overlay_delay,
        'title_video_chromakey_color': title_video_chromakey_color,
        'title_video_chromakey_similarity': title_video_chromakey_similarity,
        'title_video_chromakey_blend': title_video_chromakey_blend,
        'chromakey_color': chromakey_color,
        'chromakey_similarity': chromakey_similarity,
        'chromakey_blend': chromakey_blend,
        'enable_subtitles': enable_subtitles, # Renamed from generate_srt
        'subtitle_maxwidth': subtitle_maxwidth,
        'subtitle_font': subtitle_font,
        'subtitle_fontsize': subtitle_fontsize,
        'subtitle_fontcolor': subtitle_fontcolor,
        'subtitle_bgcolor': subtitle_bgcolor,
        'subtitle_bgopacity': subtitle_bgopacity,
        'subtitle_position': subtitle_position,
        'subtitle_outline': subtitle_outline,
        'subtitle_outlinecolor': subtitle_outlinecolor,
        'subtitle_shadow': subtitle_shadow,
        'subtitle_format': subtitle_format, # New: Subtitle format
        'punctuation_fix_enabled': punctuation_fix_enabled, # New: Punctuation fix enabled
        'subtitle_secondary_color': subtitle_secondary_color,
        'subtitle_bold': subtitle_bold,
        'subtitle_italic': subtitle_italic,
        'subtitle_underline': subtitle_underline,
        'subtitle_strikeout': subtitle_strikeout,
        'subtitle_scale_x': subtitle_scale_x,
        'subtitle_scale_y': subtitle_scale_y,
        'subtitle_spacing': subtitle_spacing,
        'subtitle_angle': subtitle_angle,
        'subtitle_border_style': subtitle_border_style,
        'subtitle_shadow_distance': subtitle_shadow_distance,
        'subtitle_margin_l': subtitle_margin_l,
        'subtitle_margin_r': subtitle_margin_r,
        'subtitle_margin_v': subtitle_margin_v,
        'subtitle_encoding': subtitle_encoding,
        'effect_overlay': effect_overlay,
        'effect_opacity': effect_opacity,
        'effect_blend': effect_blend,
        'enable_effect_overlay': enable_effect_overlay,
        'batch_input_folder': batch_input_folder, # New
        # DepthFlow settings
        'enable_depthflow': enable_depthflow,
        'depthflow_vignette_enable': depthflow_vignette_enable,
        'depthflow_dof_enable': depthflow_dof_enable,
        'depthflow_isometric_min': depthflow_isometric_min,
        'depthflow_isometric_max': depthflow_isometric_max,
        'depthflow_height_min': depthflow_height_min,
        'depthflow_height_max': depthflow_height_max,
        'depthflow_zoom_min': depthflow_zoom_min,
        'depthflow_zoom_max': depthflow_zoom_max,
        'depthflow_min_effects_per_image': depthflow_min_effects_per_image,
        'depthflow_max_effects_per_image': depthflow_max_effects_per_image,
        'depthflow_base_zoom_loops': depthflow_base_zoom_loops,
        'depthflow_workers': depthflow_workers,
        # New DepthFlow parameters
        'depthflow_height': depthflow_height,
        'depthflow_offset_x': depthflow_offset_x,
        'depthflow_offset_y': depthflow_offset_y,
        'depthflow_steady': depthflow_steady,
        'depthflow_isometric': depthflow_isometric,
        'depthflow_dolly': depthflow_dolly,
        'depthflow_focus': depthflow_focus,
        'depthflow_zoom': depthflow_zoom,
        'depthflow_invert': depthflow_invert,
        'depthflow_center_x': depthflow_center_x,
        'depthflow_center_y': depthflow_center_y,
        'depthflow_origin_x': depthflow_origin_x,
        'depthflow_origin_y': depthflow_origin_y,
        'depthflow_zoom_probability': depthflow_zoom_probability, # New
        # Logging settings
        "logging": {
            "root": "INFO",
            "main": "INFO",
            "gui": "INFO",
            "video_processor": "INFO",
            "audio_processor": "INFO",
            "subtitle_generator": "INFO",
            "depth_processor": "INFO",
            "overlay_compositor": "INFO",
            "file_utils": "INFO",
            "config_manager": "INFO",
            "gui_config_manager": "INFO",
            "font_utils": "INFO",
            "slideshow_generator": "INFO",
            "depthflow_settings_frame": "INFO",
            "gui_utils": "INFO",
            "main_settings_frame": "INFO",
            "overlay_effects_frame": "INFO",
            "subtitle_settings_frame": "INFO",
            "title_settings_frame": "INFO",
            "punctuation_utils": "INFO",
            "subtitle_processing_utils": "INFO",
        }
    }
    default_filename = "default_config.json"
    config_file = os.path.join(config_folder, default_filename)
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)
    logger.info(f"Default config created: {default_filename}")
    
    # Update the global config_files list after creating a new default config
    global config_files
    config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]
    
    return default_filename

def get_default_settings_dict():
    """
    Returns a dictionary containing all default GUI settings.
    """
    return {
        'debug_logging_enabled': debug_logging_enabled,
        'title': title,
        'watermark': watermark,
        'watermark_type': watermark_type,
        'watermark_speed': watermark_speed,
        'title_font_size': title_font_size,
        'segment_duration': segment_duration,
        'input_folder': input_folder,
        'template_folder': template_folder,
        'depthflow': depthflow,
        'time_limit': time_limit,
        'video_orientation': video_orientation,
        'blur': blur,
        'watermark_font': watermark_font,
        'enable_watermark': enable_watermark,
        'watermark_font_size': watermark_font_size,
        'watermark_opacity': watermark_opacity,
        'watermark_fontcolor': watermark_fontcolor,
        'watermark_speed_intuitive': watermark_speed_intuitive,
        'transition_duration': transition_duration,
        'fps': fps,
        'subscribe_delay': subscribe_delay,
        'title_fontcolor': title_fontcolor,
        'title_font': title_font,
        'voiceover_delay': voiceover_delay,
        'title_appearance_delay': title_appearance_delay,
        'title_visible_time': title_visible_time,
        'title_x_offset': title_x_offset,
        'title_y_offset': title_y_offset,
        'enable_title': enable_title,
        'title_opacity': title_opacity,
        'enable_title_background': enable_title_background,
        'title_background_color': title_background_color,
        'title_background_opacity': title_background_opacity,
        'enable_subscribe_overlay': enable_subscribe_overlay,
        'subscribe_overlay_file': "None",
        'title_video_overlay_file': title_video_overlay_file,
        'enable_title_video_overlay': enable_title_video_overlay,
        'title_video_overlay_delay': title_video_overlay_delay,
        'title_video_chromakey_color': title_video_chromakey_color,
        'title_video_chromakey_similarity': title_video_chromakey_similarity,
        'title_video_chromakey_blend': title_video_chromakey_blend,
        'chromakey_color': chromakey_color,
        'chromakey_similarity': chromakey_similarity,
        'chromakey_blend': chromakey_blend,
        'enable_subtitles': enable_subtitles,
        'subtitle_maxwidth': subtitle_maxwidth,
        'subtitle_font': subtitle_font,
        'subtitle_fontsize': subtitle_fontsize,
        'subtitle_fontcolor': subtitle_fontcolor,
        'subtitle_bgcolor': subtitle_bgcolor,
        'subtitle_bgopacity': subtitle_bgopacity,
        'subtitle_position': subtitle_position,
        'subtitle_outline': subtitle_outline,
        'subtitle_outlinecolor': subtitle_outlinecolor,
        'subtitle_shadow': subtitle_shadow,
        'subtitle_format': subtitle_format,
        'punctuation_fix_enabled': punctuation_fix_enabled,
        'subtitle_secondary_color': subtitle_secondary_color,
        'subtitle_bold': subtitle_bold,
        'subtitle_italic': subtitle_italic,
        'subtitle_underline': subtitle_underline,
        'subtitle_strikeout': subtitle_strikeout,
        'subtitle_scale_x': subtitle_scale_x,
        'subtitle_scale_y': subtitle_scale_y,
        'subtitle_spacing': subtitle_spacing,
        'subtitle_angle': subtitle_angle,
        'subtitle_border_style': subtitle_border_style,
        'subtitle_shadow_distance': subtitle_shadow_distance,
        'subtitle_margin_l': subtitle_margin_l,
        'subtitle_margin_r': subtitle_margin_r,
        'subtitle_margin_v': subtitle_margin_v,
        'subtitle_encoding': subtitle_encoding,
        'effect_overlay': effect_overlay,
        'effect_opacity': effect_opacity,
        'effect_blend': effect_blend,
        'enable_effect_overlay': enable_effect_overlay,
        'batch_input_folder': batch_input_folder, # New
        'enable_depthflow': enable_depthflow,
        'depthflow_vignette_enable': depthflow_vignette_enable,
        'depthflow_dof_enable': depthflow_dof_enable,
        'depthflow_isometric_min': depthflow_isometric_min,
        'depthflow_isometric_max': depthflow_isometric_max,
        'depthflow_height_min': depthflow_height_min,
        'depthflow_height_max': depthflow_height_max,
        'depthflow_zoom_min': depthflow_zoom_min,
        'depthflow_zoom_max': depthflow_zoom_max,
        'depthflow_min_effects_per_image': depthflow_min_effects_per_image,
        'depthflow_max_effects_per_image': depthflow_max_effects_per_image,
        'depthflow_base_zoom_loops': depthflow_base_zoom_loops,
        'depthflow_workers': depthflow_workers,
        'depthflow_height': depthflow_height,
        'depthflow_offset_x': depthflow_offset_x,
        'depthflow_offset_y': depthflow_offset_y,
        'depthflow_steady': depthflow_steady,
        'depthflow_isometric': depthflow_isometric,
        'depthflow_dolly': depthflow_dolly,
        'depthflow_focus': depthflow_focus,
        'depthflow_zoom': depthflow_zoom,
        'depthflow_invert': depthflow_invert,
        'depthflow_center_x': depthflow_center_x,
        'depthflow_center_y': depthflow_center_y,
        'depthflow_origin_x': depthflow_origin_x,
        'depthflow_origin_y': depthflow_origin_y,
        'depthflow_zoom_probability': depthflow_zoom_probability,
        "logging": {
            "root": "INFO",
            "main": "INFO",
            "gui": "INFO",
            "video_processor": "INFO",
            "audio_processor": "INFO",
            "subtitle_generator": "INFO",
            "depth_processor": "INFO",
            "overlay_compositor": "INFO",
            "file_utils": "INFO",
            "config_manager": "INFO",
            "gui_config_manager": "INFO",
            "font_utils": "INFO",
            "slideshow_generator": "INFO",
            "depthflow_settings_frame": "INFO",
            "gui_utils": "INFO",
            "main_settings_frame": "INFO",
            "overlay_effects_frame": "INFO",
            "subtitle_settings_frame": "INFO",
            "title_settings_frame": "INFO",
            "punctuation_utils": "INFO",
            "subtitle_processing_utils": "INFO",
        }
    }

def update_config_menu(config_menu_widget, var_config_str, gui_elements): # Added gui_elements as argument
    global config_files
    config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]
    menu = config_menu_widget['menu']
    menu.delete(0, 'end')
    for filename in config_files:
        menu.add_command(label=filename,
                        command=lambda f=filename: var_config_str.set(f) or load_config(config_menu_widget.master, var_config_str, gui_elements))

def load_config(root_widget, var_config_str, gui_elements):
    config_file = os.path.join(config_folder, var_config_str.get())
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_file}")
        messagebox.showerror("Error", f"Config file not found: {config_file}")
        return
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from config file: {config_file}. It might be empty or corrupted.")
        messagebox.showerror("Error", f"Error decoding JSON from config file: {config_file}. It might be empty or corrupted.")
        # Optionally, try to load default config as a fallback
        default_config_path = os.path.join(config_folder, "default_config.json")
        if os.path.exists(default_config_path):
            try:
                with open(default_config_path, 'r') as f_default:
                    config = json.load(f_default)
                logger.info("Loaded default_config.json as a fallback.")
                messagebox.showinfo("Info", "Loaded default_config.json as a fallback.")
            except Exception as e:
                logger.error(f"Could not load default_config.json as fallback: {e}")
                messagebox.showerror("Error", f"Could not load default_config.json as fallback: {e}")
                return # Cannot recover, return
        else:
            return # Cannot recover, return

    # Helper to safely update entry/text widgets
    def update_entry(entry_widget, value):
        if entry_widget and hasattr(entry_widget, 'delete') and hasattr(entry_widget, 'insert'):
            entry_widget.config(state=tk.NORMAL) # Ensure it's editable
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value)
            # Re-disable if it was originally disabled (e.g., calculated font size)
            # This requires storing original state or checking its type. For now, assume normal.

    # Helper to safely update text widgets
    def update_text(text_widget, value):
        if text_widget and hasattr(text_widget, 'delete') and hasattr(text_widget, 'insert'):
            text_widget.config(state=tk.NORMAL) # Ensure it's editable
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", value)
            # Re-disable if needed

    # Helper to safely update StringVar/IntVar/DoubleVar
    def update_var(tk_var, value):
        if tk_var:
            try:
                if isinstance(tk_var, tk.DoubleVar):
                    # Attempt to convert value to float, use default if it fails
                    tk_var.set(float(value))
                elif isinstance(tk_var, tk.IntVar):
                    # Attempt to convert value to int, use default if it fails
                    tk_var.set(int(value))
                else:
                    # For StringVar and BooleanVar, direct set is usually fine
                    tk_var.set(value)
            except (ValueError, tk.TclError):
                # If conversion fails, set to a sensible default (e.g., 0.0 for DoubleVar, 0 for IntVar)
                logger.warning(f"Could not set Tkinter variable {tk_var} with value '{value}'. Setting to default.")
                if isinstance(tk_var, tk.DoubleVar):
                    tk_var.set(0.0)
                elif isinstance(tk.IntVar):
                    tk_var.set(0)
                elif isinstance(tk.BooleanVar):
                    tk_var.set(False) # Sensible default for boolean
                else:
                    tk_var.set("") # Sensible default for string

    # Update GUI elements based on loaded config
    update_var(gui_elements.get('var_debug_logging_enabled'), config.get('debug_logging_enabled', debug_logging_enabled))
    # Load logging settings into the GUI elements
    logging_config = config.get("logging", {})
    for section, logger_name in LoggingSettingsFrame.log_sections.items(): # Access log_sections from the class
        var_name = f"var_logging_{logger_name}"
        if var_name in gui_elements:
            gui_elements[var_name].set(logging_config.get(logger_name, "INFO")) # Default to INFO if not in config
        else:
            logger.warning(f"Tkinter variable {var_name} not found in gui_elements during load_settings.")

    update_entry(gui_elements.get('entry_title'), config.get('title', title))
    update_text(gui_elements.get('text_watermark'), config.get('watermark', watermark))
    update_var(gui_elements.get('var_watermark_type'), config.get('watermark_type', watermark_type))
    update_var(gui_elements.get('var_enable_watermark'), config.get('enable_watermark', enable_watermark))
    update_var(gui_elements.get('var_watermark_font_size'), config.get('watermark_font_size', watermark_font_size))
    update_var(gui_elements.get('var_watermark_opacity'), config.get('watermark_opacity', watermark_opacity))
    update_var(gui_elements.get('var_watermark_fontcolor'), config.get('watermark_fontcolor', watermark_fontcolor))
    update_var(gui_elements.get('var_watermark_speed_intuitive'), config.get('watermark_speed_intuitive', watermark_speed_intuitive))

    loaded_watermark_font = config.get('watermark_font', watermark_font)
    if gui_elements.get('var_watermark_font'):
        if loaded_watermark_font in available_fonts:
            update_var(gui_elements['var_watermark_font'], loaded_watermark_font)
        elif available_fonts:
            update_var(gui_elements['var_watermark_font'], available_fonts[0])
            logger.warning(f"Watermark font '{loaded_watermark_font}' not found. Defaulting to '{available_fonts[0]}'.")
        else:
            update_var(gui_elements['var_watermark_font'], watermark_font)
            logger.warning(f"No fonts available in fonts directory. Watermark font set to '{watermark_font}'.")

    update_entry(gui_elements.get('entry_title_font_size'), config.get('title_font_size', title_font_size))
    update_entry(gui_elements.get('entry_segment_duration'), config.get('segment_duration', segment_duration))
    update_entry(gui_elements.get('entry_input_folder'), config.get('input_folder', input_folder))
    update_entry(gui_elements.get('entry_template_folder'), config.get('template_folder', template_folder))
    update_var(gui_elements.get('var_depthflow'), config.get('depthflow', depthflow))
    update_entry(gui_elements.get('entry_time_limit'), config.get('time_limit', time_limit))
    update_var(gui_elements.get('var_transition_duration'), config.get('transition_duration', transition_duration)) # New
    update_var(gui_elements.get('var_fps'), config.get('fps', fps)) # New
    update_var(gui_elements.get('var_video_orientation'), config.get('video_orientation', video_orientation))
    update_var(gui_elements.get('var_add_blur'), config.get('blur', blur))
    update_var(gui_elements.get('var_batch_input_folder'), config.get('batch_input_folder', batch_input_folder)) # New

    update_var(gui_elements.get('var_subscribe_delay'), config.get('subscribe_delay', subscribe_delay))
    update_var(gui_elements.get('var_enable_subscribe_overlay'), config.get('enable_subscribe_overlay', enable_subscribe_overlay))
    update_var(gui_elements.get('var_subscribe_overlay_file'), config.get('subscribe_overlay_file', "None"))

    update_var(gui_elements.get('var_title_fontcolor'), config.get('title_fontcolor', title_fontcolor))
    loaded_title_font = config.get('title_font', title_font)
    if gui_elements.get('var_title_font'):
        if loaded_title_font in available_fonts:
            update_var(gui_elements['var_title_font'], loaded_title_font)
        elif available_fonts:
            update_var(gui_elements['var_title_font'], available_fonts[0])
            logger.warning(f"Title font '{loaded_title_font}' not found. Defaulting to '{available_fonts[0]}'.")
        else:
            update_var(gui_elements['var_title_font'], title_font)
            logger.warning(f"No fonts available in fonts directory. Title font set to '{title_font}'.")

    update_entry(gui_elements.get('entry_voiceover_delay'), config.get('voiceover_delay', voiceover_delay))
    update_entry(gui_elements.get('entry_title_appearance_delay'), config.get('title_appearance_delay', title_appearance_delay))
    update_entry(gui_elements.get('entry_title_visible_time'), config.get('title_visible_time', title_visible_time))
    update_entry(gui_elements.get('entry_title_x_offset'), config.get('title_x_offset', title_x_offset))
    update_entry(gui_elements.get('entry_title_y_offset'), config.get('title_y_offset', title_y_offset))
    update_var(gui_elements.get('var_enable_title'), config.get('enable_title', enable_title))
    update_var(gui_elements.get('var_title_opacity'), config.get('title_opacity', title_opacity))
    update_var(gui_elements.get('var_enable_title_background'), config.get('enable_title_background', enable_title_background))
    update_var(gui_elements.get('var_title_background_color'), config.get('title_background_color', title_background_color))
    update_var(gui_elements.get('var_title_background_opacity'), config.get('title_background_opacity', title_background_opacity))

    update_var(gui_elements.get('var_enable_title_video_overlay'), config.get('enable_title_video_overlay', enable_title_video_overlay))
    update_var(gui_elements.get('var_title_video_overlay_file'), config.get('title_video_overlay_file', title_video_overlay_file))
    update_var(gui_elements.get('var_title_video_overlay_delay'), config.get('title_video_overlay_delay', title_video_overlay_delay))
    update_var(gui_elements.get('var_title_video_chromakey_color'), config.get('title_video_chromakey_color', title_video_chromakey_color))
    update_var(gui_elements.get('var_title_video_chromakey_similarity'), config.get('title_video_chromakey_similarity', title_video_chromakey_similarity))
    update_var(gui_elements.get('var_title_video_chromakey_blend'), config.get('title_video_chromakey_blend', title_video_chromakey_blend))

    update_var(gui_elements.get('var_chromakey_color'), config.get('chromakey_color', chromakey_color))
    update_entry(gui_elements.get('entry_chromakey_similarity'), config.get('chromakey_similarity', chromakey_similarity))
    update_entry(gui_elements.get('entry_chromakey_blend'), config.get('chromakey_blend', chromakey_blend))

    update_var(gui_elements.get('var_effect_overlay'), config.get('effect_overlay', effect_overlay))
    update_var(gui_elements.get('var_effect_opacity'), config.get('effect_opacity', effect_opacity))
    update_var(gui_elements.get('var_effect_blend'), config.get('effect_blend', effect_blend))
    update_var(gui_elements.get('var_enable_effect_overlay'), config.get('enable_effect_overlay', enable_effect_overlay))
    # DepthFlow settings
    update_var(gui_elements.get('var_enable_depthflow'), config.get('enable_depthflow', enable_depthflow))
    update_var(gui_elements.get('var_depthflow_vignette_enable'), config.get('depthflow_vignette_enable', depthflow_vignette_enable))
    update_var(gui_elements.get('var_depthflow_dof_enable'), config.get('depthflow_dof_enable', depthflow_dof_enable))
    update_var(gui_elements.get('var_depthflow_isometric_min'), config.get('depthflow_isometric_min', depthflow_isometric_min))
    update_var(gui_elements.get('var_depthflow_isometric_max'), config.get('depthflow_isometric_max', depthflow_isometric_max))
    update_var(gui_elements.get('var_depthflow_height_min'), config.get('depthflow_height_min', depthflow_height_min))
    update_var(gui_elements.get('var_depthflow_height_max'), config.get('depthflow_height_max', depthflow_height_max))
    update_var(gui_elements.get('var_depthflow_zoom_min'), config.get('depthflow_zoom_min', depthflow_zoom_min))
    update_var(gui_elements.get('var_depthflow_zoom_max'), config.get('depthflow_zoom_max', depthflow_zoom_max))
    update_var(gui_elements.get('var_depthflow_min_effects_per_image'), config.get('depthflow_min_effects_per_image', depthflow_min_effects_per_image))
    update_var(gui_elements.get('var_depthflow_max_effects_per_image'), config.get('depthflow_max_effects_per_image', depthflow_max_effects_per_image))
    update_var(gui_elements.get('var_depthflow_base_zoom_loops'), config.get('depthflow_base_zoom_loops', depthflow_base_zoom_loops))
    update_var(gui_elements.get('var_depthflow_workers'), config.get('depthflow_workers', depthflow_workers))

    if gui_elements.get('update_effect_opacity_value'): # This function is in gui.py, not here
        gui_elements['update_effect_opacity_value']()

    update_var(gui_elements.get('var_enable_subtitles'), config.get('enable_subtitles', enable_subtitles))
    update_entry(gui_elements.get('entry_subtitle_max_width'), config.get('subtitle_maxwidth', subtitle_maxwidth))

    update_var(gui_elements.get('var_subtitle_font'), config.get('subtitle_font', subtitle_font))
    update_var(gui_elements.get('var_subtitle_fontsize'), config.get('subtitle_fontsize', subtitle_fontsize))
    update_var(gui_elements.get('var_subtitle_fontcolor'), config.get('subtitle_fontcolor', subtitle_fontcolor))
    update_var(gui_elements.get('var_subtitle_bgcolor'), config.get('subtitle_bgcolor', subtitle_bgcolor))
    update_var(gui_elements.get('var_subtitle_bgopacity'), config.get('subtitle_bgopacity', subtitle_bgopacity))
    update_var(gui_elements.get('var_subtitle_position'), config.get('subtitle_position', subtitle_position))
    update_var(gui_elements.get('var_subtitle_outline'), config.get('subtitle_outline', subtitle_outline))
    update_var(gui_elements.get('var_subtitle_outlinecolor'), config.get('subtitle_outlinecolor', subtitle_outlinecolor))
    update_var(gui_elements.get('var_subtitle_shadow'), config.get('subtitle_shadow', subtitle_shadow))
    update_var(gui_elements.get('var_subtitle_format'), config.get('subtitle_format', subtitle_format)) # New: Update subtitle format
    update_var(gui_elements.get('var_punctuation_fix_enabled'), config.get('punctuation_fix_enabled', punctuation_fix_enabled)) # New: Update punctuation fix enabled

    # Load new ASS subtitle style parameters
    update_var(gui_elements.get('var_subtitle_secondary_color'), config.get('subtitle_secondary_color', subtitle_secondary_color))
    update_var(gui_elements.get('var_subtitle_bold'), config.get('subtitle_bold', subtitle_bold))
    update_var(gui_elements.get('var_subtitle_italic'), config.get('subtitle_italic', subtitle_italic))
    update_var(gui_elements.get('var_subtitle_underline'), config.get('subtitle_underline', subtitle_underline))
    update_var(gui_elements.get('var_subtitle_strikeout'), config.get('subtitle_strikeout', subtitle_strikeout))
    update_var(gui_elements.get('var_subtitle_scale_x'), config.get('subtitle_scale_x', subtitle_scale_x))
    update_var(gui_elements.get('var_subtitle_scale_y'), config.get('subtitle_scale_y', subtitle_scale_y))
    update_var(gui_elements.get('var_subtitle_spacing'), config.get('subtitle_spacing', subtitle_spacing))
    update_var(gui_elements.get('var_subtitle_angle'), config.get('subtitle_angle', subtitle_angle))
    update_var(gui_elements.get('var_subtitle_border_style'), config.get('subtitle_border_style', subtitle_border_style))
    update_var(gui_elements.get('var_subtitle_shadow_distance'), config.get('subtitle_shadow_distance', subtitle_shadow_distance))
    update_var(gui_elements.get('var_subtitle_margin_l'), config.get('subtitle_margin_l', subtitle_margin_l))
    update_var(gui_elements.get('var_subtitle_margin_r'), config.get('subtitle_margin_r', subtitle_margin_r))
    update_var(gui_elements.get('var_subtitle_margin_v'), config.get('subtitle_margin_v', subtitle_margin_v))
    update_var(gui_elements.get('var_subtitle_encoding'), config.get('subtitle_encoding', subtitle_encoding))

    # Calculate font size based on title length
    title_text = config.get('title', title) # Use a different variable name to avoid conflict with global 'title'
    length = len(title_text)
    if length <= 10:
        calculated_title_font_size = 90
    elif 11 <= length <= 14:
        calculated_title_font_size = 80
    elif 15 <= length <= 18:
        calculated_title_font_size = 70
    else:
        calculated_title_font_size = 65
    if gui_elements.get('entry_calculated_title_font_size'):
        gui_elements['entry_calculated_title_font_size'].config(state=tk.NORMAL)
        gui_elements['entry_calculated_title_font_size'].delete(0, tk.END)
        gui_elements['entry_calculated_title_font_size'].insert(0, calculated_title_font_size)
        gui_elements['entry_calculated_title_font_size'].config(state=tk.DISABLED)

    # Update toggle controls
    if gui_elements.get('tab_title_settings_instance'): gui_elements['tab_title_settings_instance'].toggle_title_controls()
    if gui_elements.get('tab_overlay_effects_instance'): gui_elements['tab_overlay_effects_instance'].update_all_overlay_controls()
    if gui_elements.get('tab_subtitles_instance'): gui_elements['tab_subtitles_instance'].update_all_subtitle_controls()
    if gui_elements.get('tab_depthflow_settings_instance'): gui_elements['tab_depthflow_settings_instance'].toggle_depthflow_controls()


def _get_numeric_value(tk_var, default_value, value_type=float):
    """Safely gets a numeric value from a Tkinter variable, handling empty strings."""
    try:
        val = tk_var.get()
        if isinstance(val, str) and not val.strip():
            return default_value
        return value_type(val)
    except (tk.TclError, ValueError):
        return default_value

def save_config(gui_elements):
    config_file = os.path.join(config_folder, gui_elements['var_config'].get())
    with open(config_file, 'w') as f:
        json.dump({
            'debug_logging_enabled': gui_elements['var_debug_logging_enabled'].get(), # New
            'title': gui_elements['entry_title'].get(),
            'watermark': gui_elements['text_watermark'].get("1.0", tk.END).rstrip('\n'),
            'watermark_type': gui_elements['var_watermark_type'].get(),
            'enable_watermark': gui_elements['var_enable_watermark'].get(),
            'watermark_font_size': _get_numeric_value(gui_elements['var_watermark_font_size'], watermark_font_size, int),
            'watermark_opacity': _get_numeric_value(gui_elements['var_watermark_opacity'], watermark_opacity),
            'watermark_fontcolor': gui_elements['var_watermark_fontcolor'].get(),
            'watermark_speed_intuitive': _get_numeric_value(gui_elements['var_watermark_speed_intuitive'], watermark_speed_intuitive, int),
            'transition_duration': _get_numeric_value(gui_elements['var_transition_duration'], transition_duration), # New
            'fps': _get_numeric_value(gui_elements['var_fps'], fps, int), # New
            'title_font_size': _get_numeric_value(gui_elements['entry_title_font_size'], title_font_size, int),
            'segment_duration': _get_numeric_value(gui_elements['entry_segment_duration'], segment_duration, int),
            'input_folder': gui_elements['entry_input_folder'].get(),
            'template_folder': gui_elements['entry_template_folder'].get(),
            'depthflow': gui_elements['var_depthflow'].get(),
            'time_limit': _get_numeric_value(gui_elements['entry_time_limit'], time_limit, int),
            'video_orientation': gui_elements['var_video_orientation'].get(),
            'blur': gui_elements['var_add_blur'].get(),
            'watermark_font': gui_elements['var_watermark_font'].get(),
            'subscribe_delay': _get_numeric_value(gui_elements['var_subscribe_delay'], subscribe_delay, int),
            'title_fontcolor': gui_elements['var_title_fontcolor'].get(),
            'title_font': gui_elements['var_title_font'].get(),
            'voiceover_delay': _get_numeric_value(gui_elements['entry_voiceover_delay'], voiceover_delay, int),
            'title_appearance_delay': _get_numeric_value(gui_elements['entry_title_appearance_delay'], title_appearance_delay, int),
            'title_visible_time': _get_numeric_value(gui_elements['entry_title_visible_time'], title_visible_time, int),
            'title_x_offset': _get_numeric_value(gui_elements['entry_title_x_offset'], title_x_offset, int),
            'title_y_offset': _get_numeric_value(gui_elements['entry_title_y_offset'], title_y_offset, int),
            'enable_title': gui_elements['var_enable_title'].get(),
            'title_opacity': _get_numeric_value(gui_elements['var_title_opacity'], title_opacity),
            'enable_title_background': gui_elements['var_enable_title_background'].get(),
            'title_background_color': gui_elements['var_title_background_color'].get(),
            'title_background_opacity': _get_numeric_value(gui_elements['var_title_background_opacity'], title_background_opacity),
            'enable_subscribe_overlay': gui_elements['var_enable_subscribe_overlay'].get(),
            'subscribe_overlay_file': gui_elements['var_subscribe_overlay_file'].get(),
            'title_video_overlay_file': gui_elements['var_title_video_overlay_file'].get(),
            'enable_title_video_overlay': gui_elements['var_enable_title_video_overlay'].get(),
            'title_video_overlay_delay': _get_numeric_value(gui_elements['var_title_video_overlay_delay'], title_video_overlay_delay, int),
            'title_video_chromakey_color': gui_elements['var_title_video_chromakey_color'].get(),
            'title_video_chromakey_similarity': _get_numeric_value(gui_elements['var_title_video_chromakey_similarity'], title_video_chromakey_similarity),
            'title_video_chromakey_blend': _get_numeric_value(gui_elements['var_title_video_chromakey_blend'], title_video_chromakey_blend),
            'chromakey_color': gui_elements['var_chromakey_color'].get(),
            'chromakey_similarity': _get_numeric_value(gui_elements['entry_chromakey_similarity'], chromakey_similarity),
            'chromakey_blend': _get_numeric_value(gui_elements['entry_chromakey_blend'], chromakey_blend),
            'enable_subtitles': gui_elements['var_enable_subtitles'].get(), # Renamed from generate_srt
            'subtitle_maxwidth': _get_numeric_value(gui_elements['entry_subtitle_max_width'], subtitle_maxwidth, int),
            'subtitle_font': gui_elements['var_subtitle_font'].get(),
            'subtitle_fontsize': _get_numeric_value(gui_elements['var_subtitle_fontsize'], subtitle_fontsize, int),
            'subtitle_fontcolor': gui_elements['var_subtitle_fontcolor'].get(),
            'subtitle_bgcolor': gui_elements['var_subtitle_bgcolor'].get(),
            'subtitle_bgopacity': _get_numeric_value(gui_elements['var_subtitle_bgopacity'], subtitle_bgopacity),
            'subtitle_position': _get_numeric_value(gui_elements['var_subtitle_position'], subtitle_position, int),
            'subtitle_outline': _get_numeric_value(gui_elements['var_subtitle_outline'], subtitle_outline),
            'subtitle_outlinecolor': gui_elements['var_subtitle_outlinecolor'].get(),
            'subtitle_shadow': gui_elements['var_subtitle_shadow'].get(),
            'subtitle_format': gui_elements['var_subtitle_format'].get(),
            'punctuation_fix_enabled': gui_elements['var_punctuation_fix_enabled'].get(), # New: Punctuation fix enabled
            'subtitle_secondary_color': gui_elements['var_subtitle_secondary_color'].get(),
            'subtitle_bold': _get_numeric_value(gui_elements['var_subtitle_bold'], subtitle_bold, int),
            'subtitle_italic': _get_numeric_value(gui_elements['var_subtitle_italic'], subtitle_italic, int),
            'subtitle_underline': _get_numeric_value(gui_elements['var_subtitle_underline'], subtitle_underline, int),
            'subtitle_strikeout': _get_numeric_value(gui_elements['var_subtitle_strikeout'], subtitle_strikeout, int),
            'subtitle_scale_x': _get_numeric_value(gui_elements['var_subtitle_scale_x'], subtitle_scale_x, int),
            'subtitle_scale_y': _get_numeric_value(gui_elements['var_subtitle_scale_y'], subtitle_scale_y, int),
            'subtitle_spacing': _get_numeric_value(gui_elements['var_subtitle_spacing'], subtitle_spacing),
            'subtitle_angle': _get_numeric_value(gui_elements['var_subtitle_angle'], subtitle_angle, int),
            'subtitle_border_style': _get_numeric_value(gui_elements['var_subtitle_border_style'], subtitle_border_style, int),
            'subtitle_shadow_distance': _get_numeric_value(gui_elements['var_subtitle_shadow_distance'], subtitle_shadow_distance),
            'subtitle_margin_l': _get_numeric_value(gui_elements['var_subtitle_margin_l'], subtitle_margin_l, int),
            'subtitle_margin_r': _get_numeric_value(gui_elements['var_subtitle_margin_r'], subtitle_margin_r, int),
            'subtitle_margin_v': _get_numeric_value(gui_elements['var_subtitle_margin_v'], subtitle_margin_v, int),
            'subtitle_encoding': _get_numeric_value(gui_elements['var_subtitle_encoding'], subtitle_encoding, int),
            'effect_overlay': gui_elements['var_effect_overlay'].get(),
            'effect_opacity': _get_numeric_value(gui_elements['var_effect_opacity'], effect_opacity),
            'effect_blend': gui_elements['var_effect_blend'].get(),
            'enable_effect_overlay': gui_elements['var_enable_effect_overlay'].get(),
            # DepthFlow settings
            'enable_depthflow': gui_elements['var_depthflow'].get(),
            'depthflow_vignette_enable': gui_elements['var_depthflow_vignette_enable'].get(),
            'depthflow_dof_enable': gui_elements['var_depthflow_dof_enable'].get(),
            'depthflow_isometric_min': _get_numeric_value(gui_elements['var_depthflow_isometric_min'], depthflow_isometric_min),
            'depthflow_isometric_max': _get_numeric_value(gui_elements['var_depthflow_isometric_max'], depthflow_isometric_max),
            'depthflow_height_min': _get_numeric_value(gui_elements['var_depthflow_height_min'], depthflow_height_min),
            'depthflow_height_max': _get_numeric_value(gui_elements['var_depthflow_height_max'], depthflow_height_max),
            'depthflow_zoom_min': _get_numeric_value(gui_elements['var_depthflow_zoom_min'], depthflow_zoom_min),
            'depthflow_zoom_max': _get_numeric_value(gui_elements['var_depthflow_zoom_max'], depthflow_zoom_max),
            'depthflow_min_effects_per_image': _get_numeric_value(gui_elements['var_depthflow_min_effects_per_image'], depthflow_min_effects_per_image, int),
            'depthflow_max_effects_per_image': _get_numeric_value(gui_elements['var_depthflow_max_effects_per_image'], depthflow_max_effects_per_image, int),
            'depthflow_base_zoom_loops': gui_elements['var_depthflow_base_zoom_loops'].get(),
            'depthflow_workers': _get_numeric_value(gui_elements['var_depthflow_workers'], depthflow_workers, int),
            'depthflow_zoom_probability': _get_numeric_value(gui_elements['var_depthflow_zoom_probability'], depthflow_zoom_probability),
            'batch_input_folder': gui_elements['var_batch_input_folder'].get(), # New
            # Logging settings
            "logging": {
                logger_name: gui_elements[f"var_logging_{logger_name}"].get()
                for logger_name in LoggingSettingsFrame.log_sections.values()
            }
        }, f, indent=4)
    messagebox.showinfo("Success", "Config saved successfully!")

def save_new_config(gui_elements):
    new_filename = gui_elements['entry_new_filename'].get()
    if not new_filename.endswith('.json'):
        new_filename += '.json'
    config_file = os.path.join(config_folder, new_filename)

    if os.path.exists(config_file):
        response = messagebox.askyesnocancel(
            "Config Exists",
            f"A config file named '{new_filename}' already exists.\n\n"
            "Do you want to:\n"
            "  - Yes: Overwrite it\n"
            "  - No: Save with a new name (e.g., add a number)\n"
            "  - Cancel: Abort saving"
        )

        if response is True:  # Yes, overwrite
            pass  # Continue to save
        elif response is False:  # No, save with new name
            base_name, ext = os.path.splitext(new_filename)
            i = 1
            while os.path.exists(os.path.join(config_folder, f"{base_name}_{i}{ext}")):
                i += 1
            new_filename = f"{base_name}_{i}{ext}"
            config_file = os.path.join(config_folder, new_filename)
            messagebox.showinfo("New Name", f"Saving as '{new_filename}'")
        else:  # Cancel
            messagebox.showinfo("Save Aborted", "Config save operation cancelled.")
            return

    with open(config_file, 'w') as f:
        json.dump({
            'debug_logging_enabled': gui_elements['var_debug_logging_enabled'].get(), # New
            'title': gui_elements['entry_title'].get(),
            'watermark': gui_elements['text_watermark'].get("1.0", tk.END).rstrip('\n'),
            'watermark_type': gui_elements['var_watermark_type'].get(),
            'enable_watermark': gui_elements['var_enable_watermark'].get(),
            'watermark_font_size': _get_numeric_value(gui_elements['var_watermark_font_size'], watermark_font_size, int),
            'watermark_opacity': _get_numeric_value(gui_elements['var_watermark_opacity'], watermark_opacity),
            'watermark_fontcolor': gui_elements['var_watermark_fontcolor'].get(),
            'watermark_speed_intuitive': _get_numeric_value(gui_elements['var_watermark_speed_intuitive'], watermark_speed_intuitive, int),
            'transition_duration': _get_numeric_value(gui_elements['var_transition_duration'], transition_duration),
            'fps': _get_numeric_value(gui_elements['var_fps'], fps, int),
            'title_font_size': _get_numeric_value(gui_elements['entry_title_font_size'], title_font_size, int),
            'segment_duration': _get_numeric_value(gui_elements['entry_segment_duration'], segment_duration, int),
            'input_folder': gui_elements['entry_input_folder'].get(),
            'template_folder': gui_elements['entry_template_folder'].get(),
            'depthflow': gui_elements['var_depthflow'].get(),
            'time_limit': _get_numeric_value(gui_elements['entry_time_limit'], time_limit, int),
            'video_orientation': gui_elements['var_video_orientation'].get(),
            'blur': gui_elements['var_add_blur'].get(),
            'watermark_font': gui_elements['var_watermark_font'].get(),
            'subscribe_delay': _get_numeric_value(gui_elements['var_subscribe_delay'], subscribe_delay, int),
            'title_fontcolor': gui_elements['var_title_fontcolor'].get(),
            'title_font': gui_elements['var_title_font'].get(),
            'voiceover_delay': _get_numeric_value(gui_elements['entry_voiceover_delay'], voiceover_delay, int),
            'title_appearance_delay': _get_numeric_value(gui_elements['entry_title_appearance_delay'], title_appearance_delay, int),
            'title_visible_time': _get_numeric_value(gui_elements['entry_title_visible_time'], title_visible_time, int),
            'title_x_offset': _get_numeric_value(gui_elements['entry_title_x_offset'], title_x_offset, int),
            'title_y_offset': _get_numeric_value(gui_elements['entry_title_y_offset'], title_y_offset, int),
            'enable_title': gui_elements['var_enable_title'].get(),
            'title_opacity': _get_numeric_value(gui_elements['var_title_opacity'], title_opacity),
            'enable_title_background': gui_elements['var_enable_title_background'].get(),
            'title_background_color': gui_elements['var_title_background_color'].get(),
            'title_background_opacity': _get_numeric_value(gui_elements['var_title_background_opacity'], title_background_opacity),
            'enable_subscribe_overlay': gui_elements['var_enable_subscribe_overlay'].get(),
            'subscribe_overlay_file': gui_elements['var_subscribe_overlay_file'].get(),
            'title_video_overlay_file': gui_elements['var_title_video_overlay_file'].get(),
            'enable_title_video_overlay': gui_elements['var_enable_title_video_overlay'].get(),
            'title_video_overlay_delay': _get_numeric_value(gui_elements['var_title_video_overlay_delay'], title_video_overlay_delay, int),
            'title_video_chromakey_color': gui_elements['var_title_video_chromakey_color'].get(),
            'title_video_chromakey_similarity': _get_numeric_value(gui_elements['var_title_video_chromakey_similarity'], title_video_chromakey_similarity),
            'title_video_chromakey_blend': _get_numeric_value(gui_elements['var_title_video_chromakey_blend'], title_video_chromakey_blend),
            'chromakey_color': gui_elements['var_chromakey_color'].get(),
            'chromakey_similarity': _get_numeric_value(gui_elements['entry_chromakey_similarity'], chromakey_similarity),
            'chromakey_blend': _get_numeric_value(gui_elements['entry_chromakey_blend'], chromakey_blend),
            'enable_subtitles': gui_elements['var_enable_subtitles'].get(), # Renamed from generate_srt
            'subtitle_maxwidth': _get_numeric_value(gui_elements['entry_subtitle_max_width'], subtitle_maxwidth, int),
            'subtitle_font': gui_elements['var_subtitle_font'].get(),
            'subtitle_fontsize': _get_numeric_value(gui_elements['var_subtitle_fontsize'], subtitle_fontsize, int),
            'subtitle_fontcolor': gui_elements['var_subtitle_fontcolor'].get(),
            'subtitle_bgcolor': gui_elements['var_subtitle_bgcolor'].get(),
            'subtitle_bgopacity': _get_numeric_value(gui_elements['var_subtitle_bgopacity'], subtitle_bgopacity),
            'subtitle_position': _get_numeric_value(gui_elements['var_subtitle_position'], subtitle_position, int),
            'subtitle_outline': _get_numeric_value(gui_elements['var_subtitle_outline'], subtitle_outline),
            'subtitle_outlinecolor': gui_elements['var_subtitle_outlinecolor'].get(),
            'subtitle_shadow': gui_elements['var_subtitle_shadow'].get(),
            'subtitle_format': gui_elements['var_subtitle_format'].get(),
            'punctuation_fix_enabled': gui_elements['var_punctuation_fix_enabled'].get(), # New: Punctuation fix enabled
            'subtitle_secondary_color': gui_elements['var_subtitle_secondary_color'].get(),
            'subtitle_bold': _get_numeric_value(gui_elements['var_subtitle_bold'], subtitle_bold, int),
            'subtitle_italic': _get_numeric_value(gui_elements['var_subtitle_italic'], subtitle_italic, int),
            'subtitle_underline': _get_numeric_value(gui_elements['var_subtitle_underline'], subtitle_underline, int),
            'subtitle_strikeout': _get_numeric_value(gui_elements['var_subtitle_strikeout'], subtitle_strikeout, int),
            'subtitle_scale_x': _get_numeric_value(gui_elements['var_subtitle_scale_x'], subtitle_scale_x, int),
            'subtitle_scale_y': _get_numeric_value(gui_elements['var_subtitle_scale_y'], subtitle_scale_y, int),
            'subtitle_spacing': _get_numeric_value(gui_elements['var_subtitle_spacing'], subtitle_spacing),
            'subtitle_angle': _get_numeric_value(gui_elements['var_subtitle_angle'], subtitle_angle, int),
            'subtitle_border_style': _get_numeric_value(gui_elements['var_subtitle_border_style'], subtitle_border_style, int),
            'subtitle_shadow_distance': _get_numeric_value(gui_elements['var_subtitle_shadow_distance'], subtitle_shadow_distance),
            'subtitle_margin_l': _get_numeric_value(gui_elements['var_subtitle_margin_l'], subtitle_margin_l, int),
            'subtitle_margin_r': _get_numeric_value(gui_elements['var_subtitle_margin_r'], subtitle_margin_r, int),
            'subtitle_margin_v': _get_numeric_value(gui_elements['var_subtitle_margin_v'], subtitle_margin_v, int),
            'subtitle_encoding': _get_numeric_value(gui_elements['var_subtitle_encoding'], subtitle_encoding, int),
            'effect_overlay': gui_elements['var_effect_overlay'].get(),
            'effect_opacity': _get_numeric_value(gui_elements['var_effect_opacity'], effect_opacity),
            'effect_blend': gui_elements['var_effect_blend'].get(),
            'enable_effect_overlay': gui_elements['var_enable_effect_overlay'].get(),
            # DepthFlow settings
            'enable_depthflow': gui_elements['var_depthflow'].get(),
            'depthflow_vignette_enable': gui_elements['var_depthflow_vignette_enable'].get(),
            'depthflow_dof_enable': gui_elements['var_depthflow_dof_enable'].get(),
            'depthflow_isometric_min': _get_numeric_value(gui_elements['var_depthflow_isometric_min'], depthflow_isometric_min),
            'depthflow_isometric_max': _get_numeric_value(gui_elements['var_depthflow_isometric_max'], depthflow_isometric_max),
            'depthflow_height_min': _get_numeric_value(gui_elements['var_depthflow_height_min'], depthflow_height_min),
            'depthflow_height_max': _get_numeric_value(gui_elements['var_depthflow_height_max'], depthflow_height_max),
            'depthflow_zoom_min': _get_numeric_value(gui_elements['var_depthflow_zoom_min'], depthflow_zoom_min),
            'depthflow_zoom_max': _get_numeric_value(gui_elements['var_depthflow_zoom_max'], depthflow_zoom_max),
            'depthflow_min_effects_per_image': _get_numeric_value(gui_elements['var_depthflow_min_effects_per_image'], depthflow_min_effects_per_image, int),
            'depthflow_max_effects_per_image': _get_numeric_value(gui_elements['var_depthflow_max_effects_per_image'], depthflow_max_effects_per_image, int),
            'depthflow_base_zoom_loops': gui_elements['var_depthflow_base_zoom_loops'].get(),
            'depthflow_workers': _get_numeric_value(gui_elements['var_depthflow_workers'], depthflow_workers, int),
            'batch_input_folder': gui_elements['var_batch_input_folder'].get(), # New
            # Logging settings
            "logging": {
                logger_name: gui_elements[f"var_logging_{logger_name}"].get()
                for logger_name in LoggingSettingsFrame.log_sections.values()
            }
        }, f, indent=4)
    logger.info(f"New config saved to: {config_file}")
    messagebox.showinfo("Success", f"New config saved as '{new_filename}'!")

    global config_files
    config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]
    gui_elements['var_config'].set(new_filename)
    update_config_menu(gui_elements['config_menu'], gui_elements['var_config'], gui_elements)
    load_config(gui_elements['root'], gui_elements['var_config'], gui_elements)

def delete_config(gui_elements):
    config_file = os.path.join(config_folder, gui_elements['var_config'].get())
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this config?"):
        os.remove(config_file)
        logger.info("Config deleted successfully!")
        messagebox.showinfo("Success", "Config deleted successfully!")
        global config_files
        config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]
        if config_files:
            gui_elements['var_config'].set(config_files[0])
        else:
            gui_elements['var_config'].set("")
            logger.warning("No configuration files found in the config directory.")
            messagebox.showwarning("Warning", "No configuration files found in the config directory.")
        update_config_menu(gui_elements['config_menu'], gui_elements['var_config'], gui_elements)
        load_config(gui_elements['root'], gui_elements['var_config'], gui_elements)
