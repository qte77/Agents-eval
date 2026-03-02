"""
Tests for STORY-002: GUI layout refactor -- sidebar tabs.

Covers:
- Sidebar navigation uses st.sidebar.radio or st.sidebar.selectbox
- Navigation tabs are: Run, Settings, Evaluation, Agent Graph
- Tab selection key persists in session state across reruns
- run_gui.py has no TODO comment referencing sidebar tabs
- render_sidebar returns the selected tab name
- run_gui.main dispatches correctly to each page based on sidebar selection
- Settings page is NOT rendered inline on the Run page

Mock strategy:
- Streamlit sidebar and widgets patched throughout
- No real Streamlit runtime needed
- run_gui module imported with mocked dependencies
"""

from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# 1. Sidebar navigation tabs
# ---------------------------------------------------------------------------


class TestSidebarNavigationTabs:
    """Verify sidebar contains the four required navigation tabs.

    AC1: Sidebar contains navigation tabs for: Run, Settings, Evaluation, Agent Graph

    Note: sidebar.py imports `sidebar` directly from streamlit, so we patch
    `gui.components.sidebar.sidebar` to intercept calls correctly.
    """

    def _make_sidebar_mock(self, captured_options: list) -> MagicMock:
        """Create a sidebar mock that captures radio options."""
        mock_sidebar = MagicMock()

        def capture_radio(label, options, **kwargs):
            captured_options.extend(options)
            return options[0] if options else ""

        mock_sidebar.radio.side_effect = capture_radio
        return mock_sidebar

    def test_sidebar_radio_includes_run_tab(self) -> None:
        """Sidebar navigation must include a 'Run' tab.

        Arrange: Mock sidebar to capture options
        Act: Call render_sidebar
        Expected: 'Run' is in the options passed to sidebar.radio
        """
        from gui.components.sidebar import render_sidebar

        captured_options: list = []
        mock_sidebar = self._make_sidebar_mock(captured_options)

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert "Run Research App" in captured_options, (
            "Sidebar navigation must include 'Run Research App' tab"
        )

    def test_sidebar_radio_includes_settings_tab(self) -> None:
        """Sidebar navigation must include a 'Settings' tab.

        Arrange: Mock sidebar to capture options
        Act: Call render_sidebar
        Expected: 'Settings' is in the options passed to sidebar.radio
        """
        from gui.components.sidebar import render_sidebar

        captured_options: list = []
        mock_sidebar = self._make_sidebar_mock(captured_options)

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert "Settings" in captured_options, "Sidebar navigation must include 'Settings' tab"

    def test_sidebar_radio_includes_evaluation_tab(self) -> None:
        """Sidebar navigation must include an 'Evaluation' tab.

        Arrange: Mock sidebar to capture options
        Act: Call render_sidebar
        Expected: 'Evaluation' is in the options passed to sidebar.radio
        """
        from gui.components.sidebar import render_sidebar

        captured_options: list = []
        mock_sidebar = self._make_sidebar_mock(captured_options)

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert "Evaluation Results" in captured_options, (
            "Sidebar navigation must include 'Evaluation Results' tab"
        )

    def test_sidebar_radio_includes_agent_graph_tab(self) -> None:
        """Sidebar navigation must include an 'Agent Graph' tab.

        Arrange: Mock sidebar to capture options
        Act: Call render_sidebar
        Expected: 'Agent Graph' is in the options passed to sidebar.radio
        """
        from gui.components.sidebar import render_sidebar

        captured_options: list = []
        mock_sidebar = self._make_sidebar_mock(captured_options)

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert "Agent Graph" in captured_options, (
            "Sidebar navigation must include 'Agent Graph' tab"
        )

    def test_sidebar_navigation_has_exactly_four_tabs(self) -> None:
        """Sidebar navigation must have exactly four tabs: Run, Settings, Evaluation, Agent Graph.

        AC1: Sidebar contains navigation tabs for: Run, Settings, Evaluation, Agent Graph
        """
        from gui.components.sidebar import render_sidebar

        captured_options: list = []
        mock_sidebar = self._make_sidebar_mock(captured_options)

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert set(captured_options) == {
            "Run Research App",
            "Settings",
            "Evaluation Results",
            "Agent Graph",
            "Trace Viewer",
        }, f"Expected exactly 5 tabs, got: {captured_options}"


# ---------------------------------------------------------------------------
# 2. Tab selection persists in session state
# ---------------------------------------------------------------------------


