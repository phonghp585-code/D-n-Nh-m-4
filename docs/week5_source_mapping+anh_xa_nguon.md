# Week 5 — nguồn và ánh xạ mã Hội đồng thi năm 2023

File ghép `data/raw/exam_councils_2023.csv` có ba cột: `exam_year`, `exam_council_code`, `exam_council_name`. Đây là bảng nguồn bổ sung của Week 5, tách khỏi CSV điểm gốc.

| Trường đích | Nguồn 63 mã chính | Quy tắc |
| --- | --- | --- |
| `exam_year` | Bài [Báo Chính phủ ngày 17/07/2023](https://baochinhphu.vn/cach-tra-cuu-diem-thi-tot-nghiep-thpt-nam-2023-102230717160222763.htm) | Gán năm 2023 theo kỳ thi được nêu trong bài. |
| `exam_council_code` | Cột `Mã sở` | Chuyển mã 1–9 thành `01`–`09`; mã khác giữ hai chữ số. Không có mã 20. |
| `exam_council_name` | Cột `Tên Sở GDĐT` | Giữ nguyên tên được công bố trên trang. |

Đã lưu [bảng trích 63 dòng](week5_gov_table_excerpt+trich_bang_nguon.csv), với hai cột `source_code`, `source_name`, để kiểm tra lại từng mã và tên. SHA-256 của bảng trích là `5304a9c15a3f718ed1fbf91f7e972c021e35b4797ba5d33e05efea0d26728af8`. Nguồn được kiểm tra ngày 24/09/2026.

Mã `65`, tên `Cục Nhà trường -Bộ Quốc phòng`, không có trong bảng Báo Chính phủ. Nó được bổ sung từ [Phụ lục VIII, Công văn 1515/BGDĐT-QLCL](https://hic.edu.vn/wp-content/uploads/2023/05/230407-1515_BGDDT_QLCL-HD-to-chuc-ky-thi-TN-THPT-nam-2023.pdf), trang PDF 42–44 nếu đếm từ trang đầu là 1. Bản PDF ghi tháng 4/2023 nhưng để trống ngày ban hành. Đây là bản lưu trên trang một cơ sở giáo dục, không phải URL của Bộ. Phụ lục viết mã 33 là `Sở GDĐT Thừa Thiên -Huế`, còn Báo Chính phủ viết `Sở GDĐT Thừa Thiên Huế`; file ghép dùng tên từ Báo Chính phủ cho 63 mã ở bảng đó.

[Hướng dẫn cấu trúc số báo danh năm 2023](https://caodangsaigon.edu.vn/ky-thi-thpt-cdsg/huong-dan-cach-tra-so-bao-danh-thi-thpt-quoc-gia-2023/) nêu hai chữ số đầu là mã Hội đồng thi, sáu chữ số sau là số thứ tự. Pipeline lấy hai ký tự đầu của `Student ID` làm mã; kiểm tra mã bằng bảng nguồn với khóa `(exam_year, exam_council_code)` và `validate="many_to_one"`. Bảng [`week5_reference_source_check+doi_chieu_nguon_bo_sung.csv`](../outputs/tables/week5_reference_source_check+doi_chieu_nguon_bo_sung.csv) đối chiếu 63 tên Báo Chính phủ và mã 65. Tên Hội đồng thi không xác nhận nơi cư trú hoặc trường học.

Manifest nguồn và hash của file ghép: [week5_source_registry+ho_so_nguon.json](week5_source_registry+ho_so_nguon.json). Mọi thay đổi ở các file nguồn phải được đối chiếu và cập nhật registry có căn cứ trước khi chạy pipeline.
