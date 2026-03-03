#!/usr/bin/env python3
"""Batch summarize all existing runs and sweeps.

Reads evaluation.json from each run directory and results.json from each
sweep directory, then writes a consolidated summary to OUTPUT_PATH/summary.md.

Usage:
    make app_batch_eval                          # summarize all runs + sweeps
    make app_batch_eval ARGS="--runs-only"       # summarize runs only
    make app_batch_eval ARGS="--sweeps-only"     # summarize sweeps only
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Reason: script lives in scripts/, src/ is the package root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.config.config_app import CC_RUNS_PATH, MAS_RUNS_PATH, OUTPUT_PATH

SWEEPS_PATH = f"{OUTPUT_PATH}/sweeps"
SUMMARY_PATH = Path(f"{OUTPUT_PATH}/summary.md")


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file, returning empty dict if missing."""
    if not path.exists():
        return {}
    return json.loads(path.read_text())  # type: ignore[no-any-return]


def _fmt(val: float | None) -> str:
    """Format a float score, or '-' if None."""
    return f"{val:.3f}" if val is not None else "-"


def _collect_runs() -> list[dict[str, Any]]:
    """Collect metadata + evaluation data from all run directories."""
    rows: list[dict[str, Any]] = []
    for engine, runs_path in [("mas", MAS_RUNS_PATH), ("cc", CC_RUNS_PATH)]:
        base = Path(runs_path)
        if not base.exists():
            continue
        for run_dir in sorted(base.iterdir()):
            if not run_dir.is_dir():
                continue
            meta = _load_json(run_dir / "metadata.json")
            if not meta:
                continue
            evaluation = _load_json(run_dir / "evaluation.json")
            rows.append(
                {
                    "engine": engine,
                    "dir": run_dir.name,
                    "paper_id": meta.get("paper_id", "unknown"),
                    "engine_type": meta.get("engine_type", engine),
                    "has_eval": bool(evaluation),
                    "score": evaluation.get("composite_score"),
                    "t1": evaluation.get("tier1_score"),
                    "t2": evaluation.get("tier2_score"),
                    "t3": evaluation.get("tier3_score"),
                    "recommendation": evaluation.get("recommendation", ""),
                }
            )
    return rows


def _collect_sweeps() -> list[dict[str, Any]]:
    """Collect results from all sweep directories."""
    sweeps: list[dict[str, Any]] = []
    base = Path(SWEEPS_PATH)
    if not base.exists():
        return sweeps
    for sweep_dir in sorted(base.iterdir()):
        results_path = sweep_dir / "results.json"
        if not sweep_dir.is_dir() or not results_path.exists():
            continue
        data = json.loads(results_path.read_text())
        scores = [e["result"]["composite_score"] for e in data if "result" in e]
        compositions = {
            "+".join(k.replace("include_", "") for k, v in e["composition"].items() if v)
            or "manager-only"
            for e in data
        }
        sweeps.append(
            {
                "dir": sweep_dir.name,
                "n_results": len(data),
                "compositions": sorted(compositions),
                "mean_score": statistics.mean(scores) if scores else 0.0,
                "stddev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
            }
        )
    return sweeps


def _generate_summary(runs: list[dict[str, Any]], sweeps: list[dict[str, Any]]) -> str:
    """Generate consolidated markdown summary."""
    lines = [
        "# Evaluation Summary",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    if runs:
        evaluated = [r for r in runs if r["has_eval"]]
        skipped = [r for r in runs if not r["has_eval"]]
        scores = [r["score"] for r in evaluated if r["score"] is not None]

        lines.extend(
            [
                f"## Runs ({len(evaluated)} evaluated, {len(skipped)} skipped)",
                "",
                "| Run | Engine | Paper | Score | T1 | T2 | T3 | Rec |",
                "|-----|--------|-------|-------|----|----|----|-----|",
            ]
        )
        for r in evaluated:
            lines.append(
                f"| {r['dir']} | {r['engine_type']} | {r['paper_id']} "
                f"| {_fmt(r['score'])} | {_fmt(r['t1'])} | {_fmt(r['t2'])} "
                f"| {_fmt(r['t3'])} | {r['recommendation']} |"
            )

        if scores:
            lines.extend(
                [
                    "",
                    f"**Aggregate**: n={len(scores)}, "
                    f"mean={statistics.mean(scores):.3f}, "
                    f"stddev={statistics.stdev(scores) if len(scores) > 1 else 0.0:.3f}, "
                    f"min={min(scores):.3f}, max={max(scores):.3f}",
                ]
            )

        if skipped:
            lines.extend(
                [
                    "",
                    "**Skipped** (no evaluation.json): " + ", ".join(r["dir"] for r in skipped),
                ]
            )
        lines.append("")

    if sweeps:
        lines.extend(
            [
                f"## Sweeps ({len(sweeps)} total)",
                "",
                "| Sweep | Results | Compositions | Mean Score | Stddev |",
                "|-------|---------|-------------|------------|--------|",
            ]
        )
        for s in sweeps:
            comps = ", ".join(s["compositions"])
            lines.append(
                f"| {s['dir']} | {s['n_results']} | {comps} "
                f"| {s['mean_score']:.3f} | {s['stddev']:.3f} |"
            )
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--runs-only", action="store_true", help="Summarize runs only")
    group.add_argument("--sweeps-only", action="store_true", help="Summarize sweeps only")
    return parser.parse_args()


def main() -> None:
    """Entry point: collect data and write consolidated summary."""
    args = parse_args()

    runs = _collect_runs() if not args.sweeps_only else []
    sweeps = _collect_sweeps() if not args.runs_only else []

    summary = _generate_summary(runs, sweeps)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(summary)
    print(summary)
    print(f"\nWritten to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
