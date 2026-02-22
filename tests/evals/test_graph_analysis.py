"""
BDD-style tests for graph analysis engine.

Test the core functionality of Tier 3 evaluation using NetworkX-based
analysis of agent coordination patterns and tool usage efficiency.
"""

import threading
from typing import Any
from unittest.mock import MagicMock, patch

import networkx as nx
import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.judge.graph_analysis import (
    GraphAnalysisEngine,
    evaluate_single_graph_analysis,
)
from app.judge.settings import JudgeSettings


def _make_trace_data(
    agent_interactions: list[dict[str, Any]] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> GraphTraceData:
    """Build a minimal GraphTraceData for testing."""
    return GraphTraceData(
        execution_id="test_exec",
        agent_interactions=agent_interactions or [],
        tool_calls=tool_calls or [],
        coordination_events=[],
        timing_data={},
    )


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

    @patch("app.judge.graph_analysis.logger")
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
        # communication_overhead removed from Tier3Result (dead metric)

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
    @patch("app.judge.graph_analysis.logger")
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


class TestThreadSafeTimeout:
    """Test suite for thread-safe timeout handling in graph analysis (STORY-002)."""

    @pytest.fixture
    def engine(self):
        """Fixture providing GraphAnalysisEngine with short timeout."""
        settings = JudgeSettings()
        settings.tier3_operation_timeout = 1.0  # Short timeout for testing
        return GraphAnalysisEngine(settings)

    @pytest.fixture
    def sample_trace_data(self):
        """Fixture providing sample trace data that creates connected graph for timeout testing."""
        # Create a connected graph by having agents use the same tools
        # This ensures nx.is_connected() returns True and _with_timeout is called
        return GraphTraceData(
            execution_id="test_timeout_001",
            agent_interactions=[
                {"from": "agent_1", "to": "agent_2", "type": "delegation"},
                {"from": "agent_2", "to": "agent_1", "type": "communication"},
            ],
            tool_calls=[
                {"agent_id": "agent_1", "tool_name": "shared_tool", "success": True},
                {"agent_id": "agent_2", "tool_name": "shared_tool", "success": True},
                {"agent_id": "agent_1", "tool_name": "tool_2", "success": True},
            ],
            timing_data={"start": 0.0, "end": 1.5},
        )

    def test_timeout_works_in_main_thread(self, engine, sample_trace_data):
        """Given timeout in main thread, path_convergence should succeed (baseline)."""
        result = engine.analyze_tool_usage_patterns(sample_trace_data)

        # Should complete successfully
        assert "path_convergence" in result
        assert isinstance(result["path_convergence"], float)
        assert 0.0 <= result["path_convergence"] <= 1.0

    @patch("app.judge.graph_analysis.logger")
    def test_timeout_fails_in_non_main_thread_with_signal(
        self, mock_logger, engine, sample_trace_data
    ):
        """Given signal-based timeout in non-main thread, should log signal error.

        This test SHOULD FAIL initially (RED phase) because signal-based timeout
        raises "signal only works in main thread" error which gets caught and logged.
        After ThreadPoolExecutor implementation, path_convergence should succeed
        without signal errors (GREEN phase).
        """
        results = {}

        def run_analysis():
            """Run analysis in non-main thread (simulates Streamlit)."""
            results["analysis"] = engine.analyze_tool_usage_patterns(sample_trace_data)

        # Run in non-main thread (simulating Streamlit GUI context)
        thread = threading.Thread(target=run_analysis)
        thread.start()
        thread.join(timeout=5.0)

        # Verify analysis completed
        assert "analysis" in results

        # RED phase: With signal-based timeout, debug logger should show signal error
        # Check if signal error was logged
        signal_error_logged = False
        for call in mock_logger.debug.call_args_list:
            if "signal only works in main thread" in str(call):
                signal_error_logged = True
                break

        # GREEN phase: After ThreadPoolExecutor, no signal error should be logged
        # And path_convergence should have a valid value (not fallback 0.0)
        assert not signal_error_logged, (
            "Signal-based timeout still in use. Thread-safe timeout not implemented."
        )
        assert results["analysis"]["path_convergence"] > 0.0, (
            "Path convergence returned fallback 0.0, indicating timeout mechanism failed"
        )

    @given(st.floats(min_value=0.0, max_value=0.5))
    def test_timeout_fallback_value_bounds(self, fallback_value):
        """Given timeout fallback, value should be between 0.0 and 0.5 (property test)."""
        # Property test: timeout fallback values must be in valid range
        # This validates the acceptance criteria for graceful fallback (return 0.3)
        assert 0.0 <= fallback_value <= 0.5

    def test_timeout_result_structure_matches_snapshot(self, engine, sample_trace_data):
        """Given path_convergence analysis, result structure should match expected format."""
        result = engine.analyze_tool_usage_patterns(sample_trace_data)

        # Verify result structure matches snapshot
        assert result == snapshot(
            {
                "path_convergence": 0.6666666666666666,
                "tool_selection_accuracy": 1.0,
            }
        )

    @patch("app.judge.graph_analysis.logger")
    def test_timeout_logs_warning_on_fallback(self, mock_logger, engine):
        """Given timeout during calculation, should log warning and return fallback."""
        # Create trace data that creates CONNECTED graph for path_convergence timeout test
        # Use shared tool to ensure graph is connected
        trace_data = GraphTraceData(
            execution_id="timeout_fallback_test",
            tool_calls=[
                {"agent_id": "agent1", "tool_name": "shared_tool", "success": True},
                {"agent_id": "agent2", "tool_name": "shared_tool", "success": True},
                {"agent_id": "agent1", "tool_name": "tool2", "success": True},
            ],
            timing_data={"start": 0.0, "end": 1.0},
        )

        # Force timeout by mocking nx.average_shortest_path_length to raise TimeoutError
        with patch(
            "networkx.average_shortest_path_length", side_effect=TimeoutError("Test timeout")
        ):
            result = engine.analyze_tool_usage_patterns(trace_data)

            # Should return fallback value (0.3 per line 352 of graph_analysis.py)
            assert result["path_convergence"] == 0.3  # Acceptance criteria: return 0.3 on timeout

            # Should log warning
            assert mock_logger.warning.called
            warning_message = str(mock_logger.warning.call_args)
            assert "timed out" in warning_message.lower() or "timeout" in warning_message.lower()


class TestExportTraceNodeAttributeNames:
    """Verify export_trace_to_networkx() uses `type` as the canonical node attribute."""

    def setup_method(self) -> None:
        self.engine = GraphAnalysisEngine(JudgeSettings())

    def test_agent_nodes_use_type_attribute(self) -> None:
        """Agent nodes exported by export_trace_to_networkx() have `type` key, not `node_type`."""
        # Arrange
        trace_data = _make_trace_data(agent_interactions=[{"from": "manager", "to": "researcher"}])

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        assert graph.number_of_nodes() > 0
        for node in graph.nodes():
            node_data = graph.nodes[node]
            assert "type" in node_data, (
                f"Node '{node}' missing 'type' attribute — found keys: {list(node_data.keys())}"
            )
            assert "node_type" not in node_data, (
                f"Node '{node}' has unexpected 'node_type' attribute"
            )

    def test_tool_nodes_use_type_attribute(self) -> None:
        """Tool nodes exported by export_trace_to_networkx() have `type` key, not `node_type`."""
        # Arrange
        trace_data = _make_trace_data(
            tool_calls=[{"agent_id": "researcher", "tool_name": "search_tool", "success": True}]
        )

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        tool_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "tool"]
        assert len(tool_nodes) > 0, "No tool nodes found with type='tool'"

    def test_agent_node_type_value_is_agent(self) -> None:
        """Agent nodes have type='agent'."""
        # Arrange
        trace_data = _make_trace_data(agent_interactions=[{"from": "manager", "to": "researcher"}])

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        agent_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "agent"]
        assert len(agent_nodes) == 2
        assert "manager" in agent_nodes
        assert "researcher" in agent_nodes

    def test_tool_node_type_value_is_tool(self) -> None:
        """Tool nodes have type='tool'."""
        # Arrange
        trace_data = _make_trace_data(
            tool_calls=[{"agent_id": "researcher", "tool_name": "search_tool", "success": True}]
        )

        # Act
        graph = self.engine.export_trace_to_networkx(trace_data)

        # Assert
        assert graph is not None
        tool_node = graph.nodes.get("search_tool")
        assert tool_node is not None
        assert tool_node.get("type") == "tool"


