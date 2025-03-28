"""
Image processing module for VideoCutter.

This module provides functions for processing images, including resizing,
cropping, and applying effects.
"""

import os
import shutil
from typing import Tuple, Optional
from PIL import Image, ImageFilter, ImageDraw

from .config import VideoConfig


class ImageProcessor:
    """Class for processing images."""
    
    def __init__(self, config: VideoConfig):
        """Initialize the ImageProcessor.
        
        Args:
            config: The configuration object.
        """
        self.config = config
        
        # Set target dimensions based on orientation
        self.target_height = 1920 if config.video_orientation == 'vertical' else 1080
        self.target_width = 1080 if config.video_orientation == 'vertical' else 1920
    
    def process_image(self, input_path: str, output_path: Optional[str] = None) -> Image.Image:
        """Process an image for the slideshow.
        
        Args:
            input_path: Path to the input image.
            output_path: Path to save the processed image. If None, the input path is used.
            
        Returns:
            The processed PIL Image object.
        """
        # Open the original image
        original_image = Image.open(input_path)
        width, height = original_image.size
        
        # Determine image orientation
        is_vertical_image = height > width
        output_path = output_path or input_path
        
        if is_vertical_image:
            if self.config.video_orientation == 'horizontal':
                return self._process_vertical_to_horizontal(original_image, output_path)
            else:  # vertical to vertical
                return self._process_vertical_to_vertical(original_image, output_path)
        else:  # Horizontal image
            if self.config.video_orientation == 'vertical':
                return self._process_horizontal_to_vertical(original_image, output_path)
            else:  # horizontal to horizontal
                return self._process_horizontal_to_horizontal(original_image, output_path)
    
    def _process_vertical_to_horizontal(self, original_image: Image.Image, output_path: str) -> Image.Image:
        """Process a vertical image for horizontal output.
        
        Args:
            original_image: The original PIL Image.
            output_path: Path to save the processed image.
            
        Returns:
            The processed PIL Image object.
        """
        width, height = original_image.size
        
        # Resize first maintaining aspect ratio
        target_width = self.target_height * 16 // 9
        calculated_width = int(self.target_height * width / height)
        resized_image = original_image.resize((calculated_width, self.target_height), Image.LANCZOS)
        w, h = resized_image.size
        
        # Create the horizontal gradient mask
        border_width = int(w * 0.1)  # Width of fade effect
        gradient = Image.new('L', (w, h), color=255)
        draw = ImageDraw.Draw(gradient)
        
        for x in range(border_width):
            fade = int(255 * (x / border_width))
            draw.rectangle([x, 0, x + 1, h], fill=fade)  # Left fade
            draw.rectangle([w - x - 1, 0, w - x, h], fill=fade)  # Right fade
        
        # Apply gradient as alpha channel
        resized_image.putalpha(gradient)
        
        # Create blurred background
        background_image = original_image.resize((target_width, self.target_height), Image.LANCZOS)
        blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Paste the image with fade onto the background
        x_offset = (target_width - w) // 2
        blurred_background.paste(resized_image, (x_offset, 0), mask=resized_image)
        blurred_background.save(output_path)
        
        return blurred_background
    
    def _process_vertical_to_vertical(self, original_image: Image.Image, output_path: str) -> Image.Image:
        """Process a vertical image for vertical output.
        
        Args:
            original_image: The original PIL Image.
            output_path: Path to save the processed image.
            
        Returns:
            The processed PIL Image object.
        """
        width, height = original_image.size
        
        # Resize first maintaining aspect ratio
        target_width = self.target_height * 9 // 16
        calculated_height = int(target_width * height / width)
        
        resized_image = original_image.resize((target_width, calculated_height), Image.LANCZOS)
        w, h = resized_image.size
        
        # Create vertical gradient mask
        border_width = int(h * 0.1)
        gradient = Image.new('L', (w, h), color=255)
        draw = ImageDraw.Draw(gradient)
        for y in range(border_width):
            fade = int(255 * (y / border_width))
            draw.rectangle([0, y, w, y + 1], fill=fade)  # Top fade
            draw.rectangle([0, h - y - 1, w, h - y], fill=fade)  # Bottom fade
        
        resized_image.putalpha(gradient)
        
        # Create blurred background
        background_image = original_image.resize((target_width, self.target_height), Image.LANCZOS)
        blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))
        y_offset = (self.target_height - h) // 2
        blurred_background.paste(resized_image, (0, y_offset), mask=resized_image)
        blurred_background.save(output_path)
        
        return blurred_background
    
    def _process_horizontal_to_vertical(self, original_image: Image.Image, output_path: str) -> Image.Image:
        """Process a horizontal image for vertical output.
        
        Args:
            original_image: The original PIL Image.
            output_path: Path to save the processed image.
            
        Returns:
            The processed PIL Image object.
        """
        width, height = original_image.size
        
        # Resize first maintaining aspect ratio
        target_width = self.target_height * 9 // 16
        calculated_height = int(target_width * height / width)
        resized_image = original_image.resize((target_width, calculated_height), Image.LANCZOS)
        w, h = resized_image.size
        
        # Create vertical gradient mask
        border_width = int(h * 0.1)
        gradient = Image.new('L', (w, h), color=255)
        draw = ImageDraw.Draw(gradient)
        for y in range(border_width):
            fade = int(255 * (y / border_width))
            draw.rectangle([0, y, w, y + 1], fill=fade)  # Top fade
            draw.rectangle([0, h - y - 1, w, h - y], fill=fade)  # Bottom fade
        
        resized_image.putalpha(gradient)
        
        # Create blurred background
        background_image = original_image.resize((target_width, self.target_height), Image.LANCZOS)
        blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))
        y_offset = (self.target_height - h) // 2
        blurred_background.paste(resized_image, (0, y_offset), mask=resized_image)
        blurred_background.save(output_path)
        
        return blurred_background
    
    def _process_horizontal_to_horizontal(self, original_image: Image.Image, output_path: str) -> Image.Image:
        """Process a horizontal image for horizontal output.
        
        Args:
            original_image: The original PIL Image.
            output_path: Path to save the processed image.
            
        Returns:
            The processed PIL Image object.
        """
        width, height = original_image.size
        
        # Resize first maintaining aspect ratio
        target_width = int(self.target_height * width / height)
        resized_image = original_image.resize((target_width, self.target_height), Image.LANCZOS)
        
        # Crop to 16:9
        target_width = self.target_height * 16 // 9
        if resized_image.width < target_width:
            w, h = resized_image.size
            
            # Create the horizontal gradient mask
            border_width = int(w * 0.1)  # Width of fade effect
            gradient = Image.new('L', (w, h), color=255)
            draw = ImageDraw.Draw(gradient)
            
            for x in range(border_width):
                fade = int(255 * (x / border_width))
                draw.rectangle([x, 0, x + 1, h], fill=fade)  # Left fade
                draw.rectangle([w - x - 1, 0, w - x, h], fill=fade)  # Right fade
            
            # Apply gradient as alpha channel
            resized_image.putalpha(gradient)
            
            # Create blurred background
            background_image = original_image.resize((target_width, self.target_height), Image.LANCZOS)
            blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))
            
            # Paste the image with fade onto the background
            x_offset = (target_width - w) // 2
            blurred_background.paste(resized_image, (x_offset, 0), mask=resized_image)
            blurred_background.save(output_path)
            return blurred_background
        
        elif resized_image.width >= target_width:
            # Crop directly if the resized width is sufficient
            crop_left = (resized_image.width - target_width) // 2
            final_image = resized_image.crop((crop_left, 0, crop_left + target_width, self.target_height))
            final_image.save(output_path)
            return final_image
    
    def process_images(self, input_folder: str, result_folder: str, source_folder: str) -> None:
        """Process all images in the input folder.
        
        Args:
            input_folder: Path to the input folder.
            result_folder: Path to the result folder.
            source_folder: Path to the source folder.
        """
        # Process each image
        for image_file in os.listdir(input_folder):
            if not image_file.endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            input_path = os.path.join(input_folder, image_file)
            print(f'Processing {input_path}')
            
            # Copy original to source folder
            if os.path.isfile(input_path):
                shutil.copy(input_path, os.path.join(source_folder, image_file))
            
            # Process the image
            self.process_image(input_path)
            
            # Move to result folder
            shutil.move(input_path, os.path.join(result_folder, image_file))
        
        print(f'##### Images moved to {result_folder}')
