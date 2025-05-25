import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

# Debounce mechanism for preview updates
_after_id = None
def schedule_subtitle_preview_update(root, update_function):
    global _after_id
    if _after_id:
        root.after_cancel(_after_id)
    _after_id = root.after(200, update_function) # 200ms delay

# Function to update slider value entry
def update_slider_value(var, entry):
    entry.delete(0, tk.END)
    # Format to 2 decimal places for float values
    if isinstance(var.get(), float):
        entry.insert(0, f"{var.get():.2f}")
    else:
        entry.insert(0, str(var.get()))

# Function to update slider from entry
def update_slider_from_entry(entry, var, slider, min_val, max_val, root, update_function):
    try:
        value = float(entry.get())
        if min_val <= value <= max_val:
            var.set(value)
            schedule_subtitle_preview_update(root, update_function) # Use debounced update
    except ValueError:
        pass  # Ignore invalid input

# Function to update subtitle preview
def update_subtitle_preview(gui_elements):
    # Access necessary elements from gui_elements
    root = gui_elements['root']
    var_subtitle_font = gui_elements['var_subtitle_font']
    var_subtitle_fontsize = gui_elements['var_subtitle_fontsize']
    var_subtitle_fontcolor = gui_elements['var_subtitle_fontcolor']
    var_subtitle_bgcolor = gui_elements['var_subtitle_bgcolor']
    var_subtitle_bgopacity = gui_elements['var_subtitle_bgopacity']
    var_subtitle_outline = gui_elements['var_subtitle_outline']
    var_subtitle_outlinecolor = gui_elements['var_subtitle_outlinecolor']
    var_subtitle_shadow = gui_elements['var_subtitle_shadow']
    preview_label = gui_elements['preview_label']
    preview_frame = gui_elements['preview_frame']
    fonts_dir = gui_elements['fonts_dir'] # Assuming fonts_dir is passed in gui_elements

    try:
        # Create a blank image
        img = Image.new('RGB', (400, 100), color=(100, 100, 100))
        draw = ImageDraw.Draw(img)
        
        # Try to load the selected font
        try:
            font_path = os.path.join(fonts_dir, var_subtitle_font.get())
            font = ImageFont.truetype(font_path, var_subtitle_fontsize.get())
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw sample text
        sample_text = "Sample Subtitle Text"
        # PIL.ImageDraw.textsize is deprecated since Pillow 9.2.0, use textbbox or textlength instead
        try:
            # For newer Pillow versions
            left, top, right, bottom = draw.textbbox((0, 0), sample_text, font=font)
            text_width = right - left
            text_height = bottom - top
        except AttributeError:
            # Fallback for older Pillow versions
            try:
                text_width, text_height = draw.textsize(sample_text, font=font)
            except:
                # Last resort fallback
                text_width, text_height = 200, 20
                
        position = (200 - text_width // 2, 50 - text_height // 2)
        
        # Create a base image with alpha channel for layering
        base_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
        base_draw = ImageDraw.Draw(base_img)
        
        # Draw the main text first (this will be the base layer)
        base_draw.text(position, sample_text, font=font, fill=f"#{var_subtitle_fontcolor.get()}")
        
        # If outline is enabled, create an outline layer
        outline_img = None
        if var_subtitle_outline.get() > 0:
            outline_thickness = var_subtitle_outline.get()
            outline_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            outline_draw = ImageDraw.Draw(outline_img)
            
            # Draw outline by drawing text multiple times with offset
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:  # Skip the center position
                        outline_draw.text(
                            (position[0] + dx * outline_thickness, position[1] + dy * outline_thickness),
                            sample_text,
                            font=font,
                            fill=f"#{var_subtitle_outlinecolor.get()}"
                        )
            
            # Composite outline under the text
            base_img = Image.alpha_composite(outline_img, base_img)
        
        # If shadow is enabled, create a shadow layer
        if var_subtitle_shadow.get():
            # Define shadow_offset here to ensure it's always defined when shadow is enabled
            shadow_offset = 2 

            # Calculate shadow color with opacity
            shadow_color = var_subtitle_bgcolor.get()
            r = int(shadow_color[0:2], 16)
            g = int(shadow_color[2:4], 16)
            b = int(shadow_color[4:6], 16)
            opacity = var_subtitle_bgopacity.get()
            shadow_rgba = (r, g, b, int(opacity * 255))
            
            # Create shadow image (this goes behind everything)
            shadow_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            
            # Draw shadow of the text with outline if outline is enabled
            if var_subtitle_outline.get() > 0 and outline_img:
                # Create a mask from the outline+text image
                mask = Image.new('L', img.size, 0)
                mask_draw = ImageDraw.Draw(mask)
                
                # Draw the outline shape
                outline_thickness = var_subtitle_outline.get()
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        mask_draw.text(
                            (position[0] + dx * outline_thickness, position[1] + dy * outline_thickness),
                            sample_text,
                            font=font,
                            fill=255
                        )
                
                # Draw the text shape
                mask_draw.text(position, sample_text, font=font, fill=255)
                
                # Draw shadow using the mask
                shadow_draw.bitmap(
                    (shadow_offset, shadow_offset),
                    mask,
                    fill=shadow_rgba
                )
            else:
                # Just draw shadow for the text
                shadow_draw.text(
                    (position[0] + shadow_offset, position[1] + shadow_offset),
                    sample_text,
                    font=font,
                    fill=shadow_rgba
                )
            
            # Composite shadow onto background, then add text+outline on top
            img = Image.alpha_composite(img.convert('RGBA'), shadow_img)
            img = Image.alpha_composite(img.convert('RGBA'), base_img).convert('RGB')
        else:
            # No shadow, just composite text+outline onto background
            img = Image.alpha_composite(img.convert('RGBA'), base_img).convert('RGB')
        
        # Update the draw object for any additional drawing
        draw = ImageDraw.Draw(img)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Check if preview_label and preview_frame exist and create them if needed
        if preview_frame is not None: # Ensure preview_frame exists
            if preview_label is None:
                preview_label = tk.Label(preview_frame)
                preview_label.pack(padx=10, pady=10)
            
            # Update the image
            preview_label.config(image=photo)
            preview_label.image = photo  # Keep a reference: This line should only run if preview_label is a widget
        # If preview_frame was None, preview_label might also be None, so we shouldn't try to set .image on it.
    except Exception as e:
        print(f"Error updating preview: {e}")
