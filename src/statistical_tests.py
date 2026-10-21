"""Auditable two-cohort comparisons, with discrete-score resampling."""
from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from src.analysis_catalog import subject_catalog, subject_values, label

SEED=20261021
TEST_FIELDS=['welch_t','welch_df','welch_p','delta_ci_low','delta_ci_high','mwu_U','mwu_p',
    'mwu_A','rank_biserial','ks_D','ks_location','ks_p_asymptotic_reference','ks_p_permutation',
    'ks_exceedances','ks_permutations','brown_forsythe_stat','brown_forsythe_p','levene_mean_p',
    'variance_ratio','cohen_d','d_ci_low','d_ci_high','hedges_g']

def clean_values(values, domain=(0.,10.)) -> np.ndarray:
    x=np.asarray(values,dtype=float).ravel();x=x[~np.isnan(x)]
    if (~np.isfinite(x)).any() or ((x<domain[0])|(x>domain[1])).any():
        raise ValueError(f'Nonfinite/out-of-domain observations: {domain}')
    return x

def describe_values(values, domain=(0.,10.)) -> dict:
    x=clean_values(values,domain);n=len(x)
    if not n: return dict(n=0,mean=np.nan,median=np.nan,sd=np.nan,iqr=np.nan,
        p80=np.nan,p90=np.nan,pct_below_half=np.nan,pct_ge_80=np.nan,pct_ge_90=np.nan)
    q=np.quantile(x,[.25,.5,.75,.8,.9],method='higher')
    return dict(n=n,mean=float(x.mean()),median=float(np.median(x)),
        sd=float(x.std(ddof=1)) if n>1 else np.nan,iqr=float(q[2]-q[0]),p80=float(q[3]),p90=float(q[4]),
        pct_below_half=float(100*np.mean(x<domain[1]/2)),pct_ge_80=float(100*np.mean(x>=domain[1]*.8)),
        pct_ge_90=float(100*np.mean(x>=domain[1]*.9)))

def adjust_pvalues(p, *, method: str) -> np.ndarray:
    p=np.asarray(p,dtype=float);out=np.full(p.shape,np.nan);mask=np.isfinite(p)
    x=p[mask]
    if not len(x): return out
    if ((x<0)|(x>1)).any(): raise ValueError('p-values outside [0,1]')
    if method=='bh': out[mask]=stats.false_discovery_control(x,method='bh')
    elif method=='holm':
        order=np.argsort(x,kind='stable'); adjusted=np.minimum(1,np.maximum.accumulate(x[order]*(len(x)-np.arange(len(x)))))
        back=np.empty(len(x));back[order]=adjusted;out[mask]=back
    else: raise ValueError(method)
    return out

def ks_discrete(a23,b25,*,seed:int,permutations:int=1999) -> dict:
    a=np.asarray(a23,dtype=float);b=np.asarray(b25,dtype=float)
    if not len(a) or not len(b): return {k:np.nan for k in TEST_FIELDS if k.startswith('ks_')}
    support=np.union1d(a,b)
    ca=np.bincount(np.searchsorted(support,a),minlength=len(support))
    cb=np.bincount(np.searchsorted(support,b),minlength=len(support));pooled=ca+cb
    delta=np.cumsum(ca)/len(a)-np.cumsum(cb)/len(b);j=int(np.argmax(np.abs(delta)));D=float(abs(delta[j]))
    rng=np.random.default_rng(seed)
    # Conditional label permutation on the complete score population, preserving ties.
    perm_b=rng.multivariate_hypergeometric(pooled,len(b),size=permutations,method='marginals')
    perm_a=pooled[None,:]-perm_b
    null_D=np.max(np.abs(np.cumsum(perm_a,axis=1)/len(a)-np.cumsum(perm_b,axis=1)/len(b)),axis=1)
    exceed=int(np.count_nonzero(null_D>=D-1e-12))
    return dict(ks_D=D,ks_location=float(support[j]),
        ks_p_asymptotic_reference=float(stats.ks_2samp(a,b,method='asymp').pvalue),
        ks_p_permutation=(1+exceed)/(1+permutations),ks_exceedances=exceed,ks_permutations=permutations)

