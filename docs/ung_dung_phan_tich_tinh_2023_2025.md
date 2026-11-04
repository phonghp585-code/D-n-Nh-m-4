# Ứng dụng phân tích điểm thi THPT theo địa phương, 2023–2025

## Mục tiêu

Tài liệu này chuyển các thống kê đã có trong [báo cáo phổ điểm 2023–2025](bao_cao_thpt_2023_2024_2025.md) thành bốn câu hỏi ứng dụng. Phạm vi là điểm thi theo môn và tổ hợp, theo địa phương/mã hội đồng thi lịch sử, trong ba năm. “Địa phương” ở đây không đồng nghĩa nơi cư trú hay trường học.

Bộ dữ liệu trong báo cáo bao phủ 63 địa phương mỗi năm (189 nhóm địa phương × năm). Với mỗi môn, mẫu số là số thí sinh có điểm môn đó; với tổ hợp, chỉ tính thí sinh có đủ điểm thành phần. Không điền điểm thiếu thành 0.

## 1. Theo dõi chênh lệch kết quả và cơ hội giữa các tỉnh

**Cách dùng:** so sánh P10, trung vị, P90, IQR và tỷ lệ dưới ngưỡng theo địa phương × năm × môn/tổ hợp; luôn đặt cạnh cỡ mẫu. Có thể ưu tiên xem các địa phương nằm ở nhóm thấp qua nhiều năm thay vì xếp hạng theo một điểm trung bình.

**Kết quả hiện có:** báo cáo tổng hợp các phân vị, tỷ lệ ngưỡng và phân phối cho từng địa phương, đồng thời có atlas theo tỉnh. Ví dụ, trung bình Toán toàn quốc được báo cáo là 6,251 (2023), 6,447 (2024) và 4,783 (2025). Đây là khác biệt giữa ba đoàn hệ và ba bối cảnh đề thi/chương trình, không phải bằng chứng rằng năng lực của học sinh giảm.

**Hành động phù hợp:** dùng danh sách tỉnh–môn có P10 thấp hoặc tỷ lệ dưới ngưỡng cao kéo dài để đặt câu hỏi hỗ trợ; không xem thứ hạng là đánh giá chất lượng của tỉnh. Khi công bố, kèm n và khoảng tin cậy nếu dùng tỷ lệ.

## 2. Theo dõi thay đổi lựa chọn môn giữa các tỉnh

**Cách dùng:** so sánh số dự thi và tỷ lệ tham gia từng môn/tổ hợp theo tỉnh–năm; xem thêm các môn thường đi cùng nhau và mức tập trung lựa chọn.

**Kết quả hiện có:** báo cáo đã tính cơ cấu môn, mức đủ điều kiện lập tổ hợp và thống kê cho 24 tổ hợp từ ba môn thành phần. Ví dụ, số tỉnh có ít nhất 100 thí sinh ở tổ hợp B00 là 63 năm 2023, 63 năm 2024 và 62 năm 2025. Các tổ hợp chứa GDCD ở năm 2023–2024 và GDKT&PL năm 2025 cần được đọc như khác biệt thành phần môn, không gộp cơ học.

**Hành động phù hợp:** theo dõi tỉnh có tỷ lệ chọn môn đổi nhanh để hỗ trợ lập kế hoạch giáo viên và nguồn lực; báo cáo cả số người và tỷ lệ vì quy mô đoàn hệ giữa tỉnh khác nhau.

## 3. Sàng lọc phân phối bất thường để ưu tiên rà soát

**Cách dùng:** kết hợp nhiều tín hiệu trong cùng môn/năm: hình dạng ECDF, đuôi điểm, phân vị, tỷ lệ điểm cao/thấp và cỡ mẫu. Các cờ thống kê chỉ tạo danh sách cần kiểm tra thêm.

![ECDF Ngữ văn và đường chuẩn tham chiếu](assets/thpt_2023_2024_2025/phan_phoi/ecdf_normal_literature.png)

