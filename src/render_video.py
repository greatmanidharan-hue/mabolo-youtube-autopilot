from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.create_visuals import create_visuals

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
DEFAULT_VOICE = "ta-IN-PallaviNeural"


def latest_draft() -> Path:
    drafts = sorted(OUTPUT_DIR.glob("tamil-draft-*.json"))
    if not drafts:
        raise FileNotFoundError("No draft found. Run python -m src.generate_content first.")
    return drafts[-1]


def build_ffmpeg_command(background: Path, audio: Path, subtitles: Path, video: Path) -> list[str]:
    subtitle_filter = (
        f"subtitles={subtitles}:force_style="
        "'FontName=Noto Sans Tamil,FontSize=22,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00111111,BorderStyle=1,Outline=2,Alignment=2,MarginV=190'"
    )
    video_filter = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{subtitle_filter}"
    return [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "30", "-i", str(background),
        "-i", str(audio),
        "-vf", video_filter,
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", str(video)
    ]


def render(draft_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg was not found. Install FFmpeg and ensure it is on PATH.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    script = str(draft.get("script", "")).strip()
    if not script:
        raise ValueError("Draft has no script text.")

    stem = draft_path.stem
    audio = OUTPUT_DIR / f"{stem}.mp3"
    subtitles = OUTPUT_DIR / f"{stem}.srt"
    video = OUTPUT_DIR / f"{stem}-vertical.mp4"
    background, thumbnail = create_visuals(draft_path)

    tts_command = [
        sys.executable, "-m", "edge_tts",
        "--text", script,
        "--voice", voice,
        "--write-media", str(audio),
        "--write-subtitles", str(subtitles)
    ]
    subprocess.run(tts_command, check=True)
    if not audio.exists() or not subtitles.exists():
        raise RuntimeError("Voice provider did not create both audio and subtitle files.")

    subprocess.run(build_ffmpeg_command(background, audio, subtitles, video), check=True)
    print(f"Rendered video: {video.relative_to(ROOT)}")
    print(f"Thumbnail: {thumbnail.relative_to(ROOT)}")
    return video


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Tamil voice-over, visuals and a vertical subtitled video.")
    parser.add_argument("--draft", type=Path, default=None, help="Draft JSON path; defaults to newest draft.")
    parser.add_argument("--voice", default=os.getenv("TAMIL_TTS_VOICE", DEFAULT_VOICE))
    args = parser.parse_args()
    render(args.draft or latest_draft(), args.voice)


if __name__ == "__main__":
    main()
