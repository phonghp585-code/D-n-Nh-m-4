# So sánh IQR và Z-score điểm thi THPT 2023-2025

## Mục tiêu
So sánh mức độ phân tán điểm và tỷ lệ điểm ngoại lệ theo từng môn trong ba kỳ thi 2023, 2024 và 2025.

## Chỉ số
- **IQR = Q3 - Q1**: khoảng chứa 50% điểm ở giữa. IQR lớn hơn thể hiện phần trung tâm của phân phối điểm phân tán rộng hơn.
- **Ngoại lệ IQR**: điểm nhỏ hơn Q1 - 1.5×IQR hoặc lớn hơn Q3 + 1.5×IQR.
- **Z-score = (điểm - trung bình)/độ lệch chuẩn**. Báo cáo tỷ lệ có |Z-score| > 3.

IQR và Z-score là công cụ sàng lọc thống kê. Một điểm bị gắn cờ không chứng minh có gian lận; cần kiểm tra dữ liệu, quy chế, bối cảnh địa phương và các bằng chứng độc lập.

## Cách chạy
Cài thư viện:
```bash
pip install pandas numpy matplotlib pyarrow
```

Sau khi đặt đủ ba tệp dữ liệu tại đường dẫn tương ứng:
```bash
python src/phan_tich_iqr_zscore.py --2023 data/processed/week3/exam_2023.parquet --2024 diem_thi_thpt_2024.csv --2025 data/dataset_diem_thi_thpt_2025.csv
```

Kết quả trong `outputs/iqr_zscore/`:
- `bang_so_sanh_iqr_zscore.csv`
- `so_sanh_iqr_2023_2025.png`
- `so_sanh_zscore_2023_2025.png`
- `khoang_tu_phan_vi_2023_2025.png`

## Lưu ý dữ liệu
Tệp 2024 được cung cấp kèm yêu cầu, có các cột môn thi dạng `toan`, `ngu_van`, `ngoai_ngu`, ... Dữ liệu 2023 trong dự án hiện có bản Parquet ở `data/processed/week3/exam_2023.parquet`. Tệp 2025 trong nhánh dữ liệu đang là Git LFS pointer, nên cần checkout/pull Git LFS thành công để có nội dung CSV thật trước khi chạy. Không nên thay thế dữ liệu thí sinh bằng bảng phổ điểm tổng hợp vì không thể tính chính xác IQR/Z-score cấp thí sinh từ bảng tần suất rời rạc.

Script bỏ qua giá trị thiếu và điểm ngoài [0,10]. Tên môn không có trong bộ dữ liệu nào sẽ không xuất hiện trong bảng kết quả.
