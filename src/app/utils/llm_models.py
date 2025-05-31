"""
This module provides utility functions and classes for working with different AI models.

Functions:
    get_api_key(provider: str) -> Optional[str]:
        Retrieve API key from environment variable based on the provider name.

    get_provider_config(provider: str, config: ChatConfig) -> Dict[str, str]:
        Retrieve configuration settings for the specified provider from the
            given config.

    create_model(model_config: ModelConfig) -> GeminiModel | OpenAIModel:
        Create and return an AI model instance based on the provided model
            configuration.

Classes:
    ModelConfig:
        Configuration class for model settings.
"""

from os import getenv

from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from ..config import API_SUFFIX
from .data_models import ModelConfig, ProviderConfig
from .log import logger


def get_api_key(provider: str) -> str | None:
    """Retrieve API key from environment variable."""

    if provider.lower() == "ollama":
        return None
    else:
        return getenv(f"{provider.upper()}{API_SUFFIX}")


def get_provider_config(
    provider: str, providers: dict[str, ProviderConfig]
) -> dict[str, str]:
    """Retrieve configuration settings for the specified provider."""

    try:
        model_name = providers[provider].model_name
        base_url = providers[provider].base_url
    except KeyError as e:
        msg = f"Provider '{provider}' not found in configuration: {e}"
        logger.error(msg)
        raise KeyError(msg)
    except Exception as e:
        msg = f"Error loading provider configuration: {e}"
        logger.exception(msg)
        raise Exception(msg)
    else:
        return {
            "model_name": model_name,
            "base_url": base_url,
        }


def create_model(model_config: ModelConfig) -> GeminiModel | OpenAIModel:
    """Create a model that uses base_url as inference API"""

    if model_config.provider.lower() == "gemini":
        # FIXME missing ctr signature: api_key=model_config.api_key
        return GeminiModel(model_config.model_name)
    else:
        return OpenAIModel(
            model_config.model_name,
            provider=OpenAIProvider(
                base_url=model_config.base_url, api_key=model_config.api_key
            ),
        )


def get_models(
    model_config: ModelConfig,
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
) -> dict[str, GeminiModel | OpenAIModel | None]:
    """
    Get the models for the system agents.
    Args:
        model_config (ModelConfig): Configuration for the model.
        include_analyist (Optional[bool]): Whether to include the analyst model.
            Defaults to False.
        include_synthesiser (Optional[bool]): Whether to include the synthesiser model.
            Defaults to False.
    Returns:
        Dict[str, GeminiModel | OpenAIModel]: A dictionary containing the models for the
            system agents.
    """

    model = create_model(model_config)
    return {
        "model_manager": model,
        "model_researcher": model if include_researcher else None,
        "model_analyst": model if include_analyst else None,
        "model_synthesiser": model if include_synthesiser else None,
    }
