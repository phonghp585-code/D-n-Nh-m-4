"""Descriptive reference-score profiles; never an equated ability or causal model."""
from pathlib import Path
import json

import numpy as np
import pandas as pd

from src.score_data import SUBJECT_LABELS

GROUPS=('Q1','Q2','Q3','Q4','missing')
GROUP_LABELS={'Q1':'Hạng ≤25%', 'Q2':'Hạng >25–50%', 'Q3':'Hạng >50–75%',
              'Q4':'Hạng >75%', 'missing':'Thiếu điểm tham chiếu'}
COMMON=tuple(s for s in SUBJECT_LABELS if s not in ('civics','economics_law','informatics','technology'))


def reference_groups(series):
    """Average percentile ranks over all observed reference scores of the year."""
    x=series.dropna()
    if not x.between(0,10).all():
        raise ValueError('Reference scores must be valid observed scores')
    ranks=series.rank(method='average',pct=True)
    return pd.cut(ranks,[0,.25,.5,.75,1],labels=GROUPS[:4]).astype('string').fillna('missing')


def profile_subject(frame, subject, reference, groups=None):
    if subject==reference:
        raise ValueError('The target subject cannot define its own reference profile')
    if groups is None:
        groups=reference_groups(frame[reference])
    if not groups.index.equals(frame.index) or not groups.isin(GROUPS).all():
        raise ValueError('Reference groups must cover the original cohort index')
    values=frame[subject].dropna()
    if not len(values) or not values.between(0,10).all():
        raise ValueError('Target requires valid observed scores')
    data=pd.DataFrame({'score':values,'group':groups.loc[values.index]})
    data['high']=data.score.ge(9)
    data['ten']=data.score.eq(10)
    data['low']=data.score.lt(5)
    grouped=data.groupby('group',observed=True).agg(n=('score','size'),
        sum_score=('score','sum'), mean=('score','mean'), n_ge9=('high','sum'),
        n_eq10=('ten','sum'), n_lt5=('low','sum')).reindex(GROUPS)
    for field in ('n','sum_score','n_ge9','n_eq10','n_lt5'):
        grouped[field]=grouped[field].fillna(0)
    rows=[]
    for group,r in grouped.iterrows():
        n=int(r.n)
        rows.append({'subject':subject,'reference_subject':reference,'reference_group':group,
                     'n':n,'n_subject':len(values),'share':n/len(values),
                     'sum_score':r.sum_score,'mean':r['mean'],
                     'n_ge9':int(r.n_ge9),'n_eq10':int(r.n_eq10),'n_lt5':int(r.n_lt5),
                     'pct_ge9':100*r.n_ge9/n if n else np.nan,
                     'pct_eq10':100*r.n_eq10/n if n else np.nan,
                     'pct_lt5':100*r.n_lt5/n if n else np.nan,
                     'sample_note':'n_lt100_read_counts_with_care' if n<100 else 'observed_group'})
    return pd.DataFrame(rows)


def decompose_profiles(before, after):
    """Symmetric arithmetic split; empty groups in one year are not imputed."""
    for frame in (before,after):
        if frame.reference_group.duplicated().any() or set(frame.reference_group)!=set(GROUPS):
            raise ValueError('Exactly one row for every disjoint reference group is required')
    if (before.subject.nunique()!=1 or after.subject.nunique()!=1
        or before.reference_subject.nunique()!=1 or after.reference_subject.nunique()!=1
        or before.subject.iloc[0]!=after.subject.iloc[0]
        or before.reference_subject.iloc[0]!=after.reference_subject.iloc[0]):
        raise ValueError('Only matching subject/reference definitions can be decomposed')
    a=before.set_index('reference_group'); b=after.set_index('reference_group')
    details=[]
    for group in GROUPS:
        old=a.loc[group]; new=b.loc[group]
        row={'subject':old.subject,'reference_subject':old.reference_subject,'reference_group':group,
             'n_from':int(old.n),'n_to':int(new.n),
             'delta_mean_contribution':new.sum_score/new.n_subject-old.sum_score/old.n_subject,
             'delta_ge9_contribution_pp':100*(new.n_ge9/new.n_subject-old.n_ge9/old.n_subject),
             'delta_eq10_contribution_pp':100*(new.n_eq10/new.n_subject-old.n_eq10/old.n_subject)}
        status='ok' if old.n and new.n else 'both_empty' if not old.n and not new.n else 'group_empty_in_one_year'
        row['status']=status
        for metric,field,scale in [('mean','mean',1),('ge9_pp','pct_ge9',.01),('eq10_pp','pct_eq10',.01)]:
            if status=='group_empty_in_one_year':
                composition=within=np.nan
            elif status=='both_empty':
                composition=within=0.
            else:
                p0=old[field]*scale; p1=new[field]*scale
                composition=(new.share-old.share)*(p0+p1)/2
                within=(new.share+old.share)/2*(p1-p0)
                if metric!='mean':
                    composition*=100; within*=100
            row['composition_'+metric]=composition
            row['within_'+metric]=within
        details.append(row)
    detail=pd.DataFrame(details)
    available=not detail.status.eq('group_empty_in_one_year').any()
    n0=int(before.n.sum()); n1=int(after.n.sum())
    summary={'subject':before.subject.iloc[0],'reference_subject':before.reference_subject.iloc[0],
             'n_from':n0,'n_to':n1,'delta_mean':after.sum_score.sum()/n1-before.sum_score.sum()/n0,
             'delta_pct_ge9':100*(after.n_ge9.sum()/n1-before.n_ge9.sum()/n0),
             'delta_pct_eq10':100*(after.n_eq10.sum()/n1-before.n_eq10.sum()/n0),
             'status':'ok' if available else 'group_empty_in_one_year'}
    for metric,delta in [('mean','delta_mean'),('ge9_pp','delta_pct_ge9'),('eq10_pp','delta_pct_eq10')]:
        for kind in ('composition','within'):
            summary[kind+'_'+metric]=detail[kind+'_'+metric].sum() if available else np.nan
        if available and not np.isclose(summary['composition_'+metric]+summary['within_'+metric],summary[delta]):
            raise ValueError('Descriptive decomposition failed to reconstruct total change')
    return detail,summary


