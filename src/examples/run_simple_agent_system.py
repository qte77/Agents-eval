"""
This example demonstrates how to run a simple agent system that consists of a manager
agent, a research agent, and an analysis agent. The manager agent delegates research
and analysis tasks to the corresponding agents and combines the results to provide a
comprehensive answer to the user query.
https://ai.pydantic.dev/multi-agent-applications/#agent-delegation
"""

from asyncio import run
from os import path

from openai import UnprocessableEntityError
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.exceptions import UnexpectedModelBehavior, UsageLimitExceeded
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import UsageLimits

from .utils.agent_simple_system import SystemAgent, add_tools_to_manager_agent
from .utils.data_models import AnalysisResult, ResearchResult
from .utils.utils import create_model, get_api_key, get_provider_config, load_config

CONFIG_FILE = "config.json"


def get_models(model_config: dict) -> tuple[OpenAIModel]:
    """Get the models for the system agents."""
    model_researcher = create_model(**model_config)
    model_analyst = create_model(**model_config)
    model_manager = create_model(**model_config)
    return model_researcher, model_analyst, model_manager


def get_manager(
    model_manager: OpenAIModel,
    model_researcher: OpenAIModel,
    model_analyst: OpenAIModel,
    prompts: dict[str, str],
) -> SystemAgent:
    """Get the agents for the system."""
    researcher = SystemAgent(
        model_researcher,
        ResearchResult,
        prompts["system_prompt_researcher"],
        [duckduckgo_search_tool()],
    )
    analyst = SystemAgent(
        model_analyst, AnalysisResult, prompts["system_prompt_analyst"]
    )
    manager = SystemAgent(
        model_manager, ResearchResult, prompts["system_prompt_manager"]
    )
    add_tools_to_manager_agent(manager, researcher, analyst)
    return manager


async def main():
    """Main function to run the research system."""

    provider = input("Which inference provider to use? ")
    query = input("What would you like to research? ")

    config_path = path.join(path.dirname(__file__), CONFIG_FILE)
    config = load_config(config_path)

    api_key = get_api_key(provider)
    provider_config = get_provider_config(provider, config)
    usage_limits = UsageLimits(request_limit=10, total_tokens_limit=4000)

    model_config = {
        "base_url": provider_config["base_url"],
        "model_name": provider_config["model_name"],
        "api_key": api_key,
        "provider": provider,
    }
    manager = get_manager(*get_models(model_config), config.prompts)

    print(f"\nResearching: {query}...")

    try:
        result = await manager.run(query, usage_limits=usage_limits)
    except (UnexpectedModelBehavior, UnprocessableEntityError) as e:
        print(f"Error: Model returned unexpected result: {e}")
    except UsageLimitExceeded as e:
        print(f"Usage limit exceeded: {e}")
    else:
        print("\nFindings:", {result.data.findings})
        print(f"Sources: {result.data.sources}")
        print("\nUsage statistics:")
        print(result.usage())


if __name__ == "__main__":
    run(main())
