"""
YouTube API Management
Full control over YouTube account - analytics, videos, playlists, comments
"""
import os
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class YouTubeManager:
    def __init__(self):
        """Initialize YouTube API client"""
        self.channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "UCzefTJDoZeWzix8az4rsUYg")
        self.youtube = None
        self._init_client()
    
    def _init_client(self):
        """Initialize YouTube API client with credentials"""
        try:
            # Use existing credentials from environment
            credentials = Credentials(
                token=os.getenv("YOUTUBE_ACCESS_TOKEN"),
                refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("YOUTUBE_CLIENT_ID"),
                client_secret=os.getenv("YOUTUBE_CLIENT_SECRET")
            )
            
            self.youtube = build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            print(f"YouTube API initialization error: {e}")
    
    # ===== Channel Info =====
    
    def get_channel_info(self) -> Dict[str, Any]:
        """Get channel information"""
        if not self.youtube:
            return {"error": "YouTube API not initialized"}
        
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics,brandingSettings,contentDetails",
                id=self.channel_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return {"error": "Channel not found"}
            
            channel = response["items"][0]
            return {
                "id": channel["id"],
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "custom_url": channel["snippet"].get("customUrl", ""),
                "published_at": channel["snippet"]["publishedAt"],
                "thumbnail": channel["snippet"]["thumbnails"]["high"]["url"],
                "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
                "video_count": int(channel["statistics"].get("videoCount", 0)),
                "view_count": int(channel["statistics"].get("viewCount", 0)),
                "uploads_playlist": channel["contentDetails"]["relatedPlaylists"]["uploads"]
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ===== Videos =====
    
    def get_recent_videos(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get recent uploaded videos"""
        if not self.youtube:
            return []
        
        try:
            # Get uploads playlist
            channel_info = self.get_channel_info()
            if "error" in channel_info:
                return []
            
            uploads_playlist = channel_info["uploads_playlist"]
            
            # Get videos from playlist
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                
                # Get video statistics
                video_details = self.get_video_details(video_id)
                
                videos.append({
                    "id": video_id,
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"],
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "shorts_url": f"https://www.youtube.com/shorts/{video_id}",
                    **video_details
                })
            
            return videos
        except Exception as e:
            print(f"Error getting videos: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get detailed video information including stats"""
        if not self.youtube:
            return {}
        
        try:
            request = self.youtube.videos().list(
                part="statistics,contentDetails,status",
                id=video_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return {}
            
            video = response["items"][0]
            return {
                "views": int(video["statistics"].get("viewCount", 0)),
                "likes": int(video["statistics"].get("likeCount", 0)),
                "comments": int(video["statistics"].get("commentCount", 0)),
                "duration": video["contentDetails"]["duration"],
                "privacy_status": video["status"]["privacyStatus"],
                "is_shorts": video["contentDetails"]["definition"] == "hd" and 
                           int(video["statistics"].get("viewCount", 0)) > 0
            }
        except Exception as e:
            print(f"Error getting video details: {e}")
            return {}
    
    def update_video(self, video_id: str, title: str = None, 
                    description: str = None, tags: List[str] = None,
                    privacy_status: str = None, category_id: str = None) -> bool:
        """Update video metadata (title, description, tags, privacy, category)"""
        if not self.youtube:
            return False
        
        try:
            # Get current video data
            request = self.youtube.videos().list(
                part="snippet,status",
                id=video_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return False
            
            video = response["items"][0]
            
            # Update fields
            if title:
                video["snippet"]["title"] = title
            if description:
                video["snippet"]["description"] = description
            if tags:
                video["snippet"]["tags"] = tags
            if category_id:
                video["snippet"]["categoryId"] = category_id
            if privacy_status:
                video["status"]["privacyStatus"] = privacy_status
            
            # Update video
            update_request = self.youtube.videos().update(
                part="snippet,status",
                body=video
            )
            update_request.execute()
            return True
        except Exception as e:
            print(f"Error updating video: {e}")
            return False
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload custom thumbnail for a video"""
        if not self.youtube:
            return False
        
        try:
            from googleapiclient.http import MediaFileUpload
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, chunksize=-1, resumable=True)
            )
            request.execute()
            return True
        except Exception as e:
            print(f"Error setting thumbnail: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """Delete a video"""
        if not self.youtube:
            return False
        
        try:
            request = self.youtube.videos().delete(id=video_id)
            request.execute()
            return True
        except Exception as e:
            print(f"Error deleting video: {e}")
            return False
    
    # ===== Analytics =====
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get channel analytics summary"""
        videos = self.get_recent_videos(max_results=50)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter videos in date range
        recent_videos = [
            v for v in videos 
            if datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")) >= start_date
        ]
        
        total_views = sum(v.get("views", 0) for v in recent_videos)
        total_likes = sum(v.get("likes", 0) for v in recent_videos)
        total_comments = sum(v.get("comments", 0) for v in recent_videos)
        
        return {
            "period_days": days,
            "videos_published": len(recent_videos),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_views_per_video": total_views // len(recent_videos) if recent_videos else 0,
            "engagement_rate": (total_likes + total_comments) / total_views * 100 if total_views > 0 else 0
        }
    
    # ===== Comments =====
    
    def get_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get comments for a video"""
        if not self.youtube:
            return []
        
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="relevance"
            )
            response = request.execute()
            
            comments = []
            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "id": item["id"],
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "likes": comment["likeCount"],
                    "published_at": comment["publishedAt"],
                    "can_reply": item["snippet"]["canReply"]
                })
            
            return comments
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        if not self.youtube:
            return False
        
        try:
            self.youtube.comments().delete(id=comment_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return False
    
    def mark_comment_as_spam(self, comment_id: str) -> bool:
        """Mark a comment as spam"""
        if not self.youtube:
            return False
        
        try:
            self.youtube.comments().markAsSpam(id=comment_id).execute()
            return True
        except Exception as e:
            print(f"Error marking comment as spam: {e}")
            return False
    
    def reply_to_comment(self, comment_id: str, reply_text: str) -> bool:
        """Reply to a comment"""
        if not self.youtube:
            return False
        
        try:
            request = self.youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": comment_id,
                        "textOriginal": reply_text
                    }
                }
            )
            request.execute()
            return True
        except Exception as e:
            print(f"Error replying to comment: {e}")
            return False
    
    # ===== Playlists =====
    
    def get_playlists(self) -> List[Dict[str, Any]]:
        """Get all playlists"""
        if not self.youtube:
            return []
        
        try:
            request = self.youtube.playlists().list(
                part="snippet,contentDetails,status",
                channelId=self.channel_id,
                maxResults=50
            )
            response = request.execute()
            
            playlists = []
            for item in response.get("items", []):
                playlists.append({
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "video_count": item["contentDetails"]["itemCount"],
                    "privacy": item["status"]["privacyStatus"],
                    "published_at": item["snippet"]["publishedAt"]
                })
            
            return playlists
        except Exception as e:
            print(f"Error getting playlists: {e}")
            return []
    
    def create_playlist(self, title: str, description: str = "", privacy: str = "private") -> Optional[str]:
        """Create a new playlist"""
        if not self.youtube:
            return None
        
        try:
            request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description
                    },
                    "status": {
                        "privacyStatus": privacy
                    }
                }
            )
            response = request.execute()
            return response["id"]
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None
    
    def update_playlist(self, playlist_id: str, title: str = None, 
                       description: str = None, privacy: str = None) -> bool:
        """Update playlist metadata"""
        if not self.youtube:
            return False
        
        try:
            # Get current playlist
            request = self.youtube.playlists().list(
                part="snippet,status",
                id=playlist_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return False
            
            playlist = response["items"][0]
            
            # Update fields
            if title:
                playlist["snippet"]["title"] = title
            if description:
                playlist["snippet"]["description"] = description
            if privacy:
                playlist["status"]["privacyStatus"] = privacy
            
            # Update playlist
            update_request = self.youtube.playlists().update(
                part="snippet,status",
                body=playlist
            )
            update_request.execute()
            return True
        except Exception as e:
            print(f"Error updating playlist: {e}")
            return False
    
    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist"""
        if not self.youtube:
            return False
        
        try:
            self.youtube.playlists().delete(id=playlist_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False
    
    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """Add a video to a playlist"""
        if not self.youtube:
            return False
        
        try:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            request.execute()
            return True
        except Exception as e:
            print(f"Error adding video to playlist: {e}")
            return False
    
    def remove_video_from_playlist(self, playlist_item_id: str) -> bool:
        """Remove a video from a playlist"""
        if not self.youtube:
            return False
        
        try:
            self.youtube.playlistItems().delete(id=playlist_item_id).execute()
            return True
        except Exception as e:
            print(f"Error removing video from playlist: {e}")
            return False
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get videos in a playlist"""
        if not self.youtube:
            return []
        
        try:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                videos.append({
                    "playlist_item_id": item["id"],
                    "video_id": item["contentDetails"]["videoId"],
                    "title": item["snippet"]["title"],
                    "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                    "position": item["snippet"]["position"]
                })
            
            return videos
        except Exception as e:
            print(f"Error getting playlist videos: {e}")
            return []

# Global instance
youtube_manager = YouTubeManager()
