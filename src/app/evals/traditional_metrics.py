"""
Traditional metrics implementation for Tier 1 evaluation.

Provides fast, lightweight text similarity and execution metrics
using minimal dependencies with <1s performance target.
"""

import math
import time
from dataclasses import dataclass
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data_models.evaluation_models import Tier1Result

# from torchmetrics.text import BERTScore  # Disabled due to build issues
from app.utils.log import logger


@dataclass
class SimilarityScores:
    """Container for similarity metric results."""

    cosine: float
    jaccard: float
    semantic: float


class TraditionalMetricsEngine:
    """Lightweight traditional metrics engine for fast evaluation.

    Implements text similarity metrics using minimal computational resources
    with performance targets under 1 second for typical academic reviews.
    """

    def __init__(self):
        """Initialize metrics engine with cached components.

        Uses lazy loading for computationally expensive components
        to minimize startup time and memory usage.
        """
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,  # Limit for performance
        )
        self._bertscore = None  # Lazy loading

    def _get_bertscore_model(self):
        """BERTScore model unavailable due to build issues.

        Returns:
            None - BERTScore disabled
        """
        # BERTScore disabled due to sentencepiece build issues
        return None

    def compute_cosine_similarity(self, text1: str, text2: str) -> float:
        """Compute TF-IDF cosine similarity between two texts.

        Args:
            text1: Agent-generated review text
            text2: Reference review text

        Returns:
            Similarity score between 0.0 and 1.0

        Performance: ~50ms for typical review lengths
        """
        try:
            if not text1.strip() or not text2.strip():
                return 1.0 if text1 == text2 else 0.0

            # Create TF-IDF vectors
            tfidf_matrix = self._vectorizer.fit_transform([text1, text2])

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])

        except Exception as e:
            logger.warning(f"Cosine similarity calculation failed: {e}")
            return 0.0

    def compute_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Compute word-level Jaccard similarity.

        Args:
            text1: Agent-generated review text
            text2: Reference review text

        Returns:
            Similarity score between 0.0 and 1.0

        Performance: ~10ms for typical review lengths
        """
        try:
            # Tokenize and convert to sets
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            if len(words1) == 0 and len(words2) == 0:
                return 1.0

            # Calculate Jaccard index
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))

            return intersection / union if union > 0 else 0.0

        except Exception as e:
            logger.warning(f"Jaccard similarity calculation failed: {e}")
            return 0.0

    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity using cosine similarity fallback.

        Args:
            text1: Agent-generated review text
            text2: Reference review text

        Returns:
            Cosine similarity between 0.0 and 1.0 (BERTScore disabled)

        Performance: ~50ms using TF-IDF cosine similarity
        """
        try:
            # BERTScore disabled due to build issues, use cosine similarity
            logger.debug("Using cosine similarity fallback for semantic similarity")
            return self.compute_cosine_similarity(text1, text2)

        except Exception as e:
            logger.warning(f"Semantic similarity calculation failed: {e}")
            return 0.0

    def measure_execution_time(self, start_time: float, end_time: float) -> float:
        """Calculate execution time with normalization for scoring.

        Args:
            start_time: Start timestamp (from time.perf_counter())
            end_time: End timestamp (from time.perf_counter())

        Returns:
            Normalized time score for composite scoring (0.0-1.0)
        """
        duration = max(0.001, end_time - start_time)  # Minimum 1ms

        # Normalize using exponential decay: faster is better
        # Formula: exp(-duration) with max at 1.0 for very fast execution
        normalized_score = math.exp(-duration)
        return max(0.0, min(1.0, normalized_score))

    def assess_task_success(
        self, similarity_scores: SimilarityScores, threshold: float = 0.8
    ) -> float:
        """Assess task completion success based on similarity threshold.

        Args:
            similarity_scores: Container with semantic, cosine, jaccard scores
            threshold: Minimum similarity for success (from config)

        Returns:
            1.0 for success, 0.0 for failure
        """
        try:
            # Weighted average of similarity metrics
            weights = {"semantic": 0.5, "cosine": 0.3, "jaccard": 0.2}

            overall_similarity = (
                similarity_scores.semantic * weights["semantic"]
                + similarity_scores.cosine * weights["cosine"]
                + similarity_scores.jaccard * weights["jaccard"]
            )

            return 1.0 if overall_similarity >= threshold else 0.0

        except Exception as e:
            logger.warning(f"Task success assessment failed: {e}")
            return 0.0

    def compute_all_similarities(
        self, agent_output: str, reference_text: str
    ) -> SimilarityScores:
        """Compute all similarity metrics for a single reference.

        Args:
            agent_output: Generated review text
            reference_text: Single ground truth review

        Returns:
            SimilarityScores container with all computed metrics
        """
        cosine_score = self.compute_cosine_similarity(agent_output, reference_text)
        jaccard_score = self.compute_jaccard_similarity(agent_output, reference_text)
        semantic_score = self.compute_semantic_similarity(agent_output, reference_text)

        return SimilarityScores(
            cosine=cosine_score, jaccard=jaccard_score, semantic=semantic_score
        )

    def find_best_match(
        self, agent_output: str, reference_texts: list[str]
    ) -> SimilarityScores:
        """Find best matching reference and return its similarity scores.

        Args:
            agent_output: Generated review text
            reference_texts: List of ground truth reviews

        Returns:
            Best similarity scores across all reference texts
        """
        if not reference_texts:
            return SimilarityScores(cosine=0.0, jaccard=0.0, semantic=0.0)

        all_scores = [
            self.compute_all_similarities(agent_output, ref) for ref in reference_texts
        ]

        # Take maximum score for each metric (best match approach)
        best_cosine = max(scores.cosine for scores in all_scores)
        best_jaccard = max(scores.jaccard for scores in all_scores)
        best_semantic = max(scores.semantic for scores in all_scores)

        return SimilarityScores(
            cosine=best_cosine, jaccard=best_jaccard, semantic=best_semantic
        )

    def evaluate_traditional_metrics(
        self,
        agent_output: str,
        reference_texts: list[str],
        start_time: float,
        end_time: float,
        config: dict[str, Any],
    ) -> Tier1Result:
        """Complete traditional metrics evaluation.

        Args:
            agent_output: Generated review text
            reference_texts: List of ground truth reviews
            start_time: Execution start timestamp
            end_time: Execution end timestamp
            config: Configuration from config_eval.json

        Returns:
            Tier1Result with all traditional metrics
        """
        # Find best similarity scores across all references
        best_scores = self.find_best_match(agent_output, reference_texts)

        # Calculate execution metrics
        time_score = self.measure_execution_time(start_time, end_time)
        task_success = self.assess_task_success(
            best_scores, config.get("confidence_threshold", 0.8)
        )

        # Calculate weighted overall score
        weights = config.get(
            "tier1_weights",
            {"semantic": 0.4, "cosine": 0.3, "jaccard": 0.2, "time_taken": 0.1},
        )

        overall_score = (
            best_scores.semantic * weights.get("semantic", 0.4)
            + best_scores.cosine * weights.get("cosine", 0.3)
            + best_scores.jaccard * weights.get("jaccard", 0.2)
            + time_score * weights.get("time_taken", 0.1)
        )

        return Tier1Result(
            cosine_score=best_scores.cosine,
            jaccard_score=best_scores.jaccard,
            semantic_score=best_scores.semantic,
            execution_time=end_time - start_time,
            time_score=time_score,
            task_success=task_success,
            overall_score=overall_score,
        )


def evaluate_single_traditional(
    agent_output: str,
    reference_texts: list[str],
    config: dict[str, Any] | None = None,
) -> Tier1Result:
    """Convenience function for single traditional evaluation.

    Args:
        agent_output: Generated review text
        reference_texts: List of ground truth reviews
        config: Optional configuration override

    Returns:
        Tier1Result with traditional metrics

    Example:
        >>> result = evaluate_single_traditional(
        ...     agent_output="This paper presents...",
        ...     reference_texts=["The work demonstrates...", "Strong contribution..."],
        ... )
        >>> print(f"Overall score: {result.overall_score:.3f}")
    """
    config = config or {}
    engine = TraditionalMetricsEngine()

    start_time = time.perf_counter()
    # Simulate minimal processing time for timing measurement
    time.sleep(0.001)
    end_time = time.perf_counter()

    return engine.evaluate_traditional_metrics(
        agent_output=agent_output,
        reference_texts=reference_texts,
        start_time=start_time,
        end_time=end_time,
        config=config,
    )
