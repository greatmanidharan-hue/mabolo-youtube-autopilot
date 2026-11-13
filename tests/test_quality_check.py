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

    def test_research_links_alone_are_not_verified_claims(self):
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
        self.assertFalse(report["sources_verified"])
        self.assertEqual(report["claim_check_count"], 0)
        self.assertTrue(any("research leads" in item for item in report["warnings"]))
        self.assertTrue(any("claim-by-claim" in item for item in report["warnings"]))

    def test_claim_verification_is_reported_but_never_auto_approves(self):
        report = assess_draft({
            "title": "தமிழ் வரலாறு",
            "script": "தமிழ் " * 100,
            "generated_with": "provider/model",
            "source_urls": ["https://example.org/research"],
            "sources_verified": True,
            "claim_checks": [{"claim": "Test", "verified": True}],
            "research_checklist": ["ஆதாரத்தை சரிபார்க்கவும்"],
            "review_required": True
        })
        self.assertEqual(report["status"], "ready_for_human_review")
        self.assertFalse(report["publish_allowed"])
        self.assertTrue(report["sources_verified"])
        self.assertEqual(report["claim_check_count"], 1)


if __name__ == "__main__":
    unittest.main()
