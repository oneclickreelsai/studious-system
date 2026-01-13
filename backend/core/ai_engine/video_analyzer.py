"""
Video Content Analyzer
Extracts frames from video and uses AI to describe the content.
"""
import os
import base64
import logging
import subprocess
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv("config.env")
logger = logging.getLogger(__name__)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def find_ffmpeg():
    import shutil
    import glob
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    winget = glob.glob(os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\*ffmpeg*\*\bin\ffmpeg.exe"))
    return winget[0] if winget else None

FFMPEG_PATH = find_ffmpeg()

def extract_frame(video_path: str, output_path: str, time_sec: float = 1.0) -> bool:
    """Extract a single frame from video at specified time."""
    if not FFMPEG_PATH:
        return False
    try:
        cmd = [FFMPEG_PATH, '-y', '-ss', str(time_sec), '-i', video_path, 
               '-vframes', '1', '-q:v', '2', output_path]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0 and os.path.exists(output_path)
    except:
        return False

def extract_multiple_frames(video_path: str, output_dir: str, count: int = 3) -> List[str]:
    """Extract multiple frames from video at different timestamps."""
    if not FFMPEG_PATH:
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    frames = []
    
    # Get video duration
    try:
        ffprobe = FFMPEG_PATH.replace('ffmpeg', 'ffprobe')
        cmd = [ffprobe, '-v', 'error', '-show_entries', 'format=duration', 
               '-of', 'csv=p=0', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        duration = float(result.stdout.strip())
    except:
        duration = 10.0
    
    # Extract frames at different points
    times = [duration * i / (count + 1) for i in range(1, count + 1)]
    
    for i, t in enumerate(times):
        frame_path = os.path.join(output_dir, f"frame_{i}.jpg")
        if extract_frame(video_path, frame_path, t):
            frames.append(frame_path)
    
    return frames

def analyze_video_content(video_path: str) -> Dict:
    """
    Analyze video content using AI vision.
    Returns description of what's in the video.
    """
    # Extract frames
    temp_dir = os.path.join(os.path.dirname(video_path), "analysis_frames")
    frames = extract_multiple_frames(video_path, temp_dir, count=3)
    
    if not frames:
        logger.error("Could not extract frames from video")
        return {"description": "", "objects": [], "scene": ""}
    
    result = {"description": "", "visible_text": "", "style": "animation", "mood": ""}
    
    # Try OpenAI Vision first
    if OPENAI_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_KEY)
            
            # Encode frames as base64
            images = []
            for frame_path in frames[:2]:  # Use max 2 frames to save tokens
                with open(frame_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                    images.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                    })
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Analyze these video frames and describe:
1. What is happening in the video (main action/scene)
2. Any text/captions visible
3. Style (animation, realistic, cartoon, etc.)
4. Mood/tone

