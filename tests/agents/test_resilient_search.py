"""
Tests for resilient search tool wrapper (STORY-010).

Expected behavior:
- HTTPError from search tools does not crash the agent run
- General exceptions from search tools return a descriptive error string
- Warning is logged when search fails, including error context
- Successful tool calls pass through results normally
- Wrapper applies to both DuckDuckGo and Tavily tools
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai.tools import Tool

from app.agents.agent_system import resilient_tool_wrapper


@pytest.fixture
def make_tool():
    """Factory to create a Tool wrapping a given async function."""

    def _make(func, name="test_search"):
        return Tool(func, name=name, description="Test search tool")

    return _make


@pytest.mark.asyncio
async def test_resilient_wrapper_catches_http_error_and_returns_string(make_tool):
    """HTTPError from search tool MUST be caught and an error string returned."""
    import httpx

    async def failing_tool(query: str) -> str:
        raise httpx.HTTPStatusError(
            "403 Forbidden",
            request=MagicMock(),
            response=MagicMock(status_code=403),
        )

    original_tool = make_tool(failing_tool)
    wrapped = resilient_tool_wrapper(original_tool)

    # Call the wrapped function directly
    result = await wrapped.function("test query")
    assert isinstance(result, str)
    assert "error" in result.lower() or "unavailable" in result.lower()


@pytest.mark.asyncio
async def test_resilient_wrapper_catches_429_rate_limit(make_tool):
    """429 rate limit error MUST be caught and an error string returned."""
    import httpx

    async def rate_limited_tool(query: str) -> str:
        raise httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=MagicMock(),
            response=MagicMock(status_code=429),
        )

    original_tool = make_tool(rate_limited_tool)
    wrapped = resilient_tool_wrapper(original_tool)

    result = await wrapped.function("test query")
    assert isinstance(result, str)
    assert "error" in result.lower() or "unavailable" in result.lower()


@pytest.mark.asyncio
async def test_resilient_wrapper_catches_general_exception_and_returns_string(make_tool):
    """General exceptions from search tool MUST be caught and an error string returned."""

    async def broken_tool(query: str) -> str:
        raise ConnectionError("Network unreachable")

    original_tool = make_tool(broken_tool)
    wrapped = resilient_tool_wrapper(original_tool)

    result = await wrapped.function("test query")
    assert isinstance(result, str)
    assert "error" in result.lower() or "unavailable" in result.lower()


@pytest.mark.asyncio
async def test_resilient_wrapper_logs_warning_on_failure(make_tool):
    """Warning MUST be logged at logger.warning level when search fails."""

    async def broken_tool(query: str) -> str:
        raise RuntimeError("Some search error")

    original_tool = make_tool(broken_tool)
    wrapped = resilient_tool_wrapper(original_tool)

    with patch("app.agents.agent_system.logger") as mock_logger:
        await wrapped.function("test query")
        assert mock_logger.warning.called, "Expected logger.warning to be called on failure"


@pytest.mark.asyncio
async def test_resilient_wrapper_logs_warning_with_http_status(make_tool):
    """Warning log MUST include HTTP status code when HTTPStatusError occurs."""
    import httpx

    async def forbidden_tool(query: str) -> str:
        raise httpx.HTTPStatusError(
            "403 Forbidden",
            request=MagicMock(),
            response=MagicMock(status_code=403),
        )

    original_tool = make_tool(forbidden_tool, name="duckduckgo_search")
    wrapped = resilient_tool_wrapper(original_tool)

    with patch("app.agents.agent_system.logger") as mock_logger:
        await wrapped.function("test query")
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any(
            "403" in msg for msg in warning_calls
        ), f"Expected 403 in warning log, got: {warning_calls}"


@pytest.mark.asyncio
async def test_resilient_wrapper_passes_through_on_success(make_tool):
    """Successful tool calls MUST pass through results without modification."""
    expected = [{"title": "Result 1", "href": "https://example.com"}]

    async def good_tool(query: str) -> list[dict]:
        return expected

    original_tool = make_tool(good_tool)
    wrapped = resilient_tool_wrapper(original_tool)

    result = await wrapped.function("test query")
    assert result == expected


@pytest.mark.asyncio
async def test_resilient_wrapper_preserves_tool_name_and_description(make_tool):
    """Wrapped tool MUST preserve the original tool name and description."""

    async def good_tool(query: str) -> str:
        return "results"

    original_tool = Tool(
        good_tool,
        name="duckduckgo_search",
        description="Searches DuckDuckGo for the given query and returns the results.",
    )
    wrapped = resilient_tool_wrapper(original_tool)

    assert wrapped.name == original_tool.name
    assert wrapped.description == original_tool.description


@pytest.mark.asyncio
async def test_resilient_wrapper_catches_ddgs_exception(make_tool):
    """DDGSException from ddgs library MUST be caught and an error string returned."""
    from ddgs.exceptions import DDGSException

    async def ddgs_failing_tool(query: str) -> str:
        raise DDGSException("Rate limit exceeded by ddgs")

    original_tool = make_tool(ddgs_failing_tool, name="duckduckgo_search")
    wrapped = resilient_tool_wrapper(original_tool)

    result = await wrapped.function("test query")
    assert isinstance(result, str)
    assert "error" in result.lower() or "unavailable" in result.lower()


def test_resilient_wrapper_returns_tool_instance(make_tool):
    """resilient_tool_wrapper MUST return a Tool instance."""

    async def any_tool(query: str) -> str:
        return "results"

    original_tool = make_tool(any_tool)
    wrapped = resilient_tool_wrapper(original_tool)

    assert isinstance(wrapped, Tool)
