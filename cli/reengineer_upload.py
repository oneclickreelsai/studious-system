"""
Re-Engineer & Upload Pipeline
Downloads Meta AI video, analyzes content, generates AI metadata, uploads to YouTube/Facebook.

Usage:
    python cli/reengineer_upload.py <meta_ai_url> --youtube --facebook
    python cli/reengineer_upload.py <meta_ai_url> --youtube
    python cli/reengineer_upload.py <meta_ai_url> --facebook
    python cli/reengineer_upload.py <meta_ai_url> --no-upload
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv("config.env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def reengineer_and_upload(
    meta_url: str,
    upload_youtube: bool = True,
    upload_facebook: bool = False
) -> dict:
    """
    Full re-engineering pipeline:
    1. Download video from Meta AI URL
    2. Analyze video content (OCR, AI vision)
    3. Generate optimized metadata with AI
    4. Upload to YouTube and/or Facebook
    """
    from backend.core.video_engine.meta_ai_downloader import download_meta_ai_content
    from backend.core.ai_engine.video_analyzer import analyze_video_content, generate_metadata_from_video
    from backend.core.ai_engine.video_metadata import format_youtube_description
    
    print("\n" + "=" * 60)
    print("RE-ENGINEER & UPLOAD PIPELINE")
    print("=" * 60)
    
    result = {
        "success": False,
        "video_path": None,
        "title": None,
        "youtube_url": None,
        "facebook_url": None,
        "error": None
    }
    
    # Step 1: Download from Meta AI
    print(f"\n[1/5] Downloading from Meta AI...")
    print(f"      URL: {meta_url}")
    
    try:
        download_result = download_meta_ai_content(meta_url)
    except Exception as e:
        print(f"      [X] Download failed: {e}")
        result["error"] = str(e)
        return result
    
    if not download_result.get("success"):
        print(f"      [X] Download failed: {download_result.get('message')}")
        result["error"] = download_result.get("message")
        return result
    
    video_path = download_result.get("file_path")
    original_prompt = download_result.get("prompt", "")
    
    print(f"      [OK] Downloaded: {video_path}")
    print(f"      [OK] Size: {download_result.get('file_size', 0) / 1024 / 1024:.2f} MB")
    if original_prompt:
        print(f"      [OK] Original prompt: {original_prompt[:60]}...")
    
    result["video_path"] = video_path
    
    # Step 2: Analyze video content
    print(f"\n[2/5] Analyzing video content...")
    
    try:
        analysis = analyze_video_content(video_path)
        
        if analysis.get("visible_text"):
            print(f"      [OK] Text detected: {analysis.get('visible_text')[:60]}...")
        if analysis.get("description"):
            print(f"      [OK] Content: {analysis.get('description')[:60]}...")
        if not analysis.get("visible_text") and not analysis.get("description"):
            print(f"      [!] No text/content detected, using original prompt")
    except Exception as e:
        print(f"      [!] Analysis error: {e}")
        analysis = {}
    
    result["analysis"] = analysis
    
    # Step 3: Generate AI metadata
    print(f"\n[3/5] Generating AI metadata...")
    
    try:
        # Use video analysis if available, otherwise use original prompt
        content_for_metadata = (
            analysis.get("visible_text") or 
            analysis.get("description") or 
            original_prompt or 
            "AI Generated Video"
        )
        
        metadata = generate_metadata_from_video(video_path, content_for_metadata)
        
        title = metadata.get("title", "AI Video")[:100]
        description = format_youtube_description(metadata)
        tags = metadata.get("tags", [])
        
        print(f"      [OK] Title: {title}")
        print(f"      [OK] Tags: {', '.join(tags[:5])}")
        
    except Exception as e:
        print(f"      [!] Metadata generation error: {e}")
        # Fallback metadata
        title = original_prompt[:50] if original_prompt else "AI Generated Video"
        description = f"{original_prompt}\n\n#shorts #ai #viral"
        tags = ["shorts", "ai", "viral"]
    
    result["title"] = title
    result["description"] = description
    result["tags"] = tags
    
    # Step 4: Upload to YouTube
    if upload_youtube:
        print(f"\n[4/5] Uploading to YouTube...")
        try:
            from backend.core.post_engine.youtube import upload_youtube_short
            video_id = upload_youtube_short(video_path, title, description)
            youtube_url = f"https://youtube.com/shorts/{video_id}"
            result["youtube_url"] = youtube_url
            result["youtube_id"] = video_id
            print(f"      [OK] YouTube: {youtube_url}")
        except Exception as e:
            print(f"      [X] YouTube error: {e}")
            result["youtube_error"] = str(e)
    else:
        print(f"\n[4/5] Skipping YouTube upload")
    
    # Step 5: Upload to Facebook
    if upload_facebook:
        print(f"\n[5/5] Uploading to Facebook...")
        try:
            from backend.core.post_engine.facebook import upload_facebook_reel
            fb_caption = f"{title}\n\n{description}"
            fb_id = upload_facebook_reel(video_path, fb_caption)
            facebook_url = f"https://facebook.com/reel/{fb_id}"
            result["facebook_url"] = facebook_url
            result["facebook_id"] = fb_id
            print(f"      [OK] Facebook: {facebook_url}")
        except Exception as e:
            print(f"      [X] Facebook error: {e}")
            result["facebook_error"] = str(e)
    else:
        print(f"\n[5/5] Skipping Facebook upload")
    
    result["success"] = True
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Video: {video_path}")
    print(f"Title: {title}")
    if result.get("youtube_url"):
        print(f"YouTube: {result['youtube_url']}")
    if result.get("facebook_url"):
        print(f"Facebook: {result['facebook_url']}")
    if not result.get("youtube_url") and not result.get("facebook_url"):
        print("No uploads performed")
    print("=" * 60 + "\n")
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-Engineer & Upload Meta AI Video")
    parser.add_argument("url", help="Meta AI post URL")
    parser.add_argument("--youtube", "-yt", action="store_true", help="Upload to YouTube")
    parser.add_argument("--facebook", "-fb", action="store_true", help="Upload to Facebook")
    parser.add_argument("--no-upload", action="store_true", help="Skip all uploads")
    
    args = parser.parse_args()
    
    # Default to YouTube if no option specified
    upload_yt = args.youtube or (not args.facebook and not args.no_upload)
    upload_fb = args.facebook
    
    if args.no_upload:
        upload_yt = False
        upload_fb = False
    
    reengineer_and_upload(
        args.url,
        upload_youtube=upload_yt,
        upload_facebook=upload_fb
    )
