"""Vietnamese reading guide and evidence-based explanations for parts 3/5."""
import json
import pandas as pd
from src.score_data import ALL_COMBINATIONS, SUBJECT_LABELS


def read(root, folder, name):
    return pd.read_csv(root/'outputs'/folder/(name+'.csv'))


def participation_comparison(root):
    """Display count growth separately from percentage-point share changes."""
    def number(value, digits=0):
        return f'{value:,.{digits}f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    def change(value, digits=0):
        return ('Tăng ' if value > 0 else 'Giảm ' if value < 0 else 'Không đổi ') + number(abs(value), digits)
    rows=[]
    for r in read(root, 'combinations', 'participation_deltas').itertuples():
        growth=100 * r.delta_n / r.n_from if r.n_from else None
        rows.append({'Môn':r.subject_label, 'Có điểm 2023':number(r.n_from),
                     'Có điểm 2025':number(r.n_to), 'Biến động số người':change(r.delta_n),
                     'So với số người 2023 (%)':change(growth, 2) if growth is not None else 'Không xác định',
                     'Tỷ lệ 2023 (%)':number(r.percent_from, 2),
                     'Tỷ lệ 2025 (%)':number(r.percent_to, 2),
                     'Biến động tỷ lệ (điểm phần trăm)':change(r.delta_percent, 2)})
    return pd.DataFrame(rows)


