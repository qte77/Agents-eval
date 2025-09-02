"""
A simple example of using a Pydantic AI agent to generate a structured summary of a
research topic.
"""

from os import path

from .utils.agent_simple_no_tools import get_research
from .utils.utils import (
    get_api_key,
    load_config,
    print_research_Result,
)

CONFIG_FILE = "config.json"


def main():
    """Main function to run the research agent."""

    config_path = path.join(path.dirname(__file__), CONFIG_FILE)
    config = load_config(config_path)

    provider = input("Which inference provider to use? ")
    topic = input("What topic would you like to research? ")

    api_key = get_api_key(provider)

    result = get_research(topic, config.prompts, provider, config, api_key or "")
    print_research_Result(result.data, result.usage())


if __name__ == "__main__":
    main()
