# INFO3020 Week 6–7 — Phân tích mô tả và so sánh phổ điểm thi THPT 2023–2025

## 1. Mục tiêu và câu hỏi phân tích

Báo cáo nối tiếp quy trình xử lý dữ liệu ở Week 3–5, sử dụng hai bộ dữ liệu điểm thi THPT năm 2023 và 2025 đã được chuẩn hóa mã tỉnh trong dự án Nhóm 4. Trọng tâm tuần này là **thống kê mô tả và trực quan hóa phân phối điểm**, không xây dựng mô hình dự đoán và không suy luận quan hệ nhân quả.

Các câu hỏi chính:

1. Trung bình và trung vị của từng môn thay đổi như thế nào giữa năm 2023 và 2025?
2. Điểm số năm nào phân tán hơn, và khoảng giữa 50% thí sinh (IQR) có thay đổi không?
3. Phân phối điểm lệch trái, lệch phải hay tương đối cân đối? Độ nhọn có gợi ý đuôi phân phối khác biệt không?
4. Tỷ lệ điểm rất thấp, dưới trung bình và ở nhóm điểm cao thay đổi ra sao?
5. Histogram, KDE, boxplot và violin plot có cùng hỗ trợ một nhận xét hay cho thấy các khía cạnh khác nhau?
6. Những giới hạn nào cần nêu khi so sánh hai kỳ thi khác năm?

**Phạm vi kết luận:** báo cáo mô tả những điểm hợp lệ đã quan sát trong dữ liệu. Chênh lệch giữa hai năm không tự chứng minh đề dễ/khó hơn, năng lực thí sinh tăng/giảm hoặc nguyên nhân cụ thể nào khác.

## 2. Nguồn dữ liệu và phạm vi sử dụng

| Thành phần | Nguồn sử dụng | Vai trò |
|---|---|---|
| Điểm thi năm 2023 | `data/processed/week3/exam_2023.parquet` từ nhánh `thanh` | Bảng điểm đã qua các bước kiểm tra và xử lý trước đó |
| Điểm thi năm 2025 | `data/dataset_diem_thi_thpt_2025.csv` từ nhánh `nhan` | Bảng điểm năm 2025; cần tải đầy đủ đối tượng Git LFS trước khi chạy |
| Mã phân tích | `src/week6_score_distribution.py` | Chuẩn hóa tên môn, tính thống kê, vẽ biểu đồ và tạo báo cáo DOCX |
| Notebook | `notebooks/week6/phan_tich_pho_diem_2023_2025.ipynb` | Tài liệu thực hành và kiểm tra quy trình |
| Kiểm thử | `tests/test_week6_score_distribution.py` | Kiểm tra một số quy tắc thống kê và xử lý |
| Kết quả sinh tự động | `outputs/score_distribution/` | Bảng thống kê, dữ liệu dạng dài, biểu đồ, metadata và báo cáo DOCX |

Tên môn được ánh xạ về nhãn thống nhất trước khi so sánh. Chương trình chỉ so sánh các môn nhận diện được ở cả hai năm. Vì cấu trúc môn thi có thể thay đổi giữa các năm, đặc biệt ở môn giáo dục công dân và giáo dục kinh tế và pháp luật, không được coi hai môn này là tương đương về nội dung chỉ vì chúng cùng thuộc nhóm giáo dục xã hội. Nếu hai dataset không có cùng môn, môn đó không nằm trong phép so sánh trực tiếp.

### Điều kiện sử dụng dữ liệu

- Điểm được chuyển sang dạng số; giá trị không chuyển đổi được được xem là thiếu.
- Chỉ điểm trong miền `[0, 10]` được giữ cho thống kê.
- Không tự điền điểm còn thiếu.
- Mỗi thống kê dùng mẫu số là số điểm hợp lệ của đúng môn và năm đó.
- Cỡ mẫu của từng môn được báo cáo riêng, không giả định các môn có cùng số thí sinh.
- Dữ liệu nguồn phải được tải đầy đủ. Nếu tệp 2025 vẫn chỉ là Git LFS pointer, chương trình dừng với thông báo hướng dẫn thay vì đọc nhầm pointer như CSV.

## 3. Phương pháp thống kê

### 3.1. Thống kê vị trí và độ phân tán

| Chỉ số | Ký hiệu / cách hiểu | Câu hỏi trả lời |
|---|---|---|
| Số điểm hợp lệ | (n) | Có bao nhiêu điểm được dùng cho môn-năm này? |
| Trung bình | (ar{x}) | Mức điểm trung bình của các điểm quan sát là bao nhiêu? |
| Trung vị | (Q_2) | Điểm nằm giữa phân phối là bao nhiêu? |
| Độ lệch chuẩn mẫu | (s) | Điểm số phân tán quanh trung bình ở mức nào? |
| Phân vị 25% và 75% | (Q_1, Q_3) | Hai ranh giới của khoảng giữa 50% điểm là gì? |
| Khoảng tứ phân vị | (IQR=Q_3-Q_1) | Độ rộng của 50% điểm ở giữa thay đổi thế nào? |
| Min, max | Giá trị nhỏ nhất/lớn nhất | Điểm quan sát trải từ đâu đến đâu? |

