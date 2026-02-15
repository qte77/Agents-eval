"""
Tests for composite scoring system.

Validates the CompositeScorer class integration of all three evaluation tiers,
mathematical formulas, recommendation mapping, and configuration handling.
"""

import pytest

from app.data_models.evaluation_models import (
    CompositeResult,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.judge.composite_scorer import CompositeScorer, EvaluationResults


@pytest.fixture
def scorer():
    """CompositeScorer instance with default JudgeSettings."""
    return CompositeScorer()


@pytest.fixture
def sample_tier_results():
    """Sample tier results for testing."""
    tier1 = Tier1Result(
        cosine_score=0.85,
        jaccard_score=0.72,
        semantic_score=0.91,
        execution_time=1.23,
        time_score=0.88,
        task_success=1.0,
        overall_score=0.89,
    )

    tier2 = Tier2Result(
        technical_accuracy=0.82,
        constructiveness=0.78,
        clarity=0.85,
        planning_rationality=0.80,
        overall_score=0.83,
        model_used="gpt-4o-mini",
        api_cost=0.01,
        fallback_used=False,
    )

    tier3 = Tier3Result(
        coordination_centrality=0.76,
        tool_selection_accuracy=0.84,
        path_convergence=0.79,
        task_distribution_balance=0.81,
        communication_overhead=0.72,
        overall_score=0.78,
        graph_complexity=72,
    )

    return EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)


class TestCompositeScorer:
    """Test suite for CompositeScorer functionality."""


class TestCompositeScorerMetricExtraction:
    """Test metric extraction from tier results."""

    def test_extract_metric_values_complete_results(self, scorer, sample_tier_results):
        """Should extract all six metrics from complete tier results."""
        metrics = scorer.extract_metric_values(sample_tier_results)

        assert len(metrics) == 6
        required_metrics = {
            "time_taken",
            "task_success",
            "coordination_quality",
            "tool_efficiency",
            "planning_rationality",
            "output_similarity",
        }
        assert set(metrics.keys()) == required_metrics

        # All metrics should be in valid range
        for metric, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"Metric {metric} = {value} outside valid range"

    def test_extract_metric_values_incomplete_results(self, scorer):
        """Should raise error when tier results are incomplete."""
        incomplete_results = EvaluationResults(tier1=None, tier2=None, tier3=None)

        with pytest.raises(ValueError, match="Missing required tier results"):
            scorer.extract_metric_values(incomplete_results)


class TestCompositeScorerScoreCalculation:
    """Test composite score calculation."""

    def test_calculate_composite_score_perfect_performance(self, scorer, sample_tier_results):
        """Perfect performance should yield high composite score."""
        # Set all metrics to perfect scores
        sample_tier_results.tier1.time_score = 1.0
        sample_tier_results.tier1.task_success = 1.0
        sample_tier_results.tier1.overall_score = 1.0
        sample_tier_results.tier2.overall_score = 1.0
        sample_tier_results.tier3.coordination_centrality = 1.0
        sample_tier_results.tier3.tool_selection_accuracy = 1.0

        score = scorer.calculate_composite_score(sample_tier_results)

        # Should be very high (close to 1.0)
        assert score >= 0.85
        assert score <= 1.0

    def test_calculate_composite_score_poor_performance(self, scorer, sample_tier_results):
        """Poor performance should yield low composite score."""
        # Set all metrics to poor scores
        sample_tier_results.tier1.time_score = 0.1
        sample_tier_results.tier1.task_success = 0.0
        sample_tier_results.tier1.overall_score = 0.1
        sample_tier_results.tier2.overall_score = 0.1
        sample_tier_results.tier3.coordination_centrality = 0.1
        sample_tier_results.tier3.tool_selection_accuracy = 0.1

        score = scorer.calculate_composite_score(sample_tier_results)

        # Should be low
        assert score >= 0.0
        assert score <= 0.4

    def test_calculate_composite_score_weights_applied(self, scorer, sample_tier_results):
        """Composite score should reflect configured metric weights."""
        score = scorer.calculate_composite_score(sample_tier_results)

        # Extract individual metrics to verify calculation
        metrics = scorer.extract_metric_values(sample_tier_results)
        expected_score = sum(metrics[metric] * weight for metric, weight in scorer.weights.items())

        assert abs(score - expected_score) < 0.001


