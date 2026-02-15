"""
Judge evaluation framework.

Plugin-based evaluation system for multi-tiered agent assessment.
"""

from app.judge.plugins.base import EvaluatorPlugin, PluginRegistry

__all__ = ["EvaluatorPlugin", "PluginRegistry"]
