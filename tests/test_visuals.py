import json
import tempfile
import unittest
from pathlib import Path

from src.create_visuals import create_scene_visuals, create_visuals, _draw_scene


class VisualTests(unittest.TestCase):
    def test_creates_four_distinct_vertical_scene_assets_and_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft = root / "sample.json"
            draft.write_text(json.dumps({"title": "கீழடி அகழாய்வு", "topic": "கீழடி அகழாய்வு"}), encoding="utf-8")
            import src.create_visuals as visuals
            old_output = visuals.OUTPUT_DIR
            visuals.OUTPUT_DIR = root / "output"
            try:
                background, thumbnail = create_visuals(draft)
                scenes = create_scene_visuals(draft)
                self.assertTrue(background.exists())
                self.assertTrue(thumbnail.exists())
                self.assertEqual(len(scenes), 4)
                self.assertEqual(len({p.name for p in scenes}), 4)
                from PIL import Image, ImageChops
                self.assertEqual(Image.open(background).size, (1080, 1920))
                self.assertEqual(Image.open(thumbnail).size, (1280, 720))
                self.assertIsNotNone(ImageChops.difference(Image.open(scenes[0]), Image.open(scenes[1])).getbbox())
            finally:
                visuals.OUTPUT_DIR = old_output


    def test_trending_topics_use_neutral_visual_labels(self):
        from PIL import Image, ImageDraw
        topics = ["இந்திய கிரிக்கெட் வெற்றி", "புதிய AI தொழில்நுட்பம்", "பங்குச்சந்தை மாற்றம்"]
        expected = ["முக்கிய கருத்து", "பின்னணி", "எப்படி செயல்படுகிறது?", "நினைவில் கொள்ளுங்கள்"]
        for topic in topics:
            labels = []
            for index in range(4):
                canvas = Image.new("RGBA", (1080, 1920))
                labels.append(_draw_scene(ImageDraw.Draw(canvas), topic, index))
            self.assertEqual(labels, expected)
        self.assertNotIn("தமிழர் வரலாறு", Path("src/create_visuals.py").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
