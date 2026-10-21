"""Pairwise relations use observed same-person scores, never imputed scores."""
from __future__ import annotations
from itertools import combinations
import numpy as np
import pandas as pd
from scipy import stats
from src.analysis_catalog import subject_values,label
from src.statistical_tests import adjust_pvalues

TARGETS=[tuple(sorted(p)) for p in [('math','physics'),('literature','history'),('history','geography')]]

def pairwise_correlations(frame,year,catalog,*,min_n=30):
    ids=sorted(catalog.loc[catalog.year.eq(year),'subject_id']);values={s:subject_values(frame,s).to_numpy(float) for s in ids};rows=[]
    for sx,sy in combinations(ids,2):
        a,b=values[sx],values[sy];mask=np.isfinite(a)&np.isfinite(b);x=a[mask];y=b[mask];n=len(x)
        row=dict(year=year,subject_x=sx,subject_y=sy,n_pair=n,coverage=n/len(frame),
            pearson_r=np.nan,spearman_rho=np.nan,r_ci_low=np.nan,r_ci_high=np.nan,status='insufficient_sample',reason='n<30')
        if n>=min_n and np.ptp(x)>0 and np.ptp(y)>0:
            r=float(np.clip(stats.pearsonr(x,y).statistic,-1,1));rho=float(stats.spearmanr(x,y).statistic)
            row.update(pearson_r=r,spearman_rho=rho,status='estimated' if n>=100 else 'limited_sample',reason='' if n>=100 else '30≤n<100: không xếp hạng chính')
            if abs(r)<1-1e-12:
                z=np.arctanh(r);se=1/np.sqrt(n-3);lo,hi=np.tanh([z-1.95996398454*se,z+1.95996398454*se]);row.update(r_ci_low=lo,r_ci_high=hi)
            else:row['reason']='Tương quan hoàn hảo: không dùng Fisher vô hạn.'
        elif n>=min_n:row.update(status='constant_input',reason='Một môn có SD=0 trong tập cặp.')
        rows.append(row)
    return pd.DataFrame(rows)

def weighted_pearson(xy,weights):
    w=np.atleast_2d(weights).astype(float);n=w.sum(axis=1);x=xy[:,0];y=xy[:,1]
    sx=w@x;sy=w@y;vx=w@(x*x)-sx*sx/n;vy=w@(y*y)-sy*sy/n
    with np.errstate(divide='ignore',invalid='ignore'):
        r=(w@(x*y)-sx*sy/n)/np.sqrt(np.maximum(vx,0)*np.maximum(vy,0))
    return np.clip(r,-1,1)

def bootstrap_pair_r(x,y,rng,reps):
    xy,counts=np.unique(np.column_stack([x,y]),axis=0,return_counts=True)
    weights=rng.multinomial(len(x),counts/len(x),size=reps)
    return weighted_pearson(xy,weights)

