"""
Tests for graph vs text metric comparison logging.

Validates that after evaluation completes, the system logs a comparative
summary showing Tier 1 (text) vs Tier 3 (graph) scores with individual
metric breakdowns and composite score contribution.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.data_models.evaluation_models import CompositeResult, Tier1Result, Tier3Result
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.settings import JudgeSettings

# ---------------------------------------------------------------------------
# Shared fixture — extracted per AC4
# ---------------------------------------------------------------------------


@pytest.fixture
def pipeline_with_mocked_tiers():
    """Shared fixture: EvaluationPipeline with Tier1/Tier3 returns pre-configured.

    Provides a tuple of (pipeline, mock_t1, mock_t2, mock_t3, mock_composite)
    so each test only needs to set its unique assertion without repeating setup.
    """
    settings = JudgeSettings(enable_tier2=False)

    tier1_result = Tier1Result(
        cosine_score=0.75,
        jaccard_score=0.65,
        semantic_score=0.80,
        execution_time=1.5,
        time_score=0.9,
        task_success=1.0,
        overall_score=0.73,
    )
    tier3_result = Tier3Result(
        path_convergence=0.85,
        tool_selection_accuracy=0.90,
        coordination_centrality=0.88,
        task_distribution_balance=0.82,
        overall_score=0.83,
        graph_complexity=5,
    )
    composite_result = CompositeResult(
        composite_score=0.78,
        recommendation="accept",
        recommendation_weight=0.5,
        metric_scores={
            "cosine_score": 0.75,
            "semantic_score": 0.80,
            "path_convergence": 0.85,
            "tool_selection_accuracy": 0.90,
        },
        tier1_score=0.73,
        tier2_score=0.0,
        tier3_score=0.83,
        evaluation_complete=True,
        weights_used={
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167,
            "tool_efficiency": 0.167,
            "planning_rationality": 0.167,
            "output_similarity": 0.167,
        },
        tiers_enabled=[1, 3],
    )

    return (
        settings,
        tier1_result,
        tier3_result,
        composite_result,
    )


# ---------------------------------------------------------------------------
# Tests — each uses the shared fixture and contains only its unique assertion
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_metric_comparison_called_after_evaluation(
    pipeline_with_mocked_tiers,
):
    """Test that metric comparison logging is called after evaluate_comprehensive completes."""
    settings, tier1_result, tier3_result, composite_result = pipeline_with_mocked_tiers

    with patch("app.judge.evaluation_pipeline.logger") as mock_logger:
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Unique assertion: both Tier 1 and Tier 3 overall scores are logged
            tier1_logged = any(
                "Tier 1" in str(c[0][0]) and "overall score" in str(c[0][0])
                for c in mock_logger.info.call_args_list
            )
            tier3_logged = any(
                "Tier 3" in str(c[0][0]) and "overall score" in str(c[0][0])
                for c in mock_logger.info.call_args_list
            )
            assert tier1_logged, "Logger should log Tier 1 overall score"
            assert tier3_logged, "Logger should log Tier 3 overall score"


@pytest.mark.asyncio
async def test_individual_graph_metrics_displayed(pipeline_with_mocked_tiers):
    """Test that individual graph metrics are displayed in the comparison log."""
    settings, tier1_result, tier3_result, composite_result = pipeline_with_mocked_tiers
    # Empty metric_scores to test graph-metric log path separately
    composite_result = composite_result.model_copy(update={"metric_scores": {}})

    with patch("app.judge.evaluation_pipeline.logger") as mock_logger:
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Unique assertion: individual graph metric names appear in log output
            logged_messages = " ".join(str(call[0][0]) for call in mock_logger.info.call_args_list)
            assert "path_convergence" in logged_messages
            assert "tool_selection_accuracy" in logged_messages
            assert "coordination_centrality" in logged_messages
            assert "task_distribution_balance" in logged_messages


@pytest.mark.asyncio
async def test_individual_text_metrics_displayed(pipeline_with_mocked_tiers):
    """Test that individual text metrics are displayed in the comparison log."""
    settings, tier1_result, tier3_result, composite_result = pipeline_with_mocked_tiers
    composite_result = composite_result.model_copy(update={"metric_scores": {}})

    with patch("app.judge.evaluation_pipeline.logger") as mock_logger:
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Unique assertion: individual text metric names appear in log output
            logged_messages = " ".join(str(call[0][0]) for call in mock_logger.info.call_args_list)
            assert "cosine_score" in logged_messages
            assert "jaccard_score" in logged_messages
            assert "semantic_score" in logged_messages


@pytest.mark.asyncio
async def test_composite_score_tier_contribution_displayed(pipeline_with_mocked_tiers):
    """Test that composite score shows per-tier contribution."""
    settings, tier1_result, tier3_result, composite_result = pipeline_with_mocked_tiers
    composite_result = composite_result.model_copy(update={"metric_scores": {}})

    with patch("app.judge.evaluation_pipeline.logger") as mock_logger:
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Unique assertion: tier 1 and tier 3 contributions appear in log output
            logged_messages = " ".join(str(call[0][0]) for call in mock_logger.info.call_args_list)
            assert "tier1" in logged_messages.lower() or "Tier 1" in logged_messages
            assert "tier3" in logged_messages.lower() or "Tier 3" in logged_messages
