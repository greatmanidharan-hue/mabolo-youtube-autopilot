import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.analyze_reference import analyze_reference_video


class ReferenceAnalysisTests(unittest.TestCase):
    def test_writes_indian_character_shot_plan_without_reusing_source_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "reference.mp4"
            source.write_bytes(b"fake-video")
            output = root / "out"

            def fake_run(command, **kwargs):
                if command[0] == "ffmpeg":
                    frames_dir = output / "reference-shots"
                    frames_dir.mkdir(parents=True, exist_ok=True)
                    (frames_dir / "scene-metadata.txt").write_text(
                        "frame:0 pts_time:0.0\nframe:1 pts_time:2.5\n",
                        encoding="utf-8"
                    )
                    (frames_dir / "shot-001.jpg").write_bytes(b"frame1")
                    (frames_dir / "shot-002.jpg").write_bytes(b"frame2")
                    return type("Result", (), {"stdout": "", "stderr": ""})()
                return type("Result", (), {"stdout": "5.0\n", "stderr": ""})()

            with patch("src.analyze_reference.shutil.which", side_effect=lambda name: f"/usr/bin/{name}"), \
                 patch("src.analyze_reference.subprocess.run", side_effect=fake_run):
                manifest_path = analyze_reference_video(source, output)

            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(data["shots"]), 2)
            self.assertEqual(data["shots"][0]["start_seconds"], 0.0)
            self.assertEqual(data["shots"][0]["end_seconds"], 2.5)
            self.assertEqual(data["character_replacement"]["target_style"], "Indian / South Asian characters")
            self.assertIn("do not reuse source footage", data["source_usage"])


if __name__ == "__main__":
    unittest.main()
