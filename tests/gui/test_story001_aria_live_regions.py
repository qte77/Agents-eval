"""Tests for STORY-001: Fix broken ARIA live regions in run_app.py.

Verifies that ARIA live region tags are consolidated into single st.markdown()
calls instead of split across separate calls (which creates malformed DOM).

Screen readers require well-formed ARIA live regions to announce status changes.

Mock strategy:
- Patch streamlit.markdown to capture all HTML output
- Call _display_execution_result with each state
- Assert no orphaned opening/closing ARIA tags
- Assert complete ARIA-wrapped HTML in single calls
"""

from unittest.mock import MagicMock, patch


class TestARIALiveRegionsConsolidated:
    """Verify ARIA live region tags are not split across separate st.markdown() calls.

    The bug: opening <div role="status"> and closing </div> in separate
    st.markdown() calls creates malformed DOM. Screen readers never see the
    live region content.
    """

    def test_running_state_no_orphaned_opening_aria_tag(self) -> None:
        """Running state must not emit a st.markdown() with only an opening ARIA tag."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.spinner") as mock_spinner,
            patch("streamlit.info"),
        ):
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            _display_execution_result("running")

        # No markdown call should contain ONLY an opening ARIA div tag
        for call in mock_md.call_args_list:
            html = str(call.args[0]) if call.args else ""
            stripped = html.strip()
            assert stripped != '<div role="status" aria-live="polite">', (
                "Opening ARIA tag must not be emitted alone in a separate st.markdown() call. "
                "Consolidate opening and closing tags into a single call."
            )

    def test_running_state_no_orphaned_closing_div(self) -> None:
        """Running state must not emit a st.markdown() with only a closing </div>."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.spinner") as mock_spinner,
            patch("streamlit.info"),
        ):
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            _display_execution_result("running")

        for call in mock_md.call_args_list:
            html = str(call.args[0]) if call.args else ""
            stripped = html.strip()
            assert stripped != "</div>", (
                "Closing </div> must not be emitted alone in a separate st.markdown() call. "
                "Consolidate into a single call with the opening tag."
            )

    def test_completed_state_no_orphaned_opening_aria_tag(self) -> None:
        """Completed state must not emit an orphaned opening ARIA tag."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.info"),
            patch("streamlit.session_state", {}),
        ):
            _display_execution_result("completed")

        for call in mock_md.call_args_list:
            html = str(call.args[0]) if call.args else ""
            stripped = html.strip()
            assert stripped != '<div role="status" aria-live="polite">', (
                "Completed state: opening ARIA tag must not be emitted alone."
            )

    def test_completed_state_no_orphaned_closing_div(self) -> None:
        """Completed state must not emit an orphaned closing </div>."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.info"),
            patch("streamlit.session_state", {}),
        ):
            _display_execution_result("completed")

        for call in mock_md.call_args_list:
            html = str(call.args[0]) if call.args else ""
            stripped = html.strip()
            assert stripped != "</div>", (
                "Completed state: closing </div> must not be emitted alone."
            )

    def test_error_state_no_orphaned_opening_aria_tag(self) -> None:
        """Error state must not emit an orphaned opening ARIA tag."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.exception"),
            patch("streamlit.session_state", {"execution_error": "Test error"}),
        ):
            _display_execution_result("error")

        for call in mock_md.call_args_list:
            html = str(call.args[0]) if call.args else ""
            stripped = html.strip()
            assert stripped != '<div role="alert" aria-live="assertive">', (
                "Error state: opening ARIA tag must not be emitted alone."
            )

    def test_error_state_no_orphaned_closing_div(self) -> None:
        """Error state must not emit an orphaned closing </div>."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.exception"),
            patch("streamlit.session_state", {"execution_error": "Test error"}),
        ):
            _display_execution_result("error")

        for call in mock_md.call_args_list:
            html = str(call.args[0]) if call.args else ""
            stripped = html.strip()
            assert stripped != "</div>", (
                "Error state: closing </div> must not be emitted alone."
            )


class TestARIALiveRegionsWellFormed:
    """Verify that ARIA live regions contain both opening and closing tags when present."""

    def test_running_state_aria_region_is_complete(self) -> None:
        """Running state ARIA region must contain both opening and closing tags in one call."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.spinner") as mock_spinner,
            patch("streamlit.info"),
        ):
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            _display_execution_result("running")

        # Find markdown calls with ARIA role="status"
        aria_calls = [
            str(call.args[0])
            for call in mock_md.call_args_list
            if call.args and 'role="status"' in str(call.args[0])
        ]
        assert aria_calls, "Running state must emit ARIA role='status' region"
        for html in aria_calls:
            assert "</div>" in html, (
                f"ARIA region must be self-contained with closing </div>. Got: {html[:200]}"
            )

    def test_error_state_aria_region_is_complete(self) -> None:
        """Error state ARIA region must contain both opening and closing tags in one call."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.exception"),
            patch("streamlit.session_state", {"execution_error": "Test error"}),
        ):
            _display_execution_result("error")

        aria_calls = [
            str(call.args[0])
            for call in mock_md.call_args_list
            if call.args and 'role="alert"' in str(call.args[0])
        ]
        assert aria_calls, "Error state must emit ARIA role='alert' region"
        for html in aria_calls:
            assert "</div>" in html, (
                f"ARIA region must be self-contained with closing </div>. Got: {html[:200]}"
            )

    def test_completed_state_aria_region_is_complete(self) -> None:
        """Completed state ARIA region must contain both opening and closing tags."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.info"),
            patch("streamlit.session_state", {}),
        ):
            _display_execution_result("completed")

        aria_calls = [
            str(call.args[0])
            for call in mock_md.call_args_list
            if call.args and 'role="status"' in str(call.args[0])
        ]
        assert aria_calls, "Completed state must emit ARIA role='status' region"
        for html in aria_calls:
            assert "</div>" in html, (
                f"ARIA region must be self-contained with closing </div>. Got: {html[:200]}"
            )
