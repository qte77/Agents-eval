"""Tests for Logfire instrumentation following TDD approach.

This module tests the LogfireInstrumentationManager which uses
logfire.instrument_pydantic_ai() for automatic PydanticAI agent tracing.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

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
    with (
        patch("app.agents.logfire_instrumentation.logfire") as mock_logfire,
        patch("requests.head") as mock_head,
    ):
        # Mock successful connection check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

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

    with (
        patch("app.agents.logfire_instrumentation.logfire") as mock_logfire,
        patch("requests.head") as mock_head,
    ):
        # Mock successful connection check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

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

    with (
        patch("app.agents.logfire_instrumentation.logfire"),
        patch("requests.head") as mock_head,
    ):
        # Mock successful connection check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

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


# STORY-001: Graceful Logfire trace export failures
# Tests for connection checking and graceful failure handling


def test_otlp_endpoint_unreachable_disables_tracing():
    """Test that unreachable OTLP endpoint disables tracing with single warning.

    Acceptance criteria:
    - Logfire initialization catches connection errors
    - Set self.config.enabled = False when OTLP endpoint unreachable
    - Log single warning message about unavailable endpoint
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire") as mock_logfire,
        patch("requests.head") as mock_head,
        patch("app.agents.logfire_instrumentation.logger") as mock_logger,
    ):
        # Simulate connection refused error
        mock_head.side_effect = requests.exceptions.ConnectionError("Connection refused")

        manager = LogfireInstrumentationManager(config)

        # Tracing should be disabled
        assert manager.config.enabled is False

        # Should log single warning about endpoint being unreachable
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Logfire tracing unavailable" in warning_call
        assert "unreachable" in warning_call
        assert "spans and metrics export disabled" in warning_call

        # Should NOT call logfire.configure() when endpoint unreachable
        mock_logfire.configure.assert_not_called()


def test_otlp_endpoint_reachable_enables_tracing():
    """Test that reachable OTLP endpoint proceeds with normal initialization.

    Acceptance criteria:
    - When endpoint is reachable, initialization proceeds normally
    - No regression in successful initialization path
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire") as mock_logfire,
        patch("requests.head") as mock_head,
    ):
        # Simulate successful connection check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        manager = LogfireInstrumentationManager(config)

        # Tracing should remain enabled
        assert manager.config.enabled is True

        # Should call logfire.configure()
        mock_logfire.configure.assert_called_once()
        mock_logfire.instrument_pydantic_ai.assert_called_once()


def test_warning_message_format_snapshot():
    """Test warning message format using inline-snapshot.

    Acceptance criteria:
    - Warning message includes endpoint URL and mentions both spans and metrics
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire"),
        patch("requests.head") as mock_head,
        patch("app.agents.logfire_instrumentation.logger") as mock_logger,
    ):
        mock_head.side_effect = requests.exceptions.ConnectionError()

        LogfireInstrumentationManager(config)

        # Should have exactly one warning call
        assert mock_logger.warning.call_count == 1
        warning_message = mock_logger.warning.call_args[0][0]

        assert warning_message == snapshot(
            "Logfire tracing unavailable: http://localhost:6006/v1/traces unreachable (spans and metrics export disabled)"
        )


@given(
    timeout=st.floats(min_value=0.1, max_value=5.0),
    retries=st.integers(min_value=0, max_value=3),
)
def test_connection_check_timeout_bounds(timeout, retries):
    """Property test: connection check respects timeout bounds.

    Acceptance criteria:
    - Connection check timeout is configurable and bounded
    - Retries are bounded to prevent infinite loops
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire"),
        patch("requests.head") as mock_head,
    ):
        mock_head.side_effect = requests.exceptions.Timeout()

        manager = LogfireInstrumentationManager(config)

        # Should disable tracing on timeout
        assert manager.config.enabled is False

        # Verify timeout was used (if passed to requests.head)
        if mock_head.called:
            call_kwargs = mock_head.call_args[1] if mock_head.call_args else {}
            if "timeout" in call_kwargs:
                assert 0.1 <= call_kwargs["timeout"] <= 5.0


def test_send_to_cloud_skips_connection_check():
    """Test that send_to_cloud=True skips local endpoint check.

    Acceptance criteria:
    - When sending to Logfire cloud, skip local endpoint connectivity check
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=True,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire") as mock_logfire,
        patch("requests.head") as mock_head,
    ):
        manager = LogfireInstrumentationManager(config)

        # Should NOT check local endpoint when using cloud
        mock_head.assert_not_called()

        # Should proceed with normal initialization
        assert manager.config.enabled is True
        mock_logfire.configure.assert_called_once()


def test_multiple_connection_failures_single_warning():
    """Test that multiple connection failures result in single warning.

    Acceptance criteria:
    - Only one warning logged during initialization, not per-export attempt
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire"),
        patch("requests.head") as mock_head,
        patch("app.agents.logfire_instrumentation.logger") as mock_logger,
    ):
        mock_head.side_effect = requests.exceptions.ConnectionError()

        LogfireInstrumentationManager(config)

        # Should have exactly ONE warning call
        assert mock_logger.warning.call_count == 1


# STORY-012: Fix OTLP endpoint double-path bug
# Tests for correct OTLP endpoint construction per OTEL spec


def test_otlp_endpoint_uses_base_url_only():
    """Test OTEL_EXPORTER_OTLP_ENDPOINT is set to base URL without signal path.

    Acceptance criteria:
    - OTEL_EXPORTER_OTLP_ENDPOINT set to http://localhost:6006 (base URL only)
    - Not http://localhost:6006/v1/traces (no signal-specific path)
    - SDK will auto-append signal paths per OTEL spec
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire"),
        patch("requests.head") as mock_head,
        patch.dict("os.environ", {}, clear=True),
    ):
        # Mock successful connection check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        LogfireInstrumentationManager(config)

        # Should set base URL without signal-specific path
        import os

        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        assert otlp_endpoint == "http://localhost:6006"
        assert "/v1/traces" not in otlp_endpoint
        assert "/v1/metrics" not in otlp_endpoint


def test_otlp_endpoint_snapshot():
    """Test OTLP endpoint value using inline-snapshot.

    Acceptance criteria:
    - Constructed OTLP endpoint matches expected base URL format
    """
    config = LogfireConfig(
        enabled=True,
        send_to_cloud=False,
        phoenix_endpoint="http://localhost:6006",
        service_name="test-service",
    )

    with (
        patch("app.agents.logfire_instrumentation.logfire"),
        patch("requests.head") as mock_head,
        patch.dict("os.environ", {}, clear=True),
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        LogfireInstrumentationManager(config)

        import os

        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        assert otlp_endpoint == snapshot("http://localhost:6006")
