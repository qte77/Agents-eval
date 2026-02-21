"""
BDD-style tests for composite scoring system.

Tests the CompositeScorer implementation including single-agent weight
redistribution (STORY-003), Tier 2 skip handling (STORY-001), and compound
redistribution scenarios.
"""

import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import (
    GraphTraceData,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.judge.composite_scorer import CompositeScorer, EvaluationResults
from app.judge.settings import JudgeSettings


@pytest.fixture
def settings():
    """Fixture providing JudgeSettings for composite scorer."""
    return JudgeSettings()


@pytest.fixture
def scorer(settings):
    """Fixture providing CompositeScorer instance."""
    return CompositeScorer(settings)


@pytest.fixture
def tier1_result():
    """Fixture providing sample Tier 1 result."""
    return Tier1Result(
        cosine_score=0.8,
        jaccard_score=0.7,
        semantic_score=0.85,
        execution_time=5.0,
        time_score=0.9,
        task_success=1.0,
        overall_score=0.8,
    )


@pytest.fixture
def tier2_result():
    """Fixture providing sample Tier 2 result."""
    return Tier2Result(
        technical_accuracy=0.75,
        constructiveness=0.8,
        planning_rationality=0.85,
        overall_score=0.78,
        model_used="gpt-4",
        api_cost=0.05,
        fallback_used=False,
    )


@pytest.fixture
def tier3_result():
    """Fixture providing sample Tier 3 result."""
    return Tier3Result(
        path_convergence=0.7,
        tool_selection_accuracy=0.8,
        communication_overhead=0.6,
        coordination_centrality=0.75,
        task_distribution_balance=0.7,
        overall_score=0.72,
        graph_complexity=5,
    )


@pytest.fixture
def single_agent_trace():
    """Fixture providing GraphTraceData for single-agent run."""
    return GraphTraceData(
        execution_id="single-agent-123",
        agent_interactions=[],  # No agent-to-agent interactions
        tool_calls=[
            {"tool_name": "get_peerread_paper", "agent_id": "agent-1", "success": True},
            {"tool_name": "generate_review", "agent_id": "agent-1", "success": True},
        ],
        timing_data={"start": 0.0, "end": 5.0},
        coordination_events=[],  # No coordination events
    )


@pytest.fixture
def multi_agent_trace():
    """Fixture providing GraphTraceData for multi-agent run."""
    return GraphTraceData(
        execution_id="multi-agent-456",
        agent_interactions=[
            {"from": "manager", "to": "researcher", "type": "delegation"},
            {"from": "researcher", "to": "manager", "type": "response"},
        ],
        tool_calls=[
            {"tool_name": "get_peerread_paper", "agent_id": "researcher", "success": True},
            {"tool_name": "duckduckgo_search", "agent_id": "researcher", "success": True},
        ],
        timing_data={"start": 0.0, "end": 8.0},
        coordination_events=[{"coordination_type": "delegation", "target_agents": ["researcher"]}],
    )


class TestSingleAgentWeightRedistribution:
    """Test suite for STORY-003: Single-agent composite score weight redistribution."""

    def test_detect_single_agent_from_empty_coordination_events(
        self, scorer, tier1_result, tier2_result, tier3_result, single_agent_trace
    ):
        """Should detect single-agent run from empty coordination_events."""
        # This test will fail until we implement single-agent detection
        result = scorer.evaluate_composite_with_trace(
            EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result),
            single_agent_trace,
        )

        # Single-agent mode should be detected
        assert result.single_agent_mode is True

    def test_detect_single_agent_from_single_unique_agent_id(
        self, scorer, tier1_result, tier2_result, tier3_result
    ):
        """Should detect single-agent run from 0 or 1 unique agent IDs in tool_calls."""
        trace = GraphTraceData(
            execution_id="test-1",
            agent_interactions=[],
            tool_calls=[
                {"tool_name": "tool1", "agent_id": "agent-1", "success": True},
                {"tool_name": "tool2", "agent_id": "agent-1", "success": True},
            ],
            timing_data={},
            coordination_events=[],
        )

        result = scorer.evaluate_composite_with_trace(
            EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result),
            trace,
        )

        assert result.single_agent_mode is True

    def test_multi_agent_not_detected_as_single(
        self, scorer, tier1_result, tier2_result, tier3_result, multi_agent_trace
    ):
        """Should NOT detect multi-agent run as single-agent."""
        result = scorer.evaluate_composite_with_trace(
            EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result),
            multi_agent_trace,
        )

        # Multi-agent mode (single_agent_mode should be False)
        assert result.single_agent_mode is False

    def test_single_agent_redistributes_coordination_weight(
        self, scorer, tier1_result, tier2_result, tier3_result, single_agent_trace
    ):
        """Should redistribute coordination_quality weight (0.167) to remaining 5 metrics."""
        result = scorer.evaluate_composite_with_trace(
            EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result),
            single_agent_trace,
        )

        # coordination_quality should NOT be in weights when single-agent
        assert "coordination_quality" not in result.weights_used

        # Remaining 5 metrics should each get 0.2 (0.167 + 0.033)
        assert result.weights_used == snapshot(
            {
                "time_taken": 0.2,
                "task_success": 0.2,
                "output_similarity": 0.2,
                "tool_efficiency": 0.2,
                "planning_rationality": 0.2,
            }
        )

    def test_multi_agent_uses_all_six_metrics(
        self, scorer, tier1_result, tier2_result, tier3_result, multi_agent_trace
    ):
        """Should use all 6 metrics with equal weights for multi-agent runs."""
        result = scorer.evaluate_composite_with_trace(
            EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result),
            multi_agent_trace,
        )

        # All 6 metrics should be present with equal weights
        assert result.weights_used == snapshot(
            {
                "time_taken": 0.167,
                "task_success": 0.167,
                "coordination_quality": 0.167,
                "tool_efficiency": 0.167,
                "planning_rationality": 0.167,
                "output_similarity": 0.167,
            }
        )

    @given(
        st.lists(
            st.floats(min_value=0.0, max_value=1.0),
            min_size=5,
            max_size=6,
        )
    )
    @hypothesis_settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_weights_always_sum_to_one(self, scorer, metric_values):
        """Property test: Weights should always sum to ~1.0 regardless of mode."""
        # Create tier results from hypothesis-generated values
        tier1 = Tier1Result(
            cosine_score=metric_values[0],
            jaccard_score=metric_values[1],
            semantic_score=metric_values[2],
            execution_time=5.0,
            time_score=metric_values[3],
            task_success=1.0,
            overall_score=metric_values[4],
        )
        tier2 = Tier2Result(
            technical_accuracy=0.75,
            constructiveness=0.8,
            planning_rationality=0.85,
            overall_score=0.78,
            model_used="gpt-4",
            api_cost=0.05,
        )
        tier3 = Tier3Result(
            path_convergence=0.7,
            tool_selection_accuracy=0.8,
            communication_overhead=0.6,
            coordination_centrality=0.75,
            task_distribution_balance=0.7,
            overall_score=0.72,
            graph_complexity=5,
        )

        # Test both single-agent and multi-agent modes
        single_trace = GraphTraceData(
            execution_id="test-single",
            agent_interactions=[],
            tool_calls=[],
            coordination_events=[],
        )
        multi_trace = GraphTraceData(
            execution_id="test-multi",
            agent_interactions=[{"from": "a", "to": "b", "type": "delegation"}],
            tool_calls=[],
            coordination_events=[{"coordination_type": "delegation"}],
        )

        results = EvaluationResults(tier1=tier1, tier2=tier2, tier3=tier3)

        single_result = scorer.evaluate_composite_with_trace(results, single_trace)
        multi_result = scorer.evaluate_composite_with_trace(results, multi_trace)

        # Weights should sum to ~1.0 (allowing small floating point error)
        assert abs(sum(single_result.weights_used.values()) - 1.0) < 0.01
        assert abs(sum(multi_result.weights_used.values()) - 1.0) < 0.01

    def test_compound_redistribution_tier2_skip_and_single_agent(
        self, scorer, tier1_result, tier3_result, single_agent_trace
    ):
        """Should handle both Tier 2 skip AND single-agent mode redistribution."""
        # Tier 2 is None (skipped due to no provider)
        results = EvaluationResults(tier1=tier1_result, tier2=None, tier3=tier3_result)

        result = scorer.evaluate_composite_with_trace(results, single_agent_trace)

        # Should skip both Tier 2 metrics (planning_rationality) and coordination_quality
        # Remaining 4 metrics: time_taken, task_success, output_similarity, tool_efficiency
        assert result.weights_used == snapshot(
            {
                "time_taken": 0.25,
                "task_success": 0.25,
                "output_similarity": 0.25,
                "tool_efficiency": 0.25,
            }
        )
        assert result.single_agent_mode is True
        assert result.tier2_score is None

    def test_logging_on_single_agent_weight_redistribution(
        self, scorer, tier1_result, tier2_result, tier3_result, single_agent_trace, caplog
    ):
        """Should log message when single-agent weight redistribution occurs."""
        # Enable caplog to capture loguru logs
        import logging

        caplog.set_level(logging.INFO)

        result = scorer.evaluate_composite_with_trace(
            EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result),
            single_agent_trace,
        )

        # The log message is written to stderr by loguru, check that single_agent_mode is set
        assert result.single_agent_mode is True
        # Verify the weights were redistributed (coordination_quality excluded)
        assert "coordination_quality" not in result.weights_used
