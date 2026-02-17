"""Tests for engine_comparison.py example.

Purpose: Verify the engine comparison example demonstrates loading CC artifacts
         via CCTraceAdapter and comparing MAS vs CC evaluation scores.
Setup: Uses tmp_path for CC artifact directories; mocks actual CC subprocess calls.
Expected behavior: CCTraceAdapter loads artifacts from mock directory, returns
                   GraphTraceData that can be fed to EvaluationPipeline.
Mock strategy: Create minimal CC artifact directory structure in tmp_path;
               patch EvaluationPipeline LLM calls.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from app.data_models.evaluation_models import GraphTraceData
from app.judge.cc_trace_adapter import CCTraceAdapter


class TestEngineComparisonExists:
    """Verify the engine_comparison.py example file is created."""

    def test_example_file_exists(self) -> None:
        """engine_comparison.py must exist in src/examples/."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        target = examples_dir / "engine_comparison.py"
        # Assert
        assert target.exists(), f"Example file missing: {target}"

    def test_example_documents_prerequisites(self) -> None:
        """Example must document CC artifact prerequisites."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        content = (examples_dir / "engine_comparison.py").read_text()
        # Assert
        assert (
            "collect-cc" in content or "scripts" in content or "Prerequisites" in content.lower()
        ), "Example must document prerequisites for CC artifact collection"

    def test_example_uses_cc_trace_adapter(self) -> None:
        """Example must use CCTraceAdapter for loading CC artifacts."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        content = (examples_dir / "engine_comparison.py").read_text()
        # Assert
        assert "CCTraceAdapter" in content, "Example must import and use CCTraceAdapter"


class TestCCTraceAdapterIntegration:
    """Verify CCTraceAdapter integration works as shown in the example."""

    @pytest.fixture
    def solo_artifacts_dir(self, tmp_path: Path) -> Path:
        """Create a minimal CC solo-mode artifact directory."""
        # Arrange: solo mode has metadata.json + tool_calls.jsonl (no config.json)
        artifacts_dir = tmp_path / "cc_solo_run"
        artifacts_dir.mkdir()

        metadata = {
            "model": "claude-opus-4-5",
            "session_id": "test-session-001",
            "timestamp": "2026-01-01T00:00:00Z",
        }
        (artifacts_dir / "metadata.json").write_text(json.dumps(metadata))

        tool_calls = [
            {
                "tool": "Read",
                "input": {"file_path": str(tmp_path / "test.py")},
                "output": "content",
                "timestamp": 0.0,
            },
            {"tool": "Bash", "input": {"command": "ls"}, "output": "file.py", "timestamp": 1.0},
        ]
        tool_calls_text = "\n".join(json.dumps(tc) for tc in tool_calls)
        (artifacts_dir / "tool_calls.jsonl").write_text(tool_calls_text)

        return artifacts_dir

    @pytest.fixture
    def teams_artifacts_dir(self, tmp_path: Path) -> Path:
        """Create a minimal CC teams-mode artifact directory."""
        # Arrange: teams mode has config.json with 'members' array
        artifacts_dir = tmp_path / "cc_teams_run"
        artifacts_dir.mkdir()

        config = {
            "team_name": "test-team",
            "members": [
                {"name": "researcher", "agentId": "abc-001", "agentType": "general-purpose"},
                {"name": "analyst", "agentId": "abc-002", "agentType": "general-purpose"},
            ],
        }
        (artifacts_dir / "config.json").write_text(json.dumps(config))

        # Create inboxes dir (coordination events source)
        inboxes_dir = artifacts_dir / "inboxes"
        inboxes_dir.mkdir()

        return artifacts_dir

    def test_solo_adapter_parses_to_graph_trace_data(self, solo_artifacts_dir: Path) -> None:
        """CCTraceAdapter in solo mode returns valid GraphTraceData."""
        # Arrange
        adapter = CCTraceAdapter(solo_artifacts_dir)
        # Act
        trace: GraphTraceData = adapter.parse()
        # Assert
        assert isinstance(trace, GraphTraceData), f"Expected GraphTraceData, got {type(trace)}"
        assert trace.execution_id, "GraphTraceData must have a non-empty execution_id"

    def test_teams_adapter_parses_to_graph_trace_data(self, teams_artifacts_dir: Path) -> None:
        """CCTraceAdapter in teams mode returns valid GraphTraceData."""
        # Arrange
        adapter = CCTraceAdapter(teams_artifacts_dir)
        # Act
        trace: GraphTraceData = adapter.parse()
        # Assert
        assert isinstance(trace, GraphTraceData), f"Expected GraphTraceData, got {type(trace)}"
        assert trace.execution_id, "GraphTraceData must have a non-empty execution_id"

    def test_adapter_mode_detection(
        self, solo_artifacts_dir: Path, teams_artifacts_dir: Path
    ) -> None:
        """CCTraceAdapter correctly detects solo vs teams mode."""
        # Arrange / Act
        solo_adapter = CCTraceAdapter(solo_artifacts_dir)
        teams_adapter = CCTraceAdapter(teams_artifacts_dir)
        # Assert
        assert solo_adapter.mode == "solo", f"Expected 'solo', got {solo_adapter.mode}"
        assert teams_adapter.mode == "teams", f"Expected 'teams', got {teams_adapter.mode}"

    def test_adapter_raises_on_missing_dir(self, tmp_path: Path) -> None:
        """CCTraceAdapter raises ValueError when artifacts directory does not exist."""
        # Arrange
        missing_dir = tmp_path / "nonexistent"
        # Act / Assert
        with pytest.raises(ValueError, match="does not exist"):
            CCTraceAdapter(missing_dir)


class TestEngineComparisonIsImportable:
    """Verify engine_comparison.py can be loaded without errors."""

    def test_example_is_importable(self) -> None:
        """engine_comparison.py imports without errors."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        target = examples_dir / "engine_comparison.py"

        spec = importlib.util.spec_from_file_location(
            "engine_comparison",
            target,
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        # Act / Assert: loading must not raise
        sys.modules["engine_comparison"] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]
