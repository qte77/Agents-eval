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

from contextlib import contextmanager

from logfire import error, span
from openai import APIConnectionError, RateLimitError, UnprocessableEntityError
from pydantic_ai.exceptions import (
    ModelHTTPError,
    UnexpectedModelBehavior,
    UsageLimitExceeded,
)
from pydantic_ai.usage import Usage

from .data_models import ResearchSummary
from .log import logger


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
    """Parse command line arguments."""

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


@contextmanager
def error_handling_context(operation_name: str):
    """
    Context manager for handling errors during an operation and logging them
        appropriately.
    Args:
        operation_name (str): The name of the operation being performed.
    Yields:
        None
    Raises:
        Various exceptions based on the error encountered during the operation.
    """

    reason: str | None = None
    msg: Exception | None = None
    try:
        with span(operation_name):
            yield
    except APIConnectionError as e:
        reason, msg = "API connection error", e
    except ModelHTTPError as e:
        reason, msg = "Model error", e
    except RateLimitError as e:
        reason, msg = "Rate limit exceeded", e
    except (UnexpectedModelBehavior, UnprocessableEntityError) as e:
        reason, msg = "Model returned unexpected result", e
    except UsageLimitExceeded as e:
        reason, msg = "Usage limit exceeded", e
    except Exception as e:
        reason, msg = "Exception", e
    finally:
        if reason is not None or msg is not None:
            if isinstance(msg, Exception):
                logger.exception(msg)
            else:
                is_msg_type = (
                    "type" in msg.__dict__ and msg.__dict__["type"] is not None
                )
                msg_type = f"(Type: {msg.__dict__['type']}) " if is_msg_type else ""
                error_msg = f"{reason} {msg_type}caught in {operation_name}: {msg}"
                error(f"{error_msg}")
                logger.error(error_msg)
        logger.info(f"exiting operation '{operation_name}'")
