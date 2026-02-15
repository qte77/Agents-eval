"""
Streamlit page for Evaluation Results visualization.

Displays three-tier evaluation results including traditional metrics (Tier 1),
LLM-as-Judge scores (Tier 2), and graph analysis metrics (Tier 3).
Provides comparative visualization of graph-based vs text-based metrics.
"""

import streamlit as st

from app.data_models.evaluation_models import CompositeResult
from app.judge.baseline_comparison import BaselineComparison


def _extract_graph_metrics(metric_scores: dict[str, float]) -> dict[str, float]:
    """Extract graph-specific metrics from metric scores.

    Args:
        metric_scores: Dictionary of all metric scores.

    Returns:
        Dictionary containing only graph metrics (Tier 3).
    """
    graph_metric_names = [
        "path_convergence",
        "tool_selection_accuracy",
        "communication_overhead",
        "coordination_centrality",
        "task_distribution_balance",
    ]
    return {k: v for k, v in metric_scores.items() if k in graph_metric_names}


def _extract_text_metrics(metric_scores: dict[str, float]) -> dict[str, float]:
    """Extract text-specific metrics from metric scores.

    Args:
        metric_scores: Dictionary of all metric scores.

    Returns:
        Dictionary containing only text metrics (Tier 1).
    """
    text_metric_names = ["cosine_score", "jaccard_score", "semantic_score"]
    return {k: v for k, v in metric_scores.items() if k in text_metric_names}


def _render_overall_results(result: CompositeResult) -> None:
    """Render overall results section with composite score and recommendation.

    Args:
        result: CompositeResult containing evaluation data.
    """
    st.subheader("Overall Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Composite Score",
            f"{result.composite_score:.2f}",
            help="Weighted average across all evaluation tiers",
        )
    with col2:
        st.metric("Recommendation", result.recommendation.upper())
    with col3:
        st.metric(
            "Confidence",
            f"{abs(result.recommendation_weight):.2f}",
            help="Confidence in recommendation based on score magnitude",
        )


def _render_tier_scores(result: CompositeResult) -> None:
    """Render individual tier scores section.

    Args:
        result: CompositeResult containing tier scores.
    """
    st.subheader("Tier Scores")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tier 1: Traditional Metrics",
            f"{result.tier1_score:.2f}",
            help="Text similarity and execution metrics",
        )

    with col2:
        if result.tier2_score is not None and result.tier2_score > 0:
            st.metric(
                "Tier 2: LLM-as-Judge",
                f"{result.tier2_score:.2f}",
                help="Quality assessment by LLM evaluator",
            )
        else:
            st.metric("Tier 2: LLM-as-Judge", "N/A", help="Not evaluated")

    with col3:
        if result.tier3_score > 0:
            st.metric(
                "Tier 3: Graph Analysis",
                f"{result.tier3_score:.2f}",
                help="Agent coordination and tool usage metrics",
            )
        else:
            st.metric("Tier 3: Graph Analysis", "N/A", help="Not evaluated")

    if not result.evaluation_complete:
        st.warning(
            "⚠️ Evaluation incomplete: Some tiers were not executed. "
            "Results may not reflect full system performance."
        )


def _render_metrics_comparison(result: CompositeResult) -> None:
    """Render graph vs text metrics comparison section.

    Args:
        result: CompositeResult containing metric scores.
    """
    st.subheader("Graph Metrics vs Text Metrics Comparison")

    graph_metrics = _extract_graph_metrics(result.metric_scores)
    text_metrics = _extract_text_metrics(result.metric_scores)

    if graph_metrics and text_metrics:
        comparison_data = {
            "Graph Metrics": [graph_metrics.get(k, 0.0) for k in sorted(graph_metrics)],
            "Text Metrics": [text_metrics.get(k, 0.0) for k in sorted(text_metrics)],
        }

        st.bar_chart(comparison_data)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Graph Metrics (Tier 3)**")
            for metric, value in sorted(graph_metrics.items()):
                st.text(f"{metric}: {value:.3f}")

        with col2:
            st.markdown("**Text Metrics (Tier 1)**")
            for metric, value in sorted(text_metrics.items()):
                st.text(f"{metric}: {value:.3f}")
    else:
        st.info("Insufficient metric data for comparison visualization.")


