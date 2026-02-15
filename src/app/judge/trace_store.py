"""
Thread-safe trace storage for evaluation execution.

Provides a thread-safe store for evaluation traces across all tiers
with support for concurrent read/write operations.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from app.utils.log import logger


class TraceStore:
    """
    Thread-safe storage for evaluation execution traces.

    Provides concurrent access to trace data with locking for
    safe multi-threaded operations. Supports context manager protocol
    for clean resource management.

    Attributes:
        _traces: Dictionary storing trace data by key
        _lock: Threading lock for thread-safe operations
    """

    def __init__(self) -> None:
        """Initialize empty trace store with thread safety."""
        self._traces: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        logger.debug("TraceStore initialized")

    def add_trace(self, key: str, trace_data: dict[str, Any]) -> None:
        """Add a trace to the store with timestamp.

        Args:
            key: Unique identifier for the trace
            trace_data: Trace data dictionary

        Raises:
            ValueError: If key is empty or trace_data is invalid
        """
        if not key:
            raise ValueError("Trace key cannot be empty")
        if not isinstance(trace_data, dict):
            raise ValueError("Trace data must be a dictionary")

        with self._lock:
            # Add timestamp if not present
            if "created_at" not in trace_data:
                trace_data["created_at"] = time.time()

            self._traces[key] = trace_data
            logger.debug(f"Added trace: {key}")

    def get_trace(self, key: str) -> dict[str, Any] | None:
        """Retrieve a trace by key.

        Args:
            key: Trace identifier

        Returns:
            Trace data dictionary or None if not found
        """
        with self._lock:
            return self._traces.get(key)

    def get_all_traces(self) -> list[dict[str, Any]]:
        """Get all traces in the store.

        Returns:
            List of all trace data dictionaries
        """
        with self._lock:
            return list(self._traces.values())

    def clear(self) -> None:
        """Clear all traces from the store."""
        with self._lock:
            self._traces.clear()
            logger.debug("TraceStore cleared")

    def count(self) -> int:
        """Get total number of traces.

        Returns:
            Number of traces in store
        """
        with self._lock:
            return len(self._traces)

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics for traces.

        Returns:
            Dictionary with summary information
        """
        with self._lock:
            return {
                "total_traces": len(self._traces),
                "trace_keys": list(self._traces.keys()),
            }

    def __enter__(self) -> TraceStore:
        """Enter context manager.

        Returns:
            Self for context manager use
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        # No cleanup needed - traces persist after context exit
        pass
