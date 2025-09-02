"""
This module contains a function to create a research agent with the specified model,
result type, and system prompt.
"""

from sys import exit

from openai import APIConnectionError
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.models.openai import OpenAIModel

from .data_models import Config, ResearchSummary
from .utils import create_model


def _create_research_agent(model: OpenAIModel, result_type: ResearchSummary, system_prompt: str) -> Agent:
    """
    Create a research agent with the specified model, result type, and system prompt.
    """

    return Agent(model=model, result_type=result_type, system_prompt=system_prompt)


def get_research(
    topic: str,
    prompts: dict[str, str],
    provider: str,
    provider_config: Config,
    api_key: str,
) -> AgentRunResult[ResearchSummary]:
    """Run the research agent to generate a structured summary of a research topic."""

    model = create_model(
        provider_config.providers[provider].base_url,
        provider_config.providers[provider].model_name,
        api_key,
        provider,
    )
    agent = _create_research_agent(model, ResearchSummary, prompts["system_prompt"])

    print(f"\nResearching {topic}...")
    try:
        result = agent.run_sync(f"{prompts['user_prompt']} {topic}")
    except APIConnectionError as e:
        print(f"Error connecting to API: {e}")
        exit()
    except Exception as e:
        print(f"Error connecting to API: {e}")
        exit()
    else:
        return result
