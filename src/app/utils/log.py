"""
Set up the logger with custom settings.
Logs are written to a file with automatic rotation.
"""

from pathlib import Path

from loguru import logger

from app.config.config_app import LOGS_PATH
from app.utils.artifact_registry import get_artifact_registry
from app.utils.log_scrubbing import scrub_log_record

logger.add(
    f"{LOGS_PATH}/{{time}}.log",
    rotation="1 MB",
    # level="DEBUG",
    retention="7 days",
    compression="zip",
    filter=scrub_log_record,  # type: ignore[arg-type]
)

get_artifact_registry().register("Log directory", Path(LOGS_PATH).resolve())
