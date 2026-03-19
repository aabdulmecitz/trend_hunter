"""
Gemini AI Content Engine
========================
Takes aggregated trend data and sends it to Google's Gemini AI to generate:
  1. Natural jokes about current viral trends
  2. Beluga-style Discord skit scenarios for video content inspiration
  3. Video content ideas based on what's trending

Pipeline: Detect Trends → Save JSON → Send to Gemini → Get Jokes & Scenarios
"""

import json
import logging
import os
import time

import google.generativeai as genai

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY_ENV = "GEMINI_API_KEY"

# Model fallback chain — tries each in order if rate limited
MODEL_CHAIN = [
    "gemini-1.5-pro-latest",   # Highest intelligence, user has Pro access
    "gemini-2.0-flash",        # Fast alternative
    "gemini-1.5-flash-latest", # Fallback
]
RETRY_DELAY = 30  # seconds to wait on 429 before retrying


def _get_api_key() -> str | None:
    """Get the Gemini API key from environment or .env file."""
    key = os.environ.get(API_KEY_ENV)
    if key:
        return key

    # Try loading from .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{API_KEY_ENV}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    return None


def _summarize_trends(trend_data: dict) -> str:
    """
    Create a concise summary of all trend data to send to Gemini.
    Keeps it focused so the AI understands what's currently viral.
    """
    parts = []

    # Google Trends
    us_trends = trend_data.get("google_trends_us", [])
    if us_trends and not (len(us_trends) == 1 and us_trends[0].get("error")):
        terms = [t["term"] for t in us_trends[:10]]
        parts.append(f"🔍 GOOGLE TRENDS (US): {', '.join(terms)}")

    world_trends = trend_data.get("google_trends_worldwide", [])
    if world_trends:
        terms = [t["term"] for t in world_trends[:10]]
        parts.append(f"🌍 GOOGLE TRENDS (WORLDWIDE): {', '.join(terms)}")

    # YouTube
    yt = trend_data.get("youtube_trending", {})
    videos = yt.get("videos", [])
    if videos:
        titles = [f"'{v['title']}' by {v.get('channel', 'N/A')}" for v in videos[:8]]
        parts.append(f"📺 YOUTUBE TRENDING:\n" + "\n".join(f"  - {t}" for t in titles))

    # TikTok
    tt = trend_data.get("tiktok_trends", {})
    hashtags = tt.get("trending_hashtags", [])
    sounds = tt.get("viral_sounds", [])
    if hashtags:
        tags = [h["hashtag"] for h in hashtags[:10]]
        parts.append(f"🎵 TIKTOK HASHTAGS: {', '.join(tags)}")
    if sounds:
        sound_names = [f"'{s['name']}' by {s.get('artist', 'N/A')}" for s in sounds[:5]]
        parts.append(f"🎶 TIKTOK VIRAL SOUNDS: {', '.join(sound_names)}")

    # Instagram
    ig = trend_data.get("instagram_trends", {})
    ig_hashtags = ig.get("trending_hashtags", [])
    ig_reels = ig.get("reel_trends", [])
    if ig_hashtags:
        tags = [h["hashtag"] for h in ig_hashtags[:10]]
        parts.append(f"📸 INSTAGRAM HASHTAGS: {', '.join(tags)}")
    if ig_reels:
        reels = [r["trend"] for r in ig_reels[:5]]
        parts.append(f"🎬 INSTAGRAM REEL TRENDS: {', '.join(reels)}")

    # Reddit
    rd = trend_data.get("reddit_trends", {})
    combined = rd.get("combined_top_keywords", [])
    if combined:
        kws = [kw["keyword"] for kw in combined[:15]]
        parts.append(f"🔥 REDDIT HOT KEYWORDS: {', '.join(kws)}")

    slang = rd.get("detected_slang_terms", [])
    if slang:
        parts.append(f"🧠 DETECTED INTERNET SLANG: {', '.join(slang)}")

    # Meme Dictionary
    meme_dict = trend_data.get("meme_dictionary", {})
    if meme_dict:
        definitions = [f"'{term}': {info['definition'][:80]}" for term, info in list(meme_dict.items())[:5]]
        parts.append(f"📖 MEME SLANG MEANINGS:\n" + "\n".join(f"  - {d}" for d in definitions))

    return "\n\n".join(parts)


