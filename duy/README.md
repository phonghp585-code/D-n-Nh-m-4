# Phần việc của Duy — tương quan môn thi và PCA

Thư mục này là phần việc độc lập của Duy. Nó chỉ **đọc** dữ liệu và các đầu ra đã có của dự án; không sửa các tệp `src/`, `docs/`, `outputs/` hay notebook của thành viên khác.

## Tệp bàn giao

- `phan_tich_tuong_quan_pca.py`: script tái lập Pearson, Spearman, kiểm tra nhóm điểm cao và PCA.
- `ket_qua.md`: phần viết có thể đưa trực tiếp vào báo cáo/slide.

## Chạy lại

Từ thư mục gốc dự án, sau khi Git LFS đã tải dữ liệu 2025:

```powershell
& ./.venv/Scripts/python.exe duy/phan_tich_tuong_quan_pca.py `
  --data2023 data/raw/original.csv `
  --data2025 data/dataset_diem_thi_thpt_2025.csv `
  --output duy/outputs
```

Script giữ điểm hợp lệ trong [0, 10], giữ điểm 0, không điền ô thiếu. Tương quan được tính trên đúng tập thí sinh có đủ hai môn. PCA được chạy riêng theo các tổ hợp A00, A01, B00, C00 và D01, sau chuẩn hoá z-score trong từng năm/tổ hợp; không gộp tám môn vào một PCA vì không có một mẫu thí sinh chung thi đủ tám môn.
