import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
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
default_title_font = 'Montserrat-SemiBold.otf'  # Default title font
default_title_font_size = 90
default_title_fontcolor = 'random'  # Default font color
default_delay = 21  # Default delay for subscribe overlay
default_title_appearance_delay = 1  # Default delay before title appears
default_title_visible_time = 5  # Default time title remains visible
default_title_x_offset = 110  # Default X offset for title positioning
default_title_y_offset = -35  # Default Y offset for title positioning

default_voiceover_delay = 5

default_watermark = 'Today is a\n Plus Day'
default_watermark_type = 'random'
default_watermark_speed = 50
default_watermark_font = 'Nexa Bold.otf'  # Default font

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
    'screen',     # Lightens the base color
    'multiply',   # Darkens the base color
    'addition',   # Adds pixel values
    'difference', # Subtracts pixel values
    'dodge',      # Brightens base color based on blend color
    'burn',       # Darkens base color based on blend color
    'softlight',  # Subtle light/dark effect
    'hardlight',  # Dramatic contrast effect
    'divide',     # Divides pixel values
    'subtract',   # Subtracts pixel values
]

# Get available fonts from the fonts directory
fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
available_fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
if not available_fonts:
    available_fonts = ['Nexa Bold.otf']  # Fallback if no fonts found

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
var_title_fontcolor = tk.StringVar(root)
var_title_fontcolor.set(default_title_fontcolor)  # Set default font color
var_title_font = tk.StringVar(root)
var_title_font.set(default_title_font)  # Set default title font

# Create StringVar for chromakey color
var_chromakey_color = tk.StringVar(root)
var_chromakey_color.set(default_chromakey_color)  # Set default chromakey color

# Create BooleanVar for .srt generation
var_generate_srt = tk.BooleanVar()
var_generate_srt.set(default_generate_srt)  # Default to not generating .srt

# Get config files from folder
config_folder = os.path.join(os.path.dirname(__file__), 'config')
config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]

