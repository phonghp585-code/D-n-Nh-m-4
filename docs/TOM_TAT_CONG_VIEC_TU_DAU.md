# Tóm tắt công việc từ đầu — Phân tích điểm thi THPT 2023 và 2025

Ngày cập nhật: **18/10/2026**. Nhánh đưa lên GitHub: **thanh**.


**Phạm vi báo cáo hiện tại:** Theo yêu cầu ngày 18/10/2026, báo cáo chỉ chứa phần 3 và nằm tại [docs/phan_3_to_hop_mon_2023_2025.md](phan_3_to_hop_mon_2023_2025.md), trong thư mục `docs` đã có. Các mục về phần 5 dưới đây ghi lại công việc từng thực hiện; mã/kết quả tương quan được giữ riêng và không nằm trong báo cáo chính.

## 1. Mục tiêu và phạm vi đã chốt

Mục tiêu là so sánh kết quả thi trong bối cảnh chuyển từ chương trình 2006 sang chương trình 2018, thay đổi cơ chế chọn môn và định dạng đề thi. Trọng tâm của phần việc này:

- **Phần 3:** phân tích đủ 24 mã tổ hợp theo dataset nhan, so sánh phân phối tổng điểm, quy mô người đủ điểm, ngưỡng top 10%/20% và cơ cấu môn có điểm.
- **Phần 5:** phân tích tương quan giữa các môn, thay đổi giữa hai năm và kiểm tra trong nhóm đủ điểm tổ hợp.
- Theo các yêu cầu bổ sung: kiểm chứng phổ điểm trên internet, diễn giải ngay dưới bảng/hình, phân tích vùng điểm cao, đặt giả thuyết nghiên cứu và phân nhóm theo hồ sơ điểm các môn khác.

Người dùng đã xác nhận dataset 2025 của nhan chỉ gồm **CT2018**. Cách gán tổ hợp cuối cùng giữ **đa nhãn**: một thí sinh có thể đủ nhiều tổ hợp, giống nhan; không ép mỗi người vào một khối duy nhất. PCA không nằm trong sản phẩm cuối.

## 2. Repository, dữ liệu và việc dọn file

- Kiểm tra các branch và dữ liệu hiện có; lấy dữ liệu cần thiết từ nhánh nhan, tái sử dụng các bản đã có trên máy.
- Làm việc trên nhánh thanh, giữ các phần tuần 3–6 đã có trong repository.
- Giữ nguyên dữ liệu gốc; lưu hash và chính sách xử lý để có thể kiểm tra lại.
- Dọn các file tạm, báo cáo phân tán và nhật ký triển khai thừa. Giữ một báo cáo phân tích chính. File Markdown này là bản tóm tắt riêng được người dùng yêu cầu thêm trước khi push.
- Giữ cả ảnh tuần 5 đã có trên máy: `outputs/week5/figures/ngoai_ngu_vi_sao_khong_co_ngoai_le.png`.
- Dataset 2025 có dung lượng 121.434.420 byte, được đưa lên bằng **Git LFS**; dữ liệu khớp nội dung ở nhánh nhan. Môi trường `.venv`, cache và thư mục tạm không đưa vào Git.

| Đầu vào | Phạm vi | Số dòng | Có ít nhất một điểm |
|---|---|---:|---:|
| `data/raw/original.csv` | 2023 — CT2006 | 1.022.060 | 1.017.584 |
| `data/dataset_diem_thi_thpt_2025.csv` | 2025 — CT2018 | 1.131.136 | 1.130.984 |

Số dòng trong file, số người có điểm và số đăng ký chính thức là những đại lượng khác nhau. Không coi chúng là cùng một mẫu số.

## 3. Chuẩn hóa và kiểm chứng dữ liệu

- Chuẩn hóa tên môn; giữ SBD dạng chuỗi để không mất số 0 đầu.
- Kiểm tra SBD trùng/sai định dạng, điểm ngoài phạm vi và kiểu dữ liệu.
- Chỉ dùng điểm hợp lệ trong **[0,10]**, giữ điểm 0; không điền điểm thiếu để tạo tổ hợp hoặc tính tương quan.
- Tách **Tiếng Anh mã N1** khỏi **Ngoại ngữ mọi mã N1–N7**. Anh là tập con của Ngoại ngữ, không cộng hai mục khi đếm số môn.
- Đếm riêng từng môn của cả hai năm, không lấy chung số người thi KHTN/KHXH làm số của từng môn.
- Kiểm tra lại toàn bộ 24 tổng điểm có sẵn và nhãn tổ hợp của nhan năm 2025: **không có sai khác** với phép tính từ các môn thành phần.

