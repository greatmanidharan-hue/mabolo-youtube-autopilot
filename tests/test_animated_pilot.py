import unittest
from pathlib import Path

from src.animated_pilot import build_mux_command, find_blender


class AnimatedPilotIntegrationTests(unittest.TestCase):
    def test_mux_command_combines_visual_voice_and_subtitles(self):
        command = build_mux_command(
            "ffmpeg", Path("visual.mp4"), Path("voice.mp3"),
            Path("captions.srt"), Path("final.mp4"), Path("C:/fonts/NotoSansTamil.ttf")
        )
        self.assertIn("visual.mp4", command)
        self.assertIn("voice.mp3", command)
        self.assertIn("captions.srt", command)
        self.assertIn("final.mp4", command)
        self.assertIn("-shortest", command)

    def test_find_blender_rejects_missing_explicit_path(self):
        with self.assertRaises(FileNotFoundError):
            find_blender("Z:/missing/blender.exe")


if __name__ == "__main__":
    unittest.main()
