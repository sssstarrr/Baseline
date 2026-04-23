from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# 确保脚本直接运行时也能正确导入 `src.*` 模块。
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.common.paths import PROCESSED_DATA_DIR, XGBOOST_OUTPUT_DIR

DATASET_CSV = PROCESSED_DATA_DIR / 'knhanes_2010_2012_knee_oa_dataset.csv'
MODEL_PATH = XGBOOST_OUTPUT_DIR / 'knhanes_xgboost_model.joblib'
PRED_PATH = XGBOOST_OUTPUT_DIR / 'knhanes_xgboost_test_predictions.csv'
METRICS_PATH = XGBOOST_OUTPUT_DIR / 'knhanes_xgboost_metrics.json'
PARAMS_PATH = XGBOOST_OUTPUT_DIR / 'knhanes_xgboost_best_params.json'
FEATURE_IMPORTANCE_PATH = XGBOOST_OUTPUT_DIR / 'xgboost_feature_importance.csv'
COMPARISON_PATH = XGBOOST_OUTPUT_DIR / 'lr_vs_xgboost_comparison.csv'

NUMERIC_FEATURES = [
    'age',
    'HE_BMI',
    'LQ_VAS',
]

CATEGORICAL_FEATURES = [
    'year',
    'sex',
    'incm',
    'ho_incm',
    'edu',
    'occp',
    'HE_HP',
    'HE_DM',
    'HE_mens',
]

TARGET = 'target_oa_kh'
RANDOM_STATE = 42


