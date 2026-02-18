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
    """Tests for Claude Code comparison invocation (engine=cc)."""

    @pytest.mark.asyncio
    async def test_cc_comparison_invoked_when_engine_cc(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that CC comparison is invoked when engine='cc'."""
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
            engine="cc",
        )
        runner = SweepRunner(config)

        with (
            patch("app.benchmark.sweep_runner.main") as mock_main,
            patch("app.benchmark.sweep_runner.subprocess.run") as mock_subprocess,
            patch("app.benchmark.sweep_runner.shutil.which", return_value="/usr/bin/claude"),
        ):
            mock_main.return_value = {"composite_result": mock_composite_result}
            mock_subprocess.return_value = MagicMock(returncode=0, stdout='{"result": "test"}')

            await runner.run()

            # Verify the Claude CLI was invoked (behavioral: CC comparison ran)
            mock_subprocess.assert_called_once()
            cmd = mock_subprocess.call_args[0][0]
            assert any("claude" in arg for arg in cmd)

    @pytest.mark.asyncio
    async def test_cc_comparison_error_when_claude_not_found(self, tmp_path: Path):
        """Test that sweep raises error when engine=cc but claude CLI not found."""
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
            engine="cc",
        )
        runner = SweepRunner(config)

        with patch("app.benchmark.sweep_runner.shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="claude CLI"):
                await runner.run()

    @pytest.mark.asyncio
    async def test_cc_comparison_not_invoked_when_engine_mas(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that CC comparison is not invoked when engine='mas' (default)."""
        runner = SweepRunner(basic_sweep_config)

        with (
            patch("app.benchmark.sweep_runner.main") as mock_main,
            patch("app.benchmark.sweep_runner.subprocess.run") as mock_subprocess,
        ):
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            # Verify CC was NOT invoked
            mock_subprocess.assert_not_called()


class TestStory013EngineRefactor:
    """Tests for STORY-013: engine field and renamed method in SweepRunner."""

    def test_sweep_config_has_engine_field(self, tmp_path: Path):
        """Test that SweepConfig has 'engine' field defaulting to 'mas'."""
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
        )
        assert hasattr(config, "engine"), "SweepConfig must have 'engine' field"
        assert config.engine == "mas", "engine must default to 'mas'"

    def test_sweep_config_engine_can_be_set_to_cc(self, tmp_path: Path):
        """Test that SweepConfig engine can be set to 'cc'."""
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
            engine="cc",
        )
        assert config.engine == "cc"

    def test_sweep_config_has_no_cc_baseline_enabled_field(self, tmp_path: Path):
        """Test that SweepConfig no longer has cc_baseline_enabled field."""
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
        )
        assert not hasattr(
            config, "cc_baseline_enabled"
        ), "SweepConfig must NOT have cc_baseline_enabled field (removed in STORY-013)"

    def test_sweep_runner_has_invoke_cc_comparison_method(self, basic_sweep_config: SweepConfig):
        """Test that SweepRunner has _invoke_cc_comparison() method (renamed from _invoke_cc_baseline)."""
        runner = SweepRunner(basic_sweep_config)
        assert hasattr(
            runner, "_invoke_cc_comparison"
        ), "SweepRunner must have _invoke_cc_comparison method"
        assert not hasattr(
            runner, "_invoke_cc_baseline"
        ), "SweepRunner must NOT have _invoke_cc_baseline (renamed to _invoke_cc_comparison)"

    def test_cc_baseline_enabled_not_in_model_fields(self, tmp_path: Path):
        """Test that cc_baseline_enabled is not a defined field on SweepConfig."""
        # Pydantic silently ignores extra fields by default, but the field must
        # not be declared on the model (i.e., not in model_fields)
        assert (
            "cc_baseline_enabled" not in SweepConfig.model_fields
        ), "cc_baseline_enabled must be removed from SweepConfig.model_fields in STORY-013"
