"""Tests for cc_engine.py — STORY-005.

Covers:
- check_cc_available: shutil.which detection
- run_cc_solo: subprocess.run with --output-format json, error handling
- run_cc_teams: subprocess.Popen with --output-format stream-json + JSONL parsing
- parse_stream_json: parses init/result/TeamCreate/Task JSONL events
- CCResult: Pydantic model structure
"""

import json
import subprocess
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest


class TestCheckCCAvailable:
    """Tests for check_cc_available()."""

    def test_returns_true_when_claude_on_path(self):
        """check_cc_available returns True when shutil.which finds claude."""
        from app.engines.cc_engine import check_cc_available

        with patch("shutil.which", return_value="/usr/local/bin/claude"):
            assert check_cc_available() is True

    def test_returns_false_when_claude_not_on_path(self):
        """check_cc_available returns False when shutil.which returns None."""
        from app.engines.cc_engine import check_cc_available

        with patch("shutil.which", return_value=None):
            assert check_cc_available() is False

    def test_checks_for_claude_binary(self):
        """check_cc_available queries shutil.which with 'claude'."""
        from app.engines.cc_engine import check_cc_available

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/claude"
            check_cc_available()
            mock_which.assert_called_once_with("claude")


class TestCCResult:
    """Tests for CCResult Pydantic model."""

    def test_ccresult_has_required_fields(self):
        """CCResult model has execution_id and output_data fields."""
        from app.engines.cc_engine import CCResult

        result = CCResult(
            execution_id="test-id",
            output_data={"result": "ok"},
        )
        assert result.execution_id == "test-id"
        assert result.output_data == {"result": "ok"}

    def test_ccresult_session_dir_optional(self):
        """CCResult.session_dir is optional (solo mode)."""
        from app.engines.cc_engine import CCResult

        result = CCResult(execution_id="test-id", output_data={})
        assert result.session_dir is None

    def test_ccresult_team_artifacts_defaults_empty(self):
        """CCResult.team_artifacts defaults to empty list (teams mode)."""
        from app.engines.cc_engine import CCResult

        result = CCResult(execution_id="test-id", output_data={})
        assert result.team_artifacts == []

    def test_ccresult_full_construction(self):
        """CCResult can be constructed with all fields."""
        from app.engines.cc_engine import CCResult

        result = CCResult(
            execution_id="exec-abc123",
            output_data={"cost": 0.01},
            session_dir="/home/user/.claude/sessions/abc",
            team_artifacts=[{"type": "TeamCreate", "team_name": "my-team"}],
        )
        assert result.execution_id == "exec-abc123"
        assert result.session_dir == "/home/user/.claude/sessions/abc"
        assert len(result.team_artifacts) == 1


class TestRunCCSolo:
    """Tests for run_cc_solo()."""

    def test_solo_success_returns_ccresult(self):
        """run_cc_solo returns CCResult on successful subprocess call."""
        from app.engines.cc_engine import CCResult, run_cc_solo

        output_data = {"execution_id": "exec-solo-001", "session_dir": "/tmp/session"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(output_data)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = run_cc_solo("test query")

        assert isinstance(result, CCResult)
        assert result.execution_id == "exec-solo-001"
        assert result.session_dir == "/tmp/session"

    def test_solo_uses_json_output_format(self):
        """run_cc_solo passes --output-format json to subprocess."""
        from app.engines.cc_engine import run_cc_solo

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"execution_id": "x"})

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            run_cc_solo("test query")

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--output-format" in cmd
        assert "json" in cmd

    def test_solo_uses_blocking_subprocess_run(self):
        """run_cc_solo uses subprocess.run (blocking), not Popen."""
        from app.engines.cc_engine import run_cc_solo

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"execution_id": "x"})

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("subprocess.Popen") as mock_popen:
                run_cc_solo("test query")

        mock_run.assert_called_once()
        mock_popen.assert_not_called()

    def test_solo_nonzero_exit_raises_runtime_error(self):
        """run_cc_solo raises RuntimeError on non-zero subprocess exit."""
        from app.engines.cc_engine import run_cc_solo

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "claude: some error"
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="CC failed"):
                run_cc_solo("test query")

    def test_solo_timeout_raises_runtime_error(self):
        """run_cc_solo raises RuntimeError on subprocess timeout."""
        from app.engines.cc_engine import run_cc_solo

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd=["claude"], timeout=600),
        ):
            with pytest.raises(RuntimeError, match="timed out"):
                run_cc_solo("test query")

    def test_solo_invalid_json_raises_value_error(self):
        """run_cc_solo raises ValueError on malformed JSON output."""
        from app.engines.cc_engine import run_cc_solo

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json {"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(ValueError, match="not valid JSON"):
                run_cc_solo("test query")

    def test_solo_respects_timeout_parameter(self):
        """run_cc_solo passes the timeout parameter to subprocess.run."""
        from app.engines.cc_engine import run_cc_solo

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"execution_id": "x"})

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            run_cc_solo("test query", timeout=300)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get("timeout") == 300

    def test_solo_output_data_populated_from_json(self):
        """run_cc_solo populates output_data from parsed JSON stdout."""
        from app.engines.cc_engine import run_cc_solo

        raw_output = {"cost_usd": 0.05, "num_turns": 3, "result": "done"}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(raw_output)

        with patch("subprocess.run", return_value=mock_result):
            result = run_cc_solo("test query")

        assert result.output_data == raw_output


