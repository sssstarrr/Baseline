# 可复现实验清单（非 OAI/MOST 版）

> 目标：给出一套可以直接落地的 **LR 基线实验清单**，面向“基于多模态数据的膝骨关节炎智能辅助诊断方法研究”，并严格遵守你的新要求：**不使用 OAI / MOST 数据集**。
>
> 因此本清单优先以 **KNHANES 2010–2012** 的膝痛预测任务作为 KOA 相近场景的 **LR 基线方案**。

---

# 1. 实验目标定义

## 1.1 推荐主任务

**任务名称**：膝痛二分类预测（有 / 无）

**推荐原因**：
1. 数据来源公开、真实、可追溯；
2. 不依赖 OAI/MOST；
3. 变量包含膝 X 线分级信息、人口学、临床、表型与生活方式，适合作为 KOA 多源信息场景下的 LR baseline；
4. 非常适合作为你后续多模态 KOA 课题中的“表格基线”部分。

## 1.2 标签定义

参考 Kim 2024：
- `y = 1`：有膝痛
- `y = 0`：无膝痛

膝痛定义应以原始问卷字段为准；文中核心含义为：
- 近 3 个月内膝痛持续至少 30 天

> 注意：最终实现时必须回到 KNHANES 原始字段字典确认编码，不能只凭论文文字二次猜测。

---

# 2. 数据来源与获取

## 2.1 官方数据来源
- **KNHANES 官网**：https://knhanes.kdca.go.kr
- **论文给出的直接获取入口**：https://knhanes.kdca.go.kr/knhanes/sub03/sub03_02_05.do

## 2.2 获取步骤
1. 进入 KNHANES 对应年份数据下载页面；
2. 选择 2010–2012 年；
3. 选择所需数据表；
4. 填写邮箱、姓名、单位；
5. 下载 SAS / SPSS 数据文件与变量说明。

## 2.3 建议下载的数据块
根据论文任务，建议至少准备：

1. **健康访谈数据**；
2. **体格检查数据**；
3. **DEXA 身体成分数据**；
4. **膝关节 X 线分级结果数据**；
5. **问卷中关于膝痛、生活方式、共病的数据表**。

---

# 3. 数据筛选条件

## 3.1 纳入标准
- 年龄 **50–79 岁**；
- 具有膝痛问卷信息；
- 具有膝关节 X 线分级信息；
- 具有你要纳入建模的核心变量。

## 3.2 排除标准
- 未接受膝关节 X 线检查；
- 年龄小于 50 岁或过高超出研究范围；
- 膝痛标签缺失；
- 关键协变量缺失过多且无法合理填补；
- 明显录入错误样本。

## 3.3 分层方式（可选）
如果你想贴近 Kim 2024 的设计，可分两组分别建模：

- **正常 X 线组**：K-L 0–1
- **异常 X 线组**：K-L 2–4

也可以先不分层，先做一个全样本总模型，再做分层分析作为扩展实验。

---

# 4. 变量表（建议版）

> 说明：下面是按“研究生可执行”原则整理的建议变量表。具体变量名要以你下载的 KNHANES 原始字段名为准。

| 变量类别 | 变量名（建议英文列名） | 类型 | 说明 | 建议处理 |
|---|---|---|---|---|
| ID | subject_id | 字符/整数 | 受试者唯一标识 | 原样保留 |
| 标签 | knee_pain | 二元 | 是否膝痛 | 0/1 |
| 影像分组 | kl_group | 类别 | 正常/异常 X 线组 | 0/1 或 one-hot |
| 影像等级 | kl_grade | 序数 | K-L 0–4 | 可保留为整数；必要时 one-hot |
| 人口学 | age | 连续 | 年龄 | 中位数填补 + 标准化 |
| 人口学 | sex | 二元 | 性别 | 0/1 |
| 体格 | bmi | 连续 | BMI | 中位数填补 + 标准化 |
| 身体成分 | fat_percent | 连续 | 脂肪百分比 | 中位数填补 + 标准化 |
| 病史 | hypertension | 二元 | 高血压 | 0/1 |
| 病史 | diabetes | 二元 | 糖尿病 | 0/1 |
| 病史 | dyslipidemia | 二元 | 血脂异常 | 0/1 |
| 病史 | osteoporosis | 二元 | 骨质疏松 | 0/1 |
| 病史 | renal_disease | 二元 | 肾病 | 0/1 |
| 精神状态 | depressive_mood | 二元 | 持续 14 天以上抑郁心境 | 0/1 |
| 女性相关 | menopause | 二元 | 绝经状态 | 女性样本中 0/1；男性可单独编码缺失/不适用 |
| 生活方式 | alcohol_use | 连续/类别 | 饮酒量 | 依据原始编码整理 |
| 生活方式 | smoking | 连续/类别 | 吸烟量 | 依据原始编码整理 |
| 生活方式 | physical_activity | 连续 | METs | 中位数填补 + 标准化 |
| 社会学 | occupation_blue_collar | 二元 | 蓝领职业 | 0/1 |
| 社会学 | rural_residence | 二元 | 农村居住 | 0/1 |
| 社会学 | income_top50 | 二元 | 收入前 50% | 0/1 |
| 体重变化 | weight_gain_1y | 二元 | 近一年体重增加 | 0/1 |