def compare_correlations(pairwise,*,seed=20261021,bootstrap_reps=999,frames=None):
    keys=['subject_x','subject_y'];a=pairwise.loc[pairwise.year.eq(2023)].set_index(keys);b=pairwise.loc[pairwise.year.eq(2025)].set_index(keys);rows=[]
    for index,key in enumerate(sorted(set(a.index)|set(b.index))):
        row=dict(subject_x=key[0],subject_y=key[1],n_2023=0,n_2025=0,r_2023=np.nan,r_2025=np.nan,
            rho_2023=np.nan,rho_2025=np.nan,delta_r=np.nan,delta_rho=np.nan,fisher_z=np.nan,fisher_p=np.nan,
            delta_fisher_z_ci_low=np.nan,delta_fisher_z_ci_high=np.nan,delta_r_bootstrap_ci_low=np.nan,delta_r_bootstrap_ci_high=np.nan,status='not_comparable',reason='Thiếu môn/cặp hợp lệ ở một năm.')
        for year,table in ((2023,a),(2025,b)):
            if key in table.index:
                rec=table.loc[key];row[f'n_{year}']=int(rec.n_pair);row[f'r_{year}']=rec.pearson_r;row[f'rho_{year}']=rec.spearman_rho
        r1,r2=row['r_2023'],row['r_2025'];n1,n2=row['n_2023'],row['n_2025']
        if np.isfinite(r1) and np.isfinite(r2):
            row.update(delta_r=r2-r1,delta_rho=row['rho_2025']-row['rho_2023'],status='descriptive',reason='')
            if min(n1,n2)>3 and max(abs(r1),abs(r2))<1-1e-12:
                dz=np.arctanh(r2)-np.arctanh(r1);se=np.sqrt(1/(n1-3)+1/(n2-3));z=dz/se
                row.update(fisher_z=z,fisher_p=float(2*stats.norm.sf(abs(z))),delta_fisher_z_ci_low=dz-1.95996398454*se,delta_fisher_z_ci_high=dz+1.95996398454*se,status='compared')
            else:row['reason']='|r|=1: không suy luận Fisher.'
            if frames is not None and key in TARGETS:
                rng=np.random.default_rng(seed+index);boot=[]
                for year in (2023,2025):
                    x=subject_values(frames[year],key[0]).to_numpy(float);y=subject_values(frames[year],key[1]).to_numpy(float);mask=np.isfinite(x)&np.isfinite(y)
                    boot.append(bootstrap_pair_r(x[mask],y[mask],rng,bootstrap_reps))
                difference=boot[1]-boot[0]
                if np.isfinite(difference).all():row['delta_r_bootstrap_ci_low'],row['delta_r_bootstrap_ci_high']=np.quantile(difference,[.025,.975])
        rows.append(row)
    result=pd.DataFrame(rows);result['fisher_q_bh']=adjust_pvalues(result.fisher_p,method='bh');result['family_size']=int(result.fisher_p.notna().sum())
    return result

def wilson_interval(success,n):
    if not n:return np.nan,np.nan
    z=1.95996398454;p=success/n;denom=1+z*z/n;center=(p+z*z/(2*n))/denom;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return center-half,center+half

def high_score_concordance(frame,year,catalog,*,min_n=30):
    ids=sorted(catalog.loc[catalog.year.eq(year),'subject_id']);values={s:subject_values(frame,s).to_numpy(float) for s in ids};rows=[]
    for sx,sy in combinations(ids,2):
        a,b=values[sx],values[sy];mask=np.isfinite(a)&np.isfinite(b);a=a[mask];b=b[mask]
        for xname,yname,x,y in [(sx,sy,a,b),(sy,sx,b,a)]:
            for mode in ['P80','8']:
                row=dict(year=year,subject_x=xname,subject_y=yname,cutoff_mode=mode,n_pair=len(x),
                    threshold_x=np.nan,threshold_y=np.nan,n_x_high=0,p_x_high=np.nan,p_y_high_baseline=np.nan,
                    p_y_high_given_x_high=np.nan,lift=np.nan,delta_probability=np.nan,conditional_ci_low=np.nan,conditional_ci_high=np.nan,
                    status='insufficient_sample')
                if len(x)>=min_n:
                    tx,ty=(np.quantile(x,.8,method='higher'),np.quantile(y,.8,method='higher')) if mode=='P80' else (8.,8.)
                    highx=x>=tx;highy=y>=ty;nx=int(highx.sum());success=int((highx&highy).sum());baseline=float(highy.mean());conditional=success/nx if nx else np.nan;lo,hi=wilson_interval(success,nx)
                    row.update(threshold_x=tx,threshold_y=ty,n_x_high=nx,p_x_high=float(highx.mean()),p_y_high_baseline=baseline,
                        p_y_high_given_x_high=conditional,lift=conditional/baseline if baseline>0 else np.nan,
                        delta_probability=conditional-baseline,conditional_ci_low=lo,conditional_ci_high=hi,status='estimated' if nx else 'empty_high_group')
                rows.append(row)
    return pd.DataFrame(rows)

def rank_pairs(pairwise,*,min_n_for_ranking=100):
    selected=pairwise.loc[pairwise.n_pair.ge(min_n_for_ranking)&pairwise.pearson_r.gt(0)].copy()
    return selected.sort_values(['year','pearson_r'],ascending=[True,False]).assign(rank=lambda x:x.groupby('year').cumcount()+1)

