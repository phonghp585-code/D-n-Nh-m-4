"""Reproducible part 3 deliverables for 2023 — CT2006 / 2025 — CT2018."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd

from src.score_data import COHORT_LABELS, ALL_COMBINATIONS, file_sha256, load_scores

ROOT=Path(__file__).resolve().parents[1]
REPORT_PATH=Path('docs/phan_3_to_hop_mon_2023_2025.md')
REQUIRED_TABLES={
    'combinations':['combination_summary.csv','combination_deltas.csv','top_thresholds.csv',
                    'participation.csv','cooccurrence.csv','combination_validation.csv','combination_mapping.csv',
                    'combination_membership_validation.csv','membership_count_distribution.csv'],
}


def markdown_table(frame: pd.DataFrame, limit: int | None=None) -> str:
    """Render without an optional tabulate dependency."""
    selected=frame if limit is None else frame.head(limit)
    def value(item,column):
        if pd.isna(item): return '—'
        if isinstance(item,(float,np.floating)):
            digits=3 if ('pearson' in column or 'spearman' in column) else 2
            return f'{item:.{digits}f}'
        return str(item).replace('|','/').replace('\n',' ')
    rows=['| '+' | '.join(map(str,selected.columns))+' |',
          '| '+' | '.join(['---']*len(selected.columns))+' |']
    rows.extend('| '+' | '.join(value(item,column) for item,column in zip(row,selected.columns))+' |'
                for row in selected.itertuples(index=False,name=None))
    return '\n'.join(rows)


def write_notebooks(root: Path=ROOT) -> list[Path]:
    """One part 3 notebook, with an explicit opt-in to rerun the pipeline."""
    import nbformat
    outputs=[]
    for part,folder,title,tables in [
        (3,'combinations','Tổ hợp môn, cơ cấu môn và ngưỡng top',REQUIRED_TABLES['combinations']),
    ]:
        cells=[nbformat.v4.new_markdown_cell(
            f'# Phần {part}: {title}\n\n**2023 — CT2006** so với **2025 — CT2018**. '
            'Dataset 2025 chỉ gồm CT2018 theo xác nhận của người dùng. '
            'Điểm thiếu không được điền; điểm 0 giữ nguyên.\n\n'
            'Notebook đọc đầu ra đã kiểm chứng. Đặt `RERUN=True` để chạy lại bằng `--rerun`. '
            'Chạy lại chỉ thực hiện phần 3 và các bằng chứng bổ trợ.'),
            nbformat.v4.new_code_cell(
                'from pathlib import Path\nimport sys, subprocess, json\nimport pandas as pd\n'
                'from IPython.display import display, Image, Markdown\n'
                'ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src/score_data.py").exists())\n'
                'if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))\n'
                'RERUN = False\n'
                'if RERUN:\n    subprocess.run([sys.executable, "-m", "src.run_part3", "--rerun"], cwd=ROOT, check=True)\n'
                'from src.run_part3 import validate_outputs\n'
                'print(validate_outputs(ROOT))\n'
                'metadata = json.loads((ROOT / "outputs/part3_run.json").read_text(encoding="utf-8"))\n'
                'display(pd.DataFrame(metadata["inputs"])[["cohort", "rows", "rows_with_any_score", "sha256"]])')]
        for table in tables:
            cells += [nbformat.v4.new_markdown_cell('## '+table),
                      nbformat.v4.new_code_cell(
                          f'display(pd.read_csv(ROOT / "outputs/{folder}/{table}"))')]
        cells += [nbformat.v4.new_markdown_cell('## Biểu đồ và báo cáo\nHình được đọc từ cùng bộ kết quả với các bảng trên.'),
                  nbformat.v4.new_code_cell(
                      f'figures = sorted((ROOT / "outputs/{folder}").rglob("*.png"))\n'
                      'print(f"Có {len(figures)} hình; danh sách đầy đủ:")\n'
                      'display(pd.DataFrame({"figure": [str(p.relative_to(ROOT)) for p in figures]}))\n'
                      'priority = {"top_threshold_comparison.png": 0, "participation.png": 1}\n'
                      'preview = sorted(figures, key=lambda p: (priority.get(p.name, 2 if "hist_ecdf" in p.name else 3), p.name))\n'
                      'for figure in preview[:6]:\n    display(Image(filename=str(figure), width=900))\n'
                      +(f'display(Markdown((ROOT / "{REPORT_PATH.as_posix()}").read_text(encoding="utf-8")))'
                        if part==3 else ''))]
        notebook=nbformat.v4.new_notebook(cells=cells,metadata={
            'kernelspec':{'display_name':'Python 3 (project .venv)','language':'python','name':'python3'},
            'language_info':{'name':'python','version':platform.python_version()}})
        target=root/'notebooks'/folder/'analysis.ipynb'
        target.parent.mkdir(parents=True,exist_ok=True)
        nbformat.write(notebook,target)
        outputs.append(target)
    return outputs


def validate_outputs(root: Path=ROOT) -> dict:
    """Validate part 3 cross-table counts, cutoffs and stored totals."""
    count=0
    for folder,names in REQUIRED_TABLES.items():
        for name in names:
            path=root/'outputs'/folder/name
            if not path.exists(): raise FileNotFoundError(path)
            table=pd.read_csv(path)
            if table.empty: raise ValueError(f'Empty output: {path}')
            for col in table:
                if col.startswith('pct_') or col.endswith('_pct') or col in ['percent','percent_all_rows']:
                    series=pd.to_numeric(table[col],errors='coerce').dropna()
                    if not series.between(0,100).all(): raise ValueError(f'Invalid percent {path}:{col}')
            count+=1
    def require(condition,message):
        if not condition: raise ValueError(message)
    summary=_csv(root,'combinations','combination_summary.csv')
    expected={(year,code) for year in COHORT_LABELS for code in ALL_COMBINATIONS}
    require(set(zip(summary.year,summary.combination))==expected and len(summary)==2*len(ALL_COMBINATIONS),'Incomplete combination coverage')
    for row in summary.itertuples():
        require(row.cohort==COHORT_LABELS[row.year],'Incorrect cohort label')
        require(0<=row.n<=row.denominator<=row.denominator_all_rows,'Invalid combination denominator')
        require(0<=row.p80<=row.p90<=row.p95<=30,'Invalid combination quantiles')
        require(0<=row.mean<=30,'Invalid mean')
    indexed=summary.set_index(['year','combination'])
    top=_csv(root,'combinations','top_thresholds.csv')
    require(len(top)==4*len(ALL_COMBINATIONS) and not top.duplicated(['year','combination','quantile']).any(),'Incomplete top thresholds')
    for row in top.itertuples():
        require(row.quantile in [.8,.9],'Unexpected top quantile')
        source=indexed.loc[(row.year,row.combination)]
        require(row.n==source.n,'Threshold n differs from combination n')
        require(np.isclose(row.threshold,source['p80' if row.quantile==.8 else 'p90']),'Threshold differs from summary')
        require(row.n_at+row.n_gt==row.n_ge and 0<=row.n_gt<=row.n_ge<=row.n,'Invalid threshold tie counts')
        require(np.isclose(row.pct_ge,100*row.n_ge/row.n),'Invalid threshold percent')
    validation=_csv(root,'combinations','combination_validation.csv')
    require(set(zip(validation.year,validation.combination))==expected and len(validation)==48,'Incomplete stored-total coverage')
    require(not validation.status.eq('mismatch').any(),'Stored combination totals mismatch')
    require(not validation.b00_count_status.eq('mismatch').any(),'Audited B00 count mismatch')
    require(validation.loc[validation.year.eq(2025),'status'].eq('match').all(),'Not all 24 supplied totals were validated')
    mapping=_csv(root,'combinations','combination_mapping.csv')
    require(set(zip(mapping.year,mapping.combination))==expected and len(mapping)==48,'Incomplete subject mapping')
    changed={code for code,subjects in ALL_COMBINATIONS.items() if 'economics_law' in subjects}
    require(set(mapping.loc[mapping.comparison_class.eq('changed_subject_content'),'combination'])==changed,'Changed-content flags missing')
    membership=_csv(root,'combinations','combination_membership_validation.csv')
    require(len(membership)==48 and set(zip(membership.year,membership.combination))==expected,'Incomplete membership validation')
    require(membership.loc[membership.year.eq(2025),'status'].eq('match').all(),'Source multi-label membership mismatch')
    degree=_csv(root,'combinations','membership_count_distribution.csv')
    for year in COHORT_LABELS:
        rows=degree[degree.year.eq(year)]
        require(rows.n_students.sum()==indexed.loc[(year,'A00'),'denominator_all_rows'],'Membership distribution loses students')
        require((rows.n_eligible_combinations*rows.n_students).sum()==summary.loc[summary.year.eq(year),'n'].sum(),'Membership totals do not reconcile')
    participation=_csv(root,'combinations','participation.csv')
    require((participation.n<=participation.denominator).all(),'Participation count exceeds denominator')
    require(np.allclose(participation.percent,100*participation.n/participation.denominator),'Participation percent mismatch')
    return {'checked_csv_files':count,'cohorts':list(COHORT_LABELS.values()),
            'status':'part 3 coverage, counts, ties and stored totals verified'}


def _csv(root: Path,folder: str,name: str) -> pd.DataFrame:
    return pd.read_csv(root/'outputs'/folder/name)


def _combination_mapping_table(root: Path) -> str:
    mapping=_csv(root,'combinations','combination_mapping.csv')
    old=mapping[mapping.year.eq(2023)].set_index('combination')
    new=mapping[mapping.year.eq(2025)].set_index('combination')
    rows=[{'Tổ hợp':code,'2023 — CT2006':old.loc[code,'subjects'],
           '2025 — CT2018':new.loc[code,'subjects'],
           'Ghi chú':'GDCD / GDKT&PL khác nội dung' if new.loc[code,'comparison_class']=='changed_subject_content'
                     else 'Cùng tên môn; khác đề và cohort'} for code in ALL_COMBINATIONS]
    return markdown_table(pd.DataFrame(rows))


def _combination_findings(root: Path) -> list[str]:
    summary=_csv(root,'combinations','combination_summary.csv').set_index(['year','combination'])
    findings=[]
    for code in ['A00','B00','C00','D01']:
        before,after=summary.loc[(2023,code)],summary.loc[(2025,code)]
        page=list(ALL_COMBINATIONS).index(code)//6+1
        suffix='' if page==1 else f'_page_{page:02d}'
        findings.append(
            f'- **{code}:** 2023 — CT2006 có n={int(before.n):,}, mean={before["mean"]:.2f}, '
            f'median={before["median"]:.2f}, P80={before.p80:.2f}, P90={before.p90:.2f}; '
            f'2025 — CT2018 có n={int(after.n):,}, mean={after["mean"]:.2f}, '
            f'median={after["median"]:.2f}, P80={after.p80:.2f}, P90={after.p90:.2f}. '
            f'Delta mean={after["mean"]-before["mean"]:+.2f} điểm, '
            f'delta P90={after.p90-before.p90:+.2f} điểm. '
            'Trung bình và đuôi trên có thể thay đổi khác hướng; tập người đủ điểm cũng thay đổi. '
            f'[Bằng chứng: phân phối/ECDF](../../outputs/combinations/figures/combination_hist_ecdf{suffix}.png).')
    participation=_csv(root,'combinations','participation_deltas.csv')
    biology=participation.loc[participation.subject.eq('biology')].iloc[0]
    findings.append(
        f'- **Cơ cấu môn có điểm:** Sinh từ {biology.percent_from:.2f}% '
        f'(2023 — CT2006) xuống {biology.percent_to:.2f}% (2025 — CT2018), '
        f'{biology.delta_percent:+.2f} điểm phần trăm trên mẫu số có ít nhất một điểm. '
        'Đọc giảm số người đủ B00 cùng biến động này; chưa coi đây là số nguyện vọng hoặc tác động riêng của chương trình. '
        '[Bằng chứng: bảng tỷ lệ](../../outputs/combinations/participation_deltas.csv).')
    return findings


def write_reports(root: Path=ROOT) -> None:
    """Build the part 3 report; correlation artifacts remain independent."""
    from src.report_explanations import overview, external_review, explain_table, explain_figure, participation_comparison
    sections=['# Phần 3 — Phân tích tổ hợp môn thi THPT 2023 và 2025',
              '**2023 — CT2006** so với **2025 — CT2018**. '
              'Phạm vi: đủ 24 tổ hợp, cơ cấu môn có điểm, ngưỡng top 10%/20% và bằng chứng giải thích biến động điểm.']
    sections += overview(root,markdown_table)
    from src.subject_distribution_evidence import report_section, research_section
    sections += report_section(root,markdown_table)
    sections += research_section(root,markdown_table)
    from src.subject_group_profiles import report_section as profile_report
    sections += profile_report(root,markdown_table)
    sections += external_review(root,markdown_table)
    sections += [
              '## Kiểm chứng dữ liệu và trường hợp B00',
              'Dataset 2025 của nhan có 1.131.136 dòng và 41 cột; CT2018-only theo xác nhận của người dùng. '
              'Audit toàn bộ dữ liệu không phát hiện SBD trùng/thiếu/sai định dạng, điểm ngoài [0,10], '
              'sai tổng hay sai điều kiện đủ điểm ở 24 cột tổ hợp. Có 152 dòng không có điểm môn nào. '
              'Các kiểm tra này xác nhận nhất quán nội bộ; đối chiếu phổ điểm công bố được trình bày ở trên, '
              'chưa xác thực độc lập từng điểm của từng người. '
              '[Chi tiết audit](../outputs/audits/nhan_2025_audit.json).',
              '**B00 đã được tính lại bằng kiểm tra độc lập trong dự án:** 324.554 người (2023) và 44.964 người (2025) '
              'có đủ Toán/Hóa/Sinh, giảm 279.590 người. Năm 2023 có 324.571 người có cả Hóa/Sinh, '
              'trong đó 17 người thiếu Toán. Kết quả 2023 khớp dữ liệu gốc và các bản xử lý tuần 3/4/5; '
              'kết quả 2025 khớp cột diem_B00, không sai khác tổng hay điều kiện có điểm. '
              'Đây là số người đủ điểm tổ hợp, không phải số đăng ký xét tuyển. '
              '[Bằng chứng kiểm chứng B00](../outputs/audits/b00_verification.json).']
    folder='combinations'
    title='Phần 3 — Tổ hợp môn, cơ cấu môn và ngưỡng top'
    lines=[f'## {title}', '', '**2023 — CT2006** so với **2025 — CT2018**.', '',
           'Dataset 2025 đã được người dùng xác nhận chỉ gồm CT2018. '
           'Đơn vị phân tích là điểm cùng một thí sinh trong từng năm; không ghép SBD qua hai năm.', '']
    lines += ['## Câu hỏi và phương pháp',
        'So sánh đủ **24 mã tổ hợp** theo 24 cột diem_* của dataset nhan: '
        + ', '.join(ALL_COMBINATIONS) + '. Anh chỉ lấy mã N1. '
        'Tổng chỉ có khi đủ ba điểm hợp lệ; không điền thiếu, không cộng ưu tiên/nhân hệ số. '
        'Một người có thể thuộc nhiều tổ hợp.', '',
        '**Quy tắc gán đa nhãn đã chốt với người dùng:** mỗi người nằm trong mọi tổ hợp có đủ ba điểm, '
        'giống nhãn của dataset nhan; không chọn tổ hợp cao nhất và không ép thành nhóm độc quyền. '
        'Ví dụ đủ Toán/Văn/Lý/Hóa có thể đồng thời tính A00, C01 và C02. '
        'Số n của một tổ hợp là số người đủ điểm của tổ hợp đó, không phải nguyện vọng đăng ký.', '',
        'Các mã A08/A09/C14/C19/C20/D66/D84 dùng GDCD ở **2023 — CT2006** '
        'và GDKT&PL ở **2025 — CT2018**: so sánh mô tả theo mã được cung cấp, '
        'không khẳng định nội dung môn tương đương. B08 và D08 cùng bộ Toán/Sinh/Anh trong dataset; '
        'giữ cả hai mã để khớp nguồn, nhưng không coi là hai tập người độc lập. '
        'Đây là bộ mã của file nguồn, không phải xác nhận mã tuyển sinh dùng thống nhất tại mọi trường.', '',
        '## Phạm vi và công thức cả 24 tổ hợp',_combination_mapping_table(root),'',
        'P80/P90 theo inverse empirical CDF: sắp tăng dần, lấy phần tử ceil(p×n), chỉ số từ 1. '
        'Top 20% dùng P80, top 10% dùng P90. Đồng hạng làm tỷ lệ đạt ngưỡng có thể lớn hơn mức mục tiêu.', '',
        '## Phát hiện chính',*_combination_findings(root),'',
        '## Tổng điểm: đủ 24 tổ hợp × 2 cohort',
        markdown_table(_csv(root,folder,'combination_summary.csv')[['cohort','combination','n','mean','median','sd','iqr','p80','p90']]), '',
        '## Chênh lệch 2025 — CT2018 trừ 2023 — CT2006',
        markdown_table(_csv(root,folder,'combination_deltas.csv')[['combination','delta_n','delta_mean','delta_median','delta_p80','delta_p90','comparison_class']]), '',
        '## Ngưỡng nhóm cao nhất và đồng hạng',
        markdown_table(_csv(root,folder,'top_thresholds.csv')[['cohort','combination','target_top_percent','n','threshold','n_at','pct_gt','pct_ge']]), '',
        '## Cơ cấu môn có điểm',
        'Mẫu số chính là số bản ghi có ít nhất một điểm thi quan sát được. '
        'Mẫu số phụ là toàn bộ dòng dataset. Ngoại ngữ mọi mã và Anh được phân biệt; '
        'Anh không được đếm như môn thi thứ hai cạnh Ngoại ngữ. '
        'Bảng mô tả có điểm; thiếu điểm chưa xác định riêng nguyên nhân không đăng ký, miễn, vắng hoặc thiếu nguồn.',
        markdown_table(_csv(root,folder,'participation.csv')[['cohort','subject_label','n','denominator','percent','comparability','counts_as_separate_exam']]), '',
        '### Tăng/giảm số người và tỷ lệ có điểm theo từng môn',
        markdown_table(participation_comparison(root)),'',
        '## Kiểm chứng tổng điểm có sẵn',markdown_table(_csv(root,folder,'combination_validation.csv')[['cohort','combination','n_recomputed','n_stored','n_missingness_mismatch','n_sum_mismatch','status']]), '',
        '## Kiểm chứng cách gán nhiều tổ hợp giống nhan',
        markdown_table(_csv(root,folder,'combination_membership_validation.csv')[['cohort','combination','n_eligible','n_source_label','n_disagreement','status']]), '',
        'Phân bố số tổ hợp hợp lệ trên mỗi người (kể cả người không đủ tổ hợp nào):',
        markdown_table(_csv(root,folder,'membership_count_distribution.csv')[['cohort','n_eligible_combinations','n_students']]),'',
        'Bảng cooccurrence.csv đếm các cặp môn tự chọn cùng có điểm. '
        'GDCD của 2023 — CT2006 và GDKT&PL của 2025 — CT2018 không coi là môn bất biến; '
        'Tin/Công nghệ không có mốc tương ứng ở 2023 — CT2006.']
    lines=[explain_table(root,folder,line) if line.startswith('| ') else line for line in lines]
    lines += ['', '## Biểu đồ và diễn giải từng hình', '']
    for image in sorted((root/'outputs'/folder).rglob('*.png')):
        relative=image.relative_to(root).as_posix()
        title,explanation=explain_figure(root,folder,image)
        lines += [f'### {title}', f'![{title}](../../{relative})', '**Diễn giải hình:** '+explanation, '']
    lines += ['## Giới hạn diễn giải',
        'Kết quả mô tả thay đổi trong bối cảnh chuyển chương trình, định dạng đề và cơ chế chọn môn. '
        'Không tách được tác động riêng của chương trình/cách chấm/độ khó đề/nhóm thí sinh chỉ từ hai năm. '
        'Ngưỡng phân vị không phải điểm chuẩn trúng tuyển. '
        'Nguồn xác nhận CT2018 là người dùng; phổ từng môn 2025 đã đối chiếu thống kê công bố nếu có mục kiểm chứng ở trên. '
        'Sự khớp ở mức tổng hợp chưa xác thực mọi điểm và mọi ghép môn theo thí sinh.', '',
        '## Tái lập',
        'Chạy từ gốc dự án: `python -m src.run_part3 --rerun`. '
        'Metadata và hash nguồn: `outputs/part3_run.json`. '
        'Notebook tương ứng: `notebooks/'+folder+'/analysis.ipynb`.']
    # The main report lives one directory below the repository root.
    sections.extend(('#'+line if index>0 and line.startswith('#') else line).replace('../../outputs/','../outputs/')
                    for index,line in enumerate(lines))
    target=root/REPORT_PATH
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('\n\n'.join(sections)+'\n',encoding='utf-8')


def run(data2023: Path,data2025: Path,root: Path=ROOT) -> dict:
    from src.analyze_combinations import analyze_combinations
    root.mkdir(parents=True,exist_ok=True)
    cohorts={}; audits=[]
    for year,path in [(2023,data2023),(2025,data2025)]:
        print(f'Reading {COHORT_LABELS[year]}: {path}',flush=True)
        cohorts[year],audit=load_scores(path,year); audits.append(audit)
    print('Part 3: combinations, observed participation, empirical top thresholds',flush=True)
    combination_result=analyze_combinations(cohorts,root/'outputs/combinations')
    from src.subject_distribution_evidence import generate
    generate(cohorts,root,audits)
    result={
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'part 3 only',
        'inputs':audits,'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},
        'cohort_labels':COHORT_LABELS,'seed':42,
        'combination_result':combination_result,
    }
    (root/'outputs').mkdir(exist_ok=True)
    (root/'outputs/part3_run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    write_reports(root); write_notebooks(root)
    result['verification']=validate_outputs(root)
    files=[]
    for folder in ['outputs/combinations','outputs/audits']:
        for path in sorted((root/folder).rglob('*')):
            if path.is_file(): files.append({'path':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':file_sha256(path)})
    (root/'outputs/part3_manifest.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
    (root/'outputs/part3_run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(result['verification'],ensure_ascii=False),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rerun',action='store_true',help='Recompute part 3 from immutable inputs')
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--data2023',type=Path,default=ROOT/'data/raw/original.csv')
    parser.add_argument('--data2025',type=Path,default=ROOT/'data/dataset_diem_thi_thpt_2025.csv')
    parser.add_argument('--output-root',type=Path,default=ROOT)
    args=parser.parse_args()
    if args.verify_only:
        print(validate_outputs(args.output_root)); return
    if args.rerun or not (args.output_root/'outputs/part3_run.json').exists():
        run(args.data2023,args.data2025,args.output_root)
    else:
        print(validate_outputs(args.output_root))
        write_reports(args.output_root)


if __name__=='__main__': main()
