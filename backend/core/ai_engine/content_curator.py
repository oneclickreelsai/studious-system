"""
Meta AI Content Curator
Finds and curates viral Meta AI content for YouTube Shorts.

Strategy:
1. Maintain list of quality Meta AI creators
2. Use AI to generate trending prompts
3. Score and select best content for upload
"""
import os
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from dotenv import load_dotenv
load_dotenv("config.env")

logger = logging.getLogger(__name__)

# Curated list of Meta AI creators with good content
# Format: {"username": "content_type"}
CURATED_CREATORS = {
    "rajendra.dethe.67": "bollywood_music",
    # Add more creators as you find them
}

# Content categories and their viral potential
CONTENT_CATEGORIES = [
    {"name": "funny", "weight": 25, "keywords": ["funny", "comedy", "meme", "dad", "relatable"]},
    {"name": "indian_comedy", "weight": 30, "keywords": ["indian", "desi", "comedy", "funny", "bollywood", "drama"]},
    {"name": "music", "weight": 20, "keywords": ["music", "song", "dance", "bollywood", "beats"]},
    {"name": "artistic", "weight": 15, "keywords": ["art", "beautiful", "stunning", "cinematic"]},
    {"name": "nature", "weight": 5, "keywords": ["nature", "animal", "wildlife", "ocean"]},
    {"name": "motivational", "weight": 5, "keywords": ["motivation", "success", "inspire"]},
]

# Cache file for tracking uploaded content
CACHE_FILE = "cache/uploaded_content.json"


def get_random_creator_url() -> Optional[str]:
    """Get a random post URL from curated creators."""
    if not CURATED_CREATORS:
        return None
    
    username = random.choice(list(CURATED_CREATORS.keys()))
    # Return profile URL - we'll need to scrape for specific posts
    return f"https://www.meta.ai/@{username}"


def get_trending_prompt(category: str = None) -> Dict:
    """
    Get a trending prompt idea using AI.
    Returns prompt + metadata for creating content on Meta AI.
    """
    from backend.core.ai_engine.meta_ai_discovery import search_trending_meta_ai_content
    
    if not category:
        # Weighted random selection
        total_weight = sum(c["weight"] for c in CONTENT_CATEGORIES)
        r = random.randint(1, total_weight)
        cumulative = 0
        for cat in CONTENT_CATEGORIES:
            cumulative += cat["weight"]
            if r <= cumulative:
                category = cat["name"]
                break
    
    ideas = search_trending_meta_ai_content(category)
    if ideas:
        idea = random.choice(ideas)
        idea["category"] = category
        return idea
    
    return {
        "prompt": "A cinematic, visually stunning scene that captures emotion and wonder",
        "category": category or "artistic",
        "viral_reason": "Visual appeal",
        "hashtags": ["ai", "animation", "viral"]
    }


def load_upload_history() -> List[str]:
    """Load list of already uploaded content (to avoid duplicates)."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []


def save_upload_history(history: List[str]):
    """Save upload history."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(history[-100:], f)  # Keep last 100


def mark_as_uploaded(url_or_prompt: str):
    """Mark content as uploaded to avoid duplicates."""
    history = load_upload_history()
    if url_or_prompt not in history:
        history.append(url_or_prompt)
        save_upload_history(history)


def is_already_uploaded(url_or_prompt: str) -> bool:
    """Check if content was already uploaded."""
    history = load_upload_history()
    return url_or_prompt in history


def curate_content_for_upload(count: int = 1) -> List[Dict]:
    """
    Curate content ideas for upload.
    Returns list of content to create/download and upload.
    """
    content_list = []
    
    for _ in range(count):
        # Get trending prompt idea
        idea = get_trending_prompt()
        
        # Skip if already uploaded
        if is_already_uploaded(idea["prompt"][:50]):
            continue
        
        content_list.append({
            "type": "generate",  # Need to generate on Meta AI
            "prompt": idea["prompt"],
            "category": idea.get("category", "viral"),
            "hashtags": idea.get("hashtags", []),
            "viral_reason": idea.get("viral_reason", ""),
        })
    
    return content_list


def auto_upload_pipeline(upload_youtube: bool = True, upload_facebook: bool = False) -> Dict:
    """
    Full automated pipeline:
    1. Get trending content idea
    2. Generate on Meta AI (manual step - returns prompt)
    3. Or download from curated creator
    4. Analyze and generate metadata
    5. Upload to platforms
    """
    from backend.core.ai_engine.meta_ai_discovery import generate_viral_prompt
    
    # Get content idea
    idea = get_trending_prompt()
    
    result = {
        "step": "content_ready",
        "prompt": idea["prompt"],
        "category": idea.get("category"),
        "hashtags": idea.get("hashtags", []),
        "instructions": f"""
To complete the pipeline:

1. Go to https://www.meta.ai/
2. Enter this prompt:
   {idea['prompt']}
3. Wait for video generation
4. Copy the post URL
5. Run: python cli/meta_pipeline.py <URL> --upload

Or use API:
POST /api/meta-to-youtube
{{"url": "<meta_ai_post_url>"}}
"""
    }
    
    return result


def get_daily_content_plan(count: int = 3) -> List[Dict]:
    """
    Generate a daily content plan with varied categories.
    """
    plan = []
    used_categories = []
    
    for i in range(count):
        # Try to vary categories
        available = [c for c in CONTENT_CATEGORIES if c["name"] not in used_categories]
        if not available:
            available = CONTENT_CATEGORIES
        
        # Weighted selection
        total = sum(c["weight"] for c in available)
        r = random.randint(1, total)
        cumulative = 0
        selected_cat = available[0]["name"]
        for cat in available:
            cumulative += cat["weight"]
            if r <= cumulative:
                selected_cat = cat["name"]
                break
        
        used_categories.append(selected_cat)
        idea = get_trending_prompt(selected_cat)
        
        plan.append({
            "slot": i + 1,
            "category": selected_cat,
            "prompt": idea["prompt"],
            "hashtags": idea.get("hashtags", []),
            "best_time": ["9:00 AM", "2:00 PM", "7:00 PM"][i % 3]  # Suggested post times
        })
    
    return plan


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    
    print("=" * 60)
    print("META AI CONTENT CURATOR")
    print("=" * 60)
    
    print("\n[Daily Content Plan]")
    plan = get_daily_content_plan(3)
    for item in plan:
        print(f"\nSlot {item['slot']} ({item['best_time']}) - {item['category'].upper()}")
        print(f"  Prompt: {item['prompt'][:80]}...")
        print(f"  Tags: {', '.join(item['hashtags'][:5])}")
    
    print("\n" + "=" * 60)
    print("To use a prompt:")
    print("1. Go to meta.ai and generate video with the prompt")
    print("2. Copy the post URL")
    print("3. Run: python cli/meta_pipeline.py <URL> --upload")
    print("=" * 60)
