"""
Tests for composite scoring system.

Validates the CompositeScorer class integration of all three evaluation tiers,
mathematical formulas, recommendation mapping, and configuration handling.

Consolidated from:
- test_composite_scoring_scenarios.py
- test_composite_scoring_interpretability.py
- test_composite_scoring_edge_cases.py

Mock strategy: No external mocking needed — CompositeScorer uses pure math,
no network or filesystem access.
"""

from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

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


# MARK: Property-based tests using Hypothesis


class TestCompositeScoreProperties:
    """Property-based tests for score bounds and invariants."""

    @given(
        time_score=st.floats(min_value=0.0, max_value=1.0),
        task_success=st.floats(min_value=0.0, max_value=1.0),
        tier1_overall=st.floats(min_value=0.0, max_value=1.0),
        tier2_overall=st.floats(min_value=0.0, max_value=1.0),
        coordination=st.floats(min_value=0.0, max_value=1.0),
        tool_accuracy=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_composite_score_always_in_valid_range(
        self, time_score, task_success, tier1_overall, tier2_overall, coordination, tool_accuracy
    ):
        """Property: Composite score must always be in [0.0, 1.0] for all valid inputs."""
        scorer = CompositeScorer()

        # Create tier results with random valid scores
        tier1 = Tier1Result(
            cosine_score=0.5,
            jaccard_score=0.5,
            semantic_score=0.5,
            execution_time=1.0,
            time_score=time_score,
            task_success=task_success,
            overall_score=tier1_overall,
        )
        tier2 = Tier2Result(
            technical_accuracy=0.5,
            constructiveness=0.5,
            planning_rationality=0.5,
            overall_score=tier2_overall,
            model_used="test",
            api_cost=0.0,
            fallback_used=False,
        )
        tier3 = Tier3Result(
            coordination_centrality=coordination,
            tool_selection_accuracy=tool_accuracy,
            path_convergence=0.5,
            task_distribution_balance=0.5,
            communication_overhead=0.5,
            overall_score=0.5,
            graph_complexity=10,
        )

        results = EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)
        composite_score = scorer.calculate_composite_score(results)

        # PROPERTY: Score must be in valid range
        assert 0.0 <= composite_score <= 1.0, (
            f"Composite score {composite_score} outside [0.0, 1.0]"
        )

    @given(
        scores=st.lists(
            st.floats(min_value=0.0, max_value=1.0),
            min_size=6,
            max_size=6,
        )
    )
    def test_composite_score_weight_normalization(self, scores):
        """Property: Weighted sum should preserve bounds when weights sum to ~1.0."""
        scorer = CompositeScorer()

        # Verify weights sum to approximately 1.0 (allow floating point precision)
        weight_sum = sum(scorer.weights.values())
        assert abs(weight_sum - 1.0) < 0.01, f"Weights sum to {weight_sum}, not ~1.0"

        # Calculate weighted sum manually
        metric_names = list(scorer.weights.keys())
        weighted_sum = sum(scores[i] * scorer.weights[metric_names[i]] for i in range(6))

        # PROPERTY: Weighted sum must be in [0.0, 1.0] (allow small overshoot for FP errors)
        assert -0.01 <= weighted_sum <= 1.01, f"Weighted sum {weighted_sum} outside [0.0, 1.0]"

    @given(score=st.floats(min_value=0.0, max_value=1.0))
    def test_recommendation_mapping_completeness(self, score):
        """Property: Every valid score maps to exactly one recommendation."""
        scorer = CompositeScorer()
        recommendation = scorer.map_to_recommendation(score)

        # PROPERTY: Must return one of the four valid recommendations
        valid_recommendations = {"accept", "weak_accept", "weak_reject", "reject"}
        assert recommendation in valid_recommendations, f"Invalid recommendation: {recommendation}"

    @given(
        tier1_score=st.floats(min_value=0.0, max_value=1.0),
        tier2_score=st.floats(min_value=0.0, max_value=1.0),
        tier3_score=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_metric_extraction_preserves_bounds(self, tier1_score, tier2_score, tier3_score):
        """Property: Extracted metrics maintain [0.0, 1.0] bounds."""
        scorer = CompositeScorer()

        tier1 = Tier1Result(
            cosine_score=0.5,
            jaccard_score=0.5,
            semantic_score=0.5,
            execution_time=1.0,
            time_score=tier1_score,
            task_success=tier1_score,
            overall_score=tier1_score,
        )
        tier2 = Tier2Result(
            technical_accuracy=tier2_score,
            constructiveness=tier2_score,
            planning_rationality=tier2_score,
            overall_score=tier2_score,
            model_used="test",
            api_cost=0.0,
            fallback_used=False,
        )
        tier3 = Tier3Result(
            coordination_centrality=tier3_score,
            tool_selection_accuracy=tier3_score,
            path_convergence=tier3_score,
            task_distribution_balance=tier3_score,
            communication_overhead=tier3_score,
            overall_score=tier3_score,
            graph_complexity=10,
        )

        results = EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)
        metrics = scorer.extract_metric_values(results)

        # PROPERTY: All extracted metrics in valid range
        for metric_name, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"Metric {metric_name}={value} outside [0.0, 1.0]"


