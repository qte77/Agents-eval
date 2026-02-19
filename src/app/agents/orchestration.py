"""
Multi-agent orchestration and coordination.

This module provides orchestration classes and patterns for coordinating
multiple agents in complex workflows, including delegation patterns,
state management, and error handling.
"""

import asyncio
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits

from app.data_models.app_models import (
    AnalysisResult,
    ResearchResult,
    ResearchResultSimple,
    ResearchSummary,
    UserPromptType,
)
from app.utils.log import logger


def _validate_model_return[T: BaseModel](output_str: str, result_type: type[T]) -> T:
    """Validate and convert string output to expected model type."""
    try:
        return result_type.model_validate_json(output_str)
    except Exception as e:
        logger.error(f"Failed to validate model return: {e}")
        # Return a default instance if validation fails
        return result_type()


class AgentOrchestrator:
    """Base orchestrator for managing multi-agent interactions."""

    def __init__(self):
        self.execution_trace: dict[str, Any] = {}
        self.current_step: str = "initialized"

    def log_step(self, step_name: str, data: dict[str, Any] | None = None):
        """Log orchestration steps for observability."""
        self.current_step = step_name
        if step_name not in self.execution_trace:
            self.execution_trace[step_name] = []

        if data:
            self.execution_trace[step_name].append(data)

        logger.info(f"Orchestration step: {step_name}")


class PeerReviewOrchestrator(AgentOrchestrator):
    """Orchestrates peer review generation workflow."""

    def __init__(self, manager_agent: Agent[None, BaseModel]):
        super().__init__()
        self.manager_agent = manager_agent

    async def run_full_review_workflow(
        self,
        paper_id: str,
        query: UserPromptType,
        usage_limits: UsageLimits | None = None,
    ) -> str:
        """Run complete peer review generation workflow."""
        self.log_step("start_review_workflow", {"paper_id": paper_id})

        try:
            # Step 1: Generate review using manager agent
            self.log_step("generating_review")

            result = await self.manager_agent.run(user_prompt=str(query), usage_limits=usage_limits)

            self.log_step("review_completed")
            return str(result)

        except Exception as e:
            self.log_step("review_failed", {"error": str(e)})
            logger.error(f"Peer review workflow failed: {e}")
            raise


class EvaluationOrchestrator(AgentOrchestrator):
    """Orchestrates multi-tiered evaluation processes."""

    async def run_sequential_evaluation(self, evaluation_tasks: list[dict[str, Any]]) -> list[Any]:
        """Run evaluation tasks in sequence."""
        self.log_step("start_sequential_evaluation")

        results = []
        for i, task in enumerate(evaluation_tasks):
            self.log_step(f"evaluation_step_{i}", task)

            try:
                # Execute evaluation task
                result = await self._execute_evaluation_task(task)
                results.append(result)

            except Exception as e:
                logger.error(f"Evaluation task {i} failed: {e}")
                results.append(None)

        self.log_step("sequential_evaluation_complete")
        return results

    async def run_parallel_evaluation(self, evaluation_tasks: list[dict[str, Any]]) -> list[Any]:
        """Run evaluation tasks in parallel."""
        self.log_step("start_parallel_evaluation")

        tasks = [self._execute_evaluation_task(task) for task in evaluation_tasks]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        self.log_step("parallel_evaluation_complete")
        return results

    async def _execute_evaluation_task(self, task: dict[str, Any]) -> Any:
        """Execute a single evaluation task."""
        task_type = task.get("type")

        if task_type == "traditional_metrics":
            # Execute traditional metrics evaluation
            return await self._run_traditional_metrics(task)
        elif task_type == "llm_judge":
            # Execute LLM judge evaluation
            return await self._run_llm_judge(task)
        elif task_type == "trace_collection":
            # Execute trace collection
            return await self._run_trace_collection(task)
        else:
            raise ValueError(f"Unknown evaluation task type: {task_type}")

    async def _run_traditional_metrics(self, task: dict[str, Any]) -> Any:
        """Execute traditional metrics evaluation."""
        # Placeholder - would integrate with actual traditional metrics
        await asyncio.sleep(0.1)  # Simulate work
        return {"type": "traditional_metrics", "score": 0.8}

    async def _run_llm_judge(self, task: dict[str, Any]) -> Any:
        """Execute LLM judge evaluation."""
        # Placeholder - would integrate with actual LLM judge
        await asyncio.sleep(0.5)  # Simulate work
        return {"type": "llm_judge", "score": 0.7}

    async def _run_trace_collection(self, task: dict[str, Any]) -> Any:
        """Execute trace collection."""
        # Placeholder - would integrate with actual trace collection
        await asyncio.sleep(0.1)  # Simulate work
        return {"type": "trace_collection", "traces_collected": True}


