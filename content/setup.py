# setup.py - Installation and setup script
import subprocess
import sys
import json
import logging

# Configure a basic logger for setup script output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def install_requirements():
    """Install required packages"""
    requirements = [
        "youtube-transcript-api==0.6.0",
        "openai",
        "requests",
        "nltk",
        "edge-tts",
        "selenium",
        "python-dotenv"
    ]
    
    logger.info("Installing requirements...")
    for requirement in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            logger.info(f"Successfully installed {requirement}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {requirement}: {e}")
            sys.exit(1)

def setup_config():
    """Setup configuration file with API keys and other settings"""
    logger.info("Setting up configuration...")
    
    config = {
        "openai_api_key": input("Enter OpenAI API Key: "),
        "pexels_api_key": input("Enter Pexels API Key: "),
        "headless_browser": input("Run browser in headless mode? (y/n, default n): ").lower().startswith('y'),
        "ai_model": "gpt-4o-mini",
        "max_tokens": int(input("Enter max tokens for AI rewrite (default 2000): ") or "2000"),
        "rewrite_prompt": input("Enter custom rewrite prompt (or press Enter for default): ") or 
                         "Rewrite this transcript to be more engaging and well-structured while maintaining the original meaning. Improve clarity, fix grammar, and make it more readable.",
        "seconds_per_image": int(input("Enter seconds per image (default 10): ") or "10"),
        "images_per_keyword_limit": int(input("Enter max images per keyword from Pexels (default 1): ") or "1"),
        "tts_voice": input("Enter TTS voice (default en-US-AriaNeural): ") or "en-US-AriaNeural",
        "tts_rate": input("Enter TTS rate (e.g., '+0%', '-10%', default '+0%'): ") or "+0%",
        "tts_volume": input("Enter TTS volume (e.g., '+0%', '-10%', default '+0%'): ") or "+0%",
        "output_dir": input("Enter output directory (default 'output'): ") or "output",
        "log_level": input("Enter logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL, default INFO): ").upper() or "INFO"
    }
    
    try:
        config_file_path = "content/config.json"
        with open(config_file_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_file_path}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_file_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()
    setup_config()
    logger.info("Setup complete! You can now run the main script.")
