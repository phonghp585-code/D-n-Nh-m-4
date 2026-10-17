"""Complete-case exam combinations and observed score participation.

All percentages describe the supplied records, not registrations or admission
preferences. Missing subjects are never imputed. Quantile cutoffs use the
inverse empirical CDF; quartiles use pandas' linear interpolation.
"""

from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .score_data import (COHORT_LABELS, ALL_COMBINATIONS as COMBINATIONS,
                         SUBJECT_LABELS, valid_numeric, combination_subjects,
                         combination_metadata)


_EXAM_SUBJECTS = tuple(s for s in SUBJECT_LABELS if s != "english")
_OPTIONAL = {
    2023: ("physics", "chemistry", "biology", "history", "geography", "civics", "foreign_language"),
    2025: ("physics", "chemistry", "biology", "history", "geography", "economics_law",
           "informatics", "technology", "foreign_language"),
}
_STRUCTURAL_ABSENCE = {2023: {"economics_law", "informatics", "technology"}, 2025: {"civics"}}
_B00_EXPECTED = {2023: (1022060, 324554), 2025: (1131136, 44964)}


def nearest_rank(values, quantile):
    """Return x[ceil(p*n)] (one-based), or NaN for an empty valid sample."""
    if not 0 < quantile <= 1:
        raise ValueError("quantile must be in (0, 1]")
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not values.size:
        return float("nan")
    rank = int(np.ceil(quantile * values.size)) - 1
    return float(np.partition(values, rank)[rank])


def combination_scores(frame, combination, year=None):
    """Recompute a total only when all three subject scores are valid."""
    if year is None:
        years=frame['year'].dropna().unique()
        if len(years)!=1:
            raise ValueError('combination_scores requires one explicit cohort year')
        year=int(years[0])
    subjects = combination_subjects(combination,year)
    valid = pd.DataFrame({s: valid_numeric(frame[s]) for s in subjects}, index=frame.index)
    # Preserve decimal-score ties across different addition orders. Ten decimal
    # places retain far more precision than the supplied exam scores.
    return valid.sum(axis=1, min_count=len(subjects)).round(10)


def _percent(n, denominator):
    return 100.0 * n / denominator if denominator else float("nan")


def _presence(frame):
    return pd.DataFrame({s: valid_numeric(frame[s]).notna() for s in SUBJECT_LABELS}, index=frame.index)


def _summary(year, code, scores, denominator, all_rows):
    sample = scores.dropna()
    n = len(sample)
    row = {"year": year, "cohort": COHORT_LABELS[year], "combination": code, "n": n,
           "denominator": denominator, "denominator_all_rows": all_rows,
           "pct_complete": _percent(n, denominator), "pct_complete_all_rows": _percent(n, all_rows)}
    row.update(combination_metadata(code,year))
    row.update(mean=sample.mean(), median=sample.median(), sd=sample.std(ddof=1))
    for label, p in (("p10", .1), ("q1", .25), ("p25", .25), ("p50", .5),
                     ("q3", .75), ("p75", .75)):
        row[label] = sample.quantile(p) if n else float("nan")
    for label, p in (("p80", .8), ("p90", .9), ("p95", .95)):
        row[label] = nearest_rank(sample, p)
    row["iqr"] = row["q3"] - row["q1"]
    for threshold in (15, 20, 24, 27):
        row[f"pct_ge_{threshold}"] = _percent(int((sample >= threshold).sum()), n)
    return row


def _threshold_rows(year, code, scores):
    sample = scores.dropna().to_numpy()
    rows = []
    for p in (.8, .9):
        cutoff = nearest_rank(sample, p)
        at = int(np.count_nonzero(sample == cutoff))
        gt = int(np.count_nonzero(sample > cutoff))
        ge = at + gt
        rows.append({"year": year, "cohort": COHORT_LABELS[year], "combination": code,
                     "n": len(sample), "quantile": p, "target_top_percent": 100 * (1 - p),
                     "threshold": cutoff, "n_at": at, "n_gt": gt, "n_ge": ge,
                     "pct_at": _percent(at, len(sample)), "pct_gt": _percent(gt, len(sample)),
                     "pct_ge": _percent(ge, len(sample)), "method": "nearest_rank",
                     **combination_metadata(code,year)})
    return rows


