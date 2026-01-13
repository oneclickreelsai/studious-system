"""
Fully Automated Meta AI to YouTube Pipeline

This script:
1. Gets trending prompt from AI
2. Generates video on Meta AI (browser automation)
3. Downloads the video
4. Analyzes content
5. Generates metadata
6. Uploads to YouTube/Facebook

Usage:
    python cli/auto_pipeline.py                    # Full auto with random prompt
    python cli/auto_pipeline.py --prompt "..."     # Use custom prompt
    python cli/auto_pipeline.py --category funny   # Use specific category
    python cli/auto_pipeline.py --headless         # Run browser in background
    python cli/auto_pipeline.py --no-upload        # Skip upload step
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Setup path
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv("config.env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def run_full_pipeline(
    prompt: str = None,
    category: str = None,
    headless: bool = False,
    upload_youtube: bool = True,
    upload_facebook: bool = False
) -> dict:
    """
    Run the full automated pipeline.
    
    Args:
        prompt: Custom prompt (if None, generates trending prompt)
        category: Content category (funny, music, artistic, nature)
        headless: Run browser in headless mode
        upload_youtube: Upload to YouTube
        upload_facebook: Upload to Facebook
    
    Returns:
        Result dict with all info
    """
    from backend.core.ai_engine.content_curator import get_trending_prompt, mark_as_uploaded
    from backend.core.video_engine.meta_ai_generator import run_generate_and_download
    from backend.core.ai_engine.video_analyzer import generate_metadata_from_video
    from backend.core.ai_engine.video_metadata import format_youtube_description
    
    print("\n" + "=" * 60)
    print("FULLY AUTOMATED META AI TO YOUTUBE PIPELINE")
    print("=" * 60)
    
    result = {
        "success": False,
        "prompt": None,
        "video_path": None,
        "youtube_url": None,
        "facebook_url": None,
        "error": None
    }
    
    # Step 1: Get prompt
    print("\n[1/6] Getting viral prompt...")
    if prompt:
        idea = {"prompt": prompt, "category": category or "custom", "hashtags": []}
        print(f"      Using custom prompt")
    else:
        idea = get_trending_prompt(category)
        print(f"      Category: {idea.get('category', 'viral')}")
    
    prompt = idea["prompt"]
    result["prompt"] = prompt
    print(f"      Prompt: {prompt[:70]}...")
    
    # Step 2: Generate on Meta AI (5s only - we'll extend with FFmpeg)
    print("\n[2/6] Generating video on Meta AI...")
    print("      (This may take 1-2 minutes)")
    
    download_result = run_generate_and_download(prompt, headless=headless, 
                                                 target_duration=0, add_music=False)
    
    if not download_result or not download_result.get("success"):
        error = "Failed to generate/download video from Meta AI"
        print(f"      [X] {error}")
        result["error"] = error
        return result
    
    video_path = download_result.get("file_path")
    result["video_path"] = video_path
    print(f"      [OK] Video: {video_path}")
    print(f"      [OK] Size: {download_result.get('file_size', 0) / 1024 / 1024:.2f} MB")
    
    # Check if Meta AI extended and added music
    meta_extended = download_result.get("extended", False)
    meta_music = download_result.get("music_added", False)
    meta_duration = download_result.get("duration", 5)
    
    if meta_extended:
        print(f"      [OK] Meta AI extended to {meta_duration}s")
    if meta_music:
        print("      [OK] Meta AI added music")
    
    # Step 2.5: Extend video if Meta AI didn't extend it
    if not meta_extended or meta_duration < 10:
        print("\n[2.5/6] Extending video (FFmpeg fallback)...")
        try:
            from backend.core.video_engine.video_extender import extend_video, get_video_duration, convert_to_vertical
            
            duration = get_video_duration(video_path)
            print(f"      Current: {duration:.1f}s")
            
            if duration < 15:
                extend_result = extend_video(video_path, target_duration=15, method="auto")
                if extend_result.get("success") and extend_result.get("output"):
                    video_path = extend_result["output"]
                    result["video_path"] = video_path
                    print(f"      [OK] Extended to {extend_result['final_duration']:.1f}s ({extend_result['method']})")
                else:
                    print(f"      [!] Extension failed, using original")
            else:
                print(f"      [OK] Already {duration:.1f}s, no extension needed")
            
            # Convert to 9:16 vertical for Shorts/Reels
            print("      Converting to 9:16 vertical...")
            vertical_result = convert_to_vertical(video_path)
            if vertical_result.get("success") and vertical_result.get("output"):
                video_path = vertical_result["output"]
                result["video_path"] = video_path
                print(f"      [OK] Converted to vertical (1080x1920)")
            else:
                print(f"      [!] Vertical conversion skipped")
                
        except Exception as e:
            print(f"      [!] Extension error: {e}")
    else:
        # Still convert to vertical even if Meta AI extended
        print("\n[2.5/6] Converting to 9:16 vertical...")
        try:
            from backend.core.video_engine.video_extender import convert_to_vertical
            vertical_result = convert_to_vertical(video_path)
            if vertical_result.get("success") and vertical_result.get("output"):
                video_path = vertical_result["output"]
                result["video_path"] = video_path
                print(f"      [OK] Converted to vertical (1080x1920)")
        except Exception as e:
            print(f"      [!] Vertical conversion error: {e}")
    
    # Step 2.6: Add music if Meta AI didn't add it
    if not meta_music:
        print("\n[2.6/6] Adding music (FFmpeg fallback)...")
        try:
            from backend.core.video_engine.smart_audio import add_smart_audio, video_has_audio
            
            if not video_has_audio(video_path):
                audio_result = add_smart_audio(video_path, prompt)
                if audio_result.get("success") and audio_result.get("output"):
                    video_path = audio_result["output"]
                    result["video_path"] = video_path
                    print(f"      [OK] Added: {audio_result.get('track', 'music')}")
                else:
                    print(f"      [!] Audio failed: {audio_result.get('error', 'unknown')}")
            else:
                print("      [OK] Video already has audio")
        except Exception as e:
            print(f"      [!] Audio error: {e}")
    else:
        print("\n[2.6/6] Music already added by Meta AI")
    
    # Step 3: Analyze video
    print("\n[3/6] Analyzing video content...")
    try:
        metadata = generate_metadata_from_video(video_path, prompt)
        print(f"      [OK] Analysis complete")
    except Exception as e:
        print(f"      [!] Analysis failed: {e}, using prompt-based metadata")
        metadata = None
    
    # Step 4: Generate metadata
    print("\n[4/6] Generating metadata...")
    if not metadata or not metadata.get("title"):
        from backend.core.ai_engine.video_metadata import generate_video_metadata
        # Pass the category from content curator for better emoji selection
        category = idea.get("category", "ai_animation")
        metadata = generate_video_metadata(prompt, category)
    
    title = metadata.get("title", prompt[:50])[:100]
    description = format_youtube_description(metadata)
    tags = metadata.get("tags", [])
    
    result["title"] = title
    result["description"] = description
    result["tags"] = tags
    
    print(f"      Title: {title}")
    print(f"      Tags: {', '.join(tags[:5])}")
    
    # Step 5: Upload to YouTube
    if upload_youtube:
        print("\n[5/6] Uploading to YouTube...")
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
        print("\n[5/6] Skipping YouTube upload")
    
    # Step 6: Upload to Facebook
    if upload_facebook:
        print("\n[6/6] Uploading to Facebook...")
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
        print("\n[6/6] Skipping Facebook upload")
    
    # Mark as uploaded
    mark_as_uploaded(prompt[:50])
    
    result["success"] = True
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Prompt: {prompt[:60]}...")
    print(f"Video: {video_path}")
    print(f"Title: {title}")
    if result.get("youtube_url"):
        print(f"YouTube: {result['youtube_url']}")
    if result.get("facebook_url"):
        print(f"Facebook: {result['facebook_url']}")
    print("=" * 60 + "\n")
    
    return result


def run_batch_pipeline(count: int = 3, **kwargs):
    """Run pipeline multiple times with different prompts."""
    from backend.core.ai_engine.content_curator import get_daily_content_plan
    
    print(f"\n[*] Running batch pipeline for {count} videos...")
    
    plan = get_daily_content_plan(count)
    results = []
    
    for i, item in enumerate(plan, 1):
        print(f"\n{'#' * 60}")
        print(f"# VIDEO {i}/{count}")
        print(f"{'#' * 60}")
        
        result = run_full_pipeline(
            prompt=item["prompt"],
            category=item["category"],
            **kwargs
        )
        results.append(result)
        
        # Wait between uploads to avoid rate limits
        if i < count:
            import time
            print("\n[*] Waiting 30 seconds before next video...")
            time.sleep(30)
    
    # Summary
    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print("=" * 60)
    success = sum(1 for r in results if r.get("success"))
    print(f"Success: {success}/{count}")
    for i, r in enumerate(results, 1):
        status = "[OK]" if r.get("success") else "[X]"
        url = r.get("youtube_url", r.get("error", "N/A"))
        print(f"  {i}. {status} {url}")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fully Automated Meta AI to YouTube Pipeline")
    parser.add_argument("--prompt", "-p", help="Custom prompt for video generation")
    parser.add_argument("--category", "-c", choices=["funny", "indian_comedy", "music", "artistic", "nature", "viral", "motivational"],
                        help="Content category")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--no-upload", action="store_true", help="Skip upload step")
    parser.add_argument("--facebook", "-fb", action="store_true", help="Also upload to Facebook")
    parser.add_argument("--facebook-only", action="store_true", help="Upload to Facebook only (skip YouTube)")
    parser.add_argument("--batch", "-b", type=int, help="Run batch mode with N videos")
    parser.add_argument("--login", action="store_true", help="Just open browser for login setup")
    
    args = parser.parse_args()
    
    if args.login:
        # Just open browser for login
        print("[*] Opening browser for Meta AI login...")
        print("[*] Please login and close the browser when done.")
        import asyncio
        from backend.core.video_engine.meta_ai_generator import MetaAIGenerator
        
        async def do_login():
            gen = MetaAIGenerator(headless=False)
            await gen.start()
            await gen.wait_for_login(timeout=300)
            await gen.stop()
        
        asyncio.run(do_login())
        print("[OK] Login session saved!")
    
    elif args.batch:
        run_batch_pipeline(
            count=args.batch,
            headless=args.headless,
            upload_youtube=not args.no_upload and not args.facebook_only,
            upload_facebook=args.facebook or args.facebook_only
        )
    else:
        run_full_pipeline(
            prompt=args.prompt,
            category=args.category,
            headless=args.headless,
            upload_youtube=not args.no_upload and not args.facebook_only,
            upload_facebook=args.facebook or args.facebook_only
        )
