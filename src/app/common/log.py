"""
Logging configuration for the Agents-eval application.

Sets up the logger with custom settings including file rotation,
retention, and compression. Logs are written to a file with automatic rotation.
"""

from loguru import logger

from app.config.config_app import LOGS_PATH

logger.add(
    f"{LOGS_PATH}/{{time}}.log",
    rotation="1 MB",
    retention="7 days",
    compression="zip",
)
