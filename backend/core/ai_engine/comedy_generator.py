"""
Comedy Generator - Uses Perplexity PRIMARY, OpenAI FALLBACK
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv("config.env")

# Perplexity (PRIMARY)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

# OpenAI (FALLBACK)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_client():
    """Get AI client - Perplexity first, OpenAI fallback."""
    if PERPLEXITY_API_KEY:
        return OpenAI(
            base_url="https://api.perplexity.ai",
            api_key=PERPLEXITY_API_KEY,
            timeout=30.0
        ), PERPLEXITY_MODEL
    elif OPENAI_API_KEY:
        return OpenAI(api_key=OPENAI_API_KEY, timeout=30.0), "gpt-4o-mini"
    return None, None


client, model = get_client()

SYSTEM_PROMPT = """
You are a clean Indian comedy writer.
Write ORIGINAL, relatable Hindi/Hinglish jokes.
No real people. No copied jokes.
Short, punchy, subtitle-friendly.
"""

def generate_comedy(topic: str):
    if not client:
        return "Error: No AI API configured"
    
    prompt = f"""
Create a 20–30 second funny script.
Topic: {topic}

Structure:
- Hook (1 line)
- Joke buildup (2–3 lines)
- Punchline (1 line)

Style:
Relatable Indian humor.
Simple Hindi/Hinglish.
"""

    res = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    return res.choices[0].message.content.strip()
