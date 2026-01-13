"""
Meta AI Content Discovery
Uses AI to find trending/viral Meta AI content ideas and creators.
"""
import os
import json
import logging
import httpx
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv("config.env")
logger = logging.getLogger(__name__)

PERPLEXITY_KEY = os.getenv("PERPLEXITY_API_KEY")

def search_trending_meta_ai_content(category: str = "viral") -> List[Dict]:
    """
    Search for trending Meta AI content ideas using Perplexity.
    
    Args:
        category: Type of content (viral, funny, artistic, nature, etc.)
    
    Returns:
        List of content ideas with prompts
    """
    if not PERPLEXITY_KEY:
        return _get_fallback_ideas(category)
    
    try:
        prompt = f"""Create 3 HIGHLY DETAILED, CINEMATIC video prompts for "{category}" category for Meta AI video generation.

Each prompt MUST be:
- 100-200 words long with rich visual details
- Include camera movements (continuous shot, slow pan, tracking shot, etc.)
- Describe lighting (golden hour, dramatic shadows, bioluminescent, etc.)
- Include texture and material details (liquid, metallic, organic, etc.)
- Specify mood and atmosphere (ethereal, intense, dreamy, etc.)
- End with technical specs (4K, cinematic, slow motion, etc.)

Example of GOOD detailed prompt:
"A single unbroken black ink line flows smoothly across a pure white canvas. In one continuous cinematic camera move, the line slowly morphs and reshapes itself, transforming seamlessly through iconic painting styles — classical Renaissance sketches, impressionist brush forms, cubist abstractions. The ink behaves like liquid calligraphy, organic and alive. Ultra-smooth motion, museum-quality lighting, 4K resolution, slow elegant pacing."

Return ONLY a JSON array with detailed prompts:
[{{"prompt": "DETAILED 100-200 word cinematic prompt here", "viral_reason": "why viral", "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}}]"""

        response = httpx.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 1500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            
            # Parse JSON - try multiple approaches
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                # Find JSON array in content
                start = content.find('[')
                end = content.rfind(']') + 1
                if start >= 0 and end > start:
                    content = content[start:end]
                
                ideas = json.loads(content)
                if isinstance(ideas, list) and len(ideas) > 0:
                    logger.info(f"Found {len(ideas)} trending ideas for {category}")
                    return ideas
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error: {e}")
            
    except Exception as e:
        logger.error(f"Perplexity search error: {e}")
    
    return _get_fallback_ideas(category)

def _get_fallback_ideas(category: str) -> List[Dict]:
    """Fallback trending ideas without API - DETAILED cinematic prompts."""
    ideas = {
        "viral": [
            {
                "prompt": "A tiny hamster wearing a perfectly tailored miniature business suit stands at a podium in a massive TED talk auditorium. The camera slowly pushes in as the hamster gestures dramatically with its tiny paws, explaining complex cheese investment strategies with animated charts floating behind it. The audience of various animals watches in awe. Cinematic lighting with soft spotlights, shallow depth of field focusing on the hamster's determined expression. Corporate presentation aesthetic meets adorable absurdity. 4K resolution, smooth dolly movement, professional conference atmosphere.",
                "viral_reason": "Cute + absurd humor + relatable corporate satire",
                "hashtags": ["funny", "ai", "hamster", "tedtalk", "viral"]
            },
            {
                "prompt": "Famous classical paintings come to life in a museum at night. The Mona Lisa checks her phone with a bored expression, Starry Night's sky actually swirls and moves, The Scream figure is doom-scrolling social media. One continuous tracking shot glides past each painting as they deal with modern problems - Girl with a Pearl Earring takes selfies, American Gothic couple argues about WiFi password. Dramatic museum lighting, golden frames gleaming, marble floors reflecting the magical scene. Cinematic, 4K, smooth camera movement, whimsical yet elegant tone.",
                "viral_reason": "Art history meets modern life, relatable humor",
                "hashtags": ["art", "ai", "museum", "funny", "paintings"]
            },
        ],
        "funny": [
            {
                "prompt": "A sophisticated orange tabby cat wearing tiny professor glasses stands at a chalkboard filled with quantum physics equations. The camera slowly circles as the cat lectures to an audience of confused golden retrievers, pugs, and huskies sitting at tiny desks. The dogs tilt their heads in perfect synchronization, question marks practically visible above them. One husky raises its paw to ask a question. Warm classroom lighting, chalk dust floating in sunbeams, academic atmosphere meets pet chaos. 4K, cinematic shallow depth of field, comedic timing in the pacing.",
                "viral_reason": "Pet content + educational humor + relatable confusion",
                "hashtags": ["cats", "dogs", "funny", "physics", "professor"]
            },
            {
                "prompt": "Close-up on a dad's face at a restaurant table, the check has just arrived. Time slows down as we enter his mind - a dramatic visualization of mental math chaos. Numbers float around his head, a tiny version of himself runs through a maze of percentages, sweat forms on his brow. Cut between his calm exterior smile and the internal panic of calculating 18% vs 20% tip. His wife watches knowingly. Dramatic thriller lighting inside his mind, warm restaurant ambiance outside. Split-screen reality vs imagination. 4K, intense close-ups, comedic tension building.",
                "viral_reason": "Universal dad experience, relatable anxiety humor",
                "hashtags": ["dad", "funny", "relatable", "restaurant", "math"]
            },
        ],
        "indian_comedy": [
            {
                "prompt": "A dramatic Indian wedding scene where the groom arrives on a decorated white horse, but the horse has its own personality - it stops to take selfies with guests, photobombs the official photographer, and refuses to move until someone feeds it samosas. The panicked groom tries to maintain dignity while the horse does a little dance. Colorful wedding decorations, traditional music implied, guests laughing and recording on phones. Bollywood-style dramatic zoom-ins on reactions. Warm festive lighting, vibrant colors, 4K cinematic comedy.",
                "viral_reason": "Indian wedding humor, relatable chaos, animal comedy",
                "hashtags": ["indianwedding", "funny", "horse", "desi", "comedy", "viral"]
            },
            {
                "prompt": "An Indian mother discovers her son has been hiding instant noodles in his room. The scene plays out like a crime investigation thriller - dramatic flashlight under the bed, slow-motion noodle packet falling, the son's face frozen in horror. Mother's expressions shift from shock to disappointment to planning his doom. Dramatic Bollywood-style background music implied, intense close-ups, thriller lighting in a normal bedroom. The contrast between mundane situation and epic treatment. 4K, cinematic color grading, comedy through dramatic irony.",
                "viral_reason": "Desi mom humor, relatable family dynamics, dramatic comedy",
                "hashtags": ["desimom", "indianmom", "funny", "relatable", "noodles", "comedy"]
            },
            {
                "prompt": "A group of Indian uncles at a family gathering competing to give the most unsolicited career advice. Each uncle appears with dramatic superhero-style introduction - 'CA Uncle', 'Doctor Uncle', 'Government Job Uncle'. They circle a nervous young graduate like sharks, each pitching their career path with increasing intensity. Dramatic lighting on each uncle's face, family gathering background with curious aunties watching. Bollywood drama meets family comedy. 4K, dynamic camera movements, satirical tone.",
                "viral_reason": "Universal desi family experience, uncle stereotypes, career pressure humor",
                "hashtags": ["indianuncle", "desi", "career", "funny", "family", "relatable"]
            },
            {
                "prompt": "An Indian auto-rickshaw driver navigating through impossible traffic like an action movie hero. The camera follows from inside as he squeezes through gaps that shouldn't exist, honks in musical patterns, and has philosophical conversations with passengers about life. Other vehicles part like the Red Sea. Dramatic slow-motion near-misses, intense focus on his determined eyes in the rearview mirror. Mumbai/Delhi street chaos as backdrop. Action movie cinematography for everyday commute. 4K, dynamic tracking shots, heroic comedy.",
                "viral_reason": "Indian traffic humor, auto-rickshaw culture, everyday heroes",
                "hashtags": ["autorickshaw", "indiantraffic", "desi", "funny", "mumbai", "delhi"]
            },
            {
                "prompt": "A dramatic scene of an Indian student's internal struggle during an exam - angel and devil versions of himself argue about whether to peek at the next student's paper. The angel quotes his mother's values, the devil shows visions of engineering college rejection. Time freezes as he makes his choice. Exam hall setting with rows of stressed students, harsh fluorescent lighting, clock ticking dramatically. Bollywood moral dilemma style with comedic twist. 4K, split-screen internal conflict, relatable student humor.",
                "viral_reason": "Student life humor, moral comedy, exam stress relatability",
                "hashtags": ["examstress", "indianstudent", "funny", "relatable", "school", "comedy"]
            },
        ],
        "artistic": [
            {
                "prompt": "A single unbroken line of liquid gold ink flows across an infinite black void. In one continuous camera movement, the line transforms through art history - first forming delicate Japanese calligraphy, then morphing into Renaissance anatomical sketches, flowing into impressionist water lilies, shattering into cubist fragments, and finally settling into a hyperrealistic human eye that blinks. The ink has weight and texture, catching light like molten metal. Museum-quality dramatic lighting, extreme shallow depth of field, meditative pacing. 4K, ASMR-satisfying smooth motion, artistic and profound.",
                "viral_reason": "Mesmerizing visual journey through art history",
                "hashtags": ["art", "ink", "calligraphy", "satisfying", "artistic"]
            },
            {
                "prompt": "Deep in an enchanted forest, every tree is made of living crystal that pulses with inner light. The camera floats through at twilight as bioluminescent flowers bloom in real-time, their petals unfurling like slow-motion fireworks. Crystal deer with antlers of pure light drink from a mirror-still pool that reflects impossible constellations. Fireflies made of tiny galaxies drift past the lens. Ethereal fog rolls between the glowing trunks. Fantasy lighting with aurora borealis colors, dreamy soft focus, magical realism aesthetic. 4K, smooth floating camera, wonder and tranquility.",
                "viral_reason": "Visually stunning fantasy escapism",
                "hashtags": ["fantasy", "crystal", "forest", "magical", "beautiful"]
            },
        ],
        "nature": [
            {
                "prompt": "A day in the life of a single honeybee, shot like an epic Hollywood blockbuster. Dawn breaks as our hero emerges from the hive - dramatic orchestral music implied. Macro close-ups of fuzzy legs collecting golden pollen in slow motion, wings beating with visible air distortion. A dangerous encounter with a spider becomes a tense action sequence. The triumphant return to the hive at sunset, greeted as a hero. Cinematic color grading shifting from cool morning to warm golden hour. Extreme macro photography aesthetic, shallow depth of field, nature documentary meets action film. 4K, dramatic pacing.",
                "viral_reason": "Nature content elevated to cinematic epic",
                "hashtags": ["bee", "nature", "cinematic", "macro", "documentary"]
            },
            {
                "prompt": "Ancient mountains slowly rise and walk across a primordial landscape, each step taking centuries. Time-lapse of millions of years compressed into seconds - forests grow and die on their slopes like breathing, rivers carve paths around their massive stone feet. Each mountain has a distinct personality shown through their movement - one elderly and slow, one young and eager, one grumpy and reluctant. Clouds form scarves around their peaks. Epic scale with tiny civilizations building and crumbling below. Geological time made visible. 4K, grand sweeping camera movements, awe-inspiring and humbling.",
                "viral_reason": "Imaginative nature concept, epic scale",
                "hashtags": ["mountains", "nature", "timelapse", "epic", "fantasy"]
            },
        ],
        "music": [
            {
                "prompt": "Sound waves become visible as liquid ribbons of color flowing through a dark concert hall. A single piano note creates ripples of deep blue that spread outward, a violin joins with streams of warm gold intertwining. As the music builds, the colors dance and merge, forming abstract shapes that pulse with the rhythm. The camera weaves through the flowing colors like swimming through music itself. Crescendo moment: all colors explode into a galaxy of sound-stars. Dramatic concert lighting, synesthesia visualization, emotional and immersive. 4K, smooth flowing camera, ASMR-satisfying visuals.",
                "viral_reason": "Music visualization, synesthesia experience",
                "hashtags": ["music", "synesthesia", "piano", "colorful", "artistic"]
            },
        ],
        "motivational": [
            {
                "prompt": "A tiny seed buried in cracked, dry earth. Time-lapse as it struggles to break through - dramatic close-ups of the first green shoot pushing against impossible odds. Rain comes like a blessing, sunlight breaks through clouds in golden rays. The seedling grows into a mighty tree, its roots spreading underground like a network of determination. Birds nest in its branches, children play in its shade. The journey from seed to legacy. Inspirational lighting transitions from harsh to warm, cinematic nature documentary style. 4K, emotional pacing, triumph over adversity.",
                "viral_reason": "Universal growth metaphor, visually satisfying transformation",
                "hashtags": ["motivation", "growth", "nature", "inspiration", "nevergiveup"]
            },
        ],
    }
    return ideas.get(category, ideas["viral"])


