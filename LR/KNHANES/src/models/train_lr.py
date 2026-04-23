from __future__ import annotations

from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.common.paths import LR_OUTPUT_DIR, PROCESSED_DATA_DIR

DATASET_CSV = PROCESSED_DATA_DIR / 'knhanes_2010_2012_knee_oa_dataset.csv'
MODEL_PATH = LR_OUTPUT_DIR / 'knhanes_lr_model.joblib'
PRED_PATH = LR_OUTPUT_DIR / 'knhanes_lr_test_predictions.csv'

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


def main() -> None:
    if not DATASET_CSV.exists():
        raise SystemExit(f'Missing dataset: {DATASET_CSV}. Run make_knhanes_dataset.py first.')

    data = pd.read_csv(DATASET_CSV)
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
        random_state=42,
    )

    numeric_features = [c for c in NUMERIC_FEATURES if c in X_train.columns]
    categorical_features = [c for c in CATEGORICAL_FEATURES if c in X_train.columns]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                'num',
                Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
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
        ('model', LogisticRegression(max_iter=5000, solver='lbfgs', random_state=42)),
    ])

    grid = GridSearchCV(
        estimator=pipeline,
        param_grid={
            'model__C': [0.01, 0.1, 1.0, 10.0, 100.0],
            'model__class_weight': [None, 'balanced'],
        },
        scoring='roc_auc',
        cv=5,
        n_jobs=-1,
        refit=True,
    )

    grid.fit(X_train, y_train)

    y_prob = grid.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    print('best_params:', grid.best_params_)
    print('train_rows:', len(X_train), 'test_rows:', len(X_test))
    print('AUC:', round(roc_auc_score(y_test, y_prob), 4))
    print('AP:', round(average_precision_score(y_test, y_prob), 4))
    print('ACC:', round(accuracy_score(y_test, y_pred), 4))
    print('F1:', round(f1_score(y_test, y_pred), 4))
    print(classification_report(y_test, y_pred, digits=4))

    pred_df = X_test[['id']].copy()
    pred_df['y_true'] = y_test.to_numpy()
    pred_df['y_prob'] = y_prob
    pred_df['y_pred'] = y_pred
    pred_df.to_csv(PRED_PATH, index=False, encoding='utf-8-sig')
    joblib.dump(grid.best_estimator_, MODEL_PATH)

    print('saved_model:', MODEL_PATH)
    print('saved_predictions:', PRED_PATH)


if __name__ == '__main__':
    main()
