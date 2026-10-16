import unittest
import pandas as pd
from src.week6_score_distribution import tidy_year, summarize

class TestScoreDistribution(unittest.TestCase):
    def test_alias_mapping_and_range(self):
        df=pd.DataFrame({"Mathematics":[0,1,5,8,9,10,11,None],"Literature":[4,5,6,7,8,9,10,None]})
        got=tidy_year(df,2023)
        self.assertIn("Toán",got.columns)
        self.assertEqual(got["Toán"].notna().sum(),6)
        self.assertTrue(got["Toán"].dropna().between(0,10).all())
    def test_thresholds_and_statistics(self):
        long=pd.DataFrame({"year":[2023]*5,"subject":["Toán"]*5,"score":[0,2,5,8,10]})
        s=summarize(long).iloc[0]
        self.assertEqual(s["n"],5)
        self.assertAlmostEqual(s["mean"],5)
        self.assertAlmostEqual(s["pct_le_1"],20)
        self.assertAlmostEqual(s["pct_lt_5"],40)
        self.assertAlmostEqual(s["pct_ge_8"],40)
        self.assertAlmostEqual(s["pct_ge_9"],20)
if __name__=="__main__": unittest.main()