def overview(root, table):
    summary=read(root,'combinations','combination_summary').set_index(['year','combination'])
    participation=read(root,'combinations','participation_deltas')
    current=read(root,'combinations','participation')
    lines=['## Kết quả chính — đọc phần này trước',
           'Báo cáo phần 3 trả lời ba yêu cầu: **xu hướng môn thi**, **so sánh điểm đủ 24 tổ hợp**, '
           '**ngưỡng top 10%/20%**. Các bảng chi tiết và hình ở phía sau đều có diễn giải ngay bên dưới. '
           'Dùng 2023 so với 2025 xuyên suốt; không thay năm gốc bằng 2024.',
           '### 3.1. Xu hướng môn thi: môn nào có tỷ lệ tăng hoặc giảm?',
           'Trong dữ liệu điểm, chỉ quan sát được người có bài thi/điểm. Vì vậy, “xu hướng chọn môn” dưới đây '
           'là **xu hướng tỷ lệ có điểm**, chưa phải tỷ lệ đăng ký ban đầu. Mẫu số: '
           f'{int(participation.iloc[0].denominator_from):,} người năm 2023 và '
           f'{int(participation.iloc[0].denominator_to):,} người năm 2025 có ít nhất một điểm thi.']
    lines += [table(participation_comparison(root)),
              '**Diễn giải bảng:** Toán tăng 122.799 người (+12,24%), tỷ lệ tăng 0,97 điểm phần trăm; '
              'Văn tăng 118.487 người (+11,75%), tỷ lệ tăng 0,54 điểm phần trăm. '
              'Anh giảm từ 86,10% xuống 31,11% (−54,99 điểm phần trăm); '
              'Sinh giảm 31,90% → 6,18% (−25,72); Địa giảm 67,03% → 42,13% (−24,91); '
              'Sử giảm 67,16% → 42,56% (−24,61); Hóa giảm 32,24% → 21,23% (−11,01). '
              '**Lý tăng 20.410 bài nhưng tỷ lệ vẫn giảm 32,15% → 30,73%** vì tổng số người có điểm tăng. '
              'Anh là tập con của Ngoại ngữ; hai hàng này không cộng với nhau. '
              'Đây là thay đổi cơ cấu tập dự thi, chưa đủ để kết luận học sinh giảm hứng thú với môn học.',
              '**Cách tính và đọc tăng/giảm:** n là số thí sinh có điểm hợp lệ 0–10 ở riêng cột môn đó '
              '(giữ điểm 0, không điền điểm thiếu). Tỷ lệ có điểm = 100 × n / số người có ít nhất một điểm cùng năm. '
              'Biến động số người = n2025 − n2023; % tăng/giảm số người = 100 × (n2025 / n2023 − 1). '
              'Biến động tỷ lệ = tỷ lệ 2025 − tỷ lệ 2023, đơn vị **điểm phần trăm**. '
              'Phép trừ cho biết hướng thay đổi: dương là tăng, âm là giảm. Ví dụ Lý tăng 6,24% số người, '
              'nhưng tỷ lệ giảm 1,42 điểm phần trăm vì tổng người có điểm tăng 11,14%.',
              '**Đếm từng môn độc lập cho cả hai năm:** 2023 Lý 327.189, Hóa 328.118, Sinh 324.625; '
              'Sử 683.447, Địa 682.134. Không dùng chung 327.189 cho cả ba môn tự nhiên và không dùng '
              'một số chung cho các môn xã hội. Một người có điểm ở nhiều môn được tính một lần trong từng môn. '
              'Ba số đếm 2023 (Toán, Lý, Hóa) cao hơn công bố mỗi môn 1 người; giữ số đếm từ file và '
              'nêu sai lệch tại mục đối chiếu nguồn, chưa tự loại người khi chưa xác định nguyên nhân.',
              '**Tỷ lệ đăng ký cần dữ liệu khác:** số đăng ký môn / tổng người đăng ký trong cùng phạm vi. '
              'Tỷ lệ có điểm trong người đăng ký môn = số có điểm / số đăng ký môn, cần ghép đúng '
              'năm, chương trình và phạm vi thí sinh. Hai file điểm chưa cung cấp số đăng ký và tình trạng '
              'miễn/vắng thi, nên hai tỷ lệ này chưa tính được. Không gọi tỷ lệ có điểm trên bảng là tỷ lệ đăng ký.',
              '**Vì sao cơ chế thi quan trọng?** Năm 2023, học sinh THPT xét tốt nghiệp thường thi Toán, Văn, '
              'Ngoại ngữ và một bài KHTN (Lý/Hóa/Sinh) hoặc KHXH (Sử/Địa/GDCD). '
              'Năm 2025 CT2018, Toán/Văn bắt buộc, chỉ chọn hai môn còn lại đã học ở lớp 12 '
              '(Ngoại ngữ có ngoại lệ về ngôn ngữ). Vì vậy, không thể diễn giải giảm số bài Sinh '
              'như một thay đổi độc lập về sở thích: trước đây thi KHTN thường có cả ba điểm, nay Hóa và Sinh '
              'cạnh tranh với các môn tự chọn khác. '
              '[Quy chế 2023](https://vqa.moet.gov.vn/vi/laws/detail/Van-ban-hop-nhat-Thong-tu-ban-hanh-Quy-che-thi-tot-nghiep-trung-hoc-pho-thong-31/?download=1&id=0), '
              '[Điều 20 quy chế 2025](https://vqa.moet.gov.vn/uploads/news/2024_12/final-quy-che-thi-tot-nghiep-thpt.pdf).']
    new=current[current.subject.isin(['civics','economics_law','informatics','technology'])]
    lines += [table(pd.DataFrame([{'Môn riêng theo chương trình':r.subject_label,'Năm':r.year,'Có điểm':int(r.n),'Tỷ lệ có điểm (%)':r.percent} for r in new.itertuples()])),
              '**Diễn giải bảng:** GDKT&PL, Tin học và Công nghệ có số liệu 2025, nhưng không gán tỷ lệ 2023 bằng 0 '
              'để tính “tăng trưởng”. Tin/Công nghệ chưa có bài thi tương ứng năm 2023; GDCD và GDKT&PL khác nội dung. '
              'GDCD 2023 vẫn được đếm riêng và hiển thị đầy đủ, không ghép thành một môn bất biến với GDKT&PL. '
              'Công nghệ trong CSV gộp hai định hướng Công nghiệp và Nông nghiệp nên chỉ phân tích tổng gộp.',
              '### 3.2. Điểm các tổ hợp thay đổi thế nào?']
    paired=[]; thresholds=[]
    for code in ALL_COMBINATIONS:
        a=summary.loc[(2023,code)]; b=summary.loc[(2025,code)]
        paired.append({'Tổ hợp':code,'Đủ điểm 2023':int(a.n),'Đủ điểm 2025':int(b.n),
                       'TB 2023':a['mean'],'TB 2025':b['mean'],'Thay đổi TB':b['mean']-a['mean']})
        thresholds.append({'Tổ hợp':code,'Top 20% 2023':a.p80,'Top 20% 2025':b.p80,
                           'Top 10% 2023':a.p90,'Top 10% 2025':b.p90,'Thay đổi top 10%':b.p90-a.p90})
    lines += [table(pd.DataFrame(paired)),
              '**Diễn giải bảng:** A00 giảm trung bình 1,41 điểm, B00 giảm 2,32; C00 tăng 0,75; '
              'D01 giảm 0,31. Mỗi hàng chỉ xét người đủ ba môn của hàng đó. '
              '**B00 giảm 324.554 → 44.964 người (−86,15%)**: đây là quy mô nhóm đủ Toán/Hóa/Sinh. '
              'Năm 2025 có 69.895 người có điểm Sinh, nhưng chỉ 44.964 người đồng thời có Hóa và Toán; '
              'không được lấy toàn bộ người có Sinh làm B00. Một người vẫn có thể xuất hiện ở nhiều hàng '
              '(ví dụ đủ Toán/Văn/Lý/Hóa thuộc A00, C01, C02). '
              'Bảy mã có GDCD/GDKT&PL chỉ so sánh mô tả theo mã, không xem nội dung môn bất biến.',
              '### 3.3. “Điểm chuẩn ảo”: bao nhiêu điểm để vào top 20% hoặc top 10%?',
              '**Thang tổng 30 điểm, không ưu tiên hay nhân hệ số.** Top 20% dùng P80; top 10% dùng P90 '
              'trên tập người đủ điểm của từng tổ hợp/năm. Đây là ngưỡng phân phối, không phải điểm trúng tuyển. '
              'Dấu “thay đổi” luôn là 2025 trừ 2023.',table(pd.DataFrame(thresholds)),
              '**Diễn giải bảng:** Với A00, ngưỡng top 10% tăng **24,45 → 25,25**, dù trung bình giảm. '
              'B00 cũng tăng **23,95 → 24,75**; C00 tăng **23,25 → 25,25**; D01 giảm **23,85 → 22,50**. '
              'Ví dụ, người đạt 25,25 A00 năm 2025 chạm ngưỡng P90 của nhóm đủ điểm A00 trong dữ liệu. '
              'Đồng hạng ở ngưỡng khiến nhóm “đạt từ ngưỡng trở lên” có thể lớn hơn đúng 10%; '
              'bảng chi tiết phía sau ghi riêng tỷ lệ lớn hơn và lớn hơn hoặc bằng ngưỡng.',
              '**Kết luận từ hai bảng tổ hợp:** điểm trung bình giảm không kéo theo mọi ngưỡng top đều giảm. '
              'Ở A00/B00, phần giữa và đuôi cao dịch chuyển khác hướng. Thay đổi lựa chọn môn làm tập người '
              'được so sánh khác nhau, nên không đồng nhất kết quả này với mức thay đổi năng lực của cùng một nhóm học sinh.']
    lines += [
              '**Giới hạn của mục tiêu nghiên cứu:** dữ liệu cho thấy thay đổi điểm trong bối cảnh đổi chương trình '
              'và cách thi. Hai năm quan sát không tách được phần tác động riêng của chương trình 2018, dạng đề, '
              'cách chấm, lựa chọn môn và thành phần thí sinh.']
    return lines


