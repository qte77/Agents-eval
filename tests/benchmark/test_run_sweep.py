"""Tests for run_sweep CLI provider threading.

Verifies --chat-provider flag reaches SweepConfig through both CLI args and JSON file paths.
Updated in STORY-012: --provider renamed to --chat-provider, --paper-numbers to --paper-ids.
Also covers --judge-provider, --judge-model, SweepConfig paper_ids/judge fields, and
SweepRunner judge settings threading.
"""

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from app.benchmark.sweep_config import AgentComposition, SweepConfig
from app.benchmark.sweep_runner import SweepRunner
from app.config.config_app import CHAT_DEFAULT_PROVIDER
from app.data_models.evaluation_models import CompositeResult
from run_sweep import _build_config_from_args, _load_config_from_file, parse_args


class TestParseArgsChatProvider:
    """Tests for --chat-provider CLI argument parsing (renamed from --provider in STORY-012)."""

    def test_chat_provider_flag_sets_provider(self):
        """Test that --chat-provider flag value reaches the parsed namespace."""
        with patch.object(
            sys, "argv", ["run_sweep.py", "--paper-ids=1", "--chat-provider=cerebras"]
        ):
            args = parse_args()

        assert args.chat_provider == "cerebras"


class TestBuildConfigFromArgs:
    """Tests for _build_config_from_args() provider threading."""

    def test_chat_provider_threads_to_sweep_config(self, tmp_path: Path):
        """Test that the chat_provider from CLI args is set on SweepConfig."""
        args = argparse.Namespace(
            paper_ids="1",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            chat_provider="cerebras",
            engine="mas",
            judge_provider="auto",
            judge_model=None,
        )

        config = _build_config_from_args(args)

        assert config is not None
        assert config.chat_provider == "cerebras"


class TestLoadConfigFromFile:
    """Tests for _load_config_from_file() provider threading."""

    def _write_config(self, tmp_path: Path, extra: dict[str, object]) -> Path:
        """Write a minimal sweep config JSON with optional extra keys."""
        base = {
            "compositions": [
                {"include_researcher": True, "include_analyst": False, "include_synthesiser": False}
            ],
            "repetitions": 1,
            "paper_ids": ["1"],
            "output_dir": str(tmp_path / "results"),
        }
        config_file = tmp_path / "sweep.json"
        config_file.write_text(json.dumps({**base, **extra}))
        return config_file

    def test_reads_chat_provider_from_json(self, tmp_path: Path):
        """Test that 'chat_provider' key in config JSON is used."""
        config_file = self._write_config(tmp_path, {"chat_provider": "cerebras"})

        config = _load_config_from_file(config_file)

        assert config is not None
        assert config.chat_provider == "cerebras"

    def test_legacy_provider_key_returns_none(self, tmp_path: Path):
        """Test that old 'provider' key in config JSON is ignored (legacy key removed)."""
        config_file = self._write_config(tmp_path, {"provider": "cerebras"})

        config = _load_config_from_file(config_file)

        assert config is not None
        # Legacy 'provider' key ignored; falls back to default
        assert config.chat_provider == CHAT_DEFAULT_PROVIDER

    def test_falls_back_to_default_when_provider_absent(self, tmp_path: Path):
        """Test that missing 'chat_provider' key falls back to CHAT_DEFAULT_PROVIDER."""
        config_file = self._write_config(tmp_path, {})

        config = _load_config_from_file(config_file)

        assert config is not None
        assert config.chat_provider == CHAT_DEFAULT_PROVIDER


class TestStory013EngineFlagInRunSweep:
    """Tests for STORY-013: --engine flag in run_sweep and removal of --cc-baseline."""

    def test_engine_flag_accepted_with_mas(self):
        """Test that --engine=mas is accepted by run_sweep parse_args."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1", "--engine=mas"]):
            args = parse_args()

        assert args.engine == "mas"

    def test_engine_flag_accepted_with_cc(self):
        """Test that --engine=cc is accepted by run_sweep parse_args."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1", "--engine=cc"]):
            args = parse_args()

        assert args.engine == "cc"

    def test_engine_defaults_to_mas(self):
        """Test that --engine defaults to 'mas' when not specified."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1"]):
            args = parse_args()

        assert args.engine == "mas"

    def test_cc_baseline_flag_no_longer_accepted(self):
        """Test that --cc-baseline is rejected (removed in STORY-013)."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1", "--cc-baseline"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_build_config_from_args_uses_engine_not_cc_baseline(self, tmp_path: Path):
        """Test _build_config_from_args uses engine field not cc_baseline_enabled."""
        args = argparse.Namespace(
            paper_ids="1",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            chat_provider="cerebras",
            engine="mas",
            judge_provider="auto",
            judge_model=None,
        )

        config = _build_config_from_args(args)

        assert config is not None
        assert config.engine == "mas"
        assert not hasattr(config, "cc_baseline_enabled")


