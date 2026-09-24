"""Build the standalone Vietnamese Week 5 report beside the Week 3/4 reports."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

SCORE_NAMES = {
    "Mathematics": "Toán", "Literature": "Ngữ văn", "Foreign language": "Ngoại ngữ",
    "Physics": "Vật lý", "Chemistry": "Hóa học", "Biology": "Sinh học",
    "History": "Lịch sử", "Geography": "Địa lý", "Civic education": "GDCD",
}


def fmt_int(value) -> str:
    return f"{int(value):,}".replace(",", ".")


def fmt_pct(value, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}".replace(".", ",") + "%"


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    out.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in rows)
    return "\n".join(out)


def write_report(output_root: Path, metrics: dict) -> Path:
    output_root = Path(output_root)
    tables = output_root / "outputs/tables"
    source = metrics["source"]
    merge = metrics["merge"]
    miss = pd.read_csv(tables / "week5_missing_by_column+thieu_theo_cot.csv")
    missing_groups = pd.read_csv(tables / "week5_missing_group_summary+tong_hop_thieu_theo_nhom.csv")
    compare = pd.read_csv(tables / "week5_outlier_comparison+so_sanh_ngoai_le.csv")
    clean_log = pd.read_csv(tables / "week5_cleaning_log+nhat_ky_lam_sach.csv", keep_default_na=False)
    stage_log = pd.read_csv(tables / "week5_pipeline_log+nhat_ky_quy_trinh.csv", keep_default_na=False)
    operations = pd.read_csv(tables / "week5_merge_operations+nhat_ky_phep_ghep.csv")
    operations_table = md_table(
        ["Phép ghép", "Dòng trước", "Dòng bên phải", "Dòng sau", "Kiểu", "Kiểm tra khóa"],
        [[r.merge, fmt_int(r.rows_before), fmt_int(r.right_rows), fmt_int(r.rows_after),
          r.how, r.validate] for r in operations.itertuples()])
    text = pd.read_csv(tables / "week5_text_standardization+chuan_hoa_chuoi.csv")
    unmatched = pd.read_csv(tables / "week5_unmatched_keys+khoa_khong_khop.csv", dtype={"exam_council_code": "string"})
    unused = pd.read_csv(tables / "week5_unused_reference_codes+ma_nguon_chua_dung.csv", dtype={"exam_council_code": "string"})

    missing_rows = [[r.column, fmt_int(r.missing_n), fmt_int(r.observed_n),
                     fmt_pct(r.missing_pct, 3), "Bắt buộc có; thiếu thì dừng" if r.column == "Student ID"
                     else "Giữ null"] for r in miss.itertuples()]
    missing_group_table = md_table(
        ["Nhóm điểm quan sát", "Thí sinh", "Ô điểm thiếu", "Ứng viên thiếu cấu trúc", "Chưa rõ nguyên nhân"],
        [[r.observed_exam_group, fmt_int(r.group_rows), fmt_int(r.missing_score_cells),
          fmt_int(r.structural_candidate_cells), fmt_int(r.unresolved_cells)]
         for r in missing_groups.itertuples()])

    outlier_rows = []
    for r in compare.itertuples():
        outlier_rows.append([
            SCORE_NAMES.get(r.column, r.column), fmt_int(r.n_observed),
            f"{r.iqr_lower:.5f} – {r.iqr_upper:.5f}",
            fmt_int(r.iqr_n), fmt_pct(r.iqr_pct, 4),
            f"{r.z_lower:.5f} – {r.z_upper:.5f}",
            fmt_int(r.z_n), fmt_pct(r.z_pct, 4), fmt_int(r.both_n), fmt_int(r.either_n),
        ])
    outlier_table = md_table(["Môn", "Điểm quan sát", "Ngưỡng IQR", "Cờ IQR", "Tỷ lệ",
                              "Ngưỡng Z-score", "Cờ Z", "Tỷ lệ", "Cả hai", "Hợp"], outlier_rows)

    text_rows = [[r.column, fmt_int(r.distinct_before), fmt_int(r.distinct_after),
                  fmt_int(r.missing_before), fmt_int(r.changed_rows), fmt_int(r.invalid_after)]
                 for r in text.itertuples()]
    text_table = md_table(["Cột", "Distinct trước", "Distinct sau", "Thiếu", "Dòng đổi", "Sai định dạng sau"], text_rows)

    stage_rows = [[r.step, fmt_int(r.rows_before), fmt_int(r.rows_after),
                   fmt_int(r.rows_removed), fmt_int(r.scope_rows), fmt_int(r.changed_rows), r.result]
                  for r in stage_log.itertuples()]
    stage_table = md_table(["Bước", "Dòng trước", "Dòng sau", "Loại", "Phạm vi xét", "Đổi", "Kết quả"], stage_rows)

    log_week5 = clean_log.loc[pd.to_numeric(clean_log["week"], errors="coerce").eq(5)]
    log_rows = [[r.ID, r.column_or_record, r.issue, r.decision, r.reason,
                 fmt_int(r.scope_rows), fmt_int(r.changed_rows)] for r in log_week5.itertuples()]
    w5_log_table = md_table(["ID", "Cột / bản ghi", "Vấn đề", "Quyết định", "Lý do", "Phạm vi", "Đổi"], log_rows)

    unmatched_names = ("; ".join(f"{r.exam_council_code} ({fmt_int(r.candidate_rows)} dòng)"
                                 for r in unmatched.itertuples()) if len(unmatched) else "Không có khóa không khớp.")
    unused_names = ("; ".join(f"{r.exam_council_code} — {r.exam_council_name}"
                              for r in unused.itertuples()) if len(unused) else "Không có mã nguồn chưa dùng.")
    text_total_changes = int(text["changed_rows"].sum())
    outlier_cells = int(metrics["processing"]["outlier_flagged_score_cells_union"])
    outlier_students = int(metrics["processing"]["outlier_flagged_candidates"])
    output_names = ["Student ID", "Mathematics", "Literature", "Foreign language", "Physics",
                    "Chemistry", "Biology", "History", "Geography", "Civic education",
                    "Foreign language code", "exam_year", "exam_council_code",
                    "exam_council_name", "observed_exam_group", "merge_status"]

    report = f"""# INFO3020 Week 5 — Transformation, reduction & integration

