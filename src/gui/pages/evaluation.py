"""
Streamlit page for Evaluation Results visualization.

Displays three-tier evaluation results including traditional metrics (Tier 1),
LLM-as-Judge scores (Tier 2), and graph analysis metrics (Tier 3).
Provides comparative visualization of graph-based vs text-based metrics.
"""

import streamlit as st

from app.data_models.evaluation_models import CompositeResult


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
        st.info(
            "No evaluation results available. Run an evaluation to see results here."
        )
        return

    # Display overall results
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

    # Display tier scores
    st.subheader("Tier Scores")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tier 1: Traditional Metrics",
            f"{result.tier1_score:.2f}",
            help="Text similarity and execution metrics",
        )

    with col2:
        if result.tier2_score > 0:
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

    # Warn about incomplete evaluation
    if not result.evaluation_complete:
        st.warning(
            "⚠️ Evaluation incomplete: Some tiers were not executed. "
            "Results may not reflect full system performance."
        )

    # Graph vs Text Comparison
    st.subheader("Graph Metrics vs Text Metrics Comparison")

    # Extract graph metrics (Tier 3)
    graph_metrics = {
        k: v
        for k, v in result.metric_scores.items()
        if k
        in [
            "path_convergence",
            "tool_selection_accuracy",
            "communication_overhead",
            "coordination_centrality",
            "task_distribution_balance",
        ]
    }

    # Extract text metrics (Tier 1)
    text_metrics = {
        k: v
        for k, v in result.metric_scores.items()
        if k in ["cosine_score", "jaccard_score", "semantic_score"]
    }

    if graph_metrics and text_metrics:
        # Create comparison data
        comparison_data = {
            "Graph Metrics": [graph_metrics.get(k, 0.0) for k in sorted(graph_metrics)],
            "Text Metrics": [text_metrics.get(k, 0.0) for k in sorted(text_metrics)],
        }

        st.bar_chart(comparison_data)

        # Display detailed metrics
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

    # Evaluation metadata
    with st.expander("Evaluation Details"):
        st.text(f"Timestamp: {result.timestamp}")
        st.text(f"Config Version: {result.config_version}")
        if result.weights_used:
            st.text("Tier Weights:")
            for tier, weight in result.weights_used.items():
                st.text(f"  {tier}: {weight}")
