"""
Meta AI to YouTube Pipeline CLI
Downloads Meta AI video, analyzes content, generates metadata, and optionally uploads.
"""
import os
import sys
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv("config.env")

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_and_analyze(url: str, upload: bool = False):
    """Download Meta AI video, analyze, and optionally upload to YouTube."""
    from backend.core.video_engine.meta_ai_downloader import download_meta_ai_content
    from backend.core.ai_engine.video_analyzer import analyze_video_content, generate_metadata_from_video
    from backend.core.ai_engine.video_metadata import format_youtube_description
    
    print(f"\n{'='*60}")
    print(f"META AI TO YOUTUBE PIPELINE")
    print(f"{'='*60}")
    
    # Step 1: Download
    print(f"\n[1/4] Downloading from Meta AI...")
    print(f"      URL: {url}")
    
    result = download_meta_ai_content(url)
    
    if not result.get("success"):
        print(f"[X] Download failed: {result.get('message')}")
        return None
    
    video_path = result.get("file_path")
    prompt = result.get("prompt", "")
    
    print(f"[OK] Downloaded: {video_path}")
    print(f"[OK] Size: {result.get('file_size', 0) / 1024 / 1024:.2f} MB")
    if prompt:
        print(f"[OK] Prompt: {prompt[:80]}...")
    
    # Step 2: Analyze video content
    print(f"\n[2/4] Analyzing video content...")
    
    analysis = analyze_video_content(video_path)
    
    if analysis.get("visible_text"):
        print(f"[OK] Text in video: {analysis.get('visible_text')[:100]}")
    if analysis.get("description"):
        print(f"[OK] Description: {analysis.get('description')[:100]}")
    
    # Step 3: Generate metadata
    print(f"\n[3/4] Generating metadata...")
    
    metadata = generate_metadata_from_video(video_path, prompt)
    
    title = metadata.get("title", "AI Generated Video")[:100]
    description = format_youtube_description(metadata)
    tags = metadata.get("tags", [])
    
    print(f"[OK] Title: {title}")
    print(f"[OK] Tags: {', '.join(tags[:5])}")
    
    # Step 4: Upload (optional)
    if upload:
        print(f"\n[4/4] Uploading to YouTube...")
        try:
            from backend.core.post_engine.youtube import upload_youtube_short
            video_id = upload_youtube_short(video_path, title, description)
            youtube_url = f"https://youtube.com/shorts/{video_id}"
            print(f"[OK] YouTube: {youtube_url}")
        except Exception as e:
            print(f"[X] Upload failed: {e}")
            youtube_url = None
    else:
        print(f"\n[4/4] Skipping upload (use --upload to enable)")
        youtube_url = None
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Video: {video_path}")
    print(f"Title: {title}")
    print(f"Content: {analysis.get('visible_text') or analysis.get('description') or 'N/A'}")
    if youtube_url:
        print(f"YouTube: {youtube_url}")
    print(f"{'='*60}\n")
    
    return {
        "video_path": video_path,
        "title": title,
        "description": description,
        "tags": tags,
        "analysis": analysis,
        "youtube_url": youtube_url
    }


def test_video(video_path: str):
    """Test if video plays correctly."""
    import subprocess
    
    if not os.path.exists(video_path):
        print(f"[X] Video not found: {video_path}")
        return False
    
    # Get video info
    from backend.core.video_engine.meta_ai_downloader import get_video_info, is_valid_video, has_audio
    
    if not is_valid_video(video_path):
        print(f"[X] Invalid video file")
        return False
    
    info = get_video_info(video_path)
    audio = has_audio(video_path)
    
    print(f"\n[VIDEO INFO]")
    print(f"  Resolution: {info['width']}x{info['height']}")
    print(f"  Duration: {info['duration']:.1f}s")
    print(f"  Has Audio: {audio}")
    print(f"  File Size: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
    
    # Try to play with default player
    try:
        if sys.platform == 'win32':
            os.startfile(video_path)
            print(f"[OK] Opening video in default player...")
        else:
            subprocess.run(['xdg-open', video_path], check=True)
    except:
        print(f"[!] Could not auto-open video. Path: {video_path}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Meta AI to YouTube Pipeline")
    parser.add_argument("url", nargs="?", help="Meta AI post URL")
    parser.add_argument("--upload", "-u", action="store_true", help="Upload to YouTube")
    parser.add_argument("--test", "-t", help="Test video file playback")
    parser.add_argument("--analyze", "-a", help="Analyze video file")
    
    args = parser.parse_args()
    
    if args.test:
        test_video(args.test)
    elif args.analyze:
        from backend.core.ai_engine.video_analyzer import analyze_video_content
        print(f"\nAnalyzing: {args.analyze}")
        result = analyze_video_content(args.analyze)
        print(f"\nResult:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    elif args.url:
        download_and_analyze(args.url, upload=args.upload)
    else:
        # Interactive mode
        print("\nMeta AI to YouTube Pipeline")
        print("-" * 40)
        url = input("Enter Meta AI URL: ").strip()
        if url:
            upload = input("Upload to YouTube? (y/n): ").strip().lower() == 'y'
            download_and_analyze(url, upload=upload)
        else:
            print("No URL provided.")
