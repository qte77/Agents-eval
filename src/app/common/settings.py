"""
Common settings module using pydantic-settings.

This module implements configuration following 12-Factor #3 (Config) principles:
- Defaults in code (version-controlled)
- Environment variable overrides via EVAL_ prefix
- .env file support for local development
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """
    Common settings for the Agents-eval application.

    Configuration follows 12-Factor #3 principles with typed defaults in code
    and environment variable overrides using the EVAL_ prefix.

    Attributes:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_opik: Enable Opik tracing integration
        max_content_length: Maximum content length for paper content (characters)
    """

    log_level: str = "INFO"
    enable_opik: bool = False
    max_content_length: int = 15000

    model_config = SettingsConfigDict(
        env_prefix="EVAL_", env_file=".env", env_file_encoding="utf-8"
    )
