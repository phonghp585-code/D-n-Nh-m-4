# Báo cáo từng bước: phân tích điểm thi THPT theo tỉnh, 2023–2025

Báo cáo này dẫn người đọc qua dữ liệu theo đúng thứ tự đặt câu hỏi → đọc biểu đồ → diễn giải → xác định việc có thể làm tiếp. Hình minh họa đều là ảnh đã có trong dự án tại `docs/assets/thpt_2023_2024_2025/`; không tạo biểu đồ mới.

**Báo cáo số liệu đầy đủ:** [Phổ điểm THPT 2023–2025 theo môn, tổ hợp và tỉnh](bao_cao_thpt_2023_2024_2025.md).

## Bước 0 — Xác định dữ liệu đang nói về ai

Báo cáo nền có 63 địa phương/mã hội đồng thi lịch sử trong mỗi năm, tổng cộng 189 nhóm tỉnh × năm. Mỗi môn có mẫu số riêng theo số thí sinh có điểm môn đó; tổ hợp chỉ gồm người có đủ điểm thành phần. Điểm 0 được giữ, điểm thiếu không được đổi thành 0.

Mã địa phương phản ánh nơi đăng ký dự thi theo hội đồng thi, không xác nhận nơi cư trú hay trường học. Ba năm là ba đoàn hệ khác nhau. Năm 2025 có thay đổi đề và chương trình; vì vậy, so sánh qua năm là mô tả kết quả của từng kỳ thi, không phải theo dõi cùng học sinh hay đo trực tiếp biến động năng lực.

## Bước 1 — Nhìn thay đổi chung trước khi đi vào tỉnh

Biểu đồ dumbbell đặt trung bình mỗi môn của ba năm cạnh nhau:

![Điểm trung bình theo môn trong ba năm](assets/thpt_2023_2024_2025/phan_phoi/mean_dumbbell.png)

Báo cáo ghi nhận trung bình Toán là 6,251 năm 2023, 6,447 năm 2024 và 4,783 năm 2025. Một thay đổi lớn như vậy cho biết kết quả quan sát khác nhau giữa các kỳ thi; riêng biểu đồ này không cho biết nguyên nhân, cũng không đủ để kết luận năng lực học sinh giảm. Hãy đọc cùng thay đổi đề, chương trình, cơ cấu môn lựa chọn và độ bao phủ nguồn.

**Câu hỏi dẫn sang bước tiếp:** mức thay đổi chung có giống nhau ở các tỉnh không?

## Bước 2 — Xem chênh lệch giữa các tỉnh và môn

Các heatmap dưới đây cho thấy trung bình và tỷ lệ đạt từ 9 điểm trở lên theo tỉnh × môn, mỗi năm một cặp. Chúng giúp tìm nơi cần xem kỹ hơn; nên đọc cả hai chỉ số vì trung bình và đuôi điểm trả lời hai câu hỏi khác nhau.

### Năm 2023

![Trung bình theo tỉnh và môn, 2023](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2023_mean.png)

![Tỷ lệ đạt từ 9 điểm theo tỉnh và môn, 2023](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2023_ge9.png)

### Năm 2024

![Trung bình theo tỉnh và môn, 2024](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2024_mean.png)

![Tỷ lệ đạt từ 9 điểm theo tỉnh và môn, 2024](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2024_ge9.png)

### Năm 2025

![Trung bình theo tỉnh và môn, 2025](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2025_mean.png)

![Tỷ lệ đạt từ 9 điểm theo tỉnh và môn, 2025](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2025_ge9.png)

**Cách chuyển thành chỉ báo hỗ trợ:** không chỉ xếp theo điểm trung bình. Trong bảng chi tiết, xem P10/trung vị/P90, IQR, tỷ lệ dưới ngưỡng và cỡ mẫu. Tỉnh–môn nằm ở nhóm thấp qua nhiều năm là nơi hợp lý để đặt câu hỏi về hỗ trợ học tập; các thống kê này không chỉ ra nguyên nhân và không phải đánh giá chất lượng địa phương.

