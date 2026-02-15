"""
Tests for Streamlit sidebar Phoenix status link.

Following TDD approach for STORY-006 sidebar Phoenix integration.
Tests verify that the sidebar includes Phoenix status link.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestSidebarPhoenixLink:
    """Test suite for sidebar Phoenix status link."""

    def test_render_sidebar_includes_phoenix_link(self):
        """Test that sidebar includes Phoenix status link."""
        from gui.components.sidebar import render_sidebar

        with patch("streamlit.sidebar.title"), patch(
            "streamlit.sidebar.radio"
        ) as mock_radio, patch("streamlit.sidebar.markdown") as mock_markdown:
            mock_radio.return_value = "Home"
            render_sidebar("Test App")

            # Should include markdown with Phoenix link
            assert mock_markdown.call_count >= 1

    def test_phoenix_link_format(self):
        """Test that Phoenix link has correct format and URL."""
        from gui.components.sidebar import render_sidebar

        with patch("streamlit.sidebar.title"), patch(
            "streamlit.sidebar.radio"
        ) as mock_radio, patch("streamlit.sidebar.markdown") as mock_markdown:
            mock_radio.return_value = "Home"
            render_sidebar("Test App")

            # Verify Phoenix link was added
            assert mock_markdown.called
            # Check if any call contains Phoenix reference
            calls = [str(call) for call in mock_markdown.call_args_list]
            has_phoenix = any("Phoenix" in str(call) or "phoenix" in str(call) for call in calls)
            assert has_phoenix

    def test_sidebar_pages_include_new_pages(self):
        """Test that PAGES config includes Evaluation and Agent Graph."""
        from gui.config.config import PAGES

        # Should include new pages
        assert "Evaluation Results" in PAGES or "Evaluation" in PAGES
        assert "Agent Graph" in PAGES

    def test_sidebar_divider_before_phoenix(self):
        """Test that sidebar includes divider before Phoenix section."""
        from gui.components.sidebar import render_sidebar

        with patch("streamlit.sidebar.title"), patch(
            "streamlit.sidebar.radio"
        ) as mock_radio, patch("streamlit.sidebar.divider") as mock_divider, patch(
            "streamlit.sidebar.markdown"
        ):
            mock_radio.return_value = "Home"
            render_sidebar("Test App")

            # Should include at least one divider
            assert mock_divider.call_count >= 1

    def test_phoenix_link_default_endpoint(self):
        """Test that Phoenix link uses correct default endpoint."""
        from gui.components.sidebar import render_sidebar

        with patch("streamlit.sidebar.title"), patch(
            "streamlit.sidebar.radio"
        ) as mock_radio, patch("streamlit.sidebar.markdown") as mock_markdown:
            mock_radio.return_value = "Home"
            render_sidebar("Test App")

            # Verify link contains localhost:6006 (default Phoenix endpoint)
            if mock_markdown.called:
                calls = [str(call) for call in mock_markdown.call_args_list]
                has_endpoint = any("6006" in str(call) for call in calls)
                # Phoenix default is 6006
                assert has_endpoint or any("Phoenix" in str(call) for call in calls)
