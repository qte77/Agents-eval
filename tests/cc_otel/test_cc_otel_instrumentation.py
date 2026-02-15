"""Tests for cc_otel instrumentation module following TDD approach.

This module tests the OpenTelemetry instrumentation setup for Claude Code sessions,
including initialization, graceful degradation, and Phoenix OTLP integration.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.cc_otel import disable_instrumentation, enable_instrumentation, is_enabled
from app.cc_otel.config import CCOtelConfig


def test_enable_instrumentation_with_config():
    """Test that enable_instrumentation initializes OTel with config."""
    config = CCOtelConfig(enabled=True)

    with patch("app.cc_otel.TracerProvider") as mock_tracer_provider, patch(
        "app.cc_otel.OTLPSpanExporter"
    ) as mock_exporter, patch("app.cc_otel.BatchSpanProcessor") as mock_processor:
        enable_instrumentation(config)

        # Should create OTLP exporter with Phoenix endpoint
        mock_exporter.assert_called_once_with(endpoint=config.otlp_endpoint)

        # Should create tracer provider
        mock_tracer_provider.assert_called_once()

        # Should add batch processor
        mock_processor.assert_called_once()


def test_enable_instrumentation_disabled():
    """Test that enable_instrumentation does nothing when disabled."""
    config = CCOtelConfig(enabled=False)

    with patch("app.cc_otel.TracerProvider") as mock_tracer_provider:
        enable_instrumentation(config)

        # Should not initialize anything
        mock_tracer_provider.assert_not_called()


def test_enable_instrumentation_missing_otel_library():
    """Test graceful degradation when OTel libraries are unavailable."""
    config = CCOtelConfig(enabled=True)

    with patch("app.cc_otel._otel_available", False):
        # Should not raise exception, just log warning
        enable_instrumentation(config)

        # Instrumentation should remain disabled
        assert is_enabled() is False


def test_disable_instrumentation():
    """Test that disable_instrumentation shuts down tracer provider."""
    config = CCOtelConfig(enabled=True)

    with patch("app.cc_otel.TracerProvider") as mock_tracer_provider, patch(
        "app.cc_otel.OTLPSpanExporter"
    ), patch("app.cc_otel.BatchSpanProcessor"):
        enable_instrumentation(config)

        mock_provider_instance = mock_tracer_provider.return_value
        mock_provider_instance.shutdown = MagicMock()

        disable_instrumentation()

        # Should call shutdown on the provider
        mock_provider_instance.shutdown.assert_called_once()


def test_is_enabled_returns_state():
    """Test that is_enabled returns current instrumentation state."""
    assert is_enabled() is False

    config = CCOtelConfig(enabled=True)

    with patch("app.cc_otel.TracerProvider"), patch("app.cc_otel.OTLPSpanExporter"), patch(
        "app.cc_otel.BatchSpanProcessor"
    ):
        enable_instrumentation(config)
        assert is_enabled() is True

        disable_instrumentation()
        assert is_enabled() is False


def test_enable_instrumentation_sets_service_name():
    """Test that service name from config is set in tracer provider."""
    config = CCOtelConfig(enabled=True, service_name="test-cc-service")

    with patch("app.cc_otel.TracerProvider") as mock_tracer_provider, patch(
        "app.cc_otel.OTLPSpanExporter"
    ), patch("app.cc_otel.BatchSpanProcessor"), patch("app.cc_otel.Resource") as mock_resource:
        enable_instrumentation(config)

        # Should create resource with service name
        mock_resource.create.assert_called_once()
        call_args = mock_resource.create.call_args
        assert "service.name" in call_args[0][0]
        assert call_args[0][0]["service.name"] == "test-cc-service"


def test_enable_instrumentation_idempotent():
    """Test that calling enable_instrumentation multiple times is safe."""
    config = CCOtelConfig(enabled=True)

    with patch("app.cc_otel.TracerProvider"), patch("app.cc_otel.OTLPSpanExporter"), patch(
        "app.cc_otel.BatchSpanProcessor"
    ):
        enable_instrumentation(config)
        assert is_enabled() is True

        # Second call should not raise error
        enable_instrumentation(config)
        assert is_enabled() is True


def test_otlp_exporter_configuration():
    """Test that OTLP exporter receives correct Phoenix endpoint."""
    config = CCOtelConfig(enabled=True, phoenix_endpoint="http://custom-phoenix:9999")

    with patch("app.cc_otel.TracerProvider"), patch(
        "app.cc_otel.OTLPSpanExporter"
    ) as mock_exporter, patch("app.cc_otel.BatchSpanProcessor"):
        enable_instrumentation(config)

        # Should use computed OTLP endpoint
        mock_exporter.assert_called_once_with(endpoint="http://custom-phoenix:9999/v1/traces")
