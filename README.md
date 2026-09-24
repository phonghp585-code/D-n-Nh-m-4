# Điểm thi THPT 2023 — Week 3, 4 và 5

## Bắt đầu ở đây

**Bài hiện tại là Week 5.** Dữ liệu dùng tiếp cho Week 6–8 là `data/processed/week5_final+du_lieu_cuoi.csv`. Mở báo cáo để đọc kết quả; mở notebook để xem các ô code và đầu ra.

| Bạn muốn làm gì? | Mở file này |
|---|---|
| Đọc bài Week 5 | [Báo cáo Week 5](docs/week5_report+bao_cao.md) |
| Xem notebook Week 5 | [Notebook Week 5](notebooks/week5_exercises+bai_tap_tuan5.ipynb) |
| Xem kết luận kiểm tra bài và cách quản lý file | [Kiểm tra Week 5](docs/week5_review+kiem_tra_bai.md) |
| Hiểu 16 cột dữ liệu cuối | [Từ điển dữ liệu](docs/week5_data_dictionary+tu_dien_du_lieu.md) |
| Xem các quyết định làm sạch | [Cleaning Log](outputs/tables/week5_cleaning_log+nhat_ky_lam_sach.csv) |
| Xem nguồn thứ hai và khóa ghép | [Nguồn và mapping](docs/week5_source_mapping+anh_xa_nguon.md) |
| Xem kế hoạch các tuần tiếp theo | [Kế hoạch](mujctieu.md) |

## Chạy Week 5

Tại thư mục gốc dự án trong PowerShell:

```powershell
& .venv/Scripts/python.exe src/main.py
```

Một lệnh tái tạo CSV cuối, bảng kiểm tra, hình, báo cáo và notebook đã có kết quả. Nếu Python đang dùng đã cài các thư viện trong `requirements.txt`, có thể chạy `python src/main.py`.

Kiểm thử và kiểm tra tái lập (chạy sau lệnh trên):

```powershell
& .venv/Scripts/python.exe -m unittest discover -s tests -v
& .venv/Scripts/python.exe src/verify_week5.py
```

Phép kiểm tái lập sao chép raw, hồ sơ nguồn và code vào thư mục sạch, chạy pipeline rồi so SHA-256 từng đầu ra với lần chạy hiện tại. Bằng chứng lưu tại [week5_verification+kiem_tra_tai_lap.json](outputs/week5_verification+kiem_tra_tai_lap.json). Manifest không so byte vì có thời gian chạy. Thư mục kiểm tra tạm do lệnh tạo được dọn sau khi hoàn tất.

Notebook Week 5 đọc và kiểm tra đầu ra đã sinh; **Run All của notebook không thay thế lệnh chạy từ raw**. Biểu đồ được nhúng trong notebook. Để chạy notebook, chọn kernel `.venv` và mở từ thư mục gốc hoặc `notebooks/`.

## Quy tắc đặt tên

File đầu ra và tài liệu Week 5 dùng `week5_ten_tieng_anh+ten_tieng_viet`, ví dụ `week5_cleaning_log+nhat_ky_lam_sach.csv`. Phần tiếng Việt không dấu, ngăn cách từ bằng `_`, theo mẫu song ngữ có sẵn ở Week 3. Báo cáo và notebook giữ tên song ngữ như Week 4. Module Python dùng tên import hợp lệ, không có dấu `+`: `analyze_week5.py`.

## File nào sửa, file nào được sinh lại?

| Nhóm | Vai trò | Cách quản lý |
|---|---|---|
| `data/raw/original.csv` | Nguồn điểm thi gốc, 1.022.060 dòng × 11 cột | Giữ nguyên |
| `data/raw/exam_councils_2023.csv` | Danh mục 64 mã Hội đồng thi năm 2023 | Giữ cùng hồ sơ nguồn |
| `docs/week5_source_registry+ho_so_nguon.json`, `week5_source_mapping+anh_xa_nguon.md`, `week5_gov_table_excerpt+trich_bang_nguon.csv`, `week5_prior_decisions+quyet_dinh_tuan_truoc.csv` | Đầu vào nguồn, mapping và lịch sử | Không xóa khi dọn báo cáo; pipeline cần các file này |
| `src/` | Code tính toán và tạo báo cáo/notebook | Sửa logic ở đây rồi chạy lại |
| `tests/` | Kiểm thử các quy tắc xử lý | Chạy sau khi sửa code |
| `data/processed/` | Dữ liệu cuối theo từng tuần | Dùng `week5_final+du_lieu_cuoi.csv` cho bước tiếp theo |
| `outputs/tables/` | Bảng bằng chứng do code sinh | Không cần mở từng file; đi qua link trong báo cáo |
| `outputs/figures/` | Mỗi biểu đồ chỉ có một file PNG | Code Week 3–5 chỉ xuất PNG |
| `outputs/*metrics*.json`, `week5_manifest+ho_so_dau_ra.json`, `week5_verification+kiem_tra_tai_lap.json` | Số liệu và bằng chứng kiểm tra | Dành cho truy vết, không phải báo cáo chính |
| `docs/*report+bao_cao.md`, `week5_data_dictionary+tu_dien_du_lieu.md` | Báo cáo được sinh từ code | Week 5 sửa tại `src/report_week5.py` hoặc phần từ điển trong pipeline |
| `notebooks/week*_exercises+bai_tap_tuan*.ipynb` | Notebook trình bày từng tuần | Bản sinh lại; sửa bền vững trong `src/build*_notebook.py` |
| `mujctieu.md`, các PDF W5–W7 | Kế hoạch và đề bài tham chiếu | Không phải dữ liệu đầu vào của pipeline |
| `.venv/`, `__pycache__/`, `outputs/_review/` | Môi trường và file kiểm tra tạm | Không đưa vào bài nộp |

