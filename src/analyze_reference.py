from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "reference_analysis"


def analyze_reference_video(video_path: Path, output_dir: Path = OUTPUT_DIR,
                            scene_threshold: float = 0.30) -> Path:
    """Extract scene-change frames and timestamps from a user-owned/licensed reference video.

    The source video is used only to map shot timing and composition. Its frames/audio
    are not copied into the final render.
    """
    video_path = video_path.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Reference video not found: {video_path}")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("FFmpeg and ffprobe are required for reference shot analysis.")
    if not 0.05 <= scene_threshold <= 0.95:
        raise ValueError("scene_threshold must be between 0.05 and 0.95")

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = video_path.stem
    frames_dir = output_dir / f"{stem}-shots"
    frames_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = frames_dir / "scene-metadata.txt"
    pattern = frames_dir / "shot-%03d.jpg"
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(video_path),
        "-vf", f"select='eq(n,0)+gt(scene,{scene_threshold})',metadata=print:file={metadata_path}",
        "-vsync", "vfr", "-q:v", "3", str(pattern)
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)

    duration_result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True
    )
    duration = float(duration_result.stdout.strip())
    pts_times = []
    if metadata_path.exists():
        metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
        pts_times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", metadata)]
    frame_paths = sorted(frames_dir.glob("shot-*.jpg"))
    shots: list[dict[str, Any]] = []
    for index, frame in enumerate(frame_paths):
        start = pts_times[index] if index < len(pts_times) else (0.0 if index == 0 else None)
        end = pts_times[index + 1] if index + 1 < len(pts_times) else duration
        shots.append({
            "shot_number": index + 1,
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": round(max(0.0, end - start), 3) if start is not None else None,
            "reference_frame": str(frame.relative_to(ROOT)) if frame.is_relative_to(ROOT) else str(frame),
            "visual_analysis": "",
            "recreation_prompt": ""
        })

    manifest = {
        "source_video_name": video_path.name,
        "source_duration_seconds": duration,
        "source_usage": "Shot analysis only; do not reuse source footage, audio, dialogue, logos or creator branding.",
        "character_replacement": {
            "enabled": True,
            "target_style": "Indian / South Asian characters",
            "preserve": ["shot order", "camera framing", "camera movement", "blocking", "action beats", "approximate timing"],
            "replace": ["character identity", "facial appearance", "wardrobe", "setting details where needed"],
            "avoid": ["real-person identity copying", "source logos", "distinctive copyrighted character designs"]
        },
        "shots": shots
    }
    manifest_path = output_dir / f"{stem}-shot-plan.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a shot map from a user-owned or licensed reference video.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--scene-threshold", type=float, default=0.30)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    result = analyze_reference_video(args.input, args.output_dir, args.scene_threshold)
    print(f"Shot plan created: {result}")


if __name__ == "__main__":
    main()
