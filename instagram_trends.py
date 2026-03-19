"""
Instagram Trends Module
=======================
Fetches trending Instagram hashtags and content trends using
public aggregator pages and Instagram's explore endpoints.
No login or API key required.
"""

import json
import logging
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
}

# Public hashtag aggregator sites that list trending IG hashtags
AGGREGATOR_URLS = [
    "https://top-hashtags.com/instagram/",
    "https://best-hashtags.com/",
    "https://www.all-hashtag.com/library/contents/hashtags/top-hashtags.php",
]


def _scrape_aggregator_sites() -> list[dict]:
    """
    Scrape trending hashtag aggregator sites.
    These sites compile trending Instagram hashtags from public data.
    """
    for url in AGGREGATOR_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract hashtags from page text
            text = soup.get_text()
            hashtags = re.findall(r"#(\w{2,30})", text)

            if not hashtags:
                # Try looking for list elements or spans with hashtags
                elements = (
                    soup.select("li, span, p, a")
                )
                for el in elements:
                    el_text = el.get_text(strip=True)
                    found = re.findall(r"#(\w{2,30})", el_text)
                    hashtags.extend(found)

            # Deduplicate and clean
            seen = set()
            unique = []
            # Filter out generic/noise words
            noise = {"hashtag", "hashtags", "top", "best", "instagram", "trending",
                     "popular", "copy", "share", "follow", "like", "post", "tags",
                     "reels", "explore", "account", "free", "app", "download"}
            for h in hashtags:
                h_lower = h.lower()
                if h_lower not in seen and h_lower not in noise and len(h) > 1:
                    seen.add(h_lower)
                    unique.append(h)

            if unique:
                logger.info(f"  ✅ Got {len(unique)} hashtags from {url}")
                return [
                    {"rank": i + 1, "hashtag": f"#{h}", "source": url.split("/")[2]}
                    for i, h in enumerate(unique[:20])
                ]

        except requests.RequestException as e:
            logger.debug(f"  Failed to scrape {url}: {e}")
            continue
        except Exception as e:
            logger.debug(f"  Parse error for {url}: {e}")
            continue

    return []


def _try_instagram_explore() -> list[dict]:
    """
    Try to access Instagram's explore or web API for trending content.
    This rarely works without auth but worth trying.
    """
    try:
        # Try Instagram's explore web page
        resp = requests.get(
            "https://www.instagram.com/explore/",
            headers={**HEADERS, "X-Requested-With": "XMLHttpRequest"},
            timeout=10,
        )
        if resp.status_code != 200:
            return []

        # Try to find any hashtag or trend data in the response
        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for embedded JSON
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Process structured data if available
            except (json.JSONDecodeError, TypeError):
                continue

        # Try meta tags
        hashtags = []
        meta_content = soup.find_all("meta", {"property": "og:description"})
        for meta in meta_content:
            content = meta.get("content", "")
            found = re.findall(r"#(\w{2,30})", content)
            hashtags.extend(found)

        return [
            {"rank": i + 1, "hashtag": f"#{h}", "source": "instagram.com"}
            for i, h in enumerate(hashtags[:20])
        ] if hashtags else []

    except Exception:
        return []


# Built-in list of currently trending Instagram hashtags / Reels trends (2025-2026)
FALLBACK_HASHTAGS = [
    {"hashtag": "#reels", "category": "Content Format"},
    {"hashtag": "#explore", "category": "Discovery"},
    {"hashtag": "#trending", "category": "General"},
    {"hashtag": "#aesthetic", "category": "Visual Culture"},
    {"hashtag": "#ootd", "category": "Fashion"},
    {"hashtag": "#grwm", "category": "Lifestyle"},
    {"hashtag": "#fyp", "category": "Discovery"},
    {"hashtag": "#skincare", "category": "Beauty"},
    {"hashtag": "#fitnessmotivation", "category": "Health"},
    {"hashtag": "#foodie", "category": "Food"},
    {"hashtag": "#travel", "category": "Travel"},
    {"hashtag": "#memes", "category": "Humor"},
    {"hashtag": "#brainrot", "category": "Internet Culture"},
    {"hashtag": "#sigma", "category": "Meme Culture"},
    {"hashtag": "#edit", "category": "Creative"},
    {"hashtag": "#viral", "category": "Growth"},
    {"hashtag": "#photography", "category": "Art"},
    {"hashtag": "#motivation", "category": "Inspiration"},
    {"hashtag": "#anime", "category": "Entertainment"},
    {"hashtag": "#gaming", "category": "Gaming"},
]

FALLBACK_REEL_TRENDS = [
    {"trend": "Get Ready With Me", "description": "Showing morning/evening routines and outfit selections", "status": "Evergreen"},
    {"trend": "Day in My Life", "description": "Vlog-style Reels showing daily activities", "status": "Evergreen"},
    {"trend": "Before & After Edits", "description": "Dramatic photo/video editing transformations", "status": "Trending"},
    {"trend": "POV Storytelling", "description": "First-person perspective mini-skits", "status": "Trending"},
    {"trend": "Sigma Edits", "description": "Edgy motivational edits with phonk music", "status": "Hot"},
    {"trend": "Aesthetic Mood Boards", "description": "Curated aesthetic visual compilations", "status": "Evergreen"},
    {"trend": "Text-Over-Video Rants", "description": "Hot takes and opinions with text overlays", "status": "Hot"},
    {"trend": "Silent Review / ASMR", "description": "Product/food reviews with satisfying sounds", "status": "Trending"},
]


def get_instagram_trends() -> dict:
    """
    Fetch Instagram trending hashtags and Reels trends.
    Tries multiple scraping methods with fallback.
    """
    logger.info("📸 Fetching Instagram Trends...")

    # Method 1: Aggregator sites
    hashtags = _scrape_aggregator_sites()

    # Method 2: Instagram explore (rarely works)
    if not hashtags:
        hashtags = _try_instagram_explore()

    # Use live data or fallback
    if hashtags:
        source_mode = "live_scrape"
        note = "Trending hashtags scraped from public aggregator sites"
        reel_trends = FALLBACK_REEL_TRENDS  # Always use curated Reel trends
    else:
        logger.info("  ⚠️ Instagram scraping failed — using curated trend data")
        source_mode = "curated"
        note = "Curated Instagram trend data (Instagram blocks automated scraping)"
        hashtags = [
            {**h, "rank": i + 1, "source": "curated"}
            for i, h in enumerate(FALLBACK_HASHTAGS)
        ]
        reel_trends = FALLBACK_REEL_TRENDS

    return {
        "source_mode": source_mode,
        "note": note,
        "trending_hashtags": hashtags,
        "reel_trends": reel_trends,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = get_instagram_trends()
    print(json.dumps(data, indent=2))
