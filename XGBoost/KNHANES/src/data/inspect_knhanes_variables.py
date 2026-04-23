from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.common.paths import RAW_DATA_DIR

# 收集年度原始文件，兼容文件名大小写差异。
ALL_FILES = sorted({*RAW_DATA_DIR.glob('HN*_all.sav'), *RAW_DATA_DIR.glob('hn*_all.sav')}, key=lambda p: p.name.lower())

INSPECT_VARS = [
    'id',
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
    'OA_H_scale',
    'OA_K_scale',
    'OA_L_scale',
    'OA_KH',
    'LQ_VAS',
]

# KNHANES 中用于表示缺失/未知的特殊数值编码。
MISSING_CODES = {8, 9, 88, 99, 888, 999, 8888, 9999}


def clean_series(series: pd.Series) -> pd.Series:
    """将 KNHANES 缺失哨兵编码转换为数值列中的 NA。"""
    if pd.api.types.is_numeric_dtype(series):
        return series.mask(series.isin(MISSING_CODES))
    return series


def inspect_file(path: Path) -> None:
    """输出单个 SAV 文件中目标变量的标签和取值分布。"""
    print(f'\n===== {path.name} =====')
    _, meta = pyreadstat.read_sav(path, metadataonly=True)
    available = [col for col in INSPECT_VARS if col in meta.column_names]
    print('available_columns:', available)

    for col in available:
        label = meta.column_names_to_labels.get(col)
        print(f'  {col}: {label!r}')

    df, _ = pyreadstat.read_sav(path, usecols=available)
    for col in available:
        series = clean_series(df[col])
        print(f'\n[{col}] missing={int(series.isna().sum())} non_missing={int(series.notna().sum())}')
        counts = series.value_counts(dropna=False).head(15)
        print(counts.to_string())


if __name__ == '__main__':
    if not ALL_FILES:
        raise SystemExit(f'No HN*_all.sav files found under {RAW_DATA_DIR}')

    print('Detected files:')
    for file in ALL_FILES:
        print(' -', file.name)

    for file in ALL_FILES:
        inspect_file(file)

    print('\nAlias note: raw SAV names like OA_K_SCA / OA_L_SCA are parsed by pyreadstat as OA_K_scale / OA_L_scale.')
