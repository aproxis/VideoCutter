**File: `videocutter/main.py`**

**Core Purpose and Logic:**
This script serves as the central orchestrator for the VideoCutter pipeline. It defines two main functions: `run_pipeline_for_project` and `run_batch_pipeline`.
- `run_pipeline_for_project`: Manages the end-to-end video processing workflow for a single project, coordinating various processing steps like initial media handling, video/image processing, DepthFlow (if enabled), slideshow generation, subtitle generation, audio processing, and final overlay composition. It handles file organization, temporary file management, and cleanup.
- `run_batch_pipeline`: Iterates through subfolders within a specified batch root folder, treating each subfolder as an independent project. For each project, it loads a consolidated configuration (merging global, project-specific, and runtime settings) and then calls `run_pipeline_for_project`.
The `if __name__ == "__main__":` block demonstrates how to run the pipeline for both single and batch projects, including creating dummy input structures for testing.

**Internal Dependencies:**
- `.config_manager`: `load_config` function for loading and merging configuration settings.
- `.utils.file_utils`: `setup_project_directories`, `find_files_by_extension`, `backup_original_file`, `limit_media_files_by_duration`.
- `.utils.font_utils`: Imported but not directly used in `main.py` (likely used by `subtitle_generator` or `overlay_compositor`).
- `.processing.video_processor`: `convert_to_horizontal_with_blur_bg`, `split_video_into_segments`, `clean_short_video_segments`, `get_video_duration`, `process_image_for_video`.
- `.processing.depth_processor`: `apply_depth_effects`.
- `.processing.slideshow_generator`: `generate_base_slideshow`.
- `.processing.audio_processor`: `process_audio`.
- `.processing.subtitle_generator`: `generate_subtitles_from_audio_file`.
- `.processing.overlay_compositor`: `apply_final_overlays`.

**External Dependencies:**
- `os`: For path manipulation, directory creation, file operations.
- `shutil`: For copying and removing files/directories.
- `datetime`: For timestamping directories and calculating processing times.
- `dotmap.DotMap`: For flexible access to configuration objects.
- `json`: For handling JSON configuration files (used in `if __name__ == "__main__":` block for dummy config).

**Inputs:**

**`run_pipeline_for_project` function:**
- `project_name` (str): A human-readable name for the current project.
- `project_input_folder` (str): The absolute path to the folder containing the raw media files for the current project.
- `cfg` (DotMap): The fully resolved configuration object for this project.

**`run_batch_pipeline` function:**
- `batch_root_folder` (str): The absolute path to the directory containing multiple project subfolders.
- `global_config_path` (str, optional): Path to a global configuration JSON file. Defaults to `None`.
- `gui_settings` (dict, optional): A dictionary of runtime settings, typically from the GUI, that override other configurations. Defaults to `None`.

**Files/Directories (read by the script or its dependencies):**
- Media files (videos: `.mp4`, `.mov`, `.avi`; images: `.jpg`, `.jpeg`, `.png`; audio: `.mp3`) from `project_input_folder`.
- `voiceover.mp3` (if present in `project_input_folder`).
- Project-specific configuration file (e.g., `_project_config.json`) within `project_input_folder`.
- Global configuration file (e.g., `config/default_config.json`) if `global_config_path` is provided.
- Template video files (e.g., `outro_vertical.mp4`, `outro_horizontal.mp4`) from `cfg.template_folder`.

**Outputs:**

**`run_pipeline_for_project` function:**
- Creates a timestamped directory within `project_input_folder/RESULT/` (e.g., `project_input_folder/RESULT/YYYY-MM-DD_HH-MM-SS/`).
- Creates a timestamped backup directory within `project_input_folder/SOURCE/` (e.g., `project_input_folder/SOURCE/YYYY-MM-DD_HH-MM-SS/`) where original media files are copied.
- Intermediate video files (e.g., `slideshow_base.mp4`, `slideshow_with_audio.mp4`) within the timestamped result directory.
- Subtitle files (e.g., `voiceover.srt` or `voiceover.ass`) within a `subs` subdirectory of the timestamped result directory.
- Final processed video file (e.g., `project_name_title_YYYY-MM-DD_HH-MM-SS.mp4`) in the timestamped result directory.
- Prints extensive progress and status messages to the console.

**`run_batch_pipeline` function:**
- Orchestrates the creation of outputs for multiple projects by calling `run_pipeline_for_project` for each.
- Prints batch processing start/end messages to the console.

**Temporary Files:**
- A `temp` directory is created at the project root (`VideoCutter/temp`) for temporary files, which is then cleaned up.
- Intermediate video files are created and then removed during cleanup.

---

**File: `videocutter/config_manager.py`**

**Core Purpose and Logic:**
This module is responsible for managing the application's configuration. It provides a `ConfigManager` class and a `load_config` function to handle the hierarchical loading and merging of configuration settings from multiple sources:
1.  **Global Default Configuration**: A base configuration file (e.g., `default_config.json`) that provides default values for all parameters.
2.  **Project-Specific Configuration**: A configuration file (e.g., `_project_config.json`) located within a specific project folder, which can override global defaults for that project.
3.  **Runtime Overrides**: A dictionary of settings, typically provided by the GUI or command-line arguments, that take the highest precedence and override any previously loaded settings.

The `ConfigManager` class uses `DotMap` to allow easy access to configuration parameters using dot notation (e.g., `cfg.video_orientation`). It also includes a `_apply_type_conversions_and_defaults` method to ensure that configuration values are cast to the correct data types (e.g., `int`, `float`, `bool`) and to apply default values if certain parameters are missing. A static method `_deep_merge_dicts` is used for recursively merging dictionaries, ensuring nested configurations are handled correctly.

**Internal Dependencies:**
- None directly within the `videocutter` package, but it's designed to be used by `videocutter/main.py` and potentially GUI components.

**External Dependencies:**
- `json`: For reading and parsing JSON configuration files.
- `os`: For path manipulation and checking file existence.
- `shutil`: Used in the `if __name__ == "__main__":` block for test cleanup.
- `dotmap.DotMap`: For providing dot notation access to configuration dictionaries.

**Inputs:**

**`ConfigManager` class constructor:**
- `global_default_config_path` (str, optional): Path to the global default configuration JSON file.
- `project_specific_config_path` (str, optional): Path to the project-specific configuration JSON file.
- `runtime_overrides` (dict, optional): A dictionary containing configuration settings that should override all others.

**`load_config` function:**
- `global_config_path` (str, optional): Path to the global default configuration JSON file. If `None`, it attempts to find `config/default_config.json` relative to the project root.
- `project_folder_path` (str, optional): Path to the project's root folder. The function will look for `_project_config.json` within this folder.
- `runtime_settings` (dict, optional): A dictionary of runtime overrides.
- `project_config_filename` (str, optional): The name of the project-specific configuration file (default: `_project_config.json`).

**Files (read by the script):**
- JSON files specified by `global_default_config_path` and `project_specific_config_path`.

**Outputs:**

**`ConfigManager` class constructor:**
- Initializes `self.config` as a `DotMap` object containing the merged and type-converted configuration.

**`load_config` function:**
- Returns a `DotMap` object representing the fully resolved configuration, merging global defaults, project-specific settings, and runtime overrides, with appropriate type conversions applied.
- Prints informational messages about which configuration files are loaded and warnings if files are not found or cannot be loaded.

---

**File: `videocutter/utils/gui_config_manager.py`**

**Core Purpose and Logic:**
This module centralizes default values for all GUI elements and provides functions for managing configuration files directly from the GUI. It acts as an intermediary between the GUI and the underlying configuration files (JSON).
-   **Default Values**: Defines a comprehensive set of default values for all configurable parameters used in the GUI. These are used when no specific configuration is loaded or when a parameter is missing from a loaded config.
-   **File System Interaction**: Manages the `config/` directory, including listing existing configuration files, creating a default configuration file, and saving/loading/deleting user-defined configurations.
-   **GUI Synchronization**: Provides functions (`load_config`, `save_config`, `save_new_config`, `delete_config`, `update_config_menu`) that interact with Tkinter widgets to:
    -   Load settings from a selected JSON file into the GUI elements.
    -   Save current GUI settings to an existing or new JSON file.
    -   Update the dropdown menu of available configuration files.
    -   Handle user confirmations and error messages via `tkinter.messagebox`.
-   **Dynamic Content**: Dynamically discovers available fonts from the `fonts/` directory and overlay video files from `effects/overlays`, `effects/subscribe`, and `effects/title` directories to populate GUI dropdowns.
-   **Calculated Defaults**: Includes logic to calculate a suggested title font size based on the length of the title text.

**Internal Dependencies:**
-   `videocutter/gui/gui_utils.py`: It calls `update_slider_value` and `schedule_subtitle_preview_update` from `gui_utils` via the `gui_elements` dictionary.

