"""
Tests for real-time debug log streaming in the GUI.

This module tests the incremental log capture (polling interface with thread-safety),
compliance filtering of PeerRead reviews, and display configuration.

Mock strategy:
- LogCapture internals tested directly (no Streamlit mocking needed for unit tests)
- PeerRead compliance filtering tested via _validate_papers with non-compliant reviews
- run_app._display_configuration tested to confirm st.markdown (not st.text) is used
  for strings containing Markdown
"""

import threading
import time
from unittest.mock import patch

from inline_snapshot import snapshot
from loguru import logger


class TestLogCapturePollingInterface:
    """Tests for LogCapture.get_new_logs_since() incremental polling.

    Arrange: LogCapture instance with entries added sequentially
    Act: Call get_new_logs_since with various indices
    Expected: Returns only entries added after the given index
    """

    def test_get_new_logs_since_returns_empty_on_empty_buffer(self) -> None:
        """Returns empty list when buffer has no entries."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()

        result = capture.get_new_logs_since(0)

        assert result == []

    def test_get_new_logs_since_returns_all_entries_from_zero(self) -> None:
        """Returns all entries when polling from index 0."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        capture.add_log_entry("2026-01-01 00:00:01", "INFO", "app.foo", "first")
        capture.add_log_entry("2026-01-01 00:00:02", "DEBUG", "app.bar", "second")

        result = capture.get_new_logs_since(0)

        assert len(result) == 2
        assert result[0]["message"] == "first"
        assert result[1]["message"] == "second"

    def test_get_new_logs_since_skips_already_seen_entries(self) -> None:
        """Returns only entries added after the last-seen index."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        capture.add_log_entry("2026-01-01 00:00:01", "INFO", "app.foo", "first")
        capture.add_log_entry("2026-01-01 00:00:02", "INFO", "app.foo", "second")

        # Caller already processed 1 entry (index=1)
        result = capture.get_new_logs_since(1)

        assert len(result) == 1
        assert result[0]["message"] == "second"

    def test_get_new_logs_since_returns_empty_when_all_seen(self) -> None:
        """Returns empty list when caller has already seen all entries."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        capture.add_log_entry("2026-01-01 00:00:01", "INFO", "app.x", "msg")

        result = capture.get_new_logs_since(1)

        assert result == []

    def test_get_new_logs_since_count_returns_current_length(self) -> None:
        """log_count() returns the current number of buffered entries."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        assert capture.log_count() == 0

        capture.add_log_entry("2026-01-01 00:00:01", "INFO", "app.x", "msg1")
        assert capture.log_count() == 1

        capture.add_log_entry("2026-01-01 00:00:02", "INFO", "app.x", "msg2")
        assert capture.log_count() == 2


class TestLogCaptureThreadSafety:
    """Tests for thread-safe access to LogCapture buffer.

    Arrange: LogCapture with concurrent writer and reader threads
    Act: Write entries from worker thread, read from main thread concurrently
    Expected: No data corruption; all entries eventually visible
    """

    def test_concurrent_write_and_read_no_corruption(self) -> None:
        """Concurrent writes and reads do not corrupt the buffer."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        write_count = 50
        errors: list[Exception] = []

        def writer() -> None:
            for i in range(write_count):
                try:
                    capture.add_log_entry(
                        f"2026-01-01 00:00:{i:02d}", "INFO", "app.worker", f"msg {i}"
                    )
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(e)

        t = threading.Thread(target=writer)
        t.start()

        # Poll while writer is running
        seen = 0
        for _ in range(100):
            new = capture.get_new_logs_since(seen)
            seen += len(new)
            time.sleep(0.001)

        t.join()

        assert not errors, f"Writer thread raised: {errors}"
        # After join, all entries should be visible
        total = capture.log_count()
        assert total == write_count

    def test_lock_protects_buffer_during_clear(self) -> None:
        """clear() acquires lock, preventing partial reads during clear."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        for i in range(20):
            capture.add_log_entry("2026-01-01 00:00:01", "INFO", "app.x", f"m{i}")

        # clear() should not raise; log_count() should be 0 after
        capture.clear()
        assert capture.log_count() == 0


class TestLogCaptureFiltering:
    """Tests that LogCapture only captures app.* module logs."""

    def test_non_app_module_entries_are_filtered_out(self) -> None:
        """Entries from non-app modules are not buffered."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        capture.add_log_entry("2026-01-01 00:00:01", "INFO", "gui.pages.run_app", "ignored")
        capture.add_log_entry("2026-01-01 00:00:02", "INFO", "app.agents", "kept")

        assert capture.log_count() == 1
        assert capture.get_logs()[0]["message"] == "kept"


class TestComplianceFiltering:
    """Tests for compliance filtering of non-compliant reviews.

    Arrange: PeerReadLoader with papers having reviews missing score fields
    Act: Call _validate_papers
    Expected: Papers with non-compliant reviews are excluded; compliant papers pass through
    """

    def test_non_compliant_review_excluded_from_validate_papers(self) -> None:
        """Papers with reviews missing score fields are filtered out by _validate_papers."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        loader = PeerReadLoader()

        test_papers = [
            {
                "id": "non_compliant_001",
                "title": "Paper Missing Scores",
                "abstract": "Abstract",
                "reviews": [
                    {
                        "ORIGINALITY": "3",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "3",
                        "RECOMMENDATION": "3",
                        # Missing: IMPACT, SUBSTANCE, SOUNDNESS_CORRECTNESS, etc.
                    }
                ],
                "histories": [],
            }
        ]

        validated = loader._validate_papers(test_papers)
        assert len(validated) == 0

    def test_compliant_review_passes_validate_papers(self) -> None:
        """Papers with all score fields populated pass through _validate_papers."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        loader = PeerReadLoader()

        test_papers = [
            {
                "id": "compliant_001",
                "title": "Compliant Paper",
                "abstract": "Abstract",
                "reviews": [
                    {
                        "ORIGINALITY": "3",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "3",
                        "RECOMMENDATION": "3",
                        "IMPACT": "3",
                        "SUBSTANCE": "3",
                        "APPROPRIATENESS": "3",
                        "MEANINGFUL_COMPARISON": "3",
                        "SOUNDNESS_CORRECTNESS": "3",
                    }
                ],
                "histories": [],
            }
        ]

        validated = loader._validate_papers(test_papers)
        assert len(validated) == 1
        assert validated[0].paper_id == "compliant_001"


