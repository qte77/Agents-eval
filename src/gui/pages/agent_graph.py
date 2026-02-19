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

try:
    from pyvis.network import Network  # type: ignore[import-untyped]
except ImportError:
    Network = None  # type: ignore[assignment,misc]


def render_agent_graph(graph: nx.DiGraph[str] | None = None) -> None:
    """Render agent interaction graph as interactive Pyvis visualization.

    Displays:
    - Agent nodes (distinguished visually from tool nodes)
    - Tool nodes
    - Interaction edges (delegations, tool calls)
    - Interactive pan/zoom/hover features

    Args:
        graph: NetworkX DiGraph with agent and tool nodes, or None for empty state.
    """
    st.header("🕸️ Agent Interaction Graph")

    if graph is None or graph.number_of_nodes() == 0:
        st.info(
            "No agent interaction data available. Run a multi-agent task to see the graph here."
        )
        return

    st.subheader("Interactive Agent Network Visualization")

    if Network is None:
        st.error("Pyvis library not installed. Install with: uv pip install pyvis")
        return

    # Create Pyvis network
    net = Network(
        height="600px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#ffffff",
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

    # Add nodes with visual distinction
    for node in graph.nodes():
        node_data: dict[str, Any] = graph.nodes[node]  # type: ignore[assignment]
        node_type = node_data.get("type", "agent")
        label = node_data.get("label", str(node))

        if node_type == "agent":
            # Agent nodes: blue circles
            net.add_node(
                str(node),
                label=label,
                color="#4A90E2",
                shape="dot",
                size=25,
                title=f"Agent: {label}",
            )
        else:
            # Tool nodes: green squares
            net.add_node(
                str(node),
                label=label,
                color="#50C878",
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

    # Read and render HTML
    html_content = tmp_path.read_text(encoding="utf-8")
    components.html(html_content, height=620, scrolling=False)

    # Cleanup temporary file
    tmp_path.unlink()

    # Display graph statistics
    with st.expander("Graph Statistics"):
        st.text(f"Total Nodes: {graph.number_of_nodes()}")
        st.text(f"Total Edges: {graph.number_of_edges()}")

        agent_nodes = sum(1 for n in graph.nodes() if graph.nodes[n].get("type") == "agent")
        tool_nodes = graph.number_of_nodes() - agent_nodes

        st.text(f"Agent Nodes: {agent_nodes}")
        st.text(f"Tool Nodes: {tool_nodes}")