# MARK: Snapshot tests using inline-snapshot


class TestCompositeResultStructure:
    """Snapshot tests for CompositeResult structure regression."""

    def test_composite_result_structure_snapshot(self, scorer, sample_tier_results):
        """Snapshot: CompositeResult structure should remain stable."""
        result = scorer.evaluate_composite(sample_tier_results)

        # SNAPSHOT: Capture the complete structure
        assert result.model_dump() == snapshot(
            {
                "composite_score": 0.8633900000000001,
                "recommendation": "accept",
                "recommendation_weight": 1.0,
                "metric_scores": {
                    "time_taken": 0.88,
                    "task_success": 1.0,
                    "output_similarity": 0.89,
                    "planning_rationality": 0.8,
                    "coordination_quality": 0.76,
                    "tool_efficiency": 0.84,
                },
                "tier1_score": 0.89,
                "tier2_score": 0.83,
                "tier3_score": 0.78,
                "evaluation_complete": True,
                "single_agent_mode": False,
                "timestamp": "",
                "config_version": "1.0.0",
                "weights_used": {
                    "time_taken": 0.167,
                    "task_success": 0.167,
                    "coordination_quality": 0.167,
                    "tool_efficiency": 0.167,
                    "planning_rationality": 0.167,
                    "output_similarity": 0.167,
                },
                "tiers_enabled": [1, 2, 3],
                "agent_assessment_scores": None,
            }
        )

    def test_composite_result_with_perfect_scores_snapshot(self, scorer):
        """Snapshot: Perfect score structure."""
        tier1 = Tier1Result(
            cosine_score=1.0,
            jaccard_score=1.0,
            semantic_score=1.0,
            execution_time=0.1,
            time_score=1.0,
            task_success=1.0,
            overall_score=1.0,
        )
        tier2 = Tier2Result(
            technical_accuracy=1.0,
            constructiveness=1.0,
            planning_rationality=1.0,
            overall_score=1.0,
            model_used="test-model",
            api_cost=0.001,
            fallback_used=False,
        )
        tier3 = Tier3Result(
            coordination_centrality=1.0,
            tool_selection_accuracy=1.0,
            path_convergence=1.0,
            task_distribution_balance=1.0,
            communication_overhead=1.0,
            overall_score=1.0,
            graph_complexity=5,
        )

        results = EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)
        result = scorer.evaluate_composite(results)

        # SNAPSHOT: Structure with all perfect scores
        assert result.model_dump() == snapshot(
            {
                "composite_score": 1.0,
                "recommendation": "accept",
                "recommendation_weight": 1.0,
                "metric_scores": {
                    "time_taken": 1.0,
                    "task_success": 1.0,
                    "output_similarity": 1.0,
                    "planning_rationality": 1.0,
                    "coordination_quality": 1.0,
                    "tool_efficiency": 1.0,
                },
                "tier1_score": 1.0,
                "tier2_score": 1.0,
                "tier3_score": 1.0,
                "evaluation_complete": True,
                "single_agent_mode": False,
                "timestamp": "",
                "config_version": "1.0.0",
                "weights_used": {
                    "time_taken": 0.167,
                    "task_success": 0.167,
                    "coordination_quality": 0.167,
                    "tool_efficiency": 0.167,
                    "planning_rationality": 0.167,
                    "output_similarity": 0.167,
                },
                "tiers_enabled": [1, 2, 3],
                "agent_assessment_scores": None,
            }
        )


