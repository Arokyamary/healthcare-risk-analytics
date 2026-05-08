import joblib
import numpy as np
import pandas as pd
from typing import Dict

RISK_TIERS = {
    (0.00, 0.30): 'LOW',
    (0.31, 0.55): 'MEDIUM',
    (0.56, 0.75): 'HIGH',
    (0.76, 1.00): 'CRITICAL',
}

class RiskPredictor:
    def __init__(self, model_path: str = 'models/risk_model_v1.joblib'):
        print(f"Loading model from {model_path}...")
        data = joblib.load(model_path)
        self.pipeline = data['pipeline']
        self.features = data['features']
        self.version = data['version']
        print(f"Model loaded: {self.version}")

    def predict(self, feature_dict: Dict) -> Dict:
        X = pd.DataFrame([feature_dict])[self.features]
        proba = self.pipeline.predict_proba(X)[0, 1]
        tier = self._get_tier(proba)

        return {
            'risk_score': round(float(proba), 4),
            'risk_tier': tier,
            'readmission_30d': round(float(proba), 4),
            'readmission_90d': round(float(min(proba * 1.4, 0.99)), 4),
            'mortality_risk': round(float(proba * 0.3), 4),
            'model_version': self.version,
        }

    def _get_tier(self, score: float) -> str:
        for (lo, hi), tier in RISK_TIERS.items():
            if lo <= score <= hi:
                return tier
        return 'CRITICAL'

predictor = RiskPredictor()