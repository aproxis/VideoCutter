import tkinter as tk
from tkinter import ttk
from videocutter.utils import gui_config_manager as gcm
from videocutter.gui import gui_utils

class OverlayEffectsFrame(ttk.Frame):
    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        self._initialize_variables()
        self.create_widgets()
        self.update_all_overlay_controls() # Initial update of controls

    def _initialize_variables(self):
        """Initialize overlay and effect related variables"""
        self.gui_elements['var_enable_subscribe_overlay'] = tk.BooleanVar(value=gcm.enable_subscribe_overlay)
        self.gui_elements['var_subscribe_delay'] = tk.IntVar(self.gui_elements['root'], value=gcm.subscribe_delay)
        self.gui_elements['var_enable_title_video_overlay'] = tk.BooleanVar(value=gcm.enable_title_video_overlay)
        self.gui_elements['var_title_video_overlay_file'] = tk.StringVar(self.gui_elements['root'], value=gcm.title_video_overlay_file)
        self.gui_elements['var_title_video_overlay_delay'] = tk.IntVar(self.gui_elements['root'], value=gcm.title_video_overlay_delay)
        self.gui_elements['var_title_video_chromakey_color'] = tk.StringVar(self.gui_elements['root'], value=gcm.title_video_chromakey_color)
        self.gui_elements['var_title_video_chromakey_similarity'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.title_video_chromakey_similarity)
        self.gui_elements['var_title_video_chromakey_blend'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.title_video_chromakey_blend)
        self.gui_elements['var_subscribe_overlay_file'] = tk.StringVar(self.gui_elements['root'], value="None")
        self.gui_elements['var_chromakey_color'] = tk.StringVar(self.gui_elements['root'], value=gcm.chromakey_color)

        self.gui_elements['var_enable_effect_overlay'] = tk.BooleanVar(self.gui_elements['root'], value=True)
        self.gui_elements['var_effect_overlay'] = tk.StringVar(self.gui_elements['root'], value="None")
        self.gui_elements['var_effect_opacity'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.effect_opacity)
        self.gui_elements['var_effect_blend'] = tk.StringVar(self.gui_elements['root'], value=gcm.effect_blend)

        self.gui_elements['var_watermark_type'] = tk.StringVar(self.gui_elements['root'], value=gcm.watermark_type)
        self.gui_elements['var_watermark_font'] = tk.StringVar(self.gui_elements['root'], value=gcm.watermark_font)
        self.gui_elements['var_enable_watermark'] = tk.BooleanVar(value=gcm.enable_watermark)
        self.gui_elements['var_watermark_font_size'] = tk.IntVar(self.gui_elements['root'], value=gcm.watermark_font_size)
        self.gui_elements['var_watermark_opacity'] = tk.DoubleVar(self.gui_elements['root'], value=gcm.watermark_opacity)
        self.gui_elements['var_watermark_fontcolor'] = tk.StringVar(self.gui_elements['root'], value=gcm.watermark_fontcolor)
        self.gui_elements['var_watermark_speed_intuitive'] = tk.IntVar(self.gui_elements['root'], value=gcm.watermark_speed_intuitive)

    def create_widgets(self):
        """Setup the overlay effects tab layout"""
        overlay_effects_left_column = tk.Frame(self)
        overlay_effects_left_column.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        overlay_effects_right_column = tk.Frame(self)
        overlay_effects_right_column.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

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

    def update_all_overlay_controls(self): # Initial update of controls
        self.toggle_subscribe_overlay_controls()
        self.toggle_watermark_controls()
        self.toggle_effect_overlay_controls()

    def collect_settings(self):
        """Collect all GUI settings from this frame into a dictionary"""
        watermark = self.gui_elements['text_watermark'].get("1.0", tk.END).rstrip('\n')
        watermark = watermark.replace('\n', '\\n')

        watermark_speed_intuitive = self.gui_elements['var_watermark_speed_intuitive'].get()
        watermark_speed = int(100 - (watermark_speed_intuitive - 1) * 9)

        settings = {
            'watermark': watermark.replace('\\n', '\n'),
            'watermark_type': self.gui_elements['var_watermark_type'].get(),
            'watermark_speed': watermark_speed,
            'enable_watermark': self.gui_elements['var_enable_watermark'].get(),
            'watermark_font_size': self.gui_elements['var_watermark_font_size'].get(),
            'watermark_opacity': self.gui_elements['var_watermark_opacity'].get(),
            'watermark_fontcolor': self.gui_elements['var_watermark_fontcolor'].get(),
            'watermark_speed_intuitive': watermark_speed_intuitive,
            'watermark_font': self.gui_elements['var_watermark_font'].get(),

            'enable_subscribe_overlay': self.gui_elements['var_enable_subscribe_overlay'].get(),
            'subscribe_delay': self.gui_elements['var_subscribe_delay'].get(),
            'chromakey_color': self.gui_elements['var_chromakey_color'].get(),
            'chromakey_similarity': self.gui_elements['entry_chromakey_similarity'].get(),
            'chromakey_blend': self.gui_elements['entry_chromakey_blend'].get(),

            'effect_overlay': None if self.gui_elements['var_effect_overlay'].get() == "None" else self.gui_elements['var_effect_overlay'].get(),
            'effect_opacity': self.gui_elements['var_effect_opacity'].get(),
            'effect_blend': self.gui_elements['var_effect_blend'].get(),
            'enable_effect_overlay': self.gui_elements['var_enable_effect_overlay'].get(),
        }
        return settings
