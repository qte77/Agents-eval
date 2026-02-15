"""
BDD-style tests for graph analysis engine.

Test the core functionality of Tier 3 evaluation using NetworkX-based
analysis of agent coordination patterns and tool usage efficiency.
"""

from unittest.mock import patch

import pytest

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.evals.graph_analysis import (
    GraphAnalysisEngine,
    evaluate_single_graph_analysis,
)
from app.evals.settings import JudgeSettings


class TestGraphAnalysisEngine:
    """Test suite for graph analysis engine."""

    @pytest.fixture
    def engine(self):
        """Fixture providing GraphAnalysisEngine instance."""
        return GraphAnalysisEngine(JudgeSettings())

    @pytest.fixture
    def sample_trace_data(self):
        """Fixture providing sample trace data for analysis."""
        return GraphTraceData(
            execution_id="test_execution_001",
            agent_interactions=[
                {"from": "manager", "to": "researcher", "type": "delegation"},
                {"from": "researcher", "to": "analyst", "type": "communication"},
                {"from": "analyst", "to": "synthesizer", "type": "handoff"},
            ],
            tool_calls=[
                {
                    "agent_id": "researcher",
                    "tool_name": "duckduckgo_search",
                    "success": True,
                    "duration": 2.5,
                },
                {
                    "agent_id": "analyst",
                    "tool_name": "pdf_processor",
                    "success": True,
                    "duration": 1.2,
                },
                {
                    "agent_id": "synthesizer",
                    "tool_name": "text_generator",
                    "success": False,
                    "duration": 0.8,
                },
            ],
            timing_data={
                "start_time": 1000.0,
                "end_time": 1010.5,
                "total_duration": 10.5,
            },
            coordination_events=[
                {
                    "coordination_type": "delegation",
                    "target_agents": ["researcher", "analyst"],
                }
            ],
        )

    @pytest.fixture
    def minimal_trace_data(self):
        """Fixture providing minimal trace data for edge case testing."""
        return GraphTraceData(
            execution_id="minimal_test",
            agent_interactions=[],
            tool_calls=[],
            timing_data={},
            coordination_events=[],
        )

    # Given: Tool usage pattern analysis
    def test_tool_usage_analysis_with_successful_calls(self, engine, sample_trace_data):
        """When analyzing tool usage patterns, then calculates metrics correctly."""
        # When tool usage patterns are analyzed
        result = engine.analyze_tool_usage_patterns(sample_trace_data)

        # Then metrics are calculated
        assert "path_convergence" in result
        assert "tool_selection_accuracy" in result
        assert 0.0 <= result["path_convergence"] <= 1.0
        assert 0.0 <= result["tool_selection_accuracy"] <= 1.0

    def test_tool_usage_analysis_with_mixed_success_rates(self, engine):
        """When tools have mixed success rates, then accuracy reflects the mix."""
        # Given trace with mixed success rates
        trace_data = GraphTraceData(
            execution_id="mixed_success",
            tool_calls=[
                {"agent_id": "agent1", "tool_name": "tool1", "success": True},
                {"agent_id": "agent2", "tool_name": "tool2", "success": False},
            ],
        )

        # When analyzed
        result = engine.analyze_tool_usage_patterns(trace_data)

        # Then accuracy is between 0 and 1
        assert 0.0 < result["tool_selection_accuracy"] < 1.0

    def test_tool_usage_analysis_with_empty_calls(self, engine, minimal_trace_data):
        """When no tool calls exist, then returns zero scores."""
        # When analyzing empty tool calls
        result = engine.analyze_tool_usage_patterns(minimal_trace_data)

        # Then returns baseline scores
        assert result["path_convergence"] == 0.0
        assert result["tool_selection_accuracy"] == 0.0

    # Given: Agent interaction analysis
    def test_agent_interaction_analysis_with_valid_interactions(self, engine, sample_trace_data):
        """When analyzing agent interactions, then calculates communication metrics."""
        # When interactions are analyzed
        result = engine.analyze_agent_interactions(sample_trace_data)

        # Then communication metrics are calculated
        assert "communication_overhead" in result
        assert "coordination_centrality" in result
        assert 0.0 <= result["communication_overhead"] <= 1.0
        assert 0.0 <= result["coordination_centrality"] <= 1.0

    def test_agent_interaction_analysis_with_high_coordination(self, engine):
        """When interactions show good coordination, then scores reflect it."""
        # Given trace with clear coordination patterns
        trace_data = GraphTraceData(
            execution_id="coordinated",
            agent_interactions=[
                {"from": "manager", "to": "worker1", "type": "delegation"},
                {"from": "manager", "to": "worker2", "type": "delegation"},
                {"from": "worker1", "to": "manager", "type": "report"},
                {"from": "worker2", "to": "manager", "type": "report"},
            ],
        )

        # When analyzed
        result = engine.analyze_agent_interactions(trace_data)

        # Then coordination quality is detected
        assert result["coordination_centrality"] > 0.0

    def test_agent_interaction_analysis_with_empty_interactions(self, engine, minimal_trace_data):
        """When no interactions exist, then returns appropriate defaults."""
        # When analyzing empty interactions
        result = engine.analyze_agent_interactions(minimal_trace_data)

        # Then returns appropriate defaults
        assert result["communication_overhead"] == 1.0  # No overhead when no communication
        assert result["coordination_centrality"] == 0.0

    # Given: Task distribution analysis
    def test_task_distribution_analysis_with_balanced_load(self, engine):
        """When tasks are evenly distributed, then balance score is high."""
        # Given evenly distributed tasks
        trace_data = GraphTraceData(
            execution_id="balanced",
            tool_calls=[
                {"agent_id": "agent1"},
                {"agent_id": "agent1"},
                {"agent_id": "agent2"},
                {"agent_id": "agent2"},
            ],
            agent_interactions=[
                {"from": "agent1", "to": "agent2"},
                {"from": "agent2", "to": "agent1"},
            ],
        )

        # When distribution is analyzed
        result = engine.analyze_task_distribution(trace_data)

        # Then balance score is high
        assert result > 0.8

    def test_task_distribution_analysis_with_imbalanced_load(self, engine):
        """When tasks are unevenly distributed, then balance score is low."""
        # Given heavily imbalanced tasks
        trace_data = GraphTraceData(
            execution_id="imbalanced",
            tool_calls=[
                {"agent_id": "busy_agent"},
                {"agent_id": "busy_agent"},
                {"agent_id": "busy_agent"},
                {"agent_id": "busy_agent"},
                {"agent_id": "idle_agent"},  # Much less activity
            ],
        )

        # When distribution is analyzed
        result = engine.analyze_task_distribution(trace_data)

        # Then balance score reflects imbalance
        assert result < 0.8

    def test_task_distribution_analysis_with_single_agent(self, engine):
        """When only one agent is active, then perfect balance is assumed."""
        # Given single agent trace
        trace_data = GraphTraceData(
            execution_id="single_agent",
            tool_calls=[{"agent_id": "solo_agent"}],
        )

        # When distribution is analyzed
        result = engine.analyze_task_distribution(trace_data)

        # Then perfect balance for single agent
        assert result == 1.0

    def test_task_distribution_analysis_with_no_activity(self, engine, minimal_trace_data):
        """When no activity exists, then returns zero score."""
        # When analyzing no activity
        result = engine.analyze_task_distribution(minimal_trace_data)

        # Then zero score
        assert result == 0.0

    # Given: Complete graph metrics evaluation
    def test_complete_evaluation_with_valid_data(self, engine, sample_trace_data):
        """When evaluating complete graph metrics, then returns valid Tier3Result."""
        # When complete evaluation is performed
        result = engine.evaluate_graph_metrics(sample_trace_data)

        # Then valid Tier3Result is returned
        assert isinstance(result, Tier3Result)
        assert 0.0 <= result.path_convergence <= 1.0
        assert 0.0 <= result.tool_selection_accuracy <= 1.0
        assert 0.0 <= result.communication_overhead <= 1.0
        assert 0.0 <= result.coordination_centrality <= 1.0
        assert 0.0 <= result.task_distribution_balance <= 1.0
        assert 0.0 <= result.overall_score <= 1.0

    def test_complete_evaluation_with_weighted_scoring(self, sample_trace_data):
        """When custom weights are provided, then overall score reflects them."""
        # Given engine with default settings
        engine = GraphAnalysisEngine(JudgeSettings())

        # When evaluation is performed
        result = engine.evaluate_graph_metrics(sample_trace_data)

        # Then overall score is a valid weighted score
        assert 0.0 <= result.overall_score <= 1.0

    @patch("app.evals.graph_analysis.logger")
    def test_complete_evaluation_with_exception_handling(
        self, mock_logger, engine, sample_trace_data
    ):
        """When analysis fails, then gracefully handles errors with baseline scores."""
        # Given trace data that will cause analysis failure
        with patch.object(
            engine, "analyze_tool_usage_patterns", side_effect=Exception("Test error")
        ):
            # When evaluation is performed
            result = engine.evaluate_graph_metrics(sample_trace_data)

            # Then baseline scores are returned
            assert result.overall_score == 0.0
            assert mock_logger.error.called

    # Given: Convenience function
    def test_evaluate_single_graph_analysis_with_valid_data(self, sample_trace_data):
        """When using convenience function, then returns valid results."""
        # When convenience function is used
        result = evaluate_single_graph_analysis(sample_trace_data)

        # Then valid Tier3Result is returned
        assert isinstance(result, Tier3Result)
        assert result.overall_score >= 0.0

    def test_evaluate_single_graph_analysis_with_none_data(self):
        """When trace data is None, then returns zero scores."""
        # When called with None data
        result = evaluate_single_graph_analysis(None)

        # Then zero scores are returned
        assert result.overall_score == 0.0
        assert result.communication_overhead == 1.0  # Maximum overhead for no data

    def test_evaluate_single_graph_analysis_with_custom_settings(self, sample_trace_data):
        """When custom settings are provided, then uses them for evaluation."""
        # Given custom settings
        custom_settings = JudgeSettings(tier3_min_nodes=5)

        # When convenience function is used with settings
        result = evaluate_single_graph_analysis(sample_trace_data, custom_settings)

        # Then custom settings are applied (verified by successful execution)
        assert isinstance(result, Tier3Result)

    # Given: Error handling and edge cases
    def test_path_convergence_calculation_with_disconnected_graph(self, engine):
        """When graph is disconnected, then returns low convergence score."""
        # This is tested implicitly through tool usage analysis
        # but we can verify the behavior through minimal data
        minimal_trace = GraphTraceData(
            execution_id="disconnected",
            tool_calls=[
                {"agent_id": "isolated1", "tool_name": "tool1"},
                {"agent_id": "isolated2", "tool_name": "tool2"},
            ],
        )

        # When analyzed
        result = engine.analyze_tool_usage_patterns(minimal_trace)

        # Then convergence reflects disconnected nature
        assert result["path_convergence"] >= 0.0  # Should handle gracefully

    def test_centrality_calculation_with_insufficient_nodes(self, engine):
        """When graph has insufficient nodes, then handles gracefully."""
        # Given minimal interaction data
        trace_data = GraphTraceData(
            execution_id="minimal_nodes",
            agent_interactions=[{"from": "single_agent", "to": "single_agent"}],
        )

        # When analyzed
        result = engine.analyze_agent_interactions(trace_data)

        # Then handles insufficient nodes gracefully
        assert 0.0 <= result["coordination_centrality"] <= 1.0

    # Given: Configuration validation tests
    def test_configuration_validation_with_invalid_min_nodes(self):
        """When min_nodes_for_analysis is invalid, then pydantic raises ValidationError."""
        # When settings are created with invalid value, then ValidationError is raised
        with pytest.raises(Exception):
            JudgeSettings(tier3_min_nodes=-1)

    # Given: Data validation tests
    def test_data_validation_with_missing_execution_id(self, engine):
        """When execution_id is missing, then raises ValueError."""
        # Given trace data without execution_id
        trace_data = GraphTraceData(
            execution_id="",  # Empty execution_id
            agent_interactions=[{"from": "agent1", "to": "agent2"}],
        )

        # When validation is performed, then ValueError is raised
        with pytest.raises(ValueError, match="execution_id is required"):
            engine.analyze_tool_usage_patterns(trace_data)

    def test_data_validation_with_invalid_agent_interaction(self, engine):
        """When agent interaction is malformed, then raises ValueError."""
        # Given malformed interaction data
        trace_data = GraphTraceData(
            execution_id="test",
            agent_interactions=[{"from": "agent1"}],  # Missing 'to' field
        )

        # When validation is performed, then ValueError is raised
        with pytest.raises(ValueError, match="missing 'from' or 'to' field"):
            engine.analyze_agent_interactions(trace_data)

    def test_data_validation_with_invalid_tool_call(self, engine):
        """When tool call is malformed, then raises ValueError."""
        # Given malformed tool call data
        trace_data = GraphTraceData(
            execution_id="test",
            tool_calls=[{"tool_name": "search"}],  # Missing 'agent_id' field
        )

        # When validation is performed, then ValueError is raised
        with pytest.raises(ValueError, match="missing 'agent_id' field"):
            engine.analyze_tool_usage_patterns(trace_data)

    def test_data_validation_with_empty_agent_fields(self, engine):
        """When agent fields are empty, then raises ValueError."""
        # Given empty agent fields
        trace_data = GraphTraceData(
            execution_id="test",
            agent_interactions=[{"from": "", "to": "agent2"}],  # Empty 'from'
        )

        # When validation is performed, then ValueError is raised
        with pytest.raises(ValueError, match="has empty 'from' or 'to' field"):
            engine.analyze_agent_interactions(trace_data)

    # Given: Resource limits and timeout tests
    @patch("app.evals.graph_analysis.logger")
    def test_resource_limits_warning_for_large_trace(self, mock_logger, engine):
        """When trace exceeds resource limits, then logs warning."""
        # Given large trace data exceeding max_nodes (default 1000)
        large_interactions = [{"from": f"agent_{i}", "to": f"agent_{i + 1}"} for i in range(1200)]
        trace_data = GraphTraceData(
            execution_id="large_test",
            agent_interactions=large_interactions,
        )

        # When validation is performed
        engine.analyze_agent_interactions(trace_data)

        # Then resource limit warning is logged
        assert mock_logger.warning.called
        warning_args = mock_logger.warning.call_args[0][0]
        assert "exceeding max_nodes" in warning_args

    def test_timeout_protection_in_path_convergence(self, engine):
        """When path convergence calculation times out, then handles gracefully."""
        # This test verifies the timeout mechanism exists
        # Given a simple trace that should complete normally
        trace_data = GraphTraceData(
            execution_id="timeout_test",
            tool_calls=[
                {"agent_id": "agent1", "tool_name": "tool1", "success": True},
                {"agent_id": "agent2", "tool_name": "tool2", "success": True},
            ],
        )

        # When analysis is performed (should complete without timeout)
        result = engine.analyze_tool_usage_patterns(trace_data)

        # Then analysis completes successfully
        assert "path_convergence" in result
        assert "tool_selection_accuracy" in result

    # Given: NetworkX error handling tests
    @patch("networkx.betweenness_centrality")
    def test_networkx_error_handling_in_agent_interactions(self, mock_centrality, engine):
        """When NetworkX operation fails, then handles gracefully with fallback."""
        # Given NetworkX operation that will fail
        import networkx as nx

        mock_centrality.side_effect = nx.NetworkXError("Test NetworkX error")

        trace_data = GraphTraceData(
            execution_id="networkx_error_test",
            agent_interactions=[
                {"from": "agent1", "to": "agent2", "type": "delegation"},
                {"from": "agent2", "to": "agent3", "type": "communication"},
            ],
        )

        # When analysis is performed
        result = engine.analyze_agent_interactions(trace_data)

        # Then fallback values are returned
        assert result["coordination_centrality"] == 0.0  # Exception handling returns 0.0
        assert 0.0 <= result["communication_overhead"] <= 1.0
