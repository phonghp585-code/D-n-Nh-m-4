# Báo cáo phân tích mô tả và so sánh phổ điểm thi THPT năm 2023 và 2025

> **Phiên bản tính lại từ dữ liệu của Nhóm 4.** Phân tích sử dụng tệp 2023 `data/processed/week5/week5_final+du_lieu_cuoi.csv` trên nhánh `thanh` và tệp 2025 `data/dataset_diem_thi_thpt_2025.csv` trên nhánh `nhan` (bản dữ liệu văn bản do nhóm cung cấp có cùng bộ cột điểm). Chỉ lấy điểm số hợp lệ trong khoảng 0–10; giá trị thiếu không được thay bằng 0. Các thống kê dưới đây được tính trực tiếp trên dữ liệu điểm cá nhân.

## 1. Mục tiêu và câu hỏi phân tích

1. So sánh trung bình, trung vị và độ phân tán của từng môn giữa hai năm.
2. Đánh giá hình dạng phân phối bằng skewness và excess kurtosis.
3. So sánh tỷ lệ điểm liệt tham khảo (≤1), dưới 5, từ 8 trở lên và từ 9 trở lên.
4. Dùng histogram, KDE, boxplot và violin plot để quan sát dịch chuyển vị trí, độ rộng và hình dạng phổ điểm.
5. Nêu giới hạn diễn giải: hai năm có nhóm thí sinh và cách chọn môn khác nhau; chênh lệch phân phối không tự chứng minh nguyên nhân.

## 2. Dữ liệu và phương pháp

**Nhận xét sau bước chuẩn bị dữ liệu.** Số lượng điểm hợp lệ không đồng đều giữa các môn, rõ nhất ở Ngoại ngữ và Sinh học. Vì vậy, không nên so sánh số lượng thí sinh giữa môn như thể tất cả cùng thi một nhóm môn; các tỷ lệ phải dùng số điểm hợp lệ của từng môn làm mẫu số.

- Dữ liệu 2023: 1.022.060 dòng; dữ liệu 2025: 1.131.136 dòng.
- Các môn so sánh: Toán, Ngữ văn, Ngoại ngữ, Vật lý, Hóa học, Sinh học, Lịch sử và Địa lý.
- Ánh xạ cột: `Mathematics/toan`, `Literature/ngu_van`, `Foreign language/ngoai_ngu`, `Physics/vat_li`, `Chemistry/hoa_hoc`, `Biology/sinh_hoc`, `History/lich_su`, `Geography/dia_li`.
- Mỗi thống kê dùng các điểm hợp lệ của chính môn và năm đó làm mẫu số. Số lượng điểm hợp lệ vì thế khác nhau giữa môn và năm.
- Histogram dùng cùng bin 0,25 điểm và chuẩn hóa mật độ. KDE dùng cùng bandwidth xấp xỉ 0,20 điểm. Boxplot tính trên toàn bộ điểm hợp lệ (ẩn các điểm ngoại lệ riêng lẻ để dễ đọc); violin plot dùng mẫu ngẫu nhiên có seed cố định, tối đa 12.000 điểm mỗi năm.
- Skewness âm thường gợi ý đuôi trái dài hơn; skewness dương gợi ý đuôi phải dài hơn. Excess kurtosis mô tả hình dạng/đuôi so với phân phối chuẩn; cần đọc cùng biểu đồ.

## 3. Thống kê mô tả theo môn

**Nhận xét sau thống kê mô tả.** Toán giảm mạnh về trung bình và trung vị; Hóa học và Sinh học cũng giảm. Ngược lại, Ngữ văn, Vật lý, Lịch sử và Địa lý tăng về trung bình. Độ lệch chuẩn tăng ở một số môn cho thấy điểm phân tán rộng hơn, nhưng bản thân thống kê này chưa giải thích nguyên nhân.

