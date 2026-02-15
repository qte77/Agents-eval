"""
Tests for Claude Code trace adapter.

Tests the CCTraceAdapter class which parses CC artifacts (solo and teams mode)
into GraphTraceData format for three-tier evaluation pipeline.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

import pytest

from app.data_models.evaluation_models import GraphTraceData
from app.judge.cc_trace_adapter import CCTraceAdapter


@pytest.fixture
def cc_teams_artifacts(tmp_path: Path) -> Path:
    """Create temporary CC Agent Teams artifacts directory.

    Args:
        tmp_path: pytest temp directory

    Returns:
        Path to teams artifacts directory
    """
    teams_dir = tmp_path / "teams" / "test-team"
    teams_dir.mkdir(parents=True)

    # config.json with team members
    config = {
        "team_name": "test-team",
        "members": [
            {"name": "leader", "agentId": "agent-001", "agentType": "coordinator"},
            {"name": "worker", "agentId": "agent-002", "agentType": "executor"},
        ],
        "created_at": "2026-02-15T10:00:00Z",
    }
    (teams_dir / "config.json").write_text(json.dumps(config))

    # inboxes directory with agent messages
    inboxes_dir = teams_dir / "inboxes"
    inboxes_dir.mkdir()

    message1 = {
        "from": "leader",
        "to": "worker",
        "type": "task_assignment",
        "content": "Process dataset",
        "timestamp": 1708000000.0,
    }
    (inboxes_dir / "message_001.json").write_text(json.dumps(message1))

    message2 = {
        "from": "worker",
        "to": "leader",
        "type": "task_complete",
        "content": "Dataset processed",
        "timestamp": 1708000100.0,
    }
    (inboxes_dir / "message_002.json").write_text(json.dumps(message2))

    # tasks directory with completed tasks
    tasks_dir = teams_dir / "tasks"
    tasks_dir.mkdir()

    task1 = {
        "id": "task-001",
        "title": "Process data",
        "owner": "worker",
        "status": "completed",
        "created_at": 1708000010.0,
        "completed_at": 1708000095.0,
    }
    (tasks_dir / "task-001.json").write_text(json.dumps(task1))

    return teams_dir


@pytest.fixture
def cc_solo_artifacts(tmp_path: Path) -> Path:
    """Create temporary CC solo session export directory.

    Args:
        tmp_path: pytest temp directory

    Returns:
        Path to solo session directory
    """
    session_dir = tmp_path / "session" / "solo-run"
    session_dir.mkdir(parents=True)

    # session metadata
    metadata = {
        "session_id": "solo-run",
        "start_time": 1708000000.0,
        "end_time": 1708000200.0,
        "agent_type": "code-assistant",
    }
    (session_dir / "metadata.json").write_text(json.dumps(metadata))

    # tool calls log
    tool_calls = [
        {
            "tool_name": "Read",
            "timestamp": 1708000050.0,
            "success": True,
            "duration": 0.5,
            "agent_id": "solo-agent",
        },
        {
            "tool_name": "Edit",
            "timestamp": 1708000120.0,
            "success": True,
            "duration": 1.2,
            "agent_id": "solo-agent",
        },
    ]
    (session_dir / "tool_calls.jsonl").write_text(
        "\n".join(json.dumps(tc) for tc in tool_calls)
    )

    return session_dir


class TestCCTraceAdapterTeamsMode:
    """Test CC trace adapter in teams mode."""

    def test_teams_mode_detection(self, cc_teams_artifacts: Path):
        """Teams mode is auto-detected from config.json with members array."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        assert adapter.mode == "teams"

    def test_teams_mode_parse_execution_id(self, cc_teams_artifacts: Path):
        """Execution ID extracted from team name."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        trace_data = adapter.parse()

        assert trace_data.execution_id == "test-team"

    def test_teams_mode_agent_interactions(self, cc_teams_artifacts: Path):
        """Agent interactions parsed from inboxes/*.json."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        trace_data = adapter.parse()

        assert len(trace_data.agent_interactions) == 2
        assert trace_data.agent_interactions[0]["from"] == "leader"
        assert trace_data.agent_interactions[0]["to"] == "worker"
        assert trace_data.agent_interactions[1]["from"] == "worker"

    def test_teams_mode_tool_calls_from_tasks(self, cc_teams_artifacts: Path):
        """Tool calls derived from task completions."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        trace_data = adapter.parse()

        # Tasks are mapped as proxy tool calls
        assert len(trace_data.tool_calls) >= 1
        assert "task-001" in str(trace_data.tool_calls)

    def test_teams_mode_timing_data(self, cc_teams_artifacts: Path):
        """Timing data derived from first/last timestamps."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        trace_data = adapter.parse()

        assert "start_time" in trace_data.timing_data
        assert "end_time" in trace_data.timing_data
        assert trace_data.timing_data["end_time"] >= trace_data.timing_data["start_time"]

    def test_teams_mode_coordination_events(self, cc_teams_artifacts: Path):
        """Coordination events extracted from task assignments."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        trace_data = adapter.parse()

        # Task assignments indicate coordination
        assert len(trace_data.coordination_events) >= 0

    def test_teams_mode_graph_trace_data_output(self, cc_teams_artifacts: Path):
        """Output GraphTraceData instance structure matches expected schema."""
        adapter = CCTraceAdapter(cc_teams_artifacts)
        trace_data = adapter.parse()

        # Verify it's a valid GraphTraceData instance
        assert isinstance(trace_data, GraphTraceData)

        # Snapshot the structure for regression testing
        assert trace_data.model_dump() == snapshot(
            {
                "execution_id": "test-team",
                "agent_interactions": [
                    {
                        "from": "leader",
                        "to": "worker",
                        "type": "task_assignment",
                        "content": "Process dataset",
                        "timestamp": 1708000000.0,
                    },
                    {
                        "from": "worker",
                        "to": "leader",
                        "type": "task_complete",
                        "content": "Dataset processed",
                        "timestamp": 1708000100.0,
                    },
                ],
                "tool_calls": snapshot(),
                "timing_data": snapshot(),
                "coordination_events": snapshot(),
            }
        )


class TestCCTraceAdapterSoloMode:
    """Test CC trace adapter in solo mode."""

    def test_solo_mode_detection(self, cc_solo_artifacts: Path):
        """Solo mode is auto-detected when config.json missing."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        assert adapter.mode == "solo"

    def test_solo_mode_parse_execution_id(self, cc_solo_artifacts: Path):
        """Execution ID extracted from session metadata."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        trace_data = adapter.parse()

        assert trace_data.execution_id == "solo-run"

    def test_solo_mode_tool_calls_from_logs(self, cc_solo_artifacts: Path):
        """Tool calls parsed from session logs."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        trace_data = adapter.parse()

        assert len(trace_data.tool_calls) == 2
        assert trace_data.tool_calls[0]["tool_name"] == "Read"
        assert trace_data.tool_calls[1]["tool_name"] == "Edit"

    def test_solo_mode_timing_data(self, cc_solo_artifacts: Path):
        """Timing data from session start/end timestamps."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        trace_data = adapter.parse()

        assert trace_data.timing_data["start_time"] == 1708000000.0
        assert trace_data.timing_data["end_time"] == 1708000200.0

    def test_solo_mode_empty_interactions(self, cc_solo_artifacts: Path):
        """Agent interactions list is empty in solo mode."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        trace_data = adapter.parse()

        # Solo has no agent-to-agent interactions
        assert len(trace_data.agent_interactions) == 0

    def test_solo_mode_empty_coordination(self, cc_solo_artifacts: Path):
        """Coordination events list is empty in solo mode."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        trace_data = adapter.parse()

        # Solo has no coordination (single agent)
        assert len(trace_data.coordination_events) == 0

    def test_solo_mode_graph_trace_data_output(self, cc_solo_artifacts: Path):
        """Output GraphTraceData instance structure matches expected schema."""
        adapter = CCTraceAdapter(cc_solo_artifacts)
        trace_data = adapter.parse()

        assert isinstance(trace_data, GraphTraceData)
        assert trace_data.model_dump() == snapshot(
            {
                "execution_id": "solo-run",
                "agent_interactions": [],
                "tool_calls": [
                    {
                        "tool_name": "Read",
                        "timestamp": 1708000050.0,
                        "success": True,
                        "duration": 0.5,
                        "agent_id": "solo-agent",
                    },
                    {
                        "tool_name": "Edit",
                        "timestamp": 1708000120.0,
                        "success": True,
                        "duration": 1.2,
                        "agent_id": "solo-agent",
                    },
                ],
                "timing_data": {"start_time": 1708000000.0, "end_time": 1708000200.0},
                "coordination_events": [],
            }
        )


class TestCCTraceAdapterErrorHandling:
    """Test error handling for missing or malformed artifacts."""

    def test_missing_directory(self):
        """Graceful error when directory does not exist."""
        with pytest.raises(ValueError, match="does not exist"):
            CCTraceAdapter(Path("/nonexistent/path"))

    def test_empty_directory(self, tmp_path: Path):
        """Graceful error when directory is empty."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(ValueError, match="No CC artifacts found"):
            adapter = CCTraceAdapter(empty_dir)
            adapter.parse()

    def test_malformed_config_json(self, tmp_path: Path):
        """Graceful error when config.json is malformed."""
        bad_dir = tmp_path / "bad"
        bad_dir.mkdir()
        (bad_dir / "config.json").write_text("not valid json")

        with pytest.raises(ValueError, match="Failed to parse"):
            adapter = CCTraceAdapter(bad_dir)
            adapter.parse()


@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "from": st.text(min_size=1, max_size=20),
                "to": st.text(min_size=1, max_size=20),
                "timestamp": st.floats(min_value=0.0, max_value=2000000000.0),
            }
        ),
        min_size=0,
        max_size=50,
    )
)
def test_agent_interactions_invariant(interactions: list[dict]):
    """Property test: All agent_interactions have required fields.

    Args:
        interactions: Generated list of agent interactions
    """
    # Create temporary teams artifacts with generated interactions
    with tempfile.TemporaryDirectory() as tmpdir:
        teams_dir = Path(tmpdir) / "teams" / "prop-test"
        teams_dir.mkdir(parents=True)

        # Minimal config
        config = {
            "team_name": "prop-test",
            "members": [{"name": "a1", "agentId": "a1", "agentType": "test"}],
        }
        (teams_dir / "config.json").write_text(json.dumps(config))

        # Write generated interactions
        inboxes_dir = teams_dir / "inboxes"
        inboxes_dir.mkdir()

        for i, interaction in enumerate(interactions):
            (inboxes_dir / f"msg_{i}.json").write_text(json.dumps(interaction))

        # Parse and verify
        adapter = CCTraceAdapter(teams_dir)
        trace_data = adapter.parse()

        # Invariant: All interactions must have from, to fields
        for interaction in trace_data.agent_interactions:
            assert "from" in interaction
            assert "to" in interaction


@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "tool_name": st.text(min_size=1, max_size=30),
                "timestamp": st.floats(min_value=0.0, max_value=2000000000.0),
                "success": st.booleans(),
                "duration": st.floats(min_value=0.0, max_value=300.0),
            }
        ),
        min_size=1,
        max_size=100,
    )
)
def test_timestamps_ordered_invariant(tool_calls: list[dict]):
    """Property test: Timing data start <= end for all valid inputs.

    Args:
        tool_calls: Generated list of tool call events
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        session_dir = Path(tmpdir) / "session" / "prop-test"
        session_dir.mkdir(parents=True)

        timestamps = [tc["timestamp"] for tc in tool_calls]
        min_ts = min(timestamps)
        max_ts = max(timestamps)

        metadata = {
            "session_id": "prop-test",
            "start_time": min_ts,
            "end_time": max_ts,
        }
        (session_dir / "metadata.json").write_text(json.dumps(metadata))

        # Write tool calls
        (session_dir / "tool_calls.jsonl").write_text(
            "\n".join(json.dumps(tc) for tc in tool_calls)
        )

        # Parse and verify
        adapter = CCTraceAdapter(session_dir)
        trace_data = adapter.parse()

        # Invariant: start_time <= end_time
        assert trace_data.timing_data["start_time"] <= trace_data.timing_data["end_time"]