Đã dọn các mục rác: `data.ipynb` (0 byte), `reports/` (rỗng, chỉ có `.gitkeep`) và thư mục tạm rỗng `outputs/tmpyuf6r4fg/` đều đã bị xóa. Báo cáo thật nằm trong `docs/`.

## Code của từng tuần

| Tuần | Xử lý | Sinh bài trình bày | Báo cáo / notebook |
|---|---|---|---|
| 3 | `src/analyze.py` | `src/build_notebook.py` | [Báo cáo](docs/report+bao_cao.md) · [Notebook](notebooks/week3_exercises+bai_tap_tuan3.ipynb) |
| 4 | `src/analyze_week4.py` | `src/build_week4_notebook.py`, `src/week4_explanations.py` | [Báo cáo](docs/week4_report+bao_cao.md) · [Notebook](notebooks/week4_exercises+bai_tap_tuan4.ipynb) |
| 5 | `src/main.py` → `src/analyze_week5.py` | `src/report_week5.py`, `src/build_week5_notebook.py` | [Báo cáo](docs/week5_report+bao_cao.md) · [Notebook](notebooks/week5_exercises+bai_tap_tuan5.ipynb) |

Week 5 dùng lại hàm đọc dữ liệu, chuẩn hóa và ngoại lệ trong `src/analyze_week4.py`, cùng module `src/week4_explanations.py` mà nó import. Vì thế không xóa code Week 4 khi chỉ nộp Week 5. Nộp cả `src/` là cách đơn giản nhất.

Chạy lại bài cũ khi cần:

```powershell
& .venv/Scripts/python.exe -m src.analyze
& .venv/Scripts/python.exe -m src.build_notebook
& .venv/Scripts/python.exe -m src.build_week4_notebook
```

Week 4 cần các đầu ra/bằng chứng Week 3 đi kèm để đối chiếu. Week 5 dùng bản chụp lịch sử trong `docs/` và không cần đầu ra Week 3–4 để chạy.

## Bộ bài Week 5

Yêu cầu trực tiếp của EX5.3 là `data/processed/` và Cleaning Log đầy đủ. Để người chấm đọc và chạy lại, giữ cấu trúc đường dẫn:

- `README.md`, `requirements.txt`, toàn bộ `src/` và `tests/`.
- Hai file `data/raw/` và `data/processed/week5_final+du_lieu_cuoi.csv`.
- Các file `docs/week5_*` (gồm báo cáo, từ điển và hồ sơ nguồn).
- `notebooks/week5_exercises+bai_tap_tuan5.ipynb`.
- `outputs/tables/week5_*`, `outputs/figures/week5_*`, `outputs/week5_manifest+ho_so_dau_ra.json` và `outputs/week5_verification+kiem_tra_tai_lap.json`.

Khi chia sẻ cả repo, giữ Week 3–4 để truy vết lịch sử. Không cần tạo thêm `final.csv`, `merge_report.md` hoặc `EDA.ipynb` chỉ để giống cấu trúc minh họa: nội dung tương ứng đã có trong bộ file Week 5. Trang bài tập Week 5 không bắt buộc xuất báo cáo PDF.

## Môi trường và cách đọc dữ liệu

Tạo môi trường mới nếu chưa có `.venv` (cần cài `uv` trước):

```powershell
uv venv .venv
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.venv/.uv-cache')
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

Kiểm tra hiện tại dùng Python 3.12.14, pandas 3.0.1, NumPy 2.5.3, PyArrow 25.0.1, Matplotlib 3.11.2. `requirements.txt` quy định phiên bản tối thiểu, chưa khóa toàn bộ môi trường; kết quả so hash được xác nhận trong môi trường hiện tại.

```python
import pandas as pd

df = pd.read_csv(
    'data/processed/week5_final+du_lieu_cuoi.csv',
    dtype={'Student ID': 'string', 'Foreign language code': 'string',
           'exam_council_code': 'string'},
)
```

CSV dùng UTF-8 BOM. Luôn đọc các mã dạng chuỗi để giữ số 0 đầu. Dữ liệu cuối giữ điểm 0, ô thiếu và điểm ngoại lệ chưa xác minh. `observed_exam_group` mô tả điểm đang có, không xác nhận đăng ký môn; tên Hội đồng thi không chứng minh nơi cư trú hoặc chất lượng giáo dục. Mô hình sau này phải chia train/test trước khi fit scaling, encoding hoặc imputation.
