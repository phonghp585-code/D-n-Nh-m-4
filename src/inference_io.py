"""Shared provenance and output contracts; no copies of source score datasets."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib, inspect, json, platform, re
import importlib.metadata
import numpy as np
import pandas as pd
from src.score_data import load_scores,file_sha256

ROOT=Path(__file__).resolve().parents[1]
INPUTS={2023:'data/raw/original.csv',2025:'data/dataset_diem_thi_thpt_2025.csv'}

def load_inputs(root=ROOT):
    frames={};audits=[]
    for year,rel in INPUTS.items():
        frames[year],audit=load_scores(root/rel,year);audits.append(audit)
    return frames,audits

def fingerprint(functions):
    return hashlib.sha256('\n'.join(inspect.getsource(f) for f in functions).encode()).hexdigest()

def write_tables(folder:Path,tables:dict[str,pd.DataFrame]):
    folder.mkdir(parents=True,exist_ok=True)
    for name,table in tables.items():table.to_csv(folder/(name+'.csv'),index=False,encoding='utf-8-sig')

def make_metadata(root,folder,audits,functions,config):
    files=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix in ('.csv','.png'))
    metadata=dict(schema_version=1,created_at_utc=datetime.now(timezone.utc).isoformat(),
        inputs=audits,config=config,numeric_fingerprint=fingerprint(functions),
        environment=dict(python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','matplotlib']}),
        policies=dict(scores='finite [0,10]; zero retained; no imputation',direction='2025-2023',
            sampling='Observed exam scores; no causal or equated-ability interpretation',
            inference='Independent-observation model, approximate uncertainty; possible cross-year retakers not identified'),
        artifact_hashes={p.relative_to(root).as_posix():file_sha256(p) for p in files})
    (folder/'run_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return metadata

def validate_metadata(root,folder,functions,config):
    metadata=json.loads((folder/'run_metadata.json').read_text(encoding='utf-8'))
    if metadata['schema_version']!=1 or metadata['config']!=config or metadata['numeric_fingerprint']!=fingerprint(functions):
        raise ValueError('Schema/code/config changed; run --rerun')
    for audit in metadata['inputs']:
        if file_sha256(root/INPUTS[audit['year']])!=audit['sha256']:raise ValueError('Source changed; run --rerun')
    if not metadata['artifact_hashes']:raise ValueError('No validated artifacts')
    for rel,expected in metadata['artifact_hashes'].items():
        if not (root/rel).is_file() or file_sha256(root/rel)!=expected:raise ValueError(f'Artifact changed/missing: {rel}')
    return metadata

def number(x,digits=2):
    if x is None or pd.isna(x):return '—'
    if isinstance(x,(int,np.integer)):return f'{x:,}'.replace(',','.')
    if isinstance(x,(float,np.floating)):
        if not np.isfinite(x):return '—'
        return f'{x:,.{digits}f}'.replace(',','_').replace('.',',').replace('_','.')
    return str(x).replace('|','/').replace('\n',' ')

def ptext(x):
    if x is None or pd.isna(x):return 'Không áp dụng'
    if x==0:return '≈0 (dưới độ phân giải số)'
    return f'{x:.2e}' if x<.001 else number(x,4)

def md_table(table,headers=None,digits=2):
    table=table.copy()
    if headers:table.columns=headers
    for column in table:
        if str(column).lower() in ('year','năm'):
            table[column]=table[column].map(lambda x:str(int(x)) if pd.notna(x) else '—')
    rows=['| '+' | '.join(map(str,table.columns))+' |','| '+' | '.join(['---']*len(table.columns))+' |']
    rows += ['| '+' | '.join(number(x,digits) for x in row)+' |' for row in table.itertuples(index=False,name=None)]
    return '\n'.join(rows)

def image_block(rel,alt,explanation):
    return f'![{alt}](../{rel})\n\n**Diễn giải hình:** {explanation}\n'

def validate_report_links(root,path):
    text=path.read_text(encoding='utf-8');count=0
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if re.match(r'https?://',target) or target.startswith('#'):continue
        if not (path.parent/target.split('#')[0]).exists():raise FileNotFoundError(target)
        count+=1
    for forbidden in ['TBD','TODO','FIXME','Đang cập nhật']:
        if forbidden in text:raise ValueError(f'Placeholder: {forbidden}')
    return count

def build_reading_notebook(root,path,title,report,metadata,tables,rerun_command):
    import nbformat
    cells=[nbformat.v4.new_markdown_cell(f'# {title}\n\nNotebook đọc đúng bảng và báo cáo đã sinh. Raw không bị sao chép; bật RERUN để chạy lại.'),
        nbformat.v4.new_code_cell('from pathlib import Path\nimport sys, json, subprocess\nimport pandas as pd\nfrom IPython.display import display, Markdown\nROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src/score_data.py").exists())\nif str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))\nRERUN = False\n'+f'if RERUN: subprocess.run([sys.executable, "-m", "{rerun_command}", "--rerun"], cwd=ROOT, check=True)\n'+f'meta = json.loads((ROOT / "{metadata}").read_text(encoding="utf-8"))\ndisplay(pd.DataFrame(meta["inputs"])[["year","rows","sha256"]])')]
    for rel in tables:cells.append(nbformat.v4.new_code_cell(f'display(pd.read_csv(ROOT / "{rel}"))'))
    cells.append(nbformat.v4.new_code_cell(f'display(Markdown((ROOT / "{report}").read_text(encoding="utf-8")))'))
    notebook=nbformat.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (project .venv)','language':'python','name':'python3'},'language_info':{'name':'python','version':platform.python_version()}})
    target=root/path;target.parent.mkdir(parents=True,exist_ok=True);nbformat.write(notebook,target)
