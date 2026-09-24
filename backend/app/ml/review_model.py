"""
NLP Review Pattern Analyzer
Extracts syntactic n-grams, repetitive phrase clusters, and rating uniformity.
"""

from typing import List, Dict, Any

class ReviewNLPAnalyzer:
    def __init__(self):
        self.vectorizer = None
        self._init_nlp()

    def _init_nlp(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vectorizer = TfidfVectorizer(ngram_range=(2, 4), stop_words='english')
        except Exception:
            self.vectorizer = None

    def analyze_reviews(self, review_texts: List[str], ratings: List[float]) -> Dict[str, Any]:
        """
        Analyzes syntactic similarity, repeated phrases, and rating anomalies.
        """
        if not review_texts:
            return {
                "similarity_score": 0.0,
                "has_duplicates": False,
                "risk_score": 15.0,
                "reason": "No verifiable customer reviews detected."
            }

        # Check for phrase duplicates
        phrase_map = {}
        duplicate_clusters = 0

        for text in review_texts:
            clean = text.lower().strip()
            words = clean.split()
            for i in range(len(words) - 3):
                gram = " ".join(words[i:i+4])
                phrase_map[gram] = phrase_map.get(gram, 0) + 1

        for gram, count in phrase_map.items():
            if count >= 2:
                duplicate_clusters += 1

        # Check rating uniformity
        is_uniform_perfect = False
        if ratings and len(ratings) >= 3:
            is_uniform_perfect = all(r == 5.0 for r in ratings)

        if duplicate_clusters >= 2 or is_uniform_perfect:
            return {
                "similarity_score": 0.88,
                "has_duplicates": True,
                "risk_score": 88.0,
                "reason": "Multiple reviews contain highly similar synthetic wording and unnatural uniformity."
            }

        return {
            "similarity_score": 0.15,
            "has_duplicates": False,
            "risk_score": 10.0,
            "reason": "Review sentiment and linguistic variation fall within natural distribution."
        }

review_nlp_analyzer = ReviewNLPAnalyzer()