class TestTabSelectionPersistence:
    """Verify tab selection uses a session_state key for persistence across reruns.

    AC4: Tab selection persists across Streamlit reruns within a session
    """

    def test_sidebar_radio_uses_key_for_persistence(self) -> None:
        """Sidebar radio must use a `key` parameter so Streamlit persists selection.

        Arrange: Mock sidebar to capture kwargs
        Act: Call render_sidebar
        Expected: `key` kwarg is passed to sidebar.radio

        Note: sidebar.py imports `sidebar` directly from streamlit, so we patch
        `gui.components.sidebar.sidebar` to intercept calls correctly.
        """
        from gui.components.sidebar import render_sidebar

        captured_kwargs: dict = {}

        def capture_radio(label, options, **kwargs):
            captured_kwargs.update(kwargs)
            return options[0] if options else ""

        mock_sidebar = MagicMock()
        mock_sidebar.radio.side_effect = capture_radio

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert "key" in captured_kwargs, (
            "Sidebar radio must use a `key` parameter for session state persistence"
        )


# ---------------------------------------------------------------------------
# 3. run_gui.py dispatches to correct pages
# ---------------------------------------------------------------------------


class TestRunGuiPageDispatch:
    """Verify run_gui.main dispatches to the correct page render functions.

    AC2: Settings page is accessible via its own sidebar tab
    AC5: All existing GUI functionality works unchanged after layout refactor
    """

    def test_run_tab_calls_render_app(self) -> None:
        """When 'Run' tab is selected, render_app must be called.

        Arrange: Mock render_sidebar to return 'Run', mock render_app
        Act: Call run_gui.main via asyncio.run
        Expected: render_app is called
        """
        import asyncio

        with (
            patch("run_gui.render_sidebar", return_value="Run Research App"),
            patch("run_gui.render_app") as mock_render_app,
            patch("run_gui.add_custom_styling"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_settings"),
            patch("run_gui.render_evaluation"),
            patch("run_gui.render_agent_graph"),
        ):
            mock_render_app.return_value = None
            asyncio.run(__import__("run_gui").main())

        mock_render_app.assert_called_once()

    def test_settings_tab_calls_render_settings(self) -> None:
        """When 'Settings' tab is selected, render_settings must be called.

        AC2: Settings page is accessible via its own sidebar tab (not inline on Run page)
        """
        import asyncio

        with (
            patch("run_gui.render_sidebar", return_value="Settings"),
            patch("run_gui.render_app"),
            patch("run_gui.add_custom_styling"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_settings") as mock_render_settings,
            patch("run_gui.render_evaluation"),
            patch("run_gui.render_agent_graph"),
        ):
            asyncio.run(__import__("run_gui").main())

        mock_render_settings.assert_called_once()

    def test_evaluation_tab_calls_render_evaluation(self) -> None:
        """When 'Evaluation' tab is selected, render_evaluation must be called."""
        import asyncio

        with (
            patch("run_gui.render_sidebar", return_value="Evaluation Results"),
            patch("run_gui.render_app"),
            patch("run_gui.add_custom_styling"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_settings"),
            patch("run_gui.render_evaluation") as mock_render_evaluation,
            patch("run_gui.render_agent_graph"),
            patch("run_gui.st") as mock_st,
        ):
            mock_st.session_state = {}
            asyncio.run(__import__("run_gui").main())

        mock_render_evaluation.assert_called_once()

    def test_agent_graph_tab_calls_render_agent_graph(self) -> None:
        """When 'Agent Graph' tab is selected, render_agent_graph must be called."""
        import asyncio

        with (
            patch("run_gui.render_sidebar", return_value="Agent Graph"),
            patch("run_gui.render_app"),
            patch("run_gui.add_custom_styling"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_settings"),
            patch("run_gui.render_evaluation"),
            patch("run_gui.render_agent_graph") as mock_render_agent_graph,
            patch("run_gui.st") as mock_st,
        ):
            mock_st.session_state = {}
            asyncio.run(__import__("run_gui").main())

        mock_render_agent_graph.assert_called_once()

    def test_settings_not_called_when_run_tab_selected(self) -> None:
        """render_settings must NOT be called when 'Run' tab is selected.

        AC2: Settings is NOT inline on the Run page — it has its own tab.
        """
        import asyncio

        with (
            patch("run_gui.render_sidebar", return_value="Run Research App"),
            patch("run_gui.render_app") as mock_render_app,
            patch("run_gui.add_custom_styling"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_settings") as mock_render_settings,
            patch("run_gui.render_evaluation"),
            patch("run_gui.render_agent_graph"),
        ):
            mock_render_app.return_value = None
            asyncio.run(__import__("run_gui").main())

        mock_render_settings.assert_not_called()


# ---------------------------------------------------------------------------
# 4. PAGES constant reflects the new tab structure
# ---------------------------------------------------------------------------


class TestPagesConstant:
    """Verify gui.config.config.PAGES reflects the new four-tab structure.

    The PAGES list drives the sidebar navigation options.
    """

    def test_pages_contains_run(self) -> None:
        """PAGES must contain 'Run'."""
        from gui.config.config import PAGES

        assert "Run Research App" in PAGES, f"PAGES must contain 'Run Research App', got: {PAGES}"

    def test_pages_contains_settings(self) -> None:
        """PAGES must contain 'Settings'."""
        from gui.config.config import PAGES

        assert "Settings" in PAGES, f"PAGES must contain 'Settings', got: {PAGES}"

    def test_pages_contains_evaluation(self) -> None:
        """PAGES must contain 'Evaluation'."""
        from gui.config.config import PAGES

        assert "Evaluation Results" in PAGES, (
            f"PAGES must contain 'Evaluation Results', got: {PAGES}"
        )

    def test_pages_contains_agent_graph(self) -> None:
        """PAGES must contain 'Agent Graph'."""
        from gui.config.config import PAGES

        assert "Agent Graph" in PAGES, f"PAGES must contain 'Agent Graph', got: {PAGES}"

    def test_pages_has_exactly_five_entries(self) -> None:
        """PAGES must have exactly five entries including Trace Viewer."""
        from gui.config.config import PAGES

        assert set(PAGES) == {
            "Run Research App",
            "Settings",
            "Evaluation Results",
            "Agent Graph",
            "Trace Viewer",
        }, f"Expected exactly 5 PAGES entries, got: {PAGES}"


# ---------------------------------------------------------------------------
# 5. No TODO comment in run_gui.py
# ---------------------------------------------------------------------------


class TestNoTodoComment:
    """Verify run_gui.py contains no TODO comments.

    AC6: The TODO comment at run_gui.py:43 is removed
    """

    def test_run_gui_has_no_todo_comment(self) -> None:
        """run_gui.py must not contain any TODO comments.

        AC6: The TODO comment at run_gui.py:43 is removed
        """
        import importlib.util
        from pathlib import Path

        # Find run_gui.py source file
        spec = importlib.util.find_spec("run_gui")
        assert spec is not None, "run_gui module must be importable"
        assert spec.origin is not None, "run_gui module must have an origin file"

        source = Path(spec.origin).read_text()
        lines_with_todo = [
            (i + 1, line.strip()) for i, line in enumerate(source.splitlines()) if "TODO" in line
        ]

        assert not lines_with_todo, (
            "run_gui.py must not contain TODO comments. Found:\n"
            + "\n".join(f"  Line {n}: {line}" for n, line in lines_with_todo)
        )


# ---------------------------------------------------------------------------
# 6. run_gui.main dispatches to Run page (not deprecated page names)
# ---------------------------------------------------------------------------


class TestRunGuiDoesNotUseOldPageNames:
    """Verify run_gui.main does not dispatch to old page names (App, Home, Prompts).

    The refactor removes Home, Prompts, and App from the navigation.
    """

    def test_run_gui_dispatch_does_not_use_home(self) -> None:
        """run_gui.main source must not dispatch on 'Home' page name."""
        import importlib.util
        from pathlib import Path

        spec = importlib.util.find_spec("run_gui")
        assert spec is not None
        assert spec.origin is not None
        source = Path(spec.origin).read_text()

        # The dispatch block should not check for "Home" page
        # (inspect the main() function source)
        # We look at the dispatch logic — it should not contain == "Home"
        assert '== "Home"' not in source, (
            "run_gui.main must not dispatch to 'Home' page — it was removed in sidebar refactor"
        )

    def test_run_gui_dispatch_does_not_use_prompts(self) -> None:
        """run_gui.main source must not dispatch on 'Prompts' page name."""
        import importlib.util
        from pathlib import Path

        spec = importlib.util.find_spec("run_gui")
        assert spec is not None
        assert spec.origin is not None
        source = Path(spec.origin).read_text()

        assert '== "Prompts"' not in source, (
            "run_gui.main must not dispatch to 'Prompts' page — it was removed in sidebar refactor"
        )

    def test_run_gui_dispatch_does_not_use_app_page_name(self) -> None:
        """run_gui.main source must not dispatch on 'App' page name."""
        import importlib.util
        from pathlib import Path

        spec = importlib.util.find_spec("run_gui")
        assert spec is not None
        assert spec.origin is not None
        source = Path(spec.origin).read_text()

        assert '== "App"' not in source, (
            "run_gui.main must not dispatch to 'App' page — it was renamed to 'Run' in sidebar refactor"
        )
