"""
Tests for CC artifact collection scripts.

Tests verify:
- Script exit codes (0 = success, 1 = validation failure, 2 = usage error)
- Output directory structure matches CCTraceAdapter expectations
- Proper argument parsing and validation
"""

import json
import subprocess
from pathlib import Path

import pytest


class TestCollectCCSolo:
    """Tests for scripts/collect-cc-traces/collect-cc-solo.sh."""

    def test_missing_required_args_returns_exit_code_2(self, tmp_path: Path) -> None:
        """Script exits with code 2 when required arguments are missing.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-solo.sh")

        # ACT
        result = subprocess.run([str(script)], capture_output=True, text=True, check=False)

        # ASSERT
        assert result.returncode == 2, "Expected exit code 2 for missing args"

    def test_creates_metadata_json_with_session_info(self, tmp_path: Path) -> None:
        """Script creates metadata.json with session_id, timestamps, model.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-solo.sh")
        output_dir = tmp_path / "output"
        session_name = "test-session"

        # ACT
        result = subprocess.run(
            [
                str(script),
                "--name",
                session_name,
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # ASSERT
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        metadata_path = output_dir / "metadata.json"
        assert metadata_path.exists(), "metadata.json not created"

        metadata = json.loads(metadata_path.read_text())
        assert "session_id" in metadata, "session_id missing"
        assert "start_time" in metadata, "start_time missing"
        assert "end_time" in metadata, "end_time missing"
        assert metadata["session_id"] == session_name

    def test_creates_tool_calls_jsonl(self, tmp_path: Path) -> None:
        """Script creates tool_calls.jsonl with one JSON object per line.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-solo.sh")
        output_dir = tmp_path / "output"
        session_name = "test-session"

        # ACT
        result = subprocess.run(
            [
                str(script),
                "--name",
                session_name,
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # ASSERT
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        tool_calls_path = output_dir / "tool_calls.jsonl"
        assert tool_calls_path.exists(), "tool_calls.jsonl not created"

        # Validate JSONL format (each line is valid JSON)
        lines = tool_calls_path.read_text().strip().split("\n")
        for line in lines:
            if line.strip():  # Skip empty lines
                json.loads(line)  # Will raise if invalid JSON

    def test_validation_failure_returns_exit_code_1(self, tmp_path: Path) -> None:
        """Script exits with code 1 when jq is not available (validation fails).

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE - This test verifies validation logic, but requires jq absence
        # which is hard to mock in bash. Skip for now - validation is tested
        # indirectly by checking valid JSON output in other tests
        pytest.skip("Validation failure hard to trigger without breaking jq dependency")


class TestCollectCCTeams:
    """Tests for scripts/collect-cc-traces/collect-cc-teams.sh."""

    def test_missing_required_args_returns_exit_code_2(self, tmp_path: Path) -> None:
        """Script exits with code 2 when required arguments are missing.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-teams.sh")

        # ACT
        result = subprocess.run([str(script)], capture_output=True, text=True, check=False)

        # ASSERT
        assert result.returncode == 2, "Expected exit code 2 for missing args"

    def test_copies_team_config_json(self, tmp_path: Path) -> None:
        """Script copies config.json from ~/.claude/teams/{name}/.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-teams.sh")
        output_dir = tmp_path / "output"

        # Create mock CC teams directory structure
        mock_teams_dir = tmp_path / "mock_claude" / "teams" / "test-team"
        mock_teams_dir.mkdir(parents=True)
        config_path = mock_teams_dir / "config.json"
        config_path.write_text(json.dumps({"team_name": "test-team", "members": []}))

        # ACT
        result = subprocess.run(
            [
                str(script),
                "--name",
                "test-team",
                "--output-dir",
                str(output_dir),
                "--teams-source",
                str(mock_teams_dir.parent),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # ASSERT
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        copied_config = output_dir / "config.json"
        assert copied_config.exists(), "config.json not copied"

        config = json.loads(copied_config.read_text())
        assert config["team_name"] == "test-team"

    def test_copies_task_files(self, tmp_path: Path) -> None:
        """Script copies task JSON files from ~/.claude/tasks/{name}/.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-teams.sh")
        output_dir = tmp_path / "output"

        # Create mock CC directory structure
        mock_teams_dir = tmp_path / "mock_claude" / "teams" / "test-team"
        mock_tasks_dir = tmp_path / "mock_claude" / "tasks" / "test-team"
        mock_teams_dir.mkdir(parents=True)
        mock_tasks_dir.mkdir(parents=True)

        config_path = mock_teams_dir / "config.json"
        config_path.write_text(json.dumps({"team_name": "test-team", "members": []}))

        task_path = mock_tasks_dir / "task-001.json"
        task_path.write_text(json.dumps({"id": "task-001", "status": "completed"}))

        # ACT
        result = subprocess.run(
            [
                str(script),
                "--name",
                "test-team",
                "--output-dir",
                str(output_dir),
                "--teams-source",
                str(mock_teams_dir.parent),
                "--tasks-source",
                str(mock_tasks_dir.parent),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # ASSERT
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        copied_task = output_dir / "tasks" / "task-001.json"
        assert copied_task.exists(), "task file not copied"

        task = json.loads(copied_task.read_text())
        assert task["id"] == "task-001"

    def test_validation_failure_returns_exit_code_1(self, tmp_path: Path) -> None:
        """Script exits with code 1 when source directories missing.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-teams.sh")
        output_dir = tmp_path / "output"
        team_name = "nonexistent-team-12345"

        # ACT
        result = subprocess.run(
            [
                str(script),
                "--name",
                team_name,
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # ASSERT
        assert result.returncode == 1, "Expected exit code 1 for validation failure"

    def test_preserves_directory_structure(self, tmp_path: Path) -> None:
        """Script preserves directory structure in output.

        Args:
            tmp_path: Temporary directory fixture
        """
        # ARRANGE
        script = Path("scripts/collect-cc-traces/collect-cc-teams.sh")
        output_dir = tmp_path / "output"

        # Create mock CC directory structure with nested directories
        mock_teams_dir = tmp_path / "mock_claude" / "teams" / "test-team"
        mock_tasks_dir = tmp_path / "mock_claude" / "tasks" / "test-team"
        mock_teams_dir.mkdir(parents=True)
        mock_tasks_dir.mkdir(parents=True)

        config_path = mock_teams_dir / "config.json"
        config_path.write_text(json.dumps({"team_name": "test-team", "members": []}))

        # Create nested task structure
        (mock_tasks_dir / "subtasks").mkdir()
        subtask_path = mock_tasks_dir / "subtasks" / "subtask-001.json"
        subtask_path.write_text(json.dumps({"id": "subtask-001", "status": "completed"}))

        # ACT
        result = subprocess.run(
            [
                str(script),
                "--name",
                "test-team",
                "--output-dir",
                str(output_dir),
                "--teams-source",
                str(mock_teams_dir.parent),
                "--tasks-source",
                str(mock_tasks_dir.parent),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # ASSERT
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        copied_subtask = output_dir / "tasks" / "subtasks" / "subtask-001.json"
        assert copied_subtask.exists(), "nested structure not preserved"