class TestRunCCTeams:
    """Tests for run_cc_teams()."""

    def _make_mock_popen(self, lines: list[str]) -> MagicMock:
        """Create a mock Popen that yields the given JSONL lines from stdout."""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = iter(lines)
        mock_proc.wait.return_value = 0
        mock_proc.__enter__ = MagicMock(return_value=mock_proc)
        mock_proc.__exit__ = MagicMock(return_value=False)
        return mock_proc

    def test_teams_uses_stream_json_format(self):
        """run_cc_teams passes --output-format stream-json to Popen."""
        from app.engines.cc_engine import run_cc_teams

        mock_proc = self._make_mock_popen([])

        with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
            run_cc_teams("test query")

        call_args = mock_popen.call_args
        cmd = call_args[0][0]
        assert "--output-format" in cmd
        assert "stream-json" in cmd

    def test_teams_sets_agent_teams_env_var(self):
        """run_cc_teams sets CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 in env."""
        from app.engines.cc_engine import run_cc_teams

        mock_proc = self._make_mock_popen([])

        with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
            run_cc_teams("test query")

        call_kwargs = mock_popen.call_args[1]
        env = call_kwargs.get("env", {})
        assert env.get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS") == "1"

    def test_teams_uses_popen_not_run(self):
        """run_cc_teams uses Popen (streaming), not subprocess.run."""
        from app.engines.cc_engine import run_cc_teams

        mock_proc = self._make_mock_popen([])

        with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
            with patch("subprocess.run") as mock_run:
                run_cc_teams("test query")

        mock_popen.assert_called_once()
        mock_run.assert_not_called()

    def test_teams_returns_ccresult(self):
        """run_cc_teams returns a CCResult instance."""
        from app.engines.cc_engine import CCResult, run_cc_teams

        result_line = json.dumps(
            {"type": "result", "duration_ms": 5000, "total_cost_usd": 0.02, "num_turns": 4}
        )
        mock_proc = self._make_mock_popen([result_line])

        with patch("subprocess.Popen", return_value=mock_proc):
            result = run_cc_teams("test query")

        assert isinstance(result, CCResult)

    def test_teams_extracts_team_artifacts_from_stream(self):
        """run_cc_teams populates team_artifacts from TeamCreate events in stream."""
        from app.engines.cc_engine import run_cc_teams

        team_event = json.dumps({"type": "TeamCreate", "team_name": "eval-team"})
        mock_proc = self._make_mock_popen([team_event])

        with patch("subprocess.Popen", return_value=mock_proc):
            result = run_cc_teams("test query")

        assert any(a.get("team_name") == "eval-team" for a in result.team_artifacts)

    def test_teams_nonzero_exit_raises_runtime_error(self):
        """run_cc_teams raises RuntimeError when Popen exits with non-zero code."""
        from app.engines.cc_engine import run_cc_teams

        mock_proc = self._make_mock_popen([])
        mock_proc.returncode = 1
        mock_proc.wait.return_value = 1

        with patch("subprocess.Popen", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="CC failed"):
                run_cc_teams("test query")

    def test_teams_timeout_raises_runtime_error(self):
        """run_cc_teams raises RuntimeError on TimeoutExpired during stream read."""
        from app.engines.cc_engine import run_cc_teams

        mock_proc = MagicMock()
        mock_proc.__enter__ = MagicMock(return_value=mock_proc)
        mock_proc.__exit__ = MagicMock(return_value=False)
        mock_proc.stdout = MagicMock()
        mock_proc.stdout.__iter__ = MagicMock(
            side_effect=subprocess.TimeoutExpired(cmd=["claude"], timeout=600)
        )

        with patch("subprocess.Popen", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="timed out"):
                run_cc_teams("test query")


