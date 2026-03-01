"""Tests for STORY-007: Add theme selector widget.

Covers:
- get_active_theme() returns correct theme dict for each theme name
- get_active_theme() defaults to expanse_dark when no session state
- get_theme_node_colors() returns (primaryColor, accentColor) from active theme
- Sidebar renders a theme selectbox
- Selected theme persists in session state

Mock strategy:
- Streamlit session_state simulated with _SessionDict
- Sidebar widgets patched via gui.components.sidebar.sidebar
"""

from unittest.mock import MagicMock, patch


class _SessionDict(dict):
    """Dict subclass that supports attribute access, mimicking st.session_state."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


# ---------------------------------------------------------------------------
# 1. get_active_theme()
# ---------------------------------------------------------------------------


class TestGetActiveTheme:
    """Test get_active_theme reads selected_theme from session state."""

    @patch("gui.config.styling.st")
    def test_defaults_to_expanse_dark_when_no_session_state(self, mock_st):
        """When session state has no selected_theme, return expanse_dark dict."""
        mock_st.session_state = _SessionDict()

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["expanse_dark"]

    @patch("gui.config.styling.st")
    def test_returns_nord_light_when_selected(self, mock_st):
        """When selected_theme is nord_light, return nord_light dict."""
        mock_st.session_state = _SessionDict({"selected_theme": "nord_light"})

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["nord_light"]

    @patch("gui.config.styling.st")
    def test_returns_tokyo_night_when_selected(self, mock_st):
        """When selected_theme is tokyo_night, return tokyo_night dict."""
        mock_st.session_state = _SessionDict({"selected_theme": "tokyo_night"})

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["tokyo_night"]

    @patch("gui.config.styling.st")
    def test_returns_expanse_dark_when_selected(self, mock_st):
        """When selected_theme is expanse_dark, return expanse_dark dict."""
        mock_st.session_state = _SessionDict({"selected_theme": "expanse_dark"})

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["expanse_dark"]

    @patch("gui.config.styling.st")
    def test_falls_back_to_expanse_dark_for_unknown_theme(self, mock_st):
        """When selected_theme is unknown, fall back to expanse_dark."""
        mock_st.session_state = _SessionDict({"selected_theme": "nonexistent"})

        from gui.config.styling import THEMES, get_active_theme

        result = get_active_theme()
        assert result == THEMES["expanse_dark"]


# ---------------------------------------------------------------------------
# 2. get_theme_node_colors()
# ---------------------------------------------------------------------------


class TestGetThemeNodeColors:
    """Test get_theme_node_colors returns (primaryColor, accentColor)."""

    @patch("gui.config.styling.st")
    def test_returns_tuple_of_two_strings(self, mock_st):
        """Return value must be a tuple of two hex color strings."""
        mock_st.session_state = _SessionDict()

        from gui.config.styling import get_theme_node_colors

        result = get_theme_node_colors()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(c, str) and c.startswith("#") for c in result)

    @patch("gui.config.styling.st")
    def test_default_returns_expanse_dark_colors(self, mock_st):
        """Default theme returns expanse_dark primary and accent colors."""
        mock_st.session_state = _SessionDict()

        from gui.config.styling import get_theme_node_colors

        primary, accent = get_theme_node_colors()
        assert primary == "#4A90E2"
        assert accent == "#50C878"

    @patch("gui.config.styling.st")
    def test_nord_light_returns_correct_colors(self, mock_st):
        """Nord light theme returns its primary and accent colors."""
        mock_st.session_state = _SessionDict({"selected_theme": "nord_light"})

        from gui.config.styling import get_theme_node_colors

        primary, accent = get_theme_node_colors()
        assert primary == "#5E81AC"
        assert accent == "#88C0D0"

    @patch("gui.config.styling.st")
    def test_tokyo_night_returns_correct_colors(self, mock_st):
        """Tokyo night theme returns its primary and accent colors."""
        mock_st.session_state = _SessionDict({"selected_theme": "tokyo_night"})

        from gui.config.styling import get_theme_node_colors

        primary, accent = get_theme_node_colors()
        assert primary == "#7AA2F7"
        assert accent == "#9ECE6A"


# ---------------------------------------------------------------------------
# 3. Sidebar theme selectbox
# ---------------------------------------------------------------------------


class TestSidebarThemeSelectbox:
    """Test sidebar renders a theme selectbox widget."""

    def _make_sidebar_mock(self, selectbox_return: str = "expanse_dark") -> MagicMock:
        """Create a sidebar mock with selectbox returning a given value."""
        mock_sidebar = MagicMock()
        mock_sidebar.radio.return_value = "Run Research App"
        mock_sidebar.selectbox.return_value = selectbox_return
        return mock_sidebar

    def test_sidebar_renders_theme_selectbox(self) -> None:
        """render_sidebar must call sidebar.selectbox for theme selection."""
        from gui.components.sidebar import render_sidebar

        mock_sidebar = self._make_sidebar_mock()

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            with patch("gui.components.sidebar.st") as mock_st:
                mock_st.session_state = _SessionDict()
                render_sidebar("Test App")

        mock_sidebar.selectbox.assert_called_once()

    def test_theme_selectbox_options_match_theme_keys(self) -> None:
        """Theme selectbox options must match THEMES dict keys."""
        from gui.components.sidebar import render_sidebar
        from gui.config.styling import THEMES

        captured_options = []
        mock_sidebar = MagicMock()
        mock_sidebar.radio.return_value = "Run Research App"

        def capture_selectbox(label, options, **kwargs):
            captured_options.extend(options)
            return options[0] if options else ""

        mock_sidebar.selectbox.side_effect = capture_selectbox

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            with patch("gui.components.sidebar.st") as mock_st:
                mock_st.session_state = _SessionDict()
                render_sidebar("Test App")

        assert set(captured_options) == set(THEMES.keys())

    def test_theme_selectbox_writes_to_session_state(self) -> None:
        """Theme selectbox must write selection to st.session_state['selected_theme']."""
        from gui.components.sidebar import render_sidebar

        mock_sidebar = self._make_sidebar_mock(selectbox_return="tokyo_night")
        session = _SessionDict()

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            with patch("gui.components.sidebar.st") as mock_st:
                mock_st.session_state = session
                render_sidebar("Test App")

        assert session.get("selected_theme") == "tokyo_night"

    def test_theme_selectbox_appears_before_tracing_expander(self) -> None:
        """Theme selectbox must be called before the Tracing expander section."""
        from gui.components.sidebar import render_sidebar

        call_order: list[str] = []
        mock_sidebar = MagicMock()
        mock_sidebar.radio.return_value = "Run Research App"
        mock_sidebar.selectbox.side_effect = lambda *a, **kw: call_order.append("selectbox") or "expanse_dark"

        mock_expander_ctx = MagicMock()
        mock_expander_ctx.__enter__ = MagicMock(return_value=MagicMock())
        mock_expander_ctx.__exit__ = MagicMock(return_value=False)
        mock_sidebar.expander.side_effect = lambda *a, **kw: (call_order.append("expander"), mock_expander_ctx)[1]

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            with patch("gui.components.sidebar.st") as mock_st:
                mock_st.session_state = _SessionDict()
                render_sidebar("Test App")

        assert "selectbox" in call_order
        assert "expander" in call_order
        assert call_order.index("selectbox") < call_order.index("expander")


# ---------------------------------------------------------------------------
# 4. Agent graph uses theme colors
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

        # Reason: hard-coded colors in node creation should be replaced by theme lookup
        assert 'color="#4A90E2"' not in source, (
            "agent_graph.py must not hard-code '#4A90E2' for agent nodes — use theme colors"
        )
        assert 'color="#50C878"' not in source, (
            "agent_graph.py must not hard-code '#50C878' for tool nodes — use theme colors"
        )