Các trường hợp người dùng yêu cầu kiểm tra kỹ:

- Tiếng Anh: **876.102 → 351.848** người có điểm; Ngoại ngữ mọi mã: **880.997 → 357.723**.
- Năm 2023: Lý **327.189**, Hóa **328.118**, Sinh **324.625**, Sử **683.447**, Địa **682.134**; mỗi số được đếm từ đúng cột môn.
- B00 tính lại được **324.554 → 44.964** người đủ Toán/Hóa/Sinh. Số 2023 khớp các bản dữ liệu gốc và xử lý tuần 3/4/5; số 2025 khớp tổng và nhãn nhan.
- Mức giảm số người đủ B00 không phải mức giảm số người đăng ký xét tuyển B00. Cơ chế năm 2023 tạo nhiều tổ hợp đồng thời hơn năm 2025.

## 4. Phân tích đủ 24 tổ hợp

Các mã: **A00, A01, A02, A08, A09, B00, B08, C00, C01, C02, C03, C04, C14, C19, C20, D01, D07, D08, D09, D10, D14, D15, D66, D84**.

Đã tạo:

- Bảng **48 dòng tổ hợp–năm**, gồm số người đủ ba môn, trung bình, trung vị, SD, IQR và phân vị.
- Bảng chênh lệch của **24 tổ hợp** và **96 dòng ngưỡng top**, gồm số người bằng/vượt ngưỡng.
- Histogram, ECDF và boxplot chia trang để bao phủ toàn bộ 24 mã.
- Ngưỡng **P80 = top 20%**, **P90 = top 10%**, dùng inverse empirical CDF/nearest rank, giữ đồng hạng. Đây là ngưỡng phân phối điểm, không phải điểm trúng tuyển đại học.
- Đánh dấu 7 mã đổi GDCD sang GDKT&PL: A08, A09, C14, C19, C20, D66, D84. Giữ B08/D08 theo nguồn nhưng ghi rõ hai mã cùng bộ môn.

Ví dụ: P90 A00 tăng **24,45 → 25,25** dù trung bình giảm; P90 B00 tăng **23,95 → 24,75**; P90 C00 tăng **23,25 → 25,25**; P90 D01 giảm **23,85 → 22,50**.

## 5. Xu hướng môn thi và bằng chứng qua phổ điểm

- So sánh số người có điểm và tỷ lệ có điểm từng môn; trình bày rõ tăng/giảm số người, phần trăm tăng trưởng và điểm phần trăm thay đổi tỷ lệ.
- Tỷ lệ có điểm trên toàn thí sinh dùng mẫu số người có ít nhất một điểm trong cùng năm. Tỷ lệ điểm dưới 5/từ 8/từ 9 dùng người có điểm của riêng môn đó.
- Tạo phổ điểm chuẩn hóa cho các môn chung, kèm trung bình, trung vị, tỷ lệ dưới 5/từ 8/từ 9; bổ sung số lượng và tỷ lệ điểm 10 cho tất cả môn hiện có. GDCD/GDKT&PL và các môn mới được giữ riêng.
- Phân rã trung bình theo bốn vùng không chồng lấn: **0–<5, 5–<8, 8–<9, 9–10**. Tổng đóng góp các vùng bằng đúng trung bình toàn môn.

Các phát hiện đã ghi rõ trong báo cáo:

- Lý và Sử: tỷ lệ dưới 5 giảm, từ 8 tăng.
- Địa: cả dưới 5 và từ 8 tăng; không diễn giải toàn bộ phổ cùng dịch sang phải.
- Hóa và Sinh: trung bình giảm nhưng tỷ lệ từ 9 tăng; phần giữa và vùng rất cao thay đổi khác hướng.
- Anh: dưới 5 giảm, trung vị nhích lên nhưng từ 8 thu hẹp mạnh; trung bình giảm nhẹ.
- Văn: trung bình/trung vị và tỷ lệ từ 8 tăng, nhưng tỷ lệ từ 9 giảm.
- Hóa từ 9 tăng **11.238 → 17.839 người**. Sinh từ 9 giảm **5.451 → 1.775 người** dù tỷ lệ tăng. Bảng báo cáo dùng các số này; đã đính chính những câu nói nhầm trong buổi trao đổi bằng giọng nói.

## 6. Tương quan và hồ sơ điểm thí sinh

**Tương quan:**

- Pearson và Spearman cho 8 môn chung, **28 cặp khác nhau/năm**; CSV giữ đủ ma trận 8×8 của mỗi năm.
- Lọc đủ điểm riêng từng cặp; Spearman xếp hạng sau khi lọc, giữ đồng hạng bằng hạng trung bình. Trường hợp thiếu mẫu hoặc không có phương sai để hệ số trống.
- Heatmap hệ số và số mẫu, biểu đồ mật độ cho 5 cặp đáng chú ý, bảng thay đổi tương quan.
- **30 dòng** kiểm tra trong 5 tổ hợp A00/A01/B00/C00/D01 và **6 dòng** kiểm tra điểm cao đồng xuất hiện.
- Ví dụ Pearson Sử–Địa tăng khoảng **0,608 → 0,759**, Toán–Anh giảm khoảng **0,592 → 0,497**.

**Phân nhóm hồ sơ điểm đã tính thêm:**

- Chia theo thứ hạng Toán trong từng năm; riêng khi phân tích Toán dùng Văn. Điểm của chính môn mục tiêu không được dùng để tạo nhóm.
- Bốn nhóm thứ hạng và một nhóm thiếu điểm tham chiếu; đồng điểm không bị chia tùy ý, thiếu điểm không thành 0.
- **110 dòng nhóm–môn–năm**, **45 dòng đóng góp nhóm**, **9 dòng tổng hợp thay đổi** và một heatmap đóng góp vào biến động tỷ lệ từ 9.
- Phân rã đối xứng thành phần do cơ cấu nhóm thay đổi và phần do kết quả trong nhóm thay đổi, cho trung bình và tỷ lệ từ 9/điểm 10. Các thành phần cộng đúng về chênh lệch toàn môn.
- Lý/Hóa tăng tỷ lệ từ 9 chủ yếu ở nhóm thứ hạng Toán cao; Sử/Địa tăng ở nhiều nhóm. Với Anh, tỷ trọng nhóm thứ hạng Toán cao tăng nhưng tỷ lệ Anh từ 9 ngay trong nhóm giảm.

Nhóm thứ hạng chỉ là vị trí tương đối trong từng năm, chưa phải năng lực đầu vào tương đương giữa hai đề.

## 7. Đối chiếu nguồn công bố trên internet

Lưu PDF báo cáo phổ điểm 2025, HTML bảng phổ điểm 2023 và bảng tham chiếu có nguồn, trang và hash trong `data/external/verification/`.

- **2025:** 106/106 chỉ số đối chiếu khớp; 420/420 khoảng phổ điểm khớp dữ liệu CSV.
- **2023:** phát hiện số người của Toán, Lý, Hóa trong file cao hơn công bố mỗi môn 1 người; không tự xóa bản ghi khi chưa rõ nguyên nhân.
- Văn 2023: số dưới 5 trong điểm gốc cao hơn bảng công bố 34. Có 3.962 điểm ngoài lưới 0,25; phép đối chiếu độ nhạy làm tròn về mốc 0,25 khớp bảng tần suất hiển thị. Không làm tròn điểm gốc dùng cho tổ hợp/tương quan và không coi phép khớp này là bằng chứng xác nhận quy trình xử lý của Bộ.
- Đối chiếu điều kiện thi, môn bắt buộc/tự chọn, dạng đúng/sai, trả lời ngắn, phạm vi áp dụng và cấu trúc Văn 2023/2025 bằng nguồn công bố chính thức.

Kết quả chi tiết ở `outputs/audits/external_*`. Khớp phổ tổng hợp không xác thực độc lập từng điểm của từng thí sinh.

## 8. Giả thuyết nghiên cứu và giới hạn

Đã bổ sung các giả thuyết về kết quả học tập, tự lựa chọn môn, cấu trúc/cách chấm và thành phần nhóm dự thi; nêu bằng chứng cần thêm để phân biệt chúng. Văn và Anh có cách diễn giải riêng phù hợp hình thức thi.

Hai năm dữ liệu mô tả được thay đổi phân phối và nhóm dự thi, nhưng chưa tách được số điểm tăng/giảm do riêng chương trình 2018. Tỷ lệ có điểm chưa phải mức yêu thích hay tỷ lệ đăng ký. Phổ rộng hơn chưa tự chứng minh độ phân biệt năng lực tốt hơn.

Phân nhóm theo trường/địa phương và phát hiện bất thường chưa được triển khai. Điểm 9/10 tăng không đủ kết luận gian lận; báo cáo không gắn nhãn cá nhân hay địa phương.

## 9. Sản phẩm và cách chạy lại

