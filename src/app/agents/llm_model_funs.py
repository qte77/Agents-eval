"""
Utility functions and classes for managing and instantiating LLM models and providers.

This module provides functions to retrieve API keys, provider configurations, and
to create model instances for supported LLM providers such as Gemini and OpenAI.
It also includes logic for assembling model dictionaries for system agents.
"""

from pydantic import HttpUrl
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config_app import API_SUFFIX
from app.utils.data_models import EndpointConfig, ModelDict, ProviderConfig
from app.utils.load_configs import AppEnv
from app.utils.log import logger


def get_api_key(
    provider: str,
    chat_env_config: AppEnv,
) -> str | None:
    """Retrieve API key from chat env config variable."""

    provider = provider.upper()
    if provider == "OLLAMA":
        return None
    else:
        key_name = f"{provider}{API_SUFFIX}"
        if hasattr(chat_env_config, key_name):
            logger.info(f"Found API key for provider '{provider}'")
            return getattr(chat_env_config, key_name)
        else:
            raise KeyError(
                f"API key for provider '{provider}' not found in configuration."
            )


def get_provider_config(
    provider: str, providers: dict[str, ProviderConfig]
) -> dict[str, str | HttpUrl]:
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
        # FIXME EndpointConfig: TypeError: 'ModelRequest' object is not iterable.
        raise NotImplementedError(
            "Current typing raises TypeError: 'ModelRequest' object is not iterable."
        )
    elif endpoint_config.provider.lower() == "huggingface":
        # FIXME HF not working with pydantic-ai OpenAI model
        raise NotImplementedError(
            "Hugging Face provider is not implemented yet. Please use Gemini or OpenAI."
            " https://huggingface.co/docs/inference-providers/providers/hf-inference"
        )
        # headers = {
        #    "Authorization": f"Bearer {endpoint_config.api_key}",
        # }
        # def query(payload):
        #    response = requests.post(API_URL, headers=headers, json=payload)
        #    return response.json()
        # query({"inputs": "", "parameters": {},})
    else:
        base_url_str = str(endpoint_config.provider_config.base_url)
        return OpenAIModel(
            model_name=endpoint_config.provider_config.model_name,
            provider=OpenAIProvider(
                base_url=base_url_str,
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
