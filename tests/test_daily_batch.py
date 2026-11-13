import unittest
from datetime import date

from src.daily_batch import select_daily_topics


class DailyBatchTests(unittest.TestCase):
    def test_batch_selects_distinct_topics(self):
        selected = select_daily_topics(date(2026, 11, 13), 3)
        self.assertEqual(len(selected), 3)
        self.assertEqual(len({item["topic"] for item in selected}), 3)

    def test_rotation_changes_by_day(self):
        first = select_daily_topics(date(2026, 11, 13), 1)[0]["topic"]
        second = select_daily_topics(date(2026, 11, 14), 1)[0]["topic"]
        self.assertNotEqual(first, second)

    def test_rejects_invalid_count(self):
        with self.assertRaises(ValueError):
            select_daily_topics(date(2026, 11, 13), 0)


if __name__ == "__main__":
    unittest.main()
