"""Week 4: reproducible outlier analysis, provenance and conservative cleaning.

No network access on reruns. Human source checks are versioned separately.
No Week 3 pipeline is invoked and no existing Week 3 artifact is overwritten.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src import week4_explanations as explain

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/original.csv"
TABLES = ROOT / "outputs/tables"
FIGURE = ROOT / "outputs/figures/week4_boxplot.png"
CLEANED = ROOT / "data/processed/week4_cleaned.csv"
METRICS = ROOT / "outputs/week4_metrics.json"
REPORT = ROOT / "docs/week4_report+bao_cao.md"
CHECKS = ROOT / "docs/week4_source_checks.json"
SCORES = ["Mathematics", "Literature", "Foreign language", "Physics", "Chemistry",
          "Biology", "History", "Geography", "Civic education"]
TEXT = ["Student ID", "Foreign language code"]
COLUMNS = [TEXT[0], *SCORES, TEXT[1]]
VALID_CODES = {f"N{i}" for i in range(1, 8)}
VN = dict(zip(SCORES, ["Toán", "Ngữ văn", "Ngoại ngữ", "Vật lý", "Hóa học",
                       "Sinh học", "Lịch sử", "Địa lý", "GDCD"]))


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def load_raw(path: Path = RAW) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={col: "string" for col in TEXT},
                     keep_default_na=False, na_values=[""], skip_blank_lines=False)
    if list(df.columns) != COLUMNS:
        raise ValueError("Schema nguồn khác 11 cột đã thống nhất")
    for col in SCORES:
        df[col] = pd.to_numeric(df[col], errors="raise").astype(float)
        if (~np.isfinite(df[col].dropna())).any():
            raise ValueError(f"Điểm không hữu hạn trong {col}")
    return df


def normalize_text(series: pd.Series, uppercase: bool = False) -> pd.Series:
    """Thống nhất cách viết; giữ chuỗi để ID không mất số 0 đầu."""
    result = series.astype("string").str.normalize("NFKC").str.strip()
    result = result.str.replace(r"\s+", " ", regex=True)
    if uppercase:
        result = result.str.upper()
    return result.mask(result.eq(""), pd.NA)


def invalid_text(series: pd.Series, column: str) -> pd.Series:
    valid = series.str.fullmatch(r"[0-9]{8}") if column == TEXT[0] else series.isin(VALID_CODES)
    return series.notna() & ~valid.fillna(False)


def standardize(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Trả dữ liệu chuẩn hóa, bảng trước/sau và lỗi định dạng cần kiểm tra."""
    cleaned = df.copy()
    summaries, issues = [], []
    for col in TEXT:
        before = df[col]
        after = normalize_text(before, uppercase=(col == TEXT[1]))
        # Hai ô cùng thiếu là không đổi; không đếm NA != NA thành một thay đổi.
        changed = ~(before.eq(after).fillna(False) | (before.isna() & after.isna()))
        cleaned[col] = after
        bad = invalid_text(after, col)
        summaries.append({
            "column": col, "distinct_before": int(before.nunique(dropna=True)),
            "distinct_after": int(after.nunique(dropna=True)),
            "missing_before": int(before.isna().sum()), "missing_after": int(after.isna().sum()),
            "changed_rows": int(changed.sum()), "invalid_before": int(invalid_text(before, col).sum()),
            "invalid_after": int(bad.sum()),
            "rule": "NFKC; strip; collapse whitespace" + ("; uppercase" if col == TEXT[1] else ""),
        })
        for index in df.index[bad]:
            issues.append({"source_row": int(index + 2), "column": col,
                           "before": before.loc[index], "after": after.loc[index],
                           "decision": "Giữ; cần đối soát, không đoán mã"})
    return cleaned, pd.DataFrame(summaries), pd.DataFrame(
        issues, columns=["source_row", "column", "before", "after", "decision"])


def detect_column(series: pd.Series) -> tuple[dict, pd.Series, pd.Series, pd.Series]:
    """Tính ngưỡng theo điểm quan sát; trả thống kê, hai mặt nạ cờ và Z có dấu.

    IQR đo độ rộng 50% điểm ở giữa. Z đo số độ lệch chuẩn cách trung bình.
    Cờ chỉ phục vụ điều tra, không phải chỉ thị xóa hoặc sửa điểm.
    """
    values = series.dropna()
    if not np.isfinite(values).all():
        raise ValueError("Chỉ nhận điểm hữu hạn hoặc thiếu")
    n = len(values)
    # Mỗi môn có mẫu số riêng; ô thiếu không tham gia tính phân vị/trung bình.
    q1, q3 = values.quantile([.25, .75], interpolation="linear")
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mean, std = values.mean(), values.std(ddof=0)  # σ: chia cho n, không phải n−1.
    z = (series - mean) / std if n and std > 0 else pd.Series(np.nan, index=series.index)
    a = ((series < low) | (series > high)).fillna(False)
    b = z.abs().gt(3).fillna(False)
    stats = {"n_observed": n, "n_missing": int(series.isna().sum()),
             "q1": q1, "q3": q3, "iqr": iqr, "iqr_lower": low, "iqr_upper": high,
             "mean": mean, "std_population": std, "z_lower": mean - 3 * std,
             "z_upper": mean + 3 * std,
             "status": "all_missing" if not n else "constant; z_undefined" if std == 0
             else "zero_iqr; literal_fences" if iqr == 0 else "ok"}
    for name, mask in {"iqr": a, "z": b, "both": a & b, "either": a | b,
                       "iqr_only": a & ~b, "z_only": b & ~a}.items():
        # sum(True/False) đếm cờ; tỷ lệ tính trên số điểm quan sát của môn.
        stats[f"{name}_n"] = int(mask.sum())
        stats[f"{name}_pct"] = 100 * int(mask.sum()) / n if n else np.nan
    return stats, a, b, z


