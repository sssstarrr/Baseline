# XGBoost 基线结果解读

## 1. 文档定位

本文档用于解释 `XGBoost/KNHANES` 当前基线实验结果，并说明其与现有 `LR/KNHANES` 基线的对比结论。

需要注意：
- 当前 XGBoost 项目并不是严格意义上的“膝痛问卷标签预测”版本；
- 当前实现路线是**先与现有 LR 基线完全对齐**；
- 因此当前比较任务实际为：
  - `OA_KH -> target_oa_kh`
- 这意味着本次结论应理解为：
  - **在当前 OA_KH 标签定义下，XGBoost 与 LR 的基线对比结果。**

## 2. 当前实验设置

### 数据范围
- KNHANES 2010–2012
- 使用：`HN10_all.sav`、`HN11_all.sav`、`HN12_all.sav`
- 不使用 OAI/MOST

### 目标变量
- `target_oa_kh`
- 来源于 `OA_KH`

### 特征
- 数值特征：`age`, `HE_BMI`, `LQ_VAS`
- 类别特征：`year`, `sex`, `incm`, `ho_incm`, `edu`, `occp`, `HE_HP`, `HE_DM`, `HE_mens`

### 划分与训练策略
- 训练集 / 测试集 = `80 / 20`
- `stratify=y`
- `random_state=42`
- 训练集内部 `GridSearchCV(cv=5)` 调参
- XGBoost 使用：
  - 数值变量中位数填补
  - 类别变量众数填补 + One-Hot 编码
  - `scale_pos_weight` 搜索 `[1.0, auto_ratio]`

## 3. 数据规模与类别分布

当前处理后数据集规模：
- 总样本数：`9196`
- 阴性：`7908`
- 阳性：`1288`

训练/测试划分后：
- 训练集：`7356`
  - 阴性：`6326`
  - 阳性：`1030`
- 测试集：`1840`
  - 阴性：`1582`
  - 阳性：`258`

自动计算得到的训练集类别比例：
- `auto_scale_pos_weight = 6326 / 1030 = 6.1417`

这说明当前任务存在明显类别不平衡，因此不能只看 Accuracy。

## 4. 最优 XGBoost 参数

本次网格搜索得到的最优参数为：

```python
{
    'model__colsample_bytree': 0.8,
    'model__learning_rate': 0.03,
    'model__max_depth': 3,
    'model__min_child_weight': 5,
    'model__n_estimators': 300,
    'model__scale_pos_weight': 1.0,
    'model__subsample': 0.8,
}
```

解读：
- 模型更偏向相对保守的小深度树；
- 较小学习率配合较多树数，属于较稳妥的设置；
- `scale_pos_weight` 最终没有选择自动不平衡比，而是选择了 `1.0`；
- 这说明在当前搜索空间和评分指标 `roc_auc` 下，未加权配置整体排序更优。

## 5. XGBoost 测试集结果

当前 XGBoost 测试集结果为：

- AUC：`0.8185`
- AP：`0.4183`
- Accuracy：`0.8614`
- Precision：`0.5263`
- Recall：`0.1163`
- F1：`0.1905`

混淆矩阵：

```text
[[1555,  27],
 [ 228,  30]]
```

可见：
- 模型把大多数阴性样本识别得较好；
- 但在默认 `0.5` 阈值下，仅识别出 `30 / 258` 个阳性；
- 因此 Recall 和 F1 明显偏低。

## 6. 与 LR 基线的直接对比

当前对比表见：
- `outputs/xgboost/lr_vs_xgboost_comparison.csv`

主要结果如下：

| 模型 | target | AUC | AP | Accuracy | F1 |
|---|---|---:|---:|---:|---:|
| LR | `target_oa_kh` | 0.8216 | 0.4194 | 0.7342 | 0.4386 |
| XGBoost | `target_oa_kh` | 0.8185 | 0.4183 | 0.8614 | 0.1905 |

### 结论 1：AUC 和 AP 基本接近

XGBoost 与 LR 在排序能力上几乎相当：
- AUC：`0.8216 vs 0.8185`
- AP：`0.4194 vs 0.4183`

