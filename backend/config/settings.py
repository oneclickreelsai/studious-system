"""
Application settings and configuration management
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

class Settings:
    """Application settings with validation and defaults."""
    
    def __init__(self):
        self.validate_required_settings()
    
    # API Keys
    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def pexels_api_key(self) -> str:
        return os.getenv("PEXELS_API_KEY", "")
    
    @property
    def pixabay_api_key(self) -> str:
        return os.getenv("PIXABAY_API_KEY", "")
    
    @property
    def perplexity_api_key(self) -> str:
        return os.getenv("PERPLEXITY_API_KEY", "")
    
    # YouTube Settings
    @property
    def youtube_client_id(self) -> str:
        return os.getenv("YOUTUBE_CLIENT_ID", "")
    
    @property
    def youtube_client_secret(self) -> str:
        return os.getenv("YOUTUBE_CLIENT_SECRET", "")
    
    @property
    def youtube_refresh_token(self) -> str:
        return os.getenv("YOUTUBE_REFRESH_TOKEN", "")
    
    # Facebook Settings
    @property
    def fb_page_id(self) -> str:
        return os.getenv("FB_PAGE_ID", "")
    
    @property
    def fb_access_token(self) -> str:
        return os.getenv("FB_ACCESS_TOKEN", "")
    
    # Security Settings
    @property
    def jwt_secret_key(self) -> str:
        return os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
    
    @property
    def admin_username(self) -> str:
        return os.getenv("ADMIN_USERNAME", "admin")
    
    @property
    def admin_password(self) -> str:
        return os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Application Settings
    @property
    def debug_mode(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def max_video_duration(self) -> int:
        return int(os.getenv("MAX_VIDEO_DURATION", "60"))  # seconds
    
    @property
    def default_privacy_status(self) -> str:
        return os.getenv("DEFAULT_PRIVACY_STATUS", "public")
    
    @property
    def enable_caching(self) -> bool:
        return os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    @property
    def cache_ttl(self) -> int:
        return int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # File Paths
    @property
    def assets_dir(self) -> Path:
        return Path("assets")
    
    @property
    def output_dir(self) -> Path:
        return Path("output")
    
    @property
    def cache_dir(self) -> Path:
        return Path("cache")
    
    @property
    def logs_dir(self) -> Path:
        return Path("logs")
    
    # Video Settings
    @property
    def video_resolution(self) -> tuple:
        width = int(os.getenv("VIDEO_WIDTH", "1080"))
        height = int(os.getenv("VIDEO_HEIGHT", "1920"))
        return (width, height)
    
    @property
    def video_fps(self) -> int:
        return int(os.getenv("VIDEO_FPS", "30"))
    
    @property
    def video_bitrate(self) -> str:
        return os.getenv("VIDEO_BITRATE", "2M")
    
    # Voice Settings
    @property
    def default_voice(self) -> str:
        return os.getenv("DEFAULT_VOICE", "en-US-ChristopherNeural")
    
    @property
    def comedy_voice(self) -> str:
        return os.getenv("COMEDY_VOICE", "en-IN-PrabhatNeural")
    
    def validate_required_settings(self):
        """Validate that required settings are present."""
        required_settings = [
            ("OPENAI_API_KEY", self.openai_api_key),
        ]
        
        missing_settings = []
        for setting_name, setting_value in required_settings:
            if not setting_value:
                missing_settings.append(setting_name)
        
        if missing_settings:
            raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary (excluding sensitive data)."""
        return {
            "debug_mode": self.debug_mode,
            "max_video_duration": self.max_video_duration,
            "default_privacy_status": self.default_privacy_status,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "video_resolution": self.video_resolution,
            "video_fps": self.video_fps,
            "video_bitrate": self.video_bitrate,
            "default_voice": self.default_voice,
            "comedy_voice": self.comedy_voice,
            "has_openai_key": bool(self.openai_api_key),
            "has_youtube_credentials": bool(self.youtube_client_id and self.youtube_client_secret),
            "has_facebook_credentials": bool(self.fb_page_id and self.fb_access_token),
            "has_pexels_key": bool(self.pexels_api_key),
            "has_pixabay_key": bool(self.pixabay_api_key),
        }
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.assets_dir,
            self.output_dir,
            self.cache_dir,
            self.logs_dir,
            self.assets_dir / "videos",
            self.assets_dir / "music",
            self.assets_dir / "fonts",
            self.assets_dir / "images",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()