def detect_outliers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries, details = [], []
    for col in SCORES:
        stats, a, b, z = detect_column(df[col])
        summaries.append({"column": col, **stats})
        mask = a | b
        detail = pd.DataFrame({"source_row": df.index[mask] + 2,
                               "Student ID": df.loc[mask, TEXT[0]].to_numpy(),
                               "column": col, "value": df.loc[mask, col].to_numpy(),
                               "z_score": z.loc[mask].to_numpy(), "abs_z": z.loc[mask].abs().to_numpy(),
                               "iqr_flag": a.loc[mask].to_numpy(), "z_flag": b.loc[mask].to_numpy()})
        details.append(detail)
    return pd.DataFrame(summaries), pd.concat(details, ignore_index=True)


def select_top5(details: pd.DataFrame) -> pd.DataFrame:
    # An undefined z-score cannot be ranked as a large standardized deviation.
    return (details.loc[details["abs_z"].notna()]
            .sort_values(["abs_z", "Student ID", "column"], ascending=[False, True, True], kind="stable")
            .drop_duplicates("Student ID").head(5).reset_index(drop=True))


def investigate(top: pd.DataFrame, df: pd.DataFrame, source_hash: str,
                raw_path: Path = RAW, checks_path: Path = CHECKS) -> tuple[pd.DataFrame, pd.DataFrame]:
    checks = json.loads(checks_path.read_text(encoding="utf-8"))
    if checks["source_sha256"] != source_hash:
        raise ValueError("Nguồn đã đổi; phải cập nhật bằng chứng điều tra trước khi chạy lại")
    records = {r["student_id"]: r for r in checks["records"]}
    sources = {r["id"]: r for r in checks["sources"]}
    wanted = set(top["source_row"].astype(int))
    originals = {}
    # Reopen the physical CSV; verify line numbers, raw tokens and the entire row.
    with raw_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for index, row in enumerate(reader):
            if reader.line_num != index + 2 or len(row) != len(header):
                raise ValueError("CSV có dòng trống/nhiều dòng hoặc sai số cột; cần cập nhật truy vết dòng")
            if reader.line_num in wanted:
                originals[reader.line_num] = dict(zip(header, row))
    investigation, raw_records = [], []
    for rank, (_, item) in enumerate(top.iterrows(), start=1):
        line, sid, col = int(item["source_row"]), item[TEXT[0]], item["column"]
        original = originals[line]
        parsed = df.iloc[line - 2]
        for name in COLUMNS:
            token = original[name]
            expected = token if name in TEXT else float(token) if token else np.nan
            if token == "":
                assert pd.isna(parsed[name]), (sid, name)
            else:
                assert parsed[name] == expected, (sid, name)
        assert original[TEXT[0]] == sid
        record = records.get(sid)
        if not record:
            raise ValueError(f"Thiếu nhật ký tìm nguồn cho thí sinh {sid}")
        if record["verdict"] != "unresolved":
            raise ValueError("Cần rà soát bằng chứng và bổ sung quy tắc sửa trước khi đổi kết luận")
        consulted = [sources[key] for key in record["source_ids"]]
        zero_subjects = [name for name in SCORES if pd.notna(parsed[name]) and parsed[name] == 0]
        missing_subjects = [name for name in SCORES if pd.isna(parsed[name])]
        context = (f"Có {len(zero_subjects)} môn bằng 0 ({', '.join(zero_subjects)}); "
                   f"thiếu {len(missing_subjects)} trong 9 cột điểm. "
                   "Các điểm khác và pattern thiếu không xác minh được nguyên nhân điểm 0; "
                   "không suy ra vắng thi, miễn thi hoặc chương trình học.")
        investigation.append({
            "rank": rank, **item.to_dict(), "source_sha256": source_hash,
            "raw_token": original[col], "raw_record_matches": True,
            "processed_week3_matches": True, "within_0_10": 0 <= item["value"] <= 10,
            "verdict": "unresolved", "decision": "Giữ nguyên",
            "reason": "Khớp tệp nguồn và trong miền điểm; chưa có bảng điểm độc lập xác minh.",
            "record_context": context,
            "zero_subjects": " | ".join(zero_subjects), "missing_subjects": " | ".join(missing_subjects),
            "checked_at": checks["checked_at"], "search_query": record["query"],
            "search_result": record["search_result"],
            "source_urls": " | ".join(s["url"] for s in consulted),
            "source_observations": " | ".join(s["result"] for s in consulted),
            "evidence_file": f"docs/week4_evidence.md#sbd-{sid}",
            "before": item["value"], "after": item["value"], "changed_rows": 0,
        })
        raw_records.append({"source_row": line, "source_sha256": source_hash, **original})
    # The claimed Week 3 match is verified across all selected columns, including nulls.
    previous = pd.read_parquet(ROOT / "data/processed/exam_2023.parquet")
    for line in wanted:
        pd.testing.assert_series_equal(df.iloc[line - 2], previous.iloc[line - 2],
                                       check_names=False, check_dtype=False)
    return pd.DataFrame(investigation), pd.DataFrame(raw_records)


