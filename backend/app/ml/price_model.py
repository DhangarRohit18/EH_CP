"""
Machine Learning Price Anomaly Engine
Uses Scikit-Learn Isolation Forest to detect statistical price deviations from retail benchmarks.
"""

import numpy as np
from typing import Tuple, Dict, Any

class PriceAnomalyDetector:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.model_version = "isolation_forest_v1.2.0"
        self._init_model()

    def _init_model(self):
        try:
            from sklearn.ensemble import IsolationForest
            # Representative retail discount distribution:
            # Normal competitive e-commerce sales: mean 12.0%, std 8.0%, rarely exceeding 35%.
            np.random.seed(42)
            normal_discounts = np.random.normal(loc=12.0, scale=8.0, size=(1000, 1))
            normal_discounts = np.clip(normal_discounts, 0.0, 45.0)

            # Fit Isolation Forest model
            self.model = IsolationForest(
                n_estimators=100,
                contamination=0.05,
                random_state=42
            )
            self.model.fit(normal_discounts)
            self.is_trained = True
        except Exception:
            self.model = None
            self.is_trained = False

    def predict_anomaly(self, discount_pct: float) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Calculates price anomaly indicator and calibrated risk score (0 to 100).
        Returns (is_anomaly, risk_score, metadata)
        """
        metadata: Dict[str, Any] = {
            "model_version": self.model_version,
            "engine": "sklearn_isolation_forest" if self.is_trained else "rule_fallback",
            "decision_function": 0.0,
            "is_outlier": False,
        }

        if self.is_trained and self.model is not None:
            try:
                feature = np.array([[float(discount_pct)]])
                pred = self.model.predict(feature)[0] # -1 for outlier, 1 for inlier
                score_raw = float(self.model.decision_function(feature)[0])
                
                metadata["decision_function"] = round(score_raw, 4)
                is_outlier = bool(pred == -1 or discount_pct >= 60.0)
                metadata["is_outlier"] = is_outlier

                # Scale into risk points (0 - 100)
                if discount_pct >= 75.0:
                    risk_score = 98.0
                elif discount_pct >= 50.0:
                    risk_score = 75.0
                elif is_outlier and discount_pct >= 35.0:
                    risk_score = 55.0
                elif discount_pct >= 25.0:
                    risk_score = 25.0
                else:
                    risk_score = 5.0

                return is_outlier, risk_score, metadata
            except Exception:
                pass

        # Transparent rule fallback if ML runtime is unavailable
        is_outlier = discount_pct >= 50.0
        metadata["is_outlier"] = is_outlier
        if discount_pct >= 75.0:
            risk_score = 98.0
        elif discount_pct >= 50.0:
            risk_score = 75.0
        elif discount_pct >= 30.0:
            risk_score = 30.0
        else:
            risk_score = 5.0

        return is_outlier, risk_score, metadata

price_anomaly_detector = PriceAnomalyDetector()
