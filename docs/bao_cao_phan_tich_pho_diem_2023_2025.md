# Báo cáo phân tích mô tả và so sánh phổ điểm thi THPT năm 2023 và 2025

> **Trạng thái số liệu:** Bản báo cáo này là bản phân tích tham chiếu dựa trên bảng phân phối điểm công khai của [NhanAZ-Data/diem-thi-thpt-cac-nam](https://github.com/NhanAZ-Data/diem-thi-thpt-cac-nam), tệp `data/summary/subject_score_distribution.csv`. Các con số dưới đây **chưa được xác nhận là tính trực tiếp từ hai tệp dữ liệu gốc đã hợp mã tỉnh của Nhóm 4**. Cần chạy lại pipeline trên dữ liệu của dự án trước khi dùng làm kết quả chính thức.

## 1. Mục tiêu và câu hỏi phân tích

Phần này bổ sung cho phân tích theo tổ hợp môn, tập trung vào phân phối điểm của từng môn thi có thể đối chiếu giữa năm 2023 và 2025.

Các câu hỏi chính:

1. Điểm trung bình, trung vị và độ phân tán của từng môn thay đổi như thế nào?
2. Hình dạng phân phối thay đổi ra sao qua skewness, excess kurtosis và biểu đồ phân phối?
3. Tỷ lệ điểm ở các ngưỡng quan trọng (≤ 1, < 5, ≥ 8, ≥ 9) thay đổi bao nhiêu?
4. Có thể mô tả phổ điểm năm 2025 là dịch chuyển lên, dịch chuyển xuống hay thay đổi hình dạng không đồng nhất?
5. Những giới hạn nào cần lưu ý trước khi giải thích sự khác biệt giữa hai năm?

Đây là phân tích mô tả. Chênh lệch điểm không tự chứng minh đề thi dễ/khó hơn, năng lực thí sinh tăng/giảm hay có gian lận.

## 2. Dữ liệu, phạm vi và phương pháp

### 2.1. Phạm vi so sánh

Bảng tổng hợp nguồn có chín dòng môn có thể đối chiếu sơ bộ: Địa lý, GDCD, Hóa học, Lịch sử, Ngoại ngữ, Ngữ văn, Sinh học, Toán và Vật lý. Tuy nhiên, **GDCD năm 2023 không mặc nhiên tương đương với Giáo dục kinh tế và pháp luật năm 2025**; môn này cần được xem xét riêng.

Trong pipeline dữ liệu gốc của Nhóm 4, chỉ nên so sánh các môn có trường điểm cá nhân tương ứng ở cả hai năm. Không so sánh điểm tổng hợp tổ hợp với điểm một môn. Điểm thiếu cần giữ là thiếu, không tự động thay bằng 0.

### 2.2. Chỉ số sử dụng

- **N hợp lệ:** số điểm có giá trị dùng được cho môn và năm đó.
- **Trung bình:** mức điểm trung bình của các quan sát.
- **Trung vị:** điểm ở giữa phân phối, ít nhạy với các giá trị cực đoan hơn trung bình.
- **Độ lệch chuẩn (ĐLC):** mức độ phân tán quanh trung bình.
- **Skewness:** giá trị âm thường gợi ý đuôi trái dài hơn; giá trị dương thường gợi ý đuôi phải dài hơn.
- **Excess kurtosis:** mô tả độ nhọn/đuôi so với phân phối chuẩn; cần đọc cùng biểu đồ, không kết luận chỉ bằng chỉ số này.
- **Tỷ lệ ≤ 1, < 5, ≥ 8, ≥ 9:** mẫu số là số điểm hợp lệ của chính môn và năm đó.
- **Chênh lệch:** quy ước lấy năm 2025 trừ năm 2023. Với tỷ lệ, chênh lệch được biểu diễn bằng điểm phần trăm (đpt).

### 2.3. Lưu ý về biểu đồ

Histogram, KDE, boxplot và violin plot là các góc nhìn bổ trợ: histogram thể hiện tần suất theo khoảng; KDE làm mượt hình dạng; boxplot tóm tắt trung vị, tứ phân vị và ngoại lệ; violin plot thể hiện mật độ theo vùng điểm. Nếu dựng biểu đồ từ bảng tần số theo mức điểm 0,5 thì hình dạng chỉ là **xấp xỉ từ dữ liệu phân nhóm**, không tương đương hoàn toàn với biểu đồ tính từ từng điểm thi cá thể.

## 3. Thống kê mô tả theo môn

Bảng dưới đây trình bày số quan sát và các chỉ số trung tâm/độ phân tán. N là số điểm được ghi nhận trong bảng tần số nguồn.

| Môn | N 2023 | N 2025 | TB 2023 | TB 2025 | Trung vị 2023 | Trung vị 2025 | ĐLC 2023 | ĐLC 2025 |
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

* GDCD cần thận trọng khi đối chiếu với môn Giáo dục kinh tế và pháp luật năm 2025.

### 3.1. Độ lệch và độ nhọn

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

**Cách đọc:** Toán đổi từ skewness âm sang dương; Hóa học và Sinh học cũng chuyển từ âm sang gần 0/dương. Điều này cho thấy hình dạng phân phối có thể thay đổi chứ không chỉ thay đổi vị trí trung tâm. Với các môn khác, cần kết hợp cả trung bình, trung vị, độ lệch chuẩn, các tỷ lệ theo ngưỡng và biểu đồ.

## 4. Tỷ lệ điểm theo ngưỡng

Tất cả giá trị là phần trăm. Mỗi tỷ lệ dùng số điểm hợp lệ của môn/năm tương ứng làm mẫu số.

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

## 5. Phân tích chi tiết từng môn

### 5.1. Toán

- **Vị trí trung tâm:** trung bình giảm từ 6,251 xuống 4,800, chênh lệch -1,451 điểm; trung vị giảm từ 6,60 xuống 4,60, chênh lệch -2,00 điểm.
- **Độ phân tán:** ĐLC tăng nhẹ từ 1,633 lên 1,689, cho thấy điểm phân tán rộng hơn một chút theo chỉ số này.
- **Các ngưỡng:** tỷ lệ < 5 tăng từ 21,64% lên 56,06% (+34,42 đpt); tỷ lệ ≥ 8 giảm từ 15,16% xuống 5,67% (-9,49 đpt); tỷ lệ ≥ 9 tăng nhẹ từ 1,00% lên 1,44%.
- **Hình dạng:** skewness đổi từ -0,596 sang 0,394, cho thấy phân phối có hình dạng khác đáng kể giữa hai năm.

**Kết luận mô tả:** Các chỉ số trung tâm và tỷ lệ dưới 5 cho thấy phân phối điểm Toán năm 2025 dịch về phía điểm thấp so với năm 2023. Tuy nhiên, tỷ lệ ≥ 9 tăng nhẹ, nên không nên diễn giải rằng mọi vùng điểm đều dịch chuyển theo cùng một hướng.

### 5.2. Hóa học

- **Vị trí trung tâm:** trung bình giảm 6,745 → 6,070 (-0,675 điểm); trung vị giảm 7,00 → 6,00.
- **Độ phân tán:** ĐLC tăng 1,428 → 1,812, thể hiện độ phân tán lớn hơn.
- **Các ngưỡng:** tỷ lệ < 5 tăng 11,70% → 29,44% (+17,74 đpt); tỷ lệ ≥ 8 giảm 22,67% → 19,37% (-3,30 đpt); tỷ lệ ≥ 9 tăng 3,42% → 7,40% (+3,98 đpt).
- **Hình dạng:** skewness chuyển từ -0,629 sang 0,092; excess kurtosis giảm 0,050 → -0,797.

**Kết luận mô tả:** Trung tâm phân phối Hóa học giảm và độ phân tán tăng. Tỷ lệ ≥ 8 và ≥ 9 biến động trái chiều, nên cần đọc riêng từng ngưỡng thay vì gộp mọi mức điểm cao thành một nhóm.

### 5.3. Sinh học

- **Vị trí trung tâm:** trung bình giảm 6,395 → 5,781 (-0,614 điểm); trung vị giảm 6,50 → 5,75.
- **Độ phân tán:** ĐLC tăng 1,207 → 1,594.
- **Các ngưỡng:** tỷ lệ < 5 tăng 10,40% → 32,43% (+22,03 đpt); tỷ lệ ≥ 8 thay đổi 10,57% → 11,04%; tỷ lệ ≥ 9 tăng 1,68% → 2,58%.
- **Hình dạng:** skewness chuyển từ -0,182 sang 0,123.
- **Quy mô quan sát:** N giảm từ 324.625 xuống 71.616 trong bảng nguồn.

**Kết luận mô tả:** Điểm trung tâm Sinh học giảm và độ phân tán tăng; tỷ lệ dưới 5 tăng mạnh. Năm 2025 có ít quan sát hơn nhiều, vì vậy cơ cấu người dự thi có thể khác và cần được xem xét trước khi diễn giải.

### 5.4. Địa lý

- **Vị trí trung tâm:** trung bình tăng 6,148 → 6,643 (+0,495 điểm); trung vị tăng 6,25 → 6,75.
- **Độ phân tán:** ĐLC tăng 1,169 → 1,750.
- **Các ngưỡng:** tỷ lệ ≥ 8 tăng 6,64% → 27,03% (+20,39 đpt); tỷ lệ ≥ 9 tăng 0,87% → 11,39% (+10,52 đpt). Đồng thời, tỷ lệ < 5 cũng tăng 13,35% → 18,47% (+5,12 đpt).
- **Hình dạng:** skewness gần như ổn định (-0,153 → -0,158), nhưng excess kurtosis giảm 0,252 → -0,690.

**Kết luận mô tả:** Điểm trung tâm và nhóm điểm cao của Địa lý tăng, nhưng nhóm dưới 5 cũng tăng và độ phân tán mở rộng. Vì vậy, đây không phải là sự dịch chuyển đồng đều của toàn bộ phân phối.

### 5.5. Lịch sử

- **Vị trí trung tâm:** trung bình tăng 6,026 → 6,515 (+0,489 điểm); trung vị tăng 6,00 → 6,50.
- **Độ phân tán:** ĐLC tăng 1,553 → 1,644.
- **Các ngưỡng:** tỷ lệ < 5 giảm 24,91% → 18,85% (-6,06 đpt); tỷ lệ ≥ 8 tăng 13,07% → 23,15% (+10,08 đpt); tỷ lệ ≥ 9 tăng 3,06% → 7,03% (+3,97 đpt).
- **Hình dạng:** skewness giảm 0,029 → -0,187.

**Kết luận mô tả:** Các chỉ số trung tâm và nhóm điểm cao của Lịch sử tăng, trong khi tỷ lệ dưới 5 giảm. ĐLC tăng nhẹ, nên vẫn có biến động về độ rộng phân phối chứ không chỉ thay đổi điểm trung bình.

### 5.6. Vật lý

- **Vị trí trung tâm:** trung bình tăng 6,574 → 6,978 (+0,404 điểm); trung vị tăng 6,75 → 7,00.
- **Độ phân tán:** ĐLC tăng nhẹ 1,487 → 1,522.
- **Các ngưỡng:** tỷ lệ < 5 giảm 14,79% → 9,91% (-4,88 đpt); tỷ lệ ≥ 8 tăng 21,32% → 30,68% (+9,36 đpt); tỷ lệ ≥ 9 tăng 2,97% → 11,45% (+8,48 đpt).
- **Hình dạng:** skewness âm hơn ít hơn, từ -0,451 lên -0,220; excess kurtosis giảm -0,378 → -0,544.

**Kết luận mô tả:** Phổ điểm Vật lý dịch lên theo trung bình, trung vị và các tỷ lệ theo ngưỡng; tỷ lệ dưới 5 giảm. Độ phân tán tăng nhẹ, vì vậy nên trình bày cả trung tâm lẫn độ rộng phân phối.

### 5.7. Ngữ văn

- **Vị trí trung tâm:** trung bình tăng nhẹ 6,858 → 6,990 (+0,132 điểm); trung vị tăng 7,00 → 7,25.
- **Độ phân tán:** ĐLC giảm 1,326 → 1,291.
- **Các ngưỡng:** tỷ lệ < 5 giảm 7,31% → 6,47% (-0,84 đpt); tỷ lệ ≥ 8 tăng 24,42% → 26,60% (+2,18 đpt); tỷ lệ ≥ 9 giảm 4,30% → 3,92% (-0,38 đpt).
- **Hình dạng:** skewness âm hơn (-0,535 → -0,784), excess kurtosis tăng 0,250 → 0,762.

**Kết luận mô tả:** Ngữ văn tương đối ổn định ở vùng trung tâm và có độ phân tán giảm nhẹ. Nhóm ≥ 8 tăng nhưng nhóm ≥ 9 giảm, cho thấy các phần khác nhau của phân phối không nhất thiết cùng chiều.

### 5.8. Ngoại ngữ

- **Vị trí trung tâm:** trung bình gần như ổn định, giảm 5,462 → 5,406 (-0,056 điểm); trung vị tăng nhẹ 5,20 → 5,25.
- **Độ phân tán:** ĐLC giảm 1,966 → 1,488.
- **Các ngưỡng:** tỷ lệ < 5 giảm 44,69% → 37,88% (-6,81 đpt); tỷ lệ ≥ 8 giảm 15,18% → 6,12% (-9,06 đpt); tỷ lệ ≥ 9 giảm 5,38% → 1,80% (-3,58 đpt).
- **Hình dạng:** skewness dương gần như không đổi (0,305 → 0,312); excess kurtosis tăng -0,856 → -0,076.

**Kết luận mô tả:** Trung tâm Ngoại ngữ gần như ổn định nhưng phân phối thu hẹp. Tỷ lệ dưới 5 giảm đồng thời với tỷ lệ điểm cao giảm; vì vậy thay đổi có vẻ liên quan đến hình dạng/cơ cấu phân phối hơn là một dịch chuyển đơn giản lên hoặc xuống.

### 5.9. Giáo dục công dân (GDCD)*

- **Vị trí trung tâm:** trung bình giảm 8,286 → 7,698 (-0,588 điểm); trung vị giảm 8,50 → 8,00.
- **Độ phân tán:** ĐLC tăng 1,138 → 1,532.
- **Các ngưỡng:** tỷ lệ ≥ 8 giảm 68,95% → 52,33%; tỷ lệ ≥ 9 giảm 35,45% → 23,86%; tỷ lệ < 5 tăng 0,97% → 5,17%.
- **Cỡ mẫu:** N năm 2025 chỉ 4.099, so với 565.452 năm 2023.

**Kết luận:** Không nên đưa GDCD vào kết luận so sánh trực tiếp cho đến khi xác minh tên/định nghĩa môn và nguồn dữ liệu. GDCD năm 2023 không được xem là tương đương với Giáo dục kinh tế và pháp luật năm 2025 chỉ vì hai môn có liên quan về lĩnh vực.

## 6. Tổng hợp và so sánh xu hướng giữa các môn

1. **Nhóm có trung bình giảm:** Toán (-1,451 điểm), Hóa học (-0,675) và Sinh học (-0,614). Cả ba đều có tỷ lệ < 5 tăng; Sinh học và Hóa học có độ phân tán tăng rõ hơn.
2. **Nhóm có trung bình tăng:** Địa lý (+0,495), Lịch sử (+0,489), Vật lý (+0,404) và Ngữ văn (+0,132). Trong nhóm này, Địa lý có độ phân tán tăng mạnh và tỷ lệ dưới 5 cũng tăng; Lịch sử và Vật lý có xu hướng nhất quán hơn giữa các chỉ số trung tâm và tỷ lệ điểm.
3. **Ngoại ngữ:** trung bình gần như không đổi (-0,056 điểm), nhưng ĐLC và tỷ lệ ≥ 8/≥ 9 giảm. Chỉ xem trung bình sẽ bỏ sót thay đổi này.
4. **GDCD:** cỡ mẫu năm 2025 nhỏ bất thường, nên cần xác minh trước khi so sánh.
5. **Không có một xu hướng duy nhất cho mọi môn:** các môn thay đổi khác nhau về trung tâm, độ phân tán và phần đuôi phân phối.

## 7. Đọc biểu đồ phân phối như thế nào?

Khi bổ sung biểu đồ vào bản báo cáo cuối cùng, nên dùng cùng thang điểm và cách trình bày cho từng môn, đặt đường phân phối năm 2023 và 2025 trên cùng hệ trục:

- **Histogram:** so sánh tỷ lệ/tần suất trong các khoảng điểm; cần chuẩn hóa mật độ nếu cỡ mẫu khác nhau.
- **KDE:** đường dịch sang phải thường biểu thị vùng điểm tập trung cao hơn; đường trải rộng biểu thị độ phân tán lớn hơn. Đỉnh cao hơn không có nghĩa là số thí sinh nhiều hơn nếu trục dọc là mật độ.
- **Boxplot:** so sánh trung vị, khoảng tứ phân vị và các điểm ngoài râu; ngoại lệ thống kê không tự động là lỗi dữ liệu.
- **Violin plot:** xem các vùng điểm có mật độ cao/thấp và khả năng phân phối nhiều đỉnh.
- **Đọc kết hợp:** không kết luận từ một hình riêng lẻ; đối chiếu với N, trung bình, trung vị, ĐLC và tỷ lệ theo ngưỡng.

**Ghi chú về hiện trạng:** Bản Markdown này chưa nhúng các biểu đồ được tính trực tiếp từ dữ liệu gốc của Nhóm 4. Không nên gắn đường dẫn biểu đồ giả định; cần thêm hình sau khi pipeline tạo và kiểm tra file đầu ra thực tế.

## 8. Giới hạn và nguy cơ diễn giải sai

- Các con số trong các bảng đến từ bảng tần số tổng hợp công khai, không phải kết quả đã được xác nhận từ hai tệp nội bộ của Nhóm 4.
- Biểu đồ dựng từ các mức điểm theo bước 0,5 chỉ là xấp xỉ và có thể làm mất chi tiết của phân phối điểm cá thể.
- Số thí sinh, cơ cấu chọn môn và cách tổ chức thi có thể khác giữa hai năm; số điểm hợp lệ không đồng nghĩa với số người đăng ký xét tuyển bằng một tổ hợp.
- Các ô trống không nên tự động đổi thành 0. Nếu thiếu điểm do môn không được chọn theo thiết kế, đây không phải điểm 0; cơ chế thiếu MCAR/MAR/MNAR không thể xác định chỉ từ bảng điểm nếu không có thông tin đăng ký, miễn thi, vắng thi hoặc nhật ký thu thập.
- Chênh lệch phân phối không chứng minh đề dễ/khó hơn, chất lượng dạy học thay đổi hay có gian lận.
- Trước khi kết luận chính thức, cần xác minh ánh xạ tên môn, phạm vi điểm hợp lệ, số bản ghi trùng, mã tỉnh/hội đồng và quy tắc tính mẫu số.

## 9. Quy trình cần thực hiện để xác nhận kết quả của Nhóm 4

1. Đọc hai tệp dữ liệu gốc năm 2023 và 2025 từ nhánh dự án, ghi nhận kích thước, cột và checksum.
2. Chuẩn hóa tên cột theo ánh xạ môn tương ứng; không gộp điểm tổ hợp vào điểm môn.
3. Kiểm tra miền điểm, giá trị ngoài khoảng cho phép, bản ghi trùng và tỷ lệ thiếu theo từng môn/năm.
4. Tính lại các thống kê và ngưỡng từ điểm cá thể; mẫu số mỗi chỉ số là số điểm hợp lệ của môn/năm đó.
5. Sinh histogram/KDE/boxplot/violin plot theo cùng quy ước trục.
6. Kiểm thử các điều kiện dữ liệu và đối chiếu các bảng đầu ra với báo cáo.
7. Thay các số liệu tham chiếu trong tài liệu bằng kết quả pipeline đã chạy; ghi rõ phiên bản dữ liệu, ngày chạy và nguồn.
8. Chỉ sau khi xác minh mới sử dụng báo cáo làm kết quả chính thức của Nhóm 4.

## 10. Kết luận

Theo bảng phân phối tham chiếu hiện có, phổ điểm Toán, Hóa học và Sinh học có các chỉ số trung tâm giảm; Địa lý, Lịch sử và Vật lý có các chỉ số trung tâm tăng; Ngữ văn tương đối ổn định; Ngoại ngữ có trung bình gần như không đổi nhưng phân phối thu hẹp và tỷ lệ điểm cao giảm. GDCD cần được xem xét riêng do vấn đề về cỡ mẫu và tính tương đương môn thi.

Kết quả này mô tả sự khác biệt quan sát được, không xác định nguyên nhân. **Kết luận cuối cùng của Nhóm 4 phải dựa trên việc chạy lại và kiểm tra pipeline trên hai bộ dữ liệu gốc đã chuẩn hóa**, không trình bày các số liệu tham chiếu này như thể đã được tính trực tiếp từ dữ liệu nội bộ.

## 11. Nguồn tham khảo

- Bảng phân phối điểm công khai: [NhanAZ-Data/diem-thi-thpt-cac-nam](https://github.com/NhanAZ-Data/diem-thi-thpt-cac-nam).
- Tài liệu so sánh tổ hợp môn của dự án: [Phần 3 – Phân tích theo khối thi và tổ hợp môn](./phan_3_to_hop_mon_2023_2025%2Btom_tat.md).
- Dữ liệu và mã phân tích của Nhóm 4: cần cập nhật liên kết chính xác tới tệp/pipeline sau khi xác nhận đường dẫn trên nhánh làm việc.