def start_process():
    # Get values from the entry fields
    title = entry_title.get()
    watermark = text_watermark.get("1.0", tk.END).strip()
    watermark_type = var_watermark_type.get()
    watermark_speed = entry_watermark_speed.get()
    manual_font_size = entry_title_font_size.get()
    segment_duration = entry_segment_duration.get()
    input_folder = entry_input_folder.get()
    template_folder = entry_template_folder.get()
    depthflow_tf = var_depthflow.get()
    time_limit = entry_time_limit.get()
    video_orientation = var_video_orientation.get()
    blur_checkbox = var_add_blur.get()
    
    # Get subscribe.py parameters
    delay = entry_delay.get()
    title_fontcolor = var_title_fontcolor.get()
    title_font = var_title_font.get()
    voiceover_delay = entry_voiceover_delay.get()
    title_appearance_delay = entry_title_appearance_delay.get()
    title_visible_time = entry_title_visible_time.get()
    title_x_offset = entry_title_x_offset.get()
    title_y_offset = entry_title_y_offset.get()
    
    # Get chromakey parameters
    chromakey_color = var_chromakey_color.get()
    chromakey_similarity = entry_chromakey_similarity.get()
    chromakey_blend = entry_chromakey_blend.get()
    
    # Get effect overlay parameters
    effect_overlay = var_effect_overlay.get()
    effect_opacity = var_effect_opacity.get()
    effect_blend = var_effect_blend.get()
    
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
        '--osd', str(delay),
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

    print(command)
    subprocess.run(command)
    

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
        'delay': default_delay,
        'title_fontcolor': default_title_fontcolor,
        'title_font': default_title_font,
        'voiceover_delay': default_voiceover_delay,
        'title_appearance_delay': default_title_appearance_delay,
        'title_visible_time': default_title_visible_time,
        'title_x_offset': default_title_x_offset,
        'title_y_offset': default_title_y_offset,
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
    entry_watermark_speed.delete(0, tk.END)
    entry_watermark_speed.insert(0, config.get('watermark_speed', default_watermark_speed))
    
    # Set font if it exists in config, otherwise use default
    if 'font' in config and config['font'] in available_fonts:
        var_watermark_font.set(config['font'])
    else:
        # If the configured font is not available, use the first available font
        var_watermark_font.set(available_fonts[0] if available_fonts else default_watermark_font)
    
    # Load subscribe.py parameters
    entry_delay.delete(0, tk.END)
    entry_delay.insert(0, config.get('delay', default_delay))
    
    # Load voiceover delay
    entry_voiceover_delay.delete(0, tk.END)
    entry_voiceover_delay.insert(0, config.get('voiceover_delay', default_voiceover_delay))
    
    # Load title offset parameters
    entry_title_x_offset.delete(0, tk.END)
    entry_title_x_offset.insert(0, config.get('title_x_offset', default_title_x_offset))
    
    entry_title_y_offset.delete(0, tk.END)
    entry_title_y_offset.insert(0, config.get('title_y_offset', default_title_y_offset))
    
    # Load chromakey parameters
    var_chromakey_color.set(config.get('chromakey_color', default_chromakey_color))
    
    entry_chromakey_similarity.delete(0, tk.END)
    entry_chromakey_similarity.insert(0, config.get('chromakey_similarity', default_chromakey_similarity))
    
    entry_chromakey_blend.delete(0, tk.END)
    entry_chromakey_blend.insert(0, config.get('chromakey_blend', default_chromakey_blend))
    
    # Load effect overlay parameters
    var_effect_overlay.set(config.get('effect_overlay', 'None'))
    var_effect_opacity.set(config.get('effect_opacity', 0.2))
    var_effect_blend.set(config.get('effect_blend', 'overlay'))
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
    
    # Update shadow controls state
    toggle_shadow_controls()
    
    # Update subtitle preview
    update_subtitle_preview()
    
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
            'watermark': text_watermark.get("1.0", tk.END).strip(),
            'watermark_type': var_watermark_type.get(),
            'watermark_speed': entry_watermark_speed.get(),
            'title_font_size': entry_title_font_size.get(),
            'segment_duration': entry_segment_duration.get(),
            'input_folder': entry_input_folder.get(),
            'template_folder': entry_template_folder.get(),
            'depthflow': var_depthflow.get(),
            'time_limit': entry_time_limit.get(),
            'video_orientation': var_video_orientation.get(),
            'blur': var_add_blur.get(),
            'watermark_font': var_watermark_font.get(),
            'delay': entry_delay.get(),
            'title_fontcolor': var_title_fontcolor.get(),
            'title_font': var_title_font.get(),
            'voiceover_delay': entry_voiceover_delay.get(),
            'title_appearance_delay': entry_title_appearance_delay.get(),
            'title_visible_time': entry_title_visible_time.get(),
            'title_x_offset': entry_title_x_offset.get(),
            'title_y_offset': entry_title_y_offset.get(),
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
            'effect_blend': var_effect_blend.get()
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
            'watermark': text_watermark.get("1.0", tk.END).strip(),
            'watermark_type': var_watermark_type.get(),
            'watermark_speed': entry_watermark_speed.get(),
            'title_font_size': entry_title_font_size.get(),
            'segment_duration': entry_segment_duration.get(),
            'input_folder': entry_input_folder.get(),
            'template_folder': entry_template_folder.get(),
            'depthflow': var_depthflow.get(),
            'time_limit': entry_time_limit.get(),
            'video_orientation': var_video_orientation.get(),
            'blur': var_add_blur.get(),
            'watermark_font': var_watermark_font.get(),
            'delay': entry_delay.get(),
            'title_fontcolor': var_title_fontcolor.get(),
            'title_font': var_title_font.get(),
            'voiceover_delay': entry_voiceover_delay.get(),
            'title_appearance_delay': entry_title_appearance_delay.get(),
            'title_visible_time': entry_title_visible_time.get(),
            'title_x_offset': entry_title_x_offset.get(),
            'title_y_offset': entry_title_y_offset.get(),
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
            'effect_blend': var_effect_blend.get()
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
config_frame = tk.Frame(root)
config_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Label(config_frame, text="Config:").grid(row=0, column=0, padx=10, pady=5)
config_menu = tk.OptionMenu(config_frame, var_config, *config_files)
config_menu.config(width=15)
config_menu.grid(row=0, column=1, padx=10, pady=5)

# Now that config_menu is defined, we can update it
update_config_menu()

