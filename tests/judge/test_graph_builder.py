"""
Behavioral tests for graph_builder module (STORY-008).

Tests verify that build_interaction_graph correctly converts GraphTraceData
into NetworkX DiGraphs with proper node types, edge attributes, and structure.
"""

import networkx as nx
import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import GraphTraceData
from app.judge.graph_builder import build_interaction_graph

# MARK: --- Fixtures ---


@pytest.fixture
def multi_agent_trace():
    """Trace data from a multi-agent delegation run."""
    return GraphTraceData(
        execution_id="exec-multi",
        agent_interactions=[
            {
                "source_agent": "manager",
                "target_agent": "researcher",
                "interaction_type": "delegation",
            },
            {
                "source_agent": "manager",
                "target_agent": "analyst",
                "interaction_type": "delegation",
            },
            {
                "source_agent": "researcher",
                "target_agent": "manager",
                "interaction_type": "response",
            },
        ],
        tool_calls=[
            {"agent_id": "researcher", "tool_name": "search_tool", "success": True},
            {"agent_id": "researcher", "tool_name": "search_tool", "success": False},
            {"agent_id": "analyst", "tool_name": "analysis_tool", "success": True},
        ],
        timing_data={},
        coordination_events=[],
    )


@pytest.fixture
def empty_trace():
    """Trace data with no interactions or tool calls."""
    return GraphTraceData(
        execution_id="exec-empty",
        agent_interactions=[],
        tool_calls=[],
        timing_data={},
        coordination_events=[],
    )


# MARK: --- Behavioral Tests ---


class TestBuildInteractionGraph:
    """Behavioral tests for graph construction from trace data."""

    def test_agent_interactions_create_agent_nodes(self, multi_agent_trace):
        """Agents involved in interactions appear as agent-typed nodes."""
        graph = build_interaction_graph(multi_agent_trace)

        assert graph.nodes["manager"]["node_type"] == "agent"
        assert graph.nodes["researcher"]["node_type"] == "agent"
        assert graph.nodes["analyst"]["node_type"] == "agent"

    def test_agent_interactions_create_edges(self, multi_agent_trace):
        """Each interaction creates a directed edge between agents."""
        graph = build_interaction_graph(multi_agent_trace)

        assert graph.has_edge("manager", "researcher")
        assert graph.has_edge("manager", "analyst")
        assert graph.has_edge("researcher", "manager")
        assert graph["manager"]["researcher"]["interaction"] == "delegation"

    def test_tool_calls_create_tool_nodes(self, multi_agent_trace):
        """Tools used in calls appear as tool-typed nodes."""
        graph = build_interaction_graph(multi_agent_trace)

        assert graph.nodes["search_tool"]["node_type"] == "tool"
        assert graph.nodes["analysis_tool"]["node_type"] == "tool"

    def test_tool_calls_create_agent_to_tool_edges(self, multi_agent_trace):
        """Each tool call creates an edge from agent to tool."""
        graph = build_interaction_graph(multi_agent_trace)

        assert graph.has_edge("researcher", "search_tool")
        assert graph.has_edge("analyst", "analysis_tool")
        assert graph["researcher"]["search_tool"]["interaction"] == "tool_call"

    def test_tool_edge_carries_success_attribute(self, multi_agent_trace):
        """Tool call edges carry the success status of the call."""
        graph = build_interaction_graph(multi_agent_trace)

        # Last call to search_tool was success=False (overwrites — known STORY-013 issue)
        edge_data = graph["researcher"]["search_tool"]
        assert "success" in edge_data

    def test_empty_trace_produces_empty_graph(self, empty_trace):
        """Empty trace data yields a graph with zero nodes and edges."""
        graph = build_interaction_graph(empty_trace)

        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_agent_appearing_in_both_interactions_and_tools_has_one_node(self, multi_agent_trace):
        """An agent referenced in both interactions and tool calls is a single node."""
        graph = build_interaction_graph(multi_agent_trace)

        # "researcher" appears in interactions AND tool_calls
        researcher_count = sum(1 for n in graph.nodes if n == "researcher")
        assert researcher_count == 1
        assert graph.nodes["researcher"]["node_type"] == "agent"

    def test_tool_only_trace(self):
        """Trace with only tool calls (no agent interactions) builds correctly."""
        trace = GraphTraceData(
            execution_id="exec-tools-only",
            agent_interactions=[],
            tool_calls=[
                {"agent_id": "solo_agent", "tool_name": "web_search", "success": True},
            ],
            timing_data={},
            coordination_events=[],
        )
        graph = build_interaction_graph(trace)

        assert graph.number_of_nodes() == 2
        assert graph.nodes["solo_agent"]["node_type"] == "agent"
        assert graph.nodes["web_search"]["node_type"] == "tool"
        assert graph.has_edge("solo_agent", "web_search")

    def test_alternative_key_names_for_interactions(self):
        """Interactions using 'from'/'to' keys instead of 'source_agent'/'target_agent'."""
        trace = GraphTraceData(
            execution_id="exec-alt-keys",
            agent_interactions=[
                {"from": "agent_a", "to": "agent_b", "type": "handoff"},
            ],
            tool_calls=[],
            timing_data={},
            coordination_events=[],
        )
        graph = build_interaction_graph(trace)

        assert graph.has_edge("agent_a", "agent_b")
        assert graph["agent_a"]["agent_b"]["interaction"] == "handoff"

    def test_missing_keys_default_to_unknown(self):
        """Interactions with missing keys default to 'unknown'."""
        trace = GraphTraceData(
            execution_id="exec-missing",
            agent_interactions=[{}],
            tool_calls=[{}],
            timing_data={},
            coordination_events=[],
        )
        graph = build_interaction_graph(trace)

        assert "unknown" in graph.nodes
        assert "unknown_tool" in graph.nodes


