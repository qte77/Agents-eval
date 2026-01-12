"""
LLM model creation and abstraction.

This module provides pure model creation functionality without business logic.
Handles model instantiation for different providers in a unified way.
"""

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.data_models.app_models import EndpointConfig, ModelDict
from app.utils.log import logger


def get_llm_model_name(provider: str, model_name: str) -> str:
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
    if "/" in model_name and any(model_name.startswith(p) for p in provider_mappings.values() if p):
        return model_name

    return f"{prefix}{model_name}"


def create_llm_model(endpoint_config: EndpointConfig) -> Model:
    """Create a model that works with PydanticAI."""

    provider = endpoint_config.provider.lower()
    model_name = endpoint_config.provider_config.model_name
    api_key = endpoint_config.api_key
    base_url = str(endpoint_config.provider_config.base_url)

    # Get formatted model name
    llm_model_name = get_llm_model_name(provider, model_name)

    logger.info(f"Creating LLM model: {llm_model_name}")

    # Special handling for different providers
    if provider == "ollama":
        # For Ollama, use the configured base URL directly
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key="not-required",
            ),
        )
    elif provider == "openai":
        # For OpenAI, use standard OpenAI endpoint
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                api_key=api_key or "not-required",
            ),
        )
    elif provider in ["openrouter", "github"]:
        # For OpenRouter and GitHub, use their custom base URLs with OpenAI format
        return OpenAIChatModel(
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
            from pydantic_ai.models.google import GoogleModel

            # GoogleModel uses different parameter name for API key
            return GoogleModel(model_name=model_name)
        except ImportError:
            logger.warning("GoogleModel not available, falling back to OpenAI format")
            # Fallback to OpenAI format with custom base URL
            return OpenAIChatModel(
                model_name=model_name,
                provider=OpenAIProvider(
                    base_url=base_url,
                    api_key=api_key or "not-required",
                ),
            )
    else:
        # For other providers, use their configured base URLs with OpenAI format
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key=api_key or "not-required",
            ),
        )


def create_agent_models(
    endpoint_config: EndpointConfig,
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
) -> ModelDict:
    """
    Create models for the system agents.

    Args:
        endpoint_config (EndpointConfig): Configuration for the model.
        include_researcher (bool): Whether to include the researcher model.
        include_analyst (bool): Whether to include the analyst model.
        include_synthesiser (bool): Whether to include the synthesiser model.

    Returns:
        ModelDict: A dictionary containing compatible models for the system agents.
    """

    model = create_llm_model(endpoint_config)
    return ModelDict.model_validate(
        {
            "model_manager": model,
            "model_researcher": model if include_researcher else None,
            "model_analyst": model if include_analyst else None,
            "model_synthesiser": model if include_synthesiser else None,
        }
    )


def create_simple_model(provider: str, model_name: str, api_key: str | None = None) -> Model:
    """
    Create a simple model for basic usage like evaluation.

    Args:
        provider: Provider name (e.g., "openai", "github")
        model_name: Model name (e.g., "gpt-4o-mini", "gpt-4o")
        api_key: API key (optional, will use environment if not provided)

    Returns:
        Model: PydanticAI model instance
    """
    if provider.lower() == "openai":
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(api_key=api_key or "not-required"),
        )
    elif provider.lower() == "github":
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url="https://models.inference.ai.azure.com",
                api_key=api_key or "not-required",
            ),
        )
    else:
        # Generic OpenAI-compatible format
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(api_key=api_key or "not-required"),
        )
