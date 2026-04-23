# KNHANES Knee OA Baseline Project

中文说明请见：[README_zh.md](README_zh.md)

## 1. Project Overview

This subproject provides a small, reproducible Python workflow for building a structured analysis dataset from KNHANES SPSS files and training a logistic regression baseline for knee osteoarthritis–related research.

The current implementation focuses on three practical tasks:

1. Inspect key KNHANES variables from yearly `.sav` files.
2. Build an analysis-ready CSV dataset from KNHANES 2010–2012 `HN*_all.sav` tables.
3. Train and evaluate a logistic regression baseline using the processed dataset.

The project is intended to support reproducible baseline experiments, handoff to collaborators, and future extension to additional models or richer KNHANES modules.

## 2. Scope and Current Goal

The current pipeline is designed around the KNHANES 2010–2012 main annual SPSS tables:

- `HN10_all.sav`
- `HN11_all.sav`
- `HN12_all.sav`

The current target variable is built from `OA_KH`, which is used as the primary binary label for the baseline dataset.

Although additional KNHANES raw files are stored in this project, such as `dxa` and `ijmt` files, they are **not yet integrated into the current baseline pipeline**. They are preserved for future extension.

## 3. Directory Structure

```text
LR/KNHANES/
├─ README.md
├─ data/
│  ├─ raw/
│  │  ├─ HN10_all.sav
│  │  ├─ HN11_all.sav
│  │  ├─ HN12_all.sav
│  │  ├─ hn10_dxa.sav
│  │  ├─ hn11_dxa.sav
│  │  ├─ hn10_ijmt.sav
│  │  ├─ hn11_ijmt.sav
│  │  └─ hn12_ijmt.sav
│  └─ processed/
│     └─ knhanes_2010_2012_knee_oa_dataset.csv
├─ src/
│  ├─ common/
│  │  └─ paths.py
│  ├─ data/
│  │  ├─ inspect_knhanes_variables.py
│  │  └─ make_knhanes_dataset.py
│  └─ models/
│     └─ train_lr.py
├─ outputs/
│  └─ lr/
│     ├─ knhanes_lr_model.joblib
│     └─ knhanes_lr_test_predictions.csv
└─ docs/
   ├─ KOA基线模型与LR论文筛选_非OAI_MOST版.md
   └─ 可复现实验清单_非OAI_MOST版.md
```

### Directory responsibilities

- `data/raw/`: immutable raw KNHANES SPSS source files
- `data/processed/`: derived analysis-ready datasets
- `src/common/`: shared project path definitions
- `src/data/`: data inspection and dataset construction scripts
- `src/models/`: model training scripts
- `outputs/`: saved model artifacts and evaluation outputs
- `docs/`: supporting research notes and experiment documents

## 4. Environment and Dependencies

### Recommended environment

- Python 3.10+
- Windows, macOS, or Linux with access to the KNHANES `.sav` files

### Required Python packages

- `pandas`
- `pyreadstat`
- `scikit-learn`
- `joblib`

### Installation

From the repository root:

```bash
pip install pandas pyreadstat scikit-learn joblib
```

## 5. Core Scripts

### 5.1 `src/data/inspect_knhanes_variables.py`

Purpose:
- Inspect key KNHANES variables from yearly `.sav` files.
- Print variable labels, missingness, and value distributions.
- Help verify whether target and predictor variables are available before dataset construction.

Inputs:
- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

Outputs:
- Console summary only

Notes:
- This script is diagnostic and does not modify raw data.
- It includes an alias note for variables such as `OA_K_SCA` and `OA_L_SCA`, which are parsed by `pyreadstat` as `OA_K_scale` and `OA_L_scale`.

### 5.2 `src/data/make_knhanes_dataset.py`

Purpose:
- Build the analysis-ready CSV used by the modeling pipeline.
- Read selected columns from yearly KNHANES `all` tables.
- Standardize inconsistent yearly ID naming (`ID` -> `id`).
- Convert KNHANES missing codes to null values.
- Derive the main target column.

Inputs:
- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

Output:
- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`

Current derived columns:
- `target_oa_kh`
- `target_oa_k_scale_ge2`

Key processing behavior:
- Reads only selected feature columns used by the baseline workflow
- Keeps year information
- Preserves `source_file` for traceability

### 5.3 `src/models/train_lr.py`

Purpose:
- Train and evaluate a logistic regression baseline using the processed dataset.

Input:
- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`

Outputs:
- `outputs/lr/knhanes_lr_model.joblib`
- `outputs/lr/knhanes_lr_test_predictions.csv`

