"""One self-contained Part 2 report, with explanations next to every result."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.inference_io import number as n, ptext, md_table, image_block, build_reading_notebook

REPORT='docs/phan_2_kiem_dinh_thong_ke_2023_2025.md'

def _entity_section(row,descriptions,figure,heading,maximum=10):
    title=row['label'];key=row['entity_id'];parts=[f'### {heading}. {title}\n']
    d=descriptions.loc[descriptions.entity_id.eq(key),['year','n','mean','median','sd','iqr','pct_below_half','pct_ge_80','pct_ge_90']]
    parts.append(md_table(d,['Năm','Số có điểm','Trung bình','Trung vị','SD','IQR',f'<{maximum/2:g} (%)',f'≥{maximum*.8:g} (%)',f'≥{maximum*.9:g} (%)']))
    parts.append('**Diễn giải bảng:** n là số có điểm hợp lệ của riêng mục này, không phải mọi dòng trong năm. SD đo độ trải rộng; IQR là độ rộng vùng 50% ở giữa. Các tỷ lệ chia cho n của đúng hàng; nhóm ≥90% thang điểm đã nằm trong nhóm ≥80%, không cộng hai tỷ lệ.\n')
    compared=row['status']=='compared'
    if compared:
        direction='tăng' if row.delta_mean>=0 else 'giảm'
        magnitude=abs(row.cohen_d)
        band='dưới mốc 0,2' if magnitude<.2 else ('trong khoảng 0,2–0,5' if magnitude<.5 else ('trong khoảng 0,5–0,8' if magnitude<.8 else 'từ 0,8 trở lên'))
        parts.append(f'**Nhận xét bằng số:** Trung bình {n(row.mean_2023)} → {n(row.mean_2025)}, {direction} {n(abs(row.delta_mean))} điểm; trung vị {n(row.median_2023)} → {n(row.median_2025)}. Cohen’s d={n(row.cohen_d,3)} ({band} về |d| theo quy ước tham khảo). Tỷ số phương sai 2025/2023={n(row.variance_ratio,3)}. Không dùng nhãn độ lớn như kết luận hai năm tương đương.\n')
        methods=pd.DataFrame([
            ['Welch: trung bình',f't={n(row.welch_t,3)}, df={n(row.welch_df,1)}',ptext(row.welch_p),ptext(row.welch_p_holm)],
            ['MWU: thứ hạng',f'U={n(row.mwu_U,1)}',ptext(row.mwu_p),ptext(row.mwu_p_bh)],
            ['KS: toàn phân phối',f'D={n(row.ks_D,3)}; tại điểm {n(row.ks_location)}',ptext(row.ks_p_permutation),ptext(row.ks_p_permutation_bh)],
            ['Brown–Forsythe: độ phân tán',f'W={n(row.brown_forsythe_stat,3)}',ptext(row.brown_forsythe_p),ptext(row.brown_forsythe_p_bh)],
        ],columns=['Câu hỏi/phép thử','Thống kê','p gốc','p Holm / q BH'])
        parts.append(md_table(methods))
        parts.append(f'**Diễn giải bảng:** Welch dùng Holm trong family {int(row.welch_family_size)} phép thử trung bình; ba phép thăm dò dùng BH chung trong family {int(row.exploratory_family_size)} p hữu hạn. KS dùng hoán vị {int(row.ks_permutations):,} lần, p nhỏ nhất phân giải được là 0,0005. Giá trị “≈0” ở các phép tiệm cận là giới hạn tính số, không phải xác suất bằng 0.\n')
        parts.append(f'**Khoảng tin cậy và độ lớn:** Chênh trung bình có CI 95% [{n(row.delta_ci_low,3)}; {n(row.delta_ci_high,3)}] **điểm**. d có CI bootstrap 95% [{n(row.d_ci_low,3)}; {n(row.d_ci_high,3)}] **SD gộp**; Hedges’ g={n(row.hedges_g,3)}. A={n(row.mwu_A,3)} là xác suất thắng cộng nửa xác suất hòa, không phải chỉ P(2025>2023).\n')
        expl=f'Xanh là 2023, cam là 2025; histogram chia theo % trong từng năm, không theo số người tuyệt đối. Ở ECDF, chiều cao là % điểm không vượt ngưỡng. Khoảng cách lớn nhất hai ECDF là D={n(row.ks_D,3)}, gần mốc {n(row.ks_location)}; đây là {n(100*row.ks_D,1)} điểm phần trăm ở mốc đó, không phải tỷ lệ người tiến bộ.'
        p=row.welch_p_holm
        inference='có bằng chứng chênh trung bình theo mô hình ở mức 0,05 sau Holm' if pd.notna(p) and p<.05 else 'chưa có bằng chứng chênh trung bình ở mức 0,05 sau Holm'
        conclusion=f'Kết quả {inference}. Điều này cần đọc cùng mức đổi {n(row.delta_mean,3)} điểm, |d| và hình dạng; p lớn không chứng minh tương đương. So sánh là giữa hai tập điểm quan sát, không tách được độ khó, chương trình, cách chấm và thành phần thí sinh.'
    else:
        reason=row.get('reason','Không có dữ liệu so sánh phù hợp.')
        parts.append(f'**Phạm vi so sánh:** {reason} Có thống kê và hình cho năm hiện có; ô thiếu không được thay bằng 0 và không tạo p-value/CI liên năm giả.\n')
        expl='Chỉ vẽ các năm có điểm thực. Histogram là tỷ lệ trong từng mẫu; ECDF mô tả phần tích lũy. Không có đường của một năm không có nghĩa điểm của năm đó bằng 0.'
        conclusion='Kết quả mô tả đúng mẫu có điểm. Mục này không được đưa vào family kiểm định liên năm chính; khác môn/chương trình không được diễn giải như cùng một thang năng lực.'
    parts.append(image_block(figure,title+' — phổ điểm và ECDF',expl))
    parts.append('**Ý nghĩa và giới hạn:** '+conclusion+'\n')
    return '\n\n'.join(parts)

def render_report(root:Path,*,include_combinations=False)->str:
    folder=root/'outputs/statistics';t=pd.read_csv(folder/'subject_tests.csv');d=pd.read_csv(folder/'subject_descriptives.csv');d['entity_id']=d.subject_id
    cat=pd.read_csv(folder/'subject_catalog.csv');valid=t.loc[t.status.eq('compared')]
    top=valid.loc[valid.cohen_d.abs().sort_values(ascending=False).index].head(3)
    sections=['# Phần 2 — Kiểm định thống kê điểm thi THPT 2023 và 2025\n',
        '**2023 — CT2006** so với **2025 — CT2018**. Giữ điểm 0, không điền thiếu. Báo cáo bao phủ mọi môn có điểm, tách N1–N7; không ghép GDCD với GDKT&PL thành một môn bất biến.\n',
        '## Kết quả chính — đọc phần này trước\n',
        f'Trong {len(t)} nhóm môn thuộc hợp hai năm, {len(valid)} nhóm có dữ liệu cả hai năm và {len(t)-len(valid)} nhóm chỉ có một năm. Các khác biệt |d| lớn nhất trong tập so được là: '+ '; '.join(f'{r.label}: Δ={n(r.delta_mean,3)} điểm, d={n(r.cohen_d,3)}' for r in top.itertuples())+'. Đây là chênh điểm quan sát, không phải tác động nhân quả.\n',
        '## 2.1. Phạm vi: mỗi con số dùng mẫu nào?\n',
        md_table(cat.groupby('year').agg(so_nhom_mon=('subject_id','count'),tong_diem_quan_sat=('n_observed','sum')).reset_index(),['Năm','Nhóm môn/ngôn ngữ','Tổng lượt điểm trong các nhóm']),
        '**Diễn giải bảng:** Lượt điểm không phải số người duy nhất: một người có thể có nhiều môn. Ngoại ngữ đã tách theo mã, N1 và cột Tiếng Anh dẫn xuất chỉ tính một lần. Năm 2023 có GDCD; năm 2025 có GDKT&PL, Tin học, Công nghệ. Môn chỉ một năm vẫn hiện trong báo cáo nhưng không bị gán điểm năm còn thiếu.\n',
        '## 2.2. Trung bình và mức khác biệt của mọi môn\n']
    overview=t[['label','n_2023','n_2025','mean_2023','mean_2025','delta_mean','cohen_d']].copy()
    sections += [md_table(overview,['Môn','n 2023','n 2025','TB 2023','TB 2025','Δ điểm','d'],3),
        '**Diễn giải bảng:** Δ là 2025 trừ 2023, âm là giảm. n=0 chỉ biểu thị không có điểm trong nguồn năm đó, không phải mean=0. d đo chênh tương đối bằng SD gộp, không là phần trăm. Phải đọc cả điểm gốc và d vì cùng p nhỏ có thể đi kèm mức khác biệt rất khác.\n',
        image_block('outputs/statistics/figures/subject_overview.png','So sánh mọi môn có đủ hai năm',
            'Mỗi hàng là một môn có đủ hai năm. Trái là mean, giữa là Δ/CI theo điểm, phải là d/CI bootstrap theo SD. Thanh CI hẹp ở mẫu lớn không làm một mức đổi nhỏ trở thành ảnh hưởng lớn; các ngôn ngữ ít người có CI rộng hơn.'),
        '## 2.3. Cách tính và đọc trước khi đi vào từng môn\n',
        '**Welch t-test** hỏi trung bình hai nhóm có khác không, không giả định phương sai bằng nhau. H0: hai trung bình bằng nhau; H1 hai phía: khác nhau. **p-value** đo độ bất tương thích với mô hình H0, không là xác suất H0 đúng, không đo độ lớn thay đổi. P rất nhỏ ở mẫu lớn phải đi kèm Δ và d.\n',
        '**Cohen’s d** = (mean2025−mean2023)/SD gộp. Dấu chỉ hướng; |d| 0,2/0,5/0,8 là mốc tham khảo, không ranh giới phổ quát. **Hedges’ g** hiệu chỉnh mẫu nhỏ; ở mẫu lớn g gần d. CI d bootstrap 999 lần theo tần số điểm, CI percentile; CI mean từ Welch. CI không là khoảng chứa 95% học sinh.\n',
        '**Mann–Whitney U** đối chiếu thứ hạng/phân phối, không mặc định kiểm định mean hay median. **A**=P(X2025>X2023)+0,5P(bằng điểm); **rank-biserial**=2A−1. Điểm trùng đã được hiệu chỉnh khi tính p MWU.\n',
        '**KS D** là khoảng cách lớn nhất giữa hai ECDF. P tiêu chuẩn giả thiết liên tục chỉ để tham khảo; p chính dùng hoán vị nhãn theo tần số điểm giữ đúng n hai năm (1.999 lần, seed cố định). **Brown–Forsythe** là Levene quanh median; đọc cùng SD/IQR/tỷ số phương sai, không đồng nhất với chất lượng phân hóa của đề. Levene quanh mean được giữ ở CSV như đối chiếu bổ sung.\n',
        '**Đa kiểm định:** Holm cho family Welch; BH chung cho MWU/KS/Brown–Forsythe. Môn một năm không thêm phép thử. Dữ liệu gần toàn bộ thí sinh quan sát mỗi năm nên Δ mô tả trực tiếp tập đó; p/CI chỉ có nghĩa dưới mô hình suy luận/độc lập rộng hơn. Có thể có người thi lại, số báo danh không nhận diện người liên năm.\n',
        '## 2.4. Bảng, hình và diễn giải từng môn\n']
    for i,r in enumerate(t.itertuples(index=False),1):
        row=pd.Series(r._asdict())
        sections.append(_entity_section(row,d,f'outputs/statistics/figures/dist_{row.subject_id.replace(":","_")}.png',f'2.4.{i}'))
    if include_combinations:
        from src.report_combinations import part2_sections
        sections.append(part2_sections(root))
    else:sections.append('## 2.5. Phạm vi của giai đoạn hiện tại\n\nPhần từng môn đã được tính; kiểm định tổng điểm các tổ hợp được triển khai sau khi phần từng môn và tương quan nghiệm thu, theo thứ tự đã chốt. Không dùng bảng trống như kết quả tổ hợp đã có.\n')
    sections += ['## Nguồn, khả năng tái lập và giới hạn\n',
        '[Bảng phép thử đầy đủ](../outputs/statistics/subject_tests.csv) · [Thống kê mọi môn](../outputs/statistics/subject_descriptives.csv) · [Hồ sơ chạy và hash nguồn](../outputs/statistics/run_metadata.json).\n',
        'Mọi so sánh dùng nguồn điểm của riêng môn, không ép các môn về một tập thí sinh chung. Không suy rằng tăng/giảm do riêng chương trình hoặc đề thi. Muốn đánh giá độ phân biệt câu hỏi cần dữ liệu theo câu, không thay bằng p hoặc SD tổng điểm.\n',
        'Tài liệu phương pháp: [Welch/CI](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html), [MWU và ties](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html), [KS](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html), [Levene](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html), [nguyên tắc p-value của ASA](https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf).']
    return '\n\n'.join(sections)+'\n'

def build_notebook(root:Path,*,include_combinations=False):
    tables=['outputs/statistics/subject_tests.csv','outputs/statistics/subject_descriptives.csv']
    if include_combinations:tables+=['outputs/combination_inference/total_tests.csv','outputs/combination_inference/total_descriptives.csv']
    build_reading_notebook(root,'notebooks/statistics/analysis.ipynb','Phần 2 — Kiểm định thống kê',REPORT,
        'outputs/statistics/run_metadata.json',tables,'src.run_all_inference' if include_combinations else 'src.run_part2')
