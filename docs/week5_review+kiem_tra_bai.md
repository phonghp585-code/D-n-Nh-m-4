# Kiểm tra Week 5 và quản lý file dự án

Ngày kiểm tra: 24/09/2026. Phạm vi: yêu cầu người dùng, trang PDF 35 (slide 104) của tài liệu W5, code và đầu ra thực tế trong repo, so sánh với bài Week 3–4 hiện có. `mujctieu.md` được dùng như kế hoạch tham khảo. Không có slide gốc Week 3–4 trong thư mục hiện tại để đánh giá lại toàn bộ rubric hai tuần đó.

## Kết luận

**Week 5 đáp ứng EX5.1–EX5.3 theo slide đã cung cấp, sau các chỉnh sửa ghi dưới đây.** Cả 25 kiểm thử Week 3–5 đạt. Chạy `src/main.py` thành công; một lần chạy độc lập trong thư mục sạch có raw, hồ sơ nguồn và code tạo 25 đầu ra có SHA-256 giống hệt lần chạy chính. Không dùng dữ liệu processed, báo cáo hay metrics cũ trong lần chạy sạch.

Kết luận này xác nhận yêu cầu kỹ thuật và tính nhất quán nội bộ của bài, không xác minh từng điểm thi với hồ sơ thí sinh và không xác nhận bài đã được nộp lên LMS/GitHub.

## Đối chiếu yêu cầu

| Yêu cầu | Kết quả thực tế | Bằng chứng |
|---|---|---|
| Chọn dataset và câu hỏi nghiên cứu | Điểm thi THPT 2023; phân bố điểm theo Hội đồng thi, cùng ngữ cảnh thiếu và nhóm môn quan sát | [Báo cáo](week5_report+bao_cao.md) |
| EX5.1: raw → processed bằng một lệnh | `python src/main.py` trong môi trường có dependencies; chạy trên 1.022.060 dòng | [Entry point](../src/main.py), [pipeline log](../outputs/tables/week5_pipeline_log+nhat_ky_quy_trinh.csv) |
| Thiếu, ngoại lệ, chuẩn hóa, trùng và kiểm tra | Giữ 3.394.966 ô điểm thiếu; giữ 34.857 ô ngoại lệ của 30.190 thí sinh; loại 0 dòng trùng; chuẩn hóa đổi 0 dòng | [Manifest](../outputs/week5_manifest+ho_so_dau_ra.json), các bảng được liên kết trong báo cáo |
| EX5.2: ít nhất hai nguồn | CSV điểm + danh mục mã/tên Hội đồng thi có nguồn bên ngoài | [Mapping](week5_source_mapping+anh_xa_nguon.md), [registry](week5_source_registry+ho_so_nguon.json) |
| Khóa ghép hợp lệ | `(exam_year, exam_council_code)`, mã từ hai chữ số đầu ID; `many_to_one` | [Pipeline](../src/analyze_week5.py) |
| In số dòng trước/sau mọi merge và đưa vào báo cáo | Có 4 phép merge, gồm đối soát nguồn, kiểm tra khóa, gắn số lượng và ghép chính; mỗi phép có log console và bảng báo cáo | [Nhật ký merge](../outputs/tables/week5_merge_operations+nhat_ky_phep_ghep.csv) |
| Match rate và không khớp | 1.022.060 → 1.022.060 dòng; khớp 100% theo dòng và khóa; 0 dòng không khớp | [Merge summary](../outputs/tables/week5_merge_summary+tong_hop_ghep.csv) |
| Chính sách dòng không khớp | Giữ dòng; tên thiếu và `left_only`; tình huống có dòng không khớp đã được unit test | [Tests](../tests/test_week5.py), [bảng không khớp](../outputs/tables/week5_unmatched_keys+khoa_khong_khop.csv) |
| EX5.3: processed + cleaning log | 1.022.060 dòng × 16 cột; nhật ký 43 quyết định = 35 lịch sử + 8 Week 5 | [CSV cuối](../data/processed/week5_final+du_lieu_cuoi.csv), [Cleaning Log](../outputs/tables/week5_cleaning_log+nhat_ky_lam_sach.csv) |
| Tái lập | 25/25 file giống SHA-256 trong cùng môi trường; tất cả kiểm tra round-trip đạt | [Kết quả kiểm tra](../outputs/week5_verification+kiem_tra_tai_lap.json) |

