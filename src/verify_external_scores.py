"""Compare local scores with saved published reference tables and histograms.

Run: python -m src.verify_external_scores. References preserve the published
values; mismatches are reported without changing either input dataset.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from src.score_data import load_scores, file_sha256

ROOT=Path(__file__).resolve().parents[1]


def right_closed_counts(values, step):
    """[0,step], (step,2*step], ...; preserve exact boundary scores."""
    edges=np.arange(0,10+step/2,step)
    positions=np.searchsorted(edges[1:],np.asarray(values),side='left')
    return np.bincount(positions,minlength=len(edges)-1)


def verify(root=ROOT):
    reference_path=root/'data/external/verification/official_reference.json'
    reference=json.loads(reference_path.read_text(encoding='utf-8'))
    statistic_rows=[]; bin_rows=[]; conditions=[]; inputs=[]
    for year,path in [(2023,root/'data/raw/original.csv'),(2025,root/'data/dataset_diem_thi_thpt_2025.csv')]:
        frame,audit=load_scores(path,year)
        inputs.append({'year':year,'source':str(path),'sha256':audit['sha256']})
        refs=[r for r in reference['records'] if r['year']==year]
        if year==2025:
            tech=[r for r in refs if r['subject'].startswith('technology_')]
            aggregate={'year':year,'subject':'technology','source_url':tech[0]['source_url'],
                       'histogram_step':.25,'histogram_right_closed_counts':np.sum([r['histogram_right_closed_counts'] for r in tech],axis=0).tolist()}
            for metric in ['n','n_lt5','n_ge7','n_10','n_0','n_le1']:
                aggregate[metric]=sum(r[metric] for r in tech)
            refs=[r for r in refs if not r['subject'].startswith('technology_')]+[aggregate]
        for ref in refs:
            subject=ref['subject']; scores=frame[subject].dropna()
            local={'n':len(scores),'mean':scores.mean(),'median':scores.median(),'sd':scores.std(ddof=1),
                   'mode':float(scores.mode().iloc[0]),'n_le1':int(scores.le(1).sum()),'n_lt5':int(scores.lt(5).sum()),
                   'n_ge7':int(scores.ge(7).sum()),'n_0':int(scores.eq(0).sum()),'n_10':int(scores.eq(10).sum())}
            for metric,value in local.items():
                if metric not in ref: continue
                expected=ref[metric]
                tolerance=.005000001 if metric in ['mean','sd'] else 1e-8
                statistic_rows.append(dict(year=year,subject=subject,metric=metric,local=value,published=expected,
                                           difference=value-expected,status='match' if abs(value-expected)<=tolerance else 'mismatch',
                                           tolerance=tolerance,source_url=ref['source_url'],source_page=ref.get('page')))
            if year==2023:
                frequencies={float(k):v for k,v in ref['exact_score_frequency'].items()}
                # Published literature tables display quarter-point anchors.
                # This is a verification-only sensitivity calculation; original
                # scores used for combinations/correlations remain unchanged.
                compared=(scores*4).round()/4 if subject=='literature' else scores
                observed=compared.value_counts().to_dict()
                for score in sorted(set(frequencies)|set(observed)):
                    actual=int(observed.get(score,0)); expected=int(frequencies.get(score,0))
                    kind='nearest_quarter_display_sensitivity' if subject=='literature' else 'exact_score'
                    bin_rows.append(dict(year=year,subject=subject,kind=kind,lower=score,upper=score,
                                         local=actual,published=expected,difference=actual-expected))
            else:
                step=ref['histogram_step']; expected=ref['histogram_right_closed_counts']
                observed=right_closed_counts(scores,step)
                for i,(actual,count) in enumerate(zip(observed,expected,strict=True)):
                    bin_rows.append(dict(year=year,subject=subject,kind='right_closed_interval',lower=i*step,upper=(i+1)*step,
                                         local=int(actual),published=count,difference=int(actual)-count))
        optional=['physics','chemistry','biology','history','geography','economics_law','informatics','technology','foreign_language']
        if year==2025:
            counts=frame[optional].notna().sum(axis=1)
            conditions.append(dict(year=year,check='more_than_two_optional_scores',n=int(counts.gt(2).sum())))
            for n,count in counts.value_counts().sort_index().items():
                conditions.append(dict(year=year,check=f'optional_score_count_{n}',n=int(count)))
        for subject,step in [('math',.2),('physics',.25),('chemistry',.25),('biology',.25),('history',.25),('geography',.25),('civics',.25),('english',.2)] if year==2023 else []:
            x=frame[subject].dropna()/step
            conditions.append(dict(year=year,check=f'off_score_grid_{subject}',n=int((x-x.round()).abs().gt(1e-8).sum())))
        if year==2023:
            literature=frame.literature.dropna()
            conditions.extend([dict(year=year,check='literature_off_quarter_grid',n=int(((literature*4-(literature*4).round()).abs()>1e-8).sum())),
                               dict(year=year,check='literature_below5_after_nearest_quarter_display',n=int(((literature*4).round()/4).lt(5).sum()))])
    target=root/'outputs/audits'; target.mkdir(parents=True,exist_ok=True)
    statistics=pd.DataFrame(statistic_rows); bins=pd.DataFrame(bin_rows)
    statistics.to_csv(target/'external_score_statistics.csv',index=False)
    bins.to_csv(target/'external_score_frequencies.csv',index=False)
    pd.DataFrame(conditions).to_csv(target/'external_exam_conditions.csv',index=False)
    sources=[{'path':str(p.relative_to(root)),'sha256':file_sha256(p)}
             for p in sorted(reference_path.parent.iterdir()) if p.is_file()]
    result={'retrieved_at':reference['retrieved_at'],'reference_sha256':file_sha256(reference_path),
            'inputs':inputs,'reference_files':sources,
            'statistic_checks':len(statistics),'statistic_mismatches':statistics.loc[statistics.status.eq('mismatch')].to_dict('records'),
            'frequency_checks':len(bins),'frequency_mismatches':bins.loc[bins.difference.ne(0)].to_dict('records'),
            'conditions':conditions,'scope_limit':'Aggregate agreement does not authenticate every student record or cross-subject pairing.'}
    (target/'external_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(statistics.groupby(['year','status']).size().to_string())
    print('FREQUENCY MISMATCHES\n'+bins[bins.difference.ne(0)].to_string(index=False))
    return result


if __name__=='__main__': verify()
