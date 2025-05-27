import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import json
import glob
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io

# Import custom modules
from videocutter.main import run_pipeline_for_project, run_batch_pipeline
from videocutter.utils import gui_config_manager as gcm
from videocutter.gui.title_settings_frame import TitleSettingsFrame
from videocutter.gui.subtitle_settings_frame import SubtitleSettingsFrame
from videocutter.gui.overlay_effects_frame import OverlayEffectsFrame # New import for overlay effects
from videocutter.gui.main_settings_frame import MainSettingsFrame # New import for main settings
from videocutter.gui import gui_utils
from videocutter import config_manager


class VideoCutterGUI:
    """Main GUI class for Video Cutter application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.gui_elements = {}
        self._after_id = None
        
        self._setup_window()
        self._initialize_config()
        self._initialize_variables()
        self._create_interface()
        self._load_initial_config()
        
    def _setup_window(self):
        """Configure main window properties"""
        self.root.title("Video Cutter GUI")
        self.root.geometry("1160x850")
        
    def _initialize_config(self):
        """Initialize configuration and check for config files"""
        # Ensure gcm.config_files is up-to-date before checking
        gcm.config_files = [file for file in os.listdir(gcm.config_folder) if file.endswith(".json")]
        self.config_files = gcm.config_files
        
        if not self.config_files:
            messagebox.showwarning("Warning", "No configuration files found in the config directory. Creating default config.")
            default_config_file_name = gcm.create_default_config()
            # After creating, re-read config_files to include the new default
            gcm.config_files = [file for file in os.listdir(gcm.config_folder) if file.endswith(".json")]
            self.config_files = gcm.config_files # Update instance variable
            
    def _initialize_variables(self):
        """Initialize all Tkinter variables"""
        # Core variables
        self.gui_elements['var_config'] = tk.StringVar(self.root)
        self.gui_elements['root'] = self.root
        self.gui_elements['gui_utils'] = gui_utils # Add gui_utils to gui_elements
        
        # Removed _init_video_processing_variables(), _init_batch_variables()
        self._init_title_variables()
        
        # Global lists from config manager
        self._init_global_lists()
        
    def _init_title_variables(self):
        """Initialize title-related variables"""
        self.gui_elements['var_enable_title'] = tk.BooleanVar(value=gcm.enable_title if hasattr(gcm, 'enable_title') else False)
        self.gui_elements['var_title_text'] = tk.StringVar(self.root, value=gcm.title_text if hasattr(gcm, 'title_text') else "")
        self.gui_elements['var_title_font'] = tk.StringVar(self.root, value=gcm.title_font if hasattr(gcm, 'title_font') else "Arial")
        self.gui_elements['var_title_font_size'] = tk.IntVar(self.root, value=gcm.title_font_size if hasattr(gcm, 'title_font_size') else 48)
        self.gui_elements['var_title_fontcolor'] = tk.StringVar(self.root, value=gcm.title_font_color if hasattr(gcm, 'title_font_color') else "white")
        self.gui_elements['var_title_opacity'] = tk.DoubleVar(self.root, value=gcm.title_opacity if hasattr(gcm, 'title_opacity') else 1.0)
        self.gui_elements['var_title_position'] = tk.StringVar(self.root, value=gcm.title_position if hasattr(gcm, 'title_position') else "center")
        self.gui_elements['var_title_duration'] = tk.IntVar(self.root, value=gcm.title_duration if hasattr(gcm, 'title_duration') else 5)
        self.gui_elements['var_title_bg_color'] = tk.StringVar(self.root, value=gcm.title_bg_color if hasattr(gcm, 'title_bg_color') else "black")
        self.gui_elements['var_title_bg_opacity'] = tk.DoubleVar(self.root, value=gcm.title_bg_opacity if hasattr(gcm, 'title_bg_opacity') else 0.5)
        self.gui_elements['var_enable_title_background'] = tk.BooleanVar(value=gcm.enable_title_background if hasattr(gcm, 'enable_title_background') else False)
        self.gui_elements['var_title_background_color'] = tk.StringVar(self.root, value=gcm.title_background_color if hasattr(gcm, 'title_background_color') else "black")
        self.gui_elements['var_title_background_opacity'] = tk.DoubleVar(self.root, value=gcm.title_background_opacity if hasattr(gcm, 'title_background_opacity') else 0.5)
        
    def _init_global_lists(self):
        """Initialize global lists from config manager"""
        self.gui_elements['available_fonts'] = gcm.available_fonts
        self.gui_elements['font_colors'] = gcm.font_colors
        self.gui_elements['watermark_types'] = gcm.watermark_types
        self.gui_elements['SUPPORTED_BLEND_MODES'] = gcm.SUPPORTED_BLEND_MODES
        self.gui_elements['effect_files'] = gcm.effect_files
        self.gui_elements['subscribe_overlay_files'] = gcm.subscribe_overlay_files
        self.gui_elements['title_video_overlay_files'] = gcm.title_video_overlay_files
        self.gui_elements['config_folder'] = gcm.config_folder
        self.gui_elements['config_files'] = gcm.config_files
        self.gui_elements['fonts_dir'] = gcm.fonts_dir
        
    def _create_interface(self):
        """Create the main interface components"""
        self._create_top_controls()
        self._create_tabbed_interface()
        
    def _create_top_controls(self):
        """Create top control section with config and batch processing"""
        top_controls_frame = tk.Frame(self.root)
        top_controls_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        self._create_config_frame(top_controls_frame)

        # Add START and EXIT buttons at the top
        buttons_frame = tk.Frame(top_controls_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        start_button = tk.Button(
            buttons_frame,
            text="START",
            command=self.start_process,
            fg="green",
            highlightbackground="green",
            width=15,
            height=2
        )
        start_button.pack(side=tk.TOP, pady=2)

        quit_button = tk.Button(
            buttons_frame,
            text="EXIT",
            command=self.root.quit,
            bg="black",
            highlightbackground="black",
            width=15,
            height=2
        )
        quit_button.pack(side=tk.TOP, pady=2)
        
    def _create_config_frame(self, parent):
        """Create configuration management frame"""
        config_frame = tk.LabelFrame(parent, text="Configuration Management")
        config_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Config file selection
        tk.Label(config_frame, text="Config File:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        config_menu = tk.OptionMenu(config_frame, self.gui_elements['var_config'], 
                                   *self.gui_elements['config_files'], 
                                   command=lambda _: gcm.load_config(self.root, self.gui_elements['var_config'], self.gui_elements))
        config_menu.config(width=20)
        config_menu.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.gui_elements['config_menu'] = config_menu
        
        # Save as new entry
        tk.Label(config_frame, text="Save as New:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        entry_new_filename = tk.Entry(config_frame, width=22)
        entry_new_filename.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.gui_elements['entry_new_filename'] = entry_new_filename # Add to gui_elements
        
        # Config buttons
        self._create_config_buttons(config_frame)
        
    def _create_config_buttons(self, parent):
        """Create configuration management buttons"""
        buttons_subframe_config = tk.Frame(parent)
        buttons_subframe_config.grid(row=0, column=2, rowspan=2, padx=5, pady=2, sticky="ns")
        
        save_new_button = tk.Button(buttons_subframe_config, text="Save New", 
                                   command=lambda: gcm.save_new_config(self.gui_elements), fg="blue")
        save_new_button.pack(fill=tk.X, pady=1)
        
        save_button = tk.Button(buttons_subframe_config, text="Save Current", 
                               command=lambda: gcm.save_config(self.gui_elements), fg="green")
        save_button.pack(fill=tk.X, pady=1)
        
        delete_button = tk.Button(buttons_subframe_config, text="Delete Current", 
                                 command=lambda: gcm.delete_config(self.gui_elements), fg="red")
        delete_button.pack(fill=tk.X, pady=1)
        
    def _create_tabbed_interface(self):
        """Create the main tabbed interface"""
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create tabs
        tab_main_settings = MainSettingsFrame(notebook, self.gui_elements) # Instantiate MainSettingsFrame
        self.gui_elements['tab_main_settings_instance'] = tab_main_settings # Store instance
        tab_subtitles_new = SubtitleSettingsFrame(notebook, self.gui_elements) # Instantiate SubtitleSettingsFrame
        self.gui_elements['tab_subtitles_instance'] = tab_subtitles_new # Store instance
        tab_overlay_effects = OverlayEffectsFrame(notebook, self.gui_elements) # Instantiate OverlayEffectsFrame
        self.gui_elements['tab_overlay_effects_instance'] = tab_overlay_effects # Store instance
        tab_title_settings = TitleSettingsFrame(notebook, self.gui_elements)
        self.gui_elements['tab_title_settings_instance'] = tab_title_settings # Store instance
        
        # Add tabs to notebook
        notebook.add(tab_main_settings, text="Main Settings")
        notebook.add(tab_title_settings, text="Title Settings")
        notebook.add(tab_subtitles_new, text="Subtitles")
        notebook.add(tab_overlay_effects, text="Overlay Effects")
        
    # Event handlers and utility methods
    def _load_initial_config(self):
        """Load initial configuration"""
        if self.gui_elements['config_files']:
            self.gui_elements['var_config'].set(self.gui_elements['config_files'][0])
        else:
            self.gui_elements['var_config'].set("")
            
        gcm.update_config_menu(self.gui_elements['config_menu'], self.gui_elements['var_config'], self.gui_elements)
        gcm.load_config(self.root, self.gui_elements['var_config'], self.gui_elements)

        # Initialize control states after all widgets are created and packed
        self.gui_elements['tab_title_settings_instance'].toggle_title_controls() # Call through instance
        self.gui_elements['tab_subtitles_instance'].update_all_subtitle_controls() # Call through instance
        self.gui_elements['tab_overlay_effects_instance'].update_all_overlay_controls() # Call through instance
        # Initialize subtitle preview after all subtitle GUI elements are created
        gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))
        
    # Event handlers and utility methods
    def browse_batch_folder(self):
        """Browse for batch input folder"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.gui_elements['var_batch_input_folder'].set(folder_selected)
            self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].config(state=tk.DISABLED)
            self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].delete(0, tk.END)
            self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].insert(0, "BATCH MODE ACTIVE")
        else:
            if not self.gui_elements['var_batch_input_folder'].get():
                self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].config(state=tk.NORMAL)
                self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].delete(0, tk.END)
                self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].insert(0, gcm.input_folder)
                
    def clear_batch_folder(self):
        """Clear batch input folder selection"""
        self.gui_elements['var_batch_input_folder'].set("")
        self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].config(state=tk.NORMAL)
        self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].delete(0, tk.END)
        self.gui_elements['tab_main_settings_instance'].gui_elements['entry_input_folder'].insert(0, gcm.input_folder)
        
    def schedule_subtitle_preview_update(self):
        """Debounce mechanism for preview updates"""
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(200, self.update_subtitle_preview)  # 200ms delay
        
    def update_subtitle_preview(self):
        """Update subtitle preview (placeholder)"""
        # This would contain the actual preview update logic
        pass
        
    def _run_pipeline_in_thread(self, config_file_path, gui_settings, batch_folder_path, input_folder):
        """Helper function to run the pipeline in a separate thread"""
        try:
            if batch_folder_path and os.path.isdir(batch_folder_path):
                print(f"Starting BATCH processing for folder: {batch_folder_path}")
                run_batch_pipeline(
                    batch_root_folder=batch_folder_path,
                    global_config_path=config_file_path,
                    gui_settings=gui_settings
                )
                self.root.after(0, lambda: messagebox.showinfo("Success", "Batch video processing pipeline finished!"))
                
            elif input_folder and input_folder != "BATCH MODE ACTIVE":
                print(f"Starting SINGLE project processing for folder: {input_folder}")
                cfg_single_project = config_manager.load_config(
                    global_config_path=config_file_path,
                    project_folder_path=input_folder,
                    runtime_settings=gui_settings
                )
                
                if cfg_single_project.title == 'Default Model Name' or cfg_single_project.title == '':
                    cfg_single_project.title = os.path.basename(input_folder) if os.path.basename(input_folder) else "SingleProject"
                    
                run_pipeline_for_project(
                    project_name=cfg_single_project.title,
                    project_input_folder=input_folder,
                    cfg=cfg_single_project
                )
                self.root.after(0, lambda: messagebox.showerror("Input Error", "Please specify a valid Input Folder or Batch Input Folder."))
                return
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.root.after(0, lambda e_val=e, err_det=error_detail: messagebox.showerror("Pipeline Error", f"An error occurred: {e_val}\n\nDetails:\n{err_det}"))
            print(f"Pipeline execution error: {e}")
            print(f"Full traceback:\n{error_detail}")
            
    def _collect_gui_settings(self):
        """Collect all GUI settings into a dictionary"""
        # Collect all settings
        gui_settings = {
            # Main settings (from MainSettingsFrame)
            **self.gui_elements['tab_main_settings_instance'].collect_settings(),

            # Subtitle settings (now nested)
            'subtitles': {
                'enabled': self.gui_elements['var_generate_srt'].get(), # Renamed from generate_srt
                'max_line_width': self.gui_elements['entry_subtitle_max_width'].get(),
                'font_name': self.gui_elements['var_subtitle_font'].get(),
                'font_size': self.gui_elements['var_subtitle_fontsize'].get(),
                'font_color_hex': self.gui_elements['var_subtitle_fontcolor'].get(),
                'shadow_color_hex': self.gui_elements['var_subtitle_bgcolor'].get(), # Renamed from bgcolor
                'shadow_opacity': self.gui_elements['var_subtitle_bgopacity'].get(), # Renamed from bgopacity
                'position_ass': self.gui_elements['var_subtitle_position'].get(), # Renamed from position
                'outline_thickness': self.gui_elements['var_subtitle_outline'].get(), # Renamed from outline
                'outline_color_hex': self.gui_elements['var_subtitle_outlinecolor'].get(), # Renamed from outlinecolor
                'shadow_enabled': self.gui_elements['var_subtitle_shadow'].get(), # Renamed from shadow
                'format': self.gui_elements['var_subtitle_format'].get(), # New: Subtitle format
                'secondary_color_hex': self.gui_elements['var_subtitle_secondary_color'].get(),
                'bold': self.gui_elements['var_subtitle_bold'].get(),
                'italic': self.gui_elements['var_subtitle_italic'].get(),
                'underline': self.gui_elements['var_subtitle_underline'].get(),
                'strikeout': self.gui_elements['var_subtitle_strikeout'].get(),
                'scale_x': self.gui_elements['var_subtitle_scale_x'].get(),
                'scale_y': self.gui_elements['var_subtitle_scale_y'].get(),
                'spacing': self.gui_elements['var_subtitle_spacing'].get(),
                'angle': self.gui_elements['var_subtitle_angle'].get(),
                'border_style': self.gui_elements['var_subtitle_border_style'].get(),
                'shadow_distance': self.gui_elements['var_subtitle_shadow_distance'].get(),
                'margin_l': self.gui_elements['var_subtitle_margin_l'].get(),
                'margin_r': self.gui_elements['var_subtitle_margin_r'].get(),
                'margin_v': self.gui_elements['var_subtitle_margin_v'].get(),
                'encoding': self.gui_elements['var_subtitle_encoding'].get()
            },

            # Title settings
            'enable_title': self.gui_elements['var_enable_title'].get(),
            'title_text': self.gui_elements['var_title_text'].get(),
            'title_font': self.gui_elements['var_title_font'].get(),
            'title_font_size': self.gui_elements['var_title_font_size'].get(),
            'title_font_color': self.gui_elements['var_title_fontcolor'].get(),
            'title_position': self.gui_elements['var_title_position'].get(),
            'title_duration': self.gui_elements['var_title_duration'].get(),
            'title_bg_color': self.gui_elements['var_title_bg_color'].get(),
            'title_bg_opacity': self.gui_elements['var_title_bg_opacity'].get(),
            'enable_title_background': self.gui_elements['var_enable_title_background'].get(),

            # Overlay effects settings (from OverlayEffectsFrame)
            **self.gui_elements['tab_overlay_effects_instance'].collect_settings()
        }
        
        # Get title from title settings instance
        gui_settings['title'] = self.gui_elements['tab_title_settings_instance'].collect_settings()['title_text']
        
        return gui_settings
        
    def start_process(self):
        """Start the video processing pipeline"""
        gui_settings = self._collect_gui_settings()
        
        selected_config_file = self.gui_elements['var_config'].get()
        config_file_path = None
        
        if selected_config_file:
            config_file_path = os.path.join(self.gui_elements['config_folder'], selected_config_file)
            if not os.path.exists(config_file_path):
                messagebox.showerror("Error", f"Selected config file not found: {config_file_path}")
                return
                
        # Start the pipeline in a separate thread to keep the GUI responsive
        pipeline_thread = threading.Thread(target=self._run_pipeline_in_thread, args=(config_file_path, gui_settings, self.gui_elements['var_batch_input_folder'].get(), self.gui_elements['entry_input_folder'].get()))
        pipeline_thread.start()
        
    # Removed update_effect_opacity_value()
    # Removed update_effect_opacity_from_entry()
    # Removed toggle_subscribe_overlay_controls()
    # Removed toggle_watermark_controls()
    # Removed toggle_effect_overlay_controls()

# Main execution block
if __name__ == "__main__":
    app = VideoCutterGUI()
    app.root.mainloop()
