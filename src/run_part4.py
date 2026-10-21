"""Every observed subject pair; PCA is appended after the subject gate."""
import argparse,json
import numpy as np,pandas as pd
from src.inference_io import ROOT,load_inputs,write_tables,make_metadata,validate_metadata,validate_report_links
from src.analysis_catalog import subject_values,label
from src.correlation_pca import pairwise_correlations,weighted_pearson,bootstrap_pair_r,compare_correlations,wilson_interval,high_score_concordance,rank_pairs
from src.statistical_tests import adjust_pvalues
from src.inference_plots import relation_matrix,relation_heatmap,pair_examples
from src.report_part4 import REPORT,render_report,build_notebook

CONFIG=dict(seed=20261021,bootstrap=999,min_n=30,min_rank_n=100,phase='subject_relations')
FUNCTIONS=[subject_values,label,pairwise_correlations,weighted_pearson,bootstrap_pair_r,compare_correlations,wilson_interval,high_score_concordance,rank_pairs,adjust_pvalues,relation_matrix,relation_heatmap,pair_examples]

def validate_outputs(root=ROOT):
    folder=root/'outputs/subject_relations';meta=validate_metadata(root,folder,FUNCTIONS,CONFIG)
    pairs=pd.read_csv(folder/'pairwise_correlations.csv');high=pd.read_csv(folder/'high_score_concordance.csv');delta=pd.read_csv(folder/'correlation_deltas.csv')
    cat=pd.read_csv(root/'outputs/statistics/subject_catalog.csv')
    assert not pairs.duplicated(['year','subject_x','subject_y']).any()
    for year in (2023,2025):
        count=int(cat.year.eq(year).sum());assert int(pairs.year.eq(year).sum())==count*(count-1)//2
    assert pairs.pearson_r.dropna().between(-1,1).all()
    assert pairs.loc[pairs.n_pair.lt(30),'pearson_r'].isna().all()
    assert len(high)==4*len(pairs) and high.p_y_high_given_x_high.dropna().between(0,1).all()
    assert delta.fisher_q_bh.dropna().between(0,1).all()
    checked=0;oldpath=root/'branch_imports/2026-10-21/duy/duy/outputs/pairwise_correlations.csv'
    if oldpath.exists():
        old=pd.read_csv(oldpath)
        for r in old.itertuples():
            a='foreign_language:N1' if r.subject_x=='english' else r.subject_x;b='foreign_language:N1' if r.subject_y=='english' else r.subject_y
            x,y=sorted([a,b]);new=pairs.loc[pairs.year.eq(r.year)&pairs.subject_x.eq(x)&pairs.subject_y.eq(y)].iloc[0]
            assert r.n_pair==new.n_pair and np.allclose([r.pearson_r,r.spearman_rho],[new.pearson_r,new.spearman_rho],atol=1e-10,rtol=0,equal_nan=True);checked+=1
    example=high.loc[high.year.eq(2025)&high.subject_x.eq('math')&high.subject_y.eq('physics')&high.cutoff_mode.eq('P80')].iloc[0]
    assert abs(example.p_y_high_given_x_high-.6028708808640844)<1e-12
    return dict(status='passed',pairs=len(pairs),high_score_rows=len(high),duy_pairs_checked=checked,artifacts=len(meta['artifact_hashes']),report_links=validate_report_links(root,root/REPORT))

def run(root=ROOT):
    from src.run_part2 import validate_outputs as validate_subjects
    validate_subjects(root);frames,audits=load_inputs(root);cat=pd.read_csv(root/'outputs/statistics/subject_catalog.csv')
    pairs=[];high=[]
    for year,frame in frames.items():
        print(f'Pairwise relations {year}',flush=True);pairs.append(pairwise_correlations(frame,year,cat));high.append(high_score_concordance(frame,year,cat))
    pairs=pd.concat(pairs,ignore_index=True);high=pd.concat(high,ignore_index=True);print('Correlation changes / paired bootstrap',flush=True)
    delta=compare_correlations(pairs,frames=frames);folder=root/'outputs/subject_relations'
    write_tables(folder,dict(pairwise_correlations=pairs,correlation_deltas=delta,high_score_concordance=high))
    for year in (2023,2025):
        ids=cat.loc[cat.year.eq(year),'subject_id'].tolist()
        for metric,name in [('pearson_r','pearson'),('spearman_rho','spearman'),('n_pair','n_pair')]:relation_heatmap(pairs.loc[pairs.year.eq(year)],ids,metric,folder/'figures'/f'{name}_{year}.png',f'{name} — {year}')
    common=sorted(set(cat.loc[cat.year.eq(2023),'subject_id'])&set(cat.loc[cat.year.eq(2025),'subject_id']))
    relation_heatmap(delta,common,'delta_r',folder/'figures/delta_r.png','Thay đổi Pearson r: 2025 − 2023');pair_examples(frames,high,folder/'figures')
    make_metadata(root,folder,audits,FUNCTIONS,CONFIG);(root/REPORT).write_text(render_report(root),encoding='utf-8');build_notebook(root)
    return validate_outputs(root)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rerun',action='store_true');p.add_argument('--validate',action='store_true');a=p.parse_args()
    print(json.dumps(run() if a.rerun else validate_outputs(),ensure_ascii=False,indent=2))
