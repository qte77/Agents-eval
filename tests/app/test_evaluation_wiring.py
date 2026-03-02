"""
Tests for evaluation pipeline wiring in app.py.

Validates that evaluate_comprehensive runs after run_manager,
--skip-eval flag works correctly, and graceful handling of missing
ground-truth reviews.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from inline_snapshot import snapshot

from app.data_models.evaluation_models import CompositeResult, Tier1Result


@pytest.fixture(autouse=True)
def _mock_run_context():
    """Prevent real RunContext.create() → mkdir during tests."""
    mock_ctx = MagicMock()
    mock_ctx.run_dir = None
    with patch("app.app.RunContext") as mock_rc:
        mock_rc.create.return_value = mock_ctx
        yield mock_rc


@pytest.mark.asyncio
async def test_evaluation_runs_after_manager_by_default():
    """Test that evaluation runs automatically after run_manager completes."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        mock_run_manager.return_value = ("test_exec_123", None)  # (execution_id, manager_output)

        # Mock pipeline instance
        mock_pipeline = MagicMock()
        mock_pipeline.evaluate_comprehensive = AsyncMock(
            return_value=CompositeResult(
                tier1=Tier1Result(
                    cosine_score=0.8,
                    jaccard_score=0.75,
                    semantic_score=0.85,
                    execution_time=0.5,
                    time_score=0.9,
                    task_success=1.0,
                    overall_score=0.82,
                ),
                composite_score=0.8,
                total_execution_time=1.0,
                recommendation="accept",
                recommendation_weight=1.0,
                metric_scores={"cosine_score": 0.8},
                tier1_score=0.82,
                tier2_score=0.0,
                tier3_score=0.0,
                evaluation_complete=True,
            )
        )
        mock_pipeline_class.return_value = mock_pipeline

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main without --skip-eval
        await main(
            chat_provider="test_provider",
            query="test query",
        )

        # Verify evaluation was called
        mock_pipeline.evaluate_comprehensive.assert_called_once()


@pytest.mark.asyncio
async def test_skip_eval_flag_prevents_evaluation():
    """Test that --skip-eval flag prevents evaluation from running."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        mock_run_manager.return_value = ("test_exec_123", None)  # (execution_id, manager_output)

        mock_pipeline = MagicMock()
        mock_pipeline.evaluate_comprehensive = AsyncMock()
        mock_pipeline_class.return_value = mock_pipeline

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with --skip-eval
        await main(
            chat_provider="test_provider",
            query="test query",
            skip_eval=True,
        )

        # Verify evaluation was NOT called
        mock_pipeline.evaluate_comprehensive.assert_not_called()


@pytest.mark.asyncio
async def test_graceful_skip_without_ground_truth():
    """Test graceful handling when no ground-truth reviews are available."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.judge.evaluation_runner.logger") as mock_logger,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        mock_run_manager.return_value = ("test_exec_123", None)  # (execution_id, manager_output)

        mock_pipeline = MagicMock()
        mock_pipeline.evaluate_comprehensive = AsyncMock()
        mock_pipeline_class.return_value = mock_pipeline

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main without paper_id (no ground truth available)
        await main(
            chat_provider="test_provider",
            query="test query",
        )

        # Should log info about skipping evaluation
        mock_logger.info.assert_any_call("Skipping evaluation: no ground-truth reviews available")


def test_skip_eval_cli_argument_parsing():
    """Test that --skip-eval argument is parsed correctly."""
    from run_cli import parse_args

    # Test with --skip-eval flag
    args = parse_args(["--skip-eval"])
    assert "skip_eval" in args
    assert args["skip_eval"] is True

    # Test without --skip-eval flag
    args = parse_args(["--query=test"])
    assert "skip_eval" not in args


# STORY-004: Inline-snapshot regression tests for wiring outputs
class TestEvaluationWiringSnapshots:
    """Snapshot tests for evaluation wiring output structures."""

    def test_composite_result_structure(self):
        """Snapshot: CompositeResult model dump structure."""
        # Arrange
        result = CompositeResult(
            tier1=Tier1Result(
                cosine_score=0.8,
                jaccard_score=0.75,
                semantic_score=0.85,
                execution_time=0.5,
                time_score=0.9,
                task_success=1.0,
                overall_score=0.82,
            ),
            composite_score=0.8,
            total_execution_time=1.0,
            recommendation="accept",
            recommendation_weight=1.0,
            metric_scores={"cosine_score": 0.8},
            tier1_score=0.82,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )

        # Act
        dumped = result.model_dump()

        # Assert with snapshot
        assert dumped == snapshot(
            {
                "composite_score": 0.8,
                "recommendation": "accept",
                "recommendation_weight": 1.0,
                "metric_scores": {"cosine_score": 0.8},
                "tier1_score": 0.82,
                "tier2_score": 0.0,
                "tier3_score": 0.0,
                "evaluation_complete": True,
                "single_agent_mode": False,
                "timestamp": "",
                "config_version": "1.0.0",
                "weights_used": None,
                "tiers_enabled": None,
                "agent_assessment_scores": None,
                "engine_type": "mas",
            }
        )