Current modeling setup:
- numeric features: `age`, `HE_BMI`, `LQ_VAS`
- categorical features: `year`, `sex`, `incm`, `ho_incm`, `edu`, `occp`, `HE_HP`, `HE_DM`, `HE_mens`
- target: `target_oa_kh`
- preprocessing: imputation + scaling/one-hot encoding
- model: `LogisticRegression`
- tuning: `GridSearchCV`
- evaluation: ROC-AUC, AP, ACC, F1, classification report

## 6. Input and Output Files

### Raw input files currently used by the main pipeline

- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

### Raw files present but not yet used in the current baseline pipeline

- `data/raw/hn10_dxa.sav`
- `data/raw/hn11_dxa.sav`
- `data/raw/hn10_ijmt.sav`
- `data/raw/hn11_ijmt.sav`
- `data/raw/hn12_ijmt.sav`

These files are retained because they may support future feature expansion, but the current scripts do not consume them.

### Derived data files

- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`
  - analysis-ready dataset generated from the yearly `all` tables

### Model artifacts

- `outputs/lr/knhanes_lr_model.joblib`
  - trained sklearn pipeline

- `outputs/lr/knhanes_lr_test_predictions.csv`
  - test-set prediction results with true labels and predicted probabilities

## 7. How to Run

Run all commands from the `LR/KNHANES` directory.

### Step 1: Inspect variables

```bash
python src/data/inspect_knhanes_variables.py
```

### Step 2: Build the processed dataset

```bash
python src/data/make_knhanes_dataset.py
```

### Step 3: Train the logistic regression baseline

```bash
python src/models/train_lr.py
```

## 8. Data Processing Flow

The current workflow is:

1. Read yearly KNHANES `HN*_all.sav` files from `data/raw/`
2. Select the variables required for the current analysis
3. Normalize year-specific ID naming differences (`ID` vs `id`)
4. Replace KNHANES missing codes such as `8/9/88/99/888/999` with null values
5. Concatenate yearly data into one analysis table
6. Construct target columns such as `target_oa_kh`
7. Save the processed dataset as CSV in `data/processed/`
8. Load the processed CSV into the modeling pipeline
9. Split data into train/test subsets
10. Run preprocessing, hyperparameter search, model fitting, and evaluation
11. Save the trained model and test predictions into `outputs/lr/`

## 9. Reproducibility Notes

- The project uses fixed random seeds in the training pipeline.
- The current scripts are intentionally small and explicit.
- The project separates raw data, processed data, source code, outputs, and documentation to reduce accidental confusion during reuse.
- The current implementation preserves the original core logic of dataset construction and LR training while improving file organization.

## 10. Maintenance Guidelines

### 10.1 Raw data management

- Keep raw SPSS files under `data/raw/`.
- Treat raw files as read-only.
- Do not overwrite or manually edit downloaded KNHANES source files.

### 10.2 Adding new years or new KNHANES modules

If future work needs additional KNHANES years or new modules:

1. place the raw files under `data/raw/`
2. extend `make_knhanes_dataset.py` carefully
3. document the new input files and new variables in this README
4. regenerate the processed dataset and outputs

### 10.3 Adding new models

For future baselines such as Random Forest, XGBoost, or LightGBM:

- add new training scripts under `src/models/`
- write outputs to model-specific subfolders under `outputs/`
- document the new workflow in `README.md`

Suggested future layout:

```text
outputs/
├─ lr/
├─ rf/
├─ xgboost/
└─ lightgbm/
```

### 10.4 Path management

Shared project paths are centralized in:

- `src/common/paths.py`

Any future script should import from this file instead of hardcoding local relative paths.

## 11. Current Limitations

- The current baseline pipeline uses only the yearly `HN*_all.sav` files.
- `dxa` and `ijmt` raw files are stored but not yet merged into the active dataset.
- The current baseline target is `OA_KH`; if the research question changes to knee pain or another phenotype, the dataset name, target definition, and README should be updated accordingly.
- The current implementation focuses on a reproducible LR baseline rather than a full multi-model benchmark suite.

## 12. Recommended Next Steps

Recommended future improvements, if needed:

1. add a `requirements.txt`
2. add additional model baselines
3. version outputs by run date or experiment name
4. add simple validation checks for expected columns and target distributions
5. integrate currently unused `dxa` and `ijmt` sources when the feature design is finalized

## 13. Supporting Documents

Supporting project notes are stored under `docs/`:

- `docs/KOA基线模型与LR论文筛选_非OAI_MOST版.md`
- `docs/可复现实验清单_非OAI_MOST版.md`

These documents provide research context and experiment-planning support, while this README serves as the main operational guide for the code and file structure.
