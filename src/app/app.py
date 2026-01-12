"""
Main entry point for the Agents-eval application.

This module initializes the agentic system, loads configuration files,
handles user input, and orchestrates the multi-agent workflow using
asynchronous execution. It integrates logging, tracing, and authentication,
and supports both CLI and programmatic execution.
"""

from pathlib import Path
from typing import cast

from logfire import span
from weave import op

from app.__init__ import __version__
from app.agents.agent_system import get_manager, run_manager, setup_agent_env
from app.config.config_app import (
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
    PROJECT_NAME,
)
from app.data_models.app_models import AppEnv, ChatConfig
from app.data_utils.datasets_peerread import (
    download_peerread_dataset,
)
from app.utils.error_messages import generic_exception
from app.utils.load_configs import load_config
from app.utils.log import logger
from app.utils.login import login
from app.utils.paths import resolve_config_path

CONFIG_FOLDER = "config"


@op()
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
    download_peerread_full_only: bool = False,
    download_peerread_samples_only: bool = False,
    peerread_max_papers_per_sample_download: int | None = 5,
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
    if download_peerread_full_only:
        logger.info("Full download-only mode activated")
        try:
            download_peerread_dataset(peerread_max_papers_per_sample_download=None)
            logger.info("Setup completed successfully. Exiting.")
            return
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise

    if download_peerread_samples_only:
        logger.info(f"Downloading only {peerread_max_papers_per_sample_download} samples")
        try:
            download_peerread_dataset(peerread_max_papers_per_sample_download)
            logger.info("Setup completed successfully. Exiting.")
            return
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise

    try:
        if chat_config_file is None:
            chat_config_file = resolve_config_path(CHAT_CONFIG_FILE)
        logger.info(f"Chat config file: {chat_config_file}")
        with span("main()"):
            if not chat_provider:
                chat_provider = input("Which inference chat_provider to use? ")

            chat_config = load_config(chat_config_file, ChatConfig)
            # FIXME remove type ignore and cast and properly type
            prompts: dict[str, str] = cast(dict[str, str], chat_config.prompts)  # type: ignore[reportUnknownMemberType,reportAttributeAccessIssue]

            # Handle paper review workflow
            if paper_number:
                enable_review_tools = True
                if not query:
                    paper_review_template = prompts.get(
                        "paper_review_query",
                        "Generate a structured peer review for paper '{paper_number}' from PeerRead dataset.",
                    )
                    query = paper_review_template.format(paper_number=paper_number)
                logger.info(f"Paper review mode enabled for paper {paper_number}")
            elif not query:
                # Prompt user for input when no query is provided
                default_prompt = prompts.get("default_query", "What would you like to research? ")
                query = input(f"{default_prompt} ")
            chat_env_config = AppEnv()
            agent_env = setup_agent_env(chat_provider, query, chat_config, chat_env_config)

            # FIXME enhance login, not every run?
            login(PROJECT_NAME, chat_env_config)

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
            await run_manager(
                manager,
                agent_env.query,
                agent_env.provider,
                agent_env.usage_limits,
                pydantic_ai_stream,
            )
            logger.info(f"Exiting app '{PROJECT_NAME}'")

    except Exception as e:
        msg = generic_exception(f"Aborting app '{PROJECT_NAME}' with: {e}")
        logger.exception(msg)
        raise Exception(msg) from e
