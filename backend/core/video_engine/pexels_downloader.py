
import os
import requests
import random

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def search_pexels_video(query, orientation="portrait", size="medium", min_duration=30):
    """
    Search Pexels for a video matching the query.
    Returns the URL of the best matching video file.
    Filters for videos at least min_duration seconds long.
    """
    if not PEXELS_API_KEY:
        print("[red]X PEXELS_API_KEY not found in config.env[/red]")
        return None

    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation={orientation}&size={size}&per_page=30"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            if not videos:
                return None
            
            # Filter videos by minimum duration (30+ seconds)
            long_videos = [v for v in videos if v.get("duration", 0) >= min_duration]
            
            # If no long videos found, try with shorter ones but prefer longer
            if not long_videos:
                # Sort by duration descending, pick longest available
                videos.sort(key=lambda x: x.get("duration", 0), reverse=True)
                video = videos[0]
                print(f"  [!] No {min_duration}s+ videos found, using {video.get('duration', 0)}s video")
            else:
                # Pick a random long video
                video = random.choice(long_videos)
                print(f"  [*] Found video: {video.get('duration', 0)}s")
            
            # Find the best video file (HD quality)
            video_files = video.get("video_files", [])
            
            best_file = None
            for vf in video_files:
                if vf["quality"] == "hd" and vf["width"] <= 1080:
                     best_file = vf
                     break
            
            if not best_file and video_files:
                best_file = video_files[0]
                
            return best_file["link"]
        else:
            print(f"[red]X Pexels API Error: {response.status_code}[/red]")
            return None
    except Exception as e:
        print(f"[red]X Pexels Connection Error: {e}[/red]")
        return None

def download_video(url, output_path):
    """Downloads video from URL to path"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True
    except Exception as e:
        print(f"Download failed: {e}")
    return False

def get_video_for_keyword(keyword):
    """High level function to get a video path for a keyword"""
    link = search_pexels_video(keyword)
    if link:
        # Create a filename
        safe_keyword = "".join(x for x in keyword if x.isalnum())
        output_path = f"assets/videos/pexels_{safe_keyword}_{random.randint(1000,9999)}.mp4"
        
        print(f"[cyan]Downloading background for '{keyword}'...[/cyan]")
        if download_video(link, output_path):
            print(f"  [OK] Saved: {output_path}")
            return output_path
    
    return None

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv("config.env")
    # PEXELS_API_KEY must be set in config.env for this to work
    if os.getenv("PEXELS_API_KEY"):
         get_video_for_keyword("money")
