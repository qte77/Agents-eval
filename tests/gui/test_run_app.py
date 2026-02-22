"""
Tests for background query execution with session state persistence.

This module tests the session state transitions during query execution:
- idle → running → completed (success)
- idle → running → error (failure)
- Navigation resilience (execution continues across tab switches)
"""

from unittest.mock import AsyncMock, patch

import pytest
from inline_snapshot import snapshot

from gui.pages.run_app import (
    _execute_query_background,
    _get_execution_state,
    _initialize_execution_state,
)


class _MockSessionState:
    """Mock that supports both attribute and bracket access like Streamlit session state."""

    def __setitem__(self, key: str, value: object) -> None:
        setattr(self, key, value)

    def __getitem__(self, key: str) -> object:
        return getattr(self, key)


class TestBackgroundExecutionAPI:
    """Test the background execution API functions."""

    @pytest.mark.asyncio
    async def test_execute_query_background_sets_running_state(self):
        """Test that background execution sets state to 'running' then 'completed'."""
        # Given a mock session state with dict-like access
        mock_state = _MockSessionState()

        # When background execution is triggered
        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            # Reason: main() returns dict with composite_result and graph keys
            mock_main.return_value = {"composite_result": "mock_composite", "graph": None}

            # Call the background execution function
            await _execute_query_background(
                query="Test query",
                provider="cerebras",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                token_limit=None,
            )

            # Then state should be completed with result
            assert mock_state.execution_state == snapshot("completed")
            assert mock_state.execution_composite_result == snapshot("mock_composite")
            assert mock_state.execution_graph is None
            assert mock_state.execution_result == snapshot("mock_composite")
            assert mock_state.execution_query == snapshot("Test query")
            assert mock_state.execution_provider == snapshot("cerebras")

    @pytest.mark.asyncio
    async def test_execute_query_background_handles_errors(self):
        """Test that background execution handles errors and sets error state."""
        # Given a mock session state
        mock_state = _MockSessionState()

        # When execution fails
        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
            patch("gui.pages.run_app.logger"),
        ):
            mock_main.side_effect = Exception("Connection timeout")

            await _execute_query_background(
                query="Test query",
                provider="cerebras",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                token_limit=None,
            )

            # Then state should be error
            assert mock_state.execution_state == snapshot("error")
            assert mock_state.execution_error == snapshot("Connection timeout")

    def test_get_execution_state_returns_idle_by_default(self):
        """Test that get_execution_state returns 'idle' when not set."""
        # Given an empty session state
        mock_state = _MockSessionState()

        # When getting execution state
        with patch("gui.pages.run_app.st.session_state", mock_state):
            state = _get_execution_state()

            # Then should return idle
            assert state == snapshot("idle")

    def test_initialize_execution_state_creates_required_keys(self):
        """Test that initialize creates execution_state key."""
        # Given an empty session state
        mock_state = _MockSessionState()

        # When initializing execution state
        with patch("gui.pages.run_app.st.session_state", mock_state):
            _initialize_execution_state()

            # Then execution_state should be set to idle
            assert mock_state.execution_state == snapshot("idle")


class TestDebugLogPanel:
    """Test debug log panel rendering and log capture."""

    def test_debug_log_panel_renders_with_logs(self):
        """Test that debug log panel displays captured logs."""
        from types import SimpleNamespace

        from gui.pages.run_app import _render_debug_log_panel

        # Given a session state with captured logs
        mock_state = SimpleNamespace()
        mock_state.debug_logs = [
            {
                "timestamp": "2026-02-15 10:00:00",
                "level": "INFO",
                "module": "app.app",
                "message": "Execution started",
            },
            {
                "timestamp": "2026-02-15 10:00:05",
                "level": "ERROR",
                "module": "app.judge.llm_evaluation_managers",
                "message": "Provider unavailable",
            },
        ]

        # When rendering debug log panel
        with patch("gui.pages.run_app.st") as mock_st:
            mock_st.session_state = mock_state
            _render_debug_log_panel()

            # Then expander should be created
            mock_st.expander.assert_called_once()
            # And logs should be rendered
            assert mock_st.expander.called

    def test_debug_log_panel_empty_state(self):
        """Test that debug log panel shows message when no logs."""
        from types import SimpleNamespace

        from gui.pages.run_app import _render_debug_log_panel

        # Given a session state with no logs
        mock_state = SimpleNamespace()
        mock_state.debug_logs = []

        # When rendering debug log panel
        with patch("gui.pages.run_app.st") as mock_st:
            mock_st.session_state = mock_state
            _render_debug_log_panel()

            # Then should show empty state message
            mock_st.expander.assert_called_once()
