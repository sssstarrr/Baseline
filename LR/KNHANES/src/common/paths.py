from __future__ import annotations

from pathlib import Path

"""项目内共享路径常量。"""

# KNHANES 项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
LR_OUTPUT_DIR = OUTPUTS_DIR / 'lr'
DOCS_DIR = PROJECT_ROOT / 'docs'