Danh mục có 64 mã; dữ liệu chính dùng 63 mã. Mã 65 không dùng không phải lỗi merge. Bảng nguồn chính thức công bố 63 mã/tên trên [Báo Chính phủ](https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm); mã 65 có trong Phụ lục VIII của [bản công văn lưu tại HIC](https://hic.edu.vn/wp-content/uploads/2023/05/230407-1515_BGDDT_QLCL-HD-to-chuc-ky-thi-TN-THPT-nam-2023.pdf). Quy tắc hai chữ số đầu được mô tả trong [hướng dẫn năm 2023](https://caodangsaigon.edu.vn/ky-thi-thpt-cdsg/huong-dan-cach-tra-so-bao-danh-thi-thpt-quoc-gia-2023/).

Không cần ép scaling, encoding hoặc PCA vào bài này: slide bài tập yêu cầu pipeline phù hợp với dự án, không yêu cầu áp dụng mọi kỹ thuật. Giữ đơn vị điểm 0–10 và không tự điền điểm thiếu có lý do rõ ràng. Báo cáo nêu nguyên tắc chỉ fit trên train khi chuyển sang mô hình.

## Định dạng so với Week 3–4

| Thành phần | Đánh giá |
|---|---|
| Báo cáo | Cùng định dạng Markdown trong `docs/`, chia theo EX, có bảng, phương pháp, công thức, giải nghĩa và giới hạn. Không cần thêm bản `merge_report.md` vì phần này đã nằm trong EX5.2. |
| Notebook | Cùng định dạng `.ipynb`, có ô Markdown, code và kết quả. Đã sắp xếp EX5.1 → EX5.2 → EX5.3, bổ sung cell ID và nhúng PNG như Week 4. |
| Khả năng chạy notebook | Week 3–4 gọi xử lý từ notebook; Week 5 hiện đọc các đầu ra do `src/main.py` tạo. Đã ghi rõ khác biệt này. 5 ô code Week 5 được thực thi tuần tự khi sinh notebook, không có error output. Chưa kiểm thử bằng một ứng dụng Jupyter riêng. |
| Dữ liệu | Week 3 dùng Parquet; Week 4–5 dùng CSV UTF-8 BOM. Đây là khác định dạng lưu trữ có chủ đích; Week 5 không phải đổi về Parquet để đáp ứng đề. |
| Hình | Chỉ dùng PNG; đã bỏ các bản SVG trùng và ngừng sinh SVG trong code Week 4–5. |
| Code | Cùng cấu trúc module trong `src/` và unittest trong `tests/`. Week 5 có entry point rõ ràng và dùng lại hàm Week 4. |
| Đặt tên | Đầu ra và tài liệu Week 5 dùng `week5_ten_tieng_anh+ten_tieng_viet`, theo mẫu song ngữ Week 3 và tiền tố tuần của Week 4. Code xử lý là `analyze_week5.py`, tương ứng `analyze_week4.py`. |

Bố cục `reports/`, `final.csv`, `pipeline.py`, `EDA.ipynb` trong kế hoạch là ví dụ, không phải tên file bắt buộc trên slide. Repo hiện dùng `docs/`, `week5_final+du_lieu_cuoi.csv`, `analyze_week5.py` và notebook theo tuần; tương đương về vai trò và phù hợp lịch sử Week 3–4. Trang bài tập Week 5 không bắt buộc báo cáo PDF.

## Những điểm đã sửa trong lần kiểm tra

1. Bổ sung in số dòng trước/sau cả bốn phép merge và đưa nhật ký này vào báo cáo, notebook, manifest.
2. Đồng bộ mô tả và thứ tự nhật ký với code thực tế: chuẩn hóa chuỗi trước khi kiểm tra xung đột ID; phát hiện trùng hoàn toàn vẫn dựa trên cột nguồn đã parse.
3. Sửa mô tả Student ID trong bảng missing: ID bắt buộc có, thiếu thì pipeline dừng. Làm rõ `changed_rows` đếm loại dòng/sửa giá trị gốc, không đếm việc thêm cột ngữ cảnh. Đếm dòng chuẩn hóa theo hợp hai cột để tránh đếm hai lần một dòng.
4. Bổ sung nhãn EX5.3, cell ID, nhúng biểu đồ và ghi rõ cơ chế Run All của notebook.
5. Rút gọn README thành điểm bắt đầu, chỉ dẫn bài nộp, bản đồ file và lệnh chạy. Bổ sung `src/verify_week5.py` để kiểm tra tái lập có bằng chứng.

## Quản lý file từ bây giờ

Chỉ cần mở thường xuyên **README, báo cáo Week 5 và notebook Week 5**. Khi cần dùng dữ liệu, đọc `week5_final+du_lieu_cuoi.csv`; khi cần chứng minh quyết định, đi theo link Cleaning Log trong báo cáo.

Không phải mọi file CSV đều là một dataset khác nhau. `data/raw/` giữ nguồn; `data/processed/` giữ dataset từng tuần; `outputs/tables/` giữ bằng chứng. Các bảng lỗi chỉ có header thể hiện không có vi phạm và vẫn có giá trị kiểm tra. Mỗi biểu đồ hiện chỉ giữ một PNG. Registry và manifest khác nhau: registry mô tả nguồn đầu vào, manifest mô tả lần chạy/đầu ra.

Các file cần chú ý riêng:

- `data.ipynb` (0 byte), `reports/` (rỗng, chỉ có `.gitkeep`) và thư mục tạm rỗng `outputs/tmpyuf6r4fg/` đã được xóa. Báo cáo chính ở `docs/`.
- `.venv/`, `__pycache__/`, `outputs/_review/`: môi trường/file kiểm tra tạm; không thuộc bộ bài nộp. Lần kiểm tra sạch ban đầu bị Windows từ chối truy cập thư mục tạm; lần chạy lại với quyền phù hợp đã đạt. Thư mục rỗng của lần thất bại trong `_review/` đã dọn; còn `outputs/_review/week5_requirements.png` dùng để đối chiếu đề bài.
- Nhiều file Week 4–5 đang `untracked` trong Git. Có file trên máy chưa có nghĩa là đã được commit/push. Chưa thực hiện commit, push hoặc nộp bài.

Không xóa hoặc di chuyển các file lịch sử trong lần kiểm tra này. Nếu chỉnh báo cáo/notebook lâu dài, sửa file sinh tương ứng trong `src/`, rồi chạy lại, vì đầu ra sẽ bị ghi đè.

## Giới hạn còn lại

- Hash giống nhau được kiểm chứng trong môi trường hiện tại; `requirements.txt` vẫn dùng phiên bản tối thiểu, chưa khóa mọi dependency.
- Đầu ra và code được kiểm tra trên bộ nguồn có hash đã đăng ký. Nếu thay bộ dữ liệu, phải cập nhật hồ sơ nguồn và đối soát lịch sử; không chỉ thay CSV rồi bỏ qua kiểm tra hash.
- Pipeline ghi trực tiếp các đầu ra. Nếu một lần chạy sau bị lỗi, không sử dụng đầu ra dở dang; chỉ coi kết quả hợp lệ khi lệnh kết thúc thành công và kiểm tra hash đạt.
- Chưa có ngày học Week 6 nên chỉ xác nhận hạn theo đề: 23:59 ngày trước buổi Week 6.
- Những phân tích Week 6–8, năm biểu đồ EDA và PDF giữa kỳ là giai đoạn sau, không phải phần còn thiếu của EX5.1–EX5.3.
