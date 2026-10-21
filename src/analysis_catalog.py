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
