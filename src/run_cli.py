"""
Lightweight CLI wrapper for the Agents-eval application.

This wrapper handles help and basic argument parsing quickly without
loading heavy dependencies. It only imports the main application
when actual processing is needed.
"""

import shutil
from sys import argv, exit
from typing import Any


def _convert_value(key: str, value: str | bool) -> str | bool | int:
    """Convert parsed argument value to appropriate type."""
    if key == "peerread_max_papers_per_sample_download" and isinstance(value, str):
        return int(value)
    if key == "token_limit" and isinstance(value, str):
        return int(value)
    return value


# (description, takes_value) — single source of truth for flag metadata.
_COMMANDS: dict[str, tuple[str, bool]] = {
    "--help": ("Display help information", False),
    "--version": ("Display version information", False),
    "--chat-provider": ("Specify the chat provider to use", True),
    "--query": ("Specify the query to process", True),
    "--include-researcher": ("Include the researcher agent", False),
    "--include-analyst": ("Include the analyst agent", False),
    "--include-synthesiser": ("Include the synthesiser agent", False),
    "--pydantic-ai-stream": ("Enable streaming output", False),
    "--chat-config-file": ("Specify the path to the chat configuration file", True),
    "--enable-review-tools": (
        "Enable PeerRead review generation tools (enabled by default)",
        False,
    ),
    "--no-review-tools": ("Disable PeerRead review generation tools (opt-out)", False),
    "--paper-id": (
        "Specify paper ID for PeerRead review (supports arxiv IDs like '1105.1072')",
        True,
    ),
    "--judge-provider": (
        "Override Tier 2 LLM provider for judge (default: auto, inherits provider)",
        True,
    ),
    "--judge-model": ("Override Tier 2 judge LLM model", True),
    "--skip-eval": ("Skip evaluation after run_manager completes", False),
    "--token-limit": (
        "Override agent token limit (1000-1000000, default from config)",
        True,
    ),
    "--download-peerread-full-only": (
        "Download all of the PeerRead dataset and exit (setup mode)",
        False,
    ),
    "--download-peerread-samples-only": (
        "Download a small sample of the PeerRead dataset and exit (setup mode)",
        False,
    ),
    "--peerread-max-papers-per-sample-download": (
        "Specify max papers to download per split, overrides sample default",
        True,
    ),
    "--cc-solo-dir": (
        "Path to Claude Code solo session export directory for baseline comparison",
        True,
    ),
    "--cc-teams-dir": (
        "Path to Claude Code Agent Teams artifacts directory for baseline comparison",
        True,
    ),
    "--cc-teams-tasks-dir": (
        "Path to Claude Code Agent Teams tasks directory "
        "(optional, auto-discovered if not specified)",
        True,
    ),
    "--engine": (
        "Execution engine: 'mas' for MAS pipeline (default), 'cc' for Claude Code headless",
        True,
    ),
}


def _print_help() -> None:
    """Print available commands and exit."""
    print("Available commands:")
    for cmd, (desc, _) in _COMMANDS.items():
        print(f"{cmd}: {desc}")
    exit(0)


def _parse_single_arg(arg: str) -> tuple[str, str | bool, bool] | None:
    """Parse one argument into (key, value, takes_value) or None if unrecognized."""
    flag = arg.split("=", 1)[0]
    if flag not in _COMMANDS:
        return None
    _, takes_value = _COMMANDS[flag]
    key = flag.lstrip("--").replace("-", "_")
    value: str | bool = arg.split("=", 1)[1] if "=" in arg else True
    return key, value, takes_value


def _normalize(parsed_args: dict[str, Any]) -> dict[str, Any]:
    """Apply post-parse normalization rules."""
    if "no_review_tools" in parsed_args:
        parsed_args["enable_review_tools"] = False
        del parsed_args["no_review_tools"]
    parsed_args.setdefault("engine", "mas")
    return parsed_args


def parse_args(argv: list[str]) -> dict[str, Any]:
    """
    Parse command line arguments into a dictionary.

    This function processes a list of command-line arguments,
    extracting recognized options and their values.
    Supported arguments include flags (e.g., --help, --include-researcher
    and key-value pairs (e.g., `--chat-provider=ollama`).
    If the `--help` flag is present, a list of available commands and their
    descriptions is printed, and an empty dictionary is returned.

    Returns:
        `dict[str, Any]`: A dictionary mapping argument names
        (with leading '--' removed and hyphens replaced by underscores)
        to their values (`str` for key-value pairs, `bool` for flags, `int`
        for numeric arguments). Returns an empty dict if `--help` is specified.

    Example:
        >>> `parse_args(['--chat-provider=ollama', '--include-researcher'])`
        returns `{'chat_provider': 'ollama', 'include_researcher': True}`
    """
    if "--help" in argv:
        _print_help()

    parsed_args: dict[str, Any] = {}
    i = 0
    while i < len(argv):
        arg = argv[i]
        result = _parse_single_arg(arg)
        if result is not None:
            key, value, takes_value = result
            # Reason: value-taking flags used as `--flag value` (space-separated)
            # get True from _parse_single_arg; consume next token as the value.
            if value is True and takes_value and i + 1 < len(argv):
                i += 1
                value = argv[i]
            parsed_args[key] = _convert_value(key, value)
        i += 1

    return _normalize(parsed_args)


if __name__ == "__main__":
    """
    CLI entry point that handles help quickly, then imports main app.
    """
    import json
    import subprocess
    import sys

    if "--help" in argv[1:]:
        parse_args(["--help"])

    from asyncio import run

    from app.app import main
    from app.utils.log import logger

    args = parse_args(argv[1:])

    # Validate --engine=cc requires claude CLI at arg-parse time
    engine = args.get("engine", "mas")
    if engine == "cc" and not shutil.which("claude"):
        print(
            "error: --engine=cc requires the 'claude' CLI to be installed and on PATH",
            file=sys.stderr,
        )
        exit(1)

    if args:
        logger.info(f"Used arguments: {args}")

    if engine == "cc":
        # Invoke CC headless and pass artifact dirs to main for evaluation
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

        # Extract artifact dirs from CC output and pass to main for evaluation
        cc_solo_dir = data.get("session_dir")
        run(
            main(
                cc_solo_dir=cc_solo_dir,
                **{k: v for k, v in args.items() if k != "engine"},
            )
        )
    else:
        run(main(**{k: v for k, v in args.items() if k != "engine"}))
