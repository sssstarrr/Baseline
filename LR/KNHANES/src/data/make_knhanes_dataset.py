from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.common.paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

ALL_FILES = sorted({*RAW_DATA_DIR.glob('HN*_all.sav'), *RAW_DATA_DIR.glob('hn*_all.sav')}, key=lambda p: p.name.lower())
OUTPUT_CSV = PROCESSED_DATA_DIR / 'knhanes_2010_2012_knee_oa_dataset.csv'

FEATURE_COLUMNS = [
    'id',
    'ID',
    'year',
    'age',
    'sex',
    'incm',
    'ho_incm',
    'edu',
    'occp',
    'HE_BMI',
    'HE_HP',
    'HE_DM',
    'HE_hCHOL',
    'HE_hTG',
    'HE_mens',
    'OA_K_scale',
    'OA_KH',
    'LQ_VAS',
]

MISSING_CODES = {8, 9, 88, 99, 888, 999, 8888, 9999}


def clean_missing_codes(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    numeric_cols = result.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        result[col] = result[col].mask(result[col].isin(MISSING_CODES))
    return result


def read_yearly_file(path: Path) -> pd.DataFrame:
    _, meta = pyreadstat.read_sav(path, metadataonly=True)
    usecols = [col for col in FEATURE_COLUMNS if col in meta.column_names]
    df, _ = pyreadstat.read_sav(path, usecols=usecols)
    df = clean_missing_codes(df)

    if 'id' not in df.columns and 'ID' in df.columns:
        df = df.rename(columns={'ID': 'id'})

    if 'id' not in df.columns:
        raise ValueError(f'{path.name} is missing id')
    if 'year' not in df.columns:
        raise ValueError(f'{path.name} is missing year')
    if 'OA_KH' not in df.columns:
        raise ValueError(f'{path.name} is missing OA_KH')

    df['source_file'] = path.name
    return df


def main() -> None:
    if not ALL_FILES:
        raise SystemExit(f'No HN*_all.sav files found under {RAW_DATA_DIR}')

    frames = [read_yearly_file(path) for path in ALL_FILES]
    data = pd.concat(frames, ignore_index=True, sort=False)

    if 'LQ_VAS' in data.columns:
        data.loc[data['LQ_VAS'].isin([888, 999]), 'LQ_VAS'] = pd.NA

    data = data.dropna(subset=['OA_KH']).copy()
    data['target_oa_kh'] = data['OA_KH'].astype(int)
    data['target_oa_k_scale_ge2'] = pd.NA
    if 'OA_K_scale' in data.columns:
        data.loc[data['OA_K_scale'].notna(), 'target_oa_k_scale_ge2'] = (
            data.loc[data['OA_K_scale'].notna(), 'OA_K_scale'] >= 2
        ).astype(int)

    ordered_cols = [
        'id',
        'year',
        'source_file',
        'target_oa_kh',
        'target_oa_k_scale_ge2',
        'OA_KH',
        'OA_K_scale',
        'LQ_VAS',
        'age',
        'sex',
        'HE_BMI',
        'HE_HP',
        'HE_DM',
        'HE_hCHOL',
        'HE_hTG',
        'HE_mens',
        'incm',
        'ho_incm',
        'edu',
        'occp',
    ]
    existing_cols = [col for col in ordered_cols if col in data.columns]
    remaining_cols = [col for col in data.columns if col not in existing_cols]
    data = data[existing_cols + remaining_cols]

    data.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    print('saved:', OUTPUT_CSV)
    print('rows:', len(data))
    print('columns:', len(data.columns))
    print('years:', data['year'].value_counts(dropna=False).sort_index().to_dict())
    print('target counts:', data['target_oa_kh'].value_counts(dropna=False).sort_index().to_dict())
    if 'OA_K_scale' in data.columns:
        print('oa_k_scale counts:', data['OA_K_scale'].value_counts(dropna=False).sort_index().to_dict())


if __name__ == '__main__':
    main()
