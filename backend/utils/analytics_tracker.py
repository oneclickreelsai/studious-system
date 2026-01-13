"""
Advanced analytics and performance tracking
"""
import os
import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from backend.database.db_manager import DatabaseManager
from backend.utils.monitoring import performance_monitor
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Track and analyze video performance and user behavior."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def track_video_generation(
        self,
        niche: str,
        topic: str,
        script: str,
        generation_time: float,
        success: bool,
        file_size_mb: float = 0,
        error_message: str = None
    ) -> int:
        """Track video generation event."""
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Insert video record
            cursor.execute("""
                INSERT INTO videos (
                    title, niche, topic, script, file_path, duration_seconds,
                    file_size_mb, generation_mode, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{niche.title()} - {topic}",
                niche,
                topic,
                script,
                f"output/video_{int(time.time())}.mp4" if success else None,
                0,  # Duration will be updated later
                file_size_mb,
                "ai_generated",
                datetime.now()
            ))
            
            video_id = cursor.lastrowid
            
            # Track analytics
            cursor.execute("""
                INSERT OR REPLACE INTO analytics (
                    date, videos_generated, generation_time_avg, success_rate, errors
                ) VALUES (
                    DATE('now'),
                    COALESCE((SELECT videos_generated FROM analytics WHERE date = DATE('now')), 0) + 1,
                    ?,
                    ?,
                    COALESCE((SELECT errors FROM analytics WHERE date = DATE('now')), 0) + ?
                )
            """, (
                generation_time,
                1.0 if success else 0.0,
                0 if success else 1
            ))
            
            conn.commit()
            conn.close()
            
            # Update performance monitor
            performance_monitor.record_video_generation(generation_time, success, niche)
            
            logger.info(f"Tracked video generation: {niche}/{topic}, success: {success}")
            return video_id
            
        except Exception as e:
            logger.error(f"Failed to track video generation: {e}")
            return 0
    
    def track_upload(
        self,
        video_id: int,
        platform: str,
        platform_video_id: str,
        success: bool,
        upload_time: float = 0,
        error_message: str = None
    ) -> int:
        """Track video upload event."""
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get or create account record
            cursor.execute("""
                SELECT id FROM accounts WHERE platform = ? AND is_active = 1 LIMIT 1
            """, (platform,))
            
            account_result = cursor.fetchone()
            if not account_result:
                # Create default account record
                cursor.execute("""
                    INSERT INTO accounts (platform, account_name, is_active)
                    VALUES (?, ?, 1)
                """, (platform, f"Default {platform.title()} Account"))
                account_id = cursor.lastrowid
            else:
                account_id = account_result[0]
            
            # Insert upload record
            cursor.execute("""
                INSERT INTO uploads (
                    video_id, account_id, platform, platform_video_id,
                    platform_url, uploaded_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                video_id,
                account_id,
                platform,
                platform_video_id if success else None,
                self._generate_platform_url(platform, platform_video_id) if success else None,
                datetime.now()
            ))
            
            upload_id = cursor.lastrowid
            
            # Update daily analytics
            cursor.execute("""
                INSERT OR REPLACE INTO analytics (
                    date, videos_uploaded, upload_success_rate
                ) VALUES (
                    DATE('now'),
                    COALESCE((SELECT videos_uploaded FROM analytics WHERE date = DATE('now')), 0) + 1,
                    ?
                )
            """, (1.0 if success else 0.0,))
            
            conn.commit()
            conn.close()
            
            # Update performance monitor
            performance_monitor.record_upload(platform, success, upload_time)
            
            logger.info(f"Tracked upload: video_id={video_id}, platform={platform}, success={success}")
            return upload_id
            
        except Exception as e:
            logger.error(f"Failed to track upload: {e}")
            return 0
    
    def update_video_metrics(
        self,
        platform_video_id: str,
        platform: str,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0
    ):
        """Update video performance metrics."""
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE uploads SET
                    views = ?, likes = ?, comments = ?, shares = ?,
                    last_synced_at = ?
                WHERE platform_video_id = ? AND platform = ?
            """, (views, likes, comments, shares, datetime.now(), platform_video_id, platform))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated metrics for {platform} video {platform_video_id}")
            
        except Exception as e:
            logger.error(f"Failed to update video metrics: {e}")
    
    def get_performance_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data."""
        
        cache_key = f"dashboard_{days}"
        if self._is_cache_valid(cache_key):
            return self.analytics_cache[cache_key]["data"]
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Date range
            start_date = datetime.now() - timedelta(days=days)
            
            # Video generation stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_videos,
                    AVG(file_size_mb) as avg_file_size,
                    COUNT(CASE WHEN file_path IS NOT NULL THEN 1 END) as successful_generations
                FROM videos 
                WHERE created_at >= ?
            """, (start_date,))
            
            video_stats = cursor.fetchone()
            
            # Upload stats by platform
            cursor.execute("""
                SELECT 
                    platform,
                    COUNT(*) as total_uploads,
                    COUNT(CASE WHEN platform_video_id IS NOT NULL THEN 1 END) as successful_uploads,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares
                FROM uploads u
                JOIN videos v ON u.video_id = v.id
                WHERE v.created_at >= ?
                GROUP BY platform
            """, (start_date,))
            
            platform_stats = {}
            for row in cursor.fetchall():
                platform_stats[row[0]] = {
                    "total_uploads": row[1],
                    "successful_uploads": row[2],
                    "success_rate": (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    "total_views": row[3] or 0,
                    "total_likes": row[4] or 0,
                    "total_comments": row[5] or 0,
                    "total_shares": row[6] or 0
                }
            
            # Niche performance
            cursor.execute("""
                SELECT 
                    niche,
                    COUNT(*) as video_count,
                    AVG(COALESCE(u.views, 0)) as avg_views,
                    AVG(COALESCE(u.likes, 0)) as avg_likes
                FROM videos v
                LEFT JOIN uploads u ON v.id = u.video_id
                WHERE v.created_at >= ?
                GROUP BY niche
                ORDER BY avg_views DESC
            """, (start_date,))
            
            niche_stats = {}
            for row in cursor.fetchall():
                niche_stats[row[0]] = {
                    "video_count": row[1],
                    "avg_views": row[2] or 0,
                    "avg_likes": row[3] or 0,
                    "engagement_rate": (row[3] / row[2] * 100) if row[2] > 0 else 0
                }
            
            # Daily analytics
            cursor.execute("""
                SELECT 
                    date,
                    videos_generated,
                    videos_uploaded,
                    total_views,
                    generation_time_avg
                FROM analytics
                WHERE date >= DATE(?)
                ORDER BY date DESC
            """, (start_date.date(),))
            
            daily_analytics = []
            for row in cursor.fetchall():
                daily_analytics.append({
                    "date": row[0],
                    "videos_generated": row[1] or 0,
                    "videos_uploaded": row[2] or 0,
                    "total_views": row[3] or 0,
                    "avg_generation_time": row[4] or 0
                })
            
            # Top performing videos
            cursor.execute("""
                SELECT 
                    v.title,
                    v.niche,
                    v.topic,
                    u.platform,
                    u.views,
                    u.likes,
                    u.comments,
                    u.platform_url,
                    v.created_at
                FROM videos v
                JOIN uploads u ON v.id = u.video_id
                WHERE v.created_at >= ? AND u.views > 0
                ORDER BY u.views DESC
                LIMIT 10
            """, (start_date,))
            
            top_videos = []
            for row in cursor.fetchall():
                top_videos.append({
                    "title": row[0],
                    "niche": row[1],
                    "topic": row[2],
                    "platform": row[3],
                    "views": row[4],
                    "likes": row[5],
                    "comments": row[6],
                    "url": row[7],
                    "created_at": row[8],
                    "engagement_rate": (row[5] / row[4] * 100) if row[4] > 0 else 0
                })
            
            conn.close()
            
            # Compile dashboard data
            dashboard = {
                "period": f"Last {days} days",
                "generated_at": datetime.now().isoformat(),
                "video_stats": {
                    "total_videos": video_stats[0] or 0,
                    "successful_generations": video_stats[2] or 0,
                    "success_rate": (video_stats[2] / video_stats[0] * 100) if video_stats[0] > 0 else 0,
                    "avg_file_size_mb": round(video_stats[1] or 0, 2)
                },
                "platform_stats": platform_stats,
                "niche_stats": niche_stats,
                "daily_analytics": daily_analytics,
                "top_videos": top_videos,
                "total_views": sum(stats.get("total_views", 0) for stats in platform_stats.values()),
                "total_likes": sum(stats.get("total_likes", 0) for stats in platform_stats.values()),
                "overall_engagement_rate": self._calculate_overall_engagement_rate(platform_stats)
            }
            
            # Cache the result
            self.analytics_cache[cache_key] = {
                "data": dashboard,
                "timestamp": time.time()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate performance dashboard: {e}")
            return {"error": str(e)}
    
    def get_niche_insights(self, niche: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed insights for a specific niche."""
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Niche-specific metrics
            cursor.execute("""
                SELECT 
                    v.topic,
                    COUNT(*) as video_count,
                    AVG(COALESCE(u.views, 0)) as avg_views,
                    AVG(COALESCE(u.likes, 0)) as avg_likes,
                    MAX(u.views) as max_views
                FROM videos v
                LEFT JOIN uploads u ON v.id = u.video_id
                WHERE v.niche = ? AND v.created_at >= ?
                GROUP BY v.topic
                ORDER BY avg_views DESC
                LIMIT 20
            """, (niche, start_date))
            
            topic_performance = []
            for row in cursor.fetchall():
                topic_performance.append({
                    "topic": row[0],
                    "video_count": row[1],
                    "avg_views": row[2] or 0,
                    "avg_likes": row[3] or 0,
                    "max_views": row[4] or 0,
                    "engagement_rate": (row[3] / row[2] * 100) if row[2] > 0 else 0
                })
            
            # Best performing times
            cursor.execute("""
                SELECT 
                    strftime('%H', v.created_at) as hour,
                    AVG(COALESCE(u.views, 0)) as avg_views
                FROM videos v
                LEFT JOIN uploads u ON v.id = u.video_id
                WHERE v.niche = ? AND v.created_at >= ?
                GROUP BY hour
                ORDER BY avg_views DESC
            """, (niche, start_date))
            
            best_hours = [{"hour": int(row[0]), "avg_views": row[1] or 0} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "niche": niche,
                "period": f"Last {days} days",
                "topic_performance": topic_performance,
                "best_posting_hours": best_hours,
                "total_topics": len(topic_performance),
                "avg_performance": {
                    "views": sum(t["avg_views"] for t in topic_performance) / len(topic_performance) if topic_performance else 0,
                    "engagement": sum(t["engagement_rate"] for t in topic_performance) / len(topic_performance) if topic_performance else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get niche insights for {niche}: {e}")
            return {"error": str(e)}
    
    def _generate_platform_url(self, platform: str, video_id: str) -> str:
        """Generate platform-specific URL."""
        url_templates = {
            "youtube": f"https://youtube.com/watch?v={video_id}",
            "facebook": f"https://facebook.com/watch/?v={video_id}",
            "instagram": f"https://instagram.com/reel/{video_id}",
            "tiktok": f"https://tiktok.com/@user/video/{video_id}"
        }
        return url_templates.get(platform, "")
    
    def _calculate_overall_engagement_rate(self, platform_stats: Dict) -> float:
        """Calculate overall engagement rate across platforms."""
        total_views = sum(stats.get("total_views", 0) for stats in platform_stats.values())
        total_engagement = sum(
            stats.get("total_likes", 0) + stats.get("total_comments", 0) + stats.get("total_shares", 0)
            for stats in platform_stats.values()
        )
        
        return (total_engagement / total_views * 100) if total_views > 0 else 0
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.analytics_cache:
            return False
        
        cache_age = time.time() - self.analytics_cache[cache_key]["timestamp"]
        return cache_age < self.cache_ttl
    
    def export_analytics(self, format: str = "json", days: int = 30) -> str:
        """Export analytics data in specified format."""
        
        dashboard = self.get_performance_dashboard(days)
        
        if format.lower() == "json":
            return json.dumps(dashboard, indent=2, default=str)
        elif format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            
            # Write daily analytics
            writer = csv.writer(output)
            writer.writerow(["Date", "Videos Generated", "Videos Uploaded", "Total Views", "Avg Generation Time"])
            
            for day in dashboard.get("daily_analytics", []):
                writer.writerow([
                    day["date"],
                    day["videos_generated"],
                    day["videos_uploaded"],
                    day["total_views"],
                    day["avg_generation_time"]
                ])
            
            return output.getvalue()
        else:
            return json.dumps(dashboard, indent=2, default=str)

# Global analytics tracker instance
analytics_tracker = AnalyticsTracker()