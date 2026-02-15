"""
Tests for JudgeAgent orchestrator.

Tests the agent that replaces EvaluationPipeline, using PluginRegistry
for tier-ordered plugin execution with context passing.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from app.data_models.evaluation_models import CompositeResult, GraphTraceData
from app.judge.agent import JudgeAgent
from app.judge.plugins import (
    GraphEvaluatorPlugin,
    LLMJudgePlugin,
    TraditionalMetricsPlugin,
)


class MockEvaluationInput(BaseModel):
    """Mock input for evaluation."""

    paper: str
    review: str
    reference_reviews: list[str] | None = None
    execution_trace: GraphTraceData | None = None


class TestJudgeAgent:
    """Test JudgeAgent orchestrator."""

    def test_judge_agent_initializes_with_settings(self):
        """JudgeAgent initializes with JudgeSettings."""
        # This will fail until JudgeAgent is implemented
        from app.evals.settings import JudgeSettings

        settings = JudgeSettings()
        agent = JudgeAgent(settings=settings)
        assert agent is not None
        assert agent.settings == settings

    def test_judge_agent_registers_plugins_automatically(self):
        """JudgeAgent automatically registers all three tier plugins."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()
        plugins = agent.registry.list_plugins()
        assert len(plugins) == 3
        assert any(isinstance(p, TraditionalMetricsPlugin) for p in plugins)
        assert any(isinstance(p, LLMJudgePlugin) for p in plugins)
        assert any(isinstance(p, GraphEvaluatorPlugin) for p in plugins)

    async def test_judge_agent_executes_tiers_in_order(self):
        """JudgeAgent executes plugins in tier order 1→2→3."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()
        input_data = MockEvaluationInput(
            paper="Sample paper text", review="Sample review text"
        )

        # Should execute in tier order
        result = await agent.evaluate_comprehensive(
            paper=input_data.paper,
            review=input_data.review,
            execution_trace=input_data.execution_trace,
            reference_reviews=input_data.reference_reviews,
        )

        assert isinstance(result, CompositeResult)
        assert result.composite_score >= 0.0
        assert result.composite_score <= 1.0

    async def test_judge_agent_passes_context_between_tiers(self):
        """JudgeAgent passes context from Tier 1 → Tier 2 → Tier 3."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()

        # Execute evaluation
        result = await agent.evaluate_comprehensive(
            paper="Sample paper", review="Sample review"
        )

        # Verify context passing occurred (check trace store)
        assert result.evaluation_complete

    async def test_judge_agent_handles_graceful_degradation(self):
        """JudgeAgent handles tier failures with graceful degradation."""
        # This will fail until JudgeAgent is implemented
        from app.evals.settings import JudgeSettings

        # Disable Tier 2
        settings = JudgeSettings(tier2_enabled=False)
        agent = JudgeAgent(settings=settings)

        result = await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        # Should still complete with Tier 1 and Tier 3
        assert result.composite_score >= 0.0
        assert result.tier2_score is None  # Tier 2 skipped

    async def test_judge_agent_stores_traces(self):
        """JudgeAgent stores execution traces in TraceStore."""
        # This will fail until JudgeAgent and TraceStore are implemented
        agent = JudgeAgent()

        await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        # Verify traces were stored
        assert agent.trace_store is not None
        traces = agent.trace_store.get_all_traces()
        assert len(traces) > 0

    async def test_judge_agent_returns_composite_result(self):
        """JudgeAgent returns CompositeResult from composite scorer."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()

        result = await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        assert isinstance(result, CompositeResult)
        assert hasattr(result, "composite_score")
        assert hasattr(result, "recommendation")
        assert hasattr(result, "tier1_score")
        assert hasattr(result, "tier2_score")
        assert hasattr(result, "tier3_score")

    async def test_judge_agent_respects_enabled_tiers(self):
        """JudgeAgent only executes enabled tiers."""
        # This will fail until JudgeAgent is implemented
        from app.evals.settings import JudgeSettings

        # Only enable Tier 1
        settings = JudgeSettings(tier1_enabled=True, tier2_enabled=False, tier3_enabled=False)
        agent = JudgeAgent(settings=settings)

        result = await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        # Only Tier 1 should have results
        assert result.tier1_score is not None
        assert result.tier2_score is None
        assert result.tier3_score is None


class TestJudgeAgentPerformanceMonitoring:
    """Test JudgeAgent performance monitoring integration."""

    async def test_judge_agent_records_execution_time(self):
        """JudgeAgent records execution time for each tier."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()

        await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        stats = agent.get_execution_stats()
        assert "tier1_time" in stats
        assert "tier2_time" in stats
        assert "tier3_time" in stats
        assert "total_time" in stats

    async def test_judge_agent_detects_bottlenecks(self):
        """JudgeAgent detects performance bottlenecks."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()

        await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        stats = agent.get_execution_stats()
        assert "bottlenecks_detected" in stats


class TestJudgeAgentBackwardCompatibility:
    """Test JudgeAgent maintains backward compatibility."""

    def test_judge_agent_has_same_interface_as_pipeline(self):
        """JudgeAgent exposes same interface as EvaluationPipeline."""
        # This will fail until JudgeAgent is implemented
        agent = JudgeAgent()

        # Should have same methods as EvaluationPipeline
        assert hasattr(agent, "evaluate_comprehensive")
        assert hasattr(agent, "get_execution_stats")
        assert hasattr(agent, "enabled_tiers")
        assert hasattr(agent, "performance_targets")

    def test_evaluation_pipeline_re_export_works(self):
        """EvaluationPipeline re-export from evals module works."""
        # This will fail until re-export shim is implemented
        from app.evals.evaluation_pipeline import EvaluationPipeline

        # Should be able to import and use EvaluationPipeline
        pipeline = EvaluationPipeline()
        assert pipeline is not None
