"""Consolidated Claude Code (CC) engine for solo and teams execution.

Replaces duplicated subprocess logic scattered across run_cli.py, sweep_runner.py,
and shell scripts with a single, well-tested Python module.

Critical constraint (from AGENT_LEARNINGS.md): CC teams artifacts are ephemeral in
``claude -p`` print mode. This module uses ``--output-format stream-json`` with
``Popen`` to parse team events from the live stream instead of filesystem artifacts.
"""

# S8-F3: consolidate CC subprocess into cc_engine module

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.data_models.evaluation_models import GraphTraceData

from pydantic import BaseModel, Field

from app.config.config_app import CC_STREAMS_PATH, DEFAULT_REVIEW_PROMPT_TEMPLATE
from app.utils.artifact_registry import get_artifact_registry
from app.utils.log import logger

# Team-related event types captured from the live JSONL stream
_TEAM_EVENT_TYPES = {"TeamCreate", "Task"}

# CWE-78 mitigation: max query length to prevent unbounded input to subprocess
_CC_QUERY_MAX_LENGTH = 10_000


def _sanitize_cc_query(query: str) -> str:
    """Validate and sanitize a query string before passing to CC subprocess.

    Mitigates CWE-78 argument injection by enforcing length limits,
    rejecting empty input, and blocking dash-prefixed queries that could
    smuggle CLI flags into the subprocess argument list.

    Args:
        query: Raw query string from user input.

    Returns:
        Stripped query string.

    Raises:
        ValueError: If query is empty, whitespace-only, starts with ``-``,
            or exceeds max length.
    """
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Query must not be empty")
    if cleaned.startswith("-"):
        raise ValueError("Query must not start with '-' (argument injection risk)")
    if len(cleaned) > _CC_QUERY_MAX_LENGTH:
        raise ValueError(f"Query length {len(cleaned)} exceeds maximum {_CC_QUERY_MAX_LENGTH}")
    return cleaned


class CCResult(BaseModel):
    """Result of a Claude Code execution (solo or teams mode).

    Attributes:
        execution_id: Session or team identifier extracted from stream.
        output_data: Parsed JSON output (solo) or aggregated result data (teams).
        session_dir: Solo session directory path (from JSON output), if present.
        team_artifacts: Team-related events parsed from stream-json (teams mode).
    """

    execution_id: str = Field(default="unknown", description="Session or team execution ID")
    output_data: dict[str, Any] = Field(
        default_factory=dict, description="Parsed output from CC process"
    )
    session_dir: str | None = Field(
        default=None, description="Solo session directory (if provided by CC)"
    )
    team_artifacts: list[dict[str, Any]] = Field(
        default_factory=list, description="Team events parsed from stream-json output"
    )


def build_cc_query(query: str, paper_id: str | None = None, cc_teams: bool = False) -> str:
    """Build a non-empty query for CC engine execution.

    When no explicit query is provided but a paper_id is available, generates
    a default review prompt using DEFAULT_REVIEW_PROMPT_TEMPLATE. In teams mode,
    prepends a team instruction to increase likelihood of CC spawning teammates.

    Args:
        query: User-provided query string (may be empty).
        paper_id: Optional PeerRead paper ID for auto-generating a prompt.
        cc_teams: Whether CC teams mode is enabled.

    Returns:
        Non-empty query string for CC subprocess.

    Raises:
        ValueError: When both query and paper_id are empty/None.

    Example:
        >>> build_cc_query("", paper_id="1105.1072")
        "Generate a structured peer review for paper '1105.1072'."
        >>> build_cc_query("", paper_id="1105.1072", cc_teams=True)
        "Use a team of agents. Generate a structured peer review for paper '1105.1072'."
    """
    if query:
        return query

    if not paper_id:
        raise ValueError(
            "Either query or paper_id must be provided. Use --query or --paper-id to specify input."
        )

    generated = DEFAULT_REVIEW_PROMPT_TEMPLATE.format(paper_id=paper_id)
    if cc_teams:
        return f"Use a team of agents. {generated}"
    return generated


def check_cc_available() -> bool:
    """Check whether the Claude Code CLI is installed and on PATH.

    Returns:
        True if 'claude' binary is found on PATH, False otherwise.

    Example:
        >>> if not check_cc_available():
        ...     raise RuntimeError("claude CLI required for --engine=cc")
    """
    return shutil.which("claude") is not None


def _parse_jsonl_line(line: str) -> dict[str, Any] | None:
    """Parse a single JSONL line, returning None on blank or malformed input.

    Args:
        line: Raw line from CC stdout.

    Returns:
        Parsed dict, or None if the line is blank or invalid JSON.
    """
    stripped = line.strip()
    if not stripped:
        return None
    try:
        parsed: dict[str, Any] | None = json.loads(stripped)
        return parsed
    except json.JSONDecodeError:
        logger.debug(f"Skipping malformed JSONL line: {stripped[:80]}")
        return None


