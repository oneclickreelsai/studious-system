import random

# Viral emojis by category
VIRAL_EMOJIS = {
    "motivation": ["🔥", "💪", "⚡", "🚀", "💯", "🎯", "👊", "✨", "🏆", "💎"],
    "finance": ["💰", "📈", "🤑", "💵", "💎", "🏦", "📊", "💸", "🔥", "⚡"],
    "facts": ["🤯", "😱", "🧠", "👀", "⚡", "🔥", "💡", "🎯", "❗", "✨"],
    "funny": ["😂", "🤣", "💀", "😭", "🔥", "⚡", "👀", "🤪", "😈", "💯"],
    "indian_comedy": ["😂", "🤣", "💀", "🇮🇳", "🔥", "⚡", "👀", "😭", "💯", "🎬"],
}

# Viral hook phrases
VIRAL_HOOKS = {
    "motivation": [
        "This changed my life",
        "Watch till the end",
        "Nobody talks about this",
        "Read this twice",
        "Stop scrolling",
        "You need to hear this",
        "Most people ignore this",
        "This hit different",
    ],
    "finance": [
        "Rich people know this",
        "Money secret revealed",
        "Stop being broke",
        "Wealth hack",
        "Financial freedom tip",
        "Money mindset shift",
        "This is why you're poor",
        "Millionaire habit",
    ],
    "facts": [
        "Mind = Blown",
        "Did you know this",
        "Science proves it",
        "99% don't know this",
        "Scary but true",
        "This is insane",
        "Your brain does this",
        "Unbelievable fact",
    ],
    "funny": [
        "I can't stop laughing",
        "This is too accurate",
        "Why is this so true",
        "Dead",
        "I felt this",
        "POV",
        "When you realize",
        "That one friend",
    ],
    "indian_comedy": [
        "Desi vibes only",
        "Every Indian knows",
        "Relatable AF",
        "Indian parents be like",
        "Desi problems",
        "Too accurate",
        "Why is this so true",
        "Indian family things",
    ],
}

# Viral hashtags
VIRAL_HASHTAGS = {
    "motivation": "#motivation #mindset #success #discipline #grindset #hustle #motivationalquotes #successmindset #selfimprovement #growthmindset #viral #fyp #shorts #reels",
    "finance": "#money #finance #wealth #investing #financialfreedom #moneytips #richmindset #passiveincome #millionaire #entrepreneur #viral #fyp #shorts #reels",
    "facts": "#facts #didyouknow #psychology #science #mindblown #amazingfacts #funfacts #knowledge #education #learning #viral #fyp #shorts #reels",
    "funny": "#funny #comedy #memes #humor #lol #funnyvideos #comedyvideos #laugh #hilarious #relatable #viral #fyp #shorts #reels",
    "indian_comedy": "#indiancomedy #desimemes #indianmemes #bollywood #desihumor #indianfunny #desivines #indianvines #comedy #funny #viral #fyp #shorts #reels",
}

def generate_caption(niche: str, topic: str):
    """Generate viral title and description with emojis"""
    
    # Handle unknown niche with fallback
    if niche not in VIRAL_HOOKS:
        niche = "motivation"
    
    # Get random elements
    emojis = VIRAL_EMOJIS.get(niche, VIRAL_EMOJIS["motivation"])
    hooks = VIRAL_HOOKS.get(niche, VIRAL_HOOKS["motivation"])
    hashtags = VIRAL_HASHTAGS.get(niche, VIRAL_HASHTAGS["motivation"])
    
    # Pick random emojis and hook
    e1, e2, e3, e4, e5 = random.sample(emojis, 5)
    hook = random.choice(hooks)
    
    # Create viral title with more emojis and hashtags
    title_templates = [
        f"{e1}{e2} {hook} {e3}{e4} #shorts #viral",
        f"{e1} {hook} {e2}{e3}{e4} #fyp #shorts",
        f"{e1}{e2}{e3} {hook} #viral #shorts",
        f"{e1} {topic.title()} {e2} {hook} {e3} #shorts",
        f"{e1}{e2} {hook} {e3} #motivation #shorts" if niche == "motivation" else f"{e1}{e2} {hook} {e3} #viral #shorts",
    ]
    title = random.choice(title_templates)
    
    # Create engaging description
    cta_phrases = [
        "Follow for more!",
        "Save this for later!",
        "Share with someone who needs this!",
        "Drop a 🔥 if you agree!",
        "Comment your thoughts!",
        "Like if this hit different!",
        "Tag someone!",
    ]
    cta = random.choice(cta_phrases)
    
    description = f"""{e1} {hook}

{e2} {topic.title()}

{cta}

{hashtags}"""
    
    return {
        "caption": hook,
        "title": title,
        "description": description,
        "hashtags": hashtags
    }


if __name__ == "__main__":
    # Test
    result = generate_caption("motivation", "discipline")
    print("Title:", result["title"])
    print("\nDescription:", result["description"])
