"""Run the dice game agent using simple tools."""

from os import path

from .utils.agent_simple_tools import get_dice
from .utils.utils import (
    get_api_key,
    get_provider_config,
    load_config,
)

CONFIG_FILE = "config.json"
system_prompt = (
    "You're a dice game, you should roll the die and see if the number "
    "you get back matches the user's guess. If so, tell them they're a winner. "
    "Use the player's name in the response."
)


def main():
    """Run the dice game agent."""

    provider = input("Which inference provider to use? ")
    player_name = input("Enter your name: ")
    guess = input("Guess a number between 1 and 6: ")

    config_path = path.join(path.dirname(__file__), CONFIG_FILE)
    config = load_config(config_path)

    api_key = get_api_key(provider)
    provider_config = get_provider_config(provider, config)

    result = get_dice(player_name, guess, system_prompt, provider, api_key, provider_config)
    print(result)
    print(result.usage())


if __name__ == "__main__":
    main()