| Môn | N 2023 | N 2025 | TB 2023 | TB 2025 | Trung vị 2023 | Trung vị 2025 | ĐLC 2023 | ĐLC 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Toán | 1.003.373 | 1.126.172 | 6,251 | 4,783 | 6,60 | 4,60 | 1,633 | 1,677 |
| Ngữ văn | 1.008.239 | 1.126.726 | 6,858 | 7,002 | 7,00 | 7,25 | 1,326 | 1,279 |
| Ngoại ngữ | 880.997 | 357.723 | 5,462 | 5,406 | 5,20 | 5,25 | 1,966 | 1,480 |
| Vật lý | 327.189 | 347.599 | 6,574 | 6,985 | 6,75 | 7,00 | 1,487 | 1,517 |
| Hóa học | 328.118 | 240.135 | 6,745 | 6,065 | 7,00 | 6,00 | 1,428 | 1,811 |
| Sinh học | 324.625 | 69.895 | 6,395 | 5,778 | 6,50 | 5,75 | 1,207 | 1,581 |
| Lịch sử | 683.447 | 481.293 | 6,026 | 6,519 | 6,00 | 6,60 | 1,553 | 1,633 |
| Địa lý | 682.134 | 476.472 | 6,148 | 6,628 | 6,25 | 6,75 | 1,169 | 1,750 |

## 4. Hình dạng phân phối: skewness và excess kurtosis

**Nhận xét sau phân tích hình dạng.** Skewness của Toán, Hóa học và Sinh học chuyển từ âm sang dương, gợi ý hình dạng lệch của phân phối đã thay đổi giữa hai năm. Ngữ văn có skewness âm hơn trong năm 2025. Kurtosis cần được đọc cùng histogram/KDE, không nên kết luận chỉ dựa vào một chỉ số.

| Môn | Skewness 2023 | Skewness 2025 | Excess kurtosis 2023 | Excess kurtosis 2025 |
|---|---:|---:|---:|---:|
| Toán | -0,596 | 0,400 | -0,402 | -0,276 |
| Ngữ văn | -0,535 | -0,773 | 0,250 | 0,738 |
| Ngoại ngữ | 0,305 | 0,324 | -0,856 | -0,057 |
| Vật lý | -0,451 | -0,207 | -0,378 | -0,572 |
| Hóa học | -0,629 | 0,102 | 0,050 | -0,795 |
| Sinh học | -0,182 | 0,147 | 0,160 | -0,550 |
| Lịch sử | 0,029 | -0,186 | -0,552 | -0,651 |
| Địa lý | -0,153 | -0,144 | 0,252 | -0,698 |

## 5. Tỷ lệ điểm theo ngưỡng

**Nhận xét sau phân tích ngưỡng điểm.** Toán có tỷ lệ dưới 5 tăng rất mạnh; Hóa học và Sinh học cũng tăng. Vật lý và Lịch sử có tỷ lệ dưới 5 giảm, trong khi tỷ lệ từ 8 trở lên tăng. Địa lý tăng ở cả tỷ lệ dưới 5 lẫn tỷ lệ điểm cao, gợi ý phân phối có thể trải rộng hơn. Các ngưỡng này chỉ mô tả dữ liệu, không tự xác định nguyên nhân.

| Môn | Năm | ≤ 1 | < 5 | ≥ 8 | ≥ 9 |
|---|---:|---:|---:|---:|---:|
| Toán | 2023 | 0,01% | 21,64% | 15,16% | 1,00% |
| Toán | 2025 | 0,07% | 56,39% | 5,45% | 1,43% |
| Ngữ văn | 2023 | 0,01% | 7,31% | 24,42% | 4,30% |
| Ngữ văn | 2025 | 0,01% | 6,24% | 26,69% | 3,91% |
| Ngoại ngữ | 2023 | 0,02% | 44,69% | 15,18% | 5,38% |
| Ngoại ngữ | 2025 | 0,01% | 37,86% | 6,05% | 1,80% |
| Vật lý | 2023 | 0,01% | 14,79% | 21,32% | 2,97% |
| Vật lý | 2025 | 0,00% | 9,79% | 30,79% | 11,53% |
| Hóa học | 2023 | 0,00% | 11,70% | 22,67% | 3,42% |
| Hóa học | 2025 | 0,00% | 29,53% | 19,29% | 7,43% |
| Sinh học | 2023 | 0,01% | 10,40% | 10,57% | 1,68% |
| Sinh học | 2025 | 0,00% | 32,44% | 10,83% | 2,54% |
| Lịch sử | 2023 | 0,01% | 24,91% | 13,07% | 3,06% |
| Lịch sử | 2025 | 0,00% | 18,63% | 23,03% | 6,88% |
| Địa lý | 2023 | 0,02% | 13,35% | 6,64% | 0,87% |
| Địa lý | 2025 | 0,00% | 18,69% | 26,68% | 11,26% |

