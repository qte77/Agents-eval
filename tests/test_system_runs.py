"""
Tests for SimpleAgent creation and tool usage.
"""

from pydantic_ai import Agent
from pydantic_ai.result import RunResult
from utils.tools import roll_die  # , get_player_name
from utils.agents import create_agent_with_tool, SimpleAgent


MODEL_NAME: str = "ollama:llama3.1"


def test_agent_existence() -> None:
    """Verify that a SimpleAgent instance can be created successfully."""

    agent: SimpleAgent = SimpleAgent()
    assert isinstance(agent, Agent), "Agent should be created successfully"


def test_create_agent_with_tool() -> None:
    """Ensure that Agent can add and use a correctly."""

    agent: Agent = create_agent_with_tool(roll_die, MODEL_NAME)
    result: RunResult = agent.run_sync("1")
    data: str = result.data
    assert 1 <= int(data) <= 6, "Tool should return a number between 1 and 6."
