"""Tests for MAS composition sweep runner.

This module tests the sweep runner that orchestrates multiple evaluation
runs across different agent compositions and handles Claude Code baseline
invocation.
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai.exceptions import ModelHTTPError

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
        paper_ids=["1"],
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
            paper_ids=["1"],
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
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            engine="cc",
        )
        runner = SweepRunner(config)

        from app.engines.cc_engine import CCResult

        mock_cc_result = CCResult(execution_id="exec-001", output_data={})

        with (
            patch("app.benchmark.sweep_runner.main") as mock_main,
            patch(
                "app.benchmark.sweep_runner.run_cc_solo", return_value=mock_cc_result
            ) as mock_cc_solo,
            patch("app.benchmark.sweep_runner.check_cc_available", return_value=True),
        ):
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            # Verify cc_engine.run_cc_solo was invoked (behavioral: CC comparison ran)
            mock_cc_solo.assert_called_once()

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
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            engine="cc",
        )
        runner = SweepRunner(config)

        with patch("app.benchmark.sweep_runner.check_cc_available", return_value=False):
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
            patch("app.benchmark.sweep_runner.run_cc_solo") as mock_cc_solo,
        ):
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            # Verify CC was NOT invoked when engine=mas
            mock_cc_solo.assert_not_called()


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
            paper_ids=["1"],
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
            paper_ids=["1"],
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
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
        )
        assert not hasattr(config, "cc_baseline_enabled"), (
            "SweepConfig must NOT have cc_baseline_enabled field (removed in STORY-013)"
        )

    def test_sweep_runner_has_invoke_cc_comparison_method(self, basic_sweep_config: SweepConfig):
        """Test that SweepRunner has _invoke_cc_comparison() method (renamed from _invoke_cc_baseline)."""
        runner = SweepRunner(basic_sweep_config)
        assert hasattr(runner, "_invoke_cc_comparison"), (
            "SweepRunner must have _invoke_cc_comparison method"
        )
        assert not hasattr(runner, "_invoke_cc_baseline"), (
            "SweepRunner must NOT have _invoke_cc_baseline (renamed to _invoke_cc_comparison)"
        )

    def test_cc_baseline_enabled_not_in_model_fields(self, tmp_path: Path):
        """Test that cc_baseline_enabled is not a defined field on SweepConfig."""
        # Pydantic silently ignores extra fields by default, but the field must
        # not be declared on the model (i.e., not in model_fields)
        assert "cc_baseline_enabled" not in SweepConfig.model_fields, (
            "cc_baseline_enabled must be removed from SweepConfig.model_fields in STORY-013"
        )


class TestStory013bRetryAndPersistence:
    """Tests for STORY-013b: rate-limit retry, SystemExit fix, incremental persistence."""

    def test_sweep_config_has_retry_delay_seconds_field(self, tmp_path: Path):
        """Test that SweepConfig has retry_delay_seconds field defaulting to 5.0."""
        config = SweepConfig(
            compositions=[AgentComposition(include_researcher=True)],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
        )
        assert hasattr(config, "retry_delay_seconds"), (
            "SweepConfig must have 'retry_delay_seconds' field"
        )
        assert config.retry_delay_seconds == 5.0, "retry_delay_seconds must default to 5.0"

    def test_sweep_config_retry_delay_in_model_fields(self, tmp_path: Path):
        """Test that retry_delay_seconds is a declared Pydantic field."""
        assert "retry_delay_seconds" in SweepConfig.model_fields

    def test_sweep_runner_has_save_results_json_method(self, basic_sweep_config: SweepConfig):
        """Test that SweepRunner has _save_results_json() method (split from _save_results)."""
        runner = SweepRunner(basic_sweep_config)
        assert hasattr(runner, "_save_results_json"), (
            "SweepRunner must have _save_results_json method"
        )

    @pytest.mark.asyncio
    async def test_save_results_json_writes_only_results_json(
        self, basic_sweep_config: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that _save_results_json() writes only results.json, not summary.md."""
        basic_sweep_config.output_dir.mkdir(parents=True, exist_ok=True)
        runner = SweepRunner(basic_sweep_config)
        comp = basic_sweep_config.compositions[0]
        runner.results = [(comp, mock_composite_result)]

        await runner._save_results_json()

        results_file = basic_sweep_config.output_dir / "results.json"
        summary_file = basic_sweep_config.output_dir / "summary.md"
        assert results_file.exists(), "_save_results_json must write results.json"
        assert not summary_file.exists(), "_save_results_json must NOT write summary.md"

    @pytest.mark.asyncio
    async def test_incremental_results_written_after_each_evaluation(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that results.json is written after each successful evaluation."""
        config = SweepConfig(
            compositions=[
                AgentComposition(include_researcher=True),
                AgentComposition(include_analyst=True),
            ],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            retry_delay_seconds=0.0,
        )
        config.output_dir.mkdir(parents=True, exist_ok=True)
        runner = SweepRunner(config)

        write_counts = []

        original_save_json = runner._save_results_json

        async def counting_save_json():
            await original_save_json()
            if (config.output_dir / "results.json").exists():
                with open(config.output_dir / "results.json") as f:
                    data = json.load(f)
                write_counts.append(len(data))

        runner._save_results_json = counting_save_json  # type: ignore[method-assign]

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = {"composite_result": mock_composite_result}
            await runner._run_mas_evaluations()

        # Should have been called twice (once per composition), each time with growing data
        assert len(write_counts) == 2, (
            "_save_results_json must be called after each successful evaluation"
        )
        assert write_counts[0] == 1, "After first eval, results.json should have 1 entry"
        assert write_counts[1] == 2, "After second eval, results.json should have 2 entries"

    @pytest.mark.asyncio
    async def test_run_single_evaluation_retries_on_rate_limit(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that _run_single_evaluation retries on HTTP 429 errors."""
        config = SweepConfig(
            compositions=[AgentComposition(include_researcher=True)],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            retry_delay_seconds=0.0,
        )
        runner = SweepRunner(config)
        comp = config.compositions[0]

        # Raise 429 twice, then succeed
        rate_limit_error = ModelHTTPError(status_code=429, model_name="test-model", body={})
        call_count = 0

        async def mock_main_with_retry(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise rate_limit_error
            return {"composite_result": mock_composite_result}

        with patch("app.benchmark.sweep_runner.main", side_effect=mock_main_with_retry):
            result = await runner._run_single_evaluation(comp, "1", 0)

        assert result is not None, "Should succeed after retries"
        assert call_count == 3, f"Expected 3 calls (2 retries + 1 success), got {call_count}"

    @pytest.mark.asyncio
    async def test_run_single_evaluation_returns_none_after_max_retries(self, tmp_path: Path):
        """Test that _run_single_evaluation returns None after exhausting retries."""
        config = SweepConfig(
            compositions=[AgentComposition(include_researcher=True)],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            retry_delay_seconds=0.0,
        )
        runner = SweepRunner(config)
        comp = config.compositions[0]

        rate_limit_error = ModelHTTPError(status_code=429, model_name="test-model", body={})

        with patch("app.benchmark.sweep_runner.main", side_effect=rate_limit_error):
            result = await runner._run_single_evaluation(comp, "1", 0)

        assert result is None, "Should return None after max retries exhausted"

    @pytest.mark.asyncio
    async def test_run_single_evaluation_max_retries_is_three(self, tmp_path: Path):
        """Test that _run_single_evaluation retries exactly 3 times on rate-limit errors."""
        config = SweepConfig(
            compositions=[AgentComposition(include_researcher=True)],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            retry_delay_seconds=0.0,
        )
        runner = SweepRunner(config)
        comp = config.compositions[0]

        rate_limit_error = ModelHTTPError(status_code=429, model_name="test-model", body={})
        call_count = 0

        async def counting_main(**kwargs):
            nonlocal call_count
            call_count += 1
            raise rate_limit_error

        with patch("app.benchmark.sweep_runner.main", side_effect=counting_main):
            await runner._run_single_evaluation(comp, "1", 0)

        # initial attempt + 3 retries = 4 total calls
        assert call_count == 4, f"Expected 4 calls (1 initial + 3 retries), got {call_count}"

    @pytest.mark.asyncio
    async def test_sweep_continues_after_rate_limit_exhausted(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that sweep continues to next evaluation after rate-limit max retries."""
        config = SweepConfig(
            compositions=[
                AgentComposition(include_researcher=True),
                AgentComposition(include_analyst=True),
            ],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            retry_delay_seconds=0.0,
        )
        runner = SweepRunner(config)

        rate_limit_error = ModelHTTPError(status_code=429, model_name="test-model", body={})
        call_count = 0

        async def mock_main(**kwargs):
            nonlocal call_count
            call_count += 1
            # First composition (all 4 attempts) fail with rate limit
            if call_count <= 4:
                raise rate_limit_error
            # Second composition succeeds
            return {"composite_result": mock_composite_result}

        with patch("app.benchmark.sweep_runner.main", side_effect=mock_main):
            with patch("app.benchmark.sweep_runner.SweepRunner._save_results_json"):
                await runner._run_mas_evaluations()

        # Only second composition succeeded
        assert len(runner.results) == 1, (
            "Only second composition should be in results; first exhausted retries"
        )


class TestStory013bHandleModelHttpError:
    """Tests for _handle_model_http_error re-raise fix (STORY-013b)."""

    def test_handle_model_http_error_reraises_429_as_model_http_error(self):
        """Test that _handle_model_http_error raises ModelHTTPError (not SystemExit) for 429."""
        from app.agents.agent_system import _handle_model_http_error

        error = ModelHTTPError(status_code=429, model_name="test-model", body={})

        with pytest.raises(ModelHTTPError):
            _handle_model_http_error(error, "test-provider", "test-model")

    def test_handle_model_http_error_does_not_raise_systemexit_for_429(self):
        """Test that _handle_model_http_error does NOT raise SystemExit for 429."""
        from app.agents.agent_system import _handle_model_http_error

        error = ModelHTTPError(status_code=429, model_name="test-model", body={})

        try:
            _handle_model_http_error(error, "test-provider", "test-model")
        except SystemExit:
            pytest.fail("_handle_model_http_error must not raise SystemExit for 429")
        except ModelHTTPError:
            pass  # Expected

    def test_handle_model_http_error_reraises_non_429_errors(self):
        """Test that _handle_model_http_error re-raises non-429 errors as-is."""
        from app.agents.agent_system import _handle_model_http_error

        error = ModelHTTPError(status_code=500, model_name="test-model", body={})

        with pytest.raises(ModelHTTPError) as exc_info:
            _handle_model_http_error(error, "test-provider", "test-model")

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_run_manager_raises_systemexit_on_429(self):
        """Test that run_manager catches ModelHTTPError 429 and raises SystemExit(1)."""
        from app.agents.agent_system import run_manager

        rate_limit_error = ModelHTTPError(status_code=429, model_name="test-model", body={})

        mock_manager = MagicMock()
        mock_manager.model._model_name = "test-model"
        mock_manager.run = AsyncMock(side_effect=rate_limit_error)

        mock_trace_collector = MagicMock()
        mock_trace_collector.start_execution = MagicMock()
        mock_trace_collector.end_execution = MagicMock()

        with patch(
            "app.agents.agent_system.get_trace_collector", return_value=mock_trace_collector
        ):
            with pytest.raises(SystemExit) as exc_info:
                await run_manager(mock_manager, "test query", "test-provider", None)

        assert exc_info.value.code == 1, "run_manager must exit with code 1 on rate limit"
