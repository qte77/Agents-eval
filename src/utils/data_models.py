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
    Config: Represents the overall configuration settings for agents and model providers.
"""

from pydantic import BaseModel
from pydantic_ai.usage import UsageLimits
from typing import Dict, List


class ResearchResult(BaseModel):
    """Research results from the research agent."""

    topic: str | Dict[str, str]
    findings: List[str] | Dict[str, str | List[str]]
    sources: List[str] | Dict[str, str | List[str]]


class AnalysisResult(BaseModel):
    """Analysis results from the analysis agent."""

    insights: List[str]
    recommendations: List[str]
    approval: bool


class ResearchSummary(BaseModel):
    """Expected model response of research on a topic"""

    topic: str
    key_points: List[str]
    key_points_explanation: List[str]
    conclusion: str
    sources: List[str]


class ProviderConfig(BaseModel):
    """Configuration for a model provider"""

    model_name: str
    base_url: str


class Config(BaseModel):
    """Configuration settings for agents and model providers"""

    providers: Dict[str, ProviderConfig]
    inference: Dict[str, str | int]
    prompts: Dict[str, str]


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    provider: str
    query: str | List[Dict[str, str]]  # (1) messages
    api_key: str | None
    prompts: Dict[str, str]
    provider_config: ProviderConfig
    usage_limits: UsageLimits


class ModelConfig(BaseModel):
    """Configuration for a model provider"""

    provider: str
    model_name: str
    base_url: str
    api_key: str | None
