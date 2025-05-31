"""Example tools for the utils example."""

from random import randint

from pydantic_ai import RunContext


def roll_die() -> str:
    """Tool to roll a die."""

    async def _execute(self) -> str:
        """Roll the die and return the result."""
        return str(randint(1, 6))


def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name from the context."""
    return ctx.deps
