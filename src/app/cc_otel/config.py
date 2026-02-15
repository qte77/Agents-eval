"""OpenTelemetry configuration for Claude Code sessions.

This module provides pydantic-settings configuration for OpenTelemetry tracing
with Phoenix as the OTLP backend. Configuration follows 12-Factor #3 (Config)
principles with defaults in code and environment variable overrides.
"""

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CCOtelConfig(BaseSettings):
    """Configuration for Claude Code OpenTelemetry instrumentation.

    Configuration follows 12-Factor #3 principles with typed defaults in code
    and environment variable overrides using the CC_OTEL_ prefix.

    Attributes:
        enabled: Enable OpenTelemetry instrumentation for Claude Code sessions
        service_name: Service name for OTel traces
        phoenix_endpoint: Phoenix server base endpoint (e.g., http://localhost:6006)
        otlp_endpoint: Computed OTLP endpoint for trace export (phoenix_endpoint + /v1/traces)
    """

    enabled: bool = False
    service_name: str = "agents-eval-cc"
    phoenix_endpoint: str = "http://localhost:6006"

    model_config = SettingsConfigDict(
        env_prefix="CC_OTEL_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @computed_field  # type: ignore[misc]
    @property
    def otlp_endpoint(self) -> str:
        """Compute OTLP endpoint from Phoenix base endpoint.

        Returns:
            OTLP trace endpoint (phoenix_endpoint + /v1/traces)
        """
        return f"{self.phoenix_endpoint}/v1/traces"
