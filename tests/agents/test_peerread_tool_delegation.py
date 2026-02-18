"""
Tests for PeerRead tool delegation to researcher agent.

This module validates that PeerRead tools are correctly placed on the researcher
agent in multi-agent mode and fall back to the manager in single-agent mode.
"""

import pytest

from app.agents.agent_system import get_manager
from app.data_models.app_models import ProviderConfig


@pytest.fixture
def test_prompts() -> dict[str, str]:
    """Fixture providing test prompts for agent system."""
    return {
        "system_prompt_manager": "You are a manager agent.",
        "system_prompt_researcher": "You are a researcher agent.",
        "system_prompt_analyst": "You are an analyst agent.",
        "system_prompt_synthesiser": "You are a synthesiser agent.",
    }


@pytest.fixture
def test_provider_config() -> ProviderConfig:
    """Fixture providing test provider configuration."""
    return ProviderConfig(
        provider="openai",
        model_name="gpt-4o-mini",
        base_url="https://api.openai.com/v1",
    )


def _get_tool_names(agent) -> set[str]:
    """Extract tool names from an agent's function toolset."""
    # tools is a dict mapping name -> tool
    return set(agent._function_toolset.tools.keys())


def test_multi_agent_peerread_tools_on_researcher(
    test_prompts: dict[str, str],
    test_provider_config: ProviderConfig,
) -> None:
    """Test that PeerRead tools are on researcher in multi-agent mode.

    Acceptance criteria:
    - When include_researcher=True: PeerRead base tools on researcher, not manager
    - Manager retains only delegation tools
    - Researcher has: PeerRead tools + duckduckgo_search_tool
    """
    manager = get_manager(
        provider="openai",
        provider_config=test_provider_config,
        api_key="test-key",
        prompts=test_prompts,
        include_researcher=True,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=False,
    )

    # Get manager's tools
    manager_tool_names = _get_tool_names(manager)

    # Verify manager has delegation tool for researcher
    assert "delegate_research" in manager_tool_names, "Manager should have delegate_research tool"

    # Verify PeerRead tools are NOT on manager in multi-agent mode
    peerread_base_tools = ["get_peerread_paper", "query_peerread_papers", "read_paper_pdf_tool"]
    for tool_name in peerread_base_tools:
        assert tool_name not in manager_tool_names, (
            f"PeerRead tool '{tool_name}' should NOT be on manager in multi-agent mode"
        )

    # Note: We cannot easily access the researcher agent to verify its tools without
    # running the agent. The key verification is that PeerRead tools are NOT on manager.
    # Integration tests with actual agent execution will verify researcher has the tools.


def test_single_agent_peerread_tools_on_manager(
    test_prompts: dict[str, str],
    test_provider_config: ProviderConfig,
) -> None:
    """Test that PeerRead tools fall back to manager in single-agent mode.

    Acceptance criteria:
    - When include_researcher=False: PeerRead base tools on manager (fallback)
    - Single-agent mode produces correct tool registration
    """
    manager = get_manager(
        provider="openai",
        provider_config=test_provider_config,
        api_key="test-key",
        prompts=test_prompts,
        include_researcher=False,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=False,
    )

    # Get manager's tools
    manager_tool_names = _get_tool_names(manager)

    # Verify PeerRead tools are on manager in single-agent mode
    peerread_base_tools = ["get_peerread_paper", "query_peerread_papers", "get_paper_content"]

    for tool_name in peerread_base_tools:
        assert tool_name in manager_tool_names, (
            f"PeerRead tool '{tool_name}' should be on manager in single-agent mode"
        )

    # Verify no delegation tools in single-agent mode
    assert "delegate_research" not in manager_tool_names, (
        "Manager should not have delegate_research tool in single-agent mode"
    )


def test_multi_agent_review_tools_on_researcher(
    test_prompts: dict[str, str],
    test_provider_config: ProviderConfig,
) -> None:
    """Test that review tools are on researcher in multi-agent mode.

    Acceptance criteria (STORY-008):
    - When include_researcher=True and enable_review_tools=True:
      review tools registered on researcher agent, not manager
    - Manager retains only delegation tools in multi-agent mode
    - Researcher has: PeerRead base tools + review tools + duckduckgo_search_tool
    """
    manager = get_manager(
        provider="openai",
        provider_config=test_provider_config,
        api_key="test-key",
        prompts=test_prompts,
        include_researcher=True,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=True,
    )

    # Get manager's tools
    manager_tool_names = _get_tool_names(manager)

    # Verify manager has delegation tool for researcher
    assert "delegate_research" in manager_tool_names, "Manager should have delegate_research tool"

    # Verify review tools are NOT on manager in multi-agent mode
    review_tools = [
        "generate_paper_review_content_from_template",
        "save_paper_review",
        "save_structured_review",
    ]
    for tool_name in review_tools:
        assert tool_name not in manager_tool_names, (
            f"Review tool '{tool_name}' should NOT be on manager in multi-agent mode"
        )


def test_single_agent_review_tools_on_manager(
    test_prompts: dict[str, str],
    test_provider_config: ProviderConfig,
) -> None:
    """Test that review tools fall back to manager in single-agent mode.

    Acceptance criteria (STORY-008):
    - When include_researcher=False and enable_review_tools=True:
      review tools registered on manager agent (single-agent fallback)
    - Single-agent mode produces correct review output (no regression)
    """
    manager = get_manager(
        provider="openai",
        provider_config=test_provider_config,
        api_key="test-key",
        prompts=test_prompts,
        include_researcher=False,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=True,
    )

    # Get manager's tools
    manager_tool_names = _get_tool_names(manager)

    # Verify review tools are on manager in single-agent mode
    review_tools = [
        "generate_paper_review_content_from_template",
        "save_paper_review",
        "save_structured_review",
    ]

    for tool_name in review_tools:
        assert tool_name in manager_tool_names, (
            f"Review tool '{tool_name}' should be on manager in single-agent mode"
        )

    # Verify PeerRead base tools also on manager in single-agent mode
    peerread_base_tools = ["get_peerread_paper", "query_peerread_papers", "get_paper_content"]
    for tool_name in peerread_base_tools:
        assert tool_name in manager_tool_names, (
            f"PeerRead tool '{tool_name}' should be on manager in single-agent mode"
        )


def test_review_tools_disabled_when_flag_false(
    test_prompts: dict[str, str],
    test_provider_config: ProviderConfig,
) -> None:
    """Test that review tools are not added when enable_review_tools=False.

    Acceptance criteria (STORY-008):
    - When enable_review_tools=False: no review tools on any agent
    - Works correctly in both single-agent and multi-agent modes
    """
    # Test multi-agent mode
    manager_multi = get_manager(
        provider="openai",
        provider_config=test_provider_config,
        api_key="test-key",
        prompts=test_prompts,
        include_researcher=True,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=False,
    )

    manager_multi_tools = _get_tool_names(manager_multi)
    review_tools = [
        "generate_paper_review_content_from_template",
        "save_paper_review",
        "save_structured_review",
    ]

    for tool_name in review_tools:
        assert tool_name not in manager_multi_tools, (
            f"Review tool '{tool_name}' should not exist when enable_review_tools=False (multi-agent)"
        )

    # Test single-agent mode
    manager_single = get_manager(
        provider="openai",
        provider_config=test_provider_config,
        api_key="test-key",
        prompts=test_prompts,
        include_researcher=False,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=False,
    )

    manager_single_tools = _get_tool_names(manager_single)

    for tool_name in review_tools:
        assert tool_name not in manager_single_tools, (
            f"Review tool '{tool_name}' should not exist when enable_review_tools=False (single-agent)"
        )
