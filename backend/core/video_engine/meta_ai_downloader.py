"""
Meta AI Video/Animation Downloader
Downloads AI-generated videos and animations from Meta AI posts.
"""
import os
import sys
import requests
import re
import asyncio
import logging
import subprocess
import shutil
import glob
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Playwright
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class Config:
    PAGE_LOAD_TIMEOUT = 60000
    FRAME_CAPTURE_TIMEOUT = 20000
    DEFAULT_FPS = 12
    MIN_VIDEO_SIZE = 100000
    MIN_AUDIO_SIZE = 5000
    MIN_FRAME_SIZE = 10000
    OUTPUT_BASE_DIR = "output/meta_ai_downloads"
    FFMPEG_CRF = 23
    AUDIO_BITRATE = '192k'

def find_ffmpeg() -> Optional[str]:
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    if sys.platform == 'win32':
        paths = [r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"]
        winget = glob.glob(os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\*ffmpeg*\*\bin\ffmpeg.exe"))
        paths.extend(winget)
        for path in paths:
            if os.path.exists(path):
                return path
    return None

FFMPEG_PATH = find_ffmpeg()
FFMPEG_AVAILABLE = FFMPEG_PATH is not None

def find_ffprobe() -> Optional[str]:
    if shutil.which('ffprobe'):
        return 'ffprobe'
    if FFMPEG_PATH:
        # Try same directory as ffmpeg
        ffprobe = FFMPEG_PATH.replace('ffmpeg.exe', 'ffprobe.exe')
        if os.path.exists(ffprobe):
            return ffprobe
    # Check WinGet path directly
    if sys.platform == 'win32':
        winget = glob.glob(os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\*ffmpeg*\*\bin\ffprobe.exe"))
        if winget:
            return winget[0]
    return None

FFPROBE_PATH = find_ffprobe()
if FFPROBE_PATH:
    logger.info(f"FFprobe found: {FFPROBE_PATH}")
YTDLP_AVAILABLE = shutil.which('yt-dlp') is not None

def is_valid_video(video_path: str) -> bool:
    """Check if video file is valid and playable using ffprobe."""
    if not FFPROBE_PATH or not os.path.exists(video_path):
        return False
    try:
        cmd = [FFPROBE_PATH, '-v', 'error', '-select_streams', 'v:0', 
               '-show_entries', 'stream=codec_type,width,height', '-of', 'csv=p=0', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # Valid if ffprobe returns without errors and has video dimensions
        output = result.stdout.strip()
        return result.returncode == 0 and output and len(output) > 0
    except:
        return False

def has_audio(video_path: str) -> bool:
    """Check if video has audio track."""
    if not FFPROBE_PATH or not os.path.exists(video_path):
        return False
    try:
        cmd = [FFPROBE_PATH, '-v', 'error', '-select_streams', 'a:0', 
               '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and 'audio' in result.stdout.lower()
    except:
        return False

def get_video_info(video_path: str) -> Dict:
    """Get video dimensions and duration."""
    info = {"width": 0, "height": 0, "duration": 0, "has_audio": False}
    if not FFPROBE_PATH or not os.path.exists(video_path):
        return info
    try:
        cmd = [FFPROBE_PATH, '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height,duration', '-of', 'csv=p=0', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            parts = result.stdout.strip().split(',')
            if len(parts) >= 3:
                info["width"] = int(parts[0])
                info["height"] = int(parts[1])
                info["duration"] = float(parts[2])
        info["has_audio"] = has_audio(video_path)
    except:
        pass
    return info

def download_with_ytdlp(url: str, output_dir: str) -> Optional[Dict]:
    """Download Meta AI video using yt-dlp (handles fragmented streams)."""
    if not YTDLP_AVAILABLE:
        return None
    
    try:
        temp_dir = os.path.join(output_dir, "ytdlp_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Check if this is a specific post URL (contains /post/)
        is_single_post = '/post/' in url
        
        # For single posts, use --playlist-items 1 to get only first video
        # Also use --no-playlist to avoid downloading entire profile
        cmd = ['yt-dlp', '-o', os.path.join(temp_dir, '%(autonumber)s.%(ext)s'), 
               '--merge-output-format', 'mp4', '-q']
        
        if is_single_post:
            # Single post - limit to 1 video, no playlist
            cmd.extend(['--no-playlist', '--playlist-items', '1'])
            logger.info("[*] Single post detected - downloading only this video")
        else:
            # Profile page - limit to first 3 videos max
            cmd.extend(['--playlist-items', '1-3'])
            logger.info("[*] Profile page - limiting to 3 videos")
        
        cmd.append(url)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logger.warning(f"[!] yt-dlp returned: {result.stderr[:200] if result.stderr else 'no error'}")
            # Try without playlist restrictions as fallback
            cmd_fallback = ['yt-dlp', '-o', os.path.join(temp_dir, '%(autonumber)s.%(ext)s'), 
                           '--merge-output-format', 'mp4', '-q', url]
            result = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return None
        
        # Analyze all downloaded videos
        videos = []
        for f in os.listdir(temp_dir):
            if f.endswith('.mp4'):
                path = os.path.join(temp_dir, f)
                if is_valid_video(path):
                    info = get_video_info(path)
                    info["path"] = path
                    info["size"] = os.path.getsize(path)
                    info["is_vertical"] = info["height"] > info["width"]
                    videos.append(info)
        
        if not videos:
            return None
        
        logger.info(f"[*] Found {len(videos)} video(s)")
        
        # Scoring system: prioritize vertical videos with audio (typical for Shorts)
        def score_video(v):
            score = 0
            if v["has_audio"]:
                score += 100  # Audio is important
            if v["is_vertical"]:
                score += 50   # Vertical preferred for Shorts
            if v["duration"] > 5:
                score += 20   # Longer videos preferred
            score += v["size"] / 1000000  # Larger = better quality
            return score
        
        # Sort by score
        videos.sort(key=score_video, reverse=True)
        best = videos[0]
        
        logger.info(f"[OK] Selected video: {best['width']}x{best['height']}, {best['duration']:.1f}s, audio={best['has_audio']}")
        
        final_path = os.path.join(output_dir, "video.mp4")
        shutil.move(best["path"], final_path)
        
        # Cleanup temp
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        logger.info(f"[OK] yt-dlp downloaded: {best['size'] / 1024 / 1024:.2f} MB")
        return {"path": final_path, "size": best["size"], "has_audio": best["has_audio"], 
                "width": best["width"], "height": best["height"], "duration": best["duration"]}
    except Exception as e:
        logger.error(f"[X] yt-dlp error: {e}")
        return None


class MediaCapture:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.frames_dir = os.path.join(output_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)
        self.videos: List[Dict] = []
        self.frames: List[Dict] = []
        self.audios: List[Dict] = []
        self.seen_urls: set = set()
        self.prompt_text: str = ""
        self.music_info: str = ""
        
    async def handle_response(self, response):
        try:
            url = response.url
            if url in self.seen_urls:
                return
            content_type = response.headers.get('content-type', '').lower()
            
            if 'video' in content_type or '.mp4' in url.lower():
                await self._capture_video(response, url)
            elif 'audio' in content_type or any(ext in url.lower() for ext in ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm']):
                await self._capture_audio(response, url)
            # Also check for music/audio in Facebook CDN URLs
            elif 'fbcdn' in url and ('audio' in url.lower() or 'music' in url.lower() or 'sound' in url.lower()):
                await self._capture_audio(response, url)
            elif 'image' in content_type and 'scontent' in url:
                await self._capture_frame(response, url)
        except:
            pass
    
    async def _capture_video(self, response, url: str):
        try:
            body = await response.body()
            size = len(body)
            if size > Config.MIN_VIDEO_SIZE:
                self.seen_urls.add(url)
                video_path = os.path.join(self.output_dir, f"video_{len(self.videos)}.mp4")
                with open(video_path, 'wb') as f:
                    f.write(body)
                self.videos.append({"path": video_path, "size": size, "url": url})
                logger.info(f"[VIDEO] Captured: {size / 1024:.1f} KB")
        except:
            pass
    
    async def _capture_audio(self, response, url: str):
        try:
            body = await response.body()
            if len(body) > Config.MIN_AUDIO_SIZE:
                self.seen_urls.add(url)
                # Determine extension from URL or content-type
                ext = '.mp3'
                if '.m4a' in url.lower():
                    ext = '.m4a'
                elif '.aac' in url.lower():
                    ext = '.aac'
                elif '.wav' in url.lower():
                    ext = '.wav'
                audio_path = os.path.join(self.output_dir, f"audio{ext}")
                with open(audio_path, 'wb') as f:
                    f.write(body)
                self.audios.append({"path": audio_path, "size": len(body)})
                logger.info(f"[AUDIO] Captured: {len(body) / 1024:.1f} KB from {url[:80]}...")
        except:
            pass
    
    async def _capture_frame(self, response, url: str):
        try:
            body = await response.body()
            if len(body) > Config.MIN_FRAME_SIZE:
                self.seen_urls.add(url)
                frame_path = os.path.join(self.frames_dir, f"frame_{len(self.frames):04d}.jpg")
                with open(frame_path, 'wb') as f:
                    f.write(body)
                self.frames.append({"path": frame_path, "size": len(body)})
        except:
            pass
    
    def get_best_video(self) -> Optional[Dict]:
        if not self.videos:
            return None
        # Filter to only valid videos and get the largest
        valid_videos = [v for v in self.videos if is_valid_video(v["path"])]
        if not valid_videos:
            logger.warning("[!] No valid videos found, will use frames instead")
            return None
        best = max(valid_videos, key=lambda v: v["size"])
        logger.info(f"[OK] Found {len(valid_videos)} valid videos, best: {best['size']/1024:.1f} KB")
        return best


async def extract_meta_content(post_url: str, output_dir: str) -> Optional[Dict]:
    if not PLAYWRIGHT_AVAILABLE:
        raise ValueError("Playwright required")
    
    media = MediaCapture(output_dir)
    
    try:
        async with async_playwright() as p:
            logger.info("[*] Launching browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            page.on('response', media.handle_response)
            
            logger.info(f"[*] Loading: {post_url}")
            try:
                await page.goto(post_url, wait_until='networkidle', timeout=Config.PAGE_LOAD_TIMEOUT)
            except:
                await page.goto(post_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_timeout(3000)
            
            # Extract prompt
            media.prompt_text = await extract_prompt(page)
            if media.prompt_text:
                logger.info(f"[OK] Prompt found")
            
            # Extract music info
            media.music_info = await extract_music_info(page)
            
            # Click video if present
            try:
                video = await page.query_selector('video')
                if video:
                    await video.click()
                    await page.wait_for_timeout(1000)
            except:
                pass
            
            # Wait for content
            logger.info("[*] Waiting for media...")
            await page.wait_for_timeout(Config.FRAME_CAPTURE_TIMEOUT)
            await page.evaluate("window.scrollBy(0, 300)")
            await page.wait_for_timeout(2000)
            
            await browser.close()
        
        return process_results(media, output_dir)
        
    except Exception as e:
        logger.error(f"[X] Error: {e}")
        return None

async def extract_prompt(page) -> str:
    selectors = ['[data-testid="post-content"]', 'article p', 'div[dir="auto"]', 'span[dir="auto"]']
    for selector in selectors:
        try:
            elements = await page.query_selector_all(selector)
            for el in elements:
                text = await el.inner_text()
                if text and 30 < len(text) < 5000:
                    lower = text.lower()
                    if not any(x in lower for x in ['sign in', 'create', 'explore', 'http']):
                        return text.strip()
        except:
            continue
    return ""

async def extract_music_info(page) -> Optional[str]:
    """Extract music/song name from Meta AI post."""
    try:
        # Look for music info - usually shows as "Song · Artist" format
        selectors = [
            'span[dir="auto"]',
            'div[dir="auto"]', 
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            for el in elements:
                text = await el.inner_text()
                if text:
                    text = text.strip()
                    # Look for music patterns: "Song · Artist" format
                    if '·' in text and len(text) < 200 and len(text) > 5:
                        # Could be "Song · Artist" format
                        if not any(x in text.lower() for x in ['sign in', 'create', 'explore', 'http', 'followers', 'prompt']):
                            logger.info(f"[MUSIC] Found: {text}")
                            return text
        return None
    except Exception as e:
        logger.warning(f"[!] Music extraction failed: {e}")
        return None

def download_music_from_youtube(song_query: str, output_dir: str) -> Optional[str]:
    """Download music from YouTube based on song name."""
    if not YTDLP_AVAILABLE:
        return None
    
    try:
        logger.info(f"[*] Searching YouTube for music: {song_query}")
        
        # Search and download audio only
        output_template = os.path.join(output_dir, "music.%(ext)s")
        cmd = [
            'yt-dlp',
            f'ytsearch1:{song_query}',  # Search YouTube, get first result
            '-x',  # Extract audio
            '--audio-format', 'mp3',
            '--audio-quality', '192K',
            '-o', output_template,
            '--no-playlist',
            '-q'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Find the downloaded file
        music_path = os.path.join(output_dir, "music.mp3")
        if os.path.exists(music_path):
            logger.info(f"[OK] Music downloaded: {music_path}")
            return music_path
        
        # Check for other extensions
        for ext in ['m4a', 'webm', 'opus', 'mp3']:
            check_path = os.path.join(output_dir, f"music.{ext}")
            if os.path.exists(check_path):
                if ext != 'mp3':
                    # Convert to mp3
                    mp3_path = os.path.join(output_dir, "music.mp3")
                    convert_cmd = [FFMPEG_PATH or 'ffmpeg', '-y', '-i', check_path, '-acodec', 'libmp3lame', '-b:a', '192k', mp3_path]
                    subprocess.run(convert_cmd, capture_output=True, timeout=60)
                    if os.path.exists(mp3_path):
                        os.remove(check_path)
                        logger.info(f"[OK] Music converted: {mp3_path}")
                        return mp3_path
                else:
                    return check_path
        
        logger.warning("[!] Music download failed - file not found")
        return None
        
    except Exception as e:
        logger.error(f"[X] Music download error: {e}")
        return None

def process_results(media: MediaCapture, output_dir: str) -> Dict:
    # Save prompt
    if media.prompt_text:
        with open(os.path.join(output_dir, "prompt.txt"), 'w', encoding='utf-8') as f:
            f.write(media.prompt_text)
    
    result = {
        "prompt": media.prompt_text,
        "prompt_file": os.path.join(output_dir, "prompt.txt") if media.prompt_text else None,
        "audio": media.audios[0] if media.audios else None,
        "music_info": media.music_info if hasattr(media, 'music_info') else None
    }
    
    best_video = media.get_best_video()
    
    if best_video:
        final_path = os.path.join(output_dir, "video.mp4")
        shutil.copy(best_video["path"], final_path)
        # Clean up other videos
        for v in media.videos:
            try:
                os.remove(v["path"])
            except:
                pass
        result.update({"type": "video", "path": final_path, "size": best_video["size"]})
        logger.info(f"[OK] Best video: {best_video['size'] / 1024 / 1024:.2f} MB")
    elif media.frames:
        result.update({"type": "animation", "frames_dir": media.frames_dir, "frame_count": len(media.frames)})
    else:
        result["type"] = "metadata_only" if media.prompt_text else None
    
    return result if result.get("type") else None


def stitch_frames_to_video(frames_dir: str, output_path: str, fps: int = 12) -> Optional[str]:
    if not FFMPEG_AVAILABLE:
        return None
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(('.jpg', '.png'))])
    if len(frames) < 2:
        return None
    
    cmd = [FFMPEG_PATH, '-y', '-framerate', str(fps), '-i', os.path.join(frames_dir, 'frame_%04d.jpg'),
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(Config.FFMPEG_CRF), output_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
    except:
        pass
    return None

def merge_audio_video(video_path: str, audio_path: str, output_path: str, audio_start_sec: float = 0) -> Optional[str]:
    """Merge video with audio, optionally starting audio from a specific timestamp."""
    if not FFMPEG_AVAILABLE:
        return None
    
    # Build command - if audio_start_sec > 0, skip to that point in audio (for hook/chorus)
    cmd = [FFMPEG_PATH, '-y', '-i', video_path]
    
    if audio_start_sec > 0:
        # Start audio from specified timestamp (skip intro, get to hook)
        cmd.extend(['-ss', str(audio_start_sec), '-i', audio_path])
    else:
        cmd.extend(['-i', audio_path])
    
    cmd.extend(['-c:v', 'copy', '-c:a', 'aac', '-b:a', Config.AUDIO_BITRATE, '-shortest', output_path])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return output_path
    except:
        pass
    return None


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds."""
    if not FFPROBE_PATH or not os.path.exists(audio_path):
        return 0
    try:
        cmd = [FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return 0


def estimate_hook_timestamp(audio_duration: float) -> float:
    """
    Estimate where the hook/chorus starts in a song.
    Most pop songs: Intro(0-15s) -> Verse(15-45s) -> Pre-chorus(45-60s) -> CHORUS(60-90s)
    For shorter songs, scale proportionally.
    """
    if audio_duration <= 30:
        return 0  # Short clip, use from start
    elif audio_duration <= 120:
        # Short song - hook usually around 30-40% mark
        return audio_duration * 0.35
    else:
        # Standard song (3-4 min) - hook usually around 50-70 seconds
        return min(55, audio_duration * 0.25)  # ~55 seconds or 25% in

def download_meta_ai_content(url: str, output_dir: str = None) -> Dict:
    """Download Meta AI content (video, animation, prompt)."""
    if not any(x in url for x in ['meta.ai/@', 'meta.ai/t/', 'meta.ai/post/', 'meta.ai/imagine/']):
        raise ValueError(f"Invalid Meta AI URL: {url}")
    
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(Config.OUTPUT_BASE_DIR, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"[*] Output: {output_dir}")
    
    # Try yt-dlp first (handles fragmented streams better)
    if YTDLP_AVAILABLE:
        logger.info("[*] Trying yt-dlp...")
        ytdlp_result = download_with_ytdlp(url, output_dir)
        if ytdlp_result:
            # Also extract prompt and possibly audio using playwright
            prompt = ""
            captured_audio = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(extract_meta_content(url, output_dir))
                loop.close()
                if result:
                    prompt = result.get("prompt", "")
                    captured_audio = result.get("audio")
            except:
                pass
            
            final_path = ytdlp_result["path"]
            final_size = ytdlp_result["size"]
            
            # If yt-dlp video has no audio but playwright captured audio, merge them
            if not ytdlp_result.get("has_audio") and captured_audio and os.path.exists(captured_audio.get("path", "")):
                logger.info("[*] Merging captured audio with video...")
                merged_path = os.path.join(output_dir, "video_merged.mp4")
                if merge_audio_video(final_path, captured_audio["path"], merged_path):
                    final_path = merged_path
                    final_size = os.path.getsize(merged_path)
                    logger.info("[OK] Audio merged successfully!")
            
            # If still no audio, try to download music from YouTube based on music info
            music_info = result.get("music_info") if result else None
            if not ytdlp_result.get("has_audio") and not captured_audio and music_info:
                logger.info(f"[*] No audio captured, trying to download music: {music_info}")
                music_path = download_music_from_youtube(music_info, output_dir)
                if music_path and os.path.exists(music_path):
                    # Calculate hook timestamp - skip intro, get to the catchy part
                    audio_duration = get_audio_duration(music_path)
                    hook_start = estimate_hook_timestamp(audio_duration)
                    logger.info(f"[*] Audio duration: {audio_duration:.1f}s, starting from hook at {hook_start:.1f}s")
                    
                    merged_path = os.path.join(output_dir, "video_with_music.mp4")
                    if merge_audio_video(final_path, music_path, merged_path, audio_start_sec=hook_start):
                        final_path = merged_path
                        final_size = os.path.getsize(merged_path)
                        logger.info("[OK] Music merged with hook section!")
            
            return {
                "success": True,
                "source_url": url,
                "output_folder": output_dir,
                "prompt": prompt,
                "prompt_file": os.path.join(output_dir, "prompt.txt") if prompt else None,
                "audio": captured_audio,
                "music_info": music_info,
                "type": "video",
                "file_path": final_path,
                "file_size": final_size,
                "filename": os.path.basename(final_path),
                "message": "Video downloaded successfully (yt-dlp)"
            }
    
    # Fallback to playwright extraction
    logger.info("[*] Using playwright extraction...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(extract_meta_content(url, output_dir))
        loop.close()
    except Exception as e:
        raise ValueError(f"Extraction failed: {e}")
    
    if not result:
        raise ValueError("Could not extract content")
    
    response = {
        "success": True,
        "source_url": url,
        "output_folder": output_dir,
        "prompt": result.get("prompt", ""),
        "prompt_file": result.get("prompt_file"),
        "audio": result.get("audio")
    }
    
    if result["type"] == "video":
        response.update({
            "type": "video",
            "file_path": result["path"],
            "file_size": result["size"],
            "filename": os.path.basename(result["path"]),
            "message": "Video downloaded successfully"
        })
    elif result["type"] == "animation":
        frame_count = result["frame_count"]
        if FFMPEG_AVAILABLE:
            video_path = os.path.join(output_dir, "animation.mp4")
            if stitch_frames_to_video(result["frames_dir"], video_path):
                if result.get("audio"):
                    merged = os.path.join(output_dir, "animation_with_audio.mp4")
                    if merge_audio_video(video_path, result["audio"]["path"], merged):
                        video_path = merged
                response.update({
                    "type": "animation",
                    "file_path": video_path,
                    "file_size": os.path.getsize(video_path),
                    "frame_count": frame_count,
                    "filename": os.path.basename(video_path),
                    "message": f"Animation from {frame_count} frames"
                })
            else:
                response.update({"type": "frames", "frames_dir": result["frames_dir"], "frame_count": frame_count})
        else:
            response.update({"type": "frames", "frames_dir": result["frames_dir"], "frame_count": frame_count})
    elif result["type"] == "metadata_only":
        response.update({"type": "metadata", "message": "Prompt/audio only"})
    
    return response

if __name__ == "__main__":
    print(f"\nMeta AI Downloader\nFFmpeg: {FFMPEG_PATH if FFMPEG_AVAILABLE else 'Not found'}\n")
    url = sys.argv[1] if len(sys.argv) > 1 else input("URL: ").strip()
    if url:
        try:
            r = download_meta_ai_content(url)
            print(f"[OK] {r.get('type')}: {r.get('file_path') or r.get('frames_dir')}")
        except Exception as e:
            print(f"[X] {e}")
