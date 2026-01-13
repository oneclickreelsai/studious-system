"""
Pixabay Video Downloader
Free CC0 stock videos (No attribution required)
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv("config.env")

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
PIXABAY_VIDEO_API = "https://pixabay.com/api/videos/"

def search_pixabay_videos(keyword: str, per_page: int = 10, min_width: int = 720, min_height: int = 1280):
    """
    Search for videos on Pixabay
    
    Args:
        keyword: Search term
        per_page: Number of results (max 200)
        min_width: Minimum video width (720 for vertical)
        min_height: Minimum video height (1280 for vertical)
    
    Returns:
        list: Video results with download URLs
    """
    if not PIXABAY_API_KEY:
        raise ValueError("PIXABAY_API_KEY not found in config.env")
    
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "per_page": per_page,
        "video_type": "all",
        "min_width": min_width,
        "min_height": min_height
    }
    
    response = requests.get(PIXABAY_VIDEO_API, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    videos = []
    for hit in data.get("hits", []):
        # Get video files (medium quality preferred for Shorts/Reels)
        video_files = hit.get("videos", {})
        
        # Prioritize medium or small for vertical videos
        video_url = None
        video_width = 0
        video_height = 0
        
        if "medium" in video_files:
            video_url = video_files["medium"]["url"]
            video_width = video_files["medium"]["width"]
            video_height = video_files["medium"]["height"]
        elif "small" in video_files:
            video_url = video_files["small"]["url"]
            video_width = video_files["small"]["width"]
            video_height = video_files["small"]["height"]
        elif "large" in video_files and video_files["large"]["url"]:
            video_url = video_files["large"]["url"]
            video_width = video_files["large"]["width"]
            video_height = video_files["large"]["height"]
        
        if video_url:
            videos.append({
                "id": hit.get("id"),
                "url": video_url,
                "duration": hit.get("duration"),
                "width": video_files.get("medium", {}).get("width", 0),
                "height": video_files.get("medium", {}).get("height", 0),
                "tags": hit.get("tags"),
                "user": hit.get("user")
            })
    
    return videos


def get_video_for_keyword(keyword: str, output_dir: str = "assets/videos"):
    """
    Download a vertical video from Pixabay for a given keyword
    
    Args:
        keyword: Search term (e.g., "motivation", "success", "nature")
        output_dir: Directory to save video
    
    Returns:
        str: Path to downloaded video file, or None if failed
    """
    try:
        print(f"🔍 Searching Pixabay for: '{keyword}'")
        
        # Search for vertical videos (720x1280 minimum for Shorts/Reels)
        videos = search_pixabay_videos(keyword, per_page=5, min_width=720, min_height=1280)
        
        if not videos:
            print(f"⚠️ No vertical videos found for '{keyword}' on Pixabay")
            return None
        
        # Get first result
        video = videos[0]
        video_url = video["url"]
        
        print(f"📥 Downloading video from Pixabay (Duration: {video['duration']}s)")
        
        # Download video
        os.makedirs(output_dir, exist_ok=True)
        video_filename = f"pixabay_{keyword.replace(' ', '_')}_{video['id']}.mp4"
        video_path = os.path.join(output_dir, video_filename)
        
        # Check if already downloaded
        if os.path.exists(video_path):
            print(f"[OK] Using cached video: {video_path}")
            return video_path
        
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[OK] Pixabay video downloaded: {video_path}")
        return video_path
        
    except Exception as e:
        print(f"[ERROR] Pixabay download failed: {e}")
        return None


if __name__ == "__main__":
    # Test - search for vertical videos
    result = search_pixabay_videos("motivation", per_page=3, min_width=720, min_height=1280)
    
    if result:
        print(f"\n[OK] Found {len(result)} videos:")
        for i, video in enumerate(result, 1):
            print(f"{i}. Duration: {video['duration']}s, Size: {video['width']}x{video['height']}")
            print(f"   Tags: {video['tags']}")
            print(f"   URL: {video['url']}\n")
    else:
        print("[ERROR] No videos found or API key not configured")

