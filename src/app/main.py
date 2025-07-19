"""
Main entry point for the Agents-eval application.

This module initializes the agentic system, loads configuration files,
handles user input, and orchestrates the multi-agent workflow using
asynchronous execution. It integrates logging, tracing, and authentication,
and supports both CLI and programmatic execution.
"""

from asyncio import run
from pathlib import Path
from sys import argv

from logfire import span
from weave import op

from src.app.__init__ import __version__
from src.app.agents.agent_system import get_manager, run_manager, setup_agent_env
from src.app.config.config_app import (
    CHAT_CONFIG_FILE,
    CHAT_DEFAULT_PROVIDER,
    EVAL_CONFIG_FILE,
    PROJECT_NAME,
)
from src.app.datamodels.app_models import AppEnv, ChatConfig, EvalConfig
from src.app.utils.error_messages import generic_exception
from src.app.utils.load_configs import load_config
from src.app.utils.log import logger
from src.app.utils.login import login
from src.app.utils.utils import parse_args


@op()
async def main(
    chat_provider: str = CHAT_DEFAULT_PROVIDER,
    query: str = "",
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    pydantic_ai_stream: bool = False,
    chat_config_file: str = CHAT_CONFIG_FILE,
) -> None:
    """
    Main entry point for the application.

    Args:
        chat_provider (str): The inference chat_provider to be used.
        query (str): The query to be processed by the agent.
        include_researcher (bool): Whether to include the researcher in the process.
        include_analyst (bool): Whether to include the analyst in the process.
        include_synthesiser (bool): Whether to include the synthesiser in the process.
        pydantic_ai_stream (bool): Whether to use Pydantic AI streaming.
        chat_config_file (str): Full path to the configuration file.

    Returns:
        None
    """

    logger.info(f"Starting app '{PROJECT_NAME}' v{__version__}")
    try:
        with span("main()"):
            if not chat_provider:
                chat_provider = input("Which inference chat_provider to use? ")
            if not query:
                query = input("What would you like to research? ")

            chat_config_path = Path(__file__).parent / CHAT_CONFIG_FILE
            eval_config_path = Path(__file__).parent / EVAL_CONFIG_FILE
            chat_config = load_config(chat_config_path, ChatConfig)
            eval_config = load_config(eval_config_path, EvalConfig)
            chat_env_config = AppEnv()
            agent_env = setup_agent_env(
                chat_provider, query, chat_config, chat_env_config
            )
            # TODO remove noqa and type ignore for unused variable
            metrics_and_weights = eval_config.metrics_and_weights  # noqa: F841  # type: ignore[reportUnusedVariable]

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


if __name__ == "__main__":
    args = parse_args(argv[1:])
    run(main(**args))
