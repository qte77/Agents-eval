"""
Provides tools (functions) to be used by agents.
Uses: https://ai.pydantic.dev/tools/
"""

import random
from pydantic_ai import RunContext, Tool


class DummyTool(Tool):
    """
    A dummy tool that always returns a success message.
    """

    def run(self) -> str:
        """
        Execute the dummy tool and return a success message.
        """

        return "Tool used successfully"


def roll_die() -> str:
    """Roll a six-sided die and return the result as a string."""

    return str(random.randint(1, 6))


def get_player_name(ctx: RunContext[str]) -> str:
    """Retrieve the player's name from the context."""

    return ctx.deps
