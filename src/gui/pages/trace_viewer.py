"""
Streamlit page for browsing trace execution data.

Reads traces.db (SQLite) directly via the built-in sqlite3 module.
Displays an executions overview table with drill-down to individual
trace events for a selected execution.
"""

import sqlite3
from pathlib import Path

import streamlit as st

from app.config.config_app import RUNS_PATH
from app.utils.paths import resolve_project_path
from gui.config.text import TRACE_VIEWER_HEADER


def _get_db_path() -> Path:
    """Resolve the traces.db path from project configuration.

    Returns:
        Path to the traces.db file (may not exist).
    """
    return resolve_project_path(RUNS_PATH) / "traces.db"


def _query_executions(db_path: Path) -> list[dict[str, object]]:
    """Query all executions ordered by created_at descending.

    Args:
        db_path: Path to the SQLite database.

    Returns:
        List of execution row dicts.
    """
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT execution_id, agent_count, tool_count,
                   total_duration, created_at
            FROM trace_executions
            ORDER BY created_at DESC
            """
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "execution_id": r[0],
            "agent_count": r[1],
            "tool_count": r[2],
            "total_duration": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]


def _query_events(db_path: Path, execution_id: str) -> list[dict[str, object]]:
    """Query trace events for a specific execution.

    Args:
        db_path: Path to the SQLite database.
        execution_id: Execution to filter by.

    Returns:
        List of event row dicts.
    """
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT timestamp, event_type, agent_id, data
            FROM trace_events
            WHERE execution_id = ?
            ORDER BY timestamp
            """,
            (execution_id,),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "timestamp": r[0],
            "event_type": r[1],
            "agent_id": r[2],
            "data": r[3],
        }
        for r in rows
    ]


def render_trace_viewer() -> None:
    """Render the Trace Viewer page.

    Displays:
    - Executions overview table from traces.db
    - Drill-down event table when an execution is selected
    """
    st.header(TRACE_VIEWER_HEADER)

    db_path = _get_db_path()
    if not db_path.exists():
        st.info("No traces.db found. Run an evaluation first.")
        return

    executions = _query_executions(db_path)
    if not executions:
        st.info("No executions recorded yet. Run an evaluation to populate traces.")
        return

    st.dataframe(executions, use_container_width=True)

    execution_ids = [e["execution_id"] for e in executions]
    selected = st.selectbox("Select execution for details", execution_ids)

    if selected:
        st.subheader(f"Events for {selected}")
        events = _query_events(db_path, str(selected))
        st.dataframe(events, use_container_width=True)
