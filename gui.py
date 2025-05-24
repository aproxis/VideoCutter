import tkinter as tk
from tkinter import messagebox, ttk, filedialog
# import subprocess # No longer calling cutter.py directly
# Instead, import the new pipeline orchestrator
from videocutter.main import run_pipeline_for_project, run_batch_pipeline # Updated import
import os
import json
import glob
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io

# Default values remain the same
default_segment_duration = 6
default_time_limit = 600

default_input_folder = 'INPUT'
default_template_folder = 'TEMPLATE'

default_title = 'Model Name'
default_title_font = 'Montserrat-Semi-Bold.otf'  # Default font
default_title_font_size = 90
default_title_fontcolor = 'random'  # Default font color
default_title_appearance_delay = 1  # Default delay before title appears
default_title_visible_time = 5  # Default time title remains visible
default_title_x_offset = 110  # Default X offset for title positioning
default_title_y_offset = -35  # Default Y offset for title positioning
default_enable_title = True # New default for enabling title
default_title_opacity = 1.0 # New default for title opacity (1.0 = fully opaque)
default_enable_title_background = False # New default for enabling title background
default_title_background_color = '000000' # New default for title background color (black)
default_title_background_opacity = 0.5 # New default for title background opacity

default_subscribe_delay = 21 # Default delay for subscribe overlay (renamed from default_delay)
default_enable_subscribe_overlay = True # New default for enabling subscribe overlay

default_title_video_overlay_file = 'None' # New default for title video overlay file
default_enable_title_video_overlay = False # New default for enabling title video overlay
default_title_video_overlay_delay = 0 # New default for title video overlay appearance delay
default_title_video_chromakey_color = '65db41' # New default for title video chromakey color
default_title_video_chromakey_similarity = 0.18 # New default for title video chromakey similarity
default_title_video_chromakey_blend = 0 # New default for title video chromakey blend

default_voiceover_delay = 5

default_watermark = 'Today is a\n Plus Day'
default_watermark_type = 'random'
default_watermark_speed = 50 # Old default, will be derived from intuitive speed
default_watermark_font = 'Nexa Bold.otf'  # Default font
default_enable_watermark = True # New default for watermark
default_watermark_font_size = 40 # New default
default_watermark_opacity = 0.7 # New default
default_watermark_fontcolor = 'random' # New default
default_watermark_speed_intuitive = 5 # New default (1-10 scale)

default_chromakey_color = '65db41'
default_chromakey_similarity = 0.18
default_chromakey_blend = 0

default_depthflow = 0
default_generate_srt = False  # Default value for .srt generation
default_subtitle_maxwidth = 21 

# Define watermark types
watermark_types = ['ccw', 'random']

# Define font color options
font_colors = ['random', 'FF00B4', 'ff6600', '0b4178', 'FFFFFF', '000000', '00FF00', '0000FF', 'FFFF00']

# Define supported blend modes for effects
SUPPORTED_BLEND_MODES = [
    'normal',     # Default, no special blending
    'overlay',    # Combines multiply and screen blend modes
    # 'screen',     # Lightens the base color
    # 'multiply',   # Darkens the base color
    # 'addition',   # Adds pixel values
    # 'difference', # Subtracts pixel values
    # 'dodge',      # Brightens base color based on blend color
    # 'burn',       # Darkens base color based on blend color
    # 'softlight',  # Subtle light/dark effect
    # 'hardlight',  # Dramatic contrast effect
    # 'divide',     # Divides pixel values
    # 'subtract',   # Subtracts pixel values
]

# Get available fonts from the fonts directory
fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
available_fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
if not available_fonts:
    available_fonts = ['Nexa Bold.otf']  # Fallback if no fonts found

# Define overlay directories
overlays_dir = os.path.join(os.path.dirname(__file__), 'effects', 'overlays')
subscribe_dir = os.path.join(os.path.dirname(__file__), 'effects', 'subscribe')
title_dir = os.path.join(os.path.dirname(__file__), 'effects', 'title')

# Function to toggle background color and opacity controls based on shadow checkbox
def toggle_shadow_controls(*args):
    if var_subtitle_shadow.get():
        bg_color_entry.config(state=tk.NORMAL)
        bg_opacity_slider.config(state=tk.NORMAL)
        bg_opacity_value_entry.config(state=tk.NORMAL)
    else:
        bg_color_entry.config(state=tk.DISABLED)
        bg_opacity_slider.config(state=tk.DISABLED)
        bg_opacity_value_entry.config(state=tk.DISABLED)
    schedule_subtitle_preview_update() # Use debounced update

# Function to toggle title controls based on enable_title checkbox
def toggle_title_controls(*args):
    state = tk.NORMAL if var_enable_title.get() else tk.DISABLED
    entry_title.config(state=state)
    entry_title_font.config(state=state)
    entry_title_fontcolor.config(state=state)
    entry_calculated_title_font_size.config(state=state)
    entry_title_font_size.config(state=state)
    entry_title_appearance_delay.config(state=state)
    entry_title_visible_time.config(state=state)
    entry_title_x_offset.config(state=state)
    entry_title_y_offset.config(state=state)
    title_opacity_slider.config(state=state)
    title_opacity_value_entry.config(state=state)
    title_background_checkbox.config(state=state)
    title_background_color_entry.config(state=state)
    title_background_opacity_slider.config(state=state)
    title_background_opacity_value_entry.config(state=state)
    enable_title_video_overlay_checkbox.config(state=state) # New: Enable/disable the checkbox itself
    entry_title_video_overlay_file.config(state=state)
    entry_title_video_overlay_delay.config(state=state)
    entry_title_video_chromakey_color.config(state=state)
    entry_title_video_chromakey_similarity.config(state=state)
    entry_title_video_chromakey_blend.config(state=state)

    # For ttk.Combobox, 'state' is the correct attribute. For tk.Entry, 'state'.
    # For tk.Text, 'state' is also correct.
    # For OptionMenu, it's a bit trickier, need to configure the menu button.
    entry_title_font['state'] = state
    entry_title_fontcolor['state'] = state
    entry_title_video_overlay_file['state'] = state # New

# Function to toggle subscribe overlay controls based on enable_subscribe_overlay checkbox
def toggle_subscribe_overlay_controls(*args):
    state = tk.NORMAL if var_enable_subscribe_overlay.get() else tk.DISABLED
    enable_subscribe_overlay_checkbox.config(state=state) # Ensure the checkbox itself is enabled/disabled
    entry_subscribe_overlay_file.config(state=state)
    entry_subscribe_delay.config(state=state)
    entry_chromakey_color.config(state=state)
    entry_chromakey_similarity.config(state=state)
    entry_chromakey_blend.config(state=state)
    entry_subscribe_overlay_file['state'] = state # Combobox

# Function to toggle watermark controls based on enable_watermark checkbox
def toggle_watermark_controls(*args):
    state = tk.NORMAL if var_enable_watermark.get() else tk.DISABLED
    text_watermark.config(state=state) # tk.Text
    entry_font.config(state=state) # tk.OptionMenu
    entry_watermark_font_size.config(state=state) # tk.Entry
    watermark_opacity_slider.config(state=state) # ttk.Scale
    entry_watermark_fontcolor.config(state=state) # tk.OptionMenu
    entry_watermark_type.config(state=state) # tk.OptionMenu
    watermark_speed_slider.config(state=state) # ttk.Scale

    # Explicitly set state for OptionMenu widgets
    entry_font['state'] = state
    entry_watermark_fontcolor['state'] = state
    entry_watermark_type['state'] = state
    text_watermark.config(state=state) # New: Ensure text widget is also updated
    entry_watermark_font_size.config(state=state) # New: Ensure entry widget is also updated
    watermark_opacity_slider.config(state=state) # New: Ensure scale widget is also updated
    watermark_speed_slider.config(state=state) # New: Ensure scale widget is also updated

# Function to toggle effect overlay controls based on enable_effect_overlay checkbox
def toggle_effect_overlay_controls(*args):
    state = tk.NORMAL if var_enable_effect_overlay.get() else tk.DISABLED
    effect_dropdown.config(state=state)
    blend_dropdown.config(state=state)
    effect_opacity_slider.config(state=state)
    effect_opacity_value.config(state=state)

# Create the main window
root = tk.Tk()
root.title("Video Cutter GUI")
# Set window size to use more screen space
root.geometry("1160x850") # Adjusted size

# Create StringVar for config selection
var_config = tk.StringVar(root)
var_watermark_type = tk.StringVar(root)
var_watermark_type.set(default_watermark_type)  # Set default value
var_watermark_font = tk.StringVar(root)
var_watermark_font.set(default_watermark_font)  # Set default font
var_enable_watermark = tk.BooleanVar() # New BooleanVar for watermark
var_enable_watermark.set(default_enable_watermark) # Set default value
var_watermark_font_size = tk.IntVar(root, value=default_watermark_font_size) # New IntVar
var_watermark_opacity = tk.DoubleVar(root, value=default_watermark_opacity) # New DoubleVar
var_watermark_fontcolor = tk.StringVar(root, value=default_watermark_fontcolor) # New StringVar
var_watermark_speed_intuitive = tk.IntVar(root, value=default_watermark_speed_intuitive) # New IntVar
var_title_fontcolor = tk.StringVar(root)
var_title_fontcolor.set(default_title_fontcolor)  # Set default font color
var_title_font = tk.StringVar(root)
var_title_font.set(default_title_font)  # Set default title font
var_enable_title = tk.BooleanVar() # New BooleanVar for enabling title
var_enable_title.set(default_enable_title) # Set default value
var_title_opacity = tk.DoubleVar(root, value=default_title_opacity) # New DoubleVar for title opacity
var_enable_title_background = tk.BooleanVar() # New BooleanVar for enabling title background
var_enable_title_background.set(default_enable_title_background) # Set default value
var_title_background_color = tk.StringVar(root, value=default_title_background_color) # New StringVar for title background color
var_title_background_opacity = tk.DoubleVar(root, value=default_title_background_opacity) # New DoubleVar for title background opacity

# New variables for subscribe overlay
var_enable_subscribe_overlay = tk.BooleanVar()
var_enable_subscribe_overlay.set(default_enable_subscribe_overlay)
var_subscribe_delay = tk.IntVar(root, value=default_subscribe_delay) # Renamed from var_delay

