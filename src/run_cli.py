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

_parser = argparse.ArgumentParser(description="Agents-eval CLI — run MAS evaluation pipeline")

for _flag, _help in [
    ("--version", "Display version information"),
    ("--include-researcher", "Include the researcher agent"),
    ("--include-analyst", "Include the analyst agent"),
    ("--include-synthesiser", "Include the synthesiser agent"),
    ("--pydantic-ai-stream", "Enable streaming output"),
    ("--skip-eval", "Skip evaluation after run_manager completes"),
    ("--download-peerread-full-only", "Download all PeerRead data and exit (setup mode)"),
    ("--download-peerread-samples-only", "Download PeerRead sample and exit (setup mode)"),
]:
    _parser.add_argument(_flag, action="store_true", default=None, help=_help)

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

for _flag, _help in [
    ("--chat-provider", "Specify the chat provider to use"),
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
    import json
    import subprocess
    import sys

    args = parse_args(argv[1:])
    engine = args.pop("engine")

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
        query = args.get("query", "")
        try:
            result = subprocess.run(
                ["claude", "-p", query, "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                raise RuntimeError(f"CC failed: {result.stderr}")
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise ValueError(f"CC output not valid JSON: {e}") from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"CC timed out after {e.timeout}s") from e

        args["cc_solo_dir"] = data.get("session_dir")

    run(main(**args))
