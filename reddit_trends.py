"""
Reddit Culture Module
=====================
Identifies rising keywords from meme/internet-culture subreddits using
Reddit's public JSON API (no authentication required).
"""

import logging
import re
import time
from collections import Counter

import requests

logger = logging.getLogger(__name__)

# Target subreddits for internet culture analysis
TARGET_SUBREDDITS = [
    "memes", "dankmemes", "me_irl", "shitposting",
    "discordapp", "skibiditoilet", "tiktokcringe",
    "internetculture", "trendingsubreddits",
]

# Common English stop words to filter out of keyword analysis
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "about", "between",
    "through", "after", "before", "during", "without", "under", "over",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "no", "not", "only", "own", "same", "so",
    "than", "too", "very", "just", "but", "and", "or", "if", "because",
    "until", "while", "it", "its", "this", "that", "these", "those",
    "i", "me", "my", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "they", "them", "their", "what", "which", "who", "whom",
    "up", "out", "off", "down", "like", "get", "got", "go", "going",
    "one", "two", "new", "first", "also", "back", "even", "still",
    "way", "use", "make", "know", "see", "look", "think", "come",
    "want", "say", "take", "good", "people", "well", "much", "right",
    "now", "thing", "really", "don't", "don", "doesn", "didn", "won",
    "amp", "https", "http", "www", "com", "reddit", "removed", "deleted",
    "anyone", "someone", "something", "anything", "nothing", "everything",
    "need", "time", "day", "year", "work", "life", "help", "man",
    "oc", "rule", "rules", "post", "meta", "mod", "mods", "subreddit",
}

# Minimum word length to consider
MIN_WORD_LENGTH = 3

# Internet culture slang we especially want to detect
SLANG_BOOST = {
    "sigma", "rizz", "rizzed", "aura", "skibidi", "gyatt", "slay",
    "ratio", "npc", "delulu", "sus", "cap", "nocap", "bet", "fire",
    "goat", "vibe", "vibes", "stan", "based", "cringe", "cope",
    "seethe", "mald", "poggers", "pogchamp", "brainrot", "mogged",
    "looksmax", "edging", "fanum", "tax", "ohio", "grimace", "mewing",
    "jellybeanbrains", "livvy", "dunne", "hawk", "tuah", "bussing",
    "bussin", "frfr", "ong", "deadass", "lowkey", "highkey", "simp",
    "chad", "karen", "boomer", "zoomer", "w", "l",
}


def _fetch_subreddit_posts(subreddit: str, sort: str = "hot", limit: int = 50) -> list[str]:
    """
    Fetch post titles from a subreddit using the public JSON API.
    Returns a list of post title strings.
    """
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    headers = {
        "User-Agent": "TrendHunterBot/1.0 (Educational Project; +https://github.com/trend-hunter)"
    }
    params = {"limit": limit, "t": "day"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        posts = data.get("data", {}).get("children", [])
        titles = [
            post["data"]["title"]
            for post in posts
            if post.get("data", {}).get("title")
        ]
        logger.info(f"  ✅ r/{subreddit}: fetched {len(titles)} posts")
        return titles

    except requests.RequestException as e:
        logger.warning(f"  ❌ r/{subreddit}: request failed — {e}")
        return []
    except (ValueError, KeyError) as e:
        logger.warning(f"  ❌ r/{subreddit}: parsing failed — {e}")
        return []


def _extract_keywords(titles: list[str], top_n: int = 15) -> list[dict]:
    """
    Extract and rank keywords from a list of post titles.
    Prioritizes internet culture slang terms.
    """
    word_counter: Counter = Counter()

    for title in titles:
        # Normalize: lowercase, keep only alphanumeric and spaces
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", title.lower())
        words = cleaned.split()

        for word in words:
            if len(word) < MIN_WORD_LENGTH and word not in SLANG_BOOST:
                continue
            if word in STOP_WORDS:
                continue
            word_counter[word] += 1

    # Boost slang terms by multiplying their count
    boosted: Counter = Counter()
    for word, count in word_counter.items():
        if word in SLANG_BOOST:
            boosted[word] = count * 3  # Triple weight for slang
        else:
            boosted[word] = count

    top_keywords = boosted.most_common(top_n)
    return [
        {"keyword": word, "raw_count": word_counter[word], "boosted_score": score}
        for word, score in top_keywords
    ]


def get_reddit_trends() -> dict:
    """
    Main entry point: fetches posts from target subreddits and performs
    keyword frequency analysis. Returns structured trend data.
    """
    logger.info("🔥 Fetching Reddit culture trends...")

    results = {}
    all_titles: list[str] = []

    for subreddit in TARGET_SUBREDDITS:
        titles = _fetch_subreddit_posts(subreddit)
        keywords = _extract_keywords(titles)
        results[f"r/{subreddit}"] = {
            "posts_analyzed": len(titles),
            "top_keywords": keywords,
        }
        all_titles.extend(titles)

        # Be respectful of Reddit rate limits
        time.sleep(1.5)

    # Cross-subreddit combined analysis
    combined_keywords = _extract_keywords(all_titles, top_n=20)

    # Extract detected slang terms
    detected_slang = [
        kw["keyword"]
        for kw in combined_keywords
        if kw["keyword"] in SLANG_BOOST
    ]

    return {
        "subreddits_analyzed": [f"r/{s}" for s in TARGET_SUBREDDITS],
        "per_subreddit": results,
        "combined_top_keywords": combined_keywords,
        "detected_slang_terms": detected_slang,
    }


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    data = get_reddit_trends()
    print(json.dumps(data, indent=2))
