"""Descriptive correlations on pairwise complete, valid exam scores.

The common-subject matrices deliberately exclude changed/new subjects. Each
coefficient is computed on its own observed pair, including its Spearman ranks.
No missing exam scores are imputed and no causal interpretation is implied.
"""
from itertools import combinations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.score_data import (
    COHORT_LABELS, COMBINATIONS, COMMON_SUBJECTS, SUBJECT_LABELS, valid_numeric,
)


HIGH_SCORE_PAIRS = (("math", "physics"), ("chemistry", "biology"), ("literature", "history"))
HEXBIN_PAIRS = (("math", "physics"), ("physics", "chemistry"),
                ("chemistry", "biology"), ("history", "geography"), ("math", "english"))
PAIR_COLUMNS = ["year", "cohort", "subject_x", "subject_y", "n_pair", "pearson_r", "spearman_rho", "status"]


def _clean(frame):
    return frame.reindex(columns=COMMON_SUBJECTS).apply(valid_numeric)


def _pearson(x, y):
    centered_x = x - x.mean()
    centered_y = y - y.mean()
    value = np.dot(centered_x, centered_y) / np.sqrt(np.dot(centered_x, centered_x) * np.dot(centered_y, centered_y))
    return float(np.clip(value, -1, 1))


def _pair(data, year, subject_x, subject_y, min_pair_n):
    x = data[subject_x].to_numpy(dtype=float)
    y = data[subject_y].to_numpy(dtype=float)
    paired = np.isfinite(x) & np.isfinite(y)
    x, y = x[paired], y[paired]
    n = len(x)
    row = dict(year=year, cohort=COHORT_LABELS[year], subject_x=subject_x,
               subject_y=subject_y, n_pair=n, pearson_r=np.nan, spearman_rho=np.nan)
    if n < max(2, min_pair_n):
        row["status"] = "insufficient_n"
    elif np.ptp(x) == 0 or np.ptp(y) == 0:
        row["status"] = "constant"
    else:
        row.update(status="ok", pearson_r=_pearson(x, y),
                   spearman_rho=_pearson(pd.Series(x).rank(method="average").to_numpy(),
                                         pd.Series(y).rank(method="average").to_numpy()))
    return row


def calculate_pairwise(frame, year, min_pair_n=100):
    """Return all ordered entries, including diagonal and support for masked pairs."""
    data = _clean(frame)
    rows = {}
    for i, subject_x in enumerate(COMMON_SUBJECTS):
        for subject_y in COMMON_SUBJECTS[i:]:
            row = _pair(data, year, subject_x, subject_y, min_pair_n)
            rows[subject_x, subject_y] = row
            rows[subject_y, subject_x] = dict(row, subject_x=subject_y, subject_y=subject_x)
    return pd.DataFrame([rows[x, y] for x in COMMON_SUBJECTS for y in COMMON_SUBJECTS], columns=PAIR_COLUMNS)


def calculate_group_sensitivity(frame, year, min_pair_n=100):
    """Recompute the three unique pairs on each complete three-subject group."""
    data = _clean(frame)
    rows = []
    for code, subjects in COMBINATIONS.items():
        complete = data.loc[data.loc[:, list(subjects)].notna().all(axis=1)]
        for x, y in combinations(subjects, 2):
            rows.append(dict(_pair(complete, year, x, y, min_pair_n), combination=code))
    return pd.DataFrame(rows, columns=["combination"] + PAIR_COLUMNS)


def _p80(values):
    index = int(np.ceil(0.8 * len(values))) - 1
    return float(np.partition(values, index)[index])