def cleaning_log(df: pd.DataFrame, comparison: pd.DataFrame,
                 text_summary: pd.DataFrame, top: pd.DataFrame, source_hash: str) -> pd.DataFrame:
    prior = json.loads((ROOT / "outputs/metrics+chi_so.json").read_text(encoding="utf-8"))
    if prior["provenance"]["source_sha256"] != source_hash:
        raise ValueError("Nhật ký Week 3 thuộc một nguồn khác")
    rows = []

    def add(week, target, issue, evidence, decision, reason, rule, scope, changed=0):
        rows.append({"ID": f"CL{len(rows)+1:03d}", "week": week, "column_or_record": target,
                     "issue": issue, "evidence": evidence, "decision": decision, "reason": reason,
                     "rule": rule, "scope_rows": int(scope), "changed_rows": int(changed),
                     "history_status": "Tổng hợp lại từ bằng chứng Week 3; ngày gốc chưa rõ" if week == 3
                     else "Quyết định Week 4", "original_decision_date": ""})

    old_evidence = "src/analyze.py; docs/report+bao_cao.md; outputs/metrics+chi_so.json"
    add(3, TEXT[0], "ID có số 0 đầu", old_evidence, "Đọc dạng chuỗi", "Bảo toàn định danh",
        "Không đổi sang số; không pad", len(df))
    add(3, "9 cột điểm", "Điểm 0 có thật trong CSV", old_evidence, "Giữ 0",
        "0 không phải ký hiệu thiếu", "Không đổi 0 thành null", df[SCORES].eq(0).any(axis=1).sum())
    for col in COLUMNS:
        n = df[col].isna().sum()
        if n:
            add(3, col, "Dữ liệu thiếu", "outputs/tables/missing_treatment+cach_xu_ly_thieu.csv",
                "Giữ null", "Chưa xác định nguyên nhân từng ô; không có nguồn điểm thay thế",
                "Không điền vào dữ liệu chính", n)
    groups = prior["audit"]["exam_groups"]
    add(3, "6 môn tổ hợp", "Thiếu phụ thuộc nhóm điểm quan sát", old_evidence,
        "Phân lớp ứng viên cấu trúc / chưa rõ", "Không có hồ sơ đăng ký để khẳng định nguyên nhân",
        "Suy nhóm từ điểm quan sát; không thay dữ liệu", groups["science_only"] + groups["social_only"])
    add(3, "Các dòng chỉ có Student ID", "Không có điểm và mã ngoại ngữ", old_evidence,
        "Giữ để đối soát", "Không suy ra vắng thi", "Không xóa dòng",
        df.drop(columns=TEXT[0]).isna().all(axis=1).sum())
    add(3, "Mathematics: thử nghiệm che điểm", "So sánh hai cách điền", old_evidence,
        "Chỉ điền trên bản thử nghiệm", "Không thay điểm trong dữ liệu chính",
        "Seed 3020; cùng mặt nạ và dữ liệu fit", prior["experiment"]["artificially_masked"])
    add(3, "Mathematics: thiếu tự nhiên", "So sánh độ nhạy giả định", old_evidence,
        "Không xuất điểm điền vào dữ liệu chính", "Giả định có điểm thật chưa xác minh",
        "Tách kịch bản giả định", prior["natural_missing_sensitivity"]["missing_n"])
    add(3, "Toàn bộ bản ghi", "Kiểm tra ID trùng, miền điểm và cặp mã/điểm Ngoại ngữ",
        old_evidence, "Không xóa hoặc sửa", "Audit không phát hiện vi phạm các phép kiểm này",
        "Kiểm tra không đồng nghĩa xác minh accuracy", len(df))
    for row in comparison.to_dict("records"):
        add(4, row["column"], "Ngoại lệ thống kê", "outputs/tables/week4_outlier_comparison.csv",
            "Gắn cờ; giữ điểm", "Ngoại lệ không đồng nghĩa lỗi",
            "IQR 1.5; |Z| > 3; ddof=0", row["either_n"])
    for row in top.to_dict("records"):
        add(4, f"{row['Student ID']}: {row['column']}", "Ngoại lệ trong top 5", row["evidence_file"],
            "Giữ; unresolved", row["reason"], "Chưa có điểm độc lập để sửa", 1)
    for row in text_summary.to_dict("records"):
        add(4, row["column"], "Kiểm tra cách biểu diễn chuỗi", "outputs/tables/week4_text_standardization.csv",
            "Chuẩn hóa và kiểm tra định dạng", "Không tạo biến thể giả để làm giảm distinct",
            row["rule"], len(df), row["changed_rows"])
    add(4, "Tên gọi tương đương", "Không quan sát biến thể tên", "outputs/tables/week4_text_standardization.csv",
        "Không thêm ánh xạ", "Hai cột là mã định danh, không phải tên tự do", "Chỉ xử lý biến thể có bằng chứng", 0)
    add(4, "Tệp nguồn và đầu ra", "Truy vết và kiểm tra bảo toàn", "outputs/week4_metrics.json",
        "Giữ bản gốc; xuất bản chuẩn hóa riêng", "Cho phép tái lập và đối chiếu",
        "Hash nguồn; kiểm tra round-trip CSV", len(df))
    return pd.DataFrame(rows)


