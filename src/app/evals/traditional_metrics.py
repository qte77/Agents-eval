"""
Traditional metrics implementation for Tier 1 evaluation.

Provides fast, lightweight text similarity and execution metrics
using minimal dependencies with <1s performance target.
"""

from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import textdistance
from sklearn.feature_extraction.text import TfidfVectorizer

if TYPE_CHECKING:
    from app.evals.settings import JudgeSettings
from sklearn.metrics.pairwise import cosine_similarity

from app.data_models.evaluation_models import PeerReadEvalResult, Tier1Result
from app.data_models.peerread_models import PeerReadReview

# from torchmetrics.text import BERTScore  # Disabled due to build issues
from app.utils.log import logger


@dataclass
class SimilarityScores:
    """Container for similarity metric results."""

    cosine: float
    jaccard: float
    semantic: float
    levenshtein: float = 0.0  # Optional for backward compatibility


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

    def _compute_word_overlap_fallback(self, text1: str, text2: str) -> float:
        """Fallback to simple word overlap when TF-IDF fails."""
        words1 = set(re.findall(r"\w+", text1.lower()))
        words2 = set(re.findall(r"\w+", text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def compute_cosine_similarity(self, text1: str, text2: str) -> float:
        """Compute TF-IDF cosine similarity with enhanced error handling.

        Args:
            text1: Agent-generated review text
            text2: Reference review text

        Returns:
            Similarity score between 0.0 and 1.0

        Performance: ~50ms for typical review lengths
        """
        if not text1.strip() and not text2.strip():
            return 1.0
        if not text1.strip() or not text2.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer(stop_words="english", lowercase=True, max_features=1000)
            texts = [text1, text2]
            tfidf_matrix = vectorizer.fit_transform(texts)
            dense_matrix = tfidf_matrix.toarray()  # type: ignore[union-attr]
            similarity_matrix = cosine_similarity(dense_matrix[0:1], dense_matrix[1:2])
            score: float = similarity_matrix[0][0]  # type: ignore[assignment]
            return score

        except Exception as e:
            logger.warning(f"TF-IDF cosine similarity failed: {e}")
            try:
                return self._compute_word_overlap_fallback(text1, text2)
            except Exception:
                logger.warning("Cosine similarity calculation failed completely")
                return 0.0

    def _compute_jaccard_basic(self, text1: str, text2: str) -> float:
        """Basic word-based Jaccard implementation."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if len(words1) == 0 and len(words2) == 0:
            return 1.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

    def _compute_jaccard_regex_fallback(self, text1: str, text2: str) -> float:
        """Regex-based Jaccard fallback."""
        words1 = set(re.findall(r"\w+", text1.lower()))
        words2 = set(re.findall(r"\w+", text2.lower()))

        if not words1 and not words2:
            return 1.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

    def compute_jaccard_similarity(self, text1: str, text2: str, enhanced: bool = False) -> float:
        """Compute Jaccard similarity with optional textdistance enhancement.

        Args:
            text1: Agent-generated review text
            text2: Reference review text
            enhanced: Use textdistance library for robust calculation

        Returns:
            Similarity score between 0.0 and 1.0

        Performance: ~10ms for typical review lengths
        """
        if not text1.strip() and not text2.strip():
            return 1.0
        if not text1.strip() or not text2.strip():
            return 0.0

        if enhanced:
            try:
                return float(
                    textdistance.jaccard.normalized_similarity(text1.lower(), text2.lower())
                )
            except Exception as e:
                logger.warning(f"Enhanced Jaccard similarity failed: {e}")

        try:
            return self._compute_jaccard_basic(text1, text2)
        except Exception as e:
            logger.warning(f"Jaccard similarity calculation failed: {e}")
            try:
                return self._compute_jaccard_regex_fallback(text1, text2)
            except Exception:
                return 0.0

    def _compute_char_overlap_fallback(self, text1: str, text2: str) -> float:
        """Fallback to simple character overlap when Levenshtein fails."""
        text1_clean = text1.lower().strip()
        text2_clean = text2.lower().strip()

        if text1_clean == text2_clean:
            return 1.0

        chars1 = set(text1_clean)
        chars2 = set(text2_clean)
        intersection = len(chars1 & chars2)
        union = len(chars1 | chars2)

        return intersection / union if union > 0 else 0.0

    def compute_levenshtein_similarity(self, text1: str, text2: str) -> float:
        """Compute Levenshtein (edit distance) similarity using textdistance.

        Args:
            text1: Agent-generated review text
            text2: Reference review text

        Returns:
            Normalized Levenshtein similarity score between 0.0 and 1.0

        Performance: ~20ms for typical review lengths
        """
        if not text1.strip() and not text2.strip():
            return 1.0
        if not text1.strip() or not text2.strip():
            return 0.0

        try:
            return float(
                textdistance.levenshtein.normalized_similarity(text1.lower(), text2.lower())
            )
        except Exception as e:
            logger.warning(f"Levenshtein similarity calculation failed: {e}")
            try:
                return self._compute_char_overlap_fallback(text1, text2)
            except Exception:
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
        self, agent_output: str, reference_text: str, enhanced: bool = False
    ) -> SimilarityScores:
        """Compute all similarity metrics for a single reference.

        Args:
            agent_output: Generated review text
            reference_text: Single ground truth review
            enhanced: Enable enhanced similarity features (textdistance)

        Returns:
            SimilarityScores container with all computed metrics
        """
        cosine_score = self.compute_cosine_similarity(agent_output, reference_text)
        jaccard_score = self.compute_jaccard_similarity(
            agent_output, reference_text, enhanced=enhanced
        )
        semantic_score = self.compute_semantic_similarity(agent_output, reference_text)

        # Add Levenshtein similarity when enhanced mode is enabled
        levenshtein_score = 0.0
        if enhanced:
            levenshtein_score = self.compute_levenshtein_similarity(agent_output, reference_text)

        return SimilarityScores(
            cosine=cosine_score,
            jaccard=jaccard_score,
            semantic=semantic_score,
            levenshtein=levenshtein_score,
        )

    def find_best_match(
        self, agent_output: str, reference_texts: list[str], enhanced: bool = False
    ) -> SimilarityScores:
        """Find best matching reference and return its similarity scores.

        Args:
            agent_output: Generated review text
            reference_texts: List of ground truth reviews
            enhanced: Enable enhanced similarity features

        Returns:
            Best similarity scores across all reference texts
        """
        if not reference_texts:
            return SimilarityScores(cosine=0.0, jaccard=0.0, semantic=0.0, levenshtein=0.0)

        all_scores = [
            self.compute_all_similarities(agent_output, ref, enhanced=enhanced)
            for ref in reference_texts
        ]

        # Take maximum score for each metric (best match approach)
        best_cosine = max(scores.cosine for scores in all_scores)
        best_jaccard = max(scores.jaccard for scores in all_scores)
        best_semantic = max(scores.semantic for scores in all_scores)
        best_levenshtein = max(scores.levenshtein for scores in all_scores) if enhanced else 0.0

        return SimilarityScores(
            cosine=best_cosine,
            jaccard=best_jaccard,
            semantic=best_semantic,
            levenshtein=best_levenshtein,
        )

    def evaluate_traditional_metrics(
        self,
        agent_output: str,
        reference_texts: list[str],
        start_time: float,
        end_time: float,
        settings: JudgeSettings | None = None,
    ) -> Tier1Result:
        """Complete traditional metrics evaluation.

        Args:
            agent_output: Generated review text
            reference_texts: List of ground truth reviews
            start_time: Execution start timestamp
            end_time: Execution end timestamp
            settings: JudgeSettings instance. If None, uses defaults.

        Returns:
            Tier1Result with all traditional metrics
        """
        # Find best similarity scores across all references
        best_scores = self.find_best_match(agent_output, reference_texts)

        # Calculate execution metrics
        confidence_threshold = settings.tier1_confidence_threshold if settings else 0.8
        time_score = self.measure_execution_time(start_time, end_time)
        task_success = self.assess_task_success(best_scores, confidence_threshold)

        # Calculate weighted overall score
        overall_score = (
            best_scores.semantic * 0.4
            + best_scores.cosine * 0.3
            + best_scores.jaccard * 0.2
            + time_score * 0.1
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

    def evaluate_enhanced_similarity(
        self,
        agent_output: str,
        reference_texts: list[str],
        config_weights: dict[str, float] | None = None,
    ) -> float:
        """Enhanced multi-metric evaluation with config-driven weighting.

        This method provides enhanced similarity evaluation with:
        - Levenshtein similarity calculation
        - Config-driven weighting system
        - Enhanced error fallbacks
        - Multi-metric weighted combination

        Args:
            agent_output: Generated review text
            reference_texts: List of ground truth reviews
            config_weights: Optional weight configuration for metrics

        Returns:
            Weighted overall similarity score (0-1)
        """
        try:
            # Default balanced weights
            default_weights = {
                "cosine_weight": 0.4,
                "jaccard_weight": 0.4,
                "semantic_weight": 0.2,  # Maps to Levenshtein
            }

            weights = config_weights or default_weights

            # Find best matching scores with enhanced features enabled
            best_scores = self.find_best_match(agent_output, reference_texts, enhanced=True)

            # Calculate multiple similarity metrics
            cosine_sim = best_scores.cosine
            jaccard_sim = best_scores.jaccard
            levenshtein_sim = best_scores.levenshtein  # Semantic weight maps to Levenshtein

            # Weighted combination using config weights
            cosine_weight = weights.get("cosine_weight", 0.4)
            jaccard_weight = weights.get("jaccard_weight", 0.4)
            semantic_weight = weights.get("semantic_weight", 0.2)

            # Calculate weighted average
            weighted_score = (
                cosine_sim * cosine_weight
                + jaccard_sim * jaccard_weight
                + levenshtein_sim * semantic_weight
            )

            return min(1.0, max(0.0, weighted_score))

        except Exception as e:
            logger.warning(f"Enhanced similarity evaluation failed: {e}")
            # Fallback to basic Jaccard similarity
            try:
                basic_scores = self.find_best_match(agent_output, reference_texts)
                return basic_scores.jaccard
            except Exception:
                return 0.0


def evaluate_single_traditional(
    agent_output: str,
    reference_texts: list[str],
    settings: JudgeSettings | None = None,
) -> Tier1Result:
    """Convenience function for single traditional evaluation.

    Args:
        agent_output: Generated review text
        reference_texts: List of ground truth reviews
        settings: Optional JudgeSettings override. If None, uses defaults.

    Returns:
        Tier1Result with traditional metrics

    Example:
        >>> result = evaluate_single_traditional(
        ...     agent_output="This paper presents...",
        ...     reference_texts=["The work demonstrates...", "Strong contribution..."],
        ... )
        >>> print(f"Overall score: {result.overall_score:.3f}")
    """
    if settings is None:
        from app.evals.settings import JudgeSettings

        settings = JudgeSettings()
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
        settings=settings,
    )


def evaluate_single_enhanced(
    agent_output: str,
    reference_texts: list[str],
    config_weights: dict[str, float] | None = None,
) -> float:
    """Convenience function for enhanced similarity evaluation.

    This function provides the PeerRead-style evaluation workflow with
    Levenshtein similarity, config-driven weights, and enhanced error handling.

    Args:
        agent_output: Generated review text
        reference_texts: List of ground truth reviews
        config_weights: Optional weight configuration for similarity metrics

    Returns:
        Weighted overall similarity score (0-1)

    Example:
        >>> weights = {
        ...     "cosine_weight": 0.6,
        ...     "jaccard_weight": 0.4,
        ...     "semantic_weight": 0.0,
        ... }
        >>> result = evaluate_single_enhanced(
        ...     agent_output="This paper demonstrates strong methodology...",
        ...     reference_texts=[
        ...         "The work shows solid approach...",
        ...         "Good technical quality...",
        ...     ],
        ...     config_weights=weights,
        ... )
        >>> print(f"Enhanced similarity: {result:.3f}")
    """
    engine = TraditionalMetricsEngine()
    return engine.evaluate_enhanced_similarity(
        agent_output=agent_output,
        reference_texts=reference_texts,
        config_weights=config_weights,
    )


def create_evaluation_result(
    paper_id: str,
    agent_review: str,
    ground_truth_reviews: list[PeerReadReview],
) -> PeerReadEvalResult:
    """Create evaluation result comparing agent review to ground truth.

    This function creates comprehensive evaluation results
    using enhanced similarity evaluation capabilities.

    Args:
        paper_id: Paper identifier.
        agent_review: Review generated by agent.
        ground_truth_reviews: Original peer reviews.

    Returns:
        PeerReadEvalResult with similarity metrics.
    """
    # Extract reference texts for similarity calculation
    reference_texts = [review.comments for review in ground_truth_reviews]

    # Use enhanced similarity evaluation (equivalent to evaluate_review_similarity)
    overall_similarity = evaluate_single_enhanced(
        agent_output=agent_review,
        reference_texts=reference_texts,
        config_weights=None,  # Use default weights
    )

    # Calculate individual similarity metrics for detailed breakdown
    engine = TraditionalMetricsEngine()
    best_scores = engine.find_best_match(agent_review, reference_texts, enhanced=True)

    similarity_scores = {
        "cosine": best_scores.cosine,
        "jaccard": best_scores.jaccard,
        "semantic": best_scores.semantic,  # Levenshtein-based
    }

    # Simple recommendation matching (could be more sophisticated)
    agent_sentiment = "positive" if "good" in agent_review.lower() else "negative"
    gt_recommendations = [float(r.recommendation) for r in ground_truth_reviews]

    if len(gt_recommendations) == 0:
        # No ground truth to compare - default to False
        recommendation_match = False
    else:
        # Match original logic: use 3.0 as threshold for positive/negative
        avg_gt_recommendation = sum(gt_recommendations) / len(gt_recommendations)
        recommendation_match = (agent_sentiment == "positive" and avg_gt_recommendation >= 3.0) or (
            agent_sentiment == "negative" and avg_gt_recommendation < 3.0
        )

    return PeerReadEvalResult(
        paper_id=paper_id,
        agent_review=agent_review,
        ground_truth_reviews=ground_truth_reviews,
        similarity_scores=similarity_scores,
        overall_similarity=overall_similarity,
        recommendation_match=recommendation_match,
    )


# Convenience wrapper functions
def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts.

    Convenience wrapper for compute_cosine_similarity.
    Handles empty strings gracefully.

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Cosine similarity score (0-1)
    """
    # Handle empty strings like original implementation
    if not text1.strip() or not text2.strip():
        return 0.0

    engine = TraditionalMetricsEngine()
    return engine.compute_cosine_similarity(text1, text2)


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts.

    Backward compatibility wrapper for compute_jaccard_similarity with enhanced
    features.

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Enhanced Jaccard similarity score (0-1)
    """
    engine = TraditionalMetricsEngine()
    return engine.compute_jaccard_similarity(text1, text2, enhanced=True)


def evaluate_review_similarity(agent_review: str, ground_truth: str) -> float:
    """Evaluate similarity between agent review and ground truth.

    Backward compatibility wrapper for evaluate_enhanced_similarity.

    Args:
        agent_review: Review generated by agent
        ground_truth: Ground truth review text

    Returns:
        Weighted similarity score (0-1)
    """
    return evaluate_single_enhanced(
        agent_output=agent_review,
        reference_texts=[ground_truth],
        config_weights=None,  # Use default weights
    )
