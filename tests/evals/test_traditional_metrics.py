"""
BDD-style tests for traditional metrics engine.

Test the core functionality of Tier 1 evaluation using lightweight
text similarity metrics and execution timing measurement.
"""

import time
from unittest.mock import Mock, patch

import pytest

from app.data_models.evaluation_models import Tier1Result
from app.judge.traditional_metrics import (
    TraditionalMetricsEngine,
    evaluate_single_enhanced,
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
                "This paper presents a novel approach to machine learning with solid methodology and clear results.",
                "The work demonstrates strong technical contribution with "
                "comprehensive evaluation and good presentation.",
            ),
        }

    # Cosine similarity tests
    def test_cosine_similarity_identical_texts(self, engine, sample_texts):
        """Given identical texts, cosine similarity should be 1.0."""
        text1, text2 = sample_texts["identical"]
        similarity = engine.compute_cosine_similarity(text1, text2)
        assert abs(similarity - 1.0) < 1e-10  # Account for floating-point precision

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

    # Semantic similarity tests (with mocking to avoid model dependencies)
    def test_semantic_similarity_with_bertscore(self, engine, sample_texts):
        """Semantic similarity should use cosine similarity fallback."""
        text1, text2 = sample_texts["academic_review"]

        # Mock cosine similarity to return known value
        with patch.object(engine, "compute_cosine_similarity", return_value=0.85) as mock_cosine:
            similarity = engine.compute_semantic_similarity(text1, text2)
            assert similarity == 0.85
            mock_cosine.assert_called_once_with(text1, text2)

    @patch("app.judge.traditional_metrics.TraditionalMetricsEngine._get_bertscore_model")
    def test_semantic_similarity_fallback_on_error(self, mock_bertscore, engine, sample_texts):
        """Given BERTScore failure, should fallback to cosine similarity."""
        # Mock BERTScore to raise exception
        mock_bertscore.side_effect = Exception("Model loading failed")

        text1, text2 = sample_texts["similar"]
        with patch.object(engine, "compute_cosine_similarity", return_value=0.7) as mock_cosine:
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
        from app.judge.traditional_metrics import SimilarityScores

        scores = SimilarityScores(cosine=0.85, jaccard=0.80, semantic=0.90)
        success = engine.assess_task_success(scores, threshold=0.8)

        assert success == 1.0

    def test_task_success_below_threshold(self, engine):
        """Given similarity scores below threshold, task should fail."""
        from app.judge.traditional_metrics import SimilarityScores

        scores = SimilarityScores(cosine=0.5, jaccard=0.4, semantic=0.6)
        success = engine.assess_task_success(scores, threshold=0.8)

        assert success == 0.0

    def test_task_success_weighted_average(self, engine):
        """Task success should use weighted average of similarity metrics."""
        from app.judge.traditional_metrics import SimilarityScores

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

        with patch.object(engine, "compute_cosine_similarity", side_effect=[0.2, 0.9, 0.1]):
            with patch.object(engine, "compute_jaccard_similarity", side_effect=[0.1, 0.8, 0.0]):
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

        from app.judge.settings import JudgeSettings

        settings = JudgeSettings(tier1_confidence_threshold=0.7)

        with patch.object(engine, "find_best_match") as mock_best_match:
            from app.judge.traditional_metrics import SimilarityScores

            mock_best_match.return_value = SimilarityScores(cosine=0.8, jaccard=0.7, semantic=0.85)

            result = engine.evaluate_traditional_metrics(
                agent_output, reference_texts, start_time, end_time, settings
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

    with patch("app.judge.traditional_metrics.TraditionalMetricsEngine") as mock_engine_class:
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
            "The work provides extensive experimental validation of ML approaches with comprehensive analysis.",
            "Strong experimental methodology with detailed analysis and good presentation quality.",
            "Thorough evaluation with solid methodology but could improve presentation clarity.",
        ]

        start_time = time.perf_counter()

        # Use actual implementation for performance test
        result = engine.evaluate_traditional_metrics(
            agent_output, reference_texts, start_time, start_time + 0.1
        )

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Should complete under 1 second (Day 2 performance target)
        assert duration < 1.0
        assert isinstance(result, Tier1Result)

    def test_similarity_computation_speed(self):
        """Individual similarity computations should be fast."""
        engine = TraditionalMetricsEngine()
        text1 = "Machine learning algorithms for natural language processing applications."
        text2 = "Deep learning approaches to NLP tasks and language understanding problems."

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