# S10-F1: include "result" so CC review text is captured in output_data
_RESULT_KEYS = ("duration_ms", "total_cost_usd", "num_turns", "result")


def _apply_event(
    event: dict[str, Any],
    state: dict[str, Any],
) -> None:
    """Mutate ``state`` in-place based on ``event`` type.

    Recognised events:
    - ``type=system, subtype=init`` → updates ``execution_id``
    - ``type=result`` → updates ``output_data`` with timing/cost fields
    - ``type`` in ``_TEAM_EVENT_TYPES`` → appends to ``team_artifacts``

    Args:
        event: Parsed JSONL event dict.
        state: Accumulator dict with keys ``execution_id``, ``output_data``,
            ``team_artifacts``.
    """
    event_type = event.get("type", "")
    if event_type == "system" and event.get("subtype") == "init":
        session_id = event.get("session_id")
        if session_id:
            state["execution_id"] = session_id
    elif event_type == "result":
        state["output_data"].update({k: event[k] for k in _RESULT_KEYS if k in event})
    elif event_type in _TEAM_EVENT_TYPES:
        state["team_artifacts"].append(event)


def parse_stream_json(stream: Iterator[str]) -> CCResult:
    """Parse a JSONL stream from CC ``--output-format stream-json`` into CCResult.

    Extracts:
    - ``type=system, subtype=init`` → ``session_id`` becomes ``execution_id``
    - ``type=result`` → ``duration_ms``, ``total_cost_usd``, ``num_turns`` → ``output_data``
    - ``type=TeamCreate`` or ``type=Task`` → appended to ``team_artifacts``

    Skips blank lines and malformed JSON without raising.

    Args:
        stream: Iterator of raw JSONL lines (strings) from CC stdout.

    Returns:
        CCResult populated from parsed events.

    Example:
        >>> lines = ['{"type": "result", "num_turns": 3}']
        >>> result = parse_stream_json(iter(lines))
        >>> result.output_data["num_turns"]
        3
    """
    state: dict[str, Any] = {
        "execution_id": "unknown",
        "output_data": {},
        "team_artifacts": [],
    }

    for raw_line in stream:
        event = _parse_jsonl_line(raw_line)
        if event is not None:
            _apply_event(event, state)

    return CCResult(
        execution_id=state["execution_id"],
        output_data=state["output_data"],
        team_artifacts=state["team_artifacts"],
    )


def extract_cc_review_text(cc_result: CCResult) -> str:
    """Extract review text from a CC execution result.

    Args:
        cc_result: CCResult from solo or teams execution.

    Returns:
        Review text string, or empty string if not present.

    Example:
        >>> result = CCResult(execution_id="x", output_data={"result": "Good paper."})
        >>> extract_cc_review_text(result)
        'Good paper.'
    """
    return str(cc_result.output_data.get("result", ""))


def cc_result_to_graph_trace(cc_result: CCResult) -> GraphTraceData:
    """Build GraphTraceData from a CCResult for graph-based analysis.

    Solo mode: returns minimal GraphTraceData with empty lists (the composite
    scorer detects single_agent_mode and redistributes weights).

    Teams mode: maps Task events to agent_interactions and TeamCreate events
    to coordination_events.

    Args:
        cc_result: CCResult from solo or teams execution.

    Returns:
        GraphTraceData populated from CC artifacts.

    Example:
        >>> result = CCResult(execution_id="solo-1", output_data={})
        >>> trace = cc_result_to_graph_trace(result)
        >>> trace.execution_id
        'solo-1'
    """
    from app.data_models.evaluation_models import GraphTraceData

    agent_interactions: list[dict[str, Any]] = []
    coordination_events: list[dict[str, Any]] = []

    for artifact in cc_result.team_artifacts:
        event_type = artifact.get("type", "")
        if event_type == "Task":
            agent_interactions.append(artifact)
        elif event_type == "TeamCreate":
            coordination_events.append(artifact)

    return GraphTraceData(
        execution_id=cc_result.execution_id,
        agent_interactions=agent_interactions,
        coordination_events=coordination_events,
    )


def _tee_stream(stream: Iterator[str], path: Path) -> Iterator[str]:
    """Yield lines from ``stream`` while writing each to ``path`` incrementally.

    Opens ``path`` for writing on first call and closes after the stream is
    exhausted. This ensures lines are persisted as they arrive (tee pattern)
    rather than buffered until the process exits.

    Args:
        stream: Iterator of raw lines from CC stdout.
        path: Destination file path for the JSONL copy.

    Yields:
        Each line from ``stream`` unchanged.
    """
    with path.open("w", encoding="utf-8") as fh:
        for line in stream:
            fh.write(line if line.endswith("\n") else line + "\n")
            fh.flush()
            yield line


