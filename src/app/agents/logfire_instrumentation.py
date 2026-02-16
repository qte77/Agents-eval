"""Logfire tracing instrumentation for PydanticAI agents.

Uses Logfire's native PydanticAI auto-instrumentation via
logfire.instrument_pydantic_ai(). No manual decorators or wrappers needed.
"""

import requests

from app.utils.load_configs import LogfireConfig
from app.utils.log import logger

# Set up Logfire imports with fallback
_logfire_available: bool = False

try:
    import logfire

    _logfire_available = True
except ImportError:
    # Fallback when logfire is not available
    logger.warning("Logfire library not available, tracing disabled")
    logfire = None  # type: ignore


class LogfireInstrumentationManager:
    """Manages Logfire tracing instrumentation for PydanticAI agents.

    Uses logfire.instrument_pydantic_ai() for automatic instrumentation
    of all PydanticAI agent execution. No manual decorators required.
    """

    def __init__(self, config: LogfireConfig):
        self.config = config
        self._initialize_logfire()

    def _initialize_logfire(self) -> None:
        """Initialize Logfire with Phoenix OTLP endpoint.

        Checks OTLP endpoint connectivity before initialization to prevent
        noisy stack traces when endpoint is unreachable. Logs single warning
        and disables tracing gracefully.
        """
        if not self.config.enabled:
            logger.info("Logfire tracing disabled")
            return

        if not _logfire_available:
            logger.warning("Logfire library not available, tracing disabled")
            self.config.enabled = False
            return

        try:
            # Configure Logfire with Phoenix as OTLP endpoint
            import os

            # Set Phoenix OTLP endpoint via environment variable if not sending to cloud
            # Reason: Per OTEL spec, SDK auto-appends signal-specific paths
            # (/v1/traces, /v1/metrics) to base endpoint. Set base URL only.
            # Phoenix doesn't support /v1/metrics, so disable metrics export explicitly.
            if not self.config.send_to_cloud:
                # Base URL without signal-specific path
                phoenix_base_url = self.config.phoenix_endpoint
                os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = phoenix_base_url
                os.environ["OTEL_METRICS_EXPORTER"] = "none"

                # Check endpoint connectivity before configuring exporters
                # Reason: Prevents ConnectionRefusedError stack traces during span/metrics export
                # Check /v1/traces path specifically since that's what SDK will use
                phoenix_traces_endpoint = f"{phoenix_base_url}/v1/traces"
                try:
                    requests.head(phoenix_traces_endpoint, timeout=2.0)
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                ):
                    logger.warning(
                        f"Logfire tracing unavailable: {phoenix_traces_endpoint} unreachable "
                        f"(spans and metrics export disabled)"
                    )
                    self.config.enabled = False
                    return

            # Get scrubbing patterns for sensitive data redaction
            from app.utils.log_scrubbing import get_logfire_scrubbing_patterns

            scrubbing_patterns = get_logfire_scrubbing_patterns()

            logfire.configure(  # type: ignore
                service_name=self.config.service_name,
                send_to_logfire=self.config.send_to_cloud,
                scrubbing=logfire.ScrubbingOptions(extra_patterns=scrubbing_patterns),  # type: ignore
            )

            # Auto-instrument all PydanticAI agents
            logfire.instrument_pydantic_ai()  # type: ignore

            if self.config.send_to_cloud:
                endpoint_info = "Logfire cloud"
            else:
                base_url = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "not set")
                metrics_exp = os.environ.get("OTEL_METRICS_EXPORTER", "default")
                endpoint_info = f"endpoint={base_url}, metrics_exporter={metrics_exp}"
            logger.info(f"Logfire tracing initialized: {endpoint_info}")
        except Exception as e:
            logger.error(f"Failed to initialize Logfire: {e}")
            self.config.enabled = False


# Global instrumentation manager
_instrumentation_manager: LogfireInstrumentationManager | None = None


def initialize_logfire_instrumentation(config: LogfireConfig) -> None:
    """Initialize Logfire instrumentation.

    Args:
        config: LogfireConfig instance with tracing settings.
    """
    global _instrumentation_manager
    _instrumentation_manager = LogfireInstrumentationManager(config)


def get_instrumentation_manager() -> LogfireInstrumentationManager | None:
    """Get current instrumentation manager.

    Returns:
        Current LogfireInstrumentationManager instance or None if not initialized.
    """
    return _instrumentation_manager
