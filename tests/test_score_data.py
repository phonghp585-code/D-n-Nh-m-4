"""Input-contract tests for the CT2006/CT2018 comparison."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.score_data import COHORT_LABELS, load_scores, valid_numeric


class ScoreDataTests(unittest.TestCase):
    def write_csv(self, data):
        folder = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'tmp')
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / 'scores.csv'
        pd.DataFrame(data).to_csv(path, index=False)
        return path

    def test_zero_missing_and_invalid_remain_distinct(self):
        got = valid_numeric(pd.Series([0, 10, '', None, -1, 11, np.inf, 'bad']))
        self.assertEqual(got.iloc[:2].tolist(), [0, 10])
        self.assertTrue(got.iloc[2:].isna().all())

    def test_2023_mapping_preserves_id_and_filters_english(self):
        path = self.write_csv({'Student ID':['01000001','01000002'],
            'Mathematics':[0,8], 'Literature':[7,6],
            'Foreign language':[9,8], 'Foreign language code':['N1','N4'],
            'Civic education':[8,9]})
        frame, audit = load_scores(path, 2023)
        self.assertEqual(frame.student_id.tolist(), ['01000001','01000002'])
        self.assertEqual(frame['math'].iloc[0], 0)
        self.assertEqual(frame.english.iloc[0], 9)
        self.assertTrue(pd.isna(frame.english.iloc[1]))
        self.assertTrue(frame.economics_law.isna().all())
        self.assertEqual(frame.civics.tolist(), [8,9])
        self.assertEqual(audit['rows'], 2)
        self.assertEqual(frame.cohort.unique().tolist(), [COHORT_LABELS[2023]])

    def test_2025_invalid_scores_audited_and_stored_totals_kept(self):
        path = self.write_csv({'sbd':['01000001','01000002'],
            'toan':[5,11], 'hoa_hoc':[6,7], 'sinh_hoc':[8,9],
            'ngoai_ngu':[7,6], 'ma_ngoai_ngu':['N1','N4'],
            'tieng_anh':[7,None], 'diem_B00':[19,27]})
        frame, audit = load_scores(path,2025)
        self.assertTrue(pd.isna(frame['math'].iloc[1]))
        self.assertEqual(frame.stored_B00.tolist(),[19,27])
        self.assertEqual(audit['invalid_scores']['math'],1)
        self.assertEqual(audit['curriculum_confirmation'],'user-confirmed CT2018-only')

    def test_duplicate_or_invalid_ids_fail_instead_of_silent_dedup(self):
        for ids in [['01000001','01000001'], ['1000001','01000002']]:
            with self.subTest(ids=ids):
                path=self.write_csv({'sbd':ids,'toan':[5,6]})
                with self.assertRaises(ValueError): load_scores(path,2025)

    def test_english_mismatch_detected(self):
        path=self.write_csv({'sbd':['01000001'],'ngoai_ngu':[7],
                            'ma_ngoai_ngu':['N1'],'tieng_anh':[9]})
        with self.assertRaisesRegex(ValueError,'English'): load_scores(path,2025)

    def test_raw_stored_total_parse_error_is_not_erased_before_validation(self):
        path=self.write_csv({'sbd':['01000001'],'toan':[None],
                             'hoa_hoc':[7],'sinh_hoc':[8],'diem_B00':['bad']})
        frame,_=load_scores(path,2025)
        self.assertEqual(frame.stored_B00.iloc[0],'bad')
        from src.analyze_combinations import _validation, combination_scores
        checked=_validation(2025,'B00',frame,combination_scores(frame,'B00'))
        self.assertEqual(checked['n_invalid_stored'],1)
        self.assertEqual(checked['status'],'mismatch')

    def test_lfs_pointer_fails_with_actionable_error(self):
        folder=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'tmp'); self.addCleanup(folder.cleanup)
        path=Path(folder.name)/'pointer.csv'
        path.write_text('version https://git-lfs.github.com/spec/v1\noid sha256:abc\n',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'LFS'): load_scores(path,2025)


if __name__=='__main__': unittest.main()
