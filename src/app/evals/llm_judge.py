"""
LLM-as-Judge implementation for Tier 2 evaluation.

Provides quality assessment using existing PydanticAI infrastructure
with cost optimization and fallback mechanisms. This module serves as
a compatibility layer for the comprehensive LLM evaluation manager.
"""

from typing import Any

from app.data_models.evaluation_models import Tier2Result
from app.evals.llm_evaluation_managers import LLMJudgeEngine


async def evaluate_single_llm_judge(
    paper: str,
    review: str,
    execution_trace: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> Tier2Result:
    """Convenience function for single LLM judge evaluation.

    Args:
        paper: Paper content
        review: Generated review text
        execution_trace: Optional execution trace data
        config: Optional configuration override

    Returns:
        Tier2Result with LLM judge assessments

    Example:
        >>> result = await evaluate_single_llm_judge(
        ...     paper="This paper presents...",
        ...     review="The work demonstrates...",
        ...     execution_trace=trace_data,
        ... )
        >>> print(f"Overall score: {result.overall_score:.3f}")
    """
    config = config or {}
    execution_trace = execution_trace or {}

    engine = LLMJudgeEngine(config)
    return await engine.evaluate_comprehensive(paper, review, execution_trace)
