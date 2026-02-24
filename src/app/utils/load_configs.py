"""
Configuration loading utilities.

Provides a generic function for loading and validating JSON configuration
files against Pydantic models, with error handling and logging support.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from app.config.logfire_config import LogfireConfig
from app.utils.error_messages import (
    failed_to_load_config,
    file_not_found,
    invalid_data_model_format,
    invalid_json,
)
from app.utils.log import logger

__all__ = ["LogfireConfig", "load_config"]


def load_config[T: BaseModel](config_path: str | Path, data_model: type[T]) -> T:
    """
    Generic configuration loader that validates against any Pydantic model.

    Args:
        config_path: Path to the JSON configuration file
        model: Pydantic model class for validation

    Returns:
        Validated configuration instance
    """

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        return data_model.model_validate(data)
    except FileNotFoundError as e:
        msg = file_not_found(config_path)
        logger.error(msg)
        raise FileNotFoundError(msg) from e
    except json.JSONDecodeError as e:
        msg = invalid_json(str(e))
        logger.error(msg)
        raise ValueError(msg) from e
    except ValidationError as e:
        msg = invalid_data_model_format(str(e))
        logger.error(msg)
        raise ValidationError(msg) from e
    except Exception as e:
        msg = failed_to_load_config(str(e))
        logger.exception(msg)
        raise Exception(msg) from e
