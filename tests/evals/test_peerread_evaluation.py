"""
Test cases for PeerRead evaluation utilities.

Tests for evaluation logic including similarity metrics and comparison functions
used to evaluate agent-generated reviews against ground truth.
"""

from app.data_models.peerread_evaluation_models import PeerReadEvalResult
from app.data_models.peerread_models import PeerReadReview


class TestSimilarityMetrics:
    """Test similarity calculation functions."""

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation between text vectors."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import calculate_cosine_similarity

        # Arrange
        text1 = "machine learning algorithms"
        text2 = "ML algorithms and methods"

        # Act
        similarity = calculate_cosine_similarity(text1, text2)

        # Assert
        assert 0.0 <= similarity <= 1.0
        assert isinstance(similarity, float)

    def test_cosine_similarity_identical_texts(self):
        """Test cosine similarity with identical texts."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import calculate_cosine_similarity

        # Arrange
        text = "machine learning algorithms"

        # Act
        similarity = calculate_cosine_similarity(text, text)

        # Assert
        assert similarity > 0.8  # Should be high for identical texts

    def test_cosine_similarity_empty_texts(self):
        """Test cosine similarity with empty texts."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import calculate_cosine_similarity

        # Act
        similarity1 = calculate_cosine_similarity("", "some text")
        similarity2 = calculate_cosine_similarity("", "")

        # Assert
        assert similarity1 == 0.0
        assert similarity2 == 0.0

    def test_jaccard_similarity_calculation(self):
        """Test Jaccard similarity calculation."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import calculate_jaccard_similarity

        # Arrange
        text1 = "machine learning algorithms"
        text2 = "ML algorithms and methods"

        # Act
        similarity = calculate_jaccard_similarity(text1, text2)

        # Assert
        assert 0.0 <= similarity <= 1.0
        assert isinstance(similarity, float)

    def test_jaccard_similarity_identical_texts(self):
        """Test Jaccard similarity with identical texts."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import calculate_jaccard_similarity

        # Arrange
        text = "machine learning algorithms"

        # Act
        similarity = calculate_jaccard_similarity(text, text)

        # Assert
        assert similarity == 1.0  # Should be perfect for identical texts

    def test_jaccard_similarity_empty_texts(self):
        """Test Jaccard similarity with empty texts."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import calculate_jaccard_similarity

        # Act
        similarity1 = calculate_jaccard_similarity("", "some text")
        similarity2 = calculate_jaccard_similarity("", "")

        # Assert
        assert similarity1 == 0.0
        assert similarity2 == 1.0  # Both empty should be identical


class TestReviewEvaluation:
    """Test review evaluation functionality."""

    def test_evaluate_review_similarity(self):
        """Test similarity evaluation between agent and ground truth reviews."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import evaluate_review_similarity

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
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import create_evaluation_result

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
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import create_evaluation_result

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
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import create_evaluation_result

        # Arrange
        paper_id = "test_003"
        agent_review = (
            "This is a good paper with solid contributions."  # Contains "good"
        )
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
        # Import here to avoid import errors if module doesn't exist yet
        from app.evals.peerread_evaluation import create_evaluation_result

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


class TestEvaluationModels:
    """Test evaluation-specific Pydantic models."""

    def test_peerread_eval_result_validation(self):
        """Test PeerReadEvalResult model validation."""
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

    def test_eval_result_with_ground_truth_reviews(self):
        """Test evaluation result with actual ground truth reviews."""
        # Arrange
        ground_truth_review = PeerReadReview(
            impact="3",
            substance="4",
            appropriateness="5",
            meaningful_comparison="2",
            presentation_format="Poster",
            comments="Test review comment.",
            soundness_correctness="4",
            originality="3",
            recommendation="3",
            clarity="3",
            reviewer_confidence="3",
        )

        eval_data = {
            "paper_id": "test_002",
            "agent_review": "Agent generated review",
            "ground_truth_reviews": [ground_truth_review],
            "similarity_scores": {"cosine": 0.80, "jaccard": 0.65},
            "overall_similarity": 0.73,
            "recommendation_match": False,
        }

        # Act
        result = PeerReadEvalResult.model_validate(eval_data)

        # Assert
        assert len(result.ground_truth_reviews) == 1
        assert result.ground_truth_reviews[0].comments == "Test review comment."
        assert result.recommendation_match is False
