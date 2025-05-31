"""
This script serves as the entry point for the application, utilizing Typer for CLI
commands.

Commands:
- main: Executes the application with configurable options such as provider, query,
    and additional flags.
"""

from asyncio import run

from .main import main as start_app

# from typer import Option, Typer


# TODO back to argparse,  Typer w/o native async support
# app = Typer()


# @app.callback()
def callback():
    """Global vars"""
    pass


# @app.command()
async def main(
    provider: str = "",  # Option("", help="The inference provider to be used."),
    query: str = "",  # Option("", help="The query to be processed by the agent."),
    include_researcher: bool = True,
    include_analyst: bool = True,
    include_synthesiser: bool = False,
    pydantic_ai_stream: bool = False,
    config_file: str = "config.json",
) -> None:
    """
    Main entry point for the application.

    Args:
        provider (str): The inference provider to be used.
        query (str): The query to be processed by the agent.
        include_analyst (bool): Whether to include the analyst in processing.
        include_synthesiser (bool): Whether to include the synthesiser in processing.
        pydantic_ai_stream (bool): Whether to enable Pydantic AI streaming.
        config_file (str): Path to the configuration file.

    Returns:
        None
    """
    await start_app(
        provider,
        query,
        include_researcher,
        include_analyst,
        include_synthesiser,
        pydantic_ai_stream,
        config_file,
    )


if __name__ == "__main__":
    run(main())
