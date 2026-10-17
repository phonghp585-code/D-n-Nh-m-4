"""Hand-computed fixtures for complete-case combinations and observed participation."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.analyze_combinations import (
    analyze_combinations,
    combination_scores,
    nearest_rank,
)
from src.score_data import ALL_COMBINATIONS, combination_subjects


SUBJECTS = (
    "math literature english physics chemistry biology history geography civics "
    "economics_law informatics technology foreign_language"
).split()


def cohort(year, records):
    frame = pd.DataFrame(records)
    for subject in SUBJECTS:
        if subject not in frame:
            frame[subject] = np.nan
    frame["student_id"] = [f"{i:08d}" for i in range(len(frame))]
    frame["year"] = year
    return frame


class CombinationMathTests(unittest.TestCase):
    def test_all_24_codes_match_the_nhan_dataset_columns(self):
        expected='A00 A01 A02 A08 A09 B00 B08 C00 C01 C02 C03 C04 C14 C19 C20 D01 D07 D08 D09 D10 D14 D15 D66 D84'.split()
        self.assertEqual(list(ALL_COMBINATIONS),expected)

    def test_changed_civics_subject_uses_correct_cohort_without_conflation(self):
        old=cohort(2023,[{'math':1,'history':2,'civics':3,'economics_law':9}])
        new=cohort(2025,[{'math':1,'history':2,'civics':3,'economics_law':9}])
        self.assertEqual(combination_scores(old,'A08').iloc[0],6)
        self.assertEqual(combination_scores(new,'A08').iloc[0],12)
        self.assertIn('civics',combination_subjects('C19',2023))
        self.assertIn('economics_law',combination_subjects('C19',2025))

    def test_complete_case_sum_keeps_zero_and_rejects_invalid_components(self):
        frame = cohort(2023, [
            {"math": 0, "physics": 5, "chemistry": 7},
            {"math": 8, "physics": np.nan, "chemistry": 7},
            {"math": 11, "physics": 5, "chemistry": 7},
            {"math": 8, "physics": np.inf, "chemistry": 7},
        ])
        actual = combination_scores(frame, "A00")
        self.assertEqual(actual.iloc[0], 12)
        self.assertTrue(actual.iloc[1:].isna().all())
        self.assertTrue(pd.isna(frame.loc[1, "physics"]))

    def test_nearest_rank_observed_cutoff_and_boundaries(self):
        self.assertEqual(nearest_rank([1, 2, 3, 4, 10], 0.8), 4)
        self.assertEqual(nearest_rank([1, 2, 3, 4, 10], 0.9), 10)
        self.assertTrue(np.isnan(nearest_rank([], 0.8)))
        with self.assertRaises(ValueError):
            nearest_rank([1], 0)

    def test_equal_decimal_totals_remain_tied_despite_binary_roundoff(self):
        frame = cohort(2023, [
            {"math": 0, "physics": .3, "chemistry": .3},
            {"math": .1, "physics": .2, "chemistry": .3},
        ])
        scores = combination_scores(frame, "A00")
        self.assertEqual(scores.nunique(), 1)
        self.assertEqual(scores.iloc[0], .6)


class CombinationOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary_root = Path(__file__).resolve().parents[1] / "tmp"
        temporary_root.mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=temporary_root)
        cls.output = Path(cls.temp.name)
        cls.frames = {
            2023: cohort(2023, [
                {"math": 0, "physics": 0, "chemistry": 0, "biology": 0},
                {"math": 5, "physics": 5, "chemistry": 5},
                {"math": 8, "physics": 8, "chemistry": 8},
                {"math": 8, "physics": 8, "chemistry": 8},
                {"foreign_language": 7},
                {},
            ]),
            2025: cohort(2025, [
                {"math": 6, "physics": 6, "chemistry": 6, "stored_A00": 18,
                 "english": 9, "foreign_language": 9, "informatics": 8},
                {"math": 9, "physics": 9, "chemistry": 9, "stored_A00": 26},
                {"math": 4, "chemistry": 5, "stored_A00": 9},
                {},
            ]),
        }
        cls.metadata = analyze_combinations(cls.frames, cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def table(self, name):
        return pd.read_csv(self.output / name)

    def test_summary_and_deltas_use_complete_cases_and_sample_sd(self):
        summary = self.table("combination_summary.csv")
        a = summary.query("year == 2023 and combination == 'A00'").iloc[0]
        self.assertEqual(a["n"], 4)
        self.assertEqual(a["denominator"], 5)
        self.assertEqual(a["mean"], 15.75)
        self.assertAlmostEqual(a["sd"], 11.324751652906125)
        self.assertEqual(a["median"], 19.5)
        self.assertEqual(a["pct_ge_24"], 50)
        self.assertEqual(a["cohort"], "2023 — CT2006")
        delta = self.table("combination_deltas.csv").query("combination == 'A00'").iloc[0]
        self.assertEqual(delta["delta_mean"], 6.75)
        self.assertEqual(delta["cohort_to"], "2025 — CT2018")

    def test_top_threshold_includes_all_ties_and_strict_exceedance(self):
        row = self.table("top_thresholds.csv").query(
            "year == 2023 and combination == 'A00' and quantile == 0.8"
        ).iloc[0]
        self.assertEqual(row["threshold"], 24)
        self.assertEqual(row["n_at"], 2)
        self.assertEqual(row["n_gt"], 0)
        self.assertEqual(row["n_ge"], 2)
        self.assertEqual(row["pct_ge"], 50)

    def test_participation_denominator_counts_foreign_language_once(self):
        participation = self.table("participation.csv")
        english = participation.query("year == 2025 and subject == 'english'").iloc[0]
        self.assertEqual(english["denominator"], 3)
        self.assertEqual(english["denominator_all_rows"], 4)
        self.assertEqual(english["n"], 1)
        self.assertAlmostEqual(english["percent"], 100 / 3)
        self.assertEqual(english["percent_all_rows"], 25)
        self.assertFalse(((participation.year == 2023) & (participation.subject == "informatics")).any())
        info = participation.query("year == 2025 and subject == 'informatics'").iloc[0]
        self.assertEqual(info["comparability"], "new_2025")
        counts = self.table("score_count_distribution.csv")
        row = counts.query("year == 2025 and count_type == 'exam' and score_count == 5").iloc[0]
        self.assertEqual(row["n"], 1)

    def test_cooccurrence_includes_optional_new_subjects_and_zero_scores(self):
        rows = self.table("cooccurrence.csv")
        row = rows.query("year == 2025 and subject_x == 'physics' and subject_y == 'informatics'").iloc[0]
        self.assertEqual(row["n"], 1)
        row = rows.query("year == 2023 and subject_x == 'chemistry' and subject_y == 'biology'").iloc[0]
        self.assertEqual(row["n"], 1)

    def test_participation_changes_use_percentage_points_and_exclude_changed_subjects(self):
        rows = self.table("participation_deltas.csv")
        math = rows.query("subject == 'math'").iloc[0]
        self.assertEqual(math["delta_n"], -1)
        self.assertEqual(math["percent_from"], 80)
        self.assertEqual(math["percent_to"], 100)
        self.assertEqual(math["delta_percent"], 20)
        self.assertEqual(math["cohort_from"], "2023 — CT2006")
        self.assertNotIn("informatics", set(rows.subject))
        self.assertNotIn("economics_law", set(rows.subject))

    def test_stored_validation_detects_sum_and_missingness_mismatches(self):
        row = self.table("combination_validation.csv").query(
            "year == 2025 and combination == 'A00'"
        ).iloc[0]
        self.assertEqual(row["n_recomputed"], 2)
        self.assertEqual(row["n_stored"], 3)
        self.assertEqual(row["n_missingness_mismatch"], 1)
        self.assertEqual(row["n_sum_mismatch"], 1)
        self.assertEqual(row["status"], "mismatch")

    def test_artifacts_exist_and_metadata_is_strict_json(self):
        encoded = json.dumps(self.metadata, allow_nan=False)
        self.assertIn("nearest_rank", encoded)
        for name in ["combination_hist_ecdf.png", "combination_boxplots.png",
                     "top_threshold_comparison.png", "participation.png"]:
            path = self.output / "figures" / name
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 1000)

    def test_full_24_coverage_and_changed_content_flags(self):
        summary=self.table('combination_summary.csv')
        self.assertEqual(len(summary),48)
        self.assertEqual(len(self.table('combination_deltas.csv')),24)
        self.assertEqual(len(self.table('top_thresholds.csv')),96)
        self.assertEqual(len(self.table('combination_validation.csv')),48)
        self.assertEqual(set(summary.combination),set(ALL_COMBINATIONS))
        changed=summary[summary.combination=='A08'].set_index('year')
        self.assertIn('GDCD',changed.loc[2023,'subjects'])
        self.assertIn('GDKT&PL',changed.loc[2025,'subjects'])
        self.assertTrue(changed.comparison_class.eq('changed_subject_content').all())
        self.assertEqual(self.table('combination_mapping.csv').shape[0],48)

    def test_source_multi_label_membership_checks_each_combination(self):
        from src.analyze_combinations import audit_membership
        frame=cohort(2025,[{'math':8,'literature':8.25,'physics':8.5,'chemistry':6.75}])
        frame['source_combinations']='A00, C01, C02'
        scores={code:combination_scores(frame,code) for code in ALL_COMBINATIONS}
        validation,distribution=audit_membership(frame,2025,scores)
        self.assertEqual(sum(row['n_disagreement'] for row in validation),0)
        self.assertEqual(distribution[0]['n_eligible_combinations'],3)
        frame['source_combinations']='A00'
        validation,_=audit_membership(frame,2025,scores)
        self.assertEqual(sum(row['n_disagreement'] for row in validation),2)


if __name__ == "__main__":
    unittest.main()
