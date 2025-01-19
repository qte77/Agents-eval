"""
Tests for SimpleAgent creation and tool usage.
"""

from pydantic_ai import Agent
from app import DummyTool, SimpleAgent
from tools import roll_die


def test_agent_existence():
    """
    Verify that a SimpleAgent instance can be created successfully.
    """

    agent = SimpleAgent()
    assert isinstance(agent, Agent), "Agent should be created successfully"


def test_agent_tool_usage():
    """
    Ensure that SimpleAgent can add and use a DummyTool correctly.
    """

    agent = SimpleAgent()
    tool = DummyTool(roll_die)
    agent.add_tool(tool)

    result = agent.use_tool("dummy_tool")
    assert result == "Tool used successfully", "Agent should be able to use the tool"