def external_review(root, table):
    path=root/'outputs/audits/external_verification.json'
    if not path.exists(): return []
    audit=json.loads(path.read_text(encoding='utf-8'))
    run=json.loads((root/'outputs/parts3_5_run.json').read_text(encoding='utf-8'))
    if audit.get('inputs') and {r['sha256'] for r in audit['inputs']}!={r['sha256'] for r in run['inputs']}:
        raise ValueError('External verification belongs to different input files; rerun src.verify_external_scores')
    stats=read(root,'audits','external_score_statistics')
    bins=read(root,'audits','external_score_frequencies')
    rows=[]
    for (year,subject),group in stats.groupby(['year','subject'],sort=False):
        n=group[group.metric.eq('n')].iloc[0]
        hist=bins[(bins.year==year)&bins.subject.eq(subject)]
        rows.append({'Năm':year,'Môn':SUBJECT_LABELS[subject],'Số bài trên máy':int(n.local),
                     'Số bài công bố':int(n.published),'Lệch số bài':int(n.difference),
                     'Cột phổ điểm khớp':f'{int(hist.difference.eq(0).sum())}/{len(hist)}'})
    lines=['## Đối chiếu internet: điểm, phổ điểm và điều kiện thi',
           'Đối chiếu ngày **17/10/2026** với báo cáo thống kê Bộ GDĐT ngày 15/7/2025 trên Cổng Chính phủ '
           'và bảng phổ điểm 2023 do cơ quan nhà nước đăng lại. Đếm số bài và tần số phải khớp chính xác; '
           'điểm trung bình/độ lệch chuẩn được so trong sai số làm tròn công bố 0,005. '
           '[PDF gốc 2025](https://bcp.cdnchinhphu.vn/334894974524682240/2025/7/15/bao-cao-15-7-2025-version3-1-1752569726486925110557.pdf), '
           '[bảng 9 môn 2023](https://dbndnghean.vn/cong-bo-diem-thi-tot-nghiep-trung-hoc-pho-thong-nam-2023-9656.htm), '
           '[đối chứng Toán/Lý/Hóa 2023 trên Cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/pho-diem-cac-mon-toan-vat-ly-hoa-hoc-thi-tot-nghiep-thpt-2023-119230718104051335.htm).',
           table(pd.DataFrame(rows)),
           '**Diễn giải bảng:** Năm 2025, cả **11 nhóm môn trong CSV khớp số bài và toàn bộ 420 cột phổ điểm** '
           '(Toán chia khoảng 0,5; các môn còn lại 0,25, khoảng đóng bên phải; điểm 0 ở khoảng đầu). '
           '**106/106 chỉ số tổng hợp được đối chiếu đều khớp**, gồm số bài, trung bình, trung vị, độ lệch chuẩn, '
           'mốt, số điểm 0/10, số ≤1, số <5 và số ≥7 khi tài liệu có chỉ tiêu tương ứng. '
           'Công nghệ trên máy chỉ đối chiếu tổng Công nghiệp + Nông nghiệp, không xác minh riêng từng định hướng.',
           '**Sai lệch 2023 còn phải công bố:** Toán có thêm một bài ở mức 4,4; Lý thêm một bài ở mức 2,0; '
           'Hóa thêm một bài ở mức 4,0 so với bảng ban đầu. Vì đều dưới 5, số bài dưới 5 cũng hơn một mỗi môn. '
           'Chưa có bằng chứng xác định nguyên nhân (thời điểm thu thập, cập nhật hay sai nguồn); '
           'không tự xóa một thí sinh để ép khớp. Các ngưỡng và hệ số báo cáo vẫn tính từ file nguồn hiện có.',
           '**Văn 2023 cần phân biệt điểm gốc và cách hiển thị phổ:** có **3.962 điểm không nằm đúng lưới 0,25**. '
           'Điểm gốc cho 73.656 bài <5, còn công bố ghi 73.622. Khi chỉ để đối chiếu, đưa điểm gốc về mốc 0,25 gần nhất '
           'thì **41/41 tần số công bố khớp và số <5 bằng 73.622**. Sự khớp này là bằng chứng về cách biểu diễn/gom điểm, '
           'chưa phải xác nhận trực tiếp quy trình làm tròn của Bộ. Không làm tròn điểm gốc khi tính tổ hợp hoặc tương quan.',
           '**Điều kiện thi 2025 được kiểm tra trong dữ liệu:** không có người nào có quá hai điểm tự chọn '
           '(không đếm Anh lần nữa cạnh Ngoại ngữ). Có 1.120.879 người đủ hai điểm tự chọn, '
           '9.700 người chỉ có một, 557 người không có điểm tự chọn; trong nhóm cuối có thể thiếu/vắng/bảo lưu '
           'hoặc thuộc diện khác, không tự kết luận sai quy chế từ ô trống. Điều 20 cho phép thí sinh đã tốt nghiệp '
           'đăng ký các môn theo nguyện vọng, tối đa hai môn tự chọn. Năm 2025 có cả đề CT2006 và CT2018; '
           'cohort trong báo cáo là file CT2018 người dùng xác nhận, không gán mọi dữ liệu mang năm 2025 thành CT2018. '
           '[Thông tư 24/2024, Điều 2 và Điều 20](https://vqa.moet.gov.vn/uploads/news/2024_12/final-quy-che-thi-tot-nghiep-thpt.pdf).',
           '**Dạng đề/cách chấm đã đổi:** một số môn 2025 thêm câu đúng–sai và trả lời ngắn. '
           'Trong một câu đúng–sai bốn ý, đúng 1/2/3/4 ý lần lượt được 0,10/0,25/0,50/1,00 điểm. '
           'Không áp dụng mô tả “ba dạng câu” cho mọi môn: Ngoại ngữ dùng nhiều lựa chọn; cấu trúc cụ thể tùy môn. '
           'Vì vậy, cùng thang 10 không bảo đảm cùng phép đo hay cùng độ khó. '
           '[Cục Quản lý chất lượng: định dạng đề](https://vqa.moet.gov.vn/vi/news/thong-bao/cau-truc-dinh-dang-de-thi-tot-nghiep-thpt-tu-nam-2025-74.html), '
           '[thang điểm từng dạng trên Cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/cau-truc-de-thi-tot-nghiep-thpt-tu-nam-2025-119240308200554932.htm).',
           '**Danh mục tổ hợp nguồn có lỗi mô tả:** không dùng nguyên xi `danh_muc_to_hop.csv` làm quy tắc tính. '
           'Ví dụ Toán/Văn/Hóa là C02, không phải D04; D04 là Toán/Văn/Tiếng Trung; '
           'D09 dùng Toán/Sử/Anh, D10 dùng Toán/Địa/Anh. Bảng mapping 24 mã trong báo cáo đã dùng ba môn tường minh '
           'và đối chiếu lại các tổng `diem_*`. Không coi A01 đồng nghĩa D90 hoặc B08 đồng nghĩa D99 như ghi chú nguồn. '
           '[ĐHQGHN, bảng môn theo mã năm 2025](https://sis.vnu.edu.vn/Images/images/2025/CHUY%E1%BB%82N%20B%C3%80I%20WEB/250725_-Thong-bao-ve-bang-quy-doi-tuong-duong-va-chenh-cac-to-hop_-Ban-dang-web-2.pdf), '
           '[ĐH KHTN: tổ hợp 2025](https://hus.vnu.edu.vn/thong-bao/dao-tao-tuyen-sinh/thong-bao-diem-nguong-dam-bao-chat-luong-nam-2025-142145).',
           '**Phương pháp thống kê:** ngưỡng P80/P90 theo inverse empirical CDF là một lựa chọn hợp lệ, '
           'cần nêu rõ vì khác cách nội suy mặc định. Pearson đo liên hệ tuyến tính, Spearman đo liên hệ thứ hạng/đơn điệu; '
           'n≥100 là ngưỡng chất lượng do dự án chọn, không phải định luật thống kê. '
           '[NumPy quantile](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html), '
           '[SciPy Pearson](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html), '
           '[SciPy Spearman](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).',
           '**Mức xác nhận đạt được:** năm 2025 khớp rất tốt ở mức tổng hợp/phổ môn; năm 2023 có các khác biệt nhỏ đã nêu. '
           'Khớp phổ từng môn không xác thực được điểm của từng người hoặc việc ghép các môn theo SBD. '
           'Chưa có nguồn công bố độc lập đủ cả 24 ngưỡng tổ hợp và toàn bộ tương quan để xác nhận từng kết quả đó. '
           'B00 324.554/44.964 là kết quả tính lại nội bộ trên điểm ghép, không gọi là số nhóm đã được Bộ công bố xác nhận. '
           '[Toàn bộ phép đối chiếu](../outputs/audits/external_verification.json).']
    return lines


