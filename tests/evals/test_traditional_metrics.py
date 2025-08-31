"""
BDD-style tests for traditional metrics engine.

Test the core functionality of Tier 1 evaluation using lightweight
text similarity metrics and execution timing measurement.
"""

import time
from unittest.mock import Mock, patch

import pytest

from app.data_models.evaluation_models import Tier1Result
from app.evals.traditional_metrics import (
    TraditionalMetricsEngine,
    evaluate_single_traditional,
)


class TestTraditionalMetricsEngine:
    """Test suite for traditional metrics engine."""

    @pytest.fixture
    def engine(self):
        """Fixture providing TraditionalMetricsEngine instance."""
        return TraditionalMetricsEngine()

    @pytest.fixture
    def sample_texts(self):
        """Fixture providing sample text pairs for similarity testing."""
        return {
            "identical": ("The quick brown fox", "The quick brown fox"),
            "similar": ("The quick brown fox jumps", "The quick brown fox leaps"),
            "different": ("The quick brown fox", "Machine learning algorithms"),
            "empty_first": ("", "Some text"),
            "empty_both": ("", ""),
            "academic_review": (
                "This paper presents a novel approach to machine learning with "
                "solid methodology and clear results.",
                "The work demonstrates strong technical contribution with "
                "comprehensive evaluation and good presentation.",
            ),
        }

    # Cosine similarity tests
    def test_cosine_similarity_identical_texts(self, engine, sample_texts):
        """Given identical texts, cosine similarity should be 1.0."""
        text1, text2 = sample_texts["identical"]
        similarity = engine.compute_cosine_similarity(text1, text2)
        assert similarity == 1.0

    def test_cosine_similarity_similar_texts(self, engine, sample_texts):
        """Given similar texts, cosine similarity should be high."""
        text1, text2 = sample_texts["similar"]
        similarity = engine.compute_cosine_similarity(text1, text2)
        assert 0.5 < similarity < 1.0

    def test_cosine_similarity_different_texts(self, engine, sample_texts):
        """Given different texts, cosine similarity should be lower."""
        text1, text2 = sample_texts["different"]
        similarity = engine.compute_cosine_similarity(text1, text2)
        assert 0.0 <= similarity < 0.5

    def test_cosine_similarity_empty_texts(self, engine, sample_texts):
        """Given empty texts, should handle gracefully."""
        text1, text2 = sample_texts["empty_both"]
        similarity = engine.compute_cosine_similarity(text1, text2)
        assert similarity == 1.0  # Empty texts are considered identical

        text1, text2 = sample_texts["empty_first"]
        similarity = engine.compute_cosine_similarity(text1, text2)
        assert similarity == 0.0

    # Jaccard similarity tests
    def test_jaccard_similarity_identical_texts(self, engine, sample_texts):
        """Given identical texts, Jaccard similarity should be 1.0."""
        text1, text2 = sample_texts["identical"]
        similarity = engine.compute_jaccard_similarity(text1, text2)
        assert similarity == 1.0

    def test_jaccard_similarity_overlapping_words(self, engine, sample_texts):
        """Given texts with word overlap, should compute correct Jaccard index."""
        text1, text2 = sample_texts["similar"]
        similarity = engine.compute_jaccard_similarity(text1, text2)
        assert 0.5 < similarity < 1.0  # Some word overlap expected

    def test_jaccard_similarity_no_overlap(self, engine, sample_texts):
        """Given texts with no word overlap, Jaccard similarity should be 0.0."""
        text1, text2 = sample_texts["different"]
        similarity = engine.compute_jaccard_similarity(text1, text2)
        assert similarity == 0.0  # No common words

    def test_jaccard_similarity_case_insensitive(self, engine):
        """Jaccard similarity should be case insensitive."""
        text1 = "The Quick Brown FOX"
        text2 = "the quick brown fox"
        similarity = engine.compute_jaccard_similarity(text1, text2)
        assert similarity == 1.0

    # Semantic similarity tests (with mocking to avoid model dependencies)
    @patch(
        "app.evals.traditional_metrics.TraditionalMetricsEngine._get_bertscore_model"
    )
    def test_semantic_similarity_with_bertscore(
        self, mock_bertscore, engine, sample_texts
    ):
        """Given BERTScore model, should compute semantic similarity."""
        # Mock BERTScore model
        mock_model = Mock()
        mock_model.return_value = {"f1": [0.85]}
        mock_bertscore.return_value = mock_model

        text1, text2 = sample_texts["academic_review"]
        similarity = engine.compute_semantic_similarity(text1, text2)

        assert similarity == 0.85
        mock_model.assert_called_once_with([text1], [text2])

    @patch(
        "app.evals.traditional_metrics.TraditionalMetricsEngine._get_bertscore_model"
    )
    def test_semantic_similarity_fallback_on_error(
        self, mock_bertscore, engine, sample_texts
    ):
        """Given BERTScore failure, should fallback to cosine similarity."""
        # Mock BERTScore to raise exception
        mock_bertscore.side_effect = Exception("Model loading failed")

        text1, text2 = sample_texts["similar"]
        with patch.object(
            engine, "compute_cosine_similarity", return_value=0.7
        ) as mock_cosine:
            similarity = engine.compute_semantic_similarity(text1, text2)
            assert similarity == 0.7
            mock_cosine.assert_called_once_with(text1, text2)

    # Execution time measurement tests
    def test_execution_time_measurement(self, engine):
        """Given start and end times, should compute normalized time score."""
        start_time = 1000.0
        end_time = 1001.5  # 1.5 seconds

        time_score = engine.measure_execution_time(start_time, end_time)

        assert 0.0 < time_score <= 1.0
        # Faster execution should give higher score
        fast_score = engine.measure_execution_time(1000.0, 1000.1)  # 0.1 seconds
        assert fast_score > time_score

    def test_execution_time_minimum_duration(self, engine):
        """Given very small duration, should enforce minimum 1ms."""
        start_time = 1000.0
        end_time = 1000.0  # Same time

        time_score = engine.measure_execution_time(start_time, end_time)
        assert 0.0 < time_score <= 1.0  # Should not be zero due to minimum duration

    # Task success assessment tests
    def test_task_success_above_threshold(self, engine):
        """Given similarity scores above threshold, task should succeed."""
        from app.evals.traditional_metrics import SimilarityScores

        scores = SimilarityScores(cosine=0.85, jaccard=0.80, semantic=0.90)
        success = engine.assess_task_success(scores, threshold=0.8)

        assert success == 1.0

    def test_task_success_below_threshold(self, engine):
        """Given similarity scores below threshold, task should fail."""
        from app.evals.traditional_metrics import SimilarityScores

        scores = SimilarityScores(cosine=0.5, jaccard=0.4, semantic=0.6)
        success = engine.assess_task_success(scores, threshold=0.8)

        assert success == 0.0

    def test_task_success_weighted_average(self, engine):
        """Task success should use weighted average of similarity metrics."""
        from app.evals.traditional_metrics import SimilarityScores

        # High semantic (weight 0.5), low others
        scores = SimilarityScores(cosine=0.1, jaccard=0.1, semantic=0.9)
        success = engine.assess_task_success(scores, threshold=0.5)

        # Weighted average: 0.1*0.3 + 0.1*0.2 + 0.9*0.5 = 0.5
        assert success == 1.0  # Should pass threshold

    # Integration tests
    def test_find_best_match_multiple_references(self, engine):
        """Given multiple reference texts, should find best match."""
        agent_output = "The work shows strong methodology and clear results."
        references = [
            "Poor methodology and unclear presentation.",  # Low similarity
            "Strong methodology with excellent results.",  # High similarity
            "Different topic entirely about databases.",  # Very low similarity
        ]

        with patch.object(
            engine, "compute_cosine_similarity", side_effect=[0.2, 0.9, 0.1]
        ):
            with patch.object(
                engine, "compute_jaccard_similarity", side_effect=[0.1, 0.8, 0.0]
            ):
                with patch.object(
                    engine, "compute_semantic_similarity", side_effect=[0.3, 0.95, 0.1]
                ):
                    best_scores = engine.find_best_match(agent_output, references)

                    # Should pick the best scores (from second reference)
                    assert best_scores.cosine == 0.9
                    assert best_scores.jaccard == 0.8
                    assert best_scores.semantic == 0.95

    def test_find_best_match_empty_references(self, engine):
        """Given empty reference list, should return zero scores."""
        agent_output = "Some output text"
        references = []

        best_scores = engine.find_best_match(agent_output, references)

        assert best_scores.cosine == 0.0
        assert best_scores.jaccard == 0.0
        assert best_scores.semantic == 0.0

    def test_evaluate_traditional_metrics_complete(self, engine):
        """Complete traditional metrics evaluation should return valid Tier1Result."""
        agent_output = "The paper demonstrates solid methodology and clear results."
        reference_texts = [
            "Strong technical contribution with good methodology.",
            "Clear presentation but methodology needs improvement.",
        ]
        start_time = time.perf_counter()
        time.sleep(0.01)  # Small delay to measure
        end_time = time.perf_counter()

        config = {
            "confidence_threshold": 0.7,
            "tier1_weights": {
                "semantic": 0.4,
                "cosine": 0.3,
                "jaccard": 0.2,
                "time_taken": 0.1,
            },
        }

        with patch.object(engine, "find_best_match") as mock_best_match:
            from app.evals.traditional_metrics import SimilarityScores

            mock_best_match.return_value = SimilarityScores(
                cosine=0.8, jaccard=0.7, semantic=0.85
            )

            result = engine.evaluate_traditional_metrics(
                agent_output, reference_texts, start_time, end_time, config
            )

            assert isinstance(result, Tier1Result)
            assert result.cosine_score == 0.8
            assert result.jaccard_score == 0.7
            assert result.semantic_score == 0.85
            assert result.execution_time > 0.0
            assert result.time_score > 0.0
            assert result.task_success in [0.0, 1.0]
            assert 0.0 <= result.overall_score <= 1.0


