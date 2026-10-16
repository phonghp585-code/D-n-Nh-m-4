# Kiểm tra bài Week 6–7: So sánh phổ điểm THPT 2023–2025

## Phạm vi triển khai
- [x] Dataset 2023 từ branch `thanh`, dataset 2025 đã hợp mã tỉnh từ branch `nhan`.
- [x] Mã nguồn riêng trong `src/week6_score_distribution.py`.
- [x] Notebook chạy pipeline và đọc bảng kết quả.
- [x] Unit test ánh xạ môn, miền điểm và tỷ lệ ngưỡng.
- [x] Requirements riêng.
- [x] Pipeline sinh báo cáo Word, CSV thống kê, CSV dạng dài, PNG và metadata.
- [x] Histogram, KDE, boxplot, violin plot cho từng môn chung.
- [x] Mean, median, standard deviation, skewness, excess kurtosis.
- [x] Tỷ lệ điểm ≤1, <5, ≥8, ≥9.
- [ ] Chưa chạy end-to-end trên môi trường sạch có đủ dữ liệu Git LFS; output thật cần sinh và kiểm tra sau khi tải dataset.

## Kiểm tra dữ liệu
1. Xác nhận `data/processed/week3/exam_2023.parquet` tồn tại.
2. Chạy `git lfs pull`; dataset 2025 không được còn là con trỏ LFS.
3. Kiểm tra `outputs/score_distribution/run_metadata.json` để xác nhận môn và số điểm hợp lệ.
4. Nếu cần, bổ sung alias cột và unit test.
5. Mở DOCX, kiểm tra bảng, nhãn biểu đồ và số môn khớp CSV.

## Lệnh kiểm tra
```bash
python -m pip install -r requirements-score-distribution.txt
python -m unittest tests.test_week6_score_distribution -v
python -m src.week6_score_distribution
```

## Tiêu chí chấp nhận
- Unit tests pass.
- Có thống kê cho mỗi môn-năm có điểm hợp lệ.
- Tỷ lệ thuộc [0, 100].
- Mỗi môn chung có 4 biểu đồ.
- Báo cáo Word mở được, có bảng và hình.
- Chạy lại cùng dữ liệu tái tạo được kết quả.

## Giới hạn
Không điền điểm thiếu; điểm ngoài [0, 10] bị loại. Mẫu số tỷ lệ là điểm hợp lệ của từng môn-năm. Đây là phân tích mô tả, không chứng minh nhân quả; không nên quy đổi trực tiếp điểm giữa hai cấu trúc đề thi.
