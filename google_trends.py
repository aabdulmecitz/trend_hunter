"""
Google Trends Module (Direct Scraping)
======================================
Fetches real trending search terms by scraping Google Trends directly,
bypassing the broken pytrends library (archived April 2025).
Uses the Google Trends daily trends API and trending searches RSS feed.
"""

import json
import logging
import re
import xml.etree.ElementTree as ET

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
}

# Google Trends daily trends RSS feed (still works as of 2026)
DAILY_TRENDS_RSS = "https://trends.google.com/trending/rss?geo={geo}"

# Google Trends daily trends API endpoint
DAILY_TRENDS_API = "https://trends.google.com/trends/api/dailytrends"


def _fetch_trends_rss(geo: str = "US", limit: int = 10) -> list[dict]:
    """
    Fetch trending searches from Google Trends RSS feed.
    This is the most reliable method as RSS feeds rarely break.
    """
    url = DAILY_TRENDS_RSS.format(geo=geo)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        # RSS namespace
        ns = {"ht": "https://trends.google.com/trending/rss"}

        items = root.findall(".//item")
        trends = []

        for i, item in enumerate(items[:limit]):
            title = item.find("title")
            traffic = item.find("ht:approx_traffic", ns)
            news_items = item.findall("ht:news_item", ns)

            news_title = ""
            news_url = ""
            if news_items:
                nt = news_items[0].find("ht:news_item_title", ns)
                nu = news_items[0].find("ht:news_item_url", ns)
                if nt is not None:
                    news_title = nt.text or ""
                if nu is not None:
                    news_url = nu.text or ""

            trends.append({
                "rank": i + 1,
                "term": title.text if title is not None else "Unknown",
                "traffic": traffic.text if traffic is not None else "N/A",
                "related_news": news_title,
                "news_url": news_url,
                "region": geo,
            })

        return trends

    except Exception as e:
        logger.warning(f"RSS feed failed for {geo}: {e}")
        return []


def _fetch_trends_api(geo: str = "US", limit: int = 10) -> list[dict]:
    """
    Fetch trending searches from Google Trends daily trends API.
    Fallback if RSS doesn't work.
    """
    params = {
        "hl": "en-US",
        "tz": "-180",
        "geo": geo,
        "ns": "15",
    }

    try:
        resp = requests.get(DAILY_TRENDS_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        # Google prepends ")]}'" to the JSON response
        text = resp.text
        if text.startswith(")]}'"):
            text = text[5:]

        data = json.loads(text)
        days = data.get("default", {}).get("trendingSearchesDays", [])

        trends = []
        rank = 1
        for day in days:
            for search in day.get("trendingSearches", []):
                if rank > limit:
                    break
                title = search.get("title", {}).get("query", "Unknown")
                traffic = search.get("formattedTraffic", "N/A")

                related_news = ""
                news_url = ""
                articles = search.get("articles", [])
                if articles:
                    related_news = articles[0].get("title", "")
                    news_url = articles[0].get("url", "")

                trends.append({
                    "rank": rank,
                    "term": title,
                    "traffic": traffic,
                    "related_news": related_news,
                    "news_url": news_url,
                    "region": geo,
                })
                rank += 1

        return trends

    except Exception as e:
        logger.warning(f"API method failed for {geo}: {e}")
        return []


def _fetch_google_trends_page(limit: int = 10) -> list[dict]:
    """
    Scrape the Google Trends trending now page directly.
    Last resort fallback.
    """
    url = "https://trends.google.com/trending?geo=US&hl=en-US"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to find embedded JSON data
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "trendingSearches" in script.string:
                match = re.search(r'(\{.*"trendingSearches".*\})', script.string, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    # Parse the structure...
                    return []

        # Try finding trend items in the HTML
        trend_elements = soup.select("[class*='trending']") or soup.select("[class*='trend']")
        trends = []
        for i, el in enumerate(trend_elements[:limit]):
            text = el.get_text(strip=True)
            if text and len(text) > 1:
                trends.append({
                    "rank": i + 1,
                    "term": text,
                    "traffic": "N/A",
                    "region": "US",
                })
        return trends

    except Exception as e:
        logger.warning(f"Page scrape failed: {e}")
        return []


def fetch_trends(geo: str = "US", limit: int = 10) -> list[dict]:
    """
    Fetch trending searches using multiple methods with fallbacks.
    """
    # Method 1: RSS Feed (most reliable)
    trends = _fetch_trends_rss(geo, limit)
    if trends:
        logger.info(f"  ✅ {geo}: Got {len(trends)} trends via RSS feed")
        return trends

    # Method 2: Daily Trends API
    trends = _fetch_trends_api(geo, limit)
    if trends:
        logger.info(f"  ✅ {geo}: Got {len(trends)} trends via API")
        return trends

    # Method 3: Page scraping
    trends = _fetch_google_trends_page(limit)
    if trends:
        logger.info(f"  ✅ {geo}: Got {len(trends)} trends via page scrape")
        return trends

    logger.warning(f"  ❌ {geo}: All Google Trends methods failed")
    return [{"rank": 1, "term": "Google Trends temporarily unavailable", "region": geo, "error": "All methods failed"}]


def get_all_google_trends() -> dict:
    """Main entry point: returns US and Worldwide trends."""
    logger.info("📊 Fetching Google Trends...")

    us_trends = fetch_trends("US", limit=10)
    uk_trends = fetch_trends("GB", limit=10)
    global_trends = fetch_trends("", limit=10)  # Empty geo = worldwide

    # Merge UK + global for "worldwide" view, deduplicate
    seen = set()
    worldwide = []
    rank = 1
    for t in global_trends + uk_trends:
        term = t["term"]
        if term not in seen:
            seen.add(term)
            worldwide.append({**t, "rank": rank, "region": "Worldwide"})
            rank += 1
        if rank > 10:
            break

    return {
        "us_trends": us_trends,
        "worldwide_trends": worldwide,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = get_all_google_trends()
    print(json.dumps(data, indent=2))
