"""Example of a module with data models"""

from pydantic import BaseModel


class ResearchResult(BaseModel):
    """Research results from the research agent."""

    topic: str
    findings: list[str]
    sources: list[str]


class AnalysisResult(BaseModel):
    """Analysis results from the analysis agent."""

    insights: list[str]
    recommendations: list[str]


class ResearchSummary(BaseModel):
    """Expected model response of research on a topic"""

    topic: str
    key_points: list[str]
    key_points_explanation: list[str]
    conclusion: str


class ProviderConfig(BaseModel):
    """Configuration for a model provider"""

    model_name: str
    base_url: str


class Config(BaseModel):
    """Configuration settings for the research agent and model providers"""

    providers: dict[str, ProviderConfig]
    prompts: dict[str, str]