def _validation(year, code, frame, scores):
    stored_column = f"stored_{code}"
    row = {"year": year, "cohort": COHORT_LABELS[year], "combination": code,
           "n_recomputed": int(scores.notna().sum()), "stored_available": stored_column in frame,
           "n_stored": np.nan, "n_invalid_stored": np.nan,
           "n_missingness_mismatch": np.nan, "n_sum_mismatch": np.nan,
           "max_abs_difference": np.nan, "status": "stored_unavailable",
           "expected_b00_n": np.nan, "b00_count_status": "not_applicable"}
    if stored_column in frame:
        original = frame[stored_column]
        numeric = pd.to_numeric(original, errors="coerce")
        valid = numeric.where(np.isfinite(numeric) & numeric.between(0, 30))
        both = scores.notna() & valid.notna()
        differences = (scores[both] - valid[both]).abs()
        invalid = int((original.notna() & valid.isna()).sum())
        missing = int((scores.notna() != valid.notna()).sum())
        mismatch = int((differences > 1e-8).sum())
        row.update(n_stored=int(valid.notna().sum()), n_invalid_stored=invalid,
                   n_missingness_mismatch=missing, n_sum_mismatch=mismatch,
                   max_abs_difference=float(differences.max()) if len(differences) else np.nan,
                   status="match" if not (invalid or missing or mismatch) else "mismatch")
    if code == "B00":
        expected_rows, expected_count = _B00_EXPECTED[year]
        row["expected_b00_n"] = expected_count
        row["b00_count_status"] = (
            "match" if row["n_recomputed"] == expected_count else "mismatch"
        ) if len(frame) == expected_rows else "not_full_source_row_count"
    return row


def _participation(year, present):
    all_rows = len(present)
    exam_count = present[list(_EXAM_SUBJECTS)].sum(axis=1)
    optional_count = present[list(_OPTIONAL[year])].sum(axis=1)
    denominator = int((exam_count > 0).sum())
    rows, distribution, cooccurrence = [], [], []
    for subject in SUBJECT_LABELS:
        if subject in _STRUCTURAL_ABSENCE[year]:
            continue
        n = int(present[subject].sum())
        status = "common"
        if subject in ("civics", "economics_law"):
            status = "changed_content_separate_subject"
        elif subject in ("informatics", "technology"):
            status = "new_2025"
        rows.append({"year": year, "cohort": COHORT_LABELS[year], "subject": subject,
                     "subject_label": SUBJECT_LABELS[subject], "n": n,
                     "denominator": denominator, "denominator_all_rows": all_rows,
                     "percent": _percent(n, denominator), "percent_all_rows": _percent(n, all_rows),
                     "comparability": status, "counts_as_separate_exam": subject != "english"})
    for count_type, counts in (("exam", exam_count), ("optional", optional_count)):
        for number, n in counts.value_counts().sort_index().items():
            active_n = int(((counts == number) & (exam_count > 0)).sum())
            distribution.append({"year": year, "cohort": COHORT_LABELS[year], "count_type": count_type,
                                 "score_count": int(number), "n": int(n), "n_with_any_exam": active_n,
                                 "denominator": denominator, "denominator_all_rows": all_rows,
                                 "percent": _percent(active_n, denominator),
                                 "percent_all_rows": _percent(int(n), all_rows)})
    for x, y in combinations(_OPTIONAL[year], 2):
        n = int((present[x] & present[y]).sum())
        cooccurrence.append({"year": year, "cohort": COHORT_LABELS[year], "subject_x": x,
                             "subject_y": y, "subject_x_label": SUBJECT_LABELS[x],
                             "subject_y_label": SUBJECT_LABELS[y], "n": n,
                             "denominator": denominator, "denominator_all_rows": all_rows,
                             "percent": _percent(n, denominator), "percent_all_rows": _percent(n, all_rows)})
    return rows, distribution, cooccurrence, denominator


def _deltas(summary):
    numeric = [c for c in summary.select_dtypes(include="number").columns if c != "year"]
    before = summary[summary.year == 2023].set_index("combination")
    after = summary[summary.year == 2025].set_index("combination")
    rows = []
    for code in COMBINATIONS:
        row = {"combination": code, "year_from": 2023, "year_to": 2025,
               "cohort_from": COHORT_LABELS[2023], "cohort_to": COHORT_LABELS[2025]}
        row.update(subjects_from=before.loc[code,'subjects'],subjects_to=after.loc[code,'subjects'],
                   comparison_class=after.loc[code,'comparison_class'],
                   comparison_note=after.loc[code,'comparison_note'])
        row.update({f"delta_{c}": after.loc[code, c] - before.loc[code, c] for c in numeric})
        rows.append(row)
    return pd.DataFrame(rows)


