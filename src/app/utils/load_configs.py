"""
Utility functions and classes for loading application settings and configuration.

This module defines the AppEnv class for managing environment variables using Pydantic,
and provides a function to load and validate application configuration from a JSON file.
"""

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.data_models import ChatConfig
from app.utils.log import logger


class AppEnv(BaseSettings):
    """
    Application environment settings loaded from environment variables or .env file.

    This class uses Pydantic's BaseSettings to manage API keys and configuration
    for various inference endpoints, tools, and logging/monitoring services.
    Environment variables are loaded from a .env file by default.
    """

    # Inference endpoints
    GEMINI_API_KEY: str = ""
    GITHUB_API_KEY: str = ""
    GROK_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""
    RESTACK_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""

    # Tools
    TAVILY_API_KEY: str = ""

    # Logging/Monitoring/Tracing
    AGENTOPS_API_KEY: str = ""
    LOGFIRE_API_KEY: str = ""
    WANDB_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


def load_app_config(config_path: str | Path) -> ChatConfig:
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
    except FileNotFoundError:
        msg = f"Configuration file not found: {config_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)
    except json.JSONDecodeError as e:
        msg = f"Error decoding JSON from {config_path}: {e}"
        logger.error(msg)
        raise json.JSONDecodeError(msg, str(config_path), 0)
    except Exception as e:
        msg = f"Unexpected error loading config from {config_path}: {e}"
        logger.exception(msg)
        raise Exception(msg)

    return ChatConfig.model_validate(config_data)
