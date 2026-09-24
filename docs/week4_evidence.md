# Week 4 — Bằng chứng điều tra ngoại lệ

Ngày kiểm tra web: **2026-09-23**. Kiểm tra thủ công bằng công cụ web; pipeline đọc lại nhật ký này, không tự truy vấn Internet.

Đây là ghi chép truy xuất và trích đoạn ngắn, không phải bản sao đầy đủ của website. Không tìm thấy qua tìm kiếm không có nghĩa là bản ghi không tồn tại.

## Nguồn đã kiểm tra

### kaggle

[Nguồn](https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam)

Mở trực tiếp không trích xuất được nội dung; kết quả tìm kiếm có Data Card của Truong-Binh Duong, tệp scores.csv, 11 cột và mã N1–N7. Phần mô tả đã đọc không cung cấp nhật ký thu thập hoặc liên kết bảng điểm gốc từng thí sinh. Chưa tải lại tệp Kaggle để so hash với original.csv.

> High School graduation exam scores for more 1 Million students in Vietnam 2023

Data Card nói 1,5 triệu người nhưng CSV địa phương có 1.022.060 dòng; dùng số đếm thực tế. Trang này không xác minh được điểm cá nhân.

### official_directory

[Nguồn](https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm)

Bài ngày 17/07/2023 liệt kê địa chỉ tra cứu Hà Nội và TP.HCM. Dùng làm đầu mối tìm nguồn, không làm bằng chứng điểm thi.

> Mã sở | Tên Sở GDĐT | Đường link tra cứu điểm



### hanoi

