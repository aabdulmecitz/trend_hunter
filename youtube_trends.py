"""
YouTube Trends Module
=====================
Scrapes YouTube's trending page to get currently trending videos.
Extracts video data from the embedded ytInitialData JSON blob.
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TRENDING_URL = "https://www.youtube.com/feed/trending"


def _extract_yt_initial_data(html: str) -> dict | None:
    """
    Extract the ytInitialData JSON blob from YouTube's page HTML.
    YouTube embeds all video data in a script variable.
    """
    patterns = [
        r"var\s+ytInitialData\s*=\s*(\{.*?\});\s*</script>",
        r"window\[\"ytInitialData\"\]\s*=\s*(\{.*?\});\s*</script>",
        r"ytInitialData\s*=\s*(\{.*?\});\s*",
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

    return None


def _parse_video_renderers(data: dict) -> list[dict]:
    """
    Navigate the ytInitialData structure to find video renderers.
    They contain title, channel, view count, etc.
    """
    videos = []

    def _find_renderers(obj, depth=0):
        if depth > 15 or len(videos) >= 20:
            return

        if isinstance(obj, dict):
            # Check for videoRenderer or richItemRenderer
            if "videoRenderer" in obj:
                vr = obj["videoRenderer"]
                try:
                    title = ""
                    title_runs = vr.get("title", {}).get("runs", [])
                    if title_runs:
                        title = title_runs[0].get("text", "")

                    channel = ""
                    channel_runs = vr.get("longBylineText", {}).get("runs", []) or \
                                   vr.get("shortBylineText", {}).get("runs", [])
                    if channel_runs:
                        channel = channel_runs[0].get("text", "")

                    views = vr.get("viewCountText", {}).get("simpleText", "")
                    if not views:
                        view_runs = vr.get("viewCountText", {}).get("runs", [])
                        views = " ".join(r.get("text", "") for r in view_runs) if view_runs else "N/A"

                    published = vr.get("publishedTimeText", {}).get("simpleText", "")
                    video_id = vr.get("videoId", "")
                    length = vr.get("lengthText", {}).get("simpleText", "")

                    if title:
                        videos.append({
                            "title": title,
                            "channel": channel,
                            "views": views,
                            "published": published,
                            "video_id": video_id,
                            "url": f"https://youtube.com/watch?v={video_id}" if video_id else "",
                            "length": length,
                        })
                except (KeyError, IndexError, TypeError):
                    pass
                return

            for value in obj.values():
                _find_renderers(value, depth + 1)

        elif isinstance(obj, list):
            for item in obj:
                _find_renderers(item, depth + 1)

    _find_renderers(data)
    return videos


def get_youtube_trends(limit: int = 15) -> dict:
    """
    Fetch YouTube trending videos by scraping the trending page.
    """
    logger.info("📺 Fetching YouTube Trends...")

    try:
        resp = requests.get(TRENDING_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        yt_data = _extract_yt_initial_data(resp.text)

        if yt_data:
            videos = _parse_video_renderers(yt_data)
            if videos:
                ranked = [
                    {**v, "rank": i + 1}
                    for i, v in enumerate(videos[:limit])
                ]
                logger.info(f"  ✅ Got {len(ranked)} trending YouTube videos")
                return {
                    "source": "youtube.com/feed/trending",
                    "method": "ytInitialData_extraction",
                    "video_count": len(ranked),
                    "videos": ranked,
                }

        # Fallback: try basic HTML parsing
        logger.info("  ⚠️ ytInitialData not found, trying HTML parsing...")
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to find video titles in meta tags or title elements
        title_el = soup.find("title")
        page_title = title_el.get_text() if title_el else ""

        # Look for any video-like elements
        links = soup.find_all("a", href=re.compile(r"/watch\?v="))
        videos = []
        seen = set()
        for link in links[:limit * 2]:
            title = link.get("title") or link.get_text(strip=True)
            href = link.get("href", "")
            vid_match = re.search(r"v=([a-zA-Z0-9_-]+)", href)
            vid_id = vid_match.group(1) if vid_match else ""

            if title and vid_id and vid_id not in seen:
                seen.add(vid_id)
                videos.append({
                    "title": title,
                    "video_id": vid_id,
                    "url": f"https://youtube.com/watch?v={vid_id}",
                })
                if len(videos) >= limit:
                    break

        if videos:
            ranked = [{**v, "rank": i + 1} for i, v in enumerate(videos)]
            logger.info(f"  ✅ Got {len(ranked)} videos via HTML parsing")
            return {
                "source": "youtube.com/feed/trending",
                "method": "html_parsing",
                "video_count": len(ranked),
                "videos": ranked,
            }

        logger.warning("  ❌ Could not extract any YouTube trending data")
        return {
            "source": "youtube.com/feed/trending",
            "method": "failed",
            "video_count": 0,
            "videos": [],
            "note": "YouTube trending page could not be scraped (JS-heavy rendering)",
        }

    except requests.RequestException as e:
        logger.error(f"  ❌ YouTube request failed: {e}")
        return {
            "source": "youtube.com/feed/trending",
            "method": "error",
            "video_count": 0,
            "videos": [],
            "error": str(e),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = get_youtube_trends()
    print(json.dumps(data, indent=2))
