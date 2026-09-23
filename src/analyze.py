"""Reproduce the INFO3020 Week 3 audit and missing-value experiment.

The raw CSV is read only. Published scores remain unchanged in the Parquet file;
imputed scores exist only in the controlled masking experiment.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".venv" / "matplotlib"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAW = ROOT / "data" / "raw" / "original.csv"
PARQUET = ROOT / "data" / "processed" / "exam_2023.parquet"
OUTPUT = ROOT / "outputs"
TABLES = OUTPUT / "tables"
FIGURES = OUTPUT / "figures"
SCORES = [
    "Mathematics", "Literature", "Foreign language", "Physics", "Chemistry",
    "Biology", "History", "Geography", "Civic education",
]
SCIENCE = ["Physics", "Chemistry", "Biology"]
SOCIAL = ["History", "Geography", "Civic education"]
COLUMNS = ["Student ID", *SCORES, "Foreign language code"]
VALID_CODES = {f"N{i}" for i in range(1, 8)}
SUSPECT_TOKENS = {"-", "--", "?", "n/a", "null", "không rõ", "thỏa thuận", "-999", "9999"}
NA_TOKENS = {"-", "--", "?", "n/a", "null", "không rõ", "thỏa thuận", "-999"}
GROUPS = ["science_only", "social_only", "both_observed", "neither_observed"]
CORE = ["Mathematics", "Literature", "Foreign language"]


def missing_bin(count: int) -> str:
    return str(count) if count < 3 else "3-4" if count < 5 else "5+"


def scan_raw_tokens(path: Path = RAW) -> dict:
    """Count source representations before pandas normalizes empty fields."""
    counts: Counter[tuple[str, str]] = Counter()
    na_values = {""}
    malformed_rows = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if header != COLUMNS:
            raise ValueError(f"CSV schema changed: {header!r}")
        for row in reader:
            if len(row) != len(header):
                malformed_rows += 1
                continue
            for col, value in zip(header, row):
                stripped = value.strip()
                if stripped == "":
                    counts[(col, "blank_or_whitespace")] += 1
                    if value:
                        na_values.add(value)
                elif stripped.casefold() in SUSPECT_TOKENS:
                    counts[(col, f"suspect:{stripped}")] += 1
                    if stripped.casefold() in NA_TOKENS:
                        na_values.add(value)
                elif col in SCORES and stripped == "0":
                    counts[(col, "valid_zero")] += 1
    if malformed_rows:
        raise ValueError(f"CSV contains {malformed_rows} rows with the wrong number of fields")
    return {
        "counts": {f"{col} | {token}": n for (col, token), n in sorted(counts.items())},
        "na_values": sorted(na_values),
        "malformed_rows": malformed_rows,
    }


def load_and_prepare(scan: dict | None = None) -> pd.DataFrame:
    scan = scan or scan_raw_tokens()
    df = pd.read_csv(
        RAW,
        dtype={"Student ID": "string", "Foreign language code": "string"},
        keep_default_na=False,
        na_values=scan["na_values"],
        low_memory=False,
    )
    if list(df.columns) != COLUMNS:
        raise ValueError("Parsed columns do not match the recorded source schema")
    for col in SCORES:
        df[col] = pd.to_numeric(df[col], errors="raise")
    PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET, index=False, compression="zstd")
    return df


def derive_observed_groups(df: pd.DataFrame) -> pd.DataFrame:
    science_count = df[SCIENCE].notna().sum(axis=1).astype("uint8")
    social_count = df[SOCIAL].notna().sum(axis=1).astype("uint8")
    labels = np.select(
        [
            (science_count > 0) & (social_count == 0),
            (science_count == 0) & (social_count > 0),
            (science_count > 0) & (social_count > 0),
        ],
        GROUPS[:3],
        default="neither_observed",
    )
    return pd.DataFrame({
        "science_observed_count": science_count,
        "social_observed_count": social_count,
        "observed_exam_group": labels,
    }, index=df.index)


def profile_columns(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        row = {
            "column": col,
            "dtype": str(series.dtype),
            "n_total": len(df),
            "n_observed": int(series.notna().sum()),
            "n_missing": int(series.isna().sum()),
            "pct_missing": float(100 * series.isna().mean()),
            "n_unique_observed": int(series.nunique(dropna=True)),
            "sample": str(series.dropna().iloc[0]) if series.notna().any() else "",
            "min": float(series.min()) if col in SCORES and series.notna().any() else "",
            "max": float(series.max()) if col in SCORES and series.notna().any() else "",
        }
        rows.append(row)
    return pd.DataFrame(rows)


def audit(df: pd.DataFrame, groups: pd.DataFrame, profile: pd.DataFrame) -> dict:
    id_values = df["Student ID"]
    nonnull_id = id_values.notna()
    format_ok = id_values.str.fullmatch(r"\d{8}").fillna(False)
    duplicate_id = id_values.duplicated(keep=False) & nonnull_id
    duplicate_extra = id_values.duplicated(keep="first") & nonnull_id
    conflict_ids = int(df.loc[duplicate_id].groupby("Student ID", dropna=True).nunique(dropna=False).gt(1).any(axis=1).sum())
    language = df["Foreign language"]
    code = df["Foreign language code"]
    score_invalid = {
        col: int((df[col].notna() & (~df[col].between(0, 10) | ~np.isfinite(df[col]))).sum())
        for col in SCORES
    }
    group_counts = groups["observed_exam_group"].value_counts().reindex(GROUPS, fill_value=0)
    missing = {
        row.column: {"count": int(row.n_missing), "percent": float(row.pct_missing)}
        for row in profile.itertuples(index=False)
    }
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": missing,
        "student_id_missing_count": int((~nonnull_id).sum()),
        "student_id_duplicate_extra_rows": int(duplicate_extra.sum()),
        "student_id_duplicate_involved_rows": int(duplicate_id.sum()),
        "student_id_conflicting_groups": conflict_ids,
        "whole_row_duplicate_extra_rows": int(df.duplicated().sum()),
        "invalid_student_id_format": int((nonnull_id & ~format_ok).sum()),
        "out_of_range_or_nonfinite_scores": score_invalid,
        "invalid_language_code": int((code.notna() & ~code.isin(VALID_CODES)).sum()),
        "language_score_code_mismatch": int((code.isna() != language.isna()).sum()),
        "exam_groups": {name: int(group_counts[name]) for name in GROUPS},
        "foreign_language_codes": {str(k): int(v) for k, v in code.value_counts(dropna=False).items()},
    }


def quality_scores(audit_result: dict) -> pd.DataFrame:
    """Human audit judgements with computed evidence, for the 2023 use case."""
    n = audit_result["rows"]
    math_missing = audit_result["missing"]["Mathematics"]["count"]
    social = audit_result["exam_groups"]["social_only"]
    neither = audit_result["exam_groups"]["neither_observed"]
    rows = [
        ("Completeness", 3, f"Math missing {math_missing}/{n}; {social} have social scores only; {neither} have no composite score", "Registration and exemption records are unavailable; true required-score denominator is unknown"),
        ("Accuracy", 2, "No independent official result table or candidate-level reconciliation in this project", "In-range scores alone cannot establish that a published score matches the actual result"),
        ("Consistency", 4, f"Foreign-language score/code state mismatches {audit_result['language_score_code_mismatch']}; both composite groups observed {audit_result['exam_groups']['both_observed']}", "Unusual partial subject patterns need registration metadata"),
        ("Validity", 5, f"Out-of-range/nonfinite score cells {sum(audit_result['out_of_range_or_nonfinite_scores'].values())}; invalid language codes {audit_result['invalid_language_code']}; invalid non-null ID formats {audit_result['invalid_student_id_format']}", "Language-code set follows dataset documentation and project mapping, not independent exam authority"),
        ("Uniqueness", 5, f"Extra repeated Student IDs {audit_result['student_id_duplicate_extra_rows']}; extra whole-row duplicates {audit_result['whole_row_duplicate_extra_rows']}", "Student ID is treated as the row identifier in this file"),
        ("Timeliness", 4, "2023 exam data answers questions about the 2023 published-score distribution", "No candidate-level collection/update timestamps; it is not current-year exam data"),
    ]
    result = pd.DataFrame(rows, columns=["dimension", "score_1_to_5", "evidence", "limitation"])
    return result


def analyze_missing_patterns(df: pd.DataFrame, groups: pd.DataFrame) -> dict:
    n = len(df)
    label = groups["observed_exam_group"]
    group_counts = label.value_counts().reindex(GROUPS, fill_value=0)
    cross = pd.crosstab(groups["science_observed_count"], groups["social_observed_count"])

    context_rows = []
    for col in [*SCIENCE, *SOCIAL]:
        target_missing = df[col].isna()
        for group in GROUPS:
            group_mask = label.eq(group)
            missing_n = int((target_missing & group_mask).sum())
            context_rows.append({
                "column": col,
                "observed_exam_group": group,
                "group_n": int(group_counts[group]),
                "missing_n": missing_n,
                "pct_within_group": 100 * missing_n / int(group_counts[group]) if group_counts[group] else np.nan,
            })
    context = pd.DataFrame(context_rows)

    missing_group_rows = []
    for col in ["Mathematics", "Literature", "Foreign language", "Foreign language code"]:
        for group in GROUPS:
            group_mask = label.eq(group)
            missing_n = int((df[col].isna() & group_mask).sum())
            missing_group_rows.append({
                "column": col, "observed_exam_group": group,
                "group_n": int(group_counts[group]), "missing_n": missing_n,
                "pct_within_group": 100 * missing_n / int(group_counts[group]) if group_counts[group] else np.nan,
            })
    core_group = pd.DataFrame(missing_group_rows)

    # Nine score-presence bits yield at most 512 patterns without row-wise string joins.
    flags = df[SCORES].notna().to_numpy(dtype=np.uint8)
    codes = flags @ (1 << np.arange(len(SCORES) - 1, -1, -1, dtype=np.uint16))
    counts = np.bincount(codes.astype(np.int32), minlength=1 << len(SCORES))
    patterns = pd.DataFrame([
        {"observed_bits": format(i, f"0{len(SCORES)}b"), "n": int(count)}
        for i, count in enumerate(counts) if count
    ]).sort_values("n", ascending=False)
    patterns["pct_all_rows"] = 100 * patterns["n"] / n

    language_table = pd.crosstab(
        df["Foreign language"].notna().map({True: "score_present", False: "score_missing"}),
        df["Foreign language code"].notna().map({True: "code_present", False: "code_missing"}),
    )
    return {
        "group_counts": {g: int(group_counts[g]) for g in GROUPS},
        "observed_subject_count_table": cross.reset_index().to_dict(orient="records"),
        "missing_by_context": context.astype(object).where(pd.notna(context), None).to_dict(orient="records"),
        "core_missing_by_group": core_group.astype(object).where(pd.notna(core_group), None).to_dict(orient="records"),
        "presence_pattern_columns": SCORES,
        "presence_pattern_bit_rule": "1 = published score present; 0 = missing",
        "top_score_presence_patterns": patterns.head(10).to_dict(orient="records"),
        "language_score_code_table": language_table.to_dict(),
    }


def analyze_missing_layers(df: pd.DataFrame, groups: pd.DataFrame) -> dict:
    """Separate observed-group structural candidates from unresolved blank scores."""
    labels = groups["observed_exam_group"]
    n = len(df)
    raw_counts = df[SCORES].isna().sum(axis=1).to_numpy(dtype=np.uint8)
    score_count = len(SCORES) - raw_counts
    only_id = int(((score_count == 0) & df["Foreign language code"].isna()).sum())

    raw_rows = []
    for group in GROUPS:
        selector = labels.eq(group).to_numpy()
        for count in range(len(SCORES) + 1):
            value = int(np.count_nonzero(selector & (raw_counts == count)))
            raw_rows.append({"observed_exam_group": group, "missing_count": count,
                             "missing_bin": missing_bin(count), "n": value,
                             "pct_group": 100 * value / int(selector.sum()) if selector.any() else None})
    raw_table = pd.DataFrame(raw_rows)
    raw_table.to_csv(TABLES / "raw_nine_score_missing_counts+thieu_9_mon.csv", index=False)

    six_rows = []
    pattern_rows = []
    for group, subjects in (("science_only", SCIENCE), ("social_only", SOCIAL)):
        selector = labels.eq(group)
        relevant = CORE + subjects
        blanks = df.loc[selector, relevant].isna().to_numpy(dtype=np.uint8)
        counts = blanks.sum(axis=1)
        group_n = len(counts)
        for count in range(7):
            value = int(np.count_nonzero(counts == count))
            six_rows.append({"observed_exam_group": group, "missing_count": count,
                             "missing_bin": missing_bin(count), "n": value,
                             "pct_group": 100 * value / group_n})
        # A bit is 1 if the corresponding relevant score is blank. Keep every
        # observed pattern, including rare pairs and 3/4-subject combinations.
        codes = blanks @ (1 << np.arange(5, -1, -1, dtype=np.uint8))
        frequencies = np.bincount(codes.astype(np.int32), minlength=64)
        for code, value in enumerate(frequencies):
            if not value:
                continue
            missing_subjects = [subject for index, subject in enumerate(relevant)
                                if code & (1 << (5 - index))]
            pattern_rows.append({"observed_exam_group": group,
                                 "missing_count": len(missing_subjects),
                                 "missing_bin": missing_bin(len(missing_subjects)),
                                 "missing_subjects": " | ".join(missing_subjects) or "(none)",
                                 "n": int(value), "pct_group": 100 * int(value) / group_n})
    six_table = pd.DataFrame(six_rows)
    pattern_table = pd.DataFrame(pattern_rows).sort_values(
        ["observed_exam_group", "missing_count", "n", "missing_subjects"],
        ascending=[True, True, False, True], kind="stable",
    )
    six_table.to_csv(TABLES / "context_six_score_missing_counts+thieu_6_mon.csv", index=False)
    pattern_table.to_csv(TABLES / "context_missing_subject_patterns+mau_mon_thieu.csv", index=False)

    classification_rows = []
    for col in [*SCORES, "Foreign language code"]:
        missing = df[col].isna()
        opposite = (labels.eq("social_only") if col in SCIENCE else
                    labels.eq("science_only") if col in SOCIAL else pd.Series(False, index=df.index))
        structural_candidate = int((missing & opposite).sum())
        no_group = int((missing & labels.eq("neither_observed")).sum())
        unresolved_observed_group = int(missing.sum()) - structural_candidate - no_group
        classification_rows.append({
            "column": col, "missing_n": int(missing.sum()),
            "structural_candidate_opposite_group_n": structural_candidate,
            "unresolved_observed_group_n": unresolved_observed_group,
            "unresolved_no_group_n": no_group,
            "unresolved_total_n": unresolved_observed_group + no_group,
        })
    classification = pd.DataFrame(classification_rows)
    classification.to_csv(TABLES / "missing_context_classification+phan_loai_o_thieu.csv", index=False)

    civic_missing = labels.eq("social_only") & df["Civic education"].isna()
    civic_present = labels.eq("social_only") & df["Civic education"].notna()
    fl_missing = df["Foreign language"].isna()
    civic_language = {
        "social_civic_missing_n": int(civic_missing.sum()),
        "social_civic_missing_foreign_language_missing_n": int((civic_missing & fl_missing).sum()),
        "social_civic_present_n": int(civic_present.sum()),
        "social_civic_present_foreign_language_missing_n": int((civic_present & fl_missing).sum()),
    }
    if int(raw_table["n"].sum()) != n or int(six_table["n"].sum()) != int(labels.isin(["science_only", "social_only"]).sum()):
        raise AssertionError("Missing-count tables do not reconcile to their denominators")
    if int(pattern_table["n"].sum()) != int(six_table["n"].sum()):
        raise AssertionError("Exact missing-subject patterns do not reconcile")
    if not (classification["missing_n"] == classification["structural_candidate_opposite_group_n"] + classification["unresolved_total_n"]).all():
        raise AssertionError("Missing-cell classification does not reconcile")
    return {
        "raw_nine_score_missing_counts": raw_table.astype(object).where(pd.notna(raw_table), None).to_dict(orient="records"),
        "context_six_score_missing_counts": six_table.to_dict(orient="records"),
        "context_missing_subject_patterns": pattern_table.to_dict(orient="records"),
        "missing_context_classification": classification.to_dict(orient="records"),
        "only_student_id_rows": only_id,
        "neither_group_rows": int(labels.eq("neither_observed").sum()),
        "civic_language_context": civic_language,
        "interpretation": "Opposite-group blanks are structural candidates, not verified non-applicable scores; every other blank remains unresolved.",
    }


def plot_missingness(df: pd.DataFrame, groups: pd.DataFrame, seed: int = 3020) -> None:
    rates = df.isna().mean().mul(100).sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(rates.index, rates.values, color="#277da1")
    ax.set(xlabel="Missing values (%)", title="Missing values by column, all candidates", xlim=(0, 100))
    fig.tight_layout()
    fig.savefig(FIGURES / "missing_rates+ty_le_thieu.png", dpi=160)
    plt.close(fig)

    sampled_index = df.sample(n=min(2000, len(df)), random_state=seed).index
    group_order = {"science_only": 0, "social_only": 1, "both_observed": 2, "neither_observed": 3}
    sampled_index = sampled_index[np.argsort(groups.loc[sampled_index, "observed_exam_group"].map(group_order).to_numpy(), kind="stable")]
    sample = df.loc[sampled_index, SCORES + ["Foreign language code"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(sample.isna().to_numpy(dtype=np.uint8), aspect="auto", interpolation="nearest", cmap="Greys")
    ax.set(
        title=f"Missingness pattern in {len(sample):,} sampled rows, sorted by observed subject group",
        xlabel="Column", ylabel="Sampled candidates, grouped",
        xticks=np.arange(len(sample.columns)), xticklabels=sample.columns.tolist(),
    )
    ax.tick_params(axis="x", labelrotation=50)
    fig.tight_layout()
    fig.savefig(FIGURES / "missing_matrix_sample+ma_tran_mau_o_thieu.png", dpi=160)
    plt.close(fig)


def missing_treatment_table(df: pd.DataFrame, groups: pd.DataFrame, layers: dict) -> pd.DataFrame:
    group = groups["observed_exam_group"]
    classification = {row["column"]: row for row in layers["missing_context_classification"]}
    templates = {
        "Mathematics": ("Unresolved; group association makes MCAR across all rows implausible; MAR/MNAR unverified", "Keep null; describe published Math scores with n", "Registration, absence and source-record status are unavailable."),
        "Literature": ("Unresolved; group association makes MCAR across all rows implausible; MAR/MNAR unverified", "Keep null; describe published Literature scores with n", "Registration, absence and source-record status are unavailable."),
        "Foreign language": ("Unresolved mixture of non-registration, exemption, absence or recording gaps", "Keep null; report score and code missingness together", "Score and code are jointly blank; program, registration and exemption are unknown."),
        "Foreign language code": ("Matches Foreign language score missingness; reason unverified", "Keep null", "No evidence supports assigning the most common observed code."),
    }
    for col in SCIENCE + SOCIAL:
        templates[col] = (
            "Structural candidate in opposite observed group; other blanks unresolved",
            "Keep null; report by observed subject context",
            "Observed subject patterns suggest exam choice; registration and program are unknown.",
        )
    templates["Civic education"] = (
        "Structural candidate opposite social group; social blanks may also be non-applicable for GDTX",
        "Keep null; distinguish opposite-group and within-social missingness",
        "2023 GDTX social exam omitted Civic education; this CSV has no candidate-level program flag.",
    )
    rows = []
    for col in df.columns:
        missing_n = int(df[col].isna().sum())
        if not missing_n:
            continue
        mechanism, treatment, reason = templates.get(col, ("Unknown", "Keep null", "Investigate source process"))
        row = {
            "column": col, "missing_n": missing_n,
            "missing_pct": 100 * missing_n / len(df),
            "mechanism_hypothesis": mechanism,
            "treatment": treatment, "reason": reason,
            "certainty": "Hypothesis; candidate-level cause unverified",
            "structural_candidate_opposite_group_n": classification[col]["structural_candidate_opposite_group_n"],
            "unresolved_observed_group_n": classification[col]["unresolved_observed_group_n"],
            "unresolved_no_group_n": classification[col]["unresolved_no_group_n"],
        }
        if col in SCIENCE + SOCIAL:
            opposite = "social_only" if col in SCIENCE else "science_only"
            own = "science_only" if col in SCIENCE else "social_only"
            row["opposite_only_missing_n"] = int((df[col].isna() & group.eq(opposite)).sum())
            row["neither_missing_n"] = int((df[col].isna() & group.eq("neither_observed")).sum())
            row["own_group_missing_n"] = int((df[col].isna() & group.eq(own)).sum())
            row["both_group_missing_n"] = int((df[col].isna() & group.eq("both_observed")).sum())
        rows.append(row)
    result = pd.DataFrame(rows)
    result.to_csv(TABLES / "missing_treatment+cach_xu_ly_thieu.csv", index=False)
    return result


def impute_masked_math(truth: np.ndarray, labels: np.ndarray, mask: np.ndarray, min_group_observed: int = 30) -> dict:
    """Fit both medians using only unmasked scores, then fill the same mask."""
    truth = np.asarray(truth, dtype=float)
    labels = np.asarray(labels)
    mask = np.asarray(mask, dtype=bool)
    if len(truth) != len(labels) or len(truth) != len(mask):
        raise ValueError("Truth, group labels and mask must have equal length")
    donors = ~mask & np.isfinite(truth)
    if not donors.any():
        raise ValueError("No observed Math scores are available to fit a median")
    global_median = float(np.median(truth[donors]))
    group_medians = {}
    donor_counts = {}
    for group in ("science_only", "social_only"):
        selector = donors & (labels == group)
        donor_counts[group] = int(selector.sum())
        if donor_counts[group] >= min_group_observed:
            group_medians[group] = float(np.median(truth[selector]))
    global_values = truth.copy()
    global_values[mask] = global_median
    group_values = truth.copy()
    fallback_count = 0
    group_fill_counts = Counter()
    for i in np.flatnonzero(mask):
        group = str(labels[i])
        if group in group_medians:
            group_values[i] = group_medians[group]
            group_fill_counts[group] += 1
        else:
            group_values[i] = global_median
            fallback_count += 1
    return {
        "global_values": global_values,
        "group_values": group_values,
        "global_median": global_median,
        "group_medians": group_medians,
        "donor_counts": donor_counts,
        "group_fill_counts": dict(group_fill_counts),
        "fallback_count": fallback_count,
        "n_donors": int(donors.sum()),
    }


def _summary(values: np.ndarray) -> dict:
    observed = values[np.isfinite(values)]
    return {
        "n_total": int(len(values)), "n_observed": int(len(observed)),
        "n_missing": int(len(values) - len(observed)),
        "mean": float(observed.mean()) if len(observed) else None,
        "std_sample": float(observed.std(ddof=1)) if len(observed) > 1 else None,
    }


def imputation_experiment(df: pd.DataFrame, groups: pd.DataFrame, sample_size: int = 50000, seed: int = 3020, mask_fraction: float = 0.2) -> dict:
    eligible = df["Mathematics"].notna()
    conflicted = df["Student ID"].duplicated(keep=False) & df["Student ID"].notna()
    eligible &= ~conflicted
    pool = df.loc[eligible, ["Student ID", "Mathematics"]].copy()
    pool["observed_exam_group"] = groups.loc[eligible, "observed_exam_group"].to_numpy()
    size = min(sample_size, len(pool))
    if size < 2:
        raise ValueError("At least two observed Math scores are required")
    sample = pool.sample(n=size, random_state=seed).reset_index(drop=True)
    rng = np.random.default_rng(seed)
    mask = np.zeros(size, dtype=bool)
    mask[rng.choice(size, size=max(1, round(size * mask_fraction)), replace=False)] = True
    truth = sample["Mathematics"].to_numpy(dtype=float)
    labels = sample["observed_exam_group"].to_numpy()
    masked = truth.copy()
    masked[mask] = np.nan
    fitted = impute_masked_math(truth, labels, mask)
    methods = {
        "original_observed_sample": truth,
        "after_masking": masked,
        "global_median": fitted["global_values"],
        "group_median": fitted["group_values"],
    }
    summaries = {name: _summary(values) for name, values in methods.items()}
    for name in ("global_median", "group_median"):
        errors = methods[name][mask] - truth[mask]
        summaries[name]["n_imputed"] = int(mask.sum())
        summaries[name]["mae_masked"] = float(np.mean(np.abs(errors)))
        summaries[name]["rmse_masked"] = float(np.sqrt(np.mean(errors ** 2)))
        summaries[name]["delta_mean_vs_original"] = summaries[name]["mean"] - summaries["original_observed_sample"]["mean"]
        summaries[name]["delta_std_vs_original"] = summaries[name]["std_sample"] - summaries["original_observed_sample"]["std_sample"]
    pd.DataFrame.from_dict(summaries, orient="index").rename_axis("status").to_csv(TABLES / "imputation_comparison+so_sanh_dien_khuyet.csv")

    bins = np.arange(0, 10.51, 0.5)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharex=True, sharey=True)
    for ax, name, title in zip(
        axes,
        ("original_observed_sample", "global_median", "group_median"),
        ("Published Math scores", "Global median", "Group median"),
    ):
        ax.hist(methods[name], bins=bins, density=True, color="#277da1", edgecolor="white", linewidth=0.3)
        ax.set(title=title, xlabel="Mathematics score", xlim=(0, 10))
    axes[0].set_ylabel("Density")
    fig.suptitle(f"Same {size:,} candidates; {int(mask.sum()):,} known Math scores masked (seed {seed})")
    fig.tight_layout()
    fig.savefig(FIGURES / "imputation_distribution+phan_phoi_dien_khuyet.png", dpi=170)
    plt.close(fig)

    return {
        "target_column": "Mathematics",
        "design": "Artificially mask observed scores; no naturally missing score is imputed",
        "eligible_observed_math_rows": int(eligible.sum()),
        "excluded_conflicting_id_rows": int((df["Mathematics"].notna() & conflicted).sum()),
        "sample_size": size, "seed": seed, "mask_fraction": mask_fraction,
        "artificially_masked": int(mask.sum()),
        "donor_count": fitted["n_donors"],
        "min_group_observed": 30,
        "global_median": fitted["global_median"],
        "group_medians": fitted["group_medians"],
        "group_donor_counts": fitted["donor_counts"],
        "group_fill_counts": fitted["group_fill_counts"],
        "fallback_count": fitted["fallback_count"],
        "eligible_group_counts": {g: int((pool["observed_exam_group"] == g).sum()) for g in GROUPS},
        "sample_group_counts": {g: int((sample["observed_exam_group"] == g).sum()) for g in GROUPS},
        "methods": summaries,
    }


def natural_missing_sensitivity(df: pd.DataFrame, groups: pd.DataFrame) -> dict:
    """Hypothetical comparison on naturally blank Math cells; never export scores."""
    math = df["Mathematics"].to_numpy(dtype=float)
    labels = groups["observed_exam_group"].to_numpy()
    missing = ~np.isfinite(math)
    fitted = impute_masked_math(math, labels, missing)
    methods = {
        "published_math_only": math,
        "hypothetical_global_median": fitted["global_values"],
        "hypothetical_group_median": fitted["group_values"],
    }
    summaries = {name: _summary(values) for name, values in methods.items()}
    for name in ("hypothetical_global_median", "hypothetical_group_median"):
        summaries[name]["n_imputed"] = int(missing.sum())
        summaries[name]["delta_mean_vs_published"] = summaries[name]["mean"] - summaries["published_math_only"]["mean"]
        summaries[name]["delta_std_vs_published"] = summaries[name]["std_sample"] - summaries["published_math_only"]["std_sample"]
    pd.DataFrame.from_dict(summaries, orient="index").rename_axis("status").to_csv(TABLES / "natural_missing_sensitivity+do_nhay_thieu_tu_nhien.csv")

    bins = np.arange(0, 10.51, 0.5)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharex=True, sharey=True)
    for ax, name, title in zip(
        axes,
        methods,
        ("Published Math scores", "Hypothetical global median", "Hypothetical group median"),
    ):
        ax.hist(methods[name], bins=bins, density=True, color="#577590", edgecolor="white", linewidth=0.3)
        ax.set(title=title, xlabel="Mathematics score", xlim=(0, 10))
    axes[0].set_ylabel("Density")
    fig.suptitle("Sensitivity only: all naturally blank Math cells hypothetically filled")
    fig.tight_layout()
    fig.savefig(FIGURES / "natural_missing_sensitivity+do_nhay_thieu_tu_nhien.png", dpi=170)
    plt.close(fig)

    return {
        "assumption": "Every naturally blank Math cell represents an existing but unpublished score; unverified",
        "missing_n": int(missing.sum()),
        "global_median": fitted["global_median"],
        "group_medians": fitted["group_medians"],
        "group_donor_counts": fitted["donor_counts"],
        "group_fill_counts": fitted["group_fill_counts"],
        "fallback_count": fitted["fallback_count"],
        "methods": summaries,
    }


def run() -> dict:
    OUTPUT.mkdir(exist_ok=True)
    TABLES.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    sha_before = hashlib.sha256(RAW.read_bytes()).hexdigest()
    scan = scan_raw_tokens()
    df = load_and_prepare(scan)
    groups = derive_observed_groups(df)
    profile = profile_columns(df)
    profile.to_csv(TABLES / "column_profile+ho_so_cot.csv", index=False)
    audit_result = audit(df, groups, profile)
    scores = quality_scores(audit_result)
    patterns = analyze_missing_patterns(df, groups)
    layers = analyze_missing_layers(df, groups)
    treatment = missing_treatment_table(df, groups, layers)
    plot_missingness(df, groups)
    experiment = imputation_experiment(df, groups)
    sensitivity = natural_missing_sensitivity(df, groups)
    sha_after = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if sha_before != sha_after:
        raise AssertionError("Raw CSV changed while running the analysis")
    if sum(audit_result["exam_groups"].values()) != len(df):
        raise AssertionError("Observed group counts do not sum to the number of rows")
    if layers["only_student_id_rows"] > layers["neither_group_rows"]:
        raise AssertionError("ID-only rows must be part of the no-observed-group set")
    if sum(experiment["group_fill_counts"].values()) + experiment["fallback_count"] != experiment["artificially_masked"]:
        raise AssertionError("Group imputation fill counts do not match the mask")
    if sum(sensitivity["group_fill_counts"].values()) + sensitivity["fallback_count"] != sensitivity["missing_n"]:
        raise AssertionError("Sensitivity fill counts do not match natural Math missingness")
    result = {
        "provenance": {
            "source": str(RAW.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": sha_before,
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "raw_tokens": scan["counts"],
            "slide_reference": "INFO3020 Week 3 PPTX, slides 7, 13-18, 20-29, 32, 35",
        },
        "audit": audit_result,
        "quality_scores": scores.to_dict(orient="records"),
        "missing_patterns": patterns,
        "missing_layers": layers,
        "missing_treatment_columns": treatment["column"].tolist(),
        "experiment": experiment,
        "natural_missing_sensitivity": sensitivity,
    }
    (OUTPUT / "metrics+chi_so.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "rows": result["audit"]["rows"],
        "source_sha256": result["provenance"]["source_sha256"],
        "observed_groups": result["audit"]["exam_groups"],
        "experiment_methods": result["experiment"]["methods"],
    }, ensure_ascii=False, indent=2))
