"""
This module contains a simple system of agents that can be used to research and analyze
data.
"""

from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

from .data_models import AnalysisResult, ResearchResult


class SystemAgent(Agent[None, ResearchResult | AnalysisResult]):
    """A generic system agent that can be used to research and analyze data."""

    def __init__(
        self,
        model: OpenAIChatModel,
        result_type: type[ResearchResult] | type[AnalysisResult],
        system_prompt: str,
        result_retries: int = 3,
        tools: list[Any] | None = None,
    ):
        super().__init__(  # type: ignore[call-overload]
            model,
            result_type=result_type,
            system_prompt=system_prompt,
            result_retries=result_retries,
            tools=tools or [],
        )


def add_tools_to_manager_agent(
    manager_agent: SystemAgent, research_agent: SystemAgent, analysis_agent: SystemAgent
) -> None:
    """Create and configure the joke generation agent."""

    @manager_agent.tool
    async def delegate_research(ctx: RunContext[None], query: str) -> ResearchResult:  # type: ignore[reportUnusedFunction]
        """Delegate research task to ResearchAgent."""
        result = await research_agent.run(query, usage=ctx.usage)
        assert isinstance(result.output, ResearchResult)
        return result.output

    @manager_agent.tool
    async def delegate_analysis(ctx: RunContext[None], data: str) -> AnalysisResult:  # type: ignore[reportUnusedFunction]
        """Delegate analysis task to AnalysisAgent."""
        result = await analysis_agent.run(data, usage=ctx.usage)
        assert isinstance(result.output, AnalysisResult)
        return result.output
