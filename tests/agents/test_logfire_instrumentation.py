"""Tests for Logfire instrumentation following TDD approach.

This module tests the LogfireInstrumentationManager which uses
logfire.instrument_pydantic_ai() for automatic PydanticAI agent tracing.
"""

from unittest.mock import patch

import pytest

from app.agents.logfire_instrumentation import (
    LogfireInstrumentationManager,
    get_instrumentation_manager,
    initialize_logfire_instrumentation,
)
from app.utils.load_configs import LogfireConfig


@pytest.fixture
def logfire_config_enabled():
    """Create a LogfireConfig with tracing enabled."""
    return LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )


@pytest.fixture
def logfire_config_disabled():
    """Create a LogfireConfig with tracing disabled."""
    return LogfireConfig(
        enabled=False,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )


def test_instrumentation_manager_initialization_enabled(logfire_config_enabled):
    """Test LogfireInstrumentationManager initializes when enabled."""
    with patch("app.agents.logfire_instrumentation.logfire") as mock_logfire:
        manager = LogfireInstrumentationManager(logfire_config_enabled)

        assert manager.config.enabled is True
        # Logfire configure should be called with correct parameters
        mock_logfire.configure.assert_called_once()


def test_instrumentation_manager_initialization_disabled(logfire_config_disabled):
    """Test LogfireInstrumentationManager handles disabled config."""
    with patch("app.agents.logfire_instrumentation.logfire") as mock_logfire:
        manager = LogfireInstrumentationManager(logfire_config_disabled)

        assert manager.config.enabled is False
        # Configure should not be called when disabled
        mock_logfire.configure.assert_not_called()


def test_instrumentation_manager_auto_instrument_pydantic_ai():
    """Test that instrument_pydantic_ai() is called during initialization."""
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with patch("app.agents.logfire_instrumentation.logfire") as mock_logfire:
        LogfireInstrumentationManager(config)

        # instrument_pydantic_ai() should be called for auto-instrumentation
        mock_logfire.instrument_pydantic_ai.assert_called_once()


def test_initialize_logfire_instrumentation():
    """Test initialize_logfire_instrumentation creates global manager."""
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with patch("app.agents.logfire_instrumentation.logfire"):
        initialize_logfire_instrumentation(config)
        manager = get_instrumentation_manager()

        assert manager is not None
        assert isinstance(manager, LogfireInstrumentationManager)


def test_get_instrumentation_manager_before_init():
    """Test get_instrumentation_manager returns None before initialization."""
    # Reset global state
    import app.agents.logfire_instrumentation as module

    module._instrumentation_manager = None

    assert get_instrumentation_manager() is None


def test_instrumentation_manager_graceful_degradation():
    """Test graceful degradation when logfire import fails."""
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with patch("app.agents.logfire_instrumentation._logfire_available", False):
        manager = LogfireInstrumentationManager(config)

        # Should still create manager but with disabled state
        assert manager.config.enabled is False
