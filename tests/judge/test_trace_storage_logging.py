"""
Tests for trace storage logging improvements (STORY-013).

Tests ensure:
- _store_trace() writes execution record to SQLite database
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config.judge_settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


class TestTraceStorageLogging:
    """Test that trace storage writes to the correct locations."""

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
