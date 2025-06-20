import tkinter as tk
from tkinter import ttk, filedialog # Added filedialog

# Import custom modules
from videocutter.utils import gui_config_manager as gcm
from videocutter.gui import gui_utils # Needed for toggle_blur_checkbox

class MainSettingsFrame(ttk.Frame):
    """
    A custom Tkinter Frame to encapsulate the main settings tab content.
    """
    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        
        self._initialize_variables()
        self._create_widgets()

    def _initialize_variables(self):
        """Initialize all Tkinter variables specific to main settings."""
        # These variables are now expected to be passed in via gui_elements from the main GUI
        self.gui_elements['var_add_blur'] = tk.BooleanVar(value=gcm.blur)
        self.gui_elements['var_depthflow'] = tk.BooleanVar(value=gcm.depthflow)
        self.gui_elements['var_batch_input_folder'] = tk.StringVar(self.gui_elements['root'], value=gcm.batch_input_folder)

    def _create_widgets(self):
        """Create the widgets for the main settings tab."""
        main_settings_content_frame = tk.Frame(self)
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

        # Folders Section (Left Column)
        folders_frame = tk.LabelFrame(left_column, text="Folders", padx=10, pady=5)
        folders_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        folders_frame.grid_columnconfigure(1, weight=1) # Allow entry to expand
        folders_frame.grid_columnconfigure(2, weight=0) # For buttons

        # Input Folder
        tk.Label(folders_frame, text="Input Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_input_folder = tk.Entry(folders_frame, width=30)
        self.gui_elements['entry_input_folder'] = entry_input_folder
        entry_input_folder.insert(0, gcm.input_folder)
        entry_input_folder.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        browse_input_button = tk.Button(folders_frame, text="Browse", command=self._browse_input_folder)
        browse_input_button.grid(row=0, column=2, padx=5, pady=5)

        # Template Folder
        tk.Label(folders_frame, text="Template Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_template_folder = tk.Entry(folders_frame, width=30)
        self.gui_elements['entry_template_folder'] = entry_template_folder
        entry_template_folder.insert(0, gcm.template_folder)
        entry_template_folder.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        browse_template_button = tk.Button(folders_frame, text="Browse", command=self._browse_template_folder)
        browse_template_button.grid(row=1, column=2, padx=5, pady=5)

        # Batch Input Folder (moved from separate frame)
        tk.Label(folders_frame, text="Batch Input Folder:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_batch_folder = tk.Entry(folders_frame, textvariable=self.gui_elements['var_batch_input_folder'], width=30)
        entry_batch_folder.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.gui_elements['entry_batch_folder'] = entry_batch_folder
        
        browse_batch_button = tk.Button(folders_frame, text="Browse", command=self._browse_batch_folder)
        browse_batch_button.grid(row=2, column=2, padx=5, pady=5)
        
        clear_batch_button = tk.Button(folders_frame, text="Clear Batch", command=self._clear_batch_folder)
        clear_batch_button.grid(row=3, column=2, padx=5, pady=5) # Placed below batch browse button

        # Video Duration Section (Left Column) - This frame's grid row needs to be updated
        duration_frame = tk.LabelFrame(left_column, text="Video Duration", padx=10, pady=5)
        duration_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew") # Updated row from 1 to 2
        duration_frame.grid_columnconfigure(1, weight=1) # Allow entry to expand

        tk.Label(duration_frame, text="Segment Duration:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_segment_duration = tk.Entry(duration_frame, textvariable=self.gui_elements['var_segment_duration'], width=30)
        self.gui_elements['entry_segment_duration'] = entry_segment_duration
        entry_segment_duration.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(duration_frame, text="MAX Length Limit (s):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_time_limit = tk.Entry(duration_frame, width=30)
        self.gui_elements['entry_time_limit'] = entry_time_limit
        entry_time_limit.insert(0, gcm.time_limit)
        entry_time_limit.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # New: Transition Duration
        tk.Label(duration_frame, text="Transition Duration (s):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_transition_duration = tk.Entry(duration_frame, textvariable=self.gui_elements['var_transition_duration'], width=30)
        entry_transition_duration.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.gui_elements['entry_transition_duration'] = entry_transition_duration # Add to gui_elements

        # New: FPS
        tk.Label(duration_frame, text="FPS:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        entry_fps = tk.Entry(duration_frame, textvariable=self.gui_elements['var_fps'], width=30)
        entry_fps.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.gui_elements['entry_fps'] = entry_fps # Add to gui_elements


        # Sound/Audio Section (Right Column)
        sound_frame = tk.LabelFrame(right_column, text="Audio Settings", padx=10, pady=5)
        sound_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        sound_frame.grid_columnconfigure(1, weight=1) # Allow entry to expand

        tk.Label(sound_frame, text="Voiceover Start Delay (s):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_voiceover_delay = tk.Entry(sound_frame, width=30)
        self.gui_elements['entry_voiceover_delay'] = entry_voiceover_delay
        entry_voiceover_delay.insert(0, gcm.voiceover_delay)
        entry_voiceover_delay.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Video Processing Section (Right Column)
        processing_frame = tk.LabelFrame(right_column, text="Video Processing", padx=10, pady=5)
        processing_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        processing_frame.grid_columnconfigure(0, weight=1) # Allow content to expand

        # Create a frame for orientation
        orientation_frame = tk.Frame(processing_frame)
        orientation_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        tk.Label(orientation_frame, text="Orientation:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(orientation_frame, text="Vertical", variable=self.gui_elements['var_video_orientation'], value='vertical').grid(row=0, column=1, padx=5, pady=5)
        tk.Radiobutton(orientation_frame, text="Horizontal", variable=self.gui_elements['var_video_orientation'], value='horizontal').grid(row=0, column=2, padx=5, pady=5)

        # Create a frame for checkboxes
        checkbox_frame = tk.Frame(processing_frame)
        checkbox_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        blur_checkbox = tk.Checkbutton(checkbox_frame, text="Side Blur", variable=self.gui_elements['var_add_blur'])
        self.gui_elements['blur_checkbox'] = blur_checkbox
        blur_checkbox.grid(row=0, column=0, padx=5, pady=5)


        # The blur checkbox should always be available, regardless of orientation.
        # No specific toggle function needed here.
        self.gui_elements['blur_checkbox'].config(state=tk.NORMAL)

    def collect_settings(self):
        """Collect all settings from this frame into a dictionary."""
        settings = {
            'segment_duration': self.gui_elements['var_segment_duration'].get(),
            'input_folder': self.gui_elements['entry_input_folder'].get(),
            'template_folder': self.gui_elements['entry_template_folder'].get(),
            'depthflow': self.gui_elements['var_depthflow'].get(),
            'time_limit': self.gui_elements['entry_time_limit'].get(),
            'transition_duration': self.gui_elements['var_transition_duration'].get(), # New
            'fps': self.gui_elements['var_fps'].get(), # New
            'video_orientation': self.gui_elements['var_video_orientation'].get(),
            'blur': self.gui_elements['var_add_blur'].get(),
            'vo_delay': self.gui_elements['entry_voiceover_delay'].get(),
            'batch_input_folder': self.gui_elements['var_batch_input_folder'].get(), # Added batch input folder
        }
        return settings

    def _browse_batch_folder(self):
        """Browse for batch input folder (local to MainSettingsFrame)"""
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
                
    def _clear_batch_folder(self):
        """Clear batch input folder selection (local to MainSettingsFrame)"""
        self.gui_elements['var_batch_input_folder'].set("")
        self.gui_elements['entry_input_folder'].config(state=tk.NORMAL)
        self.gui_elements['entry_input_folder'].delete(0, tk.END)
        self.gui_elements['entry_input_folder'].insert(0, gcm.input_folder)

    def _browse_input_folder(self):
        """Browse for input folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.gui_elements['entry_input_folder'].delete(0, tk.END)
            self.gui_elements['entry_input_folder'].insert(0, folder_selected)

    def _browse_template_folder(self):
        """Browse for template folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.gui_elements['entry_template_folder'].delete(0, tk.END)
            self.gui_elements['entry_template_folder'].insert(0, folder_selected)
