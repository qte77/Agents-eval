"""Tests for common.settings module following TDD approach.

This module tests the CommonSettings class which implements pydantic-settings
configuration following 12-Factor #3 (Config) principles.
"""

from pathlib import Path

import pytest

from app.common.settings import CommonSettings


def test_common_settings_defaults():
    """Test that CommonSettings initializes with correct defaults."""
    settings = CommonSettings()

    assert settings.log_level == "INFO"
    assert settings.enable_opik is False
    assert settings.max_content_length == 15000


def test_common_settings_env_prefix(monkeypatch: pytest.MonkeyPatch):
    """Test that CommonSettings loads from EVAL_ prefixed environment variables."""
    monkeypatch.setenv("EVAL_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("EVAL_ENABLE_OPIK", "true")
    monkeypatch.setenv("EVAL_MAX_CONTENT_LENGTH", "20000")

    settings = CommonSettings()

    assert settings.log_level == "DEBUG"
    assert settings.enable_opik is True
    assert settings.max_content_length == 20000


def test_common_settings_env_file_loading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that CommonSettings loads from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "EVAL_LOG_LEVEL=WARNING\nEVAL_ENABLE_OPIK=true\nEVAL_MAX_CONTENT_LENGTH=25000\n"
    )

    # Change to temp directory so .env is found
    monkeypatch.chdir(tmp_path)

    settings = CommonSettings()

    assert settings.log_level == "WARNING"
    assert settings.enable_opik is True
    assert settings.max_content_length == 25000


def test_common_settings_type_validation():
    """Test that CommonSettings validates types correctly."""
    settings = CommonSettings(log_level="ERROR", enable_opik=True, max_content_length=30000)

    assert settings.log_level == "ERROR"
    assert settings.enable_opik is True
    assert settings.max_content_length == 30000


def test_common_settings_env_override_defaults(monkeypatch: pytest.MonkeyPatch):
    """Test that environment variables override code defaults."""
    monkeypatch.setenv("EVAL_LOG_LEVEL", "CRITICAL")

    settings = CommonSettings()

    assert settings.log_level == "CRITICAL"
    # Other defaults unchanged
    assert settings.enable_opik is False
    assert settings.max_content_length == 15000
