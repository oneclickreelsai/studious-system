from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a clean Indian comedy writer.
Write ORIGINAL, relatable Hindi/Hinglish jokes.
No real people. No copied jokes.
Short, punchy, subtitle-friendly.
"""

def generate_comedy(topic: str):
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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    return res.choices[0].message.content.strip()
