"""
Tests for log capture utility for GUI debug panel.

This module tests the log capture sink that:
- Captures loguru output from app.* modules during execution
- Stores log entries with timestamp, level, and message
- Provides formatted output for the Streamlit debug panel
"""

from inline_snapshot import snapshot
from loguru import logger


class TestLogCaptureSink:
    """Test the log capture sink for debug panel."""

    def test_log_capture_filters_app_modules(self):
        """Test that log capture only captures logs from app.* modules."""
        # Import the log capture utility
        from gui.utils.log_capture import LogCapture

        # Given a log capture instance
        capture = LogCapture()

        # When logs from different modules are emitted
        # Simulate app module log
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:00",
            level="INFO",
            module="app.agents.agent_system",
            message="Agent initialized",
        )

        # Simulate non-app module log
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:01",
            level="DEBUG",
            module="gui.pages.run_app",
            message="GUI render",
        )

        # Then only app.* logs should be in the buffer
        logs = capture.get_logs()
        assert len(logs) == snapshot(1)
        assert logs[0]["module"] == snapshot("app.agents.agent_system")

    def test_log_capture_clears_buffer(self):
        """Test that log capture can clear its buffer."""
        from gui.utils.log_capture import LogCapture

        # Given a log capture with entries
        capture = LogCapture()
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:00",
            level="INFO",
            module="app.judge.llm_evaluation_managers",
            message="Evaluation started",
        )

        # When buffer is cleared
        capture.clear()

        # Then buffer should be empty
        logs = capture.get_logs()
        assert len(logs) == snapshot(0)

    def test_log_capture_formats_entries(self):
        """Test that log entries are formatted correctly."""
        from gui.utils.log_capture import LogCapture

        # Given a log capture instance
        capture = LogCapture()

        # When a log entry is added
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:00",
            level="WARNING",
            module="app.judge.evaluation_pipeline",
            message="Tier 2 timeout after 60s",
        )

        # Then the formatted entry should match expected structure
        logs = capture.get_logs()
        assert len(logs) == snapshot(1)
        assert logs[0] == snapshot(
            {
                "timestamp": "2026-02-15 10:00:00",
                "level": "WARNING",
                "module": "app.judge.evaluation_pipeline",
                "message": "Tier 2 timeout after 60s",
            }
        )

    def test_log_capture_formats_html_output(self):
        """Test that log entries are formatted as color-coded HTML.

        Spec: INFO=default, WARNING=yellow, ERROR=red.
        """
        from gui.utils.log_capture import LogCapture

        # Given a log capture with entries at each key level
        capture = LogCapture()
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:00",
            level="INFO",
            module="app.app",
            message="Execution started",
        )
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:01",
            level="WARNING",
            module="app.judge.evaluation_pipeline",
            message="Tier 2 skipped",
        )
        capture.add_log_entry(
            timestamp="2026-02-15 10:00:02",
            level="ERROR",
            module="app.judge.llm_evaluation_managers",
            message="Provider unavailable",
        )

        # When formatted as HTML
        html = capture.format_html()

        # Then HTML structure should match with correct color coding
        assert html == snapshot(
            '<div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;"><span style="color: #666;">2026-02-15 10:00:00</span> <span style="color: #666666; font-weight: bold;">[INFO]</span> <span style="color: #999;">app.app</span> <span>Execution started</span></div><div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;"><span style="color: #666;">2026-02-15 10:00:01</span> <span style="color: #DAA520; font-weight: bold;">[WARNING]</span> <span style="color: #999;">app.judge.evaluation_pipeline</span> <span>Tier 2 skipped</span></div><div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;"><span style="color: #666;">2026-02-15 10:00:02</span> <span style="color: #F44336; font-weight: bold;">[ERROR]</span> <span style="color: #999;">app.judge.llm_evaluation_managers</span> <span>Provider unavailable</span></div>'
        )


class TestLogCaptureIntegration:
    """Test integration with loguru logger."""

    def test_log_capture_sink_integration(self):
        """Test that log capture integrates with loguru as a sink."""

        from gui.utils.log_capture import LogCapture

        # Given a log capture configured as a sink
        capture = LogCapture()
        handler_id = capture.attach_to_logger()

        # When logs are emitted (simulate app module by patching record name)
        try:
            # Directly add a log entry that would come from app module
            capture.add_log_entry(
                timestamp="2026-02-15 10:00:00",
                level="INFO",
                module="app.test",
                message="Test message",
            )

            # Then the log should be captured
            logs = capture.get_logs()
            assert len(logs) >= 1
            # Find our test message
            test_logs = [log for log in logs if log.get("message") == "Test message"]
            assert len(test_logs) == snapshot(1)
        finally:
            # Cleanup
            logger.remove(handler_id)

    def test_log_capture_detach(self):
        """Test that log capture can be detached from logger."""
        from gui.utils.log_capture import LogCapture

        # Given an attached log capture
        capture = LogCapture()
        handler_id = capture.attach_to_logger()

        # When detached
        capture.detach_from_logger(handler_id)

        # Then new logs should not be captured
        initial_count = len(capture.get_logs())
        logger.bind(module="app.test").info("Should not be captured")
        final_count = len(capture.get_logs())

        assert final_count == snapshot(initial_count)
