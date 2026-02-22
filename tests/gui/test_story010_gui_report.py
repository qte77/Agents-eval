"""
Tests for STORY-010: GUI report generation (report button + inline display).

Covers:
- run_app.py: "Generate Report" button rendered only after evaluation completes
- run_app.py: report is displayed inline via st.markdown when generated
- run_app.py: download button available after report is generated
- run_app.py: report generation calls report_generator.generate_report with composite_result
- run_app.py: _render_report_section is callable and defined

Mock strategy:
- Streamlit widgets patched throughout (no real Streamlit runtime needed)
- report_generator.generate_report patched to avoid real evaluation
- inspect.signature for parameter presence checks; behavioral assertions for wiring
"""

import inspect
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# 1. run_app.py — "Generate Report" button exists after evaluation completes
# ---------------------------------------------------------------------------


class TestGenerateReportButtonPresence:
    """Verify a 'Generate Report' button section exists in run_app.

    The button must only appear when execution_state == 'completed' and
    a composite_result is available.
    """

    def test_render_report_section_signature(self) -> None:
        """_render_report_section must accept a composite_result parameter."""
        from gui.pages import run_app

        sig = inspect.signature(run_app._render_report_section)
        assert "composite_result" in sig.parameters, (
            "_render_report_section must accept 'composite_result' parameter"
        )

    def test_generate_report_button_rendered_when_result_available(self) -> None:
        """When composite_result is available, "Generate Report" button is rendered.

        Arrange: Mock st.button to capture calls; provide a fake composite_result
        Act: Call _render_report_section with a non-None result
        Expected: st.button called with text containing "Generate Report"
        """
        from gui.pages import run_app

        mock_result = MagicMock()

        with (
            patch("streamlit.button") as mock_button,
            patch("streamlit.markdown"),
            patch("streamlit.download_button"),
            patch("streamlit.session_state", {}),
            patch("gui.pages.run_app.generate_report", return_value="# Report\n"),
        ):
            mock_button.return_value = False  # Button not clicked

            run_app._render_report_section(composite_result=mock_result)

        # Verify button was rendered with generate report text
        button_labels = [str(c) for c in mock_button.call_args_list]
        assert any("Generate Report" in label for label in button_labels), (
            "'Generate Report' button must be rendered when composite_result is available"
        )

    def test_no_report_button_when_result_is_none(self) -> None:
        """When composite_result is None, report button is NOT rendered.

        Arrange: Pass None as composite_result
        Act: Call _render_report_section(composite_result=None)
        Expected: st.button NOT called with "Generate Report"
        """
        from gui.pages import run_app

        with (
            patch("streamlit.button") as mock_button,
            patch("streamlit.info"),
            patch("streamlit.markdown"),
            patch("streamlit.session_state", {}),
        ):
            mock_button.return_value = False

            run_app._render_report_section(composite_result=None)

        # Button should not be called with "Generate Report" when no result
        button_labels = [str(c) for c in mock_button.call_args_list]
        assert not any("Generate Report" in label for label in button_labels), (
            "'Generate Report' button must NOT be rendered when composite_result is None"
        )


# ---------------------------------------------------------------------------
# 2. run_app.py — report displayed inline via st.markdown on button click
# ---------------------------------------------------------------------------