**Câu hỏi dẫn sang bước tiếp:** chênh lệch nằm ở toàn bộ phân phối hay chỉ ở một phần đuôi?

## Bước 3 — Đọc hình dạng phân phối trước khi gắn cờ bất thường

ECDF Ngữ văn đặt phân phối quan sát cạnh đường chuẩn tham chiếu. Đường chuẩn chỉ giúp hình dung độ lệch; điểm thi rời rạc, bị chặn từ 0 đến 10 và không bắt buộc phải có dạng chuông.

![ECDF Ngữ văn và đường chuẩn tham chiếu](assets/thpt_2023_2024_2025/phan_phoi/ecdf_normal_literature.png)

Tỷ lệ đuôi điểm cao và thấp giữa các môn/năm được tổng hợp ở biểu đồ sau:

![Tổng hợp tỷ lệ điểm ở các ngưỡng](assets/thpt_2023_2024_2025/phan_phoi/tail_rates_overview.png)

Báo cáo nền còn có các profile tỉnh theo Isolation Forest. Chúng là công cụ xếp hạng điểm khác biệt trên các đặc trưng phân phối, không phải xác suất gian lận.

![Profile khác biệt phân phối môn Ngữ văn theo tỉnh](assets/thpt_2023_2024_2025/phan_phoi/province_anomaly_literature.png)

Trong thống kê nền, số người có ít nhất một điểm môn bị gắn cờ ngoại lệ là 43.642 (2023), 49.786 (2024) và 38.640 (2025). Cờ IQR/z-score được tính riêng cho từng tỉnh × môn. Cờ đuôi cao kết hợp cỡ mẫu, số điểm đạt ngưỡng, tỷ lệ so với phần còn lại, mức chênh tuyệt đối và hiệu chỉnh nhiều kiểm định.

Ví dụ Ngữ văn Nghệ An: tỷ lệ đạt từ 9 điểm là 5,62% năm 2023, 19,69% năm 2024 và 17,99% năm 2025. Sau đối chiếu mô tả theo dải điểm Toán, mức chênh so với kỳ vọng ghi trong báo cáo là +1,67, +11,38 và +14,62 điểm phần trăm. Đây là hiệu chỉnh một phần cơ cấu, không kiểm soát mọi khác biệt giữa thí sinh hay kỳ thi.

**Kết luận của bước:** biểu đồ có thể giúp chọn địa phương/môn cần rà soát; không thể dùng phổ điểm tổng hợp để quy kết gian lận. Muốn xác minh cần dữ liệu cấp câu hỏi/mã đề, phòng thi, chấm/phúc khảo và bằng chứng liên quan.

## Bước 4 — Đặt phân phối môn và tổ hợp cạnh nhau để hiểu lựa chọn

Báo cáo nền tính số dự thi/tỷ lệ tham gia, các môn thường đi cùng nhau và đủ 24 tổ hợp từ ba môn thành phần. Trong dữ liệu tổ hợp, B00 có ít nhất 100 thí sinh tại 63 tỉnh năm 2023, 63 tỉnh năm 2024 và 62 tỉnh năm 2025.

Hai biểu đồ Nghệ An minh họa cách chuyển từ phổ điểm môn sang phổ điểm tổ hợp:

![Phân bố điểm môn 2023–2025 tại Nghệ An](assets/thpt_2023_2024_2025/tinh/29_subjects.png)

![Phân bố điểm tổ hợp 2023–2025 tại Nghệ An](assets/thpt_2023_2024_2025/tinh/29_combinations.png)

Các hình này so sánh phân phối điểm; chúng không tự thể hiện tỷ lệ thí sinh chọn từng môn. Để lập kế hoạch giáo viên/nguồn lực, hãy dùng bảng số dự thi và tỷ lệ chọn môn bên cạnh hình. Cũng cần đọc riêng GDCD ở 2023–2024 và GDKT&PL ở 2025 vì tên môn và nội dung đánh giá đã thay đổi.

## Bước 5 — Từ tín hiệu đến hành động: ví dụ theo tỉnh và môn

