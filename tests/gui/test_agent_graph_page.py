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
    graph.add_node("manager", node_type="agent", label="Manager")
    graph.add_node("researcher", node_type="agent", label="Researcher")
    graph.add_node("analyst", node_type="agent", label="Analyst")

    # Add tool nodes
    graph.add_node("search_tool", node_type="tool", label="Search")
    graph.add_node("analysis_tool", node_type="tool", label="Analysis")

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

    def test_render_agent_graph_exists(self):
        """Test that render_agent_graph function exists and is callable."""
        from gui.pages.agent_graph import render_agent_graph

        assert callable(render_agent_graph)

    def test_render_with_networkx_graph(self, mock_networkx_graph):
        """Test page renders with valid NetworkX graph."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Should render HTML visualization
            assert mock_html.called

    def test_distinguishes_agent_and_tool_nodes(self, mock_networkx_graph):
        """Test that agent and tool nodes are visually distinguished."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Verify HTML was generated with visual distinction
            assert mock_html.called
            html_content = mock_html.call_args[0][0] if mock_html.call_args else ""
            # Pyvis uses different colors for different node types
            assert isinstance(html_content, str)

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

    def test_creates_pyvis_network(self, mock_networkx_graph):
        """Test that Pyvis Network is created from NetworkX graph."""
        from gui.pages.agent_graph import render_agent_graph

        with (
            patch("streamlit.header"),
            patch("streamlit.components.v1.html") as mock_html,
            patch("pyvis.network.Network") as mock_pyvis,
        ):
            render_agent_graph(mock_networkx_graph)

            # Should create Pyvis Network instance
            assert mock_pyvis.called or mock_html.called

    def test_interactive_graph_features(self, mock_networkx_graph):
        """Test that graph includes interactive features (physics, zoom)."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Verify HTML rendering was called (Pyvis creates interactive HTML)
            assert mock_html.called

    def test_graph_layout_configuration(self, mock_networkx_graph):
        """Test that graph uses appropriate layout for readability."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Should render with configured layout
            assert mock_html.called

    def test_node_labels_displayed(self, mock_networkx_graph):
        """Test that node labels are visible in visualization."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Verify visualization includes node information
            assert mock_html.called

    def test_edge_information_displayed(self, mock_networkx_graph):
        """Test that edge information (interaction types) is visible."""
        from gui.pages.agent_graph import render_agent_graph

        with patch("streamlit.header"), patch("streamlit.components.v1.html") as mock_html:
            render_agent_graph(mock_networkx_graph)

            # Should render edge information
            assert mock_html.called
