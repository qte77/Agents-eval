"""
Utility functions for loading application settings and configuration.

This module provides functions to load and validate application configuration from a JSON file.
For environment variables, use AppEnv from app.data_models.app_models.
"""

import json
from pathlib import Path

from app.data_models.app_models import ChatConfig
from app.utils.error_messages import (
    failed_to_load_config,
    file_not_found,
    invalid_json,
)
from app.utils.log import logger


def load_config(config_path: str | Path) -> ChatConfig:
    """
    Load and validate application configuration from a JSON file.

    Args:
        config_path (str): Path to the JSON configuration file.

    Returns:
        ChatConfig: An instance of ChatConfig with validated configuration data.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        Exception: For any other unexpected errors during loading or validation.
    """

    try:
        with open(config_path) as f:
            config_data = json.load(f)
    except FileNotFoundError as e:
        msg = file_not_found(config_path)
        logger.error(msg)
        raise FileNotFoundError(msg) from e
    except json.JSONDecodeError as e:
        msg = invalid_json(str(e))
        logger.error(msg)
        raise json.JSONDecodeError(msg, str(config_path), 0) from e
    except Exception as e:
        msg = failed_to_load_config(str(e))
        logger.exception(msg)
        raise Exception(msg) from e

    return ChatConfig.model_validate(config_data)
