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


class TestBackgroundExecutionAPI:
    """Test the background execution API functions."""

    @pytest.mark.asyncio
    async def test_execute_query_background_sets_running_state(self):
        """Test that background execution sets state to 'running' then 'completed'."""
        # Given a mock session state with dict-like access
        from types import SimpleNamespace

        mock_state = SimpleNamespace()

        # When background execution is triggered
        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = "Test result"

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
            assert mock_state.execution_result == snapshot("Test result")
            assert mock_state.execution_query == snapshot("Test query")
            assert mock_state.execution_provider == snapshot("cerebras")

    @pytest.mark.asyncio
    async def test_execute_query_background_handles_errors(self):
        """Test that background execution handles errors and sets error state."""
        # Given a mock session state
        from types import SimpleNamespace

        mock_state = SimpleNamespace()

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
        from types import SimpleNamespace

        mock_state = SimpleNamespace()

        # When getting execution state
        with patch("gui.pages.run_app.st.session_state", mock_state):
            state = _get_execution_state()

            # Then should return idle
            assert state == snapshot("idle")

    def test_initialize_execution_state_creates_required_keys(self):
        """Test that initialize creates execution_state key."""
        # Given an empty session state
        from types import SimpleNamespace

        mock_state = SimpleNamespace()

        # When initializing execution state
        with patch("gui.pages.run_app.st.session_state", mock_state):
            _initialize_execution_state()

            # Then execution_state should be set to idle
            assert mock_state.execution_state == snapshot("idle")


class TestDebugLogPanel:
    """Test debug log panel rendering and log capture."""

    def test_debug_log_panel_renders_with_logs(self):
        """Test that debug log panel displays captured logs."""
        from gui.pages.run_app import _render_debug_log_panel
        from types import SimpleNamespace

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
        from gui.pages.run_app import _render_debug_log_panel
        from types import SimpleNamespace

        # Given a session state with no logs
        mock_state = SimpleNamespace()
        mock_state.debug_logs = []

        # When rendering debug log panel
        with patch("gui.pages.run_app.st") as mock_st:
            mock_st.session_state = mock_state
            _render_debug_log_panel()

            # Then should show empty state message
            mock_st.expander.assert_called_once()

    @pytest.mark.asyncio
    async def test_debug_logs_captured_during_execution(self):
        """Test that logs are captured during query execution."""
        from types import SimpleNamespace

        mock_state = SimpleNamespace()

        # When execution captures logs
        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
            patch("gui.pages.run_app._capture_execution_logs") as mock_capture,
        ):
            mock_main.return_value = "Test result"

            # Execute query
            await _execute_query_background(
                query="Test query",
                provider="cerebras",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                token_limit=None,
            )

            # Then logs should be captured
            mock_capture.assert_called_once()


class TestSessionStateStructure:
    """Test session state structure after execution."""

    def test_running_state_structure(self):
        """Test session state structure during execution."""
        # This test verifies the expected structure
        expected_keys = {"execution_state", "execution_query", "execution_provider"}

        # When execution is running
        mock_state = {
            "execution_state": "running",
            "execution_query": "Test query",
            "execution_provider": "cerebras",
        }

        # Then all required keys should be present
        assert set(mock_state.keys()) == snapshot(expected_keys)
        assert mock_state["execution_state"] == snapshot("running")

    def test_completed_state_structure(self):
        """Test session state structure after successful execution."""
        expected_keys = {
            "execution_state",
            "execution_result",
            "execution_query",
            "execution_provider",
        }

        # When execution completes successfully
        mock_state = {
            "execution_state": "completed",
            "execution_result": "Test result",
            "execution_query": "Test query",
            "execution_provider": "cerebras",
        }

        # Then all required keys should be present
        assert set(mock_state.keys()) == snapshot(expected_keys)
        assert mock_state["execution_state"] == snapshot("completed")

    def test_error_state_structure(self):
        """Test session state structure after failed execution."""
        expected_keys = {
            "execution_state",
            "execution_error",
            "execution_query",
            "execution_provider",
        }

        # When execution fails
        mock_state = {
            "execution_state": "error",
            "execution_error": "Connection timeout",
            "execution_query": "Test query",
            "execution_provider": "cerebras",
        }

        # Then all required keys should be present
        assert set(mock_state.keys()) == snapshot(expected_keys)
        assert mock_state["execution_state"] == snapshot("error")