**Bài tập:** EX5.1–EX5.3 · **Hạn:** 23:59 ngày trước buổi học Week 6  
**Câu hỏi nghiên cứu:** *Phân bố điểm thi THPT năm 2023 khác nhau thế nào giữa các Hội đồng thi, và tỷ lệ thiếu điểm cùng nhóm môn quan sát ảnh hưởng gì đến cách diễn giải?*

## Phạm vi và nguồn dữ liệu

Pipeline xử lý toàn bộ **{fmt_int(source['main_rows'])} bản ghi** của CSV dự án, không lấy mẫu. Tệp nguồn được giữ nguyên; SHA-256 là `{source['main_sha256']}`. Dữ liệu gốc có 11 cột: mã thí sinh, 9 điểm thi và mã Ngoại ngữ.

Nguồn bổ sung là danh mục **{fmt_int(source['reference_rows'])} mã Hội đồng thi**. **63 mã và tên** được chép từ [bảng tra cứu năm 2023 của Báo Chính phủ]({source['reference_url']}); mã 1–9 được thêm số 0 đầu để khớp ID. **Mã 65** `Cục Nhà trường -Bộ Quốc phòng` bổ sung từ [Phụ lục VIII, Công văn 1515/BGDĐT-QLCL]({source['supplemental_code_65_url']}). Bản PDF này chỉ ghi tháng 4/2023 và để trống ngày ban hành, nên không suy đoán ngày. Ngày kiểm tra nguồn: **{source['reference_checked_at']}**. Mã 20 không có trong hai danh mục. Bảng trích 63 dòng có SHA-256 `{source['government_excerpt_sha256']}` và file ghép có SHA-256 `{source['reference_sha256']}`. Mã 33 có khác biệt cách viết giữa hai nguồn; file ghép dùng cách viết Báo Chính phủ. Xem [bảng trích gốc](week5_gov_table_excerpt+trich_bang_nguon.csv), [quy tắc ánh xạ](week5_source_mapping+anh_xa_nguon.md) và [bảng kiểm tra từng mã](../outputs/tables/week5_reference_source_check+doi_chieu_nguon_bo_sung.csv).

Quy tắc ghép lấy **hai ký tự đầu của Student ID** làm `exam_council_code`, theo [hướng dẫn cấu trúc số báo danh năm 2023]({source['student_id_structure_url']}). Trong lần chạy, 63/63 mã riêng ở dữ liệu chính khớp danh mục. Tên Hội đồng thi theo mã không chứng minh nơi cư trú hay trường học của thí sinh.

## EX5.1 — Pipeline tiền xử lý