def plot_boxplots(df: pd.DataFrame, comparison: pd.DataFrame) -> None:
    """Vẽ biểu đồ thống kê bằng Matplotlib; mỗi biểu đồ chỉ xuất một PNG."""
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".venv/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import FuncFormatter

    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    blue, orange, red = '#266797', '#bf651d', '#b13c42'
    stats = comparison.set_index('column')

    def count(value):
        return f'{int(value):,}'.replace(',', '.')

    def decimal(value, digits=3):
        return f'{value:.{digits}f}'.replace('.', ',')

    def style(ax, axis='x'):
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis=axis, color='#dfe4e8', linewidth=.7)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=11)

    def save(fig, name):
        # Chỉ xuất PNG để đọc báo cáo và nhúng notebook.
        for extension in ('png',):
            fig.savefig(FIGURE.parent / f'{name}.{extension}', dpi=180, facecolor='white')
        plt.close(fig)

    # 1. Thanh ngang theo tỷ lệ: so sánh công bằng khi số người có điểm khác nhau.
    fig, ax = plt.subplots(figsize=(13, 8.6))
    positions = np.arange(len(SCORES))
    for method, offset, color, label in [('iqr', -.18, blue, 'IQR: ngoài khoảng [Q1 − 1,5×IQR; Q3 + 1,5×IQR]'),
                                         ('z', .18, orange, 'Z-score: |Z| > 3')]:
        rates = stats.loc[SCORES, f'{method}_pct'].to_numpy()
        ax.barh(positions + offset, rates, height=.31, color=color, label=label)
        for y, rate, n in zip(positions + offset, rates, stats.loc[SCORES, f'{method}_n']):
            ax.text(rate + .025, y, f'{decimal(rate)}% ({count(n)})', va='center', fontsize=10, color=color)
    ax.set_yticks(positions, [VN[c] for c in SCORES])
    ax.invert_yaxis()
    ax.set_xlim(0, max(comparison['iqr_pct'].max(), comparison['z_pct'].max()) * 1.30 + .06)
    ax.set_xlabel('Tỷ lệ điểm bị gắn cờ trong số điểm quan sát của từng môn (%)', fontsize=11, labelpad=12)
    ax.set_ylabel('Môn học', fontsize=11)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: decimal(value, 1)))
    style(ax)
    fig.suptitle('So sánh ngoại lệ giữa IQR và Z-score', fontsize=19, fontweight='bold', y=.97)
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.025), frameon=False, fontsize=10)
    fig.text(.5, .025, 'Nhãn cuối thanh: tỷ lệ % (số ô điểm) · Tỷ lệ = số cờ / số điểm quan sát × 100\n'
             'Hai phương pháp có thể đánh dấu cùng một điểm; không cộng hai thanh để tính tổng.',
             ha='center', fontsize=10, linespacing=1.6)
    fig.subplots_adjust(left=.14, right=.97, top=.83, bottom=.16)
    save(fig, 'week4_outlier_rates')

    # 2. Histogram từ điểm thực, không giả định hoặc ép dữ liệu thành phân phối chuẩn.
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.7), sharey=True)
    bins = np.linspace(0, 10, 21)
    for ax, col in zip(axes, ['Mathematics', 'Civic education']):
        values = df[col].dropna().to_numpy()
        frequency, edges = np.histogram(values, bins=bins)
        percent = 100 * frequency / len(values)
        assert int(frequency.sum()) == len(values)
        ax.bar(edges[:-1], percent, width=np.diff(edges), align='edge',
               color='#a8c9df', edgecolor='white', linewidth=1)
        row = stats.loc[col]
        ax.axvline(row.iqr_lower, color=orange, linestyle='--', linewidth=2,
                   label=f'Ngưỡng dưới IQR = {decimal(row.iqr_lower, 2)}')
        ax.axvline(row.z_lower, color=red, linestyle=':', linewidth=2.5,
                   label=f'Ngưỡng dưới Z = {decimal(row.z_lower, 2)}')
        ax.set_xlim(0, 10)
        ax.set_xticks(range(11))
        ax.set_xlabel('Điểm thi (mỗi khoảng rộng 0,5 điểm)', fontsize=11, labelpad=10)
        ax.set_title(f'{VN[col]} — {count(len(values))} điểm quan sát', fontsize=13, fontweight='bold', pad=15)
        style(ax, 'y')
        ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=10)
    axes[0].set_ylabel('Tỷ lệ điểm trong mỗi khoảng (%)', fontsize=11)
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda value, _: decimal(value, 1)))
    fig.suptitle('Phân bố điểm thực tế và ngưỡng phát hiện ngoại lệ', fontsize=18, fontweight='bold', y=.97)
    fig.text(.5, .028, 'Bên trái mỗi đường ngưỡng: điểm bị phương pháp tương ứng gắn cờ.\n'
             'Ngưỡng trên đều vượt 10 ở hai môn này · Cột cuối gồm điểm 10 · Không điền ô thiếu.',
             ha='center', fontsize=10, linespacing=1.6)
    fig.subplots_adjust(left=.075, right=.98, top=.79, bottom=.21, wspace=.13)
    save(fig, 'week4_score_histograms')

    # 3. Boxplot ngang trên chung một trục; râu kết thúc tại điểm quan sát trong ngưỡng.
    fig, ax = plt.subplots(figsize=(13, 8.7))
    ax.boxplot([df[c].dropna().to_numpy() for c in SCORES], vert=False, whis=1.5,
               positions=np.arange(1, 10), widths=.5, patch_artist=True,
               boxprops={'facecolor': '#bdd7e8', 'edgecolor': blue, 'linewidth': 1.3},
               whiskerprops={'color': '#52606c', 'linewidth': 1.2},
               capprops={'color': '#52606c', 'linewidth': 1.2},
               medianprops={'color': orange, 'linewidth': 2.4},
               flierprops={'marker': 'o', 'markerfacecolor': red, 'markeredgecolor': red,
                           'markersize': 2.5, 'alpha': .4})
    ax.set_yticks(range(1, 10), [VN[c] for c in SCORES])
    ax.invert_yaxis()
    ax.set_xlim(-.15, 10.15)
    ax.set_xticks(range(11))
    ax.set_xlabel('Điểm thi', fontsize=12, labelpad=12)
    ax.set_ylabel('Môn học', fontsize=11)
    style(ax)
    fig.suptitle('Biểu đồ hộp — Vị trí và độ phân tán điểm của 9 môn', fontsize=18, fontweight='bold', y=.97)
    ax.legend(handles=[Patch(facecolor='#bdd7e8', edgecolor=blue, label='Hộp Q1–Q3: 50% điểm ở giữa'),
                       Line2D([0], [0], color=orange, lw=2.4, label='Vạch cam: trung vị Q2'),
                       Line2D([0], [0], color=red, marker='o', linestyle='', markersize=4, label='Chấm đỏ: ngoại lệ IQR')],
              loc='lower center', bbox_to_anchor=(.5, 1.03), ncol=2, frameon=False, fontsize=10)
    fig.text(.5, .023, 'Đầu râu: điểm nhỏ nhất/lớn nhất còn nằm trong ngưỡng IQR; không nhất thiết bằng ngưỡng.\n'
             'Nhiều người trùng điểm sẽ chồng chấm · Ngoại lệ thống kê chưa phải bằng chứng dữ liệu sai.',
             ha='center', fontsize=10, linespacing=1.6)
    fig.subplots_adjust(left=.13, right=.97, top=.79, bottom=.16)
    save(fig, 'week4_boxplot')


