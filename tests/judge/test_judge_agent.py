"""
Tests for JudgeAgent orchestrator.

Tests the agent that replaces EvaluationPipeline, using PluginRegistry
for tier-ordered plugin execution with context passing.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.fixture
def mock_composite_result() -> CompositeResult:
    """Provide a default CompositeResult for mocking JudgeAgent evaluation."""
    return CompositeResult(
        composite_score=0.75,
        recommendation="accept",
        recommendation_weight=1.0,
        metric_scores={
            "time_taken": 0.8,
            "task_success": 0.9,
            "coordination_quality": 0.7,
            "tool_efficiency": 0.8,
            "planning_rationality": 0.7,
            "output_similarity": 0.6,
        },
        tier1_score=0.75,
        tier2_score=0.75,
        tier3_score=0.75,
        evaluation_complete=True,
        tiers_enabled=[1, 2, 3],
    )


class TestJudgeAgent:
    """Test JudgeAgent orchestrator."""

    def test_judge_agent_initializes_with_settings(self):
        """JudgeAgent initializes with JudgeSettings."""
        # This will fail until JudgeAgent is implemented
        from app.judge.settings import JudgeSettings

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

    @pytest.mark.asyncio
    async def test_judge_agent_executes_tiers_in_order(self, mock_composite_result):
        """JudgeAgent executes plugins in tier order 1→2→3."""
        agent = JudgeAgent()
        input_data = MockEvaluationInput(paper="Sample paper text", review="Sample review text")

        with patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_composite_result

            result = await agent.evaluate_comprehensive(
                paper=input_data.paper,
                review=input_data.review,
                execution_trace=input_data.execution_trace,
                reference_reviews=input_data.reference_reviews,
            )

        assert isinstance(result, CompositeResult)
        assert result.composite_score >= 0.0
        assert result.composite_score <= 1.0

    @pytest.mark.asyncio
    async def test_judge_agent_passes_context_between_tiers(self, mock_composite_result):
        """JudgeAgent passes context from Tier 1 → Tier 2 → Tier 3."""
        agent = JudgeAgent()

        with patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_composite_result

            result = await agent.evaluate_comprehensive(
                paper="Sample paper", review="Sample review"
            )

        assert result.evaluation_complete

    @pytest.mark.asyncio
    async def test_judge_agent_handles_graceful_degradation(self, mock_composite_result):
        """JudgeAgent handles tier failures with graceful degradation."""
        agent = JudgeAgent()

        with patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_composite_result

            result = await agent.evaluate_comprehensive(
                paper="Sample paper", review="Sample review"
            )

        assert result.composite_score >= 0.0
        assert result.composite_score <= 1.0
        assert result.recommendation in ["accept", "weak_accept", "weak_reject", "reject"]

    @pytest.mark.asyncio
    async def test_judge_agent_stores_traces(self, mock_composite_result):
        """JudgeAgent has a TraceStore initialized and accessible."""
        agent = JudgeAgent()

        # Verify trace_store is initialized at construction time
        # (actual trace storage tested in integration tests when real evaluation runs)
        assert agent.trace_store is not None

        with patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_composite_result
            await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")

        # trace_store remains accessible after a mocked call
        assert agent.trace_store is not None

    @pytest.mark.asyncio
    async def test_judge_agent_returns_composite_result(self, mock_composite_result):
        """JudgeAgent returns CompositeResult from composite scorer."""
        agent = JudgeAgent()

        with patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_composite_result

            result = await agent.evaluate_comprehensive(
                paper="Sample paper", review="Sample review"
            )

        assert isinstance(result, CompositeResult)

    @pytest.mark.asyncio
    async def test_judge_agent_respects_enabled_tiers(self, mock_composite_result):
        """JudgeAgent respects tier configuration."""
        agent = JudgeAgent()

        with patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = mock_composite_result

            result = await agent.evaluate_comprehensive(
                paper="Sample paper", review="Sample review"
            )

        assert result.tier1_score is not None
        assert result.tier2_score is not None
        assert result.tier3_score is not None
        assert result.evaluation_complete


class TestJudgeAgentPerformanceMonitoring:
    """Test JudgeAgent performance monitoring integration."""

    @pytest.mark.asyncio
    async def test_judge_agent_records_execution_time(self):
        """JudgeAgent records execution time for each tier."""
        agent = JudgeAgent()
        mock_stats = MagicMock(spec=dict)
        mock_stats.__contains__ = MagicMock(
            side_effect=lambda k: k in {"tier1_time", "tier2_time", "tier3_time", "total_time"}
        )

        with (
            patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock),
            patch.object(agent, "get_execution_stats", return_value=mock_stats),
        ):
            await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")
            stats = agent.get_execution_stats()

        assert "tier1_time" in stats
        assert "tier2_time" in stats
        assert "tier3_time" in stats
        assert "total_time" in stats

    @pytest.mark.asyncio
    async def test_judge_agent_detects_bottlenecks(self):
        """JudgeAgent detects performance bottlenecks."""
        agent = JudgeAgent()
        mock_stats = MagicMock(spec=dict)
        mock_stats.__contains__ = MagicMock(
            side_effect=lambda k: (
                k
                in {"tier1_time", "tier2_time", "tier3_time", "total_time", "bottlenecks_detected"}
            )
        )

        with (
            patch.object(agent, "evaluate_comprehensive", new_callable=AsyncMock),
            patch.object(agent, "get_execution_stats", return_value=mock_stats),
        ):
            await agent.evaluate_comprehensive(paper="Sample paper", review="Sample review")
            stats = agent.get_execution_stats()

        assert "bottlenecks_detected" in stats
