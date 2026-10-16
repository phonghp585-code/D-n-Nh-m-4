# Báo cáo phân tích và so sánh phổ điểm thi THPT năm 2023 và 2025

> **Phạm vi dữ liệu:** Báo cáo này được tổng hợp từ bảng phân phối điểm theo môn/năm công khai của [NhanAZ-Data/diem-thi-thpt-cac-nam](https://github.com/NhanAZ-Data/diem-thi-thpt-cac-nam), tệp `data/summary/subject_score_distribution.csv`. Đây là dữ liệu tổng hợp theo mức điểm, **không phải kết quả được tính trực tiếp từ hai tệp dữ liệu gốc của Nhóm 4**. Vì vậy, cần thay thế hoặc xác nhận lại các con số bằng pipeline của dự án trước khi xem đây là kết quả chính thức của nhóm.

## 1. Mục tiêu

So sánh phổ điểm của các môn có dữ liệu ở cả hai năm 2023 và 2025 thông qua:

- Thống kê mô tả: số điểm hợp lệ, trung bình, trung vị, độ lệch chuẩn, skewness và excess kurtosis.
- Tỷ lệ điểm không quá 1, dưới 5, từ 8 trở lên và từ 9 trở lên.
- Nhận xét về dịch chuyển vị trí trung tâm, độ phân tán và hình dạng phân phối.
- Đối chiếu kết quả giữa các chỉ số thay vì kết luận dựa trên một con số riêng lẻ.

Phân tích có tính **mô tả**, không nhằm chứng minh đề thi dễ/khó hơn hoặc xác định nguyên nhân tạo ra chênh lệch.

## 2. Nguồn dữ liệu và cách tính

Nguồn tổng hợp ghi nhận số lượng điểm theo môn, năm và mức điểm. Các thống kê được tính có trọng số theo số lượng quan sát tại từng mức điểm.

- Chỉ so sánh trực tiếp các môn xuất hiện ở cả hai năm.
- Tỷ lệ ở mỗi ngưỡng được tính trên tổng số điểm hợp lệ của chính môn và năm đó.
- Chênh lệch được tính theo quy ước **2025 trừ 2023**.
- Các thay đổi của tỷ lệ được diễn giải bằng **điểm phần trăm (đpt)**.
- Skewness âm thường gợi ý đuôi trái dài hơn; skewness dương thường gợi ý đuôi phải dài hơn.
- Excess kurtosis được diễn giải cùng biểu đồ, không dùng riêng lẻ để kết luận phân phối chuẩn.

### Lưu ý về biểu đồ

Các biểu đồ histogram, KDE, boxplot và violin plot trong bản DOCX đi kèm được tái dựng từ bảng tần số theo các mức điểm 0,5. Vì vậy, hình dạng biểu đồ là **xấp xỉ từ dữ liệu phân nhóm**, không hoàn toàn tương đương biểu đồ dựng trực tiếp từ từng điểm thi gốc.

## 3. Thống kê mô tả

| Môn | N 2023 | N 2025 | Trung bình 2023 | Trung bình 2025 | Trung vị 2023 | Trung vị 2025 | ĐLC 2023 | ĐLC 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Địa lý | 682.134 | 489.581 | 6,148 | 6,643 | 6,25 | 6,75 | 1,169 | 1,750 |
| GDCD* | 565.452 | 4.099 | 8,286 | 7,698 | 8,50 | 8,00 | 1,138 | 1,532 |
| Hóa học | 328.118 | 244.283 | 6,745 | 6,070 | 7,00 | 6,00 | 1,428 | 1,812 |
| Lịch sử | 683.447 | 495.165 | 6,026 | 6,515 | 6,00 | 6,50 | 1,553 | 1,644 |
| Ngoại ngữ | 880.997 | 362.975 | 5,462 | 5,406 | 5,20 | 5,25 | 1,966 | 1,488 |
| Ngữ văn | 1.008.239 | 1.144.098 | 6,858 | 6,990 | 7,00 | 7,25 | 1,326 | 1,291 |
| Sinh học | 324.625 | 71.616 | 6,395 | 5,781 | 6,50 | 5,75 | 1,207 | 1,594 |
| Toán | 1.003.373 | 1.137.417 | 6,251 | 4,800 | 6,60 | 4,60 | 1,633 | 1,689 |
| Vật lý | 327.189 | 351.733 | 6,574 | 6,978 | 6,75 | 7,00 | 1,487 | 1,522 |

*ĐLC: độ lệch chuẩn. N là số điểm được ghi nhận trong bảng tần số nguồn.*

### Độ lệch và độ nhọn

| Môn | Skewness 2023 | Skewness 2025 | Excess kurtosis 2023 | Excess kurtosis 2025 |
|---|---:|---:|---:|---:|
| Địa lý | -0,153 | -0,158 | 0,252 | -0,690 |
| GDCD* | -0,974 | -1,298 | 1,223 | 2,607 |
| Hóa học | -0,629 | 0,092 | 0,050 | -0,797 |
| Lịch sử | 0,029 | -0,187 | -0,552 | -0,650 |
| Ngoại ngữ | 0,305 | 0,312 | -0,856 | -0,076 |
| Ngữ văn | -0,535 | -0,784 | 0,250 | 0,762 |
| Sinh học | -0,182 | 0,123 | 0,160 | -0,534 |
| Toán | -0,596 | 0,394 | -0,402 | -0,309 |
| Vật lý | -0,451 | -0,220 | -0,378 | -0,544 |

## 4. Tỷ lệ điểm theo ngưỡng

Các giá trị trong bảng là phần trăm (%). Chênh lệch ở cột cuối được tính bằng tỷ lệ năm 2025 trừ tỷ lệ năm 2023, đơn vị điểm phần trăm.

| Môn | Năm | ≤ 1 | < 5 | ≥ 8 | ≥ 9 |
|---|---:|---:|---:|---:|---:|
| Địa lý | 2023 | 0,02% | 13,35% | 6,64% | 0,87% |
| Địa lý | 2025 | 0,01% | 18,47% | 27,03% | 11,39% |
| GDCD* | 2023 | 0,00% | 0,97% | 68,95% | 35,45% |
| GDCD* | 2025 | 0,34% | 5,17% | 52,33% | 23,86% |
| Hóa học | 2023 | 0,00% | 11,70% | 22,67% | 3,42% |
| Hóa học | 2025 | 0,00% | 29,44% | 19,37% | 7,40% |
| Lịch sử | 2023 | 0,01% | 24,91% | 13,07% | 3,06% |
| Lịch sử | 2025 | 0,00% | 18,85% | 23,15% | 7,03% |
| Ngoại ngữ | 2023 | 0,02% | 44,69% | 15,18% | 5,38% |
| Ngoại ngữ | 2025 | 0,01% | 37,88% | 6,12% | 1,80% |
| Ngữ văn | 2023 | 0,01% | 7,31% | 24,42% | 4,30% |
| Ngữ văn | 2025 | 0,01% | 6,47% | 26,60% | 3,92% |
| Sinh học | 2023 | 0,01% | 10,40% | 10,57% | 1,68% |
| Sinh học | 2025 | 0,02% | 32,43% | 11,04% | 2,58% |
| Toán | 2023 | 0,01% | 21,64% | 15,16% | 1,00% |
| Toán | 2025 | 0,07% | 56,06% | 5,67% | 1,44% |
| Vật lý | 2023 | 0,01% | 14,79% | 21,32% | 2,97% |
| Vật lý | 2025 | 0,00% | 9,91% | 30,68% | 11,45% |

## 5. So sánh từng môn

### 5.1. Toán

- Điểm trung bình giảm từ **6,251 xuống 4,800**, trung vị giảm từ **6,60 xuống 4,60**.
- Tỷ lệ dưới 5 tăng từ **21,64% lên 56,06%**, tăng 34,42 điểm phần trăm.
- Tỷ lệ từ 8 trở lên giảm từ **15,16% xuống 5,67%**, giảm 9,49 điểm phần trăm.
- Độ lệch chuyển từ âm (-0,596) sang dương (0,394), cho thấy hình dạng phân phối thay đổi đáng kể.

**Kết luận mô tả:** Có sự dịch chuyển rõ rệt về phía điểm thấp trong phân phối Toán năm 2025 so với 2023 theo các chỉ số đang xét. Những số liệu này không tự xác định nguyên nhân của thay đổi.

### 5.2. Hóa học

- Trung bình giảm từ **6,745 xuống 6,070**; trung vị giảm từ 7 xuống 6.
- Tỷ lệ dưới 5 tăng từ **11,70% lên 29,44%**, tăng 17,74 điểm phần trăm.
- Tỷ lệ từ 8 trở lên giảm từ 22,67% xuống 19,37%, trong khi tỷ lệ từ 9 trở lên tăng từ 3,42% lên 7,40%.
- Độ lệch chuyển từ -0,629 sang 0,092.

**Kết luận mô tả:** Phân phối Hóa học có dấu hiệu dịch xuống ở trung tâm và tăng độ phân tán. Các tỷ lệ nhóm điểm cao không hoàn toàn cùng chiều, nên cần xem biểu đồ và các ngưỡng riêng biệt thay vì nói mọi mức điểm cao đều tăng hoặc giảm.

### 5.3. Sinh học

- Trung bình giảm từ **6,395 xuống 5,781**; trung vị giảm từ 6,50 xuống 5,75.
- Tỷ lệ dưới 5 tăng từ **10,40% lên 32,43%**, tăng 22,03 điểm phần trăm.
- Độ lệch chuẩn tăng từ 1,207 lên 1,594.
- Tỷ lệ từ 8 trở lên thay đổi nhẹ, từ 10,57% lên 11,04%; tỷ lệ từ 9 trở lên tăng từ 1,68% lên 2,58%.

**Kết luận mô tả:** Trung tâm phân phối Sinh học dịch xuống và độ phân tán tăng. Cỡ mẫu năm 2025 nhỏ hơn đáng kể năm 2023, vì vậy cần lưu ý sự khác biệt về số lượng quan sát và cơ cấu thí sinh.

### 5.4. Địa lý

- Trung bình tăng từ **6,148 lên 6,643**; trung vị tăng từ 6,25 lên 6,75.
- Tỷ lệ từ 8 trở lên tăng từ **6,64% lên 27,03%**; tỷ lệ từ 9 trở lên tăng từ 0,87% lên 11,39%.
- Tỷ lệ dưới 5 cũng tăng từ 13,35% lên 18,47%.
- Độ lệch chuẩn tăng từ 1,169 lên 1,750.

**Kết luận mô tả:** Điểm trung tâm và tỷ lệ ở nhóm điểm cao của Địa lý tăng, đồng thời độ phân tán lớn hơn và tỷ lệ dưới 5 cũng tăng. Điều này cho thấy phân phối không chỉ dịch chuyển đồng đều mà có sự thay đổi về độ rộng.

### 5.5. Lịch sử

- Trung bình tăng từ **6,026 lên 6,515**; trung vị tăng từ 6 lên 6,50.
- Tỷ lệ dưới 5 giảm từ 24,91% xuống 18,85%.
- Tỷ lệ từ 8 trở lên tăng từ 13,07% lên 23,15%; tỷ lệ từ 9 trở lên tăng từ 3,06% lên 7,03%.
- Độ lệch chuyển từ 0,029 sang -0,187.

**Kết luận mô tả:** Phổ điểm Lịch sử dịch lên theo trung bình, trung vị và các tỷ lệ nhóm điểm cao; tỷ lệ dưới 5 giảm. Độ phân tán tăng nhẹ theo độ lệch chuẩn, từ 1,553 lên 1,644.

### 5.6. Vật lý

- Trung bình tăng từ **6,574 lên 6,978**; trung vị tăng từ 6,75 lên 7.
- Tỷ lệ dưới 5 giảm từ 14,79% xuống 9,91%.
- Tỷ lệ từ 8 trở lên tăng từ 21,32% lên 30,68%; tỷ lệ từ 9 trở lên tăng từ 2,97% lên 11,45%.
- Độ lệch chuẩn tăng nhẹ từ 1,487 lên 1,522.

**Kết luận mô tả:** Các chỉ số trung tâm và tỷ lệ theo ngưỡng của Vật lý cho thấy phổ điểm dịch lên. Độ phân tán tăng nhẹ, vì vậy không nên mô tả thay đổi chỉ bằng trung bình.

### 5.7. Ngữ văn

- Trung bình tăng nhẹ từ **6,858 lên 6,990**; trung vị tăng từ 7 lên 7,25.
- Tỷ lệ dưới 5 giảm từ 7,31% xuống 6,47%.
- Tỷ lệ từ 8 trở lên tăng từ 24,42% lên 26,60%, nhưng tỷ lệ từ 9 trở lên giảm từ 4,30% xuống 3,92%.
- Độ lệch chuẩn giảm từ 1,326 xuống 1,291; skewness âm hơn, từ -0,535 xuống -0,784.

**Kết luận mô tả:** Ngữ văn có dịch chuyển tăng nhẹ ở trung tâm và giảm nhẹ độ phân tán. Tuy nhiên, nhóm từ 8 trở lên và nhóm từ 9 trở lên thay đổi khác chiều, cho thấy không thể kết luận rằng mọi phần của phân phối đều dịch lên.

### 5.8. Ngoại ngữ

- Trung bình gần như ổn định, giảm từ **5,462 xuống 5,406**; trung vị tăng nhẹ từ 5,20 lên 5,25.
- Tỷ lệ dưới 5 giảm từ 44,69% xuống 37,88%.
- Tỷ lệ từ 8 trở lên giảm từ 15,18% xuống 6,12%; tỷ lệ từ 9 trở lên giảm từ 5,38% xuống 1,80%.
- Độ lệch chuẩn giảm từ 1,966 xuống 1,488.

**Kết luận mô tả:** Ngoại ngữ có trung tâm gần như ổn định nhưng độ phân tán thu hẹp. Tỷ lệ dưới 5 giảm trong khi tỷ lệ ở nhóm điểm cao cũng giảm, gợi ý sự thay đổi hình dạng phân phối chứ không phải một dịch chuyển đơn giản theo một hướng.

### 5.9. Giáo dục công dân (GDCD)*

- Trung bình giảm từ 8,286 xuống 7,698; trung vị giảm từ 8,50 xuống 8.
- Tỷ lệ từ 8 trở lên giảm từ 68,95% xuống 52,33%; tỷ lệ từ 9 trở lên giảm từ 35,45% xuống 23,86%.
- Số điểm năm 2025 chỉ là **4.099**, so với **565.452** năm 2023.

**Kết luận:** Không nên dùng GDCD để đưa ra kết luận so sánh hai năm một cách trực tiếp. Cỡ mẫu 2025 nhỏ bất thường so với 2023 và cấu trúc môn thi có thể đã thay đổi; cần kiểm tra định nghĩa môn và nguồn dữ liệu. GDCD không được xem là tương đương với môn Giáo dục kinh tế và pháp luật chỉ vì có liên quan về lĩnh vực.

## 6. Tổng hợp phát hiện chính

1. **Toán** có mức giảm rõ nhất trong các chỉ số trung tâm: trung bình giảm 1,451 điểm và tỷ lệ dưới 5 tăng 34,42 điểm phần trăm.
2. **Hóa học và Sinh học** cũng giảm điểm trung tâm, đồng thời tỷ lệ dưới 5 và độ lệch chuẩn tăng.
3. **Địa lý, Lịch sử và Vật lý** tăng trung bình, trung vị và tỷ lệ từ 8 trở lên. Riêng Địa lý có độ phân tán tăng đáng kể.
4. **Ngữ văn** tương đối ổn định, trung bình tăng nhẹ và độ lệch chuẩn giảm nhẹ.
5. **Ngoại ngữ** có trung bình gần như không đổi nhưng tỷ lệ từ 8 trở lên giảm rõ và độ phân tán thu hẹp.
6. **GDCD** có vấn đề về khả năng so sánh do cỡ mẫu năm 2025 rất nhỏ; cần loại khỏi kết luận so sánh trực tiếp cho tới khi xác minh dữ liệu.

## 7. Giới hạn và cách diễn giải

- Nguồn sử dụng là bảng tần số tổng hợp công khai, không phải hai tệp dữ liệu gốc của Nhóm 4. Các con số trong báo cáo cần được chạy lại hoặc xác nhận trên dữ liệu chính thức của dự án.
- Biểu đồ dựng từ các mức điểm theo bước 0,5 là gần đúng; không thể hiện mọi đặc điểm có thể thấy từ điểm cá thể.
- Khác biệt giữa năm 2023 và 2025 không chứng minh đề thi dễ hoặc khó hơn, cũng không tự chứng minh năng lực thí sinh thay đổi.
- Cơ cấu thí sinh, số lượng người dự thi, lựa chọn môn và quy chế có thể khác nhau giữa hai năm.
- Không suy diễn nguyên nhân từ skewness, kurtosis hoặc một biểu đồ riêng lẻ.
- Cần kiểm tra tính tương đương của môn thi trước khi so sánh trực tiếp, đặc biệt với GDCD và Giáo dục kinh tế và pháp luật.

## 8. Kết luận

Phân tích cho thấy phổ điểm giữa năm 2023 và 2025 thay đổi theo những cách khác nhau tùy môn. Toán, Hóa học và Sinh học có các chỉ số trung tâm giảm; Địa lý, Lịch sử và Vật lý có các chỉ số trung tâm tăng; Ngữ văn tương đối ổn định; Ngoại ngữ có trung bình gần như không đổi nhưng phân phối thu hẹp và tỷ lệ điểm cao giảm. GDCD cần được xem xét riêng do vấn đề cỡ mẫu và khả năng tương đương giữa hai năm.

Kết luận cuối cùng của Nhóm 4 cần được xác nhận bằng cách chạy pipeline trên hai bộ dữ liệu gốc đã chuẩn hóa của dự án. Không nên trình bày các số liệu từ nguồn tổng hợp này như thể chúng đã được tính trực tiếp từ hai tệp dữ liệu nội bộ.

## 9. Nguồn tham khảo

- Bảng phân phối điểm công khai: [NhanAZ-Data/diem-thi-thpt-cac-nam](https://github.com/NhanAZ-Data/diem-thi-thpt-cac-nam)
- Tài liệu phương pháp của dự án: [`docs/week6/week6_report+bao_cao.md`](./week6_report%2Bbao_cao.md)
- Mã phân tích của dự án: [`src/week6_score_distribution.py`](../../src/week6_score_distribution.py)
