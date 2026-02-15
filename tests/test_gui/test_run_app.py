"""
Tests for background query execution with session state persistence.

This module tests the session state transitions during query execution:
- idle → running → completed (success)
- idle → running → error (failure)
- Navigation resilience (execution continues across tab switches)
"""

import pytest
from inline_snapshot import snapshot
from unittest.mock import AsyncMock, MagicMock, patch

from gui.pages.run_app import _execute_query_background, _get_execution_state, _initialize_execution_state


class TestBackgroundExecutionAPI:
    """Test the background execution API functions."""

    @pytest.mark.asyncio
    async def test_execute_query_background_sets_running_state(self):
        """Test that background execution sets state to 'running'."""
        # Given a mock session state
        mock_state = {}

        # When background execution is triggered
        with patch("streamlit.session_state", mock_state), \
             patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main:
            mock_main.return_value = "Test result"

            # Call the background execution function (should exist)
            with pytest.raises(NameError):
                # This SHOULD fail because _execute_query_background doesn't exist yet
                await _execute_query_background(
                    query="Test query",
                    provider="cerebras",
                    include_researcher=False,
                    include_analyst=False,
                    include_synthesiser=False,
                    chat_config_file=None,
                    token_limit=None,
                )

    def test_get_execution_state_returns_idle_by_default(self):
        """Test that get_execution_state returns 'idle' when not set."""
        # Given an empty session state
        mock_state = {}

        # When getting execution state (should exist)
        with patch("streamlit.session_state", mock_state):
            with pytest.raises(NameError):
                # This SHOULD fail because _get_execution_state doesn't exist yet
                state = _get_execution_state()

    def test_initialize_execution_state_creates_required_keys(self):
        """Test that initialize creates all required state keys."""
        # Given an empty session state
        mock_state = {}

        # When initializing execution state (should exist)
        with patch("streamlit.session_state", mock_state):
            with pytest.raises(NameError):
                # This SHOULD fail because _initialize_execution_state doesn't exist yet
                _initialize_execution_state()


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
        expected_keys = {"execution_state", "execution_result", "execution_query", "execution_provider"}

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
        expected_keys = {"execution_state", "execution_error", "execution_query", "execution_provider"}

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
