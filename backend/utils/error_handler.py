"""
Centralized error handling and retry logic
"""
import time
import logging
import functools
from typing import Callable, Any, Optional, Type, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    FILE_ERROR = "file_error"
    PROCESSING_ERROR = "processing_error"
    VALIDATION_ERROR = "validation_error"

class RetryableError(Exception):
    """Exception that can be retried."""
    def __init__(self, message: str, error_type: ErrorType, retry_after: int = 1):
        super().__init__(message)
        self.error_type = error_type
        self.retry_after = retry_after

class NonRetryableError(Exception):
    """Exception that should not be retried."""
    def __init__(self, message: str, error_type: ErrorType):
        super().__init__(message)
        self.error_type = error_type

def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    # Check if it's a non-retryable error
                    if isinstance(e, NonRetryableError):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    wait_time = backoff_factor ** attempt
                    if isinstance(e, RetryableError):
                        wait_time = max(wait_time, e.retry_after)
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            
            raise last_exception
        
        return wrapper
    return decorator

def handle_api_error(func: Callable) -> Callable:
    """Decorator for handling API errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"API error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            
            # Classify error type
            if "rate limit" in str(e).lower():
                raise RetryableError(error_msg, ErrorType.API_ERROR, retry_after=60)
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                raise RetryableError(error_msg, ErrorType.NETWORK_ERROR)
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise NonRetryableError(error_msg, ErrorType.API_ERROR)
            else:
                raise RetryableError(error_msg, ErrorType.API_ERROR)
    
    return wrapper

def safe_file_operation(func: Callable) -> Callable:
    """Decorator for safe file operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            error_msg = f"File not found in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise NonRetryableError(error_msg, ErrorType.FILE_ERROR)
        except PermissionError as e:
            error_msg = f"Permission denied in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise NonRetryableError(error_msg, ErrorType.FILE_ERROR)
        except OSError as e:
            error_msg = f"OS error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise RetryableError(error_msg, ErrorType.FILE_ERROR)
    
    return wrapper

class ErrorTracker:
    """Track and analyze errors for monitoring."""
    
    def __init__(self):
        self.errors = []
    
    def log_error(self, error: Exception, context: dict = None):
        """Log an error with context."""
        error_data = {
            "timestamp": time.time(),
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context or {}
        }
        self.errors.append(error_data)
        logger.error(f"Error tracked: {error_data}")
    
    def get_error_stats(self, hours: int = 24) -> dict:
        """Get error statistics for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)
        recent_errors = [e for e in self.errors if e["timestamp"] > cutoff_time]
        
        error_counts = {}
        for error in recent_errors:
            error_type = error["error_type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "error_types": error_counts,
            "error_rate": len(recent_errors) / hours if hours > 0 else 0
        }

# Global error tracker instance
error_tracker = ErrorTracker()