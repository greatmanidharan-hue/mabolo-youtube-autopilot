from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

API = "https://www.googleapis.com/youtube/v3/videos"
DEFAULT_TREND_REGIONS = ("US", "GB", "CA", "AU", "JP", "KR", "IN", "DE", "BR")


def _trend_regions(region: str | None = None) -> list[str]:
    """Resolve GLOBAL or an explicit comma-separated list of YouTube region codes."""
    requested = (region or os.getenv("TREND_REGIONS", "GLOBAL")).strip().upper()
    if requested in {"", "GLOBAL", "WORLD", "WORLDWIDE"}:
        return list(DEFAULT_TREND_REGIONS)
    return list(dict.fromkeys(code.strip().upper() for code in requested.split(",") if code.strip()))


def discover_trending_topics(
    api_key: str | None = None,
    count: int = 1,
    region: str | None = None,
) -> list[dict[str, Any]]:
    """Aggregate public YouTube popularity metadata across regions; never fetch media or transcripts."""
    key = (api_key or os.getenv("YOUTUBE_API_KEY", "")).strip()
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is required. Add it to GitHub Actions secrets.")
    if count < 1:
        raise ValueError("count must be at least 1")

    regions = _trend_regions(region)
    now = datetime.now(timezone.utc)
    candidates: dict[str, tuple[float, dict[str, Any]]] = {}
    failures: list[str] = []

    for region_code in regions:
        params = urllib.parse.urlencode({
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": min(50, max(10, count * 10)),
            "key": key,
        })
        request = urllib.request.Request(API + "?" + params, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            failures.append(f"{region_code}: {exc}")
            continue

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
            existing = candidates.get(str(video_id))
            if existing and existing[0] >= score:
                existing[1]["trend_metadata"]["regions_seen"].append(region_code)
                continue

            topic = {
                "topic": title,
                "angle": "Create a fresh Tamil explainer about the same broad subject; do not translate or reproduce the source video.",
                "source_urls": [f"https://www.youtube.com/watch?v={video_id}"],
                "source_note": "Trend-discovery reference only; it does not verify factual claims and the source clip must not be reused.",
                "trend_metadata": {
                    "video_id": str(video_id),
                    "source_title": title,
                    "channel_title": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                    "views_per_hour_estimate": round(velocity, 2),
                    "region": region_code,
                    "regions_seen": [region_code],
                    "discovered_at": now.isoformat(),
                    "ranking_note": "Heuristic based on public views per hour and engagement across selected countries; not a guarantee of future virality.",
                },
            }
            candidates[str(video_id)] = (score, topic)

    ranked = sorted(candidates.values(), key=lambda entry: entry[0], reverse=True)
    if not ranked:
        detail = "; ".join(failures[:3])
        suffix = f" Region errors: {detail}" if detail else ""
        raise RuntimeError("YouTube returned no usable popular videos for the selected regions." + suffix)
    return [topic for _, topic in ranked[:count]]
