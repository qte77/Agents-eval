"""
Tests for baseline comparison engine.

Tests the BaselineComparison model and comparison functions that diff
CompositeResult instances across PydanticAI MAS, CC solo, and CC teams.
"""

from datetime import datetime, timezone

import pytest
from hypothesis import given, strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import CompositeResult
from app.judge.baseline_comparison import BaselineComparison, compare, compare_all


# Hypothesis strategies for generating valid CompositeResult instances
@st.composite
def composite_result_strategy(draw):
    """Generate valid CompositeResult instances for property testing."""
    # Generate metric scores (all normalized 0.0-1.0)
    metric_scores = {
        "time_taken": draw(st.floats(min_value=0.0, max_value=1.0)),
        "task_success": draw(st.floats(min_value=0.0, max_value=1.0)),
        "coordination_quality": draw(st.floats(min_value=0.0, max_value=1.0)),
        "tool_efficiency": draw(st.floats(min_value=0.0, max_value=1.0)),
        "planning_rationality": draw(st.floats(min_value=0.0, max_value=1.0)),
        "output_similarity": draw(st.floats(min_value=0.0, max_value=1.0)),
    }

    composite_score = draw(st.floats(min_value=0.0, max_value=1.0))

    # Map score to recommendation
    if composite_score >= 0.8:
        recommendation = "accept"
        rec_weight = 1.0
    elif composite_score >= 0.6:
        recommendation = "weak_accept"
        rec_weight = 0.7
    elif composite_score >= 0.4:
        recommendation = "weak_reject"
        rec_weight = -0.7
    else:
        recommendation = "reject"
        rec_weight = -1.0

    tier1_score = draw(st.floats(min_value=0.0, max_value=1.0))
    tier2_score = draw(st.one_of(
        st.none(),
        st.floats(min_value=0.0, max_value=1.0)
    ))
    tier3_score = draw(st.floats(min_value=0.0, max_value=1.0))

    return CompositeResult(
        composite_score=composite_score,
        recommendation=recommendation,
        recommendation_weight=rec_weight,
        metric_scores=metric_scores,
        tier1_score=tier1_score,
        tier2_score=tier2_score,
        tier3_score=tier3_score,
        evaluation_complete=tier2_score is not None,
        timestamp=datetime.now(timezone.utc).isoformat(),
        config_version="1.0.0",
        weights_used={
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167,
            "tool_efficiency": 0.167,
            "planning_rationality": 0.167,
            "output_similarity": 0.167,
        },
        tiers_enabled=[1, 2, 3] if tier2_score is not None else [1, 3],
    )


class TestBaselineComparisonModel:
    """Tests for BaselineComparison Pydantic model."""

    def test_model_creation_with_all_fields(self):
        """BaselineComparison model accepts all required fields."""
        result_a = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.8,
                "task_success": 1.0,
                "coordination_quality": 0.7,
                "tool_efficiency": 0.6,
                "planning_rationality": 0.75,
                "output_similarity": 0.65,
            },
            tier1_score=0.8,
            tier2_score=0.75,
            tier3_score=0.65,
            evaluation_complete=True,
        )

        result_b = CompositeResult(
            composite_score=0.65,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.7,
                "task_success": 1.0,
                "coordination_quality": 0.6,
                "tool_efficiency": 0.5,
                "planning_rationality": 0.65,
                "output_similarity": 0.55,
            },
            tier1_score=0.7,
            tier2_score=0.65,
            tier3_score=0.6,
            evaluation_complete=True,
        )

        comparison = BaselineComparison(
            label_a="PydanticAI",
            label_b="CC-solo",
            result_a=result_a,
            result_b=result_b,
            metric_deltas={
                "time_taken": 0.1,
                "task_success": 0.0,
                "coordination_quality": 0.1,
                "tool_efficiency": 0.1,
                "planning_rationality": 0.1,
                "output_similarity": 0.1,
            },
            tier_deltas={
                "tier1": 0.1,
                "tier2": 0.1,
                "tier3": 0.05,
            },
            summary="PydanticAI scored +0.10 higher on average vs CC-solo",
        )

        assert comparison.label_a == "PydanticAI"
        assert comparison.label_b == "CC-solo"
        assert comparison.result_a == result_a
        assert comparison.result_b == result_b
        assert len(comparison.metric_deltas) == 6
        assert len(comparison.tier_deltas) == 3
        assert "PydanticAI" in comparison.summary


