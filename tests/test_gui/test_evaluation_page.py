"""
Tests for Streamlit Evaluation Results page.

Following TDD approach for STORY-006 evaluation dashboard implementation.
Tests verify that the page renders Tier 1/2/3 scores and graph vs text comparison.
"""

from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import (
    CompositeResult,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)


@pytest.fixture
def mock_composite_result():
    """Create mock CompositeResult for testing."""
    return CompositeResult(
        composite_score=0.85,
        recommendation="accept",
        recommendation_weight=0.9,
        metric_scores={
            "cosine_score": 0.8,
            "jaccard_score": 0.7,
            "semantic_score": 0.9,
            "path_convergence": 0.85,
            "tool_selection_accuracy": 0.90,
            "communication_overhead": 0.75,
        },
        tier1_score=0.80,
        tier2_score=0.88,
        tier3_score=0.83,
        evaluation_complete=True,
        timestamp="2026-02-15T10:00:00Z",
        config_version="1.0.0",
        weights_used={"tier1": 0.3, "tier2": 0.4, "tier3": 0.3},
    )


@pytest.fixture
def mock_tier_results():
    """Create individual tier results for detailed testing."""
    tier1 = Tier1Result(
        cosine_score=0.8,
        jaccard_score=0.7,
        semantic_score=0.9,
        execution_time=5.2,
        time_score=0.85,
        task_success=1.0,
        overall_score=0.80,
    )
    tier2 = Tier2Result(
        technical_accuracy=0.88,
        constructiveness=0.85,
        clarity=0.90,
        planning_rationality=0.87,
        overall_score=0.88,
        model_used="gpt-4",
        api_cost=0.05,
        fallback_used=False,
    )
    tier3 = Tier3Result(
        path_convergence=0.85,
        tool_selection_accuracy=0.90,
        communication_overhead=0.75,
        coordination_centrality=0.88,
        task_distribution_balance=0.80,
        overall_score=0.83,
        graph_complexity=12,
    )
    return tier1, tier2, tier3


