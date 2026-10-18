# Phân tích tương quan và PCA

Đây là phần phân tích điểm thi THPT năm 2023 và 2025:

Nội dung gồm:
- Tính ma trận tương quan Pearson và Spearman giữa các môn thi.
- Kiểm tra mối liên hệ giữa các môn và nhóm học sinh có điểm cao.
- Sử dụng PCA để tìm hiểu cấu trúc điểm thi theo một số tổ hợp môn.

## Cách chạy

Mở Terminal tại thư mục gốc của dự án và chạy:

```powershell
& ./.venv/Scripts/python.exe duy/phan_tich_tuong_quan_pca.py --data2023 data/raw/original.csv --data2025 data/dataset_diem_thi_thpt_2025.csv --output duy/outputs
```

## Lưu ý

- Dữ liệu được giữ trong khoảng điểm từ 0 đến 10, bao gồm cả điểm 0.
- Các ô thiếu dữ liệu không được tự động điền.
- Phân tích PCA được thực hiện riêng theo từng tổ hợp môn và từng năm.
- Kết quả được lưu trong thư mục `duy/outputs`.
