import os
import logging
from typing import List, Dict, Optional
from yt_dlp import YoutubeDL
from pathlib import Path

logger = logging.getLogger(__name__)

class MusicFinder:
    """
    Music Finder engine using yt-dlp to search and download music.
    Based on the robust configuration from MusicAPI.
    """
    def __init__(self):
        self.output_dir = Path("assets/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration from MusicAPI's YTDLP.py
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.4664.110 Safari/537.36'
        }
        
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'retries': 10,
            'fragment_retries': 10,
            'socket_timeout': 30,
            'extract_flat': True, # Fast search without downloading info
        }

    def search_music(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for music videos on YouTube.
        """
        logger.info(f"Searching music for: {query}")
        results = []
        
        try:
            # Add "audio" to query to bias towards music
            search_query = f"ytsearch{limit}:{query} audio"
            
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            results.append({
                                'id': entry.get('id'),
                                'title': entry.get('title'),
                                'uploader': entry.get('uploader'),
                                'duration': entry.get('duration'),
                                'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg",
                                'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                            })
                            
            return results
        except Exception as e:
            logger.error(f"Music search failed: {e}")
            return []

    def download_music(self, video_id: str) -> Optional[Dict]:
        """
        Download audio for a specific video ID.
        """
        logger.info(f"Downloading music: {video_id}")
        
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            output_template = str(self.output_dir / "%(id)s.%(ext)s")
            
            download_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': True,
                # Retain retries from MusicAPI
                'retries': float('inf'), 
                'fragment_retries': float('inf'),
                'socket_timeout': 30
            }
            
            with YoutubeDL(download_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # FFmpeg converter changes extension
                final_path = str(Path(filename).with_suffix('.mp3'))
                
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'path': f"/assets/audio/{info.get('id')}.mp3",
                    'full_path': final_path,
                    'duration': info.get('duration')
                }
                
        except Exception as e:
            logger.error(f"Music download failed: {e}")
            return None

# Singleton instance
music_finder = MusicFinder()
