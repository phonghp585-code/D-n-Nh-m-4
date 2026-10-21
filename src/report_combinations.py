"""Append every canonical block to the two existing integrated reports."""
import json
import numpy as np,pandas as pd
from src.analysis_catalog import label
from src.inference_io import number as n,md_table,image_block
from src.inference_plots import safe_name

def _read(root):
    folder=root/'outputs/combination_inference'
    return folder,pd.read_csv(folder/'combination_catalog.csv')

def lookup(cat):
    from src.score_data import combination_subjects
    rows=[]
    for code,g in cat.groupby('code',sort=True):
        a=g.loc[g.year.eq(2023)].iloc[0];b=g.loc[g.year.eq(2025)].iloc[0]
        names=lambda year:' + '.join(label('foreign_language:N1' if s=='english' else s) for s in combination_subjects(code,year))
        rows.append([code,names(2023),names(2025),a.n_complete,b.n_complete,'Dùng chung B08' if code=='D08' else 'Đổi môn: chỉ mô tả' if a.comparison_class=='changed_subject_content' else 'So được điểm quan sát'])
    return md_table(pd.DataFrame(rows,columns=['Khối','Môn 2023','Môn 2025','n2023','n2025','Phạm vi']))+'\n\n**Diễn giải bảng:** Đủ 24 mã có điểm trong nguồn; B08/D08 cùng Toán–Sinh–Anh nên chỉ tính một bộ. Bảy khối A08/A09/C14/C19/C20/D66/D84 đổi GDCD sang GDKT&PL: PCA riêng từng năm và mô tả điểm, không đưa vào family kiểm định chính liên năm. N1 là Tiếng Anh; đây là các mã nguồn có sẵn, không là mọi tổ hợp ba môn có thể tưởng tượng. Tin học/Công nghệ và N2–N7 đã phân tích ở từng môn nhưng chưa có mã khối tương ứng trong nguồn. Tổng n của các khối không phải số người vì một người có thể thuộc nhiều khối.\n'

def part2_sections(root):
    from src.report_part2 import _entity_section
    folder,cat=_read(root);t=pd.read_csv(folder/'total_tests.csv');d=pd.read_csv(folder/'total_descriptives.csv')
    sections=['## 2.5. Tổng điểm mọi khối có điểm — sau phần từng môn\n',lookup(cat),
        '**Quy tắc tính:** Chỉ cộng khi có đủ ba môn cùng người/cùng năm, giữ điểm0, tổng trong0–30. Không cộng hai điểm rồi bỏ qua môn thiếu. Chỉ chuẩn hóa sai số cộng dấu phẩy động ở mức 10⁻¹⁰ điểm, không làm tròn về bước điểm bài thi. Bandwidth KDE tổng là0,35 điểm, phản xạ ở0/30. Phép thử dùng tổng gốc sau chuẩn hóa sai số này.\n',
        md_table(t[['label','n_2023','n_2025','mean_2023','mean_2025','delta_mean','cohen_d']],['Khối','n2023','n2025','TB2023','TB2025','Δ tổng','d'],3),
        '**Diễn giải bảng:** Δ cùng chiều2025−2023, đơn vị điểm trên thang30. Family Welch chỉ gồm16 bộ không đổi môn (Holm); MWU/KS/BF gồm48 p hữu hạn (BH chung). Khối đổi môn vẫn có Δ mô tả, d/p chính bỏ trống để tránh trình bày như cùng nội dung. Tổng lớn hơn không đồng nghĩa năng lực cao hơn.\n',
        image_block('outputs/combination_inference/figures/total_overview.png','Tổng điểm và effect size các khối so được','Đọc mean/Δ trên thang30 và d theo SD gộp. Chỉ16 bộ cùng tên môn có kiểm định chính; B08/D08 hiện một lần.')]
    for i,row in enumerate(t.itertuples(index=False),1):
        series=pd.Series(row._asdict());path=f'outputs/combination_inference/figures/dist_{safe_name(row.canonical_id)}.png'
        text=_entity_section(series,d,path,f'2.5.{i}',30)
        if row.status=='changed_subject_content':text=text.replace('Có thống kê và hình cho năm hiện có','Có thống kê và hình riêng cho cả hai năm hiện có').replace('Chỉ vẽ các năm có điểm thực.','Hai đường mô tả hai bộ môn khác nội dung, không là cùng thang đã quy đổi.')
        sections.append(text)
    return '\n\n'.join(sections)

