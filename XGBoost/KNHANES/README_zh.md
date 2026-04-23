# KNHANES XGBoost 基线项目

For the English version, see: [README.md](README.md)

## 1. 项目简介

本项目是在 `LR/` 目录之外单独建立的一套 KNHANES 2010–2012 XGBoost 基线实现，用于在现有 LR 基线基础上增加一个可复现、可直接比较的树模型强基线。

需要特别说明：
- 《可复现实验清单_非OAI_MOST版.md》从研究设计上推荐“膝痛预测任务”；
- 但当前仓库尚未确认用于构建膝痛标签的 KNHANES 原始问卷字段；
- 因此本项目当前先与已实现的 LR 项目保持一致，使用：
  - `OA_KH -> target_oa_kh`
- 这样可以保证 XGBoost 与现有 LR 基线在标签、数据清洗、划分方式和评价指标上直接可比。

## 2. 项目范围

本项目：
- 使用 KNHANES 2010–2012 数据；
- 不使用 OAI/MOST；
- 从年度 `HN*_all.sav` 主表构建处理后数据集；
- 训练一个可复现的 XGBoost 分类模型；
- 输出模型、预测结果、指标、最优参数和特征重要性；
- 生成与 LR 基线的对比表。

## 3. 目录结构

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

## 4. 依赖环境

建议在本项目目录下执行：

```bash
pip install -r requirements.txt
```

主要依赖：
- pandas
- pyreadstat
- scikit-learn
- joblib
- xgboost

## 5. 数据与标签定义

当前主流程实际使用的原始文件：
- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

当前目标变量：
- `target_oa_kh`
- 来源于 `OA_KH`

当前处理后数据集：
- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`

## 6. 训练流程

为了与 LR 基线保持可比性，当前 XGBoost 采用：
- 80/20 分层训练-测试划分
- `random_state=42`
- 训练集内部 5 折交叉验证调参
- 使用与 LR 当前实现相同的特征家族

特征分组：
- 数值特征：`age`, `HE_BMI`, `LQ_VAS`
- 类别特征：`year`, `sex`, `incm`, `ho_incm`, `edu`, `occp`, `HE_HP`, `HE_DM`, `HE_mens`

类别不平衡处理：
- 划分时使用分层抽样
- 训练时搜索 `scale_pos_weight`，其中包含基于训练集自动计算的正负样本比

## 7. 输出文件

训练脚本会输出：
- `outputs/xgboost/knhanes_xgboost_model.joblib`
- `outputs/xgboost/knhanes_xgboost_test_predictions.csv`
- `outputs/xgboost/knhanes_xgboost_metrics.json`
- `outputs/xgboost/knhanes_xgboost_best_params.json`
- `outputs/xgboost/xgboost_feature_importance.csv`
- `outputs/xgboost/lr_vs_xgboost_comparison.csv`

## 8. 特征重要性分析

当前项目会输出两类特征重要性：
1. XGBoost 内置 gain importance
2. 基于测试集的 permutation importance

统一保存为：
- `outputs/xgboost/xgboost_feature_importance.csv`

## 9. 运行方式

在 `XGBoost/KNHANES` 目录下运行：

```bash
python src/data/inspect_knhanes_variables.py
python src/data/make_knhanes_dataset.py
python src/models/train_xgboost.py
```

## 10. 与 LR 基线的对比方式

本项目会生成对比表：
- `outputs/xgboost/lr_vs_xgboost_comparison.csv`

其中 LR 的参考指标来自当前已有的 `LR/KNHANES` 基线运行结果，从而保证对比是基于同一目标变量、同一划分策略和相同任务定义下进行的。

## 11. 当前限制

本项目当前**不是严格意义上的“膝痛预测”实现**，因为仓库内尚未确认 KNHANES 原始膝痛问卷字段的准确映射关系。当前版本的定位是：

> 一个与现有 `OA_KH` 版 LR baseline 完全对齐的 XGBoost baseline。

后续如果补齐膝痛字段映射，再切换到真正的膝痛标签版本会更合理。
