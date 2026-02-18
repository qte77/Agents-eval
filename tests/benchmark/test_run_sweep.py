"""Tests for run_sweep CLI provider threading.

Verifies --provider flag reaches SweepConfig through both CLI args and JSON file paths.
"""

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from app.config.config_app import CHAT_DEFAULT_PROVIDER
from run_sweep import _build_config_from_args, _load_config_from_file, parse_args


class TestParseArgsProvider:
    """Tests for --provider CLI argument parsing."""

    def test_provider_flag_sets_provider(self):
        """Test that --provider flag value reaches the parsed namespace."""
        with patch.object(
            sys, "argv", ["run_sweep.py", "--paper-numbers=1", "--provider=cerebras"]
        ):
            args = parse_args()

        assert args.provider == "cerebras"


class TestBuildConfigFromArgs:
    """Tests for _build_config_from_args() provider threading."""

    def test_provider_threads_to_sweep_config(self, tmp_path: Path):
        """Test that the provider from CLI args is set on SweepConfig."""
        args = argparse.Namespace(
            paper_numbers="1",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            provider="cerebras",
            engine="mas",
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
            "paper_numbers": [1],
            "output_dir": str(tmp_path / "results"),
        }
        config_file = tmp_path / "sweep.json"
        config_file.write_text(json.dumps({**base, **extra}))
        return config_file

    def test_reads_provider_from_json(self, tmp_path: Path):
        """Test that 'provider' key in config JSON is used as chat_provider."""
        config_file = self._write_config(tmp_path, {"provider": "cerebras"})

        config = _load_config_from_file(config_file)

        assert config is not None
        assert config.chat_provider == "cerebras"

    def test_falls_back_to_default_when_provider_absent(self, tmp_path: Path):
        """Test that missing 'provider' key falls back to CHAT_DEFAULT_PROVIDER."""
        config_file = self._write_config(tmp_path, {})

        config = _load_config_from_file(config_file)

        assert config is not None
        assert config.chat_provider == CHAT_DEFAULT_PROVIDER


class TestStory013EngineFlagInRunSweep:
    """Tests for STORY-013: --engine flag in run_sweep and removal of --cc-baseline."""

    def test_engine_flag_accepted_with_mas(self):
        """Test that --engine=mas is accepted by run_sweep parse_args."""
        with patch.object(
            sys, "argv", ["run_sweep.py", "--paper-numbers=1", "--engine=mas"]
        ):
            args = parse_args()

        assert args.engine == "mas"

    def test_engine_flag_accepted_with_cc(self):
        """Test that --engine=cc is accepted by run_sweep parse_args."""
        with patch.object(
            sys, "argv", ["run_sweep.py", "--paper-numbers=1", "--engine=cc"]
        ):
            args = parse_args()

        assert args.engine == "cc"

    def test_engine_defaults_to_mas(self):
        """Test that --engine defaults to 'mas' when not specified."""
        with patch.object(sys, "argv", ["run_sweep.py", "--paper-numbers=1"]):
            args = parse_args()

        assert args.engine == "mas"

    def test_cc_baseline_flag_no_longer_accepted(self):
        """Test that --cc-baseline is rejected (removed in STORY-013)."""
        with patch.object(
            sys, "argv", ["run_sweep.py", "--paper-numbers=1", "--cc-baseline"]
        ):
            with pytest.raises(SystemExit):
                parse_args()

    def test_build_config_from_args_uses_engine_not_cc_baseline(self, tmp_path: Path):
        """Test _build_config_from_args uses engine field not cc_baseline_enabled."""
        args = argparse.Namespace(
            paper_numbers="1",
            repetitions=1,
            output_dir=tmp_path / "results",
            all_compositions=False,
            provider="cerebras",
            engine="mas",
        )

        config = _build_config_from_args(args)

        assert config is not None
        assert config.engine == "mas"
        assert not hasattr(config, "cc_baseline_enabled")
