"""
MAiKO Logging Utility
Structured logging for better debugging and monitoring
"""
import logging
import sys
from config import config

def setup_logging():
    """Setup logging for the application"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    root_logger.addHandler(console_handler)

    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)

# Initialize logging on import
setup_logging()
