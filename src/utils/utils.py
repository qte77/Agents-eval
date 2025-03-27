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
from json import load

from logfire import error, span
from openai import APIConnectionError, RateLimitError, UnprocessableEntityError
from pydantic import ValidationError
from pydantic_ai.exceptions import (
    ModelHTTPError,
    UnexpectedModelBehavior,
    UsageLimitExceeded,
)
from pydantic_ai.usage import Usage
from rich.console import Console

from .data_models import Config


def load_config(config_path: str) -> Config:
    """
    Load and validate the configuration from the given file path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        Config: The validated configuration object.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the configuration format is invalid.
        Exception: If there is an error loading the configuration.
    """

    try:
        with open(config_path) as file:
            config_data = load(file)
        config = Config.model_validate(config_data)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except ValidationError as e:
        raise ValueError(f"Invalid configuration format: {e}")
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")
    else:
        return config


def print_research_Result(summary: dict, usage: Usage) -> None:
    """
    Prints the research summary and usage details in a formatted manner.

    Args:
        summary (Dict): A dictionary containing the research summary with keys 'topic',
            'key_points', 'key_points_explanation', and 'conclusion'.
        usage (Usage): An object containing usage details to be printed.
    """

    print(f"\n=== Research Summary: {summary.topic} ===")
    print("\nKey Points:")
    for i, point in enumerate(summary.key_points, 1):
        print(f"{i}. {point}")
    print("\nKey Points Explanation:")
    for i, point in enumerate(summary.key_points_explanation, 1):
        print(f"{i}. {point}")
    print(f"\nConclusion: {summary.conclusion}")

    print(f"\nResponse structure: {list(dict(summary).keys())}")
    print(usage)


@contextmanager
def error_handling_context(operation_name: str, console: Console = None):
    """
    Context manager for handling errors during an operation and logging them
        appropriately.
    Args:
        operation_name (str): The name of the operation being performed.
        console (Console, optional): An optional console object for printing
            error messages.
    Yields:
        None
    Raises:
        Various exceptions based on the error encountered during the operation.
    """

    reason, msg = None, None
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
            is_msg_type = "type" in msg.__dict__ and msg.__dict__["type"] is not None
            msg_type = f"(Type: {msg.__dict__['type']}) " if is_msg_type else ""
            error_msg = f"{reason} {msg_type}caught in {operation_name}: {msg}"
            error(f"{error_msg}")
            if console is None:
                print(error_msg)
            else:
                console.print(
                    f"[except]{reason} {msg_type}caught in {operation_name}:"
                    f"[bold]{msg}[/bold][/except]"
                )
            # raise  # BaseException(error_msg)
            # sys.exit()
