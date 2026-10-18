# 5. Ma trận tương quan giữa các môn và PCA

## Phương pháp

Phân tích sử dụng tám môn cùng tên ở hai năm: Toán, Ngữ văn, Tiếng Anh (chỉ mã N1), Vật lý, Hóa học, Sinh học, Lịch sử và Địa lý. Chỉ giữ điểm hợp lệ từ 0 đến 10, giữ nguyên điểm 0 và không điền các điểm thiếu. Mỗi hệ số Pearson/Spearman được tính trên đúng tập thí sinh có đủ **cả hai** môn đang xét; vì vậy, ô trống ở ma trận 2023 nghĩa là không có hoặc không đủ thí sinh đồng thời có hai điểm, không phải tương quan bằng 0.

Pearson r là chỉ số chính để so sánh quan hệ tuyến tính; Spearman rho được dùng kiểm tra tính nhất quán theo thứ hạng. So sánh 2025 với 2023 là mô tả, không khẳng định thay đổi do riêng đề thi hay chương trình, vì cơ chế chọn môn và thành phần thí sinh khác nhau.

## Ma trận Pearson r năm 2023

| Môn | Toán | Văn | Anh | Lý | Hóa | Sinh | Sử | Địa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Toán | 1.000 | 0.459 | 0.592 | 0.568 | 0.463 | 0.313 | 0.469 | 0.446 |
| Văn | 0.459 | 1.000 | 0.366 | 0.181 | 0.200 | 0.263 | 0.453 | 0.433 |
| Anh | 0.592 | 0.366 | 1.000 | 0.318 | 0.091 | 0.286 | 0.365 | 0.303 |
| Lý | 0.568 | 0.181 | 0.318 | 1.000 | 0.378 | 0.176 | — | — |
| Hóa | 0.463 | 0.200 | 0.091 | 0.378 | 1.000 | 0.407 | — | — |
| Sinh | 0.313 | 0.263 | 0.286 | 0.176 | 0.407 | 1.000 | — | — |
| Sử | 0.469 | 0.453 | 0.365 | — | — | — | 1.000 | 0.608 |
| Địa | 0.446 | 0.433 | 0.303 | — | — | — | 0.608 | 1.000 |

## Ma trận Pearson r năm 2025

| Môn | Toán | Văn | Anh | Lý | Hóa | Sinh | Sử | Địa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Toán | 1.000 | 0.383 | 0.497 | 0.709 | 0.728 | 0.739 | 0.518 | 0.554 |
| Văn | 0.383 | 1.000 | 0.184 | 0.211 | 0.207 | 0.304 | 0.527 | 0.529 |
| Anh | 0.497 | 0.184 | 1.000 | 0.477 | 0.506 | 0.497 | 0.375 | 0.344 |
| Lý | 0.709 | 0.211 | 0.477 | 1.000 | 0.745 | 0.501 | 0.439 | 0.491 |
| Hóa | 0.728 | 0.207 | 0.506 | 0.745 | 1.000 | 0.743 | 0.475 | 0.594 |
| Sinh | 0.739 | 0.304 | 0.497 | 0.501 | 0.743 | 1.000 | 0.483 | 0.641 |
| Sử | 0.518 | 0.527 | 0.375 | 0.439 | 0.475 | 0.483 | 1.000 | 0.759 |
| Địa | 0.554 | 0.529 | 0.344 | 0.491 | 0.594 | 0.641 | 0.759 | 1.000 |

## So sánh và diễn giải

