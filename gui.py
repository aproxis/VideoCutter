import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json

# Default values remain the same
default_segment_duration = 6
default_input_folder = 'INPUT'
default_model_name = 'Model Name'
default_font_size = 90
default_watermark = 'Today is a\n Plus Day'
default_watermark_type = 'random'
default_watermark_speed = 50
default_depthflow = 0
default_time_limit = 600
default_font = 'Nexa Bold.otf'  # Default font

# Define watermark types
watermark_types = ['ccw', 'random']

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
var_font = tk.StringVar(root)
var_font.set(default_font)  # Set default font

# Get config files from folder
config_folder = os.path.join(os.path.dirname(__file__), 'config')
config_files = [file for file in os.listdir(config_folder) if file.endswith(".json")]

def start_process():
    # Get values from the entry fields
    model_name = entry_model_name.get()
    watermark = text_watermark.get("1.0", tk.END).strip()
    watermark_type = var_watermark_type.get()
    watermark_speed = entry_watermark_speed.get()
    manual_font_size = entry_font_size.get()
    segment_duration = entry_segment_duration.get()
    input_folder = entry_input_folder.get()
    depthflow_tf = var_depthflow.get()
    time_limit = entry_time_limit.get()
    video_orientation = var_video_orientation.get()
    blur_checkbox = var_add_blur.get()

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
        font_size = int(manual_font_size)  # Use manual input if provided
    else:
        font_size = int(entry_calculated_font_size.get())  # Use calculated font size if manual is empty

    # Get selected font
    selected_font = var_font.get()
    
    # Construct the command with the arguments
    command = [
        'python3', 'cutter.py',
        '--n', model_name,
        '--w', watermark,
        '--wt', watermark_type,
        '--ws', watermark_speed,
        '--f', str(font_size),
        '--d', str(segment_duration),
        '--tl', str(time_limit),
        '--z', str(depthflow),
        '--i', input_folder,
        '--o', video_orientation,  # Add video orientation to command
        '--b', str(blur),
        '--font', selected_font  # Add font parameter
    ]

    print(command)
    subprocess.run(command)

def update_font_size(event):
    model_name = entry_model_name.get()
    length = len(model_name)
    if length <= 10:
        calculated_font_size = 90
    elif 11 <= length <= 14:
        calculated_font_size = 80
    elif 15 <= length <= 18:
        calculated_font_size = 70
    else:
        calculated_font_size = 65
    entry_calculated_font_size.config(state=tk.NORMAL)
    entry_calculated_font_size.delete(0, tk.END)
    entry_calculated_font_size.insert(0, calculated_font_size)
    entry_calculated_font_size.config(state=tk.DISABLED)

