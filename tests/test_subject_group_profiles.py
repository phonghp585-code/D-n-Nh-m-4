"""Checks for disjoint reference-score profiles and exact descriptive decomposition."""
import unittest
import numpy as np
import pandas as pd

from src.subject_group_profiles import reference_groups, profile_subject, decompose_profiles


class SubjectGroupProfileTests(unittest.TestCase):
    def test_reference_rank_ties_are_not_split_and_missing_is_separate(self):
        values=pd.Series([1,2,3,4,np.nan], index=[10,20,30,40,50])
        self.assertEqual(reference_groups(values).tolist(), ['Q1','Q2','Q3','Q4','missing'])
        self.assertEqual(reference_groups(pd.Series([7,7,7,7])).tolist(), ['Q3']*4)

    def test_target_missing_is_not_zero_and_high_score_boundaries_are_inclusive(self):
        data=pd.DataFrame({'math':[1,2,3,4,np.nan], 'chemistry':[0,9,10,np.nan,8]})
        rows=profile_subject(data,'chemistry','math').set_index('reference_group')
        self.assertEqual(rows.n.sum(), 4)
        self.assertEqual(rows.n_ge9.sum(), 2)
        self.assertEqual(rows.n_eq10.sum(), 1)
        self.assertEqual(rows.loc['Q4','n'], 0)
        self.assertEqual(rows.loc['missing','n'], 1)
        self.assertAlmostEqual(rows.share.sum(),1)
        self.assertEqual(rows.sum_score.sum()/rows.n.sum(),6.75)
        with self.assertRaises(ValueError): profile_subject(data,'math','math')

    def test_decomposition_separates_composition_from_within_group_change(self):
        # Fixed reference scale has two people per quartile. Only Q1/Q4 take the target.
        base=pd.DataFrame({'math':range(1,9), 'chemistry':[5,np.nan,np.nan,np.nan,np.nan,np.nan,10,np.nan]})
        shifted=pd.DataFrame({'math':range(1,9), 'chemistry':[5,np.nan,np.nan,np.nan,np.nan,np.nan,10,10]})
        a=profile_subject(base,'chemistry','math')
        b=profile_subject(shifted,'chemistry','math')
        detail, summary=decompose_profiles(a,b)
        self.assertAlmostEqual(summary['delta_pct_ge9'],100/6)
        self.assertAlmostEqual(summary['composition_ge9_pp'],100/6)
        self.assertAlmostEqual(summary['within_ge9_pp'],0)
        self.assertAlmostEqual(summary['delta_mean'],5/6)
        self.assertAlmostEqual(summary['composition_mean'],5/6)
        self.assertAlmostEqual(summary['within_mean'],0)
        self.assertAlmostEqual(detail.delta_ge9_contribution_pp.sum(),summary['delta_pct_ge9'])

    def test_new_group_is_not_given_a_fabricated_previous_rate(self):
        a=pd.DataFrame({'math':range(1,9),'chemistry':[5,np.nan,np.nan,np.nan,np.nan,np.nan,10,np.nan]})
        b=a.copy(); b.loc[2,'chemistry']=9
        detail,summary=decompose_profiles(profile_subject(a,'chemistry','math'),profile_subject(b,'chemistry','math'))
        row=detail.set_index('reference_group').loc['Q2']
        self.assertEqual(row.status,'group_empty_in_one_year')
        self.assertTrue(np.isnan(row.composition_ge9_pp))
        self.assertTrue(np.isnan(summary['composition_ge9_pp']))
        self.assertTrue(np.isfinite(row.delta_ge9_contribution_pp))

    def test_same_group_weights_isolate_within_group_changes(self):
        a=pd.DataFrame({'math':range(1,9),'chemistry':[5,np.nan,np.nan,np.nan,np.nan,np.nan,9,10]})
        b=a.copy(); b.loc[[6,7],'chemistry']=8
        _,summary=decompose_profiles(profile_subject(a,'chemistry','math'),profile_subject(b,'chemistry','math'))
        self.assertAlmostEqual(summary['composition_mean'],0)
        self.assertAlmostEqual(summary['composition_ge9_pp'],0)
        self.assertAlmostEqual(summary['within_mean'],-1)
        self.assertAlmostEqual(summary['within_ge9_pp'],-200/3)
        self.assertAlmostEqual(summary['within_eq10_pp'],-100/3)

    def test_reference_ranks_do_not_depend_on_target_observation(self):
        a=pd.DataFrame({'math':range(1,9),'chemistry':[9,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,10]})
        rows=profile_subject(a,'chemistry','math').set_index('reference_group')
        self.assertEqual(rows.loc['Q1','n'],1)
        self.assertEqual(rows.loc['Q4','n'],1)
