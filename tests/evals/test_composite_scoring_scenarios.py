"""
Composite scoring scenario validation tests.

This module tests the composite scoring system across varied performance
scenarios as specified in the validation framework. Tests all 5 core scenarios:
high quality + fast/slow execution, low quality + fast/slow execution, and
mixed performance profiles.
"""

import pytest

from app.data_models.evaluation_models import (
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.judge.composite_scorer import CompositeScorer, EvaluationResults


class CompositeScenarioTestData:
    """Generator for synthetic evaluation results representing performance scenarios."""

    @staticmethod
    def create_high_quality_fast_scenario() -> EvaluationResults:
        """Create high quality, fast execution scenario."""
        return EvaluationResults(
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
                clarity=0.86,
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
        )

    @staticmethod
    def create_high_quality_slow_scenario() -> EvaluationResults:
        """Create high quality, slow execution scenario."""
        return EvaluationResults(
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
                clarity=0.88,
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

    @staticmethod
    def create_low_quality_fast_scenario() -> EvaluationResults:
        """Create low quality, fast execution scenario."""
        return EvaluationResults(
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
                clarity=0.33,
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

    @staticmethod
    def create_low_quality_slow_scenario() -> EvaluationResults:
        """Create low quality, slow execution scenario."""
        return EvaluationResults(
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
                clarity=0.27,
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
        )

    @staticmethod
    def create_mixed_performance_scenario() -> EvaluationResults:
        """Create mixed performance profile scenario."""
        return EvaluationResults(
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
                clarity=0.60,
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
        )


class TestCompositeScoringSCenarios:
    """Test composite scoring across performance scenarios."""

    @pytest.fixture
    def composite_scorer(self):
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    @pytest.fixture
    def scenario_data(self):
        """Fixture providing scenario test data."""
        return CompositeScenarioTestData()

    @pytest.mark.parametrize(
        "scenario_name,expected_recommendation",
        [
            ("high_quality_fast", ["accept"]),
            ("high_quality_slow", ["accept", "weak_accept"]),
            ("low_quality_fast", ["weak_reject", "reject"]),
            ("low_quality_slow", ["reject"]),
            ("mixed_performance", ["weak_accept", "weak_reject"]),
        ],
    )
    def test_composite_scoring_scenarios(
        self,
        composite_scorer,
        scenario_data,
        scenario_name,
        expected_recommendation,
    ):
        """Test composite scoring across performance scenarios."""
        scenario_method = getattr(scenario_data, f"create_{scenario_name}_scenario")
        evaluation_results = scenario_method()

        composite_result = composite_scorer.evaluate_composite(evaluation_results)

        assert composite_result is not None, (
            f"Composite result should not be None for {scenario_name}"
        )
        assert 0.0 <= composite_result.composite_score <= 1.0

        assert composite_result.recommendation in expected_recommendation, (
            f"Recommendation '{composite_result.recommendation}' not in expected "
            f"{expected_recommendation} for {scenario_name} "
            f"(score={composite_result.composite_score:.3f})"
        )

    def test_recommendation_boundary_conditions(self, composite_scorer):
        """Recommendation mapping at exact threshold boundaries."""
        thresholds = composite_scorer.thresholds

        boundary_test_cases = [
            (thresholds["accept"], "accept"),
            (thresholds["accept"] - 0.001, "weak_accept"),
            (thresholds["weak_accept"], "weak_accept"),
            (thresholds["weak_accept"] - 0.001, "weak_reject"),
            (thresholds["weak_reject"], "weak_reject"),
            (thresholds["weak_reject"] - 0.001, "reject"),
        ]

        for score, expected_recommendation in boundary_test_cases:
            actual_recommendation = composite_scorer.map_to_recommendation(score)

            assert actual_recommendation == expected_recommendation, (
                f"Score {score} should map to '{expected_recommendation}', "
                f"got '{actual_recommendation}'"
            )

    def test_scenario_ranking_accuracy(self, composite_scorer, scenario_data):
        """Scenarios rank in expected quality order."""
        scenarios = {
            "high_quality_fast": scenario_data.create_high_quality_fast_scenario(),
            "high_quality_slow": scenario_data.create_high_quality_slow_scenario(),
            "mixed_performance": scenario_data.create_mixed_performance_scenario(),
            "low_quality_fast": scenario_data.create_low_quality_fast_scenario(),
            "low_quality_slow": scenario_data.create_low_quality_slow_scenario(),
        }

        scenario_scores = {}
        for name, results in scenarios.items():
            composite_result = composite_scorer.evaluate_composite(results)
            scenario_scores[name] = composite_result.composite_score

        assert scenario_scores["high_quality_fast"] >= scenario_scores["high_quality_slow"], (
            "High quality fast should score >= high quality slow"
        )
        assert scenario_scores["high_quality_slow"] >= scenario_scores["mixed_performance"], (
            "High quality slow should score >= mixed performance"
        )
        assert scenario_scores["mixed_performance"] >= scenario_scores["low_quality_fast"], (
            "Mixed performance should score >= low quality fast"
        )
        assert scenario_scores["low_quality_fast"] >= scenario_scores["low_quality_slow"], (
            "Low quality fast should score >= low quality slow"
        )

    def test_performance_vs_quality_tradeoffs(self, composite_scorer, scenario_data):
        """Quality should generally outweigh speed in the scoring system."""
        fast_low_quality = scenario_data.create_low_quality_fast_scenario()
        slow_high_quality = scenario_data.create_high_quality_slow_scenario()

        fast_result = composite_scorer.evaluate_composite(fast_low_quality)
        slow_result = composite_scorer.evaluate_composite(slow_high_quality)

        assert slow_result.composite_score > fast_result.composite_score, (
            f"High quality slow ({slow_result.composite_score:.3f}) should outscore "
            f"low quality fast ({fast_result.composite_score:.3f})"
        )

        assert slow_result.recommendation in ["accept", "weak_accept"], (
            f"High quality should get positive recommendation, got {slow_result.recommendation}"
        )
        assert fast_result.recommendation in ["weak_reject", "reject"], (
            f"Low quality should get negative recommendation, got {fast_result.recommendation}"
        )
