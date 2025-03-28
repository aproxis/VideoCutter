import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class VideoConfig:
    """Central configuration for video processing parameters"""
    segment_duration: int = 6
    time_limit: int = 595
    input_folder: str = 'INPUT'
    model_name: str = 'Model Name'
    fontsize: int = 90
    watermark: str = 'Today is a\\n Plus Day'
    depthflow: bool = False
    video_orientation: str = 'vertical'  # 'vertical' or 'horizontal'
    blur: bool = False
    slide_time: int = 5
    fps: int = 25
    watermark_opacity: float = 0.7
    wm_timer: int = 50  # watermark movement interval

    # Path configurations
    template_folder: str = os.path.join(os.path.dirname(__file__), '../TEMPLATE')
    font_path: str = '/Users/a/Library/Fonts/Nexa.otf'

    # Target dimensions
    @property
    def target_height(self) -> int:
        return 1920 if self.video_orientation == 'vertical' else 1080

    @property 
    def target_width(self) -> int:
        return 1080 if self.video_orientation == 'vertical' else 1920

    @property
    def outro_video_path(self) -> str:
        filename = 'outro_vertical.mp4' if self.video_orientation == 'vertical' else 'outro_horizontal.mp4'
        return os.path.join(self.template_folder, filename)

    def update_from_args(self, args):
        """Update configuration from command line arguments"""
        self.segment_duration = getattr(args, 'segment_duration', self.segment_duration)
        self.time_limit = getattr(args, 'time_limit', self.time_limit)
        self.input_folder = getattr(args, 'input_folder', self.input_folder)
        self.model_name = getattr(args, 'model_name', self.model_name)
        self.fontsize = getattr(args, 'fontsize', self.fontsize)
        self.watermark = getattr(args, 'watermark', self.watermark).replace('\\n', '\n')
        self.depthflow = getattr(args, 'depthflow', str(int(self.depthflow))) == '1'
        self.video_orientation = getattr(args, 'video_orientation', self.video_orientation)
        self.blur = getattr(args, 'blur', str(int(self.blur))) == '1'
        self.slide_time = getattr(args, 'slide_time', self.slide_time)
