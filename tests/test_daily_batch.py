import json
import unittest
from unittest.mock import patch

from src.trend_discovery import discover_trending_topics
from src.daily_batch import resolve_openrouter_model


class _Response:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class TrendDiscoveryTests(unittest.TestCase):
    def test_blank_openrouter_model_uses_valid_default(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {"OPENROUTER_MODEL": ""}):
            self.assertEqual(resolve_openrouter_model(), "openai/gpt-4o-mini")

    def test_custom_openrouter_model_is_preserved(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {"OPENROUTER_MODEL": "google/gemini-2.5-flash"}):
            self.assertEqual(resolve_openrouter_model(), "google/gemini-2.5-flash")

    def test_requires_youtube_api_key(self):
        with patch.dict("os.environ", {"YOUTUBE_API_KEY": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "YOUTUBE_API_KEY"):
                discover_trending_topics()

    def test_explicit_region_limits_lookup_to_that_country(self):\n        with patch("src.trend_discovery.urllib.request.urlopen", return_value=_Response({"items": []})) as mocked_open:\n            with self.assertRaisesRegex(RuntimeError, "no usable popular videos"):\n                discover_trending_topics("test-key", count=1, region="JP")\n            self.assertEqual(mocked_open.call_count, 1)\n            self.assertIn("regionCode=JP", mocked_open.call_args.args[0].full_url)\n\n    def test_rejects_invalid_count(self):
        with self.assertRaises(ValueError):
            discover_trending_topics("test-key", count=0)

    @patch("src.trend_discovery.urllib.request.urlopen")
    def test_returns_topic_metadata_without_source_media(self, mocked_open):
        mocked_open.return_value = _Response({"items": [{
            "id": "abc123",
            "snippet": {
                "title": "Popular science topic",
                "channelTitle": "Example Channel",
                "publishedAt": "2026-11-22T10:00:00Z",
                "liveBroadcastContent": "none"
            },
            "statistics": {"viewCount": "120000", "likeCount": "4000", "commentCount": "300"}
        }]})
        topics = discover_trending_topics("test-key", count=1)
        self.assertEqual(topics[0]["topic"], "Popular science topic")
        self.assertEqual(topics[0]["trend_metadata"]["video_id"], "abc123")\n        self.assertEqual(topics[0]["trend_metadata"]["regions_seen"], ["US", "GB", "CA", "AU", "JP", "KR", "IN", "DE", "BR"])\n        self.assertEqual(mocked_open.call_count, 9)
        self.assertEqual(topics[0]["source_urls"], ["https://www.youtube.com/watch?v=abc123"])
        self.assertNotIn("video_file", topics[0])
        self.assertNotIn("transcript", topics[0])


if __name__ == "__main__":
    unittest.main()
