# Phần 3 và 5: 2023 — CT2006 / 2025 — CT2018

## Phạm vi

- Phần 3: đủ 24 mã theo dataset nhan: A00/A01/A02/A08/A09/B00/B08/C00/C01/C02/C03/C04/C14/C19/C20/D01/D07/D08/D09/D10/D14/D15/D66/D84; phân phối tổng, tỷ lệ đủ điểm, cơ cấu môn có điểm, cặp môn đồng xuất hiện; ngưỡng top 20%/10% với đồng hạng. Bảng có 48 hàng tổ hợp–cohort, 24 delta và 96 ngưỡng có đồng hạng. Biểu đồ phân phối/boxplot chia 4 trang để bao phủ đủ 24 mã.
- Phần 5: Pearson/Spearman và cỡ mẫu từng cặp, delta giữa hai cohort, hình mật độ cặp điểm, kiểm tra trong từng nhóm tổ hợp và liên hệ giữa nhóm điểm cao.
- Không triển khai thêm phần 1/2, mô hình dự đoán hay địa lý. Dataset 2025 chỉ gồm CT2018 theo xác nhận người dùng.
- Theo yêu cầu giải thích tăng/giảm bằng phổ điểm, phần bổ trợ có histogram chuẩn hóa và bảng trung vị, tỷ lệ dưới 5/từ 8/từ 9 của các môn chung. Đây là bằng chứng mô tả phục vụ phần 3, không phải ước lượng tác động nhân quả. Tái lập riêng bằng `python -m src.subject_distribution_evidence`, sau đó `python -m src.run_parts3_5` để cập nhật báo cáo; lệnh `--rerun` cũng sinh phần này.
- Phần ý tưởng nghiên cứu bổ sung số lượng/tỷ lệ từ 9 và điểm 10 cho mọi môn hiện có (giữ riêng GDCD/GDKT&PL), phân rã trung bình theo bốn vùng điểm, các giả thuyết về định dạng/giảng dạy/tự lựa chọn và hướng xác định nhóm đóng góp. Phân nhóm địa phương/trường và phát hiện bất thường mới ở mức đề xuất, chưa được chạy. Dữ liệu bổ trợ: `outputs/audits/subject_distribution_evidence.csv`, `subject_score_band_contributions.csv` và metadata cùng thư mục. Không kết luận gian lận từ phổ điểm.
- Đã phân tích hồ sơ điểm theo bốn nhóm thứ hạng Toán trong từng năm (riêng môn Toán dùng Văn), giữ đồng điểm bằng hạng trung bình và thiếu điểm thành nhóm riêng. Các CSV `subject_group_profiles.csv`, `subject_group_decomposition.csv`, `subject_group_changes.csv` trong `outputs/audits/` cho biết nhóm đóng góp vào chênh lệch trung bình, tỷ lệ ≥9 và điểm 10. Phân rã đối xứng chỉ là mô tả, không phải điều chỉnh năng lực tương đương hay ước lượng tác động nhân quả. Cùng lệnh tái lập phổ điểm ở trên cũng sinh các bảng này.

## Chạy lại

Từ thư mục gốc, dùng môi trường dự án:

```powershell
& ./.venv/Scripts/python.exe -m pip install -r requirements-parts3-5.txt
& ./.venv/Scripts/python.exe -X utf8 -m src.run_parts3_5 --rerun
& ./.venv/Scripts/python.exe -X utf8 -m src.run_parts3_5 --verify-only
& ./.venv/Scripts/python.exe -X utf8 -m src.verify_external_scores
& ./.venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -v
```

Đầu vào mặc định:

- `data/raw/original.csv`: 2023 — CT2006.
- `data/dataset_diem_thi_thpt_2025.csv`: 2025 — CT2018, phải là dữ liệu thực thay vì con trỏ LFS.

Có thể đổi đường dẫn bằng `--data2023`, `--data2025`, và ghi kết quả ra vị trí khác với `--output-root`. Lệnh không có `--rerun` kiểm tra/đọc kết quả có sẵn nếu đã tồn tại; `--rerun` tính lại từ dữ liệu gốc. Hai CSV nguồn không bị sửa.

## Đọc kết quả

Báo cáo duy nhất: [bao_cao_phan_3_5.md](bao_cao_phan_3_5.md).

| Phần | Notebook | Bảng và hình |
|---|---|---|
| 3 | `notebooks/combinations/analysis.ipynb` | `outputs/combinations/` |
| 5 | `notebooks/correlations/analysis.ipynb` | `outputs/correlations/` |

