#!/usr/bin/env python3
"""Generate actual 2023 vs 2025 subject-score distribution plots from project data."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA23 = ROOT / "data/processed/week5/week5_final+du_lieu_cuoi.csv"
DATA25 = ROOT / "data2025/data/dataset_diem_thi_thpt_2025.csv"
OUT = ROOT / "outputs/week6/figures"
OUT.mkdir(parents=True, exist_ok=True)
SUBJECTS = [
    ("Toán", "Mathematics", "toan", "toan"),
    ("Ngữ văn", "Literature", "ngu_van", "ngu_van"),
    ("Ngoại ngữ", "Foreign language", "ngoai_ngu", "ngoai_ngu"),
    ("Vật lý", "Physics", "vat_li", "vat_li"),
    ("Hóa học", "Chemistry", "hoa_hoc", "hoa_hoc"),
    ("Sinh học", "Biology", "sinh_hoc", "sinh_hoc"),
    ("Lịch sử", "History", "lich_su", "lich_su"),
    ("Địa lý", "Geography", "dia_li", "dia_li"),
]
COLORS = {"2023": "#1769aa", "2025": "#e87522"}

def clean(series):
    x = pd.to_numeric(series, errors="coerce").dropna()
    return x[(x >= 0) & (x <= 10)].to_numpy(dtype=float)

def main():
    if not DATA23.exists():
        raise FileNotFoundError(DATA23)
    if not DATA25.exists():
        raise FileNotFoundError(DATA25)
    d23 = pd.read_csv(DATA23, low_memory=False)
    d25 = pd.read_csv(DATA25, low_memory=False)
    rng = np.random.default_rng(20251021)
    rows = []
    for vn, c23, c25, key in SUBJECTS:
        x23, x25 = clean(d23[c23]), clean(d25[c25])
        if not len(x23) or not len(x25):
            raise ValueError(f"No valid observations for {vn}: n23={len(x23)}, n25={len(x25)}")
        fig, axes = plt.subplots(2, 2, figsize=(13, 8))
        fig.suptitle(f"So sánh phổ điểm {vn} — THPT 2023 và 2025", fontsize=16, fontweight="bold")
        # Histogram density: all observations, common bins and scale.
        ax = axes[0, 0]
        bins = np.arange(0, 10.0001, 0.25)
        ax.hist(x23, bins=bins, density=True, alpha=.42, color=COLORS["2023"], label=f"2023 (N={len(x23):,})")
        ax.hist(x25, bins=bins, density=True, alpha=.42, color=COLORS["2025"], label=f"2025 (N={len(x25):,})")
        ax.set_title("Histogram chồng lớp"); ax.set_xlabel("Điểm"); ax.set_ylabel("Mật độ"); ax.set_xlim(0,10); ax.legend(fontsize=8)
        # KDE approximation using a deterministic sample, bandwidth 0.20 points.
        ax = axes[0, 1]
        for label, values in (("2023", x23), ("2025", x25)):
            smp = values if len(values) <= 150000 else rng.choice(values, 150000, replace=False)
            grid = np.linspace(0, 10, 401)
            # Gaussian kernel on a regular grid, using histogram + convolution for speed.
            hist, edges = np.histogram(smp, bins=np.linspace(-1,11,1201), density=True)
            dx = edges[1]-edges[0]
            sigma = .20/dx
            radius = int(np.ceil(4*sigma))
            xx = np.arange(-radius, radius+1)
            kernel = np.exp(-.5*(xx/sigma)**2); kernel /= kernel.sum()
            smooth = np.convolve(hist, kernel, mode="same")
            centers = (edges[:-1]+edges[1:])/2
            density = np.interp(grid, centers, smooth, left=0, right=0)
            ax.plot(grid, density, color=COLORS[label], linewidth=2.2, label=f"{label} (N={len(values):,})")
        ax.set_title("KDE — mật độ ước lượng"); ax.set_xlabel("Điểm"); ax.set_ylabel("Mật độ"); ax.set_xlim(0,10); ax.legend(fontsize=8)
        # Boxplot on full data, outlier points hidden to preserve readability.
        ax = axes[1, 0]
        ax.boxplot([x23, x25], labels=["2023", "2025"], showfliers=False, patch_artist=True,
                   boxprops={"facecolor":"#cbd5e1"}, medianprops={"color":"#111827","linewidth":2})
        ax.set_title("Boxplot (không hiển thị từng ngoại lệ)"); ax.set_ylabel("Điểm"); ax.set_ylim(0,10); ax.grid(axis="y", alpha=.2)
        # Violin uses deterministic sample to limit runtime.
        ax = axes[1, 1]
        v23 = x23 if len(x23) <= 12000 else rng.choice(x23, 12000, replace=False)
        v25 = x25 if len(x25) <= 12000 else rng.choice(x25, 12000, replace=False)
        parts = ax.violinplot([v23, v25], positions=[1,2], showmeans=False, showmedians=True, showextrema=False)
        for i, body in enumerate(parts["bodies"]):
            body.set_facecolor([COLORS["2023"], COLORS["2025"]][i]); body.set_edgecolor([COLORS["2023"], COLORS["2025"]][i]); body.set_alpha(.5)
        parts["cmedians"].set_color("#111827")
        ax.set_xticks([1,2], ["2023", "2025"]); ax.set_title("Violin plot (mẫu cố định tối đa 12.000 điểm)"); ax.set_ylabel("Điểm"); ax.set_ylim(0,10); ax.grid(axis="y", alpha=.2)
        for ax in axes.flat:
            ax.grid(axis="y", alpha=.18)
        fig.text(.5, .012, "Nguồn: dữ liệu dự án; điểm hợp lệ 0–10; giữ nguyên giá trị thiếu. Histogram/boxplot dùng toàn bộ điểm hợp lệ; KDE/violin dùng mẫu xác định khi cần.", ha="center", fontsize=8)
        fig.tight_layout(rect=[0, .035, 1, .94])
        path = OUT / f"pho_diem_{key}_2023_2025.svg"
        fig.savefig(path, format="svg", bbox_inches="tight")
        plt.close(fig)
        rows.append({"subject":vn,"n_2023":len(x23),"n_2025":len(x25),"figure":path.name})
        print(f"Created {path.name}: N2023={len(x23)}, N2025={len(x25)}")
    pd.DataFrame(rows).to_csv(OUT / "manifest.csv", index=False)
    print("Created manifest.csv")

if __name__ == "__main__":
    main()
