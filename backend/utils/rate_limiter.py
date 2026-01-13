"""
Rate limiting utilities for API protection
"""
import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict, deque
import threading

class RateLimiter:
    """Thread-safe rate limiter using token bucket algorithm."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier."""
        with self.lock:
            now = time.time()
            request_times = self.requests[identifier]
            
            # Remove old requests outside time window
            while request_times and request_times[0] <= now - self.time_window:
                request_times.popleft()
            
            # Check if under limit
            if len(request_times) < self.max_requests:
                request_times.append(now)
                return True
            
            return False
    
    def time_until_allowed(self, identifier: str) -> float:
        """Get seconds until next request is allowed."""
        with self.lock:
            now = time.time()
            request_times = self.requests[identifier]
            
            if len(request_times) < self.max_requests:
                return 0.0
            
            # Time until oldest request expires
            oldest_request = request_times[0]
            return max(0.0, (oldest_request + self.time_window) - now)

class APIRateLimiter:
    """Rate limiter for different API endpoints."""
    
    def __init__(self):
        self.limiters = {
            # OpenAI API limits
            "openai": RateLimiter(max_requests=60, time_window=60),  # 60 per minute
            
            # YouTube API limits
            "youtube_upload": RateLimiter(max_requests=6, time_window=3600),  # 6 per hour
            "youtube_api": RateLimiter(max_requests=100, time_window=100),  # 100 per 100 seconds
            
            # Pexels API limits
            "pexels": RateLimiter(max_requests=200, time_window=3600),  # 200 per hour
            
            # Pixabay API limits
            "pixabay": RateLimiter(max_requests=5000, time_window=3600),  # 5000 per hour
            
            # Facebook API limits
            "facebook": RateLimiter(max_requests=200, time_window=3600),  # 200 per hour
            
            # General API limits per user
            "user_api": RateLimiter(max_requests=100, time_window=3600),  # 100 per hour per user
        }
    
    def check_limit(self, service: str, identifier: str = "default") -> bool:
        """Check if request is within rate limit."""
        if service not in self.limiters:
            return True
        
        return self.limiters[service].is_allowed(identifier)
    
    def wait_time(self, service: str, identifier: str = "default") -> float:
        """Get wait time until next request is allowed."""
        if service not in self.limiters:
            return 0.0
        
        return self.limiters[service].time_until_allowed(identifier)
    
    async def wait_if_needed(self, service: str, identifier: str = "default"):
        """Async wait if rate limit exceeded."""
        wait_time = self.wait_time(service, identifier)
        if wait_time > 0:
            await asyncio.sleep(wait_time)

# Global rate limiter instance
api_rate_limiter = APIRateLimiter()

def rate_limit(service: str, identifier_func: Optional[callable] = None):
    """Decorator for rate limiting functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            identifier = "default"
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            
            if not api_rate_limiter.check_limit(service, identifier):
                wait_time = api_rate_limiter.wait_time(service, identifier)
                raise Exception(f"Rate limit exceeded for {service}. Try again in {wait_time:.1f} seconds.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def async_rate_limit(service: str, identifier_func: Optional[callable] = None):
    """Async decorator for rate limiting functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            identifier = "default"
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            
            await api_rate_limiter.wait_if_needed(service, identifier)
            return await func(*args, **kwargs)
        return wrapper
    return decorator