class DelegationOrchestrator(AgentOrchestrator):
    """Orchestrates task delegation between specialized agents."""

    def __init__(
        self,
        manager_agent: Agent[None, BaseModel],
        research_agent: Agent | None = None,
        analysis_agent: Agent | None = None,
        synthesis_agent: Agent | None = None,
    ):
        super().__init__()
        self.manager_agent = manager_agent
        self.research_agent = research_agent
        self.analysis_agent = analysis_agent
        self.synthesis_agent = synthesis_agent

        self._setup_delegation_tools()

    def _setup_delegation_tools(self):
        """Set up delegation tools on the manager agent."""
        if self.research_agent is not None:
            self._add_research_delegation()

        if self.analysis_agent is not None:
            self._add_analysis_delegation()

        if self.synthesis_agent is not None:
            self._add_synthesis_delegation()

    def _add_research_delegation(self):
        """Add research delegation tool to manager."""

        @self.manager_agent.tool
        async def delegate_research(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> ResearchResult | ResearchResultSimple:
            """Delegate research task to ResearchAgent."""
            self.log_step("delegating_research", {"query": query})

            if self.research_agent is None:
                raise ValueError("Research agent not configured")
            result = await self.research_agent.run(query)

            if isinstance(result, ResearchResult | ResearchResultSimple):
                return result
            else:
                return _validate_model_return(str(result), ResearchResult)

    def _add_analysis_delegation(self):
        """Add analysis delegation tool to manager."""

        @self.manager_agent.tool
        async def delegate_analysis(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> AnalysisResult:
            """Delegate analysis task to AnalysisAgent."""
            self.log_step("delegating_analysis", {"query": query})

            if self.analysis_agent is None:
                raise ValueError("Analysis agent not configured")
            result = await self.analysis_agent.run(query)

            if isinstance(result, AnalysisResult):
                return result
            else:
                return _validate_model_return(str(result), AnalysisResult)

    def _add_synthesis_delegation(self):
        """Add synthesis delegation tool to manager."""

        @self.manager_agent.tool
        async def delegate_synthesis(  # type: ignore[reportUnusedFunction]
            ctx: RunContext[None], query: str
        ) -> ResearchSummary:
            """Delegate synthesis task to SynthesisAgent."""
            self.log_step("delegating_synthesis", {"query": query})

            if self.synthesis_agent is None:
                raise ValueError("Synthesis agent not configured")
            result = await self.synthesis_agent.run(query)

            if isinstance(result, ResearchSummary):
                return result
            else:
                return _validate_model_return(str(result), ResearchSummary)


async def run_manager_orchestrated(
    manager: Agent[None, BaseModel],
    query: UserPromptType,
    provider: str,
    usage_limits: UsageLimits | None,
) -> None:
    """
    Run manager agent with orchestration and error handling.

    Args:
        manager: The manager agent to run
        query: The query to process
        provider: Provider name for logging
        usage_limits: Usage limits for the execution
    """
    orchestrator = AgentOrchestrator()
    orchestrator.log_step("starting_manager_execution")

    model_name = getattr(manager, "model")._model_name
    logger.info(f"Researching with {provider}({model_name}) and Topic: {query} ...")

    try:
        orchestrator.log_step("waiting_for_model_response")
        logger.info("Waiting for model response ...")

        result = await manager.run(user_prompt=str(query), usage_limits=usage_limits)

        orchestrator.log_step("model_response_received")
        logger.info(f"Result: {result}")

    except Exception as e:
        orchestrator.log_step("manager_execution_failed", {"error": str(e)})
        logger.error(f"Manager execution failed: {e}")
        raise


# Workflow templates for common orchestration patterns
async def sequential_workflow(agents: list[Agent], query: str) -> list[Any]:
    """Run agents in sequence, passing output to next agent."""
    results = []
    current_input = query

    for i, agent in enumerate(agents):
        logger.info(f"Running agent {i + 1}/{len(agents)}")
        result = await agent.run(current_input)
        results.append(result)
        current_input = str(result)  # Use result as input for next agent

    return results


async def parallel_workflow(agents: list[Agent], query: str) -> list[Any]:
    """Run agents in parallel and aggregate results."""
    logger.info(f"Running {len(agents)} agents in parallel")

    tasks = [agent.run(query) for agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [result for result in results]


async def conditional_workflow(
    condition_func: Callable[[str], str], agent_map: dict[str, Agent], query: str
) -> Any:
    """Route to different agents based on conditions."""
    condition_result = condition_func(query)

    if condition_result in agent_map:
        selected_agent = agent_map[condition_result]
        logger.info(f"Selected agent for condition: {condition_result}")
        result = await selected_agent.run(query)
        return result
    else:
        raise ValueError(f"No agent found for condition: {condition_result}")
