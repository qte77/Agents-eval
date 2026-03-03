"""
Tests for STORY-003: Debug log panel ARIA landmark.

Covers:
- format_logs_as_html() wraps output in <section role="log" aria-label="Debug logs">
- Message <span> elements use color: inherit for theme compatibility
- Individual log entry divs do not contain inline font-family/font-size declarations

Mock strategy:
- No Streamlit runtime needed — direct static method calls on LogCapture
"""

from gui.utils.log_capture import LogCapture

# Shared test fixture
_SAMPLE_LOGS: list[dict[str, str]] = [
    {
        "timestamp": "2026-01-01 12:00:00",
        "level": "INFO",
        "module": "app.test",
        "message": "Test message one",
    },
    {
        "timestamp": "2026-01-01 12:00:01",
        "level": "WARNING",
        "module": "app.test",
        "message": "Test warning",
    },
]


class TestDebugLogAriaLandmark:
    """Verify format_logs_as_html wraps output in a section with ARIA attributes."""

    def test_output_contains_role_log(self) -> None:
        """HTML output must contain role='log' attribute."""
        html = LogCapture.format_logs_as_html(_SAMPLE_LOGS)
        assert 'role="log"' in html, f"Expected role='log' in HTML, got: {html[:300]}"

    def test_output_contains_aria_label(self) -> None:
        """HTML output must contain aria-label='Debug logs'."""
        html = LogCapture.format_logs_as_html(_SAMPLE_LOGS)
        assert 'aria-label="Debug logs"' in html, (
            f"Expected aria-label='Debug logs' in HTML, got: {html[:300]}"
        )

    def test_output_wrapped_in_section_tag(self) -> None:
        """HTML output must be wrapped in a <section> element."""
        html = LogCapture.format_logs_as_html(_SAMPLE_LOGS)
        assert html.strip().startswith("<section"), (
            f"Expected HTML to start with <section, got: {html[:100]}"
        )
        assert html.strip().endswith("</section>"), (
            f"Expected HTML to end with </section>, got: {html[-100:]}"
        )


class TestMessageSpanColorInherit:
    """Verify message spans use color: inherit for theme compatibility."""

    def test_message_span_uses_color_inherit(self) -> None:
        """Message <span> must include 'color: inherit' style."""
        html = LogCapture.format_logs_as_html(_SAMPLE_LOGS)
        # The message span is the last span in each entry div
        # It should have style="color: inherit"
        assert "color: inherit" in html, (
            f"Expected 'color: inherit' on message span, got: {html[:500]}"
        )


class TestNoInlineFontDeclarations:
    """Verify individual log entry divs do not have redundant inline font styles."""

    def test_no_inline_font_family_monospace(self) -> None:
        """Log entry divs must not contain 'font-family: monospace' inline style."""
        html = LogCapture.format_logs_as_html(_SAMPLE_LOGS)
        assert "font-family: monospace" not in html, (
            f"Log entry divs must not contain inline 'font-family: monospace', got: {html[:500]}"
        )

    def test_no_inline_font_size_12px(self) -> None:
        """Log entry divs must not contain 'font-size: 12px' inline style."""
        html = LogCapture.format_logs_as_html(_SAMPLE_LOGS)
        assert "font-size: 12px" not in html, (
            f"Log entry divs must not contain inline 'font-size: 12px', got: {html[:500]}"
        )
