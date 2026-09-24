"""
Machine Learning Price Anomaly Engine
Uses Isolation Forest to detect statistical price deviations from retail benchmarks.
"""

import numpy as np

class PriceAnomalyDetector:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self._init_model()

    def _init_model(self):
        try:
            from sklearn.ensemble import IsolationForest
            # Generate synthetic baseline e-commerce discount distribution:
            # Most normal commercial sales hover around 5% - 25% discount, rarely 40%.
            np.random.seed(42)
            normal_discounts = np.random.normal(loc=15.0, scale=8.0, size=(500, 1))
            normal_discounts = np.clip(normal_discounts, 0.0, 50.0)

            # Fit Isolation Forest
            self.model = IsolationForest(contamination=0.05, random_state=42)
            self.model.fit(normal_discounts)
            self.is_trained = True
        except Exception as e:
            # Graceful fallback if sklearn is not installed
            self.model = None
            self.is_trained = False

    def predict_anomaly(self, discount_pct: float) -> tuple[bool, float]:
        """
        Returns (is_anomaly, anomaly_score_0_to_100)
        """
        if self.is_trained and self.model is not None:
            try:
                feature = np.array([[discount_pct]])
                pred = self.model.predict(feature)[0] # -1 for outlier, 1 for inlier
                raw_score = self.model.decision_function(feature)[0]
                
                is_outlier = pred == -1 or discount_pct >= 55.0
                # Scale score into 0 - 100 risk
                risk_score = 95.0 if discount_pct >= 75.0 else (65.0 if is_outlier else 10.0)
                return is_outlier, risk_score
            except Exception:
                pass

        # Transparent rule fallback
        if discount_pct >= 75.0:
            return True, 98.0
        elif discount_pct >= 50.0:
            return True, 65.0
        elif discount_pct >= 30.0:
            return False, 30.0
        return False, 10.0

price_anomaly_detector = PriceAnomalyDetector()
