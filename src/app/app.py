"""
Main entry point for the Agents-eval application.

This module initializes the agentic system, loads configuration files,
handles user input, and orchestrates the multi-agent workflow using
asynchronous execution. It integrates logging, tracing, and authentication,
and supports both CLI and programmatic execution.
"""

from collections.abc import Callable
from pathlib import Path
from typing import TypeVar, cast

from logfire import span

# Reason: weave is optional - only import if available (requires WANDB_API_KEY)
try:
    from weave import op  # type: ignore[reportMissingImports]
except ImportError:
    # Fallback: no-op decorator when weave not installed
    from typing import Any

    _T = TypeVar("_T", bound=Callable[..., Any])

    def op() -> Callable[[_T], _T]:  # type: ignore[reportRedeclaration]
        """No-op decorator fallback when weave is unavailable."""

        def decorator(func: _T) -> _T:
            return func

        return decorator


from app.__init__ import __version__
from app.agents.agent_system import (
    get_manager,
    initialize_logfire_instrumentation_from_settings,
    run_manager,
    setup_agent_env,
)
from app.config.config_app import (
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
    PROJECT_NAME,
)
from app.data_models.app_models import AppEnv, ChatConfig
from app.data_models.evaluation_models import CompositeResult
from app.data_utils.datasets_peerread import (
    download_peerread_dataset,
)
from app.judge.baseline_comparison import compare_all
from app.judge.cc_trace_adapter import CCTraceAdapter
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.settings import JudgeSettings
from app.utils.error_messages import generic_exception
from app.utils.load_configs import load_config
from app.utils.log import logger
from app.utils.login import login
from app.utils.paths import resolve_config_path

CONFIG_FOLDER = "config"


async def _run_evaluation_if_enabled(
    skip_eval: bool,
    paper_number: str | None,
    execution_id: str | None,
    cc_solo_dir: str | None = None,
    cc_teams_dir: str | None = None,
    chat_provider: str | None = None,
) -> CompositeResult | None:
    """Run evaluation pipeline after manager completes if enabled.

    Args:
        skip_eval: Whether to skip evaluation via CLI flag
        paper_number: Paper number for PeerRead review (indicates ground truth availability)
        execution_id: Execution ID for trace retrieval
        cc_solo_dir: Path to Claude Code solo artifacts directory for baseline comparison
        cc_teams_dir: Path to Claude Code teams artifacts directory for baseline comparison
        chat_provider: Active chat provider from agent system (STORY-001)

    Returns:
        CompositeResult from PydanticAI evaluation or None if skipped
    """
    if skip_eval:
        logger.info("Evaluation skipped via --skip-eval flag")
        return None

    logger.info("Running evaluation pipeline...")
    pipeline = EvaluationPipeline(chat_provider=chat_provider)

    # Gracefully handle when no ground-truth reviews available
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
    await _run_baseline_comparisons(pipeline, pydantic_result, cc_solo_dir, cc_teams_dir)

    return pydantic_result


