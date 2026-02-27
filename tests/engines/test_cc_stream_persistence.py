"""Tests for CC stream persistence — STORY-007.

Covers:
- run_cc_teams writes raw JSONL stream incrementally to CC_STREAMS_PATH
- run_cc_solo writes raw JSON response to CC_STREAMS_PATH after completion
- Persisted files are registered with ArtifactRegistry
- CC_STREAMS_PATH constant exists in config_app
- parse_stream_json behaviour is unchanged (side-effect only)
- Output directory is created lazily on first write
- Filename uses execution_id from parsed result; falls back to timestamp-only
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_popen(lines: list[str]) -> MagicMock:
    """Return a mock Popen context manager yielding ``lines`` from stdout."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = iter(lines)
    mock_proc.wait.return_value = 0
    mock_proc.__enter__ = MagicMock(return_value=mock_proc)
    mock_proc.__exit__ = MagicMock(return_value=False)
    return mock_proc


# ---------------------------------------------------------------------------
# Config constant
# ---------------------------------------------------------------------------


class TestCCStreamsPathConfig:
    """CC_STREAMS_PATH constant exists in config_app and derives from LOGS_BASE_PATH."""

    def test_cc_streams_path_exists(self):
        """config_app exposes CC_STREAMS_PATH constant."""
        from app.config.config_app import CC_STREAMS_PATH

        assert CC_STREAMS_PATH is not None

    def test_cc_streams_path_under_logs_base_path(self):
        """CC_STREAMS_PATH is rooted under LOGS_BASE_PATH."""
        from app.config.config_app import CC_STREAMS_PATH, LOGS_BASE_PATH

        assert CC_STREAMS_PATH.startswith(LOGS_BASE_PATH)

    def test_cc_streams_path_ends_with_cc_streams(self):
        """CC_STREAMS_PATH ends with the 'cc_streams' segment."""
        from app.config.config_app import CC_STREAMS_PATH

        assert CC_STREAMS_PATH.endswith("cc_streams")


# ---------------------------------------------------------------------------
# Solo persistence
# ---------------------------------------------------------------------------


