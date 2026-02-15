"""
Tests for trace data quality fixes (STORY-013).

Tests ensure:
- agent_id is included in tool_call dicts during trace processing
- GraphTraceData transformation succeeds with researcher traces
- Trace event schema invariants are maintained
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.errors import HealthCheck
from inline_snapshot import snapshot

from app.data_models.evaluation_models import GraphTraceData
from app.judge.settings import JudgeSettings
from app.judge.trace_processors import ProcessedTrace, TraceCollector, TraceEvent


class TestTraceEventAgentIdInvariant:
    """Test that agent_id is always present in tool_call trace events."""

    @given(
        agent_id=st.text(min_size=1, max_size=20),
        tool_name=st.text(min_size=1, max_size=50),
        duration=st.floats(min_value=0.0, max_value=100.0),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_process_events_includes_agent_id_in_tool_calls(
        self, agent_id: str, tool_name: str, duration: float
    ):
        """Property: _process_events() tool_call dicts MUST include agent_id field."""
        # Setup - use tempfile instead of tmp_path fixture
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings = JudgeSettings(trace_storage_path=str(tmp_path / "traces"))
            collector = TraceCollector(settings)

        # Create tool_call event
        event = TraceEvent(
            timestamp=1000.0,
            event_type="tool_call",
            agent_id=agent_id,
            data={"tool_name": tool_name, "duration": duration},
            execution_id="test-exec-001",
        )

            collector.current_execution_id = "test-exec-001"
            collector.current_events = [event]

            # Execute
            trace: ProcessedTrace = collector._process_events()

            # Verify: agent_id MUST be present in tool_call dict
            assert len(trace.tool_calls) == 1
            tool_call = trace.tool_calls[0]
            assert "agent_id" in tool_call, "agent_id missing from tool_call dict"
            assert tool_call["agent_id"] == agent_id

    @given(
        agent_id=st.text(min_size=1, max_size=20),
        tool_name=st.text(min_size=1, max_size=50),
        duration=st.floats(min_value=0.0, max_value=100.0),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_trace_events_includes_agent_id_in_tool_calls(
        self, agent_id: str, tool_name: str, duration: float
    ):
        """Property: _parse_trace_events() tool_call dicts MUST include agent_id field."""
        # Setup - use tempfile instead of tmp_path fixture
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings = JudgeSettings(trace_storage_path=str(tmp_path / "traces"))
            collector = TraceCollector(settings)

            # Simulate database events
            db_events: list[tuple[float, str, str, str]] = [
                (
                    1000.0,
                    "tool_call",
                    agent_id,
                    json.dumps({"tool_name": tool_name, "duration": duration}),
                )
            ]

            # Execute
            _, tool_calls, _ = collector._parse_trace_events(db_events)

            # Verify: agent_id MUST be present in tool_call dict
            assert len(tool_calls) == 1
            tool_call = tool_calls[0]
            assert "agent_id" in tool_call, "agent_id missing from tool_call dict"
            assert tool_call["agent_id"] == agent_id


class TestGraphTraceDataTransformation:
    """Test GraphTraceData transformation with researcher traces."""

    def test_graph_trace_data_accepts_researcher_traces(self, tmp_path: Path):
        """GraphTraceData transformation MUST succeed with researcher tool traces."""
        # Setup: Create trace with researcher agent tool calls
        settings = JudgeSettings(trace_storage_path=str(tmp_path / "traces"))
        collector = TraceCollector(settings)

        researcher_events = [
            TraceEvent(
                timestamp=1000.0,
                event_type="tool_call",
                agent_id="researcher",
                data={"tool_name": "search_papers", "duration": 1.5, "success": True},
                execution_id="test-exec-002",
            ),
            TraceEvent(
                timestamp=1001.5,
                event_type="tool_call",
                agent_id="researcher",
                data={"tool_name": "extract_citations", "duration": 0.8, "success": True},
                execution_id="test-exec-002",
            ),
        ]

        collector.current_execution_id = "test-exec-002"
        collector.current_events = researcher_events

        # Execute
        trace: ProcessedTrace = collector._process_events()

        # Convert to GraphTraceData (this was failing before fix)
        try:
            graph_trace = GraphTraceData(
                agent_interactions=trace.agent_interactions,
                tool_calls=trace.tool_calls,
                coordination_events=trace.coordination_events,
            )
        except Exception as e:
            pytest.fail(f"GraphTraceData transformation failed: {e}")

        # Verify: tool_calls have agent_id
        assert len(graph_trace.tool_calls) == 2
        for tool_call in graph_trace.tool_calls:
            assert "agent_id" in tool_call
            assert tool_call["agent_id"] == "researcher"


class TestGraphTraceDataTransformationSnapshot:
    """Test GraphTraceData transformation output structure using snapshots."""

    def test_graph_trace_data_structure_snapshot(self, tmp_path: Path):
        """Snapshot: GraphTraceData transformation output structure."""
        # Setup
        settings = JudgeSettings(trace_storage_path=str(tmp_path / "traces"))
        collector = TraceCollector(settings)

        events = [
            TraceEvent(
                timestamp=1000.0,
                event_type="agent_interaction",
                agent_id="manager",
                data={"action": "delegate", "target": "researcher"},
                execution_id="snapshot-test",
            ),
            TraceEvent(
                timestamp=1001.0,
                event_type="tool_call",
                agent_id="researcher",
                data={"tool_name": "search", "duration": 1.2},
                execution_id="snapshot-test",
            ),
            TraceEvent(
                timestamp=1002.2,
                event_type="coordination",
                agent_id="manager",
                data={"event": "task_complete"},
                execution_id="snapshot-test",
            ),
        ]

        collector.current_execution_id = "snapshot-test"
        collector.current_events = events

        # Execute
        trace = collector._process_events()
        graph_trace = GraphTraceData(
            agent_interactions=trace.agent_interactions,
            tool_calls=trace.tool_calls,
            coordination_events=trace.coordination_events,
        )

        # Snapshot the structure
        dumped = {
            "agent_interactions": graph_trace.agent_interactions,
            "tool_calls": graph_trace.tool_calls,
            "coordination_events": graph_trace.coordination_events,
        }

        assert dumped == snapshot(
            {
                "agent_interactions": [
                    {"action": "delegate", "target": "researcher", "timestamp": 1000.0}
                ],
                "tool_calls": [
                    {
                        "tool_name": "search",
                        "duration": 1.2,
                        "timestamp": 1001.0,
                        "agent_id": "researcher",
                    }
                ],
                "coordination_events": [{"event": "task_complete", "timestamp": 1002.2}],
            }
        )
