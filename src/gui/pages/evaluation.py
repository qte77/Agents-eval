"""
Streamlit page for Evaluation Results visualization.

Displays three-tier evaluation results including traditional metrics (Tier 1),
LLM-as-Judge scores (Tier 2), and graph analysis metrics (Tier 3).
Provides comparative visualization of graph-based vs text-based metrics.
"""

import streamlit as st

from app.data_models.evaluation_models import CompositeResult


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


def render_evaluation(result: CompositeResult | None = None) -> None:
    """Render evaluation results page with tier scores and metric comparisons.

    Displays:
    - Overall composite score and recommendation
    - Individual tier scores (Tier 1, 2, 3)
    - Bar chart comparing graph metrics vs text metrics
    - Detailed metric breakdowns

    Args:
        result: CompositeResult containing evaluation data, or None for empty state.
    """
    st.header("📊 Evaluation Results")

    if result is None:
        st.info("No evaluation results available. Run an evaluation to see results here.")
        return

    _render_overall_results(result)
    _render_tier_scores(result)
    _render_metrics_comparison(result)

    # Evaluation metadata
    with st.expander("Evaluation Details"):
        st.text(f"Timestamp: {result.timestamp}")
        st.text(f"Config Version: {result.config_version}")
        if result.weights_used:
            st.text("Tier Weights:")
            for tier, weight in result.weights_used.items():
                st.text(f"  {tier}: {weight}")
