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

type UserPromptType = (
    str | list[dict[str, str]] | ModelRequest | None
)  #  (1) Input validation
ResultBaseType = TypeVar(
    "ResultBaseType", bound=BaseModel
)  # (2) Generic type for model results


class ResearchResult(BaseModel):
    """Research results from the research agent."""

    topic: str | dict[str, str]
    findings: list[str] | dict[str, str | list[str]]
    sources: list[str] | dict[str, str | list[str]]


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


class ProviderConfig(BaseModel):
    """Configuration for a model provider"""

    model_name: str
    base_url: HttpUrl


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
    def validate_tools(cls, v: list[Any]) -> list[Tool | None]:
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
