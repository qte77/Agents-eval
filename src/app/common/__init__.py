"""
Common module for shared utilities and models.

This module provides shared infrastructure: logging, error messages,
and common data models used across the application.
"""

from app.common import error_messages
from app.common.log import logger

__all__ = ["error_messages", "logger"]
