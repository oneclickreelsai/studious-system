"""
Unsplash API integration for downloading high-quality stock photos.
Free tier: 50 requests/hour
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv("config.env")

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
BASE_URL = "https://api.unsplash.com"


def search_unsplash_photos(query, per_page=10, orientation="portrait"):
    """
    Search for photos on Unsplash.
    
    Args:
        query: Search keyword
        per_page: Number of results (max 30)
        orientation: 'portrait', 'landscape', or 'squarish'
    
    Returns:
        List of photo data
    """
    url = f"{BASE_URL}/search/photos"
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"🔍 Found {data['total']} photos for '{query}'")
        
        photos = []
        for result in data.get("results", []):
            photo_info = {
                "id": result["id"],
                "description": result.get("description") or result.get("alt_description"),
                "url_regular": result["urls"]["regular"],
                "url_full": result["urls"]["full"],
                "url_raw": result["urls"]["raw"],
                "width": result["width"],
                "height": result["height"],
                "photographer": result["user"]["name"],
                "photographer_url": result["user"]["links"]["html"],
                "download_location": result["links"]["download_location"]
            }
            photos.append(photo_info)
        
        return photos
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Unsplash API error: {e}")
        return []


def download_unsplash_photo(photo_data, save_dir="assets/images"):
    """
    Download a photo from Unsplash.
    
    Args:
        photo_data: Photo info dict from search_unsplash_photos()
        save_dir: Directory to save photos
    
    Returns:
        Path to downloaded photo or None
    """
    os.makedirs(save_dir, exist_ok=True)
    
    photo_id = photo_data["id"]
    photo_url = photo_data["url_regular"]  # Good quality for videos
    filename = f"unsplash_{photo_id}.jpg"
    filepath = os.path.join(save_dir, filename)
    
    # Trigger download tracking (required by Unsplash API)
    trigger_download(photo_data["download_location"])
    
    try:
        print(f"Downloading Unsplash photo by {photo_data['photographer']}...")
        response = requests.get(photo_url, stream=True)
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[OK] Photo downloaded: {filepath}")
        return filepath
    
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        return None


def trigger_download(download_location):
    """
    Trigger download tracking (required by Unsplash API guidelines).
    """
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    try:
        requests.get(download_location, headers=headers)
    except:
        pass


def get_photo_for_keyword(keyword, save_dir="assets/images"):
    """
    Search and download the first matching photo.
    
    Args:
        keyword: Search term
        save_dir: Where to save the photo
    
    Returns:
        Path to downloaded photo or None
    """
    photos = search_unsplash_photos(keyword, per_page=5, orientation="portrait")
    
    if not photos:
        print(f"⚠️ No photos found for '{keyword}'")
        return None
    
    # Download first photo
    return download_unsplash_photo(photos[0], save_dir)


if __name__ == "__main__":
    # Test the API
    print("Testing Unsplash API...")
    print("=" * 50)
    
    # Test 1: Search
    print("\nTest 1: Searching for 'motivation'...")
    photos = search_unsplash_photos("motivation", per_page=3, orientation="portrait")
    
    if photos:
        print(f"\n[OK] Found {len(photos)} photos:")
        for i, photo in enumerate(photos, 1):
            print(f"\n{i}. {photo['description']}")
            print(f"   By: {photo['photographer']}")
            print(f"   Size: {photo['width']}x{photo['height']}")
    
    # Test 2: Download
    if photos:
        print("\nTest 2: Downloading first photo...")
        downloaded = download_unsplash_photo(photos[0])
        
        if downloaded:
            print(f"\n[OK] Success! Photo saved to: {downloaded}")
        else:
            print("\n[ERROR] Download failed")
    
    print("\n" + "=" * 50)
    print("Unsplash API test complete!")
