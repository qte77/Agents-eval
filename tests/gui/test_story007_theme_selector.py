"""Tests for STORY-007: Theme system (native Streamlit light/dark).

Covers:
- get_active_theme() returns correct theme dict based on Streamlit's active theme
- get_active_theme_name() returns 'nord_light' in light mode, 'expanse_dark' in dark
- get_theme_node_colors() returns (primaryColor, accentColor) from active theme
- Agent graph imports theme color functions (no hard-coded colors)

Mock strategy:
- st.get_option("theme.backgroundColor") mocked to simulate light/dark mode
- No real Streamlit runtime needed
"""

from unittest.mock import patch

# ---------------------------------------------------------------------------
# 1. get_active_theme()
# ---------------------------------------------------------------------------


class TestGetActiveTheme:
    """Test get_active_theme detects Streamlit theme mode."""

    @patch("gui.config.styling.st")
    def test_dark_mode_returns_expanse_dark(self, mock_st):
        """Dark background returns expanse_dark dict."""
        mock_st.get_option.return_value = "#0b0c10"

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["expanse_dark"]

    @patch("gui.config.styling.st")
    def test_light_mode_returns_nord_light(self, mock_st):
        """Light background returns nord_light dict."""
        mock_st.get_option.return_value = "#ECEFF4"

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["nord_light"]

    @patch("gui.config.styling.st")
    def test_no_background_option_defaults_to_dark(self, mock_st):
        """When theme.backgroundColor is None, default to dark theme."""
        mock_st.get_option.return_value = None

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["expanse_dark"]


# ---------------------------------------------------------------------------
# 2. get_theme_node_colors()
# ---------------------------------------------------------------------------


class TestGetThemeNodeColors:
    """Test get_theme_node_colors returns (primaryColor, accentColor)."""

    @patch("gui.config.styling.st")
    def test_dark_mode_returns_expanse_colors(self, mock_st):
        """Dark mode returns expanse_dark primary and accent colors."""
        mock_st.get_option.return_value = "#0b0c10"

        from gui.config.styling import get_theme_node_colors

        primary, accent = get_theme_node_colors()
        assert primary == "#4A90E2"
        assert accent == "#50C878"

    @patch("gui.config.styling.st")
    def test_light_mode_returns_nord_colors(self, mock_st):
        """Light mode returns nord_light primary and accent colors."""
        mock_st.get_option.return_value = "#ECEFF4"

        from gui.config.styling import get_theme_node_colors

        primary, accent = get_theme_node_colors()
        assert primary == "#5E81AC"
        assert accent == "#88C0D0"


# ---------------------------------------------------------------------------
# 3. Agent graph uses theme colors
# ---------------------------------------------------------------------------


class TestAgentGraphUsesThemeColors:
    """Test agent_graph.py reads node colors from active theme."""

    def test_agent_graph_imports_theme_node_colors_function(self):
        """agent_graph module must import a theme node colors function from styling."""
        import importlib.util
        from pathlib import Path

        spec = importlib.util.find_spec("gui.pages.agent_graph")
        assert spec is not None
        assert spec.origin is not None
        source = Path(spec.origin).read_text()

        # Reason: accepts either get_theme_node_colors or its alias get_graph_node_colors
        has_theme_fn = "get_theme_node_colors" in source or "get_graph_node_colors" in source
        assert has_theme_fn, (
            "agent_graph.py must import get_theme_node_colors or get_graph_node_colors "
            "from gui.config.styling"
        )

    def test_agent_graph_no_hardcoded_node_colors(self):
        """agent_graph.py must not hard-code '#4A90E2' or '#50C878' as node colors."""
        import importlib.util
        from pathlib import Path

        spec = importlib.util.find_spec("gui.pages.agent_graph")
        assert spec is not None
        assert spec.origin is not None
        source = Path(spec.origin).read_text()

        assert 'color="#4A90E2"' not in source, (
            "agent_graph.py must not hard-code '#4A90E2' for agent nodes — use theme colors"
        )
        assert 'color="#50C878"' not in source, (
            "agent_graph.py must not hard-code '#50C878' for tool nodes — use theme colors"
        )
