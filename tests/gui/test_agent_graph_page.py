"""
Tests for Streamlit Agent Graph visualization page.

Following TDD approach for STORY-006 agent graph visualization implementation.
Tests verify that the page renders NetworkX graph as interactive Pyvis visualization.
"""

from unittest.mock import patch

import networkx as nx
import pytest

from app.data_models.evaluation_models import GraphTraceData


@pytest.fixture
def mock_networkx_graph():
    """Create mock NetworkX graph for testing."""
    graph = nx.DiGraph()
    # Add agent nodes
    graph.add_node("manager", type="agent", label="Manager")
    graph.add_node("researcher", type="agent", label="Researcher")
    graph.add_node("analyst", type="agent", label="Analyst")

    # Add tool nodes
    graph.add_node("search_tool", type="tool", label="Search")
    graph.add_node("analysis_tool", type="tool", label="Analysis")

    # Add edges (interactions)
    graph.add_edge("manager", "researcher", interaction="delegation")
    graph.add_edge("manager", "analyst", interaction="delegation")
    graph.add_edge("researcher", "search_tool", interaction="tool_call")
    graph.add_edge("analyst", "analysis_tool", interaction="tool_call")

    return graph


@pytest.fixture
def mock_trace_data():
    """Create mock GraphTraceData for testing."""
    return GraphTraceData(
        agent_interactions=[
            {
                "source_agent": "manager",
                "target_agent": "researcher",
                "interaction_type": "delegation",
                "timestamp": "2026-02-15T10:00:00Z",
            },
            {
                "source_agent": "manager",
                "target_agent": "analyst",
                "interaction_type": "delegation",
                "timestamp": "2026-02-15T10:00:05Z",
            },
        ],
        tool_calls=[
            {
                "agent_id": "researcher",
                "tool_name": "search_tool",
                "timestamp": "2026-02-15T10:00:10Z",
                "duration": 1.2,
                "success": True,
            },
            {
                "agent_id": "analyst",
                "tool_name": "analysis_tool",
                "timestamp": "2026-02-15T10:00:15Z",
                "duration": 0.8,
                "success": True,
            },
        ],
        total_agents=3,
        total_tool_calls=2,
        execution_start="2026-02-15T10:00:00Z",
        execution_end="2026-02-15T10:01:00Z",
    )


class TestAgentGraphPage:
    """Test suite for Agent Graph visualization page."""

    def test_render_with_networkx_graph(self, mock_networkx_graph):
        """Test page renders with valid NetworkX graph."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Should render HTML visualization
            assert mock_html.called

    def test_render_with_empty_graph(self):
        """Test page renders gracefully with empty graph."""
        from gui.pages.agent_graph import render_agent_graph

        empty_graph = nx.DiGraph()

        with patch("streamlit.info") as mock_info:
            render_agent_graph(empty_graph)

            # Should display informative message
            mock_info.assert_called_once()

    def test_render_with_none_graph(self):
        """Test page renders gracefully with None graph."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.info") as mock_info:
            render_agent_graph(None)

            # Should display informative message
            mock_info.assert_called_once()


# MARK: --- mode-specific empty-state messages (STORY-011) ---


class TestAgentGraphEmptyStateMessages:
    """Tests for mode-specific empty state messages in Agent Graph page."""

    def test_none_graph_shows_no_execution_message(self):
        """None graph shows generic 'no execution' message."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.info") as mock_info, patch("streamlit.header"):
            render_agent_graph(None)
            call_text = mock_info.call_args[0][0]
            assert "no" in call_text.lower() or "run" in call_text.lower()

    def test_empty_graph_cc_solo_shows_solo_message(self):
        """Empty graph with cc_solo engine shows CC solo message."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.agent_graph import render_agent_graph

        empty_graph = nx.DiGraph()
        composite = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.0,
            evaluation_complete=True,
            engine_type="cc_solo",
        )

        with patch("streamlit.info") as mock_info, patch("streamlit.header"):
            render_agent_graph(empty_graph, composite_result=composite)
            call_text = mock_info.call_args[0][0]
            assert "solo" in call_text.lower()

    def test_empty_graph_cc_teams_shows_teams_message(self):
        """Empty graph with cc_teams engine shows CC teams message."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.agent_graph import render_agent_graph

        empty_graph = nx.DiGraph()
        composite = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.0,
            evaluation_complete=True,
            engine_type="cc_teams",
        )

        with patch("streamlit.info") as mock_info, patch("streamlit.header"):
            render_agent_graph(empty_graph, composite_result=composite)
            call_text = mock_info.call_args[0][0]
            assert "teams" in call_text.lower()

    def test_empty_graph_mas_shows_generic_message(self):
        """Empty graph with MAS engine shows generic multi-agent message."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.agent_graph import render_agent_graph

        empty_graph = nx.DiGraph()
        composite = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.0,
            evaluation_complete=True,
            engine_type="mas",
        )

        with patch("streamlit.info") as mock_info, patch("streamlit.header"):
            render_agent_graph(empty_graph, composite_result=composite)
            call_text = mock_info.call_args[0][0]
            # MAS message should not mention "solo" or "teams"
            assert "solo" not in call_text.lower()
            assert "teams" not in call_text.lower()


# MARK: --- Tier 3 informational label (STORY-011) ---


class TestTier3InformationalLabel:
    """Tests for Tier 3 informational label when engine is CC."""

    def test_cc_tier3_shows_informational_note(self):
        """CC engine shows 'informational' caption on Tier 3 scores."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.evaluation import _render_tier_scores

        result = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.3,
            evaluation_complete=True,
            engine_type="cc_solo",
        )

        with (
            patch("streamlit.subheader"),
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.caption") as mock_caption,
        ):
            # Mock columns to return context managers
            patch("streamlit.metric").__enter__()
            mock_cols.return_value = [
                type("CM", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})(),
                type("CM", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})(),
                type("CM", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})(),
            ]

            _render_tier_scores(result)

            mock_caption.assert_called_once()
            caption_text = mock_caption.call_args[0][0]
            assert "informational" in caption_text.lower()

    def test_mas_tier3_no_informational_note(self):
        """MAS engine does NOT show informational caption on Tier 3 scores."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.evaluation import _render_tier_scores

        result = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.3,
            evaluation_complete=True,
            engine_type="mas",
        )

        with (
            patch("streamlit.subheader"),
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.caption") as mock_caption,
        ):
            mock_cols.return_value = [
                type("CM", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})(),
                type("CM", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})(),
                type("CM", (), {"__enter__": lambda s: s, "__exit__": lambda *a: None})(),
            ]

            _render_tier_scores(result)

            mock_caption.assert_not_called()
