"""OpenTelemetry instrumentation for Claude Code sessions.

This module provides standalone OTel → Phoenix tracing for Claude Code sessions,
independent of the existing logfire_instrumentation.py module. Enables tracing
alongside PydanticAI Logfire auto-instrumentation.

Usage:
    from app.cc_otel import enable_instrumentation
    from app.cc_otel.config import CCOtelConfig

    config = CCOtelConfig(enabled=True)
    enable_instrumentation(config)
"""

from app.cc_otel.config import CCOtelConfig
from app.utils.log import logger

# Set up OpenTelemetry imports with graceful degradation
_otel_available: bool = False

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import set_tracer_provider

    _otel_available = True
except ImportError:
    logger.warning("OpenTelemetry libraries not available, CC OTel tracing disabled")
    # Type stubs for when OTel is unavailable
    TracerProvider = None  # type: ignore
    OTLPSpanExporter = None  # type: ignore
    BatchSpanProcessor = None  # type: ignore
    Resource = None  # type: ignore
    set_tracer_provider = None  # type: ignore

# Global state
_tracer_provider: object | None = None
_enabled: bool = False


def enable_instrumentation(config: CCOtelConfig) -> None:
    """Enable OpenTelemetry instrumentation for Claude Code sessions.

    Initializes OTel tracer provider with OTLP exporter targeting Phoenix.
    Gracefully degrades when OTel libraries are unavailable or config.enabled is False.

    Args:
        config: CCOtelConfig instance with tracing settings
    """
    global _tracer_provider, _enabled

    if not config.enabled:
        logger.info("CC OTel instrumentation disabled")
        _enabled = False
        return

    if not _otel_available:
        logger.warning("OpenTelemetry libraries not available, CC OTel tracing disabled")
        _enabled = False
        return

    try:
        # Create resource with service name
        resource = Resource.create({"service.name": config.service_name})  # type: ignore

        # Create tracer provider
        _tracer_provider = TracerProvider(resource=resource)  # type: ignore

        # Create OTLP exporter targeting Phoenix
        otlp_exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint)  # type: ignore

        # Add batch span processor
        span_processor = BatchSpanProcessor(otlp_exporter)  # type: ignore
        _tracer_provider.add_span_processor(span_processor)  # type: ignore

        # Set as global tracer provider
        set_tracer_provider(_tracer_provider)  # type: ignore

        _enabled = True
        logger.info(f"CC OTel instrumentation enabled: {config.otlp_endpoint}")

    except Exception as e:
        logger.error(f"Failed to enable CC OTel instrumentation: {e}")
        _enabled = False


def disable_instrumentation() -> None:
    """Disable OpenTelemetry instrumentation and shutdown tracer provider.

    Shuts down the tracer provider, flushing any pending spans.
    Safe to call even if instrumentation was never enabled.
    """
    global _tracer_provider, _enabled

    if _tracer_provider is not None:
        try:
            _tracer_provider.shutdown()  # type: ignore
            logger.info("CC OTel instrumentation shut down")
        except Exception as e:
            logger.error(f"Error shutting down CC OTel instrumentation: {e}")
        finally:
            _tracer_provider = None
            _enabled = False
    else:
        _enabled = False


def is_enabled() -> bool:
    """Check if OpenTelemetry instrumentation is currently enabled.

    Returns:
        True if CC OTel instrumentation is active, False otherwise
    """
    return _enabled


__all__ = [
    "CCOtelConfig",
    "enable_instrumentation",
    "disable_instrumentation",
    "is_enabled",
]
