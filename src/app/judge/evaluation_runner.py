"""
Evaluation orchestration extracted from the main entry point.

Handles post-execution evaluation pipeline, baseline comparisons,
and interaction graph construction from trace data.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from app.data_models.evaluation_models import CompositeResult
from app.judge.baseline_comparison import compare_all
from app.judge.cc_trace_adapter import CCTraceAdapter
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.graph_builder import build_interaction_graph
from app.utils.log import logger


def build_graph_from_trace(execution_id: str | None) -> nx.DiGraph[str] | None:
    """Build interaction graph from execution trace data.

    Args:
        execution_id: Execution ID for trace retrieval.

    Returns:
        NetworkX DiGraph if trace data available, None otherwise.
    """
    if not execution_id:
        return None

    from app.judge.trace_processors import get_trace_collector

    trace_collector = get_trace_collector()
    execution_trace = trace_collector.load_trace(execution_id)

    if not execution_trace:
        return None

    graph = build_interaction_graph(execution_trace)
    logger.info(
        f"Built interaction graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    )
    return graph


async def run_evaluation_if_enabled(
    skip_eval: bool,
    paper_number: str | None,
    execution_id: str | None,
    cc_solo_dir: str | None = None,
    cc_teams_dir: str | None = None,
    chat_provider: str | None = None,
) -> CompositeResult | None:
    """Run evaluation pipeline after manager completes if enabled.

    Args:
        skip_eval: Whether to skip evaluation via CLI flag.
        paper_number: Paper number for PeerRead review (indicates ground truth availability).
        execution_id: Execution ID for trace retrieval.
        cc_solo_dir: Path to Claude Code solo artifacts directory for baseline comparison.
        cc_teams_dir: Path to Claude Code teams artifacts directory for baseline comparison.
        chat_provider: Active chat provider from agent system.

    Returns:
        CompositeResult from PydanticAI evaluation or None if skipped.
    """
    if skip_eval:
        logger.info("Evaluation skipped via --skip-eval flag")
        return None

    logger.info("Running evaluation pipeline...")
    pipeline = EvaluationPipeline(chat_provider=chat_provider)

    if not paper_number:
        logger.info("Skipping evaluation: no ground-truth reviews available")

    # Retrieve GraphTraceData from trace collector
    execution_trace = None
    if execution_id:
        from app.judge.trace_processors import get_trace_collector

        trace_collector = get_trace_collector()
        execution_trace = trace_collector.load_trace(execution_id)

        if execution_trace:
            logger.info(
                f"Loaded trace data: {len(execution_trace.agent_interactions)} interactions, "
                f"{len(execution_trace.tool_calls)} tool calls"
            )
        else:
            logger.warning(f"No trace data found for execution: {execution_id}")

    # TODO: Extract paper and review from run_manager result
    # For now, calling with minimal placeholder data to satisfy wiring requirement
    pydantic_result = await pipeline.evaluate_comprehensive(
        paper="",  # Placeholder - will be extracted from manager result
        review="",  # Placeholder - will be extracted from manager result
        execution_trace=execution_trace,
        reference_reviews=None,
    )

    # Run baseline comparisons if Claude Code directories provided
    await run_baseline_comparisons(pipeline, pydantic_result, cc_solo_dir, cc_teams_dir)

    return pydantic_result


async def run_baseline_comparisons(
    pipeline: EvaluationPipeline,
    pydantic_result: CompositeResult | None,
    cc_solo_dir: str | None,
    cc_teams_dir: str | None,
) -> None:
    """Run baseline comparisons against Claude Code solo and teams if directories provided.

    Args:
        pipeline: Evaluation pipeline instance.
        pydantic_result: PydanticAI evaluation result.
        cc_solo_dir: Path to Claude Code solo artifacts directory.
        cc_teams_dir: Path to Claude Code teams artifacts directory.
    """
    if not cc_solo_dir and not cc_teams_dir:
        return

    logger.info("Running baseline comparisons...")

    # Evaluate Claude Code solo baseline if directory provided
    cc_solo_result: CompositeResult | None = None
    if cc_solo_dir:
        try:
            logger.info(f"Evaluating Claude Code solo baseline from {cc_solo_dir}")
            adapter = CCTraceAdapter(Path(cc_solo_dir))
            cc_solo_trace = adapter.parse()
            cc_solo_result = await pipeline.evaluate_comprehensive(
                paper="",
                review="",
                execution_trace=cc_solo_trace,
                reference_reviews=None,
            )
            logger.info(f"Claude Code solo baseline score: {cc_solo_result.composite_score:.2f}")
        except Exception as e:
            logger.warning(f"Failed to evaluate Claude Code solo baseline: {e}")

    # Evaluate Claude Code teams baseline if directory provided
    cc_teams_result: CompositeResult | None = None
    if cc_teams_dir:
        try:
            logger.info(f"Evaluating Claude Code teams baseline from {cc_teams_dir}")
            adapter = CCTraceAdapter(Path(cc_teams_dir))
            cc_teams_trace = adapter.parse()
            cc_teams_result = await pipeline.evaluate_comprehensive(
                paper="",
                review="",
                execution_trace=cc_teams_trace,
                reference_reviews=None,
            )
            logger.info(f"Claude Code teams baseline score: {cc_teams_result.composite_score:.2f}")
        except Exception as e:
            logger.warning(f"Failed to evaluate Claude Code teams baseline: {e}")

    # Generate and log comparisons
    comparisons = compare_all(pydantic_result, cc_solo_result, cc_teams_result)
    for comparison in comparisons:
        logger.info(f"Baseline comparison: {comparison.summary}")
