#!/usr/bin/env python3
"""
Global Meme & Trend Hunter Bot v3.0 — Main Orchestrator
=========================================================
Pipeline: Scrape Trends → Save JSON → Send to Gemini AI → Get Jokes & Scenarios

1. Aggregates trend data from Google, YouTube, TikTok, Instagram, Reddit
2. Saves raw trends to global_trends.json
3. Sends trends to Gemini AI for content generation
4. Gets back jokes, Beluga-style scenarios, and video content ideas
"""

import json
import logging
import sys
from datetime import datetime, timezone

from google_trends import get_all_google_trends
from youtube_trends import get_youtube_trends
from tiktok_trends import get_tiktok_trends
from instagram_trends import get_instagram_trends
from reddit_trends import get_reddit_trends
from meme_dictionary import lookup_terms
from gemini_engine import generate_content

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OUTPUT_FILE = "global_trends.json"

BANNER = r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🌍  GLOBAL MEME & TREND HUNTER BOT v3.0  🔥                   ║
║   ─────────────────────────────────────────                      ║
║   Detect Trends → Analyze → Gemini AI → Video Content Ideas     ║
║   Google · YouTube · TikTok · Instagram · Reddit → Gemini AI     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""


def _sep(title: str) -> str:
    return f"\n{'─' * 60}\n  {title}\n{'─' * 60}"


