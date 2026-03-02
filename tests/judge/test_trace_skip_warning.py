"""
Tests for trace storage skip warnings (STORY-008).

Expected behavior:
- end_execution() returns None when skipping storage
- Three distinct skip conditions: tracing disabled, no active execution, no events collected
- Successful storage returns a ProcessedTrace (not None)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from app.config.judge_settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


@pytest.fixture(autouse=True)
def _reset_run_context():
    """Clear active run context to prevent cross-test pollution."""
    from app.utils.run_context import set_active_run_context

    set_active_run_context(None)
    yield
    set_active_run_context(None)


class TestTraceSkipWarning:
    """Test that end_execution() skips storage and warns when conditions are not met."""

    def test_returns_none_when_tracing_disabled(self, tmp_path: Path):
        """end_execution() MUST return None when trace_collection=False."""
        settings = JudgeSettings(
            trace_collection=False,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)

        result = collector.end_execution()

        assert result is None

    def test_warns_when_tracing_disabled(self, tmp_path: Path):
        """MUST warn with reason 'tracing disabled' when trace_collection=False.

        Logger mocking is required here: the only observable difference between
        the three skip conditions is the warning message. All three return None,
        and none create files. The message text is the sole behavioral signal.
        """
        settings = JudgeSettings(
            trace_collection=False,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)

        with patch("app.judge.trace_processors.logger") as mock_logger:
            result = collector.end_execution()

            assert result is None
            mock_logger.warning.assert_called_once()
            warning_msg = str(mock_logger.warning.call_args)
            assert "tracing disabled" in warning_msg

    def test_returns_none_when_no_active_execution(self, tmp_path: Path):
        """end_execution() MUST return None when called without start_execution()."""
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)
        # Don't call start_execution()

        result = collector.end_execution()

        assert result is None

    def test_silent_when_no_active_execution(self, tmp_path: Path):
        """MUST silently return None when called without start_execution().

        Idempotent guard: end_execution() may be called multiple times
        (e.g. run_manager happy path + trace_execution decorator). The second
        call finds current_execution_id=None and returns silently — no warning.
        """
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)
        # Don't call start_execution()

        with patch("app.judge.trace_processors.logger") as mock_logger:
            result = collector.end_execution()

            assert result is None
            mock_logger.warning.assert_not_called()

    def test_returns_none_when_no_events_collected(self, tmp_path: Path):
        """end_execution() MUST return None when execution has no logged events."""
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)
        collector.start_execution("test-empty-exec")
        # Don't log any events

        result = collector.end_execution()

        assert result is None

    def test_warns_when_no_events_collected(self, tmp_path: Path):
        """MUST warn 'no events collected' when execution has no logged events.

        Logger mocking is required: the only observable difference between
        skip conditions is the warning message. All return None, none create files.
        Note: no OTLP hint — TraceCollector uses manual log_tool_call(), not OTEL spans.
        """
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)
        collector.start_execution("test-empty-exec")
        # Don't log any events

        with patch("app.judge.trace_processors.logger") as mock_logger:
            result = collector.end_execution()

            assert result is None
            mock_logger.warning.assert_called_once()
            warning_msg = str(mock_logger.warning.call_args)
            assert "no events collected" in warning_msg

    def test_returns_trace_on_successful_storage(self, tmp_path: Path):
        """end_execution() MUST return a ProcessedTrace when events are present."""
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
            performance_logging=True,
        )
        collector = TraceCollector(settings)
        collector.start_execution("test-with-events")
        collector.log_tool_call(
            agent_id="manager",
            tool_name="test_tool",
            duration=1.0,
            success=True,
        )

        result = collector.end_execution()

        assert result is not None
        # Verify the JSON file was created (successful storage has observable side-effects)
        json_files = list(collector.storage_path.glob("trace_test-with-events_*.json"))
        assert len(json_files) == 1, (
            f"Expected 1 JSON file after successful storage: {json_files}"
        )