Pipeline gồm đọc và kiểm tra nguồn → chuẩn hóa chuỗi và kiểm tra mã → phát hiện/loại bản ghi trùng hoàn toàn (so trên cột gốc đã parse, giữ lần đầu) → kiểm tra ID xung đột và miền điểm → thống kê thiếu → tính cờ ngoại lệ → suy nhóm môn quan sát → ghép danh mục → ghi dữ liệu và kiểm tra round-trip. Nếu có ID xung đột, điểm ngoài 0–10, mã sai hoặc khóa nguồn trùng, pipeline dừng. **Không điền giá trị thiếu, không sửa/xóa ngoại lệ, không scale/encode/PCA.**

### Số dòng qua từng bước

{stage_table}

**Cách đọc:** `Dòng trước/sau` là số bản ghi tại ranh giới của bước; `Loại` chỉ là dòng thật sự bị loại; `Phạm vi xét` có thể là số ô thiếu hoặc ô ngoại lệ, nên không phải lúc nào cũng là số thí sinh duy nhất. Các phạm vi có thể chồng lấp và không được cộng để suy ra số người khác nhau. `Đổi` đếm dòng bị loại hoặc có giá trị trong 11 cột gốc thay đổi; việc thêm cột ngữ cảnh được mô tả riêng, không tính là sửa giá trị gốc.

### Missing values — giữ thiếu, không suy đoán

| Cột gốc | Thiếu | Quan sát | Thiếu (%) | Quyết định |
| --- | ---: | ---: | ---: | --- |
{chr(10).join("| " + " | ".join(map(str, row)) + " |" for row in missing_rows)}

**Cách tính:** `Thiếu (%) = số ô null trong cột / số dòng sau chính sách loại trùng × 100`. Null bị bỏ khỏi phép tính điểm, nhưng vẫn giữ nguyên trong file đầu ra. Tỷ lệ thiếu khác nhau giữa môn không khẳng định một nguyên nhân cụ thể; nhóm môn bên dưới chỉ suy từ điểm đang hiện diện.

{missing_group_table}

**Giải nghĩa nhóm thiếu:** `science_only` là có ít nhất một điểm Vật lý/Hóa học/Sinh học và không có điểm ở ba môn Lịch sử/Địa lý/GDCD; `social_only` định nghĩa ngược lại. `both_observed` có ít nhất một điểm ở cả hai nhóm; `neither_observed` không có điểm ở cả hai. Ở `science_only`, ô thiếu thuộc ba môn xã hội được **đánh dấu ứng viên thiếu cấu trúc**; ở `social_only`, ô thiếu thuộc ba môn tự nhiên cũng vậy. Đây là suy luận từ điểm hiện diện, **không xác nhận thí sinh đăng ký tổ hợp nào**. Mọi ô thiếu khác là `chưa rõ nguyên nhân`. Số ô thiếu = ứng viên cấu trúc + chưa rõ; các tổng đối chiếu với bảng thiếu theo cột. Chi tiết từng môn và nhóm: [`week5_missing_by_observed_group+thieu_theo_mon_va_nhom.csv`](../outputs/tables/week5_missing_by_observed_group+thieu_theo_mon_va_nhom.csv).

### Ngoại lệ thống kê

- **IQR:** Q1 và Q3 là phân vị 25%/75% nội suy tuyến tính; `IQR = Q3 − Q1`. Gắn cờ nếu `x < Q1 − 1,5×IQR` hoặc `x > Q3 + 1,5×IQR`.
- **Z-score:** `Z = (x − μ)/σ`, dùng độ lệch chuẩn tổng thể `ddof=0`; gắn cờ khi `|Z| > 3`.
- Tính riêng từng môn trên điểm quan sát; thiếu không tham gia phép tính. Cờ chỉ là tín hiệu điều tra, không phải phán quyết sai dữ liệu.

{outlier_table}

**Ý nghĩa số đếm:** `Cờ IQR`, `Cờ Z`, `Cả hai` và `Hợp` là số **ô điểm**, không phải số học sinh; `Hợp = IQR ∪ Z`. Có **{fmt_int(outlier_cells)} ô điểm** thuộc hợp cờ, của **{fmt_int(outlier_students)} thí sinh khác nhau**. Tỷ lệ của từng môn dùng số điểm quan sát của chính môn đó làm mẫu số. Bảng đầy đủ có ngưỡng chưa làm tròn và cờ từng ô tại [`week5_outlier_comparison+so_sanh_ngoai_le.csv`](../outputs/tables/week5_outlier_comparison+so_sanh_ngoai_le.csv) và [`week5_outlier_details+chi_tiet_ngoai_le.csv`](../outputs/tables/week5_outlier_details+chi_tiet_ngoai_le.csv).

### Chuẩn hóa văn bản

