"""
Tests for trace storage skip warnings (STORY-008).

Expected behavior:
- end_execution() logs a WARNING when skipping storage, with specific reason
- Three distinct reasons: tracing disabled, no active execution, no events collected
- Warning message is actionable (hints at OTLP endpoint for no-events case)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from app.judge.settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


class TestTraceSkipWarning:
    """Test that end_execution() warns when trace storage is skipped."""

    def test_warns_when_tracing_disabled(self, tmp_path: Path):
        """MUST warn with reason 'tracing disabled' when trace_collection=False."""
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

    def test_warns_when_no_active_execution(self, tmp_path: Path):
        """MUST warn with reason 'no active execution' when called without start."""
        settings = JudgeSettings(
            trace_collection=True,
            trace_storage_path=str(tmp_path / "traces"),
        )
        collector = TraceCollector(settings)
        # Don't call start_execution()

        with patch("app.judge.trace_processors.logger") as mock_logger:
            result = collector.end_execution()

            assert result is None
            mock_logger.warning.assert_called_once()
            warning_msg = str(mock_logger.warning.call_args)
            assert "no active execution" in warning_msg

    def test_warns_when_no_events_collected(self, tmp_path: Path):
        """MUST warn about OTLP endpoint when execution has no events."""
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
            assert "OTLP" in warning_msg

    def test_no_warning_on_successful_storage(self, tmp_path: Path):
        """MUST NOT warn when trace has events and stores successfully."""
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

        with patch("app.judge.trace_processors.logger") as mock_logger:
            result = collector.end_execution()

            assert result is not None
            # warning should NOT have been called
            warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
            skip_warnings = [msg for msg in warning_calls if "skipped" in msg.lower()]
            assert len(skip_warnings) == 0, (
                f"Unexpected skip warning on successful storage: {skip_warnings}"
            )
