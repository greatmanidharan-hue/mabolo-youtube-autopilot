from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"


def build_queue_entry(draft_path: Path, video_path: Path, quality_path: Path) -> dict[str, Any]:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    return {
        "title": str(draft.get("title") or draft.get("topic") or "Untitled"),
        "topic": str(draft.get("topic") or ""),
        "draft": str(draft_path.relative_to(ROOT)),
        "video": str(video_path.relative_to(ROOT)),
        "quality_report": str(quality_path.relative_to(ROOT)),
        "generated_with": quality.get("generated_with", "unknown"),
        "editorial_status": quality.get("status", "draft_only"),
        "blockers": quality.get("blockers", []),
        "warnings": quality.get("warnings", []),
        "upload_status": "not_uploaded",
        "privacy_default": "private",
        "public_publish_allowed": False,
        "human_review_required": True,
    }


def write_upload_queue(entries: list[dict[str, Any]], output_dir: Path = OUTPUT_DIR) -> Path:
    if not entries:
        raise ValueError("Upload queue cannot be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = output_dir / f"upload-queue-{stamp}.json"
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "queue_status": "review_required",
        "items": entries,
        "publishing_note": "No video is uploaded or published by this queue. Human review and explicit upload confirmation are required.",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
