"""
Evaluator plugins for multi-tiered assessment.

Provides plugin architecture for tier-ordered evaluation with
typed Pydantic models at all boundaries.
"""

from app.judge.plugins.base import EvaluatorPlugin, PluginRegistry

__all__ = ["EvaluatorPlugin", "PluginRegistry"]
