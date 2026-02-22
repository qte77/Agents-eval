"""
LLM model creation and abstraction.

This module provides pure model creation functionality without business logic.
Handles model instantiation for different providers in a unified way.
"""

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openai import OpenAIProvider

from app.data_models.app_models import PROVIDER_REGISTRY, EndpointConfig, ModelDict
from app.utils.log import logger


def get_llm_model_name(provider: str, model_name: str) -> str:
    """Convert provider and model name to required format.

    Args:
        provider: Provider name (case-insensitive)
        model_name: Model name to format

    Returns:
        Formatted model name with appropriate provider prefix
    """
    provider_lower = provider.lower()

    # Get provider metadata from registry
    provider_metadata = PROVIDER_REGISTRY.get(provider_lower)
    if not provider_metadata:
        # Fallback for unknown providers
        logger.warning(f"Provider '{provider}' not in registry, using default prefix")
        prefix = f"{provider_lower}/"
    else:
        prefix = provider_metadata.model_prefix

    # Handle special cases where model name already includes provider
    if "/" in model_name:
        # Check if it already has a valid provider prefix
        for registered_provider in PROVIDER_REGISTRY.values():
            if registered_provider.model_prefix and model_name.startswith(
                registered_provider.model_prefix
            ):
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
                api_key=api_key,
            ),
        )
    elif provider in ["openrouter", "github"]:
        # For OpenRouter and GitHub, use their custom base URLs with OpenAI format
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key=api_key,
            ),
        )
    elif provider == "anthropic":
        # Reason: Anthropic has native PydanticAI support; using the OpenAI-compatible
        # fallback loses Anthropic-specific features (caching, extended thinking).
        try:
            from pydantic_ai.models.anthropic import AnthropicModel
            from pydantic_ai.providers.anthropic import AnthropicProvider

            return AnthropicModel(
                model_name=model_name,
                provider=AnthropicProvider(api_key=api_key),
            )
        except ImportError:
            logger.warning("AnthropicModel not available, falling back to OpenAI format")
            return OpenAIChatModel(
                model_name=model_name,
                provider=OpenAIProvider(
                    base_url=base_url,
                    api_key=api_key,
                ),
            )
    elif provider in ["cerebras", "groq", "fireworks", "together", "sambanova"]:
        # Reason: These providers reject requests with mixed strict values on tools.
        # Disabling strict tool definitions prevents PydanticAI from adding
        # the 'strict' field to some tools but not others.
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key=api_key,
            ),
            profile=OpenAIModelProfile(
                openai_supports_strict_tool_definition=False,
            ),
        )
    elif provider == "gemini":
        # For Gemini, we need to use Google's Gemini model directly
        # Since PydanticAI supports Gemini natively, import and use it
        try:
            from pydantic_ai.models.google import GoogleModel
            from pydantic_ai.providers.google import GoogleProvider

            # Reason: Pass api_key via constructor to avoid os.environ exposure (AC4).
            # GoogleProvider accepts api_key directly, preventing key leakage to child
            # processes, crash reporters, and debug dumps.
            return GoogleModel(
                model_name=model_name,
                provider=GoogleProvider(api_key=api_key),
            )
        except ImportError:
            logger.warning("GoogleModel not available, falling back to OpenAI format")
            # Fallback to OpenAI format with custom base URL
            return OpenAIChatModel(
                model_name=model_name,
                provider=OpenAIProvider(
                    base_url=base_url,
                    api_key=api_key,
                ),
            )
    else:
        # For other providers, use their configured base URLs with OpenAI format
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=base_url,
                api_key=api_key,
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
            provider=OpenAIProvider(api_key=api_key),
        )
    elif provider.lower() == "github":
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url="https://models.inference.ai.azure.com",
                api_key=api_key,
            ),
        )
    else:
        # Generic OpenAI-compatible format
        return OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(api_key=api_key),
        )
