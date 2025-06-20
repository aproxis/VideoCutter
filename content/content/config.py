# config.py - Configuration management
import json
import os
from pathlib import Path

class Config:
    def __init__(self, config_path="content/config.json"):
        self.config_path = config_path
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = self.create_default_config()
            self.save_config(config_data)
        
        # API Keys
        self.openai_api_key = config_data.get('openai_api_key', '')
        self.pexels_api_key = config_data.get('pexels_api_key', '')
        
        # YouTube Settings (Selenium only)
        self.headless_browser = config_data.get('headless_browser', False)
        self.keep_browser_open = config_data.get('keep_browser_open', False) # New setting
        
        # AI Settings
        self.ai_model = config_data.get('ai_model', 'gpt-4o-mini')
        self.max_tokens = config_data.get('max_tokens', 2000)
        self.rewrite_prompt = config_data.get('rewrite_prompt', 
            "Rewrite this transcript to be more engaging and well-structured while maintaining the original meaning. "
            "Improve clarity, fix grammar, and make it more readable.")
        
        # Image Settings
        self.seconds_per_image = config_data.get('seconds_per_image', 10)
        self.images_per_keyword_limit = config_data.get('images_per_keyword_limit', 1) # New configurable limit

        # TTS Settings
        self.tts_voice = config_data.get('tts_voice', 'en-US-AriaNeural')
        self.tts_rate = config_data.get('tts_rate', '+0%')
        self.tts_volume = config_data.get('tts_volume', '+0%')
        
        # Output Settings
        self.output_dir = config_data.get('output_dir', 'output')

        # Logging Settings
        self.log_level = config_data.get('log_level', 'INFO') # New configurable log level
        self.log_file = config_data.get('log_file', 'logs/openai_usage_log.csv') # New setting for OpenAI usage log
    
    def create_default_config(self):
        """Create default configuration"""
        return {
            "openai_api_key": "",
            "pexels_api_key": "",
            "headless_browser": False,
            "keep_browser_open": False, # Default for new setting
            "ai_model": "gpt-4o-mini",
            "max_tokens": 2000,
            "rewrite_prompt": "Rewrite this transcript to be more engaging and well-structured while maintaining the original meaning. Improve clarity, fix grammar, and make it more readable.",
            "seconds_per_image": 10,
            "images_per_keyword_limit": 1, # Default for new setting
            "tts_voice": "en-US-AriaNeural",
            "tts_rate": "+0%",
            "tts_volume": "+0%",
            "output_dir": "output",
            "log_level": "INFO", # Default for new setting
            "log_file": "logs/openai_usage_log.csv" # Default for new setting
        }
    
    def save_config(self, config_data):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def update_rewrite_prompt(self, new_prompt):
        """Update the AI rewrite prompt"""
        self.rewrite_prompt = new_prompt
        config_data = self.create_default_config()
        config_data['rewrite_prompt'] = new_prompt
        self.save_config(config_data)
    
    def save_gui_settings(self, gui_settings):
        """Save GUI-specific settings to config.json."""
        config_data = self.load_config_data() # Load current data to merge
        config_data['gui_settings'] = gui_settings
        self.save_config(config_data)

    def load_gui_settings(self):
        """Load GUI-specific settings from config.json."""
        config_data = self.load_config_data()
        return config_data.get('gui_settings', {})

    def load_config_data(self):
        """Helper to load raw config data from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {} # Return empty dict if file doesn't exist