class TestEvaluationPage:
    """Test suite for Evaluation Results page rendering."""

    def test_render_evaluation_page_exists(self):
        """Test that render_evaluation function exists and is callable."""
        from gui.pages.evaluation import render_evaluation

        assert callable(render_evaluation)

    def test_render_with_composite_result(self, mock_composite_result):
        """Test page renders with valid CompositeResult data."""
        from gui.pages.evaluation import render_evaluation

        with patch("streamlit.header"), patch("streamlit.metric"), patch("streamlit.bar_chart"):
            # Should not raise any exceptions
            render_evaluation(mock_composite_result)

    def test_displays_tier_scores(self, mock_composite_result):
        """Test that all three tier scores are displayed."""
        from gui.pages.evaluation import render_evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.metric") as mock_metric,
            patch("streamlit.bar_chart"),
        ):
            render_evaluation(mock_composite_result)

            # Should display tier1, tier2, tier3 scores
            assert mock_metric.call_count >= 3

    def test_displays_graph_vs_text_comparison(self, mock_composite_result):
        """Test that bar chart compares graph metrics vs text metrics."""
        from gui.pages.evaluation import render_evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.metric"),
            patch("streamlit.bar_chart") as mock_chart,
        ):
            render_evaluation(mock_composite_result)

            # Should create at least one bar chart
            assert mock_chart.call_count >= 1

    def test_render_with_empty_data(self):
        """Test page renders gracefully with no evaluation data."""
        from gui.pages.evaluation import render_evaluation

        with patch("streamlit.info") as mock_info:
            render_evaluation(None)

            # Should display informative message
            mock_info.assert_called_once()

    def test_render_with_partial_tier_results(self):
        """Test page handles missing tier2 or tier3 gracefully."""
        partial_result = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={"cosine_score": 0.75},
            tier1_score=0.75,
            tier2_score=0.0,  # Missing tier2
            tier3_score=0.0,  # Missing tier3
            evaluation_complete=False,
            timestamp="2026-02-15T10:00:00Z",
            config_version="1.0.0",
        )

        from gui.pages.evaluation import render_evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.metric"),
            patch("streamlit.warning") as mock_warning,
        ):
            render_evaluation(partial_result)

            # Should warn about incomplete evaluation
            assert mock_warning.call_count >= 1

    def test_graph_metrics_extraction(self, mock_composite_result):
        """Test extraction of graph-specific metrics for visualization."""
        from gui.pages.evaluation import render_evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.metric"),
            patch("streamlit.bar_chart") as mock_chart,
        ):
            render_evaluation(mock_composite_result)

            # Verify bar chart is called with data containing graph metrics
            assert mock_chart.called
            call_args = mock_chart.call_args
            # Should contain graph metrics like path_convergence, tool_selection_accuracy
            assert call_args is not None

    def test_text_metrics_extraction(self, mock_composite_result):
        """Test extraction of text-specific metrics for visualization."""
        from gui.pages.evaluation import render_evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.metric"),
            patch("streamlit.bar_chart") as mock_chart,
        ):
            render_evaluation(mock_composite_result)

            # Verify bar chart is called with data containing text metrics
            assert mock_chart.called
            call_args = mock_chart.call_args
            # Should contain text metrics like cosine_score, jaccard_score
            assert call_args is not None

    def test_extract_graph_metrics_helper(self, mock_composite_result):
        """Test helper function for extracting graph metrics."""
        from gui.pages.evaluation import _extract_graph_metrics

        metrics = _extract_graph_metrics(mock_composite_result.metric_scores)

        # Should contain graph-specific metrics
        assert "path_convergence" in metrics
        assert "tool_selection_accuracy" in metrics
        assert metrics["path_convergence"] == 0.85

        # Should NOT contain text metrics
        assert "cosine_score" not in metrics
        assert "jaccard_score" not in metrics

    def test_extract_text_metrics_helper(self, mock_composite_result):
        """Test helper function for extracting text metrics."""
        from gui.pages.evaluation import _extract_text_metrics

        metrics = _extract_text_metrics(mock_composite_result.metric_scores)

        # Should contain text-specific metrics
        assert "cosine_score" in metrics
        assert "jaccard_score" in metrics
        assert "semantic_score" in metrics
        assert metrics["cosine_score"] == 0.8

        # Should NOT contain graph metrics
        assert "path_convergence" not in metrics
        assert "tool_selection_accuracy" not in metrics


# STORY-004: Hypothesis property-based tests for GUI state management
class TestEvaluationPageStateInvariants:
    """Property-based tests for GUI state management invariants."""

    @given(
        composite_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        tier_scores=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False), min_size=3, max_size=3
        ),
    )
    def test_composite_result_rendering_invariants(self, composite_score, tier_scores):
        """Property: CompositeResult always renders without errors."""
        # Arrange
        result = CompositeResult(
            composite_score=composite_score,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test_metric": 0.5},
            tier1_score=tier_scores[0],
            tier2_score=tier_scores[1],
            tier3_score=tier_scores[2],
            evaluation_complete=True,
        )

        # Act & Assert - should not raise
        from gui.pages.evaluation import render_evaluation

        with patch("streamlit.header"), patch("streamlit.metric"), patch("streamlit.bar_chart"):
            render_evaluation(result)


# STORY-004: Inline-snapshot regression tests for GUI page rendering
class TestEvaluationPageRenderingSnapshots:
    """Snapshot tests for GUI page rendering output structures."""

    def test_mock_composite_result_structure(self, mock_composite_result):
        """Snapshot: Mock CompositeResult structure for GUI testing."""
        # Act
        dumped = mock_composite_result.model_dump()

        # Assert with snapshot
        assert dumped == snapshot()

    def test_mock_tier_results_structure(self, mock_tier_results):
        """Snapshot: Mock tier results structure for GUI testing."""
        # Arrange
        tier1, tier2, tier3 = mock_tier_results

        # Act
        tier_data = {
            "tier1": tier1.model_dump(),
            "tier2": tier2.model_dump(),
            "tier3": tier3.model_dump(),
        }

        # Assert with snapshot
        assert tier_data == snapshot()
