import json
from pathlib import Path
import unittest
import numpy as np
from src.verify_external_scores import right_closed_counts


class ExternalScoreTests(unittest.TestCase):
    def test_histogram_includes_zero_and_keeps_right_boundary(self):
        counts=right_closed_counts([0,.25,.250001,.5,10],.25)
        self.assertEqual(len(counts),40)
        self.assertEqual(counts[:2].tolist(),[2,2])
        self.assertEqual(counts[-1],1)
        self.assertEqual(counts.sum(),5)

    def test_math_half_point_histogram_preserves_exact_threshold(self):
        counts=right_closed_counts([0,.5,1,9.5,10],.5)
        self.assertEqual(counts[:2].tolist(),[2,1])
        self.assertEqual(counts[-2:].tolist(),[1,1])

    def test_transcribed_reference_histograms_reconcile_with_published_counts(self):
        path=Path(__file__).resolve().parents[1]/'data/external/verification/official_reference.json'
        reference=json.loads(path.read_text(encoding='utf-8'))
        records=[row for row in reference['records'] if row['year']==2025]
        self.assertEqual(len(records),12)
        for row in records:
            counts=row['histogram_right_closed_counts']
            self.assertEqual(sum(counts),row['n'],row['subject'])
            self.assertEqual(len(counts)*row['histogram_step'],10)
            self.assertTrue(np.greater_equal(counts,0).all())


if __name__=='__main__': unittest.main()