def build_feature_importance(best_estimator: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    preprocessor = best_estimator.named_steps['preprocessor']
    model = best_estimator.named_steps['model']

    numeric_features = list(preprocessor.transformers_[0][2])
    categorical_features = list(preprocessor.transformers_[1][2])
    onehot = preprocessor.named_transformers_['cat'].named_steps['onehot']
    categorical_output_names = onehot.get_feature_names_out(categorical_features)

    transformed_feature_names = list(preprocessor.get_feature_names_out())
    raw_feature_names = numeric_features[:]
    # 将 one-hot 展开的列映射回原始类别特征名。
    for output_name in categorical_output_names:
        matched_feature = next(
            feature for feature in categorical_features
            if output_name == feature or output_name.startswith(f'{feature}_')
        )
        raw_feature_names.append(matched_feature)

    gain_name_map = {
        f'f{i}': raw_feature_names[i]
        for i in range(len(transformed_feature_names))
    }
    booster_score = model.get_booster().get_score(importance_type='gain')
    gain_rows = []
    for raw_key, score in booster_score.items():
        gain_rows.append((gain_name_map.get(raw_key, raw_key), float(score)))
    gain_df = pd.DataFrame(gain_rows, columns=['feature', 'gain_importance'])

    # 通过完整流水线在原始输入特征上计算置换重要性。
    perm = permutation_importance(
        best_estimator,
        x_test,
        y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring='roc_auc',
        n_jobs=1,
    )
    perm_df = pd.DataFrame(
        {
            'feature': x_test.columns,
            'permutation_importance_mean': perm.importances_mean,
            'permutation_importance_std': perm.importances_std,
        }
    )

    # 对 one-hot 各分箱的 gain 进行聚合，便于在原始特征粒度比较。
    gain_grouped = gain_df.groupby('feature', as_index=False)['gain_importance'].sum()
    merged = perm_df.merge(gain_grouped, on='feature', how='outer')
    merged['permutation_importance_mean'] = merged['permutation_importance_mean'].fillna(0.0)
    merged['permutation_importance_std'] = merged['permutation_importance_std'].fillna(0.0)
    merged['gain_importance'] = merged['gain_importance'].fillna(0.0)

    merged = merged.sort_values(
        by=['permutation_importance_mean', 'gain_importance'],
        ascending=False,
    ).reset_index(drop=True)
    return merged


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def main() -> None:
    if not DATASET_CSV.exists():
        raise SystemExit(f'Missing dataset: {DATASET_CSV}. Run src/data/make_knhanes_dataset.py first.')

    XGBOOST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(DATASET_CSV)
    # 仅保留所需列；保留 id 以便输出可追溯的预测结果。
    keep_cols = ['id', TARGET] + [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c in data.columns]
    data = data[keep_cols].copy()
    data = data.dropna(subset=[TARGET])
    data[TARGET] = data[TARGET].astype(int)

    X = data.drop(columns=[TARGET])
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    negative_count = int((y_train == 0).sum())
    positive_count = int((y_train == 1).sum())
    # 自动计算类别权重比例，用于缓解二分类样本不平衡。
    auto_ratio = negative_count / positive_count

    numeric_features = [c for c in NUMERIC_FEATURES if c in X_train.columns]
    categorical_features = [c for c in CATEGORICAL_FEATURES if c in X_train.columns]

    # 数值与类别特征分支分别插补后再送入模型。
    preprocessor = ColumnTransformer(
        transformers=[
            (
                'num',
                Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                ]),
                numeric_features,
            ),
            (
                'cat',
                Pipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('onehot', OneHotEncoder(handle_unknown='ignore')),
                ]),
                categorical_features,
            ),
        ]
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        (
            'model',
            XGBClassifier(
                objective='binary:logistic',
                eval_metric='logloss',
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
        ),
    ])

    # 网格搜索同时覆盖不加权和按不平衡比例加权两种设置。
    param_grid = {
        'model__n_estimators': [100, 300],
        'model__max_depth': [3, 5],
        'model__learning_rate': [0.03, 0.1],
        'model__subsample': [0.8, 1.0],
        'model__colsample_bytree': [0.8, 1.0],
        'model__min_child_weight': [1, 5],
        'model__scale_pos_weight': [1.0, auto_ratio],
    }

    grid = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring='roc_auc',
        cv=5,
        n_jobs=1,
        refit=True,
        verbose=0,
    )

    grid.fit(X_train, y_train)

    y_prob = grid.predict_proba(X_test)[:, 1]
    # 使用默认 0.5 阈值生成二分类预测，便于报告常见指标。
    y_pred = (y_prob >= 0.5).astype(int)

    auc = float(roc_auc_score(y_test, y_prob))
    ap = float(average_precision_score(y_test, y_prob))
    acc = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print('best_params:', grid.best_params_)
    print('train_rows:', len(X_train), 'test_rows:', len(X_test))
    print('train_pos_weight_auto:', round(auto_ratio, 6))
    print('AUC:', round(auc, 4))
    print('AP:', round(ap, 4))
    print('ACC:', round(acc, 4))
    print('Precision:', round(precision, 4))
    print('Recall:', round(recall, 4))
    print('F1:', round(f1, 4))
    print(classification_report(y_test, y_pred, digits=4))

    pred_df = X_test[['id']].copy()
    pred_df['y_true'] = y_test.to_numpy()
    pred_df['y_prob'] = y_prob
    pred_df['y_pred'] = y_pred
    pred_df.to_csv(PRED_PATH, index=False, encoding='utf-8-sig')

    feature_importance_df = build_feature_importance(grid.best_estimator_, X_test, y_test)
    feature_importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False, encoding='utf-8-sig')

    metrics_payload = {
        'model_name': 'xgboost',
        'target': TARGET,
        'split_strategy': '80/20 stratified holdout + 5-fold CV on train',
        'random_state': RANDOM_STATE,
        'train_rows': len(X_train),
        'test_rows': len(X_test),
        'train_target_counts': {str(k): int(v) for k, v in y_train.value_counts().sort_index().to_dict().items()},
        'test_target_counts': {str(k): int(v) for k, v in y_test.value_counts().sort_index().to_dict().items()},
        'auto_scale_pos_weight': auto_ratio,
        'metrics': {
            'auc': auc,
            'ap': ap,
            'accuracy': acc,
            'precision': precision,
            'recall': recall,
            'f1': f1,
        },
        'confusion_matrix': cm,
        'classification_report': classification_report(y_test, y_pred, digits=4, output_dict=True),
    }
    # 持久化模型产物与元数据，保证实验可复现。
    save_json(METRICS_PATH, metrics_payload)
    save_json(PARAMS_PATH, grid.best_params_)
    joblib.dump(grid.best_estimator_, MODEL_PATH)

    comparison_df = pd.DataFrame(
        [
            {
                'model': 'lr',
                'target': 'target_oa_kh',
                'split_strategy': '80/20 stratified holdout + 5-fold CV on train',
                'auc': 0.8216,
                'ap': 0.4194,
                'accuracy': 0.7342,
                'f1': 0.4386,
                'notes': 'Values copied from existing LR baseline run in LR/KNHANES',
            },
            {
                'model': 'xgboost',
                'target': TARGET,
                'split_strategy': '80/20 stratified holdout + 5-fold CV on train',
                'auc': auc,
                'ap': ap,
                'accuracy': acc,
                'f1': f1,
                'notes': 'Standalone XGBoost baseline aligned to current OA_KH target',
            },
        ]
    )
    comparison_df.to_csv(COMPARISON_PATH, index=False, encoding='utf-8-sig')

    print('saved_model:', MODEL_PATH)
    print('saved_predictions:', PRED_PATH)
    print('saved_metrics:', METRICS_PATH)
    print('saved_best_params:', PARAMS_PATH)
    print('saved_feature_importance:', FEATURE_IMPORTANCE_PATH)
    print('saved_comparison:', COMPARISON_PATH)


if __name__ == '__main__':
    main()
