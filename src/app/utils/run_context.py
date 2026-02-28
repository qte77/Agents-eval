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

# Reason: module-level constant allows tests to patch without modifying config
OUTPUT_BASE = Path("output")

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

        Creates output/runs/{YYYYMMDD_HHMMSS}_{engine_type}_{paper_id}_{exec_id_8}/
        and writes metadata.json.

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
        exec_id_short = execution_id[:8]
        safe_engine = _sanitize_path_component(engine_type)
        safe_paper = _sanitize_path_component(paper_id)
        dir_name = f"{ts}_{safe_engine}_{safe_paper}_{exec_id_short}"

        run_dir = OUTPUT_BASE / "runs" / dir_name
        run_dir.mkdir(parents=True, exist_ok=True)

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
            trace.jsonl in run_dir.
        """
        return self.run_dir / "trace.jsonl"

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
