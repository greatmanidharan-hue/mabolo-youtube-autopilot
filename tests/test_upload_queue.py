import json
import tempfile
import unittest
from pathlib import Path

from src.upload_queue import build_queue_entry, write_upload_queue


class UploadQueueTests(unittest.TestCase):
    def test_queue_entry_is_review_first_and_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft = root / "draft.json"
            video = root / "video.mp4"
            quality = root / "quality.json"
            draft.write_text(json.dumps({"title": "தமிழ் வரலாறு", "topic": "கீழடி"}), encoding="utf-8")
            quality.write_text(json.dumps({
                "status": "draft_only",
                "generated_with": "offline-template",
                "blockers": ["No sources"],
                "warnings": []
            }), encoding="utf-8")
            # Build paths relative to the module root contract using files in repo root.
            from src import upload_queue
            old_root = upload_queue.ROOT
            try:
                upload_queue.ROOT = root
                entry = build_queue_entry(draft, video, quality)
            finally:
                upload_queue.ROOT = old_root
            self.assertEqual(entry["upload_status"], "not_uploaded")
            self.assertEqual(entry["privacy_default"], "private")
            self.assertFalse(entry["public_publish_allowed"])
            self.assertTrue(entry["human_review_required"])

    def test_empty_queue_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_upload_queue([], Path(tmp))


if __name__ == "__main__":
    unittest.main()
