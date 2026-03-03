"""Tests for trace file write to per-run directory.

Verifies that _store_trace() writes the trace file to the active
RunContext's trace_path when a RunContext is active.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _reset_run_context():
    """Reset active run context before and after each test."""
    from app.utils.run_context import set_active_run_context

    set_active_run_context(None)
    yield
    set_active_run_context(None)


@pytest.fixture
def _mock_artifact_registry():
    """Patch artifact registry to avoid side effects."""
    with patch("app.judge.trace_processors.get_trace_collector") as _:
        with patch("app.utils.artifact_registry.get_artifact_registry") as mock_reg:
            mock_reg.return_value = MagicMock()
            yield


class TestTraceStoreRunContext:
    """Tests for _store_trace copying to per-run directory."""

    def _make_collector(self, tmp_path: Path):
        """Create a TraceCollector with tmp_path storage."""
        from app.config.judge_settings import JudgeSettings

        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
            performance_logging=False,
        )
        from app.judge.trace_processors import TraceCollector

        return TraceCollector(settings)

    def _make_trace(self):
        """Create a minimal ProcessedTrace."""
        from app.judge.trace_processors import ProcessedTrace

        return ProcessedTrace(
            execution_id="test-exec-1234",
            start_time=1000.0,
            end_time=1001.0,
            agent_interactions=[],
            tool_calls=[],
            coordination_events=[],
            performance_metrics={"total_duration": 1.0},
        )

    def test_copies_to_run_dir_when_active(self, tmp_path: Path) -> None:
        """_store_trace writes trace to run_context.trace_path when active."""
        from app.utils.run_context import RunContext, set_active_run_context

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="test-exec-1234",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=run_dir,
        )
        set_active_run_context(ctx)

        collector = self._make_collector(tmp_path)
        trace = self._make_trace()
        # Need events for _store_trace to write SQLite
        collector.current_events = []
        collector.current_execution_id = "test-exec-1234"

        with patch("app.utils.artifact_registry.get_artifact_registry") as mock_reg:
            mock_reg.return_value = MagicMock()
            collector._store_trace(trace)

        # Verify copy exists at run_context.trace_path
        assert ctx.trace_path.exists()
        data = json.loads(ctx.trace_path.read_text().strip())
        assert data["execution_id"] == "test-exec-1234"

    def test_default_path_when_no_run_context(self, tmp_path: Path) -> None:
        """_store_trace writes only to default storage when no RunContext active."""
        collector = self._make_collector(tmp_path)
        trace = self._make_trace()
        collector.current_events = []
        collector.current_execution_id = "test-exec-1234"

        with patch("app.utils.artifact_registry.get_artifact_registry") as mock_reg:
            mock_reg.return_value = MagicMock()
            collector._store_trace(trace)

        # Default storage should have the trace file
        trace_files = list((tmp_path / "traces").glob("trace_*.json"))
        assert len(trace_files) == 1

        # No run_dir copy should exist
        run_dir = tmp_path / "run"
        assert not run_dir.exists()
