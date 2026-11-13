from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def assess_draft(draft: dict[str, Any]) -> dict[str, Any]:
    script = str(draft.get("script", "")).strip()
    sources = draft.get("source_urls") or []
    checklist = draft.get("research_checklist") or []
    generated_with = str(draft.get("generated_with", "unknown"))
    blockers: list[str] = []
    warnings: list[str] = []

    if len(script) < 250:
        warnings.append("Script may be too short for a useful Short.")
    if len(script) > 1800:
        warnings.append("Script may be too long; check narration duration.")
    if generated_with == "offline-template":
        blockers.append("Offline template is a structure-only draft, not a researched script.")
    if not sources:
        blockers.append("No source URLs supplied; verify facts and add reliable references.")
    if not checklist:
        warnings.append("No research checklist supplied.")
    if draft.get("review_required") is not True:
        blockers.append("Draft is missing the mandatory human-review flag.")

    ready = not blockers
    return {
        "title": draft.get("title") or draft.get("topic") or "Untitled",
        "status": "ready_for_human_review" if ready else "draft_only",
        "publish_allowed": False,
        "generated_with": generated_with,
        "script_characters": len(script),
        "source_count": len(sources),
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Human fact-check and editorial approval are required before publishing."
    }


def main() -> None:
    paths = sorted((ROOT / "output").glob("tamil-draft-*.json"))
    if not paths:
        raise FileNotFoundError("No draft found in output/.")
    draft_path = paths[-1]
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    report = assess_draft(draft)
    report_path = draft_path.with_name(draft_path.stem + "-quality.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Quality report: {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
