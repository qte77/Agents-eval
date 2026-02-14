"""
LLM provider configuration and API key management.

This module provides pure provider abstraction without business logic.
Handles API key retrieval, provider configurations, and environment setup.
"""

from app.data_models.app_models import PROVIDER_REGISTRY, AppEnv, ProviderConfig
from app.utils.error_messages import generic_exception, get_key_error
from app.utils.log import logger


def get_api_key(
    provider: str,
    chat_env_config: AppEnv,
) -> tuple[bool, str]:
    """Retrieve API key from chat env config variable.

    Args:
        provider: Provider name (case-insensitive)
        chat_env_config: Application environment configuration

    Returns:
        Tuple of (success: bool, message: str) where message is either the API key or error message
    """
    provider_lower = provider.lower()

    # Check if provider exists in registry
    provider_metadata = PROVIDER_REGISTRY.get(provider_lower)
    if not provider_metadata:
        return (False, f"Provider '{provider}' is not supported.")

    # Handle providers without API keys (e.g., Ollama)
    if provider_metadata.env_key is None:
        return (False, f"{provider_metadata.name.title()} does not require an API key.")

    # Retrieve API key from environment config
    key_content = getattr(chat_env_config, provider_metadata.env_key, None)
    if key_content and key_content.strip():
        logger.info(f"Found API key for provider: '{provider}'")
        return (True, key_content)
    else:
        return (
            False,
            f"API key for provider '{provider}' not found in configuration.",
        )


def get_provider_config(provider: str, providers: dict[str, ProviderConfig]) -> ProviderConfig:
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
    """Get list of supported LLM providers from the registry."""
    return list(PROVIDER_REGISTRY.keys())
