"""Phần việc Duy: ma trận tương quan, điểm cao cùng xuất hiện và PCA theo tổ hợp."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SUBJECTS = ("math", "literature", "english", "physics", "chemistry", "biology", "history", "geography")
LABELS = dict(zip(SUBJECTS, ("Toán", "Ngữ văn", "Tiếng Anh", "Vật lý", "Hóa học", "Sinh học", "Lịch sử", "Địa lý")))
COMBINATIONS = {"A00": ("math", "physics", "chemistry"), "A01": ("math", "physics", "english"),
                "B00": ("math", "chemistry", "biology"), "C00": ("literature", "history", "geography"),
                "D01": ("math", "literature", "english")}
RAW = {2023: {"Mathematics": "math", "Literature": "literature", "Physics": "physics", "Chemistry": "chemistry", "Biology": "biology", "History": "history", "Geography": "geography", "Foreign language": "foreign_language", "Foreign language code": "language_code"},
       2025: {"toan": "math", "ngu_van": "literature", "vat_li": "physics", "hoa_hoc": "chemistry", "sinh_hoc": "biology", "lich_su": "history", "dia_li": "geography", "ngoai_ngu": "foreign_language", "ma_ngoai_ngu": "language_code"}}


def load(path: Path, year: int) -> pd.DataFrame:
    raw = pd.read_csv(path, low_memory=False)
    data = raw.rename(columns=RAW[year])
    scores = pd.DataFrame(index=data.index)
    for subject in SUBJECTS:
        if subject == "english":
            continue
        scores[subject] = pd.to_numeric(data.get(subject), errors="coerce")
        scores[subject] = scores[subject].where(scores[subject].between(0, 10))
    code = data["language_code"].astype("string").str.strip().str.upper()
    foreign = pd.to_numeric(data["foreign_language"], errors="coerce")
    scores["english"] = foreign.where(code.eq("N1") & foreign.between(0, 10))
    return scores.loc[:, SUBJECTS]


def correlations(data: pd.DataFrame, year: int) -> pd.DataFrame:
    rows = []
    for i, x in enumerate(SUBJECTS):
        for y in SUBJECTS[i + 1:]:
            pair = data[[x, y]].dropna()
            ranks = pair.rank(method="average")
            rows.append({"year": year, "subject_x": x, "subject_y": y, "n_pair": len(pair),
                         "pearson_r": pair[x].corr(pair[y], method="pearson"),
                         "spearman_rho": ranks[x].corr(ranks[y], method="pearson")})
    return pd.DataFrame(rows)


def pca(data: pd.DataFrame, year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary, loads = [], []
    for code, subjects in COMBINATIONS.items():
        complete = data.loc[:, subjects].dropna().to_numpy(float)
        z = (complete - complete.mean(axis=0)) / complete.std(axis=0, ddof=1)
        _, s, vt = np.linalg.svd(z, full_matrices=False)
        eig = s ** 2 / (len(z) - 1); explained = eig / eig.sum()
        loading = vt.T * np.sqrt(eig)
        if loading[:, 0].sum() < 0:
            loading[:, 0] *= -1
        summary.append({"year": year, "combination": code, "n_complete": len(complete),
                        "pc1_explained_pct": 100 * explained[0], "pc2_explained_pct": 100 * explained[1], "pc3_explained_pct": 100 * explained[2]})
        loads.extend({"year": year, "combination": code, "subject": subject, "pc1_loading": loading[i, 0], "pc2_loading": loading[i, 1], "pc3_loading": loading[i, 2]} for i, subject in enumerate(subjects))
    return pd.DataFrame(summary), pd.DataFrame(loads)


def high_score(data: pd.DataFrame, year: int) -> pd.DataFrame:
    rows = []
    for x, y in (("math", "physics"), ("literature", "history")):
        pair = data[[x, y]].dropna(); cutoff_x, cutoff_y = pair[x].quantile(.8, interpolation="higher"), pair[y].quantile(.8, interpolation="higher")
        xhigh, yhigh = pair[x].ge(cutoff_x), pair[y].ge(cutoff_y)
        rows.append({"year": year, "subject_x": x, "subject_y": y, "n_pair": len(pair), "p80_x": cutoff_x, "p80_y": cutoff_y,
                     "p_y_high_baseline": yhigh.mean(), "p_y_high_given_x_high": yhigh[xhigh].mean()})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data2023", type=Path, required=True); parser.add_argument("--data2025", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("duy/outputs")); args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    cohorts = {2023: load(args.data2023, 2023), 2025: load(args.data2025, 2025)}
    pair = pd.concat([correlations(cohorts[y], y) for y in cohorts]); pca_summary, pca_loadings = zip(*(pca(cohorts[y], y) for y in cohorts))
    pair.to_csv(args.output / "pairwise_correlations.csv", index=False, encoding="utf-8-sig")
    pd.concat(pca_summary).to_csv(args.output / "pca_summary.csv", index=False, encoding="utf-8-sig")
    pd.concat(pca_loadings).to_csv(args.output / "pca_loadings.csv", index=False, encoding="utf-8-sig")
    pd.concat([high_score(cohorts[y], y) for y in cohorts]).to_csv(args.output / "high_score_concordance.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote results to {args.output}")


if __name__ == "__main__":
    main()
