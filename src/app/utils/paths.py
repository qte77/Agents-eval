"""Centralized path resolution utilities for the application."""

from pathlib import Path

from app.config.config_app import REVIEW_PROMPT_TEMPLATE


def get_app_root() -> Path:
    """Get the application root directory (src/app).

    Returns:
        Path: Absolute path to the src/app directory.
    """

    return Path(__file__).parent.parent


def resolve_app_path(relative_path: str) -> Path:
    """Resolve a path relative to the application root.

    Args:
        relative_path: Path relative to src/app directory.

    Returns:
        Path: Absolute path resolved from the application root.

    Example:
        resolve_app_path("datasets/peerread") -> /full/path/to/src/app/datasets/peerread
    """

    return get_app_root() / relative_path


def get_config_dir() -> Path:
    """Get the application config directory (src/app/config).

    Returns:
        Path: Absolute path to the src/app/config directory.
    """
    return get_app_root() / "config"


def resolve_config_path(filename: str) -> Path:
    """Resolve a config file path within the config directory.

    Args:
        filename: Name of the config file (e.g., "config_chat.json").

    Returns:
        Path: Absolute path to the config file.

    Example:
        resolve_config_path("config_chat.json") ->
        /full/path/to/src/app/config/config_chat.json
    """
    return get_config_dir() / filename


def get_review_template_path() -> Path:
    """Get the path to the review template file.

    Returns:
        Path: Absolute path to the REVIEW_PROMPT_TEMPLATE file.
    """
    return get_config_dir() / REVIEW_PROMPT_TEMPLATE
