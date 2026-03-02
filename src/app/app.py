"""
Main entry point for the Agents-eval application.

This module initializes the agentic system, loads configuration files,
handles user input, and orchestrates the multi-agent workflow using
asynchronous execution. It integrates logging, tracing, and authentication,
and supports both CLI and programmatic execution.

Evaluation orchestration is delegated to app.judge.evaluation_runner.
"""

from __future__ import annotations

import uuid as _uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

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
from app.config.app_env import AppEnv
from app.config.config_app import (
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
    DEFAULT_REVIEW_PROMPT_TEMPLATE,
    PROJECT_NAME,
)
from app.config.judge_settings import JudgeSettings
from app.data_models.app_models import ChatConfig
from app.data_utils.datasets_peerread import (
    download_peerread_dataset,
)
from app.judge.evaluation_runner import (
    build_graph_from_trace as _build_graph_from_trace,
)
from app.judge.evaluation_runner import (
    run_evaluation_if_enabled as _run_evaluation_if_enabled,
)
from app.utils.error_messages import generic_exception
from app.utils.load_configs import load_config
from app.utils.log import logger
from app.utils.login import login
from app.utils.paths import resolve_config_path
from app.utils.run_context import RunContext, get_active_run_context, set_active_run_context

CONFIG_FOLDER = "config"


async def _run_agent_execution(
    chat_config_file: str | Path,
    chat_provider: str,
    query: str,
    paper_id: str | None,
    enable_review_tools: bool,
    include_researcher: bool,
    include_analyst: bool,
    include_synthesiser: bool,
    token_limit: int | None,
    execution_id: str | None = None,
) -> tuple[str, dict[str, str], Any]:
    """Execute agent system and return execution ID, prompts, and manager output.

    Args:
        chat_config_file: Path to chat configuration file.
        chat_provider: LLM provider name.
        query: User query string.
        paper_id: Optional PeerRead paper ID.
        enable_review_tools: Whether to enable review tools.
        include_researcher: Whether to include researcher agent.
        include_analyst: Whether to include analyst agent.
        include_synthesiser: Whether to include synthesiser agent.
        token_limit: Optional token limit override.
        execution_id: Optional pre-generated execution ID forwarded to run_manager.

    Returns:
        Tuple of (execution_id, prompts dict, manager_output).
    """
    chat_config = load_config(chat_config_file, ChatConfig)
    prompts: dict[str, str] = cast(dict[str, str], chat_config.prompts)  # type: ignore[reportUnknownMemberType]

    query, review_tools_enabled = _prepare_query(paper_id, query, prompts)
    enable_review_tools = enable_review_tools or review_tools_enabled

    chat_env_config = AppEnv()
    agent_env = setup_agent_env(chat_provider, query, chat_config, chat_env_config, token_limit)

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
    execution_id, manager_output = await run_manager(
        manager,
        agent_env.query,
        agent_env.provider,
        agent_env.usage_limits,
        execution_id=execution_id,
    )

    return execution_id, prompts, manager_output


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


def _prepare_query(paper_id: str | None, query: str, prompts: dict[str, str]) -> tuple[str, bool]:
    """Prepare query and determine if review tools should be enabled."""
    if paper_id:
        if not query:
            paper_review_template = prompts.get(
                "paper_review_query", DEFAULT_REVIEW_PROMPT_TEMPLATE
            )
            query = paper_review_template.format(paper_id=paper_id)
        logger.info(f"Paper review mode enabled for paper {paper_id}")
        return query, True

    if not query:
        default_prompt = prompts.get("default_query", "What would you like to research? ")
        query = input(f"{default_prompt} ")

    return query, False


def _prepare_result_dict(
    composite_result: Any | None,
    graph: Any | None,
    execution_id: str | None = None,
    run_context: RunContext | None = None,
) -> dict[str, Any] | None:
    """Prepare result dictionary for GUI usage.

    Args:
        composite_result: Evaluation result
        graph: Interaction graph
        execution_id: Execution trace ID for display on Evaluation page
        run_context: Optional per-run context for artifact paths

    Returns:
        Dict with result, graph, execution_id, and run_context if available, None otherwise
    """
    # Return dict if we have either result or graph
    if composite_result is not None or graph is not None:
        return {
            "composite_result": composite_result,
            "graph": graph,
            # S8-F8.2: include execution_id for Evaluation Results page threading
            "execution_id": execution_id,
            "run_context": run_context,
        }
    return None


