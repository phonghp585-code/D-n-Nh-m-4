"""Explicit, audited score schema for 2023 — CT2006 / 2025 — CT2018."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

COHORT_LABELS = {2023: '2023 — CT2006', 2025: '2025 — CT2018'}
COMMON_SUBJECTS = ('math','literature','english','physics','chemistry','biology','history','geography')
SUBJECT_LABELS = {
    'math':'Toán', 'literature':'Ngữ văn', 'english':'Tiếng Anh',
    'physics':'Vật lý', 'chemistry':'Hóa học', 'biology':'Sinh học',
    'history':'Lịch sử', 'geography':'Địa lý', 'civics':'GDCD',
    'economics_law':'GDKT&PL', 'informatics':'Tin học',
    'technology':'Công nghệ', 'foreign_language':'Ngoại ngữ (mọi mã)',
}
COMBINATIONS = {
    'A00':('math','physics','chemistry'),
    'A01':('math','physics','english'),
    'B00':('math','chemistry','biology'),
    'C00':('literature','history','geography'),
    'D01':('math','literature','english'),
}
# Exact set/order of the 24 diem_* columns in the supplied nhan CSV.
# Names containing economics_law use civics for the CT2006 descriptive baseline.
ALL_COMBINATIONS = {
    'A00':('math','physics','chemistry'),
    'A01':('math','physics','english'),
    'A02':('math','physics','biology'),
    'A08':('math','history','economics_law'),
    'A09':('math','geography','economics_law'),
    'B00':('math','chemistry','biology'),
    'B08':('math','biology','english'),
    'C00':('literature','history','geography'),
    'C01':('literature','math','physics'),
    'C02':('literature','math','chemistry'),
    'C03':('literature','math','history'),
    'C04':('literature','math','geography'),
    'C14':('literature','math','economics_law'),
    'C19':('literature','history','economics_law'),
    'C20':('literature','geography','economics_law'),
    'D01':('math','literature','english'),
    'D07':('math','chemistry','english'),
    'D08':('math','biology','english'),
    'D09':('math','history','english'),
    'D10':('math','geography','english'),
    'D14':('literature','history','english'),
    'D15':('literature','geography','english'),
    'D66':('literature','economics_law','english'),
    'D84':('math','economics_law','english'),
}


def combination_subjects(code: str, year: int) -> tuple[str, ...]:
    """Resolve dataset-code subjects without merging civics and economics-law."""
    if year not in COHORT_LABELS:
        raise ValueError(f'Unsupported cohort year: {year}')
    return tuple('civics' if year==2023 and key=='economics_law' else key
                 for key in ALL_COMBINATIONS[code])


def combination_metadata(code: str, year: int) -> dict:
    subjects=combination_subjects(code,year)
    changed='economics_law' in ALL_COMBINATIONS[code]
    equivalent=[name for name,keys in ALL_COMBINATIONS.items()
                if name!=code and set(keys)==set(ALL_COMBINATIONS[code])]
    return {
        'subjects':' + '.join(SUBJECT_LABELS[key] for key in subjects),
        'comparison_class':'changed_subject_content' if changed else 'same_named_subjects',
        'comparison_note':('GDCD (2023 — CT2006) / GDKT&PL (2025 — CT2018): '
                           'descriptive comparison only; content is not equivalent' if changed else
                           'Same named subjects; exams and selected cohorts still differ'),
        'same_subjects_as':', '.join(equivalent),
    }
RAW_COLUMNS = {
    2023:{'Student ID':'student_id','Mathematics':'math','Literature':'literature',
          'Foreign language':'foreign_language','Foreign language code':'language_code',
          'Physics':'physics','Chemistry':'chemistry','Biology':'biology',
          'History':'history','Geography':'geography','Civic education':'civics'},
    2025:{'sbd':'student_id','toan':'math','ngu_van':'literature',
          'ngoai_ngu':'foreign_language','ma_ngoai_ngu':'language_code',
          'vat_li':'physics','hoa_hoc':'chemistry','sinh_hoc':'biology',
          'lich_su':'history','dia_li':'geography','gdktpl':'economics_law',
          'tin_hoc':'informatics','cong_nghe':'technology'},
}


def valid_numeric(series: pd.Series) -> pd.Series:
    """Keep finite observed scores in [0,10], including zero."""
    numeric = pd.to_numeric(series, errors='coerce').astype(float)
    return numeric.where(np.isfinite(numeric) & numeric.between(0,10))


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load_scores(path: str | Path, year: int) -> tuple[pd.DataFrame, dict]:
    """Read immutable inputs; retain rows and missingness, reject unsafe IDs."""
    if year not in RAW_COLUMNS:
        raise ValueError(f'Unsupported cohort year: {year}')
    path=Path(path)
    with path.open('rb') as stream:
        if stream.read(100).startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError(f'Git LFS pointer, not data: {path}; run git lfs pull')
    if path.suffix.lower()=='.parquet':
        raw=pd.read_parquet(path)
    else:
        raw=pd.read_csv(path,dtype={'Student ID':'string','sbd':'string',
                                   'Foreign language code':'string','ma_ngoai_ngu':'string'},
                        low_memory=False)
    renamed=raw.rename(columns=RAW_COLUMNS[year])
    if 'student_id' not in renamed:
        raise ValueError('Missing student identifier column')
    ids=renamed.student_id.astype('string').str.strip()
    malformed=~ids.str.fullmatch(r'[0-9]{8}',na=False)
    if malformed.any():
        raise ValueError(f'{COHORT_LABELS[year]}: {int(malformed.sum())} malformed student IDs')
    if ids.duplicated().any():
        raise ValueError(f'{COHORT_LABELS[year]}: duplicate student IDs; resolve source first')
    frame=pd.DataFrame({'student_id':ids,'year':year,'cohort':COHORT_LABELS[year]},index=raw.index)
    invalid={}
    for key in SUBJECT_LABELS:
        if key=='english':
            continue
        original=renamed[key] if key in renamed else pd.Series(np.nan,index=raw.index)
        numeric=valid_numeric(original)
        invalid[key]=int((original.notna() & numeric.isna()).sum())
        frame[key]=numeric
    codes=(renamed.language_code.astype('string').str.strip().str.upper()
           if 'language_code' in renamed else pd.Series(pd.NA,index=raw.index,dtype='string'))
    frame['language_code']=codes
    frame['english']=frame.foreign_language.where(codes.eq('N1').fillna(False))
    if year==2025 and 'tieng_anh' in raw:
        supplied=valid_numeric(raw.tieng_anh)
        mismatch=(supplied.notna()!=frame.english.notna()) | (
            supplied.notna() & frame.english.notna() & ~np.isclose(supplied,frame.english,atol=1e-8,equal_nan=True))
        if mismatch.any():
            raise ValueError(f'English column disagrees with foreign-language code N1: {int(mismatch.sum())} rows')
    for code in ALL_COMBINATIONS:
        if 'diem_'+code in raw:
            # Keep parsing failures visible to the stored-total audit.
            frame['stored_'+code]=raw['diem_'+code]
    if 'to_hop_du_thi' in raw:
        frame['source_combinations']=raw['to_hop_du_thi'].astype('string')
    exam_columns=[key for key in SUBJECT_LABELS if key!='english']
    any_score=frame[exam_columns].notna().any(axis=1)
    audit={
        'source':str(path.resolve()),'sha256':file_sha256(path),
        'year':year,'cohort':COHORT_LABELS[year],'rows':len(frame),
        'rows_with_any_score':int(any_score.sum()),'rows_without_scores':int((~any_score).sum()),
        'invalid_scores':invalid,'duplicate_ids':0,'malformed_ids':0,
        'curriculum_confirmation':('user-confirmed CT2018-only' if year==2025 else '2023 — CT2006'),
        'score_policy':'finite [0,10], zero retained, invalid -> missing with counts; no imputation',
        'participation_policy':'observed scores, not confirmed exam registration/admission preferences',
        'available_combination_codes':[col[5:] for col in raw if col.startswith('diem_')],
    }
    return frame,audit