# MARK: Consolidated tests from scenario, interpretability, and edge case files


class TestBasicScoring:
    """Basic scoring and scenario validation tests.

    Consolidated from test_composite_scoring_scenarios.py.
    Tests all 5 core performance scenarios and threshold boundaries.

    Setup: Synthetic tier results for high/low quality × fast/slow execution.
    Expected behavior: Recommendations correlate with actual quality/speed profiles.
    """

    @pytest.fixture
    def composite_scorer(self) -> CompositeScorer:
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    @pytest.mark.parametrize(
        "scenario_name,expected_recommendations",
        [
            ("high_quality_fast", ["accept"]),
            ("high_quality_slow", ["accept", "weak_accept"]),
            ("low_quality_fast", ["weak_reject", "reject"]),
            ("low_quality_slow", ["reject"]),
            ("mixed_performance", ["weak_accept", "weak_reject"]),
        ],
    )
    def test_scoring_scenarios(self, composite_scorer, scenario_name, expected_recommendations):
        """Each performance scenario produces a recommendation in the expected set.

        Arrange: Create tier results matching the named scenario's quality/speed profile.
        Act: Evaluate with CompositeScorer.
        Assert: Recommendation falls within the expected set for that scenario.
        """
        # Arrange
        scenarios = {
            "high_quality_fast": EvaluationResults(
                tier1=Tier1Result(
                    cosine_score=0.82,
                    jaccard_score=0.78,
                    semantic_score=0.85,
                    execution_time=0.7,
                    time_score=0.95,
                    task_success=1.0,
                    overall_score=0.85,
                ),
                tier2=Tier2Result(
                    technical_accuracy=0.88,
                    constructiveness=0.85,
                    planning_rationality=0.87,
                    overall_score=0.87,
                    model_used="gpt-4o-mini",
                    api_cost=0.02,
                    fallback_used=False,
                ),
                tier3=Tier3Result(
                    coordination_centrality=0.89,
                    tool_selection_accuracy=0.86,
                    communication_overhead=0.82,
                    path_convergence=0.84,
                    task_distribution_balance=0.88,
                    overall_score=0.86,
                    graph_complexity=12,
                ),
            ),
            "high_quality_slow": EvaluationResults(
                tier1=Tier1Result(
                    cosine_score=0.84,
                    jaccard_score=0.81,
                    semantic_score=0.87,
                    execution_time=2.8,
                    time_score=0.55,
                    task_success=1.0,
                    overall_score=0.84,
                ),
                tier2=Tier2Result(
                    technical_accuracy=0.91,
                    constructiveness=0.89,
                    planning_rationality=0.92,
                    overall_score=0.91,
                    model_used="gpt-4o-mini",
                    api_cost=0.04,
                    fallback_used=False,
                ),
                tier3=Tier3Result(
                    coordination_centrality=0.73,
                    tool_selection_accuracy=0.68,
                    communication_overhead=0.65,
                    path_convergence=0.71,
                    task_distribution_balance=0.75,
                    overall_score=0.70,
                    graph_complexity=45,
                ),
            ),
            "low_quality_fast": EvaluationResults(
                tier1=Tier1Result(
                    cosine_score=0.29,
                    jaccard_score=0.27,
                    semantic_score=0.32,
                    execution_time=0.4,
                    time_score=0.92,
                    task_success=0.0,
                    overall_score=0.30,
                ),
                tier2=Tier2Result(
                    technical_accuracy=0.35,
                    constructiveness=0.31,
                    planning_rationality=0.28,
                    overall_score=0.31,
                    model_used="gpt-4o-mini",
                    api_cost=0.01,
                    fallback_used=False,
                ),
                tier3=Tier3Result(
                    coordination_centrality=0.22,
                    tool_selection_accuracy=0.25,
                    communication_overhead=0.20,
                    path_convergence=0.19,
                    task_distribution_balance=0.24,
                    overall_score=0.22,
                    graph_complexity=4,
                ),
            ),
            "low_quality_slow": EvaluationResults(
                tier1=Tier1Result(
                    cosine_score=0.25,
                    jaccard_score=0.23,
                    semantic_score=0.28,
                    execution_time=3.2,
                    time_score=0.15,
                    task_success=0.0,
                    overall_score=0.24,
                ),
                tier2=Tier2Result(
                    technical_accuracy=0.29,
                    constructiveness=0.26,
                    planning_rationality=0.22,
                    overall_score=0.26,
                    model_used="gpt-4o-mini",
                    api_cost=0.04,
                    fallback_used=False,
                ),
                tier3=Tier3Result(
                    coordination_centrality=0.18,
                    tool_selection_accuracy=0.15,
                    communication_overhead=0.12,
                    path_convergence=0.14,
                    task_distribution_balance=0.17,
                    overall_score=0.15,
                    graph_complexity=28,
                ),
            ),
            "mixed_performance": EvaluationResults(
                tier1=Tier1Result(
                    cosine_score=0.58,
                    jaccard_score=0.61,
                    semantic_score=0.64,
                    execution_time=1.8,
                    time_score=0.70,
                    task_success=1.0,
                    overall_score=0.62,
                ),
                tier2=Tier2Result(
                    technical_accuracy=0.52,
                    constructiveness=0.67,
                    planning_rationality=0.59,
                    overall_score=0.59,
                    model_used="gpt-4o-mini",
                    api_cost=0.03,
                    fallback_used=False,
                ),
                tier3=Tier3Result(
                    coordination_centrality=0.48,
                    tool_selection_accuracy=0.71,
                    communication_overhead=0.55,
                    path_convergence=0.55,
                    task_distribution_balance=0.62,
                    overall_score=0.58,
                    graph_complexity=19,
                ),
            ),
        }
        # Act
        result = composite_scorer.evaluate_composite(scenarios[scenario_name])
        # Assert
        assert result is not None
        assert 0.0 <= result.composite_score <= 1.0
        assert result.recommendation in expected_recommendations, (
            f"Recommendation '{result.recommendation}' not in expected "
            f"{expected_recommendations} for {scenario_name} "
            f"(score={result.composite_score:.3f})"
        )

    def test_recommendation_boundary_conditions(self, composite_scorer):
        """Threshold boundary values produce correct recommendations.

        Arrange: Use exact threshold values and values just below thresholds.
        Act: Map score to recommendation.
        Assert: Boundary conditions handled correctly (at/just-below thresholds).
        """
        # Arrange
        thresholds = composite_scorer.thresholds
        boundary_cases = [
            (thresholds["accept"], "accept"),
            (thresholds["accept"] - 0.001, "weak_accept"),
            (thresholds["weak_accept"], "weak_accept"),
            (thresholds["weak_accept"] - 0.001, "weak_reject"),
            (thresholds["weak_reject"], "weak_reject"),
            (thresholds["weak_reject"] - 0.001, "reject"),
        ]
        for score, expected in boundary_cases:
            # Act
            actual = composite_scorer.map_to_recommendation(score)
            # Assert
            assert actual == expected, f"Score {score} should map to '{expected}', got '{actual}'"

    def test_quality_outweighs_speed(self, composite_scorer):
        """High quality slow execution should outscore low quality fast execution.

        Arrange: Two evaluations — high quality/slow vs low quality/fast.
        Act: Evaluate both.
        Assert: High quality result has higher composite score.
        """
        # Arrange
        high_quality_slow = EvaluationResults(
            tier1=Tier1Result(
                cosine_score=0.84,
                jaccard_score=0.81,
                semantic_score=0.87,
                execution_time=2.8,
                time_score=0.55,
                task_success=1.0,
                overall_score=0.84,
            ),
            tier2=Tier2Result(
                technical_accuracy=0.91,
                constructiveness=0.89,
                planning_rationality=0.92,
                overall_score=0.91,
                model_used="gpt-4o-mini",
                api_cost=0.04,
                fallback_used=False,
            ),
            tier3=Tier3Result(
                coordination_centrality=0.73,
                tool_selection_accuracy=0.68,
                communication_overhead=0.65,
                path_convergence=0.71,
                task_distribution_balance=0.75,
                overall_score=0.70,
                graph_complexity=45,
            ),
        )
        low_quality_fast = EvaluationResults(
            tier1=Tier1Result(
                cosine_score=0.29,
                jaccard_score=0.27,
                semantic_score=0.32,
                execution_time=0.4,
                time_score=0.92,
                task_success=0.0,
                overall_score=0.30,
            ),
            tier2=Tier2Result(
                technical_accuracy=0.35,
                constructiveness=0.31,
                planning_rationality=0.28,
                overall_score=0.31,
                model_used="gpt-4o-mini",
                api_cost=0.01,
                fallback_used=False,
            ),
            tier3=Tier3Result(
                coordination_centrality=0.22,
                tool_selection_accuracy=0.25,
                communication_overhead=0.20,
                path_convergence=0.19,
                task_distribution_balance=0.24,
                overall_score=0.22,
                graph_complexity=4,
            ),
        )
        # Act
        slow_result = composite_scorer.evaluate_composite(high_quality_slow)
        fast_result = composite_scorer.evaluate_composite(low_quality_fast)
        # Assert
        assert slow_result.composite_score > fast_result.composite_score


