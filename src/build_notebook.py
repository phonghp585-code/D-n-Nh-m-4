"""Build and execute the Week 3 notebook without Jupyter-only dependencies.

Each code cell is executed sequentially in a fresh Python namespace, and its
standard output is saved in the notebook. The notebook can also be run normally
in Jupyter or VS Code with the project's .venv as kernel.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "notebooks" / "week3_exercises+bai_tap_tuan3.ipynb"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.splitlines(keepends=True)}


def build_cells() -> list[dict]:
    return [
        markdown("""# INFO3020 Week 3: Data Quality and Missing Values

Dataset: published 2023 Vietnamese high school graduation exam scores. The assignment is on slide 35 of *W3 - Data Quality and Processing_.pptx*. This notebook regenerates the full audit, then reads the tables and figures. See `../docs/report+bao_cao.md` for the written EX3.1–EX3.3 arguments. The CSV is read only.
"""),
        markdown("""## 1. Run from the raw file

The source ID stays a string, preserving leading zeros. The pipeline writes a Parquet copy with published scores and nulls, plus audit tables and experiment outputs. It does not write imputed scores to Parquet.
"""),
        code("""from pathlib import Path
import json
import sys
import pandas as pd
root = Path.cwd().resolve()
if not (root / 'src').exists:
    root = root.parent
sys.path.insert(0, str(root))
from src.analyze import run, ROOT

results = run()
print('CSV rows:', results['audit']['rows'])
print('Columns:', results['audit']['columns'])
print('Raw SHA-256:', results['provenance']['source_sha256'])
print('Raw token types:', results['provenance']['raw_tokens'])
"""),
        markdown("""## 2. EX3.1: audit six dimensions

Slides 7 and 11 define the dimensions and suggest a reusable column profile. Scores are reasoned judgments for describing *published 2023 scores*, not measured accuracy percentages. A value within 0–10 passes a validity check; it cannot verify the original exam result.
"""),
        code("""profile = pd.read_csv(ROOT / 'outputs/tables/column_profile+ho_so_cot.csv')
print(profile[['column', 'dtype', 'n_observed', 'n_missing', 'pct_missing', 'n_unique_observed', 'min', 'max']].to_string(index=False, float_format=lambda x: f'{x:.3f}'))
"""),
        code("""quality = pd.DataFrame(results['quality_scores'])
print(quality.to_string(index=False, max_colwidth=72))
print('Duplicate ID rows:', results['audit']['student_id_duplicate_extra_rows'])
print('Score cells outside 0–10:', sum(results['audit']['out_of_range_or_nonfinite_scores'].values()))
print('Language score/code state mismatches:', results['audit']['language_score_code_mismatch'])
"""),
        markdown("""![Missing percentage across all candidates](../outputs/figures/missing_rates+ty_le_thieu.png)

The bar chart uses the full CSV. High missingness in an elective subject may reflect the exam structure. It is not a data-error rate by itself.
"""),
        markdown("""## 3. EX3.2: source tokens, patterns and treatment

Slides 13–15 call for inspecting hidden missing tokens and co-occurring gaps. The group labels below mean *at least one published score in that group*. They do not prove exam registration or attendance.
"""),
        code("""tokens = pd.DataFrame([{'column_and_token': k, 'n': v} for k, v in results['provenance']['raw_tokens'].items()])
print(tokens.to_string(index=False))
observed_groups = pd.DataFrame([{'observed_exam_group': k, 'n': v, 'pct_all_rows': 100*v/results['audit']['rows']} for k, v in results['audit']['exam_groups'].items()])
print()
print('Observed subject groups:')
print(observed_groups.to_string(index=False, float_format=lambda x: f'{x:.3f}'))
print()
print('Cross-tab of published subject counts:')
print(pd.DataFrame(results['missing_patterns']['observed_subject_count_table']).to_string(index=False))
"""),
        code("""core = pd.DataFrame(results['missing_patterns']['core_missing_by_group'])
print('Missing Math, Literature and Foreign language by observed group:')
print(core.loc[core['column'].isin(['Mathematics', 'Literature', 'Foreign language'])].to_string(index=False, float_format=lambda x: f'{x:.3f}'))
print()
print('Elective-subject context:')
context = pd.DataFrame(results['missing_patterns']['missing_by_context'])
print(context[['column', 'observed_exam_group', 'group_n', 'missing_n']].to_string(index=False))
"""),
        markdown("""### Two denominators and two classes of blank scores

The raw view counts blanks among nine score columns for every candidate. The context view counts blanks among Mathematics, Literature, Foreign language and the three subjects of the **observed** composite group. It excludes candidates with no observed composite group. Opposite-group blanks are *structural candidates*, never confirmed non-applicable scores; all remaining blanks are unresolved. Only if a score should have existed does an MCAR/MAR/MNAR hypothesis apply.
"""),
        code("""layers = results['missing_layers']
raw = pd.DataFrame(layers['raw_nine_score_missing_counts'])
six = pd.DataFrame(layers['context_six_score_missing_counts'])
print('Raw missing scores among nine subjects:')
print(raw.groupby('missing_count')['n'].sum().to_string())
print('Context missing scores among six relevant subjects:')
print(six.pivot(index='missing_count', columns='observed_exam_group', values='n').to_string())
print('No observed composite group:', layers['neither_group_rows'])
print('Only Student ID remains:', layers['only_student_id_rows'])
"""),
        code("""classified = pd.DataFrame(layers['missing_context_classification'])
