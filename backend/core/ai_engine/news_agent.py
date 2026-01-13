
import os
import requests
import json
from datetime import datetime

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai"

def get_trending_news(category: str = "Technology") -> dict:
    """
    Fetches the latest trending news for a given category using Perplexity AI.
    Returns a dictionary with 'title', 'script', and 'hashtags'.
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY is not set in config.env")

    date_str = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""
    You are a viral news reporter for a 60-second YouTube Short / TikTok / Reel video.
    
    TASK:
    Find the most important and trending news story RIGHT NOW in the category: '{category}'.
    The date is {date_str}.
    
    OUTPUT FORMAT (JSON ONLY):
    {{
        "title": " Catchy Headline (Max 10 words)",
        "script": "The full spoken script for the video. Must be exciting, fast-paced, and under 140 words. Start with a hook!",
        "hashtags": "#tag1 #tag2 #tag3",
        "visual_keywords": "comma, separated, list, of, keywords, for, visuals"
    }}
    
    Do not include any other text, just the JSON.
    """

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a professional viral content scriptwriter."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # Clean up code blocks if present
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        
        return json.loads(content.strip())
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        # Fallback news if API fails
        return {
            "title": f"Latest {category} News",
            "script": f"Here is the latest update in {category}. New developments are happening fast. Stay tuned for more updates as this story unfolds. Follow for daily news!",
            "hashtags": f"#{category} #News #Update",
            "visual_keywords": f"{category}, news, breaking news"
        }

if __name__ == "__main__":
    # Test
    news = get_trending_news("Artificial Intelligence")
    print(json.dumps(news, indent=2))
