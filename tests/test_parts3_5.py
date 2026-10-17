"""Small complete run, reports and notebook contracts."""
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.run_parts3_5 import write_notebooks, validate_outputs, validate_pair_support


class DeliverableTests(unittest.TestCase):
    def test_notebooks_exclude_unrequested_dimension_reduction(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'tmp') as temp:
            for path in write_notebooks(Path(temp)):
                notebook=json.loads(path.read_text(encoding='utf-8'))
                source='\n'.join(''.join(cell['source']) for cell in notebook['cells'])
                self.assertNotIn('pca',source.lower())
                self.assertNotIn('factor analysis',source.lower())

    def test_support_validator_rejects_finite_coefficients_below_minimum(self):
        table=pd.DataFrame([{'n_pair':1,'status':'ok','pearson_r':.5,'spearman_rho':.5}])
        with self.assertRaisesRegex(ValueError,'support'): validate_pair_support(table)

    def test_support_validator_requires_finite_ok_coefficients(self):
        table=pd.DataFrame([{'n_pair':100,'status':'ok','pearson_r':float('nan'),'spearman_rho':.5}])
        with self.assertRaisesRegex(ValueError,'finite'): validate_pair_support(table)

    def test_notebooks_compile_and_use_full_cohort_labels(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'tmp') as temp:
            root=Path(temp)
            paths=write_notebooks(root)
            self.assertEqual(len(paths),2)
            for path in paths:
                notebook=json.loads(path.read_text(encoding='utf-8'))
                source='\n'.join(''.join(cell['source']) for cell in notebook['cells'])
                self.assertIn('2023 — CT2006',source)
                self.assertIn('2025 — CT2018',source)
                self.assertIn('--rerun',source)
                self.assertIn('docs/bao_cao_phan_3_5.md',source)
                self.assertNotIn('/report.md',source)
                for cell in notebook['cells']:
                    if cell['cell_type']=='code': compile(''.join(cell['source']),str(path),'exec')

    def test_validator_refuses_inconsistent_threshold_or_missing_outputs(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'tmp') as temp:
            with self.assertRaises((ValueError,FileNotFoundError)):
                validate_outputs(Path(temp))


if __name__=='__main__': unittest.main()
