"""Tests for STORY-010: Fix navigation consistency and baseline expander.

Covers:
- PAGES list matches page header text constants
- Baseline comparison expander expanded by default when no result exists
- Phoenix Trace Viewer wrapped in collapsed sidebar expander
- Page dispatch in run_gui.py matches updated PAGES values

Mock strategy:
- Streamlit sidebar and widgets patched throughout
- No real Streamlit runtime needed
"""

from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helper: dict-like session state with attribute access (from test pattern)
# ---------------------------------------------------------------------------
class _SessionDict(dict):
    """Minimal session-state stub supporting both dict and attribute access."""

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
# 1. PAGES list matches page header text
# ---------------------------------------------------------------------------


class TestPagesMatchHeaders:
    """PAGES sidebar labels must align with page header text constants.

    AC: Sidebar navigation labels align with page headers.
    AC: Update PAGES list in config.py to match page header text.
    """

    def test_pages_contains_run_research_app(self) -> None:
        """PAGES must contain 'Run Research App' matching RUN_APP_HEADER."""
        from gui.config.config import PAGES

        assert "Run Research App" in PAGES, (
            f"PAGES must contain 'Run Research App' to match RUN_APP_HEADER, got: {PAGES}"
        )

    def test_pages_contains_evaluation_results(self) -> None:
        """PAGES must contain 'Evaluation Results' matching EVALUATION_HEADER."""
        from gui.config.config import PAGES

        assert "Evaluation Results" in PAGES, (
            f"PAGES must contain 'Evaluation Results' to match EVALUATION_HEADER, got: {PAGES}"
        )

    def test_pages_contains_settings(self) -> None:
        """PAGES must still contain 'Settings' matching SETTINGS_HEADER."""
        from gui.config.config import PAGES

        assert "Settings" in PAGES, f"PAGES must contain 'Settings', got: {PAGES}"

    def test_pages_contains_agent_graph(self) -> None:
        """PAGES must contain 'Agent Graph' (short form of Agent Interaction Graph header)."""
        from gui.config.config import PAGES

        assert "Agent Graph" in PAGES, f"PAGES must contain 'Agent Graph', got: {PAGES}"

    def test_pages_has_exactly_four_entries(self) -> None:
        """PAGES must have exactly four entries."""
        from gui.config.config import PAGES

        assert len(PAGES) == 4, f"PAGES must have exactly 4 entries, got {len(PAGES)}: {PAGES}"

    def test_pages_does_not_contain_bare_run(self) -> None:
        """PAGES must NOT contain bare 'Run' (old value)."""
        from gui.config.config import PAGES

        assert "Run" not in PAGES, (
            f"PAGES must not contain bare 'Run' (should be 'Run Research App'), got: {PAGES}"
        )

    def test_pages_does_not_contain_bare_evaluation(self) -> None:
        """PAGES must NOT contain bare 'Evaluation' (old value)."""
        from gui.config.config import PAGES

        assert "Evaluation" not in PAGES, (
            f"PAGES must not contain bare 'Evaluation' (should be 'Evaluation Results'), got: {PAGES}"
        )


# ---------------------------------------------------------------------------
# 2. Baseline expander expanded by default when no result exists
# ---------------------------------------------------------------------------


class TestBaselineExpanderDefault:
    """Baseline comparison expander must be expanded=True in empty state.

    AC: Baseline comparison expander expanded by default on first visit
        (no result available).
    AC: Set expanded=True on baseline comparison expander when no result exists.
    """

    def test_empty_state_expander_expanded_true(self) -> None:
        """_render_empty_state must call st.expander with expanded=True.

        Arrange: Mock st.expander to capture kwargs
        Act: Call _render_empty_state
        Expected: expanded=True in the expander call
        """
        captured_calls: list[dict] = []

        mock_expander_ctx = MagicMock()
        mock_expander_ctx.__enter__ = MagicMock(return_value=None)
        mock_expander_ctx.__exit__ = MagicMock(return_value=False)

        def capture_expander(label, **kwargs):
            captured_calls.append({"label": label, **kwargs})
            return mock_expander_ctx

        with patch("gui.pages.evaluation.st") as mock_st:
            mock_st.expander.side_effect = capture_expander
            mock_st.info = MagicMock()
            mock_st.markdown = MagicMock()
            mock_st.text_input = MagicMock(return_value="")

            from gui.pages.evaluation import _render_empty_state

            _render_empty_state()

        baseline_calls = [c for c in captured_calls if "Baseline" in c["label"]]
        assert len(baseline_calls) == 1, f"Expected 1 baseline expander call, got {len(baseline_calls)}"
        assert baseline_calls[0].get("expanded") is True, (
            f"Baseline expander must have expanded=True in empty state, "
            f"got expanded={baseline_calls[0].get('expanded')}"
        )


