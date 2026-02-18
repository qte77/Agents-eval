"""
Tests for CLI baseline comparison integration (STORY-007).

Validates that --cc-solo-dir and --cc-teams-dir flags work correctly,
baseline comparisons are generated and displayed, and auto-detection
of CC artifact modes works properly.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from inline_snapshot import snapshot

from app.data_models.evaluation_models import CompositeResult
from app.judge.baseline_comparison import BaselineComparison


@pytest.mark.asyncio
async def test_cli_accepts_cc_solo_dir_flag(tmp_path):
    """Test that CLI accepts --cc-solo-dir flag and passes it to main()."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.judge.evaluation_runner.CCTraceAdapter") as mock_adapter,
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

        # Mock pipeline and adapter
        mock_pipeline = MagicMock()
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.8,
            tier3_score=0.8,
            evaluation_complete=True,
        )
        # Mock multiple calls: 1st for PydanticAI, 2nd for CC solo
        mock_pipeline.evaluate_comprehensive = AsyncMock(side_effect=[mock_result, mock_result])
        mock_pipeline_class.return_value = mock_pipeline

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.parse.return_value = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with --cc-solo-dir flag
        await main(
            chat_provider="test_provider",
            query="test query",
            cc_solo_dir=str(tmp_path / "cc-solo-artifacts"),
        )

        # Verify CCTraceAdapter was called with solo directory
        mock_adapter.assert_called()


@pytest.mark.asyncio
async def test_cli_accepts_cc_teams_dir_flag(tmp_path):
    """Test that CLI accepts --cc-teams-dir flag and passes it to main()."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.judge.evaluation_runner.CCTraceAdapter") as mock_adapter,
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

        # Mock pipeline and adapter
        mock_pipeline = MagicMock()
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.8,
            tier3_score=0.8,
            evaluation_complete=True,
        )
        # Mock multiple calls: 1st for PydanticAI, 2nd for CC teams
        mock_pipeline.evaluate_comprehensive = AsyncMock(side_effect=[mock_result, mock_result])
        mock_pipeline_class.return_value = mock_pipeline

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.parse.return_value = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with --cc-teams-dir flag
        await main(
            chat_provider="test_provider",
            query="test query",
            cc_teams_dir=str(tmp_path / "cc-teams-artifacts"),
        )

        # Verify CCTraceAdapter was called
        mock_adapter.assert_called()


@pytest.mark.asyncio
async def test_three_way_comparison_with_both_cc_baselines(tmp_path):
    """Test three-way comparison when both CC baselines are provided."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.judge.evaluation_runner.CCTraceAdapter") as mock_adapter,
        patch("app.judge.evaluation_runner.compare_all") as mock_compare_all,
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

        # Mock pipeline to return CompositeResult for each evaluation
        mock_pipeline = MagicMock()
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.8,
            tier3_score=0.8,
            evaluation_complete=True,
        )
        mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
        mock_pipeline_class.return_value = mock_pipeline

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.parse.return_value = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        mock_load_config.return_value = MagicMock(prompts={})

        # Mock compare_all to return 3 comparisons
        mock_comparison = BaselineComparison(
            label_a="A",
            label_b="B",
            result_a=mock_result,
            result_b=mock_result,
            metric_deltas={"test": 0.0},
            tier_deltas={"tier1": 0.0, "tier2": 0.0, "tier3": 0.0},
            summary="Test comparison",
        )
        mock_compare_all.return_value = [mock_comparison, mock_comparison, mock_comparison]

        from app.app import main

        # Run main with both CC baseline directories
        await main(
            chat_provider="test_provider",
            query="test query",
            cc_solo_dir=str(tmp_path / "cc-solo-artifacts"),
            cc_teams_dir=str(tmp_path / "cc-teams-artifacts"),
        )

        # Verify compare_all was called with 3 results
        mock_compare_all.assert_called_once()
        call_args = mock_compare_all.call_args[0]
        # Should be called with (pydantic_result, cc_solo_result, cc_teams_result)
        assert len(call_args) == 3


@pytest.mark.asyncio
async def test_baseline_comparison_printed_to_console(tmp_path):
    """Test that baseline comparison summary is printed to console."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.judge.evaluation_runner.CCTraceAdapter") as mock_adapter,
        patch("app.judge.evaluation_runner.compare_all") as mock_compare_all,
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

        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.8,
            tier3_score=0.8,
            evaluation_complete=True,
        )
        mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
        mock_pipeline_class.return_value = mock_pipeline

        mock_adapter_instance = MagicMock()
        mock_adapter_instance.parse.return_value = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        mock_load_config.return_value = MagicMock(prompts={})

        # Mock baseline comparison with summary
        mock_comparison = BaselineComparison(
            label_a="PydanticAI",
            label_b="CC-solo",
            result_a=mock_result,
            result_b=mock_result,
            metric_deltas={"test": 0.12},
            tier_deltas={"tier1": 0.12, "tier2": 0.12, "tier3": 0.12},
            summary="PydanticAI scored +0.12 higher vs CC-solo",
        )
        mock_compare_all.return_value = [mock_comparison]

        from app.app import main

        # Run main with CC baseline
        await main(
            chat_provider="test_provider",
            query="test query",
            cc_solo_dir=str(tmp_path / "cc-solo-artifacts"),
        )

        # Verify summary was logged
        mock_logger.info.assert_any_call(
            "Baseline comparison: PydanticAI scored +0.12 higher vs CC-solo"
        )


@pytest.mark.asyncio
async def test_no_baseline_comparison_when_no_cc_dirs():
    """Test that baseline comparison is skipped when no CC directories provided."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.judge.evaluation_runner.compare_all") as mock_compare_all,
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

        # Run main without CC baseline directories
        await main(
            chat_provider="test_provider",
            query="test query",
        )

        # Verify compare_all was NOT called
        mock_compare_all.assert_not_called()


