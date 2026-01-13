"""
Ultra-fast GPU-accelerated video builder using direct FFmpeg commands.
Bypasses MoviePy's CPU frame processing for maximum GPU utilization.
"""
import subprocess
import os
from pathlib import Path
from rich.console import Console

console = Console()

# Get FFmpeg from imageio-ffmpeg (bundled with moviepy)
try:
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
    FFPROBE_BINARY = FFMPEG_BINARY.replace("ffmpeg.exe", "ffprobe.exe")
except ImportError:
    FFMPEG_BINARY = "ffmpeg"
    FFPROBE_BINARY = "ffprobe"


def build_video_fast(text, output_path, voiceover_path, video_path, topic="", niche=""):
    """
    Ultra-fast video builder using FFmpeg GPU acceleration.
    Skips MoviePy entirely for maximum GPU utilization.
    """
    import time
    build_start = time.time()
    
    # Prepare paths
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("[cyan]Using FAST MODE - Direct FFmpeg GPU acceleration![/cyan]")
    
    # Get video duration from voiceover using MoviePy
    from moviepy import AudioFileClip
    with AudioFileClip(voiceover_path) as audio:
        duration = audio.duration
    target_duration = duration + 1.5  # Add buffer
    
    console.print(f"[cyan]Target: {target_duration:.1f}s video @ 30fps[/cyan]")
    
    # Ultra-fast FFmpeg command with GPU acceleration
    start_time = time.time()
    
    ffmpeg_cmd = [
        FFMPEG_BINARY, "-y",
        "-hwaccel", "cuda",  # GPU decode
        "-hwaccel_output_format", "cuda",  # Keep on GPU
        "-i", video_path,
        "-i", voiceover_path,
        "-filter_complex",
        f"[0:v]scale_cuda=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,setpts=PTS-STARTPTS,fps=30[v];"
        f"[1:a]apad,atrim=0:{target_duration}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-t", str(target_duration),
        "-c:v", "h264_nvenc",  # GPU encode
        "-preset", "p7",  # Max quality
        "-rc", "vbr",
        "-cq", "18",
        "-b:v", "12M",
        "-maxrate", "15M",
        "-bufsize", "20M",
        "-spatial_aq", "1",
        "-temporal_aq", "1",
        "-profile:v", "high",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]
    
    try:
        # Run with progress (stderr shows ffmpeg progress)
        result = subprocess.run(
            ffmpeg_cmd,
            check=True,
            capture_output=False,  # Show live progress
            text=True
        )
        
        elapsed = time.time() - start_time
        realtime_factor = target_duration / elapsed
        console.print(f"[green][OK] GPU encoding successful! ({elapsed:.1f}s, {realtime_factor:.1f}x realtime)[/green]")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red][ERROR] FFmpeg GPU encoding failed![/red]")
        console.print(f"[yellow]Falling back to standard build_video()[/yellow]")
        # Fallback to original method
        from backend.core.video_engine.video_builder import build_video
        return build_video(text, str(output_path), topic, niche)
    
    total_time = time.time() - build_start
    console.print(f"[bold green]Video complete! Total time: {total_time:.1f}s[/bold green]")
    
    return str(output_path)


def build_video_super_fast(text, output_path, voiceover_path, video_path, topic="", niche=""):
    """
    EXPERIMENTAL: Maximum speed with GPU decode + encode + filtering.
    May have compatibility issues with some video formats.
    """
    import time
    build_start = time.time()
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("[bold cyan]SUPER FAST MODE - Full GPU pipeline![/bold cyan]")
    
    # Get duration using MoviePy
    from moviepy import AudioFileClip
    with AudioFileClip(voiceover_path) as audio:
        duration = audio.duration
    target_duration = duration + 1.5
    
    console.print(f"[cyan]Target: {target_duration:.1f}s video @ 30fps[/cyan]")
    
    start_time = time.time()
    
    # Maximum GPU utilization - everything on GPU
    ffmpeg_cmd = [
        FFMPEG_BINARY, "-y",
        "-hwaccel", "cuda",
        "-hwaccel_output_format", "cuda",
        "-c:v", "h264_cuvid",  # GPU decoder
        "-i", video_path,
        "-i", voiceover_path,
        "-filter_complex",
        f"[0:v]scale_cuda=1080:1920:force_original_aspect_ratio=increase,"
        f"hwdownload,format=nv12,crop=1080:1920,hwupload_cuda,"
        f"setpts=PTS-STARTPTS,fps=30[v];"
        f"[1:a]apad,atrim=0:{target_duration}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-t", str(target_duration),
        "-c:v", "h264_nvenc",
        "-preset", "p7",
        "-rc", "vbr",
        "-cq", "18",
        "-b:v", "12M",
        "-maxrate", "15M",
        "-spatial_aq", "1",
        "-temporal_aq", "1",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=False, text=True)
        
        elapsed = time.time() - start_time
        realtime_factor = target_duration / elapsed
        console.print(f"[green][OK] SUPER FAST GPU encoding! ({elapsed:.1f}s, {realtime_factor:.1f}x realtime)[/green]")
        
    except subprocess.CalledProcessError:
        console.print(f"[yellow]Super fast mode failed, trying standard fast mode...[/yellow]")
        return build_video_fast(text, str(output_path), voiceover_path, video_path, topic, niche)
    
    total_time = time.time() - build_start
    console.print(f"[bold green]Video complete! Total time: {total_time:.1f}s[/bold green]")
    
    return str(output_path)


if __name__ == "__main__":
    # Test with existing files
    demo_text = "Discipline beats motivation. Every single day."
    build_video_super_fast(
        demo_text,
        "output/test_super_fast.mp4",
        "output/voiceover.mp3",  # Need existing voiceover
        "assets/videos/test.mp4"  # Need existing video
    )
