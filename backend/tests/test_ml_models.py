"""
Automated Test Suite: Machine Learning Anomaly Detection & NLP Review Analysis
Validates Isolation Forest price anomaly detection and TF-IDF pairwise cosine similarity.
"""

import pytest
from app.ml.price_model import PriceAnomalyDetector
from app.ml.review_model import ReviewNLPAnalyzer

def test_price_anomaly_isolation_forest_normal_discount():
    detector = PriceAnomalyDetector()
    assert detector.is_trained is True

    # 15% discount is normal competitive pricing in e-commerce
    is_anomaly, risk_score, meta = detector.predict_anomaly(15.0)
    assert is_anomaly is False
    assert risk_score <= 30.0
    assert meta["engine"] == "sklearn_isolation_forest"

def test_price_anomaly_isolation_forest_extreme_scam_discount():
    detector = PriceAnomalyDetector()
    
    # 85% discount on flagship electronics is a strong fraud anomaly indicator
    is_anomaly, risk_score, meta = detector.predict_anomaly(85.0)
    assert is_anomaly is True
    assert risk_score >= 80.0
    assert meta["is_outlier"] is True

def test_price_anomaly_fallback_when_untrained():
    detector = PriceAnomalyDetector()
    detector.is_trained = False
    detector.model = None

    is_anomaly, score, meta = detector.predict_anomaly(90.0)
    assert is_anomaly is True
    assert score >= 70.0
    assert meta["engine"] == "rule_fallback"

def test_review_nlp_exact_duplicate_detection():
    analyzer = ReviewNLPAnalyzer()
    reviews = [
        "Received original iPhone 16 Pro super fast shipping five stars!",
        "Received original iPhone 16 Pro super fast shipping five stars!",
        "Received original iPhone 16 Pro super fast shipping five stars!"
    ]
    ratings = [5.0, 5.0, 5.0]

    result = analyzer.analyze_reviews(reviews, ratings)
    assert result["has_duplicates"] is True
    assert result["duplicate_count"] == 2
    assert result["max_pairwise_cosine"] >= 0.99
    assert result["risk_score"] >= 70.0
    assert result["sample_size"] == 3

def test_review_nlp_diverse_authentic_reviews():
    analyzer = ReviewNLPAnalyzer()
    reviews = [
        "The battery life is decent, lasts about a day and a half with normal usage.",
        "Camera quality in low light is somewhat noisy compared to the previous model.",
        "Delivered on time, packaging had minor dents but phone was untouched."
    ]
    ratings = [4.0, 3.0, 5.0]

    result = analyzer.analyze_reviews(reviews, ratings)
    assert result["has_duplicates"] is False
    assert result["duplicate_count"] == 0
    assert result["max_pairwise_cosine"] < 0.60
    assert result["risk_score"] < 40.0
    assert result["sample_size"] == 3

def test_review_nlp_empty_sample_size_disclosure():
    analyzer = ReviewNLPAnalyzer()
    result = analyzer.analyze_reviews([], [])
    assert result["sample_size"] == 0
    assert result["has_duplicates"] is False
    assert "verifiable" in result["reason"].lower()