class TestWeightRedistribution:
    """Weight redistribution and interpretability tests.

    Consolidated from test_composite_scoring_interpretability.py.
    Tests score consistency, metric contribution, and threshold boundaries.

    Setup: Scaled evaluation results and dominant-metric evaluations.
    Expected behavior: Different dominant metrics produce different scores.
    """

    @pytest.fixture
    def composite_scorer(self) -> CompositeScorer:
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    def test_weights_sum_to_one(self, composite_scorer):
        """Configured weights must sum to approximately 1.0.

        Arrange: Initialized CompositeScorer with default settings.
        Act: Sum all metric weights.
        Assert: Sum is within 0.01 of 1.0 (floating-point tolerance).
        """
        # Act
        weight_sum = sum(composite_scorer.weights.values())
        # Assert
        assert abs(weight_sum - 1.0) < 0.01, f"Weights sum to {weight_sum}, not ~1.0"

    def test_recommendation_boundaries_complete(self, composite_scorer):
        """All threshold boundaries map to correct recommendations.

        Arrange: Exact threshold values and just-below values.
        Act: Map each to recommendation.
        Assert: All 9 boundary cases map correctly including 0.0 and 1.0.
        """
        # Arrange
        thresholds = composite_scorer.thresholds
        boundary_cases = [
            (thresholds["accept"], "accept"),
            (thresholds["weak_accept"], "weak_accept"),
            (thresholds["weak_reject"], "weak_reject"),
            (thresholds["reject"], "reject"),
            (thresholds["accept"] - 0.001, "weak_accept"),
            (thresholds["weak_accept"] - 0.001, "weak_reject"),
            (thresholds["weak_reject"] - 0.001, "reject"),
            (1.0, "accept"),
            (0.0, "reject"),
        ]
        for score, expected_rec in boundary_cases:
            # Act
            actual_rec = composite_scorer.map_to_recommendation(score)
            # Assert
            assert actual_rec == expected_rec, (
                f"Score {score:.3f} should map to '{expected_rec}', got '{actual_rec}'"
            )

    def test_dominant_metric_produces_different_scores(self, composite_scorer):
        """Different dominant metrics produce different composite scores.

        Arrange: Three evaluations each with a different dominant metric (similarity,
        planning, coordination) and low base values for other metrics.
        Act: Evaluate all three.
        Assert: Composite scores are distinct (not all equal).
        """
        # Arrange
        base = 0.3
        high = 0.95

        def _make_dominant(dominant: str) -> EvaluationResults:
            """Create evaluation where one metric group dominates."""
            if dominant == "similarity":
                tier1_overall = high
                tier2_overall = base
                tier3_coord = base
                tier3_tool = base
            elif dominant == "planning":
                tier1_overall = base
                tier2_overall = base
                tier3_coord = base
                tier3_tool = base
            else:  # coordination
                tier1_overall = base
                tier2_overall = base
                tier3_coord = high
                tier3_tool = base

            return EvaluationResults(
                tier1=Tier1Result(
                    cosine_score=tier1_overall,
                    jaccard_score=tier1_overall,
                    semantic_score=tier1_overall,
                    execution_time=1.0,
                    time_score=0.9 if dominant == "similarity" else base,
                    task_success=1.0 if dominant == "similarity" else 0.0,
                    overall_score=tier1_overall,
                ),
                tier2=Tier2Result(
                    technical_accuracy=tier2_overall,
                    constructiveness=tier2_overall,
                    planning_rationality=high if dominant == "planning" else base,
                    overall_score=tier2_overall,
                    model_used="gpt-4o-mini",
                    api_cost=0.02,
                    fallback_used=False,
                ),
                tier3=Tier3Result(
                    coordination_centrality=tier3_coord,
                    tool_selection_accuracy=tier3_tool,
                    communication_overhead=base,
                    path_convergence=base,
                    task_distribution_balance=base,
                    overall_score=base,
                    graph_complexity=8,
                ),
            )

        # Act
        scores = {
            m: composite_scorer.evaluate_composite(_make_dominant(m)).composite_score
            for m in ["similarity", "planning", "coordination"]
        }
        # Assert: distinct scores produced
        assert len(set(round(s, 6) for s in scores.values())) > 1, (
            "Different dominant metrics should produce different scores"
        )


