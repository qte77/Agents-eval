"""
Tests for GraphEvaluatorPlugin wrapper.

Verifies the adapter pattern wrapping GraphAnalysisEngine
as an EvaluatorPlugin with configurable timeout.
"""

from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.judge.plugins.base import EvaluatorPlugin
from app.judge.plugins.graph_metrics import GraphEvaluatorPlugin


class TestGraphEvaluatorPlugin:
    """Test suite for GraphEvaluatorPlugin adapter."""

    @pytest.fixture
    def plugin(self):
        """Fixture providing GraphEvaluatorPlugin instance."""
        return GraphEvaluatorPlugin()

    @pytest.fixture
    def plugin_with_timeout(self):
        """Fixture providing plugin with custom timeout."""
        return GraphEvaluatorPlugin(timeout_seconds=10.0)

    @pytest.fixture
    def sample_input(self):
        """Fixture providing sample evaluation input data."""

        class MockEvalInput(BaseModel):
            trace_data: GraphTraceData

        return MockEvalInput(
            trace_data=GraphTraceData(
                execution_id="test_exec_001",
                agent_interactions=[
                    {"from": "agent_1", "to": "agent_2", "type": "delegation"},
                    {"from": "agent_2", "to": "agent_1", "type": "communication"},
                ],
                tool_calls=[
                    {"agent_id": "agent_1", "tool_name": "read_paper", "success": True},
                    {"agent_id": "agent_2", "tool_name": "analyze_methods", "success": True},
                ],
                timing_data={"start": 0.0, "end": 1.5},
            )
        )

    def test_plugin_implements_evaluator_interface(self, plugin):
        """Given GraphEvaluatorPlugin, it should implement EvaluatorPlugin interface."""
        assert isinstance(plugin, EvaluatorPlugin)

    def test_plugin_name_property(self, plugin):
        """Given GraphEvaluatorPlugin, name should be 'graph_metrics'."""
        assert plugin.name == "graph_metrics"

    def test_plugin_tier_property(self, plugin):
        """Given GraphEvaluatorPlugin, tier should be 3."""
        assert plugin.tier == 3

    def test_evaluate_returns_tier3_result(self, plugin, sample_input):
        """Given valid input, evaluate should return Tier3Result."""
        result = plugin.evaluate(sample_input)

        assert isinstance(result, Tier3Result)
        assert isinstance(result, BaseModel)

    def test_evaluate_delegates_to_engine(self, plugin, sample_input):
        """Given evaluation request, should delegate to GraphAnalysisEngine."""
        with patch("app.judge.plugins.graph_metrics.GraphAnalysisEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_graph_metrics.return_value = Tier3Result(
                path_convergence=0.85,
                tool_selection_accuracy=0.90,
                communication_overhead=0.15,
                coordination_centrality=0.80,
                task_distribution_balance=0.88,
                overall_score=0.85,
                graph_complexity=10,
            )

            plugin_new = GraphEvaluatorPlugin()
            result = plugin_new.evaluate(sample_input)

            mock_engine.evaluate_graph_metrics.assert_called_once()
            assert result.overall_score == 0.85

    def test_evaluate_passes_settings_to_engine(self, plugin):
        """Given evaluation request, should pass JudgeSettings to engine."""

        class MockInput(BaseModel):
            trace_data: GraphTraceData

        input_data = MockInput(
            trace_data=GraphTraceData(
                execution_id="test_exec_002",
                agent_interactions=[{"from": "agent_1", "to": "agent_2", "type": "delegation"}],
                tool_calls=[{"agent_id": "agent_1", "tool_name": "tool_1", "success": True}],
                timing_data={"start": 0.0, "end": 0.5},
            )
        )

        with patch("app.judge.plugins.graph_metrics.GraphAnalysisEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.evaluate_graph_metrics.return_value = Tier3Result(
                path_convergence=0.5,
                tool_selection_accuracy=0.5,
                communication_overhead=0.5,
                coordination_centrality=0.5,
                task_distribution_balance=0.5,
                overall_score=0.5,
                graph_complexity=2,
            )

            plugin_new = GraphEvaluatorPlugin()
            plugin_new.evaluate(input_data)

            # Verify engine was initialized with settings
            assert mock_engine_class.call_args is not None
            assert mock_engine_class.call_args.args[0] is not None

    def test_timeout_configuration(self, plugin_with_timeout):
        """Given custom timeout, plugin should store it."""
        assert plugin_with_timeout.timeout_seconds == 10.0

    def test_default_timeout(self, plugin):
        """Given no timeout specified, should use default from JudgeSettings."""
        # Default should come from JudgeSettings.tier3_max_seconds (10.0)
        assert plugin.timeout_seconds == 10.0

    def test_get_context_for_next_tier_returns_dict(self, plugin, sample_input):
        """Given Tier3Result, should extract context (empty for final tier)."""
        result = plugin.evaluate(sample_input)
        context = plugin.get_context_for_next_tier(result)

        assert isinstance(context, dict)
        assert "tier3_overall_score" in context
        assert "tier3_graph_metrics" in context

    def test_get_context_includes_metrics(self, plugin):
        """Given Tier3Result, context should include all graph metrics."""
        mock_result = Tier3Result(
            path_convergence=0.88,
            tool_selection_accuracy=0.92,
            communication_overhead=0.12,
            coordination_centrality=0.90,
            task_distribution_balance=0.87,
            overall_score=0.89,
            graph_complexity=15,
        )

        context = plugin.get_context_for_next_tier(mock_result)

        assert context["tier3_overall_score"] == 0.89
        assert context["tier3_graph_metrics"]["path_convergence"] == 0.88
        assert context["tier3_graph_metrics"]["tool_selection_accuracy"] == 0.92
        assert context["tier3_graph_metrics"]["coordination_centrality"] == 0.90
        assert context["tier3_graph_metrics"]["task_distribution_balance"] == 0.87
        assert context["tier3_graph_complexity"] == 15

    def test_evaluate_with_empty_context(self, plugin, sample_input):
        """Given None context, evaluation should still work."""
        result = plugin.evaluate(sample_input, context=None)
        assert isinstance(result, Tier3Result)

    def test_evaluate_with_context_dict(self, plugin, sample_input):
        """Given context dict from previous tiers, evaluation should use it."""
        context = {
            "tier1_overall_score": 0.75,
            "tier2_overall_score": 0.82,
        }
        result = plugin.evaluate(sample_input, context=context)
        assert isinstance(result, Tier3Result)

    def test_existing_engine_tests_still_pass(self):
        """Given existing GraphAnalysisEngine tests, they should all still pass.

        This is a placeholder to ensure we run the full existing test suite.
        The actual tests are in tests/evals/test_graph_analysis.py.
        """
        # This test passes if we can import the module without breaking existing functionality
        from app.evals.graph_analysis import GraphAnalysisEngine

        from app.evals.settings import JudgeSettings

        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)
        assert engine is not None


