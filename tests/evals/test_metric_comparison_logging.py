"""
Tests for graph vs text metric comparison logging.

Validates that after evaluation completes, the system logs a comparative
summary showing Tier 1 (text) vs Tier 3 (graph) scores with individual
metric breakdowns and composite score contribution.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.data_models.evaluation_models import CompositeResult, Tier1Result, Tier3Result


@pytest.mark.asyncio
async def test_log_metric_comparison_called_after_evaluation():
    """Test that metric comparison logging is called after evaluate_comprehensive completes."""
    from app.judge.evaluation_pipeline import EvaluationPipeline
    from app.judge.settings import JudgeSettings

    # Create pipeline with mocked engines
    settings = JudgeSettings(enable_tier2=False)  # Disable tier2 for focused test

    with (
        patch("app.judge.evaluation_pipeline.logger") as mock_logger,
    ):
        pipeline = EvaluationPipeline(settings=settings)

        # Mock tier results
        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
            # Setup mock returns
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

            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)

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
            mock_composite.return_value = composite_result

            # Execute evaluation
            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Verify logger.info was called with metric comparison
            # Check for tier score comparison (they are in separate log calls)
            tier1_logged = False
            tier3_logged = False
            for call in mock_logger.info.call_args_list:
                call_msg = str(call[0][0])
                if "Tier 1" in call_msg and "overall score" in call_msg:
                    tier1_logged = True
                if "Tier 3" in call_msg and "overall score" in call_msg:
                    tier3_logged = True

            assert tier1_logged, "Logger should log Tier 1 overall score"
            assert tier3_logged, "Logger should log Tier 3 overall score"


@pytest.mark.asyncio
async def test_individual_graph_metrics_displayed():
    """Test that individual graph metrics are displayed in the comparison log."""
    with (
        patch("app.judge.evaluation_pipeline.logger") as mock_logger,
    ):
        from app.judge.evaluation_pipeline import EvaluationPipeline
        from app.judge.settings import JudgeSettings

        settings = JudgeSettings(enable_tier2=False)
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
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

            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)

            composite_result = CompositeResult(
                composite_score=0.78,
                recommendation="accept",
                recommendation_weight=0.5,
                metric_scores={},
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
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Verify individual graph metrics are logged
            logged_messages = " ".join(
                [str(call[0][0]) for call in mock_logger.info.call_args_list]
            )

            assert "path_convergence" in logged_messages, (
                "Graph metric path_convergence should be logged"
            )
            assert "tool_selection_accuracy" in logged_messages, (
                "Graph metric tool_selection_accuracy should be logged"
            )
            # communication_overhead removed in STORY-013 (dead metric)
            assert "coordination_centrality" in logged_messages, (
                "Graph metric coordination_centrality should be logged"
            )
            assert "task_distribution_balance" in logged_messages, (
                "Graph metric task_distribution_balance should be logged"
            )


@pytest.mark.asyncio
async def test_individual_text_metrics_displayed():
    """Test that individual text metrics are displayed in the comparison log."""
    with (
        patch("app.judge.evaluation_pipeline.logger") as mock_logger,
    ):
        from app.judge.evaluation_pipeline import EvaluationPipeline
        from app.judge.settings import JudgeSettings

        settings = JudgeSettings(enable_tier2=False)
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
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

            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)

            composite_result = CompositeResult(
                composite_score=0.78,
                recommendation="accept",
                recommendation_weight=0.5,
                metric_scores={},
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
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Verify individual text metrics are logged
            logged_messages = " ".join(
                [str(call[0][0]) for call in mock_logger.info.call_args_list]
            )

            assert "cosine_score" in logged_messages, "Text metric cosine_score should be logged"
            assert "jaccard_score" in logged_messages, "Text metric jaccard_score should be logged"
            assert "semantic_score" in logged_messages, (
                "Text metric semantic_score should be logged"
            )


@pytest.mark.asyncio
async def test_composite_score_tier_contribution_displayed():
    """Test that composite score shows per-tier contribution."""
    with (
        patch("app.judge.evaluation_pipeline.logger") as mock_logger,
    ):
        from app.judge.evaluation_pipeline import EvaluationPipeline
        from app.judge.settings import JudgeSettings

        settings = JudgeSettings(enable_tier2=False)
        pipeline = EvaluationPipeline(settings=settings)

        with (
            patch.object(pipeline, "_execute_tier1", new_callable=AsyncMock) as mock_t1,
            patch.object(pipeline, "_execute_tier2", new_callable=AsyncMock) as mock_t2,
            patch.object(pipeline, "_execute_tier3", new_callable=AsyncMock) as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_composite,
        ):
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

            mock_t1.return_value = (tier1_result, 0.5)
            mock_t2.return_value = (None, 0.0)
            mock_t3.return_value = (tier3_result, 0.3)

            composite_result = CompositeResult(
                composite_score=0.78,
                recommendation="accept",
                recommendation_weight=0.5,
                metric_scores={},
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
            mock_composite.return_value = composite_result

            await pipeline.evaluate_comprehensive(
                paper="test paper", review="test review", execution_trace=None
            )

            # Verify tier weights/contributions are logged
            logged_messages = " ".join(
                [str(call[0][0]) for call in mock_logger.info.call_args_list]
            )

            # Should show tier weights or contributions
            assert "tier1" in logged_messages.lower() or "Tier 1" in logged_messages, (
                "Tier 1 contribution should be mentioned"
            )
            assert "tier3" in logged_messages.lower() or "Tier 3" in logged_messages, (
                "Tier 3 contribution should be mentioned"
            )