---

# 5. 数据预处理流程

## 5.1 总原则
所有预处理必须写进 `sklearn Pipeline` 或等价流程中，避免数据泄漏。

## 5.2 缺失值处理

### 连续变量
- 使用 `SimpleImputer(strategy='median')`

### 类别变量
- 使用 `SimpleImputer(strategy='most_frequent')`

> 如果某个变量缺失率很高（例如 >30%），建议：
> 1. 先评估是否保留；
> 2. 若保留，需在论文中解释原因。

## 5.3 编码方式

- 二元变量：0/1；
- 多类别变量：`OneHotEncoder(handle_unknown='ignore')`；
- K-L grade：
  - 如果把它当序数特征，可直接保留整数；
  - 如果担心线性假设不合适，可 one-hot。

## 5.4 标准化
仅对以下模型做标准化：
- Logistic Regression
- SVM
- MLP

推荐：`StandardScaler()`。

## 5.5 共线性处理
建议先做一次相关性筛查：

1. 保留 BMI；
2. 不再同时保留“身高 + 体重 + BMI”三者；
3. 若某些变量高度相关（如 `r > 0.85`），保留更稳定、医学上更容易解释的那个。

---

# 6. 训练 / 验证 / 测试划分

## 6.1 推荐方案 A：单次固定划分
适合样本量中等、希望流程简单：

- train：70%
- validation：15%
- test：15%

要求：
- 使用 `stratify=y`；
- 固定 `random_state`；
- 全部模型共用这套划分。

## 6.2 推荐方案 B：5 折交叉验证 + 独立测试集
适合论文实验更稳妥：

1. 先留出 15–20% 做最终测试集；
2. 剩余训练开发集做 5-fold stratified CV；
3. 超参数选择只在开发集内部完成；
4. 最终仅在测试集报告一次主结果。

> 如果你样本量只有几千级，这个方案通常最稳。

---

# 7. 必跑基线模型清单

## 7.1 最小基线组合（推荐）

### 基线 1：Logistic Regression
- 作用：最核心医学 baseline
- 输入：全部表格特征
- 输出：膝痛概率

### 基线 2：XGBoost 或 LightGBM
- 作用：非线性强基线
- 输入：全部表格特征
- 输出：膝痛概率

### 基线 3：Random Forest（可选）
- 作用：树模型补充基线
- 输入：全部表格特征
- 输出：类别/概率

## 7.2 扩展基线（如果时间允许）

### 分层 LR
分别在：
- K-L 0–1 组；
- K-L 2–4 组；
跑两个独立 LR。

### 去掉影像分级信息的 LR
比较：
- `tabular_without_kl`
- `tabular_with_kl`

可以回答：**K-L 分级本身贡献了多少信息**。

---

# 8. 评价指标设置

## 8.1 二分类指标
必须至少报告：

- ROC-AUC
- AP 或 PR-AUC
- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

## 8.2 置信区间（推荐）
如果你想让论文更规范，建议：

- 对测试集做 1000 次 bootstrap；
- 报告 AUC 和 AP 的 95% CI。

## 8.3 阈值选择
推荐两种方式：

1. 默认阈值 0.5；
2. 在验证集上用 Youden index 选择阈值，再固定到测试集。

不能在测试集上反复调阈值。

---

# 9. 超参数调优建议

## 9.1 LR 调参网格

```python
{
    'model__C': [0.01, 0.1, 1, 10, 100],
    'model__penalty': ['l2'],
    'model__class_weight': [None, 'balanced']
}
```

> 如果特征较多、担心冗余，也可尝试 `saga + l1` 做稀疏选择。

## 9.2 RF 调参网格

```python
{
    'model__n_estimators': [100, 300, 500],
    'model__max_depth': [None, 5, 10],
    'model__min_samples_split': [2, 5, 10]
}
```

## 9.3 XGBoost / LightGBM
若时间有限，不要做太大搜索。建议小网格即可。