# Save New Config elements
tk.Label(config_frame, text="Save as:").grid(row=0, column=2, padx=10, pady=5)
entry_new_filename = tk.Entry(config_frame, width=15)
entry_new_filename.grid(row=0, column=3, padx=10, pady=5)

save_new_button = tk.Button(
    config_frame,
    text="Save New Config",
    command=save_new_config,
    fg="blue",
    highlightbackground="blue"
)
save_new_button.grid(row=0, column=4, pady=5, padx=5)

save_button = tk.Button(
    config_frame,
    text="Save",
    command=save_config,
    fg="green",
    highlightbackground="green"
)
save_button.grid(row=0, column=5, pady=5, padx=5)

delete_button = tk.Button(
    config_frame,
    text="Delete",
    command=delete_config,
    fg="red",
    highlightbackground="red"
)
delete_button.grid(row=0, column=6, pady=5, padx=5)

# Create a notebook for tabbed interface
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, sticky="nsew")
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create tabs
tab_main_settings = ttk.Frame(notebook)
tab_subtitles_new = ttk.Frame(notebook) 
tab_advanced_effects = ttk.Frame(notebook)

# Add tabs to notebook
notebook.add(tab_main_settings, text="Main Settings")
notebook.add(tab_subtitles_new, text="Subtitles")
notebook.add(tab_advanced_effects, text="Advanced Effects")

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
    update_subtitle_preview()

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
            update_subtitle_preview()
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
            shadow_offset = 2
            
            # If outline is enabled, draw shadow for the outlined text
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
            img = Image.alpha_composite(img, base_img).convert('RGB')
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
font_dropdown.bind("<<ComboboxSelected>>", update_subtitle_preview)

# Font size with slider and numeric display
font_size_frame = tk.Frame(subtitle_settings)
font_size_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

tk.Label(subtitle_settings, text="Font Size:").grid(row=3, column=0, sticky="w", padx=5, pady=5) # Adjusted row
font_size_slider = ttk.Scale(font_size_frame, from_=12, to=48, variable=var_subtitle_fontsize, orient="horizontal")
font_size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
font_size_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_subtitle_fontsize, font_size_value_entry), update_subtitle_preview()))

font_size_value_entry = tk.Entry(font_size_frame, width=4)
font_size_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
font_size_value_entry.insert(0, str(var_subtitle_fontsize.get()))
font_size_value_entry.bind("<Return>", lambda e: update_slider_from_entry(font_size_value_entry, var_subtitle_fontsize, font_size_slider, 12, 48))
font_size_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(font_size_value_entry, var_subtitle_fontsize, font_size_slider, 12, 48))

tk.Label(subtitle_settings, text="Text Color:").grid(row=4, column=0, sticky="w", padx=5, pady=5) # Adjusted row
text_color_entry = tk.Entry(subtitle_settings, textvariable=var_subtitle_fontcolor, width=10)
text_color_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5) # Adjusted row
text_color_entry.bind("<KeyRelease>", update_subtitle_preview)

# Shadow checkbox
shadow_frame = tk.Frame(subtitle_settings)
shadow_frame.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5) # Adjusted row
shadow_checkbox = tk.Checkbutton(shadow_frame, text="Enable Text Shadow", variable=var_subtitle_shadow, command=toggle_shadow_controls)
shadow_checkbox.pack(anchor="w")

tk.Label(subtitle_settings, text="Shadow Color:").grid(row=6, column=0, sticky="w", padx=5, pady=5) # Adjusted row
bg_color_entry = tk.Entry(subtitle_settings, textvariable=var_subtitle_bgcolor, width=10)
bg_color_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5) # Adjusted row
bg_color_entry.bind("<KeyRelease>", update_subtitle_preview)

# Background opacity with slider and numeric display
bg_opacity_frame = tk.Frame(subtitle_settings)
bg_opacity_frame.grid(row=7, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

tk.Label(subtitle_settings, text="Shadow Opacity:").grid(row=7, column=0, sticky="w", padx=5, pady=5) # Adjusted row
bg_opacity_slider = ttk.Scale(bg_opacity_frame, from_=0, to=1, variable=var_subtitle_bgopacity, orient="horizontal")
bg_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
bg_opacity_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_subtitle_bgopacity, bg_opacity_value_entry), update_subtitle_preview()))