# Convenience function tests
def test_evaluate_single_traditional():
    """Test convenience function for single traditional evaluation."""
    agent_output = "This is a test review with good methodology."
    reference_texts = ["Test review with solid approach."]

    with patch(
        "app.evals.traditional_metrics.TraditionalMetricsEngine"
    ) as mock_engine_class:
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine

        # Mock the evaluation result
        mock_result = Mock(spec=Tier1Result)
        mock_engine.evaluate_traditional_metrics.return_value = mock_result

        result = evaluate_single_traditional(agent_output, reference_texts)

        assert result == mock_result
        mock_engine.evaluate_traditional_metrics.assert_called_once()


# Performance tests
class TestTraditionalMetricsPerformance:
    """Performance tests for traditional metrics engine."""

    def test_performance_target_under_1_second(self):
        """Complete traditional evaluation should complete under 1 second."""
        engine = TraditionalMetricsEngine()
        agent_output = (
            "This paper presents a comprehensive evaluation of machine "
            "learning algorithms with detailed experimental validation "
            "and thorough analysis of results."
        )
        reference_texts = [
            "The work provides extensive experimental validation of ML approaches "
            "with comprehensive analysis.",
            "Strong experimental methodology with detailed analysis and good "
            "presentation quality.",
            "Thorough evaluation with solid methodology but could improve "
            "presentation clarity.",
        ]

        start_time = time.perf_counter()

        # Use actual implementation for performance test
        config = {"confidence_threshold": 0.8}
        result = engine.evaluate_traditional_metrics(
            agent_output, reference_texts, start_time, start_time + 0.1, config
        )

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Should complete under 1 second (Day 2 performance target)
        assert duration < 1.0
        assert isinstance(result, Tier1Result)

    def test_similarity_computation_speed(self):
        """Individual similarity computations should be fast."""
        engine = TraditionalMetricsEngine()
        text1 = (
            "Machine learning algorithms for natural language processing applications."
        )
        text2 = (
            "Deep learning approaches to NLP tasks and language understanding problems."
        )

        # Test cosine similarity speed
        start = time.perf_counter()
        for _ in range(10):  # Multiple iterations
            engine.compute_cosine_similarity(text1, text2)
        cosine_duration = (time.perf_counter() - start) / 10

        # Should be under 100ms per computation
        assert cosine_duration < 0.1

        # Test Jaccard similarity speed
        start = time.perf_counter()
        for _ in range(10):
            engine.compute_jaccard_similarity(text1, text2)
        jaccard_duration = (time.perf_counter() - start) / 10

        # Should be under 10ms per computation
        assert jaccard_duration < 0.01
