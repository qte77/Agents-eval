"""Opik tracing instrumentation for PydanticAI agents."""

import os
from collections.abc import Callable
from typing import Any, TypeVar, cast

from pydantic_ai import RunContext

from app.utils.load_configs import OpikConfig
from app.utils.log import logger

# Set up Opik imports with fallback
OPIK_AVAILABLE: bool = False  # type: ignore
track = None  # type: ignore
Opik = None  # type: ignore

try:
    from opik import Opik, track  # type: ignore

    OPIK_AVAILABLE = True  # type: ignore
except ImportError:
    # Fallback when opik is not available
    pass

F = TypeVar("F", bound=Callable[..., Any])


class OpikInstrumentationManager:
    """Manages Opik tracing instrumentation for PydanticAI agents."""

    def __init__(self, config: OpikConfig):
        self.config = config
        self.client: Any | None = None  # type: ignore
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Opik client if tracing is enabled."""
        if not self.config.enabled:
            logger.info("Opik tracing disabled")
            return

        if not OPIK_AVAILABLE:
            logger.warning("Opik library not available, tracing disabled")
            self.config.enabled = False
            return

        try:
            os.environ["OPIK_URL_OVERRIDE"] = self.config.api_url
            os.environ["OPIK_WORKSPACE"] = self.config.workspace
            os.environ["OPIK_PROJECT_NAME"] = self.config.project

            if self.config.log_start_trace_span:
                os.environ["OPIK_LOG_START_TRACE_SPAN"] = "True"

            self.client = Opik()  # type: ignore
            logger.info(f"Opik tracing initialized: {self.config.api_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Opik client: {e}")
            self.config.enabled = False

    def track_agent_execution(
        self,
        agent_name: str,
        agent_role: str,
        execution_phase: str,
    ) -> Callable[[F], F]:
        """Decorator for tracking agent execution with hierarchical spans."""

        def decorator(func: F) -> F:
            if not self.config.enabled or not OPIK_AVAILABLE or track is None:
                return func

            # Apply opik track decorator with graceful fallback
            if track is not None:
                try:
                    wrapped_func = track(  # type: ignore
                        name=f"{agent_name}_{func.__name__}",
                        tags=[agent_role, execution_phase, "pydantic-ai"],
                        metadata={
                            "agent_name": agent_name,
                            "agent_role": agent_role,
                            "execution_phase": execution_phase,
                            "function_name": func.__name__,
                        },
                    )(func)
                except Exception:
                    wrapped_func = func
            else:
                wrapped_func = func

            return cast(F, wrapped_func)

        return decorator

    async def _extract_context_info(
        self, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract context information from function arguments."""
        context_info = {"input": {}, "metadata": {}}

        # Extract RunContext if present
        for arg in args:
            if isinstance(arg, RunContext):
                context_info["metadata"]["usage_limits"] = str(arg.usage) if arg.usage else None
                context_info["metadata"]["run_context_present"] = True
                break

        # Extract query/prompt information
        if "query" in kwargs:
            context_info["input"]["query"] = str(kwargs["query"])[:500]  # Truncate
        elif len(args) > 0 and isinstance(args[0], str):
            context_info["input"]["query"] = args[0][:500]

        return context_info


# Global instrumentation manager
_instrumentation_manager: OpikInstrumentationManager | None = None


def initialize_opik_instrumentation(config: OpikConfig) -> None:
    """Initialize Opik instrumentation."""
    global _instrumentation_manager
    _instrumentation_manager = OpikInstrumentationManager(config)


def get_instrumentation_manager() -> OpikInstrumentationManager | None:
    """Get current instrumentation manager."""
    return _instrumentation_manager
