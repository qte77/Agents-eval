"""Tests for run_manager() accepting external execution_id.

Verifies that run_manager() uses a provided execution_id instead of
generating its own, and falls back to auto-generation when not provided.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
class TestRunManagerExecutionId:
    """Tests for external execution_id forwarding in run_manager()."""

    @pytest.fixture
    def _mock_trace_collector(self):
        """Patch get_trace_collector to return a mock collector."""
        mock_collector = MagicMock()
        with patch("app.agents.agent_system.get_trace_collector", return_value=mock_collector):
            yield mock_collector

    @pytest.fixture
    def _mock_manager(self):
        """Create a mock Agent with a successful run result."""
        manager = MagicMock()
        mock_result = MagicMock()
        mock_result.output = "test output"
        mock_result.usage.return_value = {}
        manager.run = AsyncMock(return_value=mock_result)
        # Provide model attribute for logging
        manager.model = "test-model"
        return manager

    async def test_run_manager_uses_provided_execution_id(
        self, _mock_trace_collector: MagicMock, _mock_manager: MagicMock
    ) -> None:
        """run_manager() uses the provided execution_id when given."""
        from app.agents.agent_system import run_manager

        execution_id, _ = await run_manager(
            _mock_manager,
            "test query",
            "test_provider",
            None,
            execution_id="ext-id-123",
        )

        assert execution_id == "ext-id-123"
        _mock_trace_collector.start_execution.assert_called_once_with("ext-id-123")

    async def test_run_manager_generates_id_when_not_provided(
        self, _mock_trace_collector: MagicMock, _mock_manager: MagicMock
    ) -> None:
        """run_manager() auto-generates exec_{{hex}} id when not provided."""
        from app.agents.agent_system import run_manager

        execution_id, _ = await run_manager(
            _mock_manager,
            "test query",
            "test_provider",
            None,
        )

        assert execution_id.startswith("exec_")
        assert len(execution_id) == 17  # "exec_" + 12 hex chars