**External Dependencies:**
-   `tkinter` (as `tk`): For GUI elements and message boxes.
-   `tkinter.messagebox`: For displaying informational, error, and confirmation dialogs.
-   `tkinter.ttk`: For themed Tkinter widgets (though not explicitly used with `ttk.` prefix in the provided code, it's imported).
-   `os`: For path manipulation, directory creation, and file system operations (listing, checking existence, deleting).
-   `json`: For reading from and writing to JSON configuration files.
-   `glob`: Imported but not explicitly used in the provided code snippet.

**Inputs:**

**Functions (`load_config`, `save_config`, `save_new_config`, `delete_config`, `update_config_menu`):**
-   `gui_elements` (dict): A dictionary containing references to various Tkinter widgets and `tk.Variable` objects from the main GUI. This allows the functions to directly read from and write to the GUI's state. It also contains references to `root` widget and `gui_utils` module.
-   `root_widget` (Tkinter root window): The main Tkinter window, used by `load_config` for scheduling preview updates.
-   `var_config_str` (tk.StringVar): A Tkinter string variable holding the name of the currently selected configuration file.
-   `config_menu_widget` (Tkinter OptionMenu): The widget representing the configuration file dropdown menu.

**Files/Directories (read by the script):**
-   JSON files from the `config/` directory.
-   Font files (`.ttf`, `.otf`) from the `fonts/` directory.
-   Video files (`.mp4`) from `effects/overlays`, `effects/subscribe`, and `effects/title` directories.

**Outputs:**

**Functions (`load_config`, `save_config`, `save_new_config`, `delete_config`):**
-   **GUI State Modification**: Updates the values of various Tkinter widgets (Entry, Text, StringVar, IntVar, DoubleVar) to reflect loaded or saved configuration.
-   **File System Modification**:
    -   `create_default_config`: Creates `default_config.json` in the `config/` directory.
    -   `save_config`: Writes the current GUI settings to an existing JSON file in `config/`.
    -   `save_new_config`: Writes the current GUI settings to a new JSON file in `config/`.
    -   `delete_config`: Deletes a specified JSON file from `config/`.
-   **User Feedback**: Displays `messagebox` pop-ups for success, error, or confirmation messages.
-   **Console Output**: Prints warnings if fonts are not found.

**Global Variables Modified:**
-   `config_files`: Updated list of JSON files in the `config/` directory.

---

**File: `gui.py`**

**Core Purpose and Logic:**
This script defines the main graphical user interface (GUI) for the VideoCutter application using Tkinter. The `VideoCutterGUI` class encapsulates the entire GUI logic, including window setup, variable initialization, interface creation (tabs, controls, buttons), and event handling.
-   **Initialization**: Sets up the main Tkinter window, initializes `tk.StringVar`, `tk.IntVar`, `tk.DoubleVar`, and `tk.BooleanVar` for all configurable parameters, and loads initial configuration settings.
-   **Layout Management**: Organizes the GUI into a tabbed interface (`ttk.Notebook`) with "Main Settings", "Title Settings", "Subtitles", "Overlay Effects", and "DepthFlow" tabs. Each tab contains various input widgets (Entry, Text, OptionMenu, Combobox, Scale, Checkbutton, Radiobutton) for user input.
-   **Configuration Management**: Integrates with `gui_config_manager.py` to load, save, and delete configuration presets, and to update the config file dropdown.
-   **Input Handling**: Collects all user-defined settings from the GUI widgets into a dictionary (`_collect_gui_settings`) by delegating to the `collect_settings` method of each individual frame instance.
-   **Process Orchestration**: Triggers the video processing pipeline (`run_pipeline_for_project` or `run_batch_pipeline` from `videocutter.main`) in a separate thread to keep the GUI responsive during long-running operations.
-   **Dynamic UI**: Includes logic to enable/disable related controls based on checkbox states (e.g., watermark, subscribe overlay, effect overlay, subtitle shadow, title settings). It also dynamically updates the subtitle preview based on changes to subtitle parameters.
-   **File Browsing**: Allows users to browse for batch input folders.

**Internal Dependencies:**
-   `videocutter.main`: `run_pipeline_for_project`, `run_batch_pipeline` (for starting the processing pipeline).
-   `videocutter.utils.gui_config_manager` (as `gcm`): Provides default values, functions for loading/saving/deleting configs, and lists of available fonts/overlays.
-   `videocutter.gui.title_settings_frame.TitleSettingsFrame`: A custom Tkinter frame for title-specific settings.
-   `videocutter.gui.subtitle_settings_frame.SubtitleSettingsFrame`: A custom Tkinter frame for subtitle-specific settings.
-   `videocutter.gui.overlay_effects_frame.OverlayEffectsFrame`: A custom Tkinter frame for overlay effects settings.
-   `videocutter.gui.main_settings_frame.MainSettingsFrame`: A custom Tkinter frame for main settings.
-   `videocutter.gui.depthflow_settings_frame.DepthflowSettingsFrame`: A custom Tkinter frame for DepthFlow settings.
-   `videocutter.gui.gui_utils`: Provides utility functions like `update_slider_value`, `update_slider_from_entry`, `schedule_subtitle_preview_update`, `update_subtitle_preview`.
-   `videocutter.config_manager`: `load_config` (used when starting the pipeline to load the full config).

**External Dependencies:**
-   `tkinter` (as `tk`): Core GUI toolkit.
-   `tkinter.messagebox`: For displaying pop-up messages (warnings, errors, success).
-   `tkinter.ttk`: For themed Tkinter widgets (Notebook, Scale, Combobox).
-   `tkinter.filedialog`: For opening file/folder selection dialogs.
-   `os`: For path manipulation and checking file existence.
-   `json`: For handling JSON data (though primarily handled by `gcm` and `config_manager`).
-   `glob`: Imported but not directly used in the provided code.
-   `threading`: For running the video processing pipeline in a separate thread.
-   `PIL` (Pillow): `Image`, `ImageTk`, `ImageDraw`, `ImageFont` (for subtitle preview rendering).
-   `io`: For in-memory image handling (used by PIL).

**Inputs:**
-   User interactions with GUI widgets (typing in entries, selecting from dropdowns, moving sliders, checking checkboxes, clicking buttons).
-   Configuration files (JSON) loaded via `gui_config_manager`.
-   Media files and template files (indirectly, as their paths are configured via the GUI).

**Outputs:**
-   **GUI Display**: Renders the entire application interface.
-   **Configuration Files**: Saves user-modified settings to JSON files via `gui_config_manager`.
-   **Video Processing**: Initiates the video processing pipeline by calling functions in `videocutter.main`.
-   **User Feedback**: Displays messages to the user via `messagebox` (success, error, warnings).
-   **Console Output**: Prints status messages and error tracebacks.
-   **Subtitle Preview**: Renders a visual preview of subtitles within the GUI.

---

**File: `videocutter/gui/gui_utils.py`**

**Core Purpose and Logic:**
This module provides utility functions specifically designed to support the Tkinter GUI of the VideoCutter application, particularly for managing slider-entry synchronization and rendering the subtitle preview.
-   **Slider-Entry Synchronization**: Functions `update_slider_value` and `update_slider_from_entry` ensure that a Tkinter `Scale` (slider) and an `Entry` widget (text input) always display the same value, allowing users to adjust parameters either by dragging the slider or typing a number.
-   **Subtitle Preview Rendering**: The `update_subtitle_preview` function is the core of this module. It dynamically generates a visual preview of how subtitles will appear based on the current GUI settings. It uses PIL/Pillow to:
    -   Create a blank image canvas.
    -   Load the selected font (with fallbacks if the font is not found or invalid).
    -   Draw sample text.
    -   Apply outline and shadow effects by drawing the text multiple times with offsets and using alpha compositing for layering.
    -   Convert the PIL image to a Tkinter `PhotoImage` and update a `tk.Label` in the GUI to display the preview.
-   **Debouncing**: The `schedule_subtitle_preview_update` function is intended for debouncing updates to the subtitle preview, preventing excessive redraws during rapid user input.

**Internal Dependencies:**
-   None directly within the `videocutter` package, but it relies on `gui.py` to provide the `gui_elements` dictionary containing references to Tkinter variables and widgets.

**External Dependencies:**
-   `tkinter` (as `tk`): For Tkinter widgets and variables.
-   `tkinter.ttk`: For themed Tkinter widgets (specifically `ttk.Scale`).
-   `PIL` (Pillow): `Image`, `ImageTk`, `ImageDraw`, `ImageFont` for image manipulation and text rendering.
-   `os`: For path manipulation, specifically for constructing font file paths.

**Inputs:**

**`update_slider_value` function:**
-   `var` (tk.Variable): A Tkinter variable (e.g., `tk.IntVar`, `tk.DoubleVar`) holding the slider's value.
-   `entry` (tk.Entry): The Tkinter Entry widget to update.

**`update_slider_from_entry` function:**
-   `entry` (tk.Entry): The Tkinter Entry widget from which to read the value.
-   `var` (tk.Variable): The Tkinter variable to update.
-   `slider` (ttk.Scale): The Tkinter Scale widget to synchronize.
-   `min_val` (int/float): Minimum allowed value for the entry.
-   `max_val` (int/float): Maximum allowed value for the entry.
-   `root` (tk.Tk): The main Tkinter root window (for scheduling updates).
-   `update_function` (callable): The function to call after updating the slider/entry (e.g., `update_subtitle_preview`).

**`update_subtitle_preview` function:**
-   `gui_elements` (dict): A dictionary containing references to various Tkinter variables (`var_subtitle_font`, `var_subtitle_fontsize`, `var_subtitle_fontcolor`, etc.), widgets (`preview_label`, `preview_frame`), and other necessary data (`fonts_dir`, `var_video_orientation`).

**Outputs:**

**`update_slider_value` and `update_slider_from_entry` functions:**
-   Modifies the text in the `Entry` widget or the value of the `tk.Variable` and `ttk.Scale` widget.

**`update_subtitle_preview` function:**
-   **GUI Display**: Updates the `tk.Label` (`preview_label`) with a new `PhotoImage` representing the rendered subtitle preview.
-   **Console Output**: Prints debug messages about font loading and errors during preview generation.

---

**File: `videocutter/gui/depthflow_settings_frame.py`**

**Core Purpose and Logic:**
This module defines a custom Tkinter `ttk.Frame` subclass, `DepthflowSettingsFrame`, specifically designed to encapsulate all GUI controls related to DepthFlow effects. It is intended to be embedded as a tab within the main `VideoCutterGUI`.
-   **Widget Creation**: It creates and arranges various Tkinter widgets (Checkbuttons, Labels, Entries, Sliders) for configuring DepthFlow parameters such as vignette, depth of field, isometric, height, zoom ranges, number of effects per image, base zoom loops, and worker threads. It also includes new single-value parameters for fine-grained control over DepthFlow animations (offset_x, offset_y, steady, dolly, focus, invert, center_x, center_y, origin_x, origin_y, zoom_probability).
-   **Control Toggling**: The `toggle_depthflow_controls` method enables or disables all related widgets based on the state of the "Enable DepthFlow" checkbox, ensuring that only relevant controls are active.
-   **Integration with `gui_elements`**: It receives and uses the `gui_elements` dictionary from the main GUI to access and update shared Tkinter variables and other GUI components, ensuring seamless integration.
-   **Settings Collection**: The `collect_settings` method gathers all DepthFlow-related parameters from the GUI widgets into a dictionary, ready to be passed to the processing pipeline.

**Internal Dependencies:**
-   `videocutter.gui.gui_utils`: Used for `update_slider_value` and `update_slider_from_entry` functions to synchronize sliders and entry fields.

**External Dependencies:**
-   `tkinter` (as `tk`): Core GUI toolkit.
-   `tkinter.ttk`: For themed Tkinter widgets (`ttk.Frame`, `ttk.Scale`).

**Inputs:**
-   `parent`: The parent Tkinter widget (typically a `ttk.Notebook`) where this frame will be placed.
-   `gui_elements` (dict): A dictionary containing references to various Tkinter variables and widgets from the main GUI, allowing this frame to interact with the overall application state.
-   User interactions with the widgets within this frame.

**Outputs:**
-   **GUI Display**: Renders the DepthFlow settings section of the GUI.
-   **GUI State Modification**: Updates the state (enabled/disabled) of its own widgets based on user input.
-   **Tkinter Variables**: Modifies the values of Tkinter variables (e.g., `var_depthflow_vignette_enable`, `var_depthflow_isometric_min`) stored in the `gui_elements` dictionary, which are then used by the main application logic.
-   **Collected Settings**: Returns a dictionary of DepthFlow configuration parameters via `collect_settings`.

---

**File: `videocutter/gui/main_settings_frame.py`**

**Core Purpose and Logic:**
This module defines a custom Tkinter `ttk.Frame` subclass, `MainSettingsFrame`, specifically designed to encapsulate the primary settings for the VideoCutter application. It is intended to be embedded as a tab within the main `VideoCutterGUI`.
-   **Widget Creation**: It creates and arranges various Tkinter widgets (Labels, Entries, Radiobuttons, Checkbuttons, Buttons) for configuring:
    -   **Folders**: Input and template directories.
    -   **Video Duration**: Segment duration, maximum length limit, transition duration, and FPS.
    -   **Batch Processing**: Input folder for batch processing with browse and clear options.
    -   **Audio Settings**: Voiceover start delay.
    -   **Video Processing**: Video orientation (vertical/horizontal) and a checkbox for side blur.
-   **Integration with `gui_elements`**: It receives and uses the `gui_elements` dictionary from the main GUI to access and update shared Tkinter variables and other GUI components, ensuring seamless integration.
-   **File Browsing**: Provides methods (`_browse_batch_folder`, `_clear_batch_folder`) to interact with `tkinter.filedialog` for selecting batch input folders and managing the state of the single input folder entry.
-   **Settings Collection**: The `collect_settings` method gathers all main settings parameters from the GUI widgets into a dictionary, ready to be passed to the processing pipeline.

**Internal Dependencies:**
-   `videocutter.utils.gui_config_manager` (as `gcm`): Provides default values for various settings.
-   `videocutter.gui.gui_utils`: Used for utility functions (though not directly called in the provided snippet, it's imported).

**External Dependencies:**
-   `tkinter` (as `tk`): Core GUI toolkit.
-   `tkinter.ttk`: For themed Tkinter widgets (`ttk.Frame`).
-   `tkinter.filedialog`: For opening folder selection dialogs.

**Inputs:**
-   `parent`: The parent Tkinter widget (typically a `ttk.Notebook`) where this frame will be placed.
-   `gui_elements` (dict): A dictionary containing references to various Tkinter variables and widgets from the main GUI, allowing this frame to interact with the overall application state.
-   User interactions with the widgets within this frame.

**Outputs:**
-   **GUI Display**: Renders the main settings section of the GUI.
-   **GUI State Modification**: Updates the state of its own widgets (e.g., disabling input folder entry in batch mode).
-   **Tkinter Variables**: Modifies the values of Tkinter variables (e.g., `var_batch_input_folder`, `var_video_orientation`) stored in the `gui_elements` dictionary, which are then used by the main application logic.
-   **Collected Settings**: Returns a dictionary of main configuration parameters via `collect_settings`.

---

**File: `videocutter/gui/subtitle_settings_frame.py`**

**Core Purpose and Logic:**
This module defines a custom Tkinter `ttk.Frame` subclass, `SubtitleSettingsFrame`, specifically designed to encapsulate all GUI controls related to subtitle generation and styling. It is intended to be embedded as a tab within the main `VideoCutterGUI`.
-   **Widget Creation**: It creates and arranges various Tkinter widgets (Checkbuttons, Labels, Entries, Comboboxes, Sliders, Radiobuttons) for configuring:
    -   **Basic Settings**: Enable/disable subtitles, characters per line, font, font size, text color, outline thickness and color, shadow enable/color/opacity, and position (using a 3x3 grid of radio buttons for ASS alignment).
    -   **Advanced Settings (ASS Specific)**: Secondary color, bold/italic/underline/strikeout styles, X/Y scaling, letter spacing, angle, border style, shadow distance, margins (left, right, vertical), and encoding.
-   **Control Toggling**: The `toggle_subtitle_controls` method enables or disables all related widgets based on the state of the "Enable Subtitles" checkbox. The `toggle_subtitle_shadow_controls` method specifically manages the shadow-related controls.
-   **Slider-Entry Synchronization**: Integrates with `gui_utils` to keep sliders and entry fields synchronized for font size, outline thickness, and background opacity.
-   **Subtitle Preview**: Triggers the `update_subtitle_preview` function from `gui_utils` (with debouncing) whenever relevant subtitle settings are changed, providing real-time visual feedback.
-   **Integration with `gui_elements`**: It receives and uses the `gui_elements` dictionary from the main GUI to access and update shared Tkinter variables and other GUI components, ensuring seamless integration.

**Internal Dependencies:**
-   `videocutter.utils.gui_config_manager` (as `gcm`): Provides default values for subtitle settings.
-   `videocutter.gui.gui_utils`: Used for `update_slider_value`, `update_slider_from_entry`, `schedule_subtitle_preview_update`, and `update_subtitle_preview` functions.

**External Dependencies:**
-   `tkinter` (as `tk`): Core GUI toolkit.
-   `tkinter.ttk`: For themed Tkinter widgets (`ttk.Frame`, `ttk.Scale`, `ttk.Combobox`).

**Inputs:**
-   `parent`: The parent Tkinter widget (typically a `ttk.Notebook`) where this frame will be placed.
-   `gui_elements` (dict): A dictionary containing references to various Tkinter variables and widgets from the main GUI, allowing this frame to interact with the overall application state.
-   User interactions with the widgets within this frame.

**Outputs:**
-   **GUI Display**: Renders the subtitle settings section of the GUI, including a live preview.
-   **GUI State Modification**: Updates the state (enabled/disabled) of its own widgets based on user input.
-   **Tkinter Variables**: Modifies the values of Tkinter variables (e.g., `var_generate_srt`, `var_subtitle_font`, `var_subtitle_fontsize`) stored in the `gui_elements` dictionary, which are then used by the main application logic.

---

**File: `videocutter/processing/video_processor.py`**

**Core Purpose and Logic:**
This module is responsible for fundamental video and image processing tasks, acting as a foundational component for preparing media for the slideshow generation. It encapsulates functionalities related to video metadata extraction, video splitting, video orientation conversion with optional blurring, image resizing, and image background processing.

**Major Logic Blocks:**

1.  **Video Utilities:**
    -   `get_video_metadata`: Extracts essential video metadata (width, height, duration, frame rates) using `ffprobe`. It prioritizes stream data but includes fallback logic for duration from the format section.
    -   `get_video_duration`: A wrapper around `get_video_metadata` to specifically retrieve video duration.
    -   `split_video_into_segments`: Divides an input video into multiple smaller segments of a specified duration using FFmpeg. It uses advanced FFmpeg segmenting features to ensure keyframes at segment boundaries.
    -   `convert_to_horizontal_with_blur_bg`: Transforms a vertical video to a horizontal (16:9) format. It can either add a blurred background (derived from the video itself) or simply pad with black bars if `apply_blur` is false. This uses FFmpeg's `scale` and `overlay` or `pad` filters.

2.  **Image Utilities:**
    -   `process_image_for_video`: Resizes and adapts an image to fit the target video's dimensions and orientation (vertical 9:16 or horizontal 16:9). It applies intelligent scaling, cropping, and padding. If `apply_blur` is true, it creates a blurred background from the image itself and overlays the scaled image, potentially with gradient fades for a more aesthetic look (pillarbox or letterbox effect). This function overwrites the original image file with the processed version.

3.  **Cleanup:**
    -   `clean_short_video_segments`: Scans a specified directory for video files and deletes any that are shorter than a given minimum duration. It uses `get_video_duration` to check each file.

**Internal Dependencies:**
-   `videocutter.utils.file_utils`: `find_files_by_extension` (used by `clean_short_video_segments`). This creates a slight circular dependency if `file_utils` were to import from `processing`, but in this case, `video_processor` imports from `file_utils`.

**External Dependencies:**
-   `subprocess`: For executing FFmpeg and FFprobe commands.
-   `os`: For path manipulation, file existence checks, and file deletion.
-   `shutil`: For copying and moving files.
-   `json`: For parsing FFprobe's JSON output.
-   `PIL` (Pillow): `Image`, `ImageFilter`, `ImageDraw` for image loading, resizing, filtering (blur), drawing (gradients), and saving.

**Inputs:**

**`get_video_metadata`:**
-   `video_path` (str): Path to the video file.

**`get_video_duration`:**
-   `video_path` (str): Path to the video file.

**`split_video_into_segments`:**
-   `input_file` (str): Path to the video file to be split.
-   `output_prefix` (str): Prefix for the output segment files (e.g., `video_seg`).
-   `segment_duration` (int): Desired duration of each segment in seconds.

**`convert_to_horizontal_with_blur_bg`:**
-   `input_path` (str): Path to the input video file (expected to be vertical).
-   `output_path` (str): Path where the converted horizontal video will be saved.
-   `target_output_height` (int, optional): Desired height of the output horizontal video (default: 1080).
-   `apply_blur` (bool, optional): If `True`, a blurred background is used; otherwise, black bars are used (default: `True`).

**`process_image_for_video`:**
-   `image_path` (str): Path to the image file to be processed.
-   `target_final_height` (int): Desired height of the output video frame (e.g., 1920 for vertical, 1080 for horizontal).
-   `target_video_orientation` (str): Desired orientation of the final video ('vertical' or 'horizontal').
-   `apply_blur` (bool): If `True`, a blurred background with gradients is applied; otherwise, black bars are used.

**`clean_short_video_segments`:**
-   `directory_to_clean` (str): The directory containing video files to check.
-   `min_duration_seconds` (float): The minimum duration a video must have to be kept.
-   `video_extensions` (list[str], optional): List of file extensions to consider as videos (default: `['.mp4']`).
-   `is_dry_run` (bool, optional): If `True`, only print actions. Defaults to `False`.

**Outputs:**

**`get_video_metadata`:**
-   `dict` or `None`: A dictionary containing `width`, `height`, `duration`, `r_frame_rate`, `avg_frame_rate` if successful, otherwise `None`.

**`get_video_duration`:**
-   `float` or `None`: The duration of the video in seconds, or `None` if metadata extraction fails.

**`split_video_into_segments`:**
-   Creates multiple video files (e.g., `output_prefix001.mp4`, `output_prefix002.mp4`) in the same directory as the input.
-   Prints status and error messages to the console.

**`convert_to_horizontal_with_blur_bg`:**
-   `bool`: `True` if conversion is successful, `False` otherwise.
-   Creates a new video file at `output_path`.
-   Prints status and error messages to the console.

**`process_image_for_video`:**
-   Modifies the image file at `image_path` in place, overwriting it with the processed version.
-   Prints status and error messages to the console.

**`clean_short_video_segments`:**
-   Deletes video files from `directory_to_clean` that are shorter than `min_duration_seconds`.
-   Prints which files are deleted or would be deleted (in dry run mode).

---

**File: `videocutter/processing/depth_processor.py`**

**Core Purpose and Logic:**
This module is responsible for applying 3D parallax effects to static images using the `DepthFlow` library. It integrates with external depth estimation and upscaling models to generate dynamic video segments from still images, enhancing visual engagement.

**Major Logic Blocks:**

1.  **`_combinations` Helper Function:**
    -   A utility function to generate combinations of options, used internally by `DepthFlow` for creating variations of rendered output.

2.  **`DefaultDepthScene` Class:**
    -   A simple implementation of `DepthScene` from `DepthFlow`. It defines a basic animation logic (e.g., sine wave for `offset_x` and `zoom`) that can be applied to the depth-enhanced images. This serves as a default scene if more complex, configurable scenes are not provided.

3.  **`ConfigurableDepthManager` Class:**
    -   This class orchestrates the DepthFlow processing. It manages the depth estimator (`DepthAnythingV2`) and upscaler (`BrokenUpscaler` or `NoUpscaler`) models, handles multithreading for parallel processing of images, and defines how animations and output filenames are generated based on the provided configuration.
    -   `__attrs_post_init__`: Initializes models and sets concurrency based on configuration.
    -   `parallax`: Submits an image for processing in a separate thread, managing a thread pool to limit concurrency.
    -   `_worker`: The actual processing logic for a single image, where `DepthScene` is initialized, input image is set, animations are applied, and the video is rendered.
    -   `filename`: Determines the output video filename (e.g., `image_name_df.mp4`).
    -   `animate`: Adds various `DepthFlow` animation presets (Circle, Orbital, Dolly, Horizontal) and `DepthState` parameters (vignette, DoF, isometric, height, zoom) to the scene. It randomizes some parameters and logs the applied animations to a text file.
    -   `variants`: Defines the rendering variations for `DepthFlow`, such as output height, time (duration), and FPS, pulling these values from the configuration.

4.  **`apply_depth_effects` Function:**
    -   The main entry point for this module. It takes a list of image file paths and a configuration dictionary.
    -   It initializes `ConfigurableDepthManager` with the specified estimator, upscaler, and concurrency settings.
    -   It iterates through the provided image paths, calling `manager.parallax` for each image to start the depth processing.
    -   It waits for all processing threads to complete (`manager.join()`) and returns a list of paths to the generated depth video files.

**Internal Dependencies:**
-   `Broken.Externals.Depthmap.DepthAnythingV2`: External library for depth estimation.
-   `Broken.Externals.Depthmap.DepthEstimator`: Base class for depth estimators.
-   `Broken.Externals.Upscaler.BrokenUpscaler`: External library for upscaling.
-   `Broken.Externals.Upscaler.NoUpscaler`: A placeholder upscaler.

**External Dependencies:**
-   `os`: For environment variables (`PYTORCH_ENABLE_MPS_FALLBACK`), path manipulation, and directory creation.
-   `time`: For `time.sleep` in thread management.
-   `random`: For randomizing animation parameters.
-   `itertools`: For `itertools.product` in `_combinations`.
-   `math`: For mathematical operations (e.g., `math.sin`).
-   `abc`: For `abstractmethod` (though `DepthManager` is no longer directly inherited, it's a remnant).
-   `pathlib.Path`: For object-oriented path manipulation.
-   `threading.Thread`: For running depth processing in parallel.
-   `typing.List`, `typing.Type`: For type hinting.
-   `attr.define`, `attr.Factory`: For defining classes with attributes and default factories.
-   `DepthFlow`: The core library for 3D parallax effects (`DepthScene`, `Motion`, `State`).
-   `dotmap.DotMap`: For flexible access to configuration objects.

**Inputs:**

**`apply_depth_effects` function:**
-   `image_file_paths` (List[str]): A list of absolute paths to image files (e.g., `.jpg`, `.jpeg`, `.png`).
-   `config_params` (DotMap or dict): A configuration object containing settings for DepthFlow processing, including:
    -   `depthflow.segment_duration` (int): Target duration for the output video segments.
    -   `depthflow.render_height` (int): Height of the rendered video.
    -   `depthflow.render_fps` (int): Frame rate of the rendered video.
    -   `depthflow.vignette_enable` (bool): Enable/disable vignette effect.
    -   `depthflow.dof_enable` (bool): Enable/disable depth of field effect.
    -   `depthflow.animations` (list): List of animation types and their intensity ranges.
    -   `depthflow.isometric_min`, `depthflow.isometric_max` (float): Range for isometric parameter.
    -   `depthflow.height_min`, `depthflow.height_max` (float): Range for height parameter.
    -   `depthflow.zoom_min`, `depthflow.zoom_max` (float): Range for zoom parameter.
    -   `depthflow.min_effects_per_image`, `depthflow.max_effects_per_image` (int): Number of animations to apply.
    -   `depthflow.base_zoom_loops` (bool): Whether base zoom animation loops.
    -   `output_datetime_folder` (str): Path to the output directory for logging.
    -   `workers` (int, optional): Number of concurrent threads for processing.

**Outputs:**

**`apply_depth_effects` function:**
-   `List[str]`: A list of absolute paths to the generated depth video files (e.g., `image_name_df.mp4`).
-   Creates video files (e.g., `image_name_df.mp4`) in the same directory as the input images.
-   Appends log entries to `_depth_log.txt` within the `output_datetime_folder`.
-   Prints status and error messages to the console.

---

**File: `videocutter/processing/slideshow_generator.py`**

**Core Purpose and Logic:**
This module is responsible for generating the base video slideshow from a collection of images and video segments. It uses FFmpeg to combine these media files, apply transitions between them, and optionally add a dynamic watermark. The output is a video file that serves as the visual foundation before audio and final overlays are added.

**Major Logic Blocks:**

1.  **`_get_video_dimensions` Helper Function:**
    -   Determines the target width and height for the output video based on the specified `video_orientation` (vertical or horizontal) and configuration settings.

2.  **`_prepare_media_input` Helper Function:**
    -   Prepares FFmpeg input arguments and filter complex parts for a single media item (image or video).
    -   For images, it applies a `zoompan` effect (either zoom-in or zoom-out randomly) and pre-scales the image to a high resolution to ensure quality during zooming.
    -   For videos, it scales and pads them to fit the target resolution.
    -   It handles the special case of the outro video, ensuring it's properly scaled and its duration is respected.

3.  **`_apply_watermark_filter` Helper Function:**
    -   Generates the FFmpeg `drawtext` filter string for applying a watermark.
    -   Supports two types of watermark animation: `ccw` (counter-clockwise movement) and `random` (random position changes).
    -   Configurable font, size, color (including 'random'), and opacity.

4.  **`generate_base_slideshow` Function:**
    -   The main function of this module.
    -   Takes a list of media file paths (images and video segments, with the last one expected to be the outro video) and a configuration object.
    -   Constructs a complex FFmpeg command:
        -   Iterates through each media file, preparing its input and initial filter chain using `_prepare_media_input`.
        -   Builds a transition chain using FFmpeg's `xfade` filter, applying random transition types (e.g., `hblur`, `smoothup`) and a specified duration.
        -   Conditionally applies a watermark using `_apply_watermark_filter` to each transition segment, excluding the transition to the final outro.
        -   Calculates the total duration of the final video based on slide durations and the actual outro duration.
    -   Executes the FFmpeg command to generate the base slideshow video.

**Internal Dependencies:**
-   None directly within the `videocutter` package, but it relies on `videocutter.main` to pass the `config` object which contains parameters from `config_manager`.

**External Dependencies:**
-   `subprocess`: For executing FFmpeg commands.
-   `os`: For path manipulation and file extension checking.
-   `random`: For selecting random transition types and watermark positions/speeds.
-   `dotmap.DotMap`: For flexible access to configuration parameters.

**Inputs:**

**`generate_base_slideshow` function:**
-   `media_file_paths` (list[str]): A list of absolute paths to media files (images and video segments). The last item in the list is expected to be the outro video.
-   `output_path` (str): The full path for the output slideshow.mp4.
-   `config` (DotMap): A configuration object containing parameters such as:
    -   `slide_duration` (int): Duration for each image/segment in seconds.
    -   `video_orientation` (str): 'vertical' or 'horizontal'.
    -   `target_resolution` (dict): Contains `vertical_height`, `vertical_width`, `horizontal_height`, `horizontal_width`.
    -   `fps` (int): Frames per second for the output video.
    -   `watermark_settings` (dict): Contains `text`, `type`, `speed_frames`, `font_file_path`, `font_size`, `opacity`, `fontcolor`.
    -   `enable_watermark` (bool): Whether to apply the watermark.
    -   `outro_duration` (int): Actual duration of the outro video.
    -   `transitions` (list): List of FFmpeg transition names.
    -   `transition_duration` (float): Duration of each transition in seconds.
    -   `video_crf` (int): Constant Rate Factor for video encoding.
    -   `video_preset` (str): FFmpeg encoding preset (e.g., 'medium', 'fast').

**Outputs:**

**`generate_base_slideshow` function:**
-   `str` or `None`: The `output_path` if the slideshow generation is successful, otherwise `None`.
-   Creates a video file at the specified `output_path`.
-   Prints status and error messages to the console.

---

**File: `videocutter/processing/audio_processor.py`**

**Core Purpose and Logic:**
This module is dedicated to all audio mixing and processing tasks within the VideoCutter pipeline. It takes a base video (without audio) and integrates various audio components—soundtrack, voiceover, and transition sounds—into a final mixed audio track, which is then combined with the video. It uses FFmpeg for complex audio filtering and `mutagen` for quick audio duration checks.

**Major Logic Blocks:**

1.  **`get_mp3_duration` Function:**
    -   Determines the duration of an MP3 file using the `mutagen` library. Includes a fallback to `ffprobe` if `mutagen` fails.

2.  **`process_audio` Function:**
    -   The main function of this module, orchestrating the entire audio processing workflow.
    -   **Input Preparation**: Resolves paths for template audio files (soundtrack, transition sound, voiceover end) and the project-specific voiceover file. Defines paths for numerous intermediate audio files.
    -   **Video Duration Check**: Retrieves the duration of the base video using `video_processor.get_video_duration` to ensure all audio tracks are synchronized to the video length.
    -   **Template File Verification**: Checks for the existence of required audio template files.
    -   **Soundtrack Preparation (Step 1)**: Trims the main soundtrack to the video's duration and applies fade-in/fade-out effects and a base volume.
    -   **Transitions Preparation (Step 2)**: Trims the transition sound to the video's duration (excluding the outro) and applies a base volume.
    -   **Voiceover Processing (Steps 3-7, conditional)**:
        -   If a `voiceover.mp3` exists:
            -   **Initial Delay (Step 3)**: Adds an initial silence to the voiceover based on `vo_delay` from the config.
            -   **Padding (Step 4)**: Pads the voiceover with silence at the end to match the video's duration.
            -   **Sidechain Compression (Steps 5 & 7)**: Applies sidechain compression to the main soundtrack, ducking its volume when the main voiceover (Step 5) or the end voiceover (Step 7) is present. This ensures voiceovers are clearly audible over background music.
            -   **End Voiceover Preparation (Step 6)**: Adds initial silence to the `voiceover_end.mp3` to align it with the end of the video.
        -   If no voiceover, it skips these steps and uses the adjusted soundtrack directly for the final mix.
    -   **Final Audio Mix (Step 8)**: Combines the (potentially compressed) main soundtrack with the transition sounds, applying final volume adjustments.
    -   **Video-Audio Combination (Step 9)**: Uses FFmpeg to combine the base video with the newly mixed audio track, copying the video stream and re-encoding the audio to AAC.
    -   **Cleanup**: Removes all intermediate audio files upon completion or error.

**Internal Dependencies:**
-   `.video_processor`: `get_video_duration` (for getting the base video's duration).

**External Dependencies:**
-   `subprocess`: For executing FFmpeg commands.
-   `os`: For path manipulation, file existence checks, and file deletion.
-   `shutil`: For copying files (e.g., if voiceover is skipped).
-   `json`: For parsing `ffprobe` output (used in `get_mp3_duration` fallback).
-   `mutagen.mp3`: For quickly getting MP3 file durations.
-   `dotmap.DotMap`: For flexible access to configuration parameters.

**Inputs:**

**`process_audio` function:**
-   `base_video_path` (str): Path to the input video file (e.g., `slideshow_base.mp4`) that needs audio.
-   `output_video_with_audio_path` (str): Path where the final video with the mixed audio will be saved.
-   `config` (DotMap): A configuration object containing audio-specific settings:
    -   `audio.outro_duration` (int): Duration of the outro video.
    -   `audio.vo_delay` (int): Delay before the main voiceover starts.
    -   `audio.soundtrack_volume` (float): Volume of the background soundtrack.
    -   `audio.transition_volume` (float): Volume of transition sound effects.
    -   `audio.sidechain_ratio`, `audio.sidechain_threshold`, `audio.sidechain_attack`, `audio.sidechain_release` (int/float): Parameters for sidechain compression.
    -   `audio.final_mix_main_volume`, `audio.final_mix_transition_volume` (float): Final volume adjustments for mixing.
    -   `template_folder` (str): Path to the directory containing audio template files.
-   `working_directory` (str): The directory where the project-specific `voiceover.mp3` is located and where intermediate audio files will be stored.

**Files (read by the script):**
-   `base_video_path` (video file).
-   `soundtrack.mp3`, `transition_long.mp3`, `voiceover_end.mp3` from `template_folder`.
-   `voiceover.mp3` from `working_directory` (if present).

**Outputs:**

**`process_audio` function:**
-   `str` or `None`: The `output_video_with_audio_path` if audio processing is successful, otherwise `None`.
-   Creates a new video file at `output_video_with_audio_path` with the mixed audio.
-   Creates numerous intermediate audio files within the `working_directory`, which are then cleaned up.
-   Prints status and error messages to the console.

---

**File: `videocutter/processing/subtitle_generator.py`**

**Core Purpose and Logic:**
This module is responsible for transcribing audio files and generating subtitle files in either SRT (SubRip) or ASS (Advanced SubStation Alpha) format. It leverages the `WhisperX` library for accurate speech-to-text transcription and forced alignment, and `mutagen` for basic audio duration checks. It also handles the styling of ASS subtitles based on configuration.

**Major Logic Blocks:**

1.  **`_get_audio_duration` Function:**
    -   A utility function to determine the duration of an MP3 file using `mutagen`.

2.  **`_format_time` Function:**
    -   Converts a time in seconds to the standard SRT time format (HH:MM:SS,mmm).

3.  **`_transcribe_with_whisperx` Function:**
    -   The core transcription logic. It loads a `WhisperX` model (specified by `model_name`, `device`, `compute_type`, and `language`), transcribes the audio, and then performs forced alignment to get precise word-level timings.

4.  **`_whisperx_result_to_srt` Function:**
    -   Converts the aligned transcription results from `WhisperX` into a formatted SRT string. It includes logic to wrap lines based on a `max_width` (characters per line) and applies a `time_offset`.

5.  **`_format_ass_time` Function:**
    -   Converts a time in seconds to the ASS time format (H:MM:SS.cs).

6.  **`_whisperx_result_to_ass` Function:**
    -   Converts the aligned transcription results into a formatted ASS string. This function is more complex as it dynamically generates the ASS header and style definition based on numerous subtitle styling parameters provided in the `config` (font, size, colors, bold, italic, underline, scale, spacing, angle, border style, shadow, margins, encoding). It also handles color format conversion (RGB to BGR) and determines `PlayResX`/`PlayResY` based on video orientation.

7.  **`generate_subtitles_from_audio_file` Function:**
    -   The main entry point for this module.
    -   Takes an audio file path, an output path, a configuration object, the desired `subtitle_format` ('srt' or 'ass'), and a `time_offset_seconds`.
    -   Performs input validation (checks if audio file exists).
    -   Calls `_transcribe_with_whisperx` to get the transcription.
    -   Calls either `_whisperx_result_to_srt` or `_whisperx_result_to_ass` based on the `subtitle_format` parameter.
    -   Writes the generated subtitle content to the specified `output_path`.

**Internal Dependencies:**
-   `videocutter.utils.font_utils`: `get_font_name` (used to resolve the actual font name for ASS styling).

**External Dependencies:**
-   `os`: For path manipulation, file existence checks, and directory creation.
-   `whisperx`: The primary library for audio transcription and alignment.
-   `certifi`: Used to set `SSL_CERT_FILE` environment variable for secure connections (likely for downloading WhisperX models).
-   `mutagen.mp3`: For getting MP3 audio durations.
-   `dotmap.DotMap`: For flexible access to configuration parameters.

**Inputs:**

**`generate_subtitles_from_audio_file` function:**
-   `audio_file_path` (str): Path to the input audio file (e.g., `voiceover.mp3`).
-   `output_path` (str): Path where the generated subtitle file (e.g., `.srt` or `.ass`) should be saved.
-   `config` (DotMap): A configuration object containing subtitle-specific settings:
    -   `subtitles.language` (str): Language for transcription (e.g., 'en').
    -   `subtitles.whisper_model` (str): Name of the WhisperX model to use (e.g., 'base', 'tiny').
    -   `subtitles.device` (str): Computation device ('cpu' or 'cuda').
    -   `subtitles.compute_type` (str): Compute type ('int8').
    -   `subtitles.max_line_width` (int): Maximum characters per line for SRT.
    -   `subtitles.font_name` (str): Font name for ASS.
    -   `subtitles.font_size` (int): Font size for ASS.
    -   `subtitles.font_color_hex` (str): Hex color for ASS text.
    -   `subtitles.shadow_color_hex` (str): Hex color for ASS shadow.
    -   `subtitles.shadow_opacity` (float): Opacity for ASS shadow.
    -   `subtitles.shadow_enabled` (bool): Enable/disable shadow for ASS.
    -   `subtitles.position_ass` (int): ASS alignment position (1-9).
    -   `subtitles.outline_thickness` (float): Outline thickness for ASS.
    -   `subtitles.outline_color_hex` (str): Hex color for ASS outline.
    -   `subtitles.secondary_color_hex` (str): Hex color for ASS secondary color.
    -   `subtitles.bold`, `subtitles.italic`, `subtitles.underline`, `subtitles.strikeout` (int): Font styles for ASS.
    -   `subtitles.scale_x`, `subtitles.scale_y` (int): Scaling for ASS.
    -   `subtitles.spacing` (float): Letter spacing for ASS.
    -   `subtitles.angle` (int): Rotation angle for ASS.
    -   `subtitles.border_style` (int): Border style for ASS.
    -   `subtitles.shadow_distance` (float): Shadow distance for ASS.
    -   `subtitles.margin_l`, `subtitles.margin_r`, `subtitles.margin_v` (int): Margins for ASS.
    -   `subtitles.encoding` (int): Encoding for ASS.
    -   `video_orientation` (str): 'vertical' or 'horizontal' (for `PlayResX`/`Y` in ASS).
    -   `target_resolution` (dict): Contains `vertical_width`, `vertical_height`, `horizontal_width`, `horizontal_height` (for `PlayResX`/`Y` in ASS).
    -   `fonts_folder` (str): Path to the fonts directory (for `get_font_name`).
-   `subtitle_format` (str): Desired output format ('srt' or 'ass').
-   `time_offset_seconds` (float): An offset in seconds to apply to all subtitle timestamps.

**Outputs:**

**`generate_subtitles_from_audio_file` function:**
-   `str` or `None`: The `output_path` if subtitle generation is successful, otherwise `None`.
-   Creates a subtitle file (e.g., `voiceover.srt` or `voiceover.ass`) at the specified `output_path`.
-   Creates the output directory if it does not exist.
-   Prints status and error messages to the console.

---

**File: `videocutter/processing/overlay_compositor.py`**

**Core Purpose and Logic:**
This module is responsible for the final stage of video processing: applying various visual overlays and rendering subtitles onto the video. It takes a video with audio (from `audio_processor.py`) and uses FFmpeg's complex filter graphs to layer multiple elements, producing the final output video.

**Major Logic Blocks:**

1.  **`_get_overlay_video_duration` Function:**
    -   A utility function to get the duration of an overlay video file using `ffprobe`.

2.  **`apply_final_overlays` Function:**
    -   The main function of this module.
    -   **Input Preparation**: Retrieves various configuration settings related to title text, title video, subscribe overlay, general effects, and subtitles. It also gets metadata (duration, dimensions) of the main input video.
    -   **FFmpeg Command Construction**: Builds a complex FFmpeg command with multiple filter graph parts:
        -   **Main Video and Audio Streams**: Initializes the main video and audio streams.
        -   **Subscribe Overlay (Conditional)**: If enabled and a file is provided, it adds the subscribe overlay video. This involves:
            -   Mixing the subscribe overlay's audio with the main video's audio (with a delay).
            -   Applying chromakey to the subscribe overlay video to remove its background.
            -   Overlaying the chromakeyed video onto the main video at a specified time.
        -   **Effect Overlay (Conditional)**: If enabled and a file is provided, it adds a general effect overlay. This involves:
            -   Scaling the effect overlay to match the main video's dimensions.
            -   Applying opacity and a blend mode (e.g., 'overlay', 'normal') to the effect.
            -   Overlaying the effect onto the current video stream.
        -   **Title Video Overlay (Conditional)**: If enabled and a file is provided, it adds a title video overlay. This is similar to the subscribe overlay, with chromakey and timed appearance.
        -   **Title Text Overlay (Conditional)**: If enabled, it adds dynamic text (e.g., model name) to the video. This involves:
            -   Calculating the appearance time based on any preceding title video overlay.
            -   Writing the title text to a temporary file (for FFmpeg's `textfile` option).
            -   Using FFmpeg's `drawtext` filter to render the text with configurable font, size, color, opacity, position, and optional background box.
        -   **Subtitle Rendering (Conditional)**: If enabled and a subtitle file is provided, it renders the subtitles onto the video. This uses FFmpeg's `subtitles` filter, which supports ASS styling. It resolves font paths and constructs the ASS style string based on detailed subtitle configuration.
        -   **Final Output**: Maps the final processed video stream and the mixed audio stream to the output file, specifying video and audio codecs and quality settings.
    -   **Execution and Cleanup**: Executes the constructed FFmpeg command. Cleans up any temporary files (like the title text file) upon completion or error.

**Internal Dependencies:**
-   `videocutter.utils.font_utils`: `get_font_name` (for resolving font names for subtitles).
-   `.video_processor`: `get_video_duration`, `get_video_metadata` (for getting main video and overlay video durations/metadata).

**External Dependencies:**
-   `subprocess`: For executing FFmpeg commands.
-   `os`: For path manipulation, file existence checks, and file deletion.
-   `random`: For random font colors if configured.
-   `json`: For parsing `ffprobe` output.
-   `glob`: Imported but not directly used in the provided code.
-   `tempfile`: For creating temporary files for title text.
-   `typing.Optional`: For type hinting.
-   `dotmap.DotMap`: For flexible access to configuration parameters.
-   `shutil`: For copying subtitle files to a temporary directory.

**Inputs:**

**`apply_final_overlays` function:**
-   `input_video_path` (str): Path to the video file that already has audio (e.g., `slideshow_with_audio.mp4`).
-   `output_video_path` (str): Path where the final output video will be saved.
-   `config` (DotMap): A configuration object containing various overlay and subtitle settings:
    -   `title_overlay` (dict): Text, font, size, color, timing, position, opacity, background settings.
    -   `subscribe_overlay` (dict): Enable, overlay file, delay, chromakey settings.
    -   `title_video_overlay` (dict): Enable, overlay file, delay, chromakey settings.
    -   `effects` (dict): Enable, overlay file, opacity, blend mode.
    -   `subtitles` (dict): Enable, font, size, colors, outline, shadow, position, etc. (detailed ASS styling parameters).
    -   `video_orientation` (str): 'vertical' or 'horizontal'.
    -   `template_folder` (str): Path to the template directory.
    -   `effects_folder` (str): Path to the effects overlay directory.
    -   `subscribe_folder` (str): Path to the subscribe overlay directory.
    -   `title_folder` (str): Path to the title video overlay directory.
    -   `fonts_folder` (str): Path to the fonts directory.
    -   `video_crf` (int): Constant Rate Factor for video encoding.
    -   `video_preset` (str): FFmpeg encoding preset.
    -   `audio_bitrate` (str): Audio bitrate for the final output.
-   `working_directory` (str): The base directory for the current processing run (used for resolving paths, though not directly used for file operations in this module).
-   `subtitle_file_path` (str | None): Absolute path to the generated subtitle file (SRT or ASS).

**Outputs:**

**`apply_final_overlays` function:**
-   `str` or `None`: The `output_video_path` if overlay composition is successful, otherwise `None`.
-   Creates the final output video file at `output_video_path`.
-   Creates a temporary file for title text, which is then cleaned up.
-   Prints status and error messages to the console.

---

**File: `videocutter/utils/file_utils.py`**

**Core Purpose and Logic:**
This module provides a collection of utility functions for common file and directory operations used throughout the VideoCutter project. Its primary responsibilities include setting up project-specific output and backup directories, backing up original files, finding files by extension, organizing files into timestamped folders, and limiting the number of media files based on a total duration limit.

**Major Logic Blocks:**

1.  **`setup_project_directories` Function:**
    -   Creates `RESULT` and `SOURCE` subdirectories within a given `base_input_folder`.
    -   Generates a unique timestamp string (YYYY-MM-DD_HH-MM-SS).
    -   Creates a run-specific timestamped subfolder within the `SOURCE` directory for backups.

2.  **`backup_original_file` Function:**
    -   Copies a specified `original_file_path` to the `run_specific_source_folder` (created by `setup_project_directories`), ensuring original media is preserved.

3.  **`find_files_by_extension` Function:**
    -   Recursively searches a given `directory` for all files that match a list of specified `extensions`.
    -   Returns a list of absolute paths to the found files.

4.  **`organize_files_to_timestamped_folder` Function:**
    -   Creates a new timestamped subfolder within a `source_directory`.
    -   Moves and renames files from the `source_directory` into this new subfolder.
    -   Specifically renames MP3 files to `voiceover.mp3`.
    -   Renames other files sequentially (e.g., `001.ext`, `002.ext`) based on their extension.

5.  **`limit_media_files_by_duration` Function:**
    -   Takes a `directory` and a `total_time_limit_seconds`.
    -   Calculates how many media files can be kept based on an assumed `segment_duration_seconds` for each item.
    -   Sorts all media files alphabetically and keeps only the number of files that fit within the time limit.
    -   Deletes any surplus files from the directory.

**Internal Dependencies:**
-   None.

**External Dependencies:**
-   `os`: For path manipulation, directory creation, listing directory contents, checking file/directory existence, and file deletion.
-   `shutil`: For copying and moving files/directories.
-   `datetime`: For generating timestamp strings.

**Inputs:**

**`setup_project_directories` function:**
-   `base_input_folder` (str): The path to the main input folder (e.g., `INPUT`).

**`backup_original_file` function:**
-   `original_file_path` (str): Path to the file to be backed up.
-   `run_specific_source_folder` (str): Path to the backup folder for the current run.

**`find_files_by_extension` function:**
-   `directory` (str): The directory to search within.
-   `extensions` (list[str]): A list of file extensions (e.g., `['.mp4', '.jpg']`).

**`organize_files_to_timestamped_folder` function:**
-   `source_directory` (str): The directory containing files to be sorted.
-   `datetime_string` (str): The timestamp string for the new subfolder.

**`limit_media_files_by_duration` function:**
-   `directory` (str): The directory containing media files.
-   `total_time_limit_seconds` (int): The maximum total duration allowed for all media.
-   `segment_duration_seconds` (int): The assumed duration of each media item.
-   `image_extensions` (list[str], optional): List of image extensions.
-   `video_extensions` (list[str], optional): List of video extensions.

**Outputs:**

**`setup_project_directories` function:**
-   `tuple[str, str, str, str]`: Returns paths to `result_folder`, `source_folder`, `run_specific_source_folder`, and the `datetime_str`.
-   Creates the specified directories on the filesystem.
-   Prints messages about directory creation.

**`backup_original_file` function:**
-   Copies the `original_file_path` to the `run_specific_source_folder`.
-   Prints messages about the backup operation.

**`find_files_by_extension` function:**
-   `list[str]`: A list of absolute paths to the found files.

**`organize_files_to_timestamped_folder` function:**
-   `str`: The path to the newly created timestamped folder.
-   Moves and renames files within the `source_directory` to the new subfolder.
-   Prints messages about file movements and renames.

**`limit_media_files_by_duration` function:**
-   `list[str]`: A list of filenames (not full paths) that were kept.
-   Deletes surplus files from the specified `directory`.
-   Prints messages about file deletions and the number of files kept.

---

**File: `videocutter/utils/font_utils.py`**

**Core Purpose and Logic:**
This module provides utility functions specifically for handling font-related operations, primarily extracting the full font name from a font file. This is crucial for ensuring that FFmpeg and other tools can correctly identify and use fonts by their internal names rather than just their filenames.

**Major Logic Blocks:**

1.  **`get_font_name` Function:**
    -   Takes the `font_path` to a font file (e.g., `.ttf`, `.otf`).
    -   Uses the `fontTools.ttLib.TTFont` library to open and inspect the font file's internal naming tables.
    -   It specifically looks for `nameID 4` (Full font name) first. If not found, it falls back to `nameID 1` (Font Family name).
    -   Handles decoding of the font name string from various encodings.
    -   If any error occurs during the extraction process or if no suitable nameID is found, it falls back to returning the base filename without its extension.

**Internal Dependencies:**
-   None.

**External Dependencies:**
-   `os`: For extracting the base filename from a path.
-   `fontTools.ttLib.TTFont`: A third-party library for reading and manipulating font files.

**Inputs:**

**`get_font_name` function:**
-   `font_path` (str): The absolute or relative path to a font file (e.g., `Montserrat-SemiBold.otf`).

**Outputs:**

**`get_font_name` function:**
-   `str`: The extracted full font name (e.g., "Montserrat SemiBold"), or the filename without extension if extraction fails.
-   Prints error messages to the console if font name extraction encounters an exception.

---

**File: `audio.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for mixing various audio tracks (soundtrack, voiceover, transition sounds) and combining them with a video. It uses FFmpeg extensively for audio manipulation, including cutting, fading, adding silence, and applying sidechain compression. It also has a direct dependency on `srt_generator.py` for subtitle generation.

**Major Logic Blocks:**

1.  **Argument Parsing:**
    -   Uses `argparse` to accept command-line arguments for the input directory (`--i`), outro duration (`--od`), voiceover delay (`--vd`), and subtitle generation settings (`--srt`, `--smaxw`).

2.  **`add_audio_to_video` Function:**
    -   The main function that orchestrates the audio processing.
    -   **Video Duration Retrieval**: Uses `ffprobe` to get the duration of the input slideshow video, which is crucial for synchronizing audio tracks.
    -   **Soundtrack Adjustment (Step 1)**: Cuts the main `soundtrack.mp3` to match the video's duration and applies fade-in/fade-out effects.
    -   **Transition Sound Adjustment (Step 2)**: Cuts `transition_long.mp3` to match the video's duration minus the outro duration.
    -   **Voiceover Preparation (Steps 3-5)**:
        -   Adds an initial blank audio segment to `voiceover.mp3` based on `args.vo_delay`.
        -   **SRT Subtitle Generation (Conditional)**: If `generate_srt` is enabled, it calls `srt_generator.py` as a subprocess to generate SRT subtitles.
        -   Pads the voiceover with silence at the end to match the video's total duration.
    -   **Sidechain Compression (Steps 6 & 8)**: Applies sidechain compression to the soundtrack, using the main voiceover (Step 6) and then the end voiceover (Step 8) as key inputs. This ducks the music volume when voiceovers are present.
    -   **End Voiceover Preparation (Step 7)**: Adds initial silence to `voiceover_end.mp3` to align it with the end of the video.
    -   **Final Audio Mix (Step 9)**: Mixes the compressed soundtrack with the adjusted transition sounds.
    -   **Video-Audio Combination (Final Step)**: Combines the input slideshow video with the newly mixed audio track, copying the video stream and re-encoding the audio to AAC.

**Internal Dependencies:**
-   `srt_generator.py`: Called as a subprocess for subtitle generation.

**External Dependencies:**
-   `subprocess`: For executing FFmpeg and FFprobe commands, and for calling `srt_generator.py`.
-   `os`: For path manipulation.
-   `argparse`: For parsing command-line arguments.
-   `time`: For basic timing (start_time).

**Inputs:**

**Command-line arguments:**
-   `--i` (str): Path to the directory containing audio and video.
-   `--od` (int): Outro duration (in seconds).
-   `--vd` (int): Voiceover start delay (in seconds).
-   `--srt` (str): Flag to generate SRT subtitles ('0' or '1').
-   `--smaxw` (int): Maximum characters in one line of subtitles.

**Files (read by the script):**
-   `slideshow.mp4` from the input directory.
-   `soundtrack.mp3` from `TEMPLATE/`.
-   `transition_long.mp3` from `TEMPLATE/`.
-   `voiceover.mp3` from the input directory.
-   `voiceover_end.mp3` from `TEMPLATE/`.

**Outputs:**

-   `slideshow_with_audio.mp4`: The final video file with all mixed audio.
-   Intermediate audio files (e.g., `adjusted_soundtrack.mp3`, `adjusted_transitions.mp3`, `adjusted_voiceover.mp3`, `compressed_soundtrack.mp3`, `mixed_audio.mp3`) are created in the input directory. These are not explicitly cleaned up by this script.
-   If `--srt` is '1', it triggers the creation of `voiceover.srt` by `srt_generator.py`.
-   Prints extensive status and error messages to the console.

---

**File: `cleaner.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component designed to clean up video files by deleting those that are shorter than a specified minimum duration. It can operate in a dry-run mode to preview deletions without actually performing them. It also attempts to remove parent directories if they become empty after file deletions.

**Major Logic Blocks:**

1.  **`find_video_files` Function:**
    -   Recursively searches a given `directory` for all files ending with `.mp4` (case-insensitive).
    -   Returns a list of absolute paths to the found video files.

2.  **`get_video_duration` Function:**
    -   Uses `ffprobe` to extract the duration of a video file.
    -   Parses the `sexagesimal` output format (HH:MM:SS.ms) into seconds.
    -   Includes error handling for `ffprobe` failures.

3.  **`main` Function:**
    -   **Argument Parsing**: Uses `argparse` to accept command-line arguments for the `input_folder`, a `is_dry_run` flag, and `minimum_duration`.
    -   **File Identification**: Iterates through all video files found in the `input_folder` using `find_video_files`.
    -   **Duration Check**: For each video, it calls `get_video_duration` and adds the file to a `files_to_delete` set if its duration is less than `minimum_duration`.
    -   **Deletion/Dry Run**:
        -   If `is_dry_run` is `True`, it only prints which files *would* be deleted.
        -   If `is_dry_run` is `False`, it actually deletes the identified files using `os.unlink`.
        -   **Directory Cleanup**: After deleting a file, it attempts to remove the parent directory if it becomes empty. This logic uses `os.access` which is not a reliable way to check for directory emptiness.

**Internal Dependencies:**
-   None.

**External Dependencies:**
-   `subprocess`: For executing `ffprobe` commands.
-   `argparse`: For parsing command-line arguments.
-   `os`: For path manipulation, file deletion (`os.unlink`), and directory listing (`os.walk`, `os.access`).
-   `shutil`: For removing directories (`shutil.rmtree`).

**Inputs:**

**Command-line arguments:**
-   `--i` (str): The input folder containing video files.
-   `--d` (flag): If present, performs a dry run (only prints, no deletion).
-   `--m` (int): Deletes videos shorter than this many seconds.

**Files (read by the script):**
-   Video files (`.mp4`) within the `input_folder` and its subdirectories.

**Outputs:**

-   **File System Modification**:
    -   If not in dry-run mode, deletes video files shorter than `minimum_duration`.
    -   Attempts to remove empty parent directories.
-   **Console Output**: Prints messages indicating which files are being processed, their durations, and which files are deleted or would be deleted.

---

**File: `cutter.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component that acts as the primary orchestrator for the entire video processing pipeline in its original design. It handles initial video and image processing, file organization, and then sequentially calls other standalone scripts (`cleaner.py`, `sorter.py`, `depth.py`, `slideshow.py`) as subprocesses to complete the video creation.

**Major Logic Blocks:**

1.  **Argument Parsing:**
    -   Uses `argparse` to define and parse a large number of command-line arguments, covering almost all configurable aspects of the video processing pipeline (segment duration, time limit, input/template folders, title settings, voiceover delay, watermark settings, DepthFlow enable, video orientation, chromakey settings, subtitle settings, blur, and effect overlay).

2.  **`split_video` Function:**
    -   Splits an input video into segments of a specified duration using FFmpeg. It removes audio from the segments.

3.  **Directory Setup:**
    -   Creates `RESULT` and `SOURCE` subfolders within the `input_folder`.
    -   Creates a timestamped subfolder within `SOURCE` for backing up original files.

4.  **`process_videos` Function:**
    -   Processes video files to convert vertical videos to horizontal (16:9) format with a blurred background using FFmpeg.
    -   Copies original videos to the `SOURCE` backup folder.
    -   If a video is processed (converted), it's then split; otherwise, the original is split.
    -   Removes the original video from the input folder after processing.

5.  **`process_image` Function:**
    -   Processes image files to fit the target video's orientation and dimensions.
    -   Applies scaling, cropping, and adds blurred backgrounds with gradient fades for vertical images in horizontal videos (pillarbox) or horizontal images in vertical videos (letterbox).
    -   Saves the processed image, overwriting the original.

6.  **`process_images` Function:**
    -   Iterates through image files in the `input_folder`.
    -   Copies original images to the `SOURCE` backup folder.
    -   Calls `process_image` for each image.
    -   Moves processed images to the `RESULT` folder.

7.  **Audio File Handling:**
    -   Moves `voiceover.mp3` (if present) from the `input_folder` to the `RESULT` folder after backing it up to `SOURCE`.

8.  **Orchestration of Other Scripts (via `subprocess` calls):**
    -   **`cleaner.py`**: Called to delete video segments shorter than `segment_duration`.
    -   **`sorter.py`**: Called to organize files within the `RESULT` folder into a timestamped subfolder and rename them.
    -   **`depth.py`**: Conditionally called (if `args.depthflow == '1'`) to apply DepthFlow effects to images.
    -   **`slideshow.py`**: Called to create the final slideshow video, passing a large number of arguments derived from `cutter.py`'s own arguments.

**Internal Dependencies:**
-   Calls `cleaner.py`, `sorter.py`, `depth.py`, and `slideshow.py` as subprocesses.

**External Dependencies:**
-   `os`: For path manipulation, directory creation, file listing, and file deletion.
-   `shutil`: For copying and moving files.
-   `subprocess`: For executing FFmpeg commands and calling other Python scripts.
-   `argparse`: For parsing command-line arguments.
-   `json`: For parsing `ffprobe` output.
-   `PIL` (Pillow): `Image`, `ImageFilter`, `ImageDraw` for image processing (resizing, blurring, drawing gradients).
-   `datetime`: For generating timestamp strings.

**Inputs:**

**Command-line arguments:**
-   A comprehensive set of arguments as described in the "Argument Parsing" section above, covering almost all configurable parameters of the video processing.

**Files (read by the script):**
-   Video files (`.mp4`) from `input_folder`.
-   Image files (`.jpg`, `.jpeg`, `.png`) from `input_folder`.
-   Audio files (`.mp3`) from `input_folder` (specifically `voiceover.mp3`).
-   Outro video templates (`outro_vertical.mp4`, `outro_horizontal.mp4`) from `template_folder`.

**Outputs:**

-   **File System Modification**:
    -   Creates `RESULT` and `SOURCE` directories.
    -   Creates timestamped backup folders.
    -   Moves and processes original media files.
    -   Creates video segments.
-   **Triggers Other Scripts**: Initiates the execution of `cleaner.py`, `sorter.py`, `depth.py`, and `slideshow.py`, which in turn produce their own outputs.
-   Prints extensive status and error messages to the console.

---

**File: `depth.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for applying 3D parallax effects to images using the `DepthFlow` library. It processes images found in a specified timestamped directory, generates video segments with depth effects, and manages concurrency for this process. It also includes logic to limit the number of images processed based on a time limit and segment duration, and to delete images/videos that fall outside this limit.

**Major Logic Blocks:**

1.  **Argument Parsing:**
    -   Uses `argparse` to accept command-line arguments for the output directory (`--o`), a datetime string (`--d`), segment duration (`--sd`), and a total time limit (`--tl`).

2.  **File Filtering and Limiting:**
    -   Constructs the full path to the timestamped folder.
    -   Lists all `.jpg`, `.jpeg`, `.png` (images) and `.mp4` (videos) files within this folder.
    -   Limits the number of files to be processed based on `time_limit` and `segment_duration`.
    -   Deletes any image or video files from the disk that are not included in the `merged_paths` (i.e., those that exceed the time limit).

3.  **`combinations` Helper Function:**
    -   A utility function to generate combinations of options, used internally by `DepthFlow`.

4.  **`YourScene` Class:**
    -   A simple implementation of `DepthScene` from `DepthFlow`, defining a basic animation (sine wave for `offset_x` and `zoom`).

5.  **`DepthManager` Class:**
    -   This class (which `YourManager` inherits from) orchestrates the DepthFlow processing. It manages the depth estimator (`DepthAnythingV2`) and upscaler (`BrokenUpscaler` or `NoUpscaler`) models, handles multithreading for parallel processing of images, and defines how animations and output filenames are generated.
    -   `__attrs_post_init__`: Initializes models and sets concurrency.
    -   `parallax`: Submits an image for processing in a separate thread, managing a thread pool.
    -   `_worker`: The actual processing logic for a single image, where `DepthScene` is initialized, input image is set, animations are applied, and the video is rendered.
    -   `filename`: Determines the output video filename (e.g., `image_name_df.mp4`).
    -   `animate`: Adds various `DepthFlow` animation presets and `DepthState` parameters to the scene. It randomizes some parameters and logs the applied animations to a `_depth_log.txt` file within the `datetime_folder`.
    -   `variants`: Defines the rendering variations for `DepthFlow`, such as output height, time (duration), and FPS.

6.  **`YourManager` Class:**
    -   A concrete implementation of `DepthManager` that specifies the `variants` for rendering, setting fixed height, time, loop, and FPS.

7.  **Main Execution Block (`if __name__ == "__main__":`)**
    -   Initializes `YourManager` (with `NoUpscaler`).
    -   Iterates through image files in the `datetime_folder` and calls `manager.parallax` for each.
    -   Waits for all processing threads to complete (`manager.join()`).
    -   Prints the paths of the generated video files.

**Internal Dependencies:**
-   `Broken.Externals.Depthmap.DepthAnythingV2`: External library for depth estimation.
-   `Broken.Externals.Depthmap.DepthEstimator`: Base class for depth estimators.
-   `Broken.Externals.Upscaler.BrokenUpscaler`: External library for upscaling.
-   `Broken.Externals.Upscaler.NoUpscaler`: A placeholder upscaler.

**External Dependencies:**
-   `os`: For environment variables, path manipulation, directory creation, file listing, and file deletion.
-   `time`: For `time.sleep` in thread management.
-   `random`: For randomizing animation parameters.
-   `itertools`: For `itertools.product` in `combinations`.
-   `math`: For mathematical operations (e.g., `math.sin`).
-   `argparse`: For parsing command-line arguments.
-   `abc`: For `abstractmethod`.
-   `pathlib.Path`: For object-oriented path manipulation.
-   `threading.Thread`: For running depth processing in parallel.
-   `typing.List`, `typing.Self`, `typing.Type`: For type hinting.
-   `attr.define`, `attr.Factory`: For defining classes with attributes and default factories.
-   `click.clear`: Imported but not used.
-   `DepthFlow`: The core library for 3D parallax effects (`DepthScene`, `Motion`, `State`).
-   `dotmap.DotMap`: For flexible access to configuration objects.

**Inputs:**

**Command-line arguments:**
-   `--o` (str): Path to the output directory.
-   `--d` (str): Datetime folder name.
-   `--sd` (int): Segment duration in seconds.
-   `--tl` (int): Total time limit for the clip in seconds.

**Files (read by the script):**
-   Image files (`.jpg`, `.jpeg`, `.png`) from the `datetime_folder`.
-   Video files (`.mp4`) from the `datetime_folder` (these are deleted if they exceed the time limit).

**Outputs:**

-   **File System Modification**:
    -   Creates the `datetime_folder` if it doesn't exist.
    -   Deletes image and video files from `datetime_folder` that exceed the time limit.
    -   Creates video files (e.g., `image_name_df.mp4`) in the `datetime_folder`.
    -   Appends log entries to `_depth_log.txt` within the `datetime_folder`.
-   Prints status and error messages to the console.

---

**File: `slideshow.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for creating a video slideshow from a collection of images and video segments. It uses FFmpeg to combine these media files, apply transitions, and then calls other standalone scripts (`audio.py`, `subscribe_new.py`) as subprocesses to add audio and final overlays.

**Major Logic Blocks:**

1.  **Argument Parsing:**
    -   Uses `argparse` to accept a wide range of command-line arguments, including slide duration, time limit, outro duration, template folder, title settings, voiceover delay, watermark settings, DepthFlow enable, video orientation, chromakey settings, subtitle settings, and effect overlay settings.

2.  **Global Configuration:**
    -   Sets `target_height`, `target_width`, and `outro_video_path` based on `video_orientation`.

3.  **`create_slideshow` Function:**
    -   The main function that orchestrates the slideshow creation for a given `folder_path`.
    -   **Media Collection**: Gathers image (`.jpg`, `.jpeg`) and video (`.mp4`) files from the `folder_path`.
    -   **DepthFlow Integration**: If `args.depthflow == '1'`, it explicitly ignores `.jpg` files, assuming DepthFlow has already converted them to videos.
    -   **File Limiting**: Limits the number of media files based on `args.time_limit` and `args.slide_time`.
    -   **Outro Video**: Appends the `outro_video_path` to the list of media files.
    -   **FFmpeg Command Construction**:
        -   Builds FFmpeg input arguments for each media file (looping images, setting framerate for videos).
        -   Constructs a complex FFmpeg filter graph:
            -   Applies `zoompan` effect to images.
            -   Scales and sets framerate for videos.
            -   Chains media items with `xfade` transitions (randomly chosen from a predefined list).
            -   Conditionally applies a watermark using `drawtext` filter with `ccw` or `random` movement.
        -   Sets output video properties (pixel format, codec, CRF, preset, frames, bitrate).
    -   **Execution and Chaining**:
        -   Executes the FFmpeg command to create `slideshow.mp4`.
        -   **Calls `audio.py`**: Executes `audio.py` as a subprocess to add audio to `slideshow.mp4`.
        -   **Calls `subscribe_new.py`**: Executes `subscribe_new.py` as a subprocess to add name, watermark, and subscribe overlays.

4.  **Folder Traversal:**
    -   The script iterates through subfolders within `INPUT/RESULT` and calls `create_slideshow` for each, skipping folders that already contain `slideshow.mp4`.

**Internal Dependencies:**
-   Calls `audio.py` and `subscribe_new.py` as subprocesses.

**External Dependencies:**
-   `subprocess`: For executing FFmpeg commands and calling other Python scripts.
-   `os`: For path manipulation, directory listing, and file existence checks.
-   `argparse`: For parsing command-line arguments.
-   `random`: For selecting random transition types and watermark movement.
-   `PIL.Image`: Imported but not directly used for image manipulation in the core slideshow logic (likely remnants from earlier versions or for commented-out code).
-   `time`: For basic timing.

**Inputs:**

**Command-line arguments:**
-   A comprehensive set of arguments as described in the "Argument Parsing" section above, covering various aspects of slideshow creation, audio, and overlays.

**Files (read by the script):**
-   Image files (`.jpg`, `.jpeg`) from `folder_path`.
-   Video files (`.mp4`) from `folder_path`.
-   Outro video template (`outro_vertical.mp4` or `outro_horizontal.mp4`) from `template_folder`.
-   Font files (e.g., `Nexa Bold.otf`, `Montserrat-SemiBold.otf`) from `fonts/` directory (for watermark and title).

**Outputs:**

-   **File System Modification**:
    -   Creates `slideshow.mp4` in the `folder_path`.
-   **Triggers Other Scripts**: Initiates the execution of `audio.py` and `subscribe_new.py`, which in turn produce their own outputs (e.g., `slideshow_with_audio.mp4`, final video with overlays).
-   Prints extensive status and error messages to the console.

---

**File: `sorter.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for organizing and renaming media files within a specified output directory. It moves files into a new subfolder named after a provided datetime string and renames them sequentially, with a special case for MP3 files.

**Major Logic Blocks:**

1.  **Argument Parsing:**
    -   Uses `argparse` to accept command-line arguments for the `path` (directory containing files to be sorted) and `datetimeStr` (the name for the timestamped subfolder).

2.  **Directory Setup:**
    -   Constructs the full path to the `datetime_folder` (e.g., `output_folder/YYYY-MM-DD_HH-MM-SS`).
    -   Creates this `datetime_folder` if it doesn't already exist.

3.  **File Iteration and Renaming:**
    -   Lists all files directly within the `output_folder`.
    -   Initializes counters for each file extension to ensure sequential renaming.
    -   Iterates through each file:
        -   Skips the `datetime_folder` itself and any files without extensions.
        -   If the file is an MP3, it's renamed to `voiceover.mp3`.
        -   Otherwise, it's renamed using a sequential number (e.g., `001.ext`, `002.ext`) based on its original extension.
        -   Moves the file from the `output_folder` to the `datetime_folder` with its new name.

**Internal Dependencies:**
-   None.

**External Dependencies:**
-   `os`: For path manipulation, directory creation, and listing directory contents.
-   `shutil`: For moving files.
-   `argparse`: For parsing command-line arguments.
-   `datetime`: Imported but not directly used for generating the `datetime_str` (it's expected as an argument).

**Inputs:**

**Command-line arguments:**
-   `--o` (str): Path to the directory containing files to be sorted.
-   `--d` (str): The datetime string to be used as the name for the new subfolder.

**Files (read by the script):**
-   All files directly within the `output_folder`.

**Outputs:**

-   **File System Modification**:
    -   Creates the `datetime_folder` if it doesn't exist.
    -   Moves and renames files from `output_folder` into the `datetime_folder`.
-   Prints the old and new paths of moved files to the console.

---

**File: `srt_generator.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for generating SRT subtitle files from an audio file, specifically `adjusted_voiceover.mp3`. It uses the `WhisperX` library for speech-to-text transcription and forced alignment, and `mutagen` for audio duration. It formats the transcription into SRT format, including line wrapping based on a maximum character width.

**Major Logic Blocks:**

1.  **`get_audio_duration` Function:**
    -   Determines the duration of an MP3 file using `mutagen`.

2.  **`format_time` Function:**
    -   Converts time in seconds to the standard SRT time format (HH:MM:SS,mmm).

3.  **`transcribe_with_whisperx` Function:**
    -   The core transcription logic. It loads a `WhisperX` model, transcribes the audio, and then performs forced alignment to get precise word-level timings. It uses `int8` for compute type for stability.

4.  **`whisperx_result_to_srt` Function:**
    -   Converts the aligned transcription results from `WhisperX` into a formatted SRT string. It includes logic to wrap lines based on a `max_width` (characters per line).

5.  **`generate_srt` Function:**
    -   The main function of this module.
    -   Takes a `directory`, a `generate_srt` boolean flag, and `max_width`.
    -   Checks if `generate_srt` is true and if `adjusted_voiceover.mp3` exists in the specified `directory`.
    -   Creates a `subs` subdirectory within the `directory` if it doesn't exist.
    -   Calls `transcribe_with_whisperx` to get the transcription.
    -   Calls `whisperx_result_to_srt` to format the transcription.
    -   Saves the generated SRT content to `voiceover.srt` in the `subs` directory.
    -   Includes a check to skip generation if the SRT file already exists.

6.  **Main Execution Block (`if __name__ == "__main__":`)**
    -   Parses command-line arguments for `directory`, `generate_srt`, and `subtitle_max_width`.
    -   Calls `generate_srt` with the parsed arguments.

**Internal Dependencies:**
-   None.

**External Dependencies:**
-   `os`: For path manipulation, file existence checks, and directory creation.
-   `argparse`: For parsing command-line arguments.
-   `whisperx`: The primary library for audio transcription and alignment.
-   `certifi`: Used to set `SSL_CERT_FILE` environment variable.
-   `mutagen.mp3`: For getting MP3 audio durations.

**Inputs:**

**Command-line arguments:**
-   `--i` (str): Directory containing the `adjusted_voiceover.mp3` file.
-   `--srt` (str): Flag to generate SRT subtitles ('0' or '1').
-   `--smaxw` (int): Maximum characters in one line of subtitles.

**Files (read by the script):**
-   `adjusted_voiceover.mp3` from the specified `directory`.

**Outputs:**

-   **File System Modification**:
    -   Creates a `subs` subdirectory within the input `directory`.
    -   Creates `voiceover.srt` within the `subs` directory.
-   Prints status and error messages to the console.

---

**File: `subscribe_new.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for applying various final overlays to a video that already has audio. These overlays include a subscribe/like animation, a text title, and an optional general effect overlay. It also handles rendering SRT subtitles onto the video. It uses FFmpeg's complex filter graphs to layer these elements.

**Major Logic Blocks:**

1.  **`get_font_name` Function:**
    -   A utility function (copied from `font_utils.py`) to extract the full font name from a font file using `fontTools.ttLib.TTFont`.

2.  **Argument Parsing:**
    -   Uses `argparse` to accept a wide range of command-line arguments, covering input/template folders, title settings, effect overlay settings, chromakey settings, subtitle settings, and video orientation.

3.  **Video and Overlay Path Resolution:**
    -   Determines the correct subscribe overlay video (`name_subscribe_like.mp4` or `name_subscribe_like_horizontal.mp4`) based on `video_orientation`.
    -   Constructs paths for input and output videos.

4.  **Duration Retrieval:**
    -   Uses `ffprobe` to get the duration of the subscribe overlay video and the main input video.

5.  **Overlay Application Logic:**
    -   **Title Text Styling**: Handles font color selection (including 'random'), font size, and constructs the `fontfile` path for the title text.
    -   **Subtitle Styling**: If `generate_srt` is enabled, it prepares the subtitle styling parameters for FFmpeg's `subtitles` filter. This involves:
        -   Resolving the font path and name for subtitles (checking local `fonts/` and system fonts).
        -   Converting hex colors (RGB to BGR) and handling opacity for ASS-style parameters.
        -   Constructing the `force_style` string for the `subtitles` filter.
    -   **FFmpeg Filter Complex Construction**:
        -   **Audio Mix**: Mixes the subscribe overlay's audio with the main video's audio (with a delay).
        -   **Video Base**: Sets the main video stream and applies chromakey to the subscribe overlay video, then overlays it onto the main video.
        -   **Effect Overlay (Conditional)**: If `effect_overlay` is specified and exists, it adds the effect overlay. It supports different blend modes (`normal`, `overlay`, `screen`, etc.) and opacity.
        -   **Title Text Overlay**: Adds the title text using FFmpeg's `drawtext` filter, with timing based on `delay`, `title_appearance_delay`, and `title_visible_time`.
        -   **Subtitle Rendering (Conditional)**: If `generate_srt` is enabled and the SRT file exists, it adds the `subtitles` filter to render the subtitles.
    -   **FFmpeg Command Execution**: Constructs and executes the final FFmpeg command to apply all overlays and render subtitles, saving the output to `output_video`.

**Internal Dependencies:**
-   None (the `get_font_name` function is embedded directly).

**External Dependencies:**
-   `subprocess`: For executing FFmpeg commands.
-   `os`: For path manipulation, file existence checks.
-   `random`: For random font colors.
-   `argparse`: For parsing command-line arguments.
-   `time`: For basic timing.
-   `json`: For parsing `ffprobe` output.
-   `glob`: For finding font files.
-   `fontTools.ttLib.TTFont`: For extracting font names.

**Inputs:**

**Command-line arguments:**
-   `--i` (str): Path to the directory containing input files.
-   `--tpl` (str): Path to the template folder.
-   `--t` (str): Video title.
-   `--tf` (str): Title font filename.
-   `--tfs` (int): Title font size.
-   `--tfc` (str): Title font color (hex or 'random').
-   `--osd` (int): Delay before overlay appears.
-   `--tad` (int): Delay before title appears.
-   `--tvt` (int): Title visible time.
-   `--tyo` (int): Title Y offset.
-   `--txo` (int): Title X offset.
-   `--effect` (str): Effect overlay filename.
-   `--effect-opacity` (float): Effect opacity.
-   `--effect-blend` (str): Effect blend mode.
-   `--chr` (str): Chromakey color.
-   `--cs` (float): Chromakey similarity.
-   `--cb` (float): Chromakey blend.
-   `--srt` (str): Flag to add SRT subtitles ('0' or '1').
-   `--sf` (str): Subtitle font.
-   `--sfs` (int): Subtitle font size.
-   `--sfc` (str): Subtitle font color.
-   `--sbc` (str): Subtitle background color.
-   `--sbo` (float): Subtitle background opacity.
-   `--spos` (int): Subtitle position.
-   `--sout` (float): Subtitle outline thickness.
-   `--soutc` (str): Subtitle outline color.
-   `--shadow` (int): Enable subtitle shadow ('0' or '1').
-   `--o` (str): Video orientation ('vertical' or 'horizontal').

**Files (read by the script):**
-   `slideshow_with_audio.mp4` from `input_dir`.
-   `name_subscribe_like.mp4` or `name_subscribe_like_horizontal.mp4` from `template_folder`.
-   Optional `effect_overlay` video from `effects/` folder.
-   `voiceover.srt` from `input_dir/subs/` (if `generate_srt` is enabled).
-   Font files from `fonts/` directory or system fonts.

**Outputs:**

-   **File System Modification**:
    -   Creates the final output video file in `input_dir`.
-   Prints extensive status and error messages to the console.

---

**File: `subscribe.py`**

**Core Purpose and Logic:**
This script is an older, monolithic component responsible for applying various final overlays to a video that already has audio. These overlays include a subscribe/like animation and a text title. It also handles rendering SRT subtitles onto the video. It uses FFmpeg's complex filter graphs to layer these elements.

**Major Logic Blocks:**

1.  **`get_font_name` Function:**
    -   A utility function (copied from `font_utils.py`) to extract the full font name from a font file using `fontTools.ttLib.TTFont`.

2.  **Argument Parsing:**
    -   Uses `argparse` to accept command-line arguments for input/template folders, title settings, chromakey settings, subtitle settings, and video orientation.
    -   *Note*: This version (`subscribe.py`) lacks the `effect_overlay` arguments present in `subscribe_new.py`.

3.  **Video and Overlay Path Resolution:**
    -   Determines the correct subscribe overlay video (`name_subscribe_like.mp4` or `name_subscribe_like_horizontal.mp4`) based on `video_orientation`.
    -   Constructs paths for input and output videos.

4.  **Duration Retrieval:**
    -   Uses `ffprobe` to get the duration of the subscribe overlay video and the main input video.

5.  **Overlay Application Logic:**
    -   **Title Text Styling**: Handles font color selection (including 'random'), font size, and constructs the `fontfile` path for the title text.
    -   **Subtitle Styling**: If `generate_srt` is enabled, it prepares the subtitle styling parameters for FFmpeg's `subtitles` filter. This involves:
        -   Resolving the font path and name for subtitles (checking local `fonts/` and system fonts).
        -   Converting hex colors (RGB to BGR) and handling opacity for ASS-style parameters.
        -   Constructing the `force_style` string for the `subtitles` filter.
    -   **FFmpeg Filter Complex Construction**:
        -   **Audio Mix**: Mixes the subscribe overlay's audio with the main video's audio (with a delay).
        -   **Video Base**: Sets the main video stream and applies chromakey to the subscribe overlay video, then overlays it onto the main video.
        -   **Title Text Overlay**: Adds the title text using FFmpeg's `drawtext` filter, with timing based on `delay`, `title_appearance_delay`, and `title_visible_time`.
        -   **Subtitle Rendering (Conditional)**: If `generate_srt` is enabled and the SRT file exists, it adds the `subtitles` filter to render the subtitles.
    -   **FFmpeg Command Execution**: Constructs and executes the final FFmpeg command to apply all overlays and render subtitles, saving the output to `output_video`.

**Internal Dependencies:**
-   None (the `get_font_name` function is embedded directly).

**External Dependencies:**
-   `subprocess`: For executing FFmpeg commands.
-   `os`: For path manipulation, file existence checks.
-   `random`: For random font colors.
-   `argparse`: For parsing command-line arguments.
-   `time`: For basic timing.
-   `json`: For parsing `ffprobe` output.
-   `glob`: For finding font files.
-   `fontTools.ttLib.TTFont`: For extracting font names.

**Inputs:**

**Command-line arguments:**
-   `--i` (str): Path to the directory containing input files.
-   `--tpl` (str): Path to the template folder.
-   `--t` (str): Video title.
-   `--tf` (str): Title font filename.
-   `--tfs` (int): Title font size.
-   `--tfc` (str): Title font color (hex or 'random').
-   `--osd` (int): Delay before overlay appears.
-   `--tad` (int): Delay before title appears.
-   `--tvt` (int): Title visible time.
-   `--tyo` (int): Title Y offset.
-   `--txo` (int): Title X offset.
-   `--chr` (str): Chromakey color.
-   `--cs` (float): Chromakey similarity.
-   `--cb` (float): Chromakey blend.
-   `--srt` (str): Flag to add SRT subtitles ('0' or '1').
-   `--sf` (str): Subtitle font.
-   `--sfs` (int): Subtitle font size.
-   `--sfc` (str): Subtitle font color.
-   `--sbc` (str): Subtitle background color.
-   `--sbo` (float): Subtitle background opacity.
-   `--spos` (int): Subtitle position.
-   `--sout` (float): Subtitle outline thickness.
   `--soutc` (str): Subtitle outline color.
-   `--shadow` (int): Enable subtitle shadow ('0' or '1').
-   `--o` (str): Video orientation ('vertical' or 'horizontal').

**Files (read by the script):**
-   `slideshow_with_audio.mp4` from `input_dir`.
-   `name_subscribe_like.mp4` or `name_subscribe_like_horizontal.mp4` from `template_folder`.
-   `voiceover.srt` from `input_dir/subs/` (if `generate_srt` is enabled).
-   Font files from `fonts/` directory or system fonts.

**Outputs:**

-   **File System Modification**:
    -   Creates the final output video file in `input_dir`.
-   Prints extensive status and error messages to the console.