class TestCompareFunction:
    """Tests for pairwise compare() function."""

    def test_compare_returns_baseline_comparison(self):
        """compare() returns BaselineComparison with correct structure."""
        result_a = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=1.0,
            metric_scores={
                "time_taken": 0.9,
                "task_success": 1.0,
                "coordination_quality": 0.8,
                "tool_efficiency": 0.7,
                "planning_rationality": 0.8,
                "output_similarity": 0.7,
            },
            tier1_score=0.85,
            tier2_score=0.8,
            tier3_score=0.75,
            evaluation_complete=True,
        )

        result_b = CompositeResult(
            composite_score=0.6,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.7,
                "task_success": 1.0,
                "coordination_quality": 0.6,
                "tool_efficiency": 0.5,
                "planning_rationality": 0.6,
                "output_similarity": 0.5,
            },
            tier1_score=0.7,
            tier2_score=0.6,
            tier3_score=0.5,
            evaluation_complete=True,
        )

        comparison = compare(result_a, result_b, "PydanticAI", "CC-solo")

        assert isinstance(comparison, BaselineComparison)
        assert comparison.label_a == "PydanticAI"
        assert comparison.label_b == "CC-solo"
        assert comparison.result_a == result_a
        assert comparison.result_b == result_b

        # Metric deltas should be result_a - result_b
        assert comparison.metric_deltas["time_taken"] == pytest.approx(0.2, abs=0.01)
        assert comparison.metric_deltas["coordination_quality"] == pytest.approx(0.2, abs=0.01)

        # Tier deltas
        assert comparison.tier_deltas["tier1"] == pytest.approx(0.15, abs=0.01)
        assert comparison.tier_deltas["tier2"] == pytest.approx(0.2, abs=0.01)
        assert comparison.tier_deltas["tier3"] == pytest.approx(0.25, abs=0.01)

    def test_compare_handles_missing_tier2_in_one_result(self):
        """compare() handles when one result has Tier 2 and other doesn't."""
        result_with_tier2 = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=1.0,
            metric_scores={
                "time_taken": 0.9,
                "task_success": 1.0,
                "coordination_quality": 0.8,
                "tool_efficiency": 0.7,
                "planning_rationality": 0.8,
                "output_similarity": 0.7,
            },
            tier1_score=0.85,
            tier2_score=0.8,
            tier3_score=0.75,
            evaluation_complete=True,
        )

        result_without_tier2 = CompositeResult(
            composite_score=0.7,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.8,
                "task_success": 1.0,
                "coordination_quality": 0.7,
                "tool_efficiency": 0.6,
                "output_similarity": 0.6,
            },
            tier1_score=0.75,
            tier2_score=None,
            tier3_score=0.65,
            evaluation_complete=False,
        )

        comparison = compare(result_with_tier2, result_without_tier2, "PydanticAI", "CC-solo")

        # Should handle None tier2 gracefully
        assert "tier2" in comparison.tier_deltas
        # Delta should be None or indicate missing tier
        assert comparison.tier_deltas["tier2"] is None

    @given(result_a=composite_result_strategy(), result_b=composite_result_strategy())
    def test_compare_delta_symmetry(self, result_a, result_b):
        """Property: Swapping inputs negates all deltas (symmetry)."""
        comparison_ab = compare(result_a, result_b, "A", "B")
        comparison_ba = compare(result_b, result_a, "B", "A")

        # All metric deltas should be negated
        for metric in comparison_ab.metric_deltas.keys():
            delta_ab = comparison_ab.metric_deltas[metric]
            delta_ba = comparison_ba.metric_deltas[metric]
            assert delta_ab == pytest.approx(-delta_ba, abs=0.0001)

        # Tier deltas should be negated (skip None values)
        for tier in comparison_ab.tier_deltas.keys():
            delta_ab = comparison_ab.tier_deltas[tier]
            delta_ba = comparison_ba.tier_deltas[tier]
            if delta_ab is not None and delta_ba is not None:
                assert delta_ab == pytest.approx(-delta_ba, abs=0.0001)

    def test_compare_snapshot_output_structure(self):
        """Snapshot test for BaselineComparison model dump structure."""
        result_a = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.8,
                "task_success": 1.0,
                "coordination_quality": 0.7,
                "tool_efficiency": 0.6,
                "planning_rationality": 0.75,
                "output_similarity": 0.65,
            },
            tier1_score=0.8,
            tier2_score=0.75,
            tier3_score=0.65,
            evaluation_complete=True,
        )

        result_b = CompositeResult(
            composite_score=0.65,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.7,
                "task_success": 1.0,
                "coordination_quality": 0.6,
                "tool_efficiency": 0.5,
                "planning_rationality": 0.65,
                "output_similarity": 0.55,
            },
            tier1_score=0.7,
            tier2_score=0.65,
            tier3_score=0.6,
            evaluation_complete=True,
        )

        comparison = compare(result_a, result_b, "PydanticAI", "CC-solo")

        # Model dump should have expected structure
        dump = comparison.model_dump()

        assert dump == snapshot({
            "label_a": "PydanticAI",
            "label_b": "CC-solo",
            "result_a": dict,  # Full CompositeResult
            "result_b": dict,  # Full CompositeResult
            "metric_deltas": dict,  # 6 metrics
            "tier_deltas": dict,  # 3 tiers
            "summary": str,
        })


