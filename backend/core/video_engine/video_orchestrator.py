import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Engines
from backend.core.audio_engine.kokoro_engine import kokoro_engine
from backend.core.video_engine.advanced_video_builder import AdvancedVideoBuilder
from backend.core.video_engine.pexels_downloader import get_video_for_keyword
from backend.core.audio_engine.music_finder import music_finder

logger = logging.getLogger(__name__)

class VideoOrchestrator:
    """
    Director class that orchestrates the entire video creation process:
    Script -> Voiceover -> Visuals -> Music -> Final Video
    """
    
    def __init__(self):
        self.video_builder = AdvancedVideoBuilder()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    async def generate_video_from_script(
        self, 
        script: str, 
        voice_id: str = "af_heart",
        theme: str = "nature", 
        music_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a full video from a text script.
        """
        logger.info(f"🎬 Starting video generation for theme: {theme}")
        
        try:
            timestamp = int(time.time())
            
            # 1. Generate Voiceover (Kokoro TTS)
            logger.info(f"🎙️ Generating voiceover with voice: {voice_id}")
            # Kokoro returns a relative URL like /output/tts/filename.wav
            # We need the absolute path for ffmpeg
            voice_relative_path = kokoro_engine.generate(script, voice=voice_id)
            voice_abs_path = os.path.abspath(voice_relative_path.lstrip("/"))
            
            if not os.path.exists(voice_abs_path):
                 # Try adding project root if path is relative
                voice_abs_path = os.path.join(os.getcwd(), voice_relative_path.lstrip("/"))
            
            if not os.path.exists(voice_abs_path):
                raise Exception(f"Voice file not found at {voice_abs_path}")
                
            voice_duration = self.video_builder._get_audio_duration(voice_abs_path)
            logger.info(f"[OK] Voiceover ready: {voice_duration:.2f}s")

            # 2. Find Background Video (Pexels)
            logger.info(f"Finding background video for: {theme}")
            bg_video_path = get_video_for_keyword(theme)
            
            if not bg_video_path:
                # Fallback to a default if available, or error
                logger.warning("No background video found, trying fallback 'abstract'...")
                bg_video_path = get_video_for_keyword("abstract")
                
            if not bg_video_path:
                raise Exception("Could not find any background video from Pexels")
                
            bg_abs_path = os.path.abspath(bg_video_path)

            # 3. Find Background Music (Optional)
            music_abs_path = None
            if music_prompt:
                logger.info(f"Finding music for: {music_prompt}")
                results = music_finder.search_music(music_prompt, limit=1)
                if results:
                    track = results[0]
                    dl_result = music_finder.download_music(track['id'])
                    if dl_result:
                        music_abs_path = dl_result['full_path']
                        logger.info(f"[OK] Music found: {track['title']}")

            # 4. Generate Subtitles
            logger.info("Generating subtitles...")
            # Use the simple word-timing estimation from AdvancedVideoBuilder for now
            # In V2, we can implement Whisper for accurate timestamps
            subtitles = self.video_builder.create_dynamic_subtitles(
                script=script, 
                niche="motivation", # Default style
                duration=voice_duration
            )
            
            # Create ASS subtitle file
            subtitle_path = self.output_dir / f"subs_{timestamp}.ass"
            self.video_builder._create_ass_subtitles(subtitles, subtitle_path, "motivation")

            # 5. Assemble Final Video
            logger.info("Assembling final video...")
            output_filename = f"final_reel_{timestamp}.mp4"
            output_path = self.output_dir / output_filename
            output_abs_path = os.path.abspath(output_path)
            
            final_video_path = self.video_builder.combine_components(
                video_path=bg_abs_path,
                audio_path=voice_abs_path,
                subtitle_path=str(subtitle_path),
                music_path=music_abs_path,
                output_path=output_abs_path,
                target_duration=voice_duration
            )
            
            return {
                "success": True,
                "video_url": f"/output/{output_filename}",
                "video_path": str(final_video_path),
                "duration": voice_duration,
                "components": {
                    "voice": voice_id,
                    "bg_video": theme,
                    "music": music_prompt or "None"
                }
            }

        except Exception as e:
            logger.error(f"[ERROR] Video generation failed: {e}")
            raise e

# Singleton
video_orchestrator = VideoOrchestrator()
