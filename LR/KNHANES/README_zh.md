# KNHANES 膝骨关节炎基线项目

For the English version, see: [README.md](README.md)

## 1. 项目简介

本子项目用于基于 KNHANES 的 SPSS 数据文件构建结构化分析数据集，并训练一个可复现的逻辑回归（Logistic Regression, LR）基线模型，服务于膝骨关节炎相关研究。

当前实现聚焦于三个核心任务：

1. 检查年度 `.sav` 文件中的关键变量；
2. 基于 KNHANES 2010–2012 年 `HN*_all.sav` 主表构建分析级 CSV 数据集；
3. 使用处理后的数据集训练并评估一个 LR 基线模型。

该项目适合用于：

- 快速建立可复现基线；
- 课题组内部交接；
- 后续扩展到更多模型或更多 KNHANES 模块；
- 为膝骨关节炎研究提供规范化的数据处理起点。

## 2. 当前范围与目标

当前主流程围绕以下三个 KNHANES 年度主表展开：

- `HN10_all.sav`
- `HN11_all.sav`
- `HN12_all.sav`

当前使用 `OA_KH` 构建主二分类标签，作为当前基线数据集中的目标变量。

项目中还保存了其他 KNHANES 原始文件（如 `dxa` 和 `ijmt`），但**当前版本尚未将这些文件接入基线流程**。它们目前主要作为后续特征扩展的原始数据储备。

## 3. 目录结构

```text
LR/KNHANES/
├─ README.md
├─ README_zh.md
├─ requirements.txt
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

### 目录职责说明

- `data/raw/`：存放原始 KNHANES SPSS 数据文件，视为只读输入
- `data/processed/`：存放由脚本生成的分析级数据集
- `src/common/`：存放共享路径配置等公共模块
- `src/data/`：存放变量检查和数据集构建脚本
- `src/models/`：存放模型训练脚本
- `outputs/`：存放模型文件和预测结果等输出产物
- `docs/`：存放研究说明、实验清单等辅助文档

## 4. 环境与依赖

### 推荐环境

- Python 3.10 及以上
- 可访问 KNHANES `.sav` 原始文件的本地环境

### 主要依赖包

- `pandas`
- `pyreadstat`
- `scikit-learn`
- `joblib`

### 安装方式

建议在项目根目录执行：

```bash
pip install -r LR/KNHANES/requirements.txt
```

或在 `LR/KNHANES` 目录中执行：

```bash
pip install -r requirements.txt
```

## 5. 核心脚本说明

### 5.1 `src/data/inspect_knhanes_variables.py`

作用：
- 检查年度 `.sav` 文件中的关键变量是否存在；
- 输出变量标签、缺失情况和频数分布；
- 帮助确认标签变量与特征变量是否可用于后续建模。

输入：
- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

输出：
- 控制台打印结果，不写文件

说明：
- 这是一个诊断性脚本，不会修改原始数据；
- 脚本中保留了变量别名说明，例如原始 SAV 中的 `OA_K_SCA`、`OA_L_SCA` 在 `pyreadstat` 解析后对应为 `OA_K_scale`、`OA_L_scale`。

### 5.2 `src/data/make_knhanes_dataset.py`

作用：
- 从年度 KNHANES 主表中提取当前研究所需变量；
- 清洗缺失码；
- 统一不同年份的主键命名；
- 构建建模用分析级 CSV 数据集。

输入：
- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

输出：
- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`

当前生成的派生字段：
- `target_oa_kh`
- `target_oa_k_scale_ge2`

当前主要处理逻辑：
- 只读取当前 LR 基线所需变量；
- 保留年份字段；
- 保留 `source_file` 以便追溯样本来源；
- 兼容 `ID` / `id` 差异。

### 5.3 `src/models/train_lr.py`

作用：
- 基于处理好的 CSV 数据集训练并评估逻辑回归基线模型。