# ---------------------------------------------------------------------------
# 3. Phoenix Trace Viewer in collapsed sidebar expander
# ---------------------------------------------------------------------------


class TestPhoenixInSidebarExpander:
    """Phoenix Trace Viewer must be wrapped in a sidebar expander.

    AC: Phoenix Trace Viewer moved to collapsed sidebar expander.
    AC: Wrap Phoenix link in st.sidebar.expander("Tracing (optional)").
    """

    def test_sidebar_has_tracing_expander(self) -> None:
        """render_sidebar must call sidebar.expander with 'Tracing (optional)'.

        Arrange: Mock sidebar to capture expander calls
        Act: Call render_sidebar
        Expected: sidebar.expander called with 'Tracing (optional)'
        """
        from gui.components.sidebar import render_sidebar

        expander_labels: list[str] = []

        mock_expander_ctx = MagicMock()
        mock_expander_ctx.__enter__ = MagicMock(return_value=MagicMock())
        mock_expander_ctx.__exit__ = MagicMock(return_value=False)

        mock_sidebar = MagicMock()
        mock_sidebar.radio.return_value = "Run Research App"

        def capture_expander(label, **kwargs):
            expander_labels.append(label)
            return mock_expander_ctx

        mock_sidebar.expander.side_effect = capture_expander

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        assert "Tracing (optional)" in expander_labels, (
            f"sidebar.expander must be called with 'Tracing (optional)', "
            f"got expander labels: {expander_labels}"
        )

    def test_phoenix_link_not_directly_on_sidebar(self) -> None:
        """Phoenix markdown link must NOT be called directly on sidebar (must be in expander).

        After wrapping in expander, sidebar.markdown should not contain the Phoenix link.
        """
        from gui.components.sidebar import render_sidebar

        mock_sidebar = MagicMock()
        mock_sidebar.radio.return_value = "Run Research App"

        mock_expander_ctx = MagicMock()
        mock_expander_ctx.__enter__ = MagicMock(return_value=MagicMock())
        mock_expander_ctx.__exit__ = MagicMock(return_value=False)
        mock_sidebar.expander.return_value = mock_expander_ctx

        with patch("gui.components.sidebar.sidebar", mock_sidebar):
            render_sidebar("Test App")

        # Check sidebar.markdown was not called with a Phoenix link
        for call in mock_sidebar.markdown.call_args_list:
            args = call[0] if call[0] else ()
            for arg in args:
                if isinstance(arg, str):
                    assert "Phoenix" not in arg, (
                        "Phoenix link must not be directly on sidebar.markdown — "
                        "it should be inside the Tracing expander"
                    )


# ---------------------------------------------------------------------------
# 4. Page dispatch matches updated PAGES values
# ---------------------------------------------------------------------------


class TestDispatchMatchesUpdatedPages:
    """run_gui.main must dispatch using updated PAGES string values.

    AC: PAGES values and dispatch logic must be consistent.
    """

    def test_dispatch_run_research_app(self) -> None:
        """run_gui.main must dispatch 'Run Research App' to render_app."""
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

    def test_dispatch_evaluation_results(self) -> None:
        """run_gui.main must dispatch 'Evaluation Results' to render_evaluation."""
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
            mock_st.session_state = _SessionDict()
            asyncio.run(__import__("run_gui").main())

        mock_render_evaluation.assert_called_once()
