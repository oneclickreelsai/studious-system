import os
import torch
import soundfile as sf
from kokoro import KPipeline
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KokoroEngine:
    def __init__(self):
        self.pipeline = None
        self.output_dir = "output/tts"
        os.makedirs(self.output_dir, exist_ok=True)
        # Check for CUDA (User has RTX A2000)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Kokoro Engine initialized. Device: {self.device} (Model will lazy load)")

    def load_model(self):
        """Loads the Kokoro model deeply only when needed to save VRAM."""
        if self.pipeline is None:
            logger.info("Loading Kokoro-82M model... (This may download ~300MB on first run)")
            try:
                # 'a' (American English) is the default language code
                self.pipeline = KPipeline(lang_code='a', device=self.device) 
                logger.info("Kokoro model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Kokoro model: {e}")
                raise e

    def generate(self, text: str, voice: str = "af_heart", speed: float = 1.0) -> str:
        """
        Generates audio from text using Kokoro.
        Returns the path to the generated .wav file.
        """
        self.load_model()
        
        # Sanitize filename
        safe_text = "".join([c for c in text[:20] if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
        if not safe_text:
            safe_text = "audio"
        filename = f"{safe_text}_{voice}.wav"
        output_path = os.path.join(self.output_dir, filename)

        logger.info(f"Generating TTS for: '{text[:50]}...' using voice: {voice}")

        try:
            # Generate audio
            # pipeline(text, voice=voice, speed=speed) returns a generator
            generator = self.pipeline(text, voice=voice, speed=speed)
            
            # Combine all chunks (Kokoro processes text in chunks)
            all_audio = []
            for _, _, audio in generator:
                all_audio.append(audio)
            
            if not all_audio:
                raise ValueError("No audio generated.")
            
            # Concatenate if multiple chunks
            final_audio = torch.cat(all_audio, dim=0) if len(all_audio) > 1 else all_audio[0]

            # Save to file using soundfile
            # Kokoro usually outputs at 24000 Hz
            sf.write(output_path, final_audio.cpu().numpy(), 24000)
            
            logger.info(f"TTS saved to: {output_path}")
            return f"/output/tts/{filename}"
            
        except Exception as e:
            logger.error(f"Kokoro generation failed: {e}")
            raise e

    def get_available_voices(self):
        """Returns a list of available voices."""
        # Standard Kokoro voices
        return [
            {"id": "af_heart", "name": "Heart (Female)", "gender": "Female"},
            {"id": "af_bella", "name": "Bella (Female)", "gender": "Female"},
            {"id": "af_nicole", "name": "Nicole (Female)", "gender": "Female"},
            {"id": "af_sarah", "name": "Sarah (Female)", "gender": "Female"},
            {"id": "af_sky", "name": "Sky (Female)", "gender": "Female"},
            {"id": "am_adam", "name": "Adam (Male)", "gender": "Male"},
            {"id": "am_michael", "name": "Michael (Male)", "gender": "Male"},
            {"id": "am_eric", "name": "Eric (Male)", "gender": "Male"},
            {"id": "bf_emma", "name": "Emma (British Female)", "gender": "Female"},
            {"id": "bf_isabella", "name": "Isabella (British Female)", "gender": "Female"},
            {"id": "bm_george", "name": "George (British Male)", "gender": "Male"},
            {"id": "bm_lewis", "name": "Lewis (British Male)", "gender": "Male"},
        ]

# Singleton instance
kokoro_engine = KokoroEngine()
