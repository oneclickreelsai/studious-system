"""
Smart Video Upload Pipeline
Downloads, analyzes, and uploads with proper metadata.
"""
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def download_and_preview(meta_url: str) -> Dict:
    """
    Download Meta AI video and return preview info (without uploading).
    """
    from backend.core.video_engine.meta_ai_downloader import download_meta_ai_content
    
    logger.info(f"[*] Downloading from: {meta_url}")
    result = download_meta_ai_content(meta_url)
    
    if not result.get("success"):
        raise ValueError(f"Download failed: {result.get('message')}")
    
    video_path = result.get("file_path")
    prompt = result.get("prompt", "")
    
    # Get video info
    from backend.core.video_engine.meta_ai_downloader import get_video_info
    info = get_video_info(video_path)
    
    return {
        "video_path": video_path,
        "prompt": prompt,
        "duration": info.get("duration", 0),
        "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
        "has_audio": info.get("has_audio", False),
        "file_size_mb": os.path.getsize(video_path) / 1024 / 1024,
        "output_folder": result.get("output_folder")
    }

def upload_with_custom_metadata(video_path: str, title: str, description: str, tags: list = None) -> Dict:
    """
    Upload video to YouTube with custom metadata.
    """
    from backend.core.post_engine.youtube import upload_youtube_short
    
    if tags:
        hashtags = " ".join([f"#{t}" for t in tags[:5]])
        full_desc = f"{description}\n\n{hashtags}"
    else:
        full_desc = description
    
    logger.info(f"[*] Uploading: {title}")
    video_id = upload_youtube_short(video_path, title[:100], full_desc)
    
    return {
        "success": True,
        "youtube_url": f"https://youtube.com/shorts/{video_id}",
        "youtube_id": video_id,
        "title": title,
        "description": full_desc
    }

def quick_upload(meta_url: str, title: str = None, niche: str = "entertainment") -> Dict:
    """
    Quick download and upload with AI-generated or custom metadata.
    """
    from backend.core.video_engine.meta_ai_downloader import download_meta_ai_content
    from backend.core.ai_engine.video_metadata import generate_video_metadata, format_youtube_description
    from backend.core.post_engine.youtube import upload_youtube_short
    
    # Download
    logger.info(f"[1/3] Downloading...")
    result = download_meta_ai_content(meta_url)
    
    if not result.get("success"):
        raise ValueError(f"Download failed")
    
    video_path = result["file_path"]
    prompt = result.get("prompt", "AI Generated Video")
    
    # Generate metadata
    logger.info(f"[2/3] Generating metadata...")
    if title:
        metadata = {
            "title": title,
            "description": f"AI Generated Content\n\n{prompt[:200]}",
            "tags": ["shorts", "ai", "viral", niche]
        }
    else:
        metadata = generate_video_metadata(prompt, niche)
    
    final_title = metadata["title"][:100]
    final_desc = format_youtube_description(metadata)
    
    # Upload
    logger.info(f"[3/3] Uploading: {final_title}")
    video_id = upload_youtube_short(video_path, final_title, final_desc)
    
    return {
        "success": True,
        "youtube_url": f"https://youtube.com/shorts/{video_id}",
        "title": final_title,
        "tags": metadata.get("tags", [])
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smart_upload.py <meta_url> [custom_title]")
        sys.exit(1)
    
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = quick_upload(url, title)
    print(f"\nYouTube: {result['youtube_url']}")
    print(f"Title: {result['title']}")