class TestPaperIdsRename:
    """Tests for --paper-numbers -> --paper-ids rename in run_sweep."""

    def test_paper_ids_flag_accepted(self):
        """Test that --paper-ids flag is accepted by parse_args."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1,2,3"]):
            args = parse_args()
        assert hasattr(args, "paper_ids")
        assert args.paper_ids == "1,2,3"

    def test_paper_numbers_no_longer_accepted(self):
        """Test that --paper-numbers raises SystemExit (removed)."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-numbers=1"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_paper_ids_supports_arxiv_ids(self):
        """Test that --paper-ids accepts string IDs like '1105.1072'."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1105.1072"]):
            args = parse_args()
        assert args.paper_ids == "1105.1072"

    def test_build_config_paper_ids_as_strings(self, tmp_path: Path):
        """Test that paper_ids in built config are strings, not ints."""
        args = argparse.Namespace(
            paper_ids="1,2,3",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            chat_provider=CHAT_DEFAULT_PROVIDER,
            engine="mas",
            judge_provider="auto",
            judge_model=None,
        )
        config = _build_config_from_args(args)
        assert config is not None
        assert config.paper_ids == ["1", "2", "3"]
        assert all(isinstance(p, str) for p in config.paper_ids)

    def test_build_config_arxiv_paper_id(self, tmp_path: Path):
        """Test that arxiv IDs like '1105.1072' are accepted without crashing."""
        args = argparse.Namespace(
            paper_ids="1105.1072",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            chat_provider=CHAT_DEFAULT_PROVIDER,
            engine="mas",
            judge_provider="auto",
            judge_model=None,
        )
        config = _build_config_from_args(args)
        assert config is not None
        assert config.paper_ids == ["1105.1072"]


class TestChatProviderRenameExtra:
    """Additional tests for --provider -> --chat-provider rename not covered elsewhere."""

    def test_provider_flag_no_longer_accepted(self):
        """Test that --provider raises SystemExit (renamed to --chat-provider)."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1", "--provider=cerebras"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_chat_provider_defaults_to_app_default(self):
        """Test that --chat-provider defaults to CHAT_DEFAULT_PROVIDER."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1"]):
            args = parse_args()
        assert args.chat_provider == CHAT_DEFAULT_PROVIDER


class TestJudgeProviderArgsInSweep:
    """Tests for --judge-provider and --judge-model in run_sweep."""

    def test_judge_provider_flag_accepted(self):
        """Test that --judge-provider is accepted."""
        with patch.object(
            sys, "argv", ["run_sweep.py", "--paper-ids=1", "--judge-provider=openai"]
        ):
            args = parse_args()
        assert args.judge_provider == "openai"

    def test_judge_model_flag_accepted(self):
        """Test that --judge-model is accepted."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1", "--judge-model=gpt-4o"]):
            args = parse_args()
        assert args.judge_model == "gpt-4o"

    def test_judge_provider_defaults_to_auto(self):
        """Test that --judge-provider defaults to 'auto'."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1"]):
            args = parse_args()
        assert args.judge_provider == "auto"

    def test_judge_model_defaults_to_none(self):
        """Test that --judge-model defaults to None."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-ids=1"]):
            args = parse_args()
        assert args.judge_model is None

    def test_build_config_includes_judge_fields(self, tmp_path: Path):
        """Test that _build_config_from_args includes judge_provider and judge_model."""
        args = argparse.Namespace(
            paper_ids="1",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            chat_provider=CHAT_DEFAULT_PROVIDER,
            engine="mas",
            judge_provider="openai",
            judge_model="gpt-4o",
        )
        config = _build_config_from_args(args)
        assert config is not None
        assert config.judge_provider == "openai"
        assert config.judge_model == "gpt-4o"


