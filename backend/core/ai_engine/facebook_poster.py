"""
Facebook AI Text Poster Module
Generates engaging text posts using Perplexity and posts to Facebook Page.
"""

import os
import logging
from typing import Optional, Dict, List
from functools import wraps
import time
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load config from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

logger = logging.getLogger(__name__)

# Initialize Globals
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

def get_fb_credentials():
    """Get fresh FB credentials from env."""
    load_dotenv(PROJECT_ROOT / "config.env", override=True)
    page_id = os.getenv("FB_PAGE_ID")
    page_token = os.getenv("FB_ACCESS_TOKEN")
    logger.info(f"Loaded FB credentials - Page: {page_id}, Token: {page_token[:20] if page_token else 'None'}...")
    return page_id, page_token

def get_perplexity_client():
    """Get Perplexity client."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if api_key:
        return OpenAI(
            base_url="https://api.perplexity.ai",
            api_key=api_key,
            timeout=30.0
        )
    return None

PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

# Initialize Perplexity client
client = None
if PERPLEXITY_API_KEY:
    client = OpenAI(
        base_url="https://api.perplexity.ai",
        api_key=PERPLEXITY_API_KEY,
        timeout=30.0
    )

# Topic suggestions for different niches
TOPIC_SUGGESTIONS = {
    "trading": [
        "Latest NSE options trading strategies",
        "Angel One API tips for algo traders",
        "Nifty 50 volatility analysis",
        "Python automation for Indian markets",
        "Risk management for options traders",
    ],
    "tech": [
        "Latest AI developments this week",
        "Python programming tips and tricks",
        "Web development trends",
        "Cloud computing updates",
        "Cybersecurity best practices",
    ],
    "motivation": [
        "Morning motivation for entrepreneurs",
        "Productivity hacks for remote workers",
        "Success mindset tips",
        "Work-life balance strategies",
        "Goal setting techniques",
    ],
    "finance": [
        "Personal finance tips for millennials",
        "Investment strategies for beginners",
        "Cryptocurrency market analysis",
        "Passive income ideas",
        "Tax saving tips for India",
    ],
}


def retry_with_backoff(max_retries: int = 3, base_delay: int = 2):
    """Decorator for exponential backoff retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"All {max_retries} attempts failed: {e}")
                        raise
                    delay = base_delay ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
        return wrapper
    return decorator


def fetch_dynamic_image(query: str) -> Optional[Dict[str, str]]:
    """
    Fetch an image from Pexels based on query.
    Downloads to output/ directory.
    
    Returns:
        Dict with 'local_path' and 'filename' or None
    """
    if not PEXELS_API_KEY:
        logger.warning("Pexels API Key not configured")
        return None
        
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 1, "orientation": "landscape", "size": "medium"}
        
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("photos"):
                photo = data["photos"][0]
                image_url = photo["src"]["large"]
                
                # Download
                timestamp = int(time.time())
                sanitized_query = "".join([c for c in query if c.isalnum() or c in (' ', '_')]).rstrip().replace(" ", "_")
                filename = f"pexels_{sanitized_query}_{timestamp}.jpg"
                output_dir = PROJECT_ROOT / "output"
                os.makedirs(output_dir, exist_ok=True)
                local_path = output_dir / filename
                
                img_res = requests.get(image_url, stream=True, timeout=15)
                if img_res.status_code == 200:
                    with open(local_path, "wb") as f:
                        for chunk in img_res.iter_content(1024):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded dynamic image: {filename}")
                    return {
                        "local_path": str(local_path),
                        "filename": filename,
                        "url": f"http://localhost:8002/output/{filename}", # Approximate URL, adjusted in main
                        "credit": photo["photographer"]
                    }
        else:
            logger.error(f"Pexels API Error: {res.status_code} - {res.text}")
            
        return None
    except Exception as e:
        logger.error(f"Image fetch failed: {e}")
        return None



