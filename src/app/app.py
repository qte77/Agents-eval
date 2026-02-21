"""
Main entry point for the Agents-eval application.

This module initializes the agentic system, loads configuration files,
handles user input, and orchestrates the multi-agent workflow using
asynchronous execution. It integrates logging, tracing, and authentication,
and supports both CLI and programmatic execution.

Evaluation orchestration is delegated to app.judge.evaluation_runner.
"""

from __future__ import annotations

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
from app.config.config_app import (
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
    PROJECT_NAME,
)
from app.data_models.app_models import AppEnv, ChatConfig
from app.data_utils.datasets_peerread import (
    download_peerread_dataset,
)
from app.judge.evaluation_runner import (
    build_graph_from_trace as _build_graph_from_trace,
)
from app.judge.evaluation_runner import (
    run_evaluation_if_enabled as _run_evaluation_if_enabled,
)
from app.judge.settings import JudgeSettings
from app.utils.error_messages import generic_exception
from app.utils.load_configs import load_config
from app.utils.log import logger
from app.utils.login import login
from app.utils.paths import resolve_config_path

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
) -> tuple[str, dict[str, str], Any]:
    """Execute agent system and return execution ID, prompts, and manager output.

    Args:
        All agent execution configuration parameters

    Returns:
        Tuple of (execution_id, prompts dict, manager_output)
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
            default_tmpl = "Generate a structured peer review for paper '{paper_id}'."
            paper_review_template = prompts.get("paper_review_query", default_tmpl)
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
) -> dict[str, Any] | None:
    """Prepare result dictionary for GUI usage.

    Args:
        composite_result: Evaluation result
        graph: Interaction graph
        execution_id: Execution trace ID for display on Evaluation page

    Returns:
        Dict with result, graph, and execution_id if available, None otherwise
    """
    # Return dict if we have either result or graph
    if composite_result is not None or graph is not None:
        return {
            "composite_result": composite_result,
            "graph": graph,
            # S8-F8.2: include execution_id for Evaluation Results page threading
            "execution_id": execution_id,
        }
    return None


@op()  # type: ignore[reportUntypedFunctionDecorator]
async def main(
    chat_provider: str = CHAT_DEFAULT_PROVIDER,
    query: str = "",
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    chat_config_file: str | Path | None = None,
    enable_review_tools: bool = True,
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
) -> dict[str, Any] | None:
    """Main entry point for the application.

    Args:
        See `--help`.

    Returns:
        Dictionary with 'composite_result' (CompositeResult) and 'graph' (nx.DiGraph)
        if evaluation runs successfully, None otherwise (CLI mode or download-only).
    """
    logger.info(f"Starting app '{PROJECT_NAME}' v{__version__} (engine={engine})")

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
            )

            # Run evaluation after manager completes
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
            )

            # Build interaction graph from trace data for visualization
            graph = _build_graph_from_trace(execution_id) if execution_id else None

            logger.info(f"Exiting app '{PROJECT_NAME}'")

            # Return data for GUI usage (include execution_id for Evaluation page)
            return _prepare_result_dict(composite_result, graph, execution_id)

    except Exception as e:
        msg = generic_exception(f"Aborting app '{PROJECT_NAME}' with: {e}")
        logger.exception(msg)
        raise Exception(msg) from e
