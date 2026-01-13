"""
FAST MODE - Maximum GPU utilization with direct FFmpeg commands.
Bypasses MoviePy's CPU bottleneck for 10-20x faster encoding.
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv("config.env")

from ai_engine.niche_selector import select_niche
from ai_engine.script_generator import generate_script
from ai_engine.caption_hashtags import generate_caption
from video_engine.voiceover import generate_voiceover
from video_engine.pexels_downloader import get_video_for_keyword
from video_engine.pixabay_downloader import get_video_for_keyword as get_pixabay_video
from video_engine.fast_video_builder import build_video_fast, build_video_super_fast
from post_engine.youtube import upload_youtube_short
from post_engine.facebook import upload_facebook_reel
from rich import print
import time

def run_fast_mode(super_fast=False):
    print("[bold green]🚀 OneClickReelsAI – FAST GPU MODE[/bold green]")
    total_start = time.time()

    # 1. Select niche and topic
    niche_data = select_niche()
    niche = niche_data["niche"]
    topic = niche_data["topic"]

    # 2. Generate script
    script = generate_script(niche, topic)
    meta = generate_caption(niche, topic)

    # 3. Generate voiceover
    print("[cyan]🎤 Generating Voiceover...[/cyan]")
    voice_start = time.time()
    voiceover_path = generate_voiceover(script)
    voice_time = time.time() - voice_start
    print(f"[green]✅ Voiceover ready in {voice_time:.1f}s[/green]")

    # 4. Get background video
    print(f"[cyan]🌐 Searching for background video: '{topic}'...[/cyan]")
    video_start = time.time()
    
    # Try Pixabay first, then Pexels
    video_path = get_pixabay_video(topic)
    if not video_path or not os.path.exists(video_path):
        print("[yellow]⚠️ Pixabay failed, trying Pexels...[/yellow]")
        video_path = get_video_for_keyword(topic)
    
    if not video_path or not os.path.exists(video_path):
        print("[yellow]⚠️ No video found, using fallback...[/yellow]")
        video_path = "assets/videos/default.mp4"
    
    video_time = time.time() - video_start
    print(f"[cyan]📥 Video sourced in {video_time:.1f}s[/cyan]")

    # 5. Build video with GPU acceleration
    print("[cyan]🎬 Building video with FAST GPU mode...[/cyan]")
    
    if super_fast:
        video_path = build_video_super_fast(
            script, 
            "output/reel.mp4",
            voiceover_path,
            video_path,
            topic=topic,
            niche=niche
        )
    else:
        video_path = build_video_fast(
            script,
            "output/reel.mp4",
            voiceover_path,
            video_path,
            topic=topic,
            niche=niche
        )

    total_time = time.time() - total_start
    print(f"[bold green]🎉 Total generation time: {total_time:.1f}s[/bold green]")

    # 6. Upload (optional - comment out if quota exceeded)
    title = script.split("\n")[0][:100]  # Limit title length
    description = f"{meta['caption']}\n\n{meta['hashtags']}"

    try:
        print("[cyan]📤 Uploading to YouTube Shorts...[/cyan]")
        yt_id = upload_youtube_short(video_path, title, description)
        print(f"[green]✅ YouTube Live: https://www.youtube.com/shorts/{yt_id}[/green]")
    except Exception as e:
        print(f"[yellow]⚠️ YouTube upload skipped: {e}[/yellow]")

    try:
        print("[cyan]📤 Uploading to Facebook Reels...[/cyan]")
        fb_id = upload_facebook_reel(video_path, description)
        print(f"[green]✅ Facebook Live: https://www.facebook.com/reel/{fb_id}[/green]")
    except Exception as e:
        print(f"[yellow]⚠️ Facebook upload skipped: {e}[/yellow]")

    print("[bold magenta]🎉 FAST MODE COMPLETE[/bold magenta]")

if __name__ == "__main__":
    import sys
    
    # Check if super_fast mode requested
    super_fast_mode = "--super-fast" in sys.argv or "-sf" in sys.argv
    
    if super_fast_mode:
        print("[bold cyan]⚡ SUPER FAST MODE ENABLED - Maximum GPU utilization![/bold cyan]")
    else:
        print("[cyan]💨 FAST MODE - Using direct FFmpeg GPU commands[/cyan]")
    
    run_fast_mode(super_fast=super_fast_mode)
