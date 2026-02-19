"""Tests for graph node attribute alignment between graph_analysis.py and agent_graph.py.

This module tests the attribute name consistency requirement from STORY-003:
- `graph_analysis.py:export_trace_to_networkx()` uses `type` as node attribute (canonical)
- `agent_graph.py:render_agent_graph()` must read `type` (not `node_type`)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import networkx as nx

from app.data_models.evaluation_models import GraphTraceData
from app.judge.graph_analysis import GraphAnalysisEngine
from app.judge.settings import JudgeSettings


def _make_trace_data(
    agent_interactions: list[dict[str, Any]] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> GraphTraceData:
    """Build a minimal GraphTraceData for testing."""
    return GraphTraceData(
        execution_id="test_exec",
        agent_interactions=agent_interactions or [],
        tool_calls=tool_calls or [],
        coordination_events=[],
        timing_data={},
    )


class TestExportTraceNodeAttributeNames:
    """Verify export_trace_to_networkx() uses `type` as the canonical node attribute."""

    def setup_method(self) -> None:
        self.engine = GraphAnalysisEngine(JudgeSettings())

    def test_agent_nodes_use_type_attribute(self) -> None:
        """Agent nodes exported by export_trace_to_networkx() have `type` key, not `node_type`."""
        # Arrange
        trace_data = _make_trace_data(agent_interactions=[{"from": "manager", "to": "researcher"}])

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        assert graph.number_of_nodes() > 0
        for node in graph.nodes():
            node_data = graph.nodes[node]
            assert "type" in node_data, (
                f"Node '{node}' missing 'type' attribute — found keys: {list(node_data.keys())}"
            )
            assert "node_type" not in node_data, (
                f"Node '{node}' has unexpected 'node_type' attribute"
            )

    def test_tool_nodes_use_type_attribute(self) -> None:
        """Tool nodes exported by export_trace_to_networkx() have `type` key, not `node_type`."""
        # Arrange
        trace_data = _make_trace_data(
            tool_calls=[{"agent_id": "researcher", "tool_name": "search_tool", "success": True}]
        )

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        tool_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "tool"]
        assert len(tool_nodes) > 0, "No tool nodes found with type='tool'"

    def test_agent_node_type_value_is_agent(self) -> None:
        """Agent nodes have type='agent'."""
        # Arrange
        trace_data = _make_trace_data(agent_interactions=[{"from": "manager", "to": "researcher"}])

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        agent_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "agent"]
        assert len(agent_nodes) == 2
        assert "manager" in agent_nodes
        assert "researcher" in agent_nodes

    def test_tool_node_type_value_is_tool(self) -> None:
        """Tool nodes have type='tool'."""
        # Arrange
        trace_data = _make_trace_data(
            tool_calls=[{"agent_id": "researcher", "tool_name": "search_tool", "success": True}]
        )

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        tool_node = graph.nodes.get("search_tool")
        assert tool_node is not None
        assert tool_node.get("type") == "tool"


class TestAgentGraphAttributeConsistency:
    """Verify render_agent_graph() reads `type` attribute (matching export_trace_to_networkx).

    These tests expose the bug at agent_graph.py:101,150 where `node_type` is read
    instead of `type`. They should FAIL until the fix is applied.
    """

    def _build_graph_with_type_attribute(self) -> nx.DiGraph[str]:
        """Build a graph using the canonical `type` attribute (as export_trace_to_networkx does)."""
        graph: nx.DiGraph[str] = nx.DiGraph()
        graph.add_node("manager", type="agent", label="Manager", interaction_count=2)
        graph.add_node("researcher", type="agent", label="Researcher", interaction_count=1)
        graph.add_node("search_tool", type="tool", label="search_tool", usage_count=3)
        graph.add_edge("manager", "researcher", interaction="delegation")
        graph.add_edge("researcher", "search_tool", interaction="tool_call")
        return graph

    @patch("streamlit.components.v1.html")
    @patch("streamlit.expander")
    @patch("streamlit.text")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("gui.pages.agent_graph.Network")
    def test_render_reads_type_not_node_type_for_node_styling(
        self,
        mock_network_cls: MagicMock,
        mock_header: MagicMock,
        mock_subheader: MagicMock,
        mock_text: MagicMock,
        mock_expander: MagicMock,
        mock_html: MagicMock,
        tmp_path,
    ) -> None:
        """render_agent_graph() should add agent nodes with blue color when type='agent'.

        This test FAILS with the bug because node_data.get("node_type", "agent") always
        returns the default "agent" for ALL nodes (including tool nodes that only have `type`).
        After the fix, node_data.get("type", "agent") will correctly distinguish agent/tool.
        """
        from gui.pages.agent_graph import render_agent_graph

        graph = self._build_graph_with_type_attribute()

        # Track add_node calls to verify color assignments
        mock_net = MagicMock()
        mock_net.save_graph = MagicMock()
        mock_network_cls.return_value = mock_net

        # Make save_graph write something readable
        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.name = str(tmp_path / "test_graph.html")
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value = mock_file

            with patch("pathlib.Path.read_text", return_value="<html></html>"):
                with patch("pathlib.Path.unlink"):
                    render_agent_graph(graph)

        # Verify add_node was called for all 3 nodes
        assert mock_net.add_node.call_count == 3

        # Collect calls by node id
        calls_by_node: dict[str, dict[str, Any]] = {}
        for call in mock_net.add_node.call_args_list:
            node_id = call.args[0]
            calls_by_node[node_id] = call.kwargs

        # manager and researcher should be agent nodes (blue #4A90E2)
        assert calls_by_node["manager"]["color"] == "#4A90E2", (
            f"manager should be blue agent node, got: {calls_by_node['manager']['color']}"
        )
        assert calls_by_node["researcher"]["color"] == "#4A90E2", (
            f"researcher should be blue agent node, got: {calls_by_node['researcher']['color']}"
        )
        # search_tool should be a tool node (green #50C878)
        assert calls_by_node["search_tool"]["color"] == "#50C878", (
            f"search_tool should be green tool node, got: {calls_by_node['search_tool']['color']}"
        )

    @patch("streamlit.components.v1.html")
    @patch("streamlit.expander")
    @patch("streamlit.text")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("gui.pages.agent_graph.Network")
    def test_graph_statistics_counts_agent_nodes_using_type_attribute(
        self,
        mock_network_cls: MagicMock,
        mock_header: MagicMock,
        mock_subheader: MagicMock,
        mock_text: MagicMock,
        mock_expander: MagicMock,
        mock_html: MagicMock,
        tmp_path,
    ) -> None:
        """Graph statistics section must count agent nodes using `type` attribute.

        agent_graph.py:150 reads graph.nodes[n].get("node_type") — this returns None
        for nodes that only have `type` set. After fix, it reads `type` and counts correctly:
        2 agent nodes out of 3 total.
        """
        from gui.pages.agent_graph import render_agent_graph

        graph = self._build_graph_with_type_attribute()

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net

        # Capture st.text() calls — statistics are rendered via st.text()
        text_calls: list[str] = []
        mock_text.side_effect = lambda s: text_calls.append(str(s))

        # expander returns a context manager
        mock_expander.return_value.__enter__ = MagicMock(return_value=None)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.name = str(tmp_path / "test_graph.html")
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value = mock_file

            with patch("pathlib.Path.read_text", return_value="<html></html>"):
                with patch("pathlib.Path.unlink"):
                    render_agent_graph(graph)

        # Statistics should show 2 agent nodes (manager + researcher)
        agent_stat = next((c for c in text_calls if "Agent Nodes:" in c), None)
        assert agent_stat is not None, f"Agent Nodes stat not found in: {text_calls}"
        assert "2" in agent_stat, (
            f"Expected 2 agent nodes but got: '{agent_stat}'. "
            "Bug: agent_graph.py reads 'node_type' instead of 'type', so count is 0."
        )

        # Statistics should show 1 tool node
        tool_stat = next((c for c in text_calls if "Tool Nodes:" in c), None)
        assert tool_stat is not None, f"Tool Nodes stat not found in: {text_calls}"
        assert "1" in tool_stat, (
            f"Expected 1 tool node but got: '{tool_stat}'. "
            "Bug: agent_graph.py reads 'node_type' instead of 'type', so count is 3."
        )


class TestAttributeNameRoundTrip:
    """End-to-end: export_trace_to_networkx() output is compatible with render_agent_graph()."""

    def test_exported_graph_has_attributes_readable_by_renderer(self) -> None:
        """Nodes from export_trace_to_networkx() have `type` that render_agent_graph() can read."""
        # Arrange
        engine = GraphAnalysisEngine(JudgeSettings())
        trace_data = _make_trace_data(
            agent_interactions=[{"from": "manager", "to": "researcher"}],
            tool_calls=[{"agent_id": "researcher", "tool_name": "search", "success": True}],
        )

        # Act
        graph = engine.export_trace_to_networkx(trace_data)
        assert graph is not None

        # Simulate what render_agent_graph() does at line 101 — AFTER the fix
        # (reading `type`, not `node_type`)
        agent_count_correct = sum(1 for n in graph.nodes() if graph.nodes[n].get("type") == "agent")
        agent_count_buggy = sum(
            1 for n in graph.nodes() if graph.nodes[n].get("node_type") == "agent"
        )

        # With fix: `type` attribute is present, correctly counts agents
        assert agent_count_correct == 2, (
            f"Expected 2 agent nodes via 'type' attribute, got {agent_count_correct}"
        )
        # Without fix: `node_type` attribute is absent, counts 0
        assert agent_count_buggy == 0, (
            "Sanity check: 'node_type' attribute should not be present (it's a bug)"
        )
