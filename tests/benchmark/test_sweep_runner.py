"""Tests for MAS composition sweep runner.

This module tests the sweep runner that orchestrates multiple evaluation
runs across different agent compositions and handles Claude Code baseline
invocation.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.benchmark.sweep_config import AgentComposition, SweepConfig
from app.benchmark.sweep_runner import SweepRunner, run_sweep
from app.data_models.evaluation_models import CompositeResult


@pytest.fixture
def mock_composite_result() -> CompositeResult:
    """Create a mock CompositeResult for testing."""
    return CompositeResult(
        overall_score=0.75,
        recommendation="Accept",
        tier1_score=0.8,
        tier2_score=0.7,
        tier3_score=0.75,
        confidence=0.85,
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

    def test_sweep_runner_initialization(self, basic_sweep_config: SweepConfig):
        """Test SweepRunner initializes with valid config."""
        runner = SweepRunner(basic_sweep_config)
        assert runner.config == basic_sweep_config

    @pytest.mark.asyncio
    async def test_run_single_evaluation(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test running a single evaluation with mocked main()."""
        runner = SweepRunner(basic_sweep_config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = mock_composite_result
            composition = basic_sweep_config.compositions[0]
            paper_number = 1

            result = await runner._run_single_evaluation(composition, paper_number, 0)

            assert result is not None
            assert result.overall_score == 0.75
            mock_main.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_sweep_collects_all_results(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that sweep collects results from all compositions x repetitions x papers."""
        runner = SweepRunner(basic_sweep_config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = mock_composite_result

            results = await runner.run()

            # 2 compositions x 2 repetitions x 1 paper = 4 total runs
            assert len(results) == 4
            assert mock_main.call_count == 4

    @pytest.mark.asyncio
    async def test_sweep_saves_results_json(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that sweep saves results to JSON file."""
        runner = SweepRunner(basic_sweep_config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = mock_composite_result

            await runner.run()

            results_file = basic_sweep_config.output_dir / "results.json"
            assert results_file.exists()

            with open(results_file) as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 4


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
            mock_main.return_value = mock_composite_result
            mock_subprocess.return_value = MagicMock(
                returncode=0, stdout='{"result": "test"}'
            )

            await runner.run()

            # Verify CC was invoked via subprocess
            mock_subprocess.assert_called()
            call_args = mock_subprocess.call_args
            assert "claude" in call_args[0][0]
            assert "--output-format" in call_args[0][0]
            assert "json" in call_args[0][0]

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
            mock_main.return_value = mock_composite_result

            await runner.run()

            # Verify CC was NOT invoked
            mock_subprocess.assert_not_called()


class TestRunSweepFunction:
    """Tests for run_sweep() convenience function."""

    @pytest.mark.asyncio
    async def test_run_sweep_with_config(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test run_sweep() function with config."""
        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = mock_composite_result

            results = await run_sweep(basic_sweep_config)

            assert len(results) == 4
