"""
Tests for LLMJudgePlugin wrapper.

Verifies the adapter pattern wrapping LLMJudgeEngine
as an EvaluatorPlugin with opt-in Tier 1 context enrichment.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from app.data_models.evaluation_models import Tier2Result
from app.judge.plugins.llm_judge import LLMJudgePlugin


class TestLLMJudgePlugin:
    """Test suite for LLMJudgePlugin adapter."""

    @pytest.fixture
    def plugin(self):
        """Fixture providing LLMJudgePlugin instance."""
        return LLMJudgePlugin()

    @pytest.fixture
    def plugin_with_timeout(self):
        """Fixture providing plugin with custom timeout."""
        return LLMJudgePlugin(timeout_seconds=15.0)

    @pytest.fixture
    def sample_input(self):
        """Fixture providing sample evaluation input data."""

        class MockEvalInput(BaseModel):
            paper: str
            review: str
            execution_trace: dict

        return MockEvalInput(
            paper="This is a scientific paper about machine learning.",
            review="This paper presents a novel approach to deep learning.",
            execution_trace={
                "agent_interactions": [{"type": "analysis", "agent": "reviewer"}],
                "tool_calls": [{"tool": "search", "result": "success"}],
            },
        )

    @pytest.fixture
    def tier1_context(self):
        """Fixture providing Tier 1 context for enrichment."""
        return {
            "tier1_overall_score": 0.82,
            "tier1_similarity_metrics": {
                "cosine": 0.85,
                "jaccard": 0.78,
                "semantic": 0.82,
            },
            "tier1_execution_time": 0.3,
            "tier1_task_success": 1.0,
        }

    def test_evaluate_returns_tier2_result(self, plugin, sample_input):
        """Given valid input, evaluate should return Tier2Result."""
        with patch("app.judge.plugins.llm_judge.LLMJudgeEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_comprehensive = AsyncMock(
                return_value=Tier2Result(
                    technical_accuracy=0.85,
                    constructiveness=0.78,
                    planning_rationality=0.82,
                    overall_score=0.81,
                    model_used="openai/gpt-4o-mini",
                    api_cost=0.001,
                    fallback_used=False,
                )
            )

            plugin_new = LLMJudgePlugin()
            result = plugin_new.evaluate(sample_input)

            assert isinstance(result, Tier2Result)
            assert isinstance(result, BaseModel)

    def test_evaluate_delegates_to_engine(self, plugin, sample_input):
        """Given evaluation request, should delegate to LLMJudgeEngine."""
        with patch("app.judge.plugins.llm_judge.LLMJudgeEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_comprehensive = AsyncMock(
                return_value=Tier2Result(
                    technical_accuracy=0.85,
                    constructiveness=0.78,
                    planning_rationality=0.82,
                    overall_score=0.81,
                    model_used="openai/gpt-4o-mini",
                    api_cost=0.001,
                    fallback_used=False,
                )
            )

            plugin_new = LLMJudgePlugin()
            result = plugin_new.evaluate(sample_input)

            mock_engine.evaluate_comprehensive.assert_called_once()
            assert result.overall_score == 0.81

    def test_timeout_configuration(self, plugin_with_timeout):
        """Given custom timeout, plugin should store it."""
        assert plugin_with_timeout.timeout_seconds == 15.0

    def test_default_timeout(self, plugin):
        """Given no timeout specified, should use default from JudgeSettings."""
        # Default should come from JudgeSettings.tier2_timeout_seconds (30.0)
        assert plugin.timeout_seconds == 30.0

    def test_evaluate_with_tier1_context(self, plugin, sample_input, tier1_context):
        """Given Tier 1 context, evaluation should use it for enrichment."""
        with patch("app.judge.plugins.llm_judge.LLMJudgeEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_comprehensive = AsyncMock(
                return_value=Tier2Result(
                    technical_accuracy=0.85,
                    constructiveness=0.78,
                    planning_rationality=0.82,
                    overall_score=0.81,
                    model_used="openai/gpt-4o-mini",
                    api_cost=0.001,
                    fallback_used=False,
                )
            )

            plugin_new = LLMJudgePlugin()
            result = plugin_new.evaluate(sample_input, context=tier1_context)

            # Verify context was available during evaluation
            assert isinstance(result, Tier2Result)

    def test_evaluate_without_context(self, plugin, sample_input):
        """Given no context, evaluation should still work."""
        with patch("app.judge.plugins.llm_judge.LLMJudgeEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_comprehensive = AsyncMock(
                return_value=Tier2Result(
                    technical_accuracy=0.85,
                    constructiveness=0.78,
                    planning_rationality=0.82,
                    overall_score=0.81,
                    model_used="openai/gpt-4o-mini",
                    api_cost=0.001,
                    fallback_used=False,
                )
            )

            plugin_new = LLMJudgePlugin()
            result = plugin_new.evaluate(sample_input, context=None)

            assert isinstance(result, Tier2Result)

    def test_get_context_for_next_tier_returns_dict(self, plugin):
        """Given Tier2Result, should extract context for Tier 3."""
        mock_result = Tier2Result(
            technical_accuracy=0.85,
            constructiveness=0.78,
            planning_rationality=0.82,
            overall_score=0.81,
            model_used="openai/gpt-4o-mini",
            api_cost=0.001,
            fallback_used=False,
        )

        context = plugin.get_context_for_next_tier(mock_result)

        assert isinstance(context, dict)
        assert "tier2_overall_score" in context
        assert "tier2_quality_metrics" in context

    def test_get_context_includes_metrics(self, plugin):
        """Given Tier2Result, context should include all quality metrics."""
        mock_result = Tier2Result(
            technical_accuracy=0.85,
            constructiveness=0.78,
            planning_rationality=0.82,
            overall_score=0.81,
            model_used="openai/gpt-4o-mini",
            api_cost=0.001,
            fallback_used=False,
        )

        context = plugin.get_context_for_next_tier(mock_result)

        assert context["tier2_overall_score"] == 0.81
        assert context["tier2_quality_metrics"]["technical_accuracy"] == 0.85
        assert context["tier2_quality_metrics"]["constructiveness"] == 0.78
        assert context["tier2_quality_metrics"]["planning_rationality"] == 0.82

    def test_get_context_includes_metadata(self, plugin):
        """Given Tier2Result with metadata, context should include it."""
        mock_result = Tier2Result(
            technical_accuracy=0.85,
            constructiveness=0.78,
            planning_rationality=0.82,
            overall_score=0.81,
            model_used="openai/gpt-4o-mini",
            api_cost=0.001,
            fallback_used=True,
        )

        context = plugin.get_context_for_next_tier(mock_result)

        assert context["tier2_model_used"] == "openai/gpt-4o-mini"
        assert context["tier2_fallback_used"] is True