# New variables for title video overlay
var_enable_title_video_overlay = tk.BooleanVar()
var_enable_title_video_overlay.set(default_enable_title_video_overlay)
var_title_video_overlay_file = tk.StringVar(root, value=default_title_video_overlay_file)
var_title_video_overlay_delay = tk.IntVar(root, value=default_title_video_overlay_delay)
var_title_video_chromakey_color = tk.StringVar(root, value=default_title_video_chromakey_color)
var_title_video_chromakey_similarity = tk.DoubleVar(root, value=default_title_video_chromakey_similarity)
var_title_video_chromakey_blend = tk.DoubleVar(root, value=default_title_video_chromakey_blend)

# New variable for subscribe overlay file
var_subscribe_overlay_file = tk.StringVar(root, value="None")

# New variable for enabling effect overlay
var_enable_effect_overlay = tk.BooleanVar(root, value=True)


# Create StringVar for chromakey color (this is now for subscribe overlay)
var_chromakey_color = tk.StringVar(root)
var_chromakey_color.set(default_chromakey_color)  # Set default chromakey color

# Create BooleanVar for .srt generation
var_generate_srt = tk.BooleanVar()
var_generate_srt.set(default_generate_srt)  # Default to not generating .srt

# Get config files from folder
config_folder = os.path.join(os.path.dirname(__file__), 'config')
config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]

# Variable for batch input folder
var_batch_input_folder = tk.StringVar(root)

def browse_batch_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        var_batch_input_folder.set(folder_selected)
        entry_input_folder.config(state=tk.DISABLED) # Disable single input if batch is chosen
        entry_input_folder.delete(0, tk.END)
        entry_input_folder.insert(0, "BATCH MODE ACTIVE")
    else: # User cancelled or selected nothing
        if not var_batch_input_folder.get(): # If it was already empty
            entry_input_folder.config(state=tk.NORMAL)
            entry_input_folder.delete(0, tk.END)
            entry_input_folder.insert(0, default_input_folder)


def clear_batch_folder():
    var_batch_input_folder.set("")
    entry_input_folder.config(state=tk.NORMAL)
    entry_input_folder.delete(0, tk.END)
    entry_input_folder.insert(0, default_input_folder)


def start_process():
    # Get values from the entry fields
    title = entry_title.get()
    watermark = text_watermark.get("1.0", tk.END).rstrip('\n') # Removed .strip(), use rstrip to remove only trailing newline
    watermark_type = var_watermark_type.get()
    enable_watermark = var_enable_watermark.get() # Get new watermark enable status
    watermark_font_size = var_watermark_font_size.get() # Get new watermark font size
    watermark_opacity = var_watermark_opacity.get() # Get new watermark opacity
    watermark_fontcolor = var_watermark_fontcolor.get() # Get new watermark font color
    watermark_speed_intuitive = var_watermark_speed_intuitive.get() # Get new intuitive speed

    # Convert intuitive speed (1-10) to FFmpeg frames (e.g., 100 to 19)
    # 1 (slowest) -> 100 frames, 10 (fastest) -> 19 frames
    watermark_speed = int(100 - (watermark_speed_intuitive - 1) * 9)

    manual_font_size = entry_title_font_size.get()
    segment_duration = entry_segment_duration.get()
    input_folder = entry_input_folder.get()
    template_folder = entry_template_folder.get()
    depthflow_tf = var_depthflow.get()
    time_limit = entry_time_limit.get()
    video_orientation = var_video_orientation.get()
    blur_checkbox = var_add_blur.get()
    
    # Get subscribe overlay parameters
    subscribe_delay = var_subscribe_delay.get()
    enable_subscribe_overlay = var_enable_subscribe_overlay.get()
    chromakey_color = var_chromakey_color.get()
    chromakey_similarity = entry_chromakey_similarity.get()
    chromakey_blend = entry_chromakey_blend.get()

    title_fontcolor = var_title_fontcolor.get()
    title_font = var_title_font.get()
    voiceover_delay = entry_voiceover_delay.get()
    title_appearance_delay = entry_title_appearance_delay.get()
    title_visible_time = entry_title_visible_time.get()
    title_x_offset = entry_title_x_offset.get()
    title_y_offset = entry_title_y_offset.get()
    
    # Get new title parameters
    enable_title = var_enable_title.get()
    title_opacity = var_title_opacity.get()
    enable_title_background = var_enable_title_background.get() # New
    title_background_color = var_title_background_color.get() # New
    title_background_opacity = var_title_background_opacity.get() # New

    # Get title video overlay parameters
    enable_title_video_overlay = var_enable_title_video_overlay.get()
    title_video_overlay_file = var_title_video_overlay_file.get()
    title_video_overlay_delay = var_title_video_overlay_delay.get()
    title_video_chromakey_color = var_title_video_chromakey_color.get()
    title_video_chromakey_similarity = var_title_video_chromakey_similarity.get()
    title_video_chromakey_blend = var_title_video_chromakey_blend.get()
    
    # Get effect overlay parameters
    effect_overlay = var_effect_overlay.get()
    effect_opacity = var_effect_opacity.get()
    effect_blend = var_effect_blend.get()
    enable_effect_overlay = var_enable_effect_overlay.get() # New
    
    # Get .srt generation parameter
    generate_srt = var_generate_srt.get()
    subtitle_max_width = entry_subtitle_max_width.get()
    
    # Get subtitle styling parameters
    subtitle_font = var_subtitle_font.get()
    subtitle_fontsize = var_subtitle_fontsize.get()
    subtitle_fontcolor = var_subtitle_fontcolor.get()
    subtitle_bgcolor = var_subtitle_bgcolor.get()
    subtitle_bgopacity = var_subtitle_bgopacity.get()
    subtitle_position = var_subtitle_position.get()
    subtitle_outline = var_subtitle_outline.get()
    subtitle_outlinecolor = var_subtitle_outlinecolor.get()

    if depthflow_tf:
        depthflow = '1'
    else:
        depthflow = '0'
    
    if blur_checkbox:
        blur = '1'
    else:
        blur = '0'
    
    # Replace newlines with the appropriate escaped character
    # The .rstrip('\n') above handles the trailing newline from tk.Text
    watermark = watermark.replace('\n', '\\n')

    # Determine font size to use
    if manual_font_size != "":
        title_font_size = int(manual_font_size)  # Use manual input if provided
    else:
        title_font_size = int(entry_calculated_title_font_size.get())  # Use calculated font size if manual is empty

    # Get selected font
    watermark_font = var_watermark_font.get()
    
    # Construct the command with the arguments
    command = [
        'python3', 'cutter.py',
        '--sd', str(segment_duration),
        '--tl', str(time_limit),

        '--i', input_folder,
        '--tpl', template_folder,

        '--t', title,
        '--tfs', str(title_font_size),
        '--tfc', title_fontcolor,
        '--tf', title_font,
        '--tad', str(title_appearance_delay),
        '--tvt', str(title_visible_time),
        '--osd', str(subscribe_delay), # Use subscribe_delay
        '--vd', str(voiceover_delay),
        '--txo', str(title_x_offset),
        '--tyo', str(title_y_offset),

        '--w', watermark,
        '--wt', watermark_type,
        '--ws', watermark_speed,
        '--wf', watermark_font,

        '--z', str(depthflow),
        '--o', video_orientation,
        '--b', str(blur),
        
        '--chr', chromakey_color,
        '--cs', str(chromakey_similarity),
        '--cb', str(chromakey_blend),
        
        '--srt', '1' if generate_srt else '0',
        '--smaxw', str(subtitle_max_width),
    ]
    
    # Add effect overlay parameters if an effect is selected
    if effect_overlay != "None":
        command.extend([
            '--effect', effect_overlay,
            '--effect-opacity', str(effect_opacity),
            '--effect-blend', effect_blend
        ])
    
    # Add subtitle styling parameters only if SRT generation is enabled
    if generate_srt:
        subtitle_params = [
            '--sf', subtitle_font,
            '--sfs', str(subtitle_fontsize),
            '--sfc', subtitle_fontcolor,
            '--spos', str(subtitle_position),
            '--sout', str(subtitle_outline),
            '--soutc', subtitle_outlinecolor,
            '--shadow', '1' if var_subtitle_shadow.get() else '0'
        ]
        
        # Always add shadow color and opacity parameters, they'll only be used if shadow is enabled
        subtitle_params.extend([
            '--sbc', subtitle_bgcolor,
            '--sbo', str(subtitle_bgopacity)
        ])
        
        command.extend(subtitle_params)

    # print(command) # Old command list
    # subprocess.run(command) # Old way of running

    # --- New way: Prepare settings dictionary and call run_pipeline ---
    gui_settings = {
        'title': title, # Also used for title_overlay.text by config_manager
        'watermark': watermark.replace('\\n', '\n'), # config_manager will handle internal newlines if needed
        'watermark_type': watermark_type,
        'watermark_speed': watermark_speed, # Converted to FFmpeg frames
        'enable_watermark': enable_watermark, # Add new watermark enable status
        'watermark_font_size': watermark_font_size, # Add new watermark font size
        'watermark_opacity': watermark_opacity, # Add new watermark opacity
        'watermark_fontcolor': watermark_fontcolor, # Add new watermark font color
        'watermark_speed_intuitive': watermark_speed_intuitive, # Add new intuitive speed
        'title_font_size': str(title_font_size), # Pass as string, config_manager converts
        'segment_duration': segment_duration, # config_manager will convert to int
        'input_folder': input_folder,
        'template_folder': template_folder,
        'depthflow': depthflow_tf, # Boolean
        'time_limit': time_limit, # config_manager will convert to int
        'video_orientation': video_orientation,
        'blur': blur_checkbox, # Boolean, for image processing (original blur arg)
        'watermark_font': watermark_font, # Filename, resolver in config_manager or font_utils
        
        # Title Overlay specific (some overlap with general title, config_manager can reconcile)
        'title_fontcolor': title_fontcolor,
        'title_font': title_font, # Filename
        'title_appearance_delay': title_appearance_delay,
        'title_visible_time': title_visible_time,
        'title_x_offset': title_x_offset,
        'title_y_offset': title_y_offset,
        'enable_title': enable_title, # Add new title enable status
        'title_opacity': title_opacity, # Add new title opacity
        'enable_title_background': enable_title_background, # New
        'title_background_color': title_background_color, # New
        'title_background_opacity': title_background_opacity, # New

        # Subscribe Overlay specific
        'enable_subscribe_overlay': enable_subscribe_overlay,
        'subscribe_delay': subscribe_delay,
        'chromakey_color': chromakey_color,
        'chromakey_similarity': chromakey_similarity,
        'chromakey_blend': chromakey_blend,

        # Title Video Overlay specific
        'enable_title_video_overlay': enable_title_video_overlay,
        'title_video_overlay_file': title_video_overlay_file,
        'title_video_overlay_delay': title_video_overlay_delay,
        'title_video_chromakey_color': title_video_chromakey_color,
        'title_video_chromakey_similarity': title_video_chromakey_similarity,
        'title_video_chromakey_blend': title_video_chromakey_blend,

        # Audio specific
        'vo_delay': voiceover_delay, # For audio_processor

        # Effects Overlay
        'effect_overlay': effect_overlay if effect_overlay != "None" else None,
        'effect_opacity': effect_opacity,
        'effect_blend': effect_blend,
        'enable_effect_overlay': enable_effect_overlay, # New

        # Subtitles
        'generate_srt': generate_srt, # Boolean for enabling subtitles end-to-end
        'subtitle_max_width': subtitle_max_width, # For srt_generator
        'subtitle_font': subtitle_font, # For overlay_compositor (ASS styling)
        'subtitle_fontsize': subtitle_fontsize,
        'subtitle_fontcolor': subtitle_fontcolor,
        'subtitle_bgcolor': subtitle_bgcolor, # For shadow color
        'subtitle_bgopacity': subtitle_bgopacity, # For shadow opacity
        'subtitle_position': subtitle_position,
        'subtitle_outline': subtitle_outline,
        'subtitle_outlinecolor': subtitle_outlinecolor,
        'subtitle_shadow': var_subtitle_shadow.get() # Boolean
    }

    selected_config_file = var_config.get()
    config_file_path = None
    if selected_config_file:
        config_file_path = os.path.join(config_folder, selected_config_file)
        if not os.path.exists(config_file_path):
            messagebox.showerror("Error", f"Selected config file not found: {config_file_path}")
            return
            
    try:
        print("Starting VideoCutter pipeline via main.run_pipeline...")
        print(f"Using config file: {config_file_path}")
        print(f"GUI settings to merge/override: {json.dumps(gui_settings, indent=2)}")
        
        # Call the new main pipeline function
        # This will run in the same process, so GUI might freeze.
        # For a non-freezing GUI, this should be run in a separate thread.
        # TODO: Implement threading for run_pipeline to keep GUI responsive.
        
        batch_folder_path = var_batch_input_folder.get()
        if batch_folder_path and os.path.isdir(batch_folder_path):
            print(f"Starting BATCH processing for folder: {batch_folder_path}")
            # In batch mode, gui_settings act as global overrides.
            # config_file_path is the global config. Project-specific configs are handled by main.py.
            run_batch_pipeline(
                batch_root_folder=batch_folder_path,
                global_config_path=config_file_path, # This is the selected JSON from GUI
                gui_settings=gui_settings # These are overrides from GUI fields
            )
        elif input_folder and input_folder != "BATCH MODE ACTIVE":
             print(f"Starting SINGLE project processing for folder: {input_folder}")
             # For a single run, the input_folder from GUI is the project itself.
             # The config_manager will use input_folder to look for _project_config.json if we want that,
             # or we can assume for single run, the selected JSON is the primary one.
             
             # The run_pipeline_for_project expects a fully resolved cfg.
             # So, load_config needs to be called first.
             cfg_single_project = videocutter.config_manager.load_config(
                 global_config_path=config_file_path, # Selected JSON from GUI
                 project_folder_path=input_folder, # The single input folder can also have a _project_config.json
                 runtime_settings=gui_settings
             )
             if cfg_single_project.title == 'Default Model Name' or cfg_single_project.title == '':
                 cfg_single_project.title = os.path.basename(input_folder) if os.path.basename(input_folder) else "SingleProject"

             run_pipeline_for_project(
                 project_name=cfg_single_project.title, # Use resolved title or folder name
                 project_input_folder=input_folder, # This is the direct input folder
                 cfg=cfg_single_project
             )
        else:
            messagebox.showerror("Error", "Please specify a valid Input Folder or Batch Input Folder.")
            return
        
        messagebox.showinfo("Success", "Video processing pipeline finished!")
    except Exception as e:
        messagebox.showerror("Pipeline Error", f"An error occurred: {e}")
        print(f"Pipeline execution error: {e}")
    