@op()  # type: ignore[reportUntypedFunctionDecorator]
def _extract_cc_artifacts(cc_result: Any) -> tuple[str, Any]:
    """Extract execution ID and graph from a CC engine result.

    Args:
        cc_result: CCResult from solo or teams execution.

    Returns:
        Tuple of (execution_id, interaction_graph).
    """
    from app.engines.cc_engine import cc_result_to_graph_trace
    from app.judge.graph_builder import build_interaction_graph

    graph_trace = cc_result_to_graph_trace(cc_result)
    return cc_result.execution_id, build_interaction_graph(graph_trace)


async def _run_cc_engine_path(
    cc_result: Any,
    skip_eval: bool,
    paper_id: str | None,
    cc_solo_dir: str | None,
    cc_teams_dir: str | None,
    cc_teams_tasks_dir: str | None,
    chat_provider: str,
    judge_settings: JudgeSettings | None,
    cc_teams: bool = False,
    run_dir: Path | None = None,
) -> tuple[Any, Any, str | None]:
    """Execute CC engine path: extract artifacts, evaluate, set engine_type.

    Args:
        cc_result: CCResult from solo or teams execution.
        skip_eval: Whether to skip evaluation.
        paper_id: Optional PeerRead paper ID.
        cc_solo_dir: CC solo trace directory.
        cc_teams_dir: CC teams trace directory.
        cc_teams_tasks_dir: CC teams tasks directory.
        chat_provider: LLM provider name.
        judge_settings: Optional judge settings.
        cc_teams: Whether CC was run in teams mode (source of truth for engine_type).
        run_dir: Per-run output directory from up-front RunContext.

    Returns:
        Tuple of (composite_result, graph, execution_id).
    """
    from app.engines.cc_engine import extract_cc_review_text

    execution_id, graph = _extract_cc_artifacts(cc_result)

    engine_type = "cc_teams" if cc_teams else "cc_solo"

    # S10-AC2: extract review text from CC output for evaluation
    cc_review_text = extract_cc_review_text(cc_result)
    composite_result = await _run_evaluation_if_enabled(
        skip_eval,
        paper_id,
        execution_id,
        cc_solo_dir,
        cc_teams_dir,
        cc_teams_tasks_dir,
        chat_provider,
        judge_settings,
        manager_output=None,
        review_text=cc_review_text,
        run_dir=run_dir,
    )
    # S12-STORY-002: set engine_type from explicit cc_teams flag (not team_artifacts)
    if composite_result is not None:
        composite_result.engine_type = engine_type
    return composite_result, graph, execution_id


async def _run_mas_engine_path(
    chat_config_file: str | Path,
    chat_provider: str,
    query: str,
    paper_id: str | None,
    enable_review_tools: bool,
    include_researcher: bool,
    include_analyst: bool,
    include_synthesiser: bool,
    token_limit: int | None,
    skip_eval: bool,
    cc_solo_dir: str | None,
    cc_teams_dir: str | None,
    cc_teams_tasks_dir: str | None,
    judge_settings: JudgeSettings | None,
    execution_id: str | None = None,
    run_dir: Path | None = None,
) -> tuple[Any, Any, str | None]:
    """Execute MAS engine path: run agents, evaluate, build graph.

    Args:
        chat_config_file: Path to chat configuration file.
        chat_provider: LLM provider name.
        query: User query string.
        paper_id: Optional PeerRead paper ID.
        enable_review_tools: Whether to enable review tools.
        include_researcher: Whether to include researcher agent.
        include_analyst: Whether to include analyst agent.
        include_synthesiser: Whether to include synthesiser agent.
        token_limit: Optional token limit override.
        skip_eval: Whether to skip evaluation.
        cc_solo_dir: CC solo trace directory.
        cc_teams_dir: CC teams trace directory.
        cc_teams_tasks_dir: CC teams tasks directory.
        judge_settings: Optional judge settings.
        execution_id: Pre-generated execution ID from main().
        run_dir: Per-run output directory from up-front RunContext.

    Returns:
        Tuple of (composite_result, graph, execution_id).
    """
    if not chat_provider:
        chat_provider = input("Which inference chat_provider to use? ")

    execution_id, _, manager_output = await _run_agent_execution(
        chat_config_file,
        chat_provider,
        query,
        paper_id,
        enable_review_tools,
        include_researcher,
        include_analyst,
        include_synthesiser,
        token_limit,
        execution_id=execution_id,
    )

    composite_result = await _run_evaluation_if_enabled(
        skip_eval,
        paper_id,
        execution_id,
        cc_solo_dir,
        cc_teams_dir,
        cc_teams_tasks_dir,
        chat_provider,
        judge_settings,
        manager_output,
        run_dir=run_dir,
    )

    graph = _build_graph_from_trace(execution_id) if execution_id else None
    return composite_result, graph, execution_id


