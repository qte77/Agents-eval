"""
Tests for PeerRead tools error handling — ModelRetry instead of ValueError.

Validates that agent tools raise ModelRetry (routed back to LLM) instead of
ValueError (unhandled, crashes app) when operations fail.
"""

import json
from unittest.mock import Mock, patch

import pytest
from pydantic_ai import ModelRetry


def _register_tools(register_fn):
    """Register PeerRead tools via a capture decorator and return them by name.

    Args:
        register_fn: The add_*_tools_to_agent function to call.

    Returns:
        dict: Mapping of tool function name to the captured function.
    """
    mock_agent = Mock()
    captured: list = []

    def capture_tool(func):
        captured.append(func)
        return func

    mock_agent.tool = capture_tool
    register_fn(mock_agent, agent_id="test")
    return {fn.__name__: fn for fn in captured}


class TestGetPeerreadPaperModelRetry:
    """get_peerread_paper must raise ModelRetry, not ValueError."""

    @pytest.mark.asyncio
    async def test_raises_model_retry_on_not_found(self):
        """Paper not found -> ModelRetry so the LLM can recover."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        tools = _register_tools(add_peerread_tools_to_agent)
        get_paper = tools["get_peerread_paper"]

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_cls,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_tc,
        ):
            mock_loader_cls.return_value.get_paper_by_id.return_value = None
            mock_tc.return_value = Mock()

            with pytest.raises(ModelRetry, match="not found"):
                await get_paper(None, "nonexistent_id")

    @pytest.mark.asyncio
    async def test_raises_model_retry_on_loader_error(self):
        """Loader throws an exception -> ModelRetry, not ValueError."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        tools = _register_tools(add_peerread_tools_to_agent)
        get_paper = tools["get_peerread_paper"]

        with (
            patch("app.tools.peerread_tools.load_peerread_config") as mock_cfg,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_tc,
        ):
            mock_cfg.side_effect = RuntimeError("config broken")
            mock_tc.return_value = Mock()

            with pytest.raises(ModelRetry, match="Failed to retrieve paper"):
                await get_paper(None, "any_id")


class TestQueryPeerreadPapersModelRetry:
    """query_peerread_papers must raise ModelRetry on failure."""

    @pytest.mark.asyncio
    async def test_raises_model_retry_on_error(self):
        """Query failure -> ModelRetry."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        tools = _register_tools(add_peerread_tools_to_agent)
        query = tools["query_peerread_papers"]

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_cls,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_tc,
        ):
            mock_loader_cls.return_value.query_papers.side_effect = RuntimeError("db down")
            mock_tc.return_value = Mock()

            with pytest.raises(ModelRetry, match="Failed to query papers"):
                await query(None, venue="acl", min_reviews=1)


class TestGenerateReviewTemplateModelRetry:
    """generate_paper_review_content_from_template must raise ModelRetry."""

    @pytest.mark.asyncio
    async def test_raises_model_retry_on_not_found(self):
        """Paper not found during review generation -> ModelRetry."""
        from app.tools.peerread_tools import add_peerread_review_tools_to_agent

        tools = _register_tools(add_peerread_review_tools_to_agent)
        generate = tools["generate_paper_review_content_from_template"]

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_cls,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_tc,
        ):
            mock_loader_cls.return_value.get_paper_by_id.return_value = None
            mock_tc.return_value = Mock()

            with pytest.raises(ModelRetry, match="not found"):
                await generate(None, paper_id="missing_paper")


class TestSystemPromptContainsToolGuidance:
    """System prompt must guide the LLM on when to use paper tools."""

    def test_system_prompt_has_tool_usage_guidance(self):
        """config_chat.json system_prompt_manager should tell the LLM
        to only use paper tools for paper-related queries."""
        config_path = "src/app/config/config_chat.json"
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

        prompt = config["prompts"]["system_prompt_manager"]
        prompt_lower = prompt.lower()

        # Must mention that tools are for paper-related queries
        assert "paper" in prompt_lower, "Prompt should mention papers"
        assert any(keyword in prompt_lower for keyword in ["tool", "peerread"]), (
            "Prompt should mention tools or PeerRead"
        )
        assert any(
            keyword in prompt_lower
            for keyword in ["conversational", "general question", "not related to paper"]
        ), "Prompt should guide on handling non-paper queries"
