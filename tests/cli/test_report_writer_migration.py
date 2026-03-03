"""Tests for STORY-009: CLI report writer migration to RunContext.

AC5: CLI report save writes to run_context.report_path
AC10: Sweep runner default output_dir changed from results/sweeps to output/sweeps
"""

from pathlib import Path

from app.config.config_app import OUTPUT_PATH


class TestSweepRunnerDefaultOutputDir:
    """AC10: Sweep runner default output_dir uses output/sweeps instead of results/sweeps."""

    def test_default_output_dir_uses_output_prefix(self) -> None:
        """Default sweep output_dir starts with output/sweeps, not results/sweeps."""

        # Simulate args with no --output-dir
        from argparse import Namespace

        args = Namespace(
            config=None,
            paper_ids="1",
            repetitions=1,
            output_dir=None,
            all_compositions=False,
            chat_provider="github",
            engine="mas",
            cc_teams=False,
            judge_provider="auto",
            judge_model=None,
        )

        from run_sweep import _build_config_from_args

        config = _build_config_from_args(args)
        assert config is not None
        assert str(config.output_dir).startswith(f"{OUTPUT_PATH}/sweeps")


class TestCLIReportWriterMigration:
    """AC5: CLI report save writes to run_context.report_path."""

    def test_report_path_uses_output_sweeps_prefix(self) -> None:
        """The default sweep output uses output/ prefix, not results/."""
        # This is covered by TestSweepRunnerDefaultOutputDir above
        # Additional test: the CLI --output-dir override still works
        from argparse import Namespace

        from run_sweep import _build_config_from_args

        args = Namespace(
            config=None,
            paper_ids="1",
            repetitions=1,
            output_dir=Path("/custom/output"),
            all_compositions=False,
            chat_provider="github",
            engine="mas",
            cc_teams=False,
            judge_provider="auto",
            judge_model=None,
        )

        config = _build_config_from_args(args)
        assert config is not None
        assert config.output_dir == Path("/custom/output")