def pca_by_combination(frame,year,catalog,*,min_n=30):
    import json
    summaries=[];loads=[]
    for row in catalog.loc[catalog.year.eq(year)].drop_duplicates('canonical_id').itertuples():
        subjects=json.loads(row.subjects);a=np.column_stack([subject_values(frame,s).to_numpy(float) for s in subjects]);a=a[np.isfinite(a).all(axis=1)]
        rec=dict(year=year,canonical_id=row.canonical_id,code=row.code,n_complete=len(a),coverage=len(a)/len(frame),subjects=row.subjects,comparison_class=row.comparison_class,status='insufficient_sample')
        for k in range(1,4):rec.update({f'eigenvalue_{k}':np.nan,f'pc{k}_explained_pct':np.nan})
        if len(a)>=min_n:
            means=a.mean(axis=0);sd=a.std(axis=0,ddof=1)
            if np.any(sd==0):rec['status']='constant_input'
            else:
                z=(a-means)/sd;_,s,vt=np.linalg.svd(z,full_matrices=False);eig=s*s/(len(a)-1);vectors=vt.T
                for k in range(3):
                    anchor=subjects.index('math') if k==0 and 'math' in subjects else subjects.index('literature') if k==0 and 'literature' in subjects else int(np.argmax(abs(vectors[:,k])))
                    if vectors[anchor,k]<0:vectors[:,k]*=-1
                    rec[f'eigenvalue_{k+1}']=eig[k];rec[f'pc{k+1}_explained_pct']=100*eig[k]/eig.sum()
                rec['status']='estimated'
                for j,subject in enumerate(subjects):
                    loads.append(dict(year=year,canonical_id=row.canonical_id,subject_id=subject,mean=means[j],sd=sd[j],**{f'vector_pc{k+1}':vectors[j,k] for k in range(3)},**{f'loading_pc{k+1}':vectors[j,k]*np.sqrt(eig[k]) for k in range(3)}))
        summaries.append(rec)
    return pd.DataFrame(summaries),pd.DataFrame(loads)

def pca_stability_from_vectors(a,b,ea,eb):
    from scipy.linalg import subspace_angles
    gaps=np.r_[np.diff(ea)*-1/np.maximum(ea[:-1],1e-15),np.diff(eb)*-1/np.maximum(eb[:-1],1e-15)]
    return dict(near_eigenvalues=bool(np.any(gaps<.05)),pc1_abs_cosine=float(abs(a[:,0]@b[:,0])),
        pc12_max_angle_deg=float(np.degrees(subspace_angles(a[:,:2],b[:,:2])).max()))

def compare_pca(summary,loadings):
    rows=[]
    for key,group in summary.groupby('canonical_id',sort=True):
        row=dict(canonical_id=key,status='not_comparable',reason='Thiếu mô hình hoặc đổi môn',near_eigenvalues=False,pc1_abs_cosine=np.nan,pc12_max_angle_deg=np.nan)
        if len(group)==2 and group.status.eq('estimated').all() and group.comparison_class.eq('same_named_subjects').all():
            vectors=[];eigs=[]
            for year in (2023,2025):
                t=loadings.loc[loadings.canonical_id.eq(key)&loadings.year.eq(year)].sort_values('subject_id');vectors.append(t[[f'vector_pc{k}' for k in (1,2,3)]].to_numpy());eigs.append(group.loc[group.year.eq(year),[f'eigenvalue_{k}' for k in (1,2,3)]].to_numpy()[0])
            row.update(pca_stability_from_vectors(*vectors,*eigs),status='compared',reason='Các PC được căn dấu theo cùng vector 2023 khi trình bày; góc không gian con bất biến dấu.')
        rows.append(row)
    return pd.DataFrame(rows)

def group_sensitivity(frames,catalog):
    import json
    rows=[]
    for row in catalog.drop_duplicates(['year','canonical_id']).itertuples():
        subjects=json.loads(row.subjects);a=pd.DataFrame({s:subject_values(frames[row.year],s) for s in subjects}).dropna()
        for x,y in combinations(subjects,2):
            rows.append(dict(year=row.year,canonical_id=row.canonical_id,subject_x=x,subject_y=y,n_complete=len(a),pearson_r=a[x].corr(a[y]) if len(a)>=30 else np.nan,spearman_rho=a[x].corr(a[y],method='spearman') if len(a)>=30 else np.nan))
    return pd.DataFrame(rows)
