"""
Intelligent content scheduling and automation
"""
import os
import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from backend.database.db_manager import DatabaseManager
from backend.core.ai_engine.trend_analyzer import trend_analyzer
from backend.core.ai_engine.content_optimizer import content_optimizer
from backend.utils.analytics_tracker import analytics_tracker
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class ScheduleStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledContent:
    id: int
    niche: str
    topic: str
    scheduled_time: datetime
    platforms: List[str]
    status: ScheduleStatus
    priority: int = 5  # 1-10, higher is more important
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    completed_at: datetime = None
    error_message: str = None

class SmartScheduler:
    """Intelligent content scheduler with trend-based optimization."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scheduled_content = []
        self.is_running = False
        self.check_interval = 60  # Check every minute
        
        # Platform-specific optimal posting times (24-hour format)
        self.optimal_times = {
            "youtube": {
                "weekdays": [7, 12, 18, 20],  # 7am, 12pm, 6pm, 8pm
                "weekends": [9, 14, 19, 21]   # 9am, 2pm, 7pm, 9pm
            },
            "instagram": {
                "weekdays": [6, 11, 13, 17, 19],
                "weekends": [10, 13, 16, 20]
            },
            "tiktok": {
                "weekdays": [6, 9, 12, 19, 21],
                "weekends": [9, 12, 15, 18, 20]
            },
            "facebook": {
                "weekdays": [9, 13, 15, 18],
                "weekends": [12, 15, 18, 20]
            }
        }
    
    def schedule_content_batch(
        self,
        niche: str,
        count: int = 7,
        days_ahead: int = 7,
        platforms: List[str] = ["youtube", "instagram"]
    ) -> List[ScheduledContent]:
        """Schedule a batch of content based on trends and optimal timing."""
        
        try:
            # Get trending topics and content opportunities
            opportunities = trend_analyzer.find_content_opportunities(niche, days_ahead)
            
            if not opportunities:
                logger.warning(f"No content opportunities found for {niche}")
                return []
            
            scheduled_items = []
            
            # Sort opportunities by score and schedule top ones
            opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
            
            for i, opportunity in enumerate(opportunities[:count]):
                # Calculate optimal posting time
                optimal_time = self._calculate_optimal_posting_time(
                    platforms, 
                    days_ahead=i + 1  # Spread content over multiple days
                )
                
                # Create scheduled content item
                scheduled_item = ScheduledContent(
                    id=int(time.time() * 1000) + i,  # Unique ID
                    niche=niche,
                    topic=opportunity["topic"],
                    scheduled_time=optimal_time,
                    platforms=platforms,
                    status=ScheduleStatus.PENDING,
                    priority=min(10, int(opportunity["opportunity_score"] / 10)),
                    created_at=datetime.now()
                )
                
                scheduled_items.append(scheduled_item)
                self.scheduled_content.append(scheduled_item)
                
                # Store in database
                self._save_scheduled_content(scheduled_item, opportunity)
            
            logger.info(f"Scheduled {len(scheduled_items)} content items for {niche}")
            return scheduled_items
            
        except Exception as e:
            logger.error(f"Failed to schedule content batch: {e}")
            return []
    
    def _calculate_optimal_posting_time(
        self, 
        platforms: List[str], 
        days_ahead: int = 1
    ) -> datetime:
        """Calculate optimal posting time based on platform analytics."""
        
        target_date = datetime.now() + timedelta(days=days_ahead)
        is_weekend = target_date.weekday() >= 5
        
        # Get optimal hours for each platform
        platform_hours = []
        for platform in platforms:
            if platform in self.optimal_times:
                time_key = "weekends" if is_weekend else "weekdays"
                platform_hours.extend(self.optimal_times[platform][time_key])
        
        if not platform_hours:
            # Default to general optimal times
            platform_hours = [9, 12, 18, 20]
        
        # Find most common optimal hour
        hour_counts = {}
        for hour in platform_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        optimal_hour = max(hour_counts.keys(), key=lambda x: hour_counts[x])
        
        # Set the optimal posting time
        optimal_time = target_date.replace(
            hour=optimal_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        return optimal_time
    
    def _save_scheduled_content(self, item: ScheduledContent, opportunity: Dict):
        """Save scheduled content to database."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Create scheduled_content table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_content (
                    id INTEGER PRIMARY KEY,
                    niche TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    platforms TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    opportunity_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO scheduled_content (
                    id, niche, topic, scheduled_time, platforms, status, priority,
                    retry_count, max_retries, opportunity_data, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.niche,
                item.topic,
                item.scheduled_time,
                json.dumps(item.platforms),
                item.status.value,
                item.priority,
                item.retry_count,
                item.max_retries,
                json.dumps(opportunity),
                item.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save scheduled content: {e}")
    
    def get_scheduled_content(
        self, 
        status: Optional[ScheduleStatus] = None,
        days_ahead: int = 7
    ) -> List[ScheduledContent]:
        """Get scheduled content items."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, niche, topic, scheduled_time, platforms, status, priority,
                       retry_count, max_retries, created_at, completed_at, error_message
                FROM scheduled_content
                WHERE scheduled_time <= ?
            """
            params = [datetime.now() + timedelta(days=days_ahead)]
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY scheduled_time ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            scheduled_items = []
            for row in rows:
                item = ScheduledContent(
                    id=row[0],
                    niche=row[1],
                    topic=row[2],
                    scheduled_time=datetime.fromisoformat(row[3]),
                    platforms=json.loads(row[4]),
                    status=ScheduleStatus(row[5]),
                    priority=row[6],
                    retry_count=row[7],
                    max_retries=row[8],
                    created_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    completed_at=datetime.fromisoformat(row[10]) if row[10] else None,
                    error_message=row[11]
                )
                scheduled_items.append(item)
            
            conn.close()
            return scheduled_items
            
        except Exception as e:
            logger.error(f"Failed to get scheduled content: {e}")
            return []
    
    def update_content_status(
        self, 
        content_id: int, 
        status: ScheduleStatus, 
        error_message: str = None
    ):
        """Update the status of scheduled content."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            update_fields = ["status = ?"]
            params = [status.value]
            
            if status == ScheduleStatus.COMPLETED:
                update_fields.append("completed_at = ?")
                params.append(datetime.now())
            
            if error_message:
                update_fields.append("error_message = ?")
                params.append(error_message)
            
            if status == ScheduleStatus.FAILED:
                update_fields.append("retry_count = retry_count + 1")
            
            params.append(content_id)
            
            cursor.execute(f"""
                UPDATE scheduled_content 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            conn.close()
            
            # Update in-memory list
            for item in self.scheduled_content:
                if item.id == content_id:
                    item.status = status
                    if error_message:
                        item.error_message = error_message
                    if status == ScheduleStatus.COMPLETED:
                        item.completed_at = datetime.now()
                    break
            
        except Exception as e:
            logger.error(f"Failed to update content status: {e}")
    
    async def process_scheduled_content(self):
        """Process scheduled content that's ready to be created."""
        
        # Get pending content that's ready to process
        ready_content = []
        current_time = datetime.now()
        
        for item in self.scheduled_content:
            if (item.status == ScheduleStatus.PENDING and 
                item.scheduled_time <= current_time):
                ready_content.append(item)
        
        if not ready_content:
            return
        
        logger.info(f"Processing {len(ready_content)} scheduled content items")
        
        for item in ready_content:
            try:
                # Update status to processing
                self.update_content_status(item.id, ScheduleStatus.PROCESSING)
                
                # Generate content
                success = await self._generate_and_upload_content(item)
                
                if success:
                    self.update_content_status(item.id, ScheduleStatus.COMPLETED)
                    logger.info(f"Successfully processed scheduled content: {item.topic}")
                else:
                    if item.retry_count < item.max_retries:
                        # Reschedule for retry
                        item.scheduled_time = datetime.now() + timedelta(hours=1)
                        self.update_content_status(item.id, ScheduleStatus.PENDING)
                        logger.warning(f"Retrying scheduled content: {item.topic}")
                    else:
                        self.update_content_status(
                            item.id, 
                            ScheduleStatus.FAILED, 
                            "Max retries exceeded"
                        )
                        logger.error(f"Failed to process scheduled content: {item.topic}")
                
            except Exception as e:
                error_msg = str(e)
                self.update_content_status(item.id, ScheduleStatus.FAILED, error_msg)
                logger.error(f"Error processing scheduled content {item.topic}: {e}")
    
    async def _generate_and_upload_content(self, item: ScheduledContent) -> bool:
        """Generate and upload content for a scheduled item."""
        try:
            from backend.core.ai_engine.script_generator import generate_script
            from backend.core.ai_engine.caption_hashtags import generate_caption
            from backend.core.video_engine.voiceover import generate_voiceover
            from backend.core.video_engine.advanced_video_builder import advanced_video_builder
            from backend.core.video_engine.pexels_downloader import get_video_for_keyword
            from backend.core.post_engine.youtube import upload_youtube_short
            from backend.core.post_engine.facebook import upload_facebook_reel
            
            # Generate script
            script = generate_script(item.niche, item.topic)
            
            # Optimize script if enabled
            if settings.enable_caching:  # Use as optimization flag
                optimization_result = content_optimizer.optimize_script(script, item.niche)
                if optimization_result.get("improved", False):
                    script = optimization_result["optimized_script"]
            
            # Generate voiceover
            voiceover_path = generate_voiceover(script, niche=item.niche)
            if not voiceover_path:
                raise Exception("Voiceover generation failed")
            
            # Get background video
            video_path = get_video_for_keyword(item.topic)
            if not video_path:
                raise Exception("Background video sourcing failed")
            
            # Build video
            output_path = f"output/scheduled_{item.id}_{int(time.time())}.mp4"
            final_video_path = advanced_video_builder.build_video_gpu_accelerated(
                background_video=video_path,
                voiceover_audio=voiceover_path,
                script=script,
                niche=item.niche,
                output_path=output_path,
                quality="high"
            )
            
            # Generate metadata
            meta = generate_caption(item.niche, item.topic)
            
            # Track video generation
            file_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
            video_id = analytics_tracker.track_video_generation(
                niche=item.niche,
                topic=item.topic,
                script=script,
                generation_time=0,  # Would need to track this
                success=True,
                file_size_mb=file_size_mb
            )
            
            # Upload to platforms
            upload_success = True
            for platform in item.platforms:
                try:
                    if platform == "youtube":
                        platform_video_id = upload_youtube_short(
                            final_video_path, 
                            meta["title"], 
                            meta["description"]
                        )
                    elif platform == "facebook":
                        platform_video_id = upload_facebook_reel(
                            final_video_path, 
                            meta["caption"]
                        )
                    else:
                        logger.warning(f"Unsupported platform: {platform}")
                        continue
                    
                    # Track upload
                    analytics_tracker.track_upload(
                        video_id=video_id,
                        platform=platform,
                        platform_video_id=platform_video_id,
                        success=True
                    )
                    
                except Exception as e:
                    logger.error(f"Upload failed for {platform}: {e}")
                    analytics_tracker.track_upload(
                        video_id=video_id,
                        platform=platform,
                        platform_video_id="",
                        success=False,
                        error_message=str(e)
                    )
                    upload_success = False
            
            return upload_success
            
        except Exception as e:
            logger.error(f"Content generation failed for scheduled item {item.id}: {e}")
            return False
    
    async def start_scheduler(self):
        """Start the content scheduler loop."""
        self.is_running = True
        logger.info("Smart scheduler started")
        
        while self.is_running:
            try:
                await self.process_scheduled_content()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_scheduler(self):
        """Stop the content scheduler."""
        self.is_running = False
        logger.info("Smart scheduler stopped")
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get status counts
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM scheduled_content 
                GROUP BY status
            """)
            
            status_counts = {}
            for row in cursor.fetchall():
                status_counts[row[0]] = row[1]
            
            # Get upcoming content
            cursor.execute("""
                SELECT COUNT(*) 
                FROM scheduled_content 
                WHERE status = 'pending' AND scheduled_time > datetime('now')
            """)
            
            upcoming_count = cursor.fetchone()[0]
            
            # Get success rate
            total_processed = status_counts.get('completed', 0) + status_counts.get('failed', 0)
            success_rate = (status_counts.get('completed', 0) / total_processed * 100) if total_processed > 0 else 0
            
            conn.close()
            
            return {
                "is_running": self.is_running,
                "status_counts": status_counts,
                "upcoming_content": upcoming_count,
                "success_rate": round(success_rate, 2),
                "check_interval": self.check_interval,
                "total_scheduled": len(self.scheduled_content)
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler stats: {e}")
            return {"error": str(e)}

# Global scheduler instance
smart_scheduler = SmartScheduler()