[Nguồn](https://tracuu.hanoi.edu.vn/)

Trang hiện tại có tiêu đề kỳ thi 2026; không thu được bảng điểm cá nhân năm 2023.

> Trang thông tin kỳ thi quốc gia 2026



### hcm_2023

[Nguồn](https://tracuudiemthibgd.hcm.edu.vn/)

Công cụ web trả Internal Error khi mở địa chỉ được liệt kê cho năm 2023. Đây là lỗi truy cập trong lần kiểm tra, không chứng minh website không hoạt động với mọi người.

> Internal Error



### hcm_current

[Nguồn](https://diemthi.hcm.edu.vn/)

Trang tra cứu hiện có yêu cầu số báo danh và captcha; nội dung đọc được không xác định kỳ thi 2023. Không gửi yêu cầu tra cứu hoặc thu được kết quả cá nhân.

> Nhập số báo danh để tra cứu kết quả



## Đối chiếu từng bản ghi

Số dòng tính từ 1, gồm dòng tiêu đề. Token trống trong bảng gốc được giữ là ô trống, không đổi thành 0. Đầu mối Hà Nội/TP.HCM dựa trên tiền tố mã để tìm nguồn; không bổ sung địa phương vào dữ liệu.

<a id="sbd-01053185"></a>

### SBD 01053185

Dòng CSV **53186**; Civic education = **0.0**; Z = -7.28334882. SHA-256: `cdf22a6b45f8e23b522beb1c521782e36486cac39d3fb64bca2a2395edec39b5`.

| Cột | Token trong CSV |
| --- | --- |
| Student ID | 01053185 |
| Mathematics |  |
| Literature | 4.5 |
| Foreign language |  |
| Physics |  |
| Chemistry |  |
| Biology |  |
| History | 5.0 |
| Geography | 5.0 |
| Civic education | 0.0 |
| Foreign language code |  |

Đã đọc lại dòng nguồn, đối chiếu toàn bộ 11 cột với DataFrame và bản Parquet Week 3: khớp.

Ngữ cảnh bản ghi: Có 1 môn bằng 0 (Civic education); thiếu 5 trong 9 cột điểm. Các điểm khác và pattern thiếu không xác minh được nguyên nhân điểm 0; không suy ra vắng thi, miễn thi hoặc chương trình học.

Truy vấn: `"2023" "01053185" điểm thi`. Không tìm thấy kết quả liên quan xác minh điểm cá nhân trong các kết quả được trả về.

Mở trực tiếp không trích xuất được nội dung; kết quả tìm kiếm có Data Card của Truong-Binh Duong, tệp scores.csv, 11 cột và mã N1–N7. Phần mô tả đã đọc không cung cấp nhật ký thu thập hoặc liên kết bảng điểm gốc từng thí sinh. Chưa tải lại tệp Kaggle để so hash với original.csv. | Bài ngày 17/07/2023 liệt kê địa chỉ tra cứu Hà Nội và TP.HCM. Dùng làm đầu mối tìm nguồn, không làm bằng chứng điểm thi. | Trang hiện tại có tiêu đề kỳ thi 2026; không thu được bảng điểm cá nhân năm 2023.

Các URL: https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam | https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm | https://tracuu.hanoi.edu.vn/

**Kết luận: chưa xác định (`unresolved`). Quyết định: giữ nguyên.** Khớp tệp nguồn và trong miền điểm; chưa có bảng điểm độc lập xác minh.

<a id="sbd-01053192"></a>

### SBD 01053192

Dòng CSV **53193**; Civic education = **0.0**; Z = -7.28334882. SHA-256: `cdf22a6b45f8e23b522beb1c521782e36486cac39d3fb64bca2a2395edec39b5`.

| Cột | Token trong CSV |
| --- | --- |
| Student ID | 01053192 |
| Mathematics | 7.0 |
| Literature | 6.25 |
| Foreign language |  |
| Physics |  |
| Chemistry |  |
| Biology |  |
| History | 3.75 |
| Geography | 0.0 |
| Civic education | 0.0 |
| Foreign language code |  |

Đã đọc lại dòng nguồn, đối chiếu toàn bộ 11 cột với DataFrame và bản Parquet Week 3: khớp.

Ngữ cảnh bản ghi: Có 2 môn bằng 0 (Geography, Civic education); thiếu 4 trong 9 cột điểm. Các điểm khác và pattern thiếu không xác minh được nguyên nhân điểm 0; không suy ra vắng thi, miễn thi hoặc chương trình học.

Truy vấn: `"2023" "01053192" "điểm"`. Không tìm thấy kết quả liên quan xác minh điểm cá nhân trong các kết quả được trả về.

Mở trực tiếp không trích xuất được nội dung; kết quả tìm kiếm có Data Card của Truong-Binh Duong, tệp scores.csv, 11 cột và mã N1–N7. Phần mô tả đã đọc không cung cấp nhật ký thu thập hoặc liên kết bảng điểm gốc từng thí sinh. Chưa tải lại tệp Kaggle để so hash với original.csv. | Bài ngày 17/07/2023 liệt kê địa chỉ tra cứu Hà Nội và TP.HCM. Dùng làm đầu mối tìm nguồn, không làm bằng chứng điểm thi. | Trang hiện tại có tiêu đề kỳ thi 2026; không thu được bảng điểm cá nhân năm 2023.

Các URL: https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam | https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm | https://tracuu.hanoi.edu.vn/

**Kết luận: chưa xác định (`unresolved`). Quyết định: giữ nguyên.** Khớp tệp nguồn và trong miền điểm; chưa có bảng điểm độc lập xác minh.

<a id="sbd-01053271"></a>

### SBD 01053271

Dòng CSV **53272**; Civic education = **0.0**; Z = -7.28334882. SHA-256: `cdf22a6b45f8e23b522beb1c521782e36486cac39d3fb64bca2a2395edec39b5`.

| Cột | Token trong CSV |
| --- | --- |
| Student ID | 01053271 |
| Mathematics | 6.2 |
| Literature | 6.25 |
| Foreign language |  |
| Physics |  |
| Chemistry |  |
| Biology |  |
| History | 7.75 |
| Geography | 4.0 |
| Civic education | 0.0 |
| Foreign language code |  |

Đã đọc lại dòng nguồn, đối chiếu toàn bộ 11 cột với DataFrame và bản Parquet Week 3: khớp.

Ngữ cảnh bản ghi: Có 1 môn bằng 0 (Civic education); thiếu 4 trong 9 cột điểm. Các điểm khác và pattern thiếu không xác minh được nguyên nhân điểm 0; không suy ra vắng thi, miễn thi hoặc chương trình học.

Truy vấn: `"2023" "01053271" "điểm"`. Không tìm thấy kết quả liên quan xác minh điểm cá nhân trong các kết quả được trả về.

Mở trực tiếp không trích xuất được nội dung; kết quả tìm kiếm có Data Card của Truong-Binh Duong, tệp scores.csv, 11 cột và mã N1–N7. Phần mô tả đã đọc không cung cấp nhật ký thu thập hoặc liên kết bảng điểm gốc từng thí sinh. Chưa tải lại tệp Kaggle để so hash với original.csv. | Bài ngày 17/07/2023 liệt kê địa chỉ tra cứu Hà Nội và TP.HCM. Dùng làm đầu mối tìm nguồn, không làm bằng chứng điểm thi. | Trang hiện tại có tiêu đề kỳ thi 2026; không thu được bảng điểm cá nhân năm 2023.

Các URL: https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam | https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm | https://tracuu.hanoi.edu.vn/

**Kết luận: chưa xác định (`unresolved`). Quyết định: giữ nguyên.** Khớp tệp nguồn và trong miền điểm; chưa có bảng điểm độc lập xác minh.

<a id="sbd-02016503"></a>

### SBD 02016503

Dòng CSV **118599**; Civic education = **0.0**; Z = -7.28334882. SHA-256: `cdf22a6b45f8e23b522beb1c521782e36486cac39d3fb64bca2a2395edec39b5`.

| Cột | Token trong CSV |
| --- | --- |
| Student ID | 02016503 |
| Mathematics | 3.8 |
| Literature | 2.0 |
| Foreign language | 3.8 |
| Physics |  |
| Chemistry |  |
| Biology |  |
| History | 4.25 |
| Geography | 0.0 |
| Civic education | 0.0 |
| Foreign language code | N1 |

Đã đọc lại dòng nguồn, đối chiếu toàn bộ 11 cột với DataFrame và bản Parquet Week 3: khớp.

Ngữ cảnh bản ghi: Có 2 môn bằng 0 (Geography, Civic education); thiếu 3 trong 9 cột điểm. Các điểm khác và pattern thiếu không xác minh được nguyên nhân điểm 0; không suy ra vắng thi, miễn thi hoặc chương trình học.

Truy vấn: `"2023" "02016503" điểm thi`. Không tìm thấy kết quả liên quan xác minh điểm cá nhân trong các kết quả được trả về.

Mở trực tiếp không trích xuất được nội dung; kết quả tìm kiếm có Data Card của Truong-Binh Duong, tệp scores.csv, 11 cột và mã N1–N7. Phần mô tả đã đọc không cung cấp nhật ký thu thập hoặc liên kết bảng điểm gốc từng thí sinh. Chưa tải lại tệp Kaggle để so hash với original.csv. | Bài ngày 17/07/2023 liệt kê địa chỉ tra cứu Hà Nội và TP.HCM. Dùng làm đầu mối tìm nguồn, không làm bằng chứng điểm thi. | Công cụ web trả Internal Error khi mở địa chỉ được liệt kê cho năm 2023. Đây là lỗi truy cập trong lần kiểm tra, không chứng minh website không hoạt động với mọi người. | Trang tra cứu hiện có yêu cầu số báo danh và captcha; nội dung đọc được không xác định kỳ thi 2023. Không gửi yêu cầu tra cứu hoặc thu được kết quả cá nhân.

Các URL: https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam | https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm | https://tracuudiemthibgd.hcm.edu.vn/ | https://diemthi.hcm.edu.vn/

**Kết luận: chưa xác định (`unresolved`). Quyết định: giữ nguyên.** Khớp tệp nguồn và trong miền điểm; chưa có bảng điểm độc lập xác minh.

<a id="sbd-02019084"></a>

### SBD 02019084

Dòng CSV **121180**; Civic education = **0.0**; Z = -7.28334882. SHA-256: `cdf22a6b45f8e23b522beb1c521782e36486cac39d3fb64bca2a2395edec39b5`.

| Cột | Token trong CSV |
| --- | --- |
| Student ID | 02019084 |
| Mathematics | 8.2 |
| Literature | 7.0 |
| Foreign language | 9.0 |
| Physics |  |
| Chemistry |  |
| Biology |  |
| History | 7.75 |
| Geography | 0.0 |
| Civic education | 0.0 |
| Foreign language code | N1 |

Đã đọc lại dòng nguồn, đối chiếu toàn bộ 11 cột với DataFrame và bản Parquet Week 3: khớp.

Ngữ cảnh bản ghi: Có 2 môn bằng 0 (Geography, Civic education); thiếu 3 trong 9 cột điểm. Các điểm khác và pattern thiếu không xác minh được nguyên nhân điểm 0; không suy ra vắng thi, miễn thi hoặc chương trình học.

Truy vấn: `"2023" "02019084" "điểm"`. Không tìm thấy kết quả liên quan xác minh điểm cá nhân trong các kết quả được trả về.

Mở trực tiếp không trích xuất được nội dung; kết quả tìm kiếm có Data Card của Truong-Binh Duong, tệp scores.csv, 11 cột và mã N1–N7. Phần mô tả đã đọc không cung cấp nhật ký thu thập hoặc liên kết bảng điểm gốc từng thí sinh. Chưa tải lại tệp Kaggle để so hash với original.csv. | Bài ngày 17/07/2023 liệt kê địa chỉ tra cứu Hà Nội và TP.HCM. Dùng làm đầu mối tìm nguồn, không làm bằng chứng điểm thi. | Công cụ web trả Internal Error khi mở địa chỉ được liệt kê cho năm 2023. Đây là lỗi truy cập trong lần kiểm tra, không chứng minh website không hoạt động với mọi người. | Trang tra cứu hiện có yêu cầu số báo danh và captcha; nội dung đọc được không xác định kỳ thi 2023. Không gửi yêu cầu tra cứu hoặc thu được kết quả cá nhân.

Các URL: https://www.kaggle.com/datasets/duongtruongbinh/vietnamese-national-high-school-graduation-exam | https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm | https://tracuudiemthibgd.hcm.edu.vn/ | https://diemthi.hcm.edu.vn/

**Kết luận: chưa xác định (`unresolved`). Quyết định: giữ nguyên.** Khớp tệp nguồn và trong miền điểm; chưa có bảng điểm độc lập xác minh.
