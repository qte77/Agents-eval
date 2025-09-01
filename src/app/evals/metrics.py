"""
Basic evaluation metrics functions.

This module provides simple metric calculation functions for evaluation tasks.
"""


def time_taken(start_time: float, end_time: float) -> float:
    """Calculate duration between start and end timestamps.

    Args:
        start_time: Timestamp when execution started
        end_time: Timestamp when execution completed

    Returns:
        Duration in seconds with microsecond precision

    Raises:
        ValueError: If end_time is before start_time
    """
    if end_time < start_time:
        raise ValueError("end_time must be greater than or equal to start_time")

    return end_time - start_time


def output_similarity(agent_output: str, expected_answer: str) -> float:
    """
    Calculate similarity score between agent output and expected answer.

    Args:
        agent_output: The output produced by the agent
        expected_answer: The correct or expected answer

    Returns:
        Similarity score between 0.0 (completely different) and 1.0 (identical)
    """
    if not agent_output and not expected_answer:
        return 1.0  # Both empty strings are identical

    if not agent_output or not expected_answer:
        return 0.0  # One empty, one not

    # Normalize strings for comparison
    agent_normalized = agent_output.strip().lower()
    expected_normalized = expected_answer.strip().lower()

    # Exact match
    if agent_normalized == expected_normalized:
        return 1.0

    # Simple Jaccard similarity on words
    agent_words = set(agent_normalized.split())
    expected_words = set(expected_normalized.split())

    if not agent_words and not expected_words:
        return 1.0

    intersection = agent_words & expected_words
    union = agent_words | expected_words

    return len(intersection) / len(union) if union else 0.0
