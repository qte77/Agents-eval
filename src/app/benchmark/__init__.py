"""MAS composition sweep infrastructure for benchmarking.

This package provides automated benchmarking infrastructure to run the PydanticAI
MAS evaluation pipeline across configurable agent composition variations and
optionally invoke Claude Code in headless mode for baseline comparison.
"""

from app.benchmark.sweep_analysis import (
    CompositionStats,
    SweepAnalyzer,
    calculate_statistics,
    generate_markdown_summary,
)
from app.benchmark.sweep_config import (
    AgentComposition,
    SweepConfig,
    generate_all_compositions,
)
from app.benchmark.sweep_runner import SweepRunner, run_sweep

__all__ = [
    "AgentComposition",
    "SweepConfig",
    "generate_all_compositions",
    "SweepRunner",
    "run_sweep",
    "calculate_statistics",
    "CompositionStats",
    "SweepAnalyzer",
    "generate_markdown_summary",
]