# STORY-009: Tests for default-on review tools and opt-out flag
@pytest.mark.asyncio
async def test_review_tools_enabled_by_default():
    """Test that review tools are enabled by default (STORY-009)."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
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
        mock_run_manager.return_value = ("test_exec_123", None)

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main without explicit enable_review_tools parameter
        await main(
            chat_provider="test_provider",
            query="test query",
        )

        # Verify get_manager was called with enable_review_tools=True (8th positional arg)
        call_args = mock_get_manager.call_args[0]
        # get_manager(provider, provider_config, api_key, prompts,
        #             include_researcher, include_analyst, include_synthesiser, enable_review_tools)
        assert len(call_args) >= 8
        assert call_args[7] is True  # enable_review_tools is 8th arg (index 7)


@pytest.mark.asyncio
async def test_no_review_tools_flag_disables_review_tools():
    """Test that --no-review-tools flag disables review tools (STORY-009)."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
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
        mock_run_manager.return_value = ("test_exec_123", None)

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with enable_review_tools=False (simulating --no-review-tools flag)
        await main(
            chat_provider="test_provider",
            query="test query",
            enable_review_tools=False,
        )

        # Verify get_manager was called with enable_review_tools=False (8th positional arg)
        call_args = mock_get_manager.call_args[0]
        assert len(call_args) >= 8
        assert call_args[7] is False  # enable_review_tools is 8th arg (index 7)


def test_cli_parse_args_includes_no_review_tools_flag():
    """Test that parse_args recognizes --no-review-tools flag (STORY-009)."""
    from run_cli import parse_args

    # Test --no-review-tools flag is recognized and converted to enable_review_tools=False
    args = parse_args(["--no-review-tools"])
    assert "enable_review_tools" in args
    assert args["enable_review_tools"] is False


def test_cli_help_text_includes_no_review_tools():
    """Snapshot test for CLI help text showing --no-review-tools flag (STORY-009)."""
    from run_cli import _COMMANDS

    for expected_flag in ("--no-review-tools", "--enable-review-tools"):
        assert expected_flag in _COMMANDS, f"Expected {expected_flag} in _COMMANDS dict"


# STORY-007: Inline-snapshot tests for CLI output with baselines
class TestCLIBaselineOutputSnapshots:
    """Snapshot tests for CLI baseline comparison output."""

    def test_single_baseline_comparison_output(self):
        """Snapshot: CLI output format with single CC baseline."""
        # Arrange
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.8,
            tier3_score=0.8,
            evaluation_complete=True,
        )
        mock_comparison = BaselineComparison(
            label_a="PydanticAI",
            label_b="CC-solo",
            result_a=mock_result,
            result_b=mock_result,
            metric_deltas={
                "cosine_score": 0.12,
                "jaccard_score": 0.08,
                "semantic_score": 0.15,
            },
            tier_deltas={"tier1": 0.10, "tier2": 0.12, "tier3": 0.08},
            summary="PydanticAI scored +0.10 higher on average vs CC-solo (largest diff: semantic_score +0.15)",
        )

        # Act
        output = {
            "summary": mock_comparison.summary,
            "metric_deltas": mock_comparison.metric_deltas,
            "tier_deltas": mock_comparison.tier_deltas,
        }

        # Assert with snapshot
        assert output == snapshot(
            {
                "summary": "PydanticAI scored +0.10 higher on average vs CC-solo (largest diff: semantic_score +0.15)",
                "metric_deltas": {
                    "cosine_score": 0.12,
                    "jaccard_score": 0.08,
                    "semantic_score": 0.15,
                },
                "tier_deltas": {"tier1": 0.10, "tier2": 0.12, "tier3": 0.08},
            }
        )

    def test_three_way_comparison_output(self):
        """Snapshot: CLI output format with three-way comparison."""
        # Arrange
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.8,
            tier3_score=0.8,
            evaluation_complete=True,
        )
        comparisons = [
            BaselineComparison(
                label_a="PydanticAI",
                label_b="CC-solo",
                result_a=mock_result,
                result_b=mock_result,
                metric_deltas={"cosine_score": 0.12},
                tier_deltas={"tier1": 0.10, "tier2": 0.12, "tier3": 0.08},
                summary="PydanticAI scored +0.10 higher on average vs CC-solo",
            ),
            BaselineComparison(
                label_a="PydanticAI",
                label_b="CC-teams",
                result_a=mock_result,
                result_b=mock_result,
                metric_deltas={"cosine_score": 0.05},
                tier_deltas={"tier1": 0.03, "tier2": 0.06, "tier3": 0.04},
                summary="PydanticAI scored +0.05 higher on average vs CC-teams",
            ),
            BaselineComparison(
                label_a="CC-solo",
                label_b="CC-teams",
                result_a=mock_result,
                result_b=mock_result,
                metric_deltas={"cosine_score": -0.07},
                tier_deltas={"tier1": -0.07, "tier2": -0.06, "tier3": -0.04},
                summary="CC-solo scored -0.07 lower on average vs CC-teams",
            ),
        ]

        # Act
        output = [{"summary": c.summary} for c in comparisons]

        # Assert with snapshot
        assert output == snapshot(
            [
                {"summary": "PydanticAI scored +0.10 higher on average vs CC-solo"},
                {"summary": "PydanticAI scored +0.05 higher on average vs CC-teams"},
                {"summary": "CC-solo scored -0.07 lower on average vs CC-teams"},
            ]
        )
