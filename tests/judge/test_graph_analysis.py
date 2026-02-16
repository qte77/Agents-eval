"""Tests for graph-based analysis engine (Tier 3 evaluation).

This module tests the GraphAnalysisEngine implementation, focusing on:
- Tool success_rate accumulation across repeated calls
- Agent-tool edge weight accumulation
- Proper exclusion of dead metrics from scoring
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import GraphTraceData, Tier3Result
from app.judge.graph_analysis import GraphAnalysisEngine
from app.judge.settings import JudgeSettings


class TestToolSuccessRateAccumulation:
    """Tests for tool success_rate accumulation across repeated calls.

    Issue: add_node at line 171 overwrites success_rate each time a tool
    is called, so only the last call outcome survives.

    Expected: success_rate should accumulate across all calls.
    Example: If a tool succeeds 9 times and fails once (last),
    success_rate should be 0.9, not 0.0.
    """

    def test_tool_called_multiple_times_accumulates_success_rate(self) -> None:
        """Test that tool success_rate accumulates across repeated calls."""
        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        # Tool "search_tool" called 10 times: 9 successes, 1 failure
        tool_calls = [
            {"agent_id": "agent1", "tool_name": "search_tool", "success": True}
            for _ in range(9)
        ] + [
            {"agent_id": "agent1", "tool_name": "search_tool", "success": False}
        ]

        trace_data = GraphTraceData(
            execution_id="test_exec_1",
            tool_calls=tool_calls,
            agent_interactions=[],
            coordination_events=[],
            timing_data={},
        )

        # Act
        metrics = engine.analyze_tool_usage_patterns(trace_data)

        # Assert
        # Expected: 9 successes / 10 total = 0.9
        # Actual (bug): only last call (failure) survives = 0.0
        assert metrics["tool_selection_accuracy"] == snapshot(0.9)

    def test_multiple_tools_with_different_success_rates(self) -> None:
        """Test multiple tools each with their own success rates."""
        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        # Tool A: 3/3 success = 1.0
        # Tool B: 2/4 success = 0.5
        # Expected average: (1.0 + 0.5) / 2 = 0.75
        tool_calls = [
            {"agent_id": "agent1", "tool_name": "tool_a", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_a", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_a", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_b", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_b", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_b", "success": False},
            {"agent_id": "agent1", "tool_name": "tool_b", "success": False},
        ]

        trace_data = GraphTraceData(
            execution_id="test_exec_2",
            tool_calls=tool_calls,
            agent_interactions=[],
            coordination_events=[],
            timing_data={},
        )

        # Act
        metrics = engine.analyze_tool_usage_patterns(trace_data)

        # Assert
        assert metrics["tool_selection_accuracy"] == snapshot(0.75)

    @given(
        num_successes=st.integers(min_value=0, max_value=20),
        num_failures=st.integers(min_value=0, max_value=20),
    )
    def test_tool_success_rate_property_bounded(
        self, num_successes: int, num_failures: int
    ) -> None:
        """Property test: tool success_rate is always in [0.0, 1.0]."""
        # Skip case with no tool calls
        if num_successes + num_failures == 0:
            return

        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        tool_calls = [
            {"agent_id": "agent1", "tool_name": "tool", "success": True}
            for _ in range(num_successes)
        ] + [
            {"agent_id": "agent1", "tool_name": "tool", "success": False}
            for _ in range(num_failures)
        ]

        trace_data = GraphTraceData(
            execution_id="test_exec_prop",
            tool_calls=tool_calls,
            agent_interactions=[],
            coordination_events=[],
            timing_data={},
        )

        # Act
        metrics = engine.analyze_tool_usage_patterns(trace_data)

        # Assert
        accuracy = metrics["tool_selection_accuracy"]
        assert 0.0 <= accuracy <= 1.0

        # Additional check: accuracy should match expected rate
        expected_rate = num_successes / (num_successes + num_failures)
        assert abs(accuracy - expected_rate) < 0.01


class TestAgentToolEdgeWeightAccumulation:
    """Tests for agent-tool edge weight accumulation.

    Issue: add_edge at line 173 overwrites weight each time.
    Expected: edge weight should accumulate or average across calls.
    """

    def test_agent_tool_edge_weight_accumulates(self) -> None:
        """Test that agent-tool edge weights accumulate across repeated calls."""
        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        # Same agent calling same tool multiple times
        tool_calls = [
            {"agent_id": "agent1", "tool_name": "tool_x", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_x", "success": True},
            {"agent_id": "agent1", "tool_name": "tool_x", "success": False},
        ]

        trace_data = GraphTraceData(
            execution_id="test_exec_3",
            tool_calls=tool_calls,
            agent_interactions=[],
            coordination_events=[],
            timing_data={},
        )

        # Act
        metrics = engine.analyze_tool_usage_patterns(trace_data)

        # Assert
        # With proper accumulation, we expect the tool success rate to be 2/3
        # (not just the last call's weight of 0.5 for failure)
        accuracy = metrics["tool_selection_accuracy"]
        expected = 2.0 / 3.0
        assert abs(accuracy - expected) < 0.01


class TestCommunicationOverheadMetric:
    """Tests for communication_overhead metric exclusion from scoring.

    Issue: communication_overhead is computed and stored in Tier3Result
    but never included in overall_score (lines 392-397), making it a
    dead metric that inflates the model without contributing to scoring.

    Expected: Either include it in scoring OR remove from Tier3Result.
    Decision: Remove from Tier3Result to avoid confusion.
    """

    def test_tier3_result_excludes_communication_overhead(self) -> None:
        """Test that Tier3Result does not include communication_overhead field."""
        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        trace_data = GraphTraceData(
            execution_id="test_exec_4",
            tool_calls=[
                {"agent_id": "agent1", "tool_name": "tool1", "success": True}
            ],
            agent_interactions=[
                {"from": "agent1", "to": "agent2", "type": "delegation"}
            ],
            coordination_events=[],
            timing_data={},
        )

        # Act
        result = engine.evaluate_graph_metrics(trace_data)

        # Assert
        # Tier3Result should NOT have communication_overhead field
        assert not hasattr(result, "communication_overhead")

    def test_overall_score_excludes_communication_overhead_weight(self) -> None:
        """Test that overall_score calculation does not use communication_overhead."""
        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        trace_data = GraphTraceData(
            execution_id="test_exec_5",
            tool_calls=[
                {"agent_id": "agent1", "tool_name": "tool1", "success": True}
            ],
            agent_interactions=[
                {"from": "agent1", "to": "agent2", "type": "delegation"}
            ],
            coordination_events=[],
            timing_data={},
        )

        # Act
        result = engine.evaluate_graph_metrics(trace_data)

        # Assert
        # overall_score should be computed from 4 metrics only:
        # path_convergence (0.3) + tool_accuracy (0.25) +
        # coordination_quality (0.25) + task_balance (0.2)
        # Weights should sum to 1.0
        weights = engine.weights
        assert sum(weights.values()) == snapshot(1.0)
        assert "communication_overhead" not in weights


class TestTier3WeightsSum:
    """Property tests for Tier 3 weight invariants."""

    def test_weights_sum_to_one(self) -> None:
        """Test that scoring weights always sum to 1.0."""
        # Arrange
        settings = JudgeSettings()
        engine = GraphAnalysisEngine(settings)

        # Assert
        weights = engine.weights
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 1e-6
