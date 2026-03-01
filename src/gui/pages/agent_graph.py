"""
Streamlit page for Agent Graph visualization.

Renders NetworkX agent interaction graphs as interactive Pyvis visualizations.
Displays agent-to-agent delegations and tool usage patterns with visual distinction
between agent nodes and tool nodes.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components

from gui.config.styling import get_theme_bgcolor, get_theme_node_colors
from gui.config.text import AGENT_GRAPH_HEADER, AGENT_GRAPH_NETWORK_SUBHEADER

try:
    from pyvis.network import Network  # type: ignore[import-untyped]
except ImportError:
    Network = None  # type: ignore[assignment,misc]


_EMPTY_GRAPH_MESSAGES: dict[str, str] = {
    "cc_solo": (
        "CC solo mode produces no agent interaction graph. "
        "Evaluation scores are available on the Evaluation Results page."
    ),
    "cc_teams": (
        "CC teams mode produced an empty interaction graph. "
        "Check the Evaluation Results page for coordination metrics."
    ),
}

_EMPTY_GRAPH_DEFAULT = (
    "No agent interaction data available. Run a multi-agent task to see the graph here."
)


def render_agent_graph(
    graph: nx.DiGraph[str] | None = None,
    composite_result: Any | None = None,
) -> None:
    """Render agent interaction graph as interactive Pyvis visualization.

    Displays:
    - Agent nodes (distinguished visually from tool nodes)
    - Tool nodes
    - Interaction edges (delegations, tool calls)
    - Interactive pan/zoom/hover features

    Args:
        graph: NetworkX DiGraph with agent and tool nodes, or None for empty state.
        composite_result: Optional CompositeResult for mode-specific empty messages.
    """
    st.header(AGENT_GRAPH_HEADER)

    if graph is None:
        st.info("No agent interaction data available. Run a query to see the graph here.")
        return

    if graph.number_of_nodes() == 0:
        engine_type = getattr(composite_result, "engine_type", "mas") if composite_result else "mas"
        st.info(_EMPTY_GRAPH_MESSAGES.get(engine_type, _EMPTY_GRAPH_DEFAULT))
        return

    st.subheader(AGENT_GRAPH_NETWORK_SUBHEADER)

    if Network is None:
        st.error("Pyvis library not installed. Install with: uv pip install pyvis")
        return

    # Create Pyvis network
    net = Network(
        height="600px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor=get_theme_bgcolor(),
        font_color=False,  # type: ignore[arg-type]
    )

    # Configure physics for better layout
    net.set_options(
        """
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "centralGravity": 0.3,
                    "springLength": 95,
                    "springConstant": 0.04
                },
                "stabilization": {
                    "enabled": true,
                    "iterations": 200
                }
            },
            "nodes": {
                "font": {
                    "size": 14
                }
            },
            "edges": {
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 0.5
                    }
                },
                "smooth": {
                    "type": "continuous"
                }
            }
        }
        """
    )

    # Add nodes with visual distinction — colors from active theme
    agent_color, tool_color = get_theme_node_colors()
    for node in graph.nodes():
        node_data: dict[str, Any] = graph.nodes[node]  # type: ignore[assignment]
        node_type = node_data.get("type", "agent")
        label = node_data.get("label", str(node))

        if node_type == "agent":
            # Agent nodes: themed circles
            net.add_node(
                str(node),
                label=label,
                color=agent_color,
                shape="dot",
                size=25,
                title=f"Agent: {label}",
            )
        else:
            # Tool nodes: themed squares
            net.add_node(
                str(node),
                label=label,
                color=tool_color,
                shape="box",
                size=20,
                title=f"Tool: {label}",
            )

    # Add edges
    for source, target in graph.edges():
        edge_data: dict[str, Any] = graph.edges[source, target]  # type: ignore[assignment]
        interaction = edge_data.get("interaction", "interaction")
        net.add_edge(str(source), str(target), title=interaction)

    # Generate HTML
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".html", encoding="utf-8"
    ) as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_path = Path(tmp_file.name)

    # Read and render HTML with accessibility enhancements
    html_content = tmp_path.read_text(encoding="utf-8")

    # AC-6: Insert <title> element into Pyvis HTML for screen readers
    html_content = html_content.replace("<head>", "<head><title>Agent Interaction Graph</title>", 1)

    # AC-7: Descriptive caption before the graph component
    st.caption(
        "Agent interaction graph showing agent and tool relationships. "
        "See statistics below for details."
    )
    # AC-8: scrolling=True to prevent keyboard trap
    components.html(html_content, height=620, scrolling=True)

    # Cleanup temporary file
    tmp_path.unlink()

    # Display graph statistics
    agent_nodes = sum(1 for n in graph.nodes() if graph.nodes[n].get("type") == "agent")
    tool_nodes = graph.number_of_nodes() - agent_nodes
    agent_names = [
        str(graph.nodes[n].get("label", n))
        for n in graph.nodes()
        if graph.nodes[n].get("type") == "agent"
    ]

    with st.expander("Graph Statistics"):
        st.text(f"Total Nodes: {graph.number_of_nodes()}")
        st.text(f"Total Edges: {graph.number_of_edges()}")
        st.text(f"Agent Nodes: {agent_nodes}")
        st.text(f"Tool Nodes: {tool_nodes}")

    # AC-1: Accessible text summary with node/edge counts and agent names
    st.markdown(
        f"**Graph summary:** {graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} edges. "
        f"Agents: {', '.join(agent_names)}."
    )