def update_font_size(event):
    title = entry_title.get()
    length = len(title)
    if length <= 10:
        calculated_title_font_size = 90
    elif 11 <= length <= 14:
        calculated_title_font_size = 80
    elif 15 <= length <= 18:
        calculated_title_font_size = 70
    else:
        calculated_title_font_size = 65
    entry_calculated_title_font_size.config(state=tk.NORMAL)
    entry_calculated_title_font_size.delete(0, tk.END)
    entry_calculated_title_font_size.insert(0, calculated_title_font_size)
    entry_calculated_title_font_size.config(state=tk.DISABLED)

# Debounce mechanism for preview updates
_after_id = None
def schedule_subtitle_preview_update():
    global _after_id
    if _after_id:
        root.after_cancel(_after_id)
    _after_id = root.after(200, update_subtitle_preview) # 200ms delay

def create_default_config():
    default_config = {
        'title': default_title,
        'watermark': default_watermark,
        'watermark_type': default_watermark_type,
        'watermark_speed': default_watermark_speed,
        'title_font_size': default_title_font_size,
        'segment_duration': default_segment_duration,
        'input_folder': default_input_folder,
        'template_folder': default_template_folder,
        'depthflow': default_depthflow,
        'time_limit': default_time_limit,
        'video_orientation': 'vertical',
        'blur': 0,
        'watermark_font': default_watermark_font,
        'enable_watermark': default_enable_watermark, # Add to default config
        'watermark_font_size': default_watermark_font_size, # Add to default config
        'watermark_opacity': default_watermark_opacity, # Add to default config
        'watermark_fontcolor': default_watermark_fontcolor, # Add to default config
        'watermark_speed_intuitive': default_watermark_speed_intuitive, # Add to default config
        'subscribe_delay': default_subscribe_delay, # Renamed from delay
        'title_fontcolor': default_title_fontcolor,
        'title_font': default_title_font,
        'voiceover_delay': default_voiceover_delay,
        'title_appearance_delay': default_title_appearance_delay,
        'title_visible_time': default_title_visible_time,
        'title_x_offset': default_title_x_offset,
        'title_y_offset': default_title_y_offset,
        'enable_title': default_enable_title, # Add to default config
        'title_opacity': default_title_opacity, # Add to default config
        'enable_title_background': default_enable_title_background, # New
        'title_background_color': default_title_background_color, # New
        'title_background_opacity': default_title_background_opacity, # New
        'enable_subscribe_overlay': default_enable_subscribe_overlay, # New
        'title_video_overlay_file': default_title_video_overlay_file, # New
        'enable_title_video_overlay': default_enable_title_video_overlay, # New
        'title_video_overlay_delay': default_title_video_overlay_delay, # New
        'title_video_chromakey_color': default_title_video_chromakey_color, # New
        'title_video_chromakey_similarity': default_title_video_chromakey_similarity, # New
        'title_video_chromakey_blend': default_title_video_chromakey_blend, # New
        'chromakey_color': default_chromakey_color,
        'chromakey_similarity': default_chromakey_similarity,
        'chromakey_blend': default_chromakey_blend,
        'generate_srt': default_generate_srt,
        'subtitle_maxwidth': default_subtitle_maxwidth,
        # Subtitle styling parameters
        'subtitle_font': default_subtitle_font,
        'subtitle_fontsize': default_subtitle_fontsize,
        'subtitle_fontcolor': default_subtitle_fontcolor,
        'subtitle_bgcolor': default_subtitle_bgcolor,
        'subtitle_bgopacity': default_subtitle_bgopacity,
        'subtitle_position': default_subtitle_position,
        'subtitle_outline': default_subtitle_outline,
        'subtitle_outlinecolor': default_subtitle_outlinecolor,
        'subtitle_shadow': default_subtitle_shadow,
        # Effect overlay parameters
        'effect_overlay': 'None',
        'effect_opacity': 0.2,
        'effect_blend': 'overlay'
    }
    default_filename = "default_config.json"
    config_file = os.path.join(config_folder, default_filename)
    with open(config_file, 'w') as f:
        json.dump(default_config, f)
    messagebox.showinfo("Info", f"Default config created: {default_filename}")
    return default_filename

# Check for config files
if config_files:
    var_config.set(config_files[0])
else:
    var_config.set("")
    messagebox.showwarning("Warning", "No configuration files found in the config directory.")
    default_config_file = create_default_config()
    config_files.append(default_config_file)

def update_config_menu():
    menu = config_menu['menu']
    menu.delete(0, 'end')
    for filename in config_files:
        menu.add_command(label=filename, 
                        command=lambda f=filename: var_config.set(f) or load_config())

