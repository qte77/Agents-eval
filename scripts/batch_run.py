#!/usr/bin/env python3
"""Batch composition runner — run app_cli across agent compositions.

For MAS engine (default): runs all 8 agent compositions (2^3 from
researcher/analyst/synthesiser toggles).
For CC engine: runs cc-solo and cc-teams modes only (agent toggles
do not apply).

Usage:
    make app_batch_run ARGS="--paper-ids 1105.1072"
    make app_batch_run ARGS="--paper-ids 1105.1072 --parallel 4 --chat-provider cerebras"
    make app_batch_run ARGS="--paper-ids 1105.1072 --compositions manager-only"
    make app_batch_run ARGS="--paper-ids 1105.1072 --engine cc"
    make app_batch_run ARGS="--paper-ids 1105.1072 --engine cc --compositions cc-solo"
    make app_batch_run ARGS="--paper-ids 1105.1072 --engine cc --judge-provider openai"
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

# Reason: script lives in scripts/, src/ is the package root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.data_models.app_models import PROVIDER_REGISTRY

_AGENT_TOGGLES = ("researcher", "analyst", "synthesiser")

# Reason: map common exit codes to hints so failures are actionable
_EXIT_HINTS: dict[int, str] = {
    1: "general error",
    2: "argument/config error",
    137: "killed (OOM or timeout)",
    -9: "killed (SIGKILL)",
    -15: "terminated (SIGTERM)",
}


def _all_compositions() -> list[dict[str, bool]]:
    """Generate all 8 agent compositions (2^3 boolean combinations).

    Returns:
        List of dicts mapping include_<agent> keys to booleans.
    """
    compositions: list[dict[str, bool]] = []
    for r in (False, True):
        for a in (False, True):
            for s in (False, True):
                compositions.append(
                    {
                        "include_researcher": r,
                        "include_analyst": a,
                        "include_synthesiser": s,
                    }
                )
    return compositions


def _cc_compositions() -> list[dict[str, bool]]:
    """Generate CC engine compositions: solo and teams.

    Returns:
        List of dicts with cc_teams boolean.
    """
    return [{"cc_teams": False}, {"cc_teams": True}]


def _composition_name(comp: dict[str, bool]) -> str:
    """Generate a readable name for a composition.

    Handles both MAS (agent toggles) and CC (solo/teams) compositions.

    Args:
        comp: Dict of composition toggles.

    Returns:
        Human-readable name like 'researcher+analyst', 'manager-only',
        'cc-solo', or 'cc-teams'.
    """
    if "cc_teams" in comp:
        return "cc-teams" if comp["cc_teams"] else "cc-solo"
    active = [toggle for toggle in _AGENT_TOGGLES if comp.get(f"include_{toggle}", False)]
    return "+".join(active) if active else "manager-only"


def _build_cli_args(
    paper_id: str,
    comp: dict[str, bool],
    engine: str,
    chat_provider: str | None,
    judge_provider: str | None,
    extra_args: list[str],
) -> str:
    """Construct the ARGS= string for make app_cli.

    Args:
        paper_id: Paper ID to evaluate.
        comp: Composition toggle dict.
        engine: Execution engine ('mas' or 'cc').
        chat_provider: LLM provider override, or None for default.
        judge_provider: Judge LLM provider override, or None for default.
        extra_args: Additional pass-through arguments.

    Returns:
        CLI argument string for make app_cli ARGS="...".
    """
    parts = [f"--paper-id={paper_id}", f"--engine={engine}"]

    if "cc_teams" in comp:
        if comp["cc_teams"]:
            parts.append("--cc-teams")
    else:
        for toggle in _AGENT_TOGGLES:
            if comp.get(f"include_{toggle}", False):
                parts.append(f"--include-{toggle}")

    if chat_provider:
        parts.append(f"--chat-provider={chat_provider}")

    if judge_provider:
        parts.append(f"--judge-provider={judge_provider}")

    parts.extend(extra_args)
    return " ".join(parts)


def _extract_error_line(stderr: str) -> str | None:
    """Extract the most useful error line from subprocess stderr.

    Filters out make noise (e.g. ``make[1]: ***``) and returns the last
    meaningful line — typically the Python exception message.

    Args:
        stderr: Raw stderr output from subprocess.

    Returns:
        Single error line, or None if nothing useful found.
    """
    # Reason: loguru logs non-error levels to stderr; skip them to surface
    # the actual exception line.
    _LOGURU_NON_ERROR = ("| TRACE", "| DEBUG", "| INFO", "| SUCCESS", "| WARNING")

    for line in reversed(stderr.strip().splitlines()):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip make error lines and pure tilde underline carets
        is_make = stripped.startswith("make[") or stripped.startswith("make:")
        if is_make or stripped.lstrip("~ ^") == "":
            continue
        # Skip loguru non-error log lines (INFO, DEBUG, WARNING, etc.)
        if any(level in stripped for level in _LOGURU_NON_ERROR):
            continue
        return stripped
    return None


def _run_one(
    paper_id: str,
    comp: dict[str, bool],
    engine: str,
    chat_provider: str | None,
    judge_provider: str | None,
    extra_args: list[str],
    verbose: bool,
) -> dict[str, Any]:
    """Run a single composition via make app_cli.

    Args:
        paper_id: Paper ID to evaluate.
        comp: Composition toggle dict.
        engine: Execution engine.
        chat_provider: LLM provider override.
        judge_provider: Judge LLM provider override.
        extra_args: Pass-through arguments.
        verbose: Whether to show full subprocess output.

    Returns:
        Result dict with name, paper_id, status, and exit_code.
    """
    name = _composition_name(comp)
    cli_args = _build_cli_args(paper_id, comp, engine, chat_provider, judge_provider, extra_args)
    label = f"[{paper_id}] {name}"

    print(f"  {label}: starting ...")

    try:
        result = subprocess.run(
            ["make", "app_cli", f"ARGS={cli_args}"],
            capture_output=not verbose,
            text=True,
            check=False,
        )
    except OSError as exc:
        print(f"  {label}: ERROR ({exc})")
        return {
            "name": name,
            "paper_id": paper_id,
            "status": "fail",
            "exit_code": -1,
            "error": str(exc),
        }

    if result.returncode == 0:
        print(f"  {label}: OK")
        return {"name": name, "paper_id": paper_id, "status": "pass", "exit_code": 0}

    # Reason: filter make noise (e.g. "make[1]: ***") to surface the actual error
    error_line = _extract_error_line(result.stderr) if result.stderr else None
    hint = _EXIT_HINTS.get(result.returncode, "")
    hint_suffix = f" — {hint}" if hint else ""
    print(f"  {label}: FAILED (exit {result.returncode}{hint_suffix})")
    if error_line:
        print(f"    -> {error_line}")

    return {
        "name": name,
        "paper_id": paper_id,
        "status": "fail",
        "exit_code": result.returncode,
        "error": error_line,
    }


def _print_summary(results: list[dict[str, Any]]) -> None:
    """Print pass/fail summary.

    Args:
        results: List of result dicts from _run_one.
    """
    passed = [r for r in results if r["status"] == "pass"]
    failed = [r for r in results if r["status"] == "fail"]

    print(f"\n{'=' * 50}")
    print(f"Results: {len(passed)} passed, {len(failed)} failed, {len(results)} total")

    if failed:
        print("\nFailed:")
        for r in failed:
            hint = _EXIT_HINTS.get(r["exit_code"], "")
            hint_suffix = f" — {hint}" if hint else ""
            line = f"  - [{r['paper_id']}] {r['name']} (exit {r['exit_code']}{hint_suffix})"
            if r.get("error"):
                line += f": {r['error']}"
            print(line)


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed argument namespace.
    """
    providers = sorted(PROVIDER_REGISTRY.keys())
    mas_names = [_composition_name(c) for c in _all_compositions()]
    cc_names = [_composition_name(c) for c in _cc_compositions()]
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--paper-ids",
        required=True,
        help="Comma-separated paper IDs (e.g. '1105.1072,1205.2653')",
    )
    parser.add_argument(
        "--chat-provider",
        choices=providers,
        default=None,
        help=f"LLM provider ({', '.join(providers)})",
    )
    parser.add_argument(
        "--engine",
        choices=["mas", "cc"],
        default="mas",
        help="Execution engine (default: mas)",
    )
    parser.add_argument(
        "--judge-provider",
        choices=providers,
        default=None,
        help=f"Judge LLM provider override ({', '.join(providers)})",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        metavar="N",
        help="Concurrent subprocess count (default: 1, sequential)",
    )
    parser.add_argument(
        "--compositions",
        default=None,
        metavar="NAME[,NAME,...]",
        help=(
            "Filter by name, comma-separated. "
            f"MAS: {{{','.join(mas_names)}}}; "
            f"CC: {{{','.join(cc_names)}}}"
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Write JSON results file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full subprocess output",
    )
    parser.add_argument(
        "passthrough",
        nargs="*",
        help="Extra args forwarded to app_cli (after '--')",
    )
    # Reason: show help instead of cryptic error when invoked with no args
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def main() -> None:
    """Entry point: run all compositions for each paper and print summary."""
    args = _parse_args()

    paper_ids = [p.strip() for p in args.paper_ids.split(",") if p.strip()]

    # Reason: CC engine ignores agent toggles — only solo and teams modes apply
    all_comps = _cc_compositions() if args.engine == "cc" else _all_compositions()

    # Filter compositions if requested
    if args.compositions:
        wanted = {c.strip() for c in args.compositions.split(",")}
        all_comps = [c for c in all_comps if _composition_name(c) in wanted]
        if not all_comps:
            print(f"error: no compositions matched filter: {args.compositions}", file=sys.stderr)
            sys.exit(1)

    total = len(paper_ids) * len(all_comps)
    print(f"Running {total} combinations ({len(paper_ids)} papers x {len(all_comps)} compositions)")
    print()

    results: list[dict[str, Any]] = []

    if args.parallel > 1:
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {
                executor.submit(
                    _run_one,
                    pid,
                    comp,
                    args.engine,
                    args.chat_provider,
                    args.judge_provider,
                    args.passthrough,
                    args.verbose,
                ): (pid, comp)
                for pid in paper_ids
                for comp in all_comps
            }
            for future in as_completed(futures):
                results.append(future.result())
    else:
        for pid in paper_ids:
            for comp in all_comps:
                results.append(
                    _run_one(
                        pid,
                        comp,
                        args.engine,
                        args.chat_provider,
                        args.judge_provider,
                        args.passthrough,
                        args.verbose,
                    )
                )

    _print_summary(results)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, indent=2))
        print(f"\nResults written to {output_path}")

    if any(r["status"] == "fail" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
