"""
NLP Review Pattern Analyzer
Uses Scikit-Learn TF-IDF vectorization and Pairwise Cosine Similarity
to detect synthetic review duplication, repetitive n-grams, and rating uniformity.
"""

from typing import List, Dict, Any

class ReviewNLPAnalyzer:
    def __init__(self):
        self.vectorizer = None
        self.model_version = "nlp_tfidf_cosine_v1.2.0"
        self._init_nlp()

    def _init_nlp(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words="english", min_df=1)
        except Exception:
            self.vectorizer = None

    def analyze_reviews(self, review_texts: List[str], ratings: List[float]) -> Dict[str, Any]:
        """
        Calculates exact duplicate count, maximum pairwise cosine similarity,
        repetitive phrase clusters, and rating uniformity.
        """
        sample_size = len(review_texts)
        if sample_size == 0:
            return {
                "similarity_score": 0.0,
                "has_duplicates": False,
                "max_pairwise_cosine": 0.0,
                "duplicate_count": 0,
                "sample_size": 0,
                "risk_score": 30.0,
                "confidence": 0.40,
                "reason": "No verifiable customer reviews found on listing."
            }

        # 1. Exact Duplicate Review Detection
        clean_reviews = [r.strip().lower() for r in review_texts if r.strip()]
        unique_reviews = set(clean_reviews)
        duplicate_count = len(clean_reviews) - len(unique_reviews)
        has_exact_duplicates = duplicate_count > 0

        # 2. Scikit-Learn TF-IDF Cosine Similarity Matrix
        max_cosine = 0.0
        if len(clean_reviews) >= 2 and self.vectorizer is not None:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                tfidf_matrix = self.vectorizer.fit_transform(clean_reviews)
                sim_matrix = cosine_similarity(tfidf_matrix)
                
                # Look at off-diagonal values (pairwise between distinct reviews)
                for i in range(len(clean_reviews)):
                    for j in range(i + 1, len(clean_reviews)):
                        pair_sim = float(sim_matrix[i, j])
                        if pair_sim > max_cosine:
                            max_cosine = pair_sim
            except Exception:
                max_cosine = 1.0 if has_exact_duplicates else 0.0
        elif has_exact_duplicates:
            max_cosine = 1.0

        # 3. Repeated N-Gram Phrase Clusters
        phrase_map: Dict[str, int] = {}
        duplicate_phrase_clusters = 0
        for text in clean_reviews:
            words = text.split()
            for i in range(len(words) - 2):
                tri_gram = " ".join(words[i:i+3])
                phrase_map[tri_gram] = phrase_map.get(tri_gram, 0) + 1

        for _, count in phrase_map.items():
            if count >= 2:
                duplicate_phrase_clusters += 1

        # 4. Rating Uniformity Analysis
        is_uniform_perfect = False
        if ratings and len(ratings) >= 3:
            is_uniform_perfect = all(r == 5.0 for r in ratings)

        # 5. Composite Review Risk Scoring
        risk_score = 10.0
        reasons = []

        if has_exact_duplicates or max_cosine >= 0.85:
            risk_score = 95.0
            reasons.append(f"Detected {duplicate_count} duplicate reviews with high syntactic similarity ({max_cosine:.2f} cosine)")
        elif duplicate_phrase_clusters >= 3 or max_cosine >= 0.65:
            risk_score = 75.0
            reasons.append(f"Repetitive phrasing across reviews ({duplicate_phrase_clusters} duplicate 3-gram clusters)")
        elif is_uniform_perfect:
            risk_score = 50.0
            reasons.append("Unnatural 100% five-star rating uniformity without variance")
        else:
            reasons.append(f"Analyzed {sample_size} review(s); natural linguistic variation and sentiment distribution")

        return {
            "similarity_score": round(max_cosine, 3),
            "max_pairwise_cosine": round(max_cosine, 3),
            "has_duplicates": has_exact_duplicates,
            "duplicate_count": duplicate_count,
            "duplicate_clusters": duplicate_phrase_clusters,
            "is_uniform_perfect": is_uniform_perfect,
            "sample_size": sample_size,
            "confidence": min(1.0, 0.4 + (sample_size * 0.15)),
            "risk_score": risk_score,
            "reason": reasons[0]
        }

review_nlp_analyzer = ReviewNLPAnalyzer()