class TestCompareAllFunction:
    """Tests for compare_all() convenience function."""

    def test_compare_all_returns_three_comparisons(self):
        """compare_all() returns 3 pairwise comparisons."""
        pydantic_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=1.0,
            metric_scores={
                "time_taken": 0.9,
                "task_success": 1.0,
                "coordination_quality": 0.8,
                "tool_efficiency": 0.7,
                "planning_rationality": 0.8,
                "output_similarity": 0.7,
            },
            tier1_score=0.85,
            tier2_score=0.8,
            tier3_score=0.75,
            evaluation_complete=True,
        )

        cc_solo_result = CompositeResult(
            composite_score=0.7,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.8,
                "task_success": 1.0,
                "coordination_quality": 0.7,
                "tool_efficiency": 0.6,
                "planning_rationality": 0.7,
                "output_similarity": 0.6,
            },
            tier1_score=0.75,
            tier2_score=0.7,
            tier3_score=0.65,
            evaluation_complete=True,
        )

        cc_teams_result = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.85,
                "task_success": 1.0,
                "coordination_quality": 0.75,
                "tool_efficiency": 0.65,
                "planning_rationality": 0.75,
                "output_similarity": 0.65,
            },
            tier1_score=0.8,
            tier2_score=0.75,
            tier3_score=0.7,
            evaluation_complete=True,
        )

        comparisons = compare_all(pydantic_result, cc_solo_result, cc_teams_result)

        assert len(comparisons) == 3

        # First comparison: PydanticAI vs CC-solo
        assert comparisons[0].label_a == "PydanticAI"
        assert comparisons[0].label_b == "CC-solo"

        # Second comparison: PydanticAI vs CC-teams
        assert comparisons[1].label_a == "PydanticAI"
        assert comparisons[1].label_b == "CC-teams"

        # Third comparison: CC-solo vs CC-teams
        assert comparisons[2].label_a == "CC-solo"
        assert comparisons[2].label_b == "CC-teams"

    def test_compare_all_handles_none_results(self):
        """compare_all() skips comparisons when result is None."""
        pydantic_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=1.0,
            metric_scores={
                "time_taken": 0.9,
                "task_success": 1.0,
                "coordination_quality": 0.8,
                "tool_efficiency": 0.7,
                "planning_rationality": 0.8,
                "output_similarity": 0.7,
            },
            tier1_score=0.85,
            tier2_score=0.8,
            tier3_score=0.75,
            evaluation_complete=True,
        )

        cc_solo_result = CompositeResult(
            composite_score=0.7,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.8,
                "task_success": 1.0,
                "coordination_quality": 0.7,
                "tool_efficiency": 0.6,
                "planning_rationality": 0.7,
                "output_similarity": 0.6,
            },
            tier1_score=0.75,
            tier2_score=0.7,
            tier3_score=0.65,
            evaluation_complete=True,
        )

        # CC-teams is None
        comparisons = compare_all(pydantic_result, cc_solo_result, None)

        # Should only have 1 comparison (PydanticAI vs CC-solo)
        assert len(comparisons) == 1
        assert comparisons[0].label_a == "PydanticAI"
        assert comparisons[0].label_b == "CC-solo"

    def test_compare_all_snapshot_with_one_none(self):
        """Snapshot test for compare_all() output when one result is None."""
        pydantic_result = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.8,
                "task_success": 1.0,
                "coordination_quality": 0.7,
                "tool_efficiency": 0.6,
                "planning_rationality": 0.75,
                "output_similarity": 0.65,
            },
            tier1_score=0.8,
            tier2_score=0.75,
            tier3_score=0.65,
            evaluation_complete=True,
        )

        cc_solo_result = CompositeResult(
            composite_score=0.65,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={
                "time_taken": 0.7,
                "task_success": 1.0,
                "coordination_quality": 0.6,
                "tool_efficiency": 0.5,
                "planning_rationality": 0.65,
                "output_similarity": 0.55,
            },
            tier1_score=0.7,
            tier2_score=0.65,
            tier3_score=0.6,
            evaluation_complete=True,
        )

        comparisons = compare_all(pydantic_result, cc_solo_result, None)

        assert len(comparisons) == snapshot(1)
        assert comparisons[0].label_a == snapshot("PydanticAI")
        assert comparisons[0].label_b == snapshot("CC-solo")
