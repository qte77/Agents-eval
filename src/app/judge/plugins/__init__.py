"""
Evaluator plugins for multi-tiered assessment.

Provides plugin architecture for tier-ordered evaluation with
typed Pydantic models at all boundaries.
"""

from app.judge.plugins.base import EvaluatorPlugin, PluginRegistry
from app.judge.plugins.graph_metrics import GraphEvaluatorPlugin
from app.judge.plugins.llm_judge import LLMJudgePlugin
from app.judge.plugins.traditional import TraditionalMetricsPlugin

__all__ = [
    "EvaluatorPlugin",
    "PluginRegistry",
    "TraditionalMetricsPlugin",
    "LLMJudgePlugin",
    "GraphEvaluatorPlugin",
]