def calculate_high_score(frame, year):
    """Describe X-high -> Y-high concordance at within-pair nearest-rank P80."""
    data = _clean(frame)
    rows = []
    for x, y in HIGH_SCORE_PAIRS:
        paired = data.loc[:, [x, y]].dropna()
        n = len(paired)
        row = dict(year=year, cohort=COHORT_LABELS[year], subject_x=x, subject_y=y,
                   n_pair=n, p80_x=np.nan, p80_y=np.nan, n_x_high=0, n_y_high=0,
                   n_both_high=0, n_x_at_threshold=0, n_y_at_threshold=0,
                   x_high_probability=np.nan, baseline_probability=np.nan,
                   conditional_probability=np.nan, status="no_pairs")
        if n:
            values_x, values_y = paired[x].to_numpy(), paired[y].to_numpy()
            cutoff_x, cutoff_y = _p80(values_x), _p80(values_y)
            high_x, high_y = values_x >= cutoff_x, values_y >= cutoff_y
            nx, ny, nboth = int(high_x.sum()), int(high_y.sum()), int((high_x & high_y).sum())
            row.update(p80_x=cutoff_x, p80_y=cutoff_y, n_x_high=nx, n_y_high=ny,
                       n_both_high=nboth, n_x_at_threshold=int((values_x == cutoff_x).sum()),
                       n_y_at_threshold=int((values_y == cutoff_y).sum()),
                       x_high_probability=nx / n, baseline_probability=ny / n,
                       conditional_probability=nboth / nx, status="ok")
        rows.append(row)
    return pd.DataFrame(rows)


def _deltas(pairwise):
    rows = []
    indexed = pairwise.set_index(["year", "subject_x", "subject_y"])
    for x, y in combinations(COMMON_SUBJECTS, 2):
        before, after = indexed.loc[(2023, x, y)], indexed.loc[(2025, x, y)]
        rows.append(dict(subject_x=x, subject_y=y, cohort_from=COHORT_LABELS[2023],
                         cohort_to=COHORT_LABELS[2025], year_from=2023, year_to=2025,
                         n_pair_from=int(before.n_pair), n_pair_to=int(after.n_pair),
                         pearson_r_from=before.pearson_r, pearson_r_to=after.pearson_r,
                         spearman_rho_from=before.spearman_rho, spearman_rho_to=after.spearman_rho,
                         delta_pearson_r=after.pearson_r - before.pearson_r,
                         delta_spearman_rho=after.spearman_rho - before.spearman_rho,
                         status_from=before.status, status_to=after.status))
    return pd.DataFrame(rows)


