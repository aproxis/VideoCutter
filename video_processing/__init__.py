from .config import VideoConfig
from .video import VideoProcessor
from .image import ImageProcessor
from .utils import get_media_files
import os
import shutil
import subprocess
from typing import Optional

class VideoPipeline:
    """Main video processing pipeline orchestrator"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        self.config = config or VideoConfig()
        self.video_processor = VideoProcessor(self.config)
        self.image_processor = ImageProcessor(self.config)
        
    def run(self) -> None:
        """Run the complete processing pipeline"""
        # Process videos
        self.video_processor.process_videos()
        self.video_processor.run_cleaner()
        self.video_processor.run_sorter()
        
        # Process images
        self._process_images()
        
        # Process audio
        self._process_audio()
        
        # Run slideshow if needed
        if self.config.depthflow:
            self._run_depth_processing()
            
        self._run_slideshow()

    def _process_images(self) -> None:
        """Process all images in the input folder"""
        image_files = get_media_files(self.config.input_folder, ['.jpg', '.jpeg'])
        if not image_files:
            return
            
        print('##### Processing images')
        
        for image_file in image_files:
            input_path = os.path.join(self.config.input_folder, image_file)
            
            # Process the image
            processed_image = self.image_processor.process_image(input_path)
            output_path = os.path.join(self.video_processor.result_folder, image_file)
            processed_image.save(output_path)
            
            # Move original to source folder
            shutil.move(input_path, os.path.join(self.video_processor.source_date_folder, image_file))
            
        print(f'##### Images moved to {self.video_processor.result_folder}')

    def _process_audio(self) -> None:
        """Process audio files"""
        audio_files = get_media_files(self.config.input_folder, ['.mp3'])
        if not audio_files:
            return
            
        print('##### Processing audio')
        
        for audio_file in audio_files:
            input_path = os.path.join(self.config.input_folder, audio_file)
            
            # Copy to source folder
            shutil.copy(input_path, os.path.join(self.video_processor.source_date_folder, audio_file))
            
            # Move to result folder
            shutil.move(input_path, os.path.join(self.video_processor.result_folder, audio_file))
            
        print(f'##### Audio moved to {self.video_processor.result_folder}')

    def _run_depth_processing(self) -> None:
        """Run depth processing if enabled"""
        depth_script = 'depth.py'
        depth_args = [
            '--o', self.video_processor.result_folder,
            '--d', self.video_processor.datetime_str,
            '--t', str(self.config.slide_time),
            '--tl', str(self.config.time_limit)
        ]
        cmd = ['python3', depth_script] + depth_args
        subprocess.run(cmd)
        print("Depth processing completed")

    def _run_slideshow(self) -> None:
        """Run slideshow creation"""
        slideshow_script = 'slideshow.py'
        slideshow_args = [
            '--t', str(self.config.slide_time),
            '--tl', str(self.config.time_limit),
            '--n', self.config.model_name,
            '--w', self.config.watermark.replace('\n', '\\n'),
            '--f', str(self.config.fontsize),
            '--z', str(int(self.config.depthflow)),
            '--o', self.config.video_orientation
        ]
        cmd = ['python3', slideshow_script] + slideshow_args
        subprocess.run(cmd)
        print("Slideshow creation completed")
