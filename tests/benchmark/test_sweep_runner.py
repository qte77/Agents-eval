"""Tests for MAS composition sweep runner.

This module tests the sweep runner that orchestrates multiple evaluation
runs across different agent compositions and handles Claude Code baseline
invocation.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.benchmark.sweep_config import AgentComposition, SweepConfig
from app.benchmark.sweep_runner import SweepRunner
from app.data_models.evaluation_models import CompositeResult


@pytest.fixture
def mock_composite_result() -> CompositeResult:
    """Create a mock CompositeResult for testing."""
    return CompositeResult(
        composite_score=0.75,
        recommendation="Accept",
        recommendation_weight=0.75,
        metric_scores={"tier1": 0.8, "tier2": 0.7, "tier3": 0.75},
        tier1_score=0.8,
        tier2_score=0.7,
        tier3_score=0.75,
        evaluation_complete=True,
    )


@pytest.fixture
def basic_sweep_config(tmp_path: Path) -> SweepConfig:
    """Create a basic sweep configuration for testing."""
    return SweepConfig(
        compositions=[
            AgentComposition(
                include_researcher=True,
                include_analyst=False,
                include_synthesiser=False,
            ),
            AgentComposition(
                include_researcher=False,
                include_analyst=True,
                include_synthesiser=False,
            ),
        ],
        repetitions=2,
        paper_numbers=[1],
        output_dir=tmp_path / "sweep_results",
    )


class TestSweepRunner:
    """Tests for SweepRunner class."""

    @pytest.mark.asyncio
    async def test_run_sweep_collects_all_results(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that sweep collects results from all compositions x repetitions x papers."""
        runner = SweepRunner(basic_sweep_config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = {"composite_result": mock_composite_result}

            results = await runner.run()

            # 2 compositions x 2 repetitions x 1 paper = 4 total runs
            assert len(results) == 4

    @pytest.mark.asyncio
    async def test_sweep_saves_results_json(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that sweep saves results to JSON file."""
        runner = SweepRunner(basic_sweep_config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            results_file = basic_sweep_config.output_dir / "results.json"
            assert results_file.exists()

            with open(results_file) as f:
                data = json.load(f)
            assert len(data) == 4
            assert data[0]["composition"]["include_researcher"] is True

    @pytest.mark.asyncio
    async def test_runner_passes_configured_provider_to_evaluations(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that the provider from config is forwarded to every evaluation call."""
        config = SweepConfig(
            compositions=[
                AgentComposition(
                    include_researcher=True,
                    include_analyst=False,
                    include_synthesiser=False,
                )
            ],
            repetitions=1,
            paper_numbers=[1],
            output_dir=tmp_path / "sweep_results",
            chat_provider="cerebras",
        )
        runner = SweepRunner(config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            call_kwargs = mock_main.call_args.kwargs
            assert call_kwargs["chat_provider"] == "cerebras"


class TestCCBaselineIntegration:
    """Tests for Claude Code baseline invocation."""

    @pytest.mark.asyncio
    async def test_cc_baseline_invoked_when_enabled(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that CC baseline is invoked when cc_baseline_enabled=True."""
        config = SweepConfig(
            compositions=[
                AgentComposition(
                    include_researcher=True,
                    include_analyst=False,
                    include_synthesiser=False,
                )
            ],
            repetitions=1,
            paper_numbers=[1],
            output_dir=tmp_path / "sweep_results",
            cc_baseline_enabled=True,
        )
        runner = SweepRunner(config)

        with (
            patch("app.benchmark.sweep_runner.main") as mock_main,
            patch("app.benchmark.sweep_runner.subprocess.run") as mock_subprocess,
            patch("shutil.which", return_value="/usr/bin/claude"),
        ):
            mock_main.return_value = {"composite_result": mock_composite_result}
            mock_subprocess.return_value = MagicMock(returncode=0, stdout='{"result": "test"}')

            await runner.run()

            # Verify the Claude CLI was invoked (behavioral: CC baseline ran)
            mock_subprocess.assert_called_once()
            cmd = mock_subprocess.call_args[0][0]
            assert any("claude" in arg for arg in cmd)

    @pytest.mark.asyncio
    async def test_cc_baseline_error_when_claude_not_found(self, tmp_path: Path):
        """Test that sweep exits with error when claude CLI not found."""
        config = SweepConfig(
            compositions=[
                AgentComposition(
                    include_researcher=True,
                    include_analyst=False,
                    include_synthesiser=False,
                )
            ],
            repetitions=1,
            paper_numbers=[1],
            output_dir=tmp_path / "sweep_results",
            cc_baseline_enabled=True,
        )
        runner = SweepRunner(config)

        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="claude CLI not found"):
                await runner.run()

    @pytest.mark.asyncio
    async def test_cc_baseline_not_invoked_when_disabled(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that CC baseline is not invoked when cc_baseline_enabled=False."""
        runner = SweepRunner(basic_sweep_config)

        with (
            patch("app.benchmark.sweep_runner.main") as mock_main,
            patch("app.benchmark.sweep_runner.subprocess.run") as mock_subprocess,
        ):
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            # Verify CC was NOT invoked
            mock_subprocess.assert_not_called()