async def main(
    chat_provider: str = CHAT_DEFAULT_PROVIDER,
    query: str = "",
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    chat_config_file: str | Path | None = None,
    enable_review_tools: bool = False,
    paper_id: str | None = None,
    skip_eval: bool = False,
    download_peerread_full_only: bool = False,
    download_peerread_samples_only: bool = False,
    peerread_max_papers_per_sample_download: int | None = 5,
    cc_solo_dir: str | None = None,
    cc_teams_dir: str | None = None,
    cc_teams_tasks_dir: str | None = None,
    token_limit: int | None = None,
    judge_settings: JudgeSettings | None = None,
    engine: str = "mas",
    cc_result: Any | None = None,
    cc_teams: bool = False,
) -> dict[str, Any] | None:
    """Main entry point for the application.

    Returns:
        Dictionary with 'composite_result' (CompositeResult) and 'graph' (nx.DiGraph)
        if evaluation runs successfully, None otherwise (CLI mode or download-only).
    """
    logger.info(f"Starting app '{PROJECT_NAME}' v{__version__} (engine={engine})")

    if _handle_download_mode(
        download_peerread_full_only,
        download_peerread_samples_only,
        peerread_max_papers_per_sample_download,
    ):
        return None

    try:
        if chat_config_file is None:
            chat_config_file = resolve_config_path(CHAT_CONFIG_FILE)
        logger.info(f"Chat config file: {chat_config_file}")

        with span("main()"):
            # Generate execution_id up-front so RunContext is active before engine runs
            execution_id = f"exec_{_uuid.uuid4().hex[:12]}"
            engine_type = (
                "cc_teams"
                if (engine == "cc" and cc_teams)
                else ("cc_solo" if engine == "cc" else "mas")
            )
            run_ctx = RunContext.create(
                engine_type=engine_type,
                paper_id=paper_id or "unknown",
                execution_id=execution_id,
            )
            set_active_run_context(run_ctx)

            # S10-F1: CC engine branch — skip MAS, use CC result directly
            if engine == "cc" and cc_result is not None:
                composite_result, graph, execution_id = await _run_cc_engine_path(
                    cc_result,
                    skip_eval,
                    paper_id,
                    cc_solo_dir,
                    cc_teams_dir,
                    cc_teams_tasks_dir,
                    chat_provider,
                    judge_settings,
                    cc_teams=cc_teams,
                    run_dir=run_ctx.run_dir,
                )
            else:
                composite_result, graph, execution_id = await _run_mas_engine_path(
                    chat_config_file,
                    chat_provider,
                    query,
                    paper_id,
                    enable_review_tools,
                    include_researcher,
                    include_analyst,
                    include_synthesiser,
                    token_limit,
                    skip_eval,
                    cc_solo_dir,
                    cc_teams_dir,
                    cc_teams_tasks_dir,
                    judge_settings,
                    execution_id=execution_id,
                    run_dir=run_ctx.run_dir,
                )

            logger.info(f"Exiting app '{PROJECT_NAME}'")
            return _prepare_result_dict(
                composite_result, graph, execution_id, run_context=get_active_run_context()
            )

    except Exception as e:
        msg = generic_exception(f"Aborting app '{PROJECT_NAME}' with: {e}")
        logger.exception(msg)
        raise Exception(msg) from e
    finally:
        set_active_run_context(None)
