"""Tests for the config module."""

import os
import unittest
from unittest.mock import patch
import sys

from video_processing.config import VideoConfig, parse_arguments


class TestVideoConfig(unittest.TestCase):
    """Tests for the VideoConfig class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = VideoConfig()
        
        # Check default values
        self.assertEqual(config.segment_duration, 6)
        self.assertEqual(config.time_limit, 595)
        self.assertEqual(config.input_folder, 'INPUT')
        self.assertEqual(config.model_name, 'Model Name')
        self.assertEqual(config.fontsize, 90)
        self.assertEqual(config.watermark, 'Today is a\n Plus Day')
        self.assertEqual(config.depthflow, '0')
        self.assertEqual(config.video_orientation, 'vertical')
        self.assertEqual(config.blur, '0')
    
    def test_derived_settings(self):
        """Test that derived settings are calculated correctly."""
        config = VideoConfig(input_folder='test_folder')
        
        # Check derived settings
        self.assertEqual(config.result_folder, 'test_folder/RESULT')
        self.assertEqual(config.source_folder, 'test_folder/SOURCE')
    
    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = VideoConfig(
            segment_duration=10,
            time_limit=300,
            input_folder='custom_input',
            model_name='Custom Model',
            fontsize=120,
            watermark='Custom Watermark',
            depthflow='1',
            video_orientation='horizontal',
            blur='1'
        )
        
        # Check custom values
        self.assertEqual(config.segment_duration, 10)
        self.assertEqual(config.time_limit, 300)
        self.assertEqual(config.input_folder, 'custom_input')
        self.assertEqual(config.model_name, 'Custom Model')
        self.assertEqual(config.fontsize, 120)
        self.assertEqual(config.watermark, 'Custom Watermark')
        self.assertEqual(config.depthflow, '1')
        self.assertEqual(config.video_orientation, 'horizontal')
        self.assertEqual(config.blur, '1')


class TestParseArguments(unittest.TestCase):
    """Tests for the parse_arguments function."""
    
    @patch('sys.argv', ['main.py'])
    def test_default_arguments(self):
        """Test parsing with default arguments."""
        config = parse_arguments()
        
        # Check default values
        self.assertEqual(config.segment_duration, 6)
        self.assertEqual(config.time_limit, 595)
        self.assertEqual(config.input_folder, 'INPUT')
        self.assertEqual(config.model_name, 'Model Name')
        self.assertEqual(config.fontsize, 90)
        self.assertEqual(config.watermark, 'Today is a\n Plus Day')
        self.assertEqual(config.depthflow, '0')
        self.assertEqual(config.video_orientation, 'vertical')
        self.assertEqual(config.blur, '0')
    
    @patch('sys.argv', [
        'main.py',
        '--d', '10',
        '--tl', '300',
        '--i', 'custom_input',
        '--n', 'Custom Model',
        '--f', '120',
        '--w', 'Custom\\nWatermark',
        '--z', '1',
        '--o', 'horizontal',
        '--b', '1'
    ])
    def test_custom_arguments(self):
        """Test parsing with custom arguments."""
        config = parse_arguments()
        
        # Check custom values
        self.assertEqual(config.segment_duration, 10)
        self.assertEqual(config.time_limit, 300)
        self.assertEqual(config.input_folder, 'custom_input')
        self.assertEqual(config.model_name, 'Custom Model')
        self.assertEqual(config.fontsize, 120)
        self.assertEqual(config.watermark, 'Custom\nWatermark')
        self.assertEqual(config.depthflow, '1')
        self.assertEqual(config.video_orientation, 'horizontal')
        self.assertEqual(config.blur, '1')


if __name__ == '__main__':
    unittest.main()
