# Điểm thi THPT 2023 — bài tập tuần 3–5

Mỗi tuần có một thư mục trong `src/`, `docs/`, `notebooks/`, `data/processed/` và `outputs/`. Hai tệp nguồn bất biến nằm ở `data/raw/`. Mở báo cáo để đọc kết quả; mở notebook để xem phép tính và đầu ra.

| Tuần | Báo cáo | Notebook | Dữ liệu xử lý |
| --- | --- | --- | --- |
| 3 — Chất lượng và thiếu dữ liệu | [Báo cáo](docs/week3/report+bao_cao.md) | [Notebook](notebooks/week3/week3_exercises+bai_tap_tuan3.ipynb) | [Parquet](data/processed/week3/exam_2023.parquet) |
| 4 — Ngoại lệ và nhất quán | [Báo cáo](docs/week4/week4_report+bao_cao.md) | [Notebook](notebooks/week4/week4_exercises+bai_tap_tuan4.ipynb) | [CSV](data/processed/week4/week4_cleaned.csv) |
| 5 — Xử lý và ghép nguồn | [Báo cáo](docs/week5/week5_report+bao_cao.md) | [Notebook](notebooks/week5/week5_exercises+bai_tap_tuan5.ipynb) | [CSV dùng tiếp cho tuần 6–8](data/processed/week5/week5_final+du_lieu_cuoi.csv) |

Các bảng kiểm tra và hình nằm trong `outputs/week3/`, `outputs/week4/`, `outputs/week5/`. Nhật ký làm sạch để nộp cùng dữ liệu cuối: [Cleaning Log tuần 5](outputs/week5/tables/week5_cleaning_log+nhat_ky_lam_sach.csv). Nguồn bổ sung và quy tắc ghép ở [hồ sơ nguồn](docs/week5/week5_source_registry+ho_so_nguon.json) và [mapping](docs/week5/week5_source_mapping+anh_xa_nguon.md).

## Chạy lại

Từ thư mục gốc, tạo môi trường Python rồi cài `requirements.txt`:

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Chạy các tuần theo thứ tự; tuần 4 dùng Parquet do tuần 3 tạo. Tuần 5 có thể chạy độc lập từ hai tệp trong `data/raw/` và hồ sơ nguồn trong `docs/week5/`.

```powershell
& ./.venv/Scripts/python.exe -m src.week3.analyze
& ./.venv/Scripts/python.exe -m src.week3.build_notebook
& ./.venv/Scripts/python.exe -m src.week4.analyze_week4
& ./.venv/Scripts/python.exe -m src.week4.build_week4_notebook
& ./.venv/Scripts/python.exe src/main.py
& ./.venv/Scripts/python.exe -m unittest discover -s tests -v
& ./.venv/Scripts/python.exe -m src.week5.verify_week5
```

Notebook tuần 5 đọc các đầu ra đã có; `Run All` trong notebook không thay lệnh `src/main.py`. Số báo danh và các mã cần đọc dạng chuỗi để giữ số 0 đầu. Dữ liệu cuối giữ nguyên điểm 0 và ô thiếu; các nhãn nhóm môn chỉ dựa trên điểm quan sát, không xác nhận hồ sơ đăng ký thi.
