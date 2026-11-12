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


if __name__ == "__main__":
    unittest.main()
