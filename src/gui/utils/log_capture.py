"""
Log capture utility for GUI debug panel.

This module provides a loguru sink that captures log entries from app.* modules
during execution and stores them in memory for display in the Streamlit debug panel.
"""

from typing import Any

from loguru import logger


class LogCapture:
    """Captures and formats log entries for the debug panel.

    This class acts as a loguru sink that filters and stores log entries from
    app.* modules. It provides methods to retrieve, clear, and format logs
    for display in the Streamlit UI.
    """

    def __init__(self) -> None:
        """Initialize empty log buffer."""
        self._buffer: list[dict[str, str]] = []
        self._handler_id: int | None = None

    def add_log_entry(self, timestamp: str, level: str, module: str, message: str) -> None:
        """Add a log entry to the buffer if it's from an app.* module.

        Args:
            timestamp: ISO format timestamp string
            level: Log level (INFO, WARNING, ERROR, etc.)
            module: Module name that generated the log
            message: Log message content
        """
        # Filter: only capture logs from app.* modules
        if not module.startswith("app."):
            return

        self._buffer.append(
            {
                "timestamp": timestamp,
                "level": level,
                "module": module,
                "message": message,
            }
        )

    def get_logs(self) -> list[dict[str, str]]:
        """Retrieve all captured log entries.

        Returns:
            List of log entry dictionaries
        """
        return self._buffer.copy()

    def clear(self) -> None:
        """Clear the log buffer."""
        self._buffer.clear()

    def format_html(self) -> str:
        """Format log entries as HTML with color-coded levels.

        Returns:
            HTML string with styled log entries
        """
        return self.format_logs_as_html(self._buffer)

    @staticmethod
    def format_logs_as_html(logs: list[dict[str, str]]) -> str:
        """Format a list of log entries as HTML with color-coded levels.

        Args:
            logs: List of log entry dictionaries

        Returns:
            HTML string with styled log entries
        """
        if not logs:
            return "<p>No logs captured.</p>"

        html_parts: list[str] = []
        level_colors = {
            "WARNING": "#DAA520",  # Yellow (goldenrod)
            "ERROR": "#F44336",  # Red
            "DEBUG": "#2196F3",  # Blue
            "CRITICAL": "#9C27B0",  # Purple
        }

        for entry in logs:
            level = entry["level"]
            color = level_colors.get(level, "#666666")
            html_parts.append(
                f'<div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;">'
                f'<span style="color: #666;">{entry["timestamp"]}</span> '
                f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
                f'<span style="color: #999;">{entry["module"]}</span> '
                f"<span>{entry['message']}</span>"
                f"</div>"
            )

        return "".join(html_parts)

    def _sink_handler(self, message: Any) -> None:
        """Loguru sink handler that processes log records.

        Args:
            message: Loguru message record
        """
        record = message.record
        module = record.get("name", "unknown")
        timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
        level = record["level"].name
        msg = record["message"]

        self.add_log_entry(timestamp, level, module, msg)

    def attach_to_logger(self) -> int:
        """Attach this capture instance as a loguru sink.

        Returns:
            Handler ID for later removal
        """
        self._handler_id = logger.add(self._sink_handler, format="{message}")
        return self._handler_id

    def detach_from_logger(self, handler_id: int) -> None:
        """Detach this capture instance from loguru.

        Args:
            handler_id: Handler ID returned by attach_to_logger
        """
        logger.remove(handler_id)
        self._handler_id = None
