"""Tests for cc_otel.config module following TDD approach.

This module tests the CCOtelConfig class which implements pydantic-settings
configuration for OpenTelemetry tracing with Phoenix backend.
"""

from pathlib import Path

import pytest

from app.cc_otel.config import CCOtelConfig


def test_cc_otel_config_defaults():
    """Test that CCOtelConfig initializes with correct defaults."""
    config = CCOtelConfig()

    assert config.enabled is False
    assert config.service_name == "agents-eval-cc"
    assert config.phoenix_endpoint == "http://localhost:6006"
    assert config.otlp_endpoint == "http://localhost:6006/v1/traces"


def test_cc_otel_config_env_prefix(monkeypatch: pytest.MonkeyPatch):
    """Test that CCOtelConfig loads from CC_OTEL_ prefixed environment variables."""
    monkeypatch.setenv("CC_OTEL_ENABLED", "true")
    monkeypatch.setenv("CC_OTEL_SERVICE_NAME", "custom-service")
    monkeypatch.setenv("CC_OTEL_PHOENIX_ENDPOINT", "http://localhost:8080")

    config = CCOtelConfig()

    assert config.enabled is True
    assert config.service_name == "custom-service"
    assert config.phoenix_endpoint == "http://localhost:8080"
    assert config.otlp_endpoint == "http://localhost:8080/v1/traces"


def test_cc_otel_config_env_file_loading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that CCOtelConfig loads from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CC_OTEL_ENABLED=true\n"
        "CC_OTEL_SERVICE_NAME=test-service\n"
        "CC_OTEL_PHOENIX_ENDPOINT=http://phoenix:6006\n"
    )

    monkeypatch.chdir(tmp_path)
    config = CCOtelConfig()

    assert config.enabled is True
    assert config.service_name == "test-service"
    assert config.phoenix_endpoint == "http://phoenix:6006"
    assert config.otlp_endpoint == "http://phoenix:6006/v1/traces"


def test_cc_otel_config_otlp_endpoint_computed():
    """Test that otlp_endpoint is correctly computed from phoenix_endpoint."""
    config = CCOtelConfig(phoenix_endpoint="http://custom:9999")

    assert config.otlp_endpoint == "http://custom:9999/v1/traces"


def test_cc_otel_config_type_validation():
    """Test that CCOtelConfig validates types correctly."""
    config = CCOtelConfig(
        enabled=True, service_name="my-service", phoenix_endpoint="http://localhost:7007"
    )

    assert config.enabled is True
    assert config.service_name == "my-service"
    assert config.phoenix_endpoint == "http://localhost:7007"
    assert config.otlp_endpoint == "http://localhost:7007/v1/traces"


def test_cc_otel_config_env_override_defaults(monkeypatch: pytest.MonkeyPatch):
    """Test that environment variables override code defaults."""
    monkeypatch.setenv("CC_OTEL_ENABLED", "true")

    config = CCOtelConfig()

    assert config.enabled is True
    # Other defaults unchanged
    assert config.service_name == "agents-eval-cc"
    assert config.phoenix_endpoint == "http://localhost:6006"