def bootstrap_d(a,b,seed,reps=999):
    rng=np.random.default_rng(seed)
    def moments(x):
        values,counts=np.unique(x,return_counts=True);n=len(x)
        weights=rng.multinomial(n,counts/n,size=reps)
        means=weights@values/n
        variance=np.maximum(0,(weights@(values*values)-n*means*means)/(n-1))
        return means,variance
    ma,va=moments(a);mb,vb=moments(b)
    pooled=((len(a)-1)*va+(len(b)-1)*vb)/(len(a)+len(b)-2)
    with np.errstate(divide='ignore',invalid='ignore'): d=(mb-ma)/np.sqrt(pooled)
    finite=d[np.isfinite(d)]
    return tuple(np.quantile(finite,[.025,.975])) if len(finite)==reps else (np.nan,np.nan)

def compare_values(a23,b25,*,entity_id:str,seed:int,domain=(0.,10.)) -> dict:
    a=clean_values(a23,domain);b=clean_values(b25,domain)
    record=dict(entity_id=entity_id,direction='2025-2023',status='compared',reason='',seed=seed)
    record.update({k:np.nan for k in TEST_FIELDS})
    for year,x in ((2023,a),(2025,b)):
        record.update({f'{k}_{year}':v for k,v in describe_values(x,domain).items()})
    if not len(a) or not len(b):
        record.update(status='single_year',reason='Không có điểm ở một năm; không tạo mẫu bằng 0.')
        return record
    record['delta_mean']=float(b.mean()-a.mean())
    if min(len(a),len(b))<2:
        record.update(status='insufficient_sample',reason='Cần ít nhất hai quan sát mỗi năm.');return record
    va=float(a.var(ddof=1));vb=float(b.var(ddof=1));sp2=((len(a)-1)*va+(len(b)-1)*vb)/(len(a)+len(b)-2)
    record['variance_ratio']=vb/va if va>0 else np.nan
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        if va>0 or vb>0:
            t=stats.ttest_ind(b,a,equal_var=False);ci=t.confidence_interval()
            record.update(welch_t=float(t.statistic),welch_df=float(t.df),welch_p=float(t.pvalue),
                          delta_ci_low=float(ci.low),delta_ci_high=float(ci.high))
        u=stats.mannwhitneyu(b,a,alternative='two-sided',method='asymptotic')
        A=float(u.statistic/(len(a)*len(b)))
        record.update(mwu_U=float(u.statistic),mwu_p=float(u.pvalue),mwu_A=A,rank_biserial=2*A-1)
        bf=stats.levene(a,b,center='median');lm=stats.levene(a,b,center='mean')
        record.update(brown_forsythe_stat=float(bf.statistic),brown_forsythe_p=float(bf.pvalue),levene_mean_p=float(lm.pvalue))
    if sp2>0:
        d=record['delta_mean']/np.sqrt(sp2);lo,hi=bootstrap_d(a,b,seed+100)
        record.update(cohen_d=float(d),hedges_g=float(d*(1-3/(4*(len(a)+len(b))-9))),d_ci_low=float(lo),d_ci_high=float(hi))
    else: record['reason']='SD gộp bằng 0: d/CI và Welch không xác định; MWU/KS vẫn được báo.'
    record.update(ks_discrete(a,b,seed=seed))
    record['undefined_methods']=';'.join(k for k in TEST_FIELDS if pd.isna(record[k]))
    record['underflow_methods']=';'.join(k for k in ['welch_p','mwu_p','brown_forsythe_p','ks_p_asymptotic_reference'] if record[k]==0)
    return record

