import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
from video_processing.image import ImageProcessor
from video_processing.config import VideoConfig

class TestImageProcessor:
    @patch('PIL.Image.open')
    @patch('PIL.Image.new')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.Image.Image.resize')
    @patch('PIL.Image.Image.filter')
    @patch('PIL.Image.Image.paste')
    @patch('PIL.Image.Image.save')
    def test_process_image(self, mock_save, mock_paste, mock_filter, 
                         mock_resize, mock_draw, mock_new, mock_open):
        # Setup
        config = VideoConfig()
        processor = ImageProcessor(config)
        
        # Mock image
        mock_img = MagicMock(spec=Image.Image)
        mock_img.size = (1920, 1080)
        mock_open.return_value = mock_img
        
        # Mock other PIL objects
        mock_new.return_value = MagicMock()
        mock_draw.return_value = MagicMock()
        
        # Test
        processor.process_image("test.jpg", "output.jpg")
        
        # Verify
        mock_open.assert_called_with("test.jpg")
        mock_save.assert_called_with("output.jpg")

    @patch('video_processing.image.ImageProcessor.process_image')
    @patch('os.listdir')
    @patch('shutil.copy')
    @patch('shutil.move')
    def test_process_images(self, mock_move, mock_copy, mock_listdir, mock_process):
        # Setup
        config = VideoConfig()
        processor = ImageProcessor(config)
        
        # Mock files
        mock_listdir.return_value = ['test1.jpg', 'test2.jpg']
        
        # Test
        processor.process_images("input_dir", "output_dir", "source_dir")
        
        # Verify
        assert mock_process.call_count == 2
        mock_copy.assert_called()
        mock_move.assert_called()
