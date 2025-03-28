from PIL import Image, ImageFilter, ImageDraw
from typing import Tuple
from .config import VideoConfig
import os

class ImageProcessor:
    """Handles all image processing operations"""
    
    def __init__(self, config: VideoConfig):
        self.config = config
        
    def process_image(self, media_path: str) -> Image.Image:
        """
        Process an image based on configuration settings.
        
        Args:
            media_path: Path to the image file
            
        Returns:
            Processed PIL Image object
        """
        original_image = Image.open(media_path)
        width, height = original_image.size
        is_vertical_image = height > width
        
        if is_vertical_image:
            return self._process_vertical_image(original_image)
        else:
            return self._process_horizontal_image(original_image)

    def _process_vertical_image(self, image: Image.Image) -> Image.Image:
        """Process a vertically oriented image"""
        if self.config.video_orientation == 'horizontal':
            return self._create_horizontal_composite(image)
        else:
            return self._create_vertical_composite(image)

    def _process_horizontal_image(self, image: Image.Image) -> Image.Image:
        """Process a horizontally oriented image"""
        if self.config.video_orientation == 'vertical':
            return self._create_vertical_composite(image)
        else:
            return self._create_horizontal_composite(image)

    def _create_vertical_composite(self, image: Image.Image) -> Image.Image:
        """Create composition for vertical output"""
        target_width = self.config.target_height * 9 // 16
        calculated_height = int(target_width * image.height / image.width)
        
        # Resize maintaining aspect ratio
        resized_image = image.resize(
            (target_width, calculated_height),
            Image.LANCZOS
        )
        
        # Create gradient mask
        w, h = resized_image.size
        border_width = int(h * 0.1)
        gradient = Image.new('L', (w, h), color=255)
        draw = ImageDraw.Draw(gradient)
        
        for y in range(border_width):
            fade = int(255 * (y / border_width))
            draw.rectangle([0, y, w, y + 1], fill=fade)  # Top fade
            draw.rectangle([0, h - y - 1, w, h - y], fill=fade)  # Bottom fade

        resized_image.putalpha(gradient)
        
        # Create blurred background
        background = image.resize(
            (target_width, self.config.target_height),
            Image.LANCZOS
        )
        blurred_background = background.filter(ImageFilter.GaussianBlur(20))
        
        # Composite images
        y_offset = (self.config.target_height - h) // 2
        blurred_background.paste(
            resized_image, (0, y_offset),
            mask=resized_image
        )
        
        return blurred_background

    def _create_horizontal_composite(self, image: Image.Image) -> Image.Image:
        """Create composition for horizontal output"""
        target_width = self.config.target_height * 16 // 9
        
        if image.width >= target_width:
            # Direct crop if sufficient width
            crop_left = (image.width - target_width) // 2
            return image.crop((
                crop_left, 0,
                crop_left + target_width,
                self.config.target_height
            ))
        else:
            # Create composite with blurred background
            calculated_width = int(self.config.target_height * image.width / image.height)
            resized_image = image.resize(
                (calculated_width, self.config.target_height),
                Image.LANCZOS
            )
            
            # Create gradient mask
            w, h = resized_image.size
            border_width = int(w * 0.1)
            gradient = Image.new('L', (w, h), color=255)
            draw = ImageDraw.Draw(gradient)
            
            for x in range(border_width):
                fade = int(255 * (x / border_width))
                draw.rectangle([x, 0, x + 1, h], fill=fade)  # Left fade
                draw.rectangle([w - x - 1, 0, w - x, h], fill=fade)  # Right fade

            resized_image.putalpha(gradient)
            
            # Create blurred background
            background = image.resize(
                (target_width, self.config.target_height),
                Image.LANCZOS
            )
            blurred_background = background.filter(ImageFilter.GaussianBlur(20))
            
            # Composite images
            x_offset = (target_width - w) // 2
            blurred_background.paste(
                resized_image, (x_offset, 0),
                mask=resized_image
            )
            
            return blurred_background
