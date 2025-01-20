"""
Tests for SimpleAgent creation and tool usage.
"""

from pydantic_ai import Agent, Tool
from app import SimpleAgent
from utils.tools import roll_die  # , get_player_name


def test_agent_existence() -> None:
    """Verify that a SimpleAgent instance can be created successfully."""
    agent: SimpleAgent = SimpleAgent()
    assert isinstance(agent, Agent), "Agent should be created successfully"


def test_agent_tool_usage() -> None:
    """Ensure that Agent can add and use a correctly."""
    model_name = "ollama:phi4"  # "llama3.1"
    tool: Tool = Tool(
        name="Roll Die",
        description="Rolls a die and returns a random number between 1 and 6.",
        function=roll_die,
    )
    agent: Agent = Agent(
        model_name,
        deps_type=str,
        system_prompt=(
            "You're a dice game, you should roll the die and see if the number "
            "you get back matches the user's guess. If so, tell them they're a winner. "
            "Use the player's name in the response."
        ),
        tools=[tool],
    )

    result: int = agent.run_sync("1")
    assert 1 <= result <= 6, "Tool should return a number between 1 and 6."