| Sản phẩm | Đường dẫn |
|---|---|
| Báo cáo phân tích chính — 21 bảng, 13 hình, đều có diễn giải ngay bên dưới | [Phần 3 — Tổ hợp môn 2023/2025](phan_3_to_hop_mon_2023_2025.md) |
| Hướng dẫn kỹ thuật và quy tắc | [HUONG_DAN_PHAN_3.md](HUONG_DAN_PHAN_3.md) |
| Notebook tổ hợp | [analysis.ipynb](../notebooks/combinations/analysis.ipynb) |
| Notebook tương quan | [analysis.ipynb](../notebooks/correlations/analysis.ipynb) |
| Bảng/hình tổ hợp, tương quan | `outputs/combinations/`, `outputs/correlations/` |
| Đối chiếu nguồn, phổ môn, vùng điểm, hồ sơ nhóm | `outputs/audits/` |
| Metadata, hash và xác minh | `outputs/parts3_5_run.json`, `parts3_5_manifest.json`, `parts3_5_completion_audit.json` |

Tái lập từ gốc repository:

```powershell
git lfs pull
python -m pip install -r requirements-parts3-5.txt
python -X utf8 -m src.run_parts3_5 --rerun
python -X utf8 -m src.verify_external_scores
python -X utf8 -m src.run_parts3_5 --verify-only
```

Các notebook đã được thực thi thành công ở bước trước. Sau các lần bổ sung phần diễn giải/phân nhóm, phần hiển thị báo cáo trong notebook được đồng bộ; không tuyên bố đã thực thi lại toàn notebook ở mỗi lần sửa.

## 10. Lịch sử xác minh

- Chạy lại toàn bộ suite ngày 17/10/2026: **74 test, 73 đạt, 1 lỗi nền, không có failure**. Toàn bộ **47 test liên quan phần mới** đều đạt.
- Trước khi xoá bộ test theo yêu cầu ngày 18/10/2026, đã chạy lại **75 test: 74 đạt, 1 lỗi nền cũ**; có thêm kiểm thử đường dẫn và phạm vi báo cáo phần 3. Đây là kết quả lịch sử; các file kiểm thử sau đó đã được xoá, không coi việc xoá là sửa lỗi nền.
- Lỗi nền: `test_week6_score_distribution.TestScoreDistribution.test_alias_mapping_and_range`; `src/week6_score_distribution.py` tạo DataFrame từ scalar không có index. Lỗi đã tồn tại trước phần việc này và không được sửa trong lần push này. Không ghi toàn bộ suite xanh.
- Kiểm tra lại hash dữ liệu gốc, tính đầy đủ của 24 tổ hợp, tổng/nhãn nhan, đồng hạng, tính đối xứng tương quan, đóng góp vùng điểm, nhóm tham chiếu và đường dẫn trong báo cáo.
- Git LFS được cấu hình cho dataset 2025. Đưa toàn bộ file mới của dự án lên nhánh thanh, bao gồm dữ liệu, mã nguồn, test, notebook, bảng, hình, nguồn đối chiếu, báo cáo và bản tóm tắt này.

## 11. Đổi tên và tách báo cáo theo yêu cầu ngày 18/10/2026

- Báo cáo chính chỉ còn phần 3: đủ 24 tổ hợp, ngưỡng P80/P90, cơ cấu môn, phổ điểm, phân nhóm hồ sơ và giả thuyết giải thích đã yêu cầu.
- Đặt tên rõ nội dung: `docs/phan_3_to_hop_mon_2023_2025.md`; dùng thư mục `docs` sẵn có, không tạo thư mục báo cáo mới.
- Loại khỏi báo cáo phần đọc nhanh tương quan và toàn bộ phần 5: tổng cộng 5 bảng và 12 hình. Báo cáo phần 3 còn 21 bảng và 13 hình, đều có diễn giải ngay bên dưới.
- Đổi hướng dẫn kỹ thuật thành `docs/HUONG_DAN_PHAN_3.md`; cập nhật README ở gốc dự án bằng liên kết báo cáo và vị trí file nổi bật.
- Cập nhật bộ sinh báo cáo để không ghép lại phần 5 khi chạy lại; cập nhật đường dẫn trong notebook tổ hợp và bỏ việc chèn báo cáo chung vào notebook tương quan.
- Giữ nguyên dữ liệu gốc, các bảng/hình đã tính và mã phân tích tương quan; không xóa sản phẩm phần 5 đã làm.
- Cập nhật metadata xác minh; đã kiểm tra báo cáo phần 3 không cần đọc đầu ra tương quan.
- Theo yêu cầu tiếp theo, xoá toàn bộ **11 file kiểm thử Python** trong thư mục `tests` và cache kiểm thử; bỏ lệnh chạy test khỏi README/hướng dẫn. Giữ mã phân tích trong `src` và lệnh xác minh đầu ra `--verify-only`.
