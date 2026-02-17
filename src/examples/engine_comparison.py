"""Engine comparison example: MAS vs Claude Code evaluation.

Purpose:
    Demonstrates how to compare evaluation scores between:
    - Multi-LLM MAS (PydanticAI agents)
    - Single-LLM MAS (baseline)
    - Claude Code headless (optional, requires CC artifacts)

    Uses CCTraceAdapter to load CC execution artifacts and feed them into
    the EvaluationPipeline for apples-to-apples comparison.

Prerequisites:
    For MAS evaluation: API key in .env (or use tiers_enabled=[1, 3]).
    For CC comparison: Collect CC artifacts first using the scripts:
        scripts/collect-cc-traces/collect-cc-solo.sh   # solo mode
        scripts/collect-cc-traces/collect-cc-teams.sh  # teams mode
    Artifacts are stored in ~/.claude/teams/ and ~/.claude/tasks/ during
    interactive sessions, or parsed from raw_stream.jsonl in headless mode.

Usage:
    uv run python src/examples/engine_comparison.py
"""

import asyncio
from pathlib import Path

from app.data_models.evaluation_models import CompositeResult, GraphTraceData
from app.judge.cc_trace_adapter import CCTraceAdapter
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.settings import JudgeSettings
from app.utils.log import logger

# Synthetic MAS trace representing a 3-agent review workflow
_MAS_TRACE = GraphTraceData(
    execution_id="mas-multi-llm-001",
    agent_interactions=[
        {"from": "orchestrator", "to": "researcher", "message": "Analyze paper"},
        {"from": "researcher", "to": "analyst", "message": "Pass findings"},
        {"from": "analyst", "to": "synthesiser", "message": "Draft review"},
    ],
    tool_calls=[
        {"tool": "search", "agent": "researcher", "success": True},
        {"tool": "extract", "agent": "analyst", "success": True},
        {"tool": "write", "agent": "synthesiser", "success": True},
    ],
    timing_data={"total_seconds": 6.5},
    coordination_events=[
        {"type": "delegation", "from": "orchestrator", "to": "researcher"},
    ],
)

# Synthetic single-agent baseline trace
_BASELINE_TRACE = GraphTraceData(
    execution_id="mas-single-llm-001",
    agent_interactions=[],  # No multi-agent coordination
    tool_calls=[
        {"tool": "search", "agent": "single_agent", "success": True},
        {"tool": "write", "agent": "single_agent", "success": True},
    ],
    timing_data={"total_seconds": 4.2},
    coordination_events=[],
)

_PAPER_ABSTRACT = (
    "We propose a novel self-supervised learning approach that achieves state-of-the-art "
    "performance on multiple benchmarks without labeled data. Our method uses contrastive "
    "learning with data augmentation strategies tailored for scientific text."
)

_AGENT_REVIEW = (
    "This paper presents a strong contribution to self-supervised learning for NLP. "
    "The empirical results are impressive across multiple benchmarks. "
    "The ablation studies clearly justify the design choices. "
    "Recommended for acceptance with minor revisions."
)

_REFERENCE_REVIEW = (
    "Solid paper with well-executed experiments. The method is clearly described "
    "and the results are competitive. The theoretical analysis could be strengthened."
)


async def evaluate_mas(trace: GraphTraceData, label: str) -> CompositeResult:
    """Run Tier 1 + Tier 3 evaluation for a given execution trace.

    Args:
        trace: GraphTraceData from MAS execution.
        label: Human-readable label for logging.

    Returns:
        CompositeResult with composite_score and recommendation.
    """
    settings = JudgeSettings(tiers_enabled=[1, 3])  # skip Tier 2 for example
    pipeline = EvaluationPipeline(settings=settings)

    result = await pipeline.evaluate_comprehensive(
        paper=_PAPER_ABSTRACT,
        review=_AGENT_REVIEW,
        execution_trace=trace,
        reference_reviews=[_REFERENCE_REVIEW],
    )
    logger.info(f"{label}: score={result.composite_score:.3f}, rec={result.recommendation}")
    return result


def load_cc_trace(artifacts_dir: Path) -> GraphTraceData | None:
    """Load CC execution artifacts into GraphTraceData.

    Args:
        artifacts_dir: Path to CC artifact directory (teams or solo mode).
            Teams mode: contains config.json with 'members' array.
            Solo mode: contains metadata.json + tool_calls.jsonl.

    Returns:
        GraphTraceData parsed from artifacts, or None if directory missing.
    """
    if not artifacts_dir.exists():
        logger.warning(f"CC artifacts not found at {artifacts_dir}. Skipping CC comparison.")
        return None

    try:
        adapter = CCTraceAdapter(artifacts_dir)
        trace = adapter.parse()
        logger.info(f"Loaded CC trace (mode={adapter.mode}): {trace.execution_id}")
        return trace
    except ValueError as e:
        logger.error(f"Failed to parse CC artifacts: {e}")
        return None


async def run_example() -> dict[str, CompositeResult]:
    """Compare MAS multi-agent, MAS single-agent, and optionally CC evaluation scores.

    Returns:
        Dict mapping engine label to CompositeResult.
    """
    results: dict[str, CompositeResult] = {}

    # Multi-LLM MAS (the evaluation target)
    results["MAS-MultiLLM"] = await evaluate_mas(_MAS_TRACE, label="MAS-MultiLLM")

    # Single-LLM MAS baseline
    results["MAS-SingleLLM"] = await evaluate_mas(_BASELINE_TRACE, label="MAS-SingleLLM")

    # Optional: Claude Code comparison (requires prior artifact collection)
    cc_artifacts_dir = Path.home() / ".claude" / "teams" / "evaluation-run"
    cc_trace = load_cc_trace(cc_artifacts_dir)
    if cc_trace is not None:
        results["ClaudeCode"] = await evaluate_mas(cc_trace, label="ClaudeCode")

    return results


if __name__ == "__main__":
    scores = asyncio.run(run_example())
    print("\n=== Engine Comparison Results ===")
    for engine, result in scores.items():
        print(f"  {engine:20s}  score={result.composite_score:.3f}  rec={result.recommendation}")
