"""Run subject inference first; read-only validation is available separately."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from src.inference_io import ROOT,load_inputs,write_tables,make_metadata,validate_metadata,validate_report_links
from src.analysis_catalog import subject_values,subject_catalog,label
from src.statistical_tests import analyze_subjects,compare_values,ks_discrete,bootstrap_d,adjust_pvalues,apply_families,clean_values,describe_values
from src.inference_plots import distribution_plot,effect_overview,safe_name
from src.report_part2 import render_report,build_notebook,REPORT

CONFIG=dict(seed=20261021,bootstrap=999,permutations=1999,phase='subject_statistics',domain=[0,10])
FUNCTIONS=[subject_values,subject_catalog,label,analyze_subjects,compare_values,ks_discrete,bootstrap_d,adjust_pvalues,apply_families,clean_values,describe_values]

def validate_outputs(root:Path=ROOT):
    folder=root/'outputs/statistics';meta=validate_metadata(root,folder,FUNCTIONS,CONFIG)
    cat=pd.read_csv(folder/'subject_catalog.csv');test=pd.read_csv(folder/'subject_tests.csv');desc=pd.read_csv(folder/'subject_descriptives.csv')
    assert not cat.duplicated(['year','subject_id']).any() and not test.subject_id.duplicated().any()
    assert set(test.subject_id)==set(cat.subject_id) and len(desc)==len(cat)
    for row in cat.itertuples():
        d=desc.loc[desc.year.eq(row.year)&desc.subject_id.eq(row.subject_id)]
        assert len(d)==1 and int(d.n.iloc[0])==row.n_observed
    compared=test.loc[test.status.eq('compared')];assert compared.ks_p_permutation.between(.0005,1).all()
    assert np.allclose(compared.delta_mean,compared.mean_2025-compared.mean_2023)
    assert compared.welch_family_size.eq(compared.welch_p.notna().sum()).all()
    for col in ['welch_p_holm','mwu_p_bh','ks_p_permutation_bh','brown_forsythe_p_bh']:
        assert test[col].dropna().between(0,1).all()
    baseline=root/'branch_imports/2026-10-21/son/ket_qua_2023_vs_2025_chi_tieng_anh.csv'
    checked=0
    if baseline.exists():
        old=pd.read_csv(baseline)
        names=dict(zip(['math','literature','foreign_language:N1','physics','chemistry','biology','history','geography'],['toan','ngu_van','ngoai_ngu','vat_li','hoa_hoc','sinh_hoc','lich_su','dia_li']))
        for sid,mon in names.items():
            a=test.loc[test.subject_id.eq(sid)].iloc[0];b=old.loc[old.mon.eq(mon)].iloc[0]
            assert a.n_2023==b.n_A and a.n_2025==b.n_B
            assert abs(a.mean_2023-b.mean_A)<1e-10 and abs(a.mean_2025-b.mean_B)<1e-10
            assert abs(a.cohen_d-b.cohen_d)<1e-10;checked+=1
    links=validate_report_links(root,root/REPORT)
    return dict(status='passed',catalog_rows=len(cat),subject_union=len(test),compared=len(compared),son_subjects_checked=checked,report_links=links,artifact_count=len(meta['artifact_hashes']))

def run(root:Path=ROOT):
    frames,audits=load_inputs(root);print('Loaded inputs; computing every subject',flush=True)
    result=analyze_subjects(frames,progress=lambda text:print(text,flush=True));folder=root/'outputs/statistics'
    write_tables(folder,dict(subject_catalog=result['catalog'],subject_descriptives=result['descriptives'],subject_tests=result['tests'],effect_sizes=result['effects'],mapping_issues=result['mapping_issues']))
    for r in result['tests'].itertuples():
        distribution_plot({year:subject_values(frame,r.subject_id) for year,frame in frames.items()},r.label,
            folder/'figures'/f'dist_{safe_name(r.subject_id)}.png')
    effect_overview(result['tests'],folder/'figures/subject_overview.png','Từng môn: đọc mức đổi điểm cùng effect size')
    make_metadata(root,folder,audits,FUNCTIONS,CONFIG)
    (root/REPORT).write_text(render_report(root),encoding='utf-8');build_notebook(root)
    return validate_outputs(root)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rerun',action='store_true');parser.add_argument('--validate',action='store_true');args=parser.parse_args()
    print(json.dumps(run() if args.rerun else validate_outputs(),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
