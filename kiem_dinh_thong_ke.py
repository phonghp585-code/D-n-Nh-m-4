#!/usr/bin/env python3
"""
Kiểm định thống kê so sánh điểm thi THPT giữa hai nhóm (hai năm HOẶC hai tỉnh/vùng...).

Với mỗi môn: Welch t-test, Mann-Whitney U, Kolmogorov-Smirnov, Levene (mean) và
Brown-Forsythe (median), Cohen's d (+95% CI), Hedges' g, tỉ số phương sai.

CÁCH DÙNG
  # 1) So sánh HAI NĂM (cần file dữ liệu năm còn lại, cùng tên cột)
  python kiem_dinh_thong_ke.py --a diem_2024.txt --label-a 2024 \
                               --b diem_2025.txt --label-b 2025

  # 2) So sánh hai nhóm trong cùng một file (vd. hai tỉnh)
  python kiem_dinh_thong_ke.py --a diem_2025.txt --group-col ten_tinh \
       --ga "Hà Nội" --gb "TP. Hồ Chí Minh"
"""
import argparse
import numpy as np
import pandas as pd
from scipy import stats

SUBJECTS = ["toan", "ngu_van", "ngoai_ngu", "vat_li", "hoa_hoc", "sinh_hoc",
            "lich_su", "dia_li", "gdktpl"]


# File 2023 dùng tên cột tiếng Anh -> chuẩn hoá về tên cột của file 2025.
# Lưu ý: "Civic education" (GDCD, 2023) được xếp tương ứng với "gdktpl" (GDKT&PL, 2025).
ALIASES = {
    "Student ID": "sbd", "Mathematics": "toan", "Literature": "ngu_van",
    "Foreign language": "ngoai_ngu", "Physics": "vat_li", "Chemistry": "hoa_hoc",
    "Biology": "sinh_hoc", "History": "lich_su", "Geography": "dia_li",
    "Civic education": "gdktpl", "Foreign language code": "ma_ngoai_ngu",
}


def load(path):
    df = pd.read_csv(path, dtype={"sbd": str, "ma_tinh": str, "Student ID": str})
    df = df.rename(columns=ALIASES)
    if "ma_tinh" not in df.columns and "sbd" in df.columns:
        df["ma_tinh"] = df["sbd"].str[:2]       # 2 số đầu SBD = mã tỉnh
    return df


def cohens_d(a, b):
    """d = (mean_b - mean_a) / SD gộp. Trả về d, CI95, Hedges' g."""
    n1, n2 = len(a), len(b)
    s1, s2 = a.var(ddof=1), b.var(ddof=1)
    sp = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    d = (b.mean() - a.mean()) / sp
    se = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    g = d * (1 - 3 / (4 * (n1 + n2) - 9))
    return d, d - 1.96 * se, d + 1.96 * se, g


def label_effect(d):
    d = abs(d)
    if d < 0.2:
        return "không đáng kể"
    if d < 0.5:
        return "nhỏ"
    if d < 0.8:
        return "trung bình"
    return "lớn"


def compare(a, b):
    a = a.dropna().to_numpy(float)
    b = b.dropna().to_numpy(float)
    t = stats.ttest_ind(b, a, equal_var=False)
    u = stats.mannwhitneyu(b, a, alternative="two-sided", method="asymptotic")
    ks = stats.ks_2samp(a, b)
    lev_mean = stats.levene(a, b, center="mean")
    lev_med = stats.levene(a, b, center="median")
    d, lo, hi, g = cohens_d(a, b)
    return {
        "n_A": len(a), "n_B": len(b),
        "mean_A": a.mean(), "mean_B": b.mean(), "diff_B_minus_A": b.mean() - a.mean(),
        "median_A": np.median(a), "median_B": np.median(b),
        "sd_A": a.std(ddof=1), "sd_B": b.std(ddof=1),
        "var_ratio_B/A": b.var(ddof=1) / a.var(ddof=1),
        "Welch_t": t.statistic, "Welch_p": t.pvalue,
        "MWU_U": u.statistic, "MWU_p": u.pvalue,
        "P(B>A)": u.statistic / (len(a) * len(b)),   # common-language effect size
        "KS_D": ks.statistic, "KS_p": ks.pvalue,
        "Levene_mean_p": lev_mean.pvalue,
        "BrownForsythe_p": lev_med.pvalue,
        "cohen_d": d, "d_CI_low": lo, "d_CI_high": hi, "hedges_g": g,
        "effect_size": label_effect(d),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b")
    ap.add_argument("--label-a", default="A")
    ap.add_argument("--label-b", default="B")
    ap.add_argument("--group-col")
    ap.add_argument("--ga")
    ap.add_argument("--gb")
    ap.add_argument("--ngoai-ngu-code", help="chỉ lấy điểm Ngoại ngữ của mã này (vd. N1 = tiếng Anh)")
    ap.add_argument("--out", default="ket_qua_kiem_dinh.csv")
    args = ap.parse_args()

    if args.group_col:
        df = load(args.a)
        A = df[df[args.group_col] == args.ga]
        B = df[df[args.group_col] == args.gb]
        la, lb = args.ga, args.gb
    else:
        A, B = load(args.a), load(args.b)
        la, lb = args.label_a, args.label_b

    if args.ngoai_ngu_code:
        A, B = A.copy(), B.copy()
        for X in (A, B):
            X.loc[X["ma_ngoai_ngu"] != args.ngoai_ngu_code, "ngoai_ngu"] = np.nan

    rows = []
    for s in SUBJECTS:
        if s in A and s in B:
            r = compare(A[s], B[s])
            r = {"mon": s, **r}
            rows.append(r)
    res = pd.DataFrame(rows)
    res.insert(1, "A", la)
    res.insert(2, "B", lb)
    res.to_csv(args.out, index=False, encoding="utf-8-sig")

    pd.set_option("display.width", 220, "display.max_columns", 50)
    print(res[["mon", "n_A", "n_B", "mean_A", "mean_B", "diff_B_minus_A",
               "cohen_d", "effect_size", "KS_D", "var_ratio_B/A"]].round(3))
    print(f"\nĐã lưu: {args.out}")


if __name__ == "__main__":
    main()
