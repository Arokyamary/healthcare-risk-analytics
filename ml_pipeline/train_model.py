import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import joblib
import os
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, average_precision_score
from xgboost import XGBClassifier

os.makedirs("models", exist_ok=True)
os.makedirs("mlruns", exist_ok=True)

print("Loading features...")
df = pd.read_parquet("ml_pipeline/features_train.parquet")

NUMERIC_FEATURES = [
    'age_years', 'num_admissions_12m', 'num_ed_visits_6m',
    'avg_los_12m', 'max_los', 'total_inpatient',
    'num_diagnoses', 'num_chronic_dx',
    'last_systolic_bp', 'last_bmi', 'last_spo2',
    'days_since_last_visit', 'num_medications'
]
CATEGORICAL_FEATURES = ['gender', 'insurance_type']
BINARY_FEATURES = [
    'insurance_medicaid', 'insurance_uninsured',
    'has_diabetes', 'has_hypertension', 'has_copd'
]
TARGET = 'readmission_30d'
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES

X = df[ALL_FEATURES].copy()
y = df[TARGET].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Train: {len(X_train)} | Test: {len(X_test)}")
print(f"Positive class rate: {y.mean()*100:.1f}%")

numeric_pipe = Pipeline([
    ('impute', SimpleImputer(strategy='median')),
    ('scale', StandardScaler())
])
categorical_pipe = Pipeline([
    ('impute', SimpleImputer(strategy='most_frequent')),
    ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])
preprocessor = ColumnTransformer([
    ('num', numeric_pipe, NUMERIC_FEATURES),
    ('cat', categorical_pipe, CATEGORICAL_FEATURES),
    ('bin', 'passthrough', BINARY_FEATURES)
])

class_weight = (y == 0).sum() / (y == 1).sum()

xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=class_weight,
    eval_metric='auc',
    random_state=42,
    verbosity=0
)
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
stack = StackingClassifier(
    estimators=[('xgb', xgb), ('rf', rf)],
    final_estimator=LogisticRegression(C=1.0),
    cv=5,
    n_jobs=-1
)
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', CalibratedClassifierCV(stack, cv=5, method='sigmoid'))
])

mlflow.set_experiment("healthcare_risk_v1")
with mlflow.start_run(run_name="xgb_rf_stacking"):
    print("Training model (takes 3-5 minutes)...")
    full_pipeline.fit(X_train, y_train)

    y_prob = full_pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    ap = average_precision_score(y_test, y_prob)
    cv_auc = cross_val_score(
        full_pipeline, X, y,
        cv=StratifiedKFold(5, shuffle=True, random_state=42),
        scoring='roc_auc').mean()

    mlflow.log_metrics({'test_auc': auc, 'test_ap': ap, 'cv_auc': cv_auc})
    mlflow.log_params({
        'xgb_n_estimators': 300, 'xgb_max_depth': 6,
        'rf_n_estimators': 200, 'model_type': 'xgb_rf_stack'
    })
    mlflow.sklearn.log_model(full_pipeline, "model")

    print(f"Test AUC:  {auc:.4f}")
    print(f"Test AP:   {ap:.4f}")
    print(f"CV AUC:    {cv_auc:.4f}")
    print(f"Gini:      {(2*auc-1):.4f}")

joblib.dump({
    'pipeline': full_pipeline,
    'features': ALL_FEATURES,
    'version': 'v1.0.0',
    'trained_at': pd.Timestamp.now().isoformat()
}, 'models/risk_model_v1.joblib')
print("Model saved: models/risk_model_v1.joblib")