class TestEdgeCases:
    """Edge case and error condition tests.

    Consolidated from test_composite_scoring_edge_cases.py.
    Tests missing tiers, extreme values, and error conditions.

    Setup: Helper factories for Tier1/2/3 results with sensible defaults.
    Expected behavior: Robust error handling and predictable extremes.
    """

    @pytest.fixture
    def composite_scorer(self) -> CompositeScorer:
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    @staticmethod
    def _make_tier1(**overrides: object) -> Tier1Result:
        """Create Tier1Result with defaults, applying overrides."""
        defaults: dict[str, object] = {
            "cosine_score": 0.72,
            "jaccard_score": 0.68,
            "semantic_score": 0.75,
            "execution_time": 1.2,
            "time_score": 0.85,
            "task_success": 1.0,
            "overall_score": 0.74,
        }
        defaults.update(overrides)
        return Tier1Result(**defaults)  # type: ignore[arg-type]

    @staticmethod
    def _make_tier2(**overrides: object) -> Tier2Result:
        """Create Tier2Result with defaults, applying overrides."""
        defaults: dict[str, object] = {
            "technical_accuracy": 0.78,
            "constructiveness": 0.73,
            "planning_rationality": 0.76,
            "overall_score": 0.76,
            "model_used": "gpt-4o-mini",
            "api_cost": 0.025,
            "fallback_used": False,
        }
        defaults.update(overrides)
        return Tier2Result(**defaults)  # type: ignore[arg-type]

    @staticmethod
    def _make_tier3(**overrides: object) -> Tier3Result:
        """Create Tier3Result with defaults, applying overrides."""
        defaults: dict[str, object] = {
            "coordination_centrality": 0.74,
            "tool_selection_accuracy": 0.71,
            "communication_overhead": 0.70,
            "path_convergence": 0.69,
            "task_distribution_balance": 0.73,
            "overall_score": 0.72,
            "graph_complexity": 15,
        }
        defaults.update(overrides)
        return Tier3Result(**defaults)  # type: ignore[arg-type]

    @pytest.mark.parametrize("missing_tier", ["tier1", "tier2", "tier3", "all"])
    def test_missing_tiers_raise_error(self, composite_scorer, missing_tier):
        """Missing tier results should raise ValueError with descriptive message.

        Arrange: EvaluationResults with specified tier(s) set to None.
        Act: Call extract_metric_values.
        Assert: ValueError raised with 'Missing required tier results' message.
        """
        # Arrange
        tier1 = None if missing_tier in ["tier1", "all"] else self._make_tier1()
        tier2 = None if missing_tier in ["tier2", "all"] else self._make_tier2()
        tier3 = None if missing_tier in ["tier3", "all"] else self._make_tier3()
        evaluation = EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required tier results"):
            composite_scorer.extract_metric_values(evaluation)

    def test_zero_scores_produce_low_result(self, composite_scorer):
        """All-zero scores result in low composite score and reject/weak_reject recommendation.

        Arrange: EvaluationResults with near-zero values across all tiers.
        Act: Evaluate composite.
        Assert: Score below 0.4 and recommendation is reject or weak_reject.
        """
        # Arrange
        evaluation = EvaluationResults(
            tier1=self._make_tier1(
                cosine_score=0.0,
                jaccard_score=0.0,
                semantic_score=0.0,
                time_score=0.1,
                task_success=0.0,
                overall_score=0.0,
                execution_time=0.1,
            ),
            tier2=self._make_tier2(
                technical_accuracy=0.0,
                constructiveness=0.0,
                planning_rationality=0.0,
                overall_score=0.0,
            ),
            tier3=self._make_tier3(
                coordination_centrality=0.1,
                tool_selection_accuracy=0.1,
                communication_overhead=0.0,
                path_convergence=0.0,
                task_distribution_balance=0.0,
                overall_score=0.0,
                graph_complexity=0,
            ),
        )
        # Act
        result = composite_scorer.evaluate_composite(evaluation)
        # Assert
        assert result.composite_score < 0.4
        assert result.recommendation in ["weak_reject", "reject"]

    def test_zero_execution_time_no_error(self, composite_scorer):
        """Zero execution time should not cause errors or invalid scores.

        Arrange: Tier1Result with execution_time=0.0.
        Act: Evaluate composite.
        Assert: Result is valid and score is in [0.0, 1.0].
        """
        # Arrange
        evaluation = EvaluationResults(
            tier1=self._make_tier1(execution_time=0.0, time_score=1.0),
            tier2=self._make_tier2(),
            tier3=self._make_tier3(),
        )
        # Act
        result = composite_scorer.evaluate_composite(evaluation)
        # Assert
        assert result is not None
        assert 0.0 <= result.composite_score <= 1.0


