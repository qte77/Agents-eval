"""Shared fixtures for tests/tools/ test modules.

Provides common tool test utilities. The capture_registered_tools helper
is re-exported here from root conftest.py so that existing imports from
``from conftest import capture_registered_tools`` continue to work.
Fixtures here are auto-discovered by pytest for all tests in this directory.
"""

from collections.abc import Callable
from unittest.mock import Mock


def capture_registered_tools(register_fn: Callable, agent_id: str = "test") -> dict:
    """Register agent tools via a capture decorator and return them by name.

    Re-exported from root conftest.py for subdirectory access.

    Args:
        register_fn: The add_*_tools_to_agent function to call.
        agent_id: Agent ID passed to the registration function.

    Returns:
        dict: Mapping of tool function name to the captured function.
    """
    mock_agent = Mock()
    captured: list = []

    def capture_tool(func):
        captured.append(func)
        return func

    mock_agent.tool = capture_tool
    register_fn(mock_agent, agent_id=agent_id)
    return {fn.__name__: fn for fn in captured}
