"""Focused checks for source interpretation and imputation safeguards."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.analyze import SCORES, analyze_missing_layers, audit, derive_observed_groups, impute_masked_math, profile_columns


class AnalysisTests(unittest.TestCase):
    def test_observed_group_is_based_on_published_subjects(self) -> None:
        df = pd.DataFrame({col: [np.nan] * 4 for col in SCORES})
        df.loc[0, "Physics"] = 0.0  # Zero is an observed, valid score.
        df.loc[1, "History"] = 8.0
        df.loc[2, ["Chemistry", "Geography"]] = [5.0, 6.0]
        groups = derive_observed_groups(df)
        self.assertEqual(groups["observed_exam_group"].tolist(), [
            "science_only", "social_only", "both_observed", "neither_observed",
        ])

    def test_masked_scores_do_not_influence_fitted_medians(self) -> None:
        truth = np.array([2.0, 10.0, 6.0, 8.0])
        labels = np.array(["science_only", "science_only", "social_only", "neither_observed"])
        mask = np.array([False, True, False, True])
        result = impute_masked_math(truth, labels, mask, min_group_observed=1)
        self.assertEqual(result["global_median"], 4.0)
        self.assertEqual(result["group_medians"], {"science_only": 2.0, "social_only": 6.0})
        self.assertEqual(result["global_values"].tolist(), [2.0, 4.0, 6.0, 4.0])
        self.assertEqual(result["group_values"].tolist(), [2.0, 2.0, 6.0, 4.0])
        self.assertEqual(result["fallback_count"], 1)

    def test_duplicate_id_conflict_and_leading_zero(self) -> None:
        df = pd.DataFrame({col: [np.nan, np.nan] for col in SCORES})
        df["Student ID"] = pd.Series(["01000001", "01000001"], dtype="string")
        df["Foreign language code"] = pd.Series([pd.NA, pd.NA], dtype="string")
        df.loc[0, "Mathematics"] = 0.0
        df.loc[1, "Mathematics"] = 10.0
        groups = derive_observed_groups(df)
        result = audit(df, groups, profile_columns(df))
        self.assertEqual(result["student_id_duplicate_extra_rows"], 1)
        self.assertEqual(result["student_id_conflicting_groups"], 1)
        self.assertEqual(result["invalid_student_id_format"], 0)
        self.assertEqual(result["out_of_range_or_nonfinite_scores"]["Mathematics"], 0)

    def test_no_donors_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "No observed Math scores"):
            impute_masked_math(
                np.array([np.nan, np.nan]),
                np.array(["science_only", "social_only"]),
                np.array([True, True]),
            )

    def test_structural_candidates_and_exact_missing_patterns_reconcile(self) -> None:
        df = pd.DataFrame({col: [np.nan] * 5 for col in SCORES})
        df["Student ID"] = pd.Series([f"0100000{i}" for i in range(1, 6)], dtype="string")
        df["Foreign language code"] = pd.Series([pd.NA, pd.NA, pd.NA, "N1", pd.NA], dtype="string")
        df.loc[0, ["Mathematics", "Foreign language", "Physics", "Chemistry"]] = [5, 6, 0, 7]
        df.loc[1, ["Mathematics", "Literature", "History", "Geography"]] = [6, 7, 4, 5]
        df.loc[3, ["Mathematics", "Foreign language"]] = [4, 2]
        df.loc[4, ["Physics", "History"]] = [1, 2]
        groups = derive_observed_groups(df)
        with patch("pandas.DataFrame.to_csv"):
            result = analyze_missing_layers(df, groups)
        self.assertEqual(sum(row["n"] for row in result["raw_nine_score_missing_counts"]), 5)
        self.assertEqual(sum(row["n"] for row in result["context_six_score_missing_counts"]), 2)
        self.assertEqual(result["only_student_id_rows"], 1)
        by_col = {row["column"]: row for row in result["missing_context_classification"]}
        self.assertEqual(by_col["Physics"]["structural_candidate_opposite_group_n"], 1)
        self.assertEqual(by_col["Civic education"]["structural_candidate_opposite_group_n"], 1)
        self.assertEqual(by_col["Biology"]["unresolved_observed_group_n"], 2)
        patterns = result["context_missing_subject_patterns"]
        self.assertEqual(sum(row["n"] for row in patterns), 2)
        self.assertEqual({row["missing_subjects"] for row in patterns},
                         {"Literature | Biology", "Foreign language | Civic education"})


if __name__ == "__main__":
    unittest.main()