Trung bình nhạy với các giá trị ở hai đầu phân phối; trung vị ít nhạy hơn với điểm cực thấp hoặc cực cao. Nếu trung bình thay đổi nhiều hơn trung vị, nên kiểm tra histogram, KDE và tỷ lệ theo ngưỡng để xem thay đổi có tập trung ở một phần phân phối hay không. Độ lệch chuẩn lớn hơn biểu thị mức phân tán lớn hơn theo chỉ số này, nhưng không mô tả toàn bộ hình dạng phân phối.

### 3.2. Độ lệch và độ nhọn

- **Skewness (độ lệch):** giá trị dương thường biểu thị đuôi phải dài hơn; giá trị âm thường biểu thị đuôi trái dài hơn; gần 0 gợi ý phân phối cân đối hơn nhưng không chứng minh phân phối chuẩn.
- **Excess kurtosis (độ nhọn dư):** được tính theo quy ước trong pandas; phân phối chuẩn có giá trị tham chiếu 0. Giá trị dương có thể phản ánh đuôi nặng/đỉnh nhọn hơn theo định nghĩa mô-men; giá trị âm có thể phản ánh phân phối bẹt hơn. Không diễn giải chỉ số này độc lập với biểu đồ.
- Hai chỉ số có thể nhạy với điểm cực trị và cỡ mẫu; cần đọc cùng các chỉ số khác.

### 3.3. Tỷ lệ theo ngưỡng

Báo cáo tính bốn tỷ lệ cho từng môn-năm:

- (P(X leq 1)): tỷ lệ điểm không quá 1.
- (P(X < 5)): tỷ lệ điểm dưới 5.
- (P(X geq 8)): tỷ lệ điểm từ 8 trở lên.
- (P(X geq 9)): tỷ lệ điểm từ 9 trở lên.

Các tỷ lệ được tính bằng số điểm thỏa điều kiện chia cho số điểm hợp lệ của môn-năm tương ứng, nhân 100%. Khi so sánh hai năm, **chênh lệch tỷ lệ được diễn giải bằng điểm phần trăm**, không gọi là phần trăm tăng tương đối. Ví dụ, từ 20% lên 25% là tăng 5 điểm phần trăm.

Các ngưỡng trên là mốc mô tả để đọc phân phối, không thay thế tiêu chí xét tuyển hoặc định nghĩa chính thức về đỗ/trượt trong từng bối cảnh.

## 4. Trực quan hóa và cách đọc

Mỗi môn được thể hiện bằng bốn loại biểu đồ, dùng trục điểm từ 0 đến 10.

### 4.1. Histogram

Histogram chia điểm thành các khoảng và thể hiện mật độ/tần suất tương đối. Hai năm dùng chung các khoảng điểm để việc so sánh có ý nghĩa.

**Cần quan sát:** vị trí đỉnh, số đỉnh, độ rộng, độ lệch, phần đuôi và các vùng điểm có mật độ cao. Một đỉnh dịch sang phải có thể gợi ý điểm tập trung ở vùng cao hơn, nhưng cần đối chiếu trung bình, trung vị và các tỷ lệ ngưỡng.

### 4.2. KDE (Kernel Density Estimation)

KDE làm mượt histogram để giúp quan sát hình dạng tổng thể. Mức làm mượt có thể che khuất đỉnh nhỏ hoặc tạo cảm giác đường cong liên tục hơn dữ liệu điểm rời rạc.

**Cần quan sát:** hai đường mật độ có dịch chuyển không, vùng nào tăng/giảm mật độ tương đối, và kết luận đó có nhất quán với histogram hay không. KDE là công cụ mô tả, không phải bằng chứng kiểm định thống kê.

### 4.3. Boxplot

Boxplot hiển thị trung vị, khoảng tứ phân vị và các điểm râu theo quy ước của biểu đồ. Trong biểu đồ này, điểm ngoại lệ không được vẽ để tránh quá nhiều dấu điểm, nhưng dữ liệu gốc không bị xóa khỏi thống kê.

**Cần quan sát:** trung vị, chiều cao hộp (IQR), độ bất đối xứng của hộp và độ dài râu. Boxplot tóm tắt tốt vị trí và độ phân tán nhưng không thể hiện đầy đủ nhiều đỉnh của phân phối.

