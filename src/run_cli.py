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


if __name__ == "__main__":
    import sys
    from datetime import datetime

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
    from app.utils.log import logger

    logger.info(f"Used arguments: {args}")

    if engine == "cc":
        from app.engines.cc_engine import run_cc_solo, run_cc_teams

        query = args.get("query", "")
        if cc_teams:
            cc_result = run_cc_teams(query, timeout=600)
        else:
            cc_result = run_cc_solo(query, timeout=600)

        if cc_result.session_dir:
            args["cc_solo_dir"] = cc_result.session_dir

    result_dict = run(main(**args))

    # S8-F6.1: generate report after evaluation if requested
    if generate_report_flag and result_dict:
        composite_result = result_dict.get("composite_result")
        if composite_result is not None:
            from pathlib import Path

            from app.reports.report_generator import generate_report, save_report
            from app.reports.suggestion_engine import SuggestionEngine

            engine_obj = SuggestionEngine(no_llm_suggestions=no_llm_suggestions)
            suggestions = engine_obj.generate(composite_result)
            md = generate_report(composite_result, suggestions=suggestions)

            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            output_path = Path("results") / "reports" / f"{timestamp}.md"
            save_report(md, output_path)
            logger.info(f"Report written to {output_path}")
            print(f"Report saved: {output_path}")
        else:
            logger.warning("--generate-report requested but no evaluation result available")
