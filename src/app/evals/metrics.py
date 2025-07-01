def time_taken(start_time: float, end_time: float) -> float:
    """Calculate duration between start and end timestamps

    Args:
        start_time: Timestamp when execution started
        end_time: Timestamp when execution completed

    Returns:
        Duration in seconds with microsecond precision
    """
    return end_time - start_time
