"""
Common module for shared utilities, settings, and models.

This module provides shared infrastructure following 12-Factor #3 (Config)
principles using pydantic-settings for configuration management.
"""

from app.common import error_messages
from app.common.log import logger
from app.common.settings import CommonSettings

__all__ = ["CommonSettings", "error_messages", "logger"]
