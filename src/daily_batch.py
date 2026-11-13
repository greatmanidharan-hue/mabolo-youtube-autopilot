from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from src.generate_content import (
    OUTPUT_DIR,
    build_offline_draft,
    generate_with_openrouter,
    load_topics,
)
from src.preview_gallery import write_preview_gallery
from src.quality_check import assess_draft
from src.render_video import DEFAULT_VOICE, render
from src.upload_queue import build_queue_entry, write_upload_queue

ROOT = Path(__file__).resolve().parents[1]


def select_daily_topics(day: date, count: int = 3) -> list[dict[str, Any]]:
    if count < 1:
        raise ValueError("count must be at least 1")
    topics = load_topics()
    if not topics:
        raise ValueError("Topic bank is empty")
    start = day.toordinal() % len(topics)
    return [topics[(start + offset) % len(topics)] for offset in range(min(count, len(topics)))]


def write_draft(topic: dict[str, Any], index: int, api_key: str, model: str, stamp: str) -> Path:
    draft: dict[str, Any] = (
        generate_with_openrouter(topic, api_key, model)
        if api_key else build_offline_draft(topic)
    )
    draft["created_at"] = datetime.now(timezone.utc).isoformat()
    draft["daily_batch_index"] = index
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"tamil-draft-{stamp}-{index:02d}.json"
    path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_batch(count: int = 3) -> list[Path]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    voice = os.getenv("TAMIL_TTS_VOICE", DEFAULT_VOICE)
    today = date.today()
    topics = select_daily_topics(today, count)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    results: list[Path] = []
    queue_entries: list[dict[str, Any]] = []
    preview_entries: list[dict[str, Any]] = []

    for index, topic in enumerate(topics, start=1):
        draft_path = write_draft(topic, index, api_key, model, stamp)
        report = assess_draft(json.loads(draft_path.read_text(encoding="utf-8")))
        report_path = draft_path.with_name(draft_path.stem + "-quality.json")
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        video_path = render(draft_path, voice)
        thumbnail_path = OUTPUT_DIR / f"{draft_path.stem}-thumbnail.jpg"
        results.extend([draft_path, report_path, video_path])
        queue_entries.append(build_queue_entry(draft_path, video_path, report_path))
        preview_entries.append({
            "title": report["title"],
            "topic": topic["topic"],
            "video_path": video_path,
            "thumbnail_path": thumbnail_path if thumbnail_path.exists() else None,
            "quality_status": report["status"],
        })
        print(f"Batch item {index}/{len(topics)} complete: {topic['topic']}")

    queue_path = write_upload_queue(queue_entries)
    preview_path = write_preview_gallery(preview_entries, OUTPUT_DIR)
    results.extend([queue_path, preview_path])
    print(f"Review queue created: {queue_path.relative_to(ROOT)}")
    print(f"Preview gallery created: {preview_path.relative_to(ROOT)}")
    return results


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Create a rotating daily batch of Tamil Shorts.")
    parser.add_argument("--count", type=int, default=3, help="Number of different Shorts to create (max topic bank size).")
    args = parser.parse_args()
    paths = run_batch(args.count)
    print(f"Daily batch complete: {len(paths)} output files")


if __name__ == "__main__":
    main()