def load_config():
    config_file = os.path.join(config_folder, var_config.get())
    with open(config_file, 'r') as f:
        config = json.load(f)
    entry_title.delete(0, tk.END)
    entry_title.insert(0, config['title'])
    text_watermark.delete("1.0", tk.END)
    text_watermark.insert("1.0", config['watermark'])
    entry_title_font_size.delete(0, tk.END)
    entry_title_font_size.insert(0, config['title_font_size'])
    entry_segment_duration.delete(0, tk.END)
    entry_segment_duration.insert(0, config['segment_duration'])
    entry_input_folder.delete(0, tk.END)
    entry_input_folder.insert(0, config['input_folder'])
    entry_template_folder.delete(0, tk.END)
    entry_template_folder.insert(0, config['template_folder'])
    var_depthflow.set(config['depthflow'])
    entry_time_limit.delete(0, tk.END)
    entry_time_limit.insert(0, config['time_limit'])
    var_video_orientation.set(config['video_orientation'])
    var_add_blur.set(config['blur'])
    var_watermark_type.set(config.get('watermark_type', default_watermark_type))
    # entry_watermark_speed.delete(0, tk.END) # Old entry, no longer needed
    # entry_watermark_speed.insert(0, config.get('watermark_speed', default_watermark_speed)) # Old entry
    var_enable_watermark.set(config.get('enable_watermark', default_enable_watermark)) # Load new setting
    var_watermark_font_size.set(config.get('watermark_font_size', default_watermark_font_size)) # Load new setting
    var_watermark_opacity.set(config.get('watermark_opacity', default_watermark_opacity)) # Load new setting
    var_watermark_fontcolor.set(config.get('watermark_fontcolor', default_watermark_fontcolor)) # Load new setting
    var_watermark_speed_intuitive.set(config.get('watermark_speed_intuitive', default_watermark_speed_intuitive)) # Load new setting
    
    # Set watermark font if it exists in config, otherwise use default
    loaded_watermark_font = config.get('watermark_font', default_watermark_font)
    if loaded_watermark_font in available_fonts:
        var_watermark_font.set(loaded_watermark_font)
    elif available_fonts: # If configured font not found, use first available
        var_watermark_font.set(available_fonts[0])
        print(f"Warning: Watermark font '{loaded_watermark_font}' not found. Defaulting to '{available_fonts[0]}'.")
    else: # No fonts available at all
        var_watermark_font.set(default_watermark_font) # Fallback to a hardcoded default name
        print(f"Warning: No fonts available in fonts directory. Watermark font set to '{default_watermark_font}'.")
    
    # Load subscribe.py parameters
    # entry_delay.delete(0, tk.END)
    # entry_delay.insert(0, config.get('delay', default_delay))
    
    # Load voiceover delay
    entry_voiceover_delay.delete(0, tk.END)
    entry_voiceover_delay.insert(0, config.get('voiceover_delay', default_voiceover_delay))
    
    # Load title offset parameters
    entry_title_x_offset.delete(0, tk.END)
    entry_title_x_offset.insert(0, config.get('title_x_offset', default_title_x_offset))
    
    entry_title_y_offset.delete(0, tk.END)
    entry_title_y_offset.insert(0, config.get('title_y_offset', default_title_y_offset))
    
    # Load new title parameters
    var_enable_title.set(config.get('enable_title', default_enable_title))
    var_title_opacity.set(config.get('title_opacity', default_title_opacity))
    var_enable_title_background.set(config.get('enable_title_background', default_enable_title_background)) # New
    var_title_background_color.set(config.get('title_background_color', default_title_background_color)) # New
    var_title_background_opacity.set(config.get('title_background_opacity', default_title_background_opacity)) # New
    
    # Load new subscribe overlay parameters
    var_enable_subscribe_overlay.set(config.get('enable_subscribe_overlay', default_enable_subscribe_overlay))
    var_subscribe_delay.set(config.get('subscribe_delay', default_subscribe_delay))
    var_subscribe_overlay_file.set(config.get('subscribe_overlay_file', "None")) # Load subscribe overlay file

    # Load new title video overlay parameters
    var_enable_title_video_overlay.set(config.get('enable_title_video_overlay', default_enable_title_video_overlay))
    var_title_video_overlay_file.set(config.get('title_video_overlay_file', default_title_video_overlay_file))
    var_title_video_overlay_delay.set(config.get('title_video_overlay_delay', default_title_video_overlay_delay))
    var_title_video_chromakey_color.set(config.get('title_video_chromakey_color', default_title_video_chromakey_color))
    var_title_video_chromakey_similarity.set(config.get('title_video_chromakey_similarity', default_title_video_chromakey_similarity))
    var_title_video_chromakey_blend = tk.DoubleVar(root, value=default_title_video_chromakey_blend)

    # Load chromakey parameters (now for subscribe overlay)
    var_chromakey_color.set(config.get('chromakey_color', default_chromakey_color))
    
    entry_chromakey_similarity.delete(0, tk.END)
    entry_chromakey_similarity.insert(0, config.get('chromakey_similarity', default_chromakey_similarity))
    
    entry_chromakey_blend.delete(0, tk.END)
    entry_chromakey_blend.insert(0, config.get('chromakey_blend', default_chromakey_blend))
    
    # Load effect overlay parameters
    var_effect_overlay.set(config.get('effect_overlay', 'None'))
    var_effect_opacity.set(config.get('effect_opacity', 0.2))
    var_effect_blend.set(config.get('effect_blend', 'overlay'))
    var_enable_effect_overlay.set(config.get('enable_effect_overlay', True)) # New
    update_effect_opacity_value()
    
    # Load .srt generation setting
    var_generate_srt.set(config.get('generate_srt', default_generate_srt))
    
    # Load subtitle max width
    entry_subtitle_max_width.delete(0, tk.END)
    entry_subtitle_max_width.insert(0, config.get('subtitle_maxwidth', default_subtitle_maxwidth))
    
    # Load subtitle styling parameters
    var_subtitle_font.set(config.get('subtitle_font', default_subtitle_font))
    var_subtitle_fontsize.set(config.get('subtitle_fontsize', default_subtitle_fontsize))
    var_subtitle_fontcolor.set(config.get('subtitle_fontcolor', default_subtitle_fontcolor))
    var_subtitle_bgcolor.set(config.get('subtitle_bgcolor', default_subtitle_bgcolor))
    var_subtitle_bgopacity.set(config.get('subtitle_bgopacity', default_subtitle_bgopacity))
    var_subtitle_position.set(config.get('subtitle_position', default_subtitle_position))
    var_subtitle_outline.set(config.get('subtitle_outline', default_subtitle_outline))
    var_subtitle_outlinecolor.set(config.get('subtitle_outlinecolor', default_subtitle_outlinecolor))
    var_subtitle_shadow.set(config.get('subtitle_shadow', default_subtitle_shadow))
    
    # Update slider value entries
    update_slider_value(var_subtitle_fontsize, font_size_value_entry)
    update_slider_value(var_subtitle_bgopacity, bg_opacity_value_entry)
    update_slider_value(var_subtitle_outline, outline_value_entry)
    
    
    # Update subtitle preview
    schedule_subtitle_preview_update() # Use debounced update
    
    # Load title appearance parameters
    entry_title_appearance_delay.delete(0, tk.END)
    entry_title_appearance_delay.insert(0, config.get('title_appearance_delay', default_title_appearance_delay))
    
    entry_title_visible_time.delete(0, tk.END)
    entry_title_visible_time.insert(0, config.get('title_visible_time', default_title_visible_time))
    
    if 'title_fontcolor' in config:
        var_title_fontcolor.set(config['title_fontcolor'])
    else:
        var_title_fontcolor.set(default_title_fontcolor)
    
    if 'title_font' in config and config['title_font'] in available_fonts:
        var_title_font.set(config['title_font'])
    else:
        var_title_font.set(available_fonts[0] if available_fonts else default_title_font)
    
    # Load template folder
    entry_template_folder.delete(0, tk.END)
    entry_template_folder.insert(0, config.get('template_folder', 'TEMPLATE'))

    # Calculate font size based on title length
    title = config['title']
    length = len(title)
    if length <= 10:
        calculated_title_font_size = 90
    elif 11 <= length <= 14:
        calculated_title_font_size = 80
    elif 15 <= length <= 18:
        calculated_title_font_size = 70
    else:
        calculated_title_font_size = 65
    entry_calculated_title_font_size.config(state=tk.NORMAL)
    entry_calculated_title_font_size.delete(0, tk.END)
    entry_calculated_title_font_size.insert(0, calculated_title_font_size)
    entry_calculated_title_font_size.config(state=tk.DISABLED)
    

def save_config():
    config_file = os.path.join(config_folder, var_config.get())
    with open(config_file, 'w') as f:
        json.dump({
            'title': entry_title.get(),
            'watermark': text_watermark.get("1.0", tk.END).rstrip('\n'), # Removed .strip(), use rstrip
            'watermark_type': var_watermark_type.get(),
            # 'watermark_speed': entry_watermark_speed.get(), # Old entry, no longer needed
            'enable_watermark': var_enable_watermark.get(), # Save new setting
            'watermark_font_size': var_watermark_font_size.get(), # Save new setting
            'watermark_opacity': var_watermark_opacity.get(), # Save new setting
            'watermark_fontcolor': var_watermark_fontcolor.get(), # Save new setting
            'watermark_speed_intuitive': var_watermark_speed_intuitive.get(), # Save new setting
            'title_font_size': entry_title_font_size.get(),
            'segment_duration': entry_segment_duration.get(),
            'input_folder': entry_input_folder.get(),
            'template_folder': entry_template_folder.get(),
            'depthflow': var_depthflow.get(),
            'time_limit': entry_time_limit.get(),
            'video_orientation': var_video_orientation.get(),
            'blur': var_add_blur.get(),
            'watermark_font': var_watermark_font.get(),
            'subscribe_delay': var_subscribe_delay.get(), # Renamed from delay
            'title_fontcolor': var_title_fontcolor.get(),
            'title_font': var_title_font.get(),
            'voiceover_delay': entry_voiceover_delay.get(),
            'title_appearance_delay': entry_title_appearance_delay.get(),
            'title_visible_time': entry_title_visible_time.get(),
            'title_x_offset': entry_title_x_offset.get(),
            'title_y_offset': entry_title_y_offset.get(),
            'enable_title': var_enable_title.get(), # Save new setting
            'title_opacity': var_title_opacity.get(), # Save new setting
            'enable_title_background': var_enable_title_background.get(), # New
            'title_background_color': var_title_background_color.get(), # New
            'title_background_opacity': var_title_background_opacity.get(), # New
            'enable_subscribe_overlay': var_enable_subscribe_overlay.get(), # New
            'subscribe_overlay_file': var_subscribe_overlay_file.get(), # New: Save subscribe overlay file
            'title_video_overlay_file': var_title_video_overlay_file.get(), # New
            'enable_title_video_overlay': var_enable_title_video_overlay.get(), # New
            'title_video_overlay_delay': var_title_video_overlay_delay.get(), # New
            'title_video_chromakey_color': var_title_video_chromakey_color.get(), # New
            'title_video_chromakey_similarity': var_title_video_chromakey_similarity.get(), # New
            'title_video_chromakey_blend': var_title_video_chromakey_blend.get(), # New
            'chromakey_color': var_chromakey_color.get(),
            'chromakey_similarity': entry_chromakey_similarity.get(),
            'chromakey_blend': entry_chromakey_blend.get(),
            'generate_srt': var_generate_srt.get(),
            'subtitle_maxwidth': entry_subtitle_max_width.get(),
            # Subtitle styling parameters
            'subtitle_font': var_subtitle_font.get(),
            'subtitle_fontsize': var_subtitle_fontsize.get(),
            'subtitle_fontcolor': var_subtitle_fontcolor.get(),
            'subtitle_bgcolor': var_subtitle_bgcolor.get(),
            'subtitle_bgopacity': var_subtitle_bgopacity.get(),
            'subtitle_position': var_subtitle_position.get(),
            'subtitle_outline': var_subtitle_outline.get(),
            'subtitle_outlinecolor': var_subtitle_outlinecolor.get(),
            'subtitle_shadow': var_subtitle_shadow.get(),
            # Effect overlay parameters
            'effect_overlay': var_effect_overlay.get(),
            'effect_opacity': var_effect_opacity.get(),
            'effect_blend': var_effect_blend.get(),
            'enable_effect_overlay': var_enable_effect_overlay.get() # New
        }, f)
    messagebox.showinfo("Success", "Config saved successfully!")

