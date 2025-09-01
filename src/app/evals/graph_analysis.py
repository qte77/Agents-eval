"""
Graph-based analysis engine for Tier 3 evaluation.

Provides NetworkX-based analysis of agent coordination patterns,
tool usage efficiency, and communication overhead with streamlined
implementation focusing on essential multi-agent interaction metrics.
"""

import math
import signal
from typing import Any

import networkx as nx

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.utils.log import logger


class GraphAnalysisEngine:
    """NetworkX-based graph analysis engine for agent coordination evaluation.

    Implements essential graph-based complexity metrics for multi-agent systems
    with focus on tool usage patterns, communication efficiency, and coordination
    quality using lightweight NetworkX operations.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize graph analysis engine with configuration.

        Args:
            config: Configuration from config_eval.json

        Raises:
            ValueError: If configuration is invalid
        """
        self.config = config
        tier3_config = config.get("tier3_graph", {})

        # Validate configuration first
        self._validate_config(tier3_config)

        self.min_nodes_for_analysis = tier3_config.get("min_nodes_for_analysis", 2)
        self.centrality_measures = tier3_config.get(
            "centrality_measures", ["betweenness", "closeness", "degree"]
        )

        # Weights for composite scoring
        self.weights = tier3_config.get(
            "graph_weights",
            {
                "path_convergence": 0.3,
                "tool_accuracy": 0.25,
                "coordination_quality": 0.25,
                "task_balance": 0.2,
            },
        )

        # Resource limits for production safety
        self.max_nodes = tier3_config.get("max_nodes", 1000)
        self.max_edges = tier3_config.get("max_edges", 5000)
        self.operation_timeout = tier3_config.get("operation_timeout_seconds", 10.0)

    def _validate_config(self, tier3_config: dict[str, Any]) -> None:
        """Validate tier3_graph configuration parameters.

        Args:
            tier3_config: Configuration dictionary for tier 3 analysis

        Raises:
            ValueError: If configuration parameters are invalid
        """
        # Validate min_nodes_for_analysis
        min_nodes = tier3_config.get("min_nodes_for_analysis", 2)
        if not isinstance(min_nodes, int) or min_nodes < 1:
            raise ValueError("min_nodes_for_analysis must be positive integer")

        # Validate centrality measures
        centrality_measures = tier3_config.get(
            "centrality_measures", ["betweenness", "closeness", "degree"]
        )
        valid_measures = {"betweenness", "closeness", "degree", "eigenvector"}
        if not isinstance(centrality_measures, list):
            raise ValueError("centrality_measures must be a list")
        for measure in centrality_measures:
            if measure not in valid_measures:
                raise ValueError(f"Unknown centrality measure: {measure}")

        # Validate graph weights
        weights = tier3_config.get("graph_weights", {})
        if weights:
            # Check weights are non-negative and valid keys
            valid_keys = {
                "path_convergence",
                "tool_accuracy",
                "coordination_quality",
                "task_balance",
            }
            for key, weight in weights.items():
                if key not in valid_keys:
                    raise ValueError(
                        f"Unknown weight key: {key}. Valid keys: {valid_keys}"
                    )
                if not isinstance(weight, int | float) or weight < 0:
                    raise ValueError(f"Weight {key} must be non-negative number")

            # Warn if weights sum is unusual (allow partial specifications)
            total_weight = sum(weights.values())
            if total_weight > 1.5:  # Only warn if clearly excessive
                logger.warning(
                    f"Graph weights sum to {total_weight:.3f}, "
                    "this may cause scoring issues"
                )

        # Validate resource limits if specified
        max_nodes = tier3_config.get("max_nodes")
        if max_nodes is not None and (not isinstance(max_nodes, int) or max_nodes < 10):
            raise ValueError("max_nodes must be integer >= 10")

        max_edges = tier3_config.get("max_edges")
        if max_edges is not None and (not isinstance(max_edges, int) or max_edges < 10):
            raise ValueError("max_edges must be integer >= 10")

        timeout = tier3_config.get("operation_timeout_seconds")
        if timeout is not None and (
            not isinstance(timeout, int | float) or timeout <= 0
        ):
            raise ValueError("operation_timeout_seconds must be positive number")

    def _validate_trace_data(self, trace_data: GraphTraceData) -> None:
        """Validate GraphTraceData structure and content before analysis.

        Args:
            trace_data: Execution trace data to validate

        Raises:
            ValueError: If trace data is invalid or incomplete
        """
        if not trace_data.execution_id:
            raise ValueError("execution_id is required in trace data")

        # Validate agent interactions structure
        for i, interaction in enumerate(trace_data.agent_interactions):
            if "from" not in interaction or "to" not in interaction:
                raise ValueError(f"Agent interaction {i} missing 'from' or 'to' field")
            if not interaction["from"] or not interaction["to"]:
                raise ValueError(
                    f"Agent interaction {i} has empty 'from' or 'to' field"
                )

        # Validate tool calls structure
        for i, call in enumerate(trace_data.tool_calls):
            if "agent_id" not in call:
                raise ValueError(f"Tool call {i} missing 'agent_id' field")
            if not call["agent_id"]:
                raise ValueError(f"Tool call {i} has empty 'agent_id' field")

        # Check data size limits
        total_interactions = len(trace_data.agent_interactions)
        total_calls = len(trace_data.tool_calls)
        total_events = total_interactions + total_calls

        if total_events > self.max_nodes:
            logger.warning(
                f"Trace has {total_events} events, exceeding max_nodes={self.max_nodes}"
            )

        # Estimate potential edges (interactions + tool usage patterns)
        estimated_edges = total_interactions + (
            total_calls * 2
        )  # Conservative estimate
        if estimated_edges > self.max_edges:
            logger.warning(
                f"Trace may generate ~{estimated_edges} edges, "
                f"exceeding max_edges={self.max_edges}"
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
            raise TimeoutError(
                f"Graph operation exceeded {self.operation_timeout}s timeout"
            )

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

    def analyze_tool_usage_patterns(
        self, trace_data: GraphTraceData
    ) -> dict[str, float]:
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
                tool_graph.add_node(
                    tool_name, type="tool", success_rate=1.0 if success else 0.0
                )
                tool_graph.add_node(agent_id, type="agent")
                tool_graph.add_edge(agent_id, tool_name, weight=1.0 if success else 0.5)

            if len(tool_graph.nodes) < self.min_nodes_for_analysis:
                return {"path_convergence": 0.5, "tool_selection_accuracy": 0.5}

            # Calculate path convergence using graph connectivity
            path_convergence = self._calculate_path_convergence(tool_graph)

            # Calculate tool selection accuracy from success rates
            tool_nodes = [
                n for n, d in tool_graph.nodes(data=True) if d.get("type") == "tool"
            ]
            if tool_nodes:
                success_rates = [
                    tool_graph.nodes[tool].get("success_rate", 0.0)
                    for tool in tool_nodes
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

    def analyze_agent_interactions(
        self, trace_data: GraphTraceData
    ) -> dict[str, float]:
        """Analyze agent-to-agent communication and coordination patterns.

        Args:
            trace_data: Processed execution trace data

        Returns:
            Dictionary with interaction analysis metrics
        """
        # Validate trace data first
        self._validate_trace_data(trace_data)

        if not trace_data.agent_interactions:
            return {"communication_overhead": 1.0, "coordination_centrality": 0.0}

        try:
            # Create agent interaction graph
            interaction_graph = nx.DiGraph()

            # Build interaction network
            for interaction in trace_data.agent_interactions:
                from_agent = interaction.get("from", "unknown")
                to_agent = interaction.get("to", "unknown")
                interaction_type = interaction.get("type", "communication")

                # Weight different interaction types
                weight = (
                    1.0 if interaction_type in ["delegation", "coordination"] else 0.5
                )

                interaction_graph.add_edge(from_agent, to_agent, weight=weight)

            if len(interaction_graph.nodes) < self.min_nodes_for_analysis:
                return {"communication_overhead": 0.8, "coordination_centrality": 0.5}

            # Calculate communication efficiency (lower overhead = better)
            total_edges = len(interaction_graph.edges)
            total_nodes = len(interaction_graph.nodes)

            # Ideal communication: O(n log n), actual vs ideal ratio
            if total_nodes > 1:
                ideal_communications = total_nodes * math.log2(total_nodes)
                efficiency_ratio = min(1.0, ideal_communications / max(1, total_edges))
            else:
                efficiency_ratio = 1.0

            # Calculate coordination centrality using betweenness centrality
            if len(interaction_graph.nodes) > 2:
                centrality_scores = nx.betweenness_centrality(interaction_graph)
                max_centrality = (
                    max(centrality_scores.values()) if centrality_scores else 0.0
                )
            else:
                max_centrality = 0.5

            return {
                "communication_overhead": efficiency_ratio,
                "coordination_centrality": max_centrality,
            }

        except Exception as e:
            logger.warning(f"Agent interaction analysis failed: {e}")
            return {"communication_overhead": 0.5, "coordination_centrality": 0.0}

    def analyze_task_distribution(self, trace_data: GraphTraceData) -> float:
        """Analyze task distribution balance across agents.

        Args:
            trace_data: Processed execution trace data

        Returns:
            Task distribution balance score (0.0-1.0)
        """
        # Validate trace data first
        self._validate_trace_data(trace_data)

        try:
            # Combine all agent activities
            agent_activities = {}

            # Count tool calls per agent
            for call in trace_data.tool_calls:
                agent_id = call.get("agent_id", "unknown")
                agent_activities[agent_id] = agent_activities.get(agent_id, 0) + 1

            # Count interactions per agent
            for interaction in trace_data.agent_interactions:
                from_agent = interaction.get("from", "unknown")
                agent_activities[from_agent] = agent_activities.get(from_agent, 0) + 1

            if not agent_activities:
                return 0.0

            # Calculate load balance using coefficient of variation
            activities = list(agent_activities.values())
            if len(activities) <= 1:
                return 1.0  # Perfect balance for single agent

            mean_activity = sum(activities) / len(activities)
            if mean_activity == 0:
                return 0.0

            variance = sum((x - mean_activity) ** 2 for x in activities) / len(
                activities
            )
            std_dev = math.sqrt(variance)

            # Coefficient of variation: lower = better balance
            cv = std_dev / mean_activity

            # Convert to score: perfect balance = 1.0, high imbalance = 0.0
            balance_score = max(0.0, 1.0 - cv)
            return min(1.0, balance_score)

        except Exception as e:
            logger.warning(f"Task distribution analysis failed: {e}")
            return 0.0

    def _calculate_path_convergence(self, graph: Any) -> float:
        """Calculate path convergence efficiency in tool usage graph.

        Args:
            graph: NetworkX graph of tool usage patterns

        Returns:
            Path convergence score (0.0-1.0)
        """
        try:
            if len(graph.nodes) < 2:
                return 0.5

            # Calculate average shortest path length with timeout protection
            undirected_graph = graph.to_undirected()
            if nx.is_connected(undirected_graph):
                try:
                    avg_path_length = self._with_timeout(
                        nx.average_shortest_path_length, undirected_graph
                    )
                    max_possible_length = len(graph.nodes) - 1

                    # Fix division by zero: ensure denominator is never zero
                    denominator = max_possible_length - 1
                    if denominator <= 0:
                        # For graphs with 2 nodes, path length is optimal
                        return 1.0 if len(graph.nodes) == 2 else 0.5

                    # Normalize: shorter paths = better convergence
                    convergence = 1.0 - (avg_path_length - 1) / denominator
                    return max(0.0, min(1.0, convergence))
                except (TimeoutError, nx.NetworkXError):
                    logger.warning("Path length calculation failed or timed out")
                    return 0.3  # Conservative fallback for connected graph
            else:
                # Graph is disconnected - poor convergence
                return 0.2

        except Exception as e:
            logger.debug(f"Path convergence calculation failed: {e}")
            return 0.0

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
            communication_efficiency = interaction_metrics.get(
                "communication_overhead", 0.0
            )
            coordination_quality = interaction_metrics.get(
                "coordination_centrality", 0.0
            )

            # Calculate graph complexity (total unique nodes)
            unique_agents = set()
            for interaction in trace_data.agent_interactions:
                unique_agents.add(interaction.get("from", "unknown"))
                unique_agents.add(interaction.get("to", "unknown"))
            for call in trace_data.tool_calls:
                unique_agents.add(call.get("agent_id", "unknown"))
            graph_complexity = len(unique_agents)

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
                communication_overhead=1.0
                - communication_efficiency,  # Invert for overhead
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


def evaluate_single_graph_analysis(
    trace_data: GraphTraceData | None, config: dict[str, Any] | None = None
) -> Tier3Result:
    """Convenience function for single graph analysis evaluation.

    Args:
        trace_data: Execution trace data for analysis
        config: Optional configuration override

    Returns:
        Tier3Result with graph analysis metrics

    Example:
        >>> from app.evals.trace_processors import get_trace_collector
        >>> collector = get_trace_collector()
        >>> trace_data = collector.load_trace("execution_001")
        >>> result = evaluate_single_graph_analysis(trace_data)
        >>> print(f"Overall score: {result.overall_score:.3f}")
    """
    config = config or {}
    engine = GraphAnalysisEngine(config)

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
