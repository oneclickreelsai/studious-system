"""
Caching system for OneClick Reels AI
"""
import os
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Dict
import pickle

class CacheManager:
    """File-based cache manager for API responses and generated content."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different cache types
        (self.cache_dir / "scripts").mkdir(exist_ok=True)
        (self.cache_dir / "videos").mkdir(exist_ok=True)
        (self.cache_dir / "api_responses").mkdir(exist_ok=True)
        (self.cache_dir / "voiceovers").mkdir(exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate a safe cache key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_type: str, key: str) -> Path:
        """Get the full path for a cache file."""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / cache_type / f"{cache_key}.cache"
    
    def set(self, cache_type: str, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store a value in cache with TTL (time to live) in seconds."""
        try:
            cache_path = self._get_cache_path(cache_type, key)
            
            cache_data = {
                "value": value,
                "timestamp": time.time(),
                "ttl": ttl,
                "key": key  # Store original key for debugging
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """Retrieve a value from cache if not expired."""
        try:
            cache_path = self._get_cache_path(cache_type, key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check if expired
            if time.time() - cache_data["timestamp"] > cache_data["ttl"]:
                # Remove expired cache
                cache_path.unlink()
                return None
            
            return cache_data["value"]
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def delete(self, cache_type: str, key: str) -> bool:
        """Delete a specific cache entry."""
        try:
            cache_path = self._get_cache_path(cache_type, key)
            if cache_path.exists():
                cache_path.unlink()
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries. Returns number of entries cleared."""
        cleared = 0
        try:
            for cache_type_dir in self.cache_dir.iterdir():
                if cache_type_dir.is_dir():
                    for cache_file in cache_type_dir.glob("*.cache"):
                        try:
                            with open(cache_file, 'rb') as f:
                                cache_data = pickle.load(f)
                            
                            if time.time() - cache_data["timestamp"] > cache_data["ttl"]:
                                cache_file.unlink()
                                cleared += 1
                        except:
                            # Remove corrupted cache files
                            cache_file.unlink()
                            cleared += 1
        except Exception as e:
            print(f"Cache cleanup error: {e}")
        
        return cleared
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "total_entries": 0,
            "total_size_mb": 0,
            "by_type": {}
        }
        
        try:
            for cache_type_dir in self.cache_dir.iterdir():
                if cache_type_dir.is_dir():
                    type_name = cache_type_dir.name
                    type_entries = 0
                    type_size = 0
                    
                    for cache_file in cache_type_dir.glob("*.cache"):
                        type_entries += 1
                        type_size += cache_file.stat().st_size
                    
                    stats["by_type"][type_name] = {
                        "entries": type_entries,
                        "size_mb": round(type_size / (1024 * 1024), 2)
                    }
                    
                    stats["total_entries"] += type_entries
                    stats["total_size_mb"] += type_size
            
            stats["total_size_mb"] = round(stats["total_size_mb"] / (1024 * 1024), 2)
        except Exception as e:
            print(f"Cache stats error: {e}")
        
        return stats

# Global cache manager instance
cache_manager = CacheManager()

def cached(cache_type: str, ttl: int = 3600, key_func: Optional[callable] = None):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_type, cache_key)
            if cached_result is not None:
                print(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_type, cache_key, result, ttl)
            print(f"Cache miss for {func.__name__} - result cached")
            
            return result
        return wrapper
    return decorator

# Specific cache functions for common use cases
def cache_script(niche: str, topic: str, script: str, ttl: int = 86400):  # 24 hours
    """Cache a generated script."""
    key = f"{niche}_{topic}"
    return cache_manager.set("scripts", key, script, ttl)

def get_cached_script(niche: str, topic: str) -> Optional[str]:
    """Get a cached script."""
    key = f"{niche}_{topic}"
    return cache_manager.get("scripts", key)

def cache_video_url(keyword: str, video_url: str, ttl: int = 3600):  # 1 hour
    """Cache a video URL for a keyword."""
    return cache_manager.set("videos", keyword, video_url, ttl)

def get_cached_video_url(keyword: str) -> Optional[str]:
    """Get a cached video URL."""
    return cache_manager.get("videos", keyword)