from __future__ import annotations
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

API = "https://www.googleapis.com/youtube/v3/videos"

def discover_trending_topics(api_key: str | None = None, count: int = 1, region: str = "IN") -> list[dict[str, Any]]:
    """Use public YouTube popularity metadata only; never fetch source media or transcripts."""
    key = (api_key or os.getenv("YOUTUBE_API_KEY", "")).strip()
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is required. Add it to GitHub Actions secrets.")
    if count < 1:
        raise ValueError("count must be at least 1")
    params = urllib.parse.urlencode({"part": "snippet,statistics", "chart": "mostPopular", "regionCode": region, "maxResults": min(50, max(10, count * 10)), "key": key})
    request = urllib.request.Request(API + "?" + params, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"YouTube trend lookup failed: {exc}") from exc
    now = datetime.now(timezone.utc)
    ranked = []
    for item in payload.get("items", []):
        video_id = item.get("id")
        snippet = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        title = str(snippet.get("title") or "").strip()
        if not video_id or not title or snippet.get("liveBroadcastContent") == "live":
            continue
        try:
            published = datetime.fromisoformat(str(snippet["publishedAt"]).replace("Z", "+00:00"))
            age_hours = max((now - published).total_seconds() / 3600, 1.0)
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
        except (KeyError, TypeError, ValueError):
            continue
        velocity = views / age_hours
        engagement = (likes + comments) / max(views, 1)
        score = velocity * (1.0 + min(engagement * 10, 0.5))
        ranked.append((score, {
            "topic": title,
            "angle": "Create a fresh Tamil explainer about the same broad subject; do not translate or reproduce the source video.",
            "source_urls": [f"https://www.youtube.com/watch?v={video_id}"],
            "source_note": "Trend-discovery reference only; it does not verify factual claims.",
            "trend_metadata": {
                "video_id": video_id, "source_title": title, "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""), "view_count": views, "like_count": likes,
                "comment_count": comments, "views_per_hour_estimate": round(velocity, 2), "region": region,
                "discovered_at": now.isoformat(),
                "ranking_note": "Heuristic based on public views per hour and engagement; not a guarantee of future virality."
            }
        }))
    ranked.sort(key=lambda entry: entry[0], reverse=True)
    if not ranked:
        raise RuntimeError("YouTube returned no usable popular videos for this region.")
    return [topic for _, topic in ranked[:count]]
