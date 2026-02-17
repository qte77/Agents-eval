"""
Tests for real-time debug log streaming in the GUI.

This module tests the incremental log capture (polling interface with thread-safety)
and the log noise reduction in PeerRead review creation.

Mock strategy:
- LogCapture internals tested directly (no Streamlit mocking needed for unit tests)
- datasets_peerread._create_review_from_dict tested with a loader instance and
  review dict containing missing optional fields
- run_app._display_configuration tested to confirm st.markdown (not st.text) is used
  for strings containing Markdown
"""

import threading
import time
from unittest.mock import MagicMock, patch



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


class TestLogNoiseReduction:
    """Tests for aggregated missing-field log in _create_review_from_dict.

    Arrange: PeerReadLoader with a review dict missing multiple optional fields
    Act: Call _create_review_from_dict
    Expected: A single debug log line containing all missing field names,
              not one line per field
    """

    def test_missing_fields_aggregated_into_single_log_line(self) -> None:
        """Missing optional fields produce one aggregated log instead of N separate logs."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        loader = PeerReadLoader()

        # Build a minimal review dict that is missing IMPACT, SUBSTANCE, SOUNDNESS_CORRECTNESS
        # These have validation_alias='IMPACT' etc. and default="UNKNOWN" in PeerReadReview
        review_data: dict = {
            "ORIGINALITY": "3",
            "CLARITY": "3",
            "REVIEWER_CONFIDENCE": "3",
            "RECOMMENDATION": "3",
            "RECOMMENDATION_UNOFFICIAL": "3",
            # Missing: IMPACT, SUBSTANCE, SOUNDNESS_CORRECTNESS, etc.
        }

        log_calls: list[str] = []

        with patch("app.data_utils.datasets_peerread.logger") as mock_logger:
            mock_logger.debug = MagicMock(side_effect=lambda msg: log_calls.append(str(msg)))
            loader._create_review_from_dict(review_data, "paper-306")

        # Exactly ONE debug log line should have been emitted for missing fields
        missing_field_logs = [msg for msg in log_calls if "optional fields missing" in msg]
        assert len(missing_field_logs) == 1, (
            f"Expected 1 aggregated log, got {len(missing_field_logs)}: {log_calls}"
        )
        # The log should mention the paper_id
        assert "paper-306" in missing_field_logs[0]

    def test_no_missing_field_log_when_all_fields_present(self) -> None:
        """No missing-field log emitted when all optional fields are provided."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        loader = PeerReadLoader()

        # Provide all optional fields that have validation_alias and default="UNKNOWN"
        review_data: dict = {
            "ORIGINALITY": "3",
            "CLARITY": "3",
            "REVIEWER_CONFIDENCE": "3",
            "RECOMMENDATION": "3",
            "RECOMMENDATION_UNOFFICIAL": "3",
            "IMPACT": "3",
            "SUBSTANCE": "3",
            "APPROPRIATENESS": "3",
            "MEANINGFUL_COMPARISON": "3",
            "SOUNDNESS_CORRECTNESS": "3",
        }

        log_calls: list[str] = []

        with patch("app.data_utils.datasets_peerread.logger") as mock_logger:
            mock_logger.debug = MagicMock(side_effect=lambda msg: log_calls.append(str(msg)))
            loader._create_review_from_dict(review_data, "paper-001")

        missing_field_logs = [msg for msg in log_calls if "optional fields missing" in msg]
        assert len(missing_field_logs) == 0


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
                capture.add_log_entry(
                    f"2026-01-01 00:00:{i:02d}", "INFO", "app.agent", f"step {i}"
                )
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
