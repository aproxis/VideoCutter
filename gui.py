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
        self.config_files = gcm.config_files
        
        if not self.config_files:
            messagebox.showwarning("Warning", "No configuration files found in the config directory.")
            default_config_file = gcm.create_default_config()
            self.config_files.append(default_config_file)
            
    def _initialize_variables(self):
        """Initialize all Tkinter variables"""
        # Core variables
        self.gui_elements['var_config'] = tk.StringVar(self.root)
        self.gui_elements['root'] = self.root
        self.gui_elements['gui_utils'] = gui_utils # Add gui_utils to gui_elements
        
        # Video processing variables
        self._init_watermark_variables()
        self._init_overlay_variables()
        self._init_subtitle_variables()
        self._init_effect_variables()
        self._init_title_variables()
        self._init_batch_variables()
        
        # Global lists from config manager
        self._init_global_lists()
        
    def _init_watermark_variables(self):
        """Initialize watermark-related variables"""
        self.gui_elements['var_watermark_type'] = tk.StringVar(self.root, value=gcm.watermark_type)
        self.gui_elements['var_watermark_font'] = tk.StringVar(self.root, value=gcm.watermark_font)
        self.gui_elements['var_enable_watermark'] = tk.BooleanVar(value=gcm.enable_watermark)
        self.gui_elements['var_watermark_font_size'] = tk.IntVar(self.root, value=gcm.watermark_font_size)
        self.gui_elements['var_watermark_opacity'] = tk.DoubleVar(self.root, value=gcm.watermark_opacity)
        self.gui_elements['var_watermark_fontcolor'] = tk.StringVar(self.root, value=gcm.watermark_fontcolor)
        self.gui_elements['var_watermark_speed_intuitive'] = tk.IntVar(self.root, value=gcm.watermark_speed_intuitive)
        
        
    def _init_overlay_variables(self):
        """Initialize overlay-related variables"""
        self.gui_elements['var_enable_subscribe_overlay'] = tk.BooleanVar(value=gcm.enable_subscribe_overlay)
        self.gui_elements['var_subscribe_delay'] = tk.IntVar(self.root, value=gcm.subscribe_delay)
        self.gui_elements['var_enable_title_video_overlay'] = tk.BooleanVar(value=gcm.enable_title_video_overlay)
        self.gui_elements['var_title_video_overlay_file'] = tk.StringVar(self.root, value=gcm.title_video_overlay_file)
        self.gui_elements['var_title_video_overlay_delay'] = tk.IntVar(self.root, value=gcm.title_video_overlay_delay)
        self.gui_elements['var_title_video_chromakey_color'] = tk.StringVar(self.root, value=gcm.title_video_chromakey_color)
        self.gui_elements['var_title_video_chromakey_similarity'] = tk.DoubleVar(self.root, value=gcm.title_video_chromakey_similarity)
        self.gui_elements['var_title_video_chromakey_blend'] = tk.DoubleVar(self.root, value=gcm.title_video_chromakey_blend)
        self.gui_elements['var_subscribe_overlay_file'] = tk.StringVar(self.root, value="None")
        self.gui_elements['var_chromakey_color'] = tk.StringVar(self.root, value=gcm.chromakey_color)
        
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
        
    def _init_subtitle_variables(self):
        """Initialize subtitle-related variables"""
        self.gui_elements['var_generate_srt'] = tk.BooleanVar(value=gcm.generate_srt)
        
        # Default subtitle settings
        self.gui_elements['default_subtitle_font'] = gcm.subtitle_font
        self.gui_elements['default_subtitle_fontsize'] = gcm.subtitle_fontsize
        self.gui_elements['default_subtitle_fontcolor'] = gcm.subtitle_fontcolor
        self.gui_elements['default_subtitle_bgcolor'] = gcm.subtitle_bgcolor
        self.gui_elements['default_subtitle_bgopacity'] = gcm.subtitle_bgopacity
        self.gui_elements['default_subtitle_position'] = gcm.subtitle_position
        self.gui_elements['default_subtitle_outline'] = gcm.subtitle_outline
        self.gui_elements['default_subtitle_outlinecolor'] = gcm.subtitle_outlinecolor
        self.gui_elements['default_subtitle_shadow'] = gcm.subtitle_shadow
        
        # Create subtitle variables
        self.gui_elements['var_subtitle_font'] = tk.StringVar(self.root, value=gcm.subtitle_font)
        self.gui_elements['var_subtitle_fontsize'] = tk.IntVar(self.root, value=gcm.subtitle_fontsize)
        self.gui_elements['var_subtitle_fontcolor'] = tk.StringVar(self.root, value=gcm.subtitle_fontcolor)
        self.gui_elements['var_subtitle_bgcolor'] = tk.StringVar(self.root, value=gcm.subtitle_bgcolor)
        self.gui_elements['var_subtitle_bgopacity'] = tk.DoubleVar(self.root, value=gcm.subtitle_bgopacity)
        self.gui_elements['var_subtitle_position'] = tk.IntVar(self.root, value=gcm.subtitle_position)
        self.gui_elements['var_subtitle_outline'] = tk.DoubleVar(self.root, value=gcm.subtitle_outline)
        self.gui_elements['var_subtitle_outlinecolor'] = tk.StringVar(self.root, value=gcm.subtitle_outlinecolor)
        self.gui_elements['var_subtitle_shadow'] = tk.BooleanVar(self.root, value=gcm.subtitle_shadow)
        self.gui_elements['var_subtitle_format'] = tk.StringVar(self.root, value=gcm.subtitle_format) # New: Subtitle format
        
    def _init_effect_variables(self):
        """Initialize effect-related variables"""
        self.gui_elements['var_enable_effect_overlay'] = tk.BooleanVar(self.root, value=True)
        self.gui_elements['var_effect_overlay'] = tk.StringVar(self.root, value="None")
        self.gui_elements['var_effect_opacity'] = tk.DoubleVar(self.root, value=gcm.effect_opacity)
        self.gui_elements['var_effect_blend'] = tk.StringVar(self.root, value=gcm.effect_blend)
        
    def _init_batch_variables(self):
        """Initialize batch processing variables"""
        self.gui_elements['var_batch_input_folder'] = tk.StringVar(self.root)
        
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
        self._create_batch_frame(top_controls_frame)
        
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
        
    def _create_batch_frame(self, parent):
        """Create batch processing frame"""
        batch_frame = tk.LabelFrame(parent, text="Batch Processing")
        batch_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        tk.Label(batch_frame, text="Batch Input Folder:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        entry_batch_folder = tk.Entry(batch_frame, textvariable=self.gui_elements['var_batch_input_folder'], width=30)
        entry_batch_folder.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.gui_elements['entry_batch_folder'] = entry_batch_folder # Add to gui_elements
        
        browse_batch_button = tk.Button(batch_frame, text="Browse", command=self.browse_batch_folder)
        browse_batch_button.grid(row=0, column=2, padx=5, pady=2)
        
        clear_batch_button = tk.Button(batch_frame, text="Clear Batch", command=self.clear_batch_folder)
        clear_batch_button.grid(row=1, column=2, padx=5, pady=2)
        
    def _create_tabbed_interface(self):
        """Create the main tabbed interface"""
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create tabs
        tab_main_settings = ttk.Frame(notebook)
        tab_subtitles_new = ttk.Frame(notebook)
        tab_overlay_effects = ttk.Frame(notebook)
        tab_title_settings = TitleSettingsFrame(notebook, self.gui_elements)
        self.gui_elements['tab_title_settings_instance'] = tab_title_settings # Store instance
        
        # Add tabs to notebook
        notebook.add(tab_main_settings, text="Main Settings")
        notebook.add(tab_title_settings, text="Title Settings")
        notebook.add(tab_subtitles_new, text="Subtitles")
        notebook.add(tab_overlay_effects, text="Overlay Effects")
        
        self._setup_main_settings_tab(tab_main_settings)
        self._setup_subtitles_tab(tab_subtitles_new)
        self._setup_overlay_effects_tab(tab_overlay_effects)
        
    def _setup_main_settings_tab(self, tab):
        """Setup the main settings tab layout"""
        main_settings_content_frame = tk.Frame(tab)
        main_settings_content_frame.pack(fill="both", expand=True)
        
        main_settings_columns_frame = tk.Frame(main_settings_content_frame)
        main_settings_columns_frame.pack(fill="both", expand=True)
        
        # Left and right columns
        left_column = tk.Frame(main_settings_columns_frame)
        left_column.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        right_column = tk.Frame(main_settings_columns_frame)
        right_column.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Configure columns to expand
        main_settings_columns_frame.grid_columnconfigure(0, weight=1)
        main_settings_columns_frame.grid_columnconfigure(1, weight=1)


        # Folders Section
        folders_frame = tk.LabelFrame(right_column, text="Folders", padx=10, pady=5)
        folders_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        tk.Label(folders_frame, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_input_folder = tk.Entry(folders_frame, width=30)
        self.gui_elements['entry_input_folder'] = entry_input_folder # Add to gui_elements
        entry_input_folder.insert(0, gcm.input_folder)
        entry_input_folder.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(folders_frame, text="Template Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_template_folder = tk.Entry(folders_frame, width=30)
        self.gui_elements['entry_template_folder'] = entry_template_folder # Add to gui_elements
        entry_template_folder.insert(0, gcm.template_folder)
        entry_template_folder.grid(row=1, column=1, padx=10, pady=5)

        # Video Duration Section
        duration_frame = tk.LabelFrame(right_column, text="Video Duration", padx=10, pady=5)
        duration_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        tk.Label(duration_frame, text="Segment Duration:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_segment_duration = tk.Entry(duration_frame, width=30)
        self.gui_elements['entry_segment_duration'] = entry_segment_duration # Add to gui_elements
        entry_segment_duration.insert(0, gcm.segment_duration)
        entry_segment_duration.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(duration_frame, text="MAX Length Limit (s):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_time_limit = tk.Entry(duration_frame, width=30)
        self.gui_elements['entry_time_limit'] = entry_time_limit # Add to gui_elements
        entry_time_limit.insert(0, gcm.time_limit)
        entry_time_limit.grid(row=1, column=1, padx=10, pady=5)

        # Sound/Audio Section
        sound_frame = tk.LabelFrame(right_column, text="Audio Settings", padx=10, pady=5)
        sound_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        tk.Label(sound_frame, text="Voiceover Start Delay (s):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_voiceover_delay = tk.Entry(sound_frame, width=30)
        self.gui_elements['entry_voiceover_delay'] = entry_voiceover_delay # Add to gui_elements
        entry_voiceover_delay.insert(0, gcm.voiceover_delay)
        entry_voiceover_delay.grid(row=0, column=1, padx=10, pady=5)

        # Video Processing Section
        processing_frame = tk.LabelFrame(right_column, text="Video Processing", padx=10, pady=5)
        processing_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Create a frame for orientation
        orientation_frame = tk.Frame(processing_frame)
        orientation_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        tk.Label(orientation_frame, text="Orientation:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        # Create a StringVar for video orientation
        var_video_orientation = tk.StringVar(value=gcm.video_orientation)  # Default to horizontal
        self.gui_elements['var_video_orientation'] = var_video_orientation # Add to gui_elements
        tk.Radiobutton(orientation_frame, text="Vertical", variable=var_video_orientation, value='vertical').grid(row=0, column=1, padx=5, pady=5)
        tk.Radiobutton(orientation_frame, text="Horizontal", variable=var_video_orientation, value='horizontal').grid(row=0, column=2, padx=5, pady=5)

        # Create a frame for checkboxes
        checkbox_frame = tk.Frame(processing_frame)
        checkbox_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Create a BooleanVar for adding blur
        var_add_blur = tk.BooleanVar()
        self.gui_elements['var_add_blur'] = var_add_blur # Add to gui_elements
        var_add_blur.set(gcm.blur)  # Default to not adding blur
        blur_checkbox = tk.Checkbutton(checkbox_frame, text="Side Blur", variable=var_add_blur)
        self.gui_elements['blur_checkbox'] = blur_checkbox # Add to gui_elements
        blur_checkbox.grid(row=0, column=0, padx=5, pady=5)

        # DepthFlow checkbox
        var_depthflow = tk.BooleanVar()
        self.gui_elements['var_depthflow'] = var_depthflow # Add to gui_elements
        var_depthflow.set(gcm.depthflow)
        tk.Checkbutton(checkbox_frame, text="Depthflow", variable=var_depthflow).grid(row=0, column=1, padx=5, pady=5)

        # Function to show/hide blur checkbox based on orientation
        def toggle_blur_checkbox():
            if self.gui_elements['var_video_orientation'].get() == 'horizontal':
                self.gui_elements['blur_checkbox'].config(state=tk.NORMAL)
            else:
                self.gui_elements['blur_checkbox'].config(state=tk.DISABLED)
                self.gui_elements['var_add_blur'].set(False)  # Reset blur option if not horizontal

        # Bind the radiobutton selection to the toggle function
        self.gui_elements['var_video_orientation'].trace('w', lambda *args: toggle_blur_checkbox())

        # Initialize the toggle_blur_checkbox function
        toggle_blur_checkbox()

        # Add START and EXIT buttons at the bottom
        buttons_frame = tk.Frame(self.root)
        buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        start_button = tk.Button(
            buttons_frame,
            text="START",
            command=self.start_process,
            fg="green",
            highlightbackground="green",
            width=15,
            height=2
        )
        start_button.grid(row=0, column=1, pady=10, padx=20) # Adjusted column for centering

        quit_button = tk.Button(
            buttons_frame,
            text="EXIT",
            command=self.root.quit,
            bg="black",
            highlightbackground="black",
            width=15,
            height=2
        )
        quit_button.grid(row=0, column=0, pady=10, padx=20) # Adjusted column for centering

        # Configure column weights for centering
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)

    def _setup_subtitles_tab(self, tab):
        """Setup the subtitles tab layout"""
        subtitle_frame = tk.Frame(tab, padx=10, pady=10)
        subtitle_frame.pack(fill="both", expand=True)

        # Left column for settings
        subtitle_settings = tk.LabelFrame(subtitle_frame, text="Subtitle Settings", padx=10, pady=10)
        subtitle_settings.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Subtitle Format Selection
        tk.Label(subtitle_settings, text="Subtitle Format:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        subtitle_format_dropdown = ttk.Combobox(subtitle_settings, textvariable=self.gui_elements['var_subtitle_format'], values=['srt', 'ass'], width=10)
        self.gui_elements['subtitle_format_dropdown'] = subtitle_format_dropdown
        subtitle_format_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        subtitle_format_dropdown.set(self.gui_elements['var_subtitle_format'].get()) # Set initial value

        # Add Generate Subtitles checkbox to subtitle_settings
        tk.Checkbutton(subtitle_settings, text="Generate Subtitles", variable=self.gui_elements['var_generate_srt']).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Subtitle line max width
        tk.Label(subtitle_settings, text="Characters per line (max):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_subtitle_max_width = tk.Entry(subtitle_settings, width=10) # Adjusted width
        self.gui_elements['entry_subtitle_max_width'] = entry_subtitle_max_width # Add to gui_elements
        entry_subtitle_max_width.insert(0, gcm.subtitle_maxwidth)
        entry_subtitle_max_width.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Font settings
        tk.Label(subtitle_settings, text="Font:").grid(row=2, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        font_dropdown = ttk.Combobox(subtitle_settings, textvariable=self.gui_elements['var_subtitle_font'], values=self.gui_elements['available_fonts'], width=25)
        self.gui_elements['font_dropdown'] = font_dropdown # Add to gui_elements
        font_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5) # Adjusted row
        font_dropdown.bind("<<ComboboxSelected>>", lambda e: gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Font size with slider and numeric display
        font_size_frame = tk.Frame(subtitle_settings)
        font_size_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

        tk.Label(subtitle_settings, text="Font Size:").grid(row=3, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        font_size_slider = ttk.Scale(font_size_frame, from_=12, to=48, variable=self.gui_elements['var_subtitle_fontsize'], orient="horizontal")
        self.gui_elements['font_size_slider'] = font_size_slider # Add to gui_elements
        font_size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        font_size_slider.bind("<ButtonRelease-1>", lambda e: (gui_utils.update_slider_value(self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_value_entry']), gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))) # Use debounced update

        font_size_value_entry = tk.Entry(font_size_frame, width=4)
        self.gui_elements['font_size_value_entry'] = font_size_value_entry # Add to gui_elements
        font_size_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        font_size_value_entry.insert(0, str(self.gui_elements['var_subtitle_fontsize'].get()))
        font_size_value_entry.bind("<Return>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['font_size_value_entry'], self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_slider'], 12, 48, self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))
        font_size_value_entry.bind("<FocusOut>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['font_size_value_entry'], self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_slider'], 12, 48, self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(subtitle_settings, text="Text Color:").grid(row=4, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        text_color_entry = tk.Entry(subtitle_settings, textvariable=self.gui_elements['var_subtitle_fontcolor'], width=10)
        self.gui_elements['text_color_entry'] = text_color_entry # Add to gui_elements
        text_color_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5) # Adjusted row
        text_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Shadow checkbox
        shadow_frame = tk.Frame(subtitle_settings)
        shadow_frame.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5) # Adjusted row
        shadow_checkbox = tk.Checkbutton(shadow_frame, text="Enable Text Shadow", variable=self.gui_elements['var_subtitle_shadow'], command=lambda: gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update
        self.gui_elements['shadow_checkbox'] = shadow_checkbox # Add to gui_elements
        shadow_checkbox.pack(anchor="w")

        tk.Label(subtitle_settings, text="Shadow Color:").grid(row=6, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        bg_color_entry = tk.Entry(subtitle_settings, textvariable=self.gui_elements['var_subtitle_bgcolor'], width=10)
        self.gui_elements['bg_color_entry'] = bg_color_entry # Add to gui_elements
        bg_color_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5) # Adjusted row
        bg_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Background opacity with slider and numeric display
        bg_opacity_frame = tk.Frame(subtitle_settings)
        bg_opacity_frame.grid(row=7, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

        tk.Label(subtitle_settings, text="Shadow Opacity:").grid(row=7, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        bg_opacity_slider = ttk.Scale(bg_opacity_frame, from_=0, to=1, variable=self.gui_elements['var_subtitle_bgopacity'], orient="horizontal")
        self.gui_elements['bg_opacity_slider'] = bg_opacity_slider # Add to gui_elements
        bg_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        bg_opacity_slider.bind("<ButtonRelease-1>", lambda e: (gui_utils.update_slider_value(self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_value_entry']), gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))) # Use debounced update

        bg_opacity_value_entry = tk.Entry(bg_opacity_frame, width=4)
        self.gui_elements['bg_opacity_value_entry'] = bg_opacity_value_entry # Add to gui_elements
        bg_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        bg_opacity_value_entry.insert(0, str(self.gui_elements['var_subtitle_bgopacity'].get()))
        bg_opacity_value_entry.bind("<Return>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['bg_opacity_value_entry'], self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_slider'], 0, 1, self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))
        bg_opacity_value_entry.bind("<FocusOut>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['bg_opacity_value_entry'], self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_slider'], 0, 1, self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Outline thickness with slider and numeric display
        outline_frame = tk.Frame(subtitle_settings)
        outline_frame.grid(row=8, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

        tk.Label(subtitle_settings, text="Outline Thickness:").grid(row=8, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        outline_slider = ttk.Scale(outline_frame, from_=0, to=4, variable=self.gui_elements['var_subtitle_outline'], orient="horizontal")
        self.gui_elements['outline_slider'] = outline_slider # Add to gui_elements
        outline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        outline_slider.bind("<ButtonRelease-1>", lambda e: (gui_utils.update_slider_value(self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_value_entry']), gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))) # Use debounced update

        outline_value_entry = tk.Entry(outline_frame, width=4)
        self.gui_elements['outline_value_entry'] = outline_value_entry # Add to gui_elements
        outline_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        outline_value_entry.insert(0, str(self.gui_elements['var_subtitle_outline'].get()))
        outline_value_entry.bind("<Return>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['outline_value_entry'], self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_slider'], 0, 4, self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))
        outline_value_entry.bind("<FocusOut>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['outline_value_entry'], self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_slider'], 0, 4, self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(subtitle_settings, text="Outline Color:").grid(row=9, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        outline_color_entry = tk.Entry(subtitle_settings, textvariable=self.gui_elements['var_subtitle_outlinecolor'], width=10)
        self.gui_elements['outline_color_entry'] = outline_color_entry # Add to gui_elements
        outline_color_entry.grid(row=9, column=1, sticky="w", padx=5, pady=5) # Adjusted row
        outline_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Initialize shadow controls state
        self.toggle_shadow_controls()

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

        position_dropdown = ttk.Combobox(position_frame, textvariable=self.gui_elements['var_subtitle_position'], values=position_labels, width=25)
        self.gui_elements['position_dropdown'] = position_dropdown # Add to gui_elements
        position_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        position_dropdown.bind("<<ComboboxSelected>>", lambda e: (self.gui_elements['var_subtitle_position'].set(position_values[position_labels.index(position_dropdown.get())]), gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements))))
        # Set initial value for dropdown
        position_dropdown.set(positions[position_values.index(self.gui_elements['var_subtitle_position'].get())][1])

        # Right column for preview
        preview_frame = tk.LabelFrame(subtitle_frame, text="Preview", padx=10, pady=10)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.gui_elements['preview_frame'] = preview_frame # Add preview_frame to gui_elements
        
        # Preview label
        self.gui_elements['preview_label'] = tk.Label(preview_frame)
        self.gui_elements['preview_label'].pack(padx=10, pady=10)
            
        # Initialize preview
        gui_utils.schedule_subtitle_preview_update(self.root, lambda: gui_utils.update_subtitle_preview(self.gui_elements)) # Use debounced update

        # Configure grid weights
        subtitle_frame.grid_columnconfigure(0, weight=1)
        subtitle_frame.grid_columnconfigure(1, weight=1)

    def _setup_overlay_effects_tab(self, tab):
        """Setup the overlay effects tab layout"""
        overlay_effects_left_column = tk.Frame(tab)
        overlay_effects_left_column.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        overlay_effects_right_column = tk.Frame(tab)
        overlay_effects_right_column.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # Watermark Section
        watermark_frame = tk.LabelFrame(overlay_effects_right_column, text="Watermark", padx=10, pady=5)
        watermark_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

        # New checkbox for enabling/disabling watermark (first place)
        tk.Checkbutton(watermark_frame, text="Enable", variable=self.gui_elements['var_enable_watermark'], command=self.toggle_watermark_controls).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        tk.Label(watermark_frame, text="Text:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        text_watermark = tk.Text(watermark_frame, width=30, height=3)
        self.gui_elements['text_watermark'] = text_watermark # Add to gui_elements
        text_watermark.insert("1.0", gcm.watermark)
        text_watermark.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(watermark_frame, text="Font:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_font = tk.OptionMenu(watermark_frame, self.gui_elements['var_watermark_font'], *self.gui_elements['available_fonts'])
        self.gui_elements['entry_font'] = entry_font # Add to gui_elements
        entry_font.config(width=20)
        entry_font.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(watermark_frame, text="Font Size:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_watermark_font_size = tk.Entry(watermark_frame, textvariable=self.gui_elements['var_watermark_font_size'], width=30)
        self.gui_elements['entry_watermark_font_size'] = entry_watermark_font_size # Add to gui_elements
        entry_watermark_font_size.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(watermark_frame, text="Opacity:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        watermark_opacity_slider = ttk.Scale(watermark_frame, from_=0.0, to=1.0, variable=self.gui_elements['var_watermark_opacity'], orient="horizontal")
        self.gui_elements['watermark_opacity_slider'] = watermark_opacity_slider # Add to gui_elements
        watermark_opacity_slider.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(watermark_frame, text="Font Color:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        entry_watermark_fontcolor = tk.OptionMenu(watermark_frame, self.gui_elements['var_watermark_fontcolor'], *self.gui_elements['font_colors'])
        self.gui_elements['entry_watermark_fontcolor'] = entry_watermark_fontcolor # Add to gui_elements
        entry_watermark_fontcolor.config(width=10)
        entry_watermark_fontcolor.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(watermark_frame, text="Type:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        entry_watermark_type = tk.OptionMenu(watermark_frame, self.gui_elements['var_watermark_type'], *self.gui_elements['watermark_types'])
        self.gui_elements['entry_watermark_type'] = entry_watermark_type # Add to gui_elements
        entry_watermark_type.config(width=10)
        entry_watermark_type.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(watermark_frame, text="Speed (1=Slow, 10=Fast):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        watermark_speed_slider = ttk.Scale(watermark_frame, from_=1, to=10, variable=self.gui_elements['var_watermark_speed_intuitive'], orient="horizontal")
        self.gui_elements['watermark_speed_slider'] = watermark_speed_slider # Add to gui_elements
        watermark_speed_slider.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        # Effect Overlay Section
        effect_frame = tk.LabelFrame(overlay_effects_right_column, text="Effect Overlay", padx=10, pady=5)
        effect_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

        tk.Checkbutton(effect_frame, text="Enable Effect Overlay", variable=self.gui_elements['var_enable_effect_overlay'], command=self.toggle_effect_overlay_controls).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        tk.Label(effect_frame, text="Effect:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        effect_dropdown = ttk.Combobox(effect_frame, textvariable=self.gui_elements['var_effect_overlay'], values=self.gui_elements['effect_files'], width=25)
        self.gui_elements['effect_dropdown'] = effect_dropdown # Add to gui_elements
        effect_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(effect_frame, text="Blend Mode:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        blend_dropdown = ttk.Combobox(effect_frame, textvariable=self.gui_elements['var_effect_blend'], values=self.gui_elements['SUPPORTED_BLEND_MODES'], width=25)
        self.gui_elements['blend_dropdown'] = blend_dropdown # Add to gui_elements
        blend_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Opacity with slider and numeric display
        tk.Label(effect_frame, text="Opacity:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        effect_opacity_frame = tk.Frame(effect_frame)
        effect_opacity_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        effect_opacity_slider = ttk.Scale(effect_opacity_frame, from_=0, to=1, variable=self.gui_elements['var_effect_opacity'], orient="horizontal")
        self.gui_elements['effect_opacity_slider'] = effect_opacity_slider # Add to gui_elements
        effect_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        effect_opacity_slider.bind("<ButtonRelease-1>", self.update_effect_opacity_value)

        effect_opacity_value = tk.Entry(effect_opacity_frame, width=5)
        self.gui_elements['effect_opacity_value'] = effect_opacity_value # Add to gui_elements
        effect_opacity_value.pack(side=tk.RIGHT, padx=(5, 0))
        effect_opacity_value.insert(0, f"{self.gui_elements['var_effect_opacity'].get():.2f}")
        effect_opacity_value.bind("<Return>", self.update_effect_opacity_from_entry)
        effect_opacity_value.bind("<FocusOut>", self.update_effect_opacity_from_entry)

        # Subscribe Overlay Section
        subscribe_overlay_frame = tk.LabelFrame(overlay_effects_left_column, text="Subscribe Overlay", padx=10, pady=5)
        subscribe_overlay_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

        enable_subscribe_overlay_checkbox = tk.Checkbutton(subscribe_overlay_frame, text="Enable", variable=self.gui_elements['var_enable_subscribe_overlay'], command=self.toggle_subscribe_overlay_controls)
        self.gui_elements['enable_subscribe_overlay_checkbox'] = enable_subscribe_overlay_checkbox # Add to gui_elements
        enable_subscribe_overlay_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        tk.Label(subscribe_overlay_frame, text="Overlay File:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_subscribe_overlay_file = ttk.Combobox(subscribe_overlay_frame, textvariable=self.gui_elements['var_subscribe_overlay_file'], values=self.gui_elements['subscribe_overlay_files'], width=25)
        self.gui_elements['entry_subscribe_overlay_file'] = entry_subscribe_overlay_file # Add to gui_elements
        entry_subscribe_overlay_file.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        # Removed the bind as the command on the checkbox will handle the state update

        tk.Label(subscribe_overlay_frame, text="Appearance Delay (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_subscribe_delay = tk.Entry(subscribe_overlay_frame, textvariable=self.gui_elements['var_subscribe_delay'], width=30)
        self.gui_elements['entry_subscribe_delay'] = entry_subscribe_delay # Add to gui_elements
        entry_subscribe_delay.insert(0, gcm.subscribe_delay)
        entry_subscribe_delay.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(subscribe_overlay_frame, text="Chromakey Color:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_chromakey_color = tk.Entry(subscribe_overlay_frame, width=30, textvariable=self.gui_elements['var_chromakey_color'])
        self.gui_elements['entry_chromakey_color'] = entry_chromakey_color # Add to gui_elements
        entry_chromakey_color.insert(0, gcm.chromakey_color)
        entry_chromakey_color.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(subscribe_overlay_frame, text="Chromakey Similarity:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_chromakey_similarity = tk.Entry(subscribe_overlay_frame, width=30)
        self.gui_elements['entry_chromakey_similarity'] = entry_chromakey_similarity # Add to gui_elements
        entry_chromakey_similarity.insert(0, gcm.chromakey_similarity)
        entry_chromakey_similarity.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(subscribe_overlay_frame, text="Chromakey Blend:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        entry_chromakey_blend = tk.Entry(subscribe_overlay_frame, width=30)
        self.gui_elements['entry_chromakey_blend'] = entry_chromakey_blend # Add to gui_elements
        entry_chromakey_blend.insert(0, gcm.chromakey_blend)
        entry_chromakey_blend.grid(row=5, column=1, padx=10, pady=5)


    def _load_initial_config(self):
        """Load initial configuration"""
        if self.gui_elements['config_files']:
            self.gui_elements['var_config'].set(self.gui_elements['config_files'][0])
        else:
            self.gui_elements['var_config'].set("")
            
        gcm.update_config_menu(self.gui_elements['config_menu'], self.gui_elements['var_config'], self.gui_elements)
        gcm.load_config(self.root, self.gui_elements['var_config'], self.gui_elements)

        # Initialize control states after all widgets are created and packed
        self.toggle_shadow_controls()
        self.gui_elements['tab_title_settings_instance'].toggle_title_controls() # Call through instance
        self.toggle_subscribe_overlay_controls()
        self.toggle_watermark_controls()
        self.toggle_effect_overlay_controls()
        
    # Event handlers and utility methods
    def browse_batch_folder(self):
        """Browse for batch input folder"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.gui_elements['var_batch_input_folder'].set(folder_selected)
            self.gui_elements['entry_input_folder'].config(state=tk.DISABLED)
            self.gui_elements['entry_input_folder'].delete(0, tk.END)
            self.gui_elements['entry_input_folder'].insert(0, "BATCH MODE ACTIVE")
        else:
            if not self.gui_elements['var_batch_input_folder'].get():
                self.gui_elements['entry_input_folder'].config(state=tk.NORMAL)
                self.gui_elements['entry_input_folder'].delete(0, tk.END)
                self.gui_elements['entry_input_folder'].insert(0, gcm.input_folder)
                
    def clear_batch_folder(self):
        """Clear batch input folder selection"""
        self.gui_elements['var_batch_input_folder'].set("")
        self.gui_elements['entry_input_folder'].config(state=tk.NORMAL)
        self.gui_elements['entry_input_folder'].delete(0, tk.END)
        self.gui_elements['entry_input_folder'].insert(0, gcm.input_folder)
        
    def schedule_subtitle_preview_update(self):
        """Debounce mechanism for preview updates"""
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(200, self.update_subtitle_preview)  # 200ms delay
        
    def update_subtitle_preview(self):
        """Update subtitle preview (placeholder)"""
        # This would contain the actual preview update logic
        pass
        
    def toggle_shadow_controls(self, *args):
        """Toggle background color and opacity controls based on shadow checkbox"""
        if self.gui_elements['var_subtitle_shadow'].get():
            self.gui_elements['bg_color_entry'].config(state=tk.NORMAL)
            self.gui_elements['bg_opacity_slider'].config(state=tk.NORMAL)
            self.gui_elements['bg_opacity_value_entry'].config(state=tk.NORMAL)
        else:
            self.gui_elements['bg_color_entry'].config(state=tk.DISABLED)
            self.gui_elements['bg_opacity_slider'].config(state=tk.DISABLED)
            self.gui_elements['bg_opacity_value_entry'].config(state=tk.DISABLED)
            
        gui_utils.schedule_subtitle_preview_update(
            self.root, 
            lambda: gui_utils.update_subtitle_preview(self.gui_elements)
        )
        
    def toggle_subscribe_overlay_controls(self, *args):
        """Toggle subscribe overlay controls based on enable_subscribe_overlay checkbox"""
        state = tk.NORMAL if self.gui_elements['var_enable_subscribe_overlay'].get() else tk.DISABLED
        
        controls = [
            'entry_subscribe_overlay_file',
            'entry_subscribe_delay',
            'entry_chromakey_color',
            'entry_chromakey_similarity',
            'entry_chromakey_blend'
        ]
        
        for control in controls:
            if control in self.gui_elements:
                self.gui_elements[control].config(state=state)
                
    def toggle_watermark_controls(self, *args):
        """Toggle watermark controls based on enable_watermark checkbox"""
        state = tk.NORMAL if self.gui_elements['var_enable_watermark'].get() else tk.DISABLED
        
        controls = [
            'text_watermark',
            'entry_font',
            'entry_watermark_font_size',
            'watermark_opacity_slider',
            'entry_watermark_fontcolor',
            'entry_watermark_type',
            'watermark_speed_slider'
        ]
        
        for control in controls:
            if control in self.gui_elements:
                self.gui_elements[control].config(state=state)
                
    def toggle_effect_overlay_controls(self, *args):
        """Toggle effect overlay controls based on enable_effect_overlay checkbox"""
        state = tk.NORMAL if self.gui_elements['var_enable_effect_overlay'].get() else tk.DISABLED
        
        controls = [
            'effect_dropdown',
            'blend_dropdown',
            'effect_opacity_slider',
            'effect_opacity_value'
        ]
        
        for control in controls:
            if control in self.gui_elements:
                self.gui_elements[control].config(state=state)
                
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
                self.root.after(0, lambda: messagebox.showinfo("Success", "Single video processing pipeline finished!"))
                
            else:
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
        # Get values from entry fields
        title = self.gui_elements['entry_title'].get()
        watermark = self.gui_elements['text_watermark'].get("1.0", tk.END).rstrip('\n')
        watermark = watermark.replace('\n', '\\n')
        
        # Calculate watermark speed
        watermark_speed_intuitive = self.gui_elements['var_watermark_speed_intuitive'].get()
        watermark_speed = int(100 - (watermark_speed_intuitive - 1) * 9)
        
        # Collect all settings
        gui_settings = {
            'title': title,
            'watermark': watermark.replace('\\n', '\n'),
            'watermark_type': self.gui_elements['var_watermark_type'].get(),
            'watermark_speed': watermark_speed,
            'enable_watermark': self.gui_elements['var_enable_watermark'].get(),
            'watermark_font_size': self.gui_elements['var_watermark_font_size'].get(),
            'watermark_opacity': self.gui_elements['var_watermark_opacity'].get(),
            'watermark_fontcolor': self.gui_elements['var_watermark_fontcolor'].get(),
            'watermark_speed_intuitive': watermark_speed_intuitive,
            'segment_duration': self.gui_elements['entry_segment_duration'].get(),
            'input_folder': self.gui_elements['entry_input_folder'].get(),
            'template_folder': self.gui_elements['entry_template_folder'].get(),
            'depthflow': self.gui_elements['var_depthflow'].get(),
            'time_limit': self.gui_elements['entry_time_limit'].get(),
            'video_orientation': self.gui_elements['var_video_orientation'].get(),
            'blur': self.gui_elements['var_add_blur'].get(),
            'watermark_font': self.gui_elements['var_watermark_font'].get(),
            
            # Subscribe overlay settings
            'enable_subscribe_overlay': self.gui_elements['var_enable_subscribe_overlay'].get(),
            'subscribe_delay': self.gui_elements['var_subscribe_delay'].get(),
            'chromakey_color': self.gui_elements['var_chromakey_color'].get(),
            'chromakey_similarity': self.gui_elements['entry_chromakey_similarity'].get(),
            'chromakey_blend': self.gui_elements['entry_chromakey_blend'].get(),
            
            # Audio settings
            'vo_delay': self.gui_elements['entry_voiceover_delay'].get(),
            
            # Effect overlay settings
            'effect_overlay': None if self.gui_elements['var_effect_overlay'].get() == "None" else self.gui_elements['var_effect_overlay'].get(),
            'effect_opacity': self.gui_elements['var_effect_opacity'].get(),
            'effect_blend': self.gui_elements['var_effect_blend'].get(),
            'enable_effect_overlay': self.gui_elements['var_enable_effect_overlay'].get(),
            
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
                'format': self.gui_elements['var_subtitle_format'].get() # New: Subtitle format
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
            'title_bg_opacity': self.gui_elements['var_title_bg_opacity'].get()
        }
        
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
        
    def update_effect_opacity_value(self, *args):
        """Update effect opacity value display"""
        self.gui_elements['effect_opacity_value'].delete(0, tk.END)
        self.gui_elements['effect_opacity_value'].insert(0, f"{self.gui_elements['var_effect_opacity'].get():.2f}")

    def update_effect_opacity_from_entry(self, *args):
        """Update effect opacity from entry"""
        try:
            value = float(self.gui_elements['effect_opacity_value'].get())
            if 0 <= value <= 1:
                self.gui_elements['var_effect_opacity'].set(value)
        except ValueError:
            pass

# Main execution block
if __name__ == "__main__":
    app = VideoCutterGUI()
    app.root.mainloop()
