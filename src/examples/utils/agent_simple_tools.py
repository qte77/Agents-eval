"""Simple agent for the dice game example."""

from openai import APIConnectionError
from pydantic_ai import Agent, Tool
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.models.openai import OpenAIChatModel

from .tools import get_player_name, roll_die
from .utils import create_model


class _DiceGameAgent(Agent[str, str]):
    """Dice game agent."""

    def __init__(self, model: OpenAIChatModel, system_prompt: str):
        super().__init__(
            model=model,
            deps_type=str,
            system_prompt=system_prompt,
            tools=[
                Tool(roll_die, takes_ctx=False),
                Tool(get_player_name, takes_ctx=True),
            ],
        )


def get_dice(
    player_name: str,
    guess: str,
    system_prompt: str,
    provider: str,
    api_key: str | None,
    config: dict[str, str],
) -> AgentRunResult[str]:
    """Run the dice game agent."""

    model = create_model(config["base_url"], config["model_name"], api_key, provider)
    agent = _DiceGameAgent(model, system_prompt)

    try:
        result = agent.run_sync(f"Player is guessing {guess}...", deps=player_name)
    except APIConnectionError as e:
        print(f"Error connecting to API: {e}")
        exit()
    except Exception as e:
        print(f"Error connecting to API: {e}")
        exit()
    else:
        return result