bg_opacity_value_entry = tk.Entry(bg_opacity_frame, width=4)
bg_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
bg_opacity_value_entry.insert(0, str(var_subtitle_bgopacity.get()))
bg_opacity_value_entry.bind("<Return>", lambda e: update_slider_from_entry(bg_opacity_value_entry, var_subtitle_bgopacity, bg_opacity_slider, 0, 1))
bg_opacity_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(bg_opacity_value_entry, var_subtitle_bgopacity, bg_opacity_slider, 0, 1))

# Outline thickness with slider and numeric display
outline_frame = tk.Frame(subtitle_settings)
outline_frame.grid(row=8, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

tk.Label(subtitle_settings, text="Outline Thickness:").grid(row=8, column=0, sticky="w", padx=5, pady=5) # Adjusted row
outline_slider = ttk.Scale(outline_frame, from_=0, to=4, variable=var_subtitle_outline, orient="horizontal")
outline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
outline_slider.bind("<ButtonRelease-1>", lambda e: (update_slider_value(var_subtitle_outline, outline_value_entry), update_subtitle_preview()))

outline_value_entry = tk.Entry(outline_frame, width=4)
outline_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
outline_value_entry.insert(0, str(var_subtitle_outline.get()))
outline_value_entry.bind("<Return>", lambda e: update_slider_from_entry(outline_value_entry, var_subtitle_outline, outline_slider, 0, 4))
outline_value_entry.bind("<FocusOut>", lambda e: update_slider_from_entry(outline_value_entry, var_subtitle_outline, outline_slider, 0, 4))

tk.Label(subtitle_settings, text="Outline Color:").grid(row=9, column=0, sticky="w", padx=5, pady=5) # Adjusted row
outline_color_entry = tk.Entry(subtitle_settings, textvariable=var_subtitle_outlinecolor, width=10)
outline_color_entry.grid(row=9, column=1, sticky="w", padx=5, pady=5) # Adjusted row
outline_color_entry.bind("<KeyRelease>", update_subtitle_preview)

# Initialize shadow controls state
toggle_shadow_controls()

# Position selection
tk.Label(subtitle_settings, text="Position:").grid(row=10, column=0, sticky="w", padx=5, pady=5) # Adjusted row
position_frame = tk.Frame(subtitle_settings)
position_frame.grid(row=10, column=1, sticky="w", padx=5, pady=5) # Adjusted row

positions = [
    (5, "Top Left"), (6, "Top Center"), (7, "Top Right"),
    (9, "Middle Left"), (10, "Middle Center"), (11, "Middle Right"),
    (1, "Bottom Left"), (2, "Bottom Center"), (3, "Bottom Right")
]

for pos, label in positions:
    tk.Radiobutton(
        position_frame, 
        text=label, 
        variable=var_subtitle_position, 
        value=pos,
        command=update_subtitle_preview
    ).pack(anchor="w")

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
update_subtitle_preview()

# Configure grid weights
subtitle_frame.grid_columnconfigure(0, weight=1)
subtitle_frame.grid_columnconfigure(1, weight=1)

# Title Section (First Group)
title_frame = tk.LabelFrame(left_column, text="Title Settings", padx=10, pady=5)
title_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

tk.Label(title_frame, text="Title:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_title = tk.Entry(title_frame, width=30)
entry_title.insert(0, default_title)
entry_title.grid(row=0, column=1, padx=10, pady=5)
entry_title.bind("<KeyRelease>", update_font_size)  # Bind key release event

tk.Label(title_frame, text="Font:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_title_font = tk.OptionMenu(title_frame, var_title_font, *available_fonts)
entry_title_font.config(width=20)
entry_title_font.grid(row=1, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Color:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_title_fontcolor = tk.OptionMenu(title_frame, var_title_fontcolor, *font_colors)
entry_title_fontcolor.config(width=10)
entry_title_fontcolor.grid(row=2, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Size AUTO (Montserrat font):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_calculated_title_font_size = tk.Entry(title_frame, width=30, state=tk.DISABLED)
entry_calculated_title_font_size.grid(row=3, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Size MANUAL:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_title_font_size = tk.Entry(title_frame, width=30)
entry_title_font_size.insert(0, default_title_font_size)
entry_title_font_size.grid(row=4, column=1, padx=10, pady=5)

tk.Label(title_frame, text="Overlay Delay:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_delay = tk.Entry(title_frame, width=30)
entry_delay.insert(0, default_delay)
entry_delay.grid(row=5, column=1, padx=10, pady=5)

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

# Watermark Section (Second Group)
watermark_frame = tk.LabelFrame(left_column, text="Watermark Settings", padx=10, pady=5)
watermark_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

tk.Label(watermark_frame, text="Text:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
text_watermark = tk.Text(watermark_frame, width=30, height=3)
text_watermark.insert("1.0", default_watermark)
text_watermark.grid(row=0, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Font:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_font = tk.OptionMenu(watermark_frame, var_watermark_font, *available_fonts)
entry_font.config(width=20)
entry_font.grid(row=1, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Type:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_watermark_type = tk.OptionMenu(watermark_frame, var_watermark_type, *watermark_types)
entry_watermark_type.config(width=10)
entry_watermark_type.grid(row=2, column=1, padx=10, pady=5)

tk.Label(watermark_frame, text="Speed (frames: 25 = 1s):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_watermark_speed = tk.Entry(watermark_frame, width=30)
entry_watermark_speed.insert(0, default_watermark_speed)
entry_watermark_speed.grid(row=3, column=1, padx=10, pady=5)

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

# Advanced Effects Tab Content Frame
advanced_effects_content_frame = tk.Frame(tab_advanced_effects)
advanced_effects_content_frame.pack(fill="both", expand=True)

# Effect Overlay Section (parent is now advanced_effects_content_frame)
effect_frame = tk.LabelFrame(advanced_effects_content_frame, text="Effect Overlay", padx=10, pady=5)
effect_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew", columnspan=2) 

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

# Get available effect files
effects_dir = os.path.join(os.path.dirname(__file__), 'effects')
if not os.path.exists(effects_dir):
    os.makedirs(effects_dir)
effect_files = ["None"] + [f for f in os.listdir(effects_dir) if f.endswith('.mp4')]

tk.Label(effect_frame, text="Effect:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
effect_dropdown = ttk.Combobox(effect_frame, textvariable=var_effect_overlay, values=effect_files, width=25)
effect_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

tk.Label(effect_frame, text="Blend Mode:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
blend_dropdown = ttk.Combobox(effect_frame, textvariable=var_effect_blend, values=SUPPORTED_BLEND_MODES, width=25)
blend_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

# Opacity with slider and numeric display
tk.Label(effect_frame, text="Opacity:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
effect_opacity_frame = tk.Frame(effect_frame)
effect_opacity_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

effect_opacity_slider = ttk.Scale(effect_opacity_frame, from_=0, to=1, variable=var_effect_opacity, orient="horizontal")
effect_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
effect_opacity_slider.bind("<ButtonRelease-1>", update_effect_opacity_value)

effect_opacity_value = tk.Entry(effect_opacity_frame, width=5)
effect_opacity_value.pack(side=tk.RIGHT, padx=(5, 0))
effect_opacity_value.insert(0, f"{var_effect_opacity.get():.2f}")
effect_opacity_value.bind("<Return>", update_effect_opacity_from_entry)
effect_opacity_value.bind("<FocusOut>", update_effect_opacity_from_entry)

# Chromakey Section (parent is now advanced_effects_content_frame)
chromakey_frame = tk.LabelFrame(advanced_effects_content_frame, text="Chromakey Settings", padx=10, pady=5)
chromakey_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew", columnspan=2) 

tk.Label(chromakey_frame, text="Color:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_chromakey_color = tk.Entry(chromakey_frame, width=30, textvariable=var_chromakey_color)
entry_chromakey_color.grid(row=0, column=1, padx=10, pady=5)

tk.Label(chromakey_frame, text="Similarity:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_chromakey_similarity = tk.Entry(chromakey_frame, width=30)
entry_chromakey_similarity.insert(0, default_chromakey_similarity)
entry_chromakey_similarity.grid(row=1, column=1, padx=10, pady=5)

tk.Label(chromakey_frame, text="Blend:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_chromakey_blend = tk.Entry(chromakey_frame, width=30)
entry_chromakey_blend.insert(0, default_chromakey_blend)
entry_chromakey_blend.grid(row=2, column=1, padx=10, pady=5)

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

# Start main loop
root.mainloop()
