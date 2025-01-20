"""
Tests for SimpleAgent creation and tool usage.
"""

from pydantic_ai import Agent, Tool
from pydantic_ai.result import RunResult
from app import SimpleAgent
from utils.tools import roll_die  # , get_player_name


MODEL_NAME: str = "ollama:llama3.1"


def test_agent_existence() -> None:
    """Verify that a SimpleAgent instance can be created successfully."""
    agent: SimpleAgent = SimpleAgent()
    assert isinstance(agent, Agent), "Agent should be created successfully"


def test_agent_tool_usage() -> None:
    """Ensure that Agent can add and use a correctly."""
    tool: Tool = Tool(
        name="Roll Die",
        description="Rolls a die and returns a random number between 1 and 6.",
        function=roll_die,
    )
    agent: Agent = Agent(
        MODEL_NAME,
        deps_type=str,
        system_prompt=(
            "You're a dice game, you should roll the die and only output the resulting number without surrounding. Remember to only output the number without surrounding text for example like this: 1"
        ),
        tools=[tool],
    )

    result: RunResult = agent.run_sync("1")
    data: str = result.data
    assert 1 <= int(data) <= 6, "Tool should return a number between 1 and 6."
