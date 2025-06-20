import tkinter as tk
from tkinter import ttk
import logging

class LoggingSettingsFrame(ttk.Frame):
    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        self.logger = logging.getLogger(__name__)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # Logging Levels
        logging_levels_frame = ttk.LabelFrame(self, text="Module Logging Levels")
        logging_levels_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        logging_levels_frame.columnconfigure(1, weight=1) # Make level dropdown expand

        # Get module loggers from logger_config.py (assuming it's accessible)
        # This is a bit of a hack, ideally logger_config would expose this cleanly.
        # For now, we'll replicate the structure or assume a fixed set.
        # A better way would be to pass the module_loggers dict from gui.py
        # which gets it from gcm.DEFAULT_GUI_SETTINGS or a dedicated function.
class LoggingSettingsFrame(ttk.Frame):
    # Define the sections and their corresponding logger names as a class attribute
    log_sections = {
        "Root": "root",
        "Main Application": "main",
        "GUI": "gui",
        "Video Processor": "video_processor",
        "Audio Processor": "audio_processor",
        "Subtitle Generator": "subtitle_generator",
        "Depth Processor": "depth_processor",
        "Overlay Compositor": "overlay_compositor",
        "File Utilities": "file_utils",
        "Config Manager": "config_manager",
        "GUI Config Manager": "gui_config_manager",
        "Font Utilities": "font_utils",
        "Slideshow Generator": "slideshow_generator",
        "DepthFlow Settings Frame": "depthflow_settings_frame",
        "GUI Utilities": "gui_utils",
        "Main Settings Frame": "main_settings_frame",
        "Overlay Effects Frame": "overlay_effects_frame",
        "Subtitle Settings Frame": "subtitle_settings_frame",
        "Title Settings Frame": "title_settings_frame",
        "Punctuation Utilities": "punctuation_utils",
        "Subtitle Processing Utilities": "subtitle_processing_utils",
    }

    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        self.logger = logging.getLogger(__name__)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # Logging Levels
        logging_levels_frame = ttk.LabelFrame(self, text="Module Logging Levels")
        logging_levels_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        logging_levels_frame.columnconfigure(1, weight=1) # Make level dropdown expand

        self.level_options = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
        self.level_vars = {} # To store tk.StringVar for each logger

        row_idx = 0
        for display_name, section_name in self.log_sections.items():
            ttk.Label(logging_levels_frame, text=f"{display_name}:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            var_name = f"var_logging_{section_name}"
            # Initialize with current config value or default to INFO
            initial_level = self.gui_elements.get(var_name, tk.StringVar(self, value="INFO")).get()
            
            self.level_vars[section_name] = tk.StringVar(self, value=initial_level)
            
            level_dropdown = ttk.Combobox(
                logging_levels_frame,
                textvariable=self.level_vars[section_name],
                values=self.level_options,
                state="readonly"
            )
            level_dropdown.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
            
            # Store the Tkinter variable in gui_elements for saving/loading
            self.gui_elements[var_name] = self.level_vars[section_name]

            row_idx += 1
        
        # Debug Logging Enabled Checkbox
        ttk.Checkbutton(
            self,
            text="Enable Debug Logging (Overrides other settings to DEBUG)",
            variable=self.gui_elements['var_debug_logging_enabled'],
            command=self._on_debug_logging_toggle
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="w")

    def _on_debug_logging_toggle(self):
        # When debug logging is toggled, update the logging setup immediately
        # This will be handled by the main GUI's start_process or a dedicated update function
        # For now, just log the state.
        self.logger.info(f"Debug logging toggled to: {self.gui_elements['var_debug_logging_enabled'].get()}")

    def collect_settings(self):
        """Collects logging settings from the GUI elements."""
        settings = {}
        for section_name in self.log_sections.values():
            settings[section_name] = self.level_vars[section_name].get()
        return {"logging": settings}

    def load_settings(self, config):
        """Loads logging settings into the GUI elements."""
        logging_config = config.get("logging", {})
        for section_name in self.log_sections.values():
            var_name = f"var_logging_{section_name}"
            level = logging_config.get(section_name, "INFO") # Default to INFO if not in config
            if var_name in self.gui_elements:
                self.gui_elements[var_name].set(level)
            else:
                self.logger.warning(f"Tkinter variable {var_name} not found in gui_elements during load_settings.")
        
        # Update debug logging checkbox
        if 'var_debug_logging_enabled' in self.gui_elements:
            self.gui_elements['var_debug_logging_enabled'].set(config.get('debug_logging_enabled', False))
