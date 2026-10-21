"""A single Part 4 report: every subject relation first, then all PCA blocks."""
from pathlib import Path
import numpy as np,pandas as pd
from src.analysis_catalog import label
from src.correlation_pca import rank_pairs
from src.inference_io import number as n,md_table,image_block,build_reading_notebook

REPORT='docs/phan_4_tuong_quan_pca_2023_2025.md'
CORE=['math','literature','foreign_language:N1','physics','chemistry','biology','history','geography']

def _labels(table):
    t=table.copy()
    for col in ['subject_x','subject_y']:
        if col in t:t[col]=t[col].map(label)
    return t

def render_report(root:Path,*,include_combinations=False):
    folder=root/'outputs/subject_relations';pairs=pd.read_csv(folder/'pairwise_correlations.csv');delta=pd.read_csv(folder/'correlation_deltas.csv');high=pd.read_csv(folder/'high_score_concordance.csv')
    ranked=rank_pairs(pairs);sections=['# Phần 4 — Tương quan giữa các môn và PCA tổ hợp THPT 2023–2025\n',
        '**2023 — CT2006** so với **2025 — CT2018**. Mỗi hệ số dùng người có đủ cả hai điểm. Không điền thiếu, không tạo mẫu thi đủ mọi môn. Ngoại ngữ tách N1–N7, GDCD và GDKT&PL giữ riêng.\n',
        '## Kết quả chính — đọc phần này trước\n']
    for year in (2023,2025):
        all_top=ranked.loc[ranked.year.eq(year)].iloc[0];core=ranked.loc[ranked.year.eq(year)&ranked.subject_x.isin(CORE)&ranked.subject_y.isin(CORE)].iloc[0]
        sections.append(f'- **{year}:** cặp mạnh nhất trong mọi môn được xếp hạng (n≥100) là {label(all_top.subject_x)}–{label(all_top.subject_y)}, r={n(all_top.pearson_r,3)}, n={n(int(all_top.n_pair))}. Trong riêng 8 môn chung để đối chiếu Duy, cặp cao nhất là {label(core.subject_x)}–{label(core.subject_y)}, r={n(core.pearson_r,3)}.\n')
    sections += ['## 4.1. Cách đọc r, rho, ma trận và số mẫu\n',
        '**Pearson r** đo liên hệ tuyến tính trong [−1,1]; dương là xu hướng cùng tăng, âm là ngược chiều. r=0,7 không nghĩa 70% học sinh giỏi cả hai môn; r gần0 cũng không loại mọi quan hệ phi tuyến. **Spearman rho** đo liên hệ thứ hạng/đơn điệu, được rank lại sau khi lọc đúng cặp.\n',
        '**n_pair** là người có đủ cả hai điểm, không phải số người cả năm. Một người có thể thuộc nhiều cặp; không cộng n các cặp thành số người. Các cặp Ngoại ngữ khác mã thường không có điểm đồng thời; ô trống là không ước lượng được, không phải r=0. Đường chéo tự tương quan được bỏ qua để tập trung cặp khác môn.\n',
        '**Chính sách mẫu:** n<30 hoặc một biến hằng thì không báo r/rho; 30≤n<100 có cờ mẫu nhỏ, không xếp hạng chính. Mốc100 đồng bộ tiêu chí chất lượng của phần3, không là định luật thống kê. CI Fisher là xấp xỉ, không loại được sai lệch chọn mẫu.\n',
        '## 4.2. Ma trận mỗi năm — mọi môn có điểm\n']
    for year in (2023,2025):
        t=pairs.loc[pairs.year.eq(year)];valid=t.loc[t.pearson_r.notna()]
        sections += [f'### 4.2.{1 if year==2023 else 2}. Năm {year}\n',
            md_table(pd.DataFrame([[len(t),len(valid),int(t.n_pair.eq(0).sum()),int(t.n_pair.between(1,29).sum())]],columns=['Tổng cặp','Ước lượng được','Không người đủ cặp','Có mẫu nhưng n<30'])),
            '**Diễn giải bảng:** Tổng cặp là mọi cặp môn/ngôn ngữ trong năm đó, kể cả cặp không thể ước lượng. Thiếu theo cấu trúc thi không được lấp bằng 0 để tạo ma trận đầy.\n',
            image_block(f'outputs/subject_relations/figures/pearson_{year}.png',f'Pearson mọi môn {year}','Số trong ô là Pearson r; thang màu chung −1 đến1, ô xám không có ước lượng. Đọc cùng heatmap n phía dưới; không so độ đậm mà bỏ qua khác biệt tập mẫu.'),
            image_block(f'outputs/subject_relations/figures/spearman_{year}.png',f'Spearman mọi môn {year}','Spearman đối chiếu theo thứ hạng. Khi r và rho khác nhiều, cần xem hình cặp điểm, các điểm tập trung và quan hệ phi tuyến; không chọn chỉ hệ số lớn hơn để kết luận.'),
            image_block(f'outputs/subject_relations/figures/n_pair_{year}.png',f'Số mẫu từng cặp {year}','Số trong ô là n (k=nghìn, làm tròn để đọc); màu dùng log10(n+1) để thấy cả mẫu nhỏ/lớn. Bảng phụ lục giữ số đếm chính xác. n=0 ở cặp không đồng quan sát không có nghĩa tương quan bằng0.')]
    sections += ['## 4.3. Cặp môn nào đi cùng nhau nhất?\n',
        md_table(_labels(ranked.groupby('year',sort=True).head(10)[['year','subject_x','subject_y','n_pair','pearson_r','spearman_rho']]),['Năm','Môn X','Môn Y','n cặp','Pearson r','Spearman rho'],3),
        '**Diễn giải bảng:** Xếp hạng dương theo Pearson trong tập n≥100, không là bảng chất lượng môn học. Nên đọc rho và n cùng r; các ngôn ngữ/nhóm ít người có thành phần chọn mẫu riêng. Đây không phải quan hệ nhân quả. Bảng đầy đủ tất cả cặp ở cuối báo cáo.\n',
        '## 4.4. Cấu trúc tương quan thay đổi ra sao?\n',
        image_block('outputs/subject_relations/figures/delta_r.png','Chênh tương quan 2025 trừ 2023','Dương nghĩa r2025 cao hơn r2023 trong hai tập cặp tương ứng; âm là thấp hơn. Ô xám gồm cặp thiếu ở một năm hoặc không đủ mẫu, không phải delta0. Môn chỉ một năm không bị tạo một r giả ở năm còn lại.')]
    change=delta.loc[delta.delta_r.notna()].copy();change=change.loc[change.delta_r.abs().sort_values(ascending=False).index]
    sections += [md_table(_labels(change.head(15)[['subject_x','subject_y','n_2023','n_2025','r_2023','r_2025','delta_r','delta_rho']]),['Môn X','Môn Y','n2023','n2025','r2023','r2025','Δr','Δrho'],3),
        '**Diễn giải bảng:** Đây là thay đổi lớn nhất về trị tuyệt đối trong các cặp so được, không là phép so cùng người. Fisher z và q BH được lưu ở bảng đầy đủ; CI chênh z dùng thang z, không gọi là CI Δr. Ba cặp minh họa có thêm CI Δr bootstrap theo cùng dòng/cặp điểm, độc lập giữa hai năm.\n',
        '**Ý nghĩa và giới hạn:** Cách chọn môn và quy mô các tập cặp khác nhau giữa 2023/2025. Vì vậy r tăng không tự chứng minh chương trình làm kiến thức gắn kết hơn. Không lấy trung bình mọi ô ma trận như một kiểm định cấu trúc toàn cục; các ô có thể dùng người khác nhau.\n',
        '## 4.5. Toán cao có thường đạt Lý cao?\n']
    for i,(x,y) in enumerate([('math','physics'),('literature','history'),('history','geography')],1):
        h=high.loc[high.subject_x.eq(x)&high.subject_y.eq(y)&high.cutoff_mode.eq('P80')].sort_values('year').copy()
        for col in ['p_y_high_baseline','p_y_high_given_x_high','conditional_ci_low','conditional_ci_high']:h[col]=100*h[col]
        sections += [f'### 4.5.{i}. {label(x)} → {label(y)}\n',
            md_table(h[['year','n_pair','threshold_x','threshold_y','n_x_high','p_y_high_baseline','p_y_high_given_x_high','lift','conditional_ci_low','conditional_ci_high']],['Năm','n cặp','Ngưỡng X','Ngưỡng Y','n X cao','Nền Y cao (%)','Y cao khi X cao (%)','Lift','CI thấp (%)','CI cao (%)']),
            '**Diễn giải bảng:** Cao là từ P80 trở lên trong đúng tập cặp, tính cả bằng ngưỡng. “Nền” dùng toàn tập cặp; xác suất có điều kiện chỉ chia cho n X cao; lift là tỷ số hai xác suất. Đồng hạng khiến nhóm cao có thể hơn20%. CI Wilson coi ngưỡng thực nghiệm cố định, nên là xấp xỉ có điều kiện.\n',
            image_block(f'outputs/subject_relations/figures/hexbin_{x}_{y}.png',f'Cặp {label(x)}–{label(y)}','Mỗi ô lục giác gom những người có cặp điểm gần nhau; màu theo số người/ô trên thang log. Cụm nghiêng lên phù hợp đồng biến; không hiểu đây là mật độ Gaussian hoặc tỷ lệ đạt cả hai môn.\n')]
        r=h.loc[h.year.eq(2025)].iloc[0]
        sections.append(f'**Nhận xét bằng số:** Năm2025, tỷ lệ {label(y)} cao từ mức nền {n(r.p_y_high_baseline)}% lên {n(r.p_y_high_given_x_high)}% trong nhóm {label(x)} cao, lift={n(r.lift)}. Đây là đồng xuất hiện trong mẫu, không chứng minh giỏi X gây ra giỏi Y; ngưỡng riêng từng năm không là thang năng lực chung.\n')
    sections.append(image_block('outputs/subject_relations/figures/high_score_examples.png','So mức nền và xác suất có điều kiện','Cột xám là nền, cột màu là điều kiện X cao, thanh đen là CI Wilson. Các cặp đều được tính trong phụ lục đầy đủ, kể cả chiều ngược và sensitivity ngưỡng8 điểm; trang chính minh họa ba cặp để dễ đọc.'))
    if include_combinations:
        from src.report_combinations import part4_sections
        sections.append(part4_sections(root))
    else:sections.append('## 4.6. Phạm vi giai đoạn hiện tại\n\nTương quan/điểm cao từng môn đã tính; PCA toàn bộ khối được triển khai sau nghiệm thu phần từng môn. Không điền điểm thiếu để ép PCA tám môn vì không có mẫu đủ cả tám ở hai năm.\n')
    sections += ['## Độ trải rộng điểm và độ phân biệt của đề\n',
        'SD/IQR mô tả độ trải rộng tổng điểm, r mô tả quan hệ giữa hai môn. Chúng không đo trực tiếp độ phân biệt của từng câu hỏi. Cần dữ liệu theo câu và mô hình đo lường phù hợp để kết luận về chất lượng phân hóa đề; không thay bằng phát biểu “Toán–Lý tương quan cao nên đề phân hóa tốt”.\n',
        '## Phụ lục — mọi cặp môn, số mẫu và hệ số\n']
    for year in (2023,2025):
        sections += [f'### Mọi cặp năm {year}\n',md_table(_labels(pairs.loc[pairs.year.eq(year),['subject_x','subject_y','n_pair','pearson_r','spearman_rho','status']]),['Môn X','Môn Y','n cặp','r','rho','Trạng thái'],3),
            '**Diễn giải bảng:** Hàng thiếu r/rho vẫn được giữ để thể hiện phạm vi. estimated: đủ n≥100; limited_sample: 30≤n<100; insufficient_sample: n<30; constant_input: một biến hằng. Không cộng số người giữa các hàng.\n']
    sections.append('[Bảng tương quan](../outputs/subject_relations/pairwise_correlations.csv) · [Bảng thay đổi/CI/q](../outputs/subject_relations/correlation_deltas.csv) · [Mọi xác suất điểm cao hai chiều](../outputs/subject_relations/high_score_concordance.csv) · [Hồ sơ chạy](../outputs/subject_relations/run_metadata.json).\n\nPhương pháp: [Pearson/CI](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html), [Spearman](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).')
    return '\n\n'.join(sections)+'\n'

def build_notebook(root:Path,*,include_combinations=False):
    tables=['outputs/subject_relations/pairwise_correlations.csv','outputs/subject_relations/correlation_deltas.csv','outputs/subject_relations/high_score_concordance.csv']
    if include_combinations:tables+=['outputs/combination_inference/pca_summary.csv','outputs/combination_inference/pca_loadings.csv']
    build_reading_notebook(root,'notebooks/subject_relations/analysis.ipynb','Phần 4 — Tương quan và PCA',REPORT,
        'outputs/subject_relations/run_metadata.json',tables,'src.run_all_inference' if include_combinations else 'src.run_part4')