def _rename_stream_file(src: Path, new_name: str) -> Path:
    """Rename ``src`` to ``src.parent / new_name``, returning the new path.

    Args:
        src: Existing file path.
        new_name: New filename (basename only).

    Returns:
        New Path after rename.
    """
    dest = src.parent / new_name
    src.rename(dest)
    return dest


def _persist_solo_stream(raw_stdout: str, execution_id: str) -> None:
    """Write raw solo JSON stdout to ``CC_STREAMS_PATH`` and register artifact.

    Creates the target directory lazily. Filename pattern:
    ``cc_solo_{execution_id}_{timestamp}.json``.

    Args:
        raw_stdout: Raw stdout string from the CC solo subprocess.
        execution_id: Execution ID extracted from parsed JSON (may be "unknown").
    """
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    streams_dir = Path(CC_STREAMS_PATH)
    streams_dir.mkdir(parents=True, exist_ok=True)
    out_path = streams_dir / f"cc_solo_{execution_id}_{ts}.json"
    out_path.write_text(raw_stdout, encoding="utf-8")
    get_artifact_registry().register("CC solo stream", out_path)


def run_cc_solo(query: str, timeout: int = 600) -> CCResult:
    """Run Claude Code in solo (headless print) mode.

    Uses blocking ``subprocess.run`` with ``--output-format json``. The full JSON
    response is returned as a single object after the process exits.

    Args:
        query: Prompt string passed to ``claude -p``.
        timeout: Maximum seconds to wait for the process. Defaults to 600.

    Returns:
        CCResult with output_data from parsed JSON stdout and session_dir if present.

    Raises:
        ValueError: If query fails sanitization (empty, dash-prefixed, over-length)
            or if stdout cannot be parsed as JSON.
        RuntimeError: If the subprocess exits with non-zero code or times out.

    Example:
        >>> result = run_cc_solo("Summarise this paper", timeout=300)
        >>> print(result.execution_id)
    """
    query = _sanitize_cc_query(query)
    cmd = ["claude", "-p", query, "--output-format", "json"]
    logger.info(f"CC solo: running query (timeout={timeout}s)")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"CC timed out after {e.timeout}s") from e

    if proc.returncode != 0:
        raise RuntimeError(f"CC failed: {proc.stderr}")

    try:
        data: dict[str, Any] = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ValueError(f"CC output not valid JSON: {e}") from e

    execution_id = data.get("execution_id", data.get("session_id", "unknown"))
    session_dir: str | None = data.get("session_dir")

    _persist_solo_stream(proc.stdout, execution_id)

    logger.info(f"CC solo completed: execution_id={execution_id}")
    return CCResult(
        execution_id=execution_id,
        output_data=data,
        session_dir=session_dir,
    )


def run_cc_teams(query: str, timeout: int = 600) -> CCResult:
    """Run Claude Code in teams (agent orchestration) mode.

    Uses ``subprocess.Popen`` with ``--output-format stream-json`` and the
    ``CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`` environment variable. Team events
    (``TeamCreate``, ``Task``) are parsed from the live JSONL stream, since teams
    artifacts are ephemeral in print mode and not available on the filesystem after
    the process exits.

    Args:
        query: Prompt string passed to ``claude -p``.
        timeout: Maximum seconds to allow the process to run. Defaults to 600.

    Returns:
        CCResult with team_artifacts populated from stream events.

    Raises:
        ValueError: If query is empty, whitespace-only, or exceeds max length.
        RuntimeError: If the subprocess exits with non-zero code or times out.

    Example:
        >>> result = run_cc_teams("Review paper 1234 using a team", timeout=600)
        >>> print(len(result.team_artifacts))
    """
    query = _sanitize_cc_query(query)
    # S8-F3: teams env var required for CC agent orchestration
    env = {**os.environ, "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
    logger.info(f"CC teams: running query (timeout={timeout}s)")

    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    # Reason: filename uses a placeholder timestamp; renamed after execution_id is known
    streams_dir = Path(CC_STREAMS_PATH)
    streams_dir.mkdir(parents=True, exist_ok=True)
    stream_path = streams_dir / f"cc_teams_{ts}.jsonl"

    try:
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            # S10-F1: new session so killpg can reach teammate child processes
            start_new_session=True,
        ) as proc:
            try:
                tee_stream = _tee_stream(iter(proc.stdout or []), stream_path)
                result = parse_stream_json(tee_stream)
            except subprocess.TimeoutExpired as e:
                # S10-F1: kill entire process group, not just the lead process
                import signal

                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.kill()
                raise RuntimeError(f"CC timed out after {e.timeout}s") from e

            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"CC failed with exit code {proc.returncode}")

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"CC timed out after {e.timeout}s") from e

    # Rename to include execution_id now that it is known
    final_path = _rename_stream_file(stream_path, f"cc_teams_{result.execution_id}_{ts}.jsonl")
    get_artifact_registry().register("CC teams stream", final_path)

    logger.info(f"CC teams completed: execution_id={result.execution_id}")
    return result
