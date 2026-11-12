import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.render_video import build_ffmpeg_command, latest_draft


class MediaPipelineTests(unittest.TestCase):
    def test_ffmpeg_command_targets_vertical_short(self):
        command = build_ffmpeg_command(
            Path("voice.mp3"), Path("captions.vtt"), Path("short.mp4")
        )
        self.assertIn("1080x1920", command)
        self.assertIn("libx264", command)
        self.assertEqual(command[-1], "short.mp4")

    def test_latest_draft_requires_existing_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("src.render_video.OUTPUT_DIR", Path(tmp)):
                with self.assertRaises(FileNotFoundError):
                    latest_draft()


if __name__ == "__main__":
    unittest.main()