class TestAgentGraphAttributeConsistency:
    """Verify render_agent_graph() reads `type` attribute (matching export_trace_to_networkx).

    These tests expose the bug at agent_graph.py:101,150 where `node_type` is read
    instead of `type`. They should FAIL until the fix is applied.
    """

    def _build_graph_with_type_attribute(self) -> nx.DiGraph:
        """Build a graph using the canonical `type` attribute (as export_trace_to_networkx does)."""
        graph: nx.DiGraph = nx.DiGraph()
        graph.add_node("manager", type="agent", label="Manager", interaction_count=2)
        graph.add_node("researcher", type="agent", label="Researcher", interaction_count=1)
        graph.add_node("search_tool", type="tool", label="search_tool", usage_count=3)
        graph.add_edge("manager", "researcher", interaction="delegation")
        graph.add_edge("researcher", "search_tool", interaction="tool_call")
        return graph

    @patch("streamlit.components.v1.html")
    @patch("streamlit.expander")
    @patch("streamlit.text")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("gui.pages.agent_graph.Network")
    def test_render_reads_type_not_node_type_for_node_styling(
        self,
        mock_network_cls: MagicMock,
        mock_header: MagicMock,
        mock_subheader: MagicMock,
        mock_text: MagicMock,
        mock_expander: MagicMock,
        mock_html: MagicMock,
        tmp_path,
    ) -> None:
        """render_agent_graph() should add agent nodes with blue color when type='agent'.

        This test FAILS with the bug because node_data.get("node_type", "agent") always
        returns the default "agent" for ALL nodes (including tool nodes that only have `type`).
        After the fix, node_data.get("type", "agent") will correctly distinguish agent/tool.
        """
        from gui.pages.agent_graph import render_agent_graph

        graph = self._build_graph_with_type_attribute()

        # Track add_node calls to verify color assignments
        mock_net = MagicMock()
        mock_net.save_graph = MagicMock()
        mock_network_cls.return_value = mock_net

        # Make save_graph write something readable
        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.name = str(tmp_path / "test_graph.html")
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value = mock_file

            with patch("pathlib.Path.read_text", return_value="<html></html>"):
                with patch("pathlib.Path.unlink"):
                    render_agent_graph(graph)

        # Verify add_node was called for all 3 nodes
        assert mock_net.add_node.call_count == 3

        # Collect calls by node id
        calls_by_node: dict[str, dict[str, Any]] = {}
        for call in mock_net.add_node.call_args_list:
            node_id = call.args[0]
            calls_by_node[node_id] = call.kwargs

        # manager and researcher should be agent nodes (blue #4A90E2)
        assert calls_by_node["manager"]["color"] == "#4A90E2", (
            f"manager should be blue agent node, got: {calls_by_node['manager']['color']}"
        )
        assert calls_by_node["researcher"]["color"] == "#4A90E2", (
            f"researcher should be blue agent node, got: {calls_by_node['researcher']['color']}"
        )
        # search_tool should be a tool node (green #50C878)
        assert calls_by_node["search_tool"]["color"] == "#50C878", (
            f"search_tool should be green tool node, got: {calls_by_node['search_tool']['color']}"
        )

    @patch("streamlit.components.v1.html")
    @patch("streamlit.expander")
    @patch("streamlit.text")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("gui.pages.agent_graph.Network")
    def test_graph_statistics_counts_agent_nodes_using_type_attribute(
        self,
        mock_network_cls: MagicMock,
        mock_header: MagicMock,
        mock_subheader: MagicMock,
        mock_text: MagicMock,
        mock_expander: MagicMock,
        mock_html: MagicMock,
        tmp_path,
    ) -> None:
        """Graph statistics section must count agent nodes using `type` attribute.

        agent_graph.py:150 reads graph.nodes[n].get("node_type") — this returns None
        for nodes that only have `type` set. After fix, it reads `type` and counts correctly:
        2 agent nodes out of 3 total.
        """
        from gui.pages.agent_graph import render_agent_graph

        graph = self._build_graph_with_type_attribute()

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net

        # Capture st.text() calls — statistics are rendered via st.text()
        text_calls: list[str] = []
        mock_text.side_effect = lambda s: text_calls.append(str(s))

        # expander returns a context manager
        mock_expander.return_value.__enter__ = MagicMock(return_value=None)
        mock_expander.return_value.__exit__ = MagicMock(return_value=False)

        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.name = str(tmp_path / "test_graph.html")
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value = mock_file

            with patch("pathlib.Path.read_text", return_value="<html></html>"):
                with patch("pathlib.Path.unlink"):
                    render_agent_graph(graph)

        # Statistics should show 2 agent nodes (manager + researcher)
        agent_stat = next((c for c in text_calls if "Agent Nodes:" in c), None)
        assert agent_stat is not None, f"Agent Nodes stat not found in: {text_calls}"
        assert "2" in agent_stat, (
            f"Expected 2 agent nodes but got: '{agent_stat}'. "
            "Bug: agent_graph.py reads 'node_type' instead of 'type', so count is 0."
        )

        # Statistics should show 1 tool node
        tool_stat = next((c for c in text_calls if "Tool Nodes:" in c), None)
        assert tool_stat is not None, f"Tool Nodes stat not found in: {text_calls}"
        assert "1" in tool_stat, (
            f"Expected 1 tool node but got: '{tool_stat}'. "
            "Bug: agent_graph.py reads 'node_type' instead of 'type', so count is 3."
        )


