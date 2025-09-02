#!/usr/bin/env python3
"""
Composite scoring interpretability validation tests.

This module tests score consistency, metric contribution analysis, and
recommendation threshold boundary cases to ensure the composite scoring
system produces interpretable and reliable results.
"""

import statistics
import sys
from pathlib import Path

import pytest

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.evaluation_models import (
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.evals.composite_scorer import CompositeScorer, EvaluationResults


class InterpretabilityTestData:
    """Generator for test data focused on interpretability validation."""

    @staticmethod
    def create_consistent_evaluation() -> EvaluationResults:
        """Create evaluation results for consistency testing."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.75,
                cosine_similarity=0.72,
                jaccard_similarity=0.68,
                bert_score=0.74,
                rouge_scores={"rouge1": 0.71, "rouge2": 0.67, "rougeL": 0.70},
                execution_time=1.2,
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.78,
                constructiveness=0.73,
                planning_rationality=0.76,
                overall_quality=0.76,
                execution_time=5.8,
                success=True,
                cost_usd=0.025,
                tokens_used=180,
            ),
            tier3=Tier3Result(
                coordination_quality=0.74,
                tool_efficiency=0.71,
                path_convergence=0.69,
                task_balance=0.73,
                node_count=15,
                edge_count=22,
                execution_time=8.4,
                success=True,
            ),
        )

    @staticmethod
    def create_boundary_test_evaluation(target_score: float) -> EvaluationResults:
        """Create evaluation tuned to produce specific composite score."""
        # Reason: Scale all metrics proportionally to target score for boundary testing
        scale_factor = target_score / 0.75  # Baseline around 0.75

        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=min(1.0, 0.75 * scale_factor),
                cosine_similarity=min(1.0, 0.72 * scale_factor),
                jaccard_similarity=min(1.0, 0.68 * scale_factor),
                bert_score=min(1.0, 0.74 * scale_factor),
                rouge_scores={
                    "rouge1": min(1.0, 0.71 * scale_factor),
                    "rouge2": min(1.0, 0.67 * scale_factor),
                    "rougeL": min(1.0, 0.70 * scale_factor),
                },
                execution_time=max(0.5, 1.2 / scale_factor),  # Inverse for time performance
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=min(1.0, 0.78 * scale_factor),
                constructiveness=min(1.0, 0.73 * scale_factor),
                planning_rationality=min(1.0, 0.76 * scale_factor),
                overall_quality=min(1.0, 0.76 * scale_factor),
                execution_time=max(2.0, 5.8 / scale_factor),  # Inverse for time performance
                success=True,
                cost_usd=0.025,
                tokens_used=180,
            ),
            tier3=Tier3Result(
                coordination_quality=min(1.0, 0.74 * scale_factor),
                tool_efficiency=min(1.0, 0.71 * scale_factor),
                path_convergence=min(1.0, 0.69 * scale_factor),
                task_balance=min(1.0, 0.73 * scale_factor),
                node_count=15,
                edge_count=22,
                execution_time=max(3.0, 8.4 / scale_factor),  # Inverse for time performance
                success=True,
            ),
        )

    @staticmethod
    def create_single_metric_dominant_evaluation(
        dominant_metric: str,
    ) -> EvaluationResults:
        """Create evaluation where one metric dominates the score."""
        base_score = 0.3  # Low baseline
        high_score = 0.95  # High score for dominant metric

        if dominant_metric == "similarity":
            # Make Tier 1 similarity metrics high
            return EvaluationResults(
                tier1=Tier1Result(
                    semantic_similarity=high_score,
                    cosine_similarity=high_score,
                    jaccard_similarity=high_score,
                    bert_score=high_score,
                    rouge_scores={
                        "rouge1": high_score,
                        "rouge2": high_score,
                        "rougeL": high_score,
                    },
                    execution_time=0.8,
                    success=True,
                    tier_weights={
                        "semantic": 0.4,
                        "cosine": 0.3,
                        "jaccard": 0.2,
                        "time_taken": 0.1,
                    },
                ),
                tier2=Tier2Result(
                    technical_accuracy=base_score,
                    constructiveness=base_score,
                    planning_rationality=base_score,
                    overall_quality=base_score,
                    execution_time=8.0,
                    success=True,
                    cost_usd=0.03,
                    tokens_used=200,
                ),
                tier3=Tier3Result(
                    coordination_quality=base_score,
                    tool_efficiency=base_score,
                    path_convergence=base_score,
                    task_balance=base_score,
                    node_count=8,
                    edge_count=10,
                    execution_time=12.0,
                    success=True,
                ),
            )
        elif dominant_metric == "planning":
            # Make Tier 2 planning rationality high
            return EvaluationResults(
                tier1=Tier1Result(
                    semantic_similarity=base_score,
                    cosine_similarity=base_score,
                    jaccard_similarity=base_score,
                    bert_score=base_score,
                    rouge_scores={
                        "rouge1": base_score,
                        "rouge2": base_score,
                        "rougeL": base_score,
                    },
                    execution_time=2.5,
                    success=True,
                    tier_weights={
                        "semantic": 0.4,
                        "cosine": 0.3,
                        "jaccard": 0.2,
                        "time_taken": 0.1,
                    },
                ),
                tier2=Tier2Result(
                    technical_accuracy=base_score,
                    constructiveness=base_score,
                    planning_rationality=high_score,  # Dominant metric
                    overall_quality=base_score,
                    execution_time=4.0,
                    success=True,
                    cost_usd=0.02,
                    tokens_used=150,
                ),
                tier3=Tier3Result(
                    coordination_quality=base_score,
                    tool_efficiency=base_score,
                    path_convergence=base_score,
                    task_balance=base_score,
                    node_count=8,
                    edge_count=10,
                    execution_time=12.0,
                    success=True,
                ),
            )
        elif dominant_metric == "coordination":
            # Make Tier 3 coordination quality high
            return EvaluationResults(
                tier1=Tier1Result(
                    semantic_similarity=base_score,
                    cosine_similarity=base_score,
                    jaccard_similarity=base_score,
                    bert_score=base_score,
                    rouge_scores={
                        "rouge1": base_score,
                        "rouge2": base_score,
                        "rougeL": base_score,
                    },
                    execution_time=2.5,
                    success=True,
                    tier_weights={
                        "semantic": 0.4,
                        "cosine": 0.3,
                        "jaccard": 0.2,
                        "time_taken": 0.1,
                    },
                ),
                tier2=Tier2Result(
                    technical_accuracy=base_score,
                    constructiveness=base_score,
                    planning_rationality=base_score,
                    overall_quality=base_score,
                    execution_time=8.0,
                    success=True,
                    cost_usd=0.03,
                    tokens_used=200,
                ),
                tier3=Tier3Result(
                    coordination_quality=high_score,  # Dominant metric
                    tool_efficiency=base_score,
                    path_convergence=base_score,
                    task_balance=base_score,
                    node_count=25,
                    edge_count=40,
                    execution_time=6.0,
                    success=True,
                ),
            )
        else:
            raise ValueError(f"Unknown dominant metric: {dominant_metric}")


class TestCompositeScoreInterpretability:
    """Test composite scoring interpretability and consistency."""

    @pytest.fixture
    def composite_scorer(self):
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    @pytest.fixture
    def test_data(self):
        """Fixture providing interpretability test data."""
        return InterpretabilityTestData()

    async def test_scoring_consistency(self, composite_scorer, test_data):
        """Test score consistency across multiple evaluations."""
        evaluation_results = test_data.create_consistent_evaluation()

        # Run scoring multiple times
        scores: list[float] = []
        recommendations: list[str] = []

        for run in range(10):
            result = composite_scorer.calculate_composite_score(evaluation_results)
            scores.append(result.composite_score)
            recommendations.append(result.recommendation)

        # Validate consistency
        assert len(set(scores)) == 1, f"Scores not consistent across runs: {set(scores)}"
        assert len(set(recommendations)) == 1, f"Recommendations not consistent: {set(recommendations)}"

        # Calculate statistical measures
        score_mean = statistics.mean(scores)
        score_stddev = statistics.stdev(scores) if len(scores) > 1 else 0.0

        # Standard deviation should be effectively zero
        assert score_stddev < 0.001, f"Score standard deviation too high: {score_stddev}"

        print(f"✓ Consistency test: {len(scores)} runs, score={score_mean:.6f}, stddev={score_stddev:.6f}")

    async def test_recommendation_boundary_conditions(self, composite_scorer):
        """Test recommendation mapping at threshold boundaries."""
        thresholds = composite_scorer.thresholds

        # Test cases: (score, expected_recommendation)
        boundary_cases = [
            # At exact thresholds
            (thresholds["accept"], "accept"),
            (thresholds["weak_accept"], "weak_accept"),
            (thresholds["weak_reject"], "weak_reject"),
            (thresholds["reject"], "reject"),
            # Just below thresholds
            (thresholds["accept"] - 0.001, "weak_accept"),
            (thresholds["weak_accept"] - 0.001, "weak_reject"),
            (thresholds["weak_reject"] - 0.001, "reject"),
            # Edge cases
            (1.0, "accept"),
            (0.0, "reject"),
        ]

        for score, expected_rec in boundary_cases:
            # Use scorer's internal recommendation mapping method
            actual_rec = composite_scorer._map_score_to_recommendation(score)

            assert actual_rec == expected_rec, f"Score {score:.3f} should map to '{expected_rec}', got '{actual_rec}'"

        print(f"✓ Boundary conditions: tested {len(boundary_cases)} threshold cases")

    async def test_metric_weight_validation(self, composite_scorer):
        """Validate metric weights sum to 1.0 and apply correctly."""
        weights = composite_scorer.weights

        # Validate weights sum to 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01, f"Weights sum to {total_weight}, should be ~1.0"

        # Validate individual weights are reasonable
        for metric, weight in weights.items():
            assert 0.0 < weight <= 1.0, f"Weight for {metric} out of range: {weight}"
            assert weight >= 0.1, f"Weight for {metric} suspiciously low: {weight}"

        # Validate expected metrics are present (from config)
        expected_metrics = {
            "time_taken",
            "task_success",
            "coordination_quality",
            "tool_efficiency",
            "planning_rationality",
            "output_similarity",
        }
        actual_metrics = set(weights.keys())

        assert actual_metrics == expected_metrics, (
            f"Metric mismatch. Expected: {expected_metrics}, Got: {actual_metrics}"
        )

        print(f"✓ Weight validation: {len(weights)} metrics, total={total_weight:.3f}")
        for metric, weight in weights.items():
            print(f"  {metric}: {weight:.3f}")

    async def test_metric_contribution_analysis(self, composite_scorer, test_data):
        """Test individual metric contribution calculations."""
        # Test with different scenarios to see metric contributions
        evaluation_results = test_data.create_consistent_evaluation()
        result = composite_scorer.calculate_composite_score(evaluation_results)

        # Validate that tier contributions are provided
        assert hasattr(result, "tier1_contribution"), "Missing tier1_contribution"
        assert hasattr(result, "tier2_contribution"), "Missing tier2_contribution"
        assert hasattr(result, "tier3_contribution"), "Missing tier3_contribution"

        # Tier contributions should sum to approximately 1.0
        total_contribution = result.tier1_contribution + result.tier2_contribution + result.tier3_contribution
        assert abs(total_contribution - 1.0) < 0.1, f"Tier contributions sum to {total_contribution}, should be ~1.0"

        # All contributions should be non-negative
        assert result.tier1_contribution >= 0, "Tier 1 contribution should be non-negative"
        assert result.tier2_contribution >= 0, "Tier 2 contribution should be non-negative"
        assert result.tier3_contribution >= 0, "Tier 3 contribution should be non-negative"

        print(
            f"✓ Metric contributions: T1={result.tier1_contribution:.3f}, "
            f"T2={result.tier2_contribution:.3f}, T3={result.tier3_contribution:.3f}"
        )

    async def test_score_interpretability_ranges(self, composite_scorer, test_data):
        """Test that scores fall within interpretable ranges."""
        # Test various evaluation scenarios
        test_evaluations = [
            test_data.create_consistent_evaluation(),
            test_data.create_boundary_test_evaluation(0.9),  # High score
            test_data.create_boundary_test_evaluation(0.5),  # Medium score
            test_data.create_boundary_test_evaluation(0.2),  # Low score
        ]

        for i, evaluation in enumerate(test_evaluations):
            result = composite_scorer.calculate_composite_score(evaluation)

            # Score should be within [0, 1] range
            assert 0.0 <= result.composite_score <= 1.0, (
                f"Score {result.composite_score} out of range for evaluation {i}"
            )

            # Score should be reasonable (not stuck at extremes unless justified)
            # Allow some tolerance for edge cases
            if i == 0:  # Consistent evaluation should be mid-range
                assert 0.1 < result.composite_score < 0.9, (
                    f"Consistent evaluation score seems extreme: {result.composite_score}"
                )

        print(f"✓ Interpretability ranges: tested {len(test_evaluations)} evaluation scenarios")

    async def test_dominant_metric_impact(self, composite_scorer, test_data):
        """Test how individual metrics impact overall score."""
        dominant_metrics = ["similarity", "planning", "coordination"]
        results = {}

        for metric in dominant_metrics:
            evaluation = test_data.create_single_metric_dominant_evaluation(metric)
            result = composite_scorer.calculate_composite_score(evaluation)
            results[metric] = result.composite_score

            # Dominant metric should produce reasonable score
            assert result.composite_score > 0.3, f"Dominant {metric} should improve score, got {result.composite_score}"

        # Test that different dominant metrics produce different scores
        score_values = list(results.values())
        assert len(set(score_values)) > 1, "Different dominant metrics should produce different scores"

        print("✓ Dominant metric impact:")
        for metric, score in results.items():
            print(f"  {metric} dominant: {score:.3f}")

    async def test_recommendation_distribution(self, composite_scorer, test_data):
        """Test that recommendation categories are used appropriately."""
        # Create evaluations targeting different score ranges
        target_scores = [0.9, 0.7, 0.5, 0.3, 0.1]
        recommendation_counts = {}

        for target in target_scores:
            evaluation = test_data.create_boundary_test_evaluation(target)
            result = composite_scorer.calculate_composite_score(evaluation)

            rec = result.recommendation
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

        # Should use multiple recommendation categories
        assert len(recommendation_counts) > 1, "Should use multiple recommendation categories"

        # Validate that all recommendations are valid
        valid_recommendations = {"accept", "weak_accept", "weak_reject", "reject"}
        for rec in recommendation_counts.keys():
            assert rec in valid_recommendations, f"Invalid recommendation: {rec}"

        print("✓ Recommendation distribution:")
        for rec, count in recommendation_counts.items():
            print(f"  {rec}: {count} cases")

    async def test_score_granularity(self, composite_scorer, test_data):
        """Test that scoring system provides adequate granularity."""
        # Generate evaluations with small variations
        base_evaluation = test_data.create_consistent_evaluation()
        scores: list[float] = []

        # Create slight variations in the evaluation results
        for variation in range(5):
            # Slightly modify the base evaluation
            modified_evaluation = EvaluationResults(
                tier1=Tier1Result(
                    semantic_similarity=base_evaluation.tier1.semantic_similarity + variation * 0.01,
                    cosine_similarity=base_evaluation.tier1.cosine_similarity + variation * 0.01,
                    jaccard_similarity=base_evaluation.tier1.jaccard_similarity + variation * 0.01,
                    bert_score=base_evaluation.tier1.bert_score + variation * 0.01,
                    rouge_scores=base_evaluation.tier1.rouge_scores,
                    execution_time=base_evaluation.tier1.execution_time,
                    success=True,
                    tier_weights=base_evaluation.tier1.tier_weights,
                ),
                tier2=base_evaluation.tier2,
                tier3=base_evaluation.tier3,
            )

            result = composite_scorer.calculate_composite_score(modified_evaluation)
            scores.append(result.composite_score)

        # Scores should show variation (not all identical)
        unique_scores = set(f"{score:.6f}" for score in scores)
        assert len(unique_scores) > 1, "Scoring should be sensitive to small input changes"

        # But variation should be reasonable (not chaotic)
        score_range = max(scores) - min(scores)
        assert score_range < 0.1, f"Score variation too large for small input changes: {score_range}"

        print(f"✓ Score granularity: {len(unique_scores)} unique scores, range={score_range:.6f}")


if __name__ == "__main__":
    """Run the interpretability tests directly."""

    async def run_interpretability_tests():
        print("Running composite scoring interpretability tests...")

        try:
            # Initialize components
            scorer = CompositeScorer()
            test_data = InterpretabilityTestData()

            print("✓ Scorer initialized")
            print(f"  Weights: {scorer.weights}")
            print(f"  Thresholds: {scorer.thresholds}")

            # Test weight validation
            weights = scorer.weights
            total_weight = sum(weights.values())
            print(f"✓ Weight validation: {len(weights)} metrics, sum={total_weight:.3f}")

            # Test consistency
            evaluation = test_data.create_consistent_evaluation()

            scores = []
            for _ in range(5):
                result = scorer.calculate_composite_score(evaluation)
                scores.append(result.composite_score)

            score_consistency = len(set(scores)) == 1
            print(
                f"{'✓' if score_consistency else '✗'} Consistency: {scores[0]:.6f} "
                f"({'identical' if score_consistency else 'variable'} across runs)"
            )

            # Test boundary conditions
            thresholds = scorer.thresholds
            boundary_tests = [
                (thresholds["accept"], "accept"),
                (thresholds["weak_accept"], "weak_accept"),
                (thresholds["weak_reject"], "weak_reject"),
                (0.95, "accept"),
                (0.3, "reject"),
            ]

            print("✓ Boundary condition tests:")
            for score, expected in boundary_tests:
                actual = scorer._map_score_to_recommendation(score)
                status = "✓" if actual == expected else "✗"
                print(f"  {status} Score {score:.3f} → {actual} (expected {expected})")

            # Test metric contributions
            result = scorer.calculate_composite_score(evaluation)
            tier_sum = result.tier1_contribution + result.tier2_contribution + result.tier3_contribution
            print(f"✓ Tier contributions sum to {tier_sum:.3f}")
            print(
                f"  T1: {result.tier1_contribution:.3f}, "
                f"T2: {result.tier2_contribution:.3f}, "
                f"T3: {result.tier3_contribution:.3f}"
            )

        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

        print("\n✅ Interpretability testing completed!")

    import asyncio

    asyncio.run(run_interpretability_tests())