def save_new_config():
    new_filename = entry_new_filename.get()
    if not new_filename.endswith('.json'):
        new_filename += '.json'
    config_file = os.path.join(config_folder, new_filename)
    if os.path.exists(config_file):
        messagebox.showerror("Error", "File already exists. Please choose a different name.")
        return
    with open(config_file, 'w') as f:
        json.dump({
            'title': entry_title.get(),
            'watermark': text_watermark.get("1.0", tk.END).rstrip('\n'), # Removed .strip(), use rstrip
            'watermark_type': var_watermark_type.get(),
            # 'watermark_speed': entry_watermark_speed.get(), # Old entry, no longer needed
            'watermark_font_size': var_watermark_font_size.get(), # Save new setting
            'watermark_opacity': var_watermark_opacity.get(), # Save new setting
            'watermark_fontcolor': var_watermark_fontcolor.get(), # Save new setting
            'watermark_speed_intuitive': var_watermark_speed_intuitive.get(), # Save new setting
            'title_font_size': entry_title_font_size.get(),
            'segment_duration': entry_segment_duration.get(),
            'input_folder': entry_input_folder.get(),
            'template_folder': entry_template_folder.get(),
            'depthflow': var_depthflow.get(),
            'time_limit': entry_time_limit.get(),
            'video_orientation': var_video_orientation.get(),
            'blur': var_add_blur.get(),
            'watermark_font': var_watermark_font.get(),
            'subscribe_delay': var_subscribe_delay.get(), # Renamed from delay
            'title_fontcolor': var_title_fontcolor.get(),
            'title_font': var_title_font.get(),
            'voiceover_delay': entry_voiceover_delay.get(),
            'title_appearance_delay': entry_title_appearance_delay.get(),
            'title_visible_time': entry_title_visible_time.get(),
            'title_x_offset': entry_title_x_offset.get(),
            'title_y_offset': entry_title_y_offset.get(),
            'enable_title': var_enable_title.get(), # Save new setting
            'title_opacity': var_title_opacity.get(), # Save new setting
            'enable_title_background': var_enable_title_background.get(), # New
            'title_background_color': var_title_background_color.get(), # New
            'title_background_opacity': var_title_background_opacity.get(), # New
            'enable_subscribe_overlay': var_enable_subscribe_overlay.get(), # New
            'subscribe_overlay_file': var_subscribe_overlay_file.get(), # New: Save subscribe overlay file
            'title_video_overlay_file': var_title_video_overlay_file.get(), # New
            'enable_title_video_overlay': var_enable_title_video_overlay.get(), # New
            'title_video_overlay_delay': var_title_video_overlay_delay.get(), # New
            'title_video_chromakey_color': var_title_video_chromakey_color.get(), # New
            'title_video_chromakey_similarity': var_title_video_chromakey_similarity.get(), # New
            'title_video_chromakey_blend': var_title_video_chromakey_blend.get(), # New
            'chromakey_color': var_chromakey_color.get(),
            'chromakey_similarity': entry_chromakey_similarity.get(),
            'chromakey_blend': entry_chromakey_blend.get(),
            'generate_srt': var_generate_srt.get(),
            'subtitle_maxwidth': entry_subtitle_max_width.get(),
            # Subtitle styling parameters
            'subtitle_font': var_subtitle_font.get(),
            'subtitle_fontsize': var_subtitle_fontsize.get(),
            'subtitle_fontcolor': var_subtitle_fontcolor.get(),
            'subtitle_bgcolor': var_subtitle_bgcolor.get(),
            'subtitle_bgopacity': var_subtitle_bgopacity.get(),
            'subtitle_position': var_subtitle_position.get(),
            'subtitle_outline': var_subtitle_outline.get(),
            'subtitle_outlinecolor': var_subtitle_outlinecolor.get(),
            'subtitle_shadow': var_subtitle_shadow.get(),
            # Effect overlay parameters
            'effect_overlay': var_effect_overlay.get(),
            'effect_opacity': var_effect_opacity.get(),
            'effect_blend': var_effect_blend.get(),
            'enable_effect_overlay': var_enable_effect_overlay.get() # New
        }, f)
    messagebox.showinfo("Success", "New config saved successfully!")
    
    global config_files
    config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]
    var_config.set(new_filename)
    update_config_menu()
    load_config()

def delete_config():
    config_file = os.path.join(config_folder, var_config.get())
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this config?"):
        os.remove(config_file)
        messagebox.showinfo("Success", "Config deleted successfully!")
        global config_files
        config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]
        if config_files:
            var_config.set(config_files[0])
        else:
            var_config.set("")
            messagebox.showwarning("Warning", "No configuration files found in the config directory.")
        update_config_menu()
        load_config()

# Create a frame for the config section
top_controls_frame = tk.Frame(root)
top_controls_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

config_frame = tk.LabelFrame(top_controls_frame, text="Configuration Management")
config_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)


