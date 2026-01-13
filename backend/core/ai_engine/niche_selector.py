import random

NICHES = {
    "motivation": [
        "discipline",
        "hard work",
        "self belief",
        "consistency",
        "success mindset",
        "overcoming failure",
        "morning routine",
        "staying focused",
        "building habits",
        "mental strength",
        "delayed gratification",
        "resilience",
        "taking action",
        "self improvement",
        "personal growth",
        "conquering fear",
        "time management",
        "goal setting",
        "never giving up",
        "pushing limits"
    ],
    "finance": [
        "money mindset",
        "wealth building",
        "financial discipline",
        "trading psychology",
        "saving habits",
        "investing early",
        "passive income",
        "side hustles",
        "financial freedom",
        "compound interest",
        "avoiding debt",
        "smart spending",
        "building assets",
        "emergency fund",
        "retirement planning"
    ],
    "facts": [
        "brain facts",
        "success facts",
        "money facts",
        "psychology facts",
        "productivity secrets",
        "body language",
        "decision making",
        "learning techniques",
        "memory tricks",
        "human behavior",
        "social dynamics",
        "cognitive biases",
        "emotional intelligence",
        "communication skills",
        "persuasion tactics"
    ]
}

def select_niche():
    niche = random.choice(list(NICHES.keys()))
    topic = random.choice(NICHES[niche])

    return {
        "niche": niche,
        "topic": topic
    }


if __name__ == "__main__":
    print(select_niche())
