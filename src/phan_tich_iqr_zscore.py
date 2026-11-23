#!/usr/bin/env python
"""So sánh IQR và Z-score điểm thi THPT 2023-2025.

Chạy:
python src/phan_tich_iqr_zscore.py \
  --2023 data/processed/week3/exam_2023.parquet \
  --2024 "diem_thi_thpt_2024.csv" \
  --2025 data/dataset_diem_thi_thpt_2025.csv

Có thể truyền đường dẫn CSV hoặc Parquet. Kết quả được lưu trong outputs/iqr_zscore/.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SUBJECTS = {
    "toan": "Toán",
    "ngu_van": "Ngữ văn",
    "ngoai_ngu": "Ngoại ngữ",
    "vat_li": "Vật lý",
    "hoa_hoc": "Hóa học",
    "sinh_hoc": "Sinh học",
    "lich_su": "Lịch sử",
    "dia_li": "Địa lý",
    "gdcd": "GDCD",
    "kinh_te_phap_luat": "Kinh tế và Pháp luật",
}
ALIASES = {
    "math": "toan", "literature": "ngu_van", "english": "ngoai_ngu",
    "physics": "vat_li", "chemistry": "hoa_hoc", "biology": "sinh_hoc",
    "history": "lich_su", "geography": "dia_li", "civiceducation": "gdcd",
    "kinhtephapluat": "kinh_te_phap_luat",
}

def read_data(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Không tìm thấy dữ liệu: {p}")
    if p.suffix.lower() in {".parquet", ".pq"}:
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p, low_memory=False)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    rename = {}
    for c in df.columns:
        compact = c.replace("_", "").replace("-", "")
        if compact in ALIASES:
            rename[c] = ALIASES[compact]
    return df.rename(columns=rename)

def calculate(df: pd.DataFrame, year: int) -> list[dict]:
    rows = []
    for col, label in SUBJECTS.items():
        if col not in df.columns:
            continue
        x = pd.to_numeric(df[col], errors="coerce").dropna()
        x = x[(x >= 0) & (x <= 10)]
        if len(x) < 2:
            continue
        q1, med, q3 = x.quantile([.25, .50, .75]).tolist()
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mean, sd = x.mean(), x.std(ddof=0)
        z = (x - mean) / sd if sd else pd.Series(np.zeros(len(x)), index=x.index)
        rows.append({
            "year": year, "subject": label, "column": col, "n": int(len(x)),
            "q1": q1, "median": med, "q3": q3, "iqr": iqr,
            "iqr_lower_fence": low, "iqr_upper_fence": high,
            "iqr_outlier_n": int(((x < low) | (x > high)).sum()),
            "iqr_outlier_pct": float(((x < low) | (x > high)).mean() * 100),
            "mean": mean, "std": sd,
            "z_outlier_n": int((z.abs() > 3).sum()),
            "z_outlier_pct": float((z.abs() > 3).mean() * 100),
        })
    return rows

def main():
    ap = argparse.ArgumentParser()
    for y in (2023, 2024, 2025):
        ap.add_argument(f"--{y}", dest=f"y{y}", required=True, help=f"File dữ liệu năm {y} (CSV/Parquet)")
    ap.add_argument("--out", default="outputs/iqr_zscore")
    args = ap.parse_args()
    frames = []
    for year in (2023, 2024, 2025):
        df = read_data(getattr(args, f"y{year}"))
        frames.extend(calculate(df, year))
    result = pd.DataFrame(frames)
    if result.empty:
        raise ValueError("Không tìm thấy cột môn học phù hợp. Kiểm tra tên cột của ba bộ dữ liệu.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "bang_so_sanh_iqr_zscore.csv", index=False, encoding="utf-8-sig")

    # Biểu đồ IQR: mỗi môn có 3 cột tương ứng 3 năm.
    pivot_iqr = result.pivot(index="subject", columns="year", values="iqr")
    ax = pivot_iqr.plot(kind="bar", figsize=(13, 6), width=.78)
    ax.set_title("So sánh IQR điểm thi theo môn, 2023-2025")
    ax.set_xlabel("Môn thi"); ax.set_ylabel("IQR (điểm)")
    ax.legend(title="Năm"); ax.grid(axis="y", alpha=.25)
    plt.xticks(rotation=25, ha="right"); plt.tight_layout()
    plt.savefig(out / "so_sanh_iqr_2023_2025.png", dpi=180); plt.close()

    # Biểu đồ tỷ lệ ngoại lệ theo Z-score.
    pivot_z = result.pivot(index="subject", columns="year", values="z_outlier_pct")
    ax = pivot_z.plot(kind="bar", figsize=(13, 6), width=.78)
    ax.set_title("Tỷ lệ điểm có |Z-score| > 3 theo môn, 2023-2025")
    ax.set_xlabel("Môn thi"); ax.set_ylabel("Tỷ lệ (%)")
    ax.legend(title="Năm"); ax.grid(axis="y", alpha=.25)
    plt.xticks(rotation=25, ha="right"); plt.tight_layout()
    plt.savefig(out / "so_sanh_zscore_2023_2025.png", dpi=180); plt.close()

    # Biểu đồ khoảng tứ phân vị Q1-Q3 và trung vị.
    subjects = list(result["subject"].drop_duplicates())
    fig, axes = plt.subplots(len(subjects), 1, figsize=(12, max(4, 2.3 * len(subjects))), squeeze=False)
    for ax, subject in zip(axes[:, 0], subjects):
        sub = result[result.subject == subject].sort_values("year")
        for j, (_, r) in enumerate(sub.iterrows()):
            ax.plot([r.q1, r.q3], [j, j], linewidth=7, solid_capstyle="round")
            ax.scatter(r["median"], j, s=45, zorder=3)
            ax.text(r.q3 + .08, j, f'{int(r.year)}  IQR={r.iqr:.2f}', va="center", fontsize=8)
        ax.set_yticks(range(len(sub))); ax.set_yticklabels(sub.year.astype(str))
        ax.set_xlim(0, 10.8); ax.set_xlabel("Điểm"); ax.set_title(subject, loc="left")
        ax.grid(axis="x", alpha=.2)
    fig.suptitle("Khoảng Q1-Q3 và trung vị điểm thi theo môn", y=1.002)
    fig.tight_layout()
    fig.savefig(out / "khoang_tu_phan_vi_2023_2025.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Đã lưu {len(result)} dòng thống kê và 3 biểu đồ tại: {out.resolve()}")

if __name__ == "__main__":
    main()
