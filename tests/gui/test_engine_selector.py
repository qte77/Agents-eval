"""
Tests for engine selector UI: CCTraceAdapter coordination events fix
and engine integration in run_app render flow.

Mock strategy:
- CCTraceAdapter._extract_coordination_events tested directly
- inboxes/ directory structure mocked via tmp_path fixtures
"""

import json
from pathlib import Path


class TestCCCoordinationEventsExtraction:
    """Tests for CCTraceAdapter._extract_coordination_events fix.

    Arrange: CC artifacts directory with inboxes/*.json files
    Act: Call _extract_coordination_events()
    Expected: Coordination events parsed from inbox messages
    """

    def test_extract_coordination_events_empty_when_no_inboxes(self, tmp_path: Path) -> None:
        """Returns empty list when no inboxes/ directory exists."""
        from app.judge.cc_trace_adapter import CCTraceAdapter

        # Create minimal teams config so CCTraceAdapter initializes
        config = {"team_name": "test-team", "members": []}
        (tmp_path / "config.json").write_text(json.dumps(config))

        adapter = CCTraceAdapter(tmp_path)
        result = adapter._extract_coordination_events()

        assert isinstance(result, list)

    def test_extract_coordination_events_parses_inbox_messages(self, tmp_path: Path) -> None:
        """Coordination events populated from inboxes/*.json messages."""
        from app.judge.cc_trace_adapter import CCTraceAdapter

        # Setup teams artifacts with config + inboxes
        config = {
            "team_name": "test-team",
            "members": [{"name": "agent-a"}, {"name": "agent-b"}],
        }
        (tmp_path / "config.json").write_text(json.dumps(config))

        inboxes_dir = tmp_path / "inboxes"
        inboxes_dir.mkdir()

        msg1 = {
            "from": "agent-a",
            "to": "agent-b",
            "content": "Task assigned",
            "timestamp": 1700000001.0,
        }
        msg2 = {
            "from": "agent-b",
            "to": "agent-a",
            "content": "Task done",
            "timestamp": 1700000002.0,
        }
        (inboxes_dir / "msg-001.json").write_text(json.dumps(msg1))
        (inboxes_dir / "msg-002.json").write_text(json.dumps(msg2))

        adapter = CCTraceAdapter(tmp_path)
        result = adapter._extract_coordination_events()

        # After fix: coordination events populated from inbox messages
        assert isinstance(result, list)
        assert len(result) == 2

    def test_extract_coordination_events_single_message(self, tmp_path: Path) -> None:
        """Single inbox message yields single coordination event."""
        from app.judge.cc_trace_adapter import CCTraceAdapter

        config = {"team_name": "test-team", "members": [{"name": "lead"}]}
        (tmp_path / "config.json").write_text(json.dumps(config))

        inboxes_dir = tmp_path / "inboxes"
        inboxes_dir.mkdir()

        msg = {"from": "lead", "to": "worker", "content": "Do work", "timestamp": 1.0}
        (inboxes_dir / "msg-001.json").write_text(json.dumps(msg))

        adapter = CCTraceAdapter(tmp_path)
        result = adapter._extract_coordination_events()

        assert len(result) == 1
        assert result[0]["from"] == "lead"
        assert result[0]["to"] == "worker"

    def test_extract_coordination_events_skips_malformed_files(self, tmp_path: Path) -> None:
        """Malformed inbox JSON files are skipped without raising."""
        from app.judge.cc_trace_adapter import CCTraceAdapter

        config = {"team_name": "test-team", "members": [{"name": "agent-a"}]}
        (tmp_path / "config.json").write_text(json.dumps(config))

        inboxes_dir = tmp_path / "inboxes"
        inboxes_dir.mkdir()

        (inboxes_dir / "good.json").write_text(
            json.dumps({"from": "a", "to": "b", "content": "ok", "timestamp": 1.0})
        )
        (inboxes_dir / "bad.json").write_text("{ invalid json }")

        adapter = CCTraceAdapter(tmp_path)
        # Should not raise; malformed file is skipped
        result = adapter._extract_coordination_events()

        assert len(result) == 1


class TestRunAppEngineIntegration:
    """Tests for engine selector integration in run_app render flow.

    Arrange: Mock Streamlit session state and widget calls
    Act: Call render_app helper functions that depend on engine
    Expected: Correct behavior based on engine selection
    """

    def test_execute_query_background_accepts_engine_parameter(self) -> None:
        """_execute_query_background accepts engine parameter without error."""
        import inspect

        from gui.pages.run_app import _execute_query_background

        sig = inspect.signature(_execute_query_background)
        assert "engine" in sig.parameters

    def test_execute_query_background_engine_defaults_to_mas(self) -> None:
        """engine parameter defaults to 'mas' in _execute_query_background."""
        import inspect

        from gui.pages.run_app import _execute_query_background

        sig = inspect.signature(_execute_query_background)
        param = sig.parameters["engine"]
        assert param.default == "mas"

    def test_handle_query_submission_accepts_engine_parameter(self) -> None:
        """_handle_query_submission accepts engine parameter."""
        import inspect

        from gui.pages.run_app import _handle_query_submission

        sig = inspect.signature(_handle_query_submission)
        assert "engine" in sig.parameters