# Enhanced features tests
class TestEnhancedFeatures:
    """Test suite for enhanced similarity features in traditional metrics."""

    @pytest.fixture
    def engine(self):
        """Fixture providing TraditionalMetricsEngine instance."""
        return TraditionalMetricsEngine()

    def test_levenshtein_similarity_identical_texts(self, engine):
        """Levenshtein similarity should be 1.0 for identical texts."""
        text1 = "This is a test review"
        text2 = "This is a test review"
        similarity = engine.compute_levenshtein_similarity(text1, text2)
        assert similarity == 1.0

    def test_levenshtein_similarity_similar_texts(self, engine):
        """Levenshtein similarity should give reasonable scores for similar texts."""
        text1 = "This paper presents good methodology"
        text2 = "This paper shows good methodology"
        similarity = engine.compute_levenshtein_similarity(text1, text2)
        assert 0.8 < similarity < 1.0  # Should be high similarity

    def test_levenshtein_similarity_different_texts(self, engine):
        """Levenshtein similarity should give low scores for different texts."""
        text1 = "Machine learning algorithms"
        text2 = "Database query optimization"
        similarity = engine.compute_levenshtein_similarity(text1, text2)
        assert 0.0 <= similarity < 0.5  # Should be low similarity

    def test_levenshtein_similarity_empty_texts(self, engine):
        """Levenshtein similarity should handle empty texts gracefully."""
        # Both empty
        similarity = engine.compute_levenshtein_similarity("", "")
        assert similarity == 1.0

        # One empty
        similarity = engine.compute_levenshtein_similarity("text", "")
        assert similarity == 0.0

    def test_enhanced_jaccard_similarity(self, engine):
        """Enhanced Jaccard similarity should use textdistance when enabled."""
        text1 = "machine learning algorithms"
        text2 = "machine learning methods"

        # Test enhanced mode
        enhanced_score = engine.compute_jaccard_similarity(text1, text2, enhanced=True)
        basic_score = engine.compute_jaccard_similarity(text1, text2, enhanced=False)

        # Both should give reasonable scores
        assert 0.0 <= enhanced_score <= 1.0
        assert 0.0 <= basic_score <= 1.0
        assert enhanced_score > 0.5  # Should show similarity

    def test_compute_all_similarities_with_enhancement(self, engine):
        """Enhanced compute_all_similarities should include Levenshtein scores."""
        agent_output = "This paper demonstrates solid methodology and clear results."
        reference = "The work shows strong methodology with excellent results."

        # Test basic mode
        basic_scores = engine.compute_all_similarities(agent_output, reference, enhanced=False)
        assert basic_scores.levenshtein == 0.0  # Should be 0 in basic mode

        # Test enhanced mode
        enhanced_scores = engine.compute_all_similarities(agent_output, reference, enhanced=True)
        assert enhanced_scores.levenshtein > 0.0  # Should have Levenshtein score
        assert 0.0 <= enhanced_scores.levenshtein <= 1.0

    def test_find_best_match_with_enhancement(self, engine):
        """Enhanced find_best_match should handle multiple references correctly."""
        agent_output = "Strong methodology with clear presentation."
        references = [
            "Poor methodology and unclear results.",
            "Strong methodology with excellent presentation.",
            "Different topic about databases.",
        ]

        basic_scores = engine.find_best_match(agent_output, references, enhanced=False)
        enhanced_scores = engine.find_best_match(agent_output, references, enhanced=True)

        # Basic should have no Levenshtein
        assert basic_scores.levenshtein == 0.0

        # Enhanced should have Levenshtein score
        assert enhanced_scores.levenshtein > 0.0
        assert 0.0 <= enhanced_scores.levenshtein <= 1.0

    def test_evaluate_enhanced_similarity_with_weights(self, engine):
        """Enhanced similarity evaluation should support config-driven weights."""
        agent_output = "The paper shows strong technical contribution with good methodology."
        references = [
            "Strong technical work with solid methodology.",
            "Good contribution but methodology needs improvement.",
        ]

        # Test with custom weights
        custom_weights = {
            "cosine_weight": 0.6,
            "jaccard_weight": 0.3,
            "semantic_weight": 0.1,
        }

        similarity = engine.evaluate_enhanced_similarity(
            agent_output, references, config_weights=custom_weights
        )

        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.4  # Should show reasonable similarity

    def test_evaluate_enhanced_similarity_default_weights(self, engine):
        """Enhanced similarity evaluation should work with default weights."""
        agent_output = "Machine learning approach with comprehensive evaluation."
        references = ["ML method with thorough evaluation and analysis."]

        similarity = engine.evaluate_enhanced_similarity(agent_output, references)

        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.3  # Should show some similarity

    def test_evaluate_enhanced_similarity_fallback(self, engine):
        """Enhanced similarity evaluation should fallback gracefully on errors."""
        # Test with edge case that might cause errors
        agent_output = ""
        references = ["Some reference text"]

        similarity = engine.evaluate_enhanced_similarity(agent_output, references)

        assert similarity == 0.0  # Should handle gracefully