Notebook mặc định đọc các bảng/hình đã tạo và kiểm tra tính nhất quán. Đặt `RERUN=True` trong notebook để tính lại cả hai phần. Dùng kernel Python của `.venv`.

## Các quy tắc quan trọng

- Không điền thiếu; giữ điểm 0. Không xóa điểm hợp lệ do IQR.
- A01/D01 chỉ dùng Tiếng Anh mã N1. Ngoại ngữ mọi mã có dòng cơ cấu riêng, không cộng trùng Anh khi đếm số môn thi.
- Tổng tổ hợp chỉ có khi đủ cả ba điểm. Làm tròn 10 chữ số thập phân để loại sai số số thực của phép cộng, không làm tròn điểm nguồn.
- P80/P90 dùng inverse empirical CDF/nearest rank. Công bố cả số người bằng/vượt/đạt ngưỡng. Đây là ngưỡng phân phối, không phải điểm chuẩn trúng tuyển.
- Tỷ lệ có điểm có mẫu số chính là số dòng có ít nhất một điểm thi; bảng kèm mẫu số toàn bộ dòng để kiểm tra độ nhạy. Không khẳng định ô trống là không chọn thi.
- Pearson/Spearman lọc đủ điểm riêng từng cặp. Spearman xếp hạng sau lọc cặp, average ranks cho đồng hạng. n<100 hoặc môn không phương sai: hệ số để trống.
- Một người có thể thuộc nhiều tổ hợp. Không cộng số người các nhóm thành tổng thí sinh.
- Người dùng đã xác nhận giữ đa nhãn giống nhan. `combination_membership_validation.csv` đối chiếu từng mã với nhãn nguồn; `membership_count_distribution.csv` cho biết một người có bao nhiêu tổ hợp đủ điểm. Không áp quy tắc gán duy nhất.
- Bảy mã A08/A09/C14/C19/C20/D66/D84 so sánh GDCD (2023 — CT2006) với GDKT&PL (2025 — CT2018), được gắn cờ khác nội dung. B08/D08 cùng ba môn trong dataset, giữ hai mã để khớp nguồn nhưng không phải hai quần thể độc lập. Danh mục đầy đủ theo từng năm: `outputs/combinations/combination_mapping.csv`.
- Phần tương quan kiểm tra độ nhạy trên năm nhóm cùng tên môn A00/A01/B00/C00/D01. Phạm vi phần 3 vẫn là đủ 24 mã; các nhóm kiểm tra độ nhạy không giới hạn bảng so sánh tổ hợp.
- So sánh quan sát không phân rã được ảnh hưởng riêng của chương trình, cách thi, đề, năng lực và lựa chọn môn.

## Bằng chứng tái lập

Phần đối chiếu internet dùng `data/external/verification/official_reference.json`, PDF gốc 2025 và HTML bảng công bố 2023 lưu cùng thư mục. `src/verify_external_scores.py` tính lại số bài, chỉ số, tần số phổ và điều kiện số môn; kết quả ở `outputs/audits/external_*.csv` và `external_verification.json`. Cột phổ 2025 là khoảng đóng bên phải, gồm 0 ở khoảng đầu. Riêng Văn 2023 có phép kiểm tra độ nhạy đưa điểm về mốc 0,25 gần nhất để đối chiếu bảng hiển thị; dữ liệu dùng cho tổ hợp và tương quan vẫn là điểm gốc. Không sửa dữ liệu nguồn để ép khớp số công bố.

`src/report_explanations.py` tạo phần đọc nhanh và diễn giải dưới từng bảng/hình trong báo cáo duy nhất. Các nhận xét so sánh dùng bộ dữ liệu 2023/2025 đã kiểm tra ở phiên này.

`outputs/parts3_5_run.json` lưu hash nguồn, số dòng, xử lý điểm, nhãn cohort và phiên bản. `outputs/parts3_5_manifest.json` lưu hash/size các bảng và hình. `outputs/audits/b00_verification.json` lưu kiểm chứng độc lập số người đủ B00. `outputs/parts3_5_completion_audit.json` lưu kết quả xác minh cuối cùng. File tạm, báo cáo riêng và nhật ký triển khai đã được dọn; các quy tắc cần tái lập được giữ tại đây.

Lỗi test nền đã thấy trước thay đổi: `test_week6_score_distribution.TestScoreDistribution.test_alias_mapping_and_range` trong module tuần 6 cũ tạo DataFrame từ scalar mà không có index. Module phần 3/5 không phụ thuộc module này. Báo kết quả test toàn bộ phải ghi rõ lỗi nền nếu còn tồn tại; không ghi toàn bộ suite xanh.
