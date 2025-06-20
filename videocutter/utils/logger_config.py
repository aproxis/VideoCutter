import logging
import os

def setup_logging(config_settings):
    """
    Sets up the logging configuration for the application based on provided settings.
    Each module/section can have its logging level configured.

    Args:
        config_settings (dict): A dictionary containing logging settings,
                                typically from the application's main configuration.
                                Expected format:
                                {
                                    "logging": {
                                        "main": "INFO",
                                        "gui": "INFO",
                                        "video_processor": "INFO",
                                        "audio_processor": "INFO",
                                        "subtitle_generator": "INFO",
                                        "depth_processor": "INFO",
                                        "overlay_compositor": "INFO",
                                        "file_utils": "INFO",
                                        "config_manager": "INFO",
                                        "gui_config_manager": "INFO",
                                        "root": "INFO" # Default for any unconfigured logger
                                    }
                                }
    """
    # Clear existing handlers to prevent duplicate logs if called multiple times
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.propagate = True # Ensure messages propagate to root handler

    log_config = config_settings.get("logging", {})

    # Configure a basic console handler for the root logger
    # This will catch messages from all loggers unless they are specifically handled
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.root.addHandler(console_handler)

    # Set default level for the root logger
    # Determine root logging level based on debug_logging_enabled flag
    debug_logging_enabled = config_settings.get("debug_logging_enabled", False)
    if debug_logging_enabled:
        root_level = logging.DEBUG
    else:
        root_level = getattr(logging, log_config.get("root", "INFO").upper(), logging.INFO) # Fallback to config or INFO

    logging.root.setLevel(root_level)
    console_handler.setLevel(root_level) # Ensure handler also processes messages at this level

    # Configure specific loggers based on config_settings
    module_loggers = {
        "main": "videocutter.main",
        "gui": "gui", # The main GUI script
        "video_processor": "videocutter.processing.video_processor",
        "audio_processor": "videocutter.processing.audio_processor",
        "subtitle_generator": "videocutter.processing.subtitle_generator",
        "depth_processor": "videocutter.processing.depth_processor",
        "overlay_compositor": "videocutter.processing.overlay_compositor",
        "file_utils": "videocutter.utils.file_utils",
        "config_manager": "videocutter.config_manager",
        "gui_config_manager": "videocutter.utils.gui_config_manager",
        "font_utils": "videocutter.utils.font_utils",
        "slideshow_generator": "videocutter.processing.slideshow_generator",
        "depthflow_settings_frame": "videocutter.gui.depthflow_settings_frame",
        "gui_utils": "videocutter.gui.gui_utils",
        "main_settings_frame": "videocutter.gui.main_settings_frame",
        "overlay_effects_frame": "videocutter.gui.overlay_effects_frame",
        "subtitle_settings_frame": "videocutter.gui.subtitle_settings_frame",
        "title_settings_frame": "videocutter.gui.title_settings_frame",
        "punctuation_utils": "videocutter.utils.punctuation_utils",
        "subtitle_processing_utils": "videocutter.utils.subtitle_processing_utils",
    }

    for section, logger_name in module_loggers.items():
        level_str = log_config.get(section, logging.getLevelName(root_level)).upper()
        level = getattr(logging, level_str, root_level)
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        # Prevent propagation to root if specific handler is desired for this logger
        # For now, let them propagate to the console_handler set on root
        logger.propagate = True

    # Special handling for external libraries if needed, e.g., ffmpeg-python, whisperx
    # logging.getLogger('ffmpeg').setLevel(logging.WARNING)
    # logging.getLogger('whisperx').setLevel(logging.WARNING)

    logging.info("Logging setup complete.")

if __name__ == "__main__":
    # Example usage for testing
    logging.info("Testing logger_config.py directly...")
    mock_config = {
        "logging": {
            "main": "DEBUG",
            "gui": "INFO",
            "video_processor": "WARNING",
            "root": "DEBUG"
        }
    }
    setup_logging(mock_config)

    # Test messages from different loggers
    logging.getLogger("videocutter.main").debug("This is a debug message from main.")
    logging.getLogger("videocutter.main").info("This is an info message from main.")
    logging.getLogger("videocutter.processing.video_processor").debug("This debug message from video_processor should not appear.")
    logging.getLogger("videocutter.processing.video_processor").warning("This is a warning message from video_processor.")
    logging.getLogger("gui").info("This is an info message from gui.")
    logging.getLogger("some.other.module").debug("This debug message from an unconfigured module should appear (root is DEBUG).")
    logging.getLogger("some.other.module").info("This info message from an unconfigured module should appear.")
