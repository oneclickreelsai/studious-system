
import asyncio
import edge_tts
import os
import nest_asyncio

# Allow nested event loops (for running async code from within FastAPI)
try:
    nest_asyncio.apply()
except:
    pass

VOICE = "en-US-ChristopherNeural"  # Deep, professional male voice
COMEDY_VOICE = "en-IN-PrabhatNeural"  # Indian male voice for comedy
# specific options: en-US-AriaNeural, en-US-GuyNeural, en-US-JennyNeural
# Comedy options: en-IN-PrabhatNeural, en-IN-NeerjaNeural

async def _generate_audio(text, output_file, voice=None):
    selected_voice = voice or VOICE
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(output_file)

def generate_voiceover(text, output_file="output/voiceover.mp3", niche=None):
    """
    Generates a voiceover from text using Microsoft Edge TTS (High Quality, Free).
    Synchronous wrapper for async edge-tts library.
    For comedy niche, uses Indian accent voice.
    """
    try:
        if os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Use Indian voice for comedy
        voice = COMEDY_VOICE if niche == "comedy" else VOICE
        
        # Handle both standalone and nested event loop scenarios
        try:
            loop = asyncio.get_running_loop()
            # We're inside an event loop (e.g., FastAPI), use nest_asyncio
            loop.run_until_complete(_generate_audio(text, output_file, voice))
        except RuntimeError:
            # No running event loop, safe to use asyncio.run()
            asyncio.run(_generate_audio(text, output_file, voice))
        
        return output_file
    except Exception as e:
        print(f"[ERROR] Voiceover generation failed: {e}")
        return None

if __name__ == "__main__":
    # Test
    generate_voiceover("This is a test of the One Click Reels AI voiceover system.", "test_voice.mp3")
    print("Generated test_voice.mp3")