def explain_table(root, folder, text):
    columns=[c.strip() for c in text.splitlines()[0].strip('|').split('|')]
    keys=set(columns)
    if 'Biến động số người' in keys:
        explanation='Mỗi môn được đếm độc lập theo cột điểm thực có. Cột số người cho biết quy mô tăng/giảm; cột % so với 2023 chia mức tăng/giảm đó cho số người năm 2023. Hai tỷ lệ năm dùng mẫu số người có ít nhất một điểm của từng năm; chênh lệch tỷ lệ đo bằng điểm phần trăm. Toán/Văn tăng cả quy mô và tỷ lệ; Lý tăng 20.410 người (+6,24%) nhưng tỷ lệ giảm 1,42 điểm phần trăm. Số đăng ký chưa có nên đây là tỷ lệ có điểm, không phải tỷ lệ đăng ký.'
    elif 'Tổ hợp' in keys:
        explanation='Mỗi hàng nêu đúng ba môn để cộng. Bảy mã có GDCD/GDKT&PL đổi nội dung, nên đọc như so sánh mô tả. B08/D08 trùng bộ môn; giữ hai mã của nguồn nhưng không cộng hai hàng thành hai nhóm người độc lập.'
    elif 'n_recomputed' in keys:
        explanation='“Đủ điểm tính lại” đếm người đủ ba điểm từ từng môn; “Tổng nguồn có điểm” đếm tổng có sẵn trong file. Các tổng/điều kiện đủ điểm 2025 khớp cả 24 mã. Năm 2023 không có cột tổng nguồn để đối chiếu; stored_unavailable là thiếu cột đối chứng, không phải tính sai.'
    elif 'n_eligible' in keys:
        explanation='Đây là kiểm tra nhãn nhiều tổ hợp, khác với kiểm tra phép cộng. n_disagreement=0 ở 24 mã năm 2025 nghĩa là cách tính lại theo đủ ba môn khớp nhãn to_hop_du_thi của nhan. Năm 2023 tự suy ra từ điểm, không có nhãn nguồn để xác nhận đăng ký thật.'
    elif 'n_eligible_combinations' in keys:
        explanation='Một hàng cho biết có bao nhiêu người đủ đúng k tổ hợp. k=0 vẫn được giữ. Tổng n_students trong từng năm bằng tổng dòng nguồn; một người có nhiều tổ hợp là hệ quả hợp lệ của ba môn chồng nhau, không phải bản ghi bị nhân đôi.'
    elif 'target_top_percent' in keys:
        explanation='“Ngưỡng điểm” là tổng chạm P80/P90, “Bằng ngưỡng” đếm người đồng điểm tại đó; “Cao hơn (%)” và “Từ ngưỡng (%)” phân biệt người vượt ngưỡng với người chạm ngưỡng. Ví dụ P90 A00 2025=25,25: đạt 25,25 nằm trong nhóm từ ngưỡng top 10%, nhưng tỷ lệ thực có thể hơn 10% do đồng hạng. Không dùng làm điểm đỗ đại học.'
    elif 'delta_n' in keys and 'combination' in keys:
        explanation='Các số là 2025 trừ 2023; dấu âm nghĩa là giảm. A00 giảm TB 1,41 nhưng P90 tăng 0,80; B00 giảm TB 2,32 nhưng P90 tăng 0,80; C00 tăng TB 0,75 và P90 tăng 2,00. Vì vậy cần đọc cả mức giữa và nhóm cao, không chỉ trung bình. Cột phân loại nhắc bảy mã đổi môn.'
    elif 'combination' in keys and 'mean' in keys:
        explanation='n là số người đủ cả ba môn; mean/median là trung bình/trung vị của tổng trên thang 30; sd đo độ trải rộng, IQR là độ rộng 50% giữa. P80/P90 là ngưỡng top 20%/10%. Ví dụ B00 năm 2025 trung bình 18,29, trung vị 18,00 và P90 24,75: phần lớn tổng điểm thấp hơn xa nhóm đuôi cao.'
    elif 'delta_percent' in keys:
        explanation='delta_percent tính theo điểm phần trăm, không phải phần trăm tăng trưởng tương đối. Sinh giảm 25,72 điểm phần trăm; Lý chỉ giảm tỷ lệ 1,42 điểm phần trăm dù số bài tăng. Khác biệt về cơ chế thi và mẫu số ảnh hưởng trực tiếp các tỷ lệ này.'
    elif 'counts_as_separate_exam' in keys:
        explanation='n đếm người có điểm môn, percent chia cho người có ít nhất một điểm, percent_all_rows chia cho mọi dòng. Anh đã nằm trong Ngoại ngữ nên không cộng lại. Môn mới/đổi nội dung phải đọc riêng; ô trống không tự xác định được không chọn, miễn thi hay vắng thi.'
    elif 'conditional_probability' in keys:
        explanation='Mỗi hàng hỏi: trong người có đủ hai môn và X đạt P80, bao nhiêu người cũng đạt P80 của Y? conditional_probability=0,47 tương đương 47%. So với baseline_probability để biết mức đi cùng nhau vượt tỷ lệ nền bao nhiêu. Đây là liên hệ cùng xuất hiện điểm cao, không phải xác suất nhân quả hay kết quả dự đoán cho từng người.'
    elif 'delta_pearson_r' in keys:
        explanation='delta r là r2025−r2023, không phải phần trăm thay đổi điểm. Sử–Địa tăng khoảng 0,151; Toán–Anh giảm khoảng 0,095. Đọc cùng bảng số người đủ cặp và các cỡ mẫu trong CSV: tập người có điểm đã thay đổi. Hệ số trống nghĩa là không tính được trên mẫu đủ điều kiện, không có nghĩa là r=0.'
    elif 'pearson_r' in keys and 'combination' in keys:
        explanation='Hệ số được tính lại chỉ trong người đủ ba môn của từng tổ hợp. Nó kiểm tra xem nhận xét ở toàn bộ cặp có phụ thuộc vào nhóm đủ tổ hợp hay không. Có 5 nhóm tham chiếu × 3 cặp × 2 năm=30 hàng; 5 nhóm này phục vụ kiểm tra độ nhạy, còn phân tích tổng điểm vẫn đủ 24 mã.'
    elif 'pearson_r' in keys:
        explanation='Mỗi hệ số dùng đúng những người có cả hai điểm, không ghép hai bảng phổ độc lập. Pearson r đo quan hệ tuyến tính; Spearman rho đo thứ hạng. Bảng chỉ giữ mỗi cặp một lần, bỏ đường chéo để dễ đọc; CSV vẫn giữ ma trận đầy đủ. n_pair cho biết bằng chứng có bao nhiêu cặp; status không đủ mẫu/không phương sai thì hệ số để trống. Sử–Địa 2025 r≈0,759 là liên hệ dương mạnh trong nhóm được quan sát.'
    else:
        raise ValueError(f'Missing table explanation: {columns}')
    labels={'cohort':'Nhóm năm/chương trình','combination':'Tổ hợp','year':'Năm','n':'Số người đủ điểm',
            'mean':'Trung bình','median':'Trung vị','sd':'Độ lệch chuẩn','iqr':'IQR','p80':'Top 20% (P80)','p90':'Top 10% (P90)',
            'delta_n':'Thay đổi số người','delta_mean':'Thay đổi TB','delta_median':'Thay đổi trung vị',
            'delta_p80':'Thay đổi P80','delta_p90':'Thay đổi P90','comparison_class':'Loại so sánh',
            'target_top_percent':'Nhóm top (%)','threshold':'Ngưỡng điểm','n_at':'Bằng ngưỡng','pct_gt':'Cao hơn (%)','pct_ge':'Từ ngưỡng (%)',
            'subject':'Mã môn','subject_label':'Môn','subject_x':'Môn X','subject_y':'Môn Y','n_pair':'Số người đủ cặp',
            'pearson_r':'Pearson r','spearman_rho':'Spearman rho','status':'Trạng thái',
            'denominator':'Mẫu số có điểm','denominator_all_rows':'Mẫu số mọi dòng','percent':'Tỷ lệ có điểm (%)',
            'percent_all_rows':'Tỷ lệ mọi dòng (%)','counts_as_separate_exam':'Đếm môn riêng','comparability':'Khả năng so sánh',
            'n_from':'Số bài 2023','n_to':'Số bài 2025','percent_from':'Tỷ lệ 2023 (%)','percent_to':'Tỷ lệ 2025 (%)',
            'delta_percent':'Thay đổi (điểm %)','n_recomputed':'Đủ điểm tính lại','n_stored':'Tổng nguồn có điểm',
            'n_missingness_mismatch':'Sai khác có/thiếu','n_sum_mismatch':'Sai khác phép cộng',
            'n_eligible':'Đủ điểm tính lại','n_source_label':'Có nhãn nguồn','n_disagreement':'Sai khác nhãn',
            'n_eligible_combinations':'Số tổ hợp mỗi người','n_students':'Số người',
            'pearson_r_from':'r 2023','pearson_r_to':'r 2025','delta_pearson_r':'Thay đổi r',
            'spearman_rho_from':'rho 2023','spearman_rho_to':'rho 2025','delta_spearman_rho':'Thay đổi rho',
            'p80_x':'Ngưỡng cao X','p80_y':'Ngưỡng cao Y','n_x_high':'Số người X cao',
            'baseline_probability':'Xác suất nền Y cao','conditional_probability':'Xác suất Y cao khi X cao'}
    raw=text.splitlines(); raw[0]='| '+' | '.join(labels.get(c,c) for c in columns)+' |'
    displayed='\n'.join(raw)
    for code,label in SUBJECT_LABELS.items(): displayed=displayed.replace('| '+code+' |','| '+label+' |')
    return displayed+'\n\n**Diễn giải bảng:** '+explanation