def audit_membership(frame,year,scores):
    """Compare each eligible combination with the source's multi-label field."""
    counts=np.zeros(len(frame),dtype=np.int16)
    source=frame.get('source_combinations')
    rows=[]
    for code in COMBINATIONS:
        eligible=scores[code].notna()
        counts+=eligible.to_numpy(dtype=np.int16)
        row={'year':year,'cohort':COHORT_LABELS[year],'combination':code,
             'n_eligible':int(eligible.sum()),'n_source_label':np.nan,
             'n_disagreement':np.nan,'status':'source_labels_unavailable'}
        if source is not None:
            listed=source.fillna('').str.contains(r'(?:^|,\s*)'+code+r'(?:\s*,|$)',regex=True)
            disagreement=int((eligible!=listed).sum())
            row.update(n_source_label=int(listed.sum()),n_disagreement=disagreement,
                       status='match' if disagreement==0 else 'mismatch')
        rows.append(row)
    values,frequencies=np.unique(counts,return_counts=True)
    distribution=[{'year':year,'cohort':COHORT_LABELS[year],
                   'n_eligible_combinations':int(value),'n_students':int(n),
                   'denominator_all_rows':len(frame)} for value,n in zip(values,frequencies)]
    return rows,distribution


def _save(fig, destination):
    fig.savefig(destination, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _participation_deltas(participation):
    common = participation[participation.comparability == "common"]
    before = common[common.year == 2023].set_index("subject")
    after = common[common.year == 2025].set_index("subject")
    rows = []
    for subject in before.index.intersection(after.index):
        old, new = before.loc[subject], after.loc[subject]
        rows.append({"subject": subject, "subject_label": SUBJECT_LABELS[subject],
                     "year_from": 2023, "year_to": 2025,
                     "cohort_from": COHORT_LABELS[2023], "cohort_to": COHORT_LABELS[2025],
                     "n_from": old.n, "n_to": new.n, "delta_n": new.n - old.n,
                     "denominator_from": old.denominator, "denominator_to": new.denominator,
                     "percent_from": old.percent, "percent_to": new.percent,
                     "delta_percent": new.percent - old.percent,
                     "percent_all_rows_from": old.percent_all_rows,
                     "percent_all_rows_to": new.percent_all_rows,
                     "delta_percent_all_rows": new.percent_all_rows - old.percent_all_rows})
    return pd.DataFrame(rows)


def _figures(scores, thresholds, participation, cooccurrence, output):
    colors = {2023: "#176D8A", 2025: "#C45D31"}
    codes=list(COMBINATIONS)
    for page,start in enumerate(range(0,len(codes),6),1):
        batch=codes[start:start+6]
        suffix='' if page==1 else f'_page_{page:02d}'
        fig,axes=plt.subplots(len(batch),2,figsize=(13,3.1*len(batch)),squeeze=False,constrained_layout=True)
        for index,code in enumerate(batch):
            for year in (2023,2025):
                values=scores[(year,code)].dropna().to_numpy()
                label=f'{COHORT_LABELS[year]} (n={len(values):,})'
                if values.size:
                    axes[index,0].hist(values,bins=np.linspace(0,30,61),weights=np.full(values.size,100/values.size),
                        histtype='step',color=colors[year],label=label,linewidth=1.5)
                    unique,counts=np.unique(values,return_counts=True)
                    axes[index,1].step(np.r_[0,unique,30],np.r_[0,np.cumsum(counts)/values.size,1],
                        where='post',color=colors[year],label=label)
                else:
                    for ax in axes[index]: ax.plot([],[],color=colors[year],label=label)
            marker=' *' if 'economics_law' in COMBINATIONS[code] else ''
            for ax in axes[index]:
                ax.set(xlim=(0,30),xlabel='Tổng điểm quan sát (0–30)'); ax.legend(fontsize=8)
            axes[index,0].set(title=f'{code}{marker} — histogram',ylabel='% trong khoảng điểm')
            axes[index,1].set(title=f'{code}{marker} — ECDF',ylabel='Tỷ lệ tích lũy',ylim=(0,1.02))
        fig.suptitle(f'24 tổ hợp · trang {page}/4 · * GDCD / GDKT&PL khác nội dung')
        _save(fig,output/f'combination_hist_ecdf{suffix}.png')

        fig,axes=plt.subplots(2,3,figsize=(14,9),sharey=True,constrained_layout=True)
        for ax,code in zip(axes.flat,batch):
            data=[scores[(year,code)].dropna().to_numpy() for year in (2023,2025)]
            boxes=ax.boxplot(data,tick_labels=[COHORT_LABELS[y] for y in (2023,2025)],
                patch_artist=True,showfliers=False)
            for box,year in zip(boxes['boxes'],(2023,2025)): box.set_facecolor(colors[year])
            ax.set(title=code+(' *' if 'economics_law' in COMBINATIONS[code] else ''),ylim=(0,30))
            ax.tick_params(axis='x',labelrotation=15,labelsize=8)
            ax.set_ylabel('Tổng điểm (0–30)')
        for ax in list(axes.flat)[len(batch):]: ax.set_visible(False)
        fig.suptitle(f'24 tổ hợp · boxplots trang {page}/4 · * GDCD / GDKT&PL khác nội dung\n'
                     'Hộp Q1–Q3, râu 1.5 IQR; ẩn điểm rời nhưng giữ toàn bộ thống kê')
        _save(fig,output/f'combination_boxplots{suffix}.png')

    fig, axes = plt.subplots(1, 2, figsize=(13, 13), sharey=True, constrained_layout=True)
    for ax, p in zip(axes, (.8, .9)):
        for offset, year in zip((-.18, .18), (2023, 2025)):
            values = thresholds[(thresholds.year == year) & (thresholds["quantile"] == p)]
            values = values.set_index("combination").reindex(COMBINATIONS)
            ax.barh(np.arange(len(codes)) + offset, values.threshold, height=.36,
                   color=colors[year], label=COHORT_LABELS[year])
        labels=[code+(' *' if 'economics_law' in COMBINATIONS[code] else '') for code in codes]
        ax.set(yticks=np.arange(len(codes)), yticklabels=labels, xlim=(0, 30),
               title=f"P{int(p * 100)} — 24 tổ hợp", xlabel="Ngưỡng tổng điểm")
        ax.legend()
    axes[0].invert_yaxis()
    fig.suptitle('Top 20% (P80) / top 10% (P90) · * GDCD / GDKT&PL khác nội dung')
    _save(fig, output / "top_threshold_comparison.png")

    subjects = list(SUBJECT_LABELS)
    fig, ax = plt.subplots(figsize=(14, 7), constrained_layout=True)
    for offset, year in zip((-.19, .19), (2023, 2025)):
        values = participation[participation.year == year].set_index("subject").reindex(subjects)
        ax.bar(np.arange(len(subjects)) + offset, values.percent, width=.38,
               color=colors[year], label=COHORT_LABELS[year])
    labels = [SUBJECT_LABELS[s] + (" *" if s in ("civics", "economics_law", "informatics", "technology") else "")
              for s in subjects]
    ax.set(xticks=np.arange(len(subjects)), xticklabels=labels, ylim=(0, 105),
           ylabel="% bản ghi có ít nhất một điểm thi", title="Có điểm quan sát theo môn; Anh là tập con Ngoại ngữ")
    ax.tick_params(axis="x", labelrotation=50)
    ax.legend()
    fig.text(.01, -.025, "* GDCD/GDKT&PL khác nội dung; Tin học/Công nghệ mới năm 2025. Ô không có mốc không được thay bằng 0.")
    _save(fig, output / "participation.png")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), constrained_layout=True)
    for ax, year in zip(axes, (2023, 2025)):
        subjects = _OPTIONAL[year]
        matrix = np.full((len(subjects), len(subjects)), np.nan)
        for row in cooccurrence[cooccurrence.year == year].itertuples():
            x, y = subjects.index(row.subject_x), subjects.index(row.subject_y)
            matrix[x, y] = matrix[y, x] = row.percent
        artist = ax.imshow(matrix, vmin=0, vmax=100, cmap="Blues")
        ax.set(xticks=range(len(subjects)), yticks=range(len(subjects)),
               xticklabels=[SUBJECT_LABELS[s] for s in subjects],
               yticklabels=[SUBJECT_LABELS[s] for s in subjects], title=COHORT_LABELS[year])
        ax.tick_params(axis="x", labelrotation=70)
        for i, j in zip(*np.where(np.isfinite(matrix))):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", fontsize=7,
                    color="white" if matrix[i, j] > 55 else "black")
    fig.colorbar(artist, ax=axes, label="% có cả hai điểm / bản ghi có ≥1 điểm thi", shrink=.8)
    _save(fig, output / "optional_cooccurrence.png")


