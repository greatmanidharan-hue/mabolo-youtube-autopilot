from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.render_video import DEFAULT_VOICE, tamil_font_path

ROOT = Path(__file__).resolve().parents[1]
BLENDER_SCRIPT = ROOT / "scripts" / "blender" / "keeladi_pilot.py"
PILOT = ROOT / "content" / "pilots" / "keeladi-animated-pilot.md"
OUTPUT = ROOT / "output"
VISUAL = OUTPUT / "keeladi-pilot-visual.mp4"
FINAL = OUTPUT / "keeladi-pilot-final.mp4"
AUDIO = OUTPUT / "keeladi-pilot-ta.mp3"
SUBTITLES = OUTPUT / "keeladi-pilot-ta.srt"

NARRATION = (
    "காலை வெளிச்சம் பரவும் ஒரு பழங்காலத் தமிழர் குடியிருப்பை நினைத்துப் பாருங்கள். "
    "அன்றாட வாழ்க்கையில் மண் பானைகள், கைவினைத் தொழில்கள், நீர் பயன்பாடு போன்றவை முக்கிய இடம் பெற்றிருக்கலாம். "
    "கீழடி அகழாய்வில் கிடைத்த தொல்லியல் பொருட்கள், அக்கால மக்களின் வாழ்வியல் மற்றும் தொழில்நுட்பத் திறன்களைப் பற்றி ஆய்வு செய்ய உதவுகின்றன. "
    "ஆனால் ஒவ்வொரு காட்சியும் வரலாற்று உண்மை என்று கருதாமல், கிடைத்த சான்றுகளையும் ஆய்வுகளையும் தனித்தனியாகப் புரிந்துகொள்வோம்."
)


def find_blender(explicit: str | None = None) -> str:
    candidate = explicit or os.getenv("BLENDER_BIN")
    if candidate:
        if Path(candidate).exists():
            return candidate
        raise FileNotFoundError(f"Blender executable not found: {candidate}")
    found = shutil.which("blender")
    if found:
        return found
    windows_default = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
    if windows_default.exists():
        return str(windows_default)
    raise FileNotFoundError(
        "Blender not found. Add it to PATH or pass --blender /full/path/to/blender."
    )


def build_mux_command(ffmpeg: str, visual: Path, audio: Path, subtitles: Path,
                      output: Path, font_path: Path) -> list[str]:
    subtitle_filter = (
        f"subtitles='{subtitles.resolve().as_posix()}':"
        f"fontsdir='{font_path.parent.as_posix()}':force_style="
        "'FontName=Noto Sans Tamil,FontSize=18,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00111111,BorderStyle=1,Outline=2,Shadow=0,"
        "Alignment=2,MarginV=250,MarginL=100,MarginR=100,WrapStyle=0'"
    )
    return [
        ffmpeg, "-y", "-i", str(visual), "-i", str(audio),
        "-vf", subtitle_filter, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
        str(output)
    ]


def build_pilot(blender: str | None = None, voice: str = DEFAULT_VOICE) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found on PATH. Install the free FFmpeg build first.")
    blender_bin = find_blender(blender)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if not BLENDER_SCRIPT.exists():
        raise FileNotFoundError(f"Blender scene script missing: {BLENDER_SCRIPT}")

    subprocess.run([blender_bin, "-b", "-P", str(BLENDER_SCRIPT)], cwd=ROOT, check=True)
    if not VISUAL.exists() or VISUAL.stat().st_size == 0:
        raise RuntimeError(
            "Blender did not create output/keeladi-pilot-visual.mp4. "
            "Check Blender output above; PNG frames may still be in output/keeladi-pilot-frames/."
        )

    subprocess.run([
        sys.executable, "-m", "edge_tts", "--text", NARRATION, "--voice", voice,
        "--write-media", str(AUDIO), "--write-subtitles", str(SUBTITLES)
    ], cwd=ROOT, check=True)
    if not AUDIO.exists() or not SUBTITLES.exists():
        raise RuntimeError("Tamil narration or subtitle file was not created.")
    subprocess.run(
        build_mux_command(ffmpeg, VISUAL, AUDIO, SUBTITLES, FINAL, tamil_font_path()),
        cwd=ROOT, check=True
    )
    print(f"Animated pilot ready for human review: {FINAL.relative_to(ROOT)}")
    print("This command does not upload or publish to YouTube.")
    return FINAL


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the Keeladi Blender pilot with Tamil narration and subtitles."
    )
    parser.add_argument("--blender", help="Optional full path to blender.exe.")
    parser.add_argument("--voice", default=os.getenv("TAMIL_TTS_VOICE", DEFAULT_VOICE))
    args = parser.parse_args()
    build_pilot(args.blender, args.voice)


if __name__ == "__main__":
    main()
