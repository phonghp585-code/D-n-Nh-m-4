"""Boundary and sample-size checks for the distribution evidence."""
import unittest
import numpy as np
import pandas as pd
from src.subject_distribution_evidence import summarize, band_summary, BINS


class DistributionEvidenceTests(unittest.TestCase):
    def test_thresholds_keep_zero_and_exact_cutoffs(self):
        stats=summarize(pd.Series([0, 5, 8, 9, 10, np.nan]))
        self.assertEqual(stats['n'], 5)
        self.assertEqual(stats['mean'], 6.4)
        self.assertEqual(stats['median'], 8)
        self.assertEqual(stats['pct_lt5'], 20)
        self.assertEqual(stats['pct_ge8'], 60)
        self.assertEqual(stats['pct_ge9'], 40)
        self.assertEqual(stats['n_ge9'], 2)
        self.assertEqual(stats['n_eq10'], 1)
        counts, _=np.histogram([0, .5, 5, 8, 9, 10], bins=BINS)
        self.assertEqual(counts.sum(), 6)
        self.assertEqual(counts[0], 1)
        self.assertEqual(counts[1], 1)
        self.assertEqual(counts[-1], 1)

    def test_normalized_statistics_do_not_change_with_repeated_population(self):
        sample=pd.Series([1, 4, 6, 8, 10])
        a=summarize(sample)
        b=summarize(pd.concat([sample]*3, ignore_index=True))
        self.assertEqual(b['n'], 3*a['n'])
        for key in ('mean','median','pct_lt5','pct_ge8','pct_ge9'):
            self.assertAlmostEqual(a[key], b[key])

    def test_empty_or_invalid_scores_fail(self):
        for sample in ([np.nan], [-1, 6], [11, 7]):
            with self.assertRaises(ValueError):
                summarize(pd.Series(sample))

    def test_disjoint_bands_reconstruct_mean_and_keep_boundaries(self):
        values=pd.Series([0,4,5,7,8,8.5,9,10,np.nan])
        bands=band_summary(values)
        self.assertEqual([r['n'] for r in bands], [2,2,2,2])
        self.assertEqual(sum(r['n'] for r in bands), 8)
        self.assertEqual(sum(r['share'] for r in bands), 1)
        self.assertEqual(sum(r['mean_contribution'] for r in bands), 6.4375)

    def test_empty_band_contributes_zero_not_missing(self):
        bands=band_summary(pd.Series([0,10]))
        self.assertEqual(bands[1]['mean_contribution'], 0)
        self.assertEqual(bands[2]['mean_contribution'], 0)
        self.assertEqual(sum(r['mean_contribution'] for r in bands), 5)
