import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json

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

default_watermark = 'Today is a\n Plus Day'
default_watermark_type = 'random'
default_watermark_speed = 50
default_watermark_font = 'Nexa Bold.otf'  # Default font

default_depthflow = 0

# Define watermark types
watermark_types = ['ccw', 'random']

# Define font color options
font_colors = ['random', 'FF00B4', 'ff6600', '0b4178', 'FFFFFF', '000000', '00FF00', '0000FF', 'FFFF00']

# Get available fonts from the fonts directory
fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
available_fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
if not available_fonts:
    available_fonts = ['Nexa Bold.otf']  # Fallback if no fonts found

# Create the main window
root = tk.Tk()
root.title("Video Cutter GUI")

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
        '--osd', str(delay),

        '--w', watermark,
        '--wt', watermark_type,
        '--ws', watermark_speed,
        '--wf', watermark_font,

        '--z', str(depthflow),
        '--o', video_orientation,
        '--b', str(blur)

    ]

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
        'title_font': default_title_font
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
            'title_font': var_title_font.get()
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
            'title_font': var_title_font.get()
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

# Title Section (First Group)
title_frame = tk.LabelFrame(root, text="Title Settings", padx=10, pady=5)
title_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

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

tk.Label(title_frame, text="Size AUTO:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
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

# Watermark Section (Second Group)
watermark_frame = tk.LabelFrame(root, text="Watermark Settings", padx=10, pady=5)
watermark_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Label(watermark_frame, text="Text:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
text_watermark = tk.Text(watermark_frame, width=39, height=3)
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

# Folders Section (Third Group)
folders_frame = tk.LabelFrame(root, text="Folders", padx=10, pady=5)
folders_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Label(folders_frame, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_input_folder = tk.Entry(folders_frame, width=30)
entry_input_folder.insert(0, default_input_folder)
entry_input_folder.grid(row=0, column=1, padx=10, pady=5)

tk.Label(folders_frame, text="Template Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_template_folder = tk.Entry(folders_frame, width=30)
entry_template_folder.insert(0, "TEMPLATE")
entry_template_folder.grid(row=1, column=1, padx=10, pady=5)

# Video Duration Section (Fourth Group)
duration_frame = tk.LabelFrame(root, text="Video Duration", padx=10, pady=5)
duration_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Label(duration_frame, text="Segment Duration:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_segment_duration = tk.Entry(duration_frame, width=30)
entry_segment_duration.insert(0, default_segment_duration)
entry_segment_duration.grid(row=0, column=1, padx=10, pady=5)

tk.Label(duration_frame, text="Time Limit (s):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_time_limit = tk.Entry(duration_frame, width=30)
entry_time_limit.insert(0, default_time_limit)
entry_time_limit.grid(row=1, column=1, padx=10, pady=5)

# Video Processing Section (Fifth Group)
processing_frame = tk.LabelFrame(root, text="Video Processing", padx=10, pady=5)
processing_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Create a frame for orientation
orientation_frame = tk.Frame(processing_frame)
orientation_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

tk.Label(orientation_frame, text="Video Orientation:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
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
buttons_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

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
