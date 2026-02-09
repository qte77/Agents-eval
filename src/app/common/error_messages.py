"""
Error message utilities for the Agents-eval application.

This module provides concise helper functions for generating standardized
error messages related to configuration loading and validation.
"""

from pathlib import Path


def api_connection_error(error: str) -> str:
    """
    Generate an error message for API connection error.

    Args:
        error: The error message or exception string

    Returns:
        Formatted error message string
    """
    return f"API connection error: {error}"


def failed_to_load_config(error: str) -> str:
    """
    Generate an error message for configuration loading failure.

    Args:
        error: The error message or exception string

    Returns:
        Formatted error message string
    """
    return f"Failed to load config: {error}"


def file_not_found(file_path: str | Path) -> str:
    """
    Generate an error message for a missing configuration file.

    Args:
        file_path: Path to the missing file

    Returns:
        Formatted error message string
    """
    return f"File not found: {file_path}"


def generic_exception(error: str) -> str:
    """
    Generate a generic error message.

    Args:
        error: The error message or exception string

    Returns:
        Formatted error message string
    """
    return f"Exception: {error}"


def invalid_data_model_format(error: str) -> str:
    """
    Generate an error message for invalid pydantic data model format.

    Args:
        error: The validation error message

    Returns:
        Formatted error message string
    """
    return f"Invalid pydantic data model format: {error}"


def invalid_json(error: str) -> str:
    """
    Generate an error message for invalid JSON in a configuration file.

    Args:
        error: The JSON parsing error message

    Returns:
        Formatted error message string
    """
    return f"Invalid JSON: {error}"


def invalid_type(expected_type: str, actual_type: str) -> str:
    """
    Generate an error message for invalid Type.

    Args:
        expected_type: The expected type as a string
        actual_type: The actual type received as a string

    Returns:
        Formatted error message string
    """
    return f"Type Error: Expected {expected_type}, got {actual_type} instead."


def get_key_error(error: str) -> str:
    """
    Generate a key error message.

    Args:
        error: The key error message

    Returns:
        Formatted error message string
    """
    return f"Key Error: {error}"