Các ví dụ dưới đây lấy số trực tiếp từ bảng chi tiết tỉnh trong báo cáo nền. Ngưỡng `<5 điểm` là ngưỡng mô tả để rà soát phân phối, không mặc định là chuẩn đánh giá hay điều kiện chính sách hỗ trợ.

### Ví dụ A — Ưu tiên hỗ trợ học Toán ở Hà Giang

Trong cả ba năm, Hà Giang có trung bình Toán thấp nhất trong các tỉnh ở bảng so sánh chung. Môn Toán cũng có độ bao phủ cao tại tỉnh, nên đây là tín hiệu phù hợp để ưu tiên trao đổi về hỗ trợ học tập ở cấp tỉnh/trường.

| Năm | Thí sinh có điểm Toán (n) | Tham gia trong tỉnh | Trung bình | Trung vị | Dưới 5 điểm |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2023 | 6.093 | 97,3% | 4,315 | 4,000 | 67,91% |
| 2024 | 6.644 | 96,0% | 4,585 | 4,400 | 61,18% |
| 2025 | 7.047 | 99,0% | 3,449 | 3,250 | 86,52% |

![Bản đồ nhiệt trung bình theo tỉnh và môn năm 2025](assets/thpt_2023_2024_2025/tong_quan/province_matrix_2025_mean.png)

**Hành động có thể cân nhắc:** làm việc với Sở/trường ở Hà Giang để tổ chức đánh giá chẩn đoán Toán tại trường, xác định nhóm kiến thức cần củng cố, rồi bố trí tiết phụ đạo/tài liệu phù hợp. Theo dõi lại tỷ lệ dưới ngưỡng, trung vị và P10 ở kỳ sau với cùng định nghĩa. Dữ liệu hiện có chỉ cho biết kết quả tổng hợp môn; chưa chỉ ra trường hay chủ đề Toán nào cần hỗ trợ.

**Cách đọc thận trọng:** năm 2025 có thay đổi đề/chương trình. Không diễn giải mức 86,52% như bằng chứng năng lực của cùng học sinh giảm từ năm trước. Đây là lý do để ưu tiên chẩn đoán tại chỗ, không phải căn cứ gán nguyên nhân cho địa phương.

### Ví dụ B — Lập kế hoạch môn lựa chọn ở Nghệ An

Tỷ lệ thí sinh có điểm Sinh học trong tổng hồ sơ Nghệ An là khoảng 26,5% năm 2023 (9.716/36.886), 26,5% năm 2024 (9.723/36.729) và 8,8% năm 2025 (3.437/39.183). Đây là thay đổi rõ về số người dự thi quan sát được; năm 2025 cũng thay đổi quy tắc lựa chọn môn và cơ cấu kỳ thi.

![Phân bố điểm môn theo năm tại Nghệ An](assets/thpt_2023_2024_2025/tinh/29_subjects.png)

**Hành động có thể cân nhắc:** trước khi xếp lịch giáo viên/lớp ôn Sinh học cho năm tới, đối chiếu số liệu này với đăng ký môn ở từng trường, kế hoạch mở lớp và khảo sát lựa chọn học sinh. Nếu số đăng ký hiện tại xác nhận nhu cầu thấp hơn, điều chỉnh quy mô lớp hoặc dùng chung nguồn lực liên trường; nếu số đăng ký không giảm tương ứng, kiểm tra độ bao phủ dữ liệu trước khi đổi kế hoạch.

**Không nên suy ra:** điểm Sinh học thấp hơn hoặc ít điểm Sinh học hơn có nghĩa học sinh Nghệ An yếu hơn. Tỷ lệ dự thi phản ánh lựa chọn/độ bao phủ; biểu đồ phổ điểm không cho biết lý do từng em chọn hay không chọn môn.

### Ví dụ C — Rà soát thêm tín hiệu đuôi cao ở Ngữ văn Nghệ An