tk.Label(config_frame, text="Config File:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
config_menu = tk.OptionMenu(config_frame, var_config, *config_files, command=lambda _: load_config())
config_menu.config(width=20)
config_menu.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

update_config_menu() # Populate menu

tk.Label(config_frame, text="Save as New:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
entry_new_filename = tk.Entry(config_frame, width=22)
entry_new_filename.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

buttons_subframe_config = tk.Frame(config_frame)
buttons_subframe_config.grid(row=0, column=2, rowspan=2, padx=5, pady=2, sticky="ns")

save_new_button = tk.Button(buttons_subframe_config, text="Save New", command=save_new_config, fg="blue")
save_new_button.pack(fill=tk.X, pady=1)
save_button = tk.Button(buttons_subframe_config, text="Save Current", command=save_config, fg="green")
save_button.pack(fill=tk.X, pady=1)
delete_button = tk.Button(buttons_subframe_config, text="Delete Current", command=delete_config, fg="red")
delete_button.pack(fill=tk.X, pady=1)


# Batch processing frame
batch_frame = tk.LabelFrame(top_controls_frame, text="Batch Processing")
batch_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

tk.Label(batch_frame, text="Batch Input Folder:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
entry_batch_folder = tk.Entry(batch_frame, textvariable=var_batch_input_folder, width=30)
entry_batch_folder.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
browse_batch_button = tk.Button(batch_frame, text="Browse", command=browse_batch_folder)
browse_batch_button.grid(row=0, column=2, padx=5, pady=2)
clear_batch_button = tk.Button(batch_frame, text="Clear Batch", command=clear_batch_folder)
clear_batch_button.grid(row=1, column=2, padx=5, pady=2)


# Create a notebook for tabbed interface
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, columnspan=2, sticky="nsew") # columnspan was 2
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1) # Ensure notebook column expands

# Create tabs
tab_main_settings = ttk.Frame(notebook)
tab_subtitles_new = ttk.Frame(notebook) 
tab_overlay_effects = ttk.Frame(notebook) # Renamed tab

# Add tabs to notebook
notebook.add(tab_main_settings, text="Main Settings")
notebook.add(tab_subtitles_new, text="Subtitles")
notebook.add(tab_overlay_effects, text="Overlay Effects") # Renamed tab

# Main layout - create a frame for the left and right columns in the MAIN SETTINGS tab
main_settings_content_frame = tk.Frame(tab_main_settings)
main_settings_content_frame.pack(fill="both", expand=True)

# Frame to hold the two columns within the main_settings_content_frame
main_settings_columns_frame = tk.Frame(main_settings_content_frame)
main_settings_columns_frame.pack(fill="both", expand=True)

# Left column frame (parent is now main_settings_columns_frame)
left_column = tk.Frame(main_settings_columns_frame)
left_column.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# Right column frame (parent is now main_settings_columns_frame)
right_column = tk.Frame(main_settings_columns_frame)
right_column.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

# Configure the columns to expand
main_settings_columns_frame.grid_columnconfigure(0, weight=1)
main_settings_columns_frame.grid_columnconfigure(1, weight=1)

# Default subtitle settings
default_subtitle_font = available_fonts[0] if available_fonts else "Arial"
default_subtitle_fontsize = 24
default_subtitle_fontcolor = "FFFFFF"
default_subtitle_bgcolor = "000000"
default_subtitle_bgopacity = 0.5
default_subtitle_position = 2
default_subtitle_outline = 1
default_subtitle_outlinecolor = "000000"
default_subtitle_shadow = True

# Create variables for subtitle settings
var_subtitle_font = tk.StringVar(root)
var_subtitle_font.set(default_subtitle_font)
var_subtitle_fontsize = tk.IntVar(root, value=default_subtitle_fontsize)
var_subtitle_fontcolor = tk.StringVar(root, value=default_subtitle_fontcolor)
var_subtitle_bgcolor = tk.StringVar(root, value=default_subtitle_bgcolor)
var_subtitle_bgopacity = tk.DoubleVar(root, value=default_subtitle_bgopacity)
var_subtitle_position = tk.IntVar(root, value=default_subtitle_position)
var_subtitle_outline = tk.DoubleVar(root, value=default_subtitle_outline)
var_subtitle_outlinecolor = tk.StringVar(root, value=default_subtitle_outlinecolor)
var_subtitle_shadow = tk.BooleanVar(root, value=default_subtitle_shadow)


# Function to update slider value entry
def update_slider_value(var, entry):
    entry.delete(0, tk.END)
    # Format to 2 decimal places for float values
    if isinstance(var.get(), float):
        entry.insert(0, f"{var.get():.2f}")
    else:
        entry.insert(0, str(var.get()))

# Function to update slider from entry
def update_slider_from_entry(entry, var, slider, min_val, max_val):
    try:
        value = float(entry.get())
        if min_val <= value <= max_val:
            var.set(value)
            schedule_subtitle_preview_update() # Use debounced update
    except ValueError:
        pass  # Ignore invalid input

# Create a global variable for the preview label
preview_label = None
preview_frame = None # Initialize preview_frame globally

# Function to update subtitle preview
def update_subtitle_preview(*args):
    global preview_label
    try:
        # Create a blank image
        img = Image.new('RGB', (400, 100), color=(100, 100, 100))
        draw = ImageDraw.Draw(img)
        
        # Try to load the selected font
        try:
            font_path = os.path.join(fonts_dir, var_subtitle_font.get())
            font = ImageFont.truetype(font_path, var_subtitle_fontsize.get())
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw sample text
        sample_text = "Sample Subtitle Text"
        # PIL.ImageDraw.textsize is deprecated since Pillow 9.2.0, use textbbox or textlength instead
        try:
            # For newer Pillow versions
            left, top, right, bottom = draw.textbbox((0, 0), sample_text, font=font)
            text_width = right - left
            text_height = bottom - top
        except AttributeError:
            # Fallback for older Pillow versions
            try:
                text_width, text_height = draw.textsize(sample_text, font=font)
            except:
                # Last resort fallback
                text_width, text_height = 200, 20
                
        position = (200 - text_width // 2, 50 - text_height // 2)
        
        # Create a base image with alpha channel for layering
        base_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
        base_draw = ImageDraw.Draw(base_img)
        
        # Draw the main text first (this will be the base layer)
        base_draw.text(position, sample_text, font=font, fill=f"#{var_subtitle_fontcolor.get()}")
        
        # If outline is enabled, create an outline layer
        outline_img = None
        if var_subtitle_outline.get() > 0:
            outline_thickness = var_subtitle_outline.get()
            outline_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            outline_draw = ImageDraw.Draw(outline_img)
            
            # Draw outline by drawing text multiple times with offset
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:  # Skip the center position
                        outline_draw.text(
                            (position[0] + dx * outline_thickness, position[1] + dy * outline_thickness),
                            sample_text,
                            font=font,
                            fill=f"#{var_subtitle_outlinecolor.get()}"
                        )
            
            # Composite outline under the text
            base_img = Image.alpha_composite(outline_img, base_img)
        
        # If shadow is enabled, create a shadow layer
        if var_subtitle_shadow.get():
            # Define shadow_offset here to ensure it's always defined when shadow is enabled
            shadow_offset = 2 

            # Calculate shadow color with opacity
            shadow_color = var_subtitle_bgcolor.get()
            r = int(shadow_color[0:2], 16)
            g = int(shadow_color[2:4], 16)
            b = int(shadow_color[4:6], 16)
            opacity = var_subtitle_bgopacity.get()
            shadow_rgba = (r, g, b, int(opacity * 255))
            
            # Create shadow image (this goes behind everything)
            shadow_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            
            # Draw shadow of the text with outline if outline is enabled
            if var_subtitle_outline.get() > 0 and outline_img:
                # Create a mask from the outline+text image
                mask = Image.new('L', img.size, 0)
                mask_draw = ImageDraw.Draw(mask)
                
                # Draw the outline shape
                outline_thickness = var_subtitle_outline.get()
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        mask_draw.text(
                            (position[0] + dx * outline_thickness, position[1] + dy * outline_thickness),
                            sample_text,
                            font=font,
                            fill=255
                        )
                
                # Draw the text shape
                mask_draw.text(position, sample_text, font=font, fill=255)
                
                # Draw shadow using the mask
                shadow_draw.bitmap(
                    (shadow_offset, shadow_offset),
                    mask,
                    fill=shadow_rgba
                )
            else:
                # Just draw shadow for the text
                shadow_draw.text(
                    (position[0] + shadow_offset, position[1] + shadow_offset),
                    sample_text,
                    font=font,
                    fill=shadow_rgba
                )
            
            # Composite shadow onto background, then add text+outline on top
            img = Image.alpha_composite(img.convert('RGBA'), shadow_img)
            img = Image.alpha_composite(img.convert('RGBA'), base_img).convert('RGB')
        else:
            # No shadow, just composite text+outline onto background
            img = Image.alpha_composite(img.convert('RGBA'), base_img).convert('RGB')
        
        # Update the draw object for any additional drawing
        draw = ImageDraw.Draw(img)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Check if preview_label and preview_frame exist and create them if needed
        if preview_frame is not None: # Ensure preview_frame exists
            if preview_label is None:
                preview_label = tk.Label(preview_frame)
                preview_label.pack(padx=10, pady=10)
            
            # Update the image
            preview_label.config(image=photo)
            preview_label.image = photo  # Keep a reference: This line should only run if preview_label is a widget
        # If preview_frame was None, preview_label might also be None, so we shouldn't try to set .image on it.
    except Exception as e:
        print(f"Error updating preview: {e}")

# Subtitles tab layout (parent is now tab_subtitles_new)
subtitle_frame = tk.Frame(tab_subtitles_new, padx=10, pady=10)
subtitle_frame.pack(fill="both", expand=True)

# Left column for settings
subtitle_settings = tk.LabelFrame(subtitle_frame, text="Subtitle Settings", padx=10, pady=10)
subtitle_settings.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Add Generate .srt checkbox to subtitle_settings
tk.Checkbutton(subtitle_settings, text="Generate Subtitles .srt", variable=var_generate_srt).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Subtitle line max width
tk.Label(subtitle_settings, text="Characters per line (max):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_subtitle_max_width = tk.Entry(subtitle_settings, width=10) # Adjusted width
entry_subtitle_max_width.insert(0, default_subtitle_maxwidth)
entry_subtitle_max_width.grid(row=1, column=1, padx=5, pady=5, sticky="w")


# Font settings
tk.Label(subtitle_settings, text="Font:").grid(row=2, column=0, sticky="w", padx=5, pady=5) # Adjusted row
font_dropdown = ttk.Combobox(subtitle_settings, textvariable=var_subtitle_font, values=available_fonts, width=25)
font_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5) # Adjusted row
font_dropdown.bind("<<ComboboxSelected>>", schedule_subtitle_preview_update) # Use debounced update

# Font size with slider and numeric display
font_size_frame = tk.Frame(subtitle_settings)
font_size_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

tk.Label(subtitle_settings, text="Font Size:").grid(row=3, column=0, sticky="w", padx=5, pady=5) # Adjusted row
font_size_slider = ttk.Scale(font_size_frame, from_=12, to=48, variable=var_subtitle_fontsize, orient="horizontal")
font_size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
font_size_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_subtitle_fontsize, font_size_value_entry), schedule_subtitle_preview_update())) # Use debounced update

font_size_value_entry = tk.Entry(font_size_frame, width=4)
font_size_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
font_size_value_entry.insert(0, str(var_subtitle_fontsize.get()))
font_size_value_entry.bind("<Return>", lambda e: update_slider_from_entry(font_size_value_entry, var_subtitle_fontsize, font_size_slider, 12, 48))
font_size_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(font_size_value_entry, var_subtitle_fontsize, font_size_slider, 12, 48))

tk.Label(subtitle_settings, text="Text Color:").grid(row=4, column=0, padx=5, pady=5, sticky="w") # Adjusted row
text_color_entry = tk.Entry(subtitle_settings, textvariable=var_subtitle_fontcolor, width=10)
text_color_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5) # Adjusted row
text_color_entry.bind("<KeyRelease>", schedule_subtitle_preview_update) # Use debounced update

# Shadow checkbox
shadow_frame = tk.Frame(subtitle_settings)
shadow_frame.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5) # Adjusted row
shadow_checkbox = tk.Checkbutton(shadow_frame, text="Enable Text Shadow", variable=var_subtitle_shadow, command=schedule_subtitle_preview_update) # Use debounced update
shadow_checkbox.pack(anchor="w")

tk.Label(subtitle_settings, text="Shadow Color:").grid(row=6, column=0, padx=5, pady=5, sticky="w") # Adjusted row
bg_color_entry = tk.Entry(subtitle_settings, textvariable=var_subtitle_bgcolor, width=10)
bg_color_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5) # Adjusted row
bg_color_entry.bind("<KeyRelease>", schedule_subtitle_preview_update) # Use debounced update

# Background opacity with slider and numeric display
bg_opacity_frame = tk.Frame(subtitle_settings)
bg_opacity_frame.grid(row=7, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

tk.Label(subtitle_settings, text="Shadow Opacity:").grid(row=7, column=0, padx=5, pady=5, sticky="w") # Adjusted row
bg_opacity_slider = ttk.Scale(bg_opacity_frame, from_=0, to=1, variable=var_subtitle_bgopacity, orient="horizontal")
bg_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
bg_opacity_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_subtitle_bgopacity, bg_opacity_value_entry), schedule_subtitle_preview_update())) # Use debounced update

bg_opacity_value_entry = tk.Entry(bg_opacity_frame, width=4)
bg_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
bg_opacity_value_entry.insert(0, str(var_subtitle_bgopacity.get()))
bg_opacity_value_entry.bind("<Return>", lambda e: update_slider_from_entry(bg_opacity_value_entry, var_subtitle_bgopacity, bg_opacity_slider, 0, 1))
bg_opacity_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(bg_opacity_value_entry, var_subtitle_bgopacity, bg_opacity_slider, 0, 1))

# Outline thickness with slider and numeric display
outline_frame = tk.Frame(subtitle_settings)
outline_frame.grid(row=8, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

tk.Label(subtitle_settings, text="Outline Thickness:").grid(row=8, column=0, padx=5, pady=5, sticky="w") # Adjusted row
outline_slider = ttk.Scale(outline_frame, from_=0, to=4, variable=var_subtitle_outline, orient="horizontal")
outline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
outline_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_subtitle_outline, outline_value_entry), schedule_subtitle_preview_update())) # Use debounced update

outline_value_entry = tk.Entry(outline_frame, width=4)
outline_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
outline_value_entry.insert(0, str(var_subtitle_outline.get()))
outline_value_entry.bind("<Return>", lambda e: update_slider_from_entry(outline_value_entry, var_subtitle_outline, outline_slider, 0, 4))
outline_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(outline_value_entry, var_subtitle_outline, outline_slider, 0, 4))

