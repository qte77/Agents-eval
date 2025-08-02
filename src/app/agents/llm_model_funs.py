"""
LLM model functions for integrating with various LLM providers.

This module provides functions to retrieve API keys, provider configurations, and
to create model instances for supported LLM providers such as Gemini and OpenAI.
It also includes logic for assembling model dictionaries for system agents.
"""

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.data_models.app_models import (
    AppEnv,
    EndpointConfig,
    ModelDict,
    ProviderConfig,
)
from app.utils.error_messages import generic_exception, get_key_error
from app.utils.log import logger


def get_api_key(
    provider: str,
    chat_env_config: AppEnv,
) -> tuple[bool, str]:
    """Retrieve API key from chat env config variable."""
    provider = provider.upper()

    # Provider mapping for environment variable keys
    provider_key_mapping = {
        "OPENAI": "OPENAI_API_KEY",
        "ANTHROPIC": "ANTHROPIC_API_KEY",
        "GEMINI": "GEMINI_API_KEY",
        "GITHUB": "GITHUB_API_KEY",
        "GROK": "GROK_API_KEY",
        "HUGGINGFACE": "HUGGINGFACE_API_KEY",
        "OPENROUTER": "OPENROUTER_API_KEY",
        "PERPLEXITY": "PERPLEXITY_API_KEY",
        "TOGETHER": "TOGETHER_API_KEY",
        "OLLAMA": None,  # Ollama doesn't require an API key
    }

    if provider == "OLLAMA":
        return (False, "Ollama does not require an API key.")

    key_name = provider_key_mapping.get(provider)
    if not key_name:
        return (False, f"Provider '{provider}' is not supported.")

    key_content = getattr(chat_env_config, key_name, None)
    if key_content and key_content.strip():
        logger.info(f"Found API key for provider: '{provider}'")
        return (True, key_content)
    else:
        return (
            False,
            f"API key for provider '{provider}' not found in configuration.",
        )


def get_provider_config(
    provider: str, providers: dict[str, ProviderConfig]
) -> ProviderConfig:
    """Retrieve configuration settings for the specified provider."""
    try:
        return providers[provider]
    except KeyError as e:
        msg = get_key_error(str(e))
        logger.error(msg)
        raise KeyError(msg)
    except Exception as e:
        msg = generic_exception(str(e))
        logger.exception(msg)
        raise Exception(msg)


def _get_llm_model_name(provider: str, model_name: str) -> str:
    """Convert provider and model name to required format."""
    provider_mappings = {
        "openai": "",  # OpenAI models don't need prefix
        "anthropic": "anthropic/",
        "gemini": "gemini/",
        "github": "",  # GitHub models use OpenAI-compatible format
        "grok": "grok/",
        "huggingface": "huggingface/",
        "openrouter": "openrouter/",
        "perplexity": "perplexity/",
        "together": "together_ai/",
        "ollama": "ollama/",
    }

    prefix = provider_mappings.get(provider.lower(), f"{provider.lower()}/")

    # Handle special cases where model name already includes provider
    if "/" in model_name and any(
        model_name.startswith(p) for p in provider_mappings.values() if p
    ):
        return model_name

    return f"{prefix}{model_name}"


def _create_llm_model(
    endpoint_config: EndpointConfig,
) -> Model:
    """Create a model that works with PydanticAI."""

    provider = endpoint_config.provider.lower()
    model_name = endpoint_config.provider_config.model_name
    api_key = endpoint_config.api_key
    base_url = str(endpoint_config.provider_config.base_url)

    # Get formatted model name
    llm_model_name = _get_llm_model_name(provider, model_name)

    logger.info(f"Creating LLM model: {llm_model_name}")

    # Special handling for different providers
    if provider == "ollama":
        # For Ollama, use the configured base URL directly
        return OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key="not-required",
            ),
        )
    elif provider == "openai":
        # For OpenAI, use standard OpenAI endpoint
        return OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(
                api_key=api_key or "not-required",
            ),
        )
    elif provider in ["openrouter", "github"]:
        # For OpenRouter and GitHub, use their custom base URLs with OpenAI format
        return OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key=api_key or "not-required",
            ),
        )
    elif provider == "gemini":
        # For Gemini, we need to use Google's Gemini model directly
        # Since PydanticAI supports Gemini natively, import and use it
        try:
            from pydantic_ai.models.gemini import GeminiModel

            return GeminiModel(model_name=model_name)
        except ImportError:
            logger.warning("GeminiModel not available, falling back to OpenAI format")
            # Fallback to OpenAI format with custom base URL
            return OpenAIModel(
                model_name=model_name,
                provider=OpenAIProvider(
                    base_url=base_url,
                    api_key=api_key or "not-required",
                ),
            )
    else:
        # For other providers, use their configured base URLs with OpenAI format
        return OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key=api_key or "not-required",
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
        include_researcher (bool): Whether to include the researcher model.
        include_analyst (bool): Whether to include the analyst model.
        include_synthesiser (bool): Whether to include the synthesiser model.

    Returns:
        ModelDict: A dictionary containing compatible models for the system
            agents.
    """

    model = _create_llm_model(endpoint_config)
    return ModelDict.model_validate(
        {
            "model_manager": model,
            "model_researcher": model if include_researcher else None,
            "model_analyst": model if include_analyst else None,
            "model_synthesiser": model if include_synthesiser else None,
        }
    )


def setup_llm_environment(api_keys: dict[str, str]) -> None:
    """
    Set up LLM environment variables for API keys.

    Args:
        api_keys: Dictionary mapping provider names to API keys.
    """
    import os

    # Set environment variables for LLM
    for provider, api_key in api_keys.items():
        if api_key and api_key.strip():
            env_var = f"{provider.upper()}_API_KEY"
            os.environ[env_var] = api_key
            logger.info(f"Set environment variable: {env_var}")
