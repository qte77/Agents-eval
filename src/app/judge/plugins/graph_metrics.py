"""
GraphEvaluatorPlugin wrapper for Tier 3 evaluation.

Wraps the existing GraphAnalysisEngine as an EvaluatorPlugin
following the adapter pattern with configurable timeout.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.evals.graph_analysis import GraphAnalysisEngine
from app.evals.settings import JudgeSettings
from app.judge.plugins.base import EvaluatorPlugin
from app.utils.log import logger


class GraphEvaluatorPlugin(EvaluatorPlugin):
    """Adapter wrapping GraphAnalysisEngine as an EvaluatorPlugin.

    Provides Tier 3 evaluation using graph-based analysis of agent
    coordination patterns with configurable timeout from JudgeSettings.

    Attributes:
        timeout_seconds: Maximum execution time for this plugin
        _engine: Underlying GraphAnalysisEngine instance
        _settings: JudgeSettings instance for configuration
    """

    def __init__(self, timeout_seconds: float | None = None):
        """Initialize plugin with optional timeout override.

        Args:
            timeout_seconds: Optional timeout override. If None, uses JudgeSettings default.
        """
        self._settings = JudgeSettings()
        self.timeout_seconds = timeout_seconds or self._settings.tier3_max_seconds
        self._engine = GraphAnalysisEngine(self._settings)

    @property
    def name(self) -> str:
        """Return unique plugin identifier.

        Returns:
            Plugin name string
        """
        return "graph_metrics"

    @property
    def tier(self) -> int:
        """Return evaluation tier number.

        Returns:
            Tier 3 (Graph Analysis)
        """
        return 3

    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
        """Execute Tier 3 graph-based evaluation.

        Args:
            input_data: Input containing trace_data (GraphTraceData)
            context: Optional context from previous tiers (Tier 1 and Tier 2)

        Returns:
            Tier3Result with graph analysis metrics

        Raises:
            ValueError: If input validation fails
            RuntimeError: If evaluation execution fails
        """
        # Extract trace_data from input_data
        # Reason: Pydantic BaseModel doesn't support attribute access without type checking
        trace_data = getattr(input_data, "trace_data", None)

        if trace_data is None:
            logger.warning("No trace_data provided for graph evaluation")
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

        # Log context enrichment if previous tier data available
        if context:
            tier1_score = context.get("tier1_overall_score")
            tier2_score = context.get("tier2_overall_score")
            if tier1_score is not None and tier2_score is not None:
                logger.debug(
                    f"Previous tier context available: "
                    f"Tier1={tier1_score:.2f}, Tier2={tier2_score:.2f}"
                )

        # Delegate to existing engine
        result = self._engine.evaluate_graph_metrics(trace_data)

        return result

    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
        """Extract context from Tier 3 results for potential future tiers.

        Args:
            result: Tier3Result from this plugin's evaluation

        Returns:
            Dictionary containing tier3_overall_score and graph metrics
        """
        # Reason: Type narrowing for BaseModel to Tier3Result
        if not isinstance(result, Tier3Result):
            return {}

        return {
            "tier3_overall_score": result.overall_score,
            "tier3_graph_metrics": {
                "path_convergence": result.path_convergence,
                "tool_selection_accuracy": result.tool_selection_accuracy,
                "coordination_centrality": result.coordination_centrality,
                "task_distribution_balance": result.task_distribution_balance,
            },
            "tier3_graph_complexity": result.graph_complexity,
        }
