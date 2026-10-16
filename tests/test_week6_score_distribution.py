import unittest
import pandas as pd
from src.week6_score_distribution import tidy_year, summarize

class TestScoreDistribution(unittest.TestCase):
    def test_alias_mapping_and_invalid_scores(self):
        frame = pd.DataFrame({"Mathematics": [0, 1, 5, 8, 9, 10, 11, None],
                              "Literature": [4, 5, 6, 7, 8, 9, 10, None]})
        cleaned = tidy_year(frame, 2023)
        self.assertIn("Toán", cleaned.columns)
        self.assertIn("Ngữ văn", cleaned.columns)
        self.assertEqual(cleaned["Toán"].notna().sum(), 6)
        self.assertTrue(cleaned["Toán"].dropna().between(0, 10).all())

    def test_thresholds_and_descriptive_statistics(self):
        long = pd.DataFrame({"year": [2023] * 5, "subject": ["Toán"] * 5, "score": [0, 2, 5, 8, 10]})
        row = summarize(long).iloc[0]
        self.assertEqual(row["n"], 5)
        self.assertAlmostEqual(row["mean"], 5)
        self.assertAlmostEqual(row["median"], 5)
        self.assertAlmostEqual(row["pct_le_1"], 20)
        self.assertAlmostEqual(row["pct_lt_5"], 40)
        self.assertAlmostEqual(row["pct_ge_8"], 40)
        self.assertAlmostEqual(row["pct_ge_9"], 20)

    def test_unknown_columns_fail_closed(self):
        with self.assertRaises(ValueError):
            tidy_year(pd.DataFrame({"student_id": [1], "province_code": [10]}), 2023)

if __name__ == "__main__":
    unittest.main()
