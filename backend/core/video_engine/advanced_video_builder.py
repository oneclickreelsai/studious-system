"""
Advanced video builder with AI-powered optimizations
"""
import os
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import subprocess
import json
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from backend.utils.error_handler import retry_with_backoff, safe_file_operation, RetryableError, ErrorType
from backend.utils.monitoring import performance_monitor, timed_operation
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class AdvancedVideoBuilder:
    """Advanced video builder with AI optimizations and GPU acceleration."""
    
    def __init__(self):
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Video quality presets
        self.quality_presets = {
            "ultra": {"width": 1080, "height": 1920, "fps": 60, "bitrate": "4M", "crf": 18},
            "high": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "2M", "crf": 23},
            "medium": {"width": 720, "height": 1280, "fps": 30, "bitrate": "1M", "crf": 28},
            "fast": {"width": 540, "height": 960, "fps": 24, "bitrate": "500k", "crf": 32}
        }
        
        # Subtitle styles for different niches
        self.subtitle_styles = {
            "motivation": {
                "font": "Arial-Bold",
                "fontsize": 18,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 1,
                "method": "caption"
            },
            "finance": {
                "font": "Arial-Bold",
                "fontsize": 18,
                "color": "yellow",
                "stroke_color": "black",
                "stroke_width": 1,
                "method": "caption"
            },
            "facts": {
                "font": "Arial",
                "fontsize": 18,
                "color": "white",
                "stroke_color": "blue",
                "stroke_width": 2,
                "method": "caption"
            }
        }
    
    def check_gpu_acceleration(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "h264_nvenc" in result.stdout or "h264_amf" in result.stdout
        except Exception as e:
            logger.warning(f"GPU check failed: {e}")
            return False
    
    def get_optimal_encoder(self) -> str:
        """Get the best available encoder."""
        if self.check_gpu_acceleration():
            # Try NVIDIA first, then AMD
            encoders = ["h264_nvenc", "h264_amf", "libx264"]
        else:
            encoders = ["libx264"]
        
        for encoder in encoders:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=1", 
                     "-c:v", encoder, "-f", "null", "-"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"Using encoder: {encoder}")
                    return encoder
            except Exception:
                continue
        
        logger.warning("Falling back to libx264 encoder")
        return "libx264"
    
    @timed_operation("video_analysis")
    def analyze_background_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze background video for optimal processing."""
        try:
            # Use ffprobe for detailed analysis
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {result.stderr}")
            
            data = json.loads(result.stdout)
            video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
            
            if not video_stream:
                raise Exception("No video stream found")
            
            analysis = {
                "duration": float(data["format"]["duration"]),
                "width": int(video_stream["width"]),
                "height": int(video_stream["height"]),
                "fps": eval(video_stream["r_frame_rate"]),  # Convert fraction to float
                "codec": video_stream["codec_name"],
                "bitrate": int(data["format"].get("bit_rate", 0)),
                "has_audio": any(s["codec_type"] == "audio" for s in data["streams"]),
                "aspect_ratio": int(video_stream["width"]) / int(video_stream["height"])
            }
            
            # Determine if video needs processing
            analysis["needs_resize"] = analysis["aspect_ratio"] != 9/16
            analysis["needs_fps_change"] = analysis["fps"] not in [24, 30, 60]
            analysis["is_portrait"] = analysis["height"] > analysis["width"]
            
            logger.info(f"Video analysis: {analysis['width']}x{analysis['height']}, {analysis['fps']}fps, {analysis['duration']:.1f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            # Fallback to basic MoviePy analysis
            try:
                with VideoFileClip(video_path) as clip:
                    return {
                        "duration": clip.duration,
                        "width": clip.w,
                        "height": clip.h,
                        "fps": clip.fps,
                        "needs_resize": clip.w / clip.h != 9/16,
                        "needs_fps_change": clip.fps not in [24, 30, 60],
                        "is_portrait": clip.h > clip.w,
                        "has_audio": clip.audio is not None
                    }
            except Exception as fallback_error:
                logger.error(f"Fallback analysis failed: {fallback_error}")
                raise RetryableError(f"Video analysis failed: {e}", ErrorType.PROCESSING_ERROR)
    
    @timed_operation("subtitle_generation")
    def create_dynamic_subtitles(self, script: str, niche: str, duration: float) -> List[Dict[str, Any]]:
        """Create dynamic subtitles with timing and styling."""
        
        # Split script into words and estimate timing
        words = script.split()
        words_per_second = 2.5  # Average speaking rate
        total_words = len(words)
        
        if total_words == 0:
            return []
        
        # Adjust speaking rate based on content
        if niche == "motivation":
            words_per_second = 2.2  # Slower for emphasis
        elif niche == "facts":
            words_per_second = 2.8  # Faster for information
        
        # Calculate timing for each word
        word_duration = 1.0 / words_per_second
        subtitle_chunks = []
        
        # Group words into subtitle chunks (3-5 words per chunk)
        chunk_size = 4
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            start_time = i * word_duration
            end_time = min((i + len(chunk_words)) * word_duration, duration)
            
            subtitle_chunks.append({
                "text": chunk_text,
                "start": start_time,
                "end": end_time,
                "duration": end_time - start_time
            })
        
        # Apply niche-specific styling
        style = self.subtitle_styles.get(niche, self.subtitle_styles["motivation"])
        
        for chunk in subtitle_chunks:
            chunk.update(style)
        
        logger.info(f"Created {len(subtitle_chunks)} subtitle chunks for {niche}")
        return subtitle_chunks
    
    @safe_file_operation
    @timed_operation("combine_components")
    def combine_components(
        self,
        video_path: str,
        audio_path: str,
        subtitle_path: str,
        output_path: str,
        target_duration: float,
        music_path: Optional[str] = None
    ) -> str:
        """
        Combine pre-generated components into a final video.
        - video_path: Background video (will be looped/cropped)
        - audio_path: Main TTS voiceover
        - subtitle_path: .ass subtitle file
        - music_path: Optional background music
        """
        encoder = self.get_optimal_encoder()
        preset = self.quality_presets["high"]
        
        # Temp video for visual track
        temp_visual = self.temp_dir / f"visual_{int(time.time())}.mp4"
        
        try:
            # 1. Process Visuals (Crop/Resize/Loop) to match duration
            bg_analysis = self.analyze_background_video(video_path)
            
            target_width, target_height = preset["width"], preset["height"]
            
            if not bg_analysis["is_portrait"]:
                crop_width = int(bg_analysis["height"] * 9/16)
                crop_x = (bg_analysis["width"] - crop_width) // 2
                video_filter = f"crop={crop_width}:{bg_analysis['height']}:{crop_x}:0,scale={target_width}:{target_height}"
            else:
                video_filter = f"scale={target_width}:{target_height}"
                
            input_options = []
            if bg_analysis["duration"] < target_duration:
                loop_count = int(target_duration / bg_analysis["duration"]) + 1
                input_options = ["-stream_loop", str(loop_count)]

            # Generate visual-only track first
            cmd_visual = [
                "ffmpeg", "-y",
                *input_options,
                "-i", video_path,
                "-vf", video_filter,
                "-c:v", encoder,
                "-preset", "fast" if "nvenc" in encoder else "medium",
                "-r", str(preset["fps"]),
                "-t", str(target_duration),
                "-an",
                str(temp_visual)
            ]
            
            if "nvenc" in encoder:
                cmd_visual.extend(["-gpu", "0"]) # Removed -rc vbr to simplify
                
            subprocess.run(cmd_visual, capture_output=True, check=True)
            
            # 2. Mix Audio and Burn Subtitles
            # Path escaping for subtitles
            sub_path_str = str(Path(subtitle_path).absolute()).replace('\\', '/').replace(':', '\\:')
            
            cmd_final = [
                "ffmpeg", "-y",
                "-i", str(temp_visual),
                "-i", audio_path
            ]
            
            # Add music input if present
            if music_path:
                cmd_final.extend(["-stream_loop", "-1", "-i", music_path])
                
            # Filter complex
            # [1:a] is voice, [2:a] is music (if present)
            if music_path:
                filter_complex = (
                    f"[2:a]volume=0.1[music];"
                    f"[1:a][music]amix=inputs=2:duration=first[aout];"
                    f"[0:v]subtitles='{sub_path_str}'[vout]"
                )
                map_options = ["-map", "[vout]", "-map", "[aout]"]
            else:
                filter_complex = f"[0:v]subtitles='{sub_path_str}'[vout]"
                map_options = ["-map", "[vout]", "-map", "1:a"]

            cmd_final.extend([
                "-filter_complex", filter_complex,
                *map_options,
                "-c:v", encoder,
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                output_path
            ])
             
            result = subprocess.run(cmd_final, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                raise Exception(f"Final mix failed: {result.stderr}")

            return output_path

        finally:
            if temp_visual.exists():
                temp_visual.unlink()

    @retry_with_backoff(max_retries=2)
    @safe_file_operation
    @timed_operation("gpu_video_build")
    def build_video_gpu_accelerated(
        self,
        background_video: str,
        voiceover_audio: str,
        script: str,
        niche: str,
        output_path: str,
        quality: str = "high"
    ) -> str:
        """Build video using GPU acceleration with FFmpeg."""
        
        start_time = time.time()
        
        # Get quality preset
        preset = self.quality_presets.get(quality, self.quality_presets["high"])
        encoder = self.get_optimal_encoder()
        
        # Analyze background video
        bg_analysis = self.analyze_background_video(background_video)
        
        # Create temporary files
        temp_video = self.temp_dir / f"temp_video_{int(time.time())}.mp4"
        temp_subtitles = self.temp_dir / f"temp_subs_{int(time.time())}.ass"
        
        try:
            # Step 1: Process background video
            logger.info("Processing background video with GPU acceleration...")
            
            # Calculate crop/resize parameters for 9:16 aspect ratio
            target_width, target_height = preset["width"], preset["height"]
            
            if not bg_analysis["is_portrait"]:
                # Landscape to portrait: crop center and resize
                crop_width = int(bg_analysis["height"] * 9/16)
                crop_x = (bg_analysis["width"] - crop_width) // 2
                video_filter = f"crop={crop_width}:{bg_analysis['height']}:{crop_x}:0,scale={target_width}:{target_height}"
            else:
                # Already portrait: just resize
                video_filter = f"scale={target_width}:{target_height}"
            
            # Add loop if video is too short
            voiceover_duration = self._get_audio_duration(voiceover_audio)
            logger.info(f"Voiceover duration: {voiceover_duration:.1f}s, Video duration: {bg_analysis['duration']:.1f}s")
            
            if bg_analysis["duration"] < voiceover_duration:
                # Use stream_loop for input file looping (more reliable)
                loop_count = int(voiceover_duration / bg_analysis["duration"]) + 1
                logger.info(f"Video too short, will loop {loop_count} times")
                input_options = ["-stream_loop", str(loop_count)]
            else:
                input_options = []
            
            # Build FFmpeg command for video processing
            video_cmd = [
                "ffmpeg", "-y",
                *input_options,
                "-i", background_video,
                "-vf", video_filter,
                "-c:v", encoder,
                "-preset", "fast" if "nvenc" in encoder else "medium",
                "-crf", str(preset["crf"]),
                "-r", str(preset["fps"]),
                "-t", str(voiceover_duration + 1),  # Add 1 second buffer
                "-an",  # Remove audio
                str(temp_video)
            ]
            
            # Add GPU-specific options
            if "nvenc" in encoder:
                video_cmd.extend(["-gpu", "0", "-rc", "vbr"])
            
            result = subprocess.run(video_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"Video processing failed: {result.stderr}")
            
            # Step 2: Create subtitle file
            logger.info("Generating dynamic subtitles...")
            subtitle_chunks = self.create_dynamic_subtitles(script, niche, voiceover_duration)
            self._create_ass_subtitles(subtitle_chunks, temp_subtitles, niche)
            
            # Step 3: Combine video, audio, and subtitles
            logger.info("Combining video, audio, and subtitles...")
            
            # For Windows FFmpeg, use subtitles filter with proper path escaping
            # Path format: D\:/path/to/file.ass (forward slashes, escaped colon)
            subtitle_path_str = str(temp_subtitles.absolute())
            subtitle_path_str = subtitle_path_str.replace('\\', '/')
            subtitle_path_str = subtitle_path_str.replace(':', '\\:')
            
            logger.info(f"Subtitle path for FFmpeg: {subtitle_path_str}")
            
            final_cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_video),
                "-i", voiceover_audio,
                "-vf", f"subtitles='{subtitle_path_str}'",
                "-c:v", encoder,
                "-c:a", "aac",
                "-b:a", "128k",
                "-preset", "fast" if "nvenc" in encoder else "medium",
                "-movflags", "+faststart",
                output_path
            ]
            
            result = subprocess.run(final_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"Final video creation failed: {result.stderr}")
            
            # Verify output
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                raise Exception("Output video is invalid or too small")
            
            build_time = time.time() - start_time
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            logger.info(f"GPU video build completed in {build_time:.1f}s, size: {file_size:.1f}MB")
            performance_monitor.record_video_generation(build_time, True, niche)
            
            return output_path
            
        except Exception as e:
            build_time = time.time() - start_time
            performance_monitor.record_video_generation(build_time, False, niche)
            logger.error(f"GPU video build failed after {build_time:.1f}s: {e}")
            raise
        
        finally:
            # Cleanup temporary files
            for temp_file in [temp_video, temp_subtitles]:
                if temp_file.exists():
                    temp_file.unlink()
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except Exception:
            # Fallback to MoviePy
            with AudioFileClip(audio_path) as audio:
                return audio.duration
    
    def _create_ass_subtitles(self, subtitle_chunks: List[Dict], output_path: Path, niche: str):
        """Create ASS subtitle file with advanced styling."""
        
        # ASS file header with styling
        style = self.subtitle_styles.get(niche, self.subtitle_styles["motivation"])
        
        ass_content = f"""[Script Info]
