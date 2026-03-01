"""Tests for STORY-005: Fix report generation and add clear results.

Covers:
- Report cached in session_state — no duplicate renders on re-click
- Download button persists after first generation
- "Clear Results" button resets execution state to idle
- Store generated markdown in st.session_state["generated_report"]
- Render from cache if report already exists

Mock strategy:
- _SessionDict for session state simulation
- Patch streamlit widgets (no real Streamlit runtime)
- Patch generate_report to avoid real evaluation
"""

from unittest.mock import MagicMock, patch

import pytest

_RA = "gui.pages.run_app"


class _SessionDict(dict):
    """Dict subclass that supports attribute access like st.session_state."""

    def __getattr__(self, key: str) -> object:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value: object) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


class TestReportCachedInSessionState:
    """Verify generated report is cached in st.session_state['generated_report']."""

    def test_generate_report_stores_in_session_state(self) -> None:
        """When Generate Report is clicked, markdown is stored in session_state."""
        from gui.pages import run_app

        mock_result = MagicMock()
        expected_report = "# Evaluation Report\n\n## Summary\n"
        mock_session = _SessionDict()

        with (
            patch("streamlit.button", return_value=True),
            patch("streamlit.markdown"),
            patch("streamlit.download_button"),
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.generate_report", return_value=expected_report),
        ):
            run_app._render_report_section(composite_result=mock_result)

        assert mock_session.get("generated_report") == expected_report, (
            "Generated report must be cached in st.session_state['generated_report']"
        )

    def test_cached_report_rendered_without_regeneration(self) -> None:
        """When report already cached, it renders from cache without calling generate_report."""
        from gui.pages import run_app

        mock_result = MagicMock()
        cached_report = "# Cached Report\n"
        mock_session = _SessionDict({"generated_report": cached_report})

        with (
            patch("streamlit.button", return_value=False),
            patch("streamlit.markdown") as mock_markdown,
            patch("streamlit.download_button"),
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.generate_report") as mock_gen,
        ):
            run_app._render_report_section(composite_result=mock_result)

        mock_gen.assert_not_called()
        markdown_args = [c.args[0] for c in mock_markdown.call_args_list if c.args]
        assert any(cached_report in arg for arg in markdown_args), (
            "Cached report must be rendered from session_state without regeneration"
        )

    def test_re_click_does_not_duplicate_render(self) -> None:
        """Clicking Generate Report when report exists overwrites cache, not duplicates."""
        from gui.pages import run_app

        mock_result = MagicMock()
        new_report = "# New Report\n"
        mock_session = _SessionDict({"generated_report": "# Old Report\n"})

        with (
            patch("streamlit.button", return_value=True),
            patch("streamlit.markdown") as mock_markdown,
            patch("streamlit.download_button"),
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.generate_report", return_value=new_report),
        ):
            run_app._render_report_section(composite_result=mock_result)

        assert mock_session.get("generated_report") == new_report
        # Count how many times the report markdown is rendered (should be exactly once)
        report_renders = [
            c for c in mock_markdown.call_args_list if c.args and new_report in str(c.args[0])
        ]
        assert len(report_renders) == 1, (
            "Report must be rendered exactly once, not duplicated"
        )


class TestDownloadButtonPersists:
    """Verify download button persists after first generation."""

    def test_download_button_shown_when_cached_report_exists(self) -> None:
        """Download button is shown even when Generate Report is not re-clicked."""
        from gui.pages import run_app

        mock_result = MagicMock()
        cached_report = "# Cached Report\n"
        mock_session = _SessionDict({"generated_report": cached_report})

        with (
            patch("streamlit.button", return_value=False),
            patch("streamlit.markdown"),
            patch("streamlit.download_button") as mock_download,
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.generate_report"),
        ):
            run_app._render_report_section(composite_result=mock_result)

        assert mock_download.called, (
            "Download button must persist when cached report exists"
        )
        call_kwargs = mock_download.call_args
        data_arg = call_kwargs.kwargs.get("data")
        assert data_arg == cached_report, (
            "Download button must use cached report data"
        )


class TestClearResultsButton:
    """Verify 'Clear Results' button resets execution state."""

    @pytest.mark.asyncio
    async def test_clear_results_button_exists(self) -> None:
        """A 'Clear Results' button must exist in the render_app page."""
        from gui.pages.run_app import render_app

        mock_session = _SessionDict(
            {"execution_state": "completed", "execution_result": MagicMock()}
        )
        button_labels: list[str] = []

        def capture_button(label, **kwargs):
            button_labels.append(label)
            return False

        with (
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.header"),
            patch("streamlit.radio", return_value="Multi-Agent System (MAS)"),
            patch(f"{_RA}.text_input", return_value=""),
            patch(f"{_RA}.button", side_effect=capture_button),
            patch("streamlit.button", side_effect=capture_button),
            patch("streamlit.markdown"),
            patch(f"{_RA}.info"),
            patch(f"{_RA}.subheader"),
            patch(f"{_RA}.warning"),
            patch("streamlit.expander") as mock_expander,
            patch(f"{_RA}.spinner") as mock_spinner,
            patch("streamlit.checkbox"),
            patch("streamlit.download_button"),
            patch(f"{_RA}.render_output"),
            patch(f"{_RA}._load_available_papers", return_value=[]),
            patch(f"{_RA}.generate_report", return_value="# Report"),
        ):
            mock_expander.return_value.__enter__ = MagicMock(return_value=None)
            mock_expander.return_value.__exit__ = MagicMock(return_value=False)
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            await render_app()

        assert any("Clear" in label for label in button_labels), (
            f"A 'Clear Results' button must exist. Found buttons: {button_labels}"
        )

    def test_clear_results_resets_execution_state(self) -> None:
        """When Clear Results is clicked, execution_state resets to idle."""
        from gui.pages import run_app

        mock_session = _SessionDict({
            "execution_state": "completed",
            "execution_result": MagicMock(),
            "execution_composite_result": MagicMock(),
            "generated_report": "# Report",
        })

        # We need to find and call the clear results logic
        # The clear button should be in _render_report_section or render_app
        # Let's test via render_app with button returning True for Clear
        button_call_count = 0

        def button_side_effect(label, **kwargs):
            nonlocal button_call_count
            button_call_count += 1
            # Return True only for Clear Results button
            if "Clear" in str(label):
                return True
            return False

        with (
            patch("streamlit.button", side_effect=button_side_effect),
            patch("streamlit.markdown"),
            patch("streamlit.download_button"),
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.generate_report", return_value="# Report"),
            patch("streamlit.rerun"),
        ):
            run_app._render_report_section(composite_result=MagicMock())

        assert mock_session.get("execution_state") == "idle", (
            "Clear Results must reset execution_state to 'idle'"
        )

    def test_clear_results_clears_report_cache(self) -> None:
        """When Clear Results is clicked, generated_report is cleared."""
        from gui.pages import run_app

        mock_session = _SessionDict({
            "execution_state": "completed",
            "execution_result": MagicMock(),
            "generated_report": "# Report",
        })

        def button_side_effect(label, **kwargs):
            if "Clear" in str(label):
                return True
            return False

        with (
            patch("streamlit.button", side_effect=button_side_effect),
            patch("streamlit.markdown"),
            patch("streamlit.download_button"),
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.generate_report", return_value="# Report"),
            patch("streamlit.rerun"),
        ):
            run_app._render_report_section(composite_result=MagicMock())

        assert mock_session.get("generated_report") is None, (
            "Clear Results must clear generated_report from session_state"
        )