class TestParseStreamJson:
    """Tests for parse_stream_json()."""

    def test_parses_init_event(self):
        """parse_stream_json extracts session_id from init event."""
        from app.engines.cc_engine import CCResult, parse_stream_json

        lines = [
            json.dumps(
                {
                    "type": "system",
                    "subtype": "init",
                    "session_id": "sess-abc",
                    "model": "claude-sonnet",
                }
            )
        ]
        result = parse_stream_json(iter(lines))
        assert isinstance(result, CCResult)
        assert result.execution_id == "sess-abc"

    def test_parses_result_event(self):
        """parse_stream_json extracts cost/turns from result event."""
        from app.engines.cc_engine import parse_stream_json

        lines = [
            json.dumps(
                {
                    "type": "result",
                    "duration_ms": 12000,
                    "total_cost_usd": 0.05,
                    "num_turns": 7,
                }
            )
        ]
        result = parse_stream_json(iter(lines))
        assert result.output_data.get("duration_ms") == 12000
        assert result.output_data.get("total_cost_usd") == 0.05
        assert result.output_data.get("num_turns") == 7

    def test_parses_team_create_event(self):
        """parse_stream_json adds TeamCreate events to team_artifacts."""
        from app.engines.cc_engine import parse_stream_json

        lines = [json.dumps({"type": "TeamCreate", "team_name": "eval-team"})]
        result = parse_stream_json(iter(lines))
        assert len(result.team_artifacts) == 1
        assert result.team_artifacts[0]["type"] == "TeamCreate"
        assert result.team_artifacts[0]["team_name"] == "eval-team"

    def test_parses_task_event(self):
        """parse_stream_json adds Task events to team_artifacts."""
        from app.engines.cc_engine import parse_stream_json

        lines = [
            json.dumps({"type": "Task", "id": "task-001", "subject": "Review paper 1234"})
        ]
        result = parse_stream_json(iter(lines))
        assert len(result.team_artifacts) == 1
        assert result.team_artifacts[0]["type"] == "Task"

    def test_skips_blank_lines(self):
        """parse_stream_json skips empty/whitespace-only lines without error."""
        from app.engines.cc_engine import CCResult, parse_stream_json

        lines = ["", "  ", "\n", json.dumps({"type": "result", "num_turns": 1})]
        result = parse_stream_json(iter(lines))
        assert isinstance(result, CCResult)

    def test_skips_invalid_json_lines(self):
        """parse_stream_json skips malformed JSON lines without raising."""
        from app.engines.cc_engine import CCResult, parse_stream_json

        lines = ["not valid json {", json.dumps({"type": "result", "num_turns": 2})]
        result = parse_stream_json(iter(lines))
        assert isinstance(result, CCResult)

    def test_empty_stream_returns_default_result(self):
        """parse_stream_json returns CCResult with defaults for empty stream."""
        from app.engines.cc_engine import CCResult, parse_stream_json

        result = parse_stream_json(iter([]))
        assert isinstance(result, CCResult)
        assert result.team_artifacts == []

    def test_multiple_team_events_all_collected(self):
        """parse_stream_json collects all team-related events."""
        from app.engines.cc_engine import parse_stream_json

        lines = [
            json.dumps({"type": "TeamCreate", "team_name": "team-a"}),
            json.dumps({"type": "Task", "id": "task-1", "subject": "Task 1"}),
            json.dumps({"type": "Task", "id": "task-2", "subject": "Task 2"}),
        ]
        result = parse_stream_json(iter(lines))
        assert len(result.team_artifacts) == 3