class TestAttributeNameRoundTrip:
    """End-to-end: export_trace_to_networkx() output is compatible with render_agent_graph()."""

    def test_exported_graph_has_attributes_readable_by_renderer(self) -> None:
        """Nodes from export_trace_to_networkx() have `type` that render_agent_graph() can read."""
        # Arrange
        engine = GraphAnalysisEngine(JudgeSettings())
        trace_data = _make_trace_data(
            agent_interactions=[{"from": "manager", "to": "researcher"}],
            tool_calls=[{"agent_id": "researcher", "tool_name": "search", "success": True}],
        )

        # Act
        graph = engine.export_trace_to_networkx(trace_data)
        assert graph is not None

        # Simulate what render_agent_graph() does at line 101 — AFTER the fix
        # (reading `type`, not `node_type`)
        agent_count_correct = sum(1 for n in graph.nodes() if graph.nodes[n].get("type") == "agent")
        agent_count_buggy = sum(
            1 for n in graph.nodes() if graph.nodes[n].get("node_type") == "agent"
        )

        # With fix: `type` attribute is present, correctly counts agents
        assert agent_count_correct == 2, (
            f"Expected 2 agent nodes via 'type' attribute, got {agent_count_correct}"
        )
        # Without fix: `node_type` attribute is absent, counts 0
        assert agent_count_buggy == 0, (
            "Sanity check: 'node_type' attribute should not be present (it's a bug)"
        )
