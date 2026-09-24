"""Create an executed, portable Vietnamese Week 4 notebook using the local runtime."""
from __future__ import annotations

import base64
import contextlib
import io
import json
from pathlib import Path

from src import week4_explanations as explain

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "notebooks/week4_exercises+bai_tap_tuan4.ipynb"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": source.splitlines(keepends=True)}


def build_cells() -> list[dict]:
    return [
        markdown("""# INFO3020 Week 4 — Data Cleaning

**Dự án:** Điểm thi tốt nghiệp THPT 2023. **Hạn:** 23:59 ngày trước buổi Week 5.

Mục tiêu: phát hiện ngoại lệ → xác minh nguồn → chuẩn hóa văn bản → ghi nhật ký.
Notebook tái tạo toàn bộ kết quả trên CSV gốc; điểm và ô thiếu được giữ nguyên.
Các ví dụ Salary/Location/Experience trong đề chỉ minh họa phương pháp, không thuộc dữ liệu này.

Chọn Python của `.venv`. Chạy notebook từ thư mục gốc hoặc `notebooks`.
Bằng chứng web đã được ghi ngày kiểm tra trong `docs/week4_source_checks.json`; chạy lại không cần mạng.
"""),
        code("""from pathlib import Path
import sys
import pandas as pd
root = Path.cwd().resolve()
if not (root / 'src').is_dir():
    root = root.parent
if not (root / 'src/analyze_week4.py').is_file():
    raise RuntimeError('Mở notebook từ thư mục repo hoặc notebooks')
sys.path.insert(0, str(root))
from src.analyze_week4 import run, load_raw, detect_column, normalize_text, select_top5, SCORES, TEXT
# run() tái tạo bảng/hình; load_raw() đọc ID dạng chuỗi và giữ ô thiếu.
from src.analyze_week4 import VN
from src.week4_explanations import LABELS
metrics = run()
df = load_raw()
print('Số dòng:', f"{len(df):,}")
print('Cột:', list(df.columns))
print('SHA-256 nguồn:', metrics['source_sha256'])
print('Ngày kiểm tra web:', metrics['source_checked_at'])
"""),
        markdown("""## EX4.1 — IQR và Z-score trên 9 cột điểm

Tính riêng từng môn trên **toàn bộ điểm quan sát**, không điền thiếu trước khi tính.

- IQR = Q3 − Q1, nội suy tuyến tính. Gắn cờ ngoài [Q1 − 1,5×IQR; Q3 + 1,5×IQR].
- Z = (x − μ)/σ, dùng `ddof=0`; gắn cờ khi |Z| > 3.
- Biên dùng bất đẳng thức nghiêm ngặt; giá trị nằm đúng ngưỡng không bị gắn cờ.
- Cột toàn thiếu hoặc σ=0 không gắn cờ Z; IQR=0 vẫn áp dụng khoảng suy biến.

Minh họa phép tính trực tiếp trên Toán; pipeline áp dụng cùng quy tắc cho cả 9 môn.
"""),
        markdown(explain.METHOD),
        code("""s = df['Mathematics']
# Tính hai phân vị trên điểm có dữ liệu (pandas bỏ NaN khi tính).
q1, q3 = s.quantile([0.25, 0.75], interpolation='linear')
iqr = q3 - q1
# True là một điểm có cờ; dùng < và > nên không gắn cờ điểm đúng tại biên.
iqr_flag = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
# ddof=0: độ lệch chuẩn tính với mẫu số n, tức số điểm quan sát.
z = (s - s.mean()) / s.std(ddof=0)
z_flag = z.abs() > 3
stats, checked_iqr, checked_z, _ = detect_column(s)
assert iqr_flag.equals(checked_iqr) and z_flag.equals(checked_z)
print('Toán: Q1, Q3, IQR =', q1, q3, iqr)
print('IQR:', int(iqr_flag.sum()), 'Z-score:', int(z_flag.sum()))
print(f'Ngưỡng IQR: dưới {q1 - 1.5 * iqr:.3f} hoặc trên {q3 + 1.5 * iqr:.3f}')
print(f'Tỷ lệ IQR = {int(iqr_flag.sum())} / {s.count()} × 100 = {100 * iqr_flag.sum() / s.count():.3f}%')
"""),
        markdown(explain.COMPARISON),
        code(r"""tables = root / 'outputs/tables'
comparison = pd.read_csv(tables / 'week4_outlier_comparison.csv')
details = pd.read_csv(tables / 'week4_outlier_details.csv', dtype={'Student ID': 'string'})
# Chỉ dịch nhãn hiển thị; tên cột trong các CSV vẫn giữ nguyên để tra cứu.
visible = comparison.assign(column=comparison['column'].map(VN))
print(visible[['column', 'n_observed', 'iqr_n', 'z_n', 'both_n', 'either_n', 'iqr_only_n', 'z_only_n']].rename(columns=LABELS).to_string(index=False))
print('\nTỷ lệ %, mẫu số là số điểm quan sát của từng môn:')
print(visible[['column', 'iqr_pct', 'z_pct', 'either_pct']].rename(columns=LABELS).to_string(index=False, float_format=lambda x: f'{x:.4f}'))
print('\nSố ô điểm bị gắn cờ:', metrics['flagged_cells'])
print('Số thí sinh khác nhau:', metrics['flagged_students'])
print('\nVí dụ truy vết:')
print(details.head(8).to_string(index=False))
"""),
        markdown('WORKED_EXAMPLE_PLACEHOLDER'),
        markdown('### Biểu đồ 1 — So sánh tỷ lệ ngoại lệ\n\n'
                 '![Biểu đồ thanh](attachment:week4_outlier_rates.png)\n\n' + explain.BAR +
                 '\n[Mở bản PNG để phóng to](../outputs/figures/week4_outlier_rates.png)'),
        markdown('### Biểu đồ 2 — Phân bố điểm thực tế\n\n'
                 '![Histogram](attachment:week4_score_histograms.png)\n\n' + explain.HISTOGRAM +
                 '\n[Mở bản PNG để phóng to](../outputs/figures/week4_score_histograms.png)'),
        markdown('### Biểu đồ 3 — Boxplot ngang của 9 môn\n\n'
                 '![Boxplot có chú giải](attachment:week4_boxplot.png)\n\n' + explain.BOXPLOT +
                 '\n[Mở bản PNG để phóng to](../outputs/figures/week4_boxplot.png)'),
        markdown("""## EX4.2 — Điều tra 5 ngoại lệ lớn nhất

“Lớn nhất” = |Z| lớn nhất trong **hợp** các cờ, xét cả phía thấp và cao.
Sắp xếp |Z| giảm dần, ID tăng dần, tên môn tăng dần; giữ ô đầu mỗi thí sinh rồi lấy 5.
Các trường hợp đồng hạng không được thay để lấy đủ nhiều môn.
"""),
        markdown(explain.INVESTIGATION),
        code(r"""selected = select_top5(details)
investigation = pd.read_csv(tables / 'week4_top5_investigation.csv', dtype={'Student ID': 'string', 'raw_token': 'string'})
assert selected['Student ID'].tolist() == investigation['Student ID'].tolist()
print(investigation[['rank', 'Student ID', 'source_row', 'column', 'value', 'abs_z', 'verdict', 'decision']].rename(columns=LABELS).to_string(index=False))
raw_records = pd.read_csv(tables / 'week4_top5_raw_records.csv', dtype='string', keep_default_na=False)
print('\nToàn bộ token của 5 dòng nguồn (ô trống vẫn để trống):')
print(raw_records.drop(columns='source_sha256').to_string(index=False))
for row in investigation.to_dict('records'):
    print('\nSBD', row['Student ID'], '—', row['reason'])
    print('Ngữ cảnh:', row['record_context'])
    print('Đối chiếu CSV / Parquet:', row['raw_record_matches'], row['processed_week3_matches'])
    print('Truy vấn:', row['search_query'])
    print('Kết quả:', row['search_result'])
    print('Nguồn:', row['source_urls'])
    print('Bằng chứng:', row['evidence_file'])
"""),
        markdown("""### Kết luận điều tra

Cả 5 bản ghi có GDCD bằng 0; |Z| khoảng 7,28335. Toàn bộ 11 cột khớp CSV và bản Parquet Week 3.
Điểm trong [0,10] là hợp lệ về miền, **chưa chứng minh điểm thi chính xác**.

Trang Kaggle có mô tả dataset nhưng chưa xác minh được nguồn thu thập từng điểm.
Danh sách tra cứu năm 2023 dẫn đến trang Hà Nội hiện có tiêu đề 2026; công cụ web gặp lỗi
khi mở địa chỉ TP.HCM năm 2023. Không thu được bảng điểm độc lập cho 5 ID.
Kết luận **`unresolved` (chưa xác định), giữ nguyên**. Không tìm thấy qua tìm kiếm không chứng minh điểm sai.

Đọc [bằng chứng đầy đủ](../docs/week4_evidence.md) và [nhật ký kiểm tra nguồn](../docs/week4_source_checks.json)
để xem URL, ngày, trích đoạn và giới hạn; tệp điều tra CSV cũng lưu các quan sát theo từng ID.
"""),
        markdown("""## EX4.3 — Chuẩn hóa ít nhất hai cột văn bản

Dùng hai cột chuỗi có thật: **Student ID** và **Foreign language code**.
NFKC → bỏ khoảng trắng đầu/cuối → gộp khoảng trắng liên tiếp; mã ngoại ngữ chuyển chữ hoa.
ID được giữ chuỗi; không tự pad số 0 hoặc đoán mã. Kiểm tra `[0-9]{8}` và N1–N7.
Distinct không tính thiếu; thiếu có cột riêng. Không có biến thể tên tương đương để ánh xạ.
"""),
        markdown(explain.TEXT),
        code("""text_summary = pd.read_csv(tables / 'week4_text_standardization.csv')
print(text_summary.rename(columns=LABELS).to_string(index=False))
for col in TEXT:
    normalized = normalize_text(df[col], uppercase=(col == 'Foreign language code'))
    # Kiểm tra idempotent: làm sạch lại phải cho cùng kết quả, kể cả vị trí thiếu.
    pd.testing.assert_series_equal(normalized, normalize_text(normalized, uppercase=(col == 'Foreign language code')))
print('Chuẩn hóa lần hai không tạo thay đổi.')
print('0 dòng đổi là kết quả thật: không tạo dữ liệu lỗi giả để giảm distinct.')
"""),
        markdown("""## EX4.4 — Cleaning Log từ Week 3 đến Week 4

Giữ các trường ID, cột/bản ghi, vấn đề, bằng chứng, quyết định; bổ sung lý do, tuần, quy tắc,
`scope_rows` (số dòng thuộc phạm vi) và `changed_rows` (số dòng thực sự đổi trong dữ liệu chính).
Phạm vi có thể chồng lấp nên không cộng lại thành số người duy nhất.
Week 3 được tổng hợp lại từ báo cáo/code/metrics, ngày quyết định cũ để trống.
Điểm được điền thử Week 3 không đi vào dữ liệu chính; vẫn ghi 0 dòng dữ liệu chính bị thay đổi.
"""),
        markdown(explain.LOG),
        code(r"""log = pd.read_csv(tables / 'week4_cleaning_log.csv', keep_default_na=False)
print('Số quyết định:', len(log))
print(log[['ID', 'week', 'column_or_record', 'decision', 'scope_rows', 'changed_rows']].rename(columns=LABELS).to_string(index=False))
print('\nVí dụ đầy đủ một quyết định:')
print(log.loc[log['column_or_record'].eq('01053185: Civic education')].T.to_string(header=False))
"""),
        markdown("""## Kiểm tra và kết quả bàn giao

Các phép kiểm dưới đây đối chiếu dữ liệu xuất với nguồn và bảng tổng hợp với từng cờ.
CSV được đọc với kiểu chuỗi cho hai cột mã; mở trực tiếp bằng Excel có thể tự chuyển ID thành số.
"""),
        code("""from src.analyze_week4 import sha256, RAW, CLEANED
assert sha256(RAW) == metrics['source_sha256']
cleaned = load_raw(CLEANED)
pd.testing.assert_frame_equal(df, cleaned, check_exact=True)
assert cleaned['Student ID'].iloc[0] == '01000001'
assert list(cleaned.columns) == metrics['columns']
for row in comparison.to_dict('records'):
    subset = details.loc[details['column'].eq(row['column'])]
    assert len(subset) == row['either_n']
    assert subset['iqr_flag'].sum() == row['iqr_n']
    assert subset['z_flag'].sum() == row['z_n']
assert investigation['Student ID'].nunique() == len(investigation) == 5
assert investigation['raw_record_matches'].all() and investigation['processed_week3_matches'].all()
assert all(metrics['validation'].values())
print('Đạt: nguồn bất biến; giữ số dòng, thứ tự, 11 cột, điểm, null và số 0 đầu.')
print('Đạt: số cờ khớp; top 5 duy nhất; bằng chứng đầy đủ theo khả năng truy cập.')
print('Kết luận: giữ điểm và null; 5 ngoại lệ chưa đủ bằng chứng xác minh đúng/sai.')
"""),
        markdown("""## Tài liệu bài nộp

- [Báo cáo Week 4](../docs/week4_report+bao_cao.md)
- [CSV sau chuẩn hóa](../data/processed/week4_cleaned.csv)
- [So sánh ngoại lệ](../outputs/tables/week4_outlier_comparison.csv)
- [Điều tra top 5](../outputs/tables/week4_top5_investigation.csv)
- [Thống kê văn bản](../outputs/tables/week4_text_standardization.csv)
- [Cleaning Log](../outputs/tables/week4_cleaning_log.csv)
- [Metrics và các phép kiểm](../outputs/week4_metrics.json)

Đọc trước: Wes McKinney, *Python for Data Analysis*, mục 7.2 — Data Transformation.
"""),
    ]


