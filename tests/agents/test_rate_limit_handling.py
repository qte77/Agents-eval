"""
Tests for graceful error handling in run_manager (STORY-008).

Expected behavior:
- 429 ModelHTTPError exits cleanly with SystemExit(1), no raw traceback
- Rate limit details (provider, model, wait time) are logged at ERROR level
- Non-429 ModelHTTPError re-raises for upstream handling
- UsageLimitExceeded exits cleanly with SystemExit(1)
- Trace collection finalizes on all error paths
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError, UsageLimitExceeded

from app.judge.trace_processors import TraceCollector


@pytest.mark.asyncio
async def test_rate_limit_exits_cleanly():
    """429 rate limit MUST raise SystemExit(1), not propagate raw exception."""
    with patch("app.agents.agent_system.get_trace_collector") as mock_get_collector:
        mock_collector = MagicMock(spec=TraceCollector)
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock(spec=Agent)
        mock_manager.model.model_name = "gpt-4.1"
        mock_manager.run = AsyncMock(
            side_effect=ModelHTTPError(
                status_code=429,
                model_name="gpt-4.1",
                body={
                    "code": "RateLimitReached",
                    "message": "Rate limit of 50 per 86400s exceeded. Please wait 34796 seconds.",
                },
            )
        )

        with pytest.raises(SystemExit) as exc_info:
            await run_manager(
                manager=mock_manager,
                query="test query",
                provider="github",
                usage_limits=None,
            )

        assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_rate_limit_logs_provider_and_wait_time():
    """Rate limit log MUST include provider, model name, and original detail message."""
    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
        patch("app.agents.agent_system.logger") as mock_logger,
    ):
        mock_collector = MagicMock(spec=TraceCollector)
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock(spec=Agent)
        mock_manager.model.model_name = "gpt-4.1"
        detail_msg = "Rate limit of 50 per 86400s exceeded. Please wait 34796 seconds."
        mock_manager.run = AsyncMock(
            side_effect=ModelHTTPError(
                status_code=429,
                model_name="gpt-4.1",
                body={"message": detail_msg},
            )
        )

        with pytest.raises(SystemExit):
            await run_manager(
                manager=mock_manager,
                query="test query",
                provider="github",
                usage_limits=None,
            )

        # Verify actionable error message
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        rate_limit_logged = any(
            "github" in msg and "gpt-4.1" in msg and "Rate limit" in msg for msg in error_calls
        )
        assert rate_limit_logged, f"Expected rate limit details in error log, got: {error_calls}"


@pytest.mark.asyncio
async def test_rate_limit_finalizes_trace_collection():
    """Trace collection MUST be finalized even when rate limit occurs."""
    with patch("app.agents.agent_system.get_trace_collector") as mock_get_collector:
        mock_collector = MagicMock(spec=TraceCollector)
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock(spec=Agent)
        mock_manager.model.model_name = "test-model"
        mock_manager.run = AsyncMock(
            side_effect=ModelHTTPError(
                status_code=429,
                model_name="test-model",
                body={"message": "rate limited"},
            )
        )

        with pytest.raises(SystemExit):
            await run_manager(
                manager=mock_manager,
                query="test query",
                provider="test_provider",
                usage_limits=None,
            )

        mock_collector.end_execution.assert_called_once()


@pytest.mark.asyncio
async def test_non_429_http_error_re_raises():
    """Non-429 ModelHTTPError (e.g. 500) MUST re-raise, not SystemExit."""
    with patch("app.agents.agent_system.get_trace_collector") as mock_get_collector:
        mock_collector = MagicMock(spec=TraceCollector)
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock(spec=Agent)
        mock_manager.model.model_name = "test-model"
        mock_manager.run = AsyncMock(
            side_effect=ModelHTTPError(
                status_code=500,
                model_name="test-model",
                body={"message": "Internal server error"},
            )
        )

        with pytest.raises(ModelHTTPError):
            await run_manager(
                manager=mock_manager,
                query="test query",
                provider="test_provider",
                usage_limits=None,
            )


@pytest.mark.asyncio
async def test_usage_limit_exceeded_exits_cleanly():
    """UsageLimitExceeded MUST raise SystemExit(1), not propagate raw exception."""
    with patch("app.agents.agent_system.get_trace_collector") as mock_get_collector:
        mock_collector = MagicMock(spec=TraceCollector)
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock(spec=Agent)
        mock_manager.model.model_name = "gpt-oss-120b"
        mock_manager.run = AsyncMock(
            side_effect=UsageLimitExceeded(
                "Exceeded the total_tokens_limit of 60000 (total_tokens=60339)"
            )
        )

        with pytest.raises(SystemExit) as exc_info:
            await run_manager(
                manager=mock_manager,
                query="test query",
                provider="cerebras",
                usage_limits=None,
            )

        assert exc_info.value.code == 1
        mock_collector.end_execution.assert_called_once()
