"""Tests for LogfireConfig following TDD approach.

This module tests the LogfireConfig class which replaces OpikConfig
for Logfire + Phoenix tracing integration.
"""

from app.judge.settings import JudgeSettings
from app.utils.load_configs import LogfireConfig


def test_logfire_config_from_settings_custom():
    """Test LogfireConfig creation from JudgeSettings with custom values."""
    settings = JudgeSettings(
        logfire_enabled=False,
        logfire_send_to_cloud=True,
        phoenix_endpoint="http://localhost:6007",
        logfire_service_name="custom-service",
    )
    config = LogfireConfig.from_settings(settings)

    assert config.enabled is False
    assert config.send_to_cloud is True
    assert config.phoenix_endpoint == "http://localhost:6007"
    assert config.service_name == "custom-service"
