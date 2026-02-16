"""
Tests for TraditionalMetricsPlugin wrapper.

Verifies the adapter pattern wrapping TraditionalMetricsEngine
as an EvaluatorPlugin with configurable timeout.
"""

import time
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from app.data_models.evaluation_models import Tier1Result
from app.judge.plugins.base import EvaluatorPlugin
from app.judge.plugins.traditional import TraditionalMetricsPlugin


class TestTraditionalMetricsPlugin:
    """Test suite for TraditionalMetricsPlugin adapter."""

    @pytest.fixture
    def plugin(self):
        """Fixture providing TraditionalMetricsPlugin instance."""
        return TraditionalMetricsPlugin()

    @pytest.fixture
    def plugin_with_timeout(self):
        """Fixture providing plugin with custom timeout."""
        return TraditionalMetricsPlugin(timeout_seconds=5.0)

    @pytest.fixture
    def sample_input(self):
        """Fixture providing sample evaluation input data."""

        class MockEvalInput(BaseModel):
            agent_output: str
            reference_texts: list[str]
            start_time: float
            end_time: float

        return MockEvalInput(
            agent_output="This paper presents a novel approach to machine learning.",
            reference_texts=[
                "The work demonstrates strong technical contribution.",
                "Solid methodology with good evaluation.",
            ],
            start_time=0.0,
            end_time=0.5,
        )

    def test_evaluate_returns_tier1_result(self, plugin, sample_input):
        """Given valid input, evaluate should return Tier1Result."""
        result = plugin.evaluate(sample_input)

        assert isinstance(result, Tier1Result)
        assert isinstance(result, BaseModel)

    def test_evaluate_delegates_to_engine(self, plugin, sample_input):
        """Given evaluation request, should delegate to TraditionalMetricsEngine."""
        with patch("app.judge.plugins.traditional.TraditionalMetricsEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_traditional_metrics.return_value = Tier1Result(
                cosine_score=0.8,
                jaccard_score=0.75,
                semantic_score=0.82,
                execution_time=0.5,
                time_score=0.9,
                task_success=1.0,
                overall_score=0.81,
            )

            plugin_new = TraditionalMetricsPlugin()
            result = plugin_new.evaluate(sample_input)

            mock_engine.evaluate_traditional_metrics.assert_called_once()
            assert result.overall_score == 0.81

    def test_evaluate_passes_settings_to_engine(self, plugin):
        """Given evaluation request, should pass JudgeSettings to engine."""

        class MockInput(BaseModel):
            agent_output: str
            reference_texts: list[str]
            start_time: float
            end_time: float

        input_data = MockInput(
            agent_output="Test review",
            reference_texts=["Reference review"],
            start_time=0.0,
            end_time=0.1,
        )

        with patch("app.judge.plugins.traditional.TraditionalMetricsEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_traditional_metrics.return_value = Tier1Result(
                cosine_score=0.5,
                jaccard_score=0.5,
                semantic_score=0.5,
                execution_time=0.1,
                time_score=0.8,
                task_success=0.0,
                overall_score=0.52,
            )

            plugin_new = TraditionalMetricsPlugin()
            plugin_new.evaluate(input_data)

            # Verify settings were passed
            call_args = mock_engine.evaluate_traditional_metrics.call_args
            assert call_args.kwargs.get("settings") is not None

    def test_timeout_configuration(self, plugin_with_timeout):
        """Given custom timeout, plugin should store it."""
        assert plugin_with_timeout.timeout_seconds == 5.0

    def test_default_timeout(self, plugin):
        """Given no timeout specified, should use default from JudgeSettings."""
        # Default should come from JudgeSettings.tier1_max_seconds (1.0)
        assert plugin.timeout_seconds == 1.0

    def test_get_context_for_next_tier_returns_dict(self, plugin, sample_input):
        """Given Tier1Result, should extract context for Tier 2."""
        result = plugin.evaluate(sample_input)
        context = plugin.get_context_for_next_tier(result)

        assert isinstance(context, dict)
        assert "tier1_overall_score" in context
        assert "tier1_similarity_metrics" in context

    def test_get_context_includes_metrics(self, plugin):
        """Given Tier1Result, context should include all similarity metrics."""
        mock_result = Tier1Result(
            cosine_score=0.85,
            jaccard_score=0.78,
            semantic_score=0.82,
            execution_time=0.3,
            time_score=0.95,
            task_success=1.0,
            overall_score=0.83,
        )

        context = plugin.get_context_for_next_tier(mock_result)

        assert context["tier1_overall_score"] == 0.83
        assert context["tier1_similarity_metrics"]["cosine"] == 0.85
        assert context["tier1_similarity_metrics"]["jaccard"] == 0.78
        assert context["tier1_similarity_metrics"]["semantic"] == 0.82

    def test_evaluate_with_empty_context(self, plugin, sample_input):
        """Given None context, evaluation should still work."""
        result = plugin.evaluate(sample_input, context=None)
        assert isinstance(result, Tier1Result)

    def test_evaluate_with_context_dict(self, plugin, sample_input):
        """Given context dict, evaluation should ignore it (Tier 1 doesn't use context)."""
        context = {"some_key": "some_value"}
        result = plugin.evaluate(sample_input, context=context)
        assert isinstance(result, Tier1Result)

    def test_existing_engine_tests_still_pass(self):
        """Given existing TraditionalMetricsEngine tests, they should all still pass.

        This is a placeholder to ensure we run the full existing test suite.
        The actual tests are in tests/evals/test_traditional_metrics.py.
        """
        # This test passes if we can import the module without breaking existing functionality
        from app.judge.traditional_metrics import TraditionalMetricsEngine

        engine = TraditionalMetricsEngine()
        assert engine is not None


class TestTraditionalMetricsPluginIntegration:
    """Integration tests for TraditionalMetricsPlugin with real engine."""

    def test_real_evaluation_workflow(self):
        """Given real inputs, complete evaluation should work end-to-end."""
        plugin = TraditionalMetricsPlugin()

        class EvalInput(BaseModel):
            agent_output: str
            reference_texts: list[str]
            start_time: float
            end_time: float

        input_data = EvalInput(
            agent_output="This paper presents a comprehensive study with solid methodology.",
            reference_texts=[
                "The work demonstrates strong technical approach with good evaluation.",
                "Excellent contribution to the field with clear presentation.",
            ],
            start_time=time.perf_counter(),
            end_time=time.perf_counter() + 0.1,
        )

        result = plugin.evaluate(input_data)

        # Verify result structure
        assert isinstance(result, Tier1Result)
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.cosine_score <= 1.0
        assert 0.0 <= result.jaccard_score <= 1.0
        assert 0.0 <= result.semantic_score <= 1.0

        # Verify context extraction
        context = plugin.get_context_for_next_tier(result)
        assert context["tier1_overall_score"] == result.overall_score
