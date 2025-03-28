import pytest
import os
from unittest.mock import patch, MagicMock
from video_processing.video import VideoProcessor
from video_processing.config import VideoConfig

class TestVideoProcessor:
    @patch('subprocess.Popen')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_process_videos(self, mock_makedirs, mock_exists, mock_popen):
        # Setup
        config = VideoConfig()
        config.input_folder = "test_input"
        processor = VideoProcessor(config)
        
        # Mock dependencies
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = b""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Test
        with patch('os.listdir', return_value=['test.mp4']):
            processor.process_videos()
            
        # Verify
        mock_makedirs.assert_called()
        mock_popen.assert_called()
        
    @patch('subprocess.run')
    def test_run_cleaner(self, mock_run):
        config = VideoConfig()
        processor = VideoProcessor(config)
        processor.run_cleaner()
        mock_run.assert_called()
        
    @patch('subprocess.run')
    def test_run_sorter(self, mock_run):
        config = VideoConfig()
        processor = VideoProcessor(config)
        processor.run_sorter()
        mock_run.assert_called()
