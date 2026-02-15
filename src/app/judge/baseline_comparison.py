"""
Baseline comparison engine for CompositeResult diffing.

Provides pairwise comparison of CompositeResult instances across three systems:
- PydanticAI MAS (multi-agent system)
- CC solo (Claude Code without orchestration)
- CC teams (Claude Code with Agent Teams orchestration)

Reuses existing CompositeResult model and CompositeScorer.extract_metric_values().
"""

from pydantic import BaseModel, Field

from app.data_models.evaluation_models import CompositeResult


class BaselineComparison(BaseModel):
    """Pairwise comparison of two CompositeResult instances.

    Captures metric-level and tier-level deltas between two evaluation results,
    with human-readable summary for interpretation.
    """

    label_a: str = Field(description="Label for first result (e.g., 'PydanticAI')")
    label_b: str = Field(description="Label for second result (e.g., 'CC-solo')")

    result_a: CompositeResult = Field(description="First CompositeResult instance")
    result_b: CompositeResult = Field(description="Second CompositeResult instance")

    metric_deltas: dict[str, float] = Field(
        description="Per-metric deltas (result_a - result_b) for 6 composite metrics"
    )

    tier_deltas: dict[str, float | None] = Field(
        description="Tier-level score differences (Tier 1, Tier 2, Tier 3). None if tier missing."
    )

    summary: str = Field(
        description="Human-readable comparison summary (e.g., 'PydanticAI scored +0.12 higher on technical_accuracy vs CC-solo')"
    )


def compare(
    result_a: CompositeResult,
    result_b: CompositeResult,
    label_a: str,
    label_b: str,
) -> BaselineComparison:
    """Compare two CompositeResult instances and return pairwise diff.

    Args:
        result_a: First CompositeResult instance
        result_b: Second CompositeResult instance
        label_a: Label for first result (e.g., "PydanticAI")
        label_b: Label for second result (e.g., "CC-solo")

    Returns:
        BaselineComparison with metric deltas, tier deltas, and summary

    Note:
        All deltas are calculated as (result_a - result_b).
        Positive delta means result_a scored higher.
    """
    # Calculate per-metric deltas for all 6 composite metrics
    metric_deltas = {}
    for metric in result_a.metric_scores.keys():
        score_a = result_a.metric_scores[metric]
        score_b = result_b.metric_scores.get(metric, 0.0)
        metric_deltas[metric] = score_a - score_b

    # Calculate tier-level deltas
    tier_deltas: dict[str, float | None] = {
        "tier1": result_a.tier1_score - result_b.tier1_score,
        "tier2": (
            None
            if result_a.tier2_score is None or result_b.tier2_score is None
            else result_a.tier2_score - result_b.tier2_score
        ),
        "tier3": result_a.tier3_score - result_b.tier3_score,
    }

    # Generate human-readable summary
    # Calculate average delta across all metrics
    avg_delta = sum(metric_deltas.values()) / len(metric_deltas)

    # Find metric with largest absolute delta
    max_metric = max(metric_deltas.items(), key=lambda x: abs(x[1]))
    max_metric_name = max_metric[0]
    max_metric_delta = max_metric[1]

    if avg_delta > 0:
        summary = (
            f"{label_a} scored +{avg_delta:.2f} higher on average vs {label_b} "
            f"(largest diff: {max_metric_name} +{max_metric_delta:.2f})"
        )
    elif avg_delta < 0:
        summary = (
            f"{label_a} scored {avg_delta:.2f} lower on average vs {label_b} "
            f"(largest diff: {max_metric_name} {max_metric_delta:.2f})"
        )
    else:
        summary = f"{label_a} and {label_b} scored identically on average"

    return BaselineComparison(
        label_a=label_a,
        label_b=label_b,
        result_a=result_a,
        result_b=result_b,
        metric_deltas=metric_deltas,
        tier_deltas=tier_deltas,
        summary=summary,
    )


def compare_all(
    pydantic_result: CompositeResult | None,
    cc_solo_result: CompositeResult | None,
    cc_teams_result: CompositeResult | None,
) -> list[BaselineComparison]:
    """Generate all three pairwise comparisons across the three systems.

    Args:
        pydantic_result: PydanticAI MAS evaluation result (or None)
        cc_solo_result: CC solo evaluation result (or None)
        cc_teams_result: CC teams evaluation result (or None)

    Returns:
        List of BaselineComparison instances for all valid pairwise comparisons.
        Empty list if fewer than 2 results provided.

    Note:
        Skips comparisons involving None results.
        Order: (PydanticAI vs CC-solo, PydanticAI vs CC-teams, CC-solo vs CC-teams)
    """
    comparisons = []

    # PydanticAI vs CC-solo
    if pydantic_result is not None and cc_solo_result is not None:
        comparisons.append(compare(pydantic_result, cc_solo_result, "PydanticAI", "CC-solo"))

    # PydanticAI vs CC-teams
    if pydantic_result is not None and cc_teams_result is not None:
        comparisons.append(compare(pydantic_result, cc_teams_result, "PydanticAI", "CC-teams"))

    # CC-solo vs CC-teams
    if cc_solo_result is not None and cc_teams_result is not None:
        comparisons.append(compare(cc_solo_result, cc_teams_result, "CC-solo", "CC-teams"))

    return comparisons
