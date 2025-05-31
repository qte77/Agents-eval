from loguru import logger


def setup_logger():
    """
    Set up the logger with custom settings.
    Logs are written to a file with automatic rotation.
    """

    logger.add(
        "{LOGS_PATH}/{time}.log",
        rotation="1 MB",
        retention="7 days",
        compression="zip",
    )

    return logger
