# XGBoost 基线实验说明

## 1. 实验定位

本实验是在现有 `LR/KNHANES` 项目之外，新增的一套独立 XGBoost 基线实现。

当前实验目标不是严格的“膝痛预测问卷标签版本”，而是：

- 与当前已实现的 LR 基线保持完全对齐；
- 使用相同的数据清洗逻辑；
- 使用相同的数据划分策略；
- 使用相同的目标变量 `target_oa_kh`；
- 输出可与 LR 直接比较的结果。

## 2. 数据来源

- KNHANES 2010–2012
- 使用 `HN10_all.sav`、`HN11_all.sav`、`HN12_all.sav`
- 不使用 OAI/MOST

## 3. 标签定义

当前标签为：
- `target_oa_kh`
- 来源于 `OA_KH`

说明：
- 这与《可复现实验清单_非OAI_MOST版.md》中推荐的“膝痛预测任务”不完全一致；
- 但由于仓库中尚未确认膝痛原始字段，因此当前版本先采用与 LR 对齐的实现路线。

## 4. 数据划分

当前沿用已有 LR 基线策略：
- 训练集 / 测试集 = 80 / 20
- `stratify=y`
- `random_state=42`
- 训练集内部 `GridSearchCV(cv=5)` 调参

## 5. 特征方案

### 数值特征
- `age`
- `HE_BMI`
- `LQ_VAS`

### 类别特征
- `year`
- `sex`
- `incm`
- `ho_incm`
- `edu`
- `occp`
- `HE_HP`
- `HE_DM`
- `HE_mens`

## 6. 缺失值与特征工程

- 数据构建阶段延续 LR 项目中的 KNHANES 缺失码清洗逻辑；
- 建模阶段：
  - 数值变量：中位数填补
  - 类别变量：众数填补 + One-Hot 编码
- XGBoost 不使用标准化，但整体特征输入集与 LR 保持一致。

## 7. 类别不平衡处理

当前采用两层处理：
1. 划分层面：分层抽样
2. 模型层面：搜索 `scale_pos_weight`

其中自动平衡值定义为：
- `n_negative / n_positive`
- 基于训练集计算

## 8. 超参数搜索

当前初版采用小网格：
- `n_estimators`: `[100, 300]`
- `max_depth`: `[3, 5]`
- `learning_rate`: `[0.03, 0.1]`
- `subsample`: `[0.8, 1.0]`
- `colsample_bytree`: `[0.8, 1.0]`
- `min_child_weight`: `[1, 5]`
- `scale_pos_weight`: `[1.0, auto_ratio]`

## 9. 评估指标

与 LR 保持一致，输出：
- ROC-AUC
- AP
- Accuracy
- Precision
- Recall
- F1
- Classification report
- Confusion matrix

## 10. 特征重要性

当前输出两种特征重要性：
1. XGBoost gain importance
2. permutation importance

输出文件：
- `outputs/xgboost/xgboost_feature_importance.csv`

## 11. 与 LR 的对比

当前对比文件：
- `outputs/xgboost/lr_vs_xgboost_comparison.csv`

比较字段包括：
- 模型名
- 目标变量
- 划分策略
- AUC
- AP
- Accuracy
- F1
- 备注

## 12. 后续建议

如果后续要与实验清单完全一致，建议下一步做：
1. 确认 KNHANES 膝痛标签原始字段；
2. 在数据构建脚本中新增 `target_knee_pain`；
3. 用相同 split 和模型框架重新跑 LR 与 XGBoost；
4. 将 OA_KH 版本和 knee pain 版本分开命名与记录。
