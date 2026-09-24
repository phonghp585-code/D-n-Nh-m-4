"""Reproducible Week 5 cleaning and source-integration pipeline.

The raw exam-score CSV is read-only. No imputation, scaling, score edits or
sampling are applied. The external table is the versioned 2023 exam-council
list: 63 government-table entries plus council 65 from Appendix VIII.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.analyze_week4 import (COLUMNS, SCORES, TEXT, detect_outliers, invalid_text,
                               load_raw, normalize_text, sha256, standardize)

ROOT = Path(__file__).resolve().parents[1]
RAW = Path("data/raw/original.csv")
REFERENCE = Path("data/raw/exam_councils_2023.csv")
REGISTRY = Path("docs/week5_source_registry+ho_so_nguon.json")
PRIOR_LOG = Path("docs/week5_prior_decisions+quyet_dinh_tuan_truoc.csv")
GOV_EXCERPT = Path("docs/week5_gov_table_excerpt+trich_bang_nguon.csv")
SOURCE_MAPPING = Path("docs/week5_source_mapping+anh_xa_nguon.md")
FINAL_COLUMNS = [*COLUMNS, "exam_year", "exam_council_code", "exam_council_name",
                 "observed_exam_group", "merge_status"]
SCORE_DOMAIN = (0.0, 10.0)
REF_COLUMNS = ["exam_year", "exam_council_code", "exam_council_name"]


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def make_directories(output_root: Path) -> None:
    for relative in ("data/processed", "outputs/tables", "outputs/figures", "docs",
                     "notebooks"):
        (output_root / relative).mkdir(parents=True, exist_ok=True)


def output_paths(output_root: Path) -> dict[str, Path]:
    return {
        "final": output_root / "data/processed/week5_final+du_lieu_cuoi.csv",
        "tables": output_root / "outputs/tables",
        "figures": output_root / "outputs/figures",
        "metrics": output_root / "outputs/week5_manifest+ho_so_dau_ra.json",
        "report": output_root / "docs/week5_report+bao_cao.md",
        "notebook": output_root / "notebooks/week5_exercises+bai_tap_tuan5.ipynb",
    }


def logged_merge(left: pd.DataFrame, right: pd.DataFrame, *, label: str,
                 operations: list[dict] | None = None, **kwargs) -> pd.DataFrame:
    """Print actual row counts at every merge and retain them for the report."""
    before = len(left)
    print(f"[{label}] len(df) before merge = {before:,}; right rows = {len(right):,}")
    result = left.merge(right, **kwargs)
    print(f"[{label}] len(df) after merge = {len(result):,}")
    if operations is not None:
        operations.append({"merge": label, "rows_before": before,
                           "right_rows": len(right), "rows_after": len(result),
                           "how": kwargs.get("how", "inner"),
                           "validate": kwargs.get("validate", "")})
    return result


def normalize_source_reference(root: Path, operations: list[dict] | None = None) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Read and validate the second, independently sourced data table."""
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    ref_path = root / REFERENCE
    actual_hash = file_sha256(ref_path)
    expected_hash = registry["exam_council_reference"]["sha256"]
    if actual_hash != expected_hash:
        raise ValueError("Hash danh mục Hội đồng thi khác hồ sơ nguồn; cần đối chiếu và cập nhật registry.")
    ref = pd.read_csv(ref_path, dtype={"exam_council_code": "string"},
                      keep_default_na=False)
    if list(ref.columns) != REF_COLUMNS:
        raise ValueError(f"Schema bảng Hội đồng thi không đúng: {list(ref.columns)!r}")
    ref["exam_year"] = pd.to_numeric(ref["exam_year"], errors="raise").astype("int16")
    if not ref["exam_year"].eq(2023).all():
        raise ValueError("Danh mục đang ghép phải chỉ chứa kỳ thi năm 2023.")
    if ref["exam_council_code"].isna().any() or not ref["exam_council_code"].str.fullmatch(r"[0-9]{2}").all():
        raise ValueError("Mã Hội đồng thi phải đủ hai chữ số và không được thiếu.")
    if ref["exam_council_name"].isna().any() or ref["exam_council_name"].str.strip().eq("").any():
        raise ValueError("Tên Hội đồng thi bị thiếu.")
    duplicate_keys = ref.duplicated(["exam_year", "exam_council_code"], keep=False)
    if duplicate_keys.any():
        write_csv(ref.loc[duplicate_keys].sort_values(REF_COLUMNS[:2]),
                  root / "outputs/tables/week5_reference_duplicate_keys+khoa_nguon_trung.csv")
        raise ValueError("Danh mục có khóa (exam_year, exam_council_code) trùng; dừng trước khi merge.")
    excerpt_path = root / GOV_EXCERPT
    if file_sha256(excerpt_path) != registry["government_table_excerpt"]["sha256"]:
        raise ValueError("Hash bảng trích Báo Chính phủ khác hồ sơ nguồn.")
    excerpt = pd.read_csv(excerpt_path, dtype={"source_code": "string"}, keep_default_na=False)
    if list(excerpt.columns) != ["source_code", "source_name"] or len(excerpt) != 63:
        raise ValueError("Bảng trích Báo Chính phủ phải có đúng 63 dòng và hai cột nguồn.")
    if excerpt.isna().any().any() or excerpt.eq("").any().any():
        raise ValueError("Bảng trích Báo Chính phủ chứa ô trống.")
    if not excerpt["source_code"].str.fullmatch(r"[0-9]{1,2}").all():
        raise ValueError("Mã trong bảng trích Báo Chính phủ sai định dạng.")
    excerpt["exam_council_code"] = excerpt["source_code"].str.zfill(2)
    if excerpt["exam_council_code"].duplicated().any():
        raise ValueError("Mã trong bảng trích Báo Chính phủ bị trùng.")
    audit = logged_merge(ref, excerpt, label="reference_source_check", operations=operations,
                      on="exam_council_code", how="left", validate="one_to_one",
                      indicator=True)
    supplementary = registry["supplemental_code_65"]
    is_65 = audit["exam_council_code"].eq("65")
    if (set(ref["exam_council_code"]) != set(excerpt["exam_council_code"]) | {"65"}
            or audit.loc[~is_65, "_merge"].ne("both").any()
            or audit.loc[~is_65, "exam_council_name"].ne(audit.loc[~is_65, "source_name"]).any()
            or len(audit.loc[is_65]) != 1
            or audit.loc[is_65, "exam_council_name"].iloc[0] != supplementary["exam_council_name"]):
        raise ValueError("Danh mục ghép không khớp 63 dòng Báo Chính phủ + mã 65 Phụ lục VIII.")
    audit["provenance"] = np.where(is_65, "Phụ lục VIII, Công văn 1515/BGDĐT-QLCL",
                                    "Bảng Báo Chính phủ ngày 17/07/2023")
    audit["source_check"] = np.where(is_65, "supplemental_pdf_registry",
                                     "government_name_matched")
    return ref, registry, audit.drop(columns="_merge")