Title: OneClick Reels Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style['font']},{style['fontsize']},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,{style['stroke_width']},0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Add subtitle events
        for chunk in subtitle_chunks:
            start_time = self._seconds_to_ass_time(chunk["start"])
            end_time = self._seconds_to_ass_time(chunk["end"])
            text = chunk["text"].replace("\n", "\\N")
            
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format (H:MM:SS.CC)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    @timed_operation("video_optimization")
    def optimize_for_platform(self, video_path: str, platform: str) -> str:
        """Optimize video for specific platform requirements."""
        
        platform_specs = {
            "youtube_shorts": {"max_duration": 60, "aspect_ratio": "9:16", "max_size_mb": 100},
            "instagram_reels": {"max_duration": 90, "aspect_ratio": "9:16", "max_size_mb": 100},
            "tiktok": {"max_duration": 180, "aspect_ratio": "9:16", "max_size_mb": 287},
            "facebook_reels": {"max_duration": 60, "aspect_ratio": "9:16", "max_size_mb": 100}
        }
        
        specs = platform_specs.get(platform, platform_specs["youtube_shorts"])
        
        # Check if optimization is needed
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        if file_size_mb <= specs["max_size_mb"]:
            logger.info(f"Video already optimized for {platform}")
            return video_path
        
        # Create optimized version
        optimized_path = video_path.replace(".mp4", f"_{platform}.mp4")
        
        # Calculate target bitrate to meet size requirements
        duration = self._get_video_duration(video_path)
        target_bitrate = int((specs["max_size_mb"] * 8 * 1024) / duration * 0.9)  # 90% of max for safety
        
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-b:v", f"{target_bitrate}k",
            "-maxrate", f"{target_bitrate * 1.2}k",
            "-bufsize", f"{target_bitrate * 2}k",
            "-c:a", "aac",
            "-b:a", "96k",
            optimized_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                raise Exception(f"Platform optimization failed: {result.stderr}")
            
            new_size_mb = os.path.getsize(optimized_path) / (1024 * 1024)
            logger.info(f"Optimized for {platform}: {file_size_mb:.1f}MB → {new_size_mb:.1f}MB")
            
            return optimized_path
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return video_path  # Return original if optimization fails
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except Exception:
            with VideoFileClip(video_path) as clip:
                return clip.duration

    def add_audio_to_video(self, video_path: str, audio_path: str, output_path: str, mix: bool = False):
        """Add or mix audio to the video."""
        try:
            # Check duration
            video_duration = self._get_video_duration(video_path)
            audio_duration = self._get_audio_duration(audio_path)
            
            # Loop audio if shorter
            if audio_duration < video_duration:
                stream_loop = int(video_duration / audio_duration) + 1
                audio_input_opts = ["-stream_loop", str(stream_loop)]
            else:
                audio_input_opts = []
                
            cmd = ["ffmpeg", "-y", "-i", video_path]
            cmd.extend(audio_input_opts)
            cmd.extend(["-i", audio_path])
            
            if mix:
                # Merge original audio (0:a) and new audio (1:a)
                # Keep video (0:v)
                # Adjust volumes: original 1.0, new 0.6 (background)
                cmd.extend([
                    "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k"
                ])
            else:
                # Replace audio: map video from 0, audio from 1
                cmd.extend([
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest" # Stop when shortest stream ends (usually video)
                ])
            
            cmd.append(output_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"FFmpeg failed: {result.stderr}")
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                 raise Exception("Output video is invalid or too small")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Add audio failed: {e}")
            raise e

# Global advanced video builder instance
advanced_video_builder = AdvancedVideoBuilder()