"""Utility functions for running the research agent example."""

from .data_models import Config
from dotenv import load_dotenv
from json import load
from os import getenv
from pydantic import ValidationError
from pydantic_ai.usage import Usage
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from sys import exit
from typing import Optional, Dict


API_SUFFIX = "_API_KEY"


def load_config(config_path: str) -> Config:
    """Load and validate configuration from a JSON file."""

    try:
        with open(config_path, "r") as file:
            config_data = load(file)
        config = Config.model_validate(config_data)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        exit()
    except ValidationError as e:
        raise ValueError(f"Invalid configuration format: {e}")
        exit()
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")
        exit()
    else:
        return config


def get_api_key(provider: str) -> Optional[str]:
    """Retrieve API key from environment variable."""

    # TODO replace with pydantic-settings ?
    load_dotenv()

    if provider.lower() == "ollama":
        return None
    else:
        return getenv(f"{provider.upper()}{API_SUFFIX}")


def get_provider_config(provider: str, config: Config) -> Dict[str, str]:
    """Retrieve configuration settings for the specified provider."""

    try:
        model_name = config.providers[provider].model_name
        base_url = config.providers[provider].base_url
    except KeyError as e:
        raise ValueError(f"Missing configuration for {provider}: {e}.")
        exit()
    except Exception as e:
        raise Exception(f"Error loading provider configuration: {e}")
        exit()
    else:
        return {
            "model_name": model_name,
            "base_url": base_url,
        }


def create_model(
    base_url: str,
    model_name: str,
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
) -> OpenAIModel:
    """Create a model that uses base_url as inference API"""

    if api_key is None and not provider.lower() == "ollama":
        raise ValueError("API key is required for model.")
        exit()
    else:
        return OpenAIModel(
            model_name, provider=OpenAIProvider(base_url=base_url, api_key=api_key)
        )


def print_research_Result(summary: Dict, usage: Usage) -> None:
    """Output structured summary of the research topic."""

    print(f"\n=== Research Summary: {summary.topic} ===")
    print("\nKey Points:")
    for i, point in enumerate(summary.key_points, 1):
        print(f"{i}. {point}")
    print("\nKey Points Explanation:")
    for i, point in enumerate(summary.key_points_explanation, 1):
        print(f"{i}. {point}")
    print(f"\nConclusion: {summary.conclusion}")

    print(f"\nResponse structure: {list(dict(summary).keys())}")
    print(usage)
