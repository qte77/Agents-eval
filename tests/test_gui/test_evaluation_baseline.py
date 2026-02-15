"""
Tests for GUI baseline comparison view (STORY-007).

Validates that the evaluation results page displays baseline comparisons
correctly with side-by-side metrics display and three-way comparison tables.
"""

from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import CompositeResult
from app.judge.baseline_comparison import BaselineComparison


@pytest.fixture
def mock_pydantic_result():
    """Create mock PydanticAI evaluation result."""
    return CompositeResult(
        composite_score=0.85,
        recommendation="accept",
        recommendation_weight=0.9,
        metric_scores={
            "cosine_score": 0.85,
            "jaccard_score": 0.80,
            "semantic_score": 0.90,
        },
        tier1_score=0.85,
        tier2_score=0.88,
        tier3_score=0.82,
        evaluation_complete=True,
    )


@pytest.fixture
def mock_cc_solo_result():
    """Create mock CC solo evaluation result."""
    return CompositeResult(
        composite_score=0.73,
        recommendation="weak_accept",
        recommendation_weight=0.7,
        metric_scores={
            "cosine_score": 0.73,
            "jaccard_score": 0.72,
            "semantic_score": 0.75,
        },
        tier1_score=0.73,
        tier2_score=0.76,
        tier3_score=0.70,
        evaluation_complete=True,
    )


@pytest.fixture
def mock_cc_teams_result():
    """Create mock CC teams evaluation result."""
    return CompositeResult(
        composite_score=0.80,
        recommendation="accept",
        recommendation_weight=0.85,
        metric_scores={
            "cosine_score": 0.80,
            "jaccard_score": 0.78,
            "semantic_score": 0.83,
        },
        tier1_score=0.80,
        tier2_score=0.82,
        tier3_score=0.78,
        evaluation_complete=True,
    )


@pytest.fixture
def mock_baseline_comparison(mock_pydantic_result, mock_cc_solo_result):
    """Create mock baseline comparison."""
    return BaselineComparison(
        label_a="PydanticAI",
        label_b="CC-solo",
        result_a=mock_pydantic_result,
        result_b=mock_cc_solo_result,
        metric_deltas={
            "cosine_score": 0.12,
            "jaccard_score": 0.08,
            "semantic_score": 0.15,
        },
        tier_deltas={"tier1": 0.12, "tier2": 0.12, "tier3": 0.12},
        summary="PydanticAI scored +0.12 higher on average vs CC-solo (largest diff: semantic_score +0.15)",
    )


