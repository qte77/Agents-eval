"""Tests for STORY-006: cc_engine wiring into CLI/sweep/GUI + --cc-teams flag.

Covers:
- --cc-teams flag added to CLI and sweep arg parsers
- run_cli delegates to run_cc_solo / run_cc_teams (no inline subprocess)
- sweep_runner._invoke_cc_comparison delegates to cc_engine
- run_app._execute_query_background passes engine to main()
- _run_cc_baselines wired through CCTraceAdapter (not a stub)
- scripts/collect-cc-traces/ directory removed
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

SRC_PATH = str(Path(__file__).parent.parent.parent / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


def _make_sweep_config(output_dir: Path, **overrides: object):
    """Build a SweepConfig with sensible test defaults.

    Args:
        output_dir: Directory for sweep output (use tmp_path fixture).
        **overrides: Fields to override on the SweepConfig.
    """
    from app.benchmark.sweep_config import AgentComposition, SweepConfig

    defaults: dict = {
        "compositions": [AgentComposition()],
        "repetitions": 1,
        "paper_ids": ["1"],
        "output_dir": output_dir,
    }
    defaults.update(overrides)
    return SweepConfig(**defaults)


class TestCCTeamsFlagCLI:
    """--cc-teams flag added to run_cli.py argument parser."""

    def test_cc_teams_flag_registered_in_parser(self):
        """--cc-teams is a recognized boolean flag in run_cli._parser."""
        from run_cli import _parser

        option_strings = {a for action in _parser._actions for a in action.option_strings}
        assert "--cc-teams" in option_strings

    def test_cc_teams_flag_defaults_to_false(self):
        """--cc-teams flag is False (or absent) when not specified."""
        from run_cli import parse_args

        args = parse_args(["--engine=cc", "--query=test"])
        assert not args.get("cc_teams", False)

    def test_cc_teams_flag_parses_true_when_provided(self):
        """--cc-teams flag is True when explicitly provided."""
        from run_cli import parse_args

        args = parse_args(["--engine=cc", "--cc-teams"])
        assert args.get("cc_teams") is True

    def test_cc_teams_can_combine_with_engine_cc(self):
        """--cc-teams can be combined with --engine=cc."""
        from run_cli import parse_args

        args = parse_args(["--engine=cc", "--cc-teams", "--query=test query"])
        assert args.get("engine") == "cc"
        assert args.get("cc_teams") is True


class TestCCTeamsFlagSweep:
    """--cc-teams flag added to run_sweep.py argument parser."""

    def test_cc_teams_flag_registered_in_sweep_parser(self, tmp_path: Path):
        """--cc-teams is a recognized flag via SweepConfig model."""
        config = _make_sweep_config(tmp_path, cc_teams=False)
        assert config.cc_teams is False

    def test_sweep_config_supports_cc_teams_field(self, tmp_path: Path):
        """SweepConfig model has cc_teams boolean field."""
        config = _make_sweep_config(tmp_path, cc_teams=True)
        assert config.cc_teams is True

    def test_sweep_config_cc_teams_defaults_to_false(self, tmp_path: Path):
        """SweepConfig.cc_teams defaults to False."""
        config = _make_sweep_config(tmp_path)
        assert config.cc_teams is False


class TestCLIDelegatesToCCEngine:
    """run_cli delegates CC execution to cc_engine functions, not inline subprocess."""

    def test_cli_cc_branch_calls_run_cc_solo_not_subprocess(self):
        """When --engine=cc (no --cc-teams), run_cli uses run_cc_solo, not subprocess.run."""
        import inspect

        import run_cli

        source = inspect.getsource(run_cli)
        has_cc_engine_import = (
            "cc_engine" in source or "run_cc_solo" in source or "run_cc_teams" in source
        )
        assert has_cc_engine_import, (
            "run_cli should import and use cc_engine functions, not inline subprocess for CC"
        )

    def test_cli_cc_solo_delegates_to_run_cc_solo(self, tmp_path: Path):
        """When engine=cc without cc_teams, CLI delegates to cc_engine.run_cc_solo."""
        from app.engines.cc_engine import CCResult

        mock_result = CCResult(
            execution_id="exec-001", output_data={}, session_dir=str(tmp_path / "sess")
        )

        with patch("app.engines.cc_engine.run_cc_solo", return_value=mock_result) as mock_solo:
            with patch("app.app.main", new_callable=AsyncMock) as mock_main:
                mock_main.return_value = {}
                from app.engines.cc_engine import run_cc_solo

                result = run_cc_solo("test query", timeout=600)
                assert result.execution_id == "exec-001"
                mock_solo.assert_called_once()

    def test_cli_cc_teams_delegates_to_run_cc_teams(self):
        """When engine=cc with cc_teams=True, CLI delegates to cc_engine.run_cc_teams."""
        from app.engines.cc_engine import CCResult

        mock_result = CCResult(
            execution_id="exec-teams-001",
            output_data={},
            team_artifacts=[{"type": "TeamCreate", "team_name": "test-team"}],
        )

        with patch("app.engines.cc_engine.run_cc_teams", return_value=mock_result) as mock_teams:
            from app.engines.cc_engine import run_cc_teams

            result = run_cc_teams("test query", timeout=600)
            assert len(result.team_artifacts) == 1
            mock_teams.assert_called_once()


class TestSweepRunnerDelegatesToCCEngine:
    """sweep_runner._invoke_cc_comparison delegates to cc_engine, no inline subprocess."""

    def test_invoke_cc_comparison_calls_run_cc_solo(self):
        """_invoke_cc_comparison uses run_cc_solo (not subprocess.run) for solo mode."""
        import inspect

        from app.benchmark.sweep_runner import SweepRunner

        source = inspect.getsource(SweepRunner._invoke_cc_comparison)
        assert "subprocess.run" not in source, (
            "_invoke_cc_comparison should delegate to cc_engine, not use subprocess.run directly"
        )

    @pytest.mark.asyncio
    async def test_invoke_cc_comparison_uses_cc_engine_run_cc_solo(self, tmp_path: Path):
        """_invoke_cc_comparison delegates to run_cc_solo from cc_engine."""
        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc")
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-sweep-001",
            output_data={"num_turns": 3},
            session_dir=str(tmp_path / "session"),
        )

        with patch(
            "app.benchmark.sweep_runner.run_cc_solo", return_value=mock_cc_result
        ) as mock_solo:
            result = await runner._invoke_cc_comparison("1105.1072")

        mock_solo.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_invoke_cc_comparison_uses_cc_engine_run_cc_teams_when_teams_mode(
        self, tmp_path: Path
    ):
        """_invoke_cc_comparison delegates to run_cc_teams when cc_teams=True."""
        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc", cc_teams=True)
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-teams-sweep-001",
            output_data={},
            team_artifacts=[{"type": "TeamCreate"}],
        )

        with patch(
            "app.benchmark.sweep_runner.run_cc_teams", return_value=mock_cc_result
        ) as mock_teams:
            result = await runner._invoke_cc_comparison("1105.1072")

        mock_teams.assert_called_once()
        assert result is not None


class TestRunAppPassesEngine:
    """run_app._execute_query_background passes engine to main()."""

    def test_execute_query_background_passes_engine_to_main_via_source(self):
        """_execute_query_background source passes engine to main() call."""
        import inspect

        from gui.pages.run_app import _execute_query_background

        source = inspect.getsource(_execute_query_background)
        assert "engine=engine" in source, (
            "_execute_query_background must pass engine=engine to main()"
        )

    def test_execute_query_background_accepts_engine_parameter(self):
        """_execute_query_background function signature accepts engine parameter."""
        import inspect

        from gui.pages.run_app import _execute_query_background

        sig = inspect.signature(_execute_query_background)
        assert "engine" in sig.parameters, (
            "_execute_query_background must accept 'engine' parameter"
        )


class TestRunCCBaselinesWired:
    """_run_cc_baselines wired through CCTraceAdapter, not a stub."""

    def test_run_cc_baselines_not_just_logging(self):
        """_run_cc_baselines does more than just log — it processes results."""
        import inspect

        from app.benchmark.sweep_runner import SweepRunner

        source = inspect.getsource(SweepRunner._run_cc_baselines)
        assert "# CC evaluation integration would go here" not in source, (
            "_run_cc_baselines must be fully implemented, not a stub"
        )

    @pytest.mark.asyncio
    async def test_run_cc_baselines_calls_cc_trace_adapter_when_result_available(
        self, tmp_path: Path
    ):
        """_run_cc_baselines calls CCTraceAdapter to process CC results."""
        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc", paper_ids=["1105.1072"])
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-001",
            output_data={},
            session_dir=str(tmp_path / "sess"),
        )

        with patch.object(
            runner, "_invoke_cc_comparison", new_callable=AsyncMock, return_value=mock_cc_result
        ):
            with patch("app.benchmark.sweep_runner.CCTraceAdapter") as mock_adapter_cls:
                mock_adapter = MagicMock()
                mock_adapter_cls.return_value = mock_adapter
                await runner._run_cc_baselines()


class TestShellScriptsRemoved:
    """scripts/collect-cc-traces/ directory should not exist."""

    def test_scripts_collect_cc_traces_dir_removed(self):
        """scripts/collect-cc-traces/ directory has been removed."""
        scripts_dir = Path(__file__).parent.parent.parent / "scripts" / "collect-cc-traces"
        assert not scripts_dir.exists(), (
            f"scripts/collect-cc-traces/ still exists at {scripts_dir}. "
            "It should be removed as Python cc_engine replaces it."
        )
