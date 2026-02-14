"""
Data models for agent system configuration and results.

This module defines Pydantic models for representing research and analysis results,
summaries, provider and agent configurations, and model dictionaries used throughout
the application. These models ensure type safety and validation for data exchanged
between agents and system components.
"""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from pydantic_ai.messages import ModelRequest
from pydantic_ai.models import Model
from pydantic_ai.tools import Tool
from pydantic_ai.usage import UsageLimits
from pydantic_settings import BaseSettings, SettingsConfigDict

type UserPromptType = str | list[dict[str, str]] | ModelRequest | None  #  (1) Input validation
ResultBaseType = TypeVar("ResultBaseType", bound=BaseModel)  # (2) Generic type for model results


class ResearchResult(BaseModel):
    """Research results from the research agent with flexible structure."""

    topic: str | dict[str, str]
    findings: list[str] | dict[str, str | list[str]]
    sources: list[str | HttpUrl] | dict[str, str | HttpUrl | list[str | HttpUrl]]


class ResearchResultSimple(BaseModel):
    """Simplified research results for Gemini compatibility."""

    topic: str
    findings: list[str]
    sources: list[str]


class AnalysisResult(BaseModel):
    """Analysis results from the analysis agent."""

    insights: list[str]
    recommendations: list[str]
    approval: bool


class ResearchSummary(BaseModel):
    """Expected model response of research on a topic"""

    topic: str
    key_points: list[str]
    key_points_explanation: list[str]
    conclusion: str
    sources: list[str]


class ProviderMetadata(BaseModel):
    """Metadata for an LLM provider.

    This model defines the core configuration for each supported provider,
    serving as a single source of truth for provider settings.
    """

    name: str
    env_key: str | None  # None for providers without API keys (e.g., Ollama)
    model_prefix: str  # Prefix for model names (empty string if not needed)
    default_base_url: str | None = None  # Default API endpoint for OpenAI-compatible providers
    default_model: str | None = None  # Default model ID for the provider


class ProviderConfig(BaseModel):
    """Configuration for a model provider"""

    model_name: str
    base_url: HttpUrl
    usage_limits: int | None = None
    max_content_length: int | None = 15000


class ChatConfig(BaseModel):
    """Configuration settings for agents and model providers"""

    providers: dict[str, ProviderConfig]
    inference: dict[str, str | int]
    prompts: dict[str, str]


class EndpointConfig(BaseModel):
    """Configuration for an agent"""

    provider: str
    query: UserPromptType = None
    api_key: str | None
    prompts: dict[str, str]
    provider_config: ProviderConfig
    usage_limits: UsageLimits | None = None


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    model: Model  # (1) Instance expected
    output_type: type[BaseModel]  # (2) Class expected
    system_prompt: str
    # FIXME tools: list[Callable[..., Awaitable[Any]]]
    tools: list[Any] = []  # (3) List of tools will be validated at creation
    retries: int = 3

    # Avoid pydantic.errors.PydanticSchemaGenerationError:
    # Unable to generate pydantic-core schema for <class 'openai.AsyncOpenAI'>.
    # Avoid Pydantic errors related to non-Pydantic types
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )  # (4) Suppress Error non-Pydantic types caused by <class 'openai.AsyncOpenAI'>

    @field_validator("tools", mode="before")
    def validate_tools(cls, v: list[Any]) -> list[Tool | None]:  # noqa: N805
        """Validate that all tools are instances of Tool."""
        if not v:
            return []
        if not all(isinstance(t, Tool) for t in v):
            raise ValueError("All tools must be Tool instances")
        return v


class ModelDict(BaseModel):
    """Dictionary of models used to create agent systems"""

    model_manager: Model
    model_researcher: Model | None
    model_analyst: Model | None
    model_synthesiser: Model | None
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EvalConfig(BaseModel):
    metrics_and_weights: dict[str, float]


# Registry of all supported LLM providers
# This serves as the single source of truth for provider configuration
PROVIDER_REGISTRY: dict[str, ProviderMetadata] = {
    "openai": ProviderMetadata(
        name="openai",
        env_key="OPENAI_API_KEY",
        model_prefix="",
        default_base_url="https://api.openai.com/v1",
    ),
    "anthropic": ProviderMetadata(
        name="anthropic",
        env_key="ANTHROPIC_API_KEY",
        model_prefix="anthropic/",
        default_base_url="https://api.anthropic.com",
    ),
    "gemini": ProviderMetadata(
        name="gemini",
        env_key="GEMINI_API_KEY",
        model_prefix="gemini/",
        default_base_url="https://generativelanguage.googleapis.com/v1beta",
    ),
    "github": ProviderMetadata(
        name="github",
        env_key="GITHUB_API_KEY",
        model_prefix="",
        default_base_url="https://models.inference.ai.azure.com",
    ),
    "grok": ProviderMetadata(
        name="grok",
        env_key="GROK_API_KEY",
        model_prefix="grok/",
        default_base_url="https://api.x.ai/v1",
    ),
    "huggingface": ProviderMetadata(
        name="huggingface",
        env_key="HUGGINGFACE_API_KEY",
        model_prefix="huggingface/",
        default_base_url="https://router.huggingface.co/v1",
    ),
    "openrouter": ProviderMetadata(
        name="openrouter",
        env_key="OPENROUTER_API_KEY",
        model_prefix="openrouter/",
        default_base_url="https://openrouter.ai/api/v1",
    ),
    "perplexity": ProviderMetadata(
        name="perplexity",
        env_key="PERPLEXITY_API_KEY",
        model_prefix="perplexity/",
        default_base_url="https://api.perplexity.ai",
    ),
    "restack": ProviderMetadata(
        name="restack",
        env_key="RESTACK_API_KEY",
        model_prefix="",
        default_base_url="https://ai.restack.io",
    ),
    "together": ProviderMetadata(
        name="together",
        env_key="TOGETHER_API_KEY",
        model_prefix="together_ai/",
        default_base_url="https://api.together.xyz/v1",
    ),
    "cerebras": ProviderMetadata(
        name="cerebras",
        env_key="CEREBRAS_API_KEY",
        model_prefix="",
        default_base_url="https://api.cerebras.ai/v1",
        default_model="gpt-oss-120b",
    ),
    "ollama": ProviderMetadata(
        name="ollama",
        env_key=None,
        model_prefix="ollama/",
        default_base_url="http://localhost:11434/v1",
    ),
}


class AppEnv(BaseSettings):
    """
    Application environment settings loaded from environment variables or .env file.

    This class uses Pydantic's BaseSettings to manage API keys and configuration
    for various inference endpoints, tools, and logging/monitoring services.
    Environment variables are loaded from a .env file by default.
    """

    # Inference endpoints
    ANTHROPIC_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GITHUB_API_KEY: str = ""
    GROK_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""
    RESTACK_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""

    # Tools
    TAVILY_API_KEY: str = ""

    # Logging/Monitoring/Tracing
    AGENTOPS_API_KEY: str = ""
    LOGFIRE_API_KEY: str = ""
    WANDB_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
