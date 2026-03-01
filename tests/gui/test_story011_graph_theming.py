"""Tests for STORY-011: Fix Pyvis graph contrast and color theming.

Covers:
- is_light_theme() correctly identifies light vs dark themes
- get_graph_font_color() returns correct font color per theme
- get_graph_node_colors() returns primaryColor and accentColor from active theme
- get_theme_bgcolor() returns backgroundColor from active theme dict
- agent_graph.py uses theme-aware colors (not hard-coded)

Mock strategy:
- st.session_state patched via _SessionDict for theme selection
- Pyvis Network patched to capture node/network constructor args
- No real Streamlit runtime needed
"""

from unittest.mock import MagicMock, patch

from gui.config.styling import THEMES


class _SessionDict(dict):
    """Dict that supports attribute access, mimicking st.session_state."""

    def __getattr__(self, key: str) -> object:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: object) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc


# ---------------------------------------------------------------------------
# 1. is_light_theme
# ---------------------------------------------------------------------------


class TestIsLightTheme:
    """Test is_light_theme identifies light themes correctly."""

    def test_nord_light_is_light(self) -> None:
        from gui.config.styling import is_light_theme

        assert is_light_theme("nord_light") is True

    def test_expanse_dark_is_not_light(self) -> None:
        from gui.config.styling import is_light_theme

        assert is_light_theme("expanse_dark") is False

    def test_tokyo_night_is_not_light(self) -> None:
        from gui.config.styling import is_light_theme

        assert is_light_theme("tokyo_night") is False

    def test_unknown_theme_is_not_light(self) -> None:
        from gui.config.styling import is_light_theme

        assert is_light_theme("nonexistent_theme") is False


# ---------------------------------------------------------------------------
# 2. get_active_theme_name / get_active_theme
# ---------------------------------------------------------------------------


class TestGetActiveTheme:
    """Test active theme retrieval from session state."""

    def test_get_active_theme_name_default(self) -> None:
        from gui.config.styling import get_active_theme_name

        with patch("streamlit.session_state", _SessionDict()):
            assert get_active_theme_name() == "expanse_dark"

    def test_get_active_theme_name_from_session(self) -> None:
        from gui.config.styling import get_active_theme_name

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "tokyo_night"}),
        ):
            assert get_active_theme_name() == "tokyo_night"

    def test_get_active_theme_returns_dict(self) -> None:
        from gui.config.styling import get_active_theme

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "nord_light"}),
        ):
            theme = get_active_theme()
            assert theme == THEMES["nord_light"]

    def test_get_active_theme_default_expanse_dark(self) -> None:
        from gui.config.styling import get_active_theme

        with patch("streamlit.session_state", _SessionDict()):
            theme = get_active_theme()
            assert theme == THEMES["expanse_dark"]


# ---------------------------------------------------------------------------
# 3. get_graph_font_color
# ---------------------------------------------------------------------------


class TestGetGraphFontColor:
    """Test font color selection based on active theme."""

    def test_light_theme_returns_black(self) -> None:
        from gui.config.styling import get_graph_font_color

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "nord_light"}),
        ):
            assert get_graph_font_color() == "#000000"

    def test_dark_theme_returns_light(self) -> None:
        from gui.config.styling import get_graph_font_color

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "expanse_dark"}),
        ):
            assert get_graph_font_color() == "#ECEFF4"

    def test_tokyo_night_returns_light(self) -> None:
        from gui.config.styling import get_graph_font_color

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "tokyo_night"}),
        ):
            assert get_graph_font_color() == "#ECEFF4"


# ---------------------------------------------------------------------------
# 4. get_graph_node_colors
# ---------------------------------------------------------------------------


class TestGetGraphNodeColors:
    """Test node color retrieval from active theme."""

    def test_expanse_dark_colors(self) -> None:
        from gui.config.styling import get_graph_node_colors

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "expanse_dark"}),
        ):
            agent_color, tool_color = get_graph_node_colors()
            assert agent_color == "#4A90E2"
            assert tool_color == "#50C878"

    def test_nord_light_colors(self) -> None:
        from gui.config.styling import get_graph_node_colors

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "nord_light"}),
        ):
            agent_color, tool_color = get_graph_node_colors()
            assert agent_color == "#5E81AC"
            assert tool_color == "#88C0D0"

    def test_tokyo_night_colors(self) -> None:
        from gui.config.styling import get_graph_node_colors

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "tokyo_night"}),
        ):
            agent_color, tool_color = get_graph_node_colors()
            assert agent_color == "#7AA2F7"
            assert tool_color == "#9ECE6A"


# ---------------------------------------------------------------------------
# 5. get_theme_bgcolor uses active theme dict
# ---------------------------------------------------------------------------


class TestGetThemeBgcolorFromActiveTheme:
    """Test that get_theme_bgcolor returns backgroundColor from active theme."""

    def test_expanse_dark_bgcolor(self) -> None:
        from gui.config.styling import get_theme_bgcolor

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "expanse_dark"}),
        ):
            assert get_theme_bgcolor() == "#0b0c10"

    def test_nord_light_bgcolor(self) -> None:
        from gui.config.styling import get_theme_bgcolor

        with patch(
            "streamlit.session_state",
            _SessionDict({"selected_theme": "nord_light"}),
        ):
            assert get_theme_bgcolor() == "#ECEFF4"


