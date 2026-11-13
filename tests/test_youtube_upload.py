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

    def test_public_upload_requires_human_review_and_sources(self):
        with self.assertRaisesRegex(ValueError, "editorial_reviewed"):
            build_video_body({"title": "test", "source_urls": ["https://example.org"]}, "public")

    def test_public_upload_requires_sources_even_after_review(self):
        with self.assertRaisesRegex(ValueError, "source_urls"):
            build_video_body({"title": "test", "editorial_reviewed": True}, "public")

    def test_public_upload_requires_claim_level_source_verification(self):
        draft = {
            "title": "test",
            "editorial_reviewed": True,
            "source_urls": ["https://example.org"],
            "sources_verified": True
        }
        with self.assertRaisesRegex(ValueError, "claim_checks"):
            build_video_body(draft, "public")

    def test_public_upload_accepts_fully_reviewed_source_metadata(self):
        draft = {
            "title": "test",
            "editorial_reviewed": True,
            "source_urls": ["https://example.org"],
            "sources_verified": True,
            "claim_checks": [{"claim": "Example claim", "source_url": "https://example.org", "verified": True}]
        }
        body = build_video_body(draft, "public")
        self.assertEqual(body["status"]["privacyStatus"], "public")

    def test_hashtag_metadata_is_appended(self):
        body = build_video_body({
            "title": "test", "description": "intro", "hashtags": ["#TamilHistory"]
        })
        self.assertIn("#TamilHistory", body["snippet"]["description"])


if __name__ == "__main__":
    unittest.main()
