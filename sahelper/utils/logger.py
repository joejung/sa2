import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="sahelper", level=logging.DEBUG):
    """Sets up a robust logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if already setup
    if logger.hasHandlers():
        return logger

    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", "sahelper.log")

    # File Handler (Rotating: 5MB per file, keep 3)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

# Singleton-style accessor
app_logger = setup_logger()