def diagnose_raw_csv(path: Path) -> pd.DataFrame:
    """Locate first parse issue using physical source lines after pandas fails."""
    issues = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration:
            return pd.DataFrame([{"source_row": 1, "column": "header", "raw_token": "",
                                  "issue": "CSV rỗng"}])
        if header != COLUMNS:
            issues.append({"source_row": 1, "column": "header", "raw_token": repr(header),
                           "issue": "Schema 11 cột không đúng"})
        for record in reader:
            line = reader.line_num
            if len(record) != len(COLUMNS):
                issues.append({"source_row": line, "column": "record", "raw_token": repr(record),
                               "issue": f"Số trường {len(record)} khác {len(COLUMNS)}"})
                break
            for column in SCORES:
                token = record[COLUMNS.index(column)]
                if token == "":
                    continue
                try:
                    number = float(token)
                    valid = math.isfinite(number)
                except ValueError:
                    valid = False
                if not valid:
                    issues.append({"source_row": line, "column": column,
                                   "raw_token": token, "issue": "Điểm không phải số hữu hạn"})
                    break
            if issues:
                break
    return pd.DataFrame(issues, columns=["source_row", "column", "raw_token", "issue"])


def observed_exam_group(df: pd.DataFrame) -> pd.Series:
    """Infer only from visible score columns; this is not registration metadata."""
    science = df[["Physics", "Chemistry", "Biology"]].notna().any(axis=1)
    social = df[["History", "Geography", "Civic education"]].notna().any(axis=1)
    labels = np.select(
        [science & ~social, social & ~science, science & social],
        ["science_only", "social_only", "both_observed"], default="neither_observed",
    )
    return pd.Series(labels, index=df.index, dtype="string", name="observed_exam_group")


