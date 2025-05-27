import tkinter as tk
from tkinter import ttk
from videocutter.utils import gui_config_manager as gcm # Import the new config manager

class TitleSettingsFrame(ttk.Frame):
    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        self.create_widgets()

    def toggle_title_controls(self, *args):
        state = tk.NORMAL if self.gui_elements['var_enable_title'].get() else tk.DISABLED
        self.gui_elements['entry_title'].config(state=state)
        self.gui_elements['entry_title_font'].config(state=state)
        self.gui_elements['entry_title_fontcolor'].config(state=state)
        self.gui_elements['entry_calculated_title_font_size'].config(state=state)
        self.gui_elements['entry_title_font_size'].config(state=state)
        self.gui_elements['entry_title_appearance_delay'].config(state=state)
        self.gui_elements['entry_title_visible_time'].config(state=state)
        self.gui_elements['entry_title_x_offset'].config(state=state)
        self.gui_elements['entry_title_y_offset'].config(state=state)
        self.gui_elements['title_opacity_slider'].config(state=state)
        self.gui_elements['title_opacity_value_entry'].config(state=state)
        self.gui_elements['title_background_checkbox'].config(state=state)
        self.gui_elements['title_background_color_entry'].config(state=state)
        self.gui_elements['title_background_opacity_slider'].config(state=state)
        self.gui_elements['title_background_opacity_value_entry'].config(state=state)
        self.gui_elements['enable_title_video_overlay_checkbox'].config(state=state)
        self.gui_elements['entry_title_video_overlay_file'].config(state=state)
        self.gui_elements['entry_title_video_overlay_delay'].config(state=state)
        self.gui_elements['entry_title_video_chromakey_color'].config(state=state)
        self.gui_elements['entry_title_video_chromakey_similarity'].config(state=state)
        self.gui_elements['entry_title_video_chromakey_blend'].config(state=state)

        self.gui_elements['entry_title_font']['state'] = state
        self.gui_elements['entry_title_fontcolor']['state'] = state
        self.gui_elements['entry_title_video_overlay_file']['state'] = state

    def update_font_size(self, event):
        title = self.gui_elements['entry_title'].get()
        length = len(title)
        if length <= 10:
            calculated_title_font_size = 90
        elif 11 <= length <= 14:
            calculated_title_font_size = 80
        elif 15 <= length <= 18:
            calculated_title_font_size = 70
        else:
            calculated_title_font_size = 65
        self.gui_elements['entry_calculated_title_font_size'].config(state=tk.NORMAL)
        self.gui_elements['entry_calculated_title_font_size'].delete(0, tk.END)
        self.gui_elements['entry_calculated_title_font_size'].insert(0, calculated_title_font_size)
        self.gui_elements['entry_calculated_title_font_size'].config(state=tk.DISABLED)

    def create_widgets(self):
        # Left column for text title settings
        text_title_column = tk.Frame(self)
        text_title_column.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Right column for video title overlay settings
        video_title_column = tk.Frame(self)
        video_title_column.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Text Title Settings (moved from Main Settings tab)
        title_frame = tk.LabelFrame(text_title_column, text="Text Title Settings", padx=10, pady=5)
        title_frame.pack(fill="both", expand=True)

        tk.Checkbutton(title_frame, text="Enable Text Title", variable=self.gui_elements['var_enable_title'], command=self.toggle_title_controls).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tk.Label(title_frame, text="Title:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_title = tk.Entry(title_frame, width=30)
        entry_title.insert(0, gcm.title)
        entry_title.grid(row=1, column=1, padx=10, pady=5)
        entry_title.bind("<KeyRelease>", self.update_font_size)
        self.gui_elements['entry_title'] = entry_title # Store in gui_elements

        tk.Label(title_frame, text="Font:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_title_font = tk.OptionMenu(title_frame, self.gui_elements['var_title_font'], *self.gui_elements['available_fonts'])
        entry_title_font.config(width=20)
        entry_title_font.grid(row=2, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_font'] = entry_title_font # Store in gui_elements

        tk.Label(title_frame, text="Color:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_title_fontcolor = tk.OptionMenu(title_frame, self.gui_elements['var_title_fontcolor'], *self.gui_elements['font_colors'])
        entry_title_fontcolor.config(width=10)
        entry_title_fontcolor.grid(row=3, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_fontcolor'] = entry_title_fontcolor # Store in gui_elements

        tk.Label(title_frame, text="Size AUTO (Montserrat font):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_calculated_title_font_size = tk.Entry(title_frame, width=30, state=tk.DISABLED)
        entry_calculated_title_font_size.grid(row=4, column=1, padx=10, pady=5)
        self.gui_elements['entry_calculated_title_font_size'] = entry_calculated_title_font_size # Store in gui_elements

        tk.Label(title_frame, text="Size MANUAL:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        entry_title_font_size = tk.Entry(title_frame, width=30)
        entry_title_font_size.insert(0, gcm.title_font_size)
        entry_title_font_size.grid(row=5, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_font_size'] = entry_title_font_size # Store in gui_elements

        tk.Label(title_frame, text="Appearance Delay (after overlay):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        entry_title_appearance_delay = tk.Entry(title_frame, width=30)
        entry_title_appearance_delay.insert(0, gcm.title_appearance_delay)
        entry_title_appearance_delay.grid(row=6, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_appearance_delay'] = entry_title_appearance_delay # Store in gui_elements

        tk.Label(title_frame, text="Visible Time:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        entry_title_visible_time = tk.Entry(title_frame, width=30)
        entry_title_visible_time.insert(0, gcm.title_visible_time)
        entry_title_visible_time.grid(row=7, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_visible_time'] = entry_title_visible_time # Store in gui_elements

        tk.Label(title_frame, text="X Offset:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        entry_title_x_offset = tk.Entry(title_frame, width=30)
        entry_title_x_offset.insert(0, gcm.title_x_offset)
        entry_title_x_offset.grid(row=8, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_x_offset'] = entry_title_x_offset # Store in gui_elements

        tk.Label(title_frame, text="Y Offset:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
        entry_title_y_offset = tk.Entry(title_frame, width=30)
        entry_title_y_offset.insert(0, gcm.title_y_offset)
        entry_title_y_offset.grid(row=9, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_y_offset'] = entry_title_y_offset # Store in gui_elements

        tk.Label(title_frame, text="Opacity:").grid(row=10, column=0, padx=10, pady=5, sticky="w")
        title_opacity_frame = tk.Frame(title_frame)
        title_opacity_frame.grid(row=10, column=1, sticky="ew", padx=10, pady=5)

        title_opacity_slider = ttk.Scale(title_opacity_frame, from_=0.0, to=1.0, variable=self.gui_elements['var_title_opacity'], orient="horizontal")
        title_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title_opacity_slider.bind("<ButtonRelease-1>", lambda e: (self.gui_elements['gui_utils'].update_slider_value(self.gui_elements['var_title_opacity'], self.gui_elements['title_opacity_value_entry'])))
        self.gui_elements['title_opacity_slider'] = title_opacity_slider # Store in gui_elements

        title_opacity_value_entry = tk.Entry(title_opacity_frame, width=4)
        title_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        title_opacity_value_entry.insert(0, f"{self.gui_elements['var_title_opacity'].get():.2f}")
        title_opacity_value_entry.bind("<Return>", lambda e: self.gui_elements['gui_utils'].update_slider_from_entry(self.gui_elements['title_opacity_value_entry'], self.gui_elements['var_title_opacity'], self.gui_elements['title_opacity_slider'], 0, 1))
        title_opacity_value_entry.bind("<FocusOut>", lambda e: self.gui_elements['gui_utils'].update_slider_from_entry(self.gui_elements['title_opacity_value_entry'], self.gui_elements['var_title_opacity'], self.gui_elements['title_opacity_slider'], 0, 1))
        self.gui_elements['title_opacity_value_entry'] = title_opacity_value_entry # Store in gui_elements

        title_background_checkbox = tk.Checkbutton(title_frame, text="Enable Background", variable=self.gui_elements['var_enable_title_background'], command=self.toggle_title_controls)
        title_background_checkbox.grid(row=11, column=0, padx=10, pady=5, sticky="w")
        self.gui_elements['title_background_checkbox'] = title_background_checkbox # Store in gui_elements

        tk.Label(title_frame, text="Background Color:").grid(row=12, column=0, padx=10, pady=5, sticky="w")
        title_background_color_entry = tk.Entry(title_frame, textvariable=self.gui_elements['var_title_background_color'], width=30)
        title_background_color_entry.grid(row=12, column=1, padx=10, pady=5)
        self.gui_elements['title_background_color_entry'] = title_background_color_entry # Store in gui_elements

        tk.Label(title_frame, text="Background Opacity:").grid(row=13, column=0, padx=10, pady=5, sticky="w")
        title_background_opacity_frame = tk.Frame(title_frame)
        title_background_opacity_frame.grid(row=13, column=1, sticky="ew", padx=10, pady=5)

        title_background_opacity_slider = ttk.Scale(title_background_opacity_frame, from_=0.0, to=1.0, variable=self.gui_elements['var_title_background_opacity'], orient="horizontal")
        title_background_opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title_background_opacity_slider.bind("<ButtonRelease-1>", lambda e: (self.gui_elements['gui_utils'].update_slider_value(self.gui_elements['var_title_background_opacity'], self.gui_elements['title_background_opacity_value_entry'])))
        self.gui_elements['title_background_opacity_slider'] = title_background_opacity_slider # Store in gui_elements

        title_background_opacity_value_entry = tk.Entry(title_background_opacity_frame, width=4)
        title_background_opacity_value_entry.pack(side=tk.RIGHT, padx=(5, 0))
        title_background_opacity_value_entry.insert(0, f"{self.gui_elements['var_title_background_opacity'].get():.2f}")
        title_background_opacity_value_entry.bind("<Return>", lambda e: self.gui_elements['gui_utils'].update_slider_from_entry(self.gui_elements['title_background_opacity_value_entry'], self.gui_elements['var_title_background_opacity'], self.gui_elements['title_background_opacity_slider'], 0, 1))
        title_background_opacity_value_entry.bind("<FocusOut>", lambda e: self.gui_elements['gui_utils'].update_slider_from_entry(self.gui_elements['title_background_opacity_value_entry'], self.gui_elements['var_title_background_opacity'], self.gui_elements['title_background_opacity_slider'], 0, 1))
        self.gui_elements['title_background_opacity_value_entry'] = title_background_opacity_value_entry # Store in gui_elements

        # Title Video Overlay Section (moved from Overlay Effects tab)
        title_video_overlay_frame = tk.LabelFrame(video_title_column, text="Title Video Overlay", padx=10, pady=5)
        title_video_overlay_frame.pack(fill="both", expand=True)

        enable_title_video_overlay_checkbox = tk.Checkbutton(title_video_overlay_frame, text="Enable", variable=self.gui_elements['var_enable_title_video_overlay'], command=self.toggle_title_controls)
        enable_title_video_overlay_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.gui_elements['enable_title_video_overlay_checkbox'] = enable_title_video_overlay_checkbox # Store in gui_elements

        tk.Label(title_video_overlay_frame, text="Overlay File:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_title_video_overlay_file = ttk.Combobox(title_video_overlay_frame, textvariable=self.gui_elements['var_title_video_overlay_file'], values=self.gui_elements['title_video_overlay_files'], width=25)
        entry_title_video_overlay_file.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        entry_title_video_overlay_file.bind("<<ComboboxSelected>>", self.toggle_title_controls)
        self.gui_elements['entry_title_video_overlay_file'] = entry_title_video_overlay_file # Store in gui_elements

        tk.Label(title_video_overlay_frame, text="Appearance Delay (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_title_video_overlay_delay = tk.Entry(title_video_overlay_frame, textvariable=self.gui_elements['var_title_video_overlay_delay'], width=30)
        entry_title_video_overlay_delay.grid(row=2, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_video_overlay_delay'] = entry_title_video_overlay_delay # Store in gui_elements

        tk.Label(title_video_overlay_frame, text="Chromakey Color:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_title_video_chromakey_color = tk.Entry(title_video_overlay_frame, textvariable=self.gui_elements['var_title_video_chromakey_color'], width=30)
        entry_title_video_chromakey_color.grid(row=3, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_video_chromakey_color'] = entry_title_video_chromakey_color # Store in gui_elements

        tk.Label(title_video_overlay_frame, text="Chromakey Similarity:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_title_video_chromakey_similarity = tk.Entry(title_video_overlay_frame, textvariable=self.gui_elements['var_title_video_chromakey_similarity'], width=30)
        entry_title_video_chromakey_similarity.grid(row=4, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_video_chromakey_similarity'] = entry_title_video_chromakey_similarity # Store in gui_elements

        tk.Label(title_video_overlay_frame, text="Chromakey Blend:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        entry_title_video_chromakey_blend = tk.Entry(title_video_overlay_frame, textvariable=self.gui_elements['var_title_video_chromakey_blend'], width=30)
        entry_title_video_chromakey_blend.grid(row=5, column=1, padx=10, pady=5)
        self.gui_elements['entry_title_video_chromakey_blend'] = entry_title_video_chromakey_blend # Store in gui_elements

    def collect_settings(self):
        settings = {
            'enable_title': self.gui_elements['var_enable_title'].get(),
            'title_text': self.gui_elements['entry_title'].get(),
            'title_font': self.gui_elements['var_title_font'].get(),
            'title_fontcolor': self.gui_elements['var_title_fontcolor'].get(),
            'title_font_size': int(self.gui_elements['entry_title_font_size'].get()),
            'title_appearance_delay': int(self.gui_elements['entry_title_appearance_delay'].get()),
            'title_visible_time': int(self.gui_elements['entry_title_visible_time'].get()),
            'title_x_offset': int(self.gui_elements['entry_title_x_offset'].get()),
            'title_y_offset': int(self.gui_elements['entry_title_y_offset'].get()),
            'title_opacity': float(self.gui_elements['var_title_opacity'].get()),
            'enable_title_background': self.gui_elements['var_enable_title_background'].get(),
            'title_background_color': self.gui_elements['var_title_background_color'].get(),
            'title_background_opacity': float(self.gui_elements['var_title_background_opacity'].get()),
            'enable_title_video_overlay': self.gui_elements['var_enable_title_video_overlay'].get(),
            'title_video_overlay_file': self.gui_elements['var_title_video_overlay_file'].get(),
            'title_video_overlay_delay': int(self.gui_elements['var_title_video_overlay_delay'].get()),
            'title_video_chromakey_color': self.gui_elements['var_title_video_chromakey_color'].get(),
            'title_video_chromakey_similarity': float(self.gui_elements['var_title_video_chromakey_similarity'].get()),
            'title_video_chromakey_blend': float(self.gui_elements['var_title_video_chromakey_blend'].get()),
        }
        return settings
