"""Week 5 pipeline guardrails: provenance, cleaning rules and safe integration."""
import unittest
from pathlib import Path

import pandas as pd

from src.analyze_week4 import COLUMNS, SCORES, TEXT, normalize_text
from src.analyze_week5 import (exact_duplicate_rows, id_conflicts,
                                left_merge_council, observed_exam_group,
                                missing_by_observed_group, diagnose_raw_csv,
                                score_domain_issues)


class Week5Tests(unittest.TestCase):
    def test_normalization_preserves_zero_prefixed_ids_nulls_and_is_idempotent(self):
        ids = pd.Series([" ０１０００００１ ", "01000002", pd.NA], dtype="string")
        once = normalize_text(ids)
        twice = normalize_text(once)
        self.assertEqual(once.iloc[0], "01000001")
        self.assertEqual(once.iloc[1], "01000002")
        self.assertTrue(pd.isna(once.iloc[2]))
        pd.testing.assert_series_equal(once, twice)
        self.assertTrue(once.str.fullmatch(r"[0-9]{8}").fillna(True).all())

    def test_exact_duplicate_removal_keeps_first_physical_row(self):
        frame = pd.DataFrame({col: [pd.NA, pd.NA] for col in COLUMNS})
        frame["Student ID"] = pd.Series(["01000001", "01000001"], dtype="string")
        frame["Mathematics"] = [0.0, 0.0]
        source_rows = pd.Series([2, 3], index=frame.index, name="source_row")
        duplicate, removed = exact_duplicate_rows(frame, source_rows)
        self.assertEqual(duplicate.tolist(), [False, True])
        self.assertEqual(removed["source_row"].tolist(), [3])
        self.assertEqual(removed["Student ID"].tolist(), ["01000001"])

    def test_conflicting_id_rows_are_not_silently_collapsed(self):
        frame = pd.DataFrame({col: [pd.NA, pd.NA] for col in COLUMNS})
        frame["Student ID"] = pd.Series(["01000001", "01000001"], dtype="string")
        frame["Mathematics"] = [0.0, 1.0]
        conflicts = id_conflicts(frame, pd.Series([2, 3], index=frame.index))
        self.assertEqual(len(conflicts), 2)
        self.assertEqual(conflicts["Student ID"].nunique(), 1)

    def test_left_merge_preserves_rows_order_and_reports_unmatched(self):
        main = pd.DataFrame({
            "Student ID": pd.Series(["01000001", "65000002", "20000003"], dtype="string"),
            "exam_year": [2023, 2023, 2023],
            "exam_council_code": pd.Series(["01", "65", "20"], dtype="string"),
        })
        reference = pd.DataFrame({
            "exam_year": [2023, 2023],
            "exam_council_code": pd.Series(["01", "65"], dtype="string"),
            "exam_council_name": ["Hà Nội", "Cục Nhà trường"],
        })
        result = left_merge_council(main, reference)
        self.assertEqual(len(result), len(main))
        self.assertEqual(result["Student ID"].tolist(), main["Student ID"].tolist())
        self.assertEqual(result["_merge_indicator"].astype(str).tolist(), ["both", "both", "left_only"])
        self.assertTrue(pd.isna(result.loc[2, "exam_council_name"]))

    def test_merge_rejects_duplicate_reference_keys(self):
        main = pd.DataFrame({"exam_year": [2023],
                             "exam_council_code": pd.Series(["01"], dtype="string")})
        reference = pd.DataFrame({"exam_year": [2023, 2023],
                                  "exam_council_code": pd.Series(["01", "01"], dtype="string"),
                                  "exam_council_name": ["A", "B"]})
        with self.assertRaisesRegex(ValueError, "duy nhất"):
            left_merge_council(main, reference)

    def test_merge_rejects_missing_reference_keys(self):
        main = pd.DataFrame({"exam_year": [2023],
                             "exam_council_code": pd.Series(["01"], dtype="string")})
        reference = pd.DataFrame({"exam_year": [2023],
                                  "exam_council_code": pd.Series([pd.NA], dtype="string"),
                                  "exam_council_name": ["A"]})
        with self.assertRaisesRegex(ValueError, "bị thiếu"):
            left_merge_council(main, reference)

    def test_score_domain_keeps_zero_and_ten_but_reports_out_of_range(self):
        frame = pd.DataFrame({col: [pd.NA, pd.NA, pd.NA] for col in COLUMNS})
        frame["Student ID"] = pd.Series(["01000001", "01000002", "01000003"], dtype="string")
        frame["Mathematics"] = [0.0, 10.0, -0.01]
        issues = score_domain_issues(frame, pd.Series([2, 3, 4], index=frame.index))
        self.assertEqual(issues["source_row"].tolist(), [4])
        self.assertEqual(issues["value"].tolist(), [-0.01])

    def test_generated_notebook_code_cells_compile(self):
        from src.build_week5_notebook import cells
        code_cells = [cell for cell in cells() if cell["cell_type"] == "code"]
        self.assertGreater(len(code_cells), 0)
        for index, cell in enumerate(code_cells):
            with self.subTest(cell=index):
                compile("".join(cell["source"]), f"Week 5 cell {index}", "exec")

    def test_observed_subject_group_uses_nullness_without_claiming_registration(self):
        frame = pd.DataFrame({
            "Physics": [1.0, None, 1.0, None],
            "Chemistry": [None, None, None, None],
            "Biology": [None, None, None, None],
            "History": [None, 1.0, 1.0, None],
            "Geography": [None, None, None, None],
            "Civic education": [None, None, None, None],
        })
        result = observed_exam_group(frame)
        self.assertEqual(result.tolist(), ["science_only", "social_only", "both_observed", "neither_observed"])

    def test_missing_context_counts_reconcile_without_claiming_cause(self):
        frame = pd.DataFrame({col: [None, None, None, None] for col in SCORES})
        frame.loc[0, "Physics"] = 0.0
        frame.loc[1, "History"] = 1.0
        frame.loc[2, ["Physics", "History"]] = [2.0, 3.0]
        detail, summary = missing_by_observed_group(frame)
        self.assertEqual(len(detail), 36)
        self.assertEqual(int(summary["missing_score_cells"].sum()), int(frame[SCORES].isna().sum().sum()))
        self.assertEqual(int(summary["structural_candidate_cells"].sum()), 6)
        self.assertEqual(int(summary["unresolved_cells"].sum()), int(frame[SCORES].isna().sum().sum()) - 6)

    def test_parse_diagnostic_identifies_physical_row_and_score_token(self):
        path = Path(__file__).resolve().parents[1] / "outputs/_week5_parse_test_bad.csv"
        try:
            path.write_text(",".join(COLUMNS) + "\n" +
                            ",".join(["01000001", "oops", *([""] * (len(COLUMNS) - 2))]) + "\n",
                            encoding="utf-8")
            issues = diagnose_raw_csv(path)
            self.assertEqual(issues.loc[0, "source_row"], 2)
            self.assertEqual(issues.loc[0, "column"], "Mathematics")
            self.assertEqual(issues.loc[0, "raw_token"], "oops")
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
