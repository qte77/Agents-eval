"""
Streamlit page for Evaluation Results visualization.

Displays three-tier evaluation results including traditional metrics (Tier 1),
LLM-as-Judge scores (Tier 2), and graph analysis metrics (Tier 3).
Provides comparative visualization of graph-based vs text-based metrics.
"""

from pathlib import Path

import streamlit as st

from app.data_models.evaluation_models import CompositeResult
from app.judge.baseline_comparison import BaselineComparison

# S8-F3.3: human-readable labels for metric snake_case keys (WCAG display clarity)
METRIC_LABELS: dict[str, str] = {
    "cosine_score": "Cosine Similarity",
    "jaccard_score": "Jaccard Similarity",
    "semantic_score": "Semantic Similarity",
    "path_convergence": "Path Convergence",
    "tool_selection_accuracy": "Tool Selection Accuracy",
    "coordination_centrality": "Coordination Centrality",
    "task_distribution_balance": "Task Distribution Balance",
}


def format_metric_label(metric_key: str) -> str:
    """Return a human-readable label for a metric key.

    Falls back to title-casing the key when no explicit mapping exists.

    Args:
        metric_key: Snake-case metric name (e.g. "cosine_score").

    Returns:
        Human-readable label string (e.g. "Cosine Similarity").
    """
    return METRIC_LABELS.get(metric_key, metric_key.replace("_", " ").title())


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


def _render_overall_results(
    result: CompositeResult,
    baseline_comparison: BaselineComparison | None = None,
) -> None:
    """Render overall results section with composite score and recommendation.

    Args:
        result: CompositeResult containing evaluation data.
        baseline_comparison: Optional baseline for delta indicators in metrics.
    """
    st.subheader("Overall Results")
    col1, col2, col3 = st.columns(3)

    # S8-F3.3: populate delta from baseline tier_deltas when available
    tier1_delta: float | None = None
    if baseline_comparison is not None:
        tier1_delta = baseline_comparison.tier_deltas.get("tier1")

    with col1:
        st.metric(
            "Composite Score",
            f"{result.composite_score:.2f}",
            delta=f"{tier1_delta:.3f}" if tier1_delta is not None else None,
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

    # S8-F8.2: display shortened run ID below score metrics
    execution_id: str | None = st.session_state.get("execution_id")
    if execution_id:
        st.caption(f"Run: {execution_id}")


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

        # S8-F3.3: dataframe alt text for bar chart (WCAG 1.1.1 accessibility)
        combined_rows = [
            {"Metric": format_metric_label(k), "Score": round(v, 3), "Category": "Graph (Tier 3)"}
            for k, v in sorted(graph_metrics.items())
        ] + [
            {"Metric": format_metric_label(k), "Score": round(v, 3), "Category": "Text (Tier 1)"}
            for k, v in sorted(text_metrics.items())
        ]
        st.dataframe(combined_rows, use_container_width=True)
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

        # S8-F3.3: baseline inputs in collapsed expander (progressive disclosure)
        with st.expander("🔧 Baseline Comparison Configuration", expanded=False):
            st.markdown(
                "Provide directory paths to Claude Code artifact exports to enable "
                "comparative evaluation against MAS results."
            )
            # S8-F8.2: auto-populate from known CC artifact location if it exists
            default_traces_dir = "logs/Agent_evals/traces/"
            default_value = default_traces_dir if Path(default_traces_dir).is_dir() else ""
            cc_solo_dir = st.text_input(
                "Claude Code Solo Directory",
                key="cc_solo_dir_input",
                value=default_value,
                help="Path to Claude Code solo session export directory",
            )
            # S8-F8.2: validate entered path exists on disk
            if cc_solo_dir and not Path(cc_solo_dir).is_dir():
                st.error(f"Directory not found: {cc_solo_dir}")

            cc_teams_dir = st.text_input(
                "Claude Code Teams Directory",
                key="cc_teams_dir_input",
                help="Path to Claude Code Agent Teams artifacts directory",
            )
            # S8-F8.2: validate entered path exists on disk
            if cc_teams_dir and not Path(cc_teams_dir).is_dir():
                st.error(f"Directory not found: {cc_teams_dir}")
        return

    _render_overall_results(result)
    _render_tier_scores(result)
    _render_metrics_comparison(result)

    # Render baseline comparisons if available in session state
    if "baseline_comparisons" in st.session_state:
        render_baseline_comparison(st.session_state["baseline_comparisons"])

    # Evaluation metadata
    with st.expander("Evaluation Details"):
        # S8-F8.2: show full execution_id in details expander
        full_execution_id: str | None = st.session_state.get("execution_id")
        if full_execution_id:
            st.text(f"Execution ID: {full_execution_id}")
        st.text(f"Timestamp: {result.timestamp}")
        st.text(f"Config Version: {result.config_version}")
        if result.weights_used:
            st.text("Tier Weights:")
            for tier, weight in result.weights_used.items():
                st.text(f"  {tier}: {weight}")
