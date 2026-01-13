"""
YouTube Video Downloader using yt-dlp (FREE, No API needed)
Download YouTube videos for analysis, backup, or research
"""
import os
import yt_dlp

def download_youtube_video(video_url: str, output_dir: str = "output/downloads", format: str = "best"):
    """
    Download a YouTube video using yt-dlp (completely free, no API key needed)
    
    Args:
        video_url: Full YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
        output_dir: Directory to save downloaded videos
        format: Video format/quality ('best', 'worst', '720p', etc.)
    
    Returns:
        dict: Video info including file path, title, duration, views, etc.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    print(f"🎬 Downloading: {video_url}")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video info
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
            "description": info.get("description"),
            "thumbnail": info.get("thumbnail"),
        }
        
        print(f"[OK] Downloaded: {result['title']}")
        print(f"   Saved to: {result['file_path']}")
        
        return result


def download_multiple_videos(video_urls: list, output_dir: str = "output/downloads"):
    """
    Download multiple YouTube videos
    
    Args:
        video_urls: List of YouTube URLs
        output_dir: Directory to save videos
    
    Returns:
        list: List of video info dicts
    """
    results = []
    
    print(f"Starting batch download for {len(video_urls)} videos")
    
    for url in video_urls:
        try:
            result = download_youtube_video(url, output_dir)
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Error downloading {url}: {e}")
            results.append({"video_url": url, "error": str(e)})
    
    return results


def get_video_info(video_url: str):
    """
    Get video metadata without downloading
    
    Args:
        video_url: YouTube URL
    
    Returns:
        dict: Video information
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
            "description": info.get("description", "")[:200],  # First 200 chars
        }


def download_shorts_format(video_url: str, output_dir: str = "output/downloads"):
    """
    Download YouTube video optimized for Shorts (9:16, max 60s)
    
    Args:
        video_url: YouTube URL
        output_dir: Output directory
    
    Returns:
        dict: Video info with file path
    """
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'best[height<=1920][ext=mp4]',
        'outtmpl': os.path.join(output_dir, '%(title)s_SHORT.%(ext)s'),
        'postprocessor_args': [
            '-t', '60',  # Max 60 seconds
        ],
        'quiet': False,
    }
    
    print(f"Downloading Shorts format: {video_url}")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        
        result = {
            "title": info.get("title"),
            "file_path": ydl.prepare_filename(info),
            "duration": info.get("duration"),
        }
        
        print(f"[OK] Downloaded Shorts: {result['title']}")
        
        return result


if __name__ == "__main__":
    # Test example
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        # Get info only (no download)
        print("\nGetting video info...")
        info = get_video_info(test_url)
        print(f"Title: {info['title']}")
        print(f"Views: {info['views']:,}")
        print(f"Duration: {info['duration']}s")
        print(f"Channel: {info['channel']}")
        
        # Uncomment to actually download:
        # result = download_youtube_video(test_url)
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
