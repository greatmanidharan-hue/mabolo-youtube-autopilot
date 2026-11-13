import json
import tempfile
import unittest
from pathlib import Path

from src.create_visuals import create_visuals


class VisualTests(unittest.TestCase):
    def test_creates_vertical_background_and_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft = root / "sample.json"
            draft.write_text(json.dumps({"title": "கீழடி அகழாய்வு", "topic": "கீழடி"}), encoding="utf-8")
            # Redirect generated assets to the isolated test directory.
            import src.create_visuals as visuals
            old_output = visuals.OUTPUT_DIR
            visuals.OUTPUT_DIR = root / "output"
            try:
                background, thumbnail = create_visuals(draft)
                self.assertTrue(background.exists())
                self.assertTrue(thumbnail.exists())
                from PIL import Image
                self.assertEqual(Image.open(background).size, (1080, 1920))
                self.assertEqual(Image.open(thumbnail).size, (1280, 720))
            finally:
                visuals.OUTPUT_DIR = old_output


if __name__ == "__main__":
    unittest.main()
