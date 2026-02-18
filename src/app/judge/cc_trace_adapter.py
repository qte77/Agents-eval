"""
Claude Code trace adapter for evaluation pipeline integration.

Parses Claude Code artifacts (solo and teams mode) into GraphTraceData format
for three-tier evaluation pipeline, enabling side-by-side comparison with
PydanticAI MAS runs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from app.data_models.evaluation_models import GraphTraceData
from app.utils.log import logger


class CCTraceAdapter:
    """
    Adapter for parsing Claude Code execution artifacts into GraphTraceData.

    Supports two modes:
    - Teams mode: Parses CC Agent Teams artifacts (config.json, inboxes/, tasks/)
    - Solo mode: Parses single CC session exports (metadata.json, tool_calls.jsonl)

    Auto-detects mode from directory structure.

    Attributes:
        artifacts_dir: Path to CC artifacts directory
        mode: Detected mode ('teams' or 'solo')
    """

    def __init__(self, artifacts_dir: Path, *, tasks_dir: Path | None = None):
        """Initialize adapter with artifacts directory.

        Args:
            artifacts_dir: Path to directory containing CC artifacts (teams mode)
                          or session exports (solo mode)
            tasks_dir: Optional explicit path to tasks directory. If None, will
                      auto-discover for teams mode by checking sibling and child layouts.

        Raises:
            ValueError: If directory does not exist
        """
        if not artifacts_dir.exists():
            raise ValueError(f"Artifacts directory does not exist: {artifacts_dir}")

        self.artifacts_dir = artifacts_dir
        self.mode: Literal["teams", "solo"] = self._detect_mode()
        self.tasks_dir = self._resolve_tasks_dir(tasks_dir)

        logger.debug(
            f"CCTraceAdapter initialized: mode={self.mode}, teams_path={artifacts_dir}, "
            f"tasks_path={self.tasks_dir}"
        )

    def _detect_mode(self) -> Literal["teams", "solo"]:
        """Auto-detect mode from directory structure.

        Teams mode: config.json exists with 'members' array
        Solo mode: Otherwise (or if config.json doesn't have members array)

        Returns:
            Detected mode string
        """
        config_path = self.artifacts_dir / "config.json"

        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
                if "members" in config and isinstance(config["members"], list):
                    return "teams"
                # Valid JSON but no members array - treat as incomplete teams config
                # which will fail during parse with clear error message
                if "team_name" in config or "members" in config:
                    return "teams"
            except json.JSONDecodeError:
                # Malformed JSON in config.json likely indicates attempted teams mode
                # Let parse() handle the error with a clear message
                return "teams"

        return "solo"

    def _resolve_tasks_dir(self, explicit_tasks_dir: Path | None) -> Path | None:
        """Resolve tasks directory path for teams mode.

        Supports two directory layouts:
        1. Sibling layout (real CC): ~/.claude/teams/{name}/ + ~/.claude/tasks/{name}/
        2. Child layout (legacy): teams/{name}/tasks/

        Args:
            explicit_tasks_dir: Explicitly provided tasks directory path

        Returns:
            Resolved tasks directory path, or None if not in teams mode or not found
        """
        # Solo mode doesn't use separate tasks directory
        if self.mode != "teams":
            return None

        # If explicitly provided, use it
        if explicit_tasks_dir is not None:
            if explicit_tasks_dir.exists():
                return explicit_tasks_dir
            logger.warning(f"Explicit tasks_dir does not exist: {explicit_tasks_dir}")
            return None

        # Auto-discovery: try sibling layout first (real CC structure)
        # ~/.claude/teams/{team-name}/ -> ~/.claude/tasks/{team-name}/
        team_name = self.artifacts_dir.name
        sibling_tasks = self.artifacts_dir.parent.parent / "tasks" / team_name

        if sibling_tasks.exists():
            logger.debug(f"Found tasks dir via sibling layout: {sibling_tasks}")
            return sibling_tasks

        # Fallback: child layout (backward compatibility)
        child_tasks = self.artifacts_dir / "tasks"

        if child_tasks.exists():
            logger.debug(f"Found tasks dir via child layout: {child_tasks}")
            return child_tasks

        # No tasks directory found (not an error - tasks are optional)
        logger.debug("No tasks directory found (neither sibling nor child layout)")
        return None

    def parse(self) -> GraphTraceData:
        """Parse CC artifacts into GraphTraceData format.

        Returns:
            GraphTraceData instance ready for Tier 3 evaluation

        Raises:
            ValueError: If artifacts are missing or malformed
        """
        if self.mode == "teams":
            return self._parse_teams_mode()
        else:
            return self._parse_solo_mode()

    def _parse_teams_mode(self) -> GraphTraceData:
        """Parse CC Agent Teams artifacts into GraphTraceData.

        Reads:
        - config.json: team name -> execution_id, members
        - inboxes/*.json: agent messages -> agent_interactions
        - tasks/*.json: task completions -> tool_calls (proxy)

        Returns:
            GraphTraceData with teams mode data

        Raises:
            ValueError: If required artifacts are missing or malformed
        """
        config_path = self.artifacts_dir / "config.json"

        if not config_path.exists():
            raise ValueError("No CC artifacts found: config.json missing in teams mode")

        try:
            config = json.loads(config_path.read_text())
            execution_id = config.get("team_name", "unknown-team")
        except Exception as e:
            raise ValueError(f"Failed to parse config.json: {e}") from e

        # Parse agent interactions from inboxes/
        agent_interactions = self._parse_agent_messages()

        # Parse tool calls from tasks/ (task completions as proxy)
        tool_calls = self._parse_team_tasks()

        # Derive timing data from all timestamps
        timing_data = self._derive_timing_data(agent_interactions, tool_calls)

        # Extract coordination events from task assignments
        coordination_events = self._extract_coordination_events()

        return GraphTraceData(
            execution_id=execution_id,
            agent_interactions=agent_interactions,
            tool_calls=tool_calls,
            timing_data=timing_data,
            coordination_events=coordination_events,
        )

    def _parse_solo_mode(self) -> GraphTraceData:
        """Parse CC solo session artifacts into GraphTraceData.

        Reads:
        - metadata.json: session_id -> execution_id, start_time, end_time
        - tool_calls.jsonl: tool usage events

        Returns:
            GraphTraceData with solo mode data (empty interactions/coordination)

        Raises:
            ValueError: If required artifacts are missing
        """
        metadata_path = self.artifacts_dir / "metadata.json"

        if not metadata_path.exists():
            raise ValueError("No CC artifacts found: metadata.json missing")

        try:
            metadata = json.loads(metadata_path.read_text())
            execution_id = metadata.get("session_id", "unknown-session")
        except Exception as e:
            raise ValueError(f"Failed to parse metadata.json: {e}") from e

        # Parse tool calls from logs
        tool_calls = self._parse_solo_tool_calls()

        # Extract timing from metadata
        timing_data = {
            "start_time": metadata.get("start_time", 0.0),
            "end_time": metadata.get("end_time", 0.0),
        }

        # Solo mode: no agent interactions or coordination
        return GraphTraceData(
            execution_id=execution_id,
            agent_interactions=[],
            tool_calls=tool_calls,
            timing_data=timing_data,
            coordination_events=[],
        )

    def _parse_agent_messages(self) -> list[dict[str, Any]]:
        """Parse agent-to-agent messages from inboxes/ directory.

        Returns:
            List of agent interaction dictionaries
        """
        inboxes_dir = self.artifacts_dir / "inboxes"

        if not inboxes_dir.exists():
            return []

        messages: list[dict[str, Any]] = []

        for msg_file in sorted(inboxes_dir.glob("*.json")):
            try:
                msg_data = json.loads(msg_file.read_text())
                messages.append(msg_data)
            except Exception as e:
                logger.warning(f"Failed to parse message {msg_file}: {e}")

        return messages

    def _parse_team_tasks(self) -> list[dict[str, Any]]:
        """Parse task completions as proxy tool calls.

        Task completions represent coordination work in teams mode.

        Returns:
            List of tool call dictionaries (derived from tasks)
        """
        # Use resolved tasks directory instead of assuming child layout
        if self.tasks_dir is None or not self.tasks_dir.exists():
            return []

        tasks_dir = self.tasks_dir

        tool_calls: list[dict[str, Any]] = []

        for task_file in sorted(tasks_dir.glob("*.json")):
            try:
                task_data = json.loads(task_file.read_text())

                # Map task completion to tool call proxy
                if task_data.get("status") == "completed":
                    tool_call = {
                        "tool_name": f"task_{task_data.get('id', 'unknown')}",
                        "agent_id": task_data.get("owner", "unknown"),
                        "timestamp": task_data.get("completed_at", 0.0),
                        "duration": task_data.get("completed_at", 0.0)
                        - task_data.get("created_at", 0.0),
                        "success": True,
                        "context": task_data.get("title", ""),
                    }
                    tool_calls.append(tool_call)
            except Exception as e:
                logger.warning(f"Failed to parse task {task_file}: {e}")

        return tool_calls

    def _parse_solo_tool_calls(self) -> list[dict[str, Any]]:
        """Parse tool calls from solo session logs.

        Reads tool_calls.jsonl file with one JSON object per line.

        Returns:
            List of tool call dictionaries
        """
        tool_calls_path = self.artifacts_dir / "tool_calls.jsonl"

        if not tool_calls_path.exists():
            return []

        tool_calls: list[dict[str, Any]] = []

        try:
            for line in tool_calls_path.read_text().splitlines():
                if line.strip():
                    tool_call = json.loads(line)
                    tool_calls.append(tool_call)
        except Exception as e:
            logger.warning(f"Failed to parse tool_calls.jsonl: {e}")

        return tool_calls

    def _derive_timing_data(
        self,
        agent_interactions: list[dict[str, Any]],
        tool_calls: list[dict[str, Any]],
    ) -> dict[str, float]:
        """Derive timing data from first/last timestamps across all events.

        Args:
            agent_interactions: List of agent message events
            tool_calls: List of tool call events

        Returns:
            Dictionary with start_time and end_time
        """
        all_timestamps: list[float] = []

        for interaction in agent_interactions:
            if "timestamp" in interaction:
                all_timestamps.append(interaction["timestamp"])

        for tool_call in tool_calls:
            if "timestamp" in tool_call:
                all_timestamps.append(tool_call["timestamp"])

        if not all_timestamps:
            return {"start_time": 0.0, "end_time": 0.0}

        return {"start_time": min(all_timestamps), "end_time": max(all_timestamps)}

    def _extract_coordination_events(self) -> list[dict[str, Any]]:
        """Extract coordination events from teams mode inboxes/*.json messages.

        In teams mode, agent-to-agent messages in inboxes/ represent coordination
        events (task assignments, status updates, completions).

        Returns:
            List of coordination event dictionaries parsed from inbox messages.
            Empty list if no inboxes/ directory or not in teams mode.
        """
        inboxes_dir = self.artifacts_dir / "inboxes"

        if not inboxes_dir.exists():
            return []

        events: list[dict[str, Any]] = []

        for msg_file in sorted(inboxes_dir.glob("*.json")):
            try:
                msg_data = json.loads(msg_file.read_text())
                events.append(msg_data)
            except Exception as e:
                logger.warning(f"Failed to parse inbox message {msg_file}: {e}")

        return events
