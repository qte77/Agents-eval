"""
Utility for building NetworkX graphs from GraphTraceData.

Converts execution trace data into interactive network visualizations
showing agent-to-agent interactions and tool usage patterns.
"""

from __future__ import annotations

import networkx as nx

from app.data_models.evaluation_models import GraphTraceData
from app.utils.log import logger


def build_interaction_graph(trace_data: GraphTraceData) -> nx.DiGraph[str]:
    """Build NetworkX directed graph from execution trace data.

    Creates a visual representation of agent interactions and tool usage:
    - Agent nodes (blue circles in visualization)
    - Tool nodes (green squares in visualization)
    - Edges representing delegations and tool calls

    Args:
        trace_data: GraphTraceData containing agent interactions and tool calls

    Returns:
        NetworkX DiGraph with nodes and edges representing the execution flow
    """
    graph = nx.DiGraph()

    # Add agent-to-agent interactions
    for interaction in trace_data.agent_interactions:
        source = interaction.get("from", interaction.get("source_agent", "unknown"))
        target = interaction.get("to", interaction.get("target_agent", "unknown"))
        interaction_type = interaction.get(
            "type", interaction.get("interaction_type", "communication")
        )

        # Add agent nodes if not already present
        if source not in graph:
            graph.add_node(source, node_type="agent", label=source.capitalize())
        if target not in graph:
            graph.add_node(target, node_type="agent", label=target.capitalize())

        # Add edge with interaction type
        graph.add_edge(source, target, interaction=interaction_type)

    # Add tool usage patterns
    for tool_call in trace_data.tool_calls:
        agent_id = tool_call.get("agent_id", "unknown")
        tool_name = tool_call.get("tool_name", "unknown_tool")

        # Add agent node if not already present
        if agent_id not in graph:
            graph.add_node(agent_id, node_type="agent", label=agent_id.capitalize())

        # Add tool node
        if tool_name not in graph:
            graph.add_node(tool_name, node_type="tool", label=tool_name.replace("_", " ").title())

        # Add edge from agent to tool
        success = tool_call.get("success", False)
        graph.add_edge(agent_id, tool_name, interaction="tool_call", success=success)

    logger.debug(
        f"Built interaction graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    )

    return graph