class TestCompositeScorerRecommendationMapping:
    """Test recommendation mapping from scores."""

    def test_map_to_recommendation_accept(self, scorer):
        """High scores should map to 'accept' recommendation."""
        recommendation = scorer.map_to_recommendation(0.85)
        assert recommendation == "accept"

    def test_map_to_recommendation_weak_accept(self, scorer):
        """Medium-high scores should map to 'weak_accept'."""
        recommendation = scorer.map_to_recommendation(0.65)
        assert recommendation == "weak_accept"

    def test_map_to_recommendation_weak_reject(self, scorer):
        """Medium-low scores should map to 'weak_reject'."""
        recommendation = scorer.map_to_recommendation(0.45)
        assert recommendation == "weak_reject"

    def test_map_to_recommendation_reject(self, scorer):
        """Low scores should map to 'reject'."""
        recommendation = scorer.map_to_recommendation(0.25)
        assert recommendation == "reject"


class TestCompositeScorerIntegration:
    """Test complete composite evaluation integration."""

    def test_evaluate_composite_complete_flow(self, scorer, sample_tier_results):
        """Should complete full evaluation flow with all components."""
        result = scorer.evaluate_composite(sample_tier_results)

        # Verify result structure
        assert isinstance(result, CompositeResult)
        assert 0.0 <= result.composite_score <= 1.0
        assert result.recommendation in [
            "accept",
            "weak_accept",
            "weak_reject",
            "reject",
        ]
        assert -1.0 <= result.recommendation_weight <= 1.0
        assert len(result.metric_scores) == 6
        assert result.evaluation_complete is True


class TestAgentAssessment:
    """Test agent assessment functionality."""

    def test_assess_agent_performance_default(self, scorer):
        """Test agent assessment with default parameters."""
        metrics = scorer.assess_agent_performance(
            execution_time=5.0,
            tools_used=["tool1", "tool2"],
            delegation_count=1,
            error_occurred=False,
            output_length=100,
        )

        # Should return valid AgentMetrics object
        assert 0.0 <= metrics.tool_selection_score <= 1.0
        assert 0.0 <= metrics.plan_coherence_score <= 1.0
        assert 0.0 <= metrics.coordination_score <= 1.0

        # Should have composite score
        composite = metrics.get_agent_composite_score()
        assert 0.0 <= composite <= 1.0

    def test_assess_agent_performance_error_penalty(self, scorer):
        """Test that errors result in lower scores."""
        normal_metrics = scorer.assess_agent_performance(
            execution_time=5.0,
            tools_used=["tool1"],
            error_occurred=False,
            output_length=100,
        )

        error_metrics = scorer.assess_agent_performance(
            execution_time=5.0,
            tools_used=["tool1"],
            error_occurred=True,  # Should reduce coherence score
            output_length=100,
        )

        # Error should result in lower coherence score
        assert error_metrics.plan_coherence_score < normal_metrics.plan_coherence_score

    def test_assess_agent_performance_over_tooling_penalty(self, scorer):
        """Test that over-tooling results in lower tool selection score."""
        normal_metrics = scorer.assess_agent_performance(
            execution_time=5.0,
            tools_used=["tool1", "tool2"],
            error_occurred=False,
            output_length=100,
        )

        over_tooled_metrics = scorer.assess_agent_performance(
            execution_time=5.0,
            tools_used=[
                "tool1",
                "tool2",
                "tool3",
                "tool4",
                "tool5",
                "tool6",
                "tool7",
            ],  # Too many tools
            error_occurred=False,
            output_length=100,
        )

        # Over-tooling should result in lower tool selection score
        assert over_tooled_metrics.tool_selection_score < normal_metrics.tool_selection_score
