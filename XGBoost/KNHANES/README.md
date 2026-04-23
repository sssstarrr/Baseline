# KNHANES XGBoost Baseline Project

中文说明请见：[README_zh.md](README_zh.md)

## 1. Project Overview

This project provides a standalone XGBoost baseline for KNHANES 2010–2012 tabular modeling, implemented outside the `LR/` directory while reusing the same data-cleaning and evaluation conventions as the current LR baseline.

Important note:
- The experiment checklist originally recommends a knee-pain prediction task.
- However, the current repository has not yet confirmed the raw KNHANES questionnaire field needed to construct that knee-pain label.
- Therefore, this XGBoost project is intentionally aligned with the **currently implemented LR target**, namely `OA_KH -> target_oa_kh`, so that the XGBoost baseline is directly comparable with the existing LR baseline.

## 2. Scope

This project:
- uses KNHANES 2010–2012
- does not use OAI/MOST
- builds a processed dataset from yearly `HN*_all.sav` files
- trains an XGBoost classifier with a reproducible split and CV protocol
- exports model artifacts, predictions, metrics, and feature importance outputs

## 3. Directory Structure

```text
XGBoost/KNHANES/
├─ README.md
├─ README_zh.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ raw/
│  └─ processed/
├─ src/
│  ├─ common/
│  │  └─ paths.py
│  ├─ data/
│  │  ├─ inspect_knhanes_variables.py
│  │  └─ make_knhanes_dataset.py
│  └─ models/
│     └─ train_xgboost.py
├─ outputs/
│  └─ xgboost/
└─ docs/
   ├─ 可复现实验清单_非OAI_MOST版.md
   ├─ KNHANES_2010_2012_数据集划分规则单.md
   └─ XGBoost_基线实验说明.md
```

## 4. Dependencies

Install from this project root:

```bash
pip install -r requirements.txt
```

Core packages:
- pandas
- pyreadstat
- scikit-learn
- joblib
- xgboost

## 5. Data and Target Definition

Current raw files used by the pipeline:
- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

Current target:
- `target_oa_kh`
- derived from `OA_KH`

Current processed dataset:
- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`

## 6. Modeling Protocol

To remain comparable with the LR baseline, this project uses:
- 80/20 stratified holdout split
- `random_state=42`
- 5-fold cross-validation inside the training set for hyperparameter search
- the same feature family as the current LR baseline

Feature groups:
- numeric: `age`, `HE_BMI`, `LQ_VAS`
- categorical: `year`, `sex`, `incm`, `ho_incm`, `edu`, `occp`, `HE_HP`, `HE_DM`, `HE_mens`

Class imbalance handling:
- stratified splitting
- `scale_pos_weight` search including the automatic negative/positive ratio from the training set

## 7. Outputs

The training script writes:
- `outputs/xgboost/knhanes_xgboost_model.joblib`
- `outputs/xgboost/knhanes_xgboost_test_predictions.csv`
- `outputs/xgboost/knhanes_xgboost_metrics.json`
- `outputs/xgboost/knhanes_xgboost_best_params.json`
- `outputs/xgboost/xgboost_feature_importance.csv`
- `outputs/xgboost/lr_vs_xgboost_comparison.csv`

## 8. Feature Importance

This project exports two feature-importance views:
1. XGBoost built-in gain importance
2. permutation importance on the held-out test set

These are saved together in:
- `outputs/xgboost/xgboost_feature_importance.csv`

## 9. How to Run

From `XGBoost/KNHANES`:

```bash
python src/data/inspect_knhanes_variables.py
python src/data/make_knhanes_dataset.py
python src/models/train_xgboost.py
```

## 10. Comparison with LR Baseline

A comparison table is written to:
- `outputs/xgboost/lr_vs_xgboost_comparison.csv`

The LR reference values are copied from the existing `LR/KNHANES` baseline run so that this project can report an apples-to-apples comparison under the same target and split design.

## 11. Current Limitation

This project is **not yet a literal knee-pain prediction implementation** from the experiment checklist, because the repository still lacks a confirmed raw knee-pain questionnaire field mapping. For now, the project is a faithful XGBoost counterpart to the current OA_KH-based LR baseline.
