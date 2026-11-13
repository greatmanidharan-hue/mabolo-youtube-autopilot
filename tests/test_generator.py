import unittest

from src.generate_content import build_offline_draft, load_topics


class GeneratorTests(unittest.TestCase):
    def test_topic_bank_is_not_empty(self):
        self.assertGreaterEqual(len(load_topics()), 1)

    def test_offline_draft_has_review_gate(self):
        draft = build_offline_draft(load_topics()[0])
        self.assertEqual(draft["language"], "Tamil")
        self.assertTrue(draft["review_required"])
        self.assertTrue(draft["script"])
        self.assertIn("research_checklist", draft)

    def test_offline_draft_carries_research_leads_without_claiming_verification(self):
        topic = {
            "topic": "Test topic",
            "angle": "Test angle",
            "source_urls": ["https://example.org/report"],
            "source_note": "Research leads only."
        }
        draft = build_offline_draft(topic)
        self.assertEqual(draft["source_urls"], topic["source_urls"])
        self.assertEqual(draft["source_note"], "Research leads only.")
        self.assertFalse(draft["sources_verified"])
        self.assertEqual(draft["claim_checks"], [])

    def test_missing_source_urls_remain_empty(self):
        draft = build_offline_draft({"topic": "Test", "angle": "Test angle"})
        self.assertEqual(draft["source_urls"], [])
        self.assertFalse(draft["sources_verified"])


if __name__ == "__main__":
    unittest.main()
