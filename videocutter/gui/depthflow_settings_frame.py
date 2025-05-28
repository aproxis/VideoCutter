import tkinter as tk
from tkinter import ttk
import videocutter.gui.gui_utils as gui_utils

class DepthflowSettingsFrame(ttk.Frame):
    def __init__(self, parent, gui_elements):
        super().__init__(parent)
        self.gui_elements = gui_elements
        self._initialize_variables()
        self.create_widgets()
        self.toggle_depthflow_controls() # Initial update of controls

    def _initialize_variables(self):
        """Initialize DepthFlow related variables"""
        # var_depthflow is now passed from the main GUI
        self.gui_elements['var_depthflow_vignette_enable'] = tk.BooleanVar(value=True)
        self.gui_elements['var_depthflow_dof_enable'] = tk.BooleanVar(value=True)
        self.gui_elements['var_depthflow_isometric_min'] = tk.DoubleVar(self.gui_elements['root'], value=0.4)
        self.gui_elements['var_depthflow_isometric_max'] = tk.DoubleVar(self.gui_elements['root'], value=0.5)
        self.gui_elements['var_depthflow_height_min'] = tk.DoubleVar(self.gui_elements['root'], value=0.1)
        self.gui_elements['var_depthflow_height_max'] = tk.DoubleVar(self.gui_elements['root'], value=0.15)
        self.gui_elements['var_depthflow_zoom_min'] = tk.DoubleVar(self.gui_elements['root'], value=0.65)
        self.gui_elements['var_depthflow_zoom_max'] = tk.DoubleVar(self.gui_elements['root'], value=0.75)
        self.gui_elements['var_depthflow_min_effects_per_image'] = tk.IntVar(self.gui_elements['root'], value=1)
        self.gui_elements['var_depthflow_max_effects_per_image'] = tk.IntVar(self.gui_elements['root'], value=2)
        self.gui_elements['var_depthflow_base_zoom_loops'] = tk.BooleanVar(value=False)
        self.gui_elements['var_depthflow_workers'] = tk.IntVar(self.gui_elements['root'], value=1)
        
        # New DepthFlow parameters
        # These are now handled by min/max ranges or are single values that are not ranges
        self.gui_elements['var_depthflow_offset_x'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_offset_y'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_steady'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_dolly'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_focus'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_invert'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_center_x'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_center_y'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_origin_x'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_origin_y'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_zoom_probability'] = tk.DoubleVar(self.gui_elements['root'], value=0.3) # New
        
        # Initialize new single value DepthFlow parameters
        self.gui_elements['var_depthflow_height'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_isometric'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)
        self.gui_elements['var_depthflow_zoom'] = tk.DoubleVar(self.gui_elements['root'], value=0.0)

    def create_widgets(self):
        """Setup the DepthFlow settings tab layout"""
        depthflow_frame = ttk.LabelFrame(self, text="DepthFlow Settings")
        depthflow_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid columns to expand
        depthflow_frame.grid_columnconfigure(1, weight=1) # Make the second column expandable for entries
        depthflow_frame.grid_columnconfigure(3, weight=1) # Make the fourth column expandable for entries

        # Row 0: Enable DepthFlow Checkbox
        self.enable_depthflow_checkbox = tk.Checkbutton(depthflow_frame, text="Enable DepthFlow", variable=self.gui_elements['var_depthflow'], command=self.toggle_depthflow_controls)
        self.enable_depthflow_checkbox.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")

        # Row 1: Vignette, DOF, Base Zoom Loops, Workers
        tk.Checkbutton(depthflow_frame, text="Enable Vignette", variable=self.gui_elements['var_depthflow_vignette_enable']).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        tk.Checkbutton(depthflow_frame, text="Enable Depth of Field", variable=self.gui_elements['var_depthflow_dof_enable']).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        tk.Checkbutton(depthflow_frame, text="Base Zoom Loops", variable=self.gui_elements['var_depthflow_base_zoom_loops']).grid(row=1, column=2, padx=5, pady=2, sticky="w")
        tk.Label(depthflow_frame, text="Workers:").grid(row=1, column=3, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_workers']).grid(row=1, column=4, padx=5, pady=2, sticky="ew")

        # Row 2: Offset X/Y
        row_idx = 2
        tk.Label(depthflow_frame, text="Offset X:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_offset_x']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        tk.Label(depthflow_frame, text="Offset Y:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_offset_y']).grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        # Row 3: Steady
        row_idx += 1
        tk.Label(depthflow_frame, text="Steady:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_steady']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        # Row 4: Dolly
        row_idx += 1
        tk.Label(depthflow_frame, text="Dolly:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_dolly']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        # Row 5: Focus
        row_idx += 1
        tk.Label(depthflow_frame, text="Focus:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_focus']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        # Row 6: Invert
        row_idx += 1
        tk.Label(depthflow_frame, text="Invert:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_invert']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        # Row 7: Center X/Y
        row_idx += 1
        tk.Label(depthflow_frame, text="Center X:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_center_x']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        tk.Label(depthflow_frame, text="Center Y:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_center_y']).grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        # Row 8: Origin X/Y
        row_idx += 1
        tk.Label(depthflow_frame, text="Origin X:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_origin_x']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        tk.Label(depthflow_frame, text="Origin Y:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_origin_y']).grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        # Row 9: Zoom Probability
        row_idx += 1
        tk.Label(depthflow_frame, text="Zoom Probability:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_zoom_probability']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        # Isometric Range (Min/Max)
        row_idx += 1
        tk.Label(depthflow_frame, text="Isometric Min:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        isometric_min_slider = ttk.Scale(depthflow_frame, from_=0.0, to=1.0, orient="horizontal", variable=self.gui_elements['var_depthflow_isometric_min'], command=lambda s: (print(f"DEBUG: isometric_min_slider command s={s}"), self.gui_elements['var_depthflow_isometric_min'].set(round(float(s), 2)), print(f"DEBUG: var_depthflow_isometric_min after set: {self.gui_elements['var_depthflow_isometric_min'].get()}")))
        isometric_min_slider.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        isometric_min_slider.bind("<ButtonRelease-1>", lambda e: gui_utils.update_slider_value(self.gui_elements['var_depthflow_isometric_min'].get(), isometric_min_entry))
        isometric_min_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_isometric_min'], width=5)
        isometric_min_entry.grid(row=row_idx, column=2, padx=5, pady=2, sticky="ew")
        isometric_min_entry.bind("<Return>", lambda event: gui_utils.update_slider_from_entry(isometric_min_entry, self.gui_elements['var_depthflow_isometric_min'], isometric_min_slider, 0.0, 1.0, self.gui_elements['root']))
        isometric_min_entry.bind("<FocusOut>", lambda event: gui_utils.update_slider_from_entry(isometric_min_entry, self.gui_elements['var_depthflow_isometric_min'], isometric_min_slider, 0.0, 1.0, self.gui_elements['root']))

        row_idx += 1
        tk.Label(depthflow_frame, text="Isometric Max:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        isometric_max_slider = ttk.Scale(depthflow_frame, from_=0.0, to=1.0, orient="horizontal", variable=self.gui_elements['var_depthflow_isometric_max'], command=lambda s: (print(f"DEBUG: isometric_max_slider command s={s}"), self.gui_elements['var_depthflow_isometric_max'].set(round(float(s), 2)), print(f"DEBUG: var_depthflow_isometric_max after set: {self.gui_elements['var_depthflow_isometric_max'].get()}")))
        isometric_max_slider.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        isometric_max_slider.bind("<ButtonRelease-1>", lambda e: gui_utils.update_slider_value(self.gui_elements['var_depthflow_isometric_max'].get(), isometric_max_entry))
        isometric_max_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_isometric_max'], width=5)
        isometric_max_entry.grid(row=row_idx, column=2, padx=5, pady=2, sticky="ew")
        isometric_max_entry.bind("<Return>", lambda event: gui_utils.update_slider_from_entry(isometric_max_entry, self.gui_elements['var_depthflow_isometric_max'], isometric_max_slider, 0.0, 1.0, self.gui_elements['root']))
        isometric_max_entry.bind("<FocusOut>", lambda event: gui_utils.update_slider_from_entry(isometric_max_entry, self.gui_elements['var_depthflow_isometric_max'], isometric_max_slider, 0.0, 1.0, self.gui_elements['root']))

        # Height Range (Min/Max)
        row_idx += 1
        tk.Label(depthflow_frame, text="Height Min:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        height_min_slider = ttk.Scale(depthflow_frame, from_=0.0, to=1.0, orient="horizontal", variable=self.gui_elements['var_depthflow_height_min'], command=lambda s: (print(f"DEBUG: height_min_slider command s={s}"), self.gui_elements['var_depthflow_height_min'].set(round(float(s), 2)), print(f"DEBUG: var_depthflow_height_min after set: {self.gui_elements['var_depthflow_height_min'].get()}")))
        height_min_slider.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        height_min_slider.bind("<ButtonRelease-1>", lambda e: gui_utils.update_slider_value(self.gui_elements['var_depthflow_height_min'].get(), height_min_entry))
        height_min_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_height_min'], width=5)
        height_min_entry.grid(row=row_idx, column=2, padx=5, pady=2, sticky="ew")
        height_min_entry.bind("<Return>", lambda event: gui_utils.update_slider_from_entry(height_min_entry, self.gui_elements['var_depthflow_height_min'], height_min_slider, 0.0, 1.0, self.gui_elements['root']))
        height_min_entry.bind("<FocusOut>", lambda event: gui_utils.update_slider_from_entry(height_min_entry, self.gui_elements['var_depthflow_height_min'], height_min_slider, 0.0, 1.0, self.gui_elements['root']))

        row_idx += 1
        tk.Label(depthflow_frame, text="Height Max:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        height_max_slider = ttk.Scale(depthflow_frame, from_=0.0, to=1.0, orient="horizontal", variable=self.gui_elements['var_depthflow_height_max'], command=lambda s: (print(f"DEBUG: height_max_slider command s={s}"), self.gui_elements['var_depthflow_height_max'].set(round(float(s), 2)), print(f"DEBUG: var_depthflow_height_max after set: {self.gui_elements['var_depthflow_height_max'].get()}")))
        height_max_slider.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        height_max_slider.bind("<ButtonRelease-1>", lambda e: gui_utils.update_slider_value(self.gui_elements['var_depthflow_height_max'].get(), height_max_entry))
        height_max_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_height_max'], width=5)
        height_max_entry.grid(row=row_idx, column=2, padx=5, pady=2, sticky="ew")
        height_max_entry.bind("<Return>", lambda event: gui_utils.update_slider_from_entry(height_max_entry, self.gui_elements['var_depthflow_height_max'], height_max_slider, 0.0, 1.0, self.gui_elements['root']))
        height_max_entry.bind("<FocusOut>", lambda event: gui_utils.update_slider_from_entry(height_max_entry, self.gui_elements['var_depthflow_height_max'], height_max_slider, 0.0, 1.0, self.gui_elements['root']))

        # Zoom Range (Min/Max)
        row_idx += 1
        tk.Label(depthflow_frame, text="Zoom Min:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        zoom_min_slider = ttk.Scale(depthflow_frame, from_=0.0, to=2.0, orient="horizontal", variable=self.gui_elements['var_depthflow_zoom_min'], command=lambda s: (print(f"DEBUG: zoom_min_slider command s={s}"), self.gui_elements['var_depthflow_zoom_min'].set(round(float(s), 2)), print(f"DEBUG: var_depthflow_zoom_min after set: {self.gui_elements['var_depthflow_zoom_min'].get()}")))
        zoom_min_slider.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        zoom_min_slider.bind("<ButtonRelease-1>", lambda e: gui_utils.update_slider_value(self.gui_elements['var_depthflow_zoom_min'].get(), zoom_min_entry))
        zoom_min_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_zoom_min'], width=5)
        zoom_min_entry.grid(row=row_idx, column=2, padx=5, pady=2, sticky="ew")
        zoom_min_entry.bind("<Return>", lambda event: gui_utils.update_slider_from_entry(zoom_min_entry, self.gui_elements['var_depthflow_zoom_min'], zoom_min_slider, 0.0, 2.0, self.gui_elements['root']))
        zoom_min_entry.bind("<FocusOut>", lambda event: gui_utils.update_slider_from_entry(zoom_min_entry, self.gui_elements['var_depthflow_zoom_min'], zoom_min_slider, 0.0, 2.0, self.gui_elements['root']))

        row_idx += 1
        tk.Label(depthflow_frame, text="Zoom Max:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        zoom_max_slider = ttk.Scale(depthflow_frame, from_=0.0, to=2.0, orient="horizontal", variable=self.gui_elements['var_depthflow_zoom_max'], command=lambda s: (print(f"DEBUG: zoom_max_slider command s={s}"), self.gui_elements['var_depthflow_zoom_max'].set(round(float(s), 2)), print(f"DEBUG: var_depthflow_zoom_max after set: {self.gui_elements['var_depthflow_zoom_max'].get()}")))
        zoom_max_slider.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        zoom_max_slider.bind("<ButtonRelease-1>", lambda e: gui_utils.update_slider_value(self.gui_elements['var_depthflow_zoom_max'].get(), zoom_max_entry))
        zoom_max_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_zoom_max'], width=5)
        zoom_max_entry.grid(row=row_idx, column=2, padx=5, pady=2, sticky="ew")
        zoom_max_entry.bind("<Return>", lambda event: gui_utils.update_slider_from_entry(zoom_max_entry, self.gui_elements['var_depthflow_zoom_max'], zoom_max_slider, 0.0, 2.0, self.gui_elements['root']))
        zoom_max_entry.bind("<FocusOut>", lambda event: gui_utils.update_slider_from_entry(zoom_max_entry, self.gui_elements['var_depthflow_zoom_max'], zoom_max_slider, 0.0, 2.0, self.gui_elements['root']))

        # Min/Max Effects per Image
        row_idx += 1
        tk.Label(depthflow_frame, text="Min Effects per Image:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        min_effects_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_min_effects_per_image'], width=5)
        min_effects_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Max Effects per Image:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        max_effects_entry = tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_max_effects_per_image'], width=5)
        max_effects_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        # New DepthFlow parameters (single value entries)
        row_idx += 1
        tk.Label(depthflow_frame, text="Height (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_height']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Offset X (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_offset_x']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Offset Y (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_offset_y']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Steady (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_steady']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Isometric (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_isometric']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Dolly (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_dolly']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Focus (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_focus']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Zoom (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_zoom']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Invert (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_invert']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Center X (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_center_x']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Center Y (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_center_y']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Origin X (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_origin_x']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Origin Y (single):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_origin_y']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        row_idx += 1
        tk.Label(depthflow_frame, text="Zoom Probability:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(depthflow_frame, textvariable=self.gui_elements['var_depthflow_zoom_probability']).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")


    def toggle_depthflow_controls(self):
        """Toggle DepthFlow controls based on var_depthflow checkbox"""
        state = tk.NORMAL if self.gui_elements['var_depthflow'].get() else tk.DISABLED
        
        # Iterate through all children widgets of depthflow_frame and set their state
        # The enable_depthflow_checkbox is now directly referenced in create_widgets, not stored in gui_elements
        # We need to get the children of the LabelFrame, not the frame itself
        for child in self.children.values(): # Get all direct children of this frame
            if isinstance(child, ttk.LabelFrame): # Find the main LabelFrame
                for grandchild in child.winfo_children(): # Iterate its children
                    # Exclude the "Enable DepthFlow" checkbox itself from being disabled
                    if grandchild == self.enable_depthflow_checkbox:
                        continue
                    if isinstance(grandchild, (tk.Entry, tk.Checkbutton, ttk.Combobox, ttk.Scale)):
                        grandchild.config(state=state)
                    elif isinstance(grandchild, tk.Label):
                        # Labels don't have a 'state' option, but we can change their foreground color
                        # to visually indicate disabled state if desired. For now, just skip.
                        pass
        # The enable checkbox itself should always be active
        # No longer needed as it's excluded from the loop above


    def collect_settings(self):
        """Collect all GUI settings from this frame into a dictionary"""
        main_settings_elements = self.gui_elements['tab_main_settings_instance'].gui_elements
        
        settings = {
            'enable_depthflow': self.gui_elements['var_depthflow'].get(),
            'depthflow': {
                'segment_duration': main_settings_elements['var_segment_duration'].get(), # Linked to main settings
                'render_height': 1920 if main_settings_elements['var_video_orientation'].get() == 'vertical' else 1080, # Calculated based on orientation
                'render_fps': main_settings_elements['var_fps'].get(), # Linked to main settings
                'vignette_enable': self.gui_elements['var_depthflow_vignette_enable'].get(),
                'dof_enable': self.gui_elements['var_depthflow_dof_enable'].get(),
                'isometric_min': self.gui_elements['var_depthflow_isometric_min'].get(),
                'isometric_max': self.gui_elements['var_depthflow_isometric_max'].get(),
                'height_min': self.gui_elements['var_depthflow_height_min'].get(),
                'height_max': self.gui_elements['var_depthflow_height_max'].get(),
                'zoom_min': self.gui_elements['var_depthflow_zoom_min'].get(),
                'zoom_max': self.gui_elements['var_depthflow_zoom_max'].get(),
                'min_effects_per_image': self.gui_elements['var_depthflow_min_effects_per_image'].get(),
                'max_effects_per_image': self.gui_elements['var_depthflow_max_effects_per_image'].get(),
                'base_zoom_loops': self.gui_elements['var_depthflow_base_zoom_loops'].get(),
                # New DepthFlow parameters
                'height': self.gui_elements['var_depthflow_height'].get(),
                'offset_x': self.gui_elements['var_depthflow_offset_x'].get(),
                'offset_y': self.gui_elements['var_depthflow_offset_y'].get(),
                'steady': self.gui_elements['var_depthflow_steady'].get(),
                'isometric': self.gui_elements['var_depthflow_isometric'].get(),
                'dolly': self.gui_elements['var_depthflow_dolly'].get(),
                'focus': self.gui_elements['var_depthflow_focus'].get(),
                'zoom': self.gui_elements['var_depthflow_zoom'].get(),
                'invert': self.gui_elements['var_depthflow_invert'].get(),
                'center_x': self.gui_elements['var_depthflow_center_x'].get(),
                'center_y': self.gui_elements['var_depthflow_center_y'].get(),
                'origin_x': self.gui_elements['var_depthflow_origin_x'].get(),
                'origin_y': self.gui_elements['var_depthflow_origin_y'].get(),
                'zoom_probability': self.gui_elements['var_depthflow_zoom_probability'].get(), # New
            },
            'workers': self.gui_elements['var_depthflow_workers'].get()
        }
        return settings
