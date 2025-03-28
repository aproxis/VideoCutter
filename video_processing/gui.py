"""
GUI module for VideoCutter.

This module provides a graphical user interface for the VideoCutter application.
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json
import sys

from .config import VideoConfig


class VideoCutterGUI:
    """GUI for the VideoCutter application."""
    
    def __init__(self, root=None):
        """Initialize the GUI.
        
        Args:
            root: The tkinter root window. If None, a new one will be created.
        """
        # Default values
        self.default_segment_duration = 6
        self.default_input_folder = 'INPUT'
        self.default_model_name = 'Model Name'
        self.default_font_size = 90
        self.default_watermark = 'Today is a\n Plus Day'
        self.default_depthflow = 0
        self.default_time_limit = 600
        
        # Create the main window if not provided
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        
        self.root.title("Video Cutter GUI")
        
        # Get config files from folder
        self.config_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.config_files = [file for file in os.listdir(self.config_folder) if file.endswith(".json")]
        
        # Create StringVar for config selection
        self.var_config = tk.StringVar(self.root)
        
        # Check for config files
        if self.config_files:
            self.var_config.set(self.config_files[0])
        else:
            self.var_config.set("")
            messagebox.showwarning("Warning", "No configuration files found in the config directory.")
            default_config_file = self.create_default_config()
            self.config_files.append(default_config_file)
        
        # Create GUI elements
        self.create_gui_elements()
        
        # Load initial config
        self.load_config()
    
    def create_default_config(self):
        """Create a default configuration file.
        
        Returns:
            The filename of the created config file.
        """
        default_config = {
            'model_name': self.default_model_name,
            'watermark': self.default_watermark,
            'font_size': self.default_font_size,
            'segment_duration': self.default_segment_duration,
            'input_folder': self.default_input_folder,
            'depthflow': self.default_depthflow,
            'time_limit': self.default_time_limit,
            'video_orientation': 'vertical',
            'blur': 0
        }
        default_filename = "default_config.json"
        config_file = os.path.join(self.config_folder, default_filename)
        with open(config_file, 'w') as f:
            json.dump(default_config, f)
        messagebox.showinfo("Info", f"Default config created: {default_filename}")
        return default_filename
    
    def update_config_menu(self):
        """Update the config menu with the current list of config files."""
        menu = self.config_menu['menu']
        menu.delete(0, 'end')
        for filename in self.config_files:
            menu.add_command(label=filename, 
                            command=lambda f=filename: self.var_config.set(f) or self.load_config())
    
    def load_config(self):
        """Load the selected configuration file."""
        config_file = os.path.join(self.config_folder, self.var_config.get())
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.entry_model_name.delete(0, tk.END)
        self.entry_model_name.insert(0, config['model_name'])
        
        self.text_watermark.delete("1.0", tk.END)
        self.text_watermark.insert("1.0", config['watermark'])
        
        self.entry_font_size.delete(0, tk.END)
        self.entry_font_size.insert(0, config['font_size'])
        
        self.entry_segment_duration.delete(0, tk.END)
        self.entry_segment_duration.insert(0, config['segment_duration'])
        
        self.entry_input_folder.delete(0, tk.END)
        self.entry_input_folder.insert(0, config['input_folder'])
        
        self.var_depthflow.set(config['depthflow'])
        
        self.entry_time_limit.delete(0, tk.END)
        self.entry_time_limit.insert(0, config['time_limit'])
        
        self.var_video_orientation.set(config['video_orientation'])
        self.var_add_blur.set(config['blur'])
        
        # Update calculated font size
        self.update_font_size(None)
    
    def save_config(self):
        """Save the current configuration to the selected file."""
        config_file = os.path.join(self.config_folder, self.var_config.get())
        with open(config_file, 'w') as f:
            json.dump({
                'model_name': self.entry_model_name.get(),
                'watermark': self.text_watermark.get("1.0", tk.END).strip(),
                'font_size': self.entry_font_size.get(),
                'segment_duration': self.entry_segment_duration.get(),
                'input_folder': self.entry_input_folder.get(),
                'depthflow': self.var_depthflow.get(),
                'time_limit': self.entry_time_limit.get(),
                'video_orientation': self.var_video_orientation.get(),
                'blur': self.var_add_blur.get()
            }, f)
        messagebox.showinfo("Success", "Config saved successfully!")
    
    def save_new_config(self):
        """Save the current configuration to a new file."""
        new_filename = self.entry_new_filename.get()
        if not new_filename.endswith('.json'):
            new_filename += '.json'
        
        config_file = os.path.join(self.config_folder, new_filename)
        if os.path.exists(config_file):
            messagebox.showerror("Error", "File already exists. Please choose a different name.")
            return
        
        with open(config_file, 'w') as f:
            json.dump({
                'model_name': self.entry_model_name.get(),
                'watermark': self.text_watermark.get("1.0", tk.END).strip(),
                'font_size': self.entry_font_size.get(),
                'segment_duration': self.entry_segment_duration.get(),
                'input_folder': self.entry_input_folder.get(),
                'depthflow': self.var_depthflow.get(),
                'time_limit': self.entry_time_limit.get(),
                'video_orientation': self.var_video_orientation.get(),
                'blur': self.var_add_blur.get()
            }, f)
        
        messagebox.showinfo("Success", "New config saved successfully!")
        
        self.config_files = [file for file in os.listdir(self.config_folder) if file.endswith(".json")]
        self.var_config.set(new_filename)
        self.update_config_menu()
        self.load_config()
    
    def delete_config(self):
        """Delete the selected configuration file."""
        config_file = os.path.join(self.config_folder, self.var_config.get())
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this config?"):
            os.remove(config_file)
            messagebox.showinfo("Success", "Config deleted successfully!")
            
            self.config_files = [file for file in os.listdir(self.config_folder) if file.endswith(".json")]
            if self.config_files:
                self.var_config.set(self.config_files[0])
            else:
                self.var_config.set("")
                messagebox.showwarning("Warning", "No configuration files found in the config directory.")
            
            self.update_config_menu()
            self.load_config()
    
    def update_font_size(self, event):
        """Update the calculated font size based on the model name length.
        
        Args:
            event: The event that triggered this function.
        """
        model_name = self.entry_model_name.get()
        length = len(model_name)
        
        if length <= 10:
            calculated_font_size = 90
        elif 11 <= length <= 14:
            calculated_font_size = 80
        elif 15 <= length <= 18:
            calculated_font_size = 70
        else:
            calculated_font_size = 65
        
        self.entry_calculated_font_size.config(state=tk.NORMAL)
        self.entry_calculated_font_size.delete(0, tk.END)
        self.entry_calculated_font_size.insert(0, calculated_font_size)
        self.entry_calculated_font_size.config(state=tk.DISABLED)
    
    def toggle_blur_checkbox(self, *args):
        """Toggle the blur checkbox based on the video orientation."""
        if self.var_video_orientation.get() == 'horizontal':
            self.blur_checkbox.config(state=tk.NORMAL)
        else:
            self.blur_checkbox.config(state=tk.DISABLED)
            self.var_add_blur.set(False)  # Reset blur option if not horizontal
    
    def start_process(self):
        """Start the video processing process."""
        # Get values from the entry fields
        model_name = self.entry_model_name.get()
        watermark = self.text_watermark.get("1.0", tk.END).strip()
        manual_font_size = self.entry_font_size.get()
        segment_duration = self.entry_segment_duration.get()
        input_folder = self.entry_input_folder.get()
        depthflow_tf = self.var_depthflow.get()
        time_limit = self.entry_time_limit.get()
        video_orientation = self.var_video_orientation.get()
        blur_checkbox = self.var_add_blur.get()
        
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
            font_size = int(self.entry_calculated_font_size.get())  # Use calculated font size if manual is empty
        
        # Construct the command with the arguments
        command = [
            'python3', 'main.py',
            '--n', model_name,
            '--w', watermark,
            '--f', str(font_size),
            '--d', str(segment_duration),
            '--tl', str(time_limit),
            '--z', str(depthflow),
            '--i', input_folder,
            '--o', video_orientation,
            '--b', str(blur)
        ]
        
        print(command)
        subprocess.run(command)
    
    def create_gui_elements(self):
        """Create the GUI elements."""
        # Config selection
        tk.Label(self.root, text="Config:").grid(row=0, column=0, padx=10, pady=5)
        self.config_menu = tk.OptionMenu(self.root, self.var_config, *self.config_files)
        self.config_menu.grid(row=0, column=1, padx=10, pady=5)
        self.update_config_menu()
        
        # Model name
        tk.Label(self.root, text="Model Name:").grid(row=2, column=0, padx=10, pady=5)
        self.entry_model_name = tk.Entry(self.root, width=30)
        self.entry_model_name.insert(0, self.default_model_name)
        self.entry_model_name.grid(row=2, column=1, padx=10, pady=5)
        self.entry_model_name.bind("<KeyRelease>", self.update_font_size)
        
        # Calculated font size
        tk.Label(self.root, text="Calculated Font Size:").grid(row=4, column=0, padx=10, pady=5)
        self.entry_calculated_font_size = tk.Entry(self.root, width=30, state=tk.DISABLED)
        self.entry_calculated_font_size.grid(row=4, column=1, padx=10, pady=5)
        
        # Watermark
        tk.Label(self.root, text="Watermark:").grid(row=3, column=0, padx=10, pady=5)
        self.text_watermark = tk.Text(self.root, width=39, height=3)
        self.text_watermark.insert("1.0", self.default_watermark)
        self.text_watermark.grid(row=3, column=1, padx=10, pady=5)
        
        # Font size
        tk.Label(self.root, text="Font Size:").grid(row=5, column=0, padx=10, pady=5)
        self.entry_font_size = tk.Entry(self.root, width=30)
        self.entry_font_size.insert(0, self.default_font_size)
        self.entry_font_size.grid(row=5, column=1, padx=10, pady=5)
        
        # Segment duration
        tk.Label(self.root, text="Segment Duration:").grid(row=6, column=0, padx=10, pady=5)
        self.entry_segment_duration = tk.Entry(self.root, width=30)
        self.entry_segment_duration.insert(0, self.default_segment_duration)
        self.entry_segment_duration.grid(row=6, column=1, padx=10, pady=5)
        
        # Time limit
        tk.Label(self.root, text="Time Limit:").grid(row=7, column=0, padx=10, pady=5)
        self.entry_time_limit = tk.Entry(self.root, width=30)
        self.entry_time_limit.insert(0, self.default_time_limit)
        self.entry_time_limit.grid(row=7, column=1, padx=10, pady=5)
        
        # Input folder
        tk.Label(self.root, text="Input Folder:").grid(row=8, column=0, padx=10, pady=5)
        self.entry_input_folder = tk.Entry(self.root, width=30)
        self.entry_input_folder.insert(0, self.default_input_folder)
        self.entry_input_folder.grid(row=8, column=1, padx=10, pady=5)
        
        # Save as
        tk.Label(self.root, text="Save as:").grid(row=10, column=0, padx=10, pady=5)
        self.entry_new_filename = tk.Entry(self.root, width=30)
        self.entry_new_filename.grid(row=10, column=1, padx=10, pady=5)
        
        # DepthFlow
        tk.Label(self.root, text="DepthFlow:").grid(row=9, column=0, padx=10, pady=5)
        self.var_depthflow = tk.BooleanVar()
        self.var_depthflow.set(False)
        tk.Checkbutton(self.root, text="Depthflow", variable=self.var_depthflow).grid(row=9, column=1, padx=5, pady=5)
        
        # Video orientation
        self.var_video_orientation = tk.StringVar(value='horizontal')  # Default to horizontal
        tk.Radiobutton(self.root, text="Vertical", variable=self.var_video_orientation, value='vertical').grid(row=11, column=0, padx=5, pady=5)
        tk.Radiobutton(self.root, text="Horizontal", variable=self.var_video_orientation, value='horizontal').grid(row=11, column=1, padx=5, pady=5)
        
        # Blur
        self.var_add_blur = tk.BooleanVar()
        self.var_add_blur.set(False)  # Default to not adding blur
        self.blur_checkbox = tk.Checkbutton(self.root, text="Side Blur", variable=self.var_add_blur)
        self.blur_checkbox.grid(row=12, column=1, padx=5, pady=5)
        
        # Bind the radiobutton selection to the toggle function
        self.var_video_orientation.trace('w', self.toggle_blur_checkbox)
        
        # Buttons
        self.start_button = tk.Button(
            self.root,
            text="START",
            command=self.start_process,
            fg="green",
            highlightbackground="green"
        )
        self.start_button.grid(row=14, column=1, pady=20, padx=20)
        
        self.save_button = tk.Button(
            self.root,
            text="Save",
            command=self.save_config,
            fg="green",
            highlightbackground="green"
        )
        self.save_button.grid(row=1, column=1, pady=5, padx=5)
        
        self.save_new_button = tk.Button(
            self.root,
            text="Save As",
            command=self.save_new_config,
            fg="blue",
            highlightbackground="blue"
        )
        self.save_new_button.grid(row=13, column=1, pady=5, padx=5)
        
        self.delete_button = tk.Button(
            self.root,
            text="Delete",
            command=self.delete_config,
            fg="red",
            highlightbackground="red"
        )
        self.delete_button.grid(row=1, column=0, pady=5, padx=5)
        
        self.quit_button = tk.Button(
            self.root,
            text="EXIT",
            command=self.root.quit,
            bg="black",
            highlightbackground="black"
        )
        self.quit_button.grid(row=14, column=0, pady=20, padx=20)
    
    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI."""
    gui = VideoCutterGUI()
    gui.run()


if __name__ == "__main__":
    main()
