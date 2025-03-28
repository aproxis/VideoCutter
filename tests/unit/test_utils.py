"""Tests for the utils module."""

import os
import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
import shutil
from datetime import datetime

from video_processing.utils import (
    find_video_files,
    get_video_duration,
    get_video_dimensions,
    check_aspect_ratio,
    create_timestamp_folder,
    ensure_directory
)


class TestFindVideoFiles(unittest.TestCase):
    """Tests for the find_video_files function."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create some test files
        self.video_files = [
            os.path.join(self.test_dir, 'video1.mp4'),
            os.path.join(self.test_dir, 'video2.mp4'),
            os.path.join(self.test_dir, 'subdir', 'video3.mp4')
        ]
        
        self.non_video_files = [
            os.path.join(self.test_dir, 'image.jpg'),
            os.path.join(self.test_dir, 'document.txt')
        ]
        
        # Create subdirectory
        os.makedirs(os.path.join(self.test_dir, 'subdir'))
        
        # Create empty files
        for file_path in self.video_files + self.non_video_files:
            with open(file_path, 'w') as f:
                pass
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_find_video_files(self):
        """Test finding video files in a directory."""
        found_files = find_video_files(self.test_dir)
        
        # Check that all video files were found
        self.assertEqual(len(found_files), len(self.video_files))
        
        # Check that all found files are video files
        for file_path in found_files:
            self.assertTrue(file_path.endswith('.mp4'))
            self.assertTrue(file_path in self.video_files)


class TestGetVideoDuration(unittest.TestCase):
    """Tests for the get_video_duration function."""
    
    @patch('subprocess.Popen')
    def test_get_video_duration_success(self, mock_popen):
        """Test getting video duration successfully."""
        # Mock the subprocess.Popen
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'01:30:45.5', None)
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Call the function
        duration = get_video_duration('test.mp4')
        
        # Check the result
        self.assertAlmostEqual(duration, 5445.5)  # 1h 30m 45.5s = 5445.5s
    
    @patch('subprocess.Popen')
    def test_get_video_duration_minutes_seconds(self, mock_popen):
        """Test getting video duration with minutes and seconds only."""
        # Mock the subprocess.Popen
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'30:45.5', None)
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Call the function
        duration = get_video_duration('test.mp4')
        
        # Check the result
        self.assertAlmostEqual(duration, 1845.5)  # 30m 45.5s = 1845.5s
    
    @patch('subprocess.Popen')
    def test_get_video_duration_error(self, mock_popen):
        """Test getting video duration with an error."""
        # Mock the subprocess.Popen
        mock_process = MagicMock()
        mock_process.wait.return_value = 1  # Non-zero exit code
        mock_popen.return_value = mock_process
        
        # Call the function
        duration = get_video_duration('test.mp4')
        
        # Check the result
        self.assertIsNone(duration)


class TestGetVideoDimensions(unittest.TestCase):
    """Tests for the get_video_dimensions function."""
    
    @patch('subprocess.run')
    def test_get_video_dimensions(self, mock_run):
        """Test getting video dimensions."""
        # Mock the subprocess.run
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({
            'streams': [
                {
                    'width': 1920,
                    'height': 1080
                }
            ]
        })
        mock_run.return_value = mock_result
        
        # Call the function
        width, height = get_video_dimensions('test.mp4')
        
        # Check the result
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)


class TestCheckAspectRatio(unittest.TestCase):
    """Tests for the check_aspect_ratio function."""
    
    @patch('video_processing.utils.get_video_dimensions')
    def test_check_aspect_ratio_match(self, mock_get_dimensions):
        """Test checking aspect ratio with a matching ratio."""
        # Mock the get_video_dimensions function
        mock_get_dimensions.return_value = (1920, 1080)  # 16:9 ratio
        
        # Call the function
        result = check_aspect_ratio('test.mp4', target_ratio=16/9)
        
        # Check the result
        self.assertTrue(result)
    
    @patch('video_processing.utils.get_video_dimensions')
    def test_check_aspect_ratio_mismatch(self, mock_get_dimensions):
        """Test checking aspect ratio with a mismatching ratio."""
        # Mock the get_video_dimensions function
        mock_get_dimensions.return_value = (1920, 1440)  # 4:3 ratio
        
        # Call the function
        result = check_aspect_ratio('test.mp4', target_ratio=16/9)
        
        # Check the result
        self.assertFalse(result)
    
    @patch('video_processing.utils.get_video_dimensions')
    def test_check_aspect_ratio_tolerance(self, mock_get_dimensions):
        """Test checking aspect ratio with a close ratio within tolerance."""
        # Mock the get_video_dimensions function
        # This is very close to 16:9 but not exact
        mock_get_dimensions.return_value = (1920, 1082)
        
        # Call the function with default tolerance (0.01)
        result = check_aspect_ratio('test.mp4', target_ratio=16/9)
        
        # Check the result
        self.assertTrue(result)


class TestCreateTimestampFolder(unittest.TestCase):
    """Tests for the create_timestamp_folder function."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    @patch('video_processing.utils.datetime')
    def test_create_timestamp_folder(self, mock_datetime):
        """Test creating a timestamp folder."""
        # Mock the datetime.now() function
        mock_now = MagicMock()
        mock_now.strftime.return_value = '2023-01-01_12-00-00'
        mock_datetime.now.return_value = mock_now
        
        # Call the function
        folder_path, datetime_str = create_timestamp_folder(self.test_dir)
        
        # Check the result
        expected_path = os.path.join(self.test_dir, '2023-01-01_12-00-00')
        self.assertEqual(folder_path, expected_path)
        self.assertEqual(datetime_str, '2023-01-01_12-00-00')
        
        # Check that the folder was created
        self.assertTrue(os.path.exists(expected_path))
        self.assertTrue(os.path.isdir(expected_path))


class TestEnsureDirectory(unittest.TestCase):
    """Tests for the ensure_directory function."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_ensure_directory_exists(self):
        """Test ensuring a directory exists when it already exists."""
        # Call the function
        ensure_directory(self.test_dir)
        
        # Check that the directory still exists
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.isdir(self.test_dir))
    
    def test_ensure_directory_create(self):
        """Test ensuring a directory exists when it doesn't exist."""
        # Define a new directory path
        new_dir = os.path.join(self.test_dir, 'new_dir')
        
        # Call the function
        ensure_directory(new_dir)
        
        # Check that the directory was created
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))


if __name__ == '__main__':
    unittest.main()