# ---------------------------------------------------------------------------
# 6. agent_graph.py uses theme-aware colors
# ---------------------------------------------------------------------------


class TestAgentGraphUsesThemeColors:
    """Test that agent_graph.py uses styling helpers instead of hard-coded colors."""

    def test_network_uses_theme_font_color(self) -> None:
        """Network constructor receives get_graph_font_color() not False."""
        import networkx as nx

        mock_net_instance = MagicMock()
        mock_net_cls = MagicMock(return_value=mock_net_instance)

        graph: nx.DiGraph[str] = nx.DiGraph()
        graph.add_node("a1", type="agent", label="Agent1")

        with (
            patch("gui.pages.agent_graph.Network", mock_net_cls),
            patch("gui.pages.agent_graph.get_theme_bgcolor", return_value="#0b0c10"),
            patch("gui.pages.agent_graph.get_graph_font_color", return_value="#ECEFF4"),
            patch(
                "gui.pages.agent_graph.get_graph_node_colors", return_value=("#4A90E2", "#50C878")
            ),
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.caption"),
            patch(
                "streamlit.expander",
                return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()),
            ),
            patch("streamlit.text"),
            patch("streamlit.markdown"),
            patch("streamlit.components.v1.html"),
            patch(
                "tempfile.NamedTemporaryFile",
                return_value=MagicMock(
                    __enter__=MagicMock(return_value=MagicMock(name="test.html")),
                    __exit__=MagicMock(),
                ),
            ),
            patch("pathlib.Path.read_text", return_value="<head></head>"),
            patch("pathlib.Path.unlink"),
        ):
            from gui.pages.agent_graph import render_agent_graph

            render_agent_graph(graph=graph)

            # Verify Network was called with theme font_color, not False
            net_call_kwargs = mock_net_cls.call_args
            assert net_call_kwargs is not None
            assert net_call_kwargs.kwargs.get("font_color") == "#ECEFF4" or (
                len(net_call_kwargs.args) > 5 and net_call_kwargs.args[5] == "#ECEFF4"
            )

    def test_agent_node_uses_theme_primary_color(self) -> None:
        """Agent nodes use theme primaryColor, not hard-coded #4A90E2."""
        import networkx as nx

        mock_net_instance = MagicMock()
        mock_net_cls = MagicMock(return_value=mock_net_instance)

        graph: nx.DiGraph[str] = nx.DiGraph()
        graph.add_node("a1", type="agent", label="Agent1")

        with (
            patch("gui.pages.agent_graph.Network", mock_net_cls),
            patch("gui.pages.agent_graph.get_theme_bgcolor", return_value="#0b0c10"),
            patch("gui.pages.agent_graph.get_graph_font_color", return_value="#ECEFF4"),
            patch(
                "gui.pages.agent_graph.get_graph_node_colors", return_value=("#7AA2F7", "#9ECE6A")
            ),
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.caption"),
            patch(
                "streamlit.expander",
                return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()),
            ),
            patch("streamlit.text"),
            patch("streamlit.markdown"),
            patch("streamlit.components.v1.html"),
            patch(
                "tempfile.NamedTemporaryFile",
                return_value=MagicMock(
                    __enter__=MagicMock(return_value=MagicMock(name="test.html")),
                    __exit__=MagicMock(),
                ),
            ),
            patch("pathlib.Path.read_text", return_value="<head></head>"),
            patch("pathlib.Path.unlink"),
        ):
            from gui.pages.agent_graph import render_agent_graph

            render_agent_graph(graph=graph)

            # Find add_node call for the agent
            add_node_calls = mock_net_instance.add_node.call_args_list
            assert len(add_node_calls) >= 1
            agent_call = add_node_calls[0]
            assert agent_call.kwargs.get("color") == "#7AA2F7"

    def test_tool_node_uses_theme_accent_color(self) -> None:
        """Tool nodes use theme accentColor, not hard-coded #50C878."""
        import networkx as nx

        mock_net_instance = MagicMock()
        mock_net_cls = MagicMock(return_value=mock_net_instance)

        graph: nx.DiGraph[str] = nx.DiGraph()
        graph.add_node("t1", type="tool", label="Tool1")

        with (
            patch("gui.pages.agent_graph.Network", mock_net_cls),
            patch("gui.pages.agent_graph.get_theme_bgcolor", return_value="#0b0c10"),
            patch("gui.pages.agent_graph.get_graph_font_color", return_value="#ECEFF4"),
            patch(
                "gui.pages.agent_graph.get_graph_node_colors", return_value=("#7AA2F7", "#9ECE6A")
            ),
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.caption"),
            patch(
                "streamlit.expander",
                return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()),
            ),
            patch("streamlit.text"),
            patch("streamlit.markdown"),
            patch("streamlit.components.v1.html"),
            patch(
                "tempfile.NamedTemporaryFile",
                return_value=MagicMock(
                    __enter__=MagicMock(return_value=MagicMock(name="test.html")),
                    __exit__=MagicMock(),
                ),
            ),
            patch("pathlib.Path.read_text", return_value="<head></head>"),
            patch("pathlib.Path.unlink"),
        ):
            from gui.pages.agent_graph import render_agent_graph

            render_agent_graph(graph=graph)

            add_node_calls = mock_net_instance.add_node.call_args_list
            assert len(add_node_calls) >= 1
            tool_call = add_node_calls[0]
            assert tool_call.kwargs.get("color") == "#9ECE6A"
