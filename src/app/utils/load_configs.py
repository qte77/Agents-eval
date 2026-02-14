"""
Configuration loading utilities.

Provides a generic function for loading and validating JSON configuration
files against Pydantic models, with error handling and logging support.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from app.utils.error_messages import (
    failed_to_load_config,
    file_not_found,
    invalid_data_model_format,
    invalid_json,
)
from app.utils.log import logger


def load_config(config_path: str | Path, data_model: type[BaseModel]) -> BaseModel:
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


# FIXME convert to pydantic data model ?
@dataclass
class OpikConfig:
    """Configuration for Opik tracing integration."""

    enabled: bool = False
    api_url: str = "http://localhost:3003"
    workspace: str = "peerread-evaluation"
    project: str = "agent-evaluation"
    log_start_trace_span: bool = True
    batch_size: int = 100
    timeout_seconds: float = 30.0

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "OpikConfig":
        """Create OpikConfig from evaluation config dictionary."""
        observability = config.get("observability", {})
        return cls(
            enabled=observability.get("opik_enabled", False),
            api_url=os.getenv("OPIK_URL_OVERRIDE", "http://localhost:3003"),
            workspace=os.getenv("OPIK_WORKSPACE", "peerread-evaluation"),
            project=os.getenv("OPIK_PROJECT_NAME", "agent-evaluation"),
            log_start_trace_span=observability.get("opik_log_start_trace_span", True),
            batch_size=observability.get("opik_batch_size", 100),
            timeout_seconds=observability.get("opik_timeout_seconds", 30.0),
        )