### 4.4. Violin plot

Violin plot biểu diễn mật độ theo chiều dọc, kèm trung vị và các cực trị theo cấu hình vẽ.

**Cần quan sát:** phần phình rộng cho biết vùng điểm có mật độ cao hơn; phần hẹp biểu thị mật độ thấp hơn. Hình dạng violin giúp phát hiện cấu trúc nhiều đỉnh mà boxplot không thể hiện, nhưng phụ thuộc cách ước lượng mật độ.

### Nguyên tắc đối chiếu

Không kết luận từ một biểu đồ riêng lẻ. Với mỗi môn, đọc theo thứ tự: **cỡ mẫu → trung bình/trung vị → độ lệch chuẩn/IQR → tỷ lệ ngưỡng → histogram/KDE → boxplot/violin**. Nếu các dấu hiệu không đồng nhất, báo cáo sự khác nhau thay vì chọn một chỉ số có lợi cho câu chuyện.

## 5. Kết quả định lượng và nhận xét theo môn

Các con số chính thức của báo cáo được tạo từ dữ liệu cục bộ khi chạy chương trình. Bảng đầy đủ nằm trong `outputs/score_distribution/thong_ke_mo_ta_2023_2025.csv`; bản dữ liệu điểm dạng dài nằm trong `outputs/score_distribution/diem_long_2023_2025.csv`. Báo cáo Word `outputs/score_distribution/bao_cao_phan_tich_pho_diem_2023_2025.docx` gồm bảng số liệu, biểu đồ và nhận xét theo từng môn được sinh từ kết quả thực tế.

Với từng môn, nhận xét cần ghi rõ:

1. Số điểm hợp lệ năm 2023 và năm 2025.
2. Trung bình và trung vị của mỗi năm, cùng chênh lệch 2025 trừ 2023.
3. Độ lệch chuẩn và thay đổi về độ phân tán.
4. Chênh lệch điểm phần trăm của bốn tỷ lệ ngưỡng.
5. Hình dạng phân phối thể hiện trên histogram/KDE và kiểm tra chéo bằng boxplot/violin.
6. Một câu kết luận mô tả, không gán nguyên nhân chưa được kiểm chứng.

Không đưa số liệu định lượng chưa được tính từ tệp dữ liệu vào bản báo cáo. Nếu thiếu một năm cho một môn, ghi rõ chưa đủ cơ sở so sánh trực tiếp thay vì tự suy diễn.

## 6. Kịch bản thuyết trình gợi ý

### Mở đầu

“Nhóm em tiếp tục dự án phân tích dữ liệu điểm thi THPT, sử dụng bộ dữ liệu năm 2023 và năm 2025 đã được chuẩn hóa mã tỉnh ở các tuần trước. Trong phần này, nhóm tập trung mô tả và so sánh phân phối điểm theo từng môn, xem vị trí trung tâm, mức phân tán, hình dạng và tỷ lệ ở các vùng điểm thay đổi ra sao.”

### Dữ liệu và cách làm

“Trước khi tính toán, nhóm thống nhất tên môn giữa hai bộ dữ liệu, chuyển điểm sang dạng số và chỉ sử dụng điểm nằm trong khoảng từ 0 đến 10. Nhóm không tự điền các điểm thiếu. Mỗi môn có số lượng điểm hợp lệ riêng nên các bảng đều ghi rõ cỡ mẫu.”

### Giải thích thống kê

“Trung bình cho biết mức điểm trung bình, còn trung vị cho biết điểm ở giữa phân phối. Độ lệch chuẩn và khoảng tứ phân vị mô tả độ phân tán. Skewness và excess kurtosis hỗ trợ đọc hình dạng, nhưng cần được kiểm tra bằng biểu đồ. Nhóm cũng so sánh tỷ lệ điểm không quá 1, dưới 5, từ 8 trở lên và từ 9 trở lên.”

### Trình bày từng môn

“Với môn [tên môn], số điểm hợp lệ là [năm 2023] và [năm 2025]. Trung bình thay đổi [mức chênh lệch] điểm, trung vị thay đổi [mức chênh lệch] điểm. Độ lệch chuẩn thay đổi [mức chênh lệch], trong khi tỷ lệ dưới 5 thay đổi [điểm phần trăm] và tỷ lệ từ 8 trở lên thay đổi [điểm phần trăm]. Histogram và KDE cho thấy [nhận xét dựa trên hình], còn boxplot và violin plot giúp kiểm tra thêm trung vị, độ phân tán và hình dạng. Đây là khác biệt mô tả giữa hai bộ dữ liệu, chưa phải lời giải thích nguyên nhân.”

