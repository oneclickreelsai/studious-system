"""
Simple JSON-based database for OneClick Reels AI
Stores video generation history, settings, and analytics
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

class JSONDatabase:
    def __init__(self, db_path: str = "data/database.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database with default structure"""
        if not self.db_path.exists():
            default_data = {
                "videos": [],
                "uploads": [],
                "settings": {
                    "last_updated": datetime.now().isoformat(),
                    "total_videos_generated": 0,
                    "total_uploads": 0
                },
                "analytics": {
                    "daily_stats": {},
                    "platform_stats": {
                        "youtube": {"count": 0, "views": 0},
                        "facebook": {"count": 0, "views": 0},
                        "instagram": {"count": 0, "views": 0}
                    }
                },
                "accounts": [],
                "links": []
            }
            self._write_db(default_data)
    
    def _read_db(self) -> Dict:
        """Read database file"""
        with self.lock:
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to read database: {e}")
                return {}
    
    def _write_db(self, data: Dict):
        """Write to database file"""
        with self.lock:
            try:
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[ERROR] Failed to write database: {e}")
    
    def add_video(self, title: str, niche: str, topic: str, script: str, 
                  file_path: str = "", duration: float = 0, **kwargs) -> Dict:
        """Add a generated video to database"""
        data = self._read_db()
        
        video = {
            "id": len(data["videos"]) + 1,
            "title": title,
            "niche": niche,
            "topic": topic,
            "script": script,
            "file_path": file_path,
            "duration": duration,
            "created_at": datetime.now().isoformat(),
            "status": "generated",
            **kwargs
        }
        
        data["videos"].append(video)
        data["settings"]["total_videos_generated"] += 1
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["analytics"]["daily_stats"]:
            data["analytics"]["daily_stats"][today] = {"videos": 0, "uploads": 0}
        data["analytics"]["daily_stats"][today]["videos"] += 1
        
        self._write_db(data)
        return video
    
    def add_upload(self, video_id: int, platform: str, platform_id: str, 
                   url: str = "", **kwargs) -> Dict:
        """Add an upload record"""
        data = self._read_db()
        
        upload = {
            "id": len(data["uploads"]) + 1,
            "video_id": video_id,
            "platform": platform,
            "platform_id": platform_id,
            "url": url,
            "uploaded_at": datetime.now().isoformat(),
            "status": "uploaded",
            **kwargs
        }
        
        data["uploads"].append(upload)
        data["settings"]["total_uploads"] += 1
        
        # Update platform stats
        if platform in data["analytics"]["platform_stats"]:
            data["analytics"]["platform_stats"][platform]["count"] += 1
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["analytics"]["daily_stats"]:
            data["analytics"]["daily_stats"][today] = {"videos": 0, "uploads": 0}
        data["analytics"]["daily_stats"][today]["uploads"] += 1
        
        self._write_db(data)
        return upload
    
    def get_videos(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get list of videos"""
        data = self._read_db()
        videos = data.get("videos", [])
        # Return newest first
        videos.reverse()
        return videos[offset:offset + limit]
    
    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        """Get a specific video by ID"""
        data = self._read_db()
        for video in data.get("videos", []):
            if video["id"] == video_id:
                return video
        return None
    
    def get_uploads(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get list of uploads"""
        data = self._read_db()
        uploads = data.get("uploads", [])
        uploads.reverse()
        return uploads[offset:offset + limit]
    
    def get_total_stats(self) -> Dict:
        """Get total statistics"""
        data = self._read_db()
        return {
            "total_videos": len(data.get("videos", [])),
            "total_uploads": len(data.get("uploads", [])),
            "platform_stats": data.get("analytics", {}).get("platform_stats", {}),
            "last_updated": data.get("settings", {}).get("last_updated", "")
        }
    
    def get_analytics(self, days: int = 30) -> Dict:
        """Get analytics for the last N days"""
        data = self._read_db()
        daily_stats = data.get("analytics", {}).get("daily_stats", {})
        
        # Get last N days
        from datetime import timedelta
        today = datetime.now()
        result = {}
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            result[date] = daily_stats.get(date, {"videos": 0, "uploads": 0})
        
        return {
            "daily_stats": result,
            "platform_stats": data.get("analytics", {}).get("platform_stats", {}),
            "total_videos": len(data.get("videos", [])),
            "total_uploads": len(data.get("uploads", []))
        }
    
    def add_account(self, platform: str, username: str, **kwargs) -> Dict:
        """Add a social media account"""
        data = self._read_db()
        
        account = {
            "id": len(data["accounts"]) + 1,
            "platform": platform,
            "username": username,
            "added_at": datetime.now().isoformat(),
            "status": "active",
            **kwargs
        }
        
        data["accounts"].append(account)
        self._write_db(data)
        return account
    
    def get_accounts(self) -> List[Dict]:
        """Get all accounts"""
        data = self._read_db()
        return data.get("accounts", [])
    
    def add_link(self, title: str, url: str, category: str = "general", **kwargs) -> Dict:
        """Add a useful link"""
        data = self._read_db()
        
        link = {
            "id": len(data["links"]) + 1,
            "title": title,
            "url": url,
            "category": category,
            "added_at": datetime.now().isoformat(),
            **kwargs
        }
        
        data["links"].append(link)
        self._write_db(data)
        return link
    
    def get_links(self, category: Optional[str] = None) -> List[Dict]:
        """Get all links, optionally filtered by category"""
        data = self._read_db()
        links = data.get("links", [])
        
        if category:
            links = [l for l in links if l.get("category") == category]
        
        return links
    
    def update_video_status(self, video_id: int, status: str, **kwargs):
        """Update video status"""
        data = self._read_db()
        
        for video in data["videos"]:
            if video["id"] == video_id:
                video["status"] = status
                video["updated_at"] = datetime.now().isoformat()
                video.update(kwargs)
                break
        
        self._write_db(data)
    
    def search_videos(self, query: str, limit: int = 20) -> List[Dict]:
        """Search videos by title, niche, or topic"""
        data = self._read_db()
        query_lower = query.lower()
        
        results = []
        for video in data.get("videos", []):
            if (query_lower in video.get("title", "").lower() or
                query_lower in video.get("niche", "").lower() or
                query_lower in video.get("topic", "").lower()):
                results.append(video)
                if len(results) >= limit:
                    break
        
        return results

# Singleton instance
db = JSONDatabase()

if __name__ == "__main__":
    # Test the database
    print("Testing JSON Database...")
    
    # Add a test video
    video = db.add_video(
        title="Test Video",
        niche="motivation",
        topic="discipline",
        script="Test script content",
        file_path="output/test.mp4",
        duration=30.5
    )
    print(f"Added video: {video}")
    
    # Add a test upload
    upload = db.add_upload(
        video_id=video["id"],
        platform="youtube",
        platform_id="test123",
        url="https://youtube.com/watch?v=test123"
    )
    print(f"Added upload: {upload}")
    
    # Get stats
    stats = db.get_total_stats()
    print(f"Total stats: {stats}")
    
    # Get analytics
    analytics = db.get_analytics(days=7)
    print(f"Analytics: {analytics}")
    
    print("\nDatabase test complete!")
