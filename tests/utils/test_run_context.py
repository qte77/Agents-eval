"""Tests for RunContext per-run directory infrastructure.

Verifies RunContext dataclass fields, directory creation, metadata.json contents,
and path helper methods (AC1-AC5).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from app.utils.run_context import RunContext


class TestRunContextDataclass:
    """Tests for RunContext dataclass fields (AC1)."""

    def test_has_required_fields(self, tmp_path: Path) -> None:
        """RunContext has all required fields: engine_type, paper_id, execution_id, start_time, run_dir."""
        from app.utils.run_context import RunContext

        start_time = datetime(2026, 2, 27, 10, 0, 0)
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        ctx = RunContext(
            engine_type="mas",
            paper_id="paper_001",
            execution_id="exec-1234-5678",
            start_time=start_time,
            run_dir=run_dir,
        )

        assert ctx.engine_type == "mas"
        assert ctx.paper_id == "paper_001"
        assert ctx.execution_id == "exec-1234-5678"
        assert ctx.start_time == start_time
        assert ctx.run_dir == run_dir


class TestRunContextCreate:
    """Tests for RunContext.create() factory (AC2, AC3)."""

    def test_creates_directory(self, tmp_path: Path) -> None:
        """RunContext.create() creates the run directory under output/runs/."""
        from app.utils.run_context import RunContext

        with patch("app.utils.run_context.OUTPUT_BASE", tmp_path / "output"):
            ctx = RunContext.create(
                engine_type="mas",
                paper_id="paper_001",
                execution_id="exec-1234-5678abcd",
            )

        assert ctx.run_dir.exists()
        assert ctx.run_dir.is_dir()

    def test_directory_name_pattern(self, tmp_path: Path) -> None:
        """Directory name follows {YYYYMMDD_HHMMSS}_{engine}_{paper_id}_{exec_id_8} pattern."""
        from app.utils.run_context import RunContext

        fixed_time = datetime(2026, 2, 27, 10, 30, 0)
        with (
            patch("app.utils.run_context.OUTPUT_BASE", tmp_path / "output"),
            patch("app.utils.run_context.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = fixed_time
            mock_dt.utcnow = datetime.utcnow
            ctx = RunContext.create(
                engine_type="mas",
                paper_id="paper_001",
                execution_id="exec-1234-5678abcd",
            )

        dir_name = ctx.run_dir.name
        assert dir_name.startswith("20260227_103000")
        assert "mas" in dir_name
        assert "paper_001" in dir_name
        # First 8 chars of execution_id
        assert "exec-123" in dir_name

    def test_creates_metadata_json(self, tmp_path: Path) -> None:
        """RunContext.create() writes metadata.json to run_dir (AC3)."""
        from app.utils.run_context import RunContext

        with patch("app.utils.run_context.OUTPUT_BASE", tmp_path / "output"):
            ctx = RunContext.create(
                engine_type="mas",
                paper_id="paper_001",
                execution_id="exec-1234-5678abcd",
            )

        metadata_file = ctx.run_dir / "metadata.json"
        assert metadata_file.exists()

    def test_metadata_json_contents(self, tmp_path: Path) -> None:
        """metadata.json contains engine_type, paper_id, execution_id, start_time (ISO) (AC3)."""
        from app.utils.run_context import RunContext

        with patch("app.utils.run_context.OUTPUT_BASE", tmp_path / "output"):
            ctx = RunContext.create(
                engine_type="cc_solo",
                paper_id="paper_002",
                execution_id="abcd-efgh-ijkl",
            )

        metadata_file = ctx.run_dir / "metadata.json"
        data = json.loads(metadata_file.read_text())

        assert data["engine_type"] == "cc_solo"
        assert data["paper_id"] == "paper_002"
        assert data["execution_id"] == "abcd-efgh-ijkl"
        # start_time must be ISO format string
        assert isinstance(data["start_time"], str)
        # Parse back to verify it's valid ISO
        datetime.fromisoformat(data["start_time"])

    def test_metadata_json_with_cli_args(self, tmp_path: Path) -> None:
        """metadata.json includes cli_args when provided (AC3)."""
        from app.utils.run_context import RunContext

        cli_args = {"provider": "github", "skip_eval": False}
        with patch("app.utils.run_context.OUTPUT_BASE", tmp_path / "output"):
            ctx = RunContext.create(
                engine_type="mas",
                paper_id="paper_003",
                execution_id="exec-9999",
                cli_args=cli_args,
            )

        metadata_file = ctx.run_dir / "metadata.json"
        data = json.loads(metadata_file.read_text())
        assert data["cli_args"] == cli_args

    def test_metadata_json_without_cli_args(self, tmp_path: Path) -> None:
        """metadata.json cli_args is None or absent when not provided (AC3)."""
        from app.utils.run_context import RunContext

        with patch("app.utils.run_context.OUTPUT_BASE", tmp_path / "output"):
            ctx = RunContext.create(
                engine_type="mas",
                paper_id="paper_004",
                execution_id="exec-0000",
            )

        metadata_file = ctx.run_dir / "metadata.json"
        data = json.loads(metadata_file.read_text())
        # cli_args may be absent or None
        assert data.get("cli_args") is None

    def test_run_dir_nested_under_runs(self, tmp_path: Path) -> None:
        """run_dir is nested under output/runs/ (AC2)."""
        from app.utils.run_context import RunContext

        output_base = tmp_path / "output"
        with patch("app.utils.run_context.OUTPUT_BASE", output_base):
            ctx = RunContext.create(
                engine_type="mas",
                paper_id="paper_001",
                execution_id="exec-1234-5678",
            )

        runs_dir = output_base / "runs"
        assert ctx.run_dir.parent == runs_dir


class TestRunContextPathHelpers:
    """Tests for path helper methods (AC4)."""

    @pytest.fixture
    def mas_context(self, tmp_path: Path) -> RunContext:
        """Create a MAS RunContext for testing."""
        from app.utils.run_context import RunContext

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        return RunContext(
            engine_type="mas",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=datetime(2026, 2, 27),
            run_dir=run_dir,
        )

    @pytest.fixture
    def cc_solo_context(self, tmp_path: Path) -> RunContext:
        """Create a CC solo RunContext for testing."""
        from app.utils.run_context import RunContext

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        return RunContext(
            engine_type="cc_solo",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=datetime(2026, 2, 27),
            run_dir=run_dir,
        )

    @pytest.fixture
    def cc_teams_context(self, tmp_path: Path) -> RunContext:
        """Create a CC teams RunContext for testing."""
        from app.utils.run_context import RunContext

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        return RunContext(
            engine_type="cc_teams",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=datetime(2026, 2, 27),
            run_dir=run_dir,
        )

    def test_stream_path_mas_is_json(self, mas_context: RunContext) -> None:
        """stream_path for MAS engine returns stream.json (AC4)."""
        assert mas_context.stream_path.name == "stream.json"
        assert mas_context.stream_path.parent == mas_context.run_dir

    def test_stream_path_cc_solo_is_jsonl(self, cc_solo_context: RunContext) -> None:
        """stream_path for cc_solo engine returns stream.jsonl (AC4)."""
        assert cc_solo_context.stream_path.name == "stream.jsonl"

    def test_stream_path_cc_teams_is_jsonl(self, cc_teams_context: RunContext) -> None:
        """stream_path for cc_teams engine returns stream.jsonl (AC4)."""
        assert cc_teams_context.stream_path.name == "stream.jsonl"

    def test_trace_path(self, mas_context: RunContext) -> None:
        """trace_path returns trace.jsonl in run_dir (AC4)."""
        assert mas_context.trace_path.name == "trace.jsonl"
        assert mas_context.trace_path.parent == mas_context.run_dir

    def test_review_path(self, mas_context: RunContext) -> None:
        """review_path returns review.json in run_dir (AC4)."""
        assert mas_context.review_path.name == "review.json"
        assert mas_context.review_path.parent == mas_context.run_dir

    def test_report_path(self, mas_context: RunContext) -> None:
        """report_path returns report.md in run_dir (AC4)."""
        assert mas_context.report_path.name == "report.md"
        assert mas_context.report_path.parent == mas_context.run_dir

    def test_evaluation_path(self, mas_context: RunContext) -> None:
        """evaluation_path returns evaluation.json in run_dir (AC4)."""
        assert mas_context.evaluation_path.name == "evaluation.json"
        assert mas_context.evaluation_path.parent == mas_context.run_dir


class TestConfigConstants:
    """Tests for config constant changes (AC5, AC6, AC7, AC8)."""

    def test_output_path_constant_exists(self) -> None:
        """OUTPUT_PATH constant exists in config_app (AC5)."""
        from app.config.config_app import OUTPUT_PATH

        assert OUTPUT_PATH == "output"

    def test_logs_path_unchanged(self) -> None:
        """LOGS_PATH and LOGS_BASE_PATH remain unchanged (AC7)."""
        from app.config.config_app import LOGS_BASE_PATH, LOGS_PATH

        assert LOGS_BASE_PATH == "logs/Agent_evals"
        assert LOGS_PATH == f"{LOGS_BASE_PATH}/logs"

    def test_cc_streams_path_removed(self) -> None:
        """CC_STREAMS_PATH is removed from config_app (AC6)."""
        import app.config.config_app as cfg

        assert not hasattr(cfg, "CC_STREAMS_PATH"), "CC_STREAMS_PATH should be removed"

    def test_mas_reviews_path_removed(self) -> None:
        """MAS_REVIEWS_PATH is removed from config_app (AC6)."""
        import app.config.config_app as cfg

        assert not hasattr(cfg, "MAS_REVIEWS_PATH"), "MAS_REVIEWS_PATH should be removed"

    def test_results_path_removed(self) -> None:
        """RESULTS_PATH is removed from config_app (AC6)."""
        import app.config.config_app as cfg

        assert not hasattr(cfg, "RESULTS_PATH"), "RESULTS_PATH should be removed"

    def test_judge_settings_trace_storage_path_default(self) -> None:
        """JudgeSettings.trace_storage_path default is output/runs (AC8)."""
        from app.config.judge_settings import JudgeSettings

        settings = JudgeSettings()
        assert settings.trace_storage_path == "output/runs"
