"""Observed distribution evidence supporting the subject-choice discussion."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.score_data import SUBJECT_LABELS, load_scores

SUBJECTS = ('math', 'literature', 'physics', 'chemistry', 'biology',
            'history', 'geography', 'english', 'foreign_language')
BINS = np.linspace(0, 10, 21)
EXTRA_SUBJECTS = {2023: ('civics',), 2025: ('economics_law', 'informatics', 'technology')}


def summarize(series):
    x=series.dropna()
    if not len(x):
        raise ValueError('Distribution evidence requires observed scores')
    if not x.between(0, 10).all():
        raise ValueError('Scores must be within [0,10]')
    return {'n':len(x), 'mean':x.mean(), 'median':x.median(),
            'pct_lt5':100*x.lt(5).mean(), 'pct_ge8':100*x.ge(8).mean(),
            'pct_ge9':100*x.ge(9).mean(), 'n_ge9':int(x.ge(9).sum()),
            'n_eq10':int(x.eq(10).sum()), 'pct_eq10':100*x.eq(10).mean()}


def band_summary(series):
    """Disjoint score bands; contributions add exactly to the overall mean."""
    x=series.dropna()
    summarize(x)  # Enforce the same observed-score domain, including zero.
    rows=[]
    for label, lower, upper in [('0–<5',0,5), ('5–<8',5,8), ('8–<9',8,9), ('9–10',9,10)]:
        values=x[x.ge(lower) & (x.le(upper) if upper==10 else x.lt(upper))]
        rows.append({'band':label, 'n':len(values), 'share':len(values)/len(x),
                     'band_mean':values.mean(), 'mean_contribution':values.sum()/len(x)})
    return rows


def generate(cohorts, root, inputs):
    out=Path(root)/'outputs/audits'
    out.mkdir(parents=True, exist_ok=True)
    rows=[]; bins=[]; bands=[]
    def collect(year, subject, x):
        stats=summarize(x)
        rows.append({'year':year, 'subject':subject, **stats})
        bands.extend({'year':year, 'subject':subject, **r} for r in band_summary(x))
        return stats
    fig, axes=plt.subplots(3, 3, figsize=(16, 12), sharex=True, sharey=True,
                           constrained_layout=True)
    for ax, subject in zip(axes.flat, SUBJECTS):
        for year, color in [(2023, '#176D8A'), (2025, '#C45D31')]:
            x=cohorts[year][subject].dropna()
            stats=collect(year, subject, x)
            counts, _=np.histogram(x, bins=BINS)
            assert counts.sum()==len(x)
            pct=100*counts/len(x)
            for j, count in enumerate(counts):
                bins.append({'year':year, 'subject':subject, 'lower':BINS[j],
                             'upper':BINS[j+1], 'upper_inclusive':j==19,
                             'n':int(count), 'percent':pct[j]})
            ax.stairs(pct, BINS, color=color, linewidth=1.8,
                      label=f'{year} | TB {stats["mean"]:.2f} | n={len(x):,}')
        ax.set_title(SUBJECT_LABELS[subject])
        ax.set_xticks(np.arange(0, 11, 2))
        ax.set_xlabel('Điểm môn')
        ax.set_ylabel('% người có điểm môn này')
        ax.grid(axis='y', alpha=.2)
        ax.legend(fontsize=8, loc='upper left')
    fig.suptitle('Phổ điểm 2023 và 2025 CT2018 — chuẩn hóa riêng từng môn/năm\n'
                 'Khoảng 0,5 điểm: [a,b), khoảng cuối gồm điểm 10; Anh nằm trong Ngoại ngữ', fontsize=14)
    fig.savefig(out/'subject_distributions.png', dpi=150)
    plt.close(fig)
    for year, subjects in EXTRA_SUBJECTS.items():
        for subject in subjects:
            collect(year, subject, cohorts[year][subject].dropna())
    pd.DataFrame(rows).to_csv(out/'subject_distribution_evidence.csv', index=False)
    pd.DataFrame(bins).to_csv(out/'subject_distribution_bins.csv', index=False)
    pd.DataFrame(bands).to_csv(out/'subject_score_band_contributions.csv', index=False)
    (out/'subject_distribution_metadata.json').write_text(json.dumps({
        'inputs':inputs, 'subjects':SUBJECTS, 'extra_subjects_by_year':EXTRA_SUBJECTS,
        'score_policy':'Observed valid scores; no imputation',
        'denominator':'All valid scores of the particular subject and year',
        'bin_policy':'0.5-point intervals, left closed/right open except last includes 10',
        'claim_scope':'Descriptive evidence; not a causal estimate of curriculum or self-selection'
    }, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    from src.subject_group_profiles import generate as generate_profiles
    generate_profiles(cohorts, root, inputs)


def report_section(root, table):
    out=Path(root)/'outputs/audits'
    if not (out/'subject_distribution_evidence.csv').exists():
        return []
    metadata=json.loads((out/'subject_distribution_metadata.json').read_text(encoding='utf-8'))
    run=json.loads((Path(root)/'outputs/part3_run.json').read_text(encoding='utf-8'))
    if {x['sha256'] for x in metadata['inputs']}!={x['sha256'] for x in run['inputs']}:
        raise ValueError('Subject distribution evidence is stale for current inputs')
    data=pd.read_csv(out/'subject_distribution_evidence.csv').set_index(['year','subject'])
    def pair(s, field):
        return f'{data.loc[(2023,s),field]:.2f} → {data.loc[(2025,s),field]:.2f}'.replace('.', ',')
    rows=[{'Môn':SUBJECT_LABELS[s], 'TB 2023 → 2025':pair(s,'mean'),
           'Trung vị':pair(s,'median'), 'Dưới 5 (%)':pair(s,'pct_lt5'),
           'Từ 8 (%)':pair(s,'pct_ge8'), 'Từ 9 (%)':pair(s,'pct_ge9')} for s in SUBJECTS]
    lines=['## Bằng chứng từ phổ điểm: tăng/giảm ở phần nào?',
           'Đây là phần bổ trợ để giải thích cơ cấu môn thi và điểm tổ hợp. '
           '**Mẫu số tại đây là người có điểm của riêng môn đó trong từng năm**, '
           'khác với tỷ lệ có điểm trên toàn bộ thí sinh ở mục 3.1. '
           'Chuẩn hóa về % giúp so hình dạng phổ khi số người thi khác nhau. '
           'Các thống kê dùng điểm gốc; chỉ hình vẽ gộp khoảng 0,5 điểm.',
           table(pd.DataFrame(rows)),
           '**Diễn giải bảng:** Mọi mũi tên đi từ 2023 sang 2025. Trung vị mô tả phần giữa; '
           'dưới 5, từ 8 và từ 9 mô tả các vùng điểm. Nhóm từ 9 nằm trong nhóm từ 8 nên không cộng '
           'hai tỷ lệ này. Trung bình có thể giảm dù tỷ lệ dưới 5 giảm, nếu phần điểm cao cũng thu hẹp '
           '(như Tiếng Anh). Trung bình tăng cũng không có nghĩa mọi phần của phổ tăng (như Địa lý).',
           '![Phổ điểm chuẩn hóa của chín mục môn/ngoại ngữ](../outputs/audits/subject_distributions.png)',
           '**Diễn giải hình:** Đường xanh là 2023, cam là 2025; chiều cao mỗi khoảng là % người '
           'trong đúng môn/năm đó. Các ô dùng cùng thang trục; mỗi đường cộng đủ 100%. So phần bên trái '
           'mốc 5 và bên phải mốc 8 để kiểm tra các kết luận bên dưới. Điểm thi rời rạc và bước điểm '
           'khác nhau có thể tạo răng cưa; không suy ra nguyên nhân chỉ từ một đỉnh. '
           'Ngoại ngữ gồm Tiếng Anh và các ngôn ngữ khác, không phải một nhóm độc lập với Anh.']
    interpretations={
        'math':'Phần giữa thấp hơn rõ và nhóm dưới 5 lớn hơn, phù hợp trung bình giảm. Tuy nhiên tỷ lệ từ 9 tăng: không thể nói mọi nhóm điểm đều giảm.',
        'literature':'Phần giữa cao hơn, dưới 5 giảm và từ 8 tăng, phù hợp trung bình tăng; tỷ lệ từ 9 lại giảm nên đuôi cao nhất không cùng chiều với trung bình.',
        'physics':'Dưới 5 thu hẹp, trung vị tăng và nhóm từ 8, từ 9 mở rộng: nhiều vùng của phổ cùng phù hợp với trung bình tăng.',
        'chemistry':'Dưới 5 mở rộng mạnh, trung vị giảm và từ 8 thu hẹp, phù hợp trung bình giảm. Từ 9 vẫn tăng nên nhóm rất cao biến động khác phần giữa.',
        'biology':'Dưới 5 tăng mạnh và trung vị giảm, phù hợp trung bình giảm; từ 8 gần như giữ mức cũ và từ 9 tăng. Không thể quy toàn bộ nhóm thi thành yếu hơn.',
        'history':'Dưới 5 giảm, trung vị tăng và các nhóm từ 8, từ 9 tăng: phổ có nhiều bằng chứng phù hợp với trung bình cao hơn.',
        'geography':'Dưới 5 và các nhóm từ 8, từ 9 đều tăng; trung vị và trung bình vẫn tăng. Hai vùng thấp/cao đều mở rộng, không phải toàn bộ phổ dịch đều sang phải.',
        'english':'Dưới 5 giảm và trung vị nhích lên, nhưng từ 8 và từ 9 thu hẹp rất mạnh. Trung bình giảm nhẹ phản ánh thay đổi cả hình dạng, không thể tóm thành cả phổ giảm hoặc đề khó hơn cho mọi người.',
        'foreign_language':'Mẫu gộp cho xu hướng gần Tiếng Anh vì Anh chiếm đa số. Cơ cấu ngôn ngữ cũng thay đổi nên đánh giá môn Anh phải dùng riêng N1, không dùng trung bình gộp.'}
    for s in SUBJECTS:
        lines.append(f'**{SUBJECT_LABELS[s]}:** TB {pair(s,"mean")}; trung vị {pair(s,"median")}; '
                     f'dưới 5: {pair(s,"pct_lt5")}% người; từ 8: {pair(s,"pct_ge8")}%; '
                     f'từ 9: {pair(s,"pct_ge9")}%. '+interpretations[s])
    lines += ['**Bằng chứng về cơ chế và giới hạn kết luận:** Quy chế chuyển từ bài tổ hợp sang hai môn '
              'tự chọn làm thay đổi cách hình thành nhóm dự thi. Định dạng đề 2025 cũng thay đổi, '
              'trong đó nhiều môn có thêm dạng đúng/sai hoặc trả lời ngắn; Ngoại ngữ vẫn dùng dạng nhiều lựa chọn. '
              '[Cấu trúc do Bộ GDĐT công bố](https://vqa.moet.gov.vn/vi/news/thong-bao/cau-truc-dinh-dang-de-thi-tot-nghiep-thpt-tu-nam-2025-74.html). '
              'Đây là bằng chứng các điều kiện đánh giá thay đổi, chưa chứng minh mỗi điều kiện gây ra bao nhiêu điểm. '
              'Phổ điểm cho biết kết quả tăng/giảm ở đâu; không đo trực tiếp sở thích, năng lực trước kỳ thi '
              'hay độ khó câu hỏi trên cùng một nhóm thí sinh.',
              '**Giả thuyết có thể thảo luận:** Với Lý và Sử, tăng nhóm điểm cao phù hợp với khả năng '
              'nhóm tự chọn có sở trường hoặc định hướng xét tuyển rõ hơn. Địa có biến động hai vùng '
              'nên cần diễn giải thận trọng hơn. Hóa/Sinh có trung bình giảm dù được tự chọn, và '
              'Toán bắt buộc cũng giảm trung bình; các kết quả này bác bỏ cách giải thích đơn giản '
              '“được tự chọn thì điểm chắc chắn tăng”. Đề thi, cách chấm, quá trình học và thành phần '
              'thí sinh là các yếu tố cần nghiên cứu thêm. Chưa ước lượng được tác động riêng của '
              'chương trình 2018 từ hai kỳ thi.',
              '[Bảng số liệu tái lập](../outputs/audits/subject_distribution_evidence.csv) · '
              '[Tần suất các khoảng điểm](../outputs/audits/subject_distribution_bins.csv).']
    return lines


def research_section(root, table):
    """Research ideas requested by the user; distinguish computed evidence from hypotheses."""
    out=Path(root)/'outputs/audits'
    if not (out/'subject_score_band_contributions.csv').exists():
        return []
    stats=pd.read_csv(out/'subject_distribution_evidence.csv').set_index(['year','subject'])
    bands=pd.read_csv(out/'subject_score_band_contributions.csv')
    def pair(subject, field, digits=2):
        values=[]
        for year in (2023,2025):
            if (year,subject) not in stats.index:
                values.append('—')
            else:
                value=stats.loc[(year,subject),field]
                values.append(f'{value:,.0f}'.replace(',','.') if digits==0
                              else f'{value:.{digits}f}'.replace('.',','))
        return ' → '.join(values)
    subjects=SUBJECTS+EXTRA_SUBJECTS[2023]+EXTRA_SUBJECTS[2025]
    high=[{'Môn':SUBJECT_LABELS[s], 'Số người ≥9 (2023 → 2025)':pair(s,'n_ge9',0),
           'Tỷ lệ ≥9 (%)':pair(s,'pct_ge9'), 'Số điểm 10':pair(s,'n_eq10',0),
           'Tỷ lệ điểm 10 (%)':pair(s,'pct_eq10',4)} for s in subjects]
    lines=['## Ý tưởng nghiên cứu: nhóm nào đóng góp biến động điểm cao?',
           '**Trạng thái:** Các bảng điểm cao và phân rã theo vùng điểm dưới đây đã được tính từ dữ liệu. '
           'Các giải thích về giảng dạy, định dạng đề và tự lựa chọn là giả thuyết nghiên cứu; '
           'chưa được kiểm định nhân quả. Phân nhóm theo địa phương, trường hoặc năng lực đầu vào '
           'là hướng tiếp theo, chưa có kết quả trong báo cáo này.',
           '### Điểm từ 9 và điểm 10: tăng số lượng hay chỉ tăng tỷ lệ?',
           table(pd.DataFrame(high)),
           '**Diễn giải bảng:** Mẫu số là người có điểm của riêng môn/năm. Số người từ 9 và số điểm 10 '
           'trả lời về quy mô; tỷ lệ trả lời về cơ cấu. Sinh từ 9 giảm 5.451 → 1.775 người dù tỷ lệ '
           'tăng 1,68% → 2,54%; số điểm 10 cũng giảm 135 → 82. Ngược lại, Lý và Hóa tăng cả '
           'số người từ 9 lẫn tỷ lệ. Vì vậy không gộp mọi môn vào nhận xét “điểm 9/10 đều tăng”. '
              'Văn từ 9 tăng nhẹ số người nhưng giảm tỷ lệ. Tỷ lệ điểm 10 hiển thị bốn chữ số '
              'thập phân để tránh làm tròn tỷ lệ rất nhỏ thành 0. '
           'Điểm 10 thuộc nhóm từ 9, Anh thuộc Ngoại ngữ nên không cộng trùng. Dấu — là không có '
           'mốc tương ứng; GDCD và GDKT&PL vẫn để riêng.',
           '### Phân rã mô tả: vùng điểm nào đóng góp vào chênh lệch trung bình?',
           'Chia mỗi môn thành bốn vùng không chồng lấn: 0–<5, 5–<8, 8–<9 và 9–10. '
           'Đóng góp của một vùng = tổng điểm của người trong vùng / tổng số người có điểm môn đó. '
           'Tổng bốn đóng góp bằng trung bình môn. Lấy đóng góp 2025 trừ 2023 để xác định phần '
           'thay đổi gắn với từng vùng; đơn vị là điểm trên thang 10.']
    contributions=[]
    for subject in SUBJECTS:
        before=bands[(bands.year==2023)&(bands.subject==subject)].set_index('band')
        after=bands[(bands.year==2025)&(bands.subject==subject)].set_index('band')
        row={'Môn':SUBJECT_LABELS[subject]}
        for band in ('0–<5','5–<8','8–<9','9–10'):
            row[band]=after.loc[band,'mean_contribution']-before.loc[band,'mean_contribution']
        row['Tổng thay đổi TB']=stats.loc[(2025,subject),'mean']-stats.loc[(2023,subject),'mean']
        assert np.isclose(sum(row[k] for k in ('0–<5','5–<8','8–<9','9–10')),row['Tổng thay đổi TB'])
        contributions.append(row)
    lines += [table(pd.DataFrame(contributions)),
              '**Diễn giải bảng:** Bốn cột vùng cộng lại thành cột cuối; số làm tròn có thể lệch 0,01. '
              'Ví dụ một cột 9–10 dương cho biết phần điểm do vùng này đóng góp vào trung bình lớn hơn, '
              'trong khi tổng trung bình vẫn có thể giảm nếu các cột khác giảm nhiều hơn. '
              '**Cột 0–<5 dương không có nghĩa kết quả tốt hơn**: có thể vì tỷ trọng vùng thấp lớn hơn. '
              'Đây là phép phân rã phân phối, không theo dõi cùng người qua hai năm và không xác định '
              'nguyên nhân. “Nhóm 9–10” là nhóm theo kết quả, chưa cho biết họ học trường nào hay có năng lực ban đầu ra sao.',
              '**Đọc trường hợp Hóa/Sinh:** Ở Hóa, vùng 9–10 đóng góp thêm khoảng 0,38 điểm '
              'vào trung bình, nhưng vùng 5–<8 giảm đóng góp khoảng 1,15 và vùng 8–<9 giảm khoảng '
              '0,60; tổng thay đổi vẫn âm sau cộng đủ bốn vùng. Ở Sinh, vùng 9–10 tăng đóng góp '
              'khoảng 0,08, trong khi vùng 5–<8 giảm khoảng 1,52. Hai ví dụ cho thấy tỷ lệ điểm '
              'rất cao tăng có thể cùng tồn tại với trung bình giảm, không tạo mâu thuẫn thống kê.',
              '[Dữ liệu vùng điểm và đóng góp trung bình](../outputs/audits/subject_score_band_contributions.csv).',
              '### Làm thế nào xác định nhóm thí sinh đứng sau biến động?',
              'Câu hỏi đề xuất: “Trong từng môn, thay đổi tỷ lệ từ 9/điểm 10 tập trung ở nhóm nào, '
              'và đi kèm thay đổi quy mô nhóm hay thay đổi tỷ lệ điểm cao ngay trong nhóm?” '
              'Có thể chia theo hội đồng thi/tỉnh nếu xác minh đúng bảng mã SBD từng năm; theo trường, '
              'hệ THPT/GDTX hoặc thí sinh tự do nếu bổ sung được biến tương ứng. Không suy trường, '
              'phòng thi hoặc chỗ ngồi chỉ từ các SBD gần nhau.',
              'Với điểm hiện có, có thể nghiên cứu hồ sơ điểm các môn khác: người đạt ≥9 Hóa có '
              'điểm Toán/Văn thế nào, có đồng thời đạt cao ở môn tự chọn còn lại không? '
              'Điểm thiếu do không thi không phải 0. So thứ hạng Toán/Văn trong từng năm chỉ mô tả '
              'vị trí tương đối, không tạo ra thước đo năng lực tuyệt đối tương đương giữa hai năm. '
              'Phần phân tích tiếp theo đã chia nhóm theo thứ hạng Toán/Văn; chưa có thước đo '
              'năng lực đầu vào độc lập hoặc dữ liệu trường/địa phương đã xác minh để phân nhóm.',
              'Nếu các nhóm g không chồng lấn và bao phủ toàn bộ người có điểm môn đó, '
              'tỷ lệ điểm cao toàn môn = Σ(tỷ trọng nhóm g × tỷ lệ điểm cao trong nhóm g). '
              'So hai năm để tách biến động cơ cấu nhóm khỏi biến động trong nhóm. '
              'Cần thống nhất định nghĩa nhóm và nêu nhóm thiếu thông tin. '
              '24 tổ hợp chồng lấn theo lựa chọn đa nhãn nên không cộng trực tiếp chúng để phân rã tổng thí sinh.',
              '### Các giả thuyết giải thích cần giữ riêng',
              table(pd.DataFrame([
                  {'Giả thuyết':'Kết quả học tập thay đổi', 'Cơ chế dự kiến':'Chương trình, dạy học, ôn tập và mức thích nghi ảnh hưởng kết quả', 'Bằng chứng cần thêm':'Năng lực đầu vào/đánh giá độc lập tương đương và thông tin quá trình học'},
                  {'Giả thuyết':'Định dạng và quy tắc chấm thay đổi', 'Cơ chế dự kiến':'Điểm từng phần thay đổi khác nhau theo mức nắm chắc kiến thức', 'Bằng chứng cần thêm':'Đáp án từng câu, điểm từng phần; thiết kế đối sánh phù hợp'},
                  {'Giả thuyết':'Thành phần tự chọn môn thay đổi', 'Cơ chế dự kiến':'Sở trường, ngành muốn học và lựa chọn xét tuyển làm nhóm dự thi khác trước', 'Bằng chứng cần thêm':'Đăng ký môn, định hướng xét tuyển và năng lực trước thi'},
                  {'Giả thuyết':'Nội dung/độ khó đề hoặc tiêu chí chấm khác', 'Cơ chế dự kiến':'Các vùng điểm chịu ảnh hưởng khác nhau', 'Bằng chứng cần thêm':'Đối sánh đề/câu hỏi hoặc bài viết và dữ liệu chấm; tổng điểm chưa đủ'}])),
              '**Diễn giải bảng:** Đây là những cơ chế có thể đồng thời tồn tại. Chưa có dữ liệu '
              'để xếp “đề thuận lợi hơn” cao hay thấp hơn “giảng dạy tốt hơn”. Cùng mục đích thi '
              'không bảo đảm đề tương đương độ khó; thiếu bằng chứng về một cơ chế không xác nhận cơ chế khác. '
              'Chỉ đối sánh điểm khi các điều kiện về nội dung và năng lực đo lường phù hợp. '
              '[Tài liệu ETS về đối sánh điểm](https://www.ets.org/Media/Research/pdf/LIVINGSTON2ed.pdf).',
              '**Lý, Sử và Địa:** Lý và Sử có dưới 5 giảm, từ 8 tăng; có thể đặt giả thuyết '
              'kết quả học tập tốt hơn, nhóm tự chọn có thế mạnh hơn hoặc cách đánh giá khác. '
              'Địa có cả dưới 5 và từ 8 tăng nên cần xét các vùng riêng. Quy mô Sử/Địa đều giảm '
              'trong dataset; chưa có căn cứ nói số đăng ký hai môn tăng hoặc lựa chọn 2023 là ngẫu nhiên. '
              'Lý tăng số người có điểm nhưng giảm nhẹ tỷ trọng, gợi ý duy trì quy mô dự thi sau tự chọn; '
              'chưa đo trực tiếp mức yêu thích.',
              '**Hóa và Sinh:** Giả thuyết yêu cầu đánh giá mới ảnh hưởng nhóm giữa nhiều hơn nhóm rất cao; '
              'hoặc mức chuẩn bị/thích nghi không đồng đều; hoặc nhóm chọn môn theo ngành học dù môn đó '
              'chưa phải sở trường. Các mẫu dưới 5 tăng và tỷ lệ từ 9 tăng phù hợp để nghiên cứu các '
              'giả thuyết này, chưa xác nhận giả thuyết nào. Số người thi ít đi tự nó không làm trung bình giảm.',
              '**Tiếng Anh:** Nhóm dưới 5 và từ 8 đều thu hẹp trong khi trung vị nhích lên. '
              'Có thể giả thuyết mức cơ bản tiếp cận được hơn nhưng điểm cao khó đạt; hoặc thành phần '
              'nhóm tự chọn thay đổi, gồm khả năng một phần người rất mạnh và rất yếu đều chọn hướng khác. '
              'Ngoại ngữ chỉ dùng câu nhiều lựa chọn; không lấy đúng/sai hay trả lời ngắn giải thích '
              'trực tiếp biến động Anh. Giả thuyết về lựa chọn khác cần dữ liệu đăng ký để kiểm tra.',
              '### Giả thuyết cụ thể về đúng/sai và trả lời ngắn',
              'Theo quy tắc công bố, câu đúng/sai bốn ý cho 0,10/0,25/0,50/1,00 điểm khi đúng '
              '1/2/3/4 ý. Đúng ý cuối làm điểm câu tăng 0,50, nên cách chấm có thể tạo khác biệt '
              'giữa người nắm một phần và người nắm chắc. Trả lời ngắn không có phương án đáp án '
              'để chọn. Có thể giả thuyết các dạng này thay đổi kết quả từng vùng điểm, nhưng '
              'không mặc định làm trung bình giảm hoặc tăng. Phân phối rộng hơn chưa đủ chứng minh '
              'khả năng phân biệt năng lực tốt hơn; cần dữ liệu từng câu và bằng chứng đo lường. '
              '[Cách chấm công bố](https://xaydungchinhsach.chinhphu.vn/cau-truc-de-thi-tot-nghiep-thpt-tu-nam-2025-119240308200554932.htm), '
              '[phạm vi áp dụng các dạng câu hỏi](https://vqa.moet.gov.vn/vi/news/thong-bao/cau-truc-dinh-dang-de-thi-tot-nghiep-thpt-tu-nam-2025-74.html).',
              '### Ngữ văn: giả thuyết riêng cho bài tự luận',
              'Văn vẫn thi tự luận; trọng số Đọc hiểu/Làm văn chuyển từ 3/7 năm 2023 sang '
              'Đọc hiểu/Viết 4/6 năm 2025. '
              '[Cấu trúc 2023](https://xaydungchinhsach.chinhphu.vn/tot-nghiep-thpt-2023-bi-quyet-dat-diem-cao-mon-ngu-van-khong-nen-bo-lo-119230614084944406.htm), '
              '[cấu trúc 2025](https://xaydungchinhsach.chinhphu.vn/cau-truc-de-thi-tot-nghiep-thpt-tu-nam-2025-119240308200554932.htm). '
              'TB tăng 6,86 → 7,00, trung vị 7,00 → 7,25; từ 8 tăng 24,42% → 26,69% nhưng '
              'từ 9 giảm 4,30% → 3,91%. Giả thuyết gồm kỹ năng đọc/viết thay đổi, cấu trúc và nội dung '
              'thuận lợi cho vùng điểm khá, hoặc tiêu chí chấm làm kết quả tập trung hơn ở vùng giữa. '
              'Thay đổi trọng số có thể tăng hoặc giảm điểm tùy mức đạt ở từng phần; chưa biết chiều '
              'tác động nếu thiếu điểm thành phần. Không suy ra “chấm rộng tay” hoặc chương trình tốt '
              'hơn chỉ từ phổ tổng điểm.',
              '### Có thể suy ra gian lận từ điểm cao tăng không?',
              '**Chưa thể.** Điểm 9/10 tăng, một địa phương tăng mạnh hay một hồ sơ điểm lệch giữa '
              'các môn đều chưa đủ kết luận gian lận. Cần xét quy mô mẫu, cơ cấu tự chọn, thay đổi '
              'đề/cách chấm, chất lượng và nguồn dữ liệu. So nhiều nhóm dễ xuất hiện cực trị ngẫu nhiên; '
              'nếu kiểm định hàng loạt phải xử lý việc so sánh nhiều lần và nêu độ bất định. '
              'Phát hiện thống kê chỉ xác định đối tượng cần kiểm tra dữ liệu thêm; báo cáo này '
              'chưa triển khai phát hiện bất thường và không gắn nhãn cá nhân hay địa phương.',
              'Để đánh giá nghi vấn cần bằng chứng độc lập như đáp án từng câu có mức trùng sai '
              'bất thường sau khi xét mã đề/năng lực, dữ liệu phòng thi hoặc biên bản xác minh. '
              'Ngay cả dấu hiệu từ đáp án cũng cần được thẩm tra. ETS kết hợp phân tích thống kê '
              'với các bước xem xét khác khi đánh giá tính hợp lệ của điểm. '
              '[Nghiên cứu về trùng đáp án bất thường](https://www.ets.org/research/policy_research_reports/publications/report/2017/jxrq.html), '
              '[quy trình xem xét điểm](https://www.ets.org/pdfs/about/why-how-questions.pdf).',
              '**Kết luận nghiên cứu phù hợp:** “Xác định các nhóm và vùng điểm đóng góp vào biến động '
              'điểm cao; thảo luận các cơ chế có thể giải thích và những dữ liệu cần bổ sung.” '
              'Không chuyển câu hỏi thành kết luận ai gây biến động hoặc ai gian lận khi chưa có bằng chứng.']
    return lines


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    cohorts={}; inputs=[]
    for year, rel in [(2023,'data/raw/original.csv'),(2025,'data/dataset_diem_thi_thpt_2025.csv')]:
        cohorts[year], audit=load_scores(root/rel, year)
        inputs.append(audit)
    generate(cohorts, root, inputs)
