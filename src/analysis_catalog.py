"""One catalog for observed subjects; language aliases never duplicate observations."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from src.score_data import RAW_COLUMNS, SUBJECT_LABELS

LANGUAGES = {'N1':'Tiếng Anh','N2':'Tiếng Nga','N3':'Tiếng Pháp','N4':'Tiếng Trung',
             'N5':'Tiếng Đức','N6':'Tiếng Nhật','N7':'Tiếng Hàn'}
SUBJECT_ORDER = ['math','literature','physics','chemistry','biology','history','geography',
                 'civics','economics_law','informatics','technology']

def label(subject_id: str) -> str:
    if subject_id.startswith('foreign_language:'):
        code=subject_id.split(':',1)[1]
        return f'{LANGUAGES.get(code,"Ngoại ngữ chưa ánh xạ")} ({code})'
    return SUBJECT_LABELS.get(subject_id,subject_id)

def subject_values(frame: pd.DataFrame, subject_id: str) -> pd.Series:
    if subject_id=='english': subject_id='foreign_language:N1'
    if subject_id.startswith('foreign_language:'):
        code=subject_id.split(':',1)[1]
        values=frame.get('foreign_language',pd.Series(np.nan,index=frame.index))
        codes=frame.get('language_code',pd.Series(pd.NA,index=frame.index,dtype='string'))
        return values.where(codes.eq(code).fillna(False))
    return frame.get(subject_id,pd.Series(np.nan,index=frame.index,dtype=float))

def subject_catalog(frames: dict[int,pd.DataFrame]) -> pd.DataFrame:
    rows=[]
    for year,frame in sorted(frames.items()):
        inverse={v:k for k,v in RAW_COLUMNS[year].items()}
        ids=[k for k in SUBJECT_ORDER if k in frame and frame[k].notna().any()]
        if 'foreign_language' in frame and 'language_code' in frame:
            codes=sorted(frame.loc[frame.foreign_language.notna(),'language_code'].dropna().unique())
            ids += ['foreign_language:'+str(code) for code in codes]
        for sid in ids:
            code=sid.split(':',1)[1] if ':' in sid else ''
            n=int(subject_values(frame,sid).notna().sum())
            rows.append(dict(year=year,subject_id=sid,label=label(sid),
                source_column=inverse.get('foreign_language' if code else sid,sid),
                language_code=code,n_observed=n,status='observed' if not code or code in LANGUAGES else 'unknown_language_code'))
    return pd.DataFrame(rows,columns=['year','subject_id','label','source_column','language_code','n_observed','status'])

def combination_scores(frame,subjects):
    # Decimal summation noise is canonicalized at 1e-10 points, never to a score grid.
    return pd.concat([subject_values(frame,s) for s in subjects],axis=1).sum(axis=1,min_count=len(subjects)).round(10)

def combination_catalog(frames,source_codes):
    from src.score_data import ALL_COMBINATIONS,combination_subjects
    rows=[];issues=[]
    def normalize(keys):return tuple(sorted('foreign_language:N1' if s=='english' else s for s in keys))
    first={}
    for code,keys in ALL_COMBINATIONS.items():first.setdefault(normalize(keys),code)
    codes=sorted(set(ALL_COMBINATIONS)|{c for cs in source_codes.values() for c in cs})
    for year,frame in sorted(frames.items()):
        for code in codes:
            if code not in ALL_COMBINATIONS:
                issues.append(dict(year=year,code=code,status='unknown_code',reason='Không có mapping được kiểm chứng; không đoán.'));continue
            logical=normalize(ALL_COMBINATIONS[code]);subjects=normalize(combination_subjects(code,year));total=combination_scores(frame,subjects);n=int(total.notna().sum())
            mismatch=0
            if 'stored_'+code in frame:
                stored=pd.to_numeric(frame['stored_'+code],errors='coerce');mask=stored.notna()&total.notna()
                mismatch=int(((stored.notna()!=total.notna())|(mask&~np.isclose(stored,total,atol=1e-8,rtol=0,equal_nan=True))).sum())
                if mismatch:issues.append(dict(year=year,code=code,status='stored_mismatch',reason=f'{mismatch} tổng/thiếu không khớp'))
            rows.append(dict(year=year,code=code,canonical_id='|'.join(logical),alias_of='' if first[logical]==code else first[logical],
                subjects=json.dumps(subjects),n_complete=n,coverage=n/len(frame),comparison_class='changed_subject_content' if 'economics_law' in logical else 'same_named_subjects',
                status='stored_mismatch' if mismatch else 'observed' if n else 'no_complete_scores',reason='',stored_mismatches=mismatch))
    return pd.DataFrame(rows),pd.DataFrame(issues,columns=['year','code','status','reason'])