# Convenience function tests for enhanced features
def test_evaluate_single_enhanced():
    """Test convenience function for enhanced evaluation."""
    agent_output = "This paper presents novel machine learning approach with solid evaluation."
    reference_texts = ["Novel ML method with comprehensive experimental evaluation."]

    # Test with default weights
    result = evaluate_single_enhanced(agent_output, reference_texts)
    assert 0.0 <= result <= 1.0
    assert result > 0.3  # Should show similarity

    # Test with custom weights
    weights = {"cosine_weight": 0.7, "jaccard_weight": 0.3, "semantic_weight": 0.0}
    result_weighted = evaluate_single_enhanced(agent_output, reference_texts, weights)
    assert 0.0 <= result_weighted <= 1.0


def test_evaluate_single_enhanced_empty_references():
    """Enhanced evaluation should handle empty reference lists."""
    agent_output = "Some output text"
    reference_texts = []

    result = evaluate_single_enhanced(agent_output, reference_texts)
    assert result == 0.0


class TestPeerReadEvaluation:
    """Test PeerRead evaluation functionality from traditional metrics."""

    def test_evaluate_review_similarity(self):
        """Test similarity evaluation between agent and ground truth reviews."""
        from app.judge.traditional_metrics import evaluate_review_similarity

        # Arrange
        agent_review = "This paper presents solid methodology and good results."
        ground_truth = "The methodology is well-designed and results are convincing."

        # Act
        similarity = evaluate_review_similarity(agent_review, ground_truth)

        # Assert
        assert 0.0 <= similarity <= 1.0
        assert isinstance(similarity, float)

    def test_create_evaluation_result(self):
        """Test creation of comprehensive evaluation result."""
        from app.data_models.evaluation_models import PeerReadEvalResult
        from app.data_models.peerread_models import PeerReadReview
        from app.judge.traditional_metrics import create_evaluation_result

        # Arrange
        paper_id = "test_001"
        agent_review = "This paper presents good methodology and solid results."
        ground_truth_reviews = [
            PeerReadReview(
                impact="4",
                substance="4",
                appropriateness="5",
                meaningful_comparison="3",
                presentation_format="Poster",
                comments="The methodology is well-designed and results are convincing.",
                soundness_correctness="4",
                originality="3",
                recommendation="4",  # Positive recommendation
                clarity="4",
                reviewer_confidence="3",
            ),
            PeerReadReview(
                impact="3",
                substance="3",
                appropriateness="4",
                meaningful_comparison="2",
                presentation_format="Oral",
                comments="Decent work but could use more thorough evaluation.",
                soundness_correctness="3",
                originality="2",
                recommendation="2",  # Negative recommendation
                clarity="3",
                reviewer_confidence="2",
            ),
        ]

        # Act
        result = create_evaluation_result(paper_id, agent_review, ground_truth_reviews)

        # Assert
        assert isinstance(result, PeerReadEvalResult)
        assert result.paper_id == paper_id
        assert result.agent_review == agent_review
        assert len(result.ground_truth_reviews) == 2
        assert 0.0 <= result.overall_similarity <= 1.0
        assert isinstance(result.recommendation_match, bool)
        assert "cosine" in result.similarity_scores
        assert "jaccard" in result.similarity_scores

    def test_evaluation_result_with_empty_reviews(self):
        """Test evaluation result creation with empty ground truth reviews."""
        from app.data_models.evaluation_models import PeerReadEvalResult
        from app.judge.traditional_metrics import create_evaluation_result

        # Arrange
        paper_id = "test_002"
        agent_review = "This paper has some issues."
        ground_truth_reviews = []

        # Act
        result = create_evaluation_result(paper_id, agent_review, ground_truth_reviews)

        # Assert
        assert isinstance(result, PeerReadEvalResult)
        assert result.overall_similarity == 0.0
        assert len(result.ground_truth_reviews) == 0

    def test_recommendation_matching_positive(self):
        """Test recommendation matching for positive agent sentiment."""
        from app.data_models.peerread_models import PeerReadReview
        from app.judge.traditional_metrics import create_evaluation_result

        # Arrange
        paper_id = "test_003"
        agent_review = "This is a good paper with solid contributions."  # Contains "good"
        ground_truth_reviews = [
            PeerReadReview(
                impact="4",
                substance="4",
                appropriateness="5",
                meaningful_comparison="3",
                presentation_format="Poster",
                comments="Positive review",
                soundness_correctness="4",
                originality="3",
                recommendation="4",  # High recommendation (>= 3.0)
                clarity="4",
                reviewer_confidence="3",
            )
        ]

        # Act
        result = create_evaluation_result(paper_id, agent_review, ground_truth_reviews)

        # Assert
        assert result.recommendation_match is True

    def test_recommendation_matching_negative(self):
        """Test recommendation matching for negative agent sentiment."""
        from app.data_models.peerread_models import PeerReadReview
        from app.judge.traditional_metrics import create_evaluation_result

        # Arrange
        paper_id = "test_004"
        agent_review = "This paper has significant flaws."  # No "good"
        ground_truth_reviews = [
            PeerReadReview(
                impact="2",
                substance="2",
                appropriateness="3",
                meaningful_comparison="2",
                presentation_format="Poster",
                comments="Negative review",
                soundness_correctness="2",
                originality="2",
                recommendation="2",  # Low recommendation (< 3.0)
                clarity="2",
                reviewer_confidence="2",
            )
        ]

        # Act
        result = create_evaluation_result(paper_id, agent_review, ground_truth_reviews)

        # Assert
        assert result.recommendation_match is True

    def test_peerread_eval_result_validation(self):
        """Test PeerReadEvalResult model validation."""
        from app.data_models.evaluation_models import PeerReadEvalResult

        # Arrange
        eval_data = {
            "paper_id": "test_001",
            "agent_review": "Test agent review",
            "ground_truth_reviews": [],
            "similarity_scores": {"cosine": 0.75, "jaccard": 0.60},
            "overall_similarity": 0.68,
            "recommendation_match": True,
        }

        # Act
        result = PeerReadEvalResult.model_validate(eval_data)

        # Assert
        assert result.paper_id == "test_001"
        assert result.overall_similarity == 0.68
        assert result.recommendation_match is True
        assert result.similarity_scores["cosine"] == 0.75