def md_table(df: pd.DataFrame) -> str:
    def cell(value):
        if pd.isna(value):
            return "—"
        if isinstance(value, (float, np.floating)):
            return f"{value:.5f}".rstrip("0").rstrip(".")
        return str(value).replace("|", " / ").replace("\n", " ")
    lines = ["| " + " | ".join(df.columns) + " |", "| " + " | ".join(["---"] * len(df.columns)) + " |"]
    lines.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in df.itertuples(index=False, name=None))
    return "\n".join(lines)


def write_evidence(top: pd.DataFrame, raw_records: pd.DataFrame) -> None:
    checks = json.loads(CHECKS.read_text(encoding="utf-8"))
    parts = ["# Week 4 — Bằng chứng điều tra ngoại lệ\n",
             f"Ngày kiểm tra web: **{checks['checked_at']}**. {checks['method']}\n",
             "Đây là ghi chép truy xuất và trích đoạn ngắn, không phải bản sao đầy đủ của website. "
             "Không tìm thấy qua tìm kiếm không có nghĩa là bản ghi không tồn tại.\n",
             "## Nguồn đã kiểm tra\n"]
    for source in checks["sources"]:
        parts.append(f"### {source['id']}\n\n[Nguồn]({source['url']})\n\n{source['result']}\n\n"
                     f"> {source['excerpt']}\n\n{source.get('limitation', '')}\n")
    parts.append("## Đối chiếu từng bản ghi\n\nSố dòng tính từ 1, gồm dòng tiêu đề. "
                 "Token trống trong bảng gốc được giữ là ô trống, không đổi thành 0. "
                 "Đầu mối Hà Nội/TP.HCM dựa trên tiền tố mã để tìm nguồn; không bổ sung địa phương vào dữ liệu.\n")
    for row in top.to_dict("records"):
        sid = row[TEXT[0]]
        raw = raw_records.loc[raw_records[TEXT[0]].eq(sid)].iloc[0]
        original = pd.DataFrame({"Cột": COLUMNS, "Token trong CSV": [raw[c] for c in COLUMNS]})
        parts.append(f"<a id=\"sbd-{sid}\"></a>\n\n### SBD {sid}\n\n"
                     f"Dòng CSV **{row['source_row']}**; {row['column']} = **{row['raw_token']}**; "
                     f"Z = {row['z_score']:.8f}. SHA-256: `{row['source_sha256']}`.\n\n"
                     f"{md_table(original)}\n\n"
                     "Đã đọc lại dòng nguồn, đối chiếu toàn bộ 11 cột với DataFrame và bản Parquet Week 3: khớp.\n\n"
                     f"Ngữ cảnh bản ghi: {row['record_context']}\n\n"
                     f"Truy vấn: `{row['search_query']}`. {row['search_result']}\n\n"
                     f"{row['source_observations']}\n\n"
                     f"Các URL: {row['source_urls']}\n\n"
                     f"**Kết luận: chưa xác định (`unresolved`). Quyết định: giữ nguyên.** {row['reason']}\n")
    (ROOT / "docs/week4_evidence.md").write_text("\n".join(parts), encoding="utf-8")


