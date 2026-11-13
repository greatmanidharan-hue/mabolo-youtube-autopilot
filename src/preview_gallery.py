from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def build_preview_html(entries: list[dict[str, Any]]) -> str:
    if not entries:
        raise ValueError("At least one preview entry is required.")

    cards = []
    for entry in entries:
        title = html.escape(str(entry.get("title") or "Tamil Short"))
        topic = html.escape(str(entry.get("topic") or ""))
        video = html.escape(Path(str(entry["video_path"])).name, quote=True)
        thumbnail_value = entry.get("thumbnail_path")
        thumbnail = html.escape(Path(str(thumbnail_value)).name, quote=True) if thumbnail_value else ""
        quality = html.escape(str(entry.get("quality_status") or "review_required"))
        image = f'<img src="{thumbnail}" alt="{title} thumbnail">' if thumbnail else ""
        cards.append(
            f'<article class="card">{image}<div class="body">'
            f'<p class="status">{quality.replace("_", " ")}</p>'
            f'<h2>{title}</h2><p>{topic}</p>'
            f'<video controls preload="metadata" src="{video}"></video>'
            f'<p><a href="{video}" download>Download MP4</a></p>'
            f'</div></article>'
        )

    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MABOLO TECH — Tamil Shorts Preview</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101522;color:#f5f6fa;font:16px system-ui,sans-serif}
header{padding:28px 5vw;background:#182238;border-bottom:1px solid #34415a}h1{margin:0 0 8px;font-size:clamp(24px,4vw,36px)}
header p,.note{color:#bac5d8}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:20px;padding:28px 5vw}
.card{overflow:hidden;background:#1b263a;border:1px solid #34415a;border-radius:16px}.card img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#0b1020}
.body{padding:18px}.status{color:#f4c875;text-transform:uppercase;font-size:12px;letter-spacing:.08em}
h2{font-size:20px;margin:8px 0}video{width:100%;margin-top:12px;border-radius:10px;background:#000}
a{color:#8fc5ff}.note{padding:0 5vw 28px;font-size:14px}
</style></head><body><header><h1>MABOLO TECH — Tamil Shorts</h1>
<p>Daily batch preview · Review each video before publishing</p></header>
<main class="grid">""" + "".join(cards) + """</main>
<p class="note">These are draft videos. Verify historical claims, sources, Tamil narration and subtitles. Nothing here has been uploaded or published.</p>
</body></html>
"""


def write_preview_gallery(entries: list[dict[str, Any]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "preview-index.html"
    path.write_text(build_preview_html(entries), encoding="utf-8")
    return path
