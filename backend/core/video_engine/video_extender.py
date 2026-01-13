"""
Video Extender - Extend short videos to target duration using FFmpeg.

Methods:
1. Loop - Repeat video to reach target duration
2. Slow-mo - Slow down video (0.5x-0.8x speed)
3. Reverse loop - Play forward then backward (ping-pong)
4. Combine - Mix of above methods
"""
import os
import sys
import subprocess
import shutil
import glob
import logging
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def find_ffmpeg() -> Optional[str]:
    """Find FFmpeg executable."""
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    if sys.platform == 'win32':
        winget = glob.glob(os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\*ffmpeg*\*\bin\ffmpeg.exe"))
        if winget:
            return winget[0]
    return None


def find_ffprobe() -> Optional[str]:
    """Find FFprobe executable."""
    if shutil.which('ffprobe'):
        return 'ffprobe'
    ffmpeg = find_ffmpeg()
    if ffmpeg and sys.platform == 'win32':
        return ffmpeg.replace('ffmpeg.exe', 'ffprobe.exe')
    return None


FFMPEG = find_ffmpeg()
FFPROBE = find_ffprobe()


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds."""
    if not FFPROBE or not os.path.exists(video_path):
        return 0
    try:
        cmd = [FFPROBE, '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())
    except:
        return 0


def get_video_dimensions(video_path: str) -> tuple:
    """Get video width and height."""
    if not FFPROBE or not os.path.exists(video_path):
        return (0, 0)
    try:
        cmd = [FFPROBE, '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height',
               '-of', 'csv=p=0:s=x', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        w, h = result.stdout.strip().split('x')
        return (int(w), int(h))
    except:
        return (0, 0)


def convert_to_vertical(video_path: str, output_path: str = None) -> Dict:
    """
    Convert video to 9:16 vertical aspect ratio for Shorts/Reels.
    Upscales to 1080x1920 with blur background if needed.
    """
    result = {
        "success": False,
        "input": video_path,
        "output": None,
        "original_size": None,
        "final_size": "1080x1920"
    }
    
    if not FFMPEG or not os.path.exists(video_path):
        result["error"] = "FFmpeg not found or file missing"
        return result
    
    w, h = get_video_dimensions(video_path)
    result["original_size"] = f"{w}x{h}"
    
    if w == 0 or h == 0:
        result["error"] = "Could not get video dimensions"
        return result
    
    if not output_path:
        base = os.path.splitext(video_path)[0]
        output_path = f"{base}_vertical.mp4"
    
    # Target: 1080x1920 (9:16)
    target_w, target_h = 1080, 1920
    
    # Check if already 1080x1920
    if w == 1080 and h == 1920:
        logger.info(f"[OK] Video already 1080x1920")
        result["success"] = True
        result["output"] = video_path
        return result
    
    # Determine filter based on aspect ratio
    if h > w:
        # Already vertical - just upscale/pad to 1080x1920
        logger.info(f"[*] Upscaling vertical {w}x{h} to 1080x1920...")
        vf = f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
    else:
        # Horizontal - add blur background
        logger.info(f"[*] Converting horizontal {w}x{h} to 9:16 vertical...")
        vf = (
            f"split[bg][fg];"
            f"[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg2];"
            f"[fg]scale=1080:-2:force_original_aspect_ratio=decrease[fg2];"
            f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2"
        )
    
    # Build command
    if h > w:
        cmd = [FFMPEG, '-y', '-i', video_path, '-vf', vf,
               '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
               '-c:a', 'aac', '-b:a', '192k', output_path]
    else:
        cmd = [FFMPEG, '-y', '-i', video_path, '-filter_complex', vf,
               '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
               '-c:a', 'aac', '-b:a', '192k', output_path]
    
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode == 0 and os.path.exists(output_path):
            result["success"] = True
            result["output"] = output_path
            new_w, new_h = get_video_dimensions(output_path)
            result["final_size"] = f"{new_w}x{new_h}"
            logger.info(f"[OK] Converted to {new_w}x{new_h}")
        else:
            result["error"] = proc.stderr[:300] if proc.stderr else "Unknown error"
            logger.error(f"[X] Conversion failed: {result['error']}")
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"[X] Conversion error: {e}")
    
    return result


def extend_by_loop(video_path: str, target_duration: float, output_path: str) -> bool:
    """Extend video by looping it."""
    if not FFMPEG:
        return False
    
    current = get_video_duration(video_path)
    if current <= 0:
        return False
    
    loops = int(target_duration / current) + 1
    
    logger.info(f"[*] Looping video {loops}x to reach {target_duration}s...")
    
    # Create concat file
    concat_file = output_path + '.txt'
    with open(concat_file, 'w') as f:
        for _ in range(loops):
            f.write(f"file '{os.path.abspath(video_path)}'\n")
    
    cmd = [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
           '-t', str(target_duration), '-c', 'copy', output_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        os.remove(concat_file)
        return result.returncode == 0 and os.path.exists(output_path)
    except:
        if os.path.exists(concat_file):
            os.remove(concat_file)
        return False


def extend_by_slowmo(video_path: str, target_duration: float, output_path: str) -> bool:
    """Extend video by slowing it down."""
    if not FFMPEG:
        return False
    
    current = get_video_duration(video_path)
    if current <= 0:
        return False
    
    # Calculate speed factor (0.5 = half speed = 2x duration)
    speed = current / target_duration
    speed = max(0.25, min(speed, 1.0))  # Limit between 0.25x and 1x
    
    logger.info(f"[*] Slowing video to {speed:.2f}x speed...")
    
    # Use setpts for video and atempo for audio
    video_filter = f"setpts={1/speed}*PTS"
    
    cmd = [FFMPEG, '-y', '-i', video_path,
           '-filter:v', video_filter,
           '-an',  # Remove audio (will add music later)
           '-t', str(target_duration),
           output_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0 and os.path.exists(output_path)
    except:
        return False


def extend_by_pingpong(video_path: str, target_duration: float, output_path: str) -> bool:
    """Extend video by playing forward then backward (ping-pong effect)."""
    if not FFMPEG:
        return False
    
    current = get_video_duration(video_path)
    if current <= 0:
        return False
    
    logger.info(f"[*] Creating ping-pong loop...")
    
    # Create reversed video
    temp_reversed = output_path + '_rev.mp4'
    cmd_reverse = [FFMPEG, '-y', '-i', video_path,
                   '-vf', 'reverse', '-an', temp_reversed]
    
    try:
        subprocess.run(cmd_reverse, capture_output=True, timeout=60)
        
        # Calculate how many ping-pong cycles needed
        cycle_duration = current * 2
        cycles = int(target_duration / cycle_duration) + 1
        
        # Create concat file
        concat_file = output_path + '.txt'
        with open(concat_file, 'w') as f:
            for _ in range(cycles):
                f.write(f"file '{os.path.abspath(video_path)}'\n")
                f.write(f"file '{os.path.abspath(temp_reversed)}'\n")
        
        cmd = [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
               '-t', str(target_duration), '-c', 'copy', output_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Cleanup
        os.remove(concat_file)
        os.remove(temp_reversed)
        
        return result.returncode == 0 and os.path.exists(output_path)
    except Exception as e:
        logger.error(f"[X] Ping-pong error: {e}")
        for f in [temp_reversed, output_path + '.txt']:
            if os.path.exists(f):
                os.remove(f)
        return False


def extend_video(video_path: str, target_duration: float = 15, 
                 method: str = "auto", output_path: str = None) -> Dict:
    """
    Extend video to target duration.
    
    Args:
        video_path: Input video path
        target_duration: Target duration in seconds
        method: "loop", "slowmo", "pingpong", or "auto"
        output_path: Output path (default: video_extended.mp4)
    
    Returns:
        Dict with success status and output path
    """
    result = {
        "success": False,
        "input": video_path,
        "output": None,
        "original_duration": 0,
        "final_duration": 0,
        "method": method
    }
    
    if not os.path.exists(video_path):
        result["error"] = "Input file not found"
        return result
    
    if not FFMPEG:
        result["error"] = "FFmpeg not found"
        return result
    
    current = get_video_duration(video_path)
    result["original_duration"] = current
    
    if current >= target_duration:
        logger.info(f"[OK] Video already {current:.1f}s, no extension needed")
        result["success"] = True
        result["output"] = video_path
        result["final_duration"] = current
        return result
    
    if not output_path:
        base = os.path.splitext(video_path)[0]
        output_path = f"{base}_extended.mp4"
    
    logger.info(f"[*] Extending {current:.1f}s video to {target_duration}s...")
    
    # Auto-select method based on ratio
    if method == "auto":
        ratio = target_duration / current
        if ratio <= 2:
            method = "slowmo"  # Up to 2x, slow-mo looks natural
        elif ratio <= 4:
            method = "pingpong"  # 2-4x, ping-pong looks smooth
        else:
            method = "loop"  # More than 4x, just loop
    
    result["method"] = method
    
    # Apply extension method
    success = False
    if method == "slowmo":
        success = extend_by_slowmo(video_path, target_duration, output_path)
    elif method == "pingpong":
        success = extend_by_pingpong(video_path, target_duration, output_path)
    else:  # loop
        success = extend_by_loop(video_path, target_duration, output_path)
    
    if success and os.path.exists(output_path):
        final = get_video_duration(output_path)
        result["success"] = True
        result["output"] = output_path
        result["final_duration"] = final
        logger.info(f"[OK] Extended to {final:.1f}s using {method}")
    else:
        result["error"] = f"Extension failed with method: {method}"
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extend video duration")
    parser.add_argument("video", help="Input video path")
    parser.add_argument("-t", "--target", type=float, default=15, help="Target duration (seconds)")
    parser.add_argument("-m", "--method", choices=["auto", "loop", "slowmo", "pingpong"], 
                        default="auto", help="Extension method")
    parser.add_argument("-o", "--output", help="Output path")
    
    args = parser.parse_args()
    
    print(f"\nVideo Extender")
    print(f"FFmpeg: {FFMPEG or 'Not found'}\n")
    
    result = extend_video(args.video, args.target, args.method, args.output)
    
    if result["success"]:
        print(f"\n[OK] Success!")
        print(f"  Original: {result['original_duration']:.1f}s")
        print(f"  Extended: {result['final_duration']:.1f}s")
        print(f"  Method: {result['method']}")
        print(f"  Output: {result['output']}")
    else:
        print(f"\n[X] Failed: {result.get('error', 'Unknown error')}")