class TestSweepConfigPaperIds:
    """Tests for SweepConfig.paper_ids field (renamed from paper_numbers)."""

    def test_sweep_config_has_paper_ids_field(self, tmp_path: Path):
        """Test that SweepConfig has paper_ids: list[str] field."""
        config = SweepConfig(
            compositions=[AgentComposition()],
            repetitions=1,
            paper_ids=["1", "2"],
            output_dir=tmp_path / "results",
        )
        assert config.paper_ids == ["1", "2"]

    def test_sweep_config_paper_ids_accepts_arxiv_ids(self, tmp_path: Path):
        """Test that paper_ids accepts arxiv-style IDs like '1105.1072'."""
        config = SweepConfig(
            compositions=[AgentComposition()],
            repetitions=1,
            paper_ids=["1105.1072"],
            output_dir=tmp_path / "results",
        )
        assert config.paper_ids == ["1105.1072"]

    def test_sweep_config_has_no_paper_numbers_field(self, tmp_path: Path):
        """Test that SweepConfig no longer has paper_numbers field (renamed)."""
        assert "paper_numbers" not in SweepConfig.model_fields

    def test_sweep_config_has_judge_provider_field(self, tmp_path: Path):
        """Test that SweepConfig has judge_provider field defaulting to 'auto'."""
        config = SweepConfig(
            compositions=[AgentComposition()],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "results",
        )
        assert config.judge_provider == "auto"

    def test_sweep_config_has_judge_model_field(self, tmp_path: Path):
        """Test that SweepConfig has judge_model field defaulting to None."""
        config = SweepConfig(
            compositions=[AgentComposition()],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "results",
        )
        assert config.judge_model is None

    def test_sweep_config_judge_provider_can_be_set(self, tmp_path: Path):
        """Test that judge_provider can be overridden."""
        config = SweepConfig(
            compositions=[AgentComposition()],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "results",
            judge_provider="openai",
            judge_model="gpt-4o",
        )
        assert config.judge_provider == "openai"
        assert config.judge_model == "gpt-4o"


class TestSweepRunnerPaperIdRename:
    """Tests for SweepRunner using paper_id: str instead of paper_number: int."""

    @pytest.fixture
    def mock_composite_result(self) -> CompositeResult:
        """Create a mock CompositeResult."""
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
    def sweep_config_with_str_ids(self, tmp_path: Path) -> SweepConfig:
        """Create a sweep config with string paper IDs."""
        return SweepConfig(
            compositions=[AgentComposition(include_researcher=True)],
            repetitions=1,
            paper_ids=["1105.1072"],
            output_dir=tmp_path / "sweep_results",
        )

    @pytest.mark.asyncio
    async def test_sweep_runner_uses_paper_id_as_string(
        self, sweep_config_with_str_ids: SweepConfig, mock_composite_result: CompositeResult
    ):
        """Test that SweepRunner passes paper_id as string to main()."""
        runner = SweepRunner(sweep_config_with_str_ids)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            call_kwargs = mock_main.call_args.kwargs
            # paper_id should be a string, not an integer
            assert isinstance(call_kwargs["paper_id"], str)
            assert call_kwargs["paper_id"] == "1105.1072"

    @pytest.mark.asyncio
    async def test_sweep_runner_passes_judge_settings_when_configured(
        self, tmp_path: Path, mock_composite_result: CompositeResult
    ):
        """Test that SweepRunner threads judge_provider and judge_model to main()."""
        config = SweepConfig(
            compositions=[AgentComposition(include_researcher=True)],
            repetitions=1,
            paper_ids=["1"],
            output_dir=tmp_path / "sweep_results",
            judge_provider="openai",
            judge_model="gpt-4o",
        )
        runner = SweepRunner(config)

        with patch("app.benchmark.sweep_runner.main") as mock_main:
            mock_main.return_value = {"composite_result": mock_composite_result}

            await runner.run()

            call_kwargs = mock_main.call_args.kwargs
            # judge_settings should be passed with configured values
            assert "judge_settings" in call_kwargs
            judge_settings = call_kwargs["judge_settings"]
            assert judge_settings is not None
            assert judge_settings.tier2_provider == "openai"
            assert judge_settings.tier2_model == "gpt-4o"


class TestLoadConfigFromFileStory012Extra:
    """Additional tests for backward-compatible JSON config loading not covered elsewhere."""

    def _write_config(self, tmp_path: Path, data: dict) -> Path:
        """Write a sweep config JSON."""
        config_file = tmp_path / "sweep.json"
        config_file.write_text(json.dumps(data))
        return config_file

    def test_loads_paper_ids_key(self, tmp_path: Path):
        """Test that JSON config with 'paper_ids' key is loaded correctly."""
        config_file = self._write_config(
            tmp_path,
            {
                "compositions": [
                    {
                        "include_researcher": True,
                        "include_analyst": False,
                        "include_synthesiser": False,
                    }
                ],
                "repetitions": 1,
                "paper_ids": ["1105.1072"],
                "output_dir": str(tmp_path / "results"),
            },
        )
        config = _load_config_from_file(config_file)
        assert config is not None
        assert config.paper_ids == ["1105.1072"]

    def test_paper_numbers_key_returns_none(self, tmp_path: Path):
        """Test that old 'paper_numbers' key in JSON is rejected (legacy key removed)."""
        config_file = self._write_config(
            tmp_path,
            {
                "compositions": [
                    {
                        "include_researcher": True,
                        "include_analyst": False,
                        "include_synthesiser": False,
                    }
                ],
                "repetitions": 1,
                "paper_numbers": ["1", "2"],
                "output_dir": str(tmp_path / "results"),
            },
        )
        config = _load_config_from_file(config_file)
        # Legacy key removed: missing 'paper_ids' returns None
        assert config is None