class TestDisplayConfigurationUsesMarkdown:
    """Tests that _display_configuration uses st.markdown for Markdown-formatted strings.

    Arrange: Mock st.markdown and st.text
    Act: Call _display_configuration with typical values
    Expected: Calls use st.markdown, not st.text, for strings with ** markers
    """

    def test_display_configuration_calls_markdown_not_text(self) -> None:
        """_display_configuration renders Markdown with st.markdown, not st.text."""
        with patch("gui.pages.run_app.st") as mock_st:
            from gui.pages.run_app import _display_configuration

            _display_configuration("openai", None, "Researcher, Analyst")

            # st.markdown() should be called for each display line
            assert mock_st.markdown.call_count >= 2
            # Verify the markdown calls contain bold-formatted text
            calls = [str(c) for c in mock_st.markdown.call_args_list]
            assert any("**Provider:**" in c for c in calls)
            assert any("**Enabled Sub-Agents:**" in c for c in calls)


class TestIncrementalLogStreaming:
    """Integration test: log entries captured incrementally during mock execution.

    Arrange: LogCapture; background thread adds entries via add_log_entry
    Act: Poll get_new_logs_since() from main thread while worker thread writes
    Expected: New entries visible within each polling cycle
    """

    def test_log_entries_visible_incrementally_during_execution(self) -> None:
        """Log entries appear in get_new_logs_since() as they are emitted."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()

        def emit_logs() -> None:
            for i in range(3):
                capture.add_log_entry(f"2026-01-01 00:00:{i:02d}", "INFO", "app.agent", f"step {i}")
                time.sleep(0.05)

        t = threading.Thread(target=emit_logs)
        t.start()

        seen_index = 0
        seen_messages: list[str] = []

        for _ in range(20):
            new = capture.get_new_logs_since(seen_index)
            seen_index += len(new)
            seen_messages.extend(e["message"] for e in new)
            time.sleep(0.02)

        t.join()

        # All emitted messages should eventually be visible
        our_messages = [m for m in seen_messages if m.startswith("step")]
        assert len(our_messages) == 3, f"Expected 3 step messages, got: {seen_messages}"


class TestLogCaptureEntryFormat:
    """Tests for the dict structure of stored log entries."""

    def test_log_capture_formats_entries(self) -> None:
        """Log entry stored as dict with timestamp, level, module, and message keys."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()

        capture.add_log_entry(
            timestamp="2026-02-15 10:00:00",
            level="WARNING",
            module="app.judge.evaluation_pipeline",
            message="Tier 2 timeout after 60s",
        )

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


class TestLogCaptureHtmlOutput:
    """Tests for HTML rendering of log entries with color-coded severity levels."""

    def test_log_capture_formats_html_output(self) -> None:
        """Log entries rendered as color-coded HTML: INFO=default, WARNING=yellow, ERROR=red."""
        from gui.utils.log_capture import LogCapture

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

        html = capture.format_html()

        assert html == snapshot(
            '<div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;"><span style="color: #666;">2026-02-15 10:00:00</span> <span style="color: #666666; font-weight: bold;">[INFO]</span> <span style="color: #696969;">app.app</span> <span>Execution started</span></div><div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;"><span style="color: #666;">2026-02-15 10:00:01</span> <span style="color: #DAA520; font-weight: bold;">[WARN]</span> <span style="color: #696969;">app.judge.evaluation_pipeline</span> <span>Tier 2 skipped</span></div><div style="margin-bottom: 8px; font-family: monospace; font-size: 12px;"><span style="color: #666;">2026-02-15 10:00:02</span> <span style="color: #F44336; font-weight: bold;">[ERR]</span> <span style="color: #696969;">app.judge.llm_evaluation_managers</span> <span>Provider unavailable</span></div>'
        )


class TestLogCaptureLoggerAttachment:
    """Tests for attaching and detaching LogCapture as a loguru sink."""

    def test_log_capture_sink_integration(self) -> None:
        """LogCapture can be attached to loguru and captures entries added directly."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        handler_id = capture.attach_to_logger()

        try:
            capture.add_log_entry(
                timestamp="2026-02-15 10:00:00",
                level="INFO",
                module="app.test",
                message="Test message",
            )

            logs = capture.get_logs()
            assert len(logs) >= 1
            test_logs = [log for log in logs if log.get("message") == "Test message"]
            assert len(test_logs) == snapshot(1)
        finally:
            logger.remove(handler_id)

    def test_log_capture_detach(self) -> None:
        """After detaching, new loguru emissions are not captured."""
        from gui.utils.log_capture import LogCapture

        capture = LogCapture()
        handler_id = capture.attach_to_logger()

        capture.detach_from_logger(handler_id)

        initial_count = len(capture.get_logs())
        logger.bind(module="app.test").info("Should not be captured")
        final_count = len(capture.get_logs())

        assert final_count == snapshot(initial_count)