def create_default_config():
    default_config = {
        'model_name': default_model_name,
        'watermark': default_watermark,
        'watermark_type': default_watermark_type,
        'watermark_speed': default_watermark_speed,
        'font_size': default_font_size,
        'segment_duration': default_segment_duration,
        'input_folder': default_input_folder,
        'depthflow': default_depthflow,
        'time_limit': default_time_limit,
        'video_orientation': 'vertical',
        'blur': 0,
        'font': default_font
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
    entry_model_name.delete(0, tk.END)
    entry_model_name.insert(0, config['model_name'])
    text_watermark.delete("1.0", tk.END)
    text_watermark.insert("1.0", config['watermark'])
    entry_font_size.delete(0, tk.END)
    entry_font_size.insert(0, config['font_size'])
    entry_segment_duration.delete(0, tk.END)
    entry_segment_duration.insert(0, config['segment_duration'])
    entry_input_folder.delete(0, tk.END)
    entry_input_folder.insert(0, config['input_folder'])
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
        var_font.set(config['font'])
    else:
        # If the configured font is not available, use the first available font
        var_font.set(available_fonts[0] if available_fonts else default_font)

    # Calculate font size based on model name length
    model_name = config['model_name']
    length = len(model_name)
    if length <= 10:
        calculated_font_size = 90
    elif 11 <= length <= 14:
        calculated_font_size = 80
    elif 15 <= length <= 18:
        calculated_font_size = 70
    else:
        calculated_font_size = 65
    entry_calculated_font_size.config(state=tk.NORMAL)
    entry_calculated_font_size.delete(0, tk.END)
    entry_calculated_font_size.insert(0, calculated_font_size)
    entry_calculated_font_size.config(state=tk.DISABLED)

def save_config():
    config_file = os.path.join(config_folder, var_config.get())
    with open(config_file, 'w') as f:
        json.dump({
            'model_name': entry_model_name.get(),
            'watermark': text_watermark.get("1.0", tk.END).strip(),
            'watermark_type': var_watermark_type.get(),
            'watermark_speed': entry_watermark_speed.get(),
            'font_size': entry_font_size.get(),
            'segment_duration': entry_segment_duration.get(),
            'input_folder': entry_input_folder.get(),
            'depthflow': var_depthflow.get(),
            'time_limit': entry_time_limit.get(),
            'video_orientation': var_video_orientation.get(),
            'blur': var_add_blur.get(),
            'font': var_font.get()
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
            'model_name': entry_model_name.get(),
            'watermark': text_watermark.get("1.0", tk.END).strip(),
            'watermark_type': var_watermark_type.get(),
            'watermark_speed': entry_watermark_speed.get(),
            'font_size': entry_font_size.get(),
            'segment_duration': entry_segment_duration.get(),
            'input_folder': entry_input_folder.get(),
            'depthflow': var_depthflow.get(),
            'time_limit': entry_time_limit.get(),
            'video_orientation': var_video_orientation.get(),
            'blur': var_add_blur.get(),
            'font': var_font.get()
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

# Create GUI elements
tk.Label(root, text="Config:").grid(row=0, column=0, padx=10, pady=5)
config_menu = tk.OptionMenu(root, var_config, *config_files)
config_menu.grid(row=0, column=1, padx=10, pady=5)
update_config_menu()

# Create remaining GUI elements
tk.Label(root, text="Model Name:").grid(row=2, column=0, padx=10, pady=5)
entry_model_name = tk.Entry(root, width=30)
entry_model_name.insert(0, default_model_name)
entry_model_name.grid(row=2, column=1, padx=10, pady=5)
entry_model_name.bind("<KeyRelease>", update_font_size)  # Bind key release event

tk.Label(root, text="Watermark:").grid(row=3, column=0, padx=10, pady=5)
text_watermark = tk.Text(root, width=39, height=3)
text_watermark.insert("1.0", default_watermark)
text_watermark.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Watermark Speed:").grid(row=4, column=0, padx=10, pady=5)
entry_watermark_speed = tk.Entry(root, width=30)
entry_watermark_speed.insert(0, default_watermark_speed)
entry_watermark_speed.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Watermark Type:").grid(row=5, column=0, padx=10, pady=5)
entry_watermark_type = tk.OptionMenu(root, var_watermark_type, *watermark_types)
entry_watermark_type.config(width=10)
entry_watermark_type.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Calculated Font Size:").grid(row=6, column=0, padx=10, pady=5)
entry_calculated_font_size = tk.Entry(root, width=30, state=tk.DISABLED)
entry_calculated_font_size.grid(row=6, column=1, padx=10, pady=5)

tk.Label(root, text="Font Size:").grid(row=7, column=0, padx=10, pady=5)
entry_font_size = tk.Entry(root, width=30)
entry_font_size.insert(0, default_font_size)
entry_font_size.grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Segment Duration:").grid(row=8, column=0, padx=10, pady=5)
entry_segment_duration = tk.Entry(root, width=30)
entry_segment_duration.insert(0, default_segment_duration)
entry_segment_duration.grid(row=8, column=1, padx=10, pady=5)

tk.Label(root, text="Time Limit:").grid(row=9, column=0, padx=10, pady=5)
entry_time_limit = tk.Entry(root, width=30)
entry_time_limit.insert(0, default_time_limit)
entry_time_limit.grid(row=9, column=1, padx=10, pady=5)

tk.Label(root, text="Font:").grid(row=10, column=0, padx=10, pady=5)
entry_font = tk.OptionMenu(root, var_font, *available_fonts)
entry_font.config(width=20)
entry_font.grid(row=10, column=1, padx=10, pady=5)

tk.Label(root, text="Input Folder:").grid(row=11, column=0, padx=10, pady=5)
entry_input_folder = tk.Entry(root, width=30)
entry_input_folder.insert(0, default_input_folder)
entry_input_folder.grid(row=11, column=1, padx=10, pady=5)

tk.Label(root, text="Save as:").grid(row=12, column=0, padx=10, pady=5)
entry_new_filename = tk.Entry(root, width=30)
entry_new_filename.grid(row=12, column=1, padx=10, pady=5)

tk.Label(root, text="DepthFlow:").grid(row=13, column=0, padx=10, pady=5)
var_depthflow = tk.BooleanVar()
var_depthflow.set(False)
tk.Checkbutton(root, text="Depthflow", variable=var_depthflow).grid(row=13, column=1, padx=5, pady=5)

# Create a StringVar for video orientation
var_video_orientation = tk.StringVar(value='horizontal')  # Default to horizontal

# Add Radiobuttons for video orientation
tk.Radiobutton(root, text="Vertical", variable=var_video_orientation, value='vertical').grid(row=14, column=0, padx=5, pady=5)
tk.Radiobutton(root, text="Horizontal", variable=var_video_orientation, value='horizontal').grid(row=14, column=1, padx=5, pady=5)

# Create a BooleanVar for adding blur
var_add_blur = tk.BooleanVar()
var_add_blur.set(False)  # Default to not adding blur

# Add a Checkbutton for adding blur, initially hidden
blur_checkbox = tk.Checkbutton(root, text="Side Blur", variable=var_add_blur)
blur_checkbox.grid(row=15, column=1, padx=5, pady=5)

# Function to show/hide blur checkbox based on orientation
def toggle_blur_checkbox():
    if var_video_orientation.get() == 'horizontal':
        blur_checkbox.config(state=tk.NORMAL)
    else:
        blur_checkbox.config(state=tk.DISABLED)
        var_add_blur.set(False)  # Reset blur option if not horizontal

# Bind the radiobutton selection to the toggle function
var_video_orientation.trace('w', lambda *args: toggle_blur_checkbox())

# Create buttons
start_button = tk.Button(
    root,
    text="START",
    command=start_process,
    fg="green",
    highlightbackground="green"
)
start_button.grid(row=16, column=1, pady=20, padx=20)

save_button = tk.Button(
    root,
    text="Save",
    command=save_config,
    fg="green",
    highlightbackground="green"
)
save_button.grid(row=1, column=1, pady=5, padx=5)

save_new_button = tk.Button(
    root,
    text="Save New Config",
    command=save_new_config,
    fg="blue",
    highlightbackground="blue"
)
save_new_button.grid(row=15, column=1, pady=5, padx=5)

delete_button = tk.Button(
    root,
    text="Delete",
    command=delete_config,
    fg="red",
    highlightbackground="red"
)
delete_button.grid(row=1, column=0, pady=5, padx=5)

quit_button = tk.Button(
    root,
    text="EXIT",
    command=root.quit,
    bg="black",
    highlightbackground="black"
)
quit_button.grid(row=15, column=0, pady=20, padx=20)

# Load initial config
load_config()

# Start main loop
root.mainloop()
