from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.create_visuals import create_scene_visuals, create_visuals, tamil_font_path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
DEFAULT_VOICE = "ta-IN-PallaviNeural"


def latest_draft() -> Path:
    drafts = sorted(OUTPUT_DIR.glob("tamil-draft-*.json"))
    if not drafts:
        raise FileNotFoundError("No draft found. Run python -m src.generate_content first.")
    return drafts[-1]


def build_ffmpeg_command(background: Path, audio: Path, subtitles: Path, video: Path,
                         font_path: Path | None = None) -> list[str]:
    font_path = font_path or tamil_font_path()
    font_dir = font_path.parent
    subtitle_filter = (
        f"subtitles='{subtitles}':fontsdir='{font_dir}':force_style="
        "'FontName=Noto Sans Tamil,FontSize=16,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00111111,BorderStyle=1,Outline=2,Shadow=0,"
        "Alignment=2,MarginV=270,MarginL=110,MarginR=110,WrapStyle=0'"
    )
    motion_filter = (
        "zoompan=z='min(zoom+0.00015,1.035)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        "d=1:s=1080x1920:fps=30"
    )
    video_filter = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,{motion_filter},{subtitle_filter}"
    )
    return [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(background),
        "-i", str(audio), "-vf", video_filter,
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(video)
    ]


def _audio_duration(audio: Path) -> float:
    probe = shutil.which("ffprobe")
    if not probe:
        raise RuntimeError("ffprobe is required for render quality checks.")
    result = subprocess.run(
        [probe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
        check=True, capture_output=True, text=True
    )
    duration = float(result.stdout.strip())
    if duration <= 0:
        raise RuntimeError("Audio duration could not be determined.")
    return duration


def _write_scene_concat_file(scene_paths: list[Path], duration: float, manifest: Path) -> None:
    if len(scene_paths) < 2:
        raise ValueError("At least two visual scenes are required.")
    per_scene = duration / len(scene_paths)
    lines = []
    for path in scene_paths:
        safe_path = path.resolve().as_posix().replace("'", "'\\''")
        lines.extend([f"file '{safe_path}'", f"duration {per_scene:.4f}"])
    # concat demuxer needs the final file repeated so its duration is honored.
    safe_last = scene_paths[-1].resolve().as_posix().replace("'", "'\\''")
    lines.append(f"file '{safe_last}'")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_slideshow_command(manifest: Path, audio: Path, subtitles: Path, video: Path,
                            font_path: Path) -> list[str]:
    font_dir = font_path.parent
    subtitle_filter = (
        f"subtitles='{subtitles}':fontsdir='{font_dir}':force_style="
        "'FontName=Noto Sans Tamil,FontSize=16,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00111111,BorderStyle=1,Outline=2,Shadow=0,"
        "Alignment=2,MarginV=270,MarginL=110,MarginR=110,WrapStyle=0'"
    )
    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "fps=30,format=yuv420p,"
        + subtitle_filter
    )
    return [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-i", str(audio), "-vf", video_filter, "-r", "30",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(video)
    ]


def render(draft_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg was not found. Install FFmpeg and ensure it is on PATH.")
    font_path = tamil_font_path()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    script = str(draft.get("script", "")).strip()
    if not script:
        raise ValueError("Draft has no script text.")

    stem = draft_path.stem
    audio = OUTPUT_DIR / f"{stem}.mp3"
    subtitles = OUTPUT_DIR / f"{stem}.srt"
    video = OUTPUT_DIR / f"{stem}-vertical.mp4"
    _, thumbnail = create_visuals(draft_path)

    tts_command = [
        sys.executable, "-m", "edge_tts", "--text", script, "--voice", voice,
        "--write-media", str(audio), "--write-subtitles", str(subtitles)
    ]
    subprocess.run(tts_command, check=True)
    if not audio.exists() or not subtitles.exists():
        raise RuntimeError("Voice provider did not create both audio and subtitle files.")

    scenes = create_scene_visuals(draft_path)
    manifest = OUTPUT_DIR / f"{stem}-scenes.txt"
    _write_scene_concat_file(scenes, _audio_duration(audio), manifest)
    subprocess.run(build_slideshow_command(manifest, audio, subtitles, video, font_path), check=True)
    print(f"Rendered video: {video.relative_to(ROOT)}")
    print(f"Scene count: {len(scenes)}")
    print(f"Thumbnail: {thumbnail.relative_to(ROOT)}")
    return video


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Tamil narration, four scene changes and safe subtitles.")
    parser.add_argument("--draft", type=Path, default=None, help="Draft JSON path; defaults to newest draft.")
    parser.add_argument("--voice", default=os.getenv("TAMIL_TTS_VOICE", DEFAULT_VOICE))
    args = parser.parse_args()
    render(args.draft or latest_draft(), args.voice)


if __name__ == "__main__":
    main()