## 6. Phân tích và so sánh xu hướng

**Nhận xét tổng hợp sau phân tích từng môn.** Không có một xu hướng chung cho cả tám môn: các môn có thể thay đổi theo hướng khác nhau về trung tâm, độ phân tán và đuôi phân phối. Do cơ cấu thí sinh và việc lựa chọn môn có thể khác nhau giữa 2023 và 2025, đây là so sánh mô tả giữa hai tập dữ liệu độc lập, không phải so sánh cùng một nhóm học sinh.

### 6.1. Toán

- **Trung tâm:** 6,251 → 4,783 (trung bình giảm 1,468 điểm); trung vị 6,60 → 4,60.
- **Độ phân tán:** độ lệch chuẩn 1,633 → 1,677.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi +34,75 điểm phần trăm; tỷ lệ ≥8 thay đổi -9,71 điểm phần trăm; tỷ lệ ≥9 thay đổi +0,43 điểm phần trăm.
- **Hình dạng:** skewness -0,596 → 0,400; excess kurtosis -0,402 → -0,276.

### 6.2. Ngữ văn

- **Trung tâm:** 6,858 → 7,002 (trung bình tăng 0,144 điểm); trung vị 7,00 → 7,25.
- **Độ phân tán:** độ lệch chuẩn 1,326 → 1,279.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi -1,07 điểm phần trăm; tỷ lệ ≥8 thay đổi +2,27 điểm phần trăm; tỷ lệ ≥9 thay đổi -0,39 điểm phần trăm.
- **Hình dạng:** skewness -0,535 → -0,773; excess kurtosis 0,250 → 0,738.

### 6.3. Ngoại ngữ

- **Trung tâm:** 5,462 → 5,406 (trung bình giảm 0,056 điểm); trung vị 5,20 → 5,25.
- **Độ phân tán:** độ lệch chuẩn 1,966 → 1,480.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi -6,83 điểm phần trăm; tỷ lệ ≥8 thay đổi -9,13 điểm phần trăm; tỷ lệ ≥9 thay đổi -3,58 điểm phần trăm.
- **Hình dạng:** skewness 0,305 → 0,324; excess kurtosis -0,856 → -0,057.

### 6.4. Vật lý

- **Trung tâm:** 6,574 → 6,985 (trung bình tăng 0,411 điểm); trung vị 6,75 → 7,00.
- **Độ phân tán:** độ lệch chuẩn 1,487 → 1,517.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi -5,00 điểm phần trăm; tỷ lệ ≥8 thay đổi +9,47 điểm phần trăm; tỷ lệ ≥9 thay đổi +8,56 điểm phần trăm.
- **Hình dạng:** skewness -0,451 → -0,207; excess kurtosis -0,378 → -0,572.

### 6.5. Hóa học

- **Trung tâm:** 6,745 → 6,065 (trung bình giảm 0,680 điểm); trung vị 7,00 → 6,00.
- **Độ phân tán:** độ lệch chuẩn 1,428 → 1,811.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi +17,83 điểm phần trăm; tỷ lệ ≥8 thay đổi -3,38 điểm phần trăm; tỷ lệ ≥9 thay đổi +4,01 điểm phần trăm.
- **Hình dạng:** skewness -0,629 → 0,102; excess kurtosis 0,050 → -0,795.

### 6.6. Sinh học

- **Trung tâm:** 6,395 → 5,778 (trung bình giảm 0,617 điểm); trung vị 6,50 → 5,75.
- **Độ phân tán:** độ lệch chuẩn 1,207 → 1,581.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi +22,04 điểm phần trăm; tỷ lệ ≥8 thay đổi +0,26 điểm phần trăm; tỷ lệ ≥9 thay đổi +0,86 điểm phần trăm.
- **Hình dạng:** skewness -0,182 → 0,147; excess kurtosis 0,160 → -0,550.

