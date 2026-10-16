# Phân tích phổ điểm THPT 2023 và 2025

Phần tiếp nối dữ liệu đã hợp mã tỉnh của Nhóm 4, theo cấu trúc branch `thanh`. Dataset 2023 dùng từ `data/processed/week3/exam_2023.parquet`; dataset 2025 là tệp Git LFS `data/dataset_diem_thi_thpt_2025.csv` lấy từ branch `nhan`.

## Chạy tại thư mục gốc repository

```bash
git lfs pull
python -m pip install -r requirements-score-distribution.txt
python -m unittest tests.test_week6_score_distribution -v
python -m src.week6_score_distribution
```

Có thể chỉ định đường dẫn riêng bằng `--2023`, `--2025`, `--out`.

## Sản phẩm đầu ra
- `bao_cao_phan_tich_pho_diem_2023_2025.docx`: báo cáo Word gồm bảng thống kê, tỷ lệ ngưỡng và biểu đồ.
- `thong_ke_mo_ta_2023_2025.csv`: mean, median, standard deviation, skewness, excess kurtosis, quartile và tỷ lệ ngưỡng.
- `diem_long_2023_2025.csv`: dữ liệu dạng dài.
- `figures/`: histogram, KDE, boxplot và violin plot theo môn.
- `run_metadata.json`: thông tin nguồn và số điểm hợp lệ.

## Quy tắc và cách diễn giải
Không thay đổi dataset gốc, không điền điểm thiếu; chỉ điểm trong [0, 10] được tính. So sánh các môn được nhận diện ở cả hai năm. Tỷ lệ tính trên số điểm hợp lệ của môn-năm tương ứng. Kurtosis là excess kurtosis, phân phối chuẩn có giá trị tham chiếu 0.

Tuần 6: mean/median mô tả vị trí; standard deviation/IQR mô tả độ phân tán; skewness/kurtosis mô tả hình dạng. Tuần 7: histogram, KDE, boxplot và violin plot hỗ trợ so sánh phân phối. KDE làm mượt nên có thể che các đỉnh nhỏ. Cần đối chiếu bảng số liệu và biểu đồ, không chỉ dựa vào mean.

Đây là phân tích mô tả, không chứng minh nguyên nhân. Độ khó đề thi, quy chế và thành phần thí sinh có thể khác giữa hai năm.