class TestGraphEvaluatorPluginIntegration:
    """Integration tests for GraphEvaluatorPlugin with real engine."""

    def test_real_evaluation_workflow(self):
        """Given real inputs, complete evaluation should work end-to-end."""
        plugin = GraphEvaluatorPlugin()

        class EvalInput(BaseModel):
            trace_data: GraphTraceData

        input_data = EvalInput(
            trace_data=GraphTraceData(
                execution_id="integration_test_001",
                agent_interactions=[
                    {"from": "manager", "to": "researcher", "type": "delegation"},
                    {"from": "researcher", "to": "manager", "type": "communication"},
                    {"from": "manager", "to": "analyst", "type": "delegation"},
                ],
                tool_calls=[
                    {"agent_id": "researcher", "tool_name": "read_paper", "success": True},
                    {"agent_id": "analyst", "tool_name": "analyze_data", "success": True},
                    {"agent_id": "manager", "tool_name": "synthesize", "success": True},
                ],
                timing_data={"start": 0.0, "end": 3.5},
            )
        )

        result = plugin.evaluate(input_data)

        # Verify result structure
        assert isinstance(result, Tier3Result)
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.path_convergence <= 1.0
        assert 0.0 <= result.tool_selection_accuracy <= 1.0
        assert 0.0 <= result.coordination_centrality <= 1.0
        assert 0.0 <= result.task_distribution_balance <= 1.0
        assert result.graph_complexity > 0

        # Verify context extraction
        context = plugin.get_context_for_next_tier(result)
        assert context["tier3_overall_score"] == result.overall_score