# ── The Main Prompt ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a viral content creator and comedy writer who specializes in:
- Internet meme culture and brainrot humor (2024-2026 era)
- comedy skits (like Beluga, Flamingo, etc.)
- Comedy skits set in group chats (Discord, WhatsApp, Telegram, etc.)

- Short-form video content (YouTube Shorts, TikTok, Reels)

Your style is:
- Gen-Z/Gen-Alpha humor: absurd, self-aware, ironic
- Uses internet slang naturally (sigma, rizz, aura, brainrot, skibidi, etc.)
- Group chat culture: pings, bots, moderators, voice notes, chaotic energy
- Narrative style: fast-paced dialogue, unexpected plot twists, escalating absurdity
- Discord server culture or similar things can be: pings, bots, moderators, voice chats, #general chaos
- Beluga-style: characters with funny profile pics, unexpected plot twists, escalating absurdity

Here is your cast of characters. You must ONLY use these characters for the scenarios:

🟢 THE CORE CAST (The Stars - use frequently, conflict drives the comedy)
- XZKY (Main Character / The Instigator): The "smart" but mischievous kid. Starts the chaos, turns everyone against each other, and has the final say. A modern trickster. Vibe: Smart, fast, a bit of a troll. The audience's eyes and ears.
- BILLY (Naive / Noob): Absolute peak naivety. Always misunderstands internet jokes, metaphors, and how life works. A modern clown. Vibe: Soft, confused, very sympathetic. The main source of comedy.
- VICTOR (Angry Admin / Authority): The disciplinarian. Obsessed with rules, always ready to "ban" someone. Gets incredibly frustrated by Billy's stupidity. Vibe: Harsh, strict, angry.
- ETHAN (Pro / Genius): The mysterious, "know-it-all" older brother type. Solves complex problems with a single sentence. Vibe: Calm, smart, distant. XZKY asks Ethan for help when stuck.
- SILAS (Mysterious / Creepy): Appears unexpectedly, freezing the mood. Says unsettling, weird things. Vibe: Sneaky, mysterious, like a hissing 'S'. His creepy dialogue is absurdly funny.

🟠 GUEST STARS (The Bench - use sparingly, only when the script needs them)
- TIFFANY (Drama Queen): Overreacts to everything. Cries "My life is ruined!" over a broken nail. Needs to be the center of attention.
- HARVEY (Fake Expert): Knows nothing but claims, "I'm an expert" giving Billy terrible advice. Very annoying.
- CODY (Fast Gen-Z): Speaks entirely in emojis and terms like "POV, L, W, Ratio". The Gen-Alpha kid the group can't keep up with.
- ARTHUR (Boomer / Grandpa): Enters chat saying "Kids, you'll ruin your eyes." Completely clueless about technology, an old-school retired man.

You MUST respond in valid JSON format only. No markdown, no code blocks, just raw JSON."""


def _build_prompt(trend_summary: str) -> str:
    """Build the content generation prompt for Gemini."""
    return f"""Here are the CURRENT viral trends happening right now on the internet:

{trend_summary}

Based on these REAL trending topics, generate the following content in JSON format:

{{
  "trend_analysis": {{
    "hottest_trend": "The single most viral/interesting trend right now",
    "why_its_viral": "Brief explanation of why this is blowing up",
    "meme_potential": "High/Medium/Low — how memeable is this"
  }},
  "jokes": [
    {{
      "setup": "A natural joke setup based on a real trend above",
      "punchline": "The punchline",
      "trend_reference": "Which trend this references",
      "style": "one-liner / observational / absurd / self-deprecating"
    }}
  ],
  "scenarios": [
    {{
      "title": "Episode title (catchy, clickbaity for YouTube)",
      "platform": "Discord / WhatsApp / Telegram",
      "premise": "Brief premise — what's the situation",
      "characters": [
        {{
          "name": "Character name (Must be from the provided cast list)",
          "role": "Their role in the skit"
        }}
      ],
      "script": [
        {{
          "character": "Character name",
          "action": "type/voice note/ban/kick/reply/etc",
          "message": "What they say or do in the chat",
          "visual_note": "Optional visual/editing note for the video"
        }}
      ],
      "twist": "The unexpected ending or plot twist",
      "thumbnail_idea": "What the YouTube thumbnail should look like"
    }}
  ],
  "video_content_ideas": [
    {{
      "title": "Video title (YouTube/TikTok style — clickbaity but accurate)",
      "platform": "YouTube Shorts / TikTok / YouTube",
      "format": "Discord skit / Street interview / Commentary / POV / etc",
      "hook": "The first 3 seconds — what grabs attention",
      "concept": "Full description of the video idea",
      "trending_elements": ["list", "of", "trends", "used"],
      "estimated_virality": "High/Medium/Low"
    }}
  ]
}}

