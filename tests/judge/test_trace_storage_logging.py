"""
Tests for trace storage logging improvements (STORY-013).

Tests ensure:
- _store_trace() logs full storage path (JSONL + SQLite)
- Log message appears at least once per execution
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from app.judge.settings import JudgeSettings
from app.judge.trace_processors import TraceCollector, TraceEvent


class TestTraceStorageLogging:
    """Test that trace storage logging includes full path information."""

    def test_store_trace_logs_storage_path(self, tmp_path: Path, caplog):
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
            error=None,
        )

        # Capture logs
        with caplog.at_level(logging.INFO):
            trace = collector.end_execution()

        # Verify: log message includes storage path
        # This will FAIL until implementation
        log_messages = [record.message for record in caplog.records]
        storage_path_mentioned = any(
            str(collector.storage_path) in msg for msg in log_messages
        )
        assert (
            storage_path_mentioned
        ), f"Storage path {collector.storage_path} not mentioned in logs: {log_messages}"

    def test_store_trace_logs_jsonl_and_sqlite_paths(self, tmp_path: Path, caplog):
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
            error=None,
        )

        with caplog.at_level(logging.INFO):
            trace = collector.end_execution()

        # Verify: log mentions both storage formats
        log_text = " ".join(record.message for record in caplog.records)

        # Check for JSONL or SQLite mention (will fail until implementation)
        assert (
            "jsonl" in log_text.lower() or "sqlite" in log_text.lower() or "traces.db" in log_text
        ), f"No storage format details in logs: {log_text}"

    def test_storage_logging_happens_at_least_once(self, tmp_path: Path, caplog):
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
            error=None,
        )

        with caplog.at_level(logging.INFO):
            trace = collector.end_execution()

        # Verify: at least one log mentions storage
        storage_logs = [
            record
            for record in caplog.records
            if "trace" in record.message.lower() or "stor" in record.message.lower()
        ]
        assert len(storage_logs) > 0, "No storage-related logs found"
