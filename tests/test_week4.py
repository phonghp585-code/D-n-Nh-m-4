"""Boundary, traceability and preservation checks for Week 4."""
import unittest

import numpy as np
import pandas as pd

from src.analyze_week4 import (COLUMNS, SCORES, detect_column, detect_outliers,
                               normalize_text, select_top5, standardize)


class Week4Tests(unittest.TestCase):
    def test_generated_notebook_cells_compile(self):
        from src.build_week4_notebook import build_cells
        cells = [cell for cell in build_cells() if cell['cell_type'] == 'code']
        self.assertGreater(len(cells), 0)
        for index, cell in enumerate(cells):
            with self.subTest(cell=index):
                compile(''.join(cell['source']), f'cell {index}', 'exec')

    def test_iqr_strict_boundary(self):
        # Q1=2, Q3=4, fences -1 and 7. Both exact boundaries stay unflagged.
        s = pd.Series([-2., -1., 2., 2., 3., 4., 4., 7., 8., np.nan])
        stats, a, _, _ = detect_column(s)
        self.assertEqual((stats['q1'], stats['q3']), (2, 4))
        self.assertEqual(a.tolist(), [True, False, False, False, False, False, False, False, True, False])
        self.assertEqual(stats['n_observed'], 9)

    def test_z_exact_three_is_not_flagged_and_null_excluded(self):
        stats, _, flag, z = detect_column(pd.Series([0.] * 9 + [10., np.nan]))
        self.assertEqual(z.iloc[9], 3.)
        self.assertEqual(stats['std_population'], 3.)
        self.assertFalse(flag.any())
        _, _, flag, z = detect_column(pd.Series([0.] * 10 + [10., np.nan]))
        self.assertGreater(z.iloc[10], 3)
        self.assertEqual(int(flag.sum()), 1)
        self.assertFalse(flag.iloc[-1])

    def test_empty_constant_single_and_zero_iqr(self):
        for series in (pd.Series([], dtype=float), pd.Series([np.nan]), pd.Series([5.]), pd.Series([5.] * 8)):
            _, a, b, z = detect_column(series)
            self.assertFalse(a.any())
            self.assertFalse(b.any())
            self.assertTrue(z.isna().all())
        stats, a, _, _ = detect_column(pd.Series([1.] * 9 + [2.]))
        self.assertEqual(stats['iqr'], 0)
        self.assertEqual(stats['status'], 'zero_iqr; literal_fences')
        self.assertEqual(int(a.sum()), 1)

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError, 'hữu hạn'):
            detect_column(pd.Series([1., np.inf]))

    def test_top5_deduplicates_and_breaks_ties(self):
        details = pd.DataFrame({
            'Student ID': ['00000003', '00000001', '00000001', '00000002', '00000004', '00000005', '00000006'],
            'column': ['Z', 'Z', 'A', 'B', 'A', 'A', 'A'],
            'abs_z': [5., 6., 6., 6., 4., 3.5, 3.1],
        })
        result = select_top5(details)
        self.assertEqual(result['Student ID'].tolist(), ['00000001', '00000002', '00000003', '00000004', '00000005'])
        self.assertEqual(result.iloc[0]['column'], 'A')
        self.assertEqual(len(select_top5(details.iloc[:0])), 0)

    def test_normalization_null_unicode_and_idempotence(self):
        ids = pd.Series([' ０１０００００１ ', '0100  0002', pd.NA], dtype='string')
        result = normalize_text(ids)
        self.assertEqual(result.iloc[0], '01000001')
        self.assertEqual(result.iloc[1], '0100 0002')
        self.assertTrue(pd.isna(result.iloc[2]))
        pd.testing.assert_series_equal(result, normalize_text(result))
        codes = normalize_text(pd.Series([' n1 ', 'Ｎ２', pd.NA, '   '], dtype='string'), uppercase=True)
        self.assertEqual(codes.iloc[:2].tolist(), ['N1', 'N2'])
        self.assertTrue(codes.iloc[2:].isna().all())

    def test_text_summary_counts_and_preserves_scores(self):
        df = pd.DataFrame({c: [0., np.nan, 7.] for c in SCORES})
        df['Student ID'] = pd.Series(['01000001', ' 01000002 ', '0100 003'], dtype='string')
        df['Foreign language code'] = pd.Series([' n1 ', 'N1', pd.NA], dtype='string')
        df = df[COLUMNS]
        cleaned, summary, issues = standardize(df)
        pd.testing.assert_frame_equal(df[SCORES], cleaned[SCORES])
        codes = summary.set_index('column').loc['Foreign language code']
        self.assertEqual((codes['distinct_before'], codes['distinct_after'], codes['changed_rows']), (2, 1, 1))
        self.assertEqual(codes['missing_after'], 1)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues.iloc[0]['after'], '0100 003')

    def test_detail_rows_match_summary(self):
        df = pd.DataFrame({c: [5.] * 10 + [0.] for c in SCORES})
        df['Student ID'] = [f'{i:08d}' for i in range(len(df))]
        comparison, details = detect_outliers(df)
        self.assertEqual(len(details), 9)
        self.assertEqual(details['Student ID'].nunique(), 1)
        self.assertEqual(set(details['source_row']), {12})
        self.assertEqual(comparison['either_n'].sum(), len(details))
        self.assertTrue(details['iqr_flag'].all() and details['z_flag'].all())


if __name__ == '__main__':
    unittest.main()
