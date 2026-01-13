"""
YouTube Video Downloader using yt-dlp (FREE, No API needed)
Downloads YouTube videos for analysis, backup, or research
"""
import os
import yt_dlp
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def download_youtube_video(video_url: str, output_dir: str = None):
    """
    Download a YouTube video using yt-dlp (completely free, no API key needed)
    
    Args:
        video_url: Full YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID or https://www.youtube.com/shorts/VIDEO_ID)
        output_dir: Directory to save downloaded videos (auto-generated with date/time if None)
    
    Returns:
        dict: Video info including file path, title, duration, views, etc.
    """
    # Create folder with date and time
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join("output", "downloads", timestamp)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Use single file format to avoid ffmpeg merging requirement
    ydl_opts = {
        'format': '18/22/best',  # 18=360p mp4, 22=720p mp4, best=fallback (no merge needed)
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
    }
    
    logger.info(f"Downloading: {video_url}")
    logger.info(f"Saving to: {output_dir}")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        
        result = {
            "title": info.get("title"),
            "video_url": video_url,
            "file_path": ydl.prepare_filename(info),
            "duration": info.get("duration"),
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "channel": info.get("channel"),
            "upload_date": info.get("upload_date"),
            "output_folder": output_dir,
        }
        
        logger.info(f"Downloaded: {result['title']}")
        
        return result


def get_video_info(video_url: str):
    """
    Get video metadata without downloading
    """
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        
        return {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "channel": info.get("channel"),
            "upload_date": info.get("upload_date"),
            "thumbnail": info.get("thumbnail"),
        }


if __name__ == "__main__":
    print("\nYouTube Video Downloader (yt-dlp)")
    print("-------------------------------------")
    
    # Check for arguments first, otherwise ask user
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    else:
        video_url = input("Enter YouTube Video URL: ").strip()
    
    if not video_url:
        print("[X] No URL provided. Exiting.")
        sys.exit(1)

    try:
        print("\n[*] Fetching video info...")
        info = get_video_info(video_url)
        print(f"Title: {info['title']}")
        print(f"Channel: {info['channel']}")
        print(f"Duration: {info['duration']}s")
        
        confirm = input("\nDownload this video? (y/n): ").lower().strip()
        if confirm == 'y':
            result = download_youtube_video(video_url)
            print(f"\n[OK] Done!")
            print(f"Folder: {result['output_folder']}")
            print(f"File: {os.path.abspath(result['file_path'])}")
        else:
            print("[X] Download cancelled.")
            
    except Exception as e:
        print(f"\n[X] Error: {e}")