def write_report(metrics: dict, comparison: pd.DataFrame, top: pd.DataFrame,
                 text_summary: pd.DataFrame, log: pd.DataFrame) -> None:
    counts = comparison[["column", "n_observed", "iqr_n", "z_n", "both_n", "iqr_only_n", "z_only_n"]]
    chosen = top[["Student ID", "source_row", "column", "value", "abs_z", "verdict"]]
    text_counts = text_summary[["column", "distinct_before", "distinct_after", "missing_before", "missing_after", "changed_rows"]]
    counts = counts.assign(column=counts['column'].map(VN)).rename(columns=explain.LABELS)
    chosen = chosen.assign(column=chosen['column'].map(VN)).rename(columns=explain.LABELS)
    text_counts = text_counts.rename(columns=explain.LABELS)
    report = f"""# INFO3020 Week 4 — Data Cleaning

## Dữ liệu và cách tái lập

Phân tích **{metrics['rows']:,} dòng, 11 cột** của điểm thi THPT 2023. CSV gốc được giữ nguyên;
SHA-256: `{metrics['source_sha256']}`. Nguồn được ghi nhận từ
[dataset Kaggle](https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam).
Số đếm thực tế của CSV được dùng làm mẫu số thay cho mô tả 1,5 triệu trong Data Card.
Chưa tải lại tệp Kaggle để đối chiếu hash, nên chuỗi nguồn xa hơn tệp CSV địa phương vẫn có giới hạn.

Chạy `python -m src.analyze_week4`, sau đó `python -m src.build_week4_notebook` bằng Python của `.venv`.
Notebook xây lại pipeline trên toàn bộ dữ liệu, không cần mạng. Ngày kiểm tra web được giữ riêng trong
[nhật ký nguồn](week4_source_checks.json), không đổi thành ngày chạy lại.
Hạn: **23:59 ngày trước buổi Week 5**; chưa có ngày học cụ thể.

## EX4.1 — Hai phương pháp phát hiện ngoại lệ

Mỗi môn sử dụng toàn bộ điểm không thiếu. IQR = Q3 − Q1; Q1/Q3 nội suy tuyến tính.
Ngoại lệ khi x < Q1 − 1,5×IQR hoặc x > Q3 + 1,5×IQR, dùng bất đẳng thức nghiêm ngặt.
Z = (x − μ)/σ với `ddof=0`; ngưỡng |Z| > 3. ID và mã ngoại ngữ không phải biến số đo.
Cột toàn thiếu không gắn cờ; σ = 0 làm Z không xác định; IQR = 0 vẫn dùng đúng hai hàng rào suy biến.

{explain.METHOD}

{explain.worked_example(comparison)}

{explain.COMPARISON}

{md_table(counts)}

Có **{metrics['flagged_cells']:,} ô điểm** và **{metrics['flagged_students']:,} thí sinh khác nhau**
bị ít nhất một phương pháp gắn cờ. Trong lần chạy này, mọi cờ Z-score đều nằm trong tập IQR;
đó là kết quả quan sát, không phải tính chất đúng cho mọi dữ liệu. Các ngưỡng, hợp/giao, tỷ lệ theo
số điểm quan sát được lưu trong [bảng so sánh](../outputs/tables/week4_outlier_comparison.csv).
[Bảng chi tiết](../outputs/tables/week4_outlier_details.csv) cho phép truy vết từng ô về dòng CSV.

### Biểu đồ 1 — So sánh tỷ lệ ngoại lệ

![Biểu đồ thanh so sánh tỷ lệ ngoại lệ](../outputs/figures/week4_outlier_rates.png)

{explain.BAR}

[Mở biểu đồ dạng PNG để phóng to](../outputs/figures/week4_outlier_rates.png).

### Biểu đồ 2 — Phân bố điểm Toán và GDCD

![Histogram điểm thực tế](../outputs/figures/week4_score_histograms.png)

{explain.HISTOGRAM}

[Mở histogram dạng PNG để phóng to](../outputs/figures/week4_score_histograms.png).

### Biểu đồ 3 — Boxplot ngang của 9 môn

![Boxplot ngang có chú giải](../outputs/figures/week4_boxplot.png)

{explain.BOXPLOT}

[Mở boxplot dạng PNG để phóng to](../outputs/figures/week4_boxplot.png).

## EX4.2 — Điều tra 5 ngoại lệ lớn nhất

Xếp các ô thuộc hợp cờ theo |Z| giảm dần, ID tăng dần rồi tên môn tăng dần; giữ ô đầu mỗi ID,
lấy 5 ID. “Lớn nhất” là độ lệch chuẩn hóa, không phải điểm cao nhất.

{explain.INVESTIGATION}

{md_table(chosen)}

Cả năm có GDCD = 0 và đồng hạng. Quy tắc phá hòa quyết định lựa chọn, không thay đổi để lấy nhiều môn.
Đã mở lại từng dòng CSV và đối chiếu toàn bộ 11 cột với Parquet Week 3.
Điểm trong [0,10] và khớp CSV chỉ xác nhận tính hợp lệ và tính nhất quán với bản nguồn địa phương.
**Cả năm kết luận `unresolved`, giữ nguyên** vì chưa có bảng điểm độc lập năm 2023 cho từng người.

[Bằng chứng từng bản ghi](week4_evidence.md) ghi token gốc, dòng nguồn, hash, ngày kiểm tra, URL,
truy vấn và giới hạn. [Danh sách tra cứu năm 2023 của Báo Chính phủ](https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm)
cung cấp đầu mối Hà Nội và TP.HCM. Trang Hà Nội hiện mang tiêu đề năm 2026; công cụ web gặp lỗi
khi mở địa chỉ TP.HCM năm 2023. Không dùng các trang đó để khẳng định điểm cá nhân.

## EX4.3 — Chuẩn hóa hai cột văn bản

Hai cột chuỗi thực có trong dataset là Student ID và Foreign language code.
Áp dụng Unicode NFKC, bỏ khoảng trắng đầu/cuối, gộp khoảng trắng liên tiếp; mã ngoại ngữ chuyển hoa.
ID giữ dạng chuỗi, không thêm số 0 và không xóa khoảng trắng nội bộ để đoán mã.
Kiểm tra ID bằng `[0-9]{{8}}`, mã bằng N1–N7. Mã này dựa trên Data Card, không phải xác minh điểm thi.
Distinct dùng `nunique(dropna=True)`; ô thiếu được đếm riêng. Không có biến thể tên cần ánh xạ.

{explain.TEXT}

{md_table(text_counts)}

**Không có dòng nào thay đổi** và không có giá trị không thiếu sai định dạng sau chuẩn hóa.
Kết quả không đổi là kết quả thực tế; không thêm lỗi giả hoặc cột dẫn xuất để làm bài trông có thay đổi.
Các ID/mã là dữ liệu văn bản có cấu trúc, không phải tên tự do.

## EX4.4 — Cleaning Log và kiểm tra sau xử lý

{explain.LOG}

[Cleaning Log](../outputs/tables/week4_cleaning_log.csv) gồm **{len(log)} quyết định** với ID, cột/bản ghi,
vấn đề, bằng chứng, quyết định, lý do, tuần, quy tắc, `scope_rows` và `changed_rows`.
`scope_rows` là số dòng được xét bởi quyết định; `changed_rows` là số dòng thực sự đổi trong dữ liệu chính.
Các dòng nhật ký có thể chồng lấp nên không cộng phạm vi để suy ra số người duy nhất.
Quyết định Week 3 được tổng hợp từ báo cáo/code/metrics, không gán ngày lịch sử chưa biết.
Thử nghiệm điền khuyết Week 3 chỉ thay dữ liệu thí nghiệm; số dòng đổi trong dữ liệu chính vẫn bằng 0.

CSV sau xử lý giữ **{metrics['rows']:,} dòng, 11 cột**, thứ tự dòng, mọi điểm và trạng thái thiếu.
Round-trip CSV được đọc với ID/mã dạng chuỗi; ID đầu vẫn là `01000001`.
Đã đối chiếu số cờ chi tiết/tổng hợp, 5 ID duy nhất, chuẩn hóa lặp lại, hash nguồn và kết quả xuất.
Thông tin phiên bản, thời gian chạy và các phép kiểm nằm trong [metrics](../outputs/week4_metrics.json).

Các kết quả còn chưa xác minh cần bảng điểm chính thức năm 2023 hoặc hồ sơ tương ứng.
`unresolved` không đồng nghĩa với lỗi. Điểm thiếu và ngoại lệ được giữ nguyên để tránh tạo dữ liệu không có căn cứ.
"""
    REPORT.write_text(report, encoding="utf-8")


