"""
Evaluation orchestration extracted from the main entry point.

Handles post-execution evaluation pipeline, baseline comparisons,
and interaction graph construction from trace data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

from app.config.judge_settings import JudgeSettings
from app.data_models.evaluation_models import CompositeResult
from app.data_utils.datasets_peerread import PeerReadLoader
from app.judge.baseline_comparison import compare_all
from app.judge.cc_trace_adapter import CCTraceAdapter
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.graph_builder import build_interaction_graph
from app.utils.artifact_registry import get_artifact_registry
from app.utils.log import logger


def _load_reference_reviews(paper_id: str | None) -> list[str] | None:
    """Load ground-truth reference reviews from PeerRead for a given paper.

    Args:
        paper_id: PeerRead paper identifier, or None.

    Returns:
        List of review comment strings if paper found, empty list if paper has
        no reviews, None if paper_id is None or paper not found.
    """
    if not paper_id:
        return None

    loader = PeerReadLoader()
    paper = loader.get_paper_by_id(paper_id)
    if paper is None:
        return None

    return [r.comments for r in paper.reviews]


def _extract_paper_and_review_content(manager_output: Any) -> tuple[str, str]:
    """Extract paper and review content from manager output.

    Args:
        manager_output: Manager result output containing ReviewGenerationResult (optional).

    Returns:
        Tuple of (paper_content, review_text).
    """
    paper_content = ""
    review_text = ""

    if manager_output is None:
        return paper_content, review_text

    from app.data_models.peerread_models import ReviewGenerationResult

    # Check if manager_output is ReviewGenerationResult
    if not isinstance(manager_output, ReviewGenerationResult):
        return paper_content, review_text

    # Extract review text from ReviewGenerationResult
    review_text = manager_output.review.comments

    # Load paper content (PDF → abstract fallback)
    paper_content = _load_paper_content(manager_output.paper_id)

    return paper_content, review_text


def _load_paper_content(paper_id: str) -> str:
    """Load paper content from PeerRead for any engine path.

    Tries parsed PDF first, then falls back to abstract.

    Args:
        paper_id: PeerRead paper identifier.

    Returns:
        Paper content string, or empty string if not found.
    """
    loader = PeerReadLoader()
    parsed = loader.load_parsed_pdf_content(paper_id)
    if parsed:
        return parsed

    paper = loader.get_paper_by_id(paper_id)
    if paper:
        return paper.abstract

    return ""


def _resolve_execution_trace(execution_trace: Any, execution_id: str | None) -> Any:
    """Resolve execution trace: use provided override or load from SQLite.

    Args:
        execution_trace: Pre-built GraphTraceData (CC path) or None.
        execution_id: Execution ID for SQLite lookup (MAS path).

    Returns:
        GraphTraceData if available, None otherwise.
    """
    if execution_trace is not None:
        return execution_trace

    if not execution_id:
        return None

    from app.judge.trace_processors import get_trace_collector

    trace_collector = get_trace_collector()
    loaded_trace = trace_collector.load_trace(execution_id)

    if loaded_trace:
        logger.info(
            f"Loaded trace data: {len(loaded_trace.agent_interactions)} interactions, "
            f"{len(loaded_trace.tool_calls)} tool calls"
        )
    else:
        logger.warning(f"No trace data found for execution: {execution_id}")

    return loaded_trace


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
    paper_id: str | None,
    execution_id: str | None,
    cc_solo_dir: str | None = None,
    cc_teams_dir: str | None = None,
    cc_teams_tasks_dir: str | None = None,
    chat_provider: str | None = None,
    chat_model: str | None = None,
    judge_settings: JudgeSettings | None = None,
    manager_output: Any = None,
    review_text: str | None = None,
    run_dir: Path | None = None,
    execution_trace: Any = None,
    engine_type: str = "mas",
) -> CompositeResult | None:
    """Run evaluation pipeline after manager completes if enabled.

    Args:
        skip_eval: Whether to skip evaluation via CLI flag.
        paper_id: Paper ID for PeerRead review (indicates ground truth availability).
        execution_id: Execution ID for trace retrieval.
        cc_solo_dir: Path to Claude Code solo artifacts directory for baseline comparison.
        cc_teams_dir: Path to Claude Code teams artifacts directory for baseline comparison.
        cc_teams_tasks_dir: Path to Claude Code teams tasks directory (optional,
                           auto-discovered if not specified).
        chat_provider: Active chat provider from agent system.
        chat_model: Active chat model from agent system. Forwarded to LLMJudgeEngine
            for model inheritance when tier2_provider=auto.
        judge_settings: Optional JudgeSettings override from GUI or programmatic calls.
        manager_output: Manager result output containing ReviewGenerationResult (optional).
        review_text: Pre-extracted review text (e.g. from CC engine). When provided,
            overrides text extraction from manager_output.
        run_dir: Optional per-run output directory. When provided, evaluation results
            are persisted to evaluation.json in this directory.
        execution_trace: Optional pre-built GraphTraceData (e.g. from CC engine).
            When provided, skips SQLite trace lookup. When None, falls back to
            trace_collector.load_trace() (existing MAS behavior).
        engine_type: Source engine identifier ('mas', 'cc_solo', or 'cc_teams').
            Set on CompositeResult before persisting to evaluation.json.

    Returns:
        CompositeResult from PydanticAI evaluation or None if skipped.
    """
    if skip_eval:
        logger.info("Evaluation skipped via --skip-eval flag")
        return None

    logger.info("Running evaluation pipeline...")
    pipeline = EvaluationPipeline(
        settings=judge_settings, chat_provider=chat_provider, chat_model=chat_model
    )

    if not paper_id:
        logger.info("Skipping evaluation: no ground-truth reviews available")

    execution_trace = _resolve_execution_trace(execution_trace, execution_id)

    # Extract paper and review content from manager_output (or use override)
    paper_content, extracted_review = _extract_paper_and_review_content(manager_output)

    # CC paper content fallback: when manager_output is None (CC path) but paper_id
    # is available, load paper content directly from PeerRead cache
    if not paper_content and paper_id:
        paper_content = _load_paper_content(paper_id)

    # S10-F1: CC engine passes review_text directly, overriding extraction
    if review_text is None:
        review_text = extracted_review

    # S10-F1: load reference reviews from PeerRead for all modes (fixes hardcoded None)
    reference_reviews = _load_reference_reviews(paper_id)

    pydantic_result = await pipeline.evaluate_comprehensive(
        paper=paper_content,
        review=review_text,
        execution_trace=execution_trace,
        reference_reviews=reference_reviews,
    )

    # Set engine_type before persisting so evaluation.json has the correct value
    if pydantic_result is not None:  # type: ignore[reportUnnecessaryComparison]
        pydantic_result.engine_type = engine_type

    # Persist evaluation results to run directory
    if run_dir is not None:
        eval_path = run_dir / "evaluation.json"
        eval_path.write_text(json.dumps(pydantic_result.model_dump(), indent=2), encoding="utf-8")
        get_artifact_registry().register("Evaluation", eval_path)
        logger.info(f"Evaluation results written to {eval_path}")

    # Run baseline comparisons if Claude Code directories provided
    await run_baseline_comparisons(
        pipeline, pydantic_result, cc_solo_dir, cc_teams_dir, cc_teams_tasks_dir
    )

    return pydantic_result


async def run_baseline_comparisons(
    pipeline: EvaluationPipeline,
    pydantic_result: CompositeResult | None,
    cc_solo_dir: str | None,
    cc_teams_dir: str | None,
    cc_teams_tasks_dir: str | None,
) -> None:
    """Run baseline comparisons against Claude Code solo and teams if directories provided.

    Args:
        pipeline: Evaluation pipeline instance.
        pydantic_result: PydanticAI evaluation result.
        cc_solo_dir: Path to Claude Code solo artifacts directory.
        cc_teams_dir: Path to Claude Code teams artifacts directory.
        cc_teams_tasks_dir: Path to Claude Code teams tasks directory (optional,
                           auto-discovered if not specified).
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
            # Pass optional tasks_dir if provided, otherwise let adapter auto-discover
            tasks_path = Path(cc_teams_tasks_dir) if cc_teams_tasks_dir else None
            adapter = CCTraceAdapter(Path(cc_teams_dir), tasks_dir=tasks_path)
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
