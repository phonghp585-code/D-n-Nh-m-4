# Phân tích phổ điểm THPT 2023 và 2025

Phần bổ sung cho dự án Nhóm 4, tiếp nối cấu trúc branch `thanh` và sử dụng nguồn điểm 2023 / 2025 đã có trong repository.

## Chạy
1. Cài Python 3.10+.
2. Cài thư viện: `python -m pip install -r requirements-score-distribution.txt`
3. Đảm bảo Git LFS đã tải dataset 2025: `git lfs pull`
4. Chạy ở thư mục gốc repo:
```bash
python -m src.week6_score_distribution
```

Có thể truyền đường dẫn khác:
```bash
python -m src.week6_score_distribution --2023 data/processed/week3/exam_2023.parquet --2025 data/dataset_diem_thi_thpt_2025.csv --out outputs/score_distribution
```

## Kết quả
- `outputs/score_distribution/bao_cao_phan_tich_pho_diem_2023_2025.docx`: báo cáo Word có bảng và biểu đồ.
- `thong_ke_mo_ta_2023_2025.csv`: trung bình, trung vị, độ lệch chuẩn, skewness, excess kurtosis, tỷ lệ ngưỡng.
- `diem_long_2023_2025.csv`: dữ liệu điểm dạng dài phục vụ phân tích.
- `figures/`: histogram, KDE, boxplot, violin plot cho từng môn.
- `run_metadata.json`: metadata lần chạy.

## Chính sách dữ liệu
Không thay đổi hai dataset nguồn; không điền điểm thiếu; điểm ngoài 0–10 bị loại khỏi thống kê; tỷ lệ được tính trên số điểm hợp lệ của từng môn. So sánh mô tả không đủ để suy ra quan hệ nhân quả. Tên cột được ánh xạ theo alias phổ biến; nếu không nhận diện được, chương trình dừng để tránh âm thầm bỏ môn.
