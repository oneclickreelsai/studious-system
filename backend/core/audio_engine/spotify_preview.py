"""
Spotify 30-Second Preview Downloader
Downloads the hook/catchy part of songs using Spotify's preview URLs.
These 30-second clips are curated to be the most engaging part of the song.
"""

import os
import requests
import base64
import logging
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

logger = logging.getLogger(__name__)

# Spotify API credentials (Client Credentials Flow - no user login needed)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

_access_token = None
_token_expires = 0


def get_spotify_token() -> Optional[str]:
    """Get Spotify access token using Client Credentials flow."""
    global _access_token, _token_expires
    
    import time
    if _access_token and time.time() < _token_expires:
        return _access_token
    
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        logger.warning("Spotify credentials not configured")
        return None
    
    try:
        # Base64 encode credentials
        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            _access_token = data["access_token"]
            _token_expires = time.time() + data.get("expires_in", 3600) - 60
            logger.info("Spotify token obtained")
            return _access_token
        else:
            logger.error(f"Spotify auth failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Spotify auth error: {e}")
        return None


def search_track(query: str) -> Optional[Dict]:
    """
    Search for a track on Spotify.
    Returns track info including preview_url (30-sec hook clip).
    """
    token = get_spotify_token()
    if not token:
        return None
    
    try:
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "q": query,
                "type": "track",
                "limit": 1,
                "market": "US"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tracks = data.get("tracks", {}).get("items", [])
            
            if tracks:
                track = tracks[0]
                return {
                    "name": track.get("name"),
                    "artist": ", ".join(a["name"] for a in track.get("artists", [])),
                    "album": track.get("album", {}).get("name"),
                    "preview_url": track.get("preview_url"),  # 30-sec MP3!
                    "spotify_url": track.get("external_urls", {}).get("spotify"),
                    "duration_ms": track.get("duration_ms"),
                    "id": track.get("id")
                }
        
        logger.warning(f"Spotify search failed: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Spotify search error: {e}")
        return None


def download_preview(preview_url: str, output_path: str) -> Optional[str]:
    """Download the 30-second preview MP3."""
    if not preview_url:
        return None
    
    try:
        response = requests.get(preview_url, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Preview downloaded: {output_path} ({len(response.content) / 1024:.1f} KB)")
            return output_path
        else:
            logger.error(f"Preview download failed: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Preview download error: {e}")
        return None


def get_song_hook(song_query: str, output_dir: str) -> Optional[Dict]:
    """
    Get the hook/catchy part of a song using Spotify's 30-sec preview.
    
    Args:
        song_query: Song name and artist (e.g., "iSpy KYLE Lil Yachty")
        output_dir: Directory to save the preview
    
    Returns:
        Dict with path, track info, or None if failed
    """
    # Search for the track
    track = search_track(song_query)
    
    if not track:
        logger.warning(f"Track not found: {song_query}")
        return None
    
    preview_url = track.get("preview_url")
    if not preview_url:
        logger.warning(f"No preview available for: {track.get('name')} by {track.get('artist')}")
        return None
    
    # Download preview
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "spotify_preview.mp3")
    
    if download_preview(preview_url, output_path):
        return {
            "path": output_path,
            "track_name": track.get("name"),
            "artist": track.get("artist"),
            "duration": 30,  # Spotify previews are always ~30 seconds
            "source": "spotify_preview"
        }
    
    return None


# Test function
if __name__ == "__main__":
    import sys
    
    if not SPOTIFY_CLIENT_ID:
        print("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in config.env")
        print("\nTo get credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create an app (free)")
        print("3. Copy Client ID and Client Secret")
        sys.exit(1)
    
    query = sys.argv[1] if len(sys.argv) > 1 else "iSpy KYLE Lil Yachty"
    print(f"Searching: {query}")
    
    result = get_song_hook(query, "output/test_spotify")
    if result:
        print(f"Downloaded: {result['path']}")
        print(f"Track: {result['track_name']} by {result['artist']}")
    else:
        print("Failed to get preview")
