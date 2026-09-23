# Điểm thi tốt nghiệp THPT 2023 — INFO3020 Week 3

Dự án hoàn thành ba bài EX3.1–EX3.3 của slide 35 trong `W3 - Data Quality and Processing_.pptx`: chấm sáu tiêu chí chất lượng có bằng chứng, giải thích từng cột có dữ liệu thiếu, và so sánh hai cách điền trên điểm Toán. [Bài báo cáo](docs/report+bao_cao.md) trình bày kết quả và giới hạn. Tệp slide do người dùng cung cấp nằm ngoài repo, tại thư mục Downloads.

## Dữ liệu và nguyên tắc

`data/raw/original.csv` là CSV gốc của [dataset Kaggle](https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam), gồm 1.022.060 dòng, 11 cột, SHA-256 `cdf22a6b45f8e23b522beb1c521782e36486cac39d3fb64bca2a2395edec39b5`. Code đọc Student ID như chuỗi để giữ số 0 đầu. Tệp `data/processed/exam_2023.parquet` giữ 11 cột, các điểm đã công bố và các ô trống. Điểm được điền thử chỉ nằm trong phép so sánh, không ghi vào Parquet.

Các môn tổ hợp có nhiều ô trống phù hợp với cấu trúc chọn môn, nhưng CSV không có hồ sơ đăng ký, chương trình học, miễn thi hoặc vắng thi để xác nhận nguyên nhân từng ô. Pipeline tách ô thiếu ở tổ hợp đối diện thành **ứng viên không áp dụng theo cấu trúc** và các ô còn lại thành **chưa rõ nguyên nhân**; cả hai vẫn giữ null. Báo cáo đối chiếu số môn thiếu trên cả 9 cột điểm với số môn thiếu trong 6 cột liên quan theo nhóm điểm tổ hợp quan sát. Có 4.476 dòng chỉ còn Student ID, cần đối soát nguồn trước khi diễn giải.

## Chạy lại

Dùng PowerShell tại thư mục gốc của repo:

```powershell
& .venv/Scripts/python.exe -m src.analyze
& .venv/Scripts/python.exe -m src.build_notebook
& .venv/Scripts/python.exe -m unittest discover -s tests -v
```

Nếu cần tạo môi trường mới:

```powershell
uv venv .venv
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.venv/.uv-cache')
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

Lệnh thứ nhất quét token nguồn, kiểm tra schema, xử lý số liệu trên toàn CSV và sinh bảng/hình. Lệnh thứ hai xây dựng và thực thi các ô code của notebook trong một namespace mới, lưu kết quả hiển thị vào `notebooks/week3_exercises+bai_tap_tuan3.ipynb`; không cần cài Jupyter để tạo notebook. Muốn chạy ô tương tác trong VS Code hoặc Jupyter, chọn kernel Python của `.venv` và cài hỗ trợ notebook của công cụ đó nếu cần.

## Tệp đầu ra

| Đường dẫn | Nội dung |
|---|---|
| `src/analyze.py` | Pipeline audit và hai so sánh Median |
| `src/build_notebook.py` | Tạo notebook có kết quả từ lần chạy sạch |
| `notebooks/week3_exercises+bai_tap_tuan3.ipynb` | Bài trình bày từng bước và kết quả đã chạy |
| `docs/report+bao_cao.md` | Bài viết EX3.1–EX3.3, phương pháp và giới hạn |
| `docs/foreign_language_code+ma_ngoai_ngu.md` | Ghi chú mapping mã ngoại ngữ |
| `outputs/metrics+chi_so.json` | Provenance, audit, pattern và số liệu thí nghiệm |
| `outputs/tables/column_profile+ho_so_cot.csv` | Kiểu, missing, unique, min/max của từng cột |
| `outputs/tables/missing_treatment+cach_xu_ly_thieu.csv` | Cơ chế giả thuyết, treatment và lý do của mọi cột thiếu |
| `outputs/tables/raw_nine_score_missing_counts+thieu_9_mon.csv` | Số điểm thiếu trên 9 môn, theo nhóm điểm tổ hợp quan sát |
| `outputs/tables/context_six_score_missing_counts+thieu_6_mon.csv` | Số ô trống trong 6 môn liên quan của hai nhóm xác định được |
| `outputs/tables/context_missing_subject_patterns+mau_mon_thieu.csv` | Mọi tổ hợp môn thiếu cụ thể trong 6 môn liên quan |
| `outputs/tables/missing_context_classification+phan_loai_o_thieu.csv` | Mỗi cột: ứng viên cấu trúc và phần chưa rõ theo ngữ cảnh |
| `outputs/tables/natural_missing_sensitivity+do_nhay_thieu_tu_nhien.csv` | Hai cách điền giả định trên 18.687 ô Toán đang trống |
| `outputs/tables/imputation_comparison+so_sanh_dien_khuyet.csv` | Hai cách điền trên 10.000 điểm Toán che nhân tạo và sai số |
| `outputs/figures/*.png` | Biểu đồ tỷ lệ thiếu, matrix mẫu và hai phân phối Toán |

Sáu điểm chất lượng, số đếm pattern theo nhóm, phân loại ô thiếu, bảng chéo và token nguồn được lưu trong `outputs/metrics+chi_so.json`. EX3.3 có hai góc nhìn. Bảng **nhạy cảm** điền thử những ô Toán thiếu tự nhiên dưới giả định chưa xác minh rằng tất cả đều có điểm thật. Bảng **thí nghiệm** che ngẫu nhiên 20% điểm Toán trong mẫu 50.000 dòng có điểm để đo sai số trên cùng các ô che. Hai phương pháp là Global Median và Group Median theo nhóm có điểm tự nhiên/xã hội; nhóm không rõ dùng trung vị chung. Seed 3020. Các kết quả không xác nhận giá trị thật của ô Toán tự nhiên đang trống.

Tài liệu slide tham chiếu: các trang 7, 13–18, 20–29, 32 và 35 của tệp PPTX người dùng cung cấp. Kết quả máy đọc đầy đủ nằm trong `outputs/metrics+chi_so.json`; các bảng CSV giữ số chưa làm tròn, còn báo cáo làm tròn để dễ đọc.
