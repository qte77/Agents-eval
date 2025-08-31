"""
LLM provider configuration and API key management.

This module provides pure provider abstraction without business logic.
Handles API key retrieval, provider configurations, and environment setup.
"""

from app.data_models.app_models import AppEnv, ProviderConfig
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


def get_supported_providers() -> list[str]:
    """Get list of supported LLM providers."""
    return [
        "openai",
        "anthropic",
        "gemini",
        "github",
        "grok",
        "huggingface",
        "openrouter",
        "perplexity",
        "together",
        "ollama",
    ]
