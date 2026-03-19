"""
TikTok Viral Trends Module
===========================
Attempts multiple methods to get real TikTok trending data:
1. Scrape TikTok's discover/trending page for embedded JSON
2. Try TikTok's internal API endpoints
3. Fall back to realistic simulation if all methods fail

Also extracts trending hashtags in addition to sounds.
"""

import json
import logging
import random
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.tiktok.com/",
}

# ── Real Scraping Attempts ────────────────────────────────────────────────────

def _try_tiktok_discover() -> dict | None:
    """
    Try scraping TikTok's discover page.
    TikTok embeds JSON data in __UNIVERSAL_DATA_FOR_REHYDRATION__ or SIGI_STATE.
    """
    urls = [
        "https://www.tiktok.com/discover",
        "https://www.tiktok.com/trending",
        "https://www.tiktok.com/explore",
    ]

    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
            if resp.status_code != 200:
                continue

            html = resp.text

            # Try to find embedded JSON data
            json_patterns = [
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
                r'<script id="SIGI_STATE"[^>]*>(.*?)</script>',
                r'window\[\'SIGI_STATE\'\]\s*=\s*(\{.*?\});',
            ]

            for pattern in json_patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        return _extract_tiktok_trends(data)
                    except json.JSONDecodeError:
                        continue

            # Try BeautifulSoup parsing for visible elements
            soup = BeautifulSoup(html, "html.parser")

            # Look for hashtag/trend elements
            hashtag_elements = (
                soup.select("[data-e2e*='hashtag']")
                or soup.select("[class*='hashtag']")
                or soup.select("[class*='trend']")
                or soup.select("[class*='discover-card']")
                or soup.select("a[href*='/tag/']")
            )

            if hashtag_elements:
                hashtags = []
                seen = set()
                for el in hashtag_elements:
                    text = el.get_text(strip=True).lstrip("#")
                    href = el.get("href", "")
                    tag_match = re.search(r"/tag/([^/?]+)", href)
                    tag = tag_match.group(1) if tag_match else text

                    if tag and tag not in seen and len(tag) > 1:
                        seen.add(tag)
                        hashtags.append(tag)

                if hashtags:
                    return {
                        "hashtags": [
                            {"rank": i + 1, "hashtag": f"#{h}", "source": "live_scrape"}
                            for i, h in enumerate(hashtags[:15])
                        ],
                        "sounds": [],
                    }

        except requests.RequestException:
            continue
        except Exception as e:
            logger.debug(f"TikTok parse error for {url}: {e}")
            continue

    return None