def main() -> None:
    print(BANNER)
    logger.info("🚀 Starting Trend Hunter Bot v3.0...")
    logger.info(f"⏰ {datetime.now(timezone.utc).isoformat()}")

    report: dict = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "bot_version": "3.0.0",
            "pipeline": "Scrape Trends → Save JSON → Gemini AI → Jokes & Scenarios",
        },
    }

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 1: DETECT VIRAL TRENDS
    # ══════════════════════════════════════════════════════════════════════
    print(f"\n{'═' * 60}")
    print("  PHASE 1: DETECTING VIRAL TRENDS")
    print(f"{'═' * 60}")

    # ── 1) Google Trends ──────────────────────────────────────────────────
    print(_sep("📊 GOOGLE TRENDS"))
    try:
        google_data = get_all_google_trends()
        report["google_trends_us"] = google_data["us_trends"]
        report["google_trends_worldwide"] = google_data["worldwide_trends"]

        print("\n  🇺🇸 US Top Trends:")
        for item in google_data["us_trends"][:10]:
            traffic = f" ({item.get('traffic', '')})" if item.get("traffic") and item["traffic"] != "N/A" else ""
            print(f"    {item['rank']:>2}. {item['term']}{traffic}")

        print("\n  🌍 Worldwide Top Trends:")
        for item in google_data["worldwide_trends"][:10]:
            print(f"    {item['rank']:>2}. {item['term']}")
    except Exception as e:
        logger.error(f"Google Trends failed: {e}")
        report["google_trends_us"] = [{"error": str(e)}]
        report["google_trends_worldwide"] = [{"error": str(e)}]

    # ── 2) YouTube Trending ───────────────────────────────────────────────
    print(_sep("📺 YOUTUBE TRENDING"))
    try:
        youtube_data = get_youtube_trends()
        report["youtube_trending"] = youtube_data

        print(f"\n  Method: {youtube_data.get('method', 'N/A').upper()}")
        for vid in youtube_data.get("videos", [])[:10]:
            views = f" | {vid.get('views', '')}" if vid.get("views") else ""
            print(f"    {vid.get('rank', ''):>2}. {vid['title'][:60]}")
            if vid.get("channel"):
                print(f"        📺 {vid['channel']}{views}")
    except Exception as e:
        logger.error(f"YouTube failed: {e}")
        report["youtube_trending"] = {"error": str(e)}

    # ── 3) TikTok Trends ─────────────────────────────────────────────────
    print(_sep("🎵 TIKTOK TRENDS"))
    try:
        tiktok_data = get_tiktok_trends()
        report["tiktok_trends"] = tiktok_data

        print(f"\n  Mode: {tiktok_data['source_mode'].upper()}")
        if tiktok_data.get("trending_hashtags"):
            print("  📌 Hashtags:", ", ".join(h["hashtag"] for h in tiktok_data["trending_hashtags"][:10]))
        if tiktok_data.get("viral_sounds"):
            print("  🎶 Sounds:", ", ".join(s["name"] for s in tiktok_data["viral_sounds"][:5]))
    except Exception as e:
        logger.error(f"TikTok failed: {e}")
        report["tiktok_trends"] = {"error": str(e)}

    # ── 4) Instagram Trends ───────────────────────────────────────────────
    print(_sep("📸 INSTAGRAM TRENDS"))
    try:
        insta_data = get_instagram_trends()
        report["instagram_trends"] = insta_data

        print(f"\n  Mode: {insta_data['source_mode'].upper()}")
        if insta_data.get("trending_hashtags"):
            print("  📌 Hashtags:", ", ".join(h["hashtag"] for h in insta_data["trending_hashtags"][:10]))
        if insta_data.get("reel_trends"):
            print("  🎬 Reels:", ", ".join(r["trend"] for r in insta_data["reel_trends"][:5]))
    except Exception as e:
        logger.error(f"Instagram failed: {e}")
        report["instagram_trends"] = {"error": str(e)}

    # ── 5) Reddit Culture ─────────────────────────────────────────────────
    print(_sep("🔥 REDDIT CULTURE"))
    try:
        reddit_data = get_reddit_trends()
        report["reddit_trends"] = reddit_data

        for sub, data in reddit_data.get("per_subreddit", {}).items():
            if data["posts_analyzed"] == 0:
                continue
            top_5 = [kw["keyword"] for kw in data["top_keywords"][:5]]
            print(f"  📌 {sub}: {', '.join(top_5)}")

        slang = reddit_data.get("detected_slang_terms", [])
        print(f"\n  🧠 Detected Slang: {', '.join(slang) or 'None'}")
    except Exception as e:
        logger.error(f"Reddit failed: {e}")
        report["reddit_trends"] = {"error": str(e)}

    # ── 6) Meme Dictionary ────────────────────────────────────────────────
    print(_sep("📖 MEME DICTIONARY"))
    try:
        slang_to_lookup = set()
        slang_to_lookup.update(reddit_data.get("detected_slang_terms", []))
        slang_to_lookup.update(["aura", "sigma", "rizz", "skibidi", "brainrot", "mewing"])

        for h in report.get("tiktok_trends", {}).get("trending_hashtags", []):
            tag = h.get("hashtag", "").lstrip("#").lower()
            if tag in {"sigma", "rizz", "aura", "skibidi", "brainrot", "mewing",
                       "gyatt", "bussin", "delulu", "sus", "cap", "slay"}:
                slang_to_lookup.add(tag)

        meme_dict = lookup_terms(list(slang_to_lookup))
        report["meme_dictionary"] = meme_dict

        for term, info in meme_dict.items():
            defn = info["definition"][:80] + "..." if len(info["definition"]) > 80 else info["definition"]
            print(f"    🏷️  {term:<14} {defn}")
    except Exception as e:
        logger.error(f"Meme Dictionary failed: {e}")
        report["meme_dictionary"] = {"error": str(e)}

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 2: SEND TO GEMINI AI
    # ══════════════════════════════════════════════════════════════════════
    print(f"\n{'═' * 60}")
    print("  PHASE 2: GEMINI AI CONTENT GENERATION")
    print(f"{'═' * 60}")

    print(_sep("🤖 GEMINI AI — Generating Jokes & Scenarios"))
    try:
        ai_content = generate_content(report)
        report["ai_generated_content"] = ai_content

        if "error" in ai_content and "setup_instructions" in ai_content:
            # No API key — show setup instructions
            print("\n  ⚠️  Gemini API key not configured!\n")
            for step, instruction in ai_content["setup_instructions"].items():
                print(f"    {step}: {instruction}")
        elif "error" in ai_content:
            print(f"\n  ❌ AI Generation failed: {ai_content['error']}")
        else:
            # Successfully generated content!

            # Show trend analysis
            analysis = ai_content.get("trend_analysis", {})
            if analysis:
                print(f"\n  🔥 Hottest Trend: {analysis.get('hottest_trend', 'N/A')}")
                print(f"     Why: {analysis.get('why_its_viral', 'N/A')}")
                print(f"     Meme Potential: {analysis.get('meme_potential', 'N/A')}")

            # Show jokes
            jokes = ai_content.get("jokes", [])
            if jokes:
                print(f"\n  😂 GENERATED JOKES ({len(jokes)}):")
                for i, joke in enumerate(jokes, 1):
                    print(f"\n    Joke #{i} [{joke.get('style', '')}]:")
                    print(f"      Setup: {joke.get('setup', '')}")
                    print(f"      Punchline: {joke.get('punchline', '')}")

            # Show Beluga scenarios
            scenarios = ai_content.get("scenarios", [])
            if scenarios:
                print(f"\n  🎬 SCENARIOS ({len(scenarios)}):")
                for i, scenario in enumerate(scenarios, 1):
                    print(f"\n    Scenario #{i}: \"{scenario.get('title', '')}\"")
                    print(f"      Platform: {scenario.get('platform', 'Discord')}")
                    print(f"      Premise: {scenario.get('premise', '')}")
                    print(f"      Twist: {scenario.get('twist', '')}")
                    print(f"      Thumbnail: {scenario.get('thumbnail_idea', '')}")
                    print(f"      Characters: {', '.join(c.get('name', '') for c in scenario.get('characters', []))}")
                    print(f"      Script ({len(scenario.get('script', []))} lines):")
                    for line in scenario.get("script", [])[:4]:
                        action = f"*{line.get('action', '')}*" if line.get("action") else ""
                        print(f"        [{line.get('character', '')}] {action} {line.get('message', '')}")
                    if len(scenario.get("script", [])) > 4:
                        print(f"        ... +{len(scenario['script']) - 4} more lines")

            # Show video ideas
            ideas = ai_content.get("video_content_ideas", [])
            if ideas:
                print(f"\n  🎥 VIDEO CONTENT IDEAS ({len(ideas)}):")
                for i, idea in enumerate(ideas, 1):
                    print(f"\n    Idea #{i}: \"{idea.get('title', '')}\"")
                    print(f"      Platform: {idea.get('platform', 'N/A')}")
                    print(f"      Format: {idea.get('format', 'N/A')}")
                    print(f"      Hook: {idea.get('hook', 'N/A')}")
                    print(f"      Virality: {idea.get('estimated_virality', 'N/A')}")

    except Exception as e:
        logger.error(f"Gemini AI failed: {e}")
        report["ai_generated_content"] = {"error": str(e)}

    # ══════════════════════════════════════════════════════════════════════
    # SAVE REPORT
    # ══════════════════════════════════════════════════════════════════════
    print(_sep("💾 SAVING REPORT"))
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved to {OUTPUT_FILE}")
        print(f"\n  📄 Report: {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Save failed: {e}")

    # Summary
    yt_count = len(report.get("youtube_trending", {}).get("videos", []))
    tt_count = len(report.get("tiktok_trends", {}).get("trending_hashtags", []))
    ig_count = len(report.get("instagram_trends", {}).get("trending_hashtags", []))
    rd_count = len(report.get("reddit_trends", {}).get("combined_top_keywords", []))
    ai = report.get("ai_generated_content", {})
    jokes_count = len(ai.get("jokes", []))
    scenarios_count = len(ai.get("beluga_scenarios", []))
    ideas_count = len(ai.get("video_content_ideas", []))

    print(f"""
{'═' * 60}
  ✅ TREND HUNTING + AI GENERATION COMPLETE!
{'═' * 60}
  PHASE 1 — Trends Detected:
    • Google Trends:      {len(report.get('google_trends_us', []))} US + {len(report.get('google_trends_worldwide', []))} Worldwide
    • YouTube:            {yt_count} trending videos
    • TikTok:             {tt_count} hashtags + sounds
    • Instagram:          {ig_count} hashtags + reels
    • Reddit:             {rd_count} keywords

  PHASE 2 — AI Generated Content:
    • Jokes:              {jokes_count} jokes
    • Scenarios:          {scenarios_count} video scripts
    • Video Ideas:        {ideas_count} content ideas
    • Meme Dictionary:    {len(report.get('meme_dictionary', {}))} terms
{'═' * 60}
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted. Exiting...")
        sys.exit(0)
