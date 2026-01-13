"""
Logging configuration for OneClick Reels AI
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Configure application logging."""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # API specific logger
    api_logger = logging.getLogger("api")
    api_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "api.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    api_handler.setFormatter(detailed_formatter)
    api_logger.addHandler(api_handler)
    
    # Video processing logger
    video_logger = logging.getLogger("video")
    video_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "video_processing.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    video_handler.setFormatter(detailed_formatter)
    video_logger.addHandler(video_handler)
    
    return root_logger

def log_api_request(endpoint: str, method: str, user_id: str = None, duration: float = None):
    """Log API request details."""
    api_logger = logging.getLogger("api")
    api_logger.info(f"{method} {endpoint} - User: {user_id} - Duration: {duration}s")

def log_video_generation(niche: str, topic: str, duration: float, success: bool, error: str = None):
    """Log video generation details."""
    video_logger = logging.getLogger("video")
    status = "SUCCESS" if success else "FAILED"
    message = f"Video generation {status} - Niche: {niche} - Topic: {topic} - Duration: {duration}s"
    if error:
        message += f" - Error: {error}"
    
    if success:
        video_logger.info(message)
    else:
        video_logger.error(message)

def log_upload_attempt(platform: str, video_id: str, success: bool, error: str = None):
    """Log upload attempt details."""
    logger = logging.getLogger("api")
    status = "SUCCESS" if success else "FAILED"
    message = f"Upload {status} - Platform: {platform} - Video: {video_id}"
    if error:
        message += f" - Error: {error}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)