class TestConsolidationStructure:
    """Structural tests verifying consolidation is complete.

    These tests verify that the old split files have been deleted
    and that consolidation into test_composite_scorer.py is done.
    """

    TESTS_EVALS_DIR = Path(__file__).parent

    def test_old_scenarios_file_deleted(self) -> None:
        """The scenarios file should be deleted after consolidation."""
        # Arrange/Act
        old_file = self.TESTS_EVALS_DIR / "test_composite_scoring_scenarios.py"
        # Assert: file must not exist after consolidation
        assert not old_file.exists(), (
            "test_composite_scoring_scenarios.py must be deleted after consolidation into "
            "test_composite_scorer.py"
        )

    def test_old_interpretability_file_deleted(self) -> None:
        """The interpretability file should be deleted after consolidation."""
        # Arrange/Act
        old_file = self.TESTS_EVALS_DIR / "test_composite_scoring_interpretability.py"
        # Assert: file must not exist after consolidation
        assert not old_file.exists(), (
            "test_composite_scoring_interpretability.py must be deleted after consolidation "
            "into test_composite_scorer.py"
        )

    def test_old_edge_cases_file_deleted(self) -> None:
        """The edge cases file should be deleted after consolidation."""
        # Arrange/Act
        old_file = self.TESTS_EVALS_DIR / "test_composite_scoring_edge_cases.py"
        # Assert: file must not exist after consolidation
        assert not old_file.exists(), (
            "test_composite_scoring_edge_cases.py must be deleted after consolidation into "
            "test_composite_scorer.py"
        )
