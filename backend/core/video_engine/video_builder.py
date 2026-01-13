import os
import random
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

ASSETS_DIR = "assets"
VIDEOS_DIR = os.path.join(ASSETS_DIR, "videos")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# Windows font path
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

def pick_random_file(folder, extensions=(".mp4", ".mov", ".mp3", ".wav")):
    if not os.path.exists(folder):
        return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
    if not files:
        return None
    return os.path.join(folder, random.choice(files))


from backend.core.video_engine.voiceover import generate_voiceover



from backend.core.video_engine.pexels_downloader import get_video_for_keyword
from backend.core.video_engine.pixabay_downloader import get_video_for_keyword as get_pixabay_video

def build_video(script_text: str, output_path="output/reel.mp4", use_voiceover=True, topic=None, niche=None):
    import time
    build_start = time.time()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    voice_clip = None
    voice_duration = 0

    # 1) Generate Voiceover (Optional)
    if use_voiceover:
        print("[cyan]🎤 Generating Voiceover...[/cyan]")
        voice_start = time.time()
        voice_path = generate_voiceover(script_text, "output/voiceover.mp3", niche=niche)
        
        if voice_path and os.path.exists(voice_path):
            voice_clip = AudioFileClip(voice_path)
            voice_duration = voice_clip.duration
            voice_time = time.time() - voice_start
            print(f"  [OK] Voiceover ready: {voice_duration:.2f}s (generated in {voice_time:.1f}s)")
        else:
            print("[red][ERROR] Voiceover failed[/red]")
    else:
        print("[yellow]Voiceover disabled (keeping original video audio)[/yellow]")

    # 2) Pick background video (Pixabay, Pexels, or Local)
    video_search_start = time.time()
    bg_video_path = None
    
    # Try Pixabay first (more variety, CC0 license)
    if topic:
        print(f"[cyan]Searching Pixabay for: '{topic}'...[/cyan]")
        bg_video_path = get_pixabay_video(topic)
    
    # Fallback to Pexels if Pixabay fails
    # Fallback to Pexels if Pixabay fails
    if not bg_video_path and topic:
        print(f"[yellow]Trying Pexels as fallback...[/yellow]")
        bg_video_path = get_video_for_keyword(topic)
    
    # Fallback to local random video
    if not bg_video_path:
        print("[yellow]Using random local video as fallback[/yellow]")
        bg_video_path = pick_random_file(VIDEOS_DIR, (".mp4", ".mov"))
    
    if not bg_video_path:
        # Final emergency check
        raise FileNotFoundError(f"No video found in {VIDEOS_DIR} and download failed.")
    video_search_time = time.time() - video_search_start
    print(f"[cyan]Video sourced in {video_search_time:.1f}s[/cyan]")
    
    # Load BG and Loop/Resize
    print("[cyan]Processing video...[/cyan]")
    # Load BG and Loop/Resize
    bg_source = VideoFileClip(bg_video_path).resized(height=1920)
    
    # Calculate target duration
    if voice_duration > 0:
        # Match voiceover length
        target_duration = max(voice_duration + 1.5, 5.0)
    else:
        # Default to video length (max 60s) for non-voiceover
        target_duration = min(60.0, bg_source.duration)
        if target_duration < 5.0: target_duration = 5.0 # Min duration
    
    from moviepy.video.fx import Loop

    # Loop video if it's shorter than required
    if bg_source.duration < target_duration:
        bg_source = Loop(duration=target_duration).apply(bg_source)
    else:
        bg_source = bg_source.subclipped(0, target_duration)

    bg = bg_source

    # Ensure 9:16 crop
    w, h = bg.size
    if w > 1080:
        x_center = w // 2
        bg = bg.cropped(
            x1=x_center - 540,
            x2=x_center + 540,
            y1=0,
            y2=1920
        )

    # 3) Prepare subtitles
    lines = [l.strip() for l in script_text.split("\n") if l.strip()]
    # Sync visual text with audio duration
    duration_per_line = target_duration / max(len(lines), 1)

    text_clips = []
    start = 0
    for line in lines:
        txt = TextClip(
            text=line,
            font_size=70,
            font=FONT_PATH,
            color="white",
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(900, None)
        ).with_position(("center", "center")).with_start(start).with_duration(duration_per_line)

        text_clips.append(txt)
        start += duration_per_line

    final = CompositeVideoClip([bg] + text_clips)

    # 4) Mix Audio (Voice + Music)
    music_path = pick_random_file(MUSIC_DIR, (".mp3", ".wav", ".mp4"))
    
    if voice_clip:
        final_audio = voice_clip
        if music_path:
            # Background music at lower volume
            music = AudioFileClip(music_path).with_volume_scaled(0.15)
            from moviepy.audio.fx import AudioLoop
            # Loop music if shorter
            if music.duration < target_duration:
                music = AudioLoop(duration=target_duration).apply(music)
            else:
                music = music.subclipped(0, target_duration)
            
            from moviepy.audio.AudioClip import CompositeAudioClip
            final_audio = CompositeAudioClip([voice_clip, music])
        
        final = final.with_audio(final_audio)
    elif music_path:
        # Fallback to just music if voiceover fails
        music = AudioFileClip(music_path).with_volume_scaled(0.15).subclipped(0, target_duration)
        final = final.with_audio(music)
    else:
        print("[yellow]No music found in assets/music - video will have no audio[/yellow]")

    # 5) Export with GPU acceleration (NVIDIA NVENC)
    print("[cyan]Using GPU acceleration (NVENC)...[/cyan]")
    print(f"[cyan]Target: {target_duration:.1f}s video @ 30fps = {int(target_duration * 30)} frames[/cyan]")
    
    import time
    start_time = time.time()
    
    # Try GPU encoding first, fallback to CPU if fails
    try:
        final.write_videofile(
            output_path,
            fps=30,
            codec="h264_nvenc",  # NVIDIA hardware encoder
            audio_codec="aac",
            preset="p7",  # NVENC max quality preset (p1=fastest, p7=highest quality)
            ffmpeg_params=[
                "-rc", "vbr",  # Variable bitrate
                "-cq", "18",   # High quality (lower=better, 18=excellent)
                "-b:v", "12M",  # High bitrate
                "-maxrate", "15M",
                "-bufsize", "20M",
                "-gpu", "0",   # Use first GPU
                "-spatial_aq", "1",  # Better quality
                "-temporal_aq", "1",  # Better quality
                "-2pass", "1"  # Two-pass encoding for quality
            ],
            threads=8,  # Optimal threads
            logger='bar'  # Show progress bar
        )
        elapsed = time.time() - start_time
        print(f"[green][OK] GPU encoding successful! ({elapsed:.1f}s, {target_duration/elapsed:.1f}x realtime)[/green]")
    except Exception as e:
        print(f"[yellow]GPU encoding failed ({e}), falling back to CPU...[/yellow]")
        start_time = time.time()
        final.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=16,  # Max threads for CPU
            preset="ultrafast",  # Fastest CPU preset
            logger='bar'  # Show progress bar
        )
        elapsed = time.time() - start_time
        print(f"[green][OK] CPU encoding complete ({elapsed:.1f}s)[/green]")
    
    total_time = time.time() - build_start
    print(f"[bold green]Video complete! Total time: {total_time:.1f}s[/bold green]")

    return output_path

if __name__ == "__main__":
    demo_text = "Nobody talks about this. Discipline beats motivation. Every single day."
    build_video(demo_text, "output/test_reel.mp4")
