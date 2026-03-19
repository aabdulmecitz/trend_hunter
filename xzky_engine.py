"""
Xzky Skit Engine
================
The "Xzky" AI Brainstorming Engine that takes aggregated global trends
and generates a 3-sentence Discord skit script in English featuring
the character "Xzky".
"""

import logging
import random

logger = logging.getLogger(__name__)

# Skit templates — each is a list of 3 lines (one per sentence)
# {trend} and {slang} placeholders get replaced with actual trending terms
SKIT_TEMPLATES = [
    # Template 1: Xzky joins voice chat
    [
        'Xzky: *joins voice chat at 3am* "Bro have you seen the {trend} thing? My aura literally went through the roof."',
        'Xzky: "I just spent 6 hours watching {trend} compilations. I think my {slang} levels are off the charts."',
        'Xzky: *plays {sound} at full volume* "This is the sound of victory. Skibidi out. gg no re." 🎤💀',
    ],
    # Template 2: Xzky in a server argument
    [
        'Xzky: *sends 47 messages in #general* "Listen, {trend} is the most {slang} thing to happen this year and I will NOT be taking questions."',
        'Xzky: "Anyone who disagrees has negative aura and zero rizz. I\'m literally the sigma of this server."',
        'Xzky: *changes nickname to "{trend} Enthusiast"* "Ratio + L + I just fanum taxed your opinion." 💅',
    ],
    # Template 3: Xzky's late night rant
    [
        'Xzky: *typing...* "Okay but hear me out — what if {trend} and {slang} are connected? Like on a cosmic level?"',
        'Xzky: "I made a 200-slide presentation about it. Slide 69 has {sound} playing in the background for emphasis."',
        'Xzky: *goes offline for 12 hours* *comes back* "I was mewing. Continue." 🗿',
    ],
    # Template 4: Xzky gaming moment
    [
        'Xzky: *streams at 144p* "Chat, I just discovered {trend} mid-ranked game and my brain has ascended."',
        'Xzky: "This is giving maximum {slang} energy. I\'m literally the main character right now."',
        'Xzky: *dies in-game* "That doesn\'t count, I was distracted by {sound}. This server is cooked fr fr." 💀🔥',
    ],
    # Template 5: Xzky conspiracy theory
    [
        'Xzky: *@everyone at 4am* "GUYS. What if {trend} was created by the government to boost our {slang}? Think about it."',
        'Xzky: "I\'ve been researching this for 3 hours. Every time I play {sound} backwards, it says \'subscribe.\'"',
        'Xzky: *gets muted by admin* *types in #off-topic* "They\'re trying to silence me because I\'m too based." 🤫📡',
    ],
    # Template 6: Xzky's hot take
    [
        'Xzky: *unmutes* "I don\'t care what anyone says, {trend} is the most important cultural event since sliced bread."',
        'Xzky: "My {slang} has been increasing exponentially. I can feel it in my bones. It\'s giving protagonist energy."',
        'Xzky: *{sound} starts playing* "See? Even the algorithm agrees with me. I rest my case. W." 🏆',
    ],
    # Template 7: Xzky in a Discord call
    [
        'Xzky: *screen shares a meme* "This {trend} meme has 47 layers of irony and I understand ALL of them."',
        'Xzky: "You guys don\'t get it because your {slang} comprehension is still at level 1. I\'m at prestige."',
        'Xzky: *accidentally leaves call* *rejoins* "That was intentional. Sigma exit. Now play me {sound}." 😎',
    ],
]

# Fallback trend terms if none are provided
FALLBACK_TRENDS = [
    "that new meme format", "the skibidi phenomenon", "AI-generated chaos",
    "that viral video", "the TikTok thing", "Discord's new update",
]

# Fallback slang terms
FALLBACK_SLANG = [
    "sigma", "aura", "rizz", "brainrot", "bussin", "based",
]

# Fallback sound names
FALLBACK_SOUNDS = [
    "Carnival Sped Up", "the Sigma Boy song", "Skibidi Bop Yes Yes Yes",
    "that one Phonk track", "APT by ROSÉ", "the brain rot anthem",
]


def generate_xzky_skit(
    trends: list[str] | None = None,
    slang_terms: list[str] | None = None,
    sound_names: list[str] | None = None,
) -> dict:
    """
    Generate a 3-sentence Discord skit script featuring Xzky.

    Args:
        trends:      List of trending terms/topics to inject
        slang_terms: List of slang terms detected from data
        sound_names: List of trending sound names

    Returns:
        Dict with the skit lines, template info, and keywords used.
    """
    logger.info("🎭 Generating Xzky Discord skit...")

    # Use provided data or fallbacks
    available_trends = trends if trends else FALLBACK_TRENDS
    available_slang = slang_terms if slang_terms else FALLBACK_SLANG
    available_sounds = sound_names if sound_names else FALLBACK_SOUNDS

    # Pick random items from each pool
    trend = random.choice(available_trends)
    slang = random.choice(available_slang)
    sound = random.choice(available_sounds)

    # Pick a random template
    template = random.choice(SKIT_TEMPLATES)

    # Fill in the template
    skit_lines = []
    for line in template:
        filled = line.format(trend=trend, slang=slang, sound=sound)
        skit_lines.append(filled)

    skit = {
        "character": "Xzky",
        "platform": "Discord",
        "lines": skit_lines,
        "keywords_used": {
            "trend": trend,
            "slang": slang,
            "sound": sound,
        },
        "full_script": "\n".join(skit_lines),
    }

    logger.info(f"  ✅ Skit generated using trend='{trend}', slang='{slang}', sound='{sound}'")
    return skit


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    # Demo with no input (uses fallbacks)
    skit = generate_xzky_skit()
    print("\n🎭 XZKY DISCORD SKIT:\n")
    print(skit["full_script"])
    print("\n📋 Full data:")
    print(json.dumps(skit, indent=2))
