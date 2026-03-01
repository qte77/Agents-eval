"""
Lightweight CLI wrapper for the Agents-eval application.

This wrapper handles help and basic argument parsing quickly without
loading heavy dependencies. It only imports the main application
when actual processing is needed.
"""

import argparse
import shutil
from sys import argv, exit
from typing import Any

from app.data_models.app_models import PROVIDER_REGISTRY

_parser = argparse.ArgumentParser(description="Agents-eval CLI — run MAS evaluation pipeline")

for _flag, _help in [
    ("--version", "Display version information"),
    ("--include-researcher", "Include the researcher agent"),
    ("--include-analyst", "Include the analyst agent"),
    ("--include-synthesiser", "Include the synthesiser agent"),
    ("--pydantic-ai-stream", "Enable streaming output"),
    ("--download-peerread-full-only", "Download all PeerRead data and exit (setup mode)"),
    ("--download-peerread-samples-only", "Download PeerRead sample and exit (setup mode)"),
    ("--cc-teams", "Use Claude Code Agent Teams mode (requires --engine=cc)"),
    ("--no-llm-suggestions", "Disable LLM-assisted suggestions in generated report"),
]:
    _parser.add_argument(_flag, action="store_true", default=None, help=_help)

# S8-F6.1: --generate-report and --skip-eval are mutually exclusive
_eval_group = _parser.add_mutually_exclusive_group()
_eval_group.add_argument(
    "--skip-eval",
    action="store_true",
    default=None,
    help="Skip evaluation after run_manager completes",
)
_eval_group.add_argument(
    "--generate-report",
    action="store_true",
    default=None,
    help="Generate a Markdown report after evaluation completes (incompatible with --skip-eval)",
)

_review_group = _parser.add_mutually_exclusive_group()
_review_group.add_argument(
    "--enable-review-tools",
    action="store_true",
    dest="enable_review_tools",
    help="Enable PeerRead review generation tools (enabled by default)",
)
_review_group.add_argument(
    "--no-review-tools",
    action="store_false",
    dest="enable_review_tools",
    help="Disable PeerRead review generation tools (opt-out)",
)
_parser.set_defaults(enable_review_tools=None)

_parser.add_argument(
    "--chat-provider",
    choices=sorted(PROVIDER_REGISTRY.keys()),
    help="Specify the chat provider to use",
)

for _flag, _help in [
    ("--query", "Specify the query to process"),
    ("--chat-config-file", "Path to the chat configuration file"),
    ("--paper-id", "Paper ID for PeerRead review (supports arxiv IDs like '1105.1072')"),
    ("--judge-provider", "Override Tier 2 LLM provider for judge (default: auto)"),
    ("--judge-model", "Override Tier 2 judge LLM model"),
    ("--cc-solo-dir", "Path to CC solo session export directory for baseline comparison"),
    ("--cc-teams-dir", "Path to CC Agent Teams artifacts directory for baseline comparison"),
    ("--cc-teams-tasks-dir", "Path to CC Agent Teams tasks directory (auto-discovered if omitted)"),
]:
    _parser.add_argument(_flag, help=_help)

_parser.add_argument("--token-limit", type=int, help="Override agent token limit (1000-1000000)")
_parser.add_argument(
    "--peerread-max-papers-per-sample-download",
    type=int,
    help="Max papers to download per split, overrides sample default",
)
_parser.add_argument(
    "--engine",
    default="mas",
    choices=["mas", "cc"],
    help="Execution engine: 'mas' (default) or 'cc' for Claude Code headless",
)


def parse_args(argv: list[str]) -> dict[str, Any]:
    """Parse command line arguments into a dictionary.

    Args:
        argv: List of CLI argument strings (without the program name).

    Returns:
        Dictionary of explicitly-provided arguments (plus engine default).

    Example:
        >>> parse_args(["--chat-provider", "ollama", "--include-researcher"])
        {'chat_provider': 'ollama', 'include_researcher': True, 'engine': 'mas'}
    """
    return {k: v for k, v in vars(_parser.parse_args(argv)).items() if v is not None}


def _run_cc_engine(args: dict[str, Any], cc_teams: bool) -> Any:
    """Run the Claude Code engine and return the result object.

    Args:
        args: Parsed CLI arguments dict (mutated: cc_solo_dir may be set).
        cc_teams: Whether to use Agent Teams mode.

    Returns:
        CCResult object from the engine run.
    """
    from app.engines.cc_engine import build_cc_query, run_cc_solo, run_cc_teams

    query = build_cc_query(args.get("query", ""), args.get("paper_id"), cc_teams=cc_teams)
    cc_result_obj = (
        run_cc_teams(query, timeout=600) if cc_teams else run_cc_solo(query, timeout=600)
    )

    if cc_result_obj.session_dir:
        args["cc_solo_dir"] = cc_result_obj.session_dir

    return cc_result_obj


def _maybe_generate_report(result_dict: dict[str, Any], no_llm_suggestions: bool) -> None:
    """Generate and save a Markdown report if composite result is available.

    Args:
        result_dict: Pipeline result containing composite_result and run_context.
        no_llm_suggestions: Whether to disable LLM-assisted suggestions.
    """
    from datetime import datetime
    from pathlib import Path

    from app.reports.report_generator import generate_report, save_report
    from app.reports.suggestion_engine import SuggestionEngine
    from app.utils.log import logger

    composite_result = result_dict.get("composite_result")
    if composite_result is None:
        logger.warning("--generate-report requested but no evaluation result available")
        return

    engine_obj = SuggestionEngine(no_llm_suggestions=no_llm_suggestions)
    suggestions = engine_obj.generate(composite_result)
    md = generate_report(composite_result, suggestions=suggestions)

    # Reason: use run_context report_path when available; fall back to output/reports
    run_context = result_dict.get("run_context")
    if run_context is not None:
        output_path = run_context.report_path
    else:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        output_path = Path("output") / "reports" / f"{timestamp}.md"

    save_report(md, output_path)
    logger.info(f"Report written to {output_path}")
    print(f"Report saved: {output_path}")


def cli_main() -> None:
    """Run the CLI application entry point.

    Parses arguments, selects the execution engine, runs the pipeline,
    and logs the artifact summary.
    """
    import sys

    args = parse_args(argv[1:])
    engine = args.pop("engine")
    cc_teams = args.pop("cc_teams", False) or False
    generate_report_flag = args.pop("generate_report", False) or False
    no_llm_suggestions = args.pop("no_llm_suggestions", False) or False

    if engine == "cc" and not shutil.which("claude"):
        print(
            "error: --engine=cc requires the 'claude' CLI to be installed and on PATH",
            file=sys.stderr,
        )
        exit(1)

    from asyncio import run

    from app.app import main
    from app.utils.artifact_registry import get_artifact_registry
    from app.utils.log import logger

    logger.info(f"Used arguments: {args}")

    cc_result_obj = _run_cc_engine(args, cc_teams) if engine == "cc" else None

    try:
        result_dict = run(main(**args, engine=engine, cc_result=cc_result_obj, cc_teams=cc_teams))
        if generate_report_flag and result_dict:
            _maybe_generate_report(result_dict, no_llm_suggestions)
    finally:
        logger.info(get_artifact_registry().format_summary_block())


if __name__ == "__main__":
    cli_main()