async def _run_baseline_comparisons(
    pipeline: EvaluationPipeline,
    pydantic_result: CompositeResult | None,
    cc_solo_dir: str | None,
    cc_teams_dir: str | None,
) -> None:
    """Run baseline comparisons against Claude Code solo and teams if directories provided.

    Args:
        pipeline: Evaluation pipeline instance
        pydantic_result: PydanticAI evaluation result
        cc_solo_dir: Path to Claude Code solo artifacts directory
        cc_teams_dir: Path to Claude Code teams artifacts directory
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


def _handle_download_mode(
    download_full: bool, download_samples: bool, max_samples: int | None
) -> bool:
    """Handle dataset download modes. Returns True if download was performed."""
    if download_full:
        logger.info("Full download-only mode activated")
        try:
            download_peerread_dataset(peerread_max_papers_per_sample_download=None)
            logger.info("Setup completed successfully. Exiting.")
            return True
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise

    if download_samples:
        logger.info(f"Downloading only {max_samples} samples")
        try:
            download_peerread_dataset(max_samples)
            logger.info("Setup completed successfully. Exiting.")
            return True
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise

    return False


def _initialize_instrumentation() -> None:
    """Initialize Logfire instrumentation if enabled in settings."""
    judge_settings = JudgeSettings()
    if judge_settings.logfire_enabled:
        initialize_logfire_instrumentation_from_settings(judge_settings)


def _prepare_query(
    paper_number: str | None, query: str, prompts: dict[str, str]
) -> tuple[str, bool]:
    """Prepare query and determine if review tools should be enabled."""
    if paper_number:
        if not query:
            default_tmpl = "Generate a structured peer review for paper '{paper_number}'."
            paper_review_template = prompts.get("paper_review_query", default_tmpl)
            query = paper_review_template.format(paper_number=paper_number)
        logger.info(f"Paper review mode enabled for paper {paper_number}")
        return query, True

    if not query:
        default_prompt = prompts.get("default_query", "What would you like to research? ")
        query = input(f"{default_prompt} ")

    return query, False


@op()  # type: ignore[reportUntypedFunctionDecorator]
async def main(
    chat_provider: str = CHAT_DEFAULT_PROVIDER,
    query: str = "",
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    pydantic_ai_stream: bool = False,
    chat_config_file: str | Path | None = None,
    enable_review_tools: bool = False,
    paper_number: str | None = None,
    skip_eval: bool = False,
    download_peerread_full_only: bool = False,
    download_peerread_samples_only: bool = False,
    peerread_max_papers_per_sample_download: int | None = 5,
    cc_solo_dir: str | None = None,
    cc_teams_dir: str | None = None,
    token_limit: int | None = None,
    # chat_config_path: str | Path,
) -> None:
    """
    Main entry point for the application.

    Args:
        See `--help`.

    Returns:
        None
    """
    logger.info(f"Starting app '{PROJECT_NAME}' v{__version__}")

    # Handle download-only mode (setup phase)
    if _handle_download_mode(
        download_peerread_full_only,
        download_peerread_samples_only,
        peerread_max_papers_per_sample_download,
    ):
        return

    try:
        if chat_config_file is None:
            chat_config_file = resolve_config_path(CHAT_CONFIG_FILE)
        logger.info(f"Chat config file: {chat_config_file}")

        with span("main()"):
            if not chat_provider:
                chat_provider = input("Which inference chat_provider to use? ")

            chat_config = load_config(chat_config_file, ChatConfig)
            prompts: dict[str, str] = cast(dict[str, str], chat_config.prompts)  # type: ignore[reportUnknownMemberType,reportAttributeAccessIssue]

            query, review_tools_enabled = _prepare_query(paper_number, query, prompts)
            enable_review_tools = enable_review_tools or review_tools_enabled

            chat_env_config = AppEnv()
            agent_env = setup_agent_env(
                chat_provider, query, chat_config, chat_env_config, token_limit
            )

            login(PROJECT_NAME, chat_env_config)
            _initialize_instrumentation()

            manager = get_manager(
                agent_env.provider,
                agent_env.provider_config,
                agent_env.api_key,
                agent_env.prompts,
                include_researcher,
                include_analyst,
                include_synthesiser,
                enable_review_tools,
            )
            execution_id = await run_manager(
                manager,
                agent_env.query,
                agent_env.provider,
                agent_env.usage_limits,
                pydantic_ai_stream,
            )

            # Run evaluation after manager completes
            await _run_evaluation_if_enabled(
                skip_eval, paper_number, execution_id, cc_solo_dir, cc_teams_dir, chat_provider
            )

            logger.info(f"Exiting app '{PROJECT_NAME}'")

    except Exception as e:
        msg = generic_exception(f"Aborting app '{PROJECT_NAME}' with: {e}")
        logger.exception(msg)
        raise Exception(msg) from e
