"""Export nx.DiGraph as JSON (node-link format) and PNG (static render).

Persists the agent interaction graph built after each run to the per-run
output directory. Both functions register their output with the
ArtifactRegistry for end-of-run summary display.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import networkx as nx

from app.utils.artifact_registry import get_artifact_registry
from app.utils.log import logger

# Reason: matplotlib needs a writable config dir; default may be read-only in containers
os.environ.setdefault("MPLCONFIGDIR", str(Path.home() / ".config" / "matplotlib"))


def export_graph_json(graph: nx.DiGraph[str], output_dir: Path) -> Path:
    """Serialize an nx.DiGraph to agent_graph.json using node-link format.

    Args:
        graph: NetworkX directed graph to export.
        output_dir: Directory to write the JSON file into.

    Returns:
        Path to the written agent_graph.json file.
    """
    out_path = output_dir / "agent_graph.json"
    data = nx.node_link_data(graph)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    get_artifact_registry().register("Agent Graph (JSON)", out_path)
    logger.info(f"Agent graph JSON written to {out_path}")
    return out_path


def export_graph_png(graph: nx.DiGraph[str], output_dir: Path) -> Path:
    """Render an nx.DiGraph to agent_graph.png as a static image.

    Agent nodes are drawn as circles (#4e79a7 blue), tool nodes as squares
    (#59a14f green). Layout uses spring_layout with a fixed seed for
    reproducibility.

    Args:
        graph: NetworkX directed graph to render.
        output_dir: Directory to write the PNG file into.

    Returns:
        Path to the written agent_graph.png file.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path = output_dir / "agent_graph.png"

    fig, ax = plt.subplots(figsize=(10, 8))

    if graph.number_of_nodes() == 0:
        ax.set_title("Agent Interaction Graph (empty)")
        ax.text(0.5, 0.5, "No agents or tools", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
    else:
        pos = nx.spring_layout(graph, seed=42)

        agent_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "agent"]
        tool_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "tool"]

        # Draw agent nodes (circles)
        if agent_nodes:
            nx.draw_networkx_nodes(
                graph,
                pos,
                nodelist=agent_nodes,
                node_color="#4e79a7",
                node_shape="o",
                node_size=600,
                ax=ax,
            )

        # Draw tool nodes (squares)
        if tool_nodes:
            nx.draw_networkx_nodes(
                graph,
                pos,
                nodelist=tool_nodes,
                node_color="#59a14f",
                node_shape="s",
                node_size=400,
                ax=ax,
            )

        nx.draw_networkx_edges(graph, pos, ax=ax, arrows=True)

        labels = {n: d.get("label", n) for n, d in graph.nodes(data=True)}
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, ax=ax)

        ax.set_title("Agent Interaction Graph")

    fig.savefig(out_path, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)

    get_artifact_registry().register("Agent Graph (PNG)", out_path)
    logger.info(f"Agent graph PNG written to {out_path}")
    return out_path


def persist_graph(graph: nx.DiGraph[str] | None, output_dir: Path) -> None:
    """Export graph as JSON and PNG if graph is available.

    No-op when graph is None. Convenience wrapper used by app.main()
    to avoid adding branching complexity.

    Args:
        graph: NetworkX directed graph, or None if unavailable.
        output_dir: Per-run output directory.
    """
    if graph is None:
        return
    export_graph_json(graph, output_dir)
    export_graph_png(graph, output_dir)