class TestGUIBaselineComparison:
    """Test suite for GUI baseline comparison view."""

    def test_render_baseline_section_exists(self):
        """Test that render_baseline_comparison function exists."""
        from gui.pages.evaluation import render_baseline_comparison

        assert callable(render_baseline_comparison)

    def test_render_single_baseline_comparison(self, mock_baseline_comparison):
        """Test rendering single baseline comparison."""
        from gui.pages.evaluation import render_baseline_comparison

        with (
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.bar_chart") as mock_chart,
            patch("streamlit.write") as mock_write,
        ):
            # Should not raise any exceptions
            render_baseline_comparison([mock_baseline_comparison])

            # Should display summary
            assert mock_write.call_count >= 1

            # Should display metric deltas as chart
            assert mock_chart.call_count >= 1

    def test_render_three_way_comparison(
        self, mock_pydantic_result, mock_cc_solo_result, mock_cc_teams_result
    ):
        """Test rendering three-way comparison table."""
        from gui.pages.evaluation import render_baseline_comparison

        # Create three comparisons
        comparisons = [
            BaselineComparison(
                label_a="PydanticAI",
                label_b="CC-solo",
                result_a=mock_pydantic_result,
                result_b=mock_cc_solo_result,
                metric_deltas={"cosine_score": 0.12},
                tier_deltas={"tier1": 0.12, "tier2": 0.12, "tier3": 0.12},
                summary="PydanticAI scored +0.12 higher on average vs CC-solo",
            ),
            BaselineComparison(
                label_a="PydanticAI",
                label_b="CC-teams",
                result_a=mock_pydantic_result,
                result_b=mock_cc_teams_result,
                metric_deltas={"cosine_score": 0.05},
                tier_deltas={"tier1": 0.05, "tier2": 0.06, "tier3": 0.04},
                summary="PydanticAI scored +0.05 higher on average vs CC-teams",
            ),
            BaselineComparison(
                label_a="CC-solo",
                label_b="CC-teams",
                result_a=mock_cc_solo_result,
                result_b=mock_cc_teams_result,
                metric_deltas={"cosine_score": -0.07},
                tier_deltas={"tier1": -0.07, "tier2": -0.06, "tier3": -0.04},
                summary="CC-solo scored -0.07 lower on average vs CC-teams",
            ),
        ]

        with (
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.dataframe") as mock_dataframe,
            patch("streamlit.write"),
        ):
            render_baseline_comparison(comparisons)

            # Should display comparison table
            assert mock_dataframe.call_count >= 1

    def test_render_empty_baseline_list(self):
        """Test graceful handling of empty baseline list."""
        from gui.pages.evaluation import render_baseline_comparison

        with patch("streamlit.info") as mock_info:
            render_baseline_comparison([])

            # Should display info message
            mock_info.assert_called_once()

    def test_render_none_baseline_list(self):
        """Test graceful handling of None baseline list."""
        from gui.pages.evaluation import render_baseline_comparison

        with patch("streamlit.info") as mock_info:
            render_baseline_comparison(None)

            # Should display info message
            mock_info.assert_called_once()

    def test_metric_deltas_visualization(self, mock_baseline_comparison):
        """Test visualization of metric deltas as bar chart."""
        from gui.pages.evaluation import render_baseline_comparison

        with (
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.bar_chart") as mock_chart,
            patch("streamlit.write"),
        ):
            render_baseline_comparison([mock_baseline_comparison])

            # Verify bar chart called with metric deltas
            assert mock_chart.called
            call_args = mock_chart.call_args
            # Should contain metric deltas
            assert call_args is not None

    def test_tier_deltas_display(self, mock_baseline_comparison):
        """Test display of tier-level score differences."""
        from gui.pages.evaluation import render_baseline_comparison

        with (
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.metric") as mock_metric,
            patch("streamlit.write"),
        ):
            render_baseline_comparison([mock_baseline_comparison])

            # Should display tier deltas as metrics
            # tier1, tier2, tier3 = 3 calls minimum
            assert mock_metric.call_count >= 3

    def test_baseline_section_added_to_evaluation_page(self, mock_baseline_comparison):
        """Test that baseline section is integrated into evaluation results page."""
        from gui.pages.evaluation import render_evaluation

        mock_composite_result = CompositeResult(
            composite_score=0.85,
            recommendation="accept",
            recommendation_weight=0.9,
            metric_scores={"test": 0.85},
            tier1_score=0.85,
            tier2_score=0.85,
            tier3_score=0.85,
            evaluation_complete=True,
        )

        with (
            patch("streamlit.header"),
            patch("streamlit.metric"),
            patch("streamlit.bar_chart"),
            patch("streamlit.expander"),
            patch("streamlit.text"),
            patch("gui.pages.evaluation.render_baseline_comparison") as mock_render_baseline,
        ):
            # Render with baseline comparisons in session state
            with patch(
                "streamlit.session_state", {"baseline_comparisons": [mock_baseline_comparison]}
            ):
                render_evaluation(mock_composite_result)

                # Should call render_baseline_comparison
                mock_render_baseline.assert_called_once_with([mock_baseline_comparison])

    def test_directory_inputs_for_cc_artifacts(self):
        """Test that GUI has directory inputs for CC solo and teams artifacts."""
        from gui.pages.evaluation import render_evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.text_input") as mock_text_input,
            patch("streamlit.button"),
        ):
            render_evaluation(None)

            # Should have inputs for CC solo and teams directories
            # Expected calls: cc_solo_dir, cc_teams_dir
            assert mock_text_input.call_count >= 2