**Kết quả hiện có:** báo cáo ghi nhận người có ít nhất một điểm môn bị cờ ngoại lệ là 43.642 (2023), 49.786 (2024), 38.640 (2025). Cờ IQR hoặc z-score được tính riêng theo tỉnh × môn; tiêu chí đuôi cao kết hợp cỡ mẫu, số điểm đạt ngưỡng, tỷ lệ so với phần còn lại, chênh lệch tuyệt đối và hiệu chỉnh Benjamini–Hochberg. Những cờ này không xác định sai phạm.

Một ví dụ minh họa là Ngữ văn Nghệ An: tỷ lệ ≥9 trong dữ liệu được báo cáo là 5,62% (2023), 19,69% (2024), 17,99% (2025). Sau đối chiếu mô tả theo dải điểm Toán, mức chênh so với kỳ vọng lần lượt là +1,67, +11,38 và +14,62 điểm phần trăm. Phép điều chỉnh này chỉ kiểm soát một phần cơ cấu điểm, không loại trừ các khác biệt khác.

**Hành động phù hợp:** chuyển cờ sang bước rà soát hồ sơ. Để xác minh gian lận cần dữ liệu cấp câu hỏi/mã đề, phòng thi, chấm và phúc khảo cùng bằng chứng độc lập; phổ điểm tổng hợp không đủ để quy kết cho tỉnh hay thí sinh.

## 4. Dự báo nhóm có nguy cơ điểm thấp để phân bổ hỗ trợ

**Đánh giá khả thi với dữ liệu hiện có: chưa đủ điều kiện xây mô hình dự báo trước kỳ thi.** Các tệp điểm hiện tại chủ yếu chứa kết quả thi cuối kỳ; không có thông tin đầu vào sẵn có trước kỳ thi như điểm đánh giá định kỳ, lịch sử học tập, điều kiện tiếp cận hỗ trợ hoặc trường học. Dùng điểm của môn khác cùng kỳ để dự báo sẽ chỉ là phân loại sau khi thi, không phải cảnh báo sớm. Ba năm cũng gồm thay đổi chương trình/đề thi nên không nên chia ngẫu nhiên bản ghi để tạo cảm giác mô hình dự báo ổn định.

**Bước tiếp theo nếu muốn triển khai:** xác định trước ngưỡng “điểm thấp” và hành động hỗ trợ; bổ sung biến có sẵn trước kỳ thi; huấn luyện trên các khóa cũ và đánh giá theo năm kế tiếp; so sánh với baseline đơn giản; kiểm tra hiệu năng theo tỉnh và nhóm học sinh; kiểm tra rò rỉ dữ liệu trước khi dùng kết quả phân bổ hỗ trợ. Cho đến khi có các dữ liệu này, nên dùng chỉ báo mô tả ở bài toán 1 để ưu tiên hỗ trợ cấp tỉnh–môn, không gắn nhãn rủi ro cá nhân.

## Nguồn và giới hạn tái lập

Báo cáo chi tiết ghi nguồn dữ liệu 2023, 2024 và 2025 cùng SHA-256, nhưng trong cây tệp của commit nền `codex/statistics-correlation-pca` hiện không có `data/raw/diem_thi_thpt_2024.csv`. Nguồn 2024 được mô tả là bản thu thập công khai ngày 17/07/2024 từ [anhdung98/diem_thi_2024](https://github.com/anhdung98/diem_thi_2024), chưa gồm phúc khảo. Vì vậy, các con số trích ở đây là kết quả đã ghi trong báo cáo nền; việc tái tạo độc lập toàn bộ báo cáo từ chính nhánh này cần bổ sung tệp 2024 (hoặc quy trình tải có phiên bản/hash) và mã sinh báo cáo.

Báo cáo nền cũng ghi CSV 2024 có 1.045.613 điểm Toán, ít hơn 30 so với phổ điểm công bố. Không tự suy đoán hay điền các bản ghi thiếu. Khác biệt địa giới, lựa chọn môn, thay đổi đề/chương trình và phạm vi nguồn đều giới hạn so sánh qua năm. Xem [báo cáo chi tiết](bao_cao_thpt_2023_2024_2025.md) để biết định nghĩa, thống kê theo tỉnh và các giới hạn khác.