def _render_three_way_table(comparisons: list[BaselineComparison]) -> None:
    """Render three-way comparison summary table."""
    st.markdown("**Three-Way Comparison Table**")
    comparison_data = []
    for comp in comparisons:
        comparison_data.append(
            {
                "Comparison": f"{comp.label_a} vs {comp.label_b}",
                "Tier 1 Δ": f"{comp.tier_deltas.get('tier1', 0):.3f}",
                "Tier 2 Δ": (
                    f"{comp.tier_deltas.get('tier2', 0):.3f}"
                    if comp.tier_deltas.get("tier2") is not None
                    else "N/A"
                ),
                "Tier 3 Δ": f"{comp.tier_deltas.get('tier3', 0):.3f}",
            }
        )
    st.dataframe(comparison_data, use_container_width=True)


def _render_tier_deltas(comp: BaselineComparison) -> None:
    """Render tier-level delta metrics."""
    st.markdown("**Tier-Level Differences**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Tier 1 Delta",
            f"{comp.tier_deltas.get('tier1', 0):.3f}",
            help=f"{comp.label_a} - {comp.label_b}",
        )
    with col2:
        if comp.tier_deltas.get("tier2") is not None:
            st.metric(
                "Tier 2 Delta",
                f"{comp.tier_deltas.get('tier2', 0):.3f}",
                help=f"{comp.label_a} - {comp.label_b}",
            )
        else:
            st.metric("Tier 2 Delta", "N/A", help="Tier 2 not available in one or both systems")
    with col3:
        st.metric(
            "Tier 3 Delta",
            f"{comp.tier_deltas.get('tier3', 0):.3f}",
            help=f"{comp.label_a} - {comp.label_b}",
        )


def _render_single_comparison(comp: BaselineComparison) -> None:
    """Render individual comparison details."""
    with st.expander(f"📊 {comp.label_a} vs {comp.label_b}"):
        st.write(comp.summary)
        _render_tier_deltas(comp)

        # Metric deltas bar chart
        if comp.metric_deltas:
            st.markdown("**Metric-Level Differences**")
            st.bar_chart(comp.metric_deltas)


def render_baseline_comparison(comparisons: list[BaselineComparison] | None) -> None:
    """Render baseline comparison section for Claude Code solo and teams.

    Args:
        comparisons: List of BaselineComparison instances or None.
    """
    if not comparisons:
        st.info(
            "No baseline comparisons available. "
            "Provide Claude Code artifact directories to compare."
        )
        return

    st.subheader("🔄 Baseline Comparisons")

    # Display three-way comparison table if we have 3 comparisons
    if len(comparisons) == 3:
        _render_three_way_table(comparisons)

    # Display individual comparisons
    for comp in comparisons:
        _render_single_comparison(comp)


def render_evaluation(result: CompositeResult | None = None) -> None:
    """Render evaluation results page with tier scores and metric comparisons.

    Displays:
    - Overall composite score and recommendation
    - Individual tier scores (Tier 1, 2, 3)
    - Bar chart comparing graph metrics vs text metrics
    - Detailed metric breakdowns
    - Baseline comparisons (if available in session state)

    Args:
        result: CompositeResult containing evaluation data, or None for empty state.
    """
    st.header("📊 Evaluation Results")

    if result is None:
        st.info("No evaluation results available. Run an evaluation to see results here.")

        # Show baseline configuration inputs even when no result
        st.subheader("🔧 Baseline Comparison Configuration")
        st.text_input(
            "Claude Code Solo Directory",
            key="cc_solo_dir_input",
            help="Path to Claude Code solo session export directory",
        )
        st.text_input(
            "Claude Code Teams Directory",
            key="cc_teams_dir_input",
            help="Path to Claude Code Agent Teams artifacts directory",
        )
        return

    _render_overall_results(result)
    _render_tier_scores(result)
    _render_metrics_comparison(result)

    # Render baseline comparisons if available in session state
    if "baseline_comparisons" in st.session_state:
        render_baseline_comparison(st.session_state["baseline_comparisons"])

    # Evaluation metadata
    with st.expander("Evaluation Details"):
        st.text(f"Timestamp: {result.timestamp}")
        st.text(f"Config Version: {result.config_version}")
        if result.weights_used:
            st.text("Tier Weights:")
            for tier, weight in result.weights_used.items():
                st.text(f"  {tier}: {weight}")
