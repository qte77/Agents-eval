"""Example of a module with data models"""

from pydantic import BaseModel
from typing import Dict, List


class ResearchResult(BaseModel):
    """Research results from the research agent."""

    topic: str
    findings: List[str]
    sources: List[str]


class AnalysisResult(BaseModel):
    """Analysis results from the analysis agent."""

    insights: List[str]
    recommendations: List[str]


class ResearchSummary(BaseModel):
    """Expected model response of research on a topic"""

    topic: str
    key_points: List[str]
    key_points_explanation: List[str]
    conclusion: str


class ProviderConfig(BaseModel):
    """Configuration for a model provider"""

    model_name: str
    base_url: str


class Config(BaseModel):
    """Configuration settings for the research agent and model providers"""

    providers: Dict[str, ProviderConfig]
    prompts: Dict[str, str]