### 6.7. Lịch sử

- **Trung tâm:** 6,026 → 6,519 (trung bình tăng 0,493 điểm); trung vị 6,00 → 6,60.
- **Độ phân tán:** độ lệch chuẩn 1,553 → 1,633.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi -6,28 điểm phần trăm; tỷ lệ ≥8 thay đổi +9,96 điểm phần trăm; tỷ lệ ≥9 thay đổi +3,82 điểm phần trăm.
- **Hình dạng:** skewness 0,029 → -0,186; excess kurtosis -0,552 → -0,651.

### 6.8. Địa lý

- **Trung tâm:** 6,148 → 6,628 (trung bình tăng 0,480 điểm); trung vị 6,25 → 6,75.
- **Độ phân tán:** độ lệch chuẩn 1,169 → 1,750.
- **Ngưỡng điểm:** tỷ lệ dưới 5 thay đổi +5,34 điểm phần trăm; tỷ lệ ≥8 thay đổi +20,04 điểm phần trăm; tỷ lệ ≥9 thay đổi +10,39 điểm phần trăm.
- **Hình dạng:** skewness -0,153 → -0,144; excess kurtosis 0,252 → -0,698.

## 7. Biểu đồ phổ điểm theo môn

**Cách đọc biểu đồ.** Histogram cho thấy tần suất tương đối theo khoảng điểm; KDE làm rõ hình dạng tổng thể; boxplot so sánh trung vị và tứ phân vị; violin plot cho thấy vùng tập trung điểm. Hãy đối chiếu cả bốn loại với bảng thống kê, vì bandwidth KDE và việc lấy mẫu cho violin có thể ảnh hưởng hình dạng nhìn thấy.

Mỗi hình gồm bốn biểu đồ so sánh cùng môn giữa 2023 và 2025: histogram chồng lớp, KDE, boxplot và violin plot. Các hình được tạo bởi script [`scripts/analysis/plot_subject_score_distributions.py`](../scripts/analysis/plot_subject_score_distributions.py). File ảnh được lưu trong `outputs/week6/figures/`.

### 7.1. Toán

![So sánh histogram, KDE, boxplot và violin plot môn Toán năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_toan_2023_2025.svg)

[Mở hình SVG — Toán](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_toan_2023_2025.svg)

### 7.2. Ngữ văn

![So sánh histogram, KDE, boxplot và violin plot môn Ngữ văn năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_ngu_van_2023_2025.svg)

[Mở hình SVG — Ngữ văn](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_ngu_van_2023_2025.svg)

### 7.3. Ngoại ngữ

![So sánh histogram, KDE, boxplot và violin plot môn Ngoại ngữ năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_ngoai_ngu_2023_2025.svg)

[Mở hình SVG — Ngoại ngữ](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_ngoai_ngu_2023_2025.svg)

### 7.4. Vật lý

![So sánh histogram, KDE, boxplot và violin plot môn Vật lý năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_vat_li_2023_2025.svg)

[Mở hình SVG — Vật lý](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_vat_li_2023_2025.svg)

### 7.5. Hóa học

![So sánh histogram, KDE, boxplot và violin plot môn Hóa học năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_hoa_hoc_2023_2025.svg)

[Mở hình SVG — Hóa học](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_hoa_hoc_2023_2025.svg)

### 7.6. Sinh học

![So sánh histogram, KDE, boxplot và violin plot môn Sinh học năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_sinh_hoc_2023_2025.svg)

[Mở hình SVG — Sinh học](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_sinh_hoc_2023_2025.svg)

### 7.7. Lịch sử

![So sánh histogram, KDE, boxplot và violin plot môn Lịch sử năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_lich_su_2023_2025.svg)

[Mở hình SVG — Lịch sử](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_lich_su_2023_2025.svg)

### 7.8. Địa lý

![So sánh histogram, KDE, boxplot và violin plot môn Địa lý năm 2023 và 2025](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_dia_li_2023_2025.svg)

