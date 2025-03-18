"""
This module contains a simple system of agents that can be used to research and analyze data.
"""

from .data_models import ResearchResult, AnalysisResult
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from typing import Optional


class SystemAgent(Agent):
    """A generic system agent that can be used to research and analyze data."""

    def __init__(
        self,
        model: OpenAIModel,
        result_type: ResearchResult | AnalysisResult,
        system_prompt: str,
        result_retries: int = 3,
        tools: Optional[list] = [],
    ):
        super().__init__(
            model,
            result_type=result_type,
            system_prompt=system_prompt,
            result_retries=result_retries,
            tools=tools,
        )


def add_tools_to_manager_agent(
    manager_agent: SystemAgent, research_agent: SystemAgent, analysis_agent: SystemAgent
) -> None:
    """Create and configure the joke generation agent."""

    @manager_agent.tool
    async def delegate_research(ctx: RunContext[None], query: str) -> ResearchResult:
        """Delegate research task to ResearchAgent."""
        result = await research_agent.run(query, usage=ctx.usage)
        return result.data

    @manager_agent.tool
    async def delegate_analysis(ctx: RunContext[None], data: str) -> AnalysisResult:
        """Delegate analysis task to AnalysisAgent."""
        result = await analysis_agent.run(data, usage=ctx.usage)
        return result.data