def part4_sections(root):
    folder,cat=_read(root);summary=pd.read_csv(folder/'pca_summary.csv');loads=pd.read_csv(folder/'pca_loadings.csv');stability=pd.read_csv(folder/'pca_stability.csv');sensitivity=pd.read_csv(folder/'group_sensitivity.csv');globalpairs=pd.read_csv(root/'outputs/subject_relations/pairwise_correlations.csv')
    sections=['## 4.6. PCA mọi khối có điểm — sau tương quan từng môn\n',lookup(cat),
        '**Vì sao không PCA một ma trận mọi môn?** Không có người đủ cả8 môn chung ở hai năm. Điền thiếu sẽ tạo tương quan phụ thuộc mô hình điền; vì vậy tương quan mọi môn dùng pairwise ở trên, còn PCA dùng người đủ ba môn trong từng khối. Bao phủ23 bộ ×2 năm =46 mô hình (24 nhãn ×2 =48 dòng tra cứu).\n',
        '**PCA là gì?** PCA tìm các trục tổ hợp tuyến tính không tương quan của điểm chuẩn hóa. Trong từng năm/khối, z=(điểm−mean)/SD mẫu (ddof=1); không ghép hai năm để chuẩn hóa. SVD của z cho eigenvalue λ=s²/(n−1), EVR=λ/Σλ. Ba EVR cộng100%; PC1 giữ nhiều biến thiên nhất, không là tổng điểm thi, không phải điểm IQ hay bằng chứng về một năng lực bẩm sinh.\n',
        '**Loading khác hệ số tính PC:** PC=z×v (v là eigenvector đơn vị); loading=v√λ là tương quan môn với PC trên chính tập chuẩn hóa. Ví dụ loading0,8 là tương quan0,8, không là “môn đóng góp80%”. Bình phương loading là phần phương sai của môn gắn với PC đó trong mô hình PCA. Dấu toàn bộ một PC có thể đảo mà kết quả không đổi; PC1 căn dương theo Toán hoặc Văn, PC2/3 căn theo2023 khi hai năm cùng bộ môn.\n',
        '**Đọc các trục:** PC1 có loading dương tương tự cả ba môn thường là trục thành tích cùng tăng trong khối; loading trái dấu ở PC2/3 mô tả tương phản tương đối giữa các môn sau chuẩn hóa. Chỉ gọi là trục quan sát; muốn gắn nhãn “năng lực ngôn ngữ/tư duy” cần lý thuyết và kiểm chứng đo lường độc lập. Ba môn và mẫu tự chọn không đủ xác nhận cấu trúc năng lực chung.\n',
        md_table(summary[['year','code','n_complete','pc1_explained_pct','pc2_explained_pct','pc3_explained_pct']],['Năm','Khối chuẩn','n đủ3','PC1 (%)','PC2 (%)','PC3 (%)'],3),
        '**Diễn giải bảng:** Có46 mô hình thực, mỗi dòng đúng tập người đủ ba điểm. Alias D08 tra B08. EVR cao nghĩa điểm tập trung quanh ít trục hơn trong chính mẫu khối/năm, không tự chứng minh năng lực đồng đều hơn hay đề tốt hơn. Các bộ đổi môn không so loading trực tiếp.\n']
    for i,(key,g) in enumerate(summary.groupby('canonical_id',sort=True),1):
        aliases='/'.join(cat.loc[cat.canonical_id.eq(key),'code'].unique());s=stability.loc[stability.canonical_id.eq(key)].iloc[0];l=loads.loc[loads.canonical_id.eq(key)].copy()
        sections += [f'### 4.6.{i}. {aliases}\n',md_table(g[['year','n_complete','coverage','pc1_explained_pct','pc2_explained_pct','pc3_explained_pct']],['Năm','n đủ3','Tỷ lệ đủ3 trên mọi dòng','PC1 (%)','PC2 (%)','PC3 (%)'],3),
            '**Diễn giải bảng:** Tỷ lệ là n đủ ba điểm chia số dòng nguồn cùng năm, không là tỷ lệ đăng ký/nguyện vọng. Mỗi năm chuẩn hóa riêng; dùng EVR để mô tả hình dạng biến thiên của chính nhóm đó.\n',
            md_table(l.assign(subject_id=l.subject_id.map(label))[['year','subject_id','loading_pc1','loading_pc2','loading_pc3']],['Năm','Môn','Loading PC1','Loading PC2','Loading PC3'],3),
            '**Diễn giải bảng:** Giá trị tuyệt đối gần1 là môn gắn chặt với PC; dấu cùng chiều cho biết xu hướng cùng tăng theo trục. So độ lớn và mô hình dấu chung; không diễn giải một đảo dấu toàn PC thành đổi bản chất môn.\n',
            image_block(f'outputs/combination_inference/figures/pca_{safe_name(key)}.png',f'PCA {aliases}','Trái là scree/EVR của ba PC và n thực; giữa/phải là loading cùng thang−1..1. Tổng EVR bằng100%. Hai màu đường là hai năm, không là cùng người.')]
        a=g.loc[g.year.eq(2023)].iloc[0];b=g.loc[g.year.eq(2025)].iloc[0]
        pc1=l.loc[l.year.eq(2025)].sort_values('loading_pc1',key=abs,ascending=False).iloc[0]
        sections.append(f'**Nhận xét bằng số:** PC1 giải thích {n(a.pc1_explained_pct)}% năm2023 và {n(b.pc1_explained_pct)}% năm2025; PC1+PC2 năm2025 là {n(b.pc1_explained_pct+b.pc2_explained_pct)}%. Môn gắn mạnh nhất với PC1 năm2025 theo |loading| là {label(pc1.subject_id)} ({n(pc1.loading_pc1,3)}). Trục này mô tả thành tích đồng biến/tương phản trong đúng ba môn đã chọn, không quy đổi được thành chênh năng lực tuyệt đối.\n')
        current=l.loc[l.year.eq(2025)];positive=current.loc[current.loading_pc2.idxmax()];negative=current.loc[current.loading_pc2.idxmin()]
        sections.append(f'**Giải nghĩa trục bằng chính loading:** Năm2025, '+('cả ba loading PC1 cùng dương, nên PC1 là trục thành tích cùng tăng trong khối này. ' if current.loading_pc1.gt(0).all() else 'PC1 có dấu khác nhau giữa các môn; cần đọc là tương phản điểm tương đối. ')+f'PC2 đặt {label(positive.subject_id)} (loading {n(positive.loading_pc2,3)}) ở một phía và {label(negative.subject_id)} ({n(negative.loading_pc2,3)}) ở phía kia. Đây là tương phản sau chuẩn hóa: điểm nghiêng về môn phía dương so với phía âm làm PC2 tăng; không phải một môn gây giảm môn kia hoặc một “năng lực thứ hai” đã được xác nhận.\n')
        if s.status=='compared':sections.append(f'**Ổn định cấu trúc:** |cosine| PC1={n(s.pc1_abs_cosine,3)} (gần1 là cùng hướng sau căn dấu); góc lớn nhất giữa hai không gian PC1–PC2={n(s.pc12_max_angle_deg)}°. '+('Có eigenvalues cách nhau dưới5%: ưu tiên diễn giải không gian con liên quan, tránh gắn nhãn riêng trục gần suy biến.' if s.near_eigenvalues else 'Không phát hiện cặp eigenvalues liền kề cách nhau dưới5% theo quy tắc kiểm tra này; vẫn chưa là kiểm định bất biến đo lường.')+'\n')
        else:sections.append('**Giới hạn so sánh:** GDCD và GDKT&PL khác nội dung; hai PCA riêng mô tả hai bộ môn, không so loading/cosine như cùng một cấu trúc.\n')
        t=sensitivity.loc[sensitivity.canonical_id.eq(key)].copy();records=[]
        for r in t.itertuples():
            match=globalpairs.loc[globalpairs.year.eq(r.year)&globalpairs.subject_x.eq(r.subject_x)&globalpairs.subject_y.eq(r.subject_y)]
            globalr=match.pearson_r.iloc[0] if len(match) else np.nan
            records.append([r.year,label(r.subject_x)+' – '+label(r.subject_y),r.n_complete,r.pearson_r,globalr,r.pearson_r-globalr])
        sections += [md_table(pd.DataFrame(records,columns=['Năm','Cặp','n đủ khối','r trong khối','r tập đủ cặp','Chênh r']),digits=3),
            '**Diễn giải bảng:** Đây là kiểm tra nhạy với cách chọn mẫu: r trong khối dùng cùng nhóm đủ cả3 môn; r toàn cặp chỉ cần đủ2. Chênh r cho thấy điều kiện có thêm môn thứ ba có thể thay đổi liên hệ. Hai ước lượng dùng mẫu lồng nhau, không coi là hai mẫu độc lập; bảng không chứng minh đã kiểm soát mọi khác biệt thành phần thí sinh.\n']
    sections.append('**Đối chiếu Duy và phạm vi bổ sung:** Năm khối A00/A01/B00/C00/D01 được đối chiếu n và EVR với bản Duy; phần này mở rộng lên đủ24 mã/23 bộ mỗi năm, bổ sung loading, ý nghĩa trục và kiểm tra chọn mẫu. Không tạo mô hình trùng B08/D08. [PCA/SVD](https://scikit-learn.org/stable/modules/decomposition.html#pca), [góc không gian con](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.subspace_angles.html).\n')
    return '\n\n'.join(sections)