class TestReportInlineDisplay:
    """Verify report is displayed inline as Markdown after button click."""

    def test_report_markdown_displayed_on_button_click(self) -> None:
        """When "Generate Report" button is clicked, report is displayed via st.markdown.

        Arrange: Mock st.button to return True (clicked), mock generate_report
        Act: Call _render_report_section with a valid composite_result
        Expected: st.markdown called with the report content
        """
        from gui.pages import run_app

        mock_result = MagicMock()
        expected_report = "# Evaluation Report\n\n## Executive Summary\n"

        with (
            patch("streamlit.button", return_value=True),
            patch("streamlit.markdown") as mock_markdown,
            patch("streamlit.download_button"),
            patch("streamlit.session_state", {}),
            patch("gui.pages.run_app.generate_report", return_value=expected_report),
        ):
            run_app._render_report_section(composite_result=mock_result)

        # Verify st.markdown was called with the report content
        # Extract actual positional args from each call object
        markdown_args = [c.args[0] for c in mock_markdown.call_args_list if c.args]
        assert any(expected_report in arg for arg in markdown_args), (
            "st.markdown must be called with the report content after button click"
        )

    def test_report_generation_calls_generate_report_with_result(self) -> None:
        """generate_report must be called with the composite_result.

        Arrange: Mock generate_report, mock button click
        Act: Call _render_report_section
        Expected: generate_report called with the composite_result
        """
        from gui.pages import run_app

        mock_result = MagicMock()

        with (
            patch("streamlit.button", return_value=True),
            patch("streamlit.markdown"),
            patch("streamlit.download_button"),
            patch("streamlit.session_state", {}),
            patch("gui.pages.run_app.generate_report") as mock_gen,
        ):
            mock_gen.return_value = "# Report"

            run_app._render_report_section(composite_result=mock_result)

        (
            mock_gen.assert_called_once_with(mock_result),
            ("generate_report must be called with the composite_result"),
        )


# ---------------------------------------------------------------------------
# 3. run_app.py — download button available after report generated
# ---------------------------------------------------------------------------


class TestReportDownloadButton:
    """Verify st.download_button is rendered with the report content."""

    def test_download_button_rendered_with_report_content(self) -> None:
        """After report generation, a download button is rendered.

        Arrange: Mock button click, mock generate_report, mock download_button
        Act: Call _render_report_section
        Expected: st.download_button called with report content as data
        """
        from gui.pages import run_app

        mock_result = MagicMock()
        report_content = "# Evaluation Report\n\n## Content\n"

        with (
            patch("streamlit.button", return_value=True),
            patch("streamlit.markdown"),
            patch("streamlit.download_button") as mock_download,
            patch("streamlit.session_state", {}),
            patch("gui.pages.run_app.generate_report", return_value=report_content),
        ):
            run_app._render_report_section(composite_result=mock_result)

        # download_button must be called
        assert mock_download.called, "st.download_button must be rendered after report generation"
        # The data parameter should contain the report content
        call_kwargs = mock_download.call_args
        data_arg = None
        if call_kwargs:
            data_arg = call_kwargs.kwargs.get("data") or (
                call_kwargs.args[1] if len(call_kwargs.args) > 1 else None
            )
        assert data_arg == report_content, (
            "st.download_button must receive report content as 'data' argument"
        )


# ---------------------------------------------------------------------------
# 4. run_app.py — _render_report_section imported and wired into render_app
# ---------------------------------------------------------------------------


class TestReportSectionWiredIntoRenderApp:
    """Verify _render_report_section is accessible on run_app and generate_report is wired in.

    The report section must be integrated into the app flow,
    appearing after execution completes.
    """

    def test_render_report_section_is_callable_on_run_app(self) -> None:
        """run_app module must expose _render_report_section as a callable.

        Behavioral: import run_app and verify _render_report_section attribute exists
        and is callable (STORY-010 wiring check without source inspection).
        """
        from gui.pages import run_app

        assert hasattr(run_app, "_render_report_section"), (
            "run_app must define _render_report_section (STORY-010)"
        )
        assert callable(run_app._render_report_section), (
            "_render_report_section must be callable"
        )

    def test_generate_report_is_accessible_from_run_app(self) -> None:
        """run_app module must have generate_report as a callable attribute.

        Behavioral: verify generate_report is importable from run_app's namespace,
        confirming it is wired into the module.
        """
        from gui.pages import run_app

        assert hasattr(run_app, "generate_report"), (
            "run_app must import generate_report from report_generator (STORY-010)"
        )
        assert callable(run_app.generate_report), (
            "generate_report must be callable on run_app"
        )
