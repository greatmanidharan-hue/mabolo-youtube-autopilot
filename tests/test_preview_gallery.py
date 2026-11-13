import tempfile
import unittest
from pathlib import Path

from src.preview_gallery import build_preview_html, write_preview_gallery


class PreviewGalleryTests(unittest.TestCase):
    def test_builds_video_cards_and_escapes_titles(self):
        html = build_preview_html([{
            "title": "<script>alert(1)</script>",
            "topic": "கீழடி",
            "video_path": "output/short-01.mp4",
            "thumbnail_path": "output/short-01.jpg",
            "quality_status": "draft_only",
        }])
        self.assertIn("short-01.mp4", html)
        self.assertIn("short-01.jpg", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_adds_android_file_picker_fallback(self):
        html = build_preview_html([{
            "title": "தமிழ் வரலாறு",
            "topic": "கீழடி",
            "video_path": "short.mp4",
            "quality_status": "draft_only",
        }])
        self.assertIn('type="file"', html)
        self.assertIn('accept="video/mp4,.mp4"', html)
        self.assertIn("URL.createObjectURL(file)", html)
        self.assertIn("Choose MP4 file", html)

    def test_writes_preview_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_preview_gallery([{
                "title": "தமிழ் வரலாறு",
                "topic": "கீழடி",
                "video_path": "short.mp4",
                "quality_status": "draft_only",
            }], Path(tmp))
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "preview-index.html")

    def test_rejects_empty_entries(self):
        with self.assertRaises(ValueError):
            build_preview_html([])


if __name__ == "__main__":
    unittest.main()