def _extract_tiktok_trends(data: dict) -> dict | None:
    """Extract trending hashtags and sounds from TikTok's embedded JSON."""
    hashtags = []
    sounds = []

    def _search(obj, depth=0):
        if depth > 10:
            return
        if isinstance(obj, dict):
            # Look for hashtag data
            if "hashtagName" in obj or "hashtag" in obj:
                name = obj.get("hashtagName") or obj.get("hashtag", {}).get("name", "")
                if name:
                    hashtags.append(name)

            # Look for music/sound data
            if "musicName" in obj or "title" in obj and "authorName" in obj:
                music_name = obj.get("musicName") or obj.get("title", "")
                author = obj.get("authorName") or obj.get("author", "")
                if music_name:
                    sounds.append({"name": music_name, "artist": author})

            for v in obj.values():
                _search(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                _search(item, depth + 1)

    _search(data)

    if hashtags or sounds:
        seen_h = set()
        unique_hashtags = []
        for h in hashtags:
            if h not in seen_h:
                seen_h.add(h)
                unique_hashtags.append(h)

        return {
            "hashtags": [
                {"rank": i + 1, "hashtag": f"#{h}", "source": "live_scrape"}
                for i, h in enumerate(unique_hashtags[:15])
            ],
            "sounds": [
                {**s, "rank": i + 1, "source": "live_scrape"}
                for i, s in enumerate(sounds[:10])
            ],
        }

    return None


# ── Simulation Fallback ───────────────────────────────────────────────────────

SIMULATED_HASHTAGS = [
    {"hashtag": "#fyp", "category": "General / For You"},
    {"hashtag": "#sigma", "category": "Meme / Brainrot"},
    {"hashtag": "#skibidi", "category": "Meme / Brainrot"},
    {"hashtag": "#brainrot", "category": "Meme / Internet Culture"},
    {"hashtag": "#mewing", "category": "Meme / Looksmax"},
    {"hashtag": "#aura", "category": "Meme / Internet Culture"},
    {"hashtag": "#foryou", "category": "General / Discovery"},
    {"hashtag": "#viral", "category": "General / Growth"},
    {"hashtag": "#rizz", "category": "Meme / Internet Culture"},
    {"hashtag": "#grwm", "category": "Lifestyle / Get Ready With Me"},
    {"hashtag": "#xyzbca", "category": "General / Discovery"},
    {"hashtag": "#edits", "category": "Creative / Edit Culture"},
    {"hashtag": "#phonk", "category": "Music / Phonk"},
    {"hashtag": "#fypシ", "category": "General / For You"},
    {"hashtag": "#anime", "category": "Entertainment / Anime"},
]

SIMULATED_SOUNDS = [
    {"name": "Carnival (Sped Up)", "artist": "¥$, Kanye West & Ty Dolla $ign", "category": "Hip-Hop / Viral Remix", "estimated_videos": "4.2M"},
    {"name": "Nasty", "artist": "Tinashe", "category": "Pop / Dance Trend", "estimated_videos": "3.8M"},
    {"name": "Ecstasy Slowed + Reverb", "artist": "SUICIDAL-IDOL", "category": "Phonk / Edit Audio", "estimated_videos": "2.9M"},
    {"name": "Sigma Boy Sigma Girl", "artist": "Betsy (TikTok Remix)", "category": "Meme / Brainrot", "estimated_videos": "6.1M"},
    {"name": "APT.", "artist": "ROSÉ & Bruno Mars", "category": "K-Pop / Global Pop", "estimated_videos": "5.5M"},
    {"name": "Birds of a Feather", "artist": "Billie Eilish", "category": "Pop / Emotional Trend", "estimated_videos": "3.3M"},
    {"name": "Ordinary (Slowed)", "artist": "PinkPantheress", "category": "Hyperpop / Aesthetic", "estimated_videos": "2.1M"},
    {"name": "Skibidi Bop Yes Yes Yes", "artist": "Biser King (Remix)", "category": "Meme / Brainrot", "estimated_videos": "8.4M"},
    {"name": "I Like The Way You Kiss Me", "artist": "Artemas", "category": "Alt-Pop / Viral", "estimated_videos": "4.0M"},
    {"name": "Lub Dub x Lacrimosa", "artist": "Mashup (TikTok Original)", "category": "Classical / Edit Audio", "estimated_videos": "1.7M"},
]


def _get_simulated_data() -> dict:
    """Return simulated trending data when live scraping fails."""
    hashtags = random.sample(SIMULATED_HASHTAGS, min(10, len(SIMULATED_HASHTAGS)))
    sounds = random.sample(SIMULATED_SOUNDS, min(5, len(SIMULATED_SOUNDS)))
    return {
        "hashtags": [
            {**h, "rank": i + 1, "source": "simulation"}
            for i, h in enumerate(hashtags)
        ],
        "sounds": [
            {**s, "rank": i + 1, "source": "simulation"}
            for i, s in enumerate(sounds)
        ],
    }


# ── Main Entry Point ─────────────────────────────────────────────────────────

def get_tiktok_trends() -> dict:
    """
    Fetch TikTok trending hashtags and sounds.
    Attempts real scraping first, falls back to simulation.
    """
    logger.info("🎵 Fetching TikTok Trends...")

    # Try live scraping
    live_data = _try_tiktok_discover()

    if live_data and (live_data.get("hashtags") or live_data.get("sounds")):
        logger.info(f"  ✅ Live TikTok data: {len(live_data.get('hashtags', []))} hashtags, {len(live_data.get('sounds', []))} sounds")
        return {
            "source_mode": "live_scrape",
            "note": "Live data scraped from TikTok",
            "trending_hashtags": live_data.get("hashtags", []),
            "viral_sounds": live_data.get("sounds", []),
        }

    # Fallback to simulation
    logger.info("  ⚠️ TikTok scraping blocked — using simulation mode")
    sim_data = _get_simulated_data()

    return {
        "source_mode": "simulation",
        "note": "Simulated data based on current internet culture (TikTok blocks automated scraping)",
        "trending_hashtags": sim_data["hashtags"],
        "viral_sounds": sim_data["sounds"],
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = get_tiktok_trends()
    print(json.dumps(data, indent=2))
