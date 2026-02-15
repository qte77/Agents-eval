"""
TraditionalMetricsPlugin wrapper for Tier 1 evaluation.

Wraps the existing TraditionalMetricsEngine as an EvaluatorPlugin
following the adapter pattern with configurable timeout.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.data_models.evaluation_models import Tier1Result
from app.judge.settings import JudgeSettings
from app.judge.traditional_metrics import TraditionalMetricsEngine
from app.judge.plugins.base import EvaluatorPlugin


class TraditionalMetricsPlugin(EvaluatorPlugin):
    """Adapter wrapping TraditionalMetricsEngine as an EvaluatorPlugin.

    Provides Tier 1 evaluation using lightweight text similarity metrics
    with configurable timeout from JudgeSettings.

    Attributes:
        timeout_seconds: Maximum execution time for this plugin
        _engine: Underlying TraditionalMetricsEngine instance
        _settings: JudgeSettings instance for configuration
    """

    def __init__(self, timeout_seconds: float | None = None):
        """Initialize plugin with optional timeout override.

        Args:
            timeout_seconds: Optional timeout override. If None, uses JudgeSettings default.
        """
        self._settings = JudgeSettings()
        self.timeout_seconds = timeout_seconds or self._settings.tier1_max_seconds
        self._engine = TraditionalMetricsEngine()

    @property
    def name(self) -> str:
        """Return unique plugin identifier.

        Returns:
            Plugin name string
        """
        return "traditional_metrics"

    @property
    def tier(self) -> int:
        """Return evaluation tier number.

        Returns:
            Tier 1 (Traditional Metrics)
        """
        return 1

    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
        """Execute Tier 1 traditional metrics evaluation.

        Args:
            input_data: Input containing agent_output, reference_texts, start_time, end_time
            context: Optional context from previous tiers (unused for Tier 1)

        Returns:
            Tier1Result with similarity metrics and execution timing

        Raises:
            ValueError: If input validation fails
            RuntimeError: If evaluation execution fails
        """
        # Extract fields from input_data
        # Reason: Pydantic BaseModel doesn't support attribute access without type checking
        agent_output = getattr(input_data, "agent_output", "")
        reference_texts = getattr(input_data, "reference_texts", [])
        start_time = getattr(input_data, "start_time", 0.0)
        end_time = getattr(input_data, "end_time", 0.0)

        # Delegate to existing engine
        result = self._engine.evaluate_traditional_metrics(
            agent_output=agent_output,
            reference_texts=reference_texts,
            start_time=start_time,
            end_time=end_time,
            settings=self._settings,
        )

        return result

    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
        """Extract context from Tier 1 results for Tier 2.

        Args:
            result: Tier1Result from this plugin's evaluation

        Returns:
            Dictionary containing tier1_overall_score and similarity metrics
        """
        # Reason: Type narrowing for BaseModel to Tier1Result
        if not isinstance(result, Tier1Result):
            return {}

        return {
            "tier1_overall_score": result.overall_score,
            "tier1_similarity_metrics": {
                "cosine": result.cosine_score,
                "jaccard": result.jaccard_score,
                "semantic": result.semantic_score,
            },
            "tier1_execution_time": result.execution_time,
            "tier1_task_success": result.task_success,
        }
