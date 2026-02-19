"""
This module provides utility functions and context managers for handling configurations,
error handling, and setting up agent environments.

Functions:
    load_config(config_path: str) -> Config:
        Load and validate configuration from a JSON file.

    print_research_result(summary: Dict, usage: Usage) -> None:
        Output structured summary of the research topic.

    error_handling_context(operation_name: str, console: Console = None):
        Context manager for handling errors during operations.

    setup_agent_env(config: Config, console: Console = None) -> AgentConfig:
        Set up the agent environment based on the provided configuration.
"""

from pydantic_ai.usage import RunUsage

from app.data_models.app_models import ResearchSummary
from app.utils.log import logger


def log_research_result(summary: ResearchSummary, usage: RunUsage) -> None:
    """
    Prints the research summary and usage details in a formatted manner.

    Args:
        summary (Dict): A dictionary containing the research summary with keys 'topic',
            'key_points', 'key_points_explanation', and 'conclusion'.
        usage (RunUsage): An object containing usage details to be printed.
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