Student ID và Foreign language code được đọc dạng chuỗi để giữ số 0 đầu. Quy tắc là Unicode NFKC, bỏ khoảng trắng đầu/cuối, gộp khoảng trắng liền nhau; mã ngoại ngữ được chuyển chữ hoa. ID phải khớp `[0-9]{{8}}`, mã ngoại ngữ phải thuộc N1–N7; giá trị sai không được tự đoán.

{text_table}

**Cách đếm:** distinct = số giá trị khác nhau, không tính null; thiếu được báo riêng. `Dòng đổi` so sánh giá trị trước/sau, trong đó hai null được xem là không đổi. Tổng cộng **{fmt_int(text_total_changes)} dòng đổi** ở hai cột; đây là kết quả quan sát từ dữ liệu, không đặt biến thể giả để giảm distinct. Bảng lỗi định dạng (nếu có) ở [`week5_text_validation_issues+loi_dinh_dang_chuoi.csv`](../outputs/tables/week5_text_validation_issues+loi_dinh_dang_chuoi.csv).

## EX5.2 — Ghép nguồn danh mục Hội đồng thi

Chuẩn hóa khóa `(exam_year=2023, exam_council_code=Student ID[:2])`; ghép trái bằng `validate="many_to_one"` và `indicator=True`. Khóa bên danh mục phải duy nhất. Ghép trái bảo đảm giữ thí sinh không khớp để có thể đối soát; trường tên để trống và `merge_status=left_only`.

### Kết quả ghép

Mỗi phép `merge` in `len(df)` ngay trước và sau khi thực hiện. Ba phép đầu đối soát nguồn/khóa; phép cuối tích hợp dữ liệu thí sinh. Nhật ký đầy đủ: [`week5_merge_operations+nhat_ky_phep_ghep.csv`](../outputs/tables/week5_merge_operations+nhat_ky_phep_ghep.csv).

{operations_table}

{md_table(["Chỉ số", "Kết quả", "Cách hiểu"], [
    ["Dòng bảng chính trước ghép", fmt_int(merge['main_rows_before_merge']), "Mẫu số tính match rate theo dòng."],
    ["Dòng danh mục nguồn", fmt_int(merge['reference_rows']), "Bảng khóa mã và tên của năm 2023."],
    ["Khóa mã riêng ở dữ liệu chính", fmt_int(merge['main_distinct_keys']), "Cặp (năm, mã) riêng biệt có trong ID."],
    ["Khóa trùng bên danh mục", fmt_int(merge['reference_duplicate_keys']), "Phải bằng 0 để validate many_to_one."],
    ["Số dòng sau ghép", fmt_int(merge['main_rows_after_merge']), "Phải bằng số dòng trước ghép."],
    ["Dòng khớp / không khớp", f"{fmt_int(merge['matched_rows'])} / {fmt_int(merge['unmatched_rows'])}", "matched + left_only phải bằng tổng dòng."],
    ["Match rate theo dòng", fmt_pct(merge['record_match_rate_pct']), "Matched rows / main rows × 100."],
    ["Match rate theo khóa", fmt_pct(merge['key_match_rate_pct']), "Mã riêng ghép được / tổng mã riêng × 100."],
    ["Mã danh mục chưa dùng", fmt_int(merge['unused_reference_codes']), unused_names],
])}

**Công thức:** match rate theo dòng = `số dòng matched / số dòng bảng chính trước merge × 100%`; match rate theo khóa = `số khóa riêng (năm, mã) khớp / số khóa riêng hợp lệ ở bảng chính × 100%`. Hai tỷ lệ dùng mẫu số khác nhau. `many_to_one` ngăn một mã nguồn làm nhân số dòng; `indicator` ghi trạng thái khớp. Kết quả ghép thực tế là **{fmt_pct(merge['record_match_rate_pct'])} theo dòng** và **{fmt_pct(merge['key_match_rate_pct'])} theo khóa**; sau ghép giữ **{fmt_int(merge['main_rows_after_merge'])} dòng**. Không khớp: {unmatched_names}

![Biểu đồ thanh tỷ lệ bản ghi ghép được](../outputs/figures/week5_merge_coverage+ty_le_ghep.png)

**Cách đọc biểu đồ:** đây là thanh ngang xếp chồng 100%; trục ngang là tỷ lệ bản ghi, xanh là khớp và cam là không khớp. Nhãn ghi số dòng cùng tỷ lệ trong mỗi nhóm. Biểu đồ cho thấy độ phủ của danh mục mã, không đo độ chính xác của điểm thi.

## EX5.3 — Dữ liệu bàn giao và khả năng tái lập

