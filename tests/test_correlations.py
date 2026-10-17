"""Regression checks for the descriptive, pairwise correlation analysis."""
import importlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd


SUBJECTS = ("math", "literature", "english", "physics", "chemistry", "biology", "history", "geography")


def scores(**columns):
    n = len(next(iter(columns.values())))
    frame = pd.DataFrame({subject: np.full(n, np.nan) for subject in SUBJECTS})
    for key, values in columns.items():
        frame[key] = values
    return frame


class CorrelationTests(unittest.TestCase):
    def setUp(self):
        module_path = Path(__file__).parents[1] / "src" / "analyze_correlations.py"
        self.assertTrue(module_path.exists(), "The correlation analysis feature must exist")
        self.analysis = importlib.import_module("src.analyze_correlations")

    def pair(self, table, x="math", y="physics"):
        return table.loc[(table.subject_x == x) & (table.subject_y == y)].iloc[0]

    def test_spearman_ranks_only_the_paired_subset_with_average_ties(self):
        frame = scores(math=[0, 1, 2, 3, 4], physics=[0, np.nan, np.nan, 1, 1])
        result = self.pair(self.analysis.calculate_pairwise(frame, 2023, min_pair_n=3))
        self.assertEqual(result.n_pair, 3)
        self.assertAlmostEqual(result.spearman_rho, np.sqrt(3) / 2)
        self.assertAlmostEqual(result.pearson_r, np.corrcoef([0, 3, 4], [0, 1, 1])[0, 1])

    def test_low_support_and_constant_pairs_remain_undefined_with_support(self):
        table = self.analysis.calculate_pairwise(scores(math=[0, 1, 2], physics=[5, 5, 5]), 2025)
        pair = self.pair(table)
        self.assertEqual(pair.n_pair, 3)
        self.assertEqual(pair.status, "insufficient_n")
        self.assertTrue(np.isnan(pair.pearson_r))
        table = self.analysis.calculate_pairwise(scores(math=[0, 1, 2], physics=[5, 5, 5]), 2025, 3)
        pair = self.pair(table)
        self.assertEqual(pair.status, "constant")
        self.assertTrue(np.isnan(pair.spearman_rho))
        empty = self.pair(table, "math", "biology")
        self.assertEqual(empty.n_pair, 0)
        self.assertTrue(np.isnan(empty.pearson_r))

    def test_invalid_scores_excluded_zero_preserved_and_matrix_symmetric(self):
        frame = scores(math=[0, 2, np.inf, 4, 11, -1], physics=[0, 2, 3, 4, 5, 6])
        table = self.analysis.calculate_pairwise(frame, 2023, 3)
        self.assertEqual(len(table), 64)
        forward = self.pair(table)
        backward = self.pair(table, "physics", "math")
        self.assertEqual(forward.n_pair, 3)
        self.assertAlmostEqual(forward.pearson_r, 1)
        self.assertEqual(forward.pearson_r, backward.pearson_r)
        self.assertEqual(forward.cohort, "2023 — CT2006")

    def test_default_support_threshold_includes_exactly_one_hundred(self):
        frame = scores(math=np.linspace(0, 10, 100), physics=np.linspace(10, 0, 100))
        pair = self.pair(self.analysis.calculate_pairwise(frame, 2023))
        self.assertEqual(pair.status, "ok")
        self.assertAlmostEqual(pair.pearson_r, -1)

    def test_high_score_thresholds_baseline_and_ties_use_same_paired_set(self):
        frame = scores(math=[0, 1, 2, 3, 4, 10], physics=[0, 1, 2, 3, 3, np.nan])
        result = self.pair(self.analysis.calculate_high_score(frame, 2025))
        self.assertEqual(result.n_pair, 5)
        self.assertEqual(result.p80_x, 3)
        self.assertEqual(result.p80_y, 3)
        self.assertEqual(result.n_x_high, 2)
        self.assertEqual(result.n_y_high, 2)
        self.assertEqual(result.n_x_at_threshold, 1)
        self.assertEqual(result.n_y_at_threshold, 2)
        self.assertAlmostEqual(result.baseline_probability, 0.4)
        self.assertAlmostEqual(result.conditional_probability, 1)

    def test_group_sensitivity_uses_complete_combination_subset(self):
        frame = scores(math=[0, 1, 2, 3], physics=[0, 1, 2, 0], chemistry=[0, 1, 2, np.nan])
        table = self.analysis.calculate_group_sensitivity(frame, 2023, 3)
        result = self.pair(table.loc[table.combination == "A00"])
        self.assertEqual(result.n_pair, 3)
        self.assertAlmostEqual(result.pearson_r, 1)
        self.assertEqual(set(table.combination), {"A00", "A01", "B00", "C00", "D01"})
        self.assertEqual(len(table), 15)

    def test_pipeline_writes_cohort_tables_unique_deltas_and_figures(self):
        first = scores(**{subject: [0, 1, 2, 3, 4] for subject in SUBJECTS})
        second = first.copy()
        second["physics"] = [4, 3, 2, 1, 0]
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / "tmp") as directory:
            metadata = self.analysis.analyze_correlations({2023: first, 2025: second}, directory, 3)
            json.dumps(metadata, allow_nan=False)
            output = Path(directory)
            pairs = pd.read_csv(output / "pairwise_correlations.csv")
            self.assertEqual(len(pairs), 128)
            deltas = pd.read_csv(output / "correlation_deltas.csv")
            self.assertEqual(len(deltas), 28)
            row = self.pair(deltas)
            self.assertAlmostEqual(row.delta_pearson_r, -2)
            self.assertEqual(row.cohort_from, "2023 — CT2006")
            self.assertEqual(row.cohort_to, "2025 — CT2018")
            self.assertEqual(len(pd.read_csv(output / "group_sensitivity.csv")), 30)
            self.assertEqual(len(pd.read_csv(output / "high_score_concordance.csv")), 6)
            self.assertEqual(len(list((output / "figures").glob("*.png"))), 12)
            self.assertTrue((output / "correlation_metadata.json").exists())


if __name__ == "__main__":
    unittest.main()