输入：
- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`

输出：
- `outputs/lr/knhanes_lr_model.joblib`
- `outputs/lr/knhanes_lr_test_predictions.csv`

当前建模配置：
- 数值特征：`age`、`HE_BMI`、`LQ_VAS`
- 类别特征：`year`、`sex`、`incm`、`ho_incm`、`edu`、`occp`、`HE_HP`、`HE_DM`、`HE_mens`
- 目标变量：`target_oa_kh`
- 预处理：缺失值填补 + 标准化 / One-Hot 编码
- 模型：`LogisticRegression`
- 调参：`GridSearchCV`
- 评估：ROC-AUC、AP、ACC、F1、分类报告

## 6. 输入与输出文件说明

### 当前主流程实际使用的原始文件

- `data/raw/HN10_all.sav`
- `data/raw/HN11_all.sav`
- `data/raw/HN12_all.sav`

### 当前目录中保存但尚未接入基线流程的原始文件

- `data/raw/hn10_dxa.sav`
- `data/raw/hn11_dxa.sav`
- `data/raw/hn10_ijmt.sav`
- `data/raw/hn11_ijmt.sav`
- `data/raw/hn12_ijmt.sav`

这些文件目前主要用于后续扩展，不参与当前 LR 基线脚本的实际数据构建。

### 中间数据文件

- `data/processed/knhanes_2010_2012_knee_oa_dataset.csv`
  - 基于年度主表构建的分析级数据集

### 模型输出文件

- `outputs/lr/knhanes_lr_model.joblib`
  - 训练好的 sklearn 管道模型

- `outputs/lr/knhanes_lr_test_predictions.csv`
  - 测试集预测结果，包括真实标签、预测概率和预测类别

## 7. 运行方式

建议在 `LR/KNHANES` 目录下运行以下命令。

### 第一步：检查变量

```bash
python src/data/inspect_knhanes_variables.py
```

### 第二步：构建处理后数据集

```bash
python src/data/make_knhanes_dataset.py
```

### 第三步：训练 LR 基线模型

```bash
python src/models/train_lr.py
```

## 8. 数据处理流程

当前工作流如下：

1. 从 `data/raw/` 读取年度 `HN*_all.sav` 文件；
2. 选择当前研究所需变量；
3. 统一不同年份的 ID 命名差异（`ID` 与 `id`）；
4. 将 KNHANES 常见缺失编码（如 `8/9/88/99/888/999`）转换为空值；
5. 合并多个年份的数据；
6. 构建目标变量，如 `target_oa_kh`；
7. 将处理后结果保存到 `data/processed/`；
8. 加载处理后 CSV 进入模型训练流程；
9. 划分训练集和测试集；
10. 进行预处理、调参、训练与评估；
11. 将模型和测试预测结果保存到 `outputs/lr/`。

## 9. 可复现性说明

- 训练脚本中使用了固定随机种子；
- 当前脚本保持小而清晰，便于审查和维护；
- 目录结构已经按原始数据、处理数据、代码、输出和文档分离，减少混淆；
- 在本次整理中只优化了项目结构和路径管理，没有改变核心数据处理与 LR 训练逻辑。

## 10. 维护建议

### 10.1 原始数据管理

- 所有原始 SPSS 文件统一放在 `data/raw/` 下；
- 原始数据应视为只读，不建议手工修改；
- 不要覆盖或直接编辑下载得到的 KNHANES 原始文件。

### 10.2 新增年份或新增 KNHANES 模块

如果后续要接入新的年份或新的 KNHANES 模块，建议：

1. 将原始文件放入 `data/raw/`；
2. 谨慎扩展 `make_knhanes_dataset.py`；
3. 在本 README 中同步更新输入文件和变量说明；
4. 重新生成处理后数据集和模型输出。

### 10.3 新增模型基线

如果后续要加入 Random Forest、XGBoost、LightGBM 等模型，建议：

- 在 `src/models/` 下新增训练脚本；
- 在 `outputs/` 下按模型单独建子目录；
- 在 README 中补充对应运行说明。

建议后续结构如下：

```text
outputs/
├─ lr/
├─ rf/
├─ xgboost/
└─ lightgbm/
```

### 10.4 路径统一管理

当前项目的路径统一定义在：

- `src/common/paths.py`

后续新增脚本时，建议统一从该文件导入路径定义，而不要在脚本中重新硬编码相对路径。

## 11. 当前限制

- 当前基线流程仅使用年度 `HN*_all.sav` 主表；
- `dxa` 和 `ijmt` 原始文件尚未并入当前分析级数据集；
- 当前目标变量基于 `OA_KH`，如果未来切换为 knee pain 或其他表型，需要同步更新数据集命名、目标定义和 README 描述；
- 当前实现的重点是一个可复现的 LR 基线，而不是完整的多模型基准系统。

## 12. 后续建议

如果后续继续完善，建议优先考虑：

1. 增加更多基线模型；
2. 对输出结果增加实验版本标记；
3. 增加基础数据校验脚本；
4. 在特征方案明确后，逐步接入 `dxa` 与 `ijmt` 数据；
5. 在团队交接时，优先维护本 README 与 `docs/` 中的实验说明一致。

## 13. 配套文档

研究说明与实验清单保存在 `docs/` 目录中：

- `docs/KOA基线模型与LR论文筛选_非OAI_MOST版.md`
- `docs/可复现实验清单_非OAI_MOST版.md`

这些文档提供研究背景与实验设计支持，而本 README 主要作为当前代码结构、文件关系和运行流程的操作指南。