这说明：
- 在当前特征集和标签定义下，XGBoost **没有明显超过** LR；
- 现有信息量可能不足以让树模型显著拉开差距；
- 线性模型已经能捕获这批特征中的大部分有效信号。

### 结论 2：XGBoost 的 Accuracy 更高，但不能直接说明更好

XGBoost 的 Accuracy 为 `0.8614`，明显高于 LR 的 `0.7342`。

但当前任务类别不平衡明显，Accuracy 很容易受到阴性类占比影响。结合 Recall/F1 看，当前 XGBoost 在默认阈值下更倾向于预测阴性，因此：
- 虽然总体准确率更高；
- 但对阳性样本的召回不足；
- 不能据此认定 XGBoost 更适合当前任务。

### 结论 3：当前默认阈值下，LR 更适合作为阳性识别基线

如果当前任务更关心阳性样本识别能力，那么从 F1 看：
- LR：`0.4386`
- XGBoost：`0.1905`

这说明在**默认 0.5 阈值**下：
- LR 在 Precision / Recall 平衡上更好；
- 当前 XGBoost 还没有达到一个更适合阳性筛查的工作点。

因此当前阶段更合理的结论是：
- **XGBoost 是一个有效、可复现、与 LR 可直接比较的树模型基线；**
- **但在本次默认阈值设置下，它并未优于现有 LR 基线。**

## 7. 特征重要性解读

当前特征重要性文件：
- `outputs/xgboost/xgboost_feature_importance.csv`

该文件包含两类重要性：
1. `gain_importance`
2. `permutation_importance_mean`

目前排名靠前的特征主要包括：
- `age`
- `sex`
- `LQ_VAS`
- `edu`
- `HE_BMI`

初步解读：
- `age` 和 `HE_BMI` 符合一般临床直觉；
- `LQ_VAS` 具有较强区分能力，也符合疼痛/症状相关特征的重要性预期；
- `sex` 与 `edu` 在当前数据中也提供了额外信息；
- `HE_mens`、`id` 等特征贡献很低或接近 0。

需要注意：
- gain importance 反映的是树分裂过程中的相对贡献；
- permutation importance 更接近“打乱该特征后性能下降多少”；
- 两者一致时，通常更值得关注；
- 若两者不一致，需要结合相关性、编码方式和样本规模再判断。

## 8. 当前结果应如何理解

当前最稳妥的理解方式是：

> 在与现有 LR 基线完全对齐的 OA_KH 任务上，XGBoost 成功建立了一个可复现、结构化、可直接比较的树模型基线，但目前未表现出明显优于 LR 的综合优势。

换句话说：
- 这次实验的价值主要在于**补齐基线体系**；
- 它说明“在当前任务定义下，树模型并不会自动优于线性模型”；
- 因而后续改进重点不应只是继续盲目换模型，而应优先考虑：
  - 标签定义是否更合理；
  - 是否补充更有信息量的特征；
  - 是否根据任务目标重新设定阈值与评价重点。

## 9. 建议的下一步

如果后续继续优化，建议优先做以下几项：

1. **补阈值分析**
   - 不只报告 `0.5` 阈值；
   - 可基于验证策略选择更适合 Recall/F1 的阈值；
   - 再与 LR 做更公平的工作点对比。

2. **补 PR 曲线与 ROC 曲线**
   - 当前已有 AUC 和 AP；
   - 若增加曲线图，会更容易展示不同阈值下的模型行为。

3. **扩大不平衡处理方案**
   - 在 `scale_pos_weight` 之外，增加更细粒度搜索；
   - 对比是否能提高阳性召回。

4. **回到真正的膝痛标签任务**
   - 当前项目仍是 `OA_KH` 对齐版本；
   - 若后续确认 KNHANES 原始膝痛字段，建议单独构建 `target_knee_pain`；
   - 再对 LR 与 XGBoost 同步重跑。

## 10. 相关文件

- 实验说明：`docs/XGBoost_基线实验说明.md`
- 指标文件：`outputs/xgboost/knhanes_xgboost_metrics.json`
- 最优参数：`outputs/xgboost/knhanes_xgboost_best_params.json`
- 特征重要性：`outputs/xgboost/xgboost_feature_importance.csv`
- LR 对比表：`outputs/xgboost/lr_vs_xgboost_comparison.csv`

