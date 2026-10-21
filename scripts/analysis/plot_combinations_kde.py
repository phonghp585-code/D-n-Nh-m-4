#!/usr/bin/env python3
"""Generate four KDE figures comparing 24 THPT admission combinations in 2023 vs 2025."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parents[2]
DATA23 = ROOT / "data/processed/week5/week5_final+du_lieu_cuoi.csv"
DATA25_CANDIDATES = [
    ROOT / "data/dataset_diem_thi_thpt_2025.csv",
    ROOT / "data/processed/week5/dataset_diem_thi_thpt_2025.csv",
]
OUT = ROOT / "outputs/combinations/figures"
OUT.mkdir(parents=True, exist_ok=True)
COMBOS = {
"A00":("Toán + Lý + Hóa",["Mathematics","Physics","Chemistry"],"diem_A00"),
"A01":("Toán + Lý + Anh",["Mathematics","Physics","Foreign language"],"diem_A01"),
"A02":("Toán + Lý + Sinh",["Mathematics","Physics","Biology"],"diem_A02"),
"A08":("Toán + Sử + GDCD/GDKT&PL",["Mathematics","History","Civic education"],"diem_A08"),
"A09":("Toán + Địa + GDCD/GDKT&PL",["Mathematics","Geography","Civic education"],"diem_A09"),
"B00":("Toán + Hóa + Sinh",["Mathematics","Chemistry","Biology"],"diem_B00"),
"B08":("Toán + Sinh + Anh",["Mathematics","Biology","Foreign language"],"diem_B08"),
"C00":("Văn + Sử + Địa",["Literature","History","Geography"],"diem_C00"),
"C01":("Văn + Toán + Lý",["Literature","Mathematics","Physics"],"diem_C01"),
"C02":("Văn + Toán + Hóa",["Literature","Mathematics","Chemistry"],"diem_C02"),
"C03":("Văn + Toán + Sử",["Literature","Mathematics","History"],"diem_C03"),
"C04":("Văn + Toán + Địa",["Literature","Mathematics","Geography"],"diem_C04"),
"C14":("Văn + Toán + GDCD/GDKT&PL",["Literature","Mathematics","Civic education"],"diem_C14"),
"C19":("Văn + Sử + GDCD/GDKT&PL",["Literature","History","Civic education"],"diem_C19"),
"C20":("Văn + Địa + GDCD/GDKT&PL",["Literature","Geography","Civic education"],"diem_C20"),
"D01":("Toán + Văn + Anh",["Mathematics","Literature","Foreign language"],"diem_D01"),
"D07":("Toán + Hóa + Anh",["Mathematics","Chemistry","Foreign language"],"diem_D07"),
"D08":("Toán + Sinh + Anh",["Mathematics","Biology","Foreign language"],"diem_D08"),
"D09":("Toán + Sử + Anh",["Mathematics","History","Foreign language"],"diem_D09"),
"D10":("Toán + Địa + Anh",["Mathematics","Geography","Foreign language"],"diem_D10"),
"D14":("Văn + Sử + Anh",["Literature","History","Foreign language"],"diem_D14"),
"D15":("Văn + Địa + Anh",["Literature","Geography","Foreign language"],"diem_D15"),
"D66":("Văn + GDCD/GDKT&PL + Anh",["Literature","Civic education","Foreign language"],"diem_D66"),
"D84":("Toán + GDCD/GDKT&PL + Anh",["Mathematics","Civic education","Foreign language"],"diem_D84"),
}
GROUPS = [list(COMBOS)[i:i+6] for i in range(0,24,6)]
BLUE, ORANGE = "#1769aa", "#e87522"

def load_data():
    if not DATA23.exists():
        raise FileNotFoundError(f"Missing 2023 data: {DATA23}")
    p25 = next((p for p in DATA25_CANDIDATES if p.exists()), None)
    if p25 is None:
        raise FileNotFoundError("2025 CSV not found. Expected data/dataset_diem_thi_thpt_2025.csv.")
    return pd.read_csv(DATA23, low_memory=False), pd.read_csv(p25, low_memory=False)

def values_for(d23, d25, code, spec):
    label, cols23, col25 = spec
    x23 = d23[cols23].apply(pd.to_numeric, errors="coerce")
    s23 = x23.sum(axis=1, min_count=3)
    s23 = s23[(s23 >= 0) & (s23 <= 30)].dropna().to_numpy()
    if col25 in d25:
        s25 = pd.to_numeric(d25[col25], errors="coerce").dropna()
    else:
        # Fallback for CSVs containing subject scores but no precomputed combination.
        map25 = {"Mathematics":"toan","Literature":"ngu_van","Foreign language":"ngoai_ngu",
                 "Physics":"vat_li","Chemistry":"hoa_hoc","Biology":"sinh_hoc",
                 "History":"lich_su","Geography":"dia_li","Civic education":"gdktpl"}
        cols = [map25[c] for c in cols23]
        x25 = d25[cols].apply(pd.to_numeric, errors="coerce")
        s25 = x25.sum(axis=1, min_count=3).dropna()
    s25 = s25[(s25 >= 0) & (s25 <= 30)].to_numpy()
    return s23, s25

def density_curve(values, grid, rng):
    values = np.asarray(values, dtype=float)
    if len(values) > 120_000:
        values = rng.choice(values, 120_000, replace=False)
    sd = np.std(values, ddof=1)
    if len(values) < 2 or not np.isfinite(sd) or sd == 0:
        return np.zeros_like(grid)
    # Fixed bandwidth in score points, implemented as an equivalent KDE factor.
    kde = gaussian_kde(values, bw_method=0.35 / sd)
    return kde(grid)

def main():
    d23, d25 = load_data()
    rng = np.random.default_rng(2025)
    grid = np.linspace(0, 30, 601)
    manifest = []
    for gi, group in enumerate(GROUPS, start=1):
        fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharex=True)
        for ax, code in zip(axes.flat, group):
            label, _, _ = COMBOS[code]
            s23, s25 = values_for(d23, d25, code, COMBOS[code])
            ax.plot(grid, density_curve(s23, grid, rng), color=BLUE, linestyle="--",
                    linewidth=2.1, label="2023")
            ax.plot(grid, density_curve(s25, grid, rng), color=ORANGE, linestyle="-",
                    linewidth=2.1, label="2025")
            ax.set_title(f"{code} — {label}", fontsize=10)
            ax.set_xlim(0, 30)
            ax.set_xlabel("Tổng điểm tổ hợp (thang 30)")
            ax.set_ylabel("Mật độ")
            ax.grid(alpha=.22)
            ax.legend(frameon=False, fontsize=8)
            manifest.append({"combination":code,"n_2023":len(s23),"n_2025":len(s25)})
        fig.suptitle(f"Phổ điểm tổ hợp 2023 và 2025 — Nhóm {gi} (6/24 tổ hợp)", fontsize=15)
        fig.tight_layout(rect=[0,0,1,.96])
        out = OUT / f"combination_kde+tom_tat_{gi:02d}.png"
        fig.savefig(out, dpi=180, bbox_inches="tight")
        plt.close(fig)
        print(f"Created {out}")
    pd.DataFrame(manifest).to_csv(OUT / "kde_plot_sample_counts.csv", index=False)
    print(f"Created {OUT / 'kde_plot_sample_counts.csv'}")

if __name__ == "__main__":
    main()
