#!/usr/bin/env python3
"""
Composite scoring scenario validation tests.

This module tests the composite scoring system across varied performance
scenarios as specified in the validation framework. Tests all 5 core scenarios:
high quality + fast/slow execution, low quality + fast/slow execution, and
mixed performance profiles.
"""

import sys
from pathlib import Path

import pytest

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.evaluation_models import (
    CompositeResult,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.evals.composite_scorer import CompositeScorer, EvaluationResults


class CompositeScenarioTestData:
    """Generator for synthetic evaluation results representing performance scenarios."""

    @staticmethod
    def create_high_quality_fast_scenario() -> EvaluationResults:
        """Create high quality, fast execution scenario."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.85,
                cosine_similarity=0.82,
                jaccard_similarity=0.78,
                bert_score=0.84,
                rouge_scores={"rouge1": 0.83, "rouge2": 0.79, "rougeL": 0.81},
                execution_time=0.7,  # Fast execution
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.88,
                constructiveness=0.85,
                planning_rationality=0.87,
                overall_quality=0.87,
                execution_time=4.2,  # Within time budget
                success=True,
                cost_usd=0.02,
                tokens_used=150,
            ),
            tier3=Tier3Result(
                coordination_quality=0.89,
                tool_efficiency=0.86,
                path_convergence=0.84,
                task_balance=0.88,
                node_count=12,
                edge_count=18,
                execution_time=6.1,  # Efficient execution
                success=True,
            ),
        )

    @staticmethod
    def create_high_quality_slow_scenario() -> EvaluationResults:
        """Create high quality, slow execution scenario."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.87,
                cosine_similarity=0.84,
                jaccard_similarity=0.81,
                bert_score=0.86,
                rouge_scores={"rouge1": 0.85, "rouge2": 0.82, "rougeL": 0.84},
                execution_time=2.8,  # Slower execution but still acceptable
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.91,
                constructiveness=0.89,
                planning_rationality=0.92,
                overall_quality=0.91,
                execution_time=8.7,  # Near time limit but high quality
                success=True,
                cost_usd=0.04,
                tokens_used=280,
            ),
            tier3=Tier3Result(
                coordination_quality=0.73,
                tool_efficiency=0.68,
                path_convergence=0.71,
                task_balance=0.75,
                node_count=45,
                edge_count=87,
                execution_time=13.2,  # Complex coordination, slower
                success=True,
            ),
        )

    @staticmethod
    def create_low_quality_fast_scenario() -> EvaluationResults:
        """Create low quality, fast execution scenario."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.32,
                cosine_similarity=0.29,
                jaccard_similarity=0.27,
                bert_score=0.31,
                rouge_scores={"rouge1": 0.28, "rouge2": 0.24, "rougeL": 0.26},
                execution_time=0.4,  # Very fast but poor quality
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.35,
                constructiveness=0.31,
                planning_rationality=0.28,
                overall_quality=0.31,
                execution_time=2.1,  # Fast completion
                success=True,
                cost_usd=0.01,
                tokens_used=85,
            ),
            tier3=Tier3Result(
                coordination_quality=0.22,
                tool_efficiency=0.25,
                path_convergence=0.19,
                task_balance=0.24,
                node_count=4,
                edge_count=3,
                execution_time=1.8,  # Minimal coordination
                success=True,
            ),
        )

    @staticmethod
    def create_low_quality_slow_scenario() -> EvaluationResults:
        """Create low quality, slow execution scenario."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.28,
                cosine_similarity=0.25,
                jaccard_similarity=0.23,
                bert_score=0.27,
                rouge_scores={"rouge1": 0.24, "rouge2": 0.19, "rougeL": 0.22},
                execution_time=3.2,  # Slow with poor results
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.29,
                constructiveness=0.26,
                planning_rationality=0.22,
                overall_quality=0.26,
                execution_time=9.8,  # Near timeout with poor quality
                success=True,
                cost_usd=0.04,
                tokens_used=320,
            ),
            tier3=Tier3Result(
                coordination_quality=0.18,
                tool_efficiency=0.15,
                path_convergence=0.14,
                task_balance=0.17,
                node_count=28,
                edge_count=31,
                execution_time=14.6,  # Complex but ineffective
                success=True,
            ),
        )

    @staticmethod
    def create_mixed_performance_scenario() -> EvaluationResults:
        """Create mixed performance profile scenario."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.64,
                cosine_similarity=0.58,
                jaccard_similarity=0.61,
                bert_score=0.62,
                rouge_scores={"rouge1": 0.59, "rouge2": 0.56, "rougeL": 0.60},
                execution_time=1.8,  # Moderate timing
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.52,
                constructiveness=0.67,
                planning_rationality=0.59,
                overall_quality=0.59,
                execution_time=6.4,  # Mid-range timing
                success=True,
                cost_usd=0.03,
                tokens_used=195,
            ),
            tier3=Tier3Result(
                coordination_quality=0.48,
                tool_efficiency=0.71,
                path_convergence=0.55,
                task_balance=0.62,
                node_count=19,
                edge_count=23,
                execution_time=8.9,  # Mixed coordination effectiveness
                success=True,
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
        "scenario_name,expected_score_range,expected_recommendation",
        [
            ("high_quality_fast", (0.8, 1.0), "accept"),
            ("high_quality_slow", (0.6, 0.8), "weak_accept"),
            ("low_quality_fast", (0.0, 0.4), "reject"),
            ("low_quality_slow", (0.0, 0.3), "reject"),
            ("mixed_performance", (0.4, 0.6), ["weak_accept", "weak_reject"]),
        ],
    )
    async def test_composite_scoring_scenarios(
        self,
        composite_scorer,
        scenario_data,
        scenario_name,
        expected_score_range,
        expected_recommendation,
    ):
        """Test composite scoring across performance scenarios."""
        # Get scenario data
        scenario_method = getattr(scenario_data, f"create_{scenario_name}_scenario")
        evaluation_results = scenario_method()

        # Execute composite scoring
        composite_result = composite_scorer.calculate_composite_score(
            evaluation_results
        )

        # Validate result structure
        assert composite_result is not None, (
            f"Composite result should not be None for {scenario_name}"
        )
        assert hasattr(composite_result, "composite_score"), (
            f"Missing composite_score for {scenario_name}"
        )
        assert hasattr(composite_result, "recommendation"), (
            f"Missing recommendation for {scenario_name}"
        )

        # Validate score range
        min_score, max_score = expected_score_range
        assert min_score <= composite_result.composite_score <= max_score, (
            f"Score {composite_result.composite_score:.3f} outside expected range "
            f"[{min_score}, {max_score}] for {scenario_name}"
        )

        # Validate recommendation mapping
        if isinstance(expected_recommendation, list):
            assert composite_result.recommendation in expected_recommendation, (
                f"Recommendation '{composite_result.recommendation}' not in expected "
                f"{expected_recommendation} for {scenario_name}"
            )
        else:
            assert composite_result.recommendation == expected_recommendation, (
                f"Expected '{expected_recommendation}', "
                f"got '{composite_result.recommendation}' for {scenario_name}"
            )

        # Log scenario results for debugging
        print(
            f"✓ {scenario_name}: score={composite_result.composite_score:.3f}, "
            f"recommendation={composite_result.recommendation}"
        )

    async def test_scenario_score_consistency(self, composite_scorer, scenario_data):
        """Test that scoring is consistent across multiple runs."""
        # Use high quality fast scenario for consistency testing
        evaluation_results = scenario_data.create_high_quality_fast_scenario()

        # Run scoring multiple times
        scores: list[float] = []
        recommendations: list[str] = []

        for _ in range(5):
            result = composite_scorer.calculate_composite_score(evaluation_results)
            scores.append(result.composite_score)
            recommendations.append(result.recommendation)

        # All scores should be identical (deterministic)
        assert all(abs(score - scores[0]) < 0.001 for score in scores), (
            f"Scores not consistent across runs: {scores}"
        )

        # All recommendations should be identical
        assert all(rec == recommendations[0] for rec in recommendations), (
            f"Recommendations not consistent across runs: {recommendations}"
        )

        # Standard deviation should be effectively zero
        import statistics

        score_stddev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        assert score_stddev < 0.001, (
            f"Score standard deviation too high: {score_stddev}"
        )

    async def test_metric_contribution_analysis(self, composite_scorer, scenario_data):
        """Test that individual metrics contribute as expected."""
        # Test with high quality scenario
        evaluation_results = scenario_data.create_high_quality_fast_scenario()
        result = composite_scorer.calculate_composite_score(evaluation_results)

        # Validate that scoring breakdown exists
        assert hasattr(result, "metric_breakdown") or hasattr(
            result, "tier_contributions"
        ), "Result should include metric breakdown information"

        # Calculate expected weighted contributions based on config
        config_weights = composite_scorer.weights

        # Verify weights sum to approximately 1.0
        total_weight = sum(config_weights.values())
        assert abs(total_weight - 1.0) < 0.01, (
            f"Weights should sum to 1.0, got {total_weight}"
        )

        # Validate individual weight ranges
        for metric, weight in config_weights.items():
            assert 0.0 < weight <= 1.0, (
                f"Weight for {metric} should be in (0, 1]: {weight}"
            )

    async def test_recommendation_boundary_conditions(self, composite_scorer):
        """Test recommendation mapping at exact threshold boundaries."""
        # Get recommendation thresholds from configuration
        thresholds = composite_scorer.thresholds

        # Test cases at exact boundaries
        boundary_test_cases = [
            (thresholds["accept"], "accept"),
            (thresholds["accept"] - 0.001, "weak_accept"),
            (thresholds["weak_accept"], "weak_accept"),
            (thresholds["weak_accept"] - 0.001, "weak_reject"),
            (thresholds["weak_reject"], "weak_reject"),
            (thresholds["weak_reject"] - 0.001, "reject"),
        ]

        for score, expected_recommendation in boundary_test_cases:
            # Create mock composite result for testing

            CompositeResult(
                composite_score=score,
                recommendation=expected_recommendation,  # This will be overridden
                tier1_contribution=0.33,
                tier2_contribution=0.33,
                tier3_contribution=0.34,
                evaluation_complete=True,
                execution_time=10.0,
            )

            # Get actual recommendation from scorer
            actual_recommendation = composite_scorer._map_score_to_recommendation(score)

            assert actual_recommendation == expected_recommendation, (
                f"Score {score} should map to '{expected_recommendation}', "
                f"got '{actual_recommendation}'"
            )

    async def test_scenario_ranking_accuracy(self, composite_scorer, scenario_data):
        """Test that scenarios rank in expected quality order."""
        # Create all scenarios
        scenarios = {
            "high_quality_fast": scenario_data.create_high_quality_fast_scenario(),
            "high_quality_slow": scenario_data.create_high_quality_slow_scenario(),
            "mixed_performance": scenario_data.create_mixed_performance_scenario(),
            "low_quality_fast": scenario_data.create_low_quality_fast_scenario(),
            "low_quality_slow": scenario_data.create_low_quality_slow_scenario(),
        }

        # Score all scenarios
        scenario_scores = {}
        for name, results in scenarios.items():
            composite_result = composite_scorer.calculate_composite_score(results)
            scenario_scores[name] = composite_result.composite_score

        # Validate expected ranking order
        assert (
            scenario_scores["high_quality_fast"] >= scenario_scores["high_quality_slow"]
        ), "High quality fast should score >= high quality slow"
        assert (
            scenario_scores["high_quality_slow"] >= scenario_scores["mixed_performance"]
        ), "High quality slow should score >= mixed performance"
        assert (
            scenario_scores["mixed_performance"] >= scenario_scores["low_quality_fast"]
        ), "Mixed performance should score >= low quality fast"
        assert (
            scenario_scores["low_quality_fast"] >= scenario_scores["low_quality_slow"]
        ), "Low quality fast should score >= low quality slow"

        # Log ranking for debugging
        sorted_scenarios = sorted(
            scenario_scores.items(), key=lambda x: x[1], reverse=True
        )
        print("✓ Scenario ranking (score, name):")
        for name, score in sorted_scenarios:
            print(f"  {score:.3f}: {name}")

    async def test_performance_vs_quality_tradeoffs(
        self, composite_scorer, scenario_data
    ):
        """Test how performance vs quality tradeoffs are handled in scoring."""
        fast_low_quality = scenario_data.create_low_quality_fast_scenario()
        slow_high_quality = scenario_data.create_high_quality_slow_scenario()

        fast_result = composite_scorer.calculate_composite_score(fast_low_quality)
        slow_result = composite_scorer.calculate_composite_score(slow_high_quality)

        # Quality should generally outweigh speed in the scoring system
        assert slow_result.composite_score > fast_result.composite_score, (
            f"High quality slow ({slow_result.composite_score:.3f}) should outscore "
            f"low quality fast ({fast_result.composite_score:.3f})"
        )

        # Different recommendation categories expected
        assert slow_result.recommendation in ["accept", "weak_accept"], (
            f"High quality should get positive recommendation, "
            f"got {slow_result.recommendation}"
        )
        assert fast_result.recommendation in ["weak_reject", "reject"], (
            f"Low quality should get negative recommendation, "
            f"got {fast_result.recommendation}"
        )


if __name__ == "__main__":
    """Run the composite scoring scenario tests directly."""

    async def run_scoring_scenarios():
        print("Running composite scoring scenario tests...")

        try:
            # Initialize components
            scorer = CompositeScorer()
            test_data = CompositeScenarioTestData()

            print(f"✓ Scorer initialized with {len(scorer.weights)} metrics")
            print(f"  Weights: {scorer.weights}")
            print(f"  Thresholds: {scorer.thresholds}")

            # Test all scenarios
            scenarios = [
                ("high_quality_fast", (0.8, 1.0), "accept"),
                ("high_quality_slow", (0.6, 0.8), "weak_accept"),
                ("low_quality_fast", (0.0, 0.4), "reject"),
                ("low_quality_slow", (0.0, 0.3), "reject"),
                ("mixed_performance", (0.4, 0.6), ["weak_accept", "weak_reject"]),
            ]

            results = {}
            for scenario_name, expected_range, expected_rec in scenarios:
                method_name = f"create_{scenario_name}_scenario"
                scenario_method = getattr(test_data, method_name)
                evaluation_results = scenario_method()

                composite_result = scorer.calculate_composite_score(evaluation_results)
                results[scenario_name] = composite_result

                min_score, max_score = expected_range
                score_in_range = (
                    min_score <= composite_result.composite_score <= max_score
                )

                if isinstance(expected_rec, list):
                    rec_matches = composite_result.recommendation in expected_rec
                else:
                    rec_matches = composite_result.recommendation == expected_rec

                status = "✓" if score_in_range and rec_matches else "✗"
                print(
                    f"{status} {scenario_name}: {composite_result.composite_score:.3f} "
                    f"({composite_result.recommendation})"
                )

            # Test ranking
            sorted_results = sorted(
                results.items(), key=lambda x: x[1].composite_score, reverse=True
            )
            print("\n✓ Final ranking:")
            for i, (name, result) in enumerate(sorted_results, 1):
                print(
                    f"  {i}. {name}: {result.composite_score:.3f} "
                    f"({result.recommendation})"
                )

        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

        print("\n✅ Composite scoring scenario testing completed!")

    import asyncio

    asyncio.run(run_scoring_scenarios())