def generate(cohorts, root, inputs):
    out=Path(root)/'outputs/audits'; out.mkdir(parents=True,exist_ok=True)
    profiles=[]
    for year,frame in cohorts.items():
        groups={s:reference_groups(frame[s]) for s in ('math','literature')}
        for subject in SUBJECT_LABELS:
            if not frame[subject].notna().any():
                continue
            reference='literature' if subject=='math' else 'math'
            profile=profile_subject(frame,subject,reference,groups[reference])
            profile.insert(0,'year',year)
            profiles.append(profile)
    profiles=pd.concat(profiles,ignore_index=True)
    details=[]; summaries=[]
    for subject in COMMON:
        selected=profiles[profiles.subject==subject]
        detail,summary=decompose_profiles(selected[selected.year==2023],selected[selected.year==2025])
        details.append(detail); summaries.append(summary)
    details=pd.concat(details,ignore_index=True); summary=pd.DataFrame(summaries)
    profiles.to_csv(out/'subject_group_profiles.csv',index=False)
    details.to_csv(out/'subject_group_decomposition.csv',index=False)
    summary.to_csv(out/'subject_group_changes.csv',index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    values=details.pivot(index='subject',columns='reference_group',values='delta_ge9_contribution_pp').reindex(index=COMMON,columns=GROUPS)
    limit=max(float(values.abs().max().max()),.01)
    fig,ax=plt.subplots(figsize=(12,7),constrained_layout=True)
    plot=ax.imshow(values.to_numpy(),cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='auto')
    for i in range(len(values)):
        for j in range(len(GROUPS)):
            v=values.iloc[i,j]
            ax.text(j,i,f'{v:+.3f}',ha='center',va='center',fontsize=9,
                    color='white' if abs(v)>.55*limit else '#202020')
    ax.set_xticks(range(len(GROUPS)),[GROUP_LABELS[g] for g in GROUPS],rotation=15,ha='right')
    ax.set_yticks(range(len(COMMON)),[SUBJECT_LABELS[s]+(' (theo Văn)' if s=='math' else ' (theo Toán)') for s in COMMON])
    ax.set_title('Đóng góp của nhóm hồ sơ điểm vào thay đổi tỷ lệ đạt từ 9\n2025 trừ 2023; mỗi hàng cộng thành thay đổi tỷ lệ toàn môn')
    fig.colorbar(plot,ax=ax,label='Điểm phần trăm (có thể có sai số làm tròn)')
    fig.savefig(out/'subject_group_contributions.png',dpi=150); plt.close(fig)
    (out/'subject_group_metadata.json').write_text(json.dumps({
        'inputs':inputs,'group_policy':'Average percentile ranks on all observed reference scores of each year; (0,.25],(.25,.5],(.5,.75],(.75,1]; missing separate',
        'reference_policy':'Mathematics except when mathematics is the target, then literature; target never defines its own group',
        'target_policy':'Observed valid target scores; missing is not zero; groups exhaust target population',
        'decomposition_policy':'Symmetric arithmetic split: delta(w*p)=delta(w)*average(p)+average(w)*delta(p); not causal. Both-empty groups contribute zero; one-year-empty groups not imputed.',
        'limitations':'Within-year relative positions are not equated ability levels. No anomaly/cheating detection, demographic or geographic attribution performed.',
        'profile_rows':len(profiles),'group_changes':len(details),'summary_rows':len(summary)
    },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def report_section(root, table):
    out=Path(root)/'outputs/audits'
    if not (out/'subject_group_metadata.json').exists():
        return []
    metadata=json.loads((out/'subject_group_metadata.json').read_text(encoding='utf-8'))
    run=json.loads((Path(root)/'outputs/part3_run.json').read_text(encoding='utf-8'))
    if {r['sha256'] for r in metadata['inputs']}!={r['sha256'] for r in run['inputs']}:
        raise ValueError('Reference-score profile evidence is stale')
    profiles=pd.read_csv(out/'subject_group_profiles.csv')
    changes=pd.read_csv(out/'subject_group_changes.csv')
    details=pd.read_csv(out/'subject_group_decomposition.csv')
    def pair(a,b,digits=2):
        if digits==0:
            return f'{int(a):,} → {int(b):,}'.replace(',','.')
        return f'{a:.{digits}f} → {b:.{digits}f}'.replace('.',',')
    # A common header keeps the 45-row table compact; reference subject is stated per row.
    rows=[]
    for subject in COMMON:
        for group in GROUPS:
            a=profiles[(profiles.year==2023)&(profiles.subject==subject)&(profiles.reference_group==group)].iloc[0]
            b=profiles[(profiles.year==2025)&(profiles.subject==subject)&(profiles.reference_group==group)].iloc[0]
            c=details[(details.subject==subject)&(details.reference_group==group)].iloc[0]
            rows.append({'Môn':SUBJECT_LABELS[subject],
                         'Nhóm theo môn tham chiếu':GROUP_LABELS[group]+' / '+SUBJECT_LABELS[a.reference_subject],
                         'Số có điểm môn':pair(a.n,b.n,0), 'Số đạt ≥9':pair(a.n_ge9,b.n_ge9,0),
                         'Tỷ lệ ≥9 trong nhóm (%)':pair(a.pct_ge9,b.pct_ge9),
                         'Số điểm 10':pair(a.n_eq10,b.n_eq10,0),
                         'Góp thay đổi ≥9 (điểm %)':c.delta_ge9_contribution_pp})
    high=[]; means=[]
    for r in changes.itertuples():
        high.append({'Môn':SUBJECT_LABELS[r.subject], 'Tổng thay đổi ≥9 (điểm %)':r.delta_pct_ge9,
                     'Phần cơ cấu nhóm':r.composition_ge9_pp, 'Phần thay đổi trong nhóm':r.within_ge9_pp,
                     'Thay đổi tỷ lệ điểm 10 (điểm %)':r.delta_pct_eq10})
        means.append({'Môn':SUBJECT_LABELS[r.subject], 'Tổng thay đổi TB':r.delta_mean,
                      'Phần cơ cấu nhóm':r.composition_mean, 'Phần thay đổi trong nhóm':r.within_mean})
    lines=['## Phân tích tiếp: hồ sơ điểm của nhóm đóng góp biến động',
           '**Đã tính:** Chia người có điểm của từng môn thành bốn nhóm theo thứ hạng điểm Toán '
           'trong toàn bộ người có Toán của cùng năm; thiếu Toán thành nhóm riêng. Riêng khi '
           'phân tích môn Toán dùng thứ hạng Văn, tránh dùng chính điểm cần giải thích để tạo nhóm. '
           'Đồng điểm nhận thứ hạng trung bình nên mỗi nhóm không nhất thiết đúng 25% số người. '
           'Nhóm không chồng lấn và bao phủ mọi người có điểm môn mục tiêu. Không gán thiếu điểm bằng 0.',
           '**Phạm vi suy luận:** Đây là hồ sơ điểm tương đối trong từng năm, chưa phải nhóm năng lực '
           'đầu vào hoặc thước đo tương đương giữa hai đề. Chênh lệch còn chịu ảnh hưởng của thay đổi '
           'môn tham chiếu, cơ cấu tự chọn và kỳ thi. Không xem điều chỉnh theo nhóm này là kiểm soát '
           'đầy đủ yếu tố nhiễu hoặc ước lượng tác động riêng của chương trình.',
           '### Số người điểm cao trong từng nhóm hồ sơ', table(pd.DataFrame(rows)),
           '**Diễn giải bảng:** Mũi tên là 2023 → 2025. “Số có điểm môn” là mẫu số cho tỷ lệ '
           'đạt ≥9 ngay trong nhóm. “Góp thay đổi ≥9” lấy phần người điểm cao của nhóm trên tổng '
           'người có điểm toàn môn năm 2025 trừ năm 2023; cộng năm nhóm bằng thay đổi tỷ lệ ≥9 '
           'toàn môn. Đây không phải biến động của cùng các cá nhân. Nhóm thiếu điểm thường ít '
           'người, có nhóm dưới 100; đọc số đếm và tránh suy rộng từ tỷ lệ nhóm nhỏ. Ngoại ngữ '
           'gồm Tiếng Anh, không cộng hai mục này thành tổng độc lập.',
           '### Tách thay đổi cơ cấu nhóm và thay đổi trong nhóm',table(pd.DataFrame(high)),
           '**Diễn giải bảng:** Hai phần cộng thành tổng thay đổi tỷ lệ ≥9. Phần cơ cấu phản ánh '
           'nhóm hồ sơ chiếm tỷ trọng khác trong người thi môn đó; phần trong nhóm phản ánh tỷ lệ '
           '≥9 của các nhóm cùng tên thay đổi. Dùng phép phân rã đối xứng với trọng số trung bình '
           'hai năm, không chọn một năm làm chuẩn tùy ý. Đây là đẳng thức mô tả; “trong nhóm” '
           'vẫn chứa thay đổi đề, lựa chọn thí sinh, năng lực và các yếu tố khác, không phải tác động '
           'thuần của chương trình. Mỗi môn có thể dùng nhóm tham chiếu khác, như Toán dùng Văn.',
           table(pd.DataFrame(means)),
           '**Diễn giải bảng:** Đơn vị ở đây là điểm trên thang 10, khác điểm phần trăm ở bảng trên. '
           'Hai phần cộng thành chênh lệch trung bình. Nếu phần cơ cấu dương nhưng tổng âm, '
           'thay đổi trung bình trong các nhóm đã kéo kết quả theo hướng ngược lại mạnh hơn. '
           'Các nhóm chỉ giữ vị trí tương đối; không khẳng định cùng chất lượng học sinh giữa hai năm.',
           '![Đóng góp của các nhóm hồ sơ vào biến động tỷ lệ từ 9](../outputs/audits/subject_group_contributions.png)',
           '**Diễn giải hình:** Mỗi ô là đóng góp ròng của một nhóm vào chênh lệch tỷ lệ ≥9 '
           'toàn môn, đơn vị điểm phần trăm; mỗi hàng cộng thành thay đổi toàn môn. Màu đỏ là '
           'đóng góp tăng, xanh là giảm. Màu thể hiện kết quả theo nhóm, không phải chỉ số bất thường '
           'hay nghi vấn gian lận. Nhóm của Toán được xác định bằng Văn; các hàng khác dùng Toán.']
    for subject in ('physics','chemistry','biology','english','history','geography'):
        a=profiles[(profiles.year==2023)&(profiles.subject==subject)&(profiles.reference_group=='Q4')].iloc[0]
        b=profiles[(profiles.year==2025)&(profiles.subject==subject)&(profiles.reference_group=='Q4')].iloc[0]
        lines.append(f'**{SUBJECT_LABELS[subject]} — nhóm hạng Toán >75%:** '
                     f'chiếm {pair(100*a.share,100*b.share)}% người có điểm môn này; '
                     f'tỷ lệ đạt ≥9 ngay trong nhóm {pair(a.pct_ge9,b.pct_ge9)}%; '
                     f'số người đạt ≥9 {pair(a.n_ge9,b.n_ge9,0)}. '
                     'Các tỷ lệ này dùng mẫu số khác nhau: tỷ trọng nhóm trên toàn môn và tỷ lệ điểm cao trong nhóm.')
    lines += ['**Phát hiện cần thảo luận:** Với Anh, tỷ trọng nhóm có thứ hạng Toán cao tăng '
              'nhưng tỷ lệ Anh ≥9 trong nhóm này giảm; chỉ nói “ít người thi nên điểm giảm” '
              'không mô tả đủ kết quả. Với Hóa và Sinh, nhóm hạng Toán >75% chiếm tỷ trọng thấp hơn '
              'nhưng tỷ lệ đạt ≥9 trong nhóm cao hơn. Đây là bằng chứng bổ sung về hồ sơ điểm, '
              'chưa phân biệt được thay đổi năng lực, đề/cách chấm hay cơ chế tự lựa chọn. '
              'Phân nhóm theo trường/địa phương và kiểm tra bất thường vẫn chưa được thực hiện.',
              '[Bảng nhóm và số đếm](../outputs/audits/subject_group_profiles.csv) · '
              '[Phân rã từng nhóm](../outputs/audits/subject_group_decomposition.csv) · '
              '[Tổng hợp thay đổi](../outputs/audits/subject_group_changes.csv).']
    return lines