def main() -> None:
    cells = build_cells()
    # Fail fast on invalid generated Python before rerunning the full dataset.
    for cell in cells:
        if cell['cell_type'] == 'code':
            compile(''.join(cell['source']), 'Week 4 notebook validation', 'exec')
    namespace: dict = {}
    count = 0
    for index, cell in enumerate(cells, start=1):
        cell['id'] = f'week4-{index:02d}'
        if cell['cell_type'] != 'code':
            continue
        count += 1
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(compile(''.join(cell['source']), f'Week 4 cell {count}', 'exec'), namespace)
        cell['execution_count'] = count
        cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout',
                            'text': buffer.getvalue().splitlines(keepends=True)}]
    for cell in cells:
        if ''.join(cell['source']) == 'WORKED_EXAMPLE_PLACEHOLDER':
            # Thay số từ kết quả vừa chạy, tránh ví dụ lệch với bảng thật.
            cell['source'] = explain.worked_example(namespace['comparison']).splitlines(keepends=True)
        for filename in ('week4_boxplot.png', 'week4_outlier_rates.png', 'week4_score_histograms.png'):
            if f'attachment:{filename}' in ''.join(cell['source']):
                png = base64.b64encode((ROOT / 'outputs/figures' / filename).read_bytes()).decode('ascii')
                cell.setdefault('attachments', {})[filename] = {'image/png': png}
    notebook = {'cells': cells, 'metadata': {
        'kernelspec': {'display_name': 'Python 3 (.venv)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
    }, 'nbformat': 4, 'nbformat_minor': 5}
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'Executed {count} code cells; wrote {DESTINATION}')


if __name__ == '__main__':
    main()
