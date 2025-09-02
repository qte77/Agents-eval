#!/usr/bin/env python3
"""
Composite scoring edge cases and error condition tests.

This module tests handling of missing tier results, extreme metric values,
error conditions, and fallback scoring mechanisms to ensure robust operation
under adverse conditions.
"""

import json
import sys
import tempfile
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


class EdgeCaseTestData:
    """Generator for edge case test data."""

    @staticmethod
    def create_missing_tier1_evaluation() -> EvaluationResults:
        """Create evaluation with missing Tier 1 results."""
        return EvaluationResults(
            tier1=None,  # Missing tier
            tier2=Tier2Result(
                technical_accuracy=0.75,
                constructiveness=0.70,
                planning_rationality=0.78,
                overall_quality=0.74,
                execution_time=6.2,
                success=True,
                cost_usd=0.025,
                tokens_used=170,
            ),
            tier3=Tier3Result(
                coordination_quality=0.72,
                tool_efficiency=0.68,
                path_convergence=0.70,
                task_balance=0.71,
                node_count=14,
                edge_count=20,
                execution_time=8.5,
                success=True,
            ),
        )

    @staticmethod
    def create_missing_tier2_evaluation() -> EvaluationResults:
        """Create evaluation with missing Tier 2 results."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.73,
                cosine_similarity=0.70,
                jaccard_similarity=0.67,
                bert_score=0.72,
                rouge_scores={"rouge1": 0.69, "rouge2": 0.65, "rougeL": 0.68},
                execution_time=1.1,
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=None,  # Missing tier
            tier3=Tier3Result(
                coordination_quality=0.71,
                tool_efficiency=0.69,
                path_convergence=0.66,
                task_balance=0.70,
                node_count=13,
                edge_count=19,
                execution_time=9.1,
                success=True,
            ),
        )

    @staticmethod
    def create_missing_tier3_evaluation() -> EvaluationResults:
        """Create evaluation with missing Tier 3 results."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.76,
                cosine_similarity=0.73,
                jaccard_similarity=0.69,
                bert_score=0.75,
                rouge_scores={"rouge1": 0.72, "rouge2": 0.68, "rougeL": 0.71},
                execution_time=1.3,
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
                constructiveness=0.74,
                planning_rationality=0.79,
                overall_quality=0.77,
                execution_time=5.9,
                success=True,
                cost_usd=0.023,
                tokens_used=165,
            ),
            tier3=None,  # Missing tier
        )

    @staticmethod
    def create_all_tiers_missing_evaluation() -> EvaluationResults:
        """Create evaluation with all tiers missing."""
        return EvaluationResults(tier1=None, tier2=None, tier3=None)

    @staticmethod
    def create_extreme_values_evaluation() -> EvaluationResults:
        """Create evaluation with extreme metric values."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=1.0,  # Maximum value
                cosine_similarity=0.0,  # Minimum value
                jaccard_similarity=1.0,
                bert_score=0.0,
                rouge_scores={"rouge1": 1.0, "rouge2": 0.0, "rougeL": 1.0},
                execution_time=0.01,  # Very fast
                success=True,
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=1.0,
                constructiveness=0.0,
                planning_rationality=1.0,
                overall_quality=0.5,  # Average of extremes
                execution_time=30.0,  # Very slow but still successful
                success=True,
                cost_usd=0.05,  # Maximum budget
                tokens_used=500,
            ),
            tier3=Tier3Result(
                coordination_quality=0.0,
                tool_efficiency=1.0,
                path_convergence=0.0,
                task_balance=1.0,
                node_count=1000,  # Maximum nodes
                edge_count=5000,  # Maximum edges
                execution_time=15.0,  # At timeout limit
                success=True,
            ),
        )

    @staticmethod
    def create_failed_tiers_evaluation() -> EvaluationResults:
        """Create evaluation with failed tier executions."""
        return EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.0,
                cosine_similarity=0.0,
                jaccard_similarity=0.0,
                bert_score=0.0,
                rouge_scores={"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0},
                execution_time=0.1,
                success=False,  # Failed execution
                tier_weights={
                    "semantic": 0.4,
                    "cosine": 0.3,
                    "jaccard": 0.2,
                    "time_taken": 0.1,
                },
            ),
            tier2=Tier2Result(
                technical_accuracy=0.0,
                constructiveness=0.0,
                planning_rationality=0.0,
                overall_quality=0.0,
                execution_time=10.0,  # Timeout
                success=False,  # Failed execution
                cost_usd=0.0,
                tokens_used=0,
            ),
            tier3=Tier3Result(
                coordination_quality=0.0,
                tool_efficiency=0.0,
                path_convergence=0.0,
                task_balance=0.0,
                node_count=0,
                edge_count=0,
                execution_time=15.0,  # Timeout
                success=False,  # Failed execution
            ),
        )


class TestCompositeScoreEdgeCases:
    """Test composite scoring edge cases and error conditions."""

    @pytest.fixture
    def composite_scorer(self):
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    @pytest.fixture
    def edge_case_data(self):
        """Fixture providing edge case test data."""
        return EdgeCaseTestData()

    async def test_missing_tier1_fallback(self, composite_scorer, edge_case_data):
        """Test fallback when Tier 1 results are missing."""
        evaluation = edge_case_data.create_missing_tier1_evaluation()

        # Should handle missing tier gracefully
        result = composite_scorer.calculate_composite_score(evaluation)

        # Should still produce valid result
        assert result is not None, "Should produce result even with missing Tier 1"
        assert 0.0 <= result.composite_score <= 1.0, "Score should be in valid range"
        assert result.recommendation in [
            "accept",
            "weak_accept",
            "weak_reject",
            "reject",
        ], f"Invalid recommendation: {result.recommendation}"

        # Tier 1 contribution should be 0 or handled appropriately
        assert result.tier1_contribution == 0.0, (
            "Missing tier should have 0 contribution"
        )

        print(
            f"✓ Missing Tier 1: score={result.composite_score:.3f}, "
            f"rec={result.recommendation}"
        )

    async def test_missing_tier2_fallback(self, composite_scorer, edge_case_data):
        """Test fallback when Tier 2 results are missing."""
        evaluation = edge_case_data.create_missing_tier2_evaluation()

        result = composite_scorer.calculate_composite_score(evaluation)

        assert result is not None, "Should produce result even with missing Tier 2"
        assert 0.0 <= result.composite_score <= 1.0, "Score should be in valid range"
        assert result.tier2_contribution == 0.0, (
            "Missing tier should have 0 contribution"
        )

        print(
            f"✓ Missing Tier 2: score={result.composite_score:.3f}, "
            f"rec={result.recommendation}"
        )

    async def test_missing_tier3_fallback(self, composite_scorer, edge_case_data):
        """Test fallback when Tier 3 results are missing."""
        evaluation = edge_case_data.create_missing_tier3_evaluation()

        result = composite_scorer.calculate_composite_score(evaluation)

        assert result is not None, "Should produce result even with missing Tier 3"
        assert 0.0 <= result.composite_score <= 1.0, "Score should be in valid range"
        assert result.tier3_contribution == 0.0, (
            "Missing tier should have 0 contribution"
        )

        print(
            f"✓ Missing Tier 3: score={result.composite_score:.3f}, "
            f"rec={result.recommendation}"
        )

    async def test_all_tiers_missing_fallback(self, composite_scorer, edge_case_data):
        """Test behavior when all tiers are missing."""
        evaluation = edge_case_data.create_all_tiers_missing_evaluation()

        # This should either produce a minimal fallback result or raise
        # appropriate exception
        try:
            result = composite_scorer.calculate_composite_score(evaluation)

            # If it returns a result, it should be minimal/fallback
            assert result is not None, "Should handle all missing tiers"
            assert result.composite_score >= 0.0, (
                "Fallback score should be non-negative"
            )
            assert result.recommendation == "reject", (
                "All missing should default to reject"
            )

            print(f"✓ All tiers missing: fallback score={result.composite_score:.3f}")

        except Exception as e:
            # If it raises an exception, that's also acceptable behavior
            assert "missing" in str(e).lower() or "empty" in str(e).lower(), (
                f"Should provide informative error message: {e}"
            )
            print(
                f"✓ All tiers missing: raised appropriate exception: {type(e).__name__}"
            )

    async def test_extreme_metric_values(self, composite_scorer, edge_case_data):
        """Test handling of extreme metric values (0.0, 1.0, etc.)."""
        evaluation = edge_case_data.create_extreme_values_evaluation()

        result = composite_scorer.calculate_composite_score(evaluation)

        # Should handle extreme values without error
        assert result is not None, "Should handle extreme values"
        assert 0.0 <= result.composite_score <= 1.0, (
            "Score should remain in valid range"
        )

        # Score should be reasonable despite extreme inputs
        assert result.composite_score > 0.0, (
            "Should not produce zero score with mixed extremes"
        )
        assert result.composite_score < 1.0, (
            "Should not produce perfect score with mixed extremes"
        )

        print(
            f"✓ Extreme values: score={result.composite_score:.3f}, "
            f"rec={result.recommendation}"
        )

    async def test_failed_tier_execution_handling(
        self, composite_scorer, edge_case_data
    ):
        """Test handling when tier executions fail."""
        evaluation = edge_case_data.create_failed_tiers_evaluation()

        result = composite_scorer.calculate_composite_score(evaluation)

        # Should handle failed executions
        assert result is not None, "Should handle failed tier executions"
        assert result.composite_score >= 0.0, (
            "Failed execution score should be non-negative"
        )

        # Failed executions should generally result in low scores
        assert result.composite_score < 0.5, (
            "Failed executions should result in low scores"
        )
        assert result.recommendation in ["weak_reject", "reject"], (
            f"Failed executions should get negative recommendation: "
            f"{result.recommendation}"
        )

        print(
            f"✓ Failed tiers: score={result.composite_score:.3f}, "
            f"rec={result.recommendation}"
        )

    async def test_nan_infinity_handling(self, composite_scorer):
        """Test handling of NaN and infinite values."""
        import math

        # Create evaluation with problematic values
        problematic_evaluation = EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=float("nan"),  # NaN value
                cosine_similarity=float("inf"),  # Infinity
                jaccard_similarity=-float("inf"),  # Negative infinity
                bert_score=0.75,  # Normal value
                rouge_scores={"rouge1": 0.7, "rouge2": float("nan"), "rougeL": 0.68},
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
                technical_accuracy=0.76,
                constructiveness=float("inf"),
                planning_rationality=0.78,
                overall_quality=0.75,
                execution_time=5.8,
                success=True,
                cost_usd=0.025,
                tokens_used=180,
            ),
            tier3=Tier3Result(
                coordination_quality=0.74,
                tool_efficiency=0.71,
                path_convergence=float("nan"),
                task_balance=0.73,
                node_count=15,
                edge_count=22,
                execution_time=8.4,
                success=True,
            ),
        )

        # Should either handle gracefully or raise informative error
        try:
            result = composite_scorer.calculate_composite_score(problematic_evaluation)

            # If it handles the values, result should be valid
            assert result is not None, "Should handle NaN/infinity values"
            assert not math.isnan(result.composite_score), (
                "Result score should not be NaN"
            )
            assert not math.isinf(result.composite_score), (
                "Result score should not be infinite"
            )
            assert 0.0 <= result.composite_score <= 1.0, (
                "Should produce valid score range"
            )

            print(f"✓ NaN/Infinity handling: score={result.composite_score:.3f}")

        except (ValueError, TypeError) as e:
            # If it raises an exception, should be informative
            assert any(
                word in str(e).lower() for word in ["nan", "inf", "invalid", "finite"]
            ), f"Should provide informative error for NaN/infinity: {e}"
            print(
                f"✓ NaN/Infinity handling: raised appropriate exception: "
                f"{type(e).__name__}"
            )

    async def test_invalid_configuration_handling(self, edge_case_data):
        """Test behavior with invalid configuration."""
        # Create temporary invalid config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            invalid_config = {
                "composite_scoring": {
                    "metrics_and_weights": {
                        "invalid_metric": 0.5,
                        "another_invalid": 0.7,  # Sum > 1.0
                    },
                    "recommendation_thresholds": {
                        "accept": 1.2,  # Invalid threshold > 1.0
                        "weak_accept": 0.8,
                        "weak_reject": 0.6,
                        "reject": 0.4,  # Thresholds in wrong order
                    },
                }
            }
            json.dump(invalid_config, f)
            temp_config_path = f.name

        try:
            # Should either handle gracefully or raise informative error
            try:
                CompositeScorer(temp_config_path)
                print(
                    "✓ Invalid config: handled gracefully with defaults or validation"
                )
            except (ValueError, KeyError, FileNotFoundError) as e:
                assert len(str(e)) > 0, "Should provide error message"
                print(
                    f"✓ Invalid config: raised appropriate exception: "
                    f"{type(e).__name__}"
                )

        finally:
            # Clean up temporary file
            Path(temp_config_path).unlink(missing_ok=True)

    async def test_partial_tier_data(self, composite_scorer):
        """Test handling of tiers with partial/incomplete data."""
        # Create tier results with missing optional fields
        incomplete_evaluation = EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.75,
                cosine_similarity=0.72,
                jaccard_similarity=0.68,
                bert_score=0.74,
                rouge_scores={},  # Empty scores dict
                execution_time=1.2,
                success=True,
                tier_weights={"semantic": 0.5, "cosine": 0.5},  # Incomplete weights
            ),
            tier2=Tier2Result(
                technical_accuracy=0.78,
                constructiveness=0.0,  # Zero value (could be missing data)
                planning_rationality=0.76,
                overall_quality=0.77,
                execution_time=5.8,
                success=True,
                cost_usd=0.0,  # Zero cost
                tokens_used=0,  # Zero tokens
            ),
            tier3=Tier3Result(
                coordination_quality=0.74,
                tool_efficiency=0.71,
                path_convergence=0.69,
                task_balance=0.73,
                node_count=0,  # Empty graph
                edge_count=0,
                execution_time=0.1,
                success=True,
            ),
        )

        result = composite_scorer.calculate_composite_score(incomplete_evaluation)

        # Should handle incomplete data gracefully
        assert result is not None, "Should handle incomplete tier data"
        assert 0.0 <= result.composite_score <= 1.0, "Score should be in valid range"

        print(
            f"✓ Partial data: score={result.composite_score:.3f}, "
            f"rec={result.recommendation}"
        )

    async def test_zero_execution_time_handling(self, composite_scorer):
        """Test handling of zero or negative execution times."""
        zero_time_evaluation = EvaluationResults(
            tier1=Tier1Result(
                semantic_similarity=0.75,
                cosine_similarity=0.72,
                jaccard_similarity=0.68,
                bert_score=0.74,
                rouge_scores={"rouge1": 0.71, "rouge2": 0.67, "rougeL": 0.70},
                execution_time=0.0,  # Zero execution time
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
                execution_time=-1.0,  # Negative execution time
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
                execution_time=0.0,  # Zero execution time
                success=True,
            ),
        )

        # Should handle zero/negative times without crashing
        result = composite_scorer.calculate_composite_score(zero_time_evaluation)

        assert result is not None, "Should handle zero/negative execution times"
        assert 0.0 <= result.composite_score <= 1.0, "Score should be in valid range"

        print(f"✓ Zero/negative times: score={result.composite_score:.3f}")


if __name__ == "__main__":
    """Run the edge case tests directly."""

    async def run_edge_case_tests():
        print("Running composite scoring edge case tests...")

        try:
            # Initialize components
            scorer = CompositeScorer()
            test_data = EdgeCaseTestData()

            print("✓ Scorer initialized for edge case testing")

            # Test missing tiers
            missing_tier_cases = [
                ("Tier 1", test_data.create_missing_tier1_evaluation()),
                ("Tier 2", test_data.create_missing_tier2_evaluation()),
                ("Tier 3", test_data.create_missing_tier3_evaluation()),
            ]

            print("\nTesting missing tier fallbacks:")
            for tier_name, evaluation in missing_tier_cases:
                try:
                    result = scorer.calculate_composite_score(evaluation)
                    print(
                        f"  ✓ Missing {tier_name}: score={result.composite_score:.3f}, "
                        f"rec={result.recommendation}"
                    )
                except Exception as e:
                    print(
                        f"  ✗ Missing {tier_name}: failed with {type(e).__name__}: {e}"
                    )

            # Test extreme values
            print("\nTesting extreme values:")
            try:
                extreme_eval = test_data.create_extreme_values_evaluation()
                result = scorer.calculate_composite_score(extreme_eval)
                print(
                    f"  ✓ Extreme values: score={result.composite_score:.3f}, "
                    f"rec={result.recommendation}"
                )
            except Exception as e:
                print(f"  ✗ Extreme values: failed with {type(e).__name__}: {e}")

            # Test failed executions
            print("\nTesting failed executions:")
            try:
                failed_eval = test_data.create_failed_tiers_evaluation()
                result = scorer.calculate_composite_score(failed_eval)
                print(
                    f"  ✓ Failed executions: score={result.composite_score:.3f}, "
                    f"rec={result.recommendation}"
                )
            except Exception as e:
                print(f"  ✗ Failed executions: failed with {type(e).__name__}: {e}")

            # Test all tiers missing
            print("\nTesting all tiers missing:")
            try:
                empty_eval = test_data.create_all_tiers_missing_evaluation()
                result = scorer.calculate_composite_score(empty_eval)
                print(
                    f"  ✓ All missing: score={result.composite_score:.3f}, "
                    f"rec={result.recommendation}"
                )
            except Exception as e:
                print(f"  ✓ All missing: appropriately failed with {type(e).__name__}")

            # Test configuration validation
            print("\nTesting configuration validation:")
            config_weights = scorer.weights
            weight_sum = sum(config_weights.values())
            print(f"  ✓ Weight sum: {weight_sum:.3f} (should be ~1.0)")

            config_thresholds = scorer.thresholds
            threshold_order = (
                config_thresholds["accept"]
                > config_thresholds["weak_accept"]
                > config_thresholds["weak_reject"]
                > config_thresholds["reject"]
            )
            print(f"  {'✓' if threshold_order else '✗'} Threshold ordering correct")

        except Exception as e:
            print(f"✗ Edge case testing failed: {e}")
            raise

        print("\n✅ Edge case testing completed!")

    import asyncio

    asyncio.run(run_edge_case_tests())
