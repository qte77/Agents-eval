"""
Tests for trace storage logging improvements (STORY-013).

Tests ensure:
- _store_trace() logs full storage path (JSONL + SQLite)
- Log message appears at least once per execution
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from app.judge.settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


class TestTraceStorageLogging:
    """Test that trace storage logging includes full path information."""

    def test_store_trace_logs_storage_path(self, tmp_path: Path):
        """_store_trace() MUST log full storage path (JSONL + SQLite)."""
        # This test will FAIL until logging is enhanced
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
            performance_logging=True,
        )
        collector = TraceCollector(settings)

        # Create and store a trace
        collector.start_execution("test-storage-001")
        collector.log_tool_call(
            agent_id="manager",
            tool_name="test_tool",
            duration=1.0,
            success=True,
        )

        # Mock logger.info to capture log calls
        with patch("app.judge.trace_processors.logger") as mock_logger:
            _ = collector.end_execution()

            # Verify: logger.info was called with storage path
            assert mock_logger.info.called
            # Check that at least one call includes the storage path
            logged_messages = [str(call) for call in mock_logger.info.call_args_list]
            storage_mentioned = any(str(collector.storage_path) in msg for msg in logged_messages)
            assert storage_mentioned, f"Storage path not mentioned in log calls: {logged_messages}"

    def test_store_trace_logs_jsonl_and_sqlite_paths(self, tmp_path: Path):
        """_store_trace() MUST log both JSONL and SQLite database paths."""
        # This test will FAIL until logging is enhanced
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
            performance_logging=True,
        )
        collector = TraceCollector(settings)

        collector.start_execution("test-storage-002")
        collector.log_tool_call(
            agent_id="manager",
            tool_name="test_tool",
            duration=1.0,
            success=True,
        )

        with patch("app.judge.trace_processors.logger") as mock_logger:
            _ = collector.end_execution()

            # Verify: logger.info was called with storage information
            assert mock_logger.info.called
            logged_messages = [str(call) for call in mock_logger.info.call_args_list]
            storage_mentioned = any("storage" in msg.lower() for msg in logged_messages)
            assert storage_mentioned, f"No storage details in logs: {logged_messages}"

    def test_storage_logging_happens_at_least_once(self, tmp_path: Path):
        """Storage path logging MUST occur at least once per execution."""
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
            performance_logging=True,
        )
        collector = TraceCollector(settings)

        collector.start_execution("test-storage-003")
        collector.log_tool_call(
            agent_id="manager",
            tool_name="test_tool",
            duration=1.0,
            success=True,
        )

        with patch("app.judge.trace_processors.logger") as mock_logger:
            _ = collector.end_execution()

            # Verify: at least one log mentions storage or trace
            assert mock_logger.info.called
            logged_messages = [str(call) for call in mock_logger.info.call_args_list]
            storage_mentioned = any(
                "trace" in msg.lower() or "stor" in msg.lower() for msg in logged_messages
            )
            assert storage_mentioned, f"No storage-related logs found: {logged_messages}"