REQUIREMENTS:
- Generate exactly 5 jokes (mix of styles)
- Generate exactly 2 Scenario scripts (each with 10-15 script lines). Use different platforms (e.g. one Discord, one WhatsApp).
- Only use the characters from the provided cast (XZKY, BILLY, VICTOR, etc.). Include at least 3 core characters per scenario. Guest stars are optional.
- Generate exactly 3 video content ideas
- ALL content must reference REAL trends from the data above
- Make the humor natural, not forced — like something that would actually go viral
- Group chat skits should have escalating absurdity, unexpected twists, and relatable chat moments
- Video ideas should be things a small creator could actually produce for their YouTube channel"""


# ── Gemini API Call ───────────────────────────────────────────────────────────

def generate_content(trend_data: dict) -> dict:
    """
    Main entry point: sends trend data to Gemini AI and gets back
    jokes, Beluga-style scenarios, and video content ideas.
    """
    logger.info("🤖 Starting Gemini AI Content Generation...")

    api_key = _get_api_key()
    if not api_key:
        logger.error("❌ No Gemini API key found!")
        return {
            "error": "No API key. Set GEMINI_API_KEY environment variable or create a .env file.",
            "setup_instructions": {
                "step_1": "Get a free API key from https://aistudio.google.com/apikey",
                "step_2": "Create a .env file in the trend_hunter directory",
                "step_3": "Add this line: GEMINI_API_KEY=your_key_here",
                "step_4": "Run the bot again: python3 main.py",
            },
        }

    # Configure Gemini
    genai.configure(api_key=api_key)

    # Summarize all trend data
    trend_summary = _summarize_trends(trend_data)
    logger.info(f"  📋 Trend summary: {len(trend_summary)} chars")

    # Build the prompt
    prompt = _build_prompt(trend_summary)

    # Try each model in the fallback chain
    last_error = None
    for model_name in MODEL_CHAIN:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    temperature=0.9,
                    top_p=0.95,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                ),
            )

            logger.info(f"  🚀 Trying model: {model_name}...")
            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Try to parse as JSON
            try:
                content = json.loads(response_text)
                logger.info(f"  ✅ Success with {model_name}!")

                # Validate expected sections
                for section in ["trend_analysis", "jokes", "scenarios", "video_content_ideas"]:
                    if section not in content:
                        content[section] = []

                content["_meta"] = {
                    "model": model_name,
                    "prompt_length": len(prompt),
                    "response_length": len(response_text),
                    "source": "gemini_api",
                }
                return content

            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        content = json.loads(json_match.group())
                        content["_meta"] = {"model": model_name, "source": "gemini_api", "note": "extracted"}
                        return content
                    except json.JSONDecodeError:
                        pass

                return {
                    "raw_response": response_text,
                    "_meta": {"model": model_name, "source": "gemini_api"},
                    "error": "Could not parse AI response as JSON",
                }

        except Exception as e:
            err_str = str(e)
            last_error = err_str

            if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                logger.warning(f"  ⚠️ {model_name}: Rate limited, trying next model...")
                continue  # Try next model immediately
            else:
                logger.error(f"  ❌ {model_name}: {e}")
                continue

    # All models failed — try one more time with delay
    logger.info(f"  ⏳ All models rate-limited. Waiting {RETRY_DELAY}s and retrying...")
    time.sleep(RETRY_DELAY)

    try:
        model_name = MODEL_CHAIN[0]
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.9, top_p=0.95, max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        )
        logger.info(f"  🔄 Retry with {model_name}...")
        response = model.generate_content(prompt)
        content = json.loads(response.text.strip())
        content["_meta"] = {"model": model_name, "source": "gemini_api", "note": "after_retry"}
        return content
    except Exception as e:
        logger.error(f"  ❌ Final retry failed: {e}")
        return {
            "error": f"All models failed. Last error: {last_error}",
            "_meta": {"models_tried": MODEL_CHAIN, "source": "gemini_api_error"},
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Load existing trend data
    try:
        with open("global_trends.json", "r", encoding="utf-8") as f:
            trend_data = json.load(f)
        print("📂 Loaded global_trends.json")

        result = generate_content(trend_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        print("❌ Run main.py first to generate global_trends.json")
