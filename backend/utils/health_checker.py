"""
Health check utilities for external services
"""
import os
import time
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class HealthChecker:
    """Check health of external services and APIs."""
    
    def __init__(self):
        self.last_check = {}
        self.check_interval = 300  # 5 minutes
    
    def check_perplexity(self) -> Dict[str, Any]:
        """Check Perplexity API health (PRIMARY AI)."""
        try:
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                return {
                    "service": "perplexity",
                    "status": "unhealthy",
                    "error": "No API key configured",
                    "details": "PERPLEXITY_API_KEY not set"
                }
            
            client = OpenAI(
                base_url="https://api.perplexity.ai",
                api_key=api_key,
                timeout=10.0
            )
            
            response = client.chat.completions.create(
                model="sonar",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            
            return {
                "service": "perplexity",
                "status": "healthy",
                "response_time": time.time(),
                "details": "API responding normally (PRIMARY)"
            }
        except Exception as e:
            return {
                "service": "perplexity",
                "status": "unhealthy",
                "error": str(e),
                "details": "API request failed"
            }
    
    def check_openai(self) -> Dict[str, Any]:
        """Check OpenAI API health (FALLBACK only) - just verify key exists, don't call API."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return {
                    "service": "openai",
                    "status": "unhealthy",
                    "error": "No API key configured",
                    "details": "OPENAI_API_KEY not set (fallback)"
                }
            
            # Don't make actual API call - OpenAI has strict rate limits
            # Just verify the key is configured
            return {
                "service": "openai",
                "status": "healthy",
                "response_time": time.time(),
                "details": "API key configured (FALLBACK - not tested to avoid rate limits)"
            }
        except Exception as e:
            return {
                "service": "openai",
                "status": "unhealthy",
                "error": str(e),
                "details": "Configuration check failed (fallback)"
            }
    
    def check_youtube(self) -> Dict[str, Any]:
        """Check YouTube API health."""
        try:
            creds = Credentials(
                None,
                refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("YOUTUBE_CLIENT_ID"),
                client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            )
            
            youtube = build("youtube", "v3", credentials=creds)
            
            # Simple test request - get channel info
            response = youtube.channels().list(
                part="snippet",
                mine=True
            ).execute()
            
            return {
                "service": "youtube",
                "status": "healthy",
                "response_time": time.time(),
                "details": f"Connected to channel: {response.get('items', [{}])[0].get('snippet', {}).get('title', 'Unknown')}"
            }
        except Exception as e:
            return {
                "service": "youtube",
                "status": "unhealthy",
                "error": str(e),
                "details": "YouTube API connection failed"
            }
    
    def check_pexels(self) -> Dict[str, Any]:
        """Check Pexels API health."""
        try:
            api_key = os.getenv("PEXELS_API_KEY")
            if not api_key:
                return {
                    "service": "pexels",
                    "status": "unhealthy",
                    "error": "No API key configured",
                    "details": "PEXELS_API_KEY not set"
                }
            
            headers = {"Authorization": api_key}
            response = requests.get(
                "https://api.pexels.com/videos/search?query=test&per_page=1",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "service": "pexels",
                    "status": "healthy",
                    "response_time": time.time(),
                    "details": "API responding normally"
                }
            else:
                return {
                    "service": "pexels",
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "details": response.text[:200]
                }
        except Exception as e:
            return {
                "service": "pexels",
                "status": "unhealthy",
                "error": str(e),
                "details": "API request failed"
            }
    
    def check_pixabay(self) -> Dict[str, Any]:
        """Check Pixabay API health."""
        try:
            api_key = os.getenv("PIXABAY_API_KEY")
            if not api_key:
                return {
                    "service": "pixabay",
                    "status": "unhealthy",
                    "error": "No API key configured",
                    "details": "PIXABAY_API_KEY not set"
                }
            
            response = requests.get(
                f"https://pixabay.com/api/videos/?key={api_key}&q=test&per_page=3",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "service": "pixabay",
                    "status": "healthy",
                    "response_time": time.time(),
                    "details": "API responding normally"
                }
            else:
                return {
                    "service": "pixabay",
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "details": response.text[:200]
                }
        except Exception as e:
            return {
                "service": "pixabay",
                "status": "unhealthy",
                "error": str(e),
                "details": "API request failed"
            }
    
    def check_facebook(self) -> Dict[str, Any]:
        """Check Facebook API health."""
        try:
            page_id = os.getenv("FB_PAGE_ID")
            access_token = os.getenv("FB_ACCESS_TOKEN")
            
            if not page_id or not access_token:
                return {
                    "service": "facebook",
                    "status": "unhealthy",
                    "error": "No credentials configured",
                    "details": "FB_PAGE_ID or FB_ACCESS_TOKEN not set"
                }
            
            response = requests.get(
                f"https://graph.facebook.com/v19.0/{page_id}?access_token={access_token}&fields=name",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "service": "facebook",
                    "status": "healthy",
                    "response_time": time.time(),
                    "details": f"Connected to page: {data.get('name', 'Unknown')}"
                }
            else:
                return {
                    "service": "facebook",
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "details": response.text[:200]
                }
        except Exception as e:
            return {
                "service": "facebook",
                "status": "unhealthy",
                "error": str(e),
                "details": "API request failed"
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """Check health of all configured services."""
        results = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "services": {}
        }
        
        # Check each service - Perplexity FIRST (primary)
        services = [
            ("perplexity", self.check_perplexity),
            ("openai", self.check_openai),
            ("youtube", self.check_youtube),
            ("pexels", self.check_pexels),
            ("pixabay", self.check_pixabay),
            ("facebook", self.check_facebook),
        ]
        
        unhealthy_count = 0
        for service_name, check_func in services:
            try:
                service_result = check_func()
                results["services"][service_name] = service_result
                
                if service_result["status"] == "unhealthy":
                    unhealthy_count += 1
                    
            except Exception as e:
                results["services"][service_name] = {
                    "service": service_name,
                    "status": "unhealthy",
                    "error": str(e),
                    "details": "Health check failed"
                }
                unhealthy_count += 1
        
        # Determine overall status
        if unhealthy_count == 0:
            results["overall_status"] = "healthy"
        elif unhealthy_count < len(services):
            results["overall_status"] = "degraded"
        else:
            results["overall_status"] = "unhealthy"
        
        results["healthy_services"] = len(services) - unhealthy_count
        results["total_services"] = len(services)
        
        return results
    
    def get_cached_health_check(self) -> Optional[Dict[str, Any]]:
        """Get cached health check results if recent enough."""
        if "all_services" in self.last_check:
            last_time = self.last_check["all_services"].get("timestamp", 0)
            if time.time() - last_time < self.check_interval:
                return self.last_check["all_services"]
        return None
    
    def health_check_with_cache(self) -> Dict[str, Any]:
        """Get health check results with caching."""
        cached_result = self.get_cached_health_check()
        if cached_result:
            cached_result["from_cache"] = True
            return cached_result
        
        result = self.check_all_services()
        result["from_cache"] = False
        self.last_check["all_services"] = result
        
        return result

# Global health checker instance
health_checker = HealthChecker()