"""
Provides tools (functions) to be used by agents.
Uses https://dev.to/yashddesai/pydanticai-a-comprehensive-guide-to-building-production-ready-ai-applications-20me
"""

import random
from pydantic_ai import Agent, RunContext

agent = Agent(
    "ollama:llama3.1",
    deps_type=str,
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    ),
)


@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))


@agent.tool
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps
