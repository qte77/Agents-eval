"""
Tests for trace storage logging improvements (STORY-013).

Tests ensure:
- _store_trace() writes trace to JSONL file and SQLite database
- Storage path is used as expected during execution
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.judge.settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


class TestTraceStorageLogging:
    """Test that trace storage writes to the correct locations."""

    def test_store_trace_writes_jsonl_file(self, tmp_path: Path):
        """_store_trace() MUST write a JSONL file to the configured storage path."""
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
            performance_logging=True,
        )
        collector = TraceCollector(settings)

        collector.start_execution("test-storage-001")
        collector.log_tool_call(
            agent_id="manager",
            tool_name="test_tool",
            duration=1.0,
            success=True,
        )

        result = collector.end_execution()

        assert result is not None
        # Verify a JSONL trace file was created under storage_path
        jsonl_files = list(collector.storage_path.glob("trace_test-storage-001_*.jsonl"))
        assert len(jsonl_files) == 1, f"Expected 1 JSONL file, found: {jsonl_files}"

    def test_store_trace_writes_to_sqlite(self, tmp_path: Path):
        """_store_trace() MUST write execution record to SQLite database."""
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

        result = collector.end_execution()

        assert result is not None
        # Verify the execution was written to SQLite
        conn = sqlite3.connect(collector.db_path)
        try:
            row = conn.execute(
                "SELECT execution_id FROM trace_executions WHERE execution_id = ?",
                ("test-storage-002",),
            ).fetchone()
        finally:
            conn.close()
        assert row is not None, "Execution record not found in SQLite database"

    def test_storage_creates_files_in_configured_path(self, tmp_path: Path):
        """Storage MUST create files inside the configured trace_storage_path."""
        storage_dir = tmp_path / "traces"
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(storage_dir),
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

        result = collector.end_execution()

        assert result is not None
        # At least one JSONL file must exist inside the storage path
        jsonl_files = list(storage_dir.glob("*.jsonl"))
        assert len(jsonl_files) >= 1, f"No JSONL files found in {storage_dir}"
