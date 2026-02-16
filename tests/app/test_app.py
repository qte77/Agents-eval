"""
Tests for app.py main flow (STORY-002).

Validates that agent interaction graph is built whenever execution_id exists,
regardless of evaluation success (composite_result can be None).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_graph_built_when_skip_eval_and_execution_id_exists():
    """Test that graph is built even when evaluation is skipped (composite_result=None)."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.app._run_evaluation_if_enabled", new_callable=AsyncMock) as mock_eval,
        patch("app.app._build_graph_from_trace") as mock_build_graph,
        patch("app.app.load_config") as mock_load_config,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        mock_run_manager.return_value = "test_exec_123"  # Valid execution_id
        mock_eval.return_value = None  # No evaluation result (skipped)
        mock_build_graph.return_value = MagicMock()  # Mock graph object
        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with --skip-eval
        result = await main(
            chat_provider="test_provider",
            query="test query",
            skip_eval=True,
        )

        # Graph should be built even though composite_result is None
        mock_build_graph.assert_called_once_with("test_exec_123")
        assert result["graph"] is not None


@pytest.mark.asyncio
async def test_graph_built_when_evaluation_fails():
    """Test that graph is built even when evaluation fails (composite_result=None)."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.app._run_evaluation_if_enabled", new_callable=AsyncMock) as mock_eval,
        patch("app.app._build_graph_from_trace") as mock_build_graph,
        patch("app.app.load_config") as mock_load_config,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        mock_run_manager.return_value = "test_exec_456"  # Valid execution_id
        mock_eval.return_value = None  # Evaluation failed
        mock_build_graph.return_value = MagicMock()  # Mock graph object
        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with evaluation enabled but it fails
        result = await main(
            chat_provider="test_provider",
            query="test query",
            skip_eval=False,
        )

        # Graph should still be built when execution_id exists
        mock_build_graph.assert_called_once_with("test_exec_456")
        assert result["graph"] is not None


@pytest.mark.asyncio
async def test_graph_not_built_when_no_execution_id():
    """Test that graph is not built when execution_id is None."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.app._run_evaluation_if_enabled", new_callable=AsyncMock) as mock_eval,
        patch("app.app._build_graph_from_trace") as mock_build_graph,
        patch("app.app.load_config") as mock_load_config,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        mock_run_manager.return_value = None  # No execution_id
        mock_eval.return_value = None
        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main
        result = await main(
            chat_provider="test_provider",
            query="test query",
        )

        # Graph should not be built when no execution_id
        mock_build_graph.assert_not_called()
        # When no execution happens, result is None
        assert result is None