tk.Label(subtitle_settings, text="Outline Color:").grid(row=9, column=0, padx=5, pady=5, sticky="w") # Adjusted row
outline_color_entry = tk.Entry(subtitle_settings, textvariable=var_subtitle_outlinecolor, width=10)
outline_color_entry.grid(row=9, column=1, sticky="w", padx=5, pady=5) # Adjusted row
outline_color_entry.bind("<KeyRelease>", schedule_subtitle_preview_update) # Use debounced update

# Initialize shadow controls state
toggle_shadow_controls()

# Position selection
tk.Label(subtitle_settings, text="Position:").grid(row=10, column=0, padx=5, pady=5, sticky="w") # Adjusted row
position_frame = tk.Frame(subtitle_settings)
position_frame.grid(row=10, column=1, sticky="w", padx=5, pady=5) # Adjusted row

positions = [
    (5, "Top Left"), (6, "Top Center"), (7, "Top Right"),
    (9, "Middle Left"), (10, "Middle Center"), (11, "Middle Right"),
    (1, "Bottom Left"), (2, "Bottom Center"), (3, "Bottom Right")
]

# Replace Radiobuttons with Combobox
position_labels = [label for val, label in positions]
position_values = [val for val, label in positions]

position_dropdown = ttk.Combobox(position_frame, textvariable=var_subtitle_position, values=position_labels, width=25)
position_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
position_dropdown.bind("<<ComboboxSelected>>", lambda e: (var_subtitle_position.set(position_values[position_labels.index(position_dropdown.get())]), schedule_subtitle_preview_update()))
# Set initial value for dropdown
position_dropdown.set(positions[position_values.index(var_subtitle_position.get())][1])


# Right column for preview
# preview_frame is now initialized globally, just configure it here.
# No 'global' keyword needed here as this is top-level module code.
preview_frame = tk.LabelFrame(subtitle_frame, text="Preview", padx=10, pady=10)
preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# Preview label (already initialized globally or within update_subtitle_preview)
# Ensure preview_label is created if it's None and preview_frame exists
if preview_frame is not None and preview_label is None: # preview_frame will be a widget here
    preview_label = tk.Label(preview_frame)
    preview_label.pack(padx=10, pady=10)

# Initialize preview
schedule_subtitle_preview_update() # Use debounced update

# Configure grid weights
subtitle_frame.grid_columnconfigure(0, weight=1)
subtitle_frame.grid_columnconfigure(1, weight=1)


# Title Section (First Group)
title_frame = tk.LabelFrame(left_column, text="Title Settings", padx=10, pady=5)
title_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

# New checkbox for enabling/disabling title - moved to first place
tk.Checkbutton(title_frame, text="Enable Title", variable=var_enable_title, command=toggle_title_controls).grid(row=0, column=0, padx=10, pady=5, sticky="w")

