"""
Graph-based analysis engine for Tier 3 evaluation.

Provides NetworkX-based analysis of agent coordination patterns,
tool usage efficiency, and communication overhead with streamlined
implementation focusing on essential multi-agent interaction metrics.

Note: This module contains type: ignore comments for NetworkX operations
due to incomplete type hints in the NetworkX library itself.
"""

from __future__ import annotations

import math
import signal
from typing import TYPE_CHECKING, Any

import networkx as nx

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.utils.log import logger

if TYPE_CHECKING:
    from app.judge.settings import JudgeSettings


class GraphAnalysisEngine:
    """NetworkX-based graph analysis engine for agent coordination evaluation.

    Implements essential graph-based complexity metrics for multi-agent systems
    with focus on tool usage patterns, communication efficiency, and coordination
    quality using lightweight NetworkX operations.
    """

    def __init__(self, settings: JudgeSettings) -> None:
        """Initialize graph analysis engine with settings.

        Args:
            settings: JudgeSettings instance with tier3 configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        self.settings = settings

        self.min_nodes_for_analysis = settings.tier3_min_nodes
        self.centrality_measures = list(settings.tier3_centrality_measures)

        # Weights for composite scoring
        self.weights = {
            "path_convergence": 0.3,
            "tool_accuracy": 0.25,
            "coordination_quality": 0.25,
            "task_balance": 0.2,
        }

        # Resource limits for production safety
        self.max_nodes = settings.tier3_max_nodes
        self.max_edges = settings.tier3_max_edges
        self.operation_timeout = settings.tier3_operation_timeout

    def _validate_trace_data(self, trace_data: GraphTraceData) -> None:
        """Validate GraphTraceData structure and content before analysis.

        Args:
            trace_data: Execution trace data to validate

        Raises:
            ValueError: If trace data is invalid or incomplete
        """
        if not trace_data.execution_id:
            raise ValueError("execution_id is required in trace data")

        self._validate_agent_interactions(trace_data.agent_interactions)
        self._validate_tool_calls(trace_data.tool_calls)
        self._check_data_size_limits(trace_data)

    def _validate_agent_interactions(self, interactions: list[dict[str, Any]]) -> None:
        """Validate agent interactions structure."""
        for i, interaction in enumerate(interactions):
            if "from" not in interaction or "to" not in interaction:
                raise ValueError(f"Agent interaction {i} missing 'from' or 'to' field")
            if not interaction["from"] or not interaction["to"]:
                raise ValueError(f"Agent interaction {i} has empty 'from' or 'to' field")

    def _validate_tool_calls(self, tool_calls: list[dict[str, Any]]) -> None:
        """Validate tool calls structure."""
        for i, call in enumerate(tool_calls):
            if "agent_id" not in call:
                raise ValueError(f"Tool call {i} missing 'agent_id' field")
            if not call["agent_id"]:
                raise ValueError(f"Tool call {i} has empty 'agent_id' field")

    def _check_data_size_limits(self, trace_data: GraphTraceData) -> None:
        """Check trace data against size limits."""
        total_interactions = len(trace_data.agent_interactions)
        total_calls = len(trace_data.tool_calls)
        total_events = total_interactions + total_calls

        if total_events > self.max_nodes:
            logger.warning(f"Trace has {total_events} events, exceeding max_nodes={self.max_nodes}")

        estimated_edges = total_interactions + (total_calls * 2)
        if estimated_edges > self.max_edges:
            logger.warning(
                f"Trace may generate ~{estimated_edges} edges, exceeding max_edges={self.max_edges}"
            )

    def _with_timeout(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute function with timeout protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result or None if timeout

        Raises:
            TimeoutError: If operation exceeds timeout limit
        """

        def timeout_handler(signum: int, frame: Any) -> None:
            raise TimeoutError(f"Graph operation exceeded {self.operation_timeout}s timeout")

        # Set up timeout signal
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.operation_timeout))

        try:
            result = func(*args, **kwargs)
            return result
        except TimeoutError:
            logger.error(f"Graph operation timed out after {self.operation_timeout}s")
            raise
        except (
            nx.NetworkXError,
            nx.NetworkXPointlessConcept,
            nx.NetworkXAlgorithmError,
        ) as e:
            logger.warning(f"NetworkX operation failed: {e}")
            raise
        finally:
            # Always restore signal handler and cancel alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def analyze_tool_usage_patterns(self, trace_data: GraphTraceData) -> dict[str, float]:
        """Analyze tool usage efficiency and selection patterns.

        Args:
            trace_data: Processed execution trace data

        Returns:
            Dictionary with tool analysis metrics
        """
        # Validate trace data first
        self._validate_trace_data(trace_data)

        if not trace_data.tool_calls:
            return {"path_convergence": 0.0, "tool_selection_accuracy": 0.0}

        try:
            # Create tool usage graph
            tool_graph = nx.DiGraph()

            # Add tool call sequences as graph edges
            for i, call in enumerate(trace_data.tool_calls):
                tool_name = call.get("tool_name", f"tool_{i}")
                agent_id = call.get("agent_id", f"agent_{i}")
                success = call.get("success", False)

                # Add nodes and edges for tool usage patterns
                tool_graph.add_node(tool_name, type="tool", success_rate=1.0 if success else 0.0)
                tool_graph.add_node(agent_id, type="agent")
                tool_graph.add_edge(agent_id, tool_name, weight=1.0 if success else 0.5)

            if len(tool_graph.nodes) < self.min_nodes_for_analysis:  # type: ignore[arg-type]
                return {"path_convergence": 0.5, "tool_selection_accuracy": 0.5}

            # Calculate path convergence using graph connectivity
            path_convergence = self._calculate_path_convergence(tool_graph)

            # Calculate tool selection accuracy from success rates
            tool_nodes = [n for n, d in tool_graph.nodes(data=True) if d.get("type") == "tool"]
            if tool_nodes:
                success_rates = [
                    tool_graph.nodes[tool].get("success_rate", 0.0) for tool in tool_nodes
                ]
                tool_accuracy = sum(success_rates) / len(success_rates)
            else:
                tool_accuracy = 0.0

            return {
                "path_convergence": path_convergence,
                "tool_selection_accuracy": tool_accuracy,
            }

        except Exception as e:
            logger.warning(f"Tool usage pattern analysis failed: {e}")
            return {"path_convergence": 0.0, "tool_selection_accuracy": 0.0}

    def analyze_agent_interactions(self, trace_data: GraphTraceData) -> dict[str, float]:
        """Analyze agent-to-agent communication and coordination patterns.

        Args:
            trace_data: Processed execution trace data

        Returns:
            Dictionary with interaction analysis metrics
        """
        self._validate_trace_data(trace_data)

        if not trace_data.agent_interactions:
            return {"communication_overhead": 1.0, "coordination_centrality": 0.0}

        try:
            interaction_graph = self._build_interaction_graph(trace_data.agent_interactions)

            if len(interaction_graph.nodes) < self.min_nodes_for_analysis:  # type: ignore[arg-type]
                return {"communication_overhead": 0.8, "coordination_centrality": 0.5}

            efficiency_ratio = self._calculate_communication_efficiency(interaction_graph)
            max_centrality = self._calculate_coordination_centrality(interaction_graph)

            return {
                "communication_overhead": efficiency_ratio,
                "coordination_centrality": max_centrality,
            }

        except Exception as e:
            logger.warning(f"Agent interaction analysis failed: {e}")
            return {"communication_overhead": 0.5, "coordination_centrality": 0.0}

    def _build_interaction_graph(self, interactions: list[dict[str, Any]]) -> Any:
        """Build NetworkX graph from agent interactions."""
        interaction_graph = nx.DiGraph()

        for interaction in interactions:
            from_agent = interaction.get("from", "unknown")
            to_agent = interaction.get("to", "unknown")
            interaction_type = interaction.get("type", "communication")

            weight = 1.0 if interaction_type in ["delegation", "coordination"] else 0.5
            interaction_graph.add_edge(from_agent, to_agent, weight=weight)

        return interaction_graph

    def _calculate_communication_efficiency(self, graph: Any) -> float:
        """Calculate communication efficiency ratio."""
        total_edges = len(graph.edges)  # type: ignore[arg-type]
        total_nodes = len(graph.nodes)  # type: ignore[arg-type]

        if total_nodes <= 1:
            return 1.0

        ideal_communications = total_nodes * math.log2(total_nodes)
        return min(1.0, ideal_communications / max(1, total_edges))

    def _calculate_coordination_centrality(self, graph: Any) -> float:
        """Calculate coordination centrality from betweenness."""
        if len(graph.nodes) <= 2:  # type: ignore[arg-type]
            return 0.5

        centrality_scores = nx.betweenness_centrality(graph)  # type: ignore[arg-type]
        return max(centrality_scores.values()) if centrality_scores else 0.0  # type: ignore[arg-type]

    def analyze_task_distribution(self, trace_data: GraphTraceData) -> float:
        """Analyze task distribution balance across agents.

        Args:
            trace_data: Processed execution trace data

        Returns:
            Task distribution balance score (0.0-1.0)
        """
        self._validate_trace_data(trace_data)

        try:
            agent_activities = self._count_agent_activities(trace_data)

            if not agent_activities:
                return 0.0

            activities = list(agent_activities.values())
            if len(activities) <= 1:
                return 1.0

            return self._calculate_balance_score(activities)

        except Exception as e:
            logger.warning(f"Task distribution analysis failed: {e}")
            return 0.0

    def _count_agent_activities(self, trace_data: GraphTraceData) -> dict[str, int]:
        """Count activities per agent from trace data."""
        agent_activities: dict[str, int] = {}

        for call in trace_data.tool_calls:
            agent_id = call.get("agent_id", "unknown")
            agent_activities[agent_id] = agent_activities.get(agent_id, 0) + 1

        for interaction in trace_data.agent_interactions:
            from_agent = interaction.get("from", "unknown")
            agent_activities[from_agent] = agent_activities.get(from_agent, 0) + 1

        return agent_activities

    def _calculate_balance_score(self, activities: list[int]) -> float:
        """Calculate balance score from activity counts."""
        mean_activity = sum(activities) / len(activities)
        if mean_activity == 0:
            return 0.0

        variance = sum((x - mean_activity) ** 2 for x in activities) / len(activities)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_activity

        balance_score = max(0.0, 1.0 - cv)
        return min(1.0, balance_score)

    def _calculate_path_convergence(self, graph: Any) -> float:
        """Calculate path convergence efficiency in tool usage graph.

        Args:
            graph: NetworkX graph of tool usage patterns

        Returns:
            Path convergence score (0.0-1.0)
        """
        if len(graph.nodes) < 2:
            return 0.5

        try:
            undirected_graph = graph.to_undirected()
            if not nx.is_connected(undirected_graph):
                return 0.2  # Disconnected graph has poor convergence

            return self._calculate_connected_graph_convergence(graph, undirected_graph)
        except Exception as e:
            logger.debug(f"Path convergence calculation failed: {e}")
            return 0.0

    def _calculate_connected_graph_convergence(self, graph: Any, undirected_graph: Any) -> float:
        """Calculate convergence for connected graph."""
        try:
            avg_path_length = self._with_timeout(nx.average_shortest_path_length, undirected_graph)
            return self._normalize_path_length(len(graph.nodes), avg_path_length)
        except (TimeoutError, nx.NetworkXError):
            logger.warning("Path length calculation failed or timed out")
            return 0.3

    def _normalize_path_length(self, num_nodes: int, avg_path_length: float) -> float:
        """Normalize average path length to convergence score."""
        max_possible_length = num_nodes - 1
        denominator = max_possible_length - 1

        if denominator <= 0:
            return 1.0 if num_nodes == 2 else 0.5

        convergence = 1.0 - (avg_path_length - 1) / denominator
        return max(0.0, min(1.0, convergence))

    def evaluate_graph_metrics(self, trace_data: GraphTraceData) -> Tier3Result:
        """Complete graph-based analysis evaluation.

        Args:
            trace_data: Processed execution trace data

        Returns:
            Tier3Result with all graph analysis metrics
        """
        try:
            # Analyze different aspects of the execution graph
            tool_metrics = self.analyze_tool_usage_patterns(trace_data)
            interaction_metrics = self.analyze_agent_interactions(trace_data)
            task_balance = self.analyze_task_distribution(trace_data)

            # Extract individual metrics
            path_convergence = tool_metrics.get("path_convergence", 0.0)
            tool_accuracy = tool_metrics.get("tool_selection_accuracy", 0.0)
            communication_efficiency = interaction_metrics.get("communication_overhead", 0.0)
            coordination_quality = interaction_metrics.get("coordination_centrality", 0.0)

            # Calculate graph complexity (total unique nodes)
            unique_agents = set()
            for interaction in trace_data.agent_interactions:
                unique_agents.add(interaction.get("from", "unknown"))
                unique_agents.add(interaction.get("to", "unknown"))
            for call in trace_data.tool_calls:
                unique_agents.add(call.get("agent_id", "unknown"))
            graph_complexity = len(unique_agents)  # type: ignore[arg-type]

            # Calculate weighted overall score
            overall_score = (
                path_convergence * self.weights.get("path_convergence", 0.3)
                + tool_accuracy * self.weights.get("tool_accuracy", 0.25)
                + coordination_quality * self.weights.get("coordination_quality", 0.25)
                + task_balance * self.weights.get("task_balance", 0.2)
            )

            return Tier3Result(
                path_convergence=path_convergence,
                tool_selection_accuracy=tool_accuracy,
                communication_overhead=1.0 - communication_efficiency,  # Invert for overhead
                coordination_centrality=coordination_quality,
                task_distribution_balance=task_balance,
                overall_score=overall_score,
                graph_complexity=graph_complexity,
            )

        except Exception as e:
            logger.error(f"Graph metrics evaluation failed: {e}")
            # Return minimal baseline scores
            return Tier3Result(
                path_convergence=0.0,
                tool_selection_accuracy=0.0,
                communication_overhead=1.0,
                coordination_centrality=0.0,
                task_distribution_balance=0.0,
                overall_score=0.0,
                graph_complexity=0,
            )

    def export_trace_to_networkx(self, trace_data: GraphTraceData) -> nx.DiGraph[str] | None:
        """Export trace data to NetworkX graph for Opik integration.

        Args:
            trace_data: Execution trace data to convert

        Returns:
            NetworkX directed graph or None if export fails
        """
        try:
            graph = nx.DiGraph()
            agent_nodes = self._add_agent_interactions_to_graph(
                graph, trace_data.agent_interactions
            )
            self._add_tool_usage_to_graph(graph, trace_data.tool_calls)
            self._add_graph_metadata(graph, trace_data, agent_nodes)

            logger.debug(
                f"Exported NetworkX graph: {graph.number_of_nodes()} nodes, "
                f"{graph.number_of_edges()} edges"
            )
            return graph

        except Exception as e:
            logger.error(f"Failed to export trace to NetworkX: {e}")
            return None

    def _add_agent_interactions_to_graph(
        self, graph: Any, interactions: list[dict[str, Any]]
    ) -> set[str]:
        """Add agent nodes and interactions to graph."""
        agent_nodes: set[str] = set()

        for interaction in interactions:
            source = interaction.get("from", "unknown")
            target = interaction.get("to", "unknown")
            agent_nodes.add(source)
            agent_nodes.add(target)

            self._ensure_agent_node(graph, source)
            self._ensure_agent_node(graph, target)
            self._add_interaction_edge(graph, source, target)

        return agent_nodes

    def _ensure_agent_node(self, graph: Any, agent_id: str) -> None:
        """Ensure agent node exists in graph."""
        if not graph.has_node(agent_id):
            graph.add_node(agent_id, type="agent", interaction_count=0)

    def _add_interaction_edge(self, graph: Any, source: str, target: str) -> None:
        """Add or update interaction edge between agents."""
        if not graph.has_edge(source, target):
            graph.add_edge(source, target, interaction_count=0)

        graph.edges[source, target]["interaction_count"] += 1
        graph.nodes[source]["interaction_count"] += 1
        graph.nodes[target]["interaction_count"] += 1

    def _add_tool_usage_to_graph(self, graph: Any, tool_calls: list[dict[str, Any]]) -> None:
        """Add tool nodes and usage edges to graph."""
        for tool_call in tool_calls:
            agent_id = tool_call.get("agent_id", "unknown")
            tool_name = tool_call.get("tool_name", "unknown_tool")

            self._ensure_tool_node(graph, tool_name)
            self._add_tool_usage_edge(graph, agent_id, tool_name)

    def _ensure_tool_node(self, graph: Any, tool_name: str) -> None:
        """Ensure tool node exists in graph."""
        if not graph.has_node(tool_name):
            graph.add_node(tool_name, type="tool", usage_count=0)

    def _add_tool_usage_edge(self, graph: Any, agent_id: str, tool_name: str) -> None:
        """Add or update tool usage edge."""
        if not graph.has_edge(agent_id, tool_name):
            graph.add_edge(agent_id, tool_name, usage_count=0)

        graph.edges[agent_id, tool_name]["usage_count"] += 1
        graph.nodes[tool_name]["usage_count"] += 1

    def _add_graph_metadata(
        self, graph: Any, trace_data: GraphTraceData, agent_nodes: set[str]
    ) -> None:
        """Add metadata to graph for Opik integration."""
        graph.graph.update(
            {
                "execution_id": trace_data.execution_id,
                "total_agents": len(agent_nodes),
                "total_interactions": len(trace_data.agent_interactions),
                "total_tool_calls": len(trace_data.tool_calls),
                "timing_data": trace_data.timing_data,
            }
        )


def evaluate_single_graph_analysis(
    trace_data: GraphTraceData | None, settings: JudgeSettings | None = None
) -> Tier3Result:
    """Convenience function for single graph analysis evaluation.

    Args:
        trace_data: Execution trace data for analysis
        settings: Optional JudgeSettings override. If None, uses defaults.

    Returns:
        Tier3Result with graph analysis metrics

    Example:
        >>> from app.judge.trace_processors import get_trace_collector
        >>> collector = get_trace_collector()
        >>> trace_data = collector.load_trace("execution_001")
        >>> result = evaluate_single_graph_analysis(trace_data)
        >>> print(f"Overall score: {result.overall_score:.3f}")
    """
    if settings is None:
        from app.judge.settings import JudgeSettings

        settings = JudgeSettings()
    engine = GraphAnalysisEngine(settings)

    if trace_data is None:
        # Return zero scores for missing trace data
        return Tier3Result(
            path_convergence=0.0,
            tool_selection_accuracy=0.0,
            communication_overhead=1.0,
            coordination_centrality=0.0,
            task_distribution_balance=0.0,
            overall_score=0.0,
            graph_complexity=0,
        )

    return engine.evaluate_graph_metrics(trace_data)
