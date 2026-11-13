import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.render_video import build_ffmpeg_command, latest_draft


class MediaPipelineTests(unittest.TestCase):
    def test_ffmpeg_command_uses_tamil_font_safe_subtitles_and_motion(self):
        command = build_ffmpeg_command(
            Path("background.png"), Path("voice.mp3"),
            Path("captions.srt"), Path("short.mp4"), Path("/fonts/NotoSansTamil-Regular.ttf")
        )
        video_filter = command[command.index("-vf") + 1]
        self.assertIn("1080:1920", video_filter)
        self.assertIn("fontsdir='/fonts'", video_filter)
        self.assertIn("FontSize=16", video_filter)
        self.assertIn("MarginV=270", video_filter)
        self.assertIn("WrapStyle=0", video_filter)
        self.assertIn("MarginL=110", video_filter)
        self.assertIn("zoompan", video_filter)
        self.assertIn("libx264", command)
        self.assertIn("background.png", command)
        self.assertEqual(command[-1], "short.mp4")

    def test_latest_draft_requires_existing_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("src.render_video.OUTPUT_DIR", Path(tmp)):
                with self.assertRaises(FileNotFoundError):
                    latest_draft()


if __name__ == "__main__":
    unittest.main()