*Lưu ý:* Khi trình bày thật, thay các phần trong ngoặc vuông bằng kết quả đã sinh trong DOCX/CSV. Không đọc nguyên kịch bản mẫu nếu chưa kiểm tra bảng và biểu đồ tương ứng.

### Kết luận

“Nhìn chung, việc kết hợp thống kê mô tả với nhiều loại biểu đồ giúp tránh phụ thuộc vào một con số duy nhất. Tuy nhiên, hai kỳ thi diễn ra ở hai năm khác nhau nên đề thi, quy chế, cơ cấu thí sinh và lựa chọn môn có thể khác nhau. Vì vậy, nhóm chỉ kết luận về khác biệt quan sát được trong phân phối điểm, không khẳng định nguyên nhân hoặc quy đổi trực tiếp thành mức năng lực.”

## 7. Giới hạn và nguy cơ diễn giải sai

- Hai năm là hai kỳ thi khác nhau; khác biệt mô tả không tự chứng minh độ khó đề thi hoặc năng lực thí sinh thay đổi.
- Thành phần thí sinh và số lượng điểm hợp lệ có thể khác nhau giữa môn và năm.
- Các môn không tương đương về nội dung hoặc quy chế không nên gộp thành một môn so sánh trực tiếp.
- Không dùng số dòng toàn bộ dataset làm mẫu số cho tỷ lệ của một môn; phải dùng số điểm hợp lệ của môn đó.
- Điểm thiếu không được xem là điểm 0, và không được tự động điền trung bình/trung vị.
- Histogram phụ thuộc cách chia bin; KDE phụ thuộc mức làm mượt; violin plot cũng phụ thuộc ước lượng mật độ.
- Skewness và kurtosis không đủ để xác nhận phân phối chuẩn.
- Báo cáo hiện tại là phân tích mô tả. Không có kiểm định giả thuyết, khoảng tin cậy hay mô hình nhân quả trong phạm vi này.

## 8. Tái lập và kiểm tra

Từ thư mục gốc của repository, tạo môi trường Python và cài thư viện:

```bash
python -m pip install -r requirements-score-distribution.txt
git lfs pull
python -m pytest tests/test_week6_score_distribution.py -q
python -m src.week6_score_distribution
```

Nếu chỉ muốn chỉ định đường dẫn hoặc thư mục đầu ra khác:

```bash
python -m src.week6_score_distribution --2023 data/processed/week3/exam_2023.parquet --2025 data/dataset_diem_thi_thpt_2025.csv --out outputs/score_distribution
```

Sau khi chạy thành công, kiểm tra tối thiểu:

- `thong_ke_mo_ta_2023_2025.csv`: đủ các môn-năm, cỡ mẫu và chỉ số.
- `diem_long_2023_2025.csv`: các điểm hợp lệ dùng trong phân tích.
- `figures/`: bốn biểu đồ cho từng môn được nhận diện.
- `bao_cao_phan_tich_pho_diem_2023_2025.docx`: báo cáo tổng hợp, nhận xét từng môn và kịch bản trình bày.
- `run_metadata.json`: đường dẫn nguồn, năm, danh sách môn và số điểm hợp lệ.

Nếu chương trình báo tệp 2025 vẫn là Git LFS pointer, chạy `git lfs pull` trong repository có quyền truy cập và xác nhận tệp CSV có dữ liệu thật trước khi chạy lại. Không xem việc chạy test đơn vị thành công là bằng chứng pipeline đã chạy thành công trên dữ liệu đầy đủ.

## 9. Sản phẩm bàn giao

| Sản phẩm | Nội dung |
|---|---|
| Mã phân tích | `src/week6_score_distribution.py` |
| Notebook | `notebooks/week6/phan_tich_pho_diem_2023_2025.ipynb` |
| Kiểm thử | `tests/test_week6_score_distribution.py` |
| Báo cáo mô tả phương pháp | `docs/week6/week6_report+bao_cao.md` |
| Hướng dẫn đầu ra | `docs/week6/README_score_distribution.md` |
| Bản rà soát | `docs/week6/week6_review+kiem_tra_bai.md` |
| Bảng thống kê và dữ liệu phân tích | `outputs/score_distribution/*.csv` |
| Hình minh họa | `outputs/score_distribution/figures/*.png` |
| Báo cáo Word hoàn chỉnh sau khi chạy | `outputs/score_distribution/bao_cao_phan_tich_pho_diem_2023_2025.docx` |

**Kết luận bàn giao:** mã nguồn đã được chuẩn bị để sinh bảng thống kê, biểu đồ, nhận xét theo từng môn và báo cáo Word. Chỉ được xem báo cáo Word là bản kết quả cuối cùng sau khi chạy thành công với hai tệp dữ liệu thật và kiểm tra đầu ra; không thay thế số liệu chưa chạy bằng phỏng đoán.