- Cặp đi cùng nhau mạnh nhất theo Pearson ở cả hai năm là **Lịch sử – Địa lý**: 2023 r = 0,608; 2025 r = 0,759. Đây là liên hệ dương mạnh trong tập thí sinh có đủ hai điểm, không phải quan hệ nhân quả.
- Với nhóm tự nhiên, **Toán – Vật lý** tăng từ r = 0,568 lên 0,709. Đồng thời, Lý – Hóa đạt 0,745; Hóa – Sinh đạt 0,743; Toán – Sinh đạt 0,739 trong năm 2025. Cấu trúc điểm khối tự nhiên năm 2025 gắn kết chặt hơn trong các nhóm có điểm quan sát.
- Với ví dụ Văn – Sử, hệ số tăng từ r = 0,453 (2023) lên 0,527 (2025). Tuy nhiên, Ngữ văn không phải môn có liên hệ mạnh nhất với nhóm xã hội: năm 2025, Sử – Địa cao hơn rõ rệt (0,759).
- Các thay đổi lớn cần đọc kèm sự thay đổi cơ chế thi. Năm 2023, nhiều cặp tự nhiên/xã hội không xuất hiện cùng nhau; năm 2025 thí sinh chọn môn, nên quy mô và thành phần mẫu của từng cặp khác nhau.

## Thí sinh giỏi Toán có giỏi Lý không?

Xét trong tập có đủ hai điểm, ngưỡng cao P80 được tính riêng theo từng năm. Năm 2023, xác suất đạt Lý cao khi đã đạt Toán cao là **47,13%**, so với tỷ lệ nền Lý cao **21,32%**. Năm 2025, xác suất này là **60,00%**, cao hơn tỷ lệ nền khoảng **20%**. Kết quả cho thấy điểm cao Toán và Lý thường đồng xuất hiện hơn mức nền, nhưng không cho phép kết luận rằng giỏi Toán gây ra giỏi Lý.

## PCA: các điểm quy về năng lực nào?

PCA được thực hiện riêng trong từng tổ hợp ba môn A00, A01, B00, C00 và D01 sau chuẩn hoá z-score. Cách này phù hợp hơn PCA gộp tám môn vì không tồn tại mẫu chung thi đủ tám môn ở cả hai năm.

| Tổ hợp | PC1 giải thích 2023 | PC1 giải thích 2025 | Diễn giải thận trọng |
| --- | ---: | ---: | --- |
| A00 (Toán–Lý–Hóa) | 64,73% | 81,81% | PC1 có tải dương cao ở cả ba môn; mô tả năng lực chung trong tổ hợp tự nhiên. |
| A01 (Toán–Lý–Anh) | 61,98% | 70,35% | PC1 là trục thành tích chung của ba môn, trong đó Anh tải thấp hơn Toán/Lý. |
| B00 (Toán–Hóa–Sinh) | 59,64% | 82,74% | PC1 tăng mạnh; ba môn cùng đóng góp lớn vào trục chung của nhóm B00. |
| C00 (Văn–Sử–Địa) | 66,68% | 74,59% | PC1 mô tả thành tích chung nhóm xã hội; Sử và Địa có tải rất cao. |
| D01 (Toán–Văn–Anh) | 63,54% | 54,13% | PC1 yếu hơn năm 2025, cho thấy D01 kém một chiều hơn; Văn có tải PC1 thấp hơn Toán/Anh. |

Không nên gọi các PC là “năng lực bẩm sinh” hay dùng chúng để xếp loại cá nhân. Chúng chỉ là các trục thống kê tóm tắt biến thiên điểm trong đúng tổ hợp và năm đang xét.

## Lưu ý về độ phân hoá đề

Tương quan giữa các môn **không đo trực tiếp độ phân hoá của đề**. Một đề có phân hoá tốt cần dữ liệu theo câu hỏi (tỷ lệ đúng, tương quan điểm-câu, đường đặc trưng câu hỏi hoặc IRT). Từ dữ liệu tổng điểm, báo cáo chỉ có thể nói rằng Toán–Lý liên hệ mạnh hơn ở 2025 và nhóm A00/B00 có PC1 giải thích tỷ lệ biến thiên lớn hơn; không được suy ra chỉ từ đó rằng đề năm nào phân hoá tốt hơn.