---

# 10. sklearn 实现步骤（可直接照着做）

## 10.1 文件组织建议

```text
project/
├─ data/
│  ├─ raw/
│  ├─ interim/
│  └─ processed/
├─ notebooks/
├─ src/
│  ├─ make_dataset.py
│  ├─ train_lr.py
│  ├─ train_xgb.py
│  ├─ evaluate.py
│  └─ utils.py
├─ results/
│  ├─ splits/
│  ├─ metrics/
│  └─ models/
└─ README.md
```

## 10.2 读取并合并数据

你需要完成：
1. 读取各年份原始表；
2. 用 `subject_id` 合并；
3. 选出年龄 50–79 岁；
4. 构造 `knee_pain` 标签；
5. 构造 `kl_grade` 和 `kl_group`；
6. 保留最终变量表。

## 10.3 划分数据

```python
from sklearn.model_selection import train_test_split

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, stratify=y, random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
)
```

## 10.4 建立预处理器

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

numeric_features = ['age', 'bmi', 'fat_percent', 'physical_activity']
categorical_features = [
    'sex', 'kl_group', 'kl_grade', 'hypertension', 'diabetes',
    'dyslipidemia', 'osteoporosis', 'renal_disease', 'depressive_mood',
    'menopause', 'occupation_blue_collar', 'rural_residence',
    'income_top50', 'weight_gain_1y'
]

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)
```

## 10.5 训练 LR

```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

lr_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', LogisticRegression(max_iter=2000, random_state=42))
])

lr_pipeline.fit(X_train, y_train)
```

## 10.6 调参

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'model__C': [0.01, 0.1, 1, 10, 100],
    'model__class_weight': [None, 'balanced']
}

grid = GridSearchCV(
    lr_pipeline,
    param_grid=param_grid,
    scoring='roc_auc',
    cv=5,
    n_jobs=-1
)

grid.fit(X_train, y_train)
```

## 10.7 评估

```python
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, f1_score

y_prob = grid.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

print('AUC:', roc_auc_score(y_test, y_prob))
print('AP:', average_precision_score(y_test, y_prob))
print('ACC:', accuracy_score(y_test, y_pred))
print('F1:', f1_score(y_test, y_pred))
```

## 10.8 保存结果
必须保存：

1. 训练/验证/测试索引；
2. 最佳参数；
3. 每个模型的 test 指标；
4. 预测概率；
5. confusion matrix；
6. 特征系数（对 LR）。

---

# 11. LR 基线的解释性输出

对于 KOA 相关研究，建议额外输出：

1. 每个变量的回归系数；
2. OR（odds ratio）= `exp(coef)`；
3. 重要变量排序；
4. 校准曲线。

这会让你的基线不仅是“跑了一个模型”，而是“有医学解释的风险模型”。

---

# 12. 时间和算力有限时的优先级

如果你现在时间有限，我建议按下面顺序执行：

## 一级优先
1. 数据清洗与变量表确定；
2. 单个全样本 LR；
3. 单个全样本 XGBoost；
4. 写出结果表。

## 二级优先
5. 正常/异常 X 线分层 LR；
6. 去掉 KL grade 的消融；
7. bootstrap 置信区间。

## 三级优先
8. RF / SVM；
9. 外部验证；
10. 更复杂多模态融合。

---

# 13. 最终建议：你这篇课题里怎么用这套清单

最实用的写法是：

## 论文 / 开题中的表述方式
- 先建立 **临床-人口学-表型 LR 基线模型**；
- 再建立 **XGBoost 强基线模型**；
- 若后续取得原始影像，再加入 **影像单模态 CNN** 与 **多模态融合模型**；
- 所有模型共享同一数据划分与评价指标，以保证公平对比。

## 工程实施方式
你可以把这套清单直接拆成四个脚本：

1. `make_dataset.py`
2. `train_lr.py`
3. `train_xgb.py`
4. `evaluate.py`

这样后续无论你换成自己的 KOA 数据，还是加入图像分支，都能继续复用。

---

# 14. 本清单对应的参考依据

## KOA 相近场景主参考
- Kim T. 2024, PLOS One:
  - https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0314789
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC11611080/

## KNHANES 数据入口
- https://knhanes.kdca.go.kr/knhanes/sub03/sub03_02_05.do

## 方法模板参考
- Wisconsin breast cancer paper: https://arxiv.org/abs/1711.07831
- GitHub code: https://github.com/AFAgarap/wisconsin-breast-cancer
- sklearn dataset doc: https://scikit-learn.org/1.5/modules/generated/sklearn.datasets.load_breast_cancer.html