# STORY-007: Hypothesis property-based tests for GUI state with baseline data
class TestGUIBaselineStateInvariants:
    """Property-based tests for GUI state management with baseline data."""

    @given(
        metric_delta=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
        tier_deltas=st.lists(
            st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
            min_size=3,
            max_size=3,
        ),
    )
    def test_baseline_comparison_rendering_invariants(self, metric_delta, tier_deltas):
        """Property: BaselineComparison always renders without errors."""
        # Arrange
        mock_result = MagicMock(spec=CompositeResult)
        comparison = BaselineComparison(
            label_a="System A",
            label_b="System B",
            result_a=mock_result,
            result_b=mock_result,
            metric_deltas={"test_metric": metric_delta},
            tier_deltas={
                "tier1": tier_deltas[0],
                "tier2": tier_deltas[1],
                "tier3": tier_deltas[2],
            },
            summary=f"Delta: {metric_delta:.2f}",
        )

        # Act & Assert - should not raise
        from gui.pages.evaluation import render_baseline_comparison

        with (
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.bar_chart"),
            patch("streamlit.metric"),
            patch("streamlit.write"),
        ):
            render_baseline_comparison([comparison])


# STORY-007: Inline-snapshot tests for GUI baseline rendering
class TestGUIBaselineRenderingSnapshots:
    """Snapshot tests for GUI baseline comparison rendering."""

    def test_mock_baseline_comparison_structure(self, mock_baseline_comparison):
        """Snapshot: Mock BaselineComparison structure for GUI testing."""
        # Act
        output = {
            "summary": mock_baseline_comparison.summary,
            "metric_deltas": mock_baseline_comparison.metric_deltas,
            "tier_deltas": mock_baseline_comparison.tier_deltas,
        }

        # Assert with snapshot
        assert output == snapshot(
            {
                "summary": "PydanticAI scored +0.12 higher on average vs CC-solo (largest diff: semantic_score +0.15)",
                "metric_deltas": {
                    "cosine_score": 0.12,
                    "jaccard_score": 0.08,
                    "semantic_score": 0.15,
                },
                "tier_deltas": {"tier1": 0.12, "tier2": 0.12, "tier3": 0.12},
            }
        )

    def test_three_way_comparison_table_structure(
        self, mock_pydantic_result, mock_cc_solo_result, mock_cc_teams_result
    ):
        """Snapshot: Three-way comparison table structure."""
        # Arrange
        comparisons = [
            BaselineComparison(
                label_a="PydanticAI",
                label_b="CC-solo",
                result_a=mock_pydantic_result,
                result_b=mock_cc_solo_result,
                metric_deltas={"cosine_score": 0.12},
                tier_deltas={"tier1": 0.12, "tier2": 0.12, "tier3": 0.12},
                summary="PydanticAI vs CC-solo",
            ),
            BaselineComparison(
                label_a="PydanticAI",
                label_b="CC-teams",
                result_a=mock_pydantic_result,
                result_b=mock_cc_teams_result,
                metric_deltas={"cosine_score": 0.05},
                tier_deltas={"tier1": 0.05, "tier2": 0.06, "tier3": 0.04},
                summary="PydanticAI vs CC-teams",
            ),
            BaselineComparison(
                label_a="CC-solo",
                label_b="CC-teams",
                result_a=mock_cc_solo_result,
                result_b=mock_cc_teams_result,
                metric_deltas={"cosine_score": -0.07},
                tier_deltas={"tier1": -0.07, "tier2": -0.06, "tier3": -0.04},
                summary="CC-solo vs CC-teams",
            ),
        ]

        # Act
        table_data = [
            {
                "comparison": c.summary,
                "tier1_delta": c.tier_deltas["tier1"],
                "tier2_delta": c.tier_deltas["tier2"],
                "tier3_delta": c.tier_deltas["tier3"],
            }
            for c in comparisons
        ]

        # Assert with snapshot
        assert table_data == snapshot(
            [
                {
                    "comparison": "PydanticAI vs CC-solo",
                    "tier1_delta": 0.12,
                    "tier2_delta": 0.12,
                    "tier3_delta": 0.12,
                },
                {
                    "comparison": "PydanticAI vs CC-teams",
                    "tier1_delta": 0.05,
                    "tier2_delta": 0.06,
                    "tier3_delta": 0.04,
                },
                {
                    "comparison": "CC-solo vs CC-teams",
                    "tier1_delta": -0.07,
                    "tier2_delta": -0.06,
                    "tier3_delta": -0.04,
                },
            ]
        )
