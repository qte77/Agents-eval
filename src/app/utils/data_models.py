"""
This module defines data models using Pydantic's BaseModel for various components
of the application, including research results, analysis results, research summaries,
provider configurations, model configurations, prompt configurations, and overall
configuration settings for agents and model providers.

Classes:
    ResearchResult: Represents research results from the research agent.
    AnalysisResult: Represents analysis results from the analysis agent.
    ResearchSummary: Represents the expected model response of research on a topic.
    ProviderConfig: Represents the configuration for a model provider.
    ModelConfig: Represents the configuration for a model provider with API key.
    ChatConfig: Represents the overall configuration settings for agents and model
        providers.
"""

from pydantic import BaseModel
from pydantic_ai.usage import UsageLimits


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
    base_url: str


class ChatConfig(BaseModel):
    """Configuration settings for agents and model providers"""

    providers: dict[str, ProviderConfig]
    inference: dict[str, str | int]
    prompts: dict[str, str]


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    provider: str
    query: str | list[dict[str, str]]  # (1) messages
    api_key: str | None
    prompts: dict[str, str]
    provider_config: ProviderConfig
    usage_limits: UsageLimits


class ModelConfig(BaseModel):
    """Configuration for a model provider"""

    provider: str
    model_name: str
    base_url: str
    api_key: str | None