def explain_figure(root, folder, image):
    name=image.stem
    if name.startswith('combination_'):
        page=int(name.rsplit('_',1)[-1]) if '_page_' in name else 1
        codes=list(ALL_COMBINATIONS)[6*(page-1):6*page]
        summary=read(root,'combinations','combination_summary').set_index(['year','combination'])
        points=[]
        for code in codes:
            a=summary.loc[(2023,code)]; b=summary.loc[(2025,code)]
            if 'boxplots' in name:
                points.append(f'**{code}**: trung vị {a["median"]:.2f} → {b["median"]:.2f}; IQR {a.iqr:.2f} → {b.iqr:.2f}')
            else:
                points.append(f'**{code}**: TB {a["mean"]:.2f} → {b["mean"]:.2f}; P90 {a.p90:.2f} → {b.p90:.2f}')
        how=('Đường giữa hộp là trung vị; hộp chứa 50% ở giữa. Hộp rộng hơn theo trục điểm biểu thị phân tán lớn hơn; '
             'không suy ra đề tốt hơn chỉ từ hộp rộng. Các dấu ngoài râu không bị xóa khỏi dữ liệu.' if 'boxplots' in name else
             'Bên trái là tỷ lệ trong từng khoảng tổng điểm; bên phải là tỷ lệ tích lũy ≤ điểm đang đọc. '
             'Tại cùng một mức điểm, ECDF cao hơn nghĩa là nhiều người nằm dưới mức ấy hơn. Mỗi năm được chuẩn hóa riêng, không so chiều cao như số bài tuyệt đối.')
        title=('Boxplot' if 'boxplots' in name else 'Phổ tổng điểm và ECDF')+' — '+', '.join(codes)
        return title,how+'\n\n'+'; '.join(points)+'. Các mã có dấu * thay GDCD bằng GDKT&PL, cần đọc riêng nội dung môn.'
    if name=='participation':
        return 'Tỷ lệ có điểm từng môn — xu hướng cơ cấu môn thi','So chiều cao hai cột cùng một môn trên mẫu số có ít nhất một điểm. Toán tăng tỷ lệ 0,97 và Văn tăng 0,54 điểm phần trăm. Sinh, Hóa, Sử, Địa và Anh giảm tỷ lệ; Lý tăng số người 6,24% nhưng giảm tỷ lệ 1,42 điểm phần trăm. Hình thể hiện tỷ lệ nên không dùng chiều cao cột để kết luận số người tăng/giảm. Ngoại ngữ chứa cả Anh, không cộng hai cột này. Môn mới/đổi chương trình có dấu * không phải tăng từ 0 theo cùng một phép đo. Thay đổi cơ chế chọn môn là ngữ cảnh chính, chưa phải bằng chứng thay đổi sở thích riêng.'
    if name=='top_threshold_comparison':
        return 'Ngưỡng top 20% và top 10% — đủ 24 tổ hợp','Hai điểm/đường ở mỗi tổ hợp biểu thị ngưỡng hai năm; dịch sang phải nghĩa là cần tổng cao hơn để chạm cùng phân vị trong nhóm đó. A00 và B00 có P90 tăng 0,80; C00 tăng 2,00; D01 giảm 1,35. Không đọc điểm này như ngưỡng trúng tuyển hay quy đổi điểm đại học.'
    if name=='optional_cooccurrence':
        data=read(root,'combinations','cooccurrence'); parts=[]
        for y in [2023,2025]:
            r=data[(data.year==y)&data.subject_x.eq('chemistry')&data.subject_y.eq('biology')].iloc[0]
            parts.append(f'{y}: Hóa–Sinh cùng có điểm {int(r.n):,} người ({r.percent:.2f}%)')
        return 'Các cặp môn cùng có điểm','Màu thể hiện tỷ lệ có đủ hai điểm trên mẫu có ít nhất một môn; đây là bản đồ cơ cấu thi, không phải hệ số tương quan điểm. '+'; '.join(parts)+'. Năm 2023 các môn trong cùng bài KHTN/KHXH thường xuất hiện cùng nhau; năm 2025 chỉ chọn hai môn tự chọn nên cấu trúc này thay đổi.'
    if name.startswith(('pearson_r_','spearman_rho_','n_pair_')):
        year=int(name[-4:]); pairs=read(root,'correlations','pairwise_correlations')
        unique=pairs[(pairs.year==year)&(pairs.subject_x<pairs.subject_y)&pairs.status.eq('ok')]
        if name.startswith('n_pair'):
            low=unique.loc[unique.n_pair.idxmin()]; high=unique.loc[unique.n_pair.idxmax()]
            return f'Số người có đủ từng cặp môn — {year}',f'Mỗi ô là số người dùng tính hệ số tương ứng. Trong các cặp đủ mẫu, ít nhất là {SUBJECT_LABELS[low.subject_x]}–{SUBJECT_LABELS[low.subject_y]} ({int(low.n_pair):,}), nhiều nhất {SUBJECT_LABELS[high.subject_x]}–{SUBJECT_LABELS[high.subject_y]} ({int(high.n_pair):,}). Ô thiếu mẫu không được đọc như tương quan bằng 0. Các cặp giữa nhóm tự nhiên/xã hội có thể không có người cùng thi ở 2023 do bài thi khác nhau.'
        metric='pearson_r' if name.startswith('pearson') else 'spearman_rho'
        strongest=unique.loc[unique[metric].abs().idxmax()]
        return f'{"Pearson" if metric=="pearson_r" else "Spearman"} giữa các môn — {year}',f'Màu dương đậm hơn thể hiện liên hệ {"tuyến tính" if metric=="pearson_r" else "thứ hạng/đơn điệu"} dương mạnh hơn. Bỏ đường chéo tự tương quan bằng 1. Cặp có độ lớn hệ số lớn nhất là {SUBJECT_LABELS[strongest.subject_x]}–{SUBJECT_LABELS[strongest.subject_y]}: {strongest[metric]:.3f}, n={int(strongest.n_pair):,}. Ô trống là không xác định/không đủ mẫu; không suy ra hai môn không liên quan. Đọc cùng hình cỡ mẫu ngay trong bộ hình này.'
    if name.startswith('hexbin_'):
        identifiers={'hexbin_math_physics':('math','physics'),'hexbin_physics_chemistry':('physics','chemistry'),
                     'hexbin_chemistry_biology':('chemistry','biology'),'hexbin_history_geography':('history','geography'),
                     'hexbin_math_english':('math','english')}
        x,y=identifiers[name]; pairs=read(root,'correlations','pairwise_correlations'); parts=[]
        for year in [2023,2025]:
            r=pairs[(pairs.year==year)&pairs.subject_x.eq(x)&pairs.subject_y.eq(y)].iloc[0]
            parts.append(f'{year}: r={r.pearson_r:.3f}, rho={r.spearman_rho:.3f}, n={int(r.n_pair):,}')
        return f'Mật độ điểm {SUBJECT_LABELS[x]} – {SUBJECT_LABELS[y]}','Mỗi vùng lục giác gom các cặp điểm gần nhau; dải nghiêng lên cho thấy hai môn thường tăng cùng nhau. '+'; '.join(parts)+'. Hình dùng tối đa 50.000 cặp lấy mẫu/năm để dễ quan sát, còn hệ số tính trên toàn bộ cặp hợp lệ. Thang màu biểu thị số điểm trong vùng của mẫu vẽ, không suy ra quy mô dân số hai năm từ độ đậm.'
    if name=='high_score_concordance':
        return 'Người có điểm cao ở môn X có thường cao ở môn Y?','So cột xác suất Y đạt P80 khi X đạt P80 với tỷ lệ nền Y đạt P80 trên cùng tập người đủ hai môn. Với Toán–Lý năm 2023, xác suất có điều kiện khoảng 47,13%, cao hơn nền 21,32%. Nếu cột có điều kiện cao hơn nền, điểm cao thường đi cùng nhau; điều đó không chứng minh X gây ra Y. Ngưỡng tính riêng theo năm và giữ người đồng điểm.'
    raise ValueError(f'Missing figure explanation: {name}')
