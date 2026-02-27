"""Tests for STORY-009: CC engine writer migration to RunContext.

AC1: run_cc_solo writes stream to run_context.stream_path
AC2: run_cc_teams writes stream to run_context.stream_path
AC8: No code references CC_STREAMS_PATH for file writes
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.utils.run_context import RunContext


class TestRunCCSoloWritesToRunContext:
    """AC1: run_cc_solo writes stream to run_context.stream_path."""

    def test_solo_accepts_run_context_parameter(self, tmp_path: Path) -> None:
        """run_cc_solo accepts an optional run_context parameter."""
        from app.engines.cc_engine import run_cc_solo

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="cc_solo",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=__import__("datetime").datetime.now(),
            run_dir=run_dir,
        )

        raw = {"execution_id": "exec-solo-001", "result": "Good paper"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = run_cc_solo("test query", run_context=ctx)

        assert result.execution_id == "exec-solo-001"

    def test_solo_writes_to_stream_path(self, tmp_path: Path) -> None:
        """run_cc_solo writes stdout JSON to run_context.stream_path when provided."""
        from app.engines.cc_engine import run_cc_solo

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="cc_solo",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=__import__("datetime").datetime.now(),
            run_dir=run_dir,
        )

        raw = {"execution_id": "exec-solo-001", "result": "Good paper"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            run_cc_solo("test query", run_context=ctx)

        assert ctx.stream_path.exists()
        content = ctx.stream_path.read_text()
        assert "exec-solo-001" in content

    def test_solo_registers_artifact_at_stream_path(self, tmp_path: Path) -> None:
        """run_cc_solo registers the stream_path artifact when run_context provided."""
        from app.engines.cc_engine import run_cc_solo

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="cc_solo",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=__import__("datetime").datetime.now(),
            run_dir=run_dir,
        )

        raw = {"execution_id": "exec-solo-001", "result": "done"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_registry = MagicMock()
            mock_reg.return_value = mock_registry
            run_cc_solo("test query", run_context=ctx)

        mock_registry.register.assert_called_once()
        _, registered_path = mock_registry.register.call_args[0]
        assert registered_path == ctx.stream_path


class TestRunCCTeamsWritesToRunContext:
    """AC2: run_cc_teams writes stream to run_context.stream_path."""

    def _make_mock_popen(self, lines: list[str]) -> MagicMock:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = iter(lines)
        mock_proc.wait.return_value = 0
        mock_proc.__enter__ = MagicMock(return_value=mock_proc)
        mock_proc.__exit__ = MagicMock(return_value=False)
        return mock_proc

    def test_teams_accepts_run_context_parameter(self, tmp_path: Path) -> None:
        """run_cc_teams accepts an optional run_context parameter."""
        from app.engines.cc_engine import run_cc_teams

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="cc_teams",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=__import__("datetime").datetime.now(),
            run_dir=run_dir,
        )

        lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "sess-001"}),
            json.dumps({"type": "result", "num_turns": 3}),
        ]
        mock_proc = self._make_mock_popen(lines)

        with patch("subprocess.Popen", return_value=mock_proc):
            result = run_cc_teams("test query", run_context=ctx)

        assert result.execution_id == "sess-001"

    def test_teams_writes_to_stream_path(self, tmp_path: Path) -> None:
        """run_cc_teams writes JSONL stream to run_context.stream_path when provided."""
        from app.engines.cc_engine import run_cc_teams

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="cc_teams",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=__import__("datetime").datetime.now(),
            run_dir=run_dir,
        )

        lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "sess-teams"}),
            json.dumps({"type": "result", "num_turns": 5}),
        ]
        mock_proc = self._make_mock_popen(lines)

        with patch("subprocess.Popen", return_value=mock_proc):
            run_cc_teams("test query", run_context=ctx)

        assert ctx.stream_path.exists()
        written_lines = [l for l in ctx.stream_path.read_text().splitlines() if l.strip()]
        assert len(written_lines) == 2

    def test_teams_registers_artifact_at_stream_path(self, tmp_path: Path) -> None:
        """run_cc_teams registers the stream_path artifact when run_context provided."""
        from app.engines.cc_engine import run_cc_teams

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="cc_teams",
            paper_id="paper_001",
            execution_id="exec-1234",
            start_time=__import__("datetime").datetime.now(),
            run_dir=run_dir,
        )

        lines = [json.dumps({"type": "result", "num_turns": 1})]
        mock_proc = self._make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_registry = MagicMock()
            mock_reg.return_value = mock_registry
            run_cc_teams("test query", run_context=ctx)

        mock_registry.register.assert_called_once()
        _, registered_path = mock_registry.register.call_args[0]
        assert registered_path == ctx.stream_path


class TestCCStreamsPathRemoved:
    """AC8: No code references CC_STREAMS_PATH for file writes after migration."""

    def test_cc_engine_no_longer_uses_cc_streams_path_for_writes(self) -> None:
        """CC_STREAMS_PATH constant is removed from cc_engine.py."""
        import app.engines.cc_engine as mod

        assert not hasattr(mod, "CC_STREAMS_PATH"), (
            "CC_STREAMS_PATH should be removed from cc_engine.py"
        )