Be concise. Return JSON: {"description": "...", "visible_text": "...", "style": "...", "mood": "..."}"""},
                        *images
                    ]
                }],
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON
            import json
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content)
            logger.info(f"Video analysis: {result.get('description', '')[:100]}")
            
        except Exception as e:
            logger.warning(f"OpenAI vision error: {e}")
            # Try OCR fallback
            result = _analyze_with_ocr(frames)
    else:
        # No OpenAI, try OCR
        result = _analyze_with_ocr(frames)
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result

def _analyze_with_ocr(frames: List[str]) -> Dict:
    """Fallback: Extract text from frames using Tesseract OCR."""
    result = {"description": "", "visible_text": "", "style": "animation", "mood": ""}
    
    # Try to use pytesseract if available
    try:
        import pytesseract
        from PIL import Image
        
        # Set Tesseract path for Windows
        if os.name == 'nt':
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
            ]
            for tesseract_path in tesseract_paths:
                if os.path.exists(tesseract_path):
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    logger.info(f"Tesseract found: {tesseract_path}")
                    break
            else:
                logger.warning("Tesseract not found in common paths")
                return result
        
        all_text = []
        for frame_path in frames:
            try:
                img = Image.open(frame_path)
                text = pytesseract.image_to_string(img)
                if text.strip():
                    # Clean up OCR text
                    clean_text = " ".join(text.strip().split())
                    if len(clean_text) > 5:  # Ignore very short text
                        all_text.append(clean_text)
            except Exception as e:
                logger.warning(f"OCR error on frame {frame_path}: {e}")
                continue
        
        if all_text:
            result["visible_text"] = " | ".join(all_text)[:300]
            result["description"] = f"Video with text: {result['visible_text'][:100]}"
            logger.info(f"OCR extracted: {result['visible_text'][:80]}")
        else:
            logger.info("OCR found no text in frames")
    except ImportError:
        logger.warning("pytesseract not available for OCR")
    except Exception as e:
        logger.warning(f"OCR error: {e}")
    
    return result


def generate_metadata_from_video(video_path: str, original_prompt: str = "") -> Dict:
    """
    Generate metadata by analyzing actual video content.
    Combines video analysis with original prompt for best results.
    """
    from backend.core.ai_engine.video_metadata import _generate_with_perplexity
    
    # Analyze video content
    analysis = analyze_video_content(video_path)
    
    video_description = analysis.get("description", "")
    visible_text = analysis.get("visible_text", "")
    style = analysis.get("style", "animation")
    
    # If video has visible text (captions), use that as primary content
    if visible_text and len(visible_text) > 10:
        content_prompt = f"{visible_text}. {video_description}"
        logger.info(f"Using visible text for metadata: {visible_text[:50]}")
    elif video_description:
        content_prompt = video_description
        logger.info(f"Using video description for metadata: {video_description[:50]}")
    else:
        content_prompt = original_prompt
        logger.info("Using original prompt for metadata (no video analysis)")
    
    # Determine video type from analysis
    video_type = "ai_animation"
    desc_lower = (video_description + " " + visible_text).lower()
    if any(w in desc_lower for w in ["dance", "dancing"]):
        video_type = "dance"
    elif any(w in desc_lower for w in ["music", "song", "singing"]):
        video_type = "music"
    elif any(w in desc_lower for w in ["funny", "comedy", "joke", "meme", "dad", "mom"]):
        video_type = "comedy"
    elif any(w in desc_lower for w in ["nature", "animal", "wildlife"]):
        video_type = "nature"
    
    # Generate metadata based on actual content
    metadata = _generate_with_perplexity(content_prompt, video_type)
    
    # Add analysis info
    metadata["video_analysis"] = analysis
    metadata["content_source"] = "video_analysis" if video_description else "original_prompt"
    
    return metadata


def verify_title_matches_content(title: str, video_path: str) -> Dict:
    """
    Verify if the title matches the actual video content.
    Returns match score and suggested title if mismatch.
    """
    analysis = analyze_video_content(video_path)
    
    if not analysis.get("description"):
        return {"matches": True, "confidence": 0, "reason": "Could not analyze video"}
    
    video_desc = analysis.get("description", "").lower()
    visible_text = analysis.get("visible_text", "").lower()
    title_lower = title.lower()
    
    # Check for keyword overlap
    title_words = set(title_lower.split())
    content_words = set((video_desc + " " + visible_text).split())
    
    overlap = title_words & content_words
    overlap_ratio = len(overlap) / max(len(title_words), 1)
    
    matches = overlap_ratio > 0.2 or any(w in video_desc for w in title_words if len(w) > 4)
    
    result = {
        "matches": matches,
        "confidence": overlap_ratio,
        "video_description": analysis.get("description"),
        "visible_text": analysis.get("visible_text"),
        "title_words": list(title_words),
        "content_words": list(content_words)[:20]
    }
    
    if not matches:
        # Generate better title from content
        from backend.core.ai_engine.video_metadata import _generate_with_perplexity
        content = visible_text if visible_text else video_desc
        new_meta = _generate_with_perplexity(content, "ai_animation")
        result["suggested_title"] = new_meta.get("title", "")
        result["suggested_description"] = new_meta.get("description", "")
    
    return result
