# Kiểm tra bài Week 6: So sánh phổ điểm THPT 2023–2025

## Phạm vi
- [x] Có mã nguồn tách riêng trong `src/`.
- [x] Có notebook chạy pipeline và xem bảng thống kê.
- [x] Có unit test kiểm tra ánh xạ cột, miền điểm, thống kê và các ngưỡng.
- [x] Có file requirements riêng.
- [x] Có thư mục output và README giải thích các đầu ra.
- [x] Pipeline tạo báo cáo Word `.docx`, CSV thống kê, CSV dạng dài và biểu đồ PNG.
- [x] So sánh histogram, KDE, boxplot, violin plot cho các môn được nhận diện ở cả hai năm.
- [x] Tính mean, median, standard deviation, skewness, excess kurtosis, tỷ lệ ≤1, <5, ≥8, ≥9.
- [x] Không tự điền điểm thiếu; không thay đổi dataset gốc.
- [ ] Chưa xác nhận thực thi end-to-end trong môi trường sạch ở thời điểm commit.
- [ ] Chưa có báo cáo DOCX/PNG/CSV sinh từ dữ liệu thật được commit sẵn; cần chạy pipeline sau khi tải đủ Git LFS và cài dependencies.

## Kiểm tra dữ liệu trước khi chạy
1. Kiểm tra file 2023 tồn tại: `data/processed/week3/exam_2023.parquet`.
2. Dataset 2025 đang được quản lý bằng Git LFS. Chạy `git lfs pull` và xác nhận file không còn là con trỏ văn bản LFS.
3. Nếu tên cột môn khác alias trong mã, cập nhật `SUBJECT_ALIASES` và thêm unit test trước khi chạy.
4. Xác nhận số dòng, cột môn nhận diện, số điểm hợp lệ và file đầu ra trong `run_metadata.json`.

## Lệnh kiểm tra
```bash
python -m pip install -r requirements-score-distribution.txt
python -m unittest tests.test_week6_score_distribution -v
python -m src.week6_score_distribution
```

## Tiêu chí chấp nhận
- Lệnh chạy kết thúc với mã thoát 0.
- Có một dòng thống kê cho mỗi cặp năm–môn có điểm hợp lệ.
- Tỷ lệ phần trăm nằm trong [0,100].
- Mỗi môn có tối đa bốn biểu đồ, đặt trong `outputs/score_distribution/figures/`.
- Báo cáo Word mở được và chứa bảng thống kê cùng hình minh họa.
- Các kết quả có thể tái lập khi dùng cùng dữ liệu và cùng phiên bản thư viện.

## Giới hạn cần nêu trong báo cáo
Đây là phân tích mô tả, không kết luận nguyên nhân làm điểm thay đổi. Tỷ lệ tính trên điểm hợp lệ của từng môn. Thay đổi cấu trúc đề thi, quy chế và thành phần thí sinh có thể ảnh hưởng khả năng so sánh giữa năm.