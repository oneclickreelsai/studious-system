"""
AI-powered video metadata generator for YouTube Shorts.
Generates optimized titles, descriptions, and tags.
"""
import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv("config.env")
logger = logging.getLogger(__name__)

# Try OpenAI first, then Perplexity
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_KEY = os.getenv("PERPLEXITY_API_KEY")

def generate_video_metadata(prompt: str, video_type: str = "ai_animation") -> Dict:
    """
    Generate optimized YouTube metadata from video prompt/description.
    
    Args:
        prompt: The original prompt or description of the video
        video_type: Type of video (ai_animation, music, dance, etc.)
    
    Returns:
        dict with title, description, tags
    """
    # Try Perplexity first (usually has quota and faster), then OpenAI
    if PERPLEXITY_KEY:
        result = _generate_with_perplexity(prompt, video_type)
        if result.get("title") and len(result.get("title", "")) > 10:
            return result
    
    # Fallback to OpenAI if Perplexity fails
    if OPENAI_KEY:
        try:
            return _generate_with_openai(prompt, video_type)
        except Exception as e:
            logger.warning(f"OpenAI fallback failed: {e}")
    
    return _generate_fallback(prompt, video_type)

def _generate_with_openai(prompt: str, video_type: str) -> Dict:
    """Generate metadata using OpenAI."""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_KEY)
        
        system_prompt = """You are a VIRAL YouTube Shorts expert. Generate EXPLOSIVE metadata!

TITLE RULES:
- Max 70 chars
- Start with 2-3 ATTENTION-GRABBING emojis
- Use power words: INSANE, EPIC, MIND-BLOWING, CRAZY, UNBELIEVABLE, WOW, WAIT FOR IT
- Make it clickable and curiosity-driven
- Examples: "🤯😱 This AI Video Will BLOW Your Mind!", "🔥💯 INSANE AI Animation!"

DESCRIPTION RULES:
- Start with emojis
- 2-3 short punchy sentences
- Include call-to-action with emojis
- Use trending keywords
- Example: "🎬 This AI masterpiece is INSANE! 🤯\n\n✨ Like & Subscribe for VIRAL content! 🔥\n💯 Turn on notifications! 🔔"

EMOJI PALETTE: 🔥💯✨🎬🎥🤯😱🎨🎭🎪🌟💫⚡🚀👀💥🎯🏆😍🤩🙌👏💪🌈🎉🎊

Return JSON: {"title": "...", "description": "...", "tags": ["tag1", "tag2", ...]}"""

        user_prompt = f"""Generate EXPLOSIVE VIRAL YouTube Shorts metadata for:

Content: {prompt}
Category: {video_type}

Make it IRRESISTIBLE! Return JSON only."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        # Parse JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        data = json.loads(content)
        return {
            "title": data.get("title", prompt[:50]),
            "description": data.get("description", f"AI Generated {video_type}"),
            "tags": data.get("tags", ["shorts", "ai", "viral"])
        }
    except Exception as e:
        logger.error(f"OpenAI metadata error: {e}")
        return _generate_fallback(prompt, video_type)


def _generate_with_perplexity(prompt: str, video_type: str) -> Dict:
    """Generate metadata using Perplexity AI."""
    try:
        import httpx
        
        system_prompt = """You are a VIRAL YouTube Shorts expert. Generate EXPLOSIVE metadata with emojis!

TITLE RULES:
- Max 70 chars
- Start with 2-3 ATTENTION-GRABBING emojis
- Use power words: INSANE, EPIC, MIND-BLOWING, CRAZY, UNBELIEVABLE, WOW
- Make it clickable and curiosity-driven
- Examples: "🤯😱 This AI Video Will BLOW Your Mind!", "🔥💯 INSANE AI Animation You MUST See!"