def missing_by_observed_group(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Count possible structural blanks without asserting why each score is absent."""
    groups = observed_exam_group(df)
    science = {"Physics", "Chemistry", "Biology"}
    social = {"History", "Geography", "Civic education"}
    rows = []
    for group in ("science_only", "social_only", "both_observed", "neither_observed"):
        subset = df.loc[groups.eq(group)]
        for column in SCORES:
            missing = int(subset[column].isna().sum())
            candidate = missing if ((group == "science_only" and column in social)
                                    or (group == "social_only" and column in science)) else 0
            rows.append({"observed_exam_group": group, "column": column,
                         "group_rows": len(subset), "missing_cells": missing,
                         "structural_candidate_cells": candidate,
                         "unresolved_cells": missing - candidate,
                         "missing_pct_within_group": 100 * missing / len(subset) if len(subset) else 0.0})
    detail = pd.DataFrame(rows)
    summary = detail.groupby("observed_exam_group", sort=False, as_index=False).agg(
        group_rows=("group_rows", "first"), missing_score_cells=("missing_cells", "sum"),
        structural_candidate_cells=("structural_candidate_cells", "sum"),
        unresolved_cells=("unresolved_cells", "sum"))
    if int(summary["missing_score_cells"].sum()) != int(df[SCORES].isna().sum().sum()):
        raise AssertionError("Nhóm điểm quan sát không khớp tổng ô thiếu.")
    return detail, summary


def exact_duplicate_rows(df: pd.DataFrame, source_rows: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    """Mark repeated complete source records; keep the first physical occurrence."""
    repeated = df.duplicated(subset=COLUMNS, keep="first")
    removed = pd.DataFrame({
        "source_row": source_rows.loc[repeated].astype("int64"),
        "Student ID": df.loc[repeated, "Student ID"].astype("string"),
        "decision": "Loại bản sao hoàn toàn; giữ lần xuất hiện đầu",
    })
    return repeated, removed


def left_merge_council(main: pd.DataFrame, reference: pd.DataFrame,
                       operations: list[dict] | None = None) -> pd.DataFrame:
    """Perform a row-preserving, one-to-many-safe left join with an indicator."""
    keys = ["exam_year", "exam_council_code"]
    if reference[keys].isna().any().any():
        raise ValueError("Khóa của danh mục bị thiếu.")
    if reference.duplicated(keys).any():
        raise ValueError("Khóa danh mục phải duy nhất trước khi ghép.")
    if not main["exam_council_code"].astype("string").str.fullmatch(r"[0-9]{2}").all():
        raise ValueError("Khóa mã Hội đồng thi ở bảng chính phải gồm hai chữ số.")
    before = len(main)
    merged = logged_merge(main, reference, label="exam_council_integration", operations=operations,
                        on=keys, how="left", validate="many_to_one",
                        indicator="_merge_indicator", sort=False)
    if len(merged) != before:
        raise AssertionError("Left merge altered the number of main rows.")
    return merged


def score_domain_issues(df: pd.DataFrame, source_rows: pd.Series) -> pd.DataFrame:
    rows = []
    for column in SCORES:
        values = df[column]
        mask = values.notna() & ~values.between(*SCORE_DOMAIN)
        if mask.any():
            rows.append(pd.DataFrame({
                "source_row": source_rows.loc[mask].to_numpy(),
                "Student ID": df.loc[mask, "Student ID"].to_numpy(),
                "column": column, "value": values.loc[mask].to_numpy(),
                "rule": "Điểm quan sát phải nằm trong [0, 10]",
            }))
    return (pd.concat(rows, ignore_index=True) if rows else
            pd.DataFrame(columns=["source_row", "Student ID", "column", "value", "rule"]))


def id_conflicts(df: pd.DataFrame, source_rows: pd.Series) -> pd.DataFrame:
    duplicated = df["Student ID"].duplicated(keep=False)
    return pd.DataFrame({
        "source_row": source_rows.loc[duplicated].to_numpy(),
        "Student ID": df.loc[duplicated, "Student ID"].to_numpy(),
        **{col: df.loc[duplicated, col].to_numpy() for col in COLUMNS if col != "Student ID"},
    }).sort_values(["Student ID", "source_row"], kind="stable") if duplicated.any() else pd.DataFrame(
        columns=["source_row", "Student ID", *[c for c in COLUMNS if c != "Student ID"]])


def make_cleaning_log(root: Path, data: pd.DataFrame, comparison: pd.DataFrame,
                      text_summary: pd.DataFrame, n_original: int, n_duplicates: int,
                      n_matched: int, n_unmatched: int) -> pd.DataFrame:
    prior_path = root / PRIOR_LOG
    prior = pd.read_csv(prior_path, keep_default_na=False, dtype={"ID": "string"})
    expected = ["ID", "week", "column_or_record", "issue", "evidence", "decision",
                "reason", "rule", "scope_rows", "changed_rows", "history_status",
                "original_decision_date"]
    if list(prior.columns) != expected or len(prior) != 35:
        raise ValueError("Bản chụp nhật ký Week 3–4 không đủ 35 quyết định hoặc khác schema.")
    source_hash = sha256(root / RAW)
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    if registry["historical_cleaning_decisions"]["source_sha256"] != source_hash:
        raise ValueError("Nhật ký lịch sử được lập trên hash nguồn khác; cần đối chiếu thủ công.")
    rows = prior.to_dict("records")

    def add(target: str, issue: str, evidence: str, decision: str, reason: str,
            rule: str, scope: int, changed: int = 0) -> None:
        rows.append({
            "ID": f"CL{len(rows) + 1:03d}", "week": 5,
            "column_or_record": target, "issue": issue, "evidence": evidence,
            "decision": decision, "reason": reason, "rule": rule,
            "scope_rows": int(scope), "changed_rows": int(changed),
            "history_status": "Quyết định Week 5; tạo từ pipeline tái lập được",
            "original_decision_date": "",
        })

    table_evidence = "outputs/tables/week5_*; outputs/week5_manifest+ho_so_dau_ra.json; docs/week5_report+bao_cao.md"
    missing_cells = int(data[SCORES].isna().sum().sum())
    outlier_cells = int(comparison["either_n"].sum())
    add("Toàn bộ bản ghi", "Bản ghi trùng hoàn toàn", table_evidence,
        "Loại bản sao; giữ lần xuất hiện đầu" if n_duplicates else "Không loại; không có dòng trùng hoàn toàn",
        "Tránh đếm lặp một bản ghi y hệt; hiện trạng được xác nhận bằng quét toàn bộ 11 cột.",
        "So sánh toàn bộ cột nguồn sau parse; giữ bản ghi đầu theo thứ tự nguồn",
        n_original, n_duplicates)
    add("9 cột điểm", "Giá trị điểm thiếu", table_evidence, "Giữ null",
        "CSV không cung cấp điểm thay thế; ô thiếu có thể liên quan lựa chọn môn nhưng không xác nhận từng trường hợp.",
        "Bỏ qua null khi thống kê; không điền median hay số 0", missing_cells)
    add("9 cột điểm", "Ngoại lệ thống kê", "outputs/tables/week5_outlier_comparison+so_sanh_ngoai_le.csv; outputs/tables/week5_outlier_details+chi_tiet_ngoai_le.csv",
        "Gắn cờ để điều tra; giữ điểm",
        "Cờ IQR/Z-score không chứng minh nhập sai; các quyết định sửa điểm cần đối chứng độc lập.",
        "IQR 1,5×IQR; |Z|>3; phân vị tuyến tính; ddof=0", outlier_cells)
    for col in TEXT:
        summary = text_summary.set_index("column").loc[col]
        add(col, "Chuẩn hóa chuỗi", table_evidence, "Chuẩn hóa; không sửa nếu đã đạt quy tắc",
            "Giữ ID dạng chuỗi và không suy đoán giá trị; mã ngoại ngữ dùng chữ hoa.",
            "NFKC; strip; gộp whitespace" + ("; uppercase" if col == TEXT[1] else ""),
            len(data), int(summary["changed_rows"]))
    add("Student ID → mã Hội đồng thi", "Ghép nguồn địa phương năm 2023", table_evidence,
        "Left join; giữ dòng không khớp và để tên thiếu",
        f"Không fuzzy-match; 63 tên từ Báo Chính phủ năm 2023 và mã 65 từ Phụ lục VIII. Kết quả: {n_matched:,} dòng khớp, {n_unmatched:,} dòng không khớp.",
        "exam_year=2023 và hai ký tự đầu ID; many_to_one; indicator=True",
        len(data), 0)
    add("observed_exam_group", "Gắn nhóm theo điểm tổ hợp quan sát", table_evidence,
        "Thêm biến ngữ cảnh; không sửa bản ghi nguồn",
        "Nhóm chỉ phản ánh điểm nào đang quan sát được; không khẳng định hồ sơ đăng ký thi.",
        "science_only / social_only / both_observed / neither_observed",
        len(data), 0)
    add("Điểm và ô thiếu", "Không biến đổi điểm, không điền thiếu", table_evidence,
        "Bảo toàn dữ liệu gốc sau chuẩn hóa mã; xuất riêng cột nguồn",
        "Giữ đơn vị 0–10 để EDA; tránh tạo giá trị không có căn cứ hoặc leakage.",
        "Kiểm tra round-trip: mọi điểm và mặt nạ thiếu phải trùng trước/sau",
        len(data), 0)
    return pd.DataFrame(rows, columns=expected)


def make_data_dictionary() -> pd.DataFrame:
    meanings = {
        "Student ID": ("Mã thí sinh dạng chuỗi 8 chữ số; hai chữ số đầu là mã Hội đồng thi năm 2023.", "Nguồn chính"),
        "Mathematics": ("Điểm môn Toán, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Literature": ("Điểm môn Ngữ văn, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Foreign language": ("Điểm môn Ngoại ngữ, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Physics": ("Điểm môn Vật lý, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Chemistry": ("Điểm môn Hóa học, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Biology": ("Điểm môn Sinh học, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "History": ("Điểm môn Lịch sử, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Geography": ("Điểm môn Địa lý, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Civic education": ("Điểm môn Giáo dục công dân, thang 0–10; null được giữ nguyên.", "Nguồn chính"),
        "Foreign language code": ("Mã ngôn ngữ N1–N7; giữ chuỗi, viết hoa sau chuẩn hóa.", "Nguồn chính"),
        "exam_year": ("Năm kỳ thi dùng khi ghép danh mục; mọi dòng trong bộ này là 2023.", "Thông tin kỳ thi"),
        "exam_council_code": ("Mã Hội đồng thi hai ký tự tra từ hai số đầu của Student ID.", "Tính từ Student ID; xác minh bằng danh mục nguồn"),
        "exam_council_name": ("Tên Hội đồng thi năm 2023: 63 mã theo bảng Báo Chính phủ, mã 65 theo Phụ lục VIII; không nhất thiết là nơi cư trú/trường học.", "Danh mục Hội đồng thi"),
        "observed_exam_group": ("Nhóm suy từ điểm quan sát ở ba môn KHTN/KHXH; không khẳng định môn đã đăng ký.", "Tính từ điểm nguồn"),
        "merge_status": ("matched: mã có trong danh mục; left_only: không ghép được và tên để thiếu.", "Kết quả merge"),
    }
    return pd.DataFrame([{"column": c, "meaning": meanings[c][0], "origin": meanings[c][1]}
                         for c in FINAL_COLUMNS])


def draw_merge_chart(matched: int, unmatched: int, destination: Path) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "khdl-week5-matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    total = matched + unmatched
    pct = 100 * matched / total if total else 0.0
    unmatched_pct = 100.0 - pct
    fig, ax = plt.subplots(figsize=(9.0, 2.8), constrained_layout=True)
    ax.barh(["Bản ghi CSV chính"], [pct], height=.28, color="#2878B5", label="Khớp danh mục")
    if unmatched:
        ax.barh(["Bản ghi CSV chính"], [unmatched_pct], left=[pct], height=.28,
                color="#E07A5F", label="Không khớp")
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100], ["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.set_xlabel("Tỷ lệ bản ghi")
    ax.set_title("Tỷ lệ bản ghi khớp danh mục Hội đồng thi năm 2023")
    ax.grid(axis="x", alpha=.2)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", ncol=2, frameon=False)
    matched_label = (f"Khớp\n{matched:,}".replace(",", ".")
                     + f" ({pct:.4f}%)".replace(".", ","))
    unmatched_label = (f"Không khớp\n{unmatched:,}".replace(",", ".")
                       + f" ({unmatched_pct:.4f}%)".replace(".", ","))
    if pct >= 16:
        ax.text(pct / 2, 0, matched_label, va="center", ha="center",
                color="white", fontsize=10, fontweight="bold")
    else:
        ax.text(pct + 1, 0, matched_label.replace("\n", " "), va="center", ha="left",
                color="#174A6E", fontsize=9, fontweight="bold")
    if unmatched and unmatched_pct >= 16:
        ax.text(pct + unmatched_pct / 2, 0, unmatched_label,
                va="center", ha="center", color="white", fontsize=9, fontweight="bold")
    elif unmatched:
        ax.text(99, 0, unmatched_label.replace("\n", " "), va="center",
                ha="right", color="#8A3825", fontsize=9, fontweight="bold")
    ax.set_ylim(-.55, .55)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=180, facecolor="white", metadata={"Software": "matplotlib"})
    plt.close(fig)


def run_week5(root: Path = ROOT, output_root: Path | None = None) -> dict:
    """Run the full local pipeline and write reproducible Week 5 deliverables."""
    started = time.perf_counter()
    root = Path(root).resolve()
    output_root = Path(output_root or root).resolve()
    make_directories(output_root)
    if output_root != root:
        for source_doc in (REGISTRY, PRIOR_LOG, GOV_EXCERPT, SOURCE_MAPPING):
            shutil.copyfile(root / source_doc, output_root / source_doc)
    paths = output_paths(output_root)
    tables = paths["tables"]

    source_path = root / RAW
    source_hash_before = file_sha256(source_path)
    merge_operations = []
    ref, source_registry, reference_audit = normalize_source_reference(root, merge_operations)
    write_csv(reference_audit, tables / "week5_reference_source_check+doi_chieu_nguon_bo_sung.csv")
    if source_hash_before != source_registry["main_dataset"]["sha256"]:
        raise ValueError("Hash CSV gốc khác hồ sơ nguồn; dừng, không dùng bằng chứng cũ.")

    try:
        raw = load_raw(source_path)
    except (ValueError, pd.errors.ParserError) as error:
        issues = diagnose_raw_csv(source_path)
        write_csv(issues, tables / "week5_source_parse_issues+loi_doc_du_lieu.csv")
        first = issues.iloc[0].to_dict() if not issues.empty else {}
        raise ValueError(f"Không đọc được CSV gốc; xem week5_source_parse_issues+loi_doc_du_lieu.csv. Vị trí đầu: {first}") from error
    if list(raw.columns) != COLUMNS:
        issues = diagnose_raw_csv(source_path)
        write_csv(issues, tables / "week5_source_parse_issues+loi_doc_du_lieu.csv")
        raise ValueError("Schema CSV gốc khác 11 cột dự án tại dòng tiêu đề 1; xem week5_source_parse_issues+loi_doc_du_lieu.csv.")
    raw_rows = len(raw)
    source_rows = pd.Series(raw.index.to_numpy(dtype="int64") + 2, index=raw.index,
                            name="source_row")

    # Keep a pre-normalization copy for exact-record duplicate detection.
    text_clean, text_summary, text_issues = standardize(raw)
    write_csv(text_summary, tables / "week5_text_standardization+chuan_hoa_chuoi.csv")
    write_csv(text_issues, tables / "week5_text_validation_issues+loi_dinh_dang_chuoi.csv")
    invalid_ids = invalid_text(text_clean["Student ID"], "Student ID")
    if invalid_ids.any():
        write_csv(pd.DataFrame({"source_row": source_rows.loc[invalid_ids].to_numpy(),
                                "Student ID": raw.loc[invalid_ids, "Student ID"].to_numpy(),
                                "normalized": text_clean.loc[invalid_ids, "Student ID"].to_numpy()}),
                  tables / "week5_invalid_student_ids+ma_thi_sinh_khong_hop_le.csv")
        raise ValueError(f"Có {int(invalid_ids.sum()):,} Student ID không khớp [0-9]{{8}} sau chuẩn hóa.")
    invalid_codes = invalid_text(text_clean["Foreign language code"], "Foreign language code")
    if invalid_codes.any():
        raise ValueError(f"Có {int(invalid_codes.sum()):,} mã Ngoại ngữ sai; xem week5_text_validation_issues+loi_dinh_dang_chuoi.csv.")

    duplicates, duplicate_table = exact_duplicate_rows(raw, source_rows)
    write_csv(duplicate_table, tables / "week5_duplicate_rows_removed+dong_trung_da_loai.csv")
    clean = text_clean.loc[~duplicates].copy()
    clean_source_rows = source_rows.loc[~duplicates]
    conflict_table = id_conflicts(clean, clean_source_rows)
    write_csv(conflict_table, tables / "week5_conflicting_ids+ma_thi_sinh_xung_dot.csv")
    if not conflict_table.empty:
        raise ValueError(f"Có {conflict_table['Student ID'].nunique():,} ID lặp với bản ghi khác nhau; xem week5_conflicting_ids+ma_thi_sinh_xung_dot.csv.")

    score_issues = score_domain_issues(clean, clean_source_rows)
    write_csv(score_issues, tables / "week5_score_domain_issues+diem_ngoai_mien.csv")
    if not score_issues.empty:
        raise ValueError(f"Có {len(score_issues):,} điểm ngoài [0, 10]; xem week5_score_domain_issues+diem_ngoai_mien.csv.")
    if clean["Student ID"].isna().any():
        raise ValueError("Student ID bị thiếu; pipeline dừng và không xuất final.csv.")
    if clean["Student ID"].duplicated().any():
        raise ValueError("ID trùng sau khi loại bản ghi giống hệt; xem bảng chẩn đoán.")

    # The code and score are expected to be missing together. Any mismatch is
    # reported as a quality issue; never guess or fill either value.
    language_mismatch = clean["Foreign language"].isna().ne(clean["Foreign language code"].isna())
    mismatch_table = pd.DataFrame({
        "source_row": clean_source_rows.loc[language_mismatch].to_numpy(),
        "Student ID": clean.loc[language_mismatch, "Student ID"].to_numpy(),
        "Foreign language": clean.loc[language_mismatch, "Foreign language"].to_numpy(),
        "Foreign language code": clean.loc[language_mismatch, "Foreign language code"].to_numpy(),
    })
    write_csv(mismatch_table, tables / "week5_language_score_code_mismatches+diem_ma_ngoai_ngu_khong_khop.csv")
    if not mismatch_table.empty:
        raise ValueError(f"Có {len(mismatch_table):,} mâu thuẫn giữa điểm và mã Ngoại ngữ.")

    missing_rows = []
    for col in COLUMNS:
        count = int(clean[col].isna().sum())
        missing_rows.append({"column": col, "rows_total": len(clean), "missing_n": count,
                             "observed_n": len(clean) - count,
                             "missing_pct": 100 * count / len(clean) if len(clean) else 0.0,
                             "decision": "Giữ null; không suy đoán nguyên nhân từng dòng"})
    missing = pd.DataFrame(missing_rows)
    write_csv(missing, tables / "week5_missing_by_column+thieu_theo_cot.csv")
    missing_context, missing_context_summary = missing_by_observed_group(clean)
    write_csv(missing_context, tables / "week5_missing_by_observed_group+thieu_theo_mon_va_nhom.csv")
    write_csv(missing_context_summary, tables / "week5_missing_group_summary+tong_hop_thieu_theo_nhom.csv")

    comparison, details = detect_outliers(clean)
    if int(comparison["either_n"].sum()) != len(details):
        raise AssertionError("Tổng cờ theo môn không khớp số dòng của bảng chi tiết.")
    write_csv(comparison, tables / "week5_outlier_comparison+so_sanh_ngoai_le.csv")
    details = details.sort_values(["abs_z", "Student ID", "column"],
                                  ascending=[False, True, True], kind="stable")
    write_csv(details, tables / "week5_outlier_details+chi_tiet_ngoai_le.csv")

    clean = clean.copy()
    clean["exam_year"] = np.int16(2023)
    clean["exam_council_code"] = clean["Student ID"].str.slice(0, 2).astype("string")
    clean["observed_exam_group"] = observed_exam_group(clean)
    left_n = len(clean)
    source_keys = clean[["exam_year", "exam_council_code"]].drop_duplicates()
    if source_keys.duplicated(["exam_year", "exam_council_code"]).any():
        raise AssertionError("Main-key distinct table unexpectedly contains duplicates.")
    used_codes = set(clean["exam_council_code"].dropna().astype(str))
    reference_codes = set(ref["exam_council_code"].astype(str))
    key_audit = logged_merge(source_keys, ref, label="distinct_key_check", operations=merge_operations,
                                  on=["exam_year", "exam_council_code"], how="left",
                                  validate="one_to_one", indicator="merge_status")
    # Obtain the candidate count per key for an interpretable mismatch report.
    key_sizes = clean.groupby(["exam_year", "exam_council_code"], as_index=False).size()
    key_audit = logged_merge(
        key_audit, key_sizes, label="key_candidate_counts", operations=merge_operations,
        on=["exam_year", "exam_council_code"], validate="one_to_one")
    key_audit = key_audit.rename(columns={"size": "candidate_rows"})
    key_audit["exam_council_name"] = key_audit["exam_council_name"].fillna("")
    write_csv(key_audit.sort_values(["exam_year", "exam_council_code"]),
              tables / "week5_merge_key_audit+kiem_tra_khoa_ghep.csv")

    # Merge is many-to-one, left preserving, and retains original source order.
    clean["_pipeline_order"] = np.arange(left_n, dtype="int64")
    merged = left_merge_council(clean, ref, merge_operations)
    write_csv(pd.DataFrame(merge_operations), tables / "week5_merge_operations+nhat_ky_phep_ghep.csv")
    merged = merged.sort_values("_pipeline_order", kind="stable").reset_index(drop=True)
    merged["merge_status"] = merged["_merge_indicator"].map(
        {"both": "matched", "left_only": "left_only"}).astype("string")
    n_matched = int(merged["merge_status"].eq("matched").sum())
    n_unmatched = int(merged["merge_status"].eq("left_only").sum())
    if len(merged) != left_n or n_matched + n_unmatched != left_n:
        raise AssertionError("Left merge changed row count or did not reconcile match states.")
    left_rate = 100 * n_matched / left_n if left_n else 0.0
    key_matched = int(key_audit["merge_status"].eq("both").sum())
    key_rate = 100 * key_matched / len(key_audit) if len(key_audit) else 0.0
    merge_summary = pd.DataFrame([{
        "main_rows_before_merge": left_n, "main_rows_after_merge": len(merged),
        "reference_rows": len(ref), "main_distinct_keys": len(key_audit),
        "reference_distinct_keys": len(ref), "reference_duplicate_keys": 0,
        "matched_rows": n_matched, "unmatched_rows": n_unmatched,
        "record_match_rate_pct": left_rate, "matched_distinct_keys": key_matched,
        "unmatched_distinct_keys": len(key_audit) - key_matched,
        "key_match_rate_pct": key_rate,
        "unused_reference_codes": len(reference_codes - used_codes),
        "row_count_preserved": len(merged) == left_n,
    }])
    write_csv(merge_summary, tables / "week5_merge_summary+tong_hop_ghep.csv")
    unmatched = key_audit.loc[key_audit["merge_status"].ne("both")].copy()
    write_csv(unmatched, tables / "week5_unmatched_keys+khoa_khong_khop.csv")
    unused = ref.loc[~ref["exam_council_code"].astype(str).isin(used_codes)].copy()
    write_csv(unused, tables / "week5_unused_reference_codes+ma_nguon_chua_dung.csv")

    final = merged[FINAL_COLUMNS].copy()
    # Final data contains the original 11 fields plus exactly five documented
    # context columns. Scores and their null masks are never altered.
    if list(final.columns) != FINAL_COLUMNS:
        raise AssertionError("Final schema does not match the documented Week 5 schema.")
    final.to_csv(paths["final"], index=False, encoding="utf-8-sig")
    roundtrip = pd.read_csv(paths["final"], dtype={
        "Student ID": "string", "Foreign language code": "string",
        "exam_council_code": "string", "exam_council_name": "string",
        "observed_exam_group": "string", "merge_status": "string",
    }, keep_default_na=False, na_values=[""])
    text_idempotent = True
    for col in TEXT:
        once = normalize_text(raw[col], uppercase=(col == "Foreign language code"))
        twice = normalize_text(once, uppercase=(col == "Foreign language code"))
        text_idempotent &= once.equals(twice)
    checks = {
        "source_hash_unchanged": source_hash_before == file_sha256(source_path),
        "row_count_preserved_after_duplicate_policy": len(roundtrip) == len(clean),
        "output_schema_exact": list(roundtrip.columns) == FINAL_COLUMNS,
        "source_id_order_preserved": roundtrip["Student ID"].astype("string").equals(
            clean["Student ID"].astype("string").reset_index(drop=True)),
        "scores_identical": all(np.array_equal(
            pd.to_numeric(roundtrip[col], errors="raise").to_numpy(dtype="float64"),
            clean[col].reset_index(drop=True).to_numpy(dtype="float64"), equal_nan=True)
            for col in SCORES),
        "missingness_identical": all(roundtrip[col].isna().equals(
            clean[col].reset_index(drop=True).isna()) for col in SCORES),
        "leading_zero_ids_preserved": bool(roundtrip["Student ID"].str.fullmatch(r"[0-9]{8}").all()),
        "merge_rows_preserved": len(merged) == left_n,
        "merge_counts_reconciled": n_matched + n_unmatched == left_n,
        "outlier_detail_counts_reconciled": int(comparison["either_n"].sum()) == len(details),
        "all_ids_unique_after_exact_duplicate_policy": not final["Student ID"].duplicated().any(),
        "roundtrip_text_standardization_idempotent": bool(text_idempotent),
    }
    if not all(checks.values()):
        raise AssertionError(f"Week 5 validation failed: {checks}")

    dictionary = make_data_dictionary()
    write_csv(dictionary, tables / "week5_data_dictionary+tu_dien_du_lieu.csv")
    dictionary_lines = ["# Từ điển dữ liệu Week 5", "", "Bảng mô tả 16 cột của `data/processed/week5_final+du_lieu_cuoi.csv`. Các tên cột giữ nguyên để đối chiếu dữ liệu nguồn.", "", "| Cột | Ý nghĩa | Nguồn |", "| --- | --- | --- |"]
    dictionary_lines.extend(f"| `{r.column}` | {r.meaning} | {r.origin} |" for r in dictionary.itertuples())
    dictionary_lines.extend(["", "`observed_exam_group` chỉ là nhóm điểm hiện diện trong CSV; `science_only`/`social_only` không xác minh hồ sơ đăng ký. Những ô thiếu ở tổ hợp đối diện chỉ là ứng viên thiếu có tính cấu trúc.", "", "Nguồn và quy tắc ánh xạ: [week5_source_mapping+anh_xa_nguon.md](week5_source_mapping+anh_xa_nguon.md).", ""])
    (output_root / "docs/week5_data_dictionary+tu_dien_du_lieu.md").write_text("\n".join(dictionary_lines), encoding="utf-8")
    cleaning = make_cleaning_log(root, clean, comparison, text_summary, raw_rows,
                                 int(duplicates.sum()), n_matched, n_unmatched)
    write_csv(cleaning, tables / "week5_cleaning_log+nhat_ky_lam_sach.csv")

    stage_rows = [
        {"step": "01_read_sources", "rows_before": 0, "rows_after": raw_rows,
         "rows_removed": 0, "scope_rows": raw_rows, "changed_rows": 0,
         "result": "Đọc CSV gốc và danh mục 2023; kiểm tra schema, hash, mã duy nhất."},
        {"step": "02_text_standardization", "rows_before": raw_rows, "rows_after": raw_rows,
         "rows_removed": 0, "scope_rows": raw_rows,
         "changed_rows": int((raw[TEXT].fillna("").ne(text_clean[TEXT].fillna("")).any(axis=1)).sum()),
         "result": "NFKC, strip, gộp whitespace; uppercase mã ngoại ngữ; kiểm tra mã sau chuẩn hóa."},
        {"step": "03_exact_duplicate_removal", "rows_before": raw_rows,
         "rows_after": len(clean), "rows_removed": int(duplicates.sum()),
         "scope_rows": raw_rows, "changed_rows": int(duplicates.sum()),
         "result": "Loại bản ghi trùng hoàn toàn sau lần xuất hiện đầu; xung đột ID làm pipeline dừng."},
        {"step": "04_audit_and_missing", "rows_before": len(clean), "rows_after": len(clean),
         "rows_removed": 0, "scope_rows": int(clean[SCORES].isna().sum().sum()),
         "changed_rows": 0, "result": "Giữ null; xác thực ID, mã, miền điểm 0–10; phân nhóm ô thiếu cấu trúc ứng viên và chưa rõ."},
        {"step": "05_outlier_detection", "rows_before": len(clean), "rows_after": len(clean),
         "rows_removed": 0, "scope_rows": int(comparison["either_n"].sum()),
         "changed_rows": 0, "result": "Tính lại IQR/Z-score; cờ chỉ để điều tra, không sửa/xóa điểm."},
        {"step": "06_merge_exam_council", "rows_before": left_n,
         "rows_after": len(merged), "rows_removed": 0, "scope_rows": left_n,
         "changed_rows": 0, "result": f"Left many-to-one merge; {n_matched:,} khớp, {n_unmatched:,} không khớp."},
        {"step": "07_roundtrip_validation", "rows_before": left_n,
         "rows_after": len(roundtrip), "rows_removed": 0, "scope_rows": left_n,
         "changed_rows": 0, "result": "Đọc lại CSV, xác nhận schema, thứ tự, điểm, null, mã chuỗi và match count."},
    ]
    stage_log = pd.DataFrame(stage_rows)
    write_csv(stage_log, tables / "week5_pipeline_log+nhat_ky_quy_trinh.csv")
    draw_merge_chart(n_matched, n_unmatched,
                     paths["figures"] / "week5_merge_coverage+ty_le_ghep.png")

    metrics = {
        "source": {"main_file": str(RAW).replace("\\", "/"),
                   "main_sha256": source_hash_before, "main_rows": raw_rows,
                   "main_columns": COLUMNS,
                   "reference_file": str(REFERENCE).replace("\\", "/"),
                   "reference_sha256": file_sha256(root / REFERENCE),
                   "reference_rows": len(ref),
                   "reference_url": source_registry["exam_council_reference"]["url"],
                   "reference_checked_at": source_registry["exam_council_reference"]["checked_at"],
                   "government_excerpt_sha256": file_sha256(root / GOV_EXCERPT),
                   "government_excerpt_rows": 63,
                   "supplemental_code_65_url": source_registry["supplemental_code_65"]["url"],
                   "student_id_structure_url": source_registry["student_id_structure"]["url"]},
        "processing": {"rows_after_exact_duplicate_removal": len(clean),
                       "exact_duplicate_rows_removed": int(duplicates.sum()),
                       "unique_candidate_ids": int(clean["Student ID"].nunique()),
                       "scores_are_not_imputed_scaled_encoded_or_changed": True,
                       "outlier_parameters": {"iqr_multiplier": 1.5,
                                              "quantile_interpolation": "linear",
                                              "z_threshold": 3, "ddof": 0},
                       "outlier_flagged_score_cells_union": len(details),
                       "outlier_flagged_candidates": int(details["Student ID"].nunique()),
                       "missing_score_cells_kept": int(clean[SCORES].isna().sum().sum()),
                       "structural_candidate_missing_cells": int(missing_context_summary["structural_candidate_cells"].sum()),
                       "unresolved_missing_cells": int(missing_context_summary["unresolved_cells"].sum()),
                       "text_standardization": text_summary.to_dict(orient="records")},
        "merge": {**{key: (value.item() if isinstance(value, np.generic) else value)
                      for key, value in merge_summary.iloc[0].to_dict().items()},
                  "match_rate_definition": "matched rows / main rows before merge × 100",
                  "key_match_rate_definition": "matched distinct (year, code) keys / valid distinct main keys × 100",
                  "unmatched_policy": "keep the main row; exam_council_name stays missing; merge_status=left_only"},
        "output": {"file": "data/processed/week5_final+du_lieu_cuoi.csv",
                   "sha256": file_sha256(paths["final"]), "rows": len(final),
                   "columns": FINAL_COLUMNS, "roundtrip_rows": len(roundtrip)},
        "validation": checks,
        "environment": {"python": platform.python_version(), "pandas": pd.__version__,
                        "numpy": np.__version__},
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
    write_json(metrics, paths["metrics"])

    # Render the independent Week 5 report and a cached, executable notebook.
    from src.build_week5_notebook import build_notebook
    from src.report_week5 import write_report
    write_report(output_root, metrics)
    build_notebook(output_root)

    # Hash all reproducibility-critical outputs except the manifest, which
    # deliberately includes runtime duration and therefore changes per run.
    manifest_hashes = {}
    for rel in ["data/processed/week5_final+du_lieu_cuoi.csv", *[
        f"outputs/tables/{p.name}" for p in sorted(tables.glob("week5_*.csv"))],
        "outputs/figures/week5_merge_coverage+ty_le_ghep.png",
        "docs/week5_report+bao_cao.md", "docs/week5_data_dictionary+tu_dien_du_lieu.md",
        "notebooks/week5_exercises+bai_tap_tuan5.ipynb"]:
        full = output_root / rel
        if full.exists():
            manifest_hashes[rel.replace("\\", "/")] = file_sha256(full)
    metrics["deterministic_output_sha256"] = manifest_hashes
    write_json(metrics, paths["metrics"])
    return metrics
