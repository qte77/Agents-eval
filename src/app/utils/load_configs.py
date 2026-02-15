"""
Configuration loading utilities.

Provides a generic function for loading and validating JSON configuration
files against Pydantic models, with error handling and logging support.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.evals.settings import JudgeSettings

from pathlib import Path

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


class OpikConfig(BaseModel):
    """Configuration for Opik tracing integration.

    Constructed from JudgeSettings via from_settings(). All values
    are controlled by JUDGE_OPIK_* env vars through pydantic-settings.

    DEPRECATED: Use LogfireConfig instead. Kept for backward compatibility.
    """

    enabled: bool = False
    api_url: str = "http://localhost:8080"
    workspace: str = "peerread-evaluation"
    project: str = "peerread-evaluation"
    log_start_trace_span: bool = True
    batch_size: int = 100
    timeout_seconds: float = 30.0

    @classmethod
    def from_settings(cls, settings: JudgeSettings) -> OpikConfig:
        """Create OpikConfig from JudgeSettings.

        Args:
            settings: JudgeSettings instance with opik fields.

        Returns:
            OpikConfig populated from pydantic-settings.

        DEPRECATED: Use LogfireConfig.from_settings() instead.
        """
        # Return disabled config since Opik is deprecated
        return cls(enabled=False)


class LogfireConfig(BaseModel):
    """Configuration for Logfire + Phoenix tracing integration.

    Constructed from JudgeSettings via from_settings(). All values
    are controlled by JUDGE_LOGFIRE_* and JUDGE_PHOENIX_* env vars
    through pydantic-settings.
    """

    enabled: bool = True
    send_to_cloud: bool = False
    phoenix_endpoint: str = "http://localhost:6006"
    service_name: str = "peerread-evaluation"

    @classmethod
    def from_settings(cls, settings: JudgeSettings) -> LogfireConfig:
        """Create LogfireConfig from JudgeSettings.

        Args:
            settings: JudgeSettings instance with logfire fields.

        Returns:
            LogfireConfig populated from pydantic-settings.
        """
        return cls(
            enabled=settings.logfire_enabled,
            send_to_cloud=settings.logfire_send_to_cloud,
            phoenix_endpoint=settings.phoenix_endpoint,
            service_name=settings.logfire_service_name,
        )