def apply_families(table: pd.DataFrame, prefix: str) -> pd.DataFrame:
    table=table.copy()
    if 'welch_p' not in table: table['welch_p']=np.nan
    table['welch_p_holm']=adjust_pvalues(table.welch_p,method='holm')
    methods=['mwu_p','ks_p_permutation','brown_forsythe_p']
    for name in methods:
        if name not in table: table[name]=np.nan
    p=table[methods].to_numpy().ravel();q=adjust_pvalues(p,method='bh').reshape(len(table),3)
    for i,name in enumerate(methods):table[name+'_bh']=q[:,i]
    table['welch_family']=prefix+'_welch';table['welch_family_size']=int(table.welch_p.notna().sum())
    table['exploratory_family']=prefix+'_mwu_ks_bf';table['exploratory_family_size']=int(np.isfinite(p).sum())
    return table

def analyze_subjects(frames,*,seed=SEED,progress=None):
    catalog=subject_catalog(frames);rows=[];descriptions=[]
    for index,sid in enumerate(sorted(catalog.subject_id.unique())):
        arrays={year:subject_values(frame,sid).to_numpy(dtype=float) for year,frame in frames.items()}
        if progress:progress(f'Môn {label(sid)}')
        record=compare_values(arrays.get(2023,[]),arrays.get(2025,[]),entity_id=sid,seed=seed+index)
        record.update(subject_id=sid,label=label(sid));rows.append(record)
        for year,x in arrays.items():
            if np.isfinite(x).any():descriptions.append(dict(year=year,subject_id=sid,label=label(sid),**describe_values(x)))
    table=apply_families(pd.DataFrame(rows),'subject')
    effect_cols=['subject_id','label','status','reason','n_2023','n_2025','delta_mean','delta_ci_low','delta_ci_high',
        'cohen_d','d_ci_low','d_ci_high','hedges_g','mwu_A','rank_biserial','variance_ratio']
    issues=catalog.loc[catalog.status.ne('observed'),['year','subject_id','status']].copy()
    for year,frame in frames.items():
        missing=int((frame.foreign_language.notna() & frame.language_code.isna()).sum())
        if missing:issues=pd.concat([issues,pd.DataFrame([dict(year=year,subject_id='foreign_language:missing',status=f'{missing} điểm thiếu mã')])],ignore_index=True)
    return dict(catalog=catalog,descriptives=pd.DataFrame(descriptions),tests=table,
                effects=table.reindex(columns=effect_cols),mapping_issues=issues)

def analyze_combination_totals(frames,catalog,*,seed=SEED,progress=None):
    import json
    from src.analysis_catalog import combination_scores
    rows=[];descs=[]
    for i,(key,group) in enumerate(catalog.groupby('canonical_id',sort=True)):
        arrays={r.year:combination_scores(frames[r.year],json.loads(r.subjects)).to_numpy(float) for r in group.drop_duplicates('year').itertuples()}
        aliases='/'.join(group.code.unique());changed=group.comparison_class.eq('changed_subject_content').any()
        if progress:progress(f'Tổ hợp {aliases}')
        if changed:
            # Only descriptions, never infer equivalence between GDCD and economics/law.
            record=compare_values([],[],entity_id=key,seed=seed+10000+i,domain=(0,30));record.update(status='changed_subject_content',reason='GDCD 2023 được thay bằng GDKT&PL 2025; chỉ mô tả riêng, không kiểm định chính liên năm.')
            for year,x in arrays.items():record.update({f'{k}_{year}':v for k,v in describe_values(x,(0,30)).items()})
            record['delta_mean']=record['mean_2025']-record['mean_2023']
        else:record=compare_values(arrays.get(2023,[]),arrays.get(2025,[]),entity_id=key,seed=seed+10000+i,domain=(0,30))
        record.update(label=aliases,canonical_id=key);rows.append(record)
        for year,x in arrays.items():descs.append(dict(year=year,entity_id=key,label=aliases,**describe_values(x,(0,30))))
    table=apply_families(pd.DataFrame(rows),'combination')
    return dict(tests=table,descriptives=pd.DataFrame(descs))
