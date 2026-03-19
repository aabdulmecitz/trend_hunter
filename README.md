# 🌍 Global Meme & Trend Hunter Bot v2.0 🔥

A Python bot that scrapes **real trending data** from 5 platforms and generates a meme-culture intelligence report with a Discord skit.

## 🎯 Data Sources

| Platform | Method | What It Gets |
|----------|--------|-------------|
| **Google Trends** | RSS feed + API | Top 10 trending searches (US & Worldwide) with traffic data |
| **YouTube** | Page scraping (ytInitialData) | Trending videos with channel, views, timestamps |
| **TikTok** | Discover page scraping + simulation | Trending hashtags & viral sounds |
| **Instagram** | Aggregator scraping + curated data | Trending hashtags & Reel trend formats |
| **Reddit** | Public JSON API | Rising keywords from 9 meme/culture subreddits |

**Bonus features:**
- 📖 **Meme Dictionary** — Auto-defines slang (aura, sigma, rizz...) via built-in dict + Urban Dictionary API
- 🎭 **Xzky Engine** — Generates Discord skit scripts using real trending terms

## 📦 Structure

```
trend_hunter/
├── main.py               # Orchestrator
├── google_trends.py       # Google Trends (RSS + API, no pytrends!)
├── youtube_trends.py      # YouTube trending videos
├── tiktok_trends.py       # TikTok hashtags & sounds
├── instagram_trends.py    # Instagram hashtags & Reels
├── reddit_trends.py       # Reddit keyword analysis (9 subreddits)
├── meme_dictionary.py     # Slang lookup
├── xzky_engine.py         # Discord skit generator
├── index.html / style.css / app.js  # Dashboard website
├── requirements.txt       # Dependencies
└── global_trends.json     # Output (generated at runtime)
```

## 🚀 Quick Start

```bash
# 1. Setup
cd trend_hunter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run the bot
python3 main.py

# 3. View the dashboard
python3 -m http.server 8080
# Open http://localhost:8080
```

## ⚙️ Dependencies

Only **2 packages** required (no API keys needed):
- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing

## 📝 Notes

- **Google Trends**: Uses Google's RSS feed (most reliable) with API fallback
- **YouTube**: Extracts embedded `ytInitialData` JSON from the trending page
- **TikTok**: Attempts real scraping, falls back to simulation if blocked
- **Instagram**: Scrapes public aggregator sites, with curated fallback
- **Reddit**: Analyzes 9 subreddits with slang-boosted keyword detection
# trend_hunter
# trend_hunter
# trend_hunter
