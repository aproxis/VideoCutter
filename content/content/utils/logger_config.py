import logging
import os
from datetime import datetime

def setup_logging(log_level_str="INFO", log_file_path="app.log"):
    """
    Sets up a centralized logging configuration.
    Logs to console and a file.
    
    Args:
        log_level_str (str): The logging level as a string (e.g., "DEBUG", "INFO", "WARNING").
        log_file_path (str): The path to the log file.
    """
    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Map string level to logging constant
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.info(f"Logging set up with level: {log_level_str.upper()} and log file: {log_file_path}")

# Example usage (can be called from main.py or other entry points)
if __name__ == "__main__":
    # This part is for testing the logger_config module itself
    # In a real application, setup_logging would be called once at startup
    setup_logging(log_level_str="DEBUG", log_file_path="test_app.log")
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
