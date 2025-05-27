import tkinter as tk
from tkinter import ttk
from videocutter.utils import gui_config_manager as gcm
from videocutter.gui import gui_utils

class SubtitleSettingsFrame(ttk.Frame):
    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        self._after_id = None # For debouncing preview updates
        self._initialize_variables()
        self.create_widgets()
        self.update_all_subtitle_controls() # Initial update of controls

    def _initialize_variables(self):
        """Initialize subtitle-related variables"""
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
        self.gui_elements['var_generate_srt'] = tk.BooleanVar(value=gcm.generate_srt)
        self.gui_elements['var_subtitle_font'] = tk.StringVar(self.gui_elements['root'], value=gcm.subtitle_font)
        self.gui_elements['var_subtitle_fontsize'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_fontsize)
        self.gui_elements['var_subtitle_fontcolor'] = tk.StringVar(self.gui_elements['root'], value=gcm.subtitle_fontcolor)
        self.gui_elements['var_subtitle_bgcolor'] = tk.StringVar(self.gui_elements['root'], value=gcm.subtitle_bgcolor)
        self.gui_elements['var_subtitle_bgopacity'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.subtitle_bgopacity)
        self.gui_elements['var_subtitle_position'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_position)
        self.gui_elements['var_subtitle_outline'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.subtitle_outline)
        self.gui_elements['var_subtitle_outlinecolor'] = tk.StringVar(self.gui_elements['root'], value=gcm.subtitle_outlinecolor)
        self.gui_elements['var_subtitle_shadow'] = tk.BooleanVar(self.gui_elements['root'], value=gcm.subtitle_shadow)
        self.gui_elements['var_subtitle_format'] = tk.StringVar(self.gui_elements['root'], value='ass') # Always ASS

        # New ASS subtitle style variables
        self.gui_elements['var_subtitle_secondary_color'] = tk.StringVar(self.gui_elements['root'], value=gcm.subtitle_secondary_color)
        self.gui_elements['var_subtitle_bold'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_bold)
        self.gui_elements['var_subtitle_italic'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_italic)
        self.gui_elements['var_subtitle_underline'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_underline)
        self.gui_elements['var_subtitle_strikeout'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_strikeout)
        self.gui_elements['var_subtitle_scale_x'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_scale_x)
        self.gui_elements['var_subtitle_scale_y'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_scale_y)
        self.gui_elements['var_subtitle_spacing'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.subtitle_spacing)
        self.gui_elements['var_subtitle_angle'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_angle)
        self.gui_elements['var_subtitle_border_style'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_border_style)
        self.gui_elements['var_subtitle_shadow_distance'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.subtitle_shadow_distance)
        self.gui_elements['var_subtitle_margin_l'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_margin_l)
        self.gui_elements['var_subtitle_margin_r'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_margin_r)
        self.gui_elements['var_subtitle_margin_v'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_margin_v)
        self.gui_elements['var_subtitle_encoding'] = tk.IntVar(self.gui_elements['root'], value=gcm.subtitle_encoding)

    def create_widgets(self):
        """Setup the subtitles tab layout"""
        subtitle_frame = self # Use self as the frame
        subtitle_frame.pack(fill="both", expand=True)

        # Left column for settings
        subtitle_settings = tk.LabelFrame(subtitle_frame, text="Subtitle Settings", padx=10, pady=10)
        # Configure grid for two columns and two rows in the subtitle_frame
        subtitle_frame.grid_columnconfigure(0, weight=1) # Left column for basic settings
        subtitle_frame.grid_columnconfigure(1, weight=1) # Right column for advanced settings and preview
        subtitle_frame.grid_rowconfigure(0, weight=1) # Top row for settings
        subtitle_frame.grid_rowconfigure(1, weight=1) # Bottom row for preview

        # Left column for basic settings
        subtitle_settings_basic = tk.LabelFrame(subtitle_frame, text="Basic Subtitle Settings", padx=10, pady=10)
        subtitle_settings_basic.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        # Add Enable Subtitles checkbox to subtitle_settings_basic
        tk.Checkbutton(subtitle_settings_basic, text="Enable Subtitles", variable=self.gui_elements['var_generate_srt'], command=self.toggle_subtitle_controls).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Subtitle line max width
        tk.Label(subtitle_settings_basic, text="Characters per line (max):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_subtitle_max_width = tk.Entry(subtitle_settings_basic, width=10) # Adjusted width
        self.gui_elements['entry_subtitle_max_width'] = entry_subtitle_max_width # Add to gui_elements
        entry_subtitle_max_width.insert(0, gcm.subtitle_maxwidth)
        entry_subtitle_max_width.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        entry_subtitle_max_width.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Font settings
        tk.Label(subtitle_settings_basic, text="Font:").grid(row=2, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        font_dropdown = ttk.Combobox(subtitle_settings_basic, textvariable=self.gui_elements['var_subtitle_font'], values=self.gui_elements['available_fonts'], width=25)
        self.gui_elements['font_dropdown'] = font_dropdown # Add to gui_elements
        font_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5) # Adjusted row
        font_dropdown.bind("<<ComboboxSelected>>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Font size with slider and numeric display
        font_size_frame = tk.Frame(subtitle_settings_basic)
        font_size_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

        tk.Label(subtitle_settings_basic, text="Font Size:").grid(row=3, column=0, sticky="w", padx=5, pady=5) # Adjusted row
        font_size_slider = ttk.Scale(font_size_frame, from_=12, to=150, variable=self.gui_elements['var_subtitle_fontsize'], orient="horizontal")
        self.gui_elements['font_size_slider'] = font_size_slider # Add to gui_elements
        font_size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        font_size_slider.bind("<ButtonRelease-1>", lambda e: (gui_utils.update_slider_value(self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_value_entry']), gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))) # Use debounced update

        font_size_value_entry = tk.Entry(font_size_frame, width=4)
        self.gui_elements['font_size_value_entry'] = font_size_value_entry # Add to gui_elements
        font_size_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        font_size_value_entry.insert(0, str(self.gui_elements['var_subtitle_fontsize'].get()))
        font_size_value_entry.bind("<Return>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['font_size_value_entry'], self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_slider'], 12, 150, self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))
        font_size_value_entry.bind("<FocusOut>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['font_size_value_entry'], self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_slider'], 12, 150, self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(subtitle_settings_basic, text="Text Color:").grid(row=4, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        text_color_entry = tk.Entry(subtitle_settings_basic, textvariable=self.gui_elements['var_subtitle_fontcolor'], width=10)
        self.gui_elements['text_color_entry'] = text_color_entry # Add to gui_elements
        text_color_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5) # Adjusted row
        text_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Secondary Color
        tk.Label(subtitle_settings_basic, text="Secondary Color:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        secondary_color_entry = tk.Entry(subtitle_settings_basic, textvariable=self.gui_elements['var_subtitle_secondary_color'], width=10)
        self.gui_elements['secondary_color_entry'] = secondary_color_entry
        secondary_color_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        secondary_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Outline thickness with slider and numeric display
        outline_frame = tk.Frame(subtitle_settings_basic)
        outline_frame.grid(row=6, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

        tk.Label(subtitle_settings_basic, text="Outline Thickness:").grid(row=6, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        outline_slider = ttk.Scale(outline_frame, from_=0, to=4, variable=self.gui_elements['var_subtitle_outline'], orient="horizontal")
        self.gui_elements['outline_slider'] = outline_slider # Add to gui_elements
        outline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        outline_slider.bind("<ButtonRelease-1>", lambda e: (gui_utils.update_slider_value(self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_value_entry']), gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))) # Use debounced update

        outline_value_entry = tk.Entry(outline_frame, width=4)
        self.gui_elements['outline_value_entry'] = outline_value_entry # Add to gui_elements
        outline_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        outline_value_entry.insert(0, str(self.gui_elements['var_subtitle_outline'].get()))
        outline_value_entry.bind("<Return>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['outline_value_entry'], self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_slider'], 0, 4, self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))
        outline_value_entry.bind("<FocusOut>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['outline_value_entry'], self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_slider'], 0, 4, self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(subtitle_settings_basic, text="Outline Color:").grid(row=7, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        outline_color_entry = tk.Entry(subtitle_settings_basic, textvariable=self.gui_elements['var_subtitle_outlinecolor'], width=10)
        self.gui_elements['outline_color_entry'] = outline_color_entry # Add to gui_elements
        outline_color_entry.grid(row=7, column=1, sticky="w", padx=5, pady=5) # Adjusted row
        outline_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Shadow checkbox
        shadow_frame = tk.Frame(subtitle_settings_basic)
        shadow_frame.grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5) # Adjusted row
        shadow_checkbox = tk.Checkbutton(shadow_frame, text="Enable Text Shadow", variable=self.gui_elements['var_subtitle_shadow'], command=self.toggle_subtitle_shadow_controls) # Use debounced update
        self.gui_elements['shadow_checkbox'] = shadow_checkbox # Add to gui_elements
        shadow_checkbox.pack(anchor="w")

        tk.Label(subtitle_settings_basic, text="Shadow Color:").grid(row=9, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        bg_color_entry = tk.Entry(subtitle_settings_basic, textvariable=self.gui_elements['var_subtitle_bgcolor'], width=10)
        self.gui_elements['bg_color_entry'] = bg_color_entry # Add to gui_elements
        bg_color_entry.grid(row=9, column=1, sticky="w", padx=5, pady=5) # Adjusted row
        bg_color_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))) # Use debounced update

        # Background opacity with slider and numeric display
        bg_opacity_frame = tk.Frame(subtitle_settings_basic)
        bg_opacity_frame.grid(row=10, column=1, sticky="ew", padx=5, pady=5) # Adjusted row

        tk.Label(subtitle_settings_basic, text="Shadow Opacity:").grid(row=10, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        bg_opacity_slider = ttk.Scale(bg_opacity_frame, from_=0, to=1, variable=self.gui_elements['var_subtitle_bgopacity'], orient="horizontal")
        self.gui_elements['bg_opacity_slider'] = bg_opacity_slider # Add to gui_elements
        bg_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        bg_opacity_slider.bind("<ButtonRelease-1>", lambda e: (gui_utils.update_slider_value(self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_value_entry']), gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))) # Use debounced update

        bg_opacity_value_entry = tk.Entry(bg_opacity_frame, width=4)
        self.gui_elements['bg_opacity_value_entry'] = bg_opacity_value_entry # Add to gui_elements
        bg_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        bg_opacity_value_entry.insert(0, str(self.gui_elements['var_subtitle_bgopacity'].get()))
        bg_opacity_value_entry.bind("<Return>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['bg_opacity_value_entry'], self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_slider'], 0, 1, self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))
        bg_opacity_value_entry.bind("<FocusOut>", lambda e: gui_utils.update_slider_from_entry(self.gui_elements['bg_opacity_value_entry'], self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_slider'], 0, 1, self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Position selection
        tk.Label(subtitle_settings_basic, text="Position:").grid(row=11, column=0, padx=5, pady=5, sticky="w") # Adjusted row
        position_frame = tk.Frame(subtitle_settings_basic)
        position_frame.grid(row=11, column=1, sticky="w", padx=5, pady=5) # Adjusted row

        # Create a frame for the 9 radio buttons
        position_grid_frame = tk.Frame(position_frame)
        position_grid_frame.pack(fill="both", expand=True)

        # Define the ASS alignment values and their corresponding labels/grid positions
        # ASS Alignment:
        # 7 8 9 (Top Left, Top Center, Top Right)
        # 4 5 6 (Middle Left, Middle Center, Middle Right)
        # 1 2 3 (Bottom Left, Bottom Center, Bottom Right)
        ass_positions = [
            (7, "Top Left", 0, 0), (8, "Top Center", 0, 1), (9, "Top Right", 0, 2),
            (4, "Middle Left", 1, 0), (5, "Middle Center", 1, 1), (6, "Middle Right", 1, 2),
            (1, "Bottom Left", 2, 0), (2, "Bottom Center", 2, 1), (3, "Bottom Right", 2, 2)
        ]

        # Create 9 radio buttons
        for ass_val, label, row, col in ass_positions:
            rb = tk.Radiobutton(
                position_grid_frame,
                text="",
                variable=self.gui_elements['var_subtitle_position'],
                value=ass_val,
                command=lambda: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))
            )
            rb.grid(row=row, column=col, sticky="w", padx=2, pady=2)
            # Store radio button for potential future access if needed
            self.gui_elements[f'rb_subtitle_position_{ass_val}'] = rb

        # Ensure the correct radio button is selected initially
        initial_pos_val = self.gui_elements['var_subtitle_position'].get()
        for ass_val, label, row, col in ass_positions:
            if ass_val == initial_pos_val:
                self.gui_elements['var_subtitle_position'].set(ass_val) # Explicitly set to trigger update if needed
                break

        # Right column for advanced settings
        subtitle_settings_advanced = tk.LabelFrame(subtitle_frame, text="Advanced Subtitle Settings", padx=10, pady=10)
        subtitle_settings_advanced.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Bold, Italic, Underline, StrikeOut
        font_style_frame = tk.LabelFrame(subtitle_settings_advanced, text="Font Style", padx=5, pady=5)
        font_style_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.gui_elements['font_style_frame'] = font_style_frame # Add to gui_elements

        tk.Checkbutton(font_style_frame, text="Bold", variable=self.gui_elements['var_subtitle_bold'], onvalue=-1, offvalue=0, command=lambda: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(font_style_frame, text="Italic", variable=self.gui_elements['var_subtitle_italic'], onvalue=-1, offvalue=0, command=lambda: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(font_style_frame, text="Underline", variable=self.gui_elements['var_subtitle_underline'], onvalue=-1, offvalue=0, command=lambda: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(font_style_frame, text="StrikeOut", variable=self.gui_elements['var_subtitle_strikeout'], onvalue=-1, offvalue=0, command=lambda: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))).pack(side=tk.LEFT, padx=5)

        # ScaleX, ScaleY
        scale_frame = tk.LabelFrame(subtitle_settings_advanced, text="Scaling", padx=5, pady=5)
        scale_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.gui_elements['scale_frame'] = scale_frame # Add to gui_elements

        tk.Label(scale_frame, text="Scale X (%):").pack(side=tk.LEFT, padx=5)
        scale_x_entry = tk.Entry(scale_frame, textvariable=self.gui_elements['var_subtitle_scale_x'], width=5)
        scale_x_entry.pack(side=tk.LEFT, padx=5)
        scale_x_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(scale_frame, text="Scale Y (%):").pack(side=tk.LEFT, padx=5)
        scale_y_entry = tk.Entry(scale_frame, textvariable=self.gui_elements['var_subtitle_scale_y'], width=5)
        scale_y_entry.pack(side=tk.LEFT, padx=5)
        scale_y_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Spacing
        tk.Label(subtitle_settings_advanced, text="Spacing (px):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        spacing_entry = tk.Entry(subtitle_settings_advanced, textvariable=self.gui_elements['var_subtitle_spacing'], width=10)
        self.gui_elements['spacing_entry'] = spacing_entry
        spacing_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        spacing_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Angle
        tk.Label(subtitle_settings_advanced, text="Angle (deg):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        angle_entry = tk.Entry(subtitle_settings_advanced, textvariable=self.gui_elements['var_subtitle_angle'], width=10)
        self.gui_elements['angle_entry'] = angle_entry
        angle_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        angle_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # BorderStyle
        tk.Label(subtitle_settings_advanced, text="Border Style:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        border_style_options = [1, 3] # 1: Outline+Shadow, 3: Opaque Box
        border_style_dropdown = ttk.Combobox(subtitle_settings_advanced, textvariable=self.gui_elements['var_subtitle_border_style'], values=border_style_options, width=10)
        self.gui_elements['border_style_dropdown'] = border_style_dropdown
        border_style_dropdown.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        border_style_dropdown.bind("<<ComboboxSelected>>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Shadow Distance
        tk.Label(subtitle_settings_advanced, text="Shadow Distance:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        shadow_distance_entry = tk.Entry(subtitle_settings_advanced, textvariable=self.gui_elements['var_subtitle_shadow_distance'], width=10)
        self.gui_elements['shadow_distance_entry'] = shadow_distance_entry
        shadow_distance_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        shadow_distance_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Margins
        margins_frame = tk.LabelFrame(subtitle_settings_advanced, text="Margins", padx=5, pady=5)
        margins_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.gui_elements['margins_frame'] = margins_frame # Add to gui_elements

        tk.Label(margins_frame, text="Left:").pack(side=tk.LEFT, padx=5)
        margin_l_entry = tk.Entry(margins_frame, textvariable=self.gui_elements['var_subtitle_margin_l'], width=5)
        margin_l_entry.pack(side=tk.LEFT, padx=5)
        margin_l_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(margins_frame, text="Right:").pack(side=tk.LEFT, padx=5)
        margin_r_entry = tk.Entry(margins_frame, textvariable=self.gui_elements['var_subtitle_margin_r'], width=5)
        margin_r_entry.pack(side=tk.LEFT, padx=5)
        margin_r_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        tk.Label(margins_frame, text="Vertical:").pack(side=tk.LEFT, padx=5)
        margin_v_entry = tk.Entry(margins_frame, textvariable=self.gui_elements['var_subtitle_margin_v'], width=5)
        margin_v_entry.pack(side=tk.LEFT, padx=5)
        margin_v_entry.bind("<KeyRelease>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))

        # Encoding
        tk.Label(subtitle_settings_advanced, text="Encoding:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        encoding_options = [0, 1] # 0: ANSI, 1: Default (UTF-8)
        encoding_dropdown = ttk.Combobox(subtitle_settings_advanced, textvariable=self.gui_elements['var_subtitle_encoding'], values=encoding_options, width=10)
        self.gui_elements['encoding_dropdown'] = encoding_dropdown
        encoding_dropdown.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        encoding_dropdown.bind("<<ComboboxSelected>>", lambda e: gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements)))


        # Right column for preview
        preview_frame = tk.LabelFrame(subtitle_frame, text="Preview", padx=10, pady=10)
        preview_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10) # Moved to bottom-right
        self.gui_elements['preview_frame'] = preview_frame # Add preview_frame to gui_elements
        
        # Preview label
        self.gui_elements['preview_label'] = tk.Label(preview_frame)
        self.gui_elements['preview_label'].pack(padx=10, pady=10)
            
        # Configure grid weights
        subtitle_frame.grid_columnconfigure(0, weight=1)
        subtitle_frame.grid_columnconfigure(1, weight=1)
        subtitle_frame.grid_rowconfigure(0, weight=1) # Top row for settings
        subtitle_frame.grid_rowconfigure(1, weight=1) # Bottom row for preview

    def toggle_subtitle_controls(self, *args):
        """Toggle subtitle controls based on enable_subtitles checkbox"""
        state = tk.NORMAL if self.gui_elements['var_generate_srt'].get() else tk.DISABLED
        
        controls = [
            'entry_subtitle_max_width',
            'font_dropdown',
            'font_size_slider',
            'font_size_value_entry',
            'text_color_entry',
            'secondary_color_entry',
            'outline_slider',
            'outline_value_entry',
            'outline_color_entry',
            'shadow_checkbox',
            'bg_color_entry',
            'bg_opacity_slider',
            'bg_opacity_value_entry',
            'position_grid_frame', # This is a frame, need to iterate its children
            'spacing_entry',
            'angle_entry',
            'border_style_dropdown',
            'shadow_distance_entry',
            'encoding_dropdown'
        ]
        
        for control_name in controls:
            if control_name in self.gui_elements:
                widget = self.gui_elements[control_name]
                if isinstance(widget, tk.Frame): # Handle frames by iterating children
                    for child in widget.winfo_children():
                        child.config(state=state)
                else:
                    widget.config(state=state)
        
        # Special handling for font style checkboxes (Bold, Italic, Underline, StrikeOut)
        font_style_frame = self.gui_elements['font_style_frame'] # Assuming this is stored
        if font_style_frame:
            for child in font_style_frame.winfo_children():
                child.config(state=state)

        # Special handling for scaling entries (ScaleX, ScaleY)
        scale_frame = self.gui_elements['scale_frame'] # Assuming this is stored
        if scale_frame:
            for child in scale_frame.winfo_children():
                child.config(state=state)

        # Special handling for margins entries
        margins_frame = self.gui_elements['margins_frame'] # Assuming this is stored
        if margins_frame:
            for child in margins_frame.winfo_children():
                child.config(state=state)

        self.toggle_subtitle_shadow_controls() # Update shadow controls based on new state
        gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))

    def toggle_subtitle_shadow_controls(self, *args):
        """Toggle shadow color and opacity controls based on shadow checkbox"""
        # Only enable/disable if the main subtitle controls are enabled
        if self.gui_elements['var_generate_srt'].get():
            state = tk.NORMAL if self.gui_elements['var_subtitle_shadow'].get() else tk.DISABLED
        else:
            state = tk.DISABLED # If subtitles are disabled, shadow controls are always disabled

        self.gui_elements['bg_color_entry'].config(state=state)
        self.gui_elements['bg_opacity_slider'].config(state=state)
        self.gui_elements['bg_opacity_value_entry'].config(state=state)
            
        gui_utils.schedule_subtitle_preview_update(
            self.gui_elements['root'], 
            lambda: gui_utils.update_subtitle_preview(self.gui_elements)
        )

    def update_all_subtitle_controls(self):
        """Updates all subtitle-related controls after config load"""
        # Update slider value entries
        gui_utils.update_slider_value(self.gui_elements['var_subtitle_fontsize'], self.gui_elements['font_size_value_entry'])
        gui_utils.update_slider_value(self.gui_elements['var_subtitle_bgopacity'], self.gui_elements['bg_opacity_value_entry'])
        gui_utils.update_slider_value(self.gui_elements['var_subtitle_outline'], self.gui_elements['outline_value_entry'])
        
        # Ensure the correct radio button for position is selected
        initial_pos_val = self.gui_elements['var_subtitle_position'].get()
        for ass_val, label, row, col in [
            (7, "Top Left", 0, 0), (8, "Top Center", 0, 1), (9, "Top Right", 0, 2),
            (4, "Middle Left", 1, 0), (5, "Middle Center", 1, 1), (6, "Middle Right", 1, 2),
            (1, "Bottom Left", 2, 0), (2, "Bottom Center", 2, 1), (3, "Bottom Right", 2, 2)
        ]:
            rb = self.gui_elements[f'rb_subtitle_position_{ass_val}']
            if ass_val == initial_pos_val:
                rb.select()
            else:
                rb.deselect()

        # Toggle controls based on current state
        self.toggle_subtitle_controls()
        # The toggle_subtitle_controls will call toggle_subtitle_shadow_controls internally
        
        # Schedule initial preview update
        gui_utils.schedule_subtitle_preview_update(self.gui_elements['root'], lambda: gui_utils.update_subtitle_preview(self.gui_elements))