DESCRIPTION RULES:
- Start with emojis
- 2-3 short punchy sentences
- Include call-to-action with emojis
- Use trending keywords
- Example: "🎬 This AI-generated masterpiece is INSANE! 🤯\n\n✨ Like & Subscribe for more VIRAL content! 🔥\n💯 Turn on notifications! 🔔"

EMOJI PALETTE: 🔥💯✨🎬🎥🤯😱🎨🎭🎪🌟💫⚡🚀👀💥🎯🏆😍🤩🙌👏💪🌈🎉🎊

Return JSON: {"title": "...", "description": "...", "tags": ["tag1", "tag2"]}"""

        user_prompt = f"Generate EXPLOSIVE VIRAL YouTube Shorts metadata for: {prompt}\n\nCategory: {video_type}\n\nMake it IRRESISTIBLE!"

        response = httpx.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            # Extract JSON from markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Find JSON object in text
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]
            
            data = json.loads(content)
            return {
                "title": data.get("title", prompt[:50])[:100],
                "description": data.get("description", f"AI Generated {video_type}"),
                "tags": data.get("tags", ["shorts", "ai", "viral"])[:15]
            }
    except json.JSONDecodeError as e:
        logger.error(f"Perplexity JSON parse error: {e}")
    except Exception as e:
        logger.error(f"Perplexity metadata error: {e}")
    
    return _generate_fallback(prompt, video_type)

def _generate_fallback(prompt: str, video_type: str) -> Dict:
    """Fallback metadata generation without AI - VIRAL VERSION."""
    # Clean up prompt for title
    title_base = prompt[:40].strip()
    if len(prompt) > 40:
        title_base = title_base.rsplit(' ', 1)[0]
    
    # Add VIRAL emojis and power words based on type
    type_config = {
        "ai_animation": {"emojis": "🤯✨", "power": "INSANE"},
        "funny": {"emojis": "😂🔥", "power": "HILARIOUS"},
        "dance": {"emojis": "💃🔥", "power": "EPIC"},
        "music": {"emojis": "🎵🔥", "power": "AMAZING"},
        "art": {"emojis": "🎨✨", "power": "STUNNING"},
        "nature": {"emojis": "🌿💫", "power": "BREATHTAKING"},
        "motivational": {"emojis": "💪🔥", "power": "POWERFUL"},
        "artistic": {"emojis": "🎭✨", "power": "MIND-BLOWING"}
    }
    config = type_config.get(video_type, {"emojis": "🔥✨", "power": "EPIC"})
    
    # Create viral title
    title = f"{config['emojis']} {config['power']} AI: {title_base}!"
    
    # Generate VIRAL description with emojis
    description = f"""🎬 {prompt[:80]}... 🤯

✨ This AI animation is {config['power']}! 
🔥 LIKE & SUBSCRIBE for more VIRAL content!
💯 Turn on notifications! 🔔
👀 Watch till the end!

#shorts #ai #animation #viral #trending #fyp"""

    # Generate tags based on prompt words
    words = prompt.lower().split()
    base_tags = ["shorts", "ai", "animation", "viral", "trending", "fyp", "reels", "aiart", "aianimation", "aiartwork", "aivideo"]
    prompt_tags = [w for w in words if len(w) > 3 and w.isalpha()][:6]
    tags = list(set(base_tags + prompt_tags))[:15]
    
    return {
        "title": title[:100],
        "description": description,
        "tags": tags
    }

def format_youtube_description(metadata: Dict) -> str:
    """Format metadata into YouTube description with hashtags and emojis."""
    desc = metadata.get("description", "")
    tags = metadata.get("tags", [])
    
    # Ensure description has emojis if not already present
    if not any(ord(c) > 127 for c in desc):  # No emojis detected
        desc = f"🎬 {desc}\n\n✨ AI Generated | 🔥 Like & Subscribe!"
    
    # Add hashtags at the end (top 8 tags for better visibility)
    hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in tags[:8]])
    
    return f"{desc}\n\n{hashtags}"
