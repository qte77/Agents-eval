"""
Error message utilities for the Agents-eval application.

This module provides concise helper functions for generating standardized
error messages related to configuration loading and validation.
"""

from pathlib import Path


def api_connection_error(error: str) -> str:
    """
    Generate a error message for API connection error.
    """
    return f"API connection error: {error}"


def failed_to_load_config(error: str) -> str:
    """
    Generate a error message for configuration loading failure.
    """
    return f"Failed to load config: {error}"


def file_not_found(file_path: str | Path) -> str:
    """
    Generate an error message for a missing configuration file.
    """
    return f"File not found: {file_path}"


def generic_exception(error: str) -> str:
    """
    Generate a generic error message.
    """
    return f"Exception: {error}"


def invalid_data_model_format(error: str) -> str:
    """
    Generate an error message for invalid pydantic data model format.
    """
    return f"Invalid pydantic data model format: {error}"


def invalid_json(error: str) -> str:
    """
    Generate an error message for invalid JSON in a configuration file.
    """
    return f"Invalid JSON: {error}"


def invalid_type(expected_type: str, actual_type: str) -> str:
    """
    Generate an error message for invalid Type.
    """
    return f"Type Error: Expected {expected_type}, got {actual_type} instead."


def get_key_error(error: str) -> str:
    """
    Generate a generic error message.
    """
    return f"Key Error: {error}"