print(classified.to_string(index=False))
patterns = pd.read_csv(ROOT / 'outputs/tables/context_missing_subject_patterns+mau_mon_thieu.csv')
print('Most common exact missing-subject patterns (1-4 blanks, by group):')
print(patterns.loc[patterns.missing_count.between(1, 4)].groupby(['observed_exam_group', 'missing_count'], sort=False).head(3).to_string(index=False))
print('Social Civic/Foreign language context:', layers['civic_language_context'])
"""),
        markdown("""![Missingness matrix: 2,000 randomly sampled rows sorted by observed subject group](../outputs/figures/missing_matrix_sample+ma_tran_mau_o_thieu.png)

The matrix is only a picture of a seeded sample. All counts and percentages in the tables use the full CSV. The GDTX social exam in 2023 did not include Civic education, so a blank Civic score within the observed social group can also be structurally non-applicable; the CSV cannot confirm a candidate's program. MCAR/MAR/MNAR are hypotheses about a score that should have existed (slides 16–18). A subject that was never taken should not be imputed as a lost score.
"""),
        code("""treatment = pd.read_csv(ROOT / 'outputs/tables/missing_treatment+cach_xu_ly_thieu.csv')
print(treatment[['column', 'missing_n', 'missing_pct', 'mechanism_hypothesis', 'treatment', 'reason']].to_string(index=False, max_colwidth=62, float_format=lambda x: f'{x:.3f}'))
"""),
        markdown("""## 4. EX3.3: two ways to fill Mathematics

Slides 32 and 35 require the same column, n, mean, sample standard deviation and a distribution plot for two methods. The first comparison hypothetically fills the **18,687 naturally blank Math cells**. It does not assert that a Math score existed for every one of those candidates. The canonical Parquet retains nulls.
"""),
        code("""natural = pd.read_csv(ROOT / 'outputs/tables/natural_missing_sensitivity+do_nhay_thieu_tu_nhien.csv')
print(natural.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
print('Group medians:', results['natural_missing_sensitivity']['group_medians'])
print('Fallback count:', results['natural_missing_sensitivity']['fallback_count'])
"""),
        markdown("""![Math distribution under the hypothetical natural-missing sensitivity scenario](../outputs/figures/natural_missing_sensitivity+do_nhay_thieu_tu_nhien.png)

The second comparison hides 20% of **known** Math scores from a 50,000-row sample, then checks both methods against the held-out truth. Both use the same mask and donors. It measures performance for an artificial random gap, not for natural gaps whose causes are unknown.
"""),
        code("""experiment = pd.read_csv(ROOT / 'outputs/tables/imputation_comparison+so_sanh_dien_khuyet.csv')
print(experiment.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
print('Fit medians:', results['experiment']['global_median'], results['experiment']['group_medians'])
print('Masked scores:', results['experiment']['artificially_masked'])
print('Fallback count:', results['experiment']['fallback_count'])
"""),
        markdown("""![Distribution after randomly masking 10,000 known Math scores](../outputs/figures/imputation_distribution+phan_phoi_dien_khuyet.png)

Both median methods change the score distribution. Compare the mean and standard deviation with the original sample, and the MAE/RMSE only on the masked cells. Group Median has lower error in this particular experiment, but that cannot establish the correct values of naturally missing scores.
"""),
        markdown("""## 5. Reconciliation and conclusion

The project's chosen treatment is to keep unverified missing exam scores as null. One-subject statistics use the observed scores and disclose n; two-subject statistics use pairs with both scores; a composite total requires every included score. Further metadata on subject registration, school program, exemptions and absences would be needed to classify candidate-level causes. Independent official scores would be needed to verify accuracy.
"""),
        code("""import hashlib
raw_sha = hashlib.sha256((ROOT / 'data/raw/original.csv').read_bytes()).hexdigest()
assert raw_sha == results['provenance']['source_sha256']
assert sum(results['audit']['exam_groups'].values()) == results['audit']['rows']
assert len(treatment) == sum(profile['n_missing'] > 0)
assert results['experiment']['artificially_masked'] == results['experiment']['fallback_count'] + sum(results['experiment']['group_fill_counts'].values())
assert results['natural_missing_sensitivity']['missing_n'] == results['audit']['missing']['Mathematics']['count']
assert sum(row['n'] for row in layers['raw_nine_score_missing_counts']) == results['audit']['rows']
assert sum(row['n'] for row in layers['context_six_score_missing_counts']) == results['audit']['exam_groups']['science_only'] + results['audit']['exam_groups']['social_only']
assert layers['only_student_id_rows'] == 4476
processed = pd.read_parquet(ROOT / 'data/processed/exam_2023.parquet')
assert list(processed.columns) == list(profile['column'])
assert len(processed) == results['audit']['rows']
assert processed['Mathematics'].isna().sum() == results['audit']['missing']['Mathematics']['count']
assert processed['Student ID'].iloc[0] == '01000001'
print('Reconciliation passed; published scores and natural nulls remain in Parquet.')
"""),
    ]


def main() -> None:
    cells = build_cells()
    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"week3-{index:02d}"
    namespace: dict = {}
    count = 0
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        count += 1
        source = "".join(cell["source"])
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(compile(source, f"notebook cell {count}", "exec"), namespace)
        cell["execution_count"] = count
        output = buffer.getvalue()
        if output:
            cell["outputs"] = [{"output_type": "stream", "name": "stdout", "text": output.splitlines(keepends=True)}]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (.venv)", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }
    DESTINATION.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Executed {count} code cells and wrote {DESTINATION}")


if __name__ == "__main__":
    main()
