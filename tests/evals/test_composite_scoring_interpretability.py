"""
Composite scoring interpretability validation tests.

This module tests score consistency, metric contribution analysis, and
recommendation threshold boundary cases to ensure the composite scoring
system produces interpretable and reliable results.
"""

import pytest

from app.data_models.evaluation_models import (
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.evals.composite_scorer import CompositeScorer, EvaluationResults


def _make_evaluation(scale: float = 1.0) -> EvaluationResults:
    """Create evaluation results scaled by a factor for boundary testing.

    Args:
        scale: Scale factor applied to baseline scores (~0.75 baseline).
    """
    s = scale / 0.75  # Normalize to baseline

    return EvaluationResults(
        tier1=Tier1Result(
            cosine_score=min(1.0, 0.72 * s),
            jaccard_score=min(1.0, 0.68 * s),
            semantic_score=min(1.0, 0.75 * s),
            execution_time=max(0.5, 1.2 / s) if s > 0 else 1.2,
            time_score=min(1.0, 0.85 * s),
            task_success=1.0 if scale >= 0.3 else 0.0,
            overall_score=min(1.0, 0.74 * s),
        ),
        tier2=Tier2Result(
            technical_accuracy=min(1.0, 0.78 * s),
            constructiveness=min(1.0, 0.73 * s),
            clarity=min(1.0, 0.75 * s),
            planning_rationality=min(1.0, 0.76 * s),
            overall_score=min(1.0, 0.76 * s),
            model_used="gpt-4o-mini",
            api_cost=0.025,
            fallback_used=False,
        ),
        tier3=Tier3Result(
            coordination_centrality=min(1.0, 0.74 * s),
            tool_selection_accuracy=min(1.0, 0.71 * s),
            communication_overhead=min(1.0, 0.70 * s),
            path_convergence=min(1.0, 0.69 * s),
            task_distribution_balance=min(1.0, 0.73 * s),
            overall_score=min(1.0, 0.72 * s),
            graph_complexity=15,
        ),
    )


def _make_dominant_evaluation(dominant_metric: str) -> EvaluationResults:
    """Create evaluation where one metric dominates the score."""
    base = 0.3
    high = 0.95

    if dominant_metric == "similarity":
        return EvaluationResults(
            tier1=Tier1Result(
                cosine_score=high,
                jaccard_score=high,
                semantic_score=high,
                execution_time=0.8,
                time_score=0.9,
                task_success=1.0,
                overall_score=high,
            ),
            tier2=Tier2Result(
                technical_accuracy=base,
                constructiveness=base,
                clarity=base,
                planning_rationality=base,
                overall_score=base,
                model_used="gpt-4o-mini",
                api_cost=0.03,
                fallback_used=False,
            ),
            tier3=Tier3Result(
                coordination_centrality=base,
                tool_selection_accuracy=base,
                communication_overhead=base,
                path_convergence=base,
                task_distribution_balance=base,
                overall_score=base,
                graph_complexity=8,
            ),
        )
    elif dominant_metric == "planning":
        return EvaluationResults(
            tier1=Tier1Result(
                cosine_score=base,
                jaccard_score=base,
                semantic_score=base,
                execution_time=2.5,
                time_score=base,
                task_success=0.0,
                overall_score=base,
            ),
            tier2=Tier2Result(
                technical_accuracy=base,
                constructiveness=base,
                clarity=base,
                planning_rationality=high,
                overall_score=base,
                model_used="gpt-4o-mini",
                api_cost=0.02,
                fallback_used=False,
            ),
            tier3=Tier3Result(
                coordination_centrality=base,
                tool_selection_accuracy=base,
                communication_overhead=base,
                path_convergence=base,
                task_distribution_balance=base,
                overall_score=base,
                graph_complexity=8,
            ),
        )
    elif dominant_metric == "coordination":
        return EvaluationResults(
            tier1=Tier1Result(
                cosine_score=base,
                jaccard_score=base,
                semantic_score=base,
                execution_time=2.5,
                time_score=base,
                task_success=0.0,
                overall_score=base,
            ),
            tier2=Tier2Result(
                technical_accuracy=base,
                constructiveness=base,
                clarity=base,
                planning_rationality=base,
                overall_score=base,
                model_used="gpt-4o-mini",
                api_cost=0.03,
                fallback_used=False,
            ),
            tier3=Tier3Result(
                coordination_centrality=high,
                tool_selection_accuracy=base,
                communication_overhead=base,
                path_convergence=base,
                task_distribution_balance=base,
                overall_score=base,
                graph_complexity=25,
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

    def test_recommendation_boundary_conditions(self, composite_scorer):
        """Recommendation mapping at threshold boundaries."""
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
            actual_rec = composite_scorer.map_to_recommendation(score)
            assert actual_rec == expected_rec, (
                f"Score {score:.3f} should map to '{expected_rec}', got '{actual_rec}'"
            )

    def test_dominant_metric_impact(self, composite_scorer):
        """Individual metrics impact overall score differently."""
        dominant_metrics = ["similarity", "planning", "coordination"]
        results = {}

        for metric in dominant_metrics:
            evaluation = _make_dominant_evaluation(metric)
            result = composite_scorer.evaluate_composite(evaluation)
            results[metric] = result.composite_score

            assert result.composite_score > 0.2, (
                f"Dominant {metric} should improve score, got {result.composite_score}"
            )

        score_values = list(results.values())
        assert len(set(round(s, 6) for s in score_values)) > 1, (
            "Different dominant metrics should produce different scores"
        )