def run() -> dict:
    source_hash = sha256(RAW)
    df = load_raw()
    if df[TEXT[0]].isna().any() or df[TEXT[0]].duplicated().any():
        raise ValueError("Cần ID duy nhất và không thiếu để điều tra 5 thí sinh")
    cleaned, text_summary, issues = standardize(df)
    if cleaned[TEXT[0]].duplicated().any():
        raise ValueError("Chuẩn hóa tạo ID trùng; cần đối soát")
    comparison, details = detect_outliers(df)
    top, raw_records = investigate(select_top5(details), df, source_hash)
    log = cleaning_log(df, comparison, text_summary, top, source_hash)
    for row in comparison.to_dict("records"):
        subset = details.loc[details["column"].eq(row["column"])]
        assert len(subset) == row["either_n"]
        assert int(subset["iqr_flag"].sum()) == row["iqr_n"]
        assert int(subset["z_flag"].sum()) == row["z_n"]
        assert int((subset["iqr_flag"] & subset["z_flag"]).sum()) == row["both_n"]
    assert len(top) == 5 and top[TEXT[0]].nunique() == 5
    pd.testing.assert_frame_equal(df[SCORES], cleaned[SCORES])
    pd.testing.assert_frame_equal(df.isna(), cleaned.isna())
    twice, _, _ = standardize(cleaned)
    pd.testing.assert_frame_equal(cleaned, twice)
    del twice
    TABLES.mkdir(parents=True, exist_ok=True)
    CLEANED.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEANED, index=False, encoding="utf-8-sig")
    roundtrip = load_raw(CLEANED)
    pd.testing.assert_frame_equal(cleaned, roundtrip, check_exact=True)
    assert sha256(RAW) == source_hash
    for name, table in {
        "outlier_comparison": comparison, "outlier_details": details,
        "top5_investigation": top, "top5_raw_records": raw_records,
        "text_standardization": text_summary, "text_validation_issues": issues,
        "cleaning_log": log,
    }.items():
        table.to_csv(TABLES / f"week4_{name}.csv", index=False, encoding="utf-8-sig")
    plot_boxplots(df, comparison)
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "source": "data/raw/original.csv",
        "source_sha256": source_hash, "cleaned_sha256": sha256(CLEANED), "rows": len(df),
        "columns": list(df.columns), "python": platform.python_version(),
        "pandas": pd.__version__, "numpy": np.__version__,
        "parameters": {"iqr_multiplier": 1.5, "quantile_interpolation": "linear", "z_threshold": 3,
                       "ddof": 0, "ranking": "abs_z desc, Student ID asc, column asc; distinct Student ID"},
        "flagged_cells": len(details), "flagged_students": int(details[TEXT[0]].nunique()),
        "iqr_students": int(details.loc[details["iqr_flag"], TEXT[0]].nunique()),
        "z_students": int(details.loc[details["z_flag"], TEXT[0]].nunique()),
        "top5_ids": top[TEXT[0]].tolist(), "verdicts": top["verdict"].value_counts().to_dict(),
        "source_checks_sha256": sha256(CHECKS),
        "source_checked_at": json.loads(CHECKS.read_text(encoding="utf-8"))["checked_at"],
        "text_changed_rows": dict(zip(text_summary["column"], text_summary["changed_rows"])),
        "cleaning_log_entries": len(log),
        "validation": {"source_unchanged": True, "same_scores": True, "same_missingness": True,
                       "csv_roundtrip_exact": True, "same_schema_and_order": True,
                       "text_idempotent": True, "detail_counts_reconciled": True,
                       "top5_unique": True, "top5_raw_and_week3_match": True},
    }
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    write_evidence(top, raw_records)
    write_report(metrics, comparison, top, text_summary, log)
    return metrics


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