tk.Label(title_frame, text="Title:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_title = tk.Entry(title_frame, width=30)
entry_title.insert(0, default_title)
entry_title.grid(row=1, column=1, padx=10, pady=5)
entry_title.bind("<KeyRelease>", update_font_size)  # Bind key release event

tk.Label(title_frame, text="Font:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_title_font = tk.OptionMenu(title_frame, var_title_font, *available_fonts)
entry_title_font.config(width=20)
entry_title_font.grid(row=2, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Color:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_title_fontcolor = tk.OptionMenu(title_frame, var_title_fontcolor, *font_colors)
entry_title_fontcolor.config(width=10)
entry_title_fontcolor.grid(row=3, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Size AUTO (Montserrat font):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_calculated_title_font_size = tk.Entry(title_frame, width=30, state=tk.DISABLED)
entry_calculated_title_font_size.grid(row=4, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Size MANUAL:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_title_font_size = tk.Entry(title_frame, width=30)
entry_title_font_size.insert(0, default_title_font_size)
entry_title_font_size.grid(row=5, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Appearance Delay (after overlay):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
entry_title_appearance_delay = tk.Entry(title_frame, width=30)
entry_title_appearance_delay.insert(0, default_title_appearance_delay)
entry_title_appearance_delay.grid(row=6, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Visible Time:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
entry_title_visible_time = tk.Entry(title_frame, width=30)
entry_title_visible_time.insert(0, default_title_visible_time)
entry_title_visible_time.grid(row=7, column=1, padx=10, pady=5)

tk.Label(title_frame, text="X Offset:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
entry_title_x_offset = tk.Entry(title_frame, width=30)
entry_title_x_offset.insert(0, default_title_x_offset)
entry_title_x_offset.grid(row=8, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Y Offset:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
entry_title_y_offset = tk.Entry(title_frame, width=30)
entry_title_y_offset.insert(0, default_title_y_offset)
entry_title_y_offset.grid(row=9, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Opacity:").grid(row=10, column=0, padx=10, pady=5, sticky="w")
title_opacity_frame = tk.Frame(title_frame)
title_opacity_frame.grid(row=10, column=1, sticky="ew", padx=10, pady=5)

title_opacity_slider = ttk.Scale(title_opacity_frame, from_=0.0, to=1.0, variable=var_title_opacity, orient="horizontal")
title_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
title_opacity_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_title_opacity, title_opacity_value_entry)))

title_opacity_value_entry = tk.Entry(title_opacity_frame, width=4)
title_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
title_opacity_value_entry.insert(0, f"{var_title_opacity.get():.2f}")
title_opacity_value_entry.bind("<Return>", lambda e: update_slider_from_entry(title_opacity_value_entry, var_title_opacity, title_opacity_slider, 0, 1))
title_opacity_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(title_opacity_value_entry, var_title_opacity, title_opacity_slider, 0, 1))

# New: Title Background controls
title_background_checkbox = tk.Checkbutton(title_frame, text="Enable Background", variable=var_enable_title_background, command=toggle_title_controls)
title_background_checkbox.grid(row=11, column=0, padx=10, pady=5, sticky="w")

tk.Label(title_frame, text="Background Color:").grid(row=12, column=0, padx=10, pady=5, sticky="w")
title_background_color_entry = tk.Entry(title_frame, textvariable=var_title_background_color, width=30)
title_background_color_entry.grid(row=12, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Background Opacity:").grid(row=13, column=0, padx=10, pady=5, sticky="w")
title_background_opacity_frame = tk.Frame(title_frame)
title_background_opacity_frame.grid(row=13, column=1, sticky="ew", padx=10, pady=5)

title_background_opacity_slider = ttk.Scale(title_background_opacity_frame, from_=0.0, to=1.0, variable=var_title_background_opacity, orient="horizontal")
title_background_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
title_background_opacity_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_title_background_opacity, title_background_opacity_value_entry)))

title_background_opacity_value_entry = tk.Entry(title_background_opacity_frame, width=4)
title_background_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
title_background_opacity_value_entry.insert(0, f"{var_title_background_opacity.get():.2f}")
title_background_opacity_value_entry.bind("<Return>", lambda e: update_slider_from_entry(title_background_opacity_value_entry, var_title_background_opacity, title_background_opacity_slider, 0, 1))
title_background_opacity_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(title_background_opacity_value_entry, var_title_background_opacity, title_background_opacity_slider, 0, 1))

# Initialize title controls state
# toggle_title_controls()



# Overlay Effects Tab Content Frame
overlay_effects_left_column = tk.Frame(tab_overlay_effects)
overlay_effects_left_column.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
overlay_effects_right_column = tk.Frame(tab_overlay_effects)
overlay_effects_right_column.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

tab_overlay_effects.grid_rowconfigure(0, weight=1)
tab_overlay_effects.grid_columnconfigure(0, weight=1)
tab_overlay_effects.grid_columnconfigure(1, weight=1)

# Watermark Section (New location: Overlay Effects tab)
watermark_frame = tk.LabelFrame(overlay_effects_right_column, text="Watermark", padx=10, pady=5)
watermark_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew", columnspan=2) # Adjusted grid

# New checkbox for enabling/disabling watermark (first place)
tk.Checkbutton(watermark_frame, text="Enable", variable=var_enable_watermark, command=toggle_watermark_controls).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

tk.Label(watermark_frame, text="Text:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
text_watermark = tk.Text(watermark_frame, width=30, height=3)
text_watermark.insert("1.0", default_watermark)
text_watermark.grid(row=1, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Font:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_font = tk.OptionMenu(watermark_frame, var_watermark_font, *available_fonts)
entry_font.config(width=20)
entry_font.grid(row=2, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Font Size:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_watermark_font_size = tk.Entry(watermark_frame, textvariable=var_watermark_font_size, width=30)
entry_watermark_font_size.grid(row=3, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Opacity:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
watermark_opacity_slider = ttk.Scale(watermark_frame, from_=0.0, to=1.0, variable=var_watermark_opacity, orient="horizontal")
watermark_opacity_slider.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

tk.Label(watermark_frame, text="Font Color:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_watermark_fontcolor = tk.OptionMenu(watermark_frame, var_watermark_fontcolor, *font_colors)
entry_watermark_fontcolor.config(width=10)
entry_watermark_fontcolor.grid(row=5, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Type:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
entry_watermark_type = tk.OptionMenu(watermark_frame, var_watermark_type, *watermark_types)
entry_watermark_type.config(width=10)
entry_watermark_type.grid(row=6, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Speed (1=Slow, 10=Fast):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
watermark_speed_slider = ttk.Scale(watermark_frame, from_=1, to=10, variable=var_watermark_speed_intuitive, orient="horizontal")
watermark_speed_slider.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

# Folders Section (First Group in Right Column)
folders_frame = tk.LabelFrame(right_column, text="Folders", padx=10, pady=5)
folders_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

tk.Label(folders_frame, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_input_folder = tk.Entry(folders_frame, width=30)
entry_input_folder.insert(0, default_input_folder)
entry_input_folder.grid(row=0, column=1, padx=10, pady=5)

tk.Label(folders_frame, text="Template Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_template_folder = tk.Entry(folders_frame, width=30)
entry_template_folder.insert(0, "TEMPLATE")
entry_template_folder.grid(row=1, column=1, padx=10, pady=5)

# Video Duration Section (Second Group in Right Column)
duration_frame = tk.LabelFrame(right_column, text="Video Duration", padx=10, pady=5)
duration_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

tk.Label(duration_frame, text="Segment Duration:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_segment_duration = tk.Entry(duration_frame, width=30)
entry_segment_duration.insert(0, default_segment_duration)
entry_segment_duration.grid(row=0, column=1, padx=10, pady=5)

tk.Label(duration_frame, text="MAX Length Limit (s):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_time_limit = tk.Entry(duration_frame, width=30)
entry_time_limit.insert(0, default_time_limit)
entry_time_limit.grid(row=1, column=1, padx=10, pady=5)

# Sound/Audio Section
sound_frame = tk.LabelFrame(right_column, text="Audio Settings", padx=10, pady=5)
sound_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

tk.Label(sound_frame, text="Voiceover Start Delay (s):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_voiceover_delay = tk.Entry(sound_frame, width=30)
entry_voiceover_delay.insert(0, default_voiceover_delay)
entry_voiceover_delay.grid(row=0, column=1, padx=10, pady=5)

# Overlay Effects Tab Content Frame
# Effect Overlay Section (parent is now overlay_effects_left_column)
effect_frame = tk.LabelFrame(overlay_effects_right_column, text="Effect Overlay", padx=10, pady=5) # Corrected parent
effect_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew", columnspan=2) # Adjusted row to 0

# Create variables for effect settings
var_effect_overlay = tk.StringVar(root, value="None")
var_effect_opacity = tk.DoubleVar(root, value=0.2)
var_effect_blend = tk.StringVar(root, value="overlay")

# Function to update effect opacity value display
def update_effect_opacity_value(*args):
    effect_opacity_value.delete(0, tk.END)
    effect_opacity_value.insert(0, f"{var_effect_opacity.get():.2f}")

# Function to update effect opacity from entry
def update_effect_opacity_from_entry(*args):
    try:
        value = float(effect_opacity_value.get())
        if 0 <= value <= 1:
            var_effect_opacity.set(value)
    except ValueError:
        pass


# Get available effect files (general overlays)
if not os.path.exists(overlays_dir):
    os.makedirs(overlays_dir)
effect_files = ["None"] + [f for f in os.listdir(overlays_dir) if f.endswith('.mp4')]

tk.Checkbutton(effect_frame, text="Enable Effect Overlay", variable=var_enable_effect_overlay, command=toggle_effect_overlay_controls).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

tk.Label(effect_frame, text="Effect:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
effect_dropdown = ttk.Combobox(effect_frame, textvariable=var_effect_overlay, values=effect_files, width=25)
effect_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

tk.Label(effect_frame, text="Blend Mode:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
blend_dropdown = ttk.Combobox(effect_frame, textvariable=var_effect_blend, values=SUPPORTED_BLEND_MODES, width=25)
blend_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

# Opacity with slider and numeric display
tk.Label(effect_frame, text="Opacity:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
effect_opacity_frame = tk.Frame(effect_frame)
effect_opacity_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

effect_opacity_slider = ttk.Scale(effect_opacity_frame, from_=0, to=1, variable=var_effect_opacity, orient="horizontal")
effect_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
effect_opacity_slider.bind("<ButtonRelease-1>", update_effect_opacity_value)

effect_opacity_value = tk.Entry(effect_opacity_frame, width=5)
effect_opacity_value.pack(side=tk.RIGHT, padx=(5, 0))
effect_opacity_value.insert(0, f"{var_effect_opacity.get():.2f}")
effect_opacity_value.bind("<Return>", update_effect_opacity_from_entry)
effect_opacity_value.bind("<FocusOut>", update_effect_opacity_from_entry)

# Subscribe Overlay Section (new LabelFrame)
subscribe_overlay_frame = tk.LabelFrame(overlay_effects_left_column, text="Subscribe Overlay", padx=10, pady=5)
subscribe_overlay_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

enable_subscribe_overlay_checkbox = tk.Checkbutton(subscribe_overlay_frame, text="Enable", variable=var_enable_subscribe_overlay)
enable_subscribe_overlay_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

# Get available subscribe overlay files
if not os.path.exists(subscribe_dir):
    os.makedirs(subscribe_dir)
subscribe_overlay_files = ["None"] + [f for f in os.listdir(subscribe_dir) if f.endswith('.mp4')]

tk.Label(subscribe_overlay_frame, text="Overlay File:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_subscribe_overlay_file = ttk.Combobox(subscribe_overlay_frame, textvariable=var_subscribe_overlay_file, values=subscribe_overlay_files, width=25)
entry_subscribe_overlay_file.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
entry_subscribe_overlay_file.bind("<<ComboboxSelected>>", toggle_subscribe_overlay_controls) # Bind to update state

tk.Label(subscribe_overlay_frame, text="Appearance Delay (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_subscribe_delay = tk.Entry(subscribe_overlay_frame, textvariable=var_subscribe_delay, width=30)
entry_subscribe_delay.grid(row=2, column=1, padx=10, pady=5)

# Relocated Chromakey Controls
tk.Label(subscribe_overlay_frame, text="Chromakey Color:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_chromakey_color = tk.Entry(subscribe_overlay_frame, width=30, textvariable=var_chromakey_color)
entry_chromakey_color.grid(row=3, column=1, padx=10, pady=5)

tk.Label(subscribe_overlay_frame, text="Chromakey Similarity:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_chromakey_similarity = tk.Entry(subscribe_overlay_frame, width=30)
entry_chromakey_similarity.insert(0, default_chromakey_similarity)
entry_chromakey_similarity.grid(row=4, column=1, padx=10, pady=5)

tk.Label(subscribe_overlay_frame, text="Chromakey Blend:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_chromakey_blend = tk.Entry(subscribe_overlay_frame, width=30)
entry_chromakey_blend.insert(0, default_chromakey_blend)
entry_chromakey_blend.grid(row=5, column=1, padx=10, pady=5)

# New: Title Video Overlay Section (moved from Main Settings tab)
title_video_overlay_frame = tk.LabelFrame(overlay_effects_left_column, text="Title Overlay", padx=10, pady=5)
title_video_overlay_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

enable_title_video_overlay_checkbox = tk.Checkbutton(title_video_overlay_frame, text="Enable", variable=var_enable_title_video_overlay)
enable_title_video_overlay_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

# Get available title video overlay files
if not os.path.exists(title_dir):
    os.makedirs(title_dir)
title_video_overlay_files = ["None"] + [f for f in os.listdir(title_dir) if f.endswith('.mp4')]

tk.Label(title_video_overlay_frame, text="Overlay File:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_title_video_overlay_file = ttk.Combobox(title_video_overlay_frame, textvariable=var_title_video_overlay_file, values=title_video_overlay_files, width=25)
entry_title_video_overlay_file.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
entry_title_video_overlay_file.bind("<<ComboboxSelected>>", toggle_title_controls) # Bind to update state

tk.Label(title_video_overlay_frame, text="Appearance Delay (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_title_video_overlay_delay = tk.Entry(title_video_overlay_frame, textvariable=var_title_video_overlay_delay, width=30)
entry_title_video_overlay_delay.grid(row=2, column=1, padx=10, pady=5)

tk.Label(title_video_overlay_frame, text="Chromakey Color:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_title_video_chromakey_color = tk.Entry(title_video_overlay_frame, textvariable=var_title_video_chromakey_color, width=30)
entry_title_video_chromakey_color.grid(row=3, column=1, padx=10, pady=5)

tk.Label(title_video_overlay_frame, text="Chromakey Similarity:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_title_video_chromakey_similarity = tk.Entry(title_video_overlay_frame, textvariable=var_title_video_chromakey_similarity, width=30)
entry_title_video_chromakey_similarity.grid(row=4, column=1, padx=10, pady=5)

tk.Label(title_video_overlay_frame, text="Chromakey Blend:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_title_video_chromakey_blend = tk.Entry(title_video_overlay_frame, textvariable=var_title_video_chromakey_blend, width=30)
entry_title_video_chromakey_blend.grid(row=5, column=1, padx=10, pady=5)

# Video Processing Section (Last Group in Right Column of Main Settings Tab)
processing_frame = tk.LabelFrame(right_column, text="Video Processing", padx=10, pady=5)
processing_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew") # Adjusted row

# Create a frame for orientation
orientation_frame = tk.Frame(processing_frame)
orientation_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

tk.Label(orientation_frame, text="Orientation:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
# Create a StringVar for video orientation
var_video_orientation = tk.StringVar(value='horizontal')  # Default to horizontal
tk.Radiobutton(orientation_frame, text="Vertical", variable=var_video_orientation, value='vertical').grid(row=0, column=1, padx=5, pady=5)
tk.Radiobutton(orientation_frame, text="Horizontal", variable=var_video_orientation, value='horizontal').grid(row=0, column=2, padx=5, pady=5)

# Create a frame for checkboxes
checkbox_frame = tk.Frame(processing_frame)
checkbox_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

# Create a BooleanVar for adding blur
var_add_blur = tk.BooleanVar()
var_add_blur.set(False)  # Default to not adding blur
blur_checkbox = tk.Checkbutton(checkbox_frame, text="Side Blur", variable=var_add_blur)
blur_checkbox.grid(row=0, column=0, padx=5, pady=5)

# DepthFlow checkbox
var_depthflow = tk.BooleanVar()
var_depthflow.set(False)
tk.Checkbutton(checkbox_frame, text="Depthflow", variable=var_depthflow).grid(row=0, column=1, padx=5, pady=5)

# Function to show/hide blur checkbox based on orientation
def toggle_blur_checkbox():
    if var_video_orientation.get() == 'horizontal':
        blur_checkbox.config(state=tk.NORMAL)
    else:
        blur_checkbox.config(state=tk.DISABLED)
        var_add_blur.set(False)  # Reset blur option if not horizontal

# Bind the radiobutton selection to the toggle function
var_video_orientation.trace('w', lambda *args: toggle_blur_checkbox())

# Initialize the toggle_blur_checkbox function
toggle_blur_checkbox()

# Add START and EXIT buttons at the bottom
buttons_frame = tk.Frame(root)
buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

start_button = tk.Button(
    buttons_frame,
    text="START",
    command=start_process,
    fg="green",
    highlightbackground="green",
    width=15,
    height=2
)
start_button.grid(row=0, column=1, pady=10, padx=20)

quit_button = tk.Button(
    buttons_frame,
    text="EXIT",
    command=root.quit,
    bg="black",
    highlightbackground="black",
    width=15,
    height=2
)
quit_button.grid(row=0, column=0, pady=10, padx=20)

# Load initial config
load_config()

# Initialize control states after all widgets are created and packed
toggle_shadow_controls()
toggle_title_controls()
toggle_subscribe_overlay_controls()
toggle_watermark_controls()
toggle_effect_overlay_controls()

# Start main loop
root.mainloop()