def _matrix_figure(table, year, metric, destination):
    subjects = list(COMMON_SUBJECTS)
    matrix = table.pivot(index="subject_x", columns="subject_y", values=metric).reindex(index=subjects, columns=subjects).to_numpy()
    support = metric == "n_pair"
    fig, axis = plt.subplots(figsize=(10, 8))
    cmap = plt.get_cmap("viridis" if support else "RdBu_r").with_extremes(bad="#dedede")
    image = axis.imshow(np.ma.masked_invalid(matrix), cmap=cmap,
                        **({"vmin": 0} if support else {"vmin": -1, "vmax": 1}))
    labels = [SUBJECT_LABELS[s] for s in subjects]
    axis.set_xticks(range(len(subjects)), labels, rotation=45, ha="right")
    axis.set_yticks(range(len(subjects)), labels)
    title = {"pearson_r": "Pearson r", "spearman_rho": "Spearman ρ", "n_pair": "Pairwise complete sample n"}[metric]
    axis.set_title(f"{COHORT_LABELS[year]}\n{title}")
    for i in range(len(subjects)):
        for j in range(len(subjects)):
            value = matrix[i, j]
            label = "NA" if not np.isfinite(value) else f"{int(value):,}" if support else f"{value:.2f}"
            axis.text(j, i, label, ha="center", va="center", fontsize=8,
                      color="white" if np.isfinite(value) and ((support and value <= np.nanmax(matrix) * 0.55) or (not support and abs(value) > 0.55)) else "black")
    fig.colorbar(image, ax=axis, label=title, shrink=0.8)
    fig.tight_layout()
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def _hexbin_figure(cohorts, x, y, destination):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)
    for axis, year in zip(axes, (2023, 2025)):
        pair = cohorts[year].loc[:, [x, y]].dropna()
        n_full = len(pair)
        if n_full > 50000:
            pair = pair.sample(n=50000, random_state=42)
        if len(pair):
            image = axis.hexbin(pair[x], pair[y], gridsize=40, extent=(0, 10, 0, 10), mincnt=1, bins="log", cmap="viridis")
            fig.colorbar(image, ax=axis, label="Plotted observations (log count)", shrink=0.8)
        else:
            axis.text(0.5, 0.5, "No paired observations", transform=axis.transAxes, ha="center")
        axis.set(xlim=(0, 10), ylim=(0, 10), xlabel=SUBJECT_LABELS[x], ylabel=SUBJECT_LABELS[y],
                 title=f"{COHORT_LABELS[year]}\nn_pair={n_full:,}; plotted={len(pair):,}")
    fig.suptitle(f"{SUBJECT_LABELS[x]} / {SUBJECT_LABELS[y]}")
    fig.tight_layout()
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def _high_score_figure(table, destination):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for axis, (x, y) in zip(axes, HIGH_SCORE_PAIRS):
        pair = table.loc[(table.subject_x == x) & (table.subject_y == y)].set_index("year").reindex([2023, 2025])
        positions = np.arange(2)
        axis.bar(positions - 0.18, pair.baseline_probability * 100, 0.36, label="P(Y high): baseline")
        axis.bar(positions + 0.18, pair.conditional_probability * 100, 0.36, label="P(Y high | X high)")
        axis.set_xticks(positions, [COHORT_LABELS[year] for year in (2023, 2025)], rotation=12)
        axis.set(title=f"X: {SUBJECT_LABELS[x]}\nY: {SUBJECT_LABELS[y]}", ylim=(0, 105))
        axis.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Probability (%)")
    axes[-1].legend(loc="upper right", fontsize=8)
    fig.suptitle("Within-pair P80 thresholds, including ties")
    fig.tight_layout()
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def analyze_correlations(cohorts, output_dir, min_pair_n=100):
    """Write four result tables, twelve figures and reproducibility metadata."""
    if set(cohorts) != {2023, 2025}:
        raise ValueError("Correlation comparison requires cohorts 2023 and 2025")
    if not isinstance(min_pair_n, (int, np.integer)) or min_pair_n < 2:
        raise ValueError("min_pair_n must be an integer >= 2")
    output = Path(output_dir).resolve()
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    cleaned = {year: _clean(frame) for year, frame in cohorts.items()}
    pairwise = pd.concat([calculate_pairwise(cleaned[year], year, min_pair_n) for year in (2023, 2025)], ignore_index=True)
    groups = pd.concat([calculate_group_sensitivity(cleaned[year], year, min_pair_n) for year in (2023, 2025)], ignore_index=True)
    high = pd.concat([calculate_high_score(cleaned[year], year) for year in (2023, 2025)], ignore_index=True)
    tables = {"pairwise_correlations": pairwise, "correlation_deltas": _deltas(pairwise),
              "group_sensitivity": groups, "high_score_concordance": high}
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False, encoding="utf-8-sig")
    figure_paths = []
    for year in (2023, 2025):
        table = pairwise.loc[pairwise.year == year]
        for metric in ("pearson_r", "spearman_rho", "n_pair"):
            path = figures / f"{metric}_{year}.png"
            _matrix_figure(table, year, metric, path)
            figure_paths.append(str(path))
    for x, y in HEXBIN_PAIRS:
        path = figures / f"hexbin_{x}_{y}.png"
        _hexbin_figure(cleaned, x, y, path)
        figure_paths.append(str(path))
    path = figures / "high_score_concordance.png"
    _high_score_figure(high, path)
    figure_paths.append(str(path))
    metadata = dict(
        cohorts={str(year): COHORT_LABELS[year] for year in (2023, 2025)},
        subjects=list(COMMON_SUBJECTS), min_pair_n=int(min_pair_n),
        tables={name: str(output / f"{name}.csv") for name in tables},
        row_counts={name: len(table) for name, table in tables.items()}, figures=figure_paths,
        missing_policy="Valid finite scores [0,10]; pairwise complete; no imputation; zero retained",
        spearman_policy="Average tie ranks recomputed on each exact paired subset",
        delta_direction="2025 minus 2023; unique unordered common-subject pairs",
        quantile_method="Inverse empirical CDF: sorted x[ceil(0.8*n)], one-based indexing",
        high_score_policy="P(Y >= P80_Y | X >= P80_X), paired-sample thresholds, includes ties; baseline P(Y >= P80_Y)",
        plot_sampling=dict(seed=42, max_hexbin_observations_per_cohort=50000, statistics="All valid paired observations"),
        limitations=["Pairwise samples and complete-combination samples may differ between cohorts.",
                     "Changes in coefficients do not establish causality or item discrimination.",
                     "GDCD, economics/law and new subjects are excluded from the eight-subject comparison."])
    (output / "correlation_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata
