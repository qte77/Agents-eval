"""
This script serves as the main entry point for running a simple agent-based system.

It initializes the environment, loads configurations, and manages the execution of agents
based on user inputs or predefined settings. The script supports optional inclusion of
analyst and synthesizer agents, as well as integration with Pydantic AI streaming.

Modules:
- agent_simple_system: Provides agent environment setup and management utilities.
- login: Handles project-specific login functionality.
- utils: Loads configuration files and other utilities.

Functions:
- main: Orchestrates the setup and execution of the agent system.

Usage:
Run the script directly to start the agent system.
"""

from .utils.agent_simple_system import get_manager, run_manager, setup_agent_env
from .utils.login import login
from .utils.utils import load_config
from asyncio import run
from dotenv import load_dotenv
from logfire import span
from os import path
from rich.console import Console
from rich.theme import Theme
import weave


PROJECT_NAME = "rd-mas-example"
CONSOLE_THEME = Theme(
    {"info": "green", "debug": "bold", "warn": "magenta", "except": "red"}
)

console = Console(theme=CONSOLE_THEME)


@weave.op()
async def main(
    # TODO error Missing configuration for <typer.models.OptionInfo object at 0x7dc819510050>
    provider: str = "",  # Option(..., help="The inference provider to be used."),
    query: str = "",  # , help="The query to be processed by the agent."),
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    pydantic_ai_stream: bool = False,
    config_file: str = "config.json",
) -> None:
    """
    Main entry point for the application.

    Args:
        provider (str): The inference provider to be used.
        query (str): The query to be processed by the agent.
        include_analyst (bool): Whether to include the analyst in the process.
        include_synthesiser (bool): Whether to include the synthesiser in the process.
        pydantic_ai_stream (bool): Whether to use Pydantic AI streaming.
        config_file (str): Path to the configuration file.

    Returns:
        None
    """

    load_dotenv()  # TODO replace with pydantic-settings ?
    login(PROJECT_NAME)  # TODO enhance login, not every run?

    try:
        with span("main()"):
            config_path = path.join(path.dirname(__file__), config_file)
            config = load_config(config_path)

            if not provider:
                provider = input("Which inference provider to use? ")
            if not query:
                query = input("What would you like to research? ")

            agent_env = setup_agent_env(provider, query, config, console)
            manager = get_manager(
                agent_env.provider,
                agent_env.provider_config,
                agent_env.api_key,
                agent_env.prompts,
                include_analyst,
                include_synthesiser,
                console,
            )
            await run_manager(
                manager,
                agent_env.query,
                agent_env.provider,
                agent_env.usage_limits,
                pydantic_ai_stream,
                console,
            )

        print("exit:main.main()")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    run(main())
