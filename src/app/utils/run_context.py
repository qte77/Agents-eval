"""Per-run output directory management for the application.

Provides RunContext dataclass that owns the per-run output directory structure.
Each run creates a timestamped directory under output/runs/ and writes metadata.json.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config.config_app import OUTPUT_PATH

# Reason: module-level constant allows tests to patch without modifying config
OUTPUT_BASE = Path(OUTPUT_PATH)

# Reason: prevents path traversal — only safe chars allowed in directory name components
_SAFE_PATH_RE = re.compile(r"[^a-zA-Z0-9._-]")


def _sanitize_path_component(value: str) -> str:
    """Sanitize a string for safe use in filesystem directory names.

    Replaces any character that is not alphanumeric, dot, hyphen, or underscore
    with an underscore. Prevents path traversal via ``../`` or ``/`` in
    user-controlled values like ``paper_id``.

    Args:
        value: Raw string to sanitize.

    Returns:
        Sanitized string safe for directory name construction.
    """
    return _SAFE_PATH_RE.sub("_", value)


@dataclass
class RunContext:
    """Per-run context owning the output directory for a single application run.

    Created at the start of each main() invocation after the execution_id
    is known. Exposes path helpers for standard output files.

    Attributes:
        engine_type: Engine that produced this run ('mas', 'cc_solo', 'cc_teams').
        paper_id: PeerRead paper identifier.
        execution_id: Unique execution trace ID.
        start_time: Datetime when the run started.
        run_dir: Path to the per-run output directory.
    """

    engine_type: str
    paper_id: str
    execution_id: str
    start_time: datetime
    run_dir: Path

    @classmethod
    def create(
        cls,
        engine_type: str,
        paper_id: str,
        execution_id: str,
        cli_args: dict[str, Any] | None = None,
    ) -> RunContext:
        """Create a RunContext and its output directory.

        Creates output/runs/{category}/{ts}_{engine}_{paper}_{exec_id_8}/
        and writes metadata.json. Category is ``mas`` or ``cc``.

        Args:
            engine_type: Engine identifier ('mas', 'cc_solo', 'cc_teams').
            paper_id: PeerRead paper identifier.
            execution_id: Unique execution trace ID.
            cli_args: Optional CLI arguments dict to persist in metadata.

        Returns:
            RunContext with run_dir created and metadata.json written.
        """
        start_time = datetime.now()
        ts = start_time.strftime("%Y%m%d_%H%M%S")
        safe_engine = _sanitize_path_component(engine_type)
        safe_paper = _sanitize_path_component(paper_id)
        safe_exec_id = _sanitize_path_component(execution_id[:8])
        dir_name = f"{ts}_{safe_engine}_{safe_paper}_{safe_exec_id}"
        category = "cc" if engine_type.startswith("cc") else "mas"

        run_dir = (
            OUTPUT_BASE / "runs" / category / dir_name
        ).resolve()  # CodeQL[py/path-injection]
        if not run_dir.is_relative_to(OUTPUT_BASE.resolve()):
            msg = f"Path traversal detected: {run_dir}"
            raise ValueError(msg)
        run_dir.mkdir(parents=True, exist_ok=True)  # CodeQL[py/path-injection]

        ctx = cls(
            engine_type=engine_type,
            paper_id=paper_id,
            execution_id=execution_id,
            start_time=start_time,
            run_dir=run_dir,
        )
        ctx._write_metadata(cli_args)
        return ctx

    def _write_metadata(self, cli_args: dict[str, Any] | None) -> None:
        """Write metadata.json to the run directory.

        Args:
            cli_args: Optional CLI arguments to include in metadata.
        """
        metadata: dict[str, Any] = {
            "engine_type": self.engine_type,
            "paper_id": self.paper_id,
            "execution_id": self.execution_id,
            "start_time": self.start_time.isoformat(),
            "cli_args": cli_args,
        }
        (self.run_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

    @property
    def stream_path(self) -> Path:
        """Path to the stream output file.

        Returns:
            stream.jsonl for CC engines, stream.json for MAS engine.
        """
        ext = "jsonl" if self.engine_type.startswith("cc") else "json"
        return self.run_dir / f"stream.{ext}"

    @property
    def trace_path(self) -> Path:
        """Path to the trace output file.

        Returns:
            trace.json in run_dir.
        """
        return self.run_dir / "trace.json"

    @property
    def review_path(self) -> Path:
        """Path to the review output file.

        Returns:
            review.json in run_dir.
        """
        return self.run_dir / "review.json"

    @property
    def report_path(self) -> Path:
        """Path to the report output file.

        Returns:
            report.md in run_dir.
        """
        return self.run_dir / "report.md"

    @property
    def evaluation_path(self) -> Path:
        """Path to the evaluation output file.

        Returns:
            evaluation.json in run_dir.
        """
        return self.run_dir / "evaluation.json"

    @property
    def graph_json_path(self) -> Path:
        """Path to the agent graph JSON export file.

        Returns:
            agent_graph.json in run_dir.
        """
        return self.run_dir / "agent_graph.json"

    @property
    def graph_png_path(self) -> Path:
        """Path to the agent graph PNG export file.

        Returns:
            agent_graph.png in run_dir.
        """
        return self.run_dir / "agent_graph.png"


# Reason: module-level singleton matches existing patterns (artifact_registry, trace_collector)
_active_run_context: RunContext | None = None


def get_active_run_context() -> RunContext | None:
    """Get the active per-run context, if any.

    Returns:
        The active RunContext, or None if no run is in progress.
    """
    return _active_run_context


def set_active_run_context(ctx: RunContext | None) -> None:
    """Set or clear the active per-run context.

    Args:
        ctx: RunContext to activate, or None to clear.
    """
    global _active_run_context
    _active_run_context = ctx
