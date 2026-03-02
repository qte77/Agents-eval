"""
Tests for Trace Viewer Streamlit page.

Verifies render behavior for three scenarios: no database file,
empty database, and populated database with execution records.
"""

import sqlite3
from unittest.mock import patch

import pytest


@pytest.fixture
def traces_db(tmp_path):
    """Create a populated traces.db with schema and sample data."""
    db_path = tmp_path / "traces.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE trace_executions (
            execution_id TEXT PRIMARY KEY,
            start_time REAL,
            end_time REAL,
            agent_count INTEGER,
            tool_count INTEGER,
            total_duration REAL,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE trace_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT,
            timestamp REAL,
            event_type TEXT,
            agent_id TEXT,
            data TEXT
        )
    """)
    conn.execute(
        "INSERT INTO trace_executions VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("exec_abc123", 100.0, 102.5, 3, 5, 2.5, "2026-03-01T10:00:00Z"),
    )
    conn.execute(
        "INSERT INTO trace_events VALUES (NULL, ?, ?, ?, ?, ?)",
        (
            "exec_abc123",
            100.0,
            "agent_interaction",
            "manager",
            '{"from":"manager","to":"researcher"}',
        ),
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_traces_db(tmp_path):
    """Create a traces.db with schema but no data."""
    db_path = tmp_path / "traces.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE trace_executions (
            execution_id TEXT PRIMARY KEY,
            start_time REAL,
            end_time REAL,
            agent_count INTEGER,
            tool_count INTEGER,
            total_duration REAL,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE trace_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT,
            timestamp REAL,
            event_type TEXT,
            agent_id TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


class TestTraceViewerPage:
    """Test suite for Trace Viewer page rendering."""

    def test_render_no_db_shows_info(self, tmp_path):
        """When traces.db does not exist, show informational message."""
        from gui.pages.trace_viewer import render_trace_viewer

        with (
            patch("gui.pages.trace_viewer.resolve_project_path", return_value=tmp_path),
            patch("streamlit.header"),
            patch("streamlit.info") as mock_info,
        ):
            render_trace_viewer()
            mock_info.assert_called_once()
            assert "No traces.db" in mock_info.call_args[0][0]

    def test_render_empty_db_shows_empty_dataframe(self, empty_traces_db):
        """When traces.db exists but has no rows, show empty state."""
        from gui.pages.trace_viewer import render_trace_viewer

        with (
            patch(
                "gui.pages.trace_viewer.resolve_project_path", return_value=empty_traces_db.parent
            ),
            patch("streamlit.header"),
            patch("streamlit.info") as mock_info,
            patch("streamlit.dataframe"),
        ):
            render_trace_viewer()
            mock_info.assert_called_once()
            assert "No executions" in mock_info.call_args[0][0]

    def test_render_populated_db_shows_executions(self, traces_db):
        """When traces.db has records, display executions dataframe."""
        from gui.pages.trace_viewer import render_trace_viewer

        with (
            patch("gui.pages.trace_viewer.resolve_project_path", return_value=traces_db.parent),
            patch("streamlit.header"),
            patch("streamlit.dataframe") as mock_df,
            patch("streamlit.selectbox", return_value=None),
        ):
            render_trace_viewer()
            mock_df.assert_called_once()

    def test_render_drilldown_shows_events(self, traces_db):
        """When an execution is selected, display its events."""
        from gui.pages.trace_viewer import render_trace_viewer

        with (
            patch("gui.pages.trace_viewer.resolve_project_path", return_value=traces_db.parent),
            patch("streamlit.header"),
            patch("streamlit.dataframe") as mock_df,
            patch("streamlit.selectbox", return_value="exec_abc123"),
            patch("streamlit.subheader"),
        ):
            render_trace_viewer()
            # Two dataframes: executions table + events table
            assert mock_df.call_count == 2
