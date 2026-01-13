"""
Meta AI to YouTube Pipeline
Downloads Meta AI video and uploads to YouTube with AI-generated metadata.
"""
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def meta_ai_to_youtube(meta_url: str, custom_title: str = None, custom_desc: str = None, analyze_content: bool = True) -> Dict:
    """
    Download Meta AI video and upload to YouTube Shorts.
    
    Args:
        meta_url: Meta AI post URL
        custom_title: Optional custom title (overrides AI generation)
        custom_desc: Optional custom description
        analyze_content: If True, analyze actual video content for better metadata
    
    Returns:
        dict with youtube_url, video_id, metadata used
    """
    from backend.core.video_engine.meta_ai_downloader import download_meta_ai_content
    from backend.core.ai_engine.video_metadata import generate_video_metadata, format_youtube_description
    from backend.core.post_engine.youtube import upload_youtube_short
    
    # Step 1: Download from Meta AI
    logger.info(f"[1/4] Downloading from Meta AI...")
    result = download_meta_ai_content(meta_url)
    
    if not result.get("success"):
        raise ValueError(f"Download failed: {result.get('message')}")
    
    video_path = result.get("file_path")
    prompt = result.get("prompt", "AI Generated Video")
    
    if not video_path or not os.path.exists(video_path):
        raise ValueError("No video file downloaded")
    
    logger.info(f"[OK] Downloaded: {video_path}")
    logger.info(f"[OK] Original prompt: {prompt[:80]}...")
    
    # Step 2: Analyze actual video content
    video_analysis = None
    if analyze_content:
        logger.info(f"[2/4] Analyzing video content...")
        try:
            from backend.core.ai_engine.video_analyzer import generate_metadata_from_video
            metadata = generate_metadata_from_video(video_path, prompt)
            video_analysis = metadata.get("video_analysis", {})
            
            if video_analysis.get("description"):
                logger.info(f"[OK] Video shows: {video_analysis.get('description', '')[:80]}...")
                if video_analysis.get("visible_text"):
                    logger.info(f"[OK] Text in video: {video_analysis.get('visible_text', '')[:50]}...")
        except Exception as e:
            logger.warning(f"[!] Video analysis failed: {e}, using prompt-based metadata")
            metadata = None
    else:
        metadata = None
    
    # Step 3: Generate metadata
    logger.info(f"[3/4] Generating metadata...")
    
    if custom_title and custom_desc:
        metadata = {
            "title": custom_title,
            "description": custom_desc,
            "tags": ["shorts", "ai", "animation"]
        }
    elif not metadata or not metadata.get("title"):
        # Fallback to prompt-based metadata
        video_type = "ai_animation"
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["dance", "dancing", "choreography"]):
            video_type = "dance"
        elif any(w in prompt_lower for w in ["music", "song", "beats", "singer"]):
            video_type = "music"
        elif any(w in prompt_lower for w in ["nature", "animal", "wildlife"]):
            video_type = "nature"
        
        metadata = generate_video_metadata(prompt, video_type)
    
    # Override with custom values if provided
    if custom_title:
        metadata["title"] = custom_title
    if custom_desc:
        metadata["description"] = custom_desc
    
    title = metadata["title"][:100]
    description = format_youtube_description(metadata)
    
    logger.info(f"[OK] Title: {title}")
    logger.info(f"[OK] Tags: {metadata.get('tags', [])[:5]}")
    
    # Step 4: Upload to YouTube
    logger.info(f"[4/4] Uploading to YouTube...")
    
    video_id = upload_youtube_short(video_path, title, description)
    youtube_url = f"https://youtube.com/shorts/{video_id}"
    
    logger.info(f"[OK] YouTube: {youtube_url}")
    
    return {
        "success": True,
        "youtube_url": youtube_url,
        "youtube_id": video_id,
        "video_path": video_path,
        "prompt": prompt,
        "video_analysis": video_analysis,
        "metadata": metadata,
        "title": title,
        "description": description
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python meta_to_youtube.py <meta_ai_url> [custom_title]")
        sys.exit(1)
    
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = meta_ai_to_youtube(url, custom_title=title)
        print(f"\n[SUCCESS]")
        print(f"YouTube: {result['youtube_url']}")
        print(f"Title: {result['title']}")
    except Exception as e:
        print(f"[ERROR] {e}")
