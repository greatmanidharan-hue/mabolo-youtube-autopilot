import unittest

from src.youtube_upload import build_video_body


class YouTubeUploadTests(unittest.TestCase):
    def test_upload_defaults_to_private_metadata(self):
        body = build_video_body({"title": "தமிழர் வரலாறு", "description": "விளக்கம்"}, "private")
        self.assertEqual(body["status"]["privacyStatus"], "private")
        self.assertEqual(body["snippet"]["title"], "தமிழர் வரலாறு")

    def test_rejects_unknown_privacy(self):
        with self.assertRaises(ValueError):
            build_video_body({"title": "test"}, "friends-only")

    def test_hashtag_metadata_is_appended(self):
        body = build_video_body({
            "title": "test", "description": "intro", "hashtags": ["#TamilHistory"]
        })
        self.assertIn("#TamilHistory", body["snippet"]["description"])


if __name__ == "__main__":
    unittest.main()
