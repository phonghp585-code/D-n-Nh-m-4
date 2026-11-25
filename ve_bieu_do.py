"""
TÁI DỰNG CÁC BIỂU ĐỒ TRONG BÁO CÁO "Phân tích phổ điểm thi THPT Quốc gia 2023-2025"

Mọi số liệu được chép trực tiếp từ bảng/hình in trong PDF báo cáo,
nên KHÔNG cần file CSV. Chạy:

    pip install numpy matplotlib
    python ve_bieu_do_giong_bao_cao.py

"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = "outputs/figures_bao_cao"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREEN = "#1f5fbf", "#e08a00", "#2a9d6f"
C23, C24, C25 = "#2a5d8f", "#2a9d6f", "#e07b1a"


def save(fig, name):
    fig.tight_layout()
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Đã lưu:", p)


# ---------------------------------------------------------------- Hình 1.1
def hinh_1_1():
    steps = ["Đặt câu hỏi\nvà phạm vi", "Kiểm tra\nnguồn và\ndữ liệu",
             "Chuẩn hóa và\nlập bảng\nphân tích", "Thống kê, so\nsánh và trực\nquan hóa",
             "Đánh giá độ\ntin cậy và\ngiới hạn", "Báo cáo, đề\nxuất kiểm tra/\nhỗ trợ"]
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 3.4); ax.axis("off")
    w, gap = 1.7, 0.35
    for i, s in enumerate(steps):
        x = 0.2 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 1.5), w, 1.4, boxstyle="round,pad=0.03,rounding_size=0.12",
                                    fc="#ece9ff", ec="#7b6fd6", lw=1.2))
        ax.text(x + w / 2, 2.2, s, ha="center", va="center", fontsize=8.5)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + w + 0.02, 2.2), (x + w + gap - 0.02, 2.2),
                                         arrowstyle="-|>", mutation_scale=10, color="#444"))
    x0, x1 = 0.2 + w / 2, 0.2 + 5 * (w + gap) + w / 2
    ax.plot([x0, x0], [1.5, 0.6], color="#444", lw=1, ls="--")
    ax.plot([x1, x1], [1.5, 0.6], color="#444", lw=1, ls="--")
    ax.plot([x0, x1], [0.6, 0.6], color="#444", lw=1, ls="--")
    ax.annotate("", xy=(x0, 1.5), xytext=(x0, 0.6), arrowprops=dict(arrowstyle="-|>", color="#444"))
    ax.text((x0 + x1) / 2, 0.35, "phản hồi, cập nhật", ha="center", style="italic", fontsize=9, color="#555")
    ax.set_title("Hình 1.1. Vòng đời khoa học dữ liệu áp dụng cho dự án", fontsize=10, style="italic", y=-0.05)
    save(fig, "Hinh_1_1_vong_doi_KHDL.png")


# ---------------------------------------------------- Tỷ lệ thiếu 2023 (chương 2)
def thieu_2023():
    mon = ["Toán", "Ngữ văn", "Ngoại ngữ", "Vật lí", "Hóa học", "Sinh học", "Lịch sử", "Địa lí", "Giáo dục công dân"]
    pct = [1.828, 1.352, 13.802, 67.987, 67.896, 68.238, 33.130, 33.259, 44.675]
    cnt = [18687, 13821, 141063, 694871, 693942, 697435, 338613, 339926, 456608]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(mon, pct, color="#1f77b4")
    ax.invert_yaxis()
    for i, (p, c) in enumerate(zip(pct, cnt)):
        ax.text(p + 0.8, i, f"{p:.3f}%  ({c:,})".replace(",", "."), va="center", fontsize=7)
    ax.set_xlim(0, 78)
    ax.set_xlabel("Tỷ lệ thiếu (%)")
    ax.set_title("Tỷ lệ dữ liệu thiếu theo môn học – THPT 2023", fontsize=9)
    fig.text(0.01, 0.0, "Tỷ lệ tính trên 1.022.060 dòng; số lượng là số ô thiếu theo môn.", fontsize=6, color="gray")
    save(fig, "Tyle_thieu_2023.png")


# ---------------------------------------------------------------- Hình 2.1
def hinh_2_1():
    nhan = ["Có điểm nhóm tự nhiên,\nkhông có nhóm xã hội", "Có điểm nhóm xã hội,\nkhông có nhóm tự nhiên",
            "Không có điểm\ncả hai nhóm"]
    v = [329430, 683813, 8817]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar(nhan, v, color=["#1f5fbf", "#e08a00", "#8896b3"], width=0.6)
    for i, x in enumerate(v):
        ax.text(i, x + 8000, f"{x:,}".replace(",", "."), ha="center", fontsize=9)
    ax.set_title("Cấu trúc nhóm môn của thí sinh năm 2023")
    ax.set_ylim(0, 800000)
    fig.text(0.01, 0.0, "Không có hồ sơ nào có điểm ở cả hai nhóm (tổng 1.022.060 hồ sơ).", fontsize=6, color="gray")
    save(fig, "Hinh_2_1_cau_truc_nhom_mon_2023.png")


# ---------------------------------------------------------------- Hình 2.2
def hinh_2_2():
    m23 = ["Toán", "Ngữ văn", "Ngoại ngữ", "Vật lí", "Hóa học", "Sinh học", "Lịch sử", "Địa lí", "GDCD"]
    p23 = [1.8, 1.4, 13.8, 68.0, 67.9, 68.2, 33.1, 33.3, 44.7]
    m25 = ["Toán", "Ngữ văn", "Ngoại ngữ", "Vật lí", "Hóa học", "Sinh học", "Lịch sử", "Địa lí",
           "GDKT&PL", "Tin học", "Công nghệ"]
    p25 = [0.4, 0.4, 68.4, 69.3, 78.8, 93.8, 57.5, 57.9, 78.2, 99.3, 97.8]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    for ax, m, p, c, t in zip(axes, [m23, m25], [p23, p25], ["#7f8fa9", "#1f5fbf"], ["Năm 2023", "Năm 2025"]):
        ax.barh(m, p, color=c)
        ax.invert_yaxis()
        for i, x in enumerate(p):
            ax.text(x + 1, i, f"{x:.1f}%".replace(".", ","), va="center", fontsize=7)
        ax.set_title(t, fontsize=9)
        ax.set_xlim(0, 112)
        ax.set_xlabel("Tỷ lệ thiếu điểm (%)")
    fig.suptitle("Tỷ lệ thiếu điểm theo môn năm 2023 và 2025", fontsize=9, x=0.02, ha="left")
    save(fig, "Hinh_2_2_ty_le_thieu_2023_2025.png")


# ---------------------------------------------------------------- Hình 2.3
def hinh_2_3():
    mon = ["Toán", "Ngữ văn", "Ngoại ngữ", "Vật lý", "Hóa học", "Sinh học", "Lịch sử", "Địa lý", "GDCD"]
    iqr = [(0.196, 1965), (1.160, 11697), (0, 0), (0.147, 481), (0.520, 1706),
           (0.418, 1357), (0.040, 270), (0.972, 6627), (1.902, 10754)]
    z = [(0.037, 371), (0.555, 5598), (0, 0), (0.147, 481), (0.300, 985),
         (0.376, 1222), (0.017, 117), (0.342, 2332), (0.971, 5492)]
    y = np.arange(len(mon)); h = 0.38
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(y - h / 2, [a for a, _ in iqr], h, color="#2a6496", label="IQR: ngoài khoảng [Q1 − 1,5×IQR; Q3 + 1,5×IQR]")
    ax.barh(y + h / 2, [a for a, _ in z], h, color="#c0651c", label="Z-score: |Z| > 3")
    for i in range(len(mon)):
        ax.text(iqr[i][0] + 0.03, i - h / 2, f"{iqr[i][0]:.3f}% ({iqr[i][1]:,})".replace(",", "."), va="center", fontsize=7, color="#2a6496")
        ax.text(z[i][0] + 0.03, i + h / 2, f"{z[i][0]:.3f}% ({z[i][1]:,})".replace(",", "."), va="center", fontsize=7, color="#c0651c")
    ax.set_yticks(y, mon); ax.invert_yaxis()
    ax.set_xlim(0, 2.5)
    ax.set_xlabel("Tỷ lệ điểm bị gắn cờ trong số điểm quan sát của từng môn (%)")
    ax.set_ylabel("Môn học")
    ax.set_title("So sánh ngoại lệ giữa IQR và Z-score", fontweight="bold")
    ax.legend(fontsize=7, loc="upper left", frameon=False)
    fig.text(0.01, 0.0, "Hai phương pháp có thể đánh dấu cùng một điểm; không cộng hai thanh để tính tổng.", fontsize=6, color="gray")
    save(fig, "Hinh_2_3_IQR_vs_Zscore.png")


# ---------------------------------------------------------------- Hình 2.4
def hinh_2_4():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.2]})
    a = axes[0]
    a.bar(["Thí sinh gắn cờ\nIQR", "Thí sinh gắn cờ\nZ-score"], [30190, 15037], color=[BLUE, ORANGE], width=0.75)
    for i, x in enumerate([30190, 15037]):
        a.text(i, x + 500, f"{x:,}".replace(",", "."), ha="center", fontsize=8)
    a.set_ylim(0, 35000); a.set_title("Năm 2023: theo phương pháp phát hiện", fontsize=9)
    b = axes[1]
    v = [43642, 49786, 38640]
    b.bar(["2023", "2024", "2025"], v, color=["#7f8fa9", "#a8b8cf", BLUE], width=0.75)
    for i, x in enumerate(v):
        b.text(i, x + 500, f"{x:,}".replace(",", "."), ha="center", fontsize=8)
    b.set_ylim(0, 52000); b.set_title("Phân tích theo tỉnh × môn: thí sinh có ≥1 điểm bị gắn cờ", fontsize=9)
    fig.suptitle("Số thí sinh bị gắn cờ ngoại lệ", fontsize=9, x=0.02, ha="left")
    fig.text(0.01, 0.0, "Hai bảng thuộc hai quy trình khác nhau nên không so sánh trực tiếp. Cờ ngoại lệ không đồng nghĩa với gian lận.", fontsize=6, color="gray")
    save(fig, "Hinh_2_4_so_thi_sinh_bi_co.png")


# ------------------------------------------------- Hình 1 (3.9): TB 3 năm
def hinh_tb_3_nam():
    mon = ["Toán", "Ngữ văn", "Vật lý", "Hóa học", "Sinh học", "Lịch sử", "Địa lý", "Tiếng Anh (N1)"]
    tb = {2023: [6.251, 6.858, 6.574, 6.745, 6.395, 6.026, 6.148, 5.454],
          2024: [6.447, 7.231, 6.667, 6.681, 6.284, 6.570, 7.194, 5.513],
          2025: [4.783, 7.002, 6.985, 6.065, 5.778, 6.519, 6.628, 5.375]}
    y = np.arange(len(mon))
    arr = np.array(list(tb.values()))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hlines(y, arr.min(0), arr.max(0), color="#8aa0b5", lw=1.5, zorder=1)
    for (yr, v), c in zip(tb.items(), [C23, C24, C25]):
        ax.scatter(v, y, color=c, s=40, label=str(yr), zorder=2)
    ax.set_yticks(y, mon)
    ax.set_xlabel("Điểm trung bình")
    ax.set_title("Trung bình theo môn: ba đoàn hệ 2023, 2024, 2025")
    ax.legend(title="Năm", loc="upper left", fontsize=8)
    save(fig, "Hinh_1_trung_binh_3_nam.png")


# ------------------------------------------------- Hình 3 (3.9): heatmap 37 cặp
PAIRS = [
    ("Hà Giang", "Toán", 67.91, 61.18, 86.52), ("Hà Giang", "Ngữ văn", 41.87, 22.69, 24.52),
    ("Hà Giang", "Lịch sử", 46.91, 29.91, 34.65), ("Hà Giang", "Địa lý", 29.77, 14.59, 32.75),
    ("Hà Giang", "Tiếng Anh", 80.96, 79.96, 51.33), ("Cao Bằng", "Toán", 53.39, 48.23, 80.81),
    ("Cao Bằng", "Ngữ văn", 30.17, 25.36, 23.71), ("Cao Bằng", "Tiếng Anh", 72.01, 70.40, 46.97),
    ("Lai Châu", "Toán", 33.26, 33.50, 76.54), ("Lai Châu", "Tiếng Anh", 72.76, 76.12, 51.79),
    ("Lào Cai", "Tiếng Anh", 61.58, 63.03, 42.46), ("Lạng Sơn", "Toán", 45.51, 36.89, 77.61),
    ("Lạng Sơn", "Tiếng Anh", 68.47, 66.93, 41.77), ("Bắc Kạn", "Toán", 44.63, 41.59, 81.79),
    ("Bắc Kạn", "Tiếng Anh", 71.48, 71.69, 41.67), ("Thái Nguyên", "Tiếng Anh", 57.05, 56.14, 44.36),
    ("Yên Bái", "Toán", 42.68, 34.53, 75.77), ("Sơn La", "Toán", 52.67, 43.02, 84.69),
    ("Sơn La", "Tiếng Anh", 77.66, 72.39, 40.13), ("Hòa Bình", "Toán", 47.29, 40.07, 77.37),
    ("Hòa Bình", "Tiếng Anh", 71.24, 69.77, 42.87), ("Quảng Trị", "Tiếng Anh", 60.52, 60.89, 42.78),
    ("Kon Tum", "Tiếng Anh", 61.86, 60.41, 39.92), ("Gia Lai", "Tiếng Anh", 60.63, 56.53, 44.54),
    ("Đắk Lắk", "Toán", 36.80, 32.45, 67.16), ("Đắk Lắk", "Tiếng Anh", 63.20, 63.31, 46.93),
    ("Ninh Thuận", "Tiếng Anh", 55.86, 55.70, 50.00), ("Trà Vinh", "Toán", 37.50, 28.59, 75.92),
    ("Trà Vinh", "Tiếng Anh", 68.81, 61.10, 54.84), ("Sóc Trăng", "Toán", 32.84, 28.36, 75.36),
    ("Sóc Trăng", "Tiếng Anh", 59.72, 62.06, 58.60), ("Cà Mau", "Tiếng Anh", 56.87, 57.25, 52.56),
    ("Điện Biên", "Toán", 47.40, 43.65, 81.40), ("Điện Biên", "Tiếng Anh", 79.58, 78.66, 37.91),
    ("Đắk Nông", "Toán", 33.91, 29.59, 70.56), ("Đắk Nông", "Tiếng Anh", 69.40, 70.67, 50.68),
    ("Hậu Giang", "Tiếng Anh", 68.19, 64.66, 54.82),
]


def hinh_heatmap_37():
    data = np.array([[p[2], p[3], p[4]] for p in PAIRS])
    lab = [f"{p[0]} – {p[1]}" for p in PAIRS]
    fig, ax = plt.subplots(figsize=(8, 10))
    im = ax.imshow(data, aspect="auto", cmap="viridis", vmin=0, vmax=100)
    ax.set_xticks(range(3), ["2023", "2024", "2025"])
    ax.set_yticks(range(len(lab)), lab, fontsize=7)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax); cb.set_label("Tỷ lệ dưới 5 (%)")
    ax.set_title("Tỷ lệ bài dưới 5 ở 37 cặp tỉnh–môn được sàng lọc")
    save(fig, "Hinh_3_heatmap_37_cap_tinh_mon.png")


# ------------------------------------------------- Hình 4 (3.9): vùng miền
def hinh_vung_mien():
    nam = [2023, 2024, 2025]
    toan = [1.349, 1.272, 1.288]
    van = [0.728, 0.980, 0.781]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(nam, toan, marker="o", color="#1f77b4", label="Toán")
    ax.plot(nam, van, marker="o", color="#ff7f0e", label="Ngữ văn")
    ax.set_xticks(nam)
    ax.set_ylabel("ĐBSH trừ Tây Bắc (điểm)")
    ax.set_title("Chênh lệch điểm trung bình giữa ĐBSH và Tây Bắc")
    ax.legend(loc="center right")
    fig.text(0.01, 0.0, "Khoảng cách kết quả thi giữa hai nhóm vùng, không phải ước lượng nhân quả.", fontsize=6, color="gray")
    save(fig, "Hinh_4_chenh_lech_vung_mien.png")


# ------------------------------------------------- Hình 5 (3.9): tổ hợp
def hinh_to_hop():
    nam = [2023, 2024, 2025]
    th = {"A00": ([32.0, 32.4, 14.3], "#1f77b4"), "A01": ([30.9, 31.0, 13.0], "#ff7f0e"),
          "B00": ([31.9, 32.2, 4.0], "#2ca02c"), "C00": ([67.0, 66.3, 26.3], "#d62728"),
          "C03": ([65.8, 65.1, 42.1], "#9467bd"), "D01": ([85.8, 85.0, 31.0], "#8c564b")}
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, (v, c) in th.items():
        ax.plot(nam, v, marker="o", color=c, label=k)
    ax.set_xticks(nam)
    ax.set_ylabel("Tỷ lệ hồ sơ trên hồ sơ có điểm (%)")
    ax.set_title("Tỷ lệ hồ sơ có đủ ba điểm ở một số tổ hợp")
    ax.legend(ncol=3, fontsize=8)
    save(fig, "Hinh_5_ty_le_to_hop.png")


# ------------------------------------------------- Heatmap tương quan 2023
MON15 = ["Toán", "Ngữ văn", "Vật lý", "Hóa học", "Sinh học", "Lịch sử", "Địa lý", "GDCD",
         "Anh (N1)", "Nga (N2)", "Pháp (N3)", "Trung (N4)", "Đức (N5)", "Nhật (N6)", "Hàn (N7)"]
N = np.nan
# 8 hàng đầu: đủ 15 cột (chéo = N). 7 hàng sau: chỉ 8 cột đầu (các môn gốc).
PEARSON = [
    [N, .46, .57, .46, .31, .47, .45, .50, .59, .28, .56, .60, .32, .49, .35],
    [.46, N, .18, .20, .26, .45, .43, .48, .37, .15, .51, .51, .38, .32, .25],
    [.57, .18, N, .38, .18, N, N, N, .32, N, .32, .17, N, .28, -.10],
    [.46, .20, .38, N, .41, N, N, N, .09, N, .28, .22, N, .10, .21],
    [.31, .26, .18, .41, N, N, N, N, .29, N, .40, .29, N, .38, .03],
    [.47, .45, N, N, N, N, .61, .58, .37, .04, .28, .38, .56, .23, .16],
    [.45, .43, N, N, N, .61, N, .57, .30, .02, .26, .34, .37, .20, .13],
    [.50, .48, N, N, N, .58, .57, N, .39, .22, .47, .43, .60, .27, .08],
    [.59, .37, .32, .09, .29, .37, .30, .39],
    [.28, .15, N, N, N, .04, .02, .22],
    [.56, .51, .32, .28, .40, .28, .26, .47],
    [.60, .51, .17, .22, .29, .38, .34, .43],
    [.32, .38, N, N, N, .56, .37, .60],
    [.49, .32, .28, .10, .38, .23, .20, .27],
    [.35, .25, -.10, .21, .03, .16, .13, .08],
]
SPEARMAN = [
    [N, .42, .56, .44, .29, .46, .43, .48, .61, .18, .51, .54, .32, .49, .36],
    [.42, N, .17, .19, .26, .44, .40, .45, .37, .23, .50, .45, .36, .32, .25],
    [.56, .17, N, .37, .18, N, N, N, .31, N, .32, .16, N, .26, -.09],
    [.44, .19, .37, N, .39, N, N, N, .08, N, .28, .20, N, .14, .15],
    [.29, .26, .18, .39, N, N, N, N, .28, N, .40, .33, N, .41, .07],
    [.46, .44, N, N, N, N, .59, .59, .37, .13, .28, .37, .54, .23, .16],
    [.43, .40, N, N, N, .59, N, .56, .31, .09, .29, .32, .35, .22, .12],
    [.48, .45, N, N, N, .59, .56, N, .41, .29, .41, .40, .59, .28, .10],
    [.61, .37, .31, .08, .28, .37, .31, .41],
    [.18, .23, N, N, N, .13, .09, .29],
    [.51, .50, .32, .28, .40, .28, .29, .41],
    [.54, .45, .16, .20, .33, .37, .32, .40],
    [.32, .36, N, N, N, .54, .35, .59],
    [.49, .32, .26, .14, .41, .23, .22, .28],
    [.36, .25, -.09, .15, .07, .16, .12, .10],
]


def to_matrix(rows):
    m = np.full((15, 15), np.nan)
    for i, r in enumerate(rows):
        m[i, :len(r)] = r
    return m


def hinh_tuong_quan(rows, ten, nhan):
    m = to_matrix(rows)
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    im = ax.imshow(np.ma.masked_invalid(m), cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_facecolor("#eeeeee")
    ax.set_xticks(range(15), MON15, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(15), MON15, fontsize=7)
    ax.grid(False)
    for i in range(15):
        for j in range(15):
            if i == j:
                continue
            v = m[i, j]
            ax.text(j, i, "—" if np.isnan(v) else f"{v:.2f}", ha="center", va="center",
                    fontsize=6, color="#555" if np.isnan(v) else "k")
    cb = fig.colorbar(im, ax=ax, shrink=0.8); cb.set_label(nhan)
    ax.set_title(f"{ten} — 2023\nÔ xám: không ước lượng; đường chéo bỏ qua", fontsize=9)
    save(fig, f"Heatmap_{ten.lower()}_2023.png")


if __name__ == "__main__":
    hinh_1_1()
    thieu_2023()
    hinh_2_1()
    hinh_2_2()
    hinh_2_3()
    hinh_2_4()
    hinh_tb_3_nam()
    hinh_heatmap_37()
    hinh_vung_mien()
    hinh_to_hop()
    hinh_tuong_quan(PEARSON, "Pearson", "pearson_r")
    hinh_tuong_quan(SPEARMAN, "Spearman", "spearman_rho")
    print("Xong. Xem thư mục:", OUT)
