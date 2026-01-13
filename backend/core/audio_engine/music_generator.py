
import os
import sys
import logging
import torch
import torchaudio
import typing as tp
import time
from pathlib import Path

# Add the local audiocraft folder to sys.path if it exists
# This allows using the cloned repo without full pip installation if dependencies are met
AUDIOCRAFT_PATH = Path(r"d:\oneclick_reels_ai\audiocraft")
if AUDIOCRAFT_PATH.exists():
    sys.path.append(str(AUDIOCRAFT_PATH))

# Try importing audiocraft. If it fails, we handle it gracefully.
try:
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    HAS_AUDIOCRAFT = True
except ImportError as e:
    logging.warning(f"AudioCraft not found or dependencies missing: {e}")
    HAS_AUDIOCRAFT = False
    MusicGen = None  # type: ignore

class MusicGenerator:
    def __init__(self, model_size: str = 'facebook/musicgen-small'):
        self.model_size = model_size
        self.model = None
        self.output_dir = Path("assets/generated_music")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def load_model(self):
        """Lazy load the model only when needed."""
        if not HAS_AUDIOCRAFT:
            raise ImportError("AudioCraft library is not installed. Please install it to use this feature.")
        
        if self.model is None:
            logging.info(f"Loading MusicGen model: {self.model_size} on {self.device}...")
            try:
                self.model = MusicGen.get_pretrained(self.model_size, device=self.device)
                self.model.set_generation_params(duration=15) # Default, can be overridden
                logging.info("MusicGen model loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load MusicGen model: {e}")
                raise e

    def unload_model(self):
        """Unload model to free VRAM."""
        if self.model is not None:
            logging.info("Unloading MusicGen model to free VRAM...")
            del self.model
            self.model = None
            if self.device == 'cuda':
                torch.cuda.empty_cache()

    def generate(self, prompt: str, duration: int = 15) -> str:
        """
        Generate music from a text prompt.
        Returns the relative path to the generated file.
        """
        if not HAS_AUDIOCRAFT:
             raise ImportError("AudioCraft is missing. Please run: pip install -r audiocraft/requirements.txt")

        self.load_model()
        
        logging.info(f"Generating music for prompt: '{prompt}' ({duration}s)...")
        self.model.set_generation_params(duration=duration)
        
        # Generate
        start_time = time.time()
        wav_tensor = self.model.generate([prompt], progress=True)
        
        # Save to file
        filename = f"gen_{int(time.time())}_{prompt[:10].replace(' ', '_')}"
        # audio_write adds .wav automatically
        filepath = self.output_dir / filename
        
        # The tensor is [Batch, Channel, Time]. We have batch=1.
        # audio_write expects [Channel, Time]
        audio_write(
            str(filepath), 
            wav_tensor[0].cpu(), 
            self.model.sample_rate, 
            strategy="loudness", 
            loudness_headroom_db=16
        )
        
        elapsed = time.time() - start_time
        logging.info(f"Generation complete in {elapsed:.2f}s. Saved to {filepath}.wav")
        
        # Return local web-accessible path (e.g., /assets/generated_music/...)
        return f"/assets/generated_music/{filename}.wav"

# Singleton instance
music_gen = MusicGenerator()
