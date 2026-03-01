"""Smoke test: CLI report picks up run_context from result dict.

Verifies that _maybe_generate_report uses run_context.report_path
when run_context is present in the result dict (Phase 4 wiring).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch


class TestReportRunContext:
    """Tests for _maybe_generate_report using run_context."""

    def test_uses_run_context_report_path(self, tmp_path: Path) -> None:
        """_maybe_generate_report writes to run_context.report_path when present."""
        from app.utils.run_context import RunContext

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="e1",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=run_dir,
        )

        mock_composite = MagicMock()
        result_dict = {
            "composite_result": mock_composite,
            "run_context": ctx,
        }

        with (
            patch("app.reports.suggestion_engine.SuggestionEngine") as mock_engine_cls,
            patch("app.reports.report_generator.generate_report", return_value="# Report"),
            patch("app.reports.report_generator.save_report") as mock_save,
        ):
            mock_engine = MagicMock()
            mock_engine.generate.return_value = []
            mock_engine_cls.return_value = mock_engine

            from run_cli import _maybe_generate_report

            _maybe_generate_report(result_dict, no_llm_suggestions=False)

        mock_save.assert_called_once_with("# Report", ctx.report_path)

    def test_falls_back_without_run_context(self, tmp_path: Path) -> None:
        """_maybe_generate_report uses output/reports/ when no run_context."""
        mock_composite = MagicMock()
        result_dict = {
            "composite_result": mock_composite,
        }

        with (
            patch("app.reports.suggestion_engine.SuggestionEngine") as mock_engine_cls,
            patch("app.reports.report_generator.generate_report", return_value="# Report"),
            patch("app.reports.report_generator.save_report") as mock_save,
        ):
            mock_engine = MagicMock()
            mock_engine.generate.return_value = []
            mock_engine_cls.return_value = mock_engine

            from run_cli import _maybe_generate_report

            _maybe_generate_report(result_dict, no_llm_suggestions=False)

        # Verify save_report was called with a path under output/reports/
        call_args = mock_save.call_args
        output_path = call_args[0][1]
        assert "output" in str(output_path)
        assert "reports" in str(output_path)