def analyze_combinations(cohorts, output_dir):
    """Write reproducible comparisons for 2023 CT2006 and 2025 CT2018.

    Returns JSON-compatible metadata and relative output paths. Input frames must
    have the canonical subject columns supplied by ``score_data.load_scores``.
    """
    if set(cohorts) != {2023, 2025}:
        raise ValueError("cohorts must contain exactly 2023 and 2025")
    output = Path(output_dir)
    figure_dir = output / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    summary, thresholds, participation, distribution, cooccurrence, validation = [], [], [], [], [], []
    membership,membership_distribution=[],[]
    scores = {}
    for year in (2023, 2025):
        frame = cohorts[year]
        present = _presence(frame)
        parts, counts, pairs, denominator = _participation(year, present)
        participation.extend(parts)
        distribution.extend(counts)
        cooccurrence.extend(pairs)
        for code in COMBINATIONS:
            values = combination_scores(frame, code, year)
            scores[(year, code)] = values
            summary.append(_summary(year, code, values, denominator, len(frame)))
            thresholds.extend(_threshold_rows(year, code, values))
            validation.append(_validation(year, code, frame, values))
        checked,degree=audit_membership(frame,year,{code:scores[(year,code)] for code in COMBINATIONS})
        membership.extend(checked); membership_distribution.extend(degree)
    summary = pd.DataFrame(summary)
    tables = {"combination_summary.csv": summary, "combination_deltas.csv": _deltas(summary),
              "top_thresholds.csv": pd.DataFrame(thresholds), "participation.csv": pd.DataFrame(participation),
              "score_count_distribution.csv": pd.DataFrame(distribution),
              "cooccurrence.csv": pd.DataFrame(cooccurrence), "combination_validation.csv": pd.DataFrame(validation)}
    tables["participation_deltas.csv"] = _participation_deltas(tables["participation.csv"])
    tables['combination_mapping.csv']=summary[['year','cohort','combination','subjects','comparison_class',
                                              'comparison_note','same_subjects_as']].copy()
    tables['combination_membership_validation.csv']=pd.DataFrame(membership)
    tables['membership_count_distribution.csv']=pd.DataFrame(membership_distribution)
    for name, table in tables.items():
        table.to_csv(output / name, index=False, encoding="utf-8-sig")
    _figures(scores, tables["top_thresholds.csv"], tables["participation.csv"], tables["cooccurrence.csv"], figure_dir)
    mismatches = sum(row["status"] == "mismatch" for row in validation)
    return {"cohorts": {str(y): COHORT_LABELS[y] for y in (2023, 2025)},
            "tables": list(tables), "figures": [p.relative_to(output).as_posix() for p in sorted(figure_dir.glob('*.png'))],
            'combination_count':len(COMBINATIONS),
            'code_policy':'24 codes exactly as supplied diem_* columns; not a universal admissions-code registry',
            'changed_content_codes':[c for c,s in COMBINATIONS.items() if 'economics_law' in s],
            'duplicate_subject_set_note':'B08 and D08 have the same three subjects in the supplied dataset; retained as two supplied codes, not independent populations.',
            "quantile_method": "nearest_rank: x[ceil(p*n)], one-based; P80/P90/P95",
            "quartile_method": "linear interpolation; SD uses ddof=1",
            "sum_arithmetic": "complete-case sums rounded to 10 decimal places to remove binary roundoff; raw component scores unchanged",
            "delta_direction": "2025 minus 2023; percent changes are percentage points",
            "primary_denominator": "records with at least one valid actual exam score; English is a subset of foreign_language",
            "secondary_denominator": "all supplied rows",
            "optional_subject_set": {str(y): list(_OPTIONAL[y]) for y in (2023, 2025)},
            "optional_count_interpretation": "Counts presence in the subject set eligible as 2025 optional exams, using year-specific subject names; not confirmed elective registrations in 2023.",
            "validation_mismatch_groups": mismatches,
            "limitations": ["Observed score presence is not registration or admission preference.",
                            "Different cohorts, exams and selection mechanisms do not identify causal effects.",
                            "GDCD and economics_law have changed content; informatics/technology have no 2023 baseline.",
                            "B00 expected counts checked only when source row counts match the audited full files."]}
