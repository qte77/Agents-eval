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
from typing import Any, Iterator

from pydantic import BaseModel, Field

from app.utils.log import logger

# Team-related event types captured from the live JSONL stream
_TEAM_EVENT_TYPES = {"TeamCreate", "Task"}


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


def check_cc_available() -> bool:
    """Check whether the Claude Code CLI is installed and on PATH.

    Returns:
        True if 'claude' binary is found on PATH, False otherwise.

    Example:
        >>> if not check_cc_available():
        ...     raise RuntimeError("claude CLI required for --engine=cc")
    """
    return shutil.which("claude") is not None


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
    execution_id = "unknown"
    output_data: dict[str, Any] = {}
    team_artifacts: list[dict[str, Any]] = []

    for raw_line in stream:
        line = raw_line.strip()
        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            logger.debug(f"Skipping malformed JSONL line: {line[:80]}")
            continue

        event_type = event.get("type", "")

        if event_type == "system" and event.get("subtype") == "init":
            # S8-F3: extract session_id from init event as execution_id
            session_id = event.get("session_id")
            if session_id:
                execution_id = session_id

        elif event_type == "result":
            # S8-F3: merge result fields into output_data
            for key in ("duration_ms", "total_cost_usd", "num_turns"):
                if key in event:
                    output_data[key] = event[key]

        elif event_type in _TEAM_EVENT_TYPES:
            team_artifacts.append(event)

    return CCResult(
        execution_id=execution_id,
        output_data=output_data,
        team_artifacts=team_artifacts,
    )


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
        RuntimeError: If the subprocess exits with non-zero code or times out.
        ValueError: If stdout cannot be parsed as JSON.

    Example:
        >>> result = run_cc_solo("Summarise this paper", timeout=300)
        >>> print(result.execution_id)
    """
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
        RuntimeError: If the subprocess exits with non-zero code or times out.

    Example:
        >>> result = run_cc_teams("Review paper 1234 using a team", timeout=600)
        >>> print(len(result.team_artifacts))
    """
    # S8-F3: teams env var required for CC agent orchestration
    env = {**os.environ, "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
    logger.info(f"CC teams: running query (timeout={timeout}s)")

    try:
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        ) as proc:
            try:
                result = parse_stream_json(iter(proc.stdout or []))
            except subprocess.TimeoutExpired as e:
                proc.kill()
                raise RuntimeError(f"CC timed out after {e.timeout}s") from e

            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"CC failed with exit code {proc.returncode}")

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"CC timed out after {e.timeout}s") from e

    logger.info(f"CC teams completed: execution_id={result.execution_id}")
    return result
