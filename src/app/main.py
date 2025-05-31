"""
This script serves as the main entry point for running a simple agent-based system.

It initializes the environment, loads configurations, and manages the execution of
agents based on user inputs or predefined settings. The script supports optional
inclusion of analyst and synthesizer agents, as well as integration with Pydantic
AI streaming.

Modules:
- agent_simple_system: Provides agent environment setup and management utilities.
- login: Handles project-specific login functionality.
- utils: Loads configuration files and other utilities.

Functions:
- main: Orchestrates the setup and execution of the agent system.

Usage:
Run the script directly to start the agent system.
"""

from asyncio import run
from os import path

import weave
from dotenv import load_dotenv
from logfire import span

from .config import CHAT_CONFIG_FILE, CHAT_DEFAULT_PROVIDER, PROJECT_NAME
from .utils.agent_simple_system import get_manager, run_manager, setup_agent_env
from .utils.log import logger
from .utils.login import login
from .utils.utils import load_config


@weave.op()
async def main(
    chat_provider: str = CHAT_DEFAULT_PROVIDER,  # help="The inference chat_provider to be used."),
    query: str = "",  # , help="The query to be processed by the agent."),
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

    load_dotenv()  # TODO replace with pydantic-settings ?
    login(PROJECT_NAME)  # TODO enhance login, not every run?

    try:
        with span("main()"):
            chat_config_path = path.join(path.dirname(__file__), chat_config_file)
            chat_config = load_config(chat_config_path)

            if not chat_provider:
                chat_provider = input("Which inference chat_provider to use? ")
            if not query:
                query = input("What would you like to research? ")

            # TODO remove
            logger.debug(f"{chat_config_path=}")
            logger.debug(f"{chat_provider=}")
            logger.debug(f"{chat_config.chat_provider=}")

            agent_env = setup_agent_env(chat_provider, query, chat_config)
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
        logger.exception(f"Aborting with: {e}")


if __name__ == "__main__":
    run(main())
