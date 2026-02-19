"""
LLMJudgePlugin wrapper for Tier 2 evaluation.

Wraps the existing LLMJudgeEngine as an EvaluatorPlugin
following the adapter pattern with opt-in Tier 1 context enrichment.
"""

from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel

from app.data_models.evaluation_models import Tier2Result
from app.judge.llm_evaluation_managers import LLMJudgeEngine
from app.judge.plugins.base import EvaluatorPlugin
from app.judge.settings import JudgeSettings
from app.utils.log import logger


class LLMJudgePlugin(EvaluatorPlugin):
    """Adapter wrapping LLMJudgeEngine as an EvaluatorPlugin.

    Provides Tier 2 evaluation using LLM-as-Judge methodology
    with configurable timeout and optional Tier 1 context enrichment.

    Attributes:
        timeout_seconds: Maximum execution time for this plugin
        _engine: Underlying LLMJudgeEngine instance
        _settings: JudgeSettings instance for configuration
    """

    def __init__(self, timeout_seconds: float | None = None):
        """Initialize plugin with optional timeout override.

        Args:
            timeout_seconds: Optional timeout override. If None, uses JudgeSettings default.
        """
        self._settings = JudgeSettings()
        self.timeout_seconds = timeout_seconds or self._settings.tier2_timeout_seconds
        self._engine = LLMJudgeEngine(self._settings)

    @property
    def name(self) -> str:
        """Return unique plugin identifier.

        Returns:
            Plugin name string
        """
        return "llm_judge"

    @property
    def tier(self) -> int:
        """Return evaluation tier number.

        Returns:
            Tier 2 (LLM-as-Judge)
        """
        return 2

    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
        """Execute Tier 2 LLM-as-Judge evaluation.

        Args:
            input_data: Input containing paper, review, execution_trace
            context: Optional context from Tier 1 (for enrichment)

        Returns:
            Tier2Result with LLM quality assessments

        Raises:
            ValueError: If input validation fails
            RuntimeError: If evaluation execution fails
        """
        # Extract fields from input_data
        # Reason: Pydantic BaseModel doesn't support attribute access without type checking
        paper = getattr(input_data, "paper", "")
        review = getattr(input_data, "review", "")
        execution_trace = getattr(input_data, "execution_trace", {})

        # Log context enrichment if Tier 1 data available
        if context and "tier1_overall_score" in context:
            logger.debug(
                f"Tier 1 context available for enrichment: "
                f"score={context['tier1_overall_score']:.2f}"
            )

        # Delegate to existing engine (run async method in new event loop)
        result = asyncio.run(
            self._engine.evaluate_comprehensive(
                paper=paper, review=review, execution_trace=execution_trace
            )
        )

        return result

    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
        """Extract context from Tier 2 results for Tier 3.

        Args:
            result: Tier2Result from this plugin's evaluation

        Returns:
            Dictionary containing tier2_overall_score and quality metrics
        """
        # Reason: Type narrowing for BaseModel to Tier2Result
        if not isinstance(result, Tier2Result):
            return {}

        return {
            "tier2_overall_score": result.overall_score,
            "tier2_quality_metrics": {
                "technical_accuracy": result.technical_accuracy,
                "constructiveness": result.constructiveness,
                "clarity": result.clarity,
                "planning_rationality": result.planning_rationality,
            },
            "tier2_model_used": result.model_used,
            "tier2_fallback_used": result.fallback_used,
        }
