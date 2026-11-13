import unittest

from src.quality_check import assess_draft


class QualityCheckTests(unittest.TestCase):
    def test_offline_template_is_not_publishable(self):
        report = assess_draft({
            "title": "தமிழ் வரலாறு",
            "script": "வணக்கம் " * 50,
            "generated_with": "offline-template",
            "review_required": True,
            "research_checklist": ["ஆதாரம் சரிபார்க்கவும்"]
        })
        self.assertEqual(report["status"], "draft_only")
        self.assertFalse(report["publish_allowed"])
        self.assertTrue(any("Offline template" in item for item in report["blockers"]))

    def test_sources_do_not_remove_human_review_requirement(self):
        report = assess_draft({
            "title": "தமிழ் வரலாறு",
            "script": "தமிழ் " * 100,
            "generated_with": "provider/model",
            "source_urls": ["https://example.org/research"],
            "research_checklist": ["ஆதாரத்தை சரிபார்க்கவும்"],
            "review_required": True
        })
        self.assertEqual(report["status"], "ready_for_human_review")
        self.assertFalse(report["publish_allowed"])


if __name__ == "__main__":
    unittest.main()
