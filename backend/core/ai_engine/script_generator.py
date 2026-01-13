import os
import logging
import requests
from openai import OpenAI
from dotenv import load_dotenv
from backend.utils.error_handler import retry_with_backoff, handle_api_error, RetryableError, ErrorType
from backend.utils.rate_limiter import rate_limit
from backend.utils.cache_manager import cached, get_cached_script, cache_script

load_dotenv("config.env")

logger = logging.getLogger(__name__)

# Perplexity (Primary)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")

# OpenAI (Fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = """
You are a viral short-form content writer.
You write punchy, emotional, high-retention scripts for 20–40 second reels.

CRITICAL RULES:
- No emojis
- No hashtags
- No labels like "Hook:", "Body:", "Closing:" 
- No markdown formatting (no **, no ##, no *)
- Just write the raw script text, line by line
- Simple English
- Strong hooks
"""

def _generate_with_perplexity(user_prompt: str) -> str:
    """Generate script using Perplexity API (Primary)."""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 500
    }
    
    response = requests.post(
        f"{PERPLEXITY_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")

def _generate_with_openai(user_prompt: str) -> str:
    """Generate script using OpenAI API (Fallback)."""
    if not openai_client:
        raise Exception("OpenAI API key not configured")
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.8,
        timeout=30
    )
    
    return response.choices[0].message.content.strip()

@retry_with_backoff(max_retries=3)
@handle_api_error
def generate_script(niche: str, topic: str):
    # Check cache first
    cached_script = get_cached_script(niche, topic)
    if cached_script:
        logger.info(f"Using cached script for {niche}/{topic}")
        return cached_script
    
    logger.info(f"Generating new script for {niche}/{topic}")
    
    user_prompt = f"""
Write a short reel script about: {topic} (niche: {niche})

Just write 5-7 short punchy lines. No labels, no formatting, no markdown.
First line should be a strong hook (max 6 words).
Last line should be powerful and memorable.

Example format:
Stop satisfying everyone.
Your energy is limited.
Give it to those who deserve it.
Not everyone needs your time.
Protect your peace.
Choose yourself first.
"""

    script = None
    
    # Try Perplexity first (Primary - cheaper)
    if PERPLEXITY_API_KEY:
        try:
            logger.info("Using Perplexity API (primary)")
            script = _generate_with_perplexity(user_prompt)
        except Exception as e:
            logger.warning(f"Perplexity failed: {e}, trying OpenAI fallback...")
    
    # Fallback to OpenAI
    if not script and OPENAI_API_KEY:
        try:
            logger.info("Using OpenAI API (fallback)")
            script = _generate_with_openai(user_prompt)
        except Exception as e:
            logger.error(f"OpenAI also failed: {e}")
            raise RetryableError(f"All AI APIs failed: {e}", ErrorType.API_ERROR)
    
    if not script:
        raise RetryableError("No AI API available", ErrorType.API_ERROR)
    
    # Clean up any markdown formatting that slipped through
    import re
    script = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)  # Remove **bold**
    script = re.sub(r'\*([^*]+)\*', r'\1', script)      # Remove *italic*
    script = re.sub(r'^#+\s*', '', script, flags=re.MULTILINE)  # Remove ## headers
    script = re.sub(r'^(Hook|Body|Closing|Opening|Intro|Outro):\s*', '', script, flags=re.MULTILINE | re.IGNORECASE)
    script = re.sub(r'^\d+[\.\)]\s*', '', script, flags=re.MULTILINE)  # Remove 1. or 1)
    script = script.strip()
    
    # Cache the result
    cache_script(niche, topic, script)
    logger.info(f"Script generated and cached for {niche}/{topic}")
    
    return script


if __name__ == "__main__":
    print(generate_script("motivation", "discipline"))
