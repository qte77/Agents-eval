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
            self._configure_phoenix_endpoint()
            self._configure_logfire()
            logfire.instrument_pydantic_ai()  # type: ignore
            self._log_initialization_info()
        except Exception as e:
            logger.error(f"Failed to initialize Logfire: {e}")
            self.config.enabled = False

    def _configure_phoenix_endpoint(self) -> None:
        """Configure Phoenix OTLP endpoint environment variables.

        Checks endpoint connectivity before configuration to prevent
        ConnectionRefusedError stack traces during span export.
        """
        if self.config.send_to_cloud:
            return

        import os

        # Set Phoenix OTLP endpoint via environment variable
        # Reason: Per OTEL spec, SDK auto-appends signal-specific paths
        # (/v1/traces, /v1/metrics) to base endpoint. Set base URL only.
        # Phoenix doesn't support /v1/metrics, so disable metrics export explicitly.
        phoenix_base_url = self.config.phoenix_endpoint
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = phoenix_base_url
        os.environ["OTEL_METRICS_EXPORTER"] = "none"

        # Check endpoint connectivity before configuring exporters
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
            raise ConnectionError("Phoenix endpoint unreachable")

    def _configure_logfire(self) -> None:
        """Configure Logfire with scrubbing patterns.

        Reason: When send_to_cloud=False, pass token=None to prevent SDK from
        making API handshake calls to logfire-us.pydantic.dev. When True,
        omit token parameter to let SDK read from LOGFIRE_TOKEN env var.
        """
        from app.utils.log_scrubbing import get_logfire_scrubbing_patterns

        scrubbing_patterns = get_logfire_scrubbing_patterns()

        if self.config.send_to_cloud:
            logfire.configure(  # type: ignore
                service_name=self.config.service_name,
                send_to_logfire=True,
                scrubbing=logfire.ScrubbingOptions(extra_patterns=scrubbing_patterns),  # type: ignore
            )
        else:
            logfire.configure(  # type: ignore
                service_name=self.config.service_name,
                send_to_logfire=False,
                token=None,  # Disable cloud API calls
                scrubbing=logfire.ScrubbingOptions(extra_patterns=scrubbing_patterns),  # type: ignore
            )

    def _log_initialization_info(self) -> None:
        """Log tracing initialization info with endpoint details."""
        import os

        if self.config.send_to_cloud:
            logger.info("Logfire tracing initialized: Logfire cloud")
        else:
            base_url = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "not set")
            metrics_exp = os.environ.get("OTEL_METRICS_EXPORTER", "default")
            logger.info(
                f"Phoenix tracing initialized: endpoint={base_url}, metrics_exporter={metrics_exp}"
            )


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
