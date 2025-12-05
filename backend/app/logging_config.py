"""Logging configuration for Daily Ad Agent backend."""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(app=None):
    """
    Configure logging with:
    - Day-wise log files in logs/ folder (DEBUG and above)
    - Console output for ERROR only
    """
    # Determine log directory - relative to backend folder
    if app:
        log_dir = Path(app.root_path).parent / 'logs'
    else:
        log_dir = Path(__file__).parent.parent / 'logs'

    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True)

    # Log file path with date suffix (handled by TimedRotatingFileHandler)
    log_file = log_dir / 'dailyadagent.log'

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Create file handler - rotates at midnight, keeps 30 days of logs
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    file_handler.suffix = '%Y-%m-%d'  # Adds date suffix to rotated files

    # Create console handler - ERROR only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(console_formatter)

    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    # Reduce verbosity of some third-party libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.INFO)
    logging.getLogger('langchain_core').setLevel(logging.INFO)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - logs directory: {log_dir}")
    logger.info(f"Console: ERROR only | File: DEBUG and above")

    return log_dir
