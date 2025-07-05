def time_taken(start_time: float, end_time: float) -> float:
    """Calculate duration between start and end timestamps

    Args:
        start_time: Timestamp when execution started
        end_time: Timestamp when execution completed

    Returns:
        Duration in seconds with microsecond precision
    """

    # TODO implement
    return end_time - start_time


def output_similarity(agent_output: str, expected_answer: str) -> bool:
    """
    Determine to what degree the agent's output matches the expected answer.

    Args:
        agent_output (str): The output produced by the agent.
        expected_answer (str): The correct or expected answer.

    Returns:
        bool: True if the output matches the expected answer, False otherwise.
    """

    # TODO score instead of bool
    return agent_output.strip() == expected_answer.strip()