class TestRunCCSoloPersistence:
    """run_cc_solo writes raw JSON to a .json file in CC_STREAMS_PATH."""

    def test_solo_writes_raw_json_to_file(self, tmp_path):
        """run_cc_solo writes stdout JSON to cc_solo_{execution_id}_{ts}.json."""
        from app.engines.cc_engine import run_cc_solo

        raw = {"execution_id": "solo-abc", "result": "Nice paper"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        written_files: list[Path] = []

        def capture_open(path, mode="r", **kw):
            p = Path(path)
            written_files.append(p)
            return open(str(tmp_path / p.name), mode, **kw)

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_solo("test query")

        # At least one file was written to the streams path
        # (verify by checking artifact registry was called)
        mock_reg.return_value.register.assert_called_once()

    def test_solo_stream_file_contains_raw_json(self, tmp_path):
        """The .json file written by run_cc_solo contains the original stdout bytes."""
        from app.engines.cc_engine import run_cc_solo

        raw = {"execution_id": "solo-xyz", "result": "Summary here"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_solo("test query")

        # Find the written file
        files = list(tmp_path.glob("cc_solo_*.json"))
        assert len(files) == 1, f"Expected 1 cc_solo_*.json, found {files}"
        content = files[0].read_text()
        assert "solo-xyz" in content

    def test_solo_filename_includes_execution_id(self, tmp_path):
        """Persisted solo filename contains the execution_id."""
        from app.engines.cc_engine import run_cc_solo

        raw = {"execution_id": "my-exec-id-123", "result": "ok"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_solo("test query")

        files = list(tmp_path.glob("cc_solo_*my-exec-id-123*.json"))
        assert len(files) == 1, (
            f"Expected filename with execution_id, found {list(tmp_path.iterdir())}"
        )

    def test_solo_creates_output_directory_lazily(self, tmp_path):
        """run_cc_solo creates CC_STREAMS_PATH if it does not exist."""
        from app.engines.cc_engine import run_cc_solo

        streams_dir = tmp_path / "cc_streams"
        assert not streams_dir.exists()

        raw = {"execution_id": "solo-lazy", "result": "done"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(streams_dir)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_solo("test query")

        assert streams_dir.exists()

    def test_solo_registers_artifact_with_registry(self, tmp_path):
        """run_cc_solo registers the written file with ArtifactRegistry."""
        from app.engines.cc_engine import run_cc_solo

        raw = {"execution_id": "solo-reg", "result": "done"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_registry = MagicMock()
            mock_reg.return_value = mock_registry
            run_cc_solo("test query")

        mock_registry.register.assert_called_once()
        label, path = mock_registry.register.call_args[0]
        assert "solo" in label.lower() or "stream" in label.lower() or "cc" in label.lower()
        assert str(path).endswith(".json")

    def test_solo_no_write_on_failure(self, tmp_path):
        """run_cc_solo does not write a stream file when the process fails."""
        from app.engines.cc_engine import run_cc_solo

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error"
        mock_result.stdout = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
        ):
            with pytest.raises(RuntimeError):
                run_cc_solo("test query")

        files = list(tmp_path.glob("cc_solo_*.json"))
        assert len(files) == 0

    def test_solo_fallback_filename_when_execution_id_unknown(self, tmp_path):
        """When execution_id is 'unknown', solo filename still uses a timestamp."""
        from app.engines.cc_engine import run_cc_solo

        raw = {"some_key": "some_val"}  # no execution_id / session_id
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw)
        mock_result.stderr = ""

        with (
            patch("subprocess.run", return_value=mock_result),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_solo("test query")

        files = list(tmp_path.glob("cc_solo_*.json"))
        assert len(files) == 1


# ---------------------------------------------------------------------------
# Teams persistence
# ---------------------------------------------------------------------------


class TestRunCCTeamsPersistence:
    """run_cc_teams writes raw JSONL stream incrementally to CC_STREAMS_PATH."""

    def test_teams_writes_jsonl_file(self, tmp_path):
        """run_cc_teams writes a .jsonl file to CC_STREAMS_PATH."""
        from app.engines.cc_engine import run_cc_teams

        lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "sess-teams-001"}),
            json.dumps({"type": "result", "num_turns": 3}),
        ]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_teams("test query")

        files = list(tmp_path.glob("cc_teams_*.jsonl"))
        assert len(files) == 1, f"Expected 1 cc_teams_*.jsonl, found {files}"

    def test_teams_jsonl_file_contains_all_lines(self, tmp_path):
        """All JSONL lines from stdout are persisted to the file."""
        from app.engines.cc_engine import run_cc_teams

        lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "sess-abc"}),
            json.dumps({"type": "TeamCreate", "team_name": "review-team"}),
            json.dumps({"type": "result", "num_turns": 5}),
        ]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_teams("test query")

        files = list(tmp_path.glob("cc_teams_*.jsonl"))
        assert len(files) == 1
        written_lines = [line for line in files[0].read_text().splitlines() if line.strip()]
        assert len(written_lines) == 3

    def test_teams_filename_includes_execution_id(self, tmp_path):
        """Persisted teams filename contains the execution_id (session_id from init)."""
        from app.engines.cc_engine import run_cc_teams

        lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "my-team-exec-999"}),
            json.dumps({"type": "result", "num_turns": 2}),
        ]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_teams("test query")

        files = list(tmp_path.glob("cc_teams_*my-team-exec-999*.jsonl"))
        assert len(files) == 1, (
            f"Expected filename with execution_id, found {list(tmp_path.iterdir())}"
        )

    def test_teams_creates_output_directory_lazily(self, tmp_path):
        """run_cc_teams creates CC_STREAMS_PATH if it does not exist."""
        from app.engines.cc_engine import run_cc_teams

        streams_dir = tmp_path / "cc_streams"
        assert not streams_dir.exists()

        lines = [json.dumps({"type": "result", "num_turns": 1})]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(streams_dir)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_teams("test query")

        assert streams_dir.exists()

    def test_teams_registers_artifact_with_registry(self, tmp_path):
        """run_cc_teams registers the written file with ArtifactRegistry."""
        from app.engines.cc_engine import run_cc_teams

        lines = [json.dumps({"type": "result", "num_turns": 1})]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_registry = MagicMock()
            mock_reg.return_value = mock_registry
            run_cc_teams("test query")

        mock_registry.register.assert_called_once()
        label, path = mock_registry.register.call_args[0]
        assert "team" in label.lower() or "stream" in label.lower() or "cc" in label.lower()
        assert str(path).endswith(".jsonl")

    def test_teams_parse_stream_json_behavior_unchanged(self, tmp_path):
        """Persistence is a side-effect; parse_stream_json result is identical."""
        from app.engines.cc_engine import run_cc_teams

        lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "sess-unchanged"}),
            json.dumps(
                {"type": "system", "subtype": "task_started", "agent_id": "agent-1"}
            ),
            json.dumps({"type": "result", "num_turns": 4, "total_cost_usd": 0.03}),
        ]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            result = run_cc_teams("test query")

        assert result.execution_id == "sess-unchanged"
        assert result.output_data.get("num_turns") == 4
        assert len(result.team_artifacts) == 1
        assert result.team_artifacts[0]["agent_id"] == "agent-1"

    def test_teams_incremental_write_not_buffered(self, tmp_path):
        """Stream is written line-by-line (tee pattern), not buffered until end."""
        from app.engines.cc_engine import run_cc_teams

        original_lines = [
            json.dumps({"type": "system", "subtype": "init", "session_id": "sess-tee"}),
            json.dumps({"type": "result", "num_turns": 2}),
        ]

        # We can't easily verify incremental writes without hooking into the file,
        # but we can verify the file exists and contains content after each line.
        # Instead: verify the file is opened before process completion by checking
        # that the JSONL file exists before proc.wait() returns.
        wait_called_before_file_exists: list[bool] = []

        class ProcMock:
            returncode = 0
            stdout = iter(original_lines)
            stderr = iter([])

            def wait(self):
                # Check if file already exists when wait() is called
                files = list(tmp_path.glob("cc_teams_*.jsonl"))
                wait_called_before_file_exists.append(len(files) > 0)
                return 0

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with (
            patch("subprocess.Popen", return_value=ProcMock()),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_teams("test query")

        # The file should have been created before proc.wait() was called,
        # meaning writes happened during iteration (incremental), not after.
        assert wait_called_before_file_exists == [True], (
            "JSONL file should exist before proc.wait() — writes must be incremental"
        )

    def test_teams_fallback_filename_when_execution_id_unknown(self, tmp_path):
        """When no session_id in stream, teams filename still has a timestamp."""
        from app.engines.cc_engine import run_cc_teams

        lines = [json.dumps({"type": "result", "num_turns": 1})]
        mock_proc = _make_mock_popen(lines)

        with (
            patch("subprocess.Popen", return_value=mock_proc),
            patch("app.engines.cc_engine.CC_STREAMS_PATH", str(tmp_path)),
            patch("app.engines.cc_engine.get_artifact_registry") as mock_reg,
        ):
            mock_reg.return_value = MagicMock()
            run_cc_teams("test query")

        files = list(tmp_path.glob("cc_teams_*.jsonl"))
        assert len(files) == 1
