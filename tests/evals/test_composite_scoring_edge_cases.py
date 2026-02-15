"""
Composite scoring edge cases and error condition tests.

This module tests handling of missing tier results, extreme metric values,
error conditions, and fallback scoring mechanisms to ensure robust operation
under adverse conditions.
"""

import pytest

from app.data_models.evaluation_models import (
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.judge.composite_scorer import CompositeScorer, EvaluationResults


def _make_tier1(**overrides: object) -> Tier1Result:
    """Create Tier1Result with sensible defaults, applying overrides."""
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


def _make_tier2(**overrides: object) -> Tier2Result:
    """Create Tier2Result with sensible defaults, applying overrides."""
    defaults: dict[str, object] = {
        "technical_accuracy": 0.78,
        "constructiveness": 0.73,
        "clarity": 0.75,
        "planning_rationality": 0.76,
        "overall_score": 0.76,
        "model_used": "gpt-4o-mini",
        "api_cost": 0.025,
        "fallback_used": False,
    }
    defaults.update(overrides)
    return Tier2Result(**defaults)  # type: ignore[arg-type]


def _make_tier3(**overrides: object) -> Tier3Result:
    """Create Tier3Result with sensible defaults, applying overrides."""
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


class TestCompositeScoreEdgeCases:
    """Test composite scoring edge cases and error conditions."""

    @pytest.fixture
    def composite_scorer(self):
        """Fixture providing initialized composite scorer."""
        return CompositeScorer()

    @pytest.mark.parametrize(
        "missing_tier",
        ["tier1", "tier2", "tier3", "all"],
    )
    def test_missing_tiers_raise_error(self, composite_scorer, missing_tier):
        """Missing tier results should raise ValueError."""
        tier1 = None if missing_tier in ["tier1", "all"] else _make_tier1()
        tier2 = None if missing_tier in ["tier2", "all"] else _make_tier2()
        tier3 = None if missing_tier in ["tier3", "all"] else _make_tier3()

        evaluation = EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)
        with pytest.raises(ValueError, match="Missing required tier results"):
            composite_scorer.extract_metric_values(evaluation)

    def test_zero_scores_produce_low_result(self, composite_scorer):
        """All-zero scores should result in low composite score and reject."""
        evaluation = EvaluationResults(
            tier1=_make_tier1(
                cosine_score=0.0,
                jaccard_score=0.0,
                semantic_score=0.0,
                time_score=0.1,
                task_success=0.0,
                overall_score=0.0,
                execution_time=0.1,
            ),
            tier2=_make_tier2(
                technical_accuracy=0.0,
                constructiveness=0.0,
                clarity=0.0,
                planning_rationality=0.0,
                overall_score=0.0,
            ),
            tier3=_make_tier3(
                coordination_centrality=0.1,
                tool_selection_accuracy=0.1,
                communication_overhead=0.0,
                path_convergence=0.0,
                task_distribution_balance=0.0,
                overall_score=0.0,
                graph_complexity=0,
            ),
        )

        result = composite_scorer.evaluate_composite(evaluation)

        assert result.composite_score < 0.4
        assert result.recommendation in ["weak_reject", "reject"]

    def test_zero_execution_time(self, composite_scorer):
        """Zero execution time should not cause errors."""
        evaluation = EvaluationResults(
            tier1=_make_tier1(execution_time=0.0, time_score=1.0),
            tier2=_make_tier2(),
            tier3=_make_tier3(),
        )

        result = composite_scorer.evaluate_composite(evaluation)

        assert result is not None
        assert 0.0 <= result.composite_score <= 1.0
