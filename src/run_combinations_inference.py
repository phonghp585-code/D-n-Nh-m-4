"""Final phase, consuming verified subject statistics and relations."""
import argparse,json
import numpy as np,pandas as pd
from src.inference_io import ROOT,load_inputs,write_tables,make_metadata,validate_metadata,validate_report_links
from src.analysis_catalog import combination_catalog,combination_scores,subject_values,label
from src.statistical_tests import analyze_combination_totals,compare_values,describe_values,apply_families
from src.correlation_pca import pca_by_combination,compare_pca,pca_stability_from_vectors,group_sensitivity
from src.inference_plots import distribution_plot,effect_overview,pca_plot,safe_name
from src import report_part2,report_part4

CONFIG=dict(seed=20261021,offset=10000,bootstrap=999,permutations=1999,min_pca_n=30,phase='combinations',sum_noise_rounding=10,density_bandwidth=.35,pca_ddof=1)
FUNCTIONS=[combination_catalog,combination_scores,subject_values,label,analyze_combination_totals,compare_values,describe_values,apply_families,pca_by_combination,compare_pca,pca_stability_from_vectors,group_sensitivity,pca_plot]

def validate_outputs(root=ROOT):
    folder=root/'outputs/combination_inference';meta=validate_metadata(root,folder,FUNCTIONS,CONFIG)
    cat=pd.read_csv(folder/'combination_catalog.csv');t=pd.read_csv(folder/'total_tests.csv');s=pd.read_csv(folder/'pca_summary.csv');l=pd.read_csv(folder/'pca_loadings.csv')
    assert len(cat)==48 and cat.groupby('year').canonical_id.nunique().eq(23).all() and cat.stored_mismatches.eq(0).all()
    assert len(t)==23 and t.status.eq('compared').sum()==16 and t.status.eq('changed_subject_content').sum()==7
    assert t.loc[t.status.eq('changed_subject_content'),'welch_p'].isna().all()
    assert t.welch_family_size.eq(16).all() and t.exploratory_family_size.eq(48).all()
    assert len(s)==46 and s.status.eq('estimated').all() and len(l)==138
    assert np.allclose(s[[f'pc{k}_explained_pct' for k in (1,2,3)]].sum(axis=1),100,atol=1e-10)
    oldpath=root/'branch_imports/2026-10-21/duy/duy/outputs/pca_summary.csv';checked=0
    if oldpath.exists():
        for old in pd.read_csv(oldpath).itertuples():
            new=s.loc[s.year.eq(old.year)&s.code.eq(old.combination)].iloc[0]
            assert old.n_complete==new.n_complete
            assert np.allclose([getattr(old,f'pc{k}_explained_pct') for k in (1,2,3)],[getattr(new,f'pc{k}_explained_pct') for k in (1,2,3)],rtol=0,atol=1e-8);checked+=1
    baseline=pd.read_csv(root/'outputs/combinations/combination_validation.csv')
    for r in cat.itertuples():assert r.n_complete==baseline.loc[baseline.year.eq(r.year)&baseline.combination.eq(r.code),'n_recomputed'].iloc[0]
    return dict(status='passed',code_years=len(cat),canonical_models=len(s),tested_totals=16,changed_totals=7,duy_pca_checked=checked,part3_counts_checked=len(cat),artifacts=len(meta['artifact_hashes']),report_links=[validate_report_links(root,root/p.REPORT) for p in (report_part2,report_part4)])

def run(root=ROOT):
    from src.run_part2 import validate_outputs as va
    from src.run_part4 import validate_outputs as vb
    va(root);vb(root);frames,audits=load_inputs(root);cat,issues=combination_catalog(frames,{a['year']:a['available_combination_codes'] for a in audits})
    assert issues.empty,'Resolve mapping issues before inference'
    totals=analyze_combination_totals(frames,cat,progress=lambda s:print(s,flush=True));summaries=[];loadings=[]
    for year,frame in frames.items():
        print(f'PCA all combinations {year}',flush=True);s,l=pca_by_combination(frame,year,cat);summaries.append(s);loadings.append(l)
    summary=pd.concat(summaries,ignore_index=True);loads=pd.concat(loadings,ignore_index=True)
    for key,g in summary.groupby('canonical_id'):
        if g.comparison_class.eq('same_named_subjects').all():
            a=loads.loc[loads.canonical_id.eq(key)&loads.year.eq(2023)].sort_values('subject_id');b=loads.loc[loads.canonical_id.eq(key)&loads.year.eq(2025)].sort_values('subject_id')
            for k in (1,2,3):
                if a[f'vector_pc{k}'].to_numpy()@b[f'vector_pc{k}'].to_numpy()<0:loads.loc[b.index,[f'vector_pc{k}',f'loading_pc{k}']]*=-1
    stability=compare_pca(summary,loads);sensitivity=group_sensitivity(frames,cat);folder=root/'outputs/combination_inference'
    write_tables(folder,dict(combination_catalog=cat,mapping_issues=issues,total_descriptives=totals['descriptives'],total_tests=totals['tests'],total_effect_sizes=totals['tests'][['canonical_id','label','status','cohen_d','d_ci_low','d_ci_high']],pca_summary=summary,pca_loadings=loads,pca_stability=stability,group_sensitivity=sensitivity))
    for key,group in cat.groupby('canonical_id',sort=True):
        title='/'.join(group.code.unique());changed=group.comparison_class.eq('changed_subject_content').any();title+=' — đổi GDCD / GDKT&PL' if changed else ''
        arrays={r.year:combination_scores(frames[r.year],json.loads(r.subjects)) for r in group.drop_duplicates('year').itertuples()}
        distribution_plot(arrays,title,folder/'figures'/f'dist_{safe_name(key)}.png',maximum=30)
        pca_plot(summary.loc[summary.canonical_id.eq(key)],loads.loc[loads.canonical_id.eq(key)],title,folder/'figures'/f'pca_{safe_name(key)}.png')
    effect_overview(totals['tests'],folder/'figures/total_overview.png','Các tổng cùng tên môn: điểm và effect size')
    make_metadata(root,folder,audits,FUNCTIONS,CONFIG)
    for p in (report_part2,report_part4):(root/p.REPORT).write_text(p.render_report(root,include_combinations=True),encoding='utf-8');p.build_notebook(root,include_combinations=True)
    return validate_outputs(root)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rerun',action='store_true');p.add_argument('--validate',action='store_true');a=p.parse_args()
    print(json.dumps(run() if a.rerun else validate_outputs(),ensure_ascii=False,indent=2))