@retry_with_backoff(max_retries=3)
def generate_facebook_post(topic: str, niche: str = "general") -> Dict:
    """
    Generate an engaging Facebook post using Perplexity AI.
    
    Returns:
        Dict with 'success', 'content', 'error' keys
    """
    client = get_perplexity_client()
    if not client:
        return {"success": False, "content": "", "error": "Perplexity API not configured"}
    
    try:
        logger.info(f"Generating Facebook post for topic: {topic}")
        
        # Customize prompt based on niche
        niche_context = {
            "trading": "targeting Indian retail traders and algo developers using platforms like Angel One and Zerodha",
            "tech": "targeting tech enthusiasts and developers",
            "motivation": "targeting entrepreneurs and professionals seeking inspiration",
            "finance": "targeting young professionals interested in personal finance",
            "general": "targeting a general social media audience",
        }
        
        context = niche_context.get(niche, niche_context["general"])
        
        response = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional social media manager {context}. "
                        "Create engaging, informative Facebook posts (150-200 words). "
                        "Requirements:\n"
                        "- Conversational tone with strategic emoji use (2-4 max)\n"
                        "- Include 1-2 specific facts/stats when available\n"
                        "- End with engaging CTA (question or call-to-action)\n"
                        "- Avoid overhyped language or financial advice\n"
                        "- Add relevant hashtags (3-5 max) at the end\n"
                        "FINALLY: Suggest a 3-5 word visual search query for a stock photo that matches this post. "
                        "Format the output as:\n"
                        "Content: [Post Content]\n"
                        "Visual Query: [Query]"
                    )
                },
                {"role": "user", "content": topic}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Parse Content and visual query
        content = raw_content
        visual_query = topic # Default to topic
        
        if "Visual Query:" in raw_content:
            parts = raw_content.split("Visual Query:")
            if len(parts) > 1:
                content = parts[0].replace("Content:", "").strip()
                visual_query = parts[1].strip()
        
        logger.info(f"Generated content. Visual Query: {visual_query}")
        
        # Fetch Image
        image_data = fetch_dynamic_image(visual_query)
        
        return {
            "success": True,
            "content": content,
            "image": image_data,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return {
            "success": False,
            "content": "",
            "error": str(e)
        }


def moderate_content(content: str) -> Dict:
    """Basic content moderation to avoid policy violations."""
    forbidden_terms = [
        "guaranteed returns", "risk-free", "get rich quick",
        "buy now", "pump", "dump", "insider tip"
    ]
    
    content_lower = content.lower()
    
    for term in forbidden_terms:
        if term in content_lower:
            return {"safe": False, "reason": f"Contains forbidden term: {term}"}
    
    if len(content) < 50:
        return {"safe": False, "reason": "Content too short"}
    
    if len(content) > 3000:
        return {"safe": False, "reason": "Content too long"}
    
    return {"safe": True, "reason": "Approved"}


@retry_with_backoff(max_retries=3)
def post_to_facebook(message: str) -> Dict:
    """
    Post message to Facebook Page.
    
    Returns:
        Dict with 'success', 'post_id', 'post_url', 'error' keys
    """
    # Get fresh credentials (not stale module-level vars)
    PAGE_ID, PAGE_ACCESS_TOKEN = get_fb_credentials()
    
    if not PAGE_ID or not PAGE_ACCESS_TOKEN:
        return {
            "success": False,
            "post_id": None,
            "post_url": None,
            "error": "Facebook credentials not configured"
        }
    
    # Moderate first
    moderation = moderate_content(message)
    if not moderation["safe"]:
        return {
            "success": False,
            "post_id": None,
            "post_url": None,
            "error": f"Moderation failed: {moderation['reason']}"
        }
    
    try:
        # Exchange User Token for Page Token (required for new Pages experience)
        token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={PAGE_ACCESS_TOKEN}"
        token_res = requests.get(token_url, timeout=10)
        if token_res.status_code == 200 and "access_token" in token_res.json():
            page_token = token_res.json()["access_token"]
            logger.info("Exchanged User Token for Page Token")
        else:
            page_token = PAGE_ACCESS_TOKEN
            logger.warning(f"Could not get Page Token, using User Token: {token_res.text[:100]}")
        
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        payload = {
            "message": message,
            "access_token": page_token  # Use Page Token!
        }
        
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        
        post_data = response.json()
        post_id = post_data.get('id')
        
        logger.info(f"Post published: {post_id}")
        
        return {
            "success": True,
            "post_id": post_id,
            "post_url": f"https://facebook.com/{post_id}",
            "error": None
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return {
            "success": False,
            "post_id": None,
            "post_url": None,
            "error": error_msg
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "post_id": None,
            "post_url": None,
            "error": str(e)
        }


@retry_with_backoff(max_retries=3)
def post_photo_to_facebook(image_path: str, message: str) -> Dict:
    """
    Post a photo to Facebook Page.
    
    Returns:
        Dict with 'success', 'post_id', 'post_url', 'error' keys
    """
    PAGE_ID, PAGE_ACCESS_TOKEN = get_fb_credentials()
    
    if not PAGE_ID or not PAGE_ACCESS_TOKEN:
        return {
            "success": False, 
            "error": "Facebook credentials not configured"
        }

    # Verify file exists
    if not os.path.exists(image_path):
        return {
            "success": False, 
            "error": f"Image file not found: {image_path}"
        }

    try:
        # Exchange Token
        token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={PAGE_ACCESS_TOKEN}"
        token_res = requests.get(token_url, timeout=10)
        if token_res.status_code == 200 and "access_token" in token_res.json():
            page_token = token_res.json()["access_token"]
        else:
            page_token = PAGE_ACCESS_TOKEN
        
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
        
        # Upload using multipart/form-data
        with open(image_path, "rb") as image_file:
            payload = {
                "message": message,
                "access_token": page_token
            }
            files = {
                "source": image_file
            }
            
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            
            post_data = response.json()
            post_id = post_data.get('post_id') # /photos returns 'post_id' or 'id'
            if not post_id:
                post_id = post_data.get('id')
            
            logger.info(f"Photo published: {post_id}")
            
            return {
                "success": True,
                "post_id": post_id,
                "post_url": f"https://facebook.com/{post_id}",
                "error": None
            }

    except Exception as e:
        logger.error(f"Photo upload failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

    """Get Facebook Page statistics."""
    PAGE_ID, PAGE_ACCESS_TOKEN = get_fb_credentials()
    
    if not PAGE_ID or not PAGE_ACCESS_TOKEN:
        return {"success": False, "error": "Facebook credentials not configured"}
    
    try:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}"
        params = {
            "fields": "name,fan_count,followers_count,talking_about_count,link,category",
            "access_token": PAGE_ACCESS_TOKEN
        }
        
        response = requests.get(url, params=params, timeout=10)
        logger.info(f"Page stats response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "name": data.get("name", "Unknown"),
                "likes": data.get("fan_count", 0),
                "followers": data.get("followers_count", 0),
                "talking_about": data.get("talking_about_count", 0),
                "category": data.get("category", ""),
                "link": data.get("link", ""),
            }
        else:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                return {"success": False, "error": f"{error_message}"}
            except:
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Page stats error: {e}")
        return {"success": False, "error": str(e)}


def get_recent_posts(limit: int = 5) -> List[Dict]:
    """Get recent posts from Facebook Page."""
    PAGE_ID, PAGE_ACCESS_TOKEN = get_fb_credentials()
    
    if not PAGE_ID or not PAGE_ACCESS_TOKEN:
        return []
    
    try:
        # Exchange User Token for Page Token
        token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={PAGE_ACCESS_TOKEN}"
        token_res = requests.get(token_url, timeout=10)
        if token_res.status_code == 200 and "access_token" in token_res.json():
            page_token = token_res.json()["access_token"]
        else:
            page_token = PAGE_ACCESS_TOKEN
        
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/posts"
        params = {
            "fields": "id,message,created_time,reactions.summary(true),comments.summary(true),shares",
            "limit": limit,
            "access_token": page_token  # Use Page Token!
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            posts = []
            for post in data:
                posts.append({
                    "id": post.get("id"),
                    "message": post.get("message", "")[:100] + "..." if len(post.get("message", "")) > 100 else post.get("message", "[No text]"),
                    "created_time": post.get("created_time"),
                    "reactions": post.get("reactions", {}).get("summary", {}).get("total_count", 0),
                    "comments": post.get("comments", {}).get("summary", {}).get("total_count", 0),
                    "shares": post.get("shares", {}).get("count", 0),
                })
            logger.info(f"Fetched {len(posts)} recent posts")
            return posts
        else:
            logger.error(f"Failed to fetch posts: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching recent posts: {e}")
        return []


def get_topic_suggestions(niche: str = "general") -> List[str]:
    """Get topic suggestions for a given niche."""
    return TOPIC_SUGGESTIONS.get(niche, TOPIC_SUGGESTIONS.get("tech", []))