# MARK: --- Inline-Snapshot Tests ---


class TestGraphBuilderSnapshots:
    """Snapshot tests for graph structure verification."""

    def test_multi_agent_graph_structure(self, multi_agent_trace):
        """Snapshot: complete graph structure from multi-agent trace."""
        graph = build_interaction_graph(multi_agent_trace)

        structure = {
            "nodes": sorted(
                [{"id": n, "type": graph.nodes[n]["node_type"]} for n in graph.nodes],
                key=lambda x: x["id"],
            ),
            "edge_count": graph.number_of_edges(),
            "node_count": graph.number_of_nodes(),
        }

        assert structure == snapshot(
            {
                "nodes": [
                    {"id": "analysis_tool", "type": "tool"},
                    {"id": "analyst", "type": "agent"},
                    {"id": "manager", "type": "agent"},
                    {"id": "researcher", "type": "agent"},
                    {"id": "search_tool", "type": "tool"},
                ],
                "edge_count": 5,
                "node_count": 5,
            }
        )

    def test_empty_trace_graph_structure(self, empty_trace):
        """Snapshot: empty graph from empty trace."""
        graph = build_interaction_graph(empty_trace)

        assert {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges()} == snapshot(
            {"nodes": 0, "edges": 0}
        )


# MARK: --- Hypothesis Property Tests ---


class TestGraphBuilderProperties:
    """Property-based tests for graph construction invariants."""

    @given(
        num_interactions=st.integers(min_value=0, max_value=10),
        num_tool_calls=st.integers(min_value=0, max_value=10),
    )
    def test_node_count_bounded_by_inputs(self, num_interactions, num_tool_calls):
        """Property: node count <= 2*interactions + 2*tool_calls (upper bound)."""
        interactions = [
            {
                "source_agent": f"agent_{i}",
                "target_agent": f"agent_{i + 1}",
                "interaction_type": "delegation",
            }
            for i in range(num_interactions)
        ]
        tool_calls = [
            {"agent_id": f"tool_agent_{i}", "tool_name": f"tool_{i}", "success": True}
            for i in range(num_tool_calls)
        ]
        trace = GraphTraceData(
            execution_id="prop-test",
            agent_interactions=interactions,
            tool_calls=tool_calls,
            timing_data={},
            coordination_events=[],
        )

        graph = build_interaction_graph(trace)

        # Each interaction introduces at most 2 new nodes, each tool call at most 2
        max_nodes = 2 * num_interactions + 2 * num_tool_calls
        assert graph.number_of_nodes() <= max_nodes

    @given(
        num_interactions=st.integers(min_value=0, max_value=10),
        num_tool_calls=st.integers(min_value=0, max_value=10),
    )
    def test_edge_count_bounded_by_inputs(self, num_interactions, num_tool_calls):
        """Property: edge count <= interactions + tool_calls."""
        interactions = [
            {
                "source_agent": f"agent_{i}",
                "target_agent": f"agent_{i + 1}",
                "interaction_type": "delegation",
            }
            for i in range(num_interactions)
        ]
        tool_calls = [
            {"agent_id": f"tool_agent_{i}", "tool_name": f"tool_{i}", "success": True}
            for i in range(num_tool_calls)
        ]
        trace = GraphTraceData(
            execution_id="prop-test",
            agent_interactions=interactions,
            tool_calls=tool_calls,
            timing_data={},
            coordination_events=[],
        )

        graph = build_interaction_graph(trace)

        assert graph.number_of_edges() <= num_interactions + num_tool_calls

    @given(num_tool_calls=st.integers(min_value=1, max_value=15))
    def test_all_tool_nodes_typed_as_tool(self, num_tool_calls):
        """Property: every tool node has node_type='tool'."""
        tool_calls = [
            {"agent_id": "agent_0", "tool_name": f"tool_{i}", "success": True}
            for i in range(num_tool_calls)
        ]
        trace = GraphTraceData(
            execution_id="prop-test",
            agent_interactions=[],
            tool_calls=tool_calls,
            timing_data={},
            coordination_events=[],
        )

        graph = build_interaction_graph(trace)

        tool_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "tool"]
        assert len(tool_nodes) == num_tool_calls

    @given(num_interactions=st.integers(min_value=0, max_value=10))
    def test_graph_is_always_directed(self, num_interactions):
        """Property: result is always a directed graph."""
        interactions = [
            {"source_agent": f"a_{i}", "target_agent": f"a_{i + 1}", "interaction_type": "x"}
            for i in range(num_interactions)
        ]
        trace = GraphTraceData(
            execution_id="prop-test",
            agent_interactions=interactions,
            tool_calls=[],
            timing_data={},
            coordination_events=[],
        )

        graph = build_interaction_graph(trace)

        assert isinstance(graph, nx.DiGraph)
