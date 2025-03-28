import pytest
from video_processing.config import VideoConfig

class TestVideoConfig:
    def test_default_values(self):
        config = VideoConfig()
        assert config.segment_duration == 6
        assert config.time_limit == 595
        assert config.input_folder == "INPUT"
        assert config.model_name == "Model Name"

    def test_update_from_args(self):
        config = VideoConfig()
        args = type('Args', (), {
            'segment_duration': 10,
            'time_limit': 300,
            'input_folder': "test_input",
            'model_name': "Test Model",
            'fontsize': 100,
            'watermark': "Test\\nWatermark",
            'depthflow': "1",
            'video_orientation': "horizontal",
            'blur': "1"
        })()
        
        config.update_from_args(args)
        assert config.segment_duration == 10
        assert config.time_limit == 300
        assert config.input_folder == "test_input"
        assert config.model_name == "Test Model"
        assert config.fontsize == 100
        assert config.watermark == "Test\nWatermark"
        assert config.depthflow is True
        assert config.video_orientation == "horizontal"
        assert config.blur is True
