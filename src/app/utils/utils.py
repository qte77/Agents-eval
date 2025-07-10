"""
This module provides utility functions and context managers for handling configurations,
error handling, and setting up agent environments.

Functions:
    load_config(config_path: str) -> Config:
        Load and validate configuration from a JSON file.

    print_research_Result(summary: Dict, usage: Usage) -> None:
        Output structured summary of the research topic.

    error_handling_context(operation_name: str, console: Console = None):
        Context manager for handling errors during operations.

    setup_agent_env(config: Config, console: Console = None) -> AgentConfig:
        Set up the agent environment based on the provided configuration.
"""

from pydantic_ai.usage import Usage

from app.datamodels.app_models import ResearchSummary
from app.utils.log import logger


def log_research_result(summary: ResearchSummary, usage: Usage) -> None:
    """
    Prints the research summary and usage details in a formatted manner.

    Args:
        summary (Dict): A dictionary containing the research summary with keys 'topic',
            'key_points', 'key_points_explanation', and 'conclusion'.
        usage (Usage): An object containing usage details to be printed.
    """

    logger.info(f"\n=== Research Summary: {summary.topic} ===")
    logger.info("\nKey Points:")
    for i, point in enumerate(summary.key_points, 1):
        logger.info(f"{i}. {point}")
    logger.info("\nKey Points Explanation:")
    for i, point in enumerate(summary.key_points_explanation, 1):
        logger.info(f"{i}. {point}")
    logger.info(f"\nConclusion: {summary.conclusion}")
    logger.info(f"\nResponse structure: {list(dict(summary).keys())}")
    logger.info(usage)


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """
    Parse command line arguments into a dictionary.

    This function processes a list of command-line arguments,
    extracting recognized options and their values.
    Supported arguments include flags (e.g., --help, --include-researcher
    and key-value pairs (e.g., `--chat-provider=ollama`).
    If the `--help` flag is present, a list of available commands and their
    descriptions is printed, and an empty dictionary is returned.

    Recognized arguments as list[str]
    ```
        --help                   Display help information and exit.
        --version                Display version information.
        --chat-provider=<str>    Specify the chat provider to use.
        --query=<str>            Specify the query to process.
        --include-researcher     Include the researcher agent.
        --include-analyst        Include the analyst agent.
        --include-synthesiser    Include the synthesiser agent.
        --no-stream              Disable streaming output.
        --chat-config-file=<str> Specify the path to the chat configuration file.
    ```

    Returns:
        `dict[str, str | bool]`: A dictionary mapping argument names
        (with leading '--' removed and hyphens replaced by underscores)
        to their values (`str` for key-value pairs, `bool` for flags).
        Returns an empty dict if `--help` is specified.

    Example:
        >>> `parse_args(['--chat-provider=ollama', '--include-researcher'])`
        returns `{'chat_provider': 'ollama', 'include_researcher': True}`
    """

    commands = {
        "--help": "Display help information",
        "--version": "Display version information",
        "--chat-provider": "Specify the chat provider to use",
        "--query": "Specify the query to process",
        "--include-researcher": "Include the researcher agent",
        "--include-analyst": "Include the analyst agent",
        "--include-synthesiser": "Include the synthesiser agent",
        "--no-stream": "Disable streaming output",
        "--chat-config-file": "Specify the path to the chat configuration file",
    }
    parsed_args: dict[str, str | bool] = {}

    if "--help" in argv:
        print("Available commands:")
        for cmd, desc in commands.items():
            print(f"{cmd}: {desc}")
        return parsed_args

    for arg in argv:
        if arg.split("=", 1)[0] in commands.keys():
            key, value = arg.split("=", 1) if "=" in arg else (arg, True)
            key = key.lstrip("--").replace("-", "_")
            parsed_args[key] = value

    if parsed_args:
        logger.info(f"Used arguments: {parsed_args}")

    return parsed_args