Tỷ lệ Ngữ văn đạt từ 9 điểm tại Nghệ An là 5,62% năm 2023 (n=36.273), 19,69% năm 2024 (n=36.273) và 17,99% năm 2025 (n=39.062). Báo cáo còn đối chiếu theo dải điểm Toán; mức chênh so với tỷ lệ kỳ vọng lần lượt là +1,67, +11,38 và +14,62 điểm phần trăm. Đây là một dấu hiệu để đặt câu hỏi kiểm tra.

![ECDF Ngữ văn và đường chuẩn tham chiếu](assets/thpt_2023_2024_2025/phan_phoi/ecdf_normal_literature.png)

**Hành động có thể cân nhắc:** xem phân phối theo trường/điểm thi và đối chiếu với đáp án, mã đề, quy trình chấm/phúc khảo nếu nhóm có quyền truy cập; xem liệu chênh lệch có tập trung vào một nhóm cụ thể hay trải rộng. Chỉ đưa vào danh sách rà soát sau khi kiểm tra cỡ mẫu, nguồn và các khác biệt về đề/chương trình.

**Không nên kết luận:** chênh lệch đuôi điểm hoặc ECDF khác nhau đồng nghĩa với gian lận. Biểu đồ điểm không phải bằng chứng về hành vi.

### Ví dụ D — Học sinh nào cần hỗ trợ?

Các ví dụ Hà Giang ở trên chỉ ra **địa phương–môn nên được ưu tiên đánh giá hỗ trợ**. Chúng chưa xác định học sinh cụ thể nào cần hỗ trợ. Muốn lập danh sách hậu kiểm sau kỳ thi, nhà trường cần ghép kết quả cá nhân với dữ liệu học tập được phép sử dụng và bảo vệ thông tin định danh. Muốn cảnh báo **trước kỳ thi**, cần các biến đã có trước kỳ thi như điểm đánh giá định kỳ; không dùng điểm môn khác của chính kỳ thi làm đầu vào vì khi đó kết quả đã xảy ra.

| Kết quả quan sát | Ví dụ cụ thể | Hành động cân nhắc |
| --- | --- | --- |
| Kết quả thấp kéo dài ở môn có độ bao phủ cao | Hà Giang – Toán: trung bình thấp nhất cả ba năm; 61,18–86,52% dưới 5 | Ưu tiên chẩn đoán học tập ở trường, bố trí hỗ trợ Toán, theo dõi lại bằng cùng chỉ số |
| Cơ cấu dự thi thay đổi | Nghệ An – Sinh học: khoảng 26,5% năm 2023–2024 xuống 8,8% năm 2025 | Đối chiếu đăng ký môn theo trường trước khi phân bổ giáo viên/lớp ôn |
| Đuôi điểm khác biệt | Nghệ An – Ngữ văn: ≥9 là 19,69% năm 2024; chênh điều chỉnh theo Toán +11,38 điểm phần trăm | Kiểm tra hồ sơ và dữ liệu độc lập; không gắn nhãn gian lận |
| Cần nhận diện từng học sinh | Dữ liệu tổng hợp tỉnh không chứa nguyên nhân hay thông tin trước thi | Bổ sung dữ liệu học tập phù hợp; đánh giá theo thời gian và bảo vệ dữ liệu cá nhân |

## Giới hạn nguồn và khả năng tái lập

Các số liệu và biểu đồ trên được dẫn từ báo cáo nền. Tại commit nền `codex/statistics-correlation-pca`, tệp `data/raw/diem_thi_thpt_2024.csv` không có trong cây tệp dù báo cáo ghi đường dẫn và SHA-256. Nguồn được nêu là bản công khai ngày 17/07/2024, chưa gồm phúc khảo; báo cáo ghi nhận 1.045.613 điểm Toán, ít hơn 30 so với phổ điểm công bố. Cần bổ sung đúng snapshot nguồn và mã sinh báo cáo để người khác chạy lại toàn bộ kết quả từ đầu.

Xem [báo cáo nền đầy đủ](bao_cao_thpt_2023_2024_2025.md) để tra bảng chi tiết theo tỉnh, môn và tổ hợp.