Dữ liệu cuối [`week5_final+du_lieu_cuoi.csv`](../data/processed/week5_final+du_lieu_cuoi.csv) gồm **{fmt_int(metrics['output']['rows'])} dòng, {len(output_names)} cột** theo đúng thứ tự:

`{", ".join(output_names)}`

11 cột gốc được giữ nguyên (ngoại trừ chuẩn hóa khoảng trắng/Unicode/chữ hoa nếu phát sinh); bổ sung năm thi, mã/tên Hội đồng thi, nhóm điểm tổ hợp quan sát và trạng thái ghép. Cột `observed_exam_group` nhận `science_only`, `social_only`, `both_observed` hoặc `neither_observed`; tên gọi mô tả **điểm đang có trong CSV**, không phải đăng ký môn. Điểm 0, điểm thiếu và ngoại lệ chưa xác minh tiếp tục giữ nguyên.

Cleaning Log tổng hợp **{fmt_int(len(clean_log))} quyết định** Week 3–5. 35 dòng đầu là bản chụp nhật ký Week 3–4 đã dựng từ bằng chứng hiện có; ngày gốc chưa rõ được để trống. Các cột `scope_rows` và `changed_rows` lần lượt phân biệt số bản ghi/ô thuộc phạm vi xét với số dòng thực sự đổi. Các quyết định mới của Week 5:

{w5_log_table}

### Chạy lại

Tại thư mục gốc trong PowerShell:

```powershell
& .venv/Scripts/python.exe src/main.py
```

Lệnh đọc hai tệp trong `data/raw`, kiểm tra hash và schema, tạo CSV đã xử lý, các bảng kiểm tra, Cleaning Log, manifest, biểu đồ, báo cáo Markdown Week 5 riêng và notebook Week 5 đã chạy. Không phụ thuộc vào dữ liệu `processed`, metrics hoặc bảng kết quả Week 3–4; nhật ký lịch sử Week 3–4 được lưu thành nguồn đầu vào có phiên bản tại [`week5_prior_decisions+quyet_dinh_tuan_truoc.csv`](week5_prior_decisions+quyet_dinh_tuan_truoc.csv).

Manifest [`week5_manifest+ho_so_dau_ra.json`](../outputs/week5_manifest+ho_so_dau_ra.json) lưu hash, thông số và phiên bản môi trường. Kiểm tra đọc lại CSV xác nhận schema, số dòng, thứ tự ID, mã chuỗi có số 0 đầu, điểm và mặt nạ null; SHA-256 dùng để đối chiếu nội dung file giữa các lần chạy. Bảng tóm tắt nhật ký pipeline: [`week5_pipeline_log+nhat_ky_quy_trinh.csv`](../outputs/tables/week5_pipeline_log+nhat_ky_quy_trinh.csv). [Từ điển dữ liệu Week 5](week5_data_dictionary+tu_dien_du_lieu.md) và [bảng CSV tương ứng](../outputs/tables/week5_data_dictionary+tu_dien_du_lieu.csv) giải thích từng cột.

Khi chuyển sang mô hình dự đoán, phải chia train/test trước; mọi bước học tham số từ dữ liệu như scaling hoặc encoding chỉ được `fit` trên train hoặc trong từng fold. Dataset Week 5 hiện giữ đơn vị điểm gốc để phục vụ EDA, không đưa phép biến đổi học từ toàn bộ tập vào đây.

## Câu hỏi nghiên cứu và giới hạn

Chênh lệch điểm giữa Hội đồng thi chỉ là so sánh phân bố mô tả; không được diễn giải thành chênh lệch năng lực địa phương hay tác động của chất lượng trường. Thành phần thí sinh, môn lựa chọn, thiếu dữ liệu, trường học và điều kiện tổ chức có thể khác nhau nhưng chưa có trong hai nguồn. Tuần 6 cần báo cáo mẫu số theo môn, nhóm và Hội đồng thi; tuần 7 chọn biểu đồ phù hợp; mọi nhận định phải nêu phạm vi dữ liệu hỗ trợ.

Tệp chính và bảng nguồn có thể được đối chiếu trực tiếp bằng hash tại manifest. Bảng các mã không dùng nằm ở [`week5_unused_reference_codes+ma_nguon_chua_dung.csv`](../outputs/tables/week5_unused_reference_codes+ma_nguon_chua_dung.csv); khóa không khớp ở [`week5_unmatched_keys+khoa_khong_khop.csv`](../outputs/tables/week5_unmatched_keys+khoa_khong_khop.csv).
"""
    destination = output_root / "docs/week5_report+bao_cao.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    return destination