def find_meta_ai_creators(niche: str = "animation") -> List[Dict]:
    """
    Find popular Meta AI creators/accounts.
    """
    if not PERPLEXITY_KEY:
        return []
    
    try:
        prompt = f"""Find 5 popular Meta AI creators who make {niche} content.
Return their Meta AI profile URLs if available, or describe their content style.

Return JSON: [{{"name": "creator name", "url": "meta.ai/@username or null", "style": "content description"}}]"""

        response = httpx.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content)
    except Exception as e:
        logger.error(f"Creator search error: {e}")
    
    return []

def generate_viral_prompt(topic: str) -> str:
    """
    Generate a viral-worthy Meta AI prompt for a given topic.
    """
    if not PERPLEXITY_KEY:
        return f"A stunning, cinematic {topic} scene with dramatic lighting and emotional depth"
    
    try:
        prompt = f"""Create a detailed, viral-worthy prompt for Meta AI video generation about: {topic}

The prompt should:
- Be visually interesting and unique
- Have emotional appeal or humor
- Work well for short-form video (under 60 seconds)
- Be specific enough to generate consistent results

Return only the prompt text, no explanation."""

        response = httpx.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_tokens": 300
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Prompt generation error: {e}")
    
    return f"A stunning, cinematic {topic} scene with dramatic lighting and emotional depth"


if __name__ == "__main__":
    # Test
    print("Trending viral ideas:")
    ideas = search_trending_meta_ai_content("funny")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea['prompt'][:60]}...")
    
    print("\nGenerated prompt for 'space exploration':")
    print(generate_viral_prompt("space exploration"))
