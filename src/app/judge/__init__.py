"""
Judge evaluation framework.

Plugin-based evaluation system for multi-tiered agent assessment.
"""

from app.judge.agent import JudgeAgent
from app.judge.composite_scorer import CompositeScorer, EvaluationResults
from app.judge.performance_monitor import PerformanceMonitor
from app.judge.plugins.base import EvaluatorPlugin, PluginRegistry
from app.judge.trace_store import TraceStore

__all__ = [
    "EvaluatorPlugin",
    "PluginRegistry",
    "JudgeAgent",
    "TraceStore",
    "CompositeScorer",
    "EvaluationResults",
    "PerformanceMonitor",
]
