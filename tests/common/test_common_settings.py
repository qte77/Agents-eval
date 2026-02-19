"""Tests for common.settings module following TDD approach.

This module tests the CommonSettings class which implements pydantic-settings
configuration following 12-Factor #3 (Config) principles.
"""

from pathlib import Path

import pytest

from app.common.settings import CommonSettings


def test_common_settings_env_prefix(monkeypatch: pytest.MonkeyPatch):
    """Test that CommonSettings loads from EVAL_ prefixed environment variables."""
    monkeypatch.setenv("EVAL_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("EVAL_ENABLE_LOGFIRE", "true")
    monkeypatch.setenv("EVAL_MAX_CONTENT_LENGTH", "20000")

    settings = CommonSettings()

    assert settings.log_level == "DEBUG"
    assert settings.enable_logfire is True
    assert settings.max_content_length == 20000


def test_common_settings_env_file_loading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that CommonSettings loads from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "EVAL_LOG_LEVEL=WARNING\nEVAL_ENABLE_LOGFIRE=true\nEVAL_MAX_CONTENT_LENGTH=25000\n"
    )

    # Change to temp directory so .env is found
    monkeypatch.chdir(tmp_path)

    settings = CommonSettings()

    assert settings.log_level == "WARNING"
    assert settings.enable_logfire is True
    assert settings.max_content_length == 25000


def test_common_settings_env_override_defaults(monkeypatch: pytest.MonkeyPatch):
    """Test that environment variables override code defaults."""
    monkeypatch.setenv("EVAL_LOG_LEVEL", "CRITICAL")

    settings = CommonSettings()

    assert settings.log_level == "CRITICAL"
    # Other defaults unchanged
    assert settings.enable_logfire is False
    assert settings.max_content_length == 15000
