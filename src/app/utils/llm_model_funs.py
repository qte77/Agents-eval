"""
Utility functions and classes for managing and instantiating LLM models and providers.

This module provides functions to retrieve API keys, provider configurations, and
to create model instances for supported LLM providers such as Gemini and OpenAI.
It also includes logic for assembling model dictionaries for system agents.
"""

from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from ..config_app import API_SUFFIX
from .data_models import EndpointConfig, ModelDict, ProviderConfig
from .load_configs import AppEnv
from .log import logger


def get_api_key(
    provider: str,
    chat_env_config: AppEnv,
) -> str | None:
    """Retrieve API key from chat env config variable."""

    provider = provider.upper()
    if provider == "OLLAMA":
        return None
    else:
        return getattr(chat_env_config, f"{provider}{API_SUFFIX}")


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


def _create_model(endpoint_config: EndpointConfig) -> GeminiModel | OpenAIModel:
    """Create a model that uses model_name and base_url for inference API"""

    if endpoint_config.provider.lower() == "gemini":
        # FIXME missing ctr signature: api_key=model_config.api_key
        return GeminiModel(endpoint_config.provider_config.model_name)
    else:
        return OpenAIModel(
            model_name=endpoint_config.provider_config.model_name,
            provider=OpenAIProvider(
                base_url=endpoint_config.provider_config.base_url,
                api_key=endpoint_config.api_key,
            ),
        )


def get_models(
    endpoint_config: EndpointConfig,
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
) -> ModelDict:
    """
    Get the models for the system agents.
    Args:
        endpoint_config (EndpointConfig): Configuration for the model.
        include_analyist (Optional[bool]): Whether to include the analyst model.
            Defaults to False.
        include_synthesiser (Optional[bool]): Whether to include the synthesiser model.
            Defaults to False.
    Returns:
        Dict[str, GeminiModel | OpenAIModel]: A dictionary containing the models for the
            system agents.
    """

    model = _create_model(endpoint_config)
    return ModelDict.model_validate(
        {
            "model_manager": model,
            "model_researcher": model if include_researcher else None,
            "model_analyst": model if include_analyst else None,
            "model_synthesiser": model if include_synthesiser else None,
        }
    )