[Mở hình SVG — Địa lý](https://raw.githubusercontent.com/phonghp585-code/D-n-Nh-m-4/thanh/outputs/week6/figures/pho_diem_dia_li_2023_2025.svg)

## 8. Kết luận chung

**Nhận xét sau kết luận.** Kết quả phù hợp để xác định những môn cần phân tích sâu hơn, nhưng không đủ để khẳng định đề thi dễ/khó hơn hoặc có gian lận. Muốn giải thích nguyên nhân cần bổ sung thông tin về quy chế thi, cơ cấu dự thi, dữ liệu đăng ký môn và nguồn dữ liệu độc lập.

- **Toán** có mức giảm trung tâm rõ nhất: trung bình giảm khoảng 1,47 điểm, tỷ lệ dưới 5 tăng khoảng 34,75 điểm phần trăm, còn tỷ lệ ≥8 giảm khoảng 9,71 điểm phần trăm.
- **Hóa học và Sinh học** có trung bình giảm và tỷ lệ dưới 5 tăng; N của Sinh học năm 2025 nhỏ hơn đáng kể, cần lưu ý khác biệt cơ cấu thí sinh.
- **Vật lý, Lịch sử và Địa lý** có trung bình tăng và tỷ lệ ≥8 tăng. Với Địa lý, tỷ lệ dưới 5 cũng tăng, nên phân phối có vẻ rộng hơn thay vì dịch chuyển đồng đều.
- **Ngữ văn** tăng nhẹ ở trung bình, trung vị và tỷ lệ ≥8, nhưng tỷ lệ ≥9 giảm nhẹ.
- **Ngoại ngữ** có trung bình gần như không đổi, nhưng tỷ lệ ≥8 và ≥9 giảm; N năm 2025 thấp hơn nhiều, vì vậy không nên diễn giải như so sánh cùng một nhóm thí sinh.
- **Không có một xu hướng chung cho tất cả môn.** Cần kết hợp trung tâm, độ phân tán, tỷ lệ theo ngưỡng và biểu đồ.

## 9. Giới hạn diễn giải

1. Hai năm không phải cùng một nhóm thí sinh. Cơ cấu chọn môn và quy chế thi khác nhau, đặc biệt ở môn tự chọn.
2. Điểm trung bình và phân phối quan sát không đủ để kết luận đề thi dễ/khó hơn hay năng lực học sinh thay đổi do một nguyên nhân cụ thể.
3. Tỷ lệ ≤1 được trình bày như một ngưỡng mô tả “điểm rất thấp”; việc xác định chính thức điểm liệt cần đối chiếu quy định áp dụng từng năm.
4. Các ô trống được giữ là thiếu; không thể phân loại MCAR/MAR/MNAR chỉ từ bảng điểm.
5. Các mã GDCD/GDKT&PL không được gộp vào so sánh theo môn cá nhân trong báo cáo này vì khác nội dung môn thi.

## 10. Tái lập kết quả

Chạy `python scripts/analysis/plot_subject_score_distributions.py` trong môi trường có pandas, numpy và matplotlib để tạo lại hình. Workflow GitHub Actions [`subject-score-plots.yml`](../.github/workflows/subject-score-plots.yml) được cấu hình để tạo hình và commit vào nhánh `thanh` khi các tệp liên quan thay đổi. Kiểm tra tab **Actions** để xác nhận workflow đã hoàn tất thành công trước khi dùng hình trong bản nộp.

## 11. Nguồn và tệp đầu ra

- Dữ liệu 2023: `data/processed/week5/week5_final+du_lieu_cuoi.csv` (nhánh `thanh`).
- Dữ liệu 2025: `data/dataset_diem_thi_thpt_2025.csv` (nhánh `nhan`).
- Script biểu đồ: [`plot_subject_score_distributions.py`](../scripts/analysis/plot_subject_score_distributions.py).
- Hình: `outputs/week6/figures/pho_diem_*_2023_2025.svg`.
- Báo cáo theo tổ hợp: [Phần 3 – Phân tích theo khối thi và tổ hợp môn](./phan_3_to_hop_mon_2023_2025%2Btom_tat.md).
