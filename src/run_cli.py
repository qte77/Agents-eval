"""
Lightweight CLI wrapper for the Agents-eval application.

This wrapper handles help and basic argument parsing quickly without
loading heavy dependencies. It only imports the main application
when actual processing is needed.
"""

from sys import argv, exit


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """
    Parse command line arguments into a dictionary.

    This function processes a list of command-line arguments,
    extracting recognized options and their values.
    Supported arguments include flags (e.g., --help, --include-researcher
    and key-value pairs (e.g., `--chat-provider=ollama`).
    If the `--help` flag is present, a list of available commands and their
    descriptions is printed, and an empty dictionary is returned.

    Returns:
        `dict[str, str | bool]`: A dictionary mapping argument names
        (with leading '--' removed and hyphens replaced by underscores)
        to their values (`str` for key-value pairs, `bool` for flags).
        Returns an empty dict if `--help` is specified.

    Example:
        >>> `parse_args(['--chat-provider=ollama', '--include-researcher'])`
        returns `{'chat_provider': 'ollama', 'include_researcher': True}`
    """

    commands = {
        "--help": "Display help information",
        "--version": "Display version information",
        "--chat-provider": "Specify the chat provider to use",
        "--query": "Specify the query to process",
        "--include-researcher": "Include the researcher agent",
        "--include-analyst": "Include the analyst agent",
        "--include-synthesiser": "Include the synthesiser agent",
        "--no-stream": "Disable streaming output",
        "--chat-config-file": "Specify the path to the chat configuration file",
        "--paper-number": "Specify paper number for PeerRead review generation",
        "--skip-eval": "Skip evaluation after run_manager completes",
        "--download-peerread-full-only": (
            "Download all of the PeerRead dataset and exit (setup mode)"
        ),
        "--download-peerread-samples-only": (
            "Download a small sample of the PeerRead dataset and exit (setup mode)"
        ),
        "--peerread-max-papers-per-sample-download": (
            "Specify max papers to download per split, overrides sample default"
        ),
    }

    # output help and exit
    if "--help" in argv:
        print("Available commands:")
        for cmd, desc in commands.items():
            print(f"{cmd}: {desc}")
        exit(0)

    parsed_args: dict[str, str | bool] = {}

    # parse arguments for key-value pairs and flags
    for arg in argv:
        if arg.split("=", 1)[0] in commands.keys():
            key, value = arg.split("=", 1) if "=" in arg else (arg, True)
            key = key.lstrip("--").replace("-", "_")
            parsed_args[key] = value

    return parsed_args


if __name__ == "__main__":
    """
    CLI entry point that handles help quickly, then imports main app.
    """

    if "--help" in argv[1:]:
        parse_args(["--help"])

    from asyncio import run

    from app.app import main
    from app.utils.log import logger

    args = parse_args(argv[1:])
    if args:
        logger.info(f"Used arguments: {args}")
    run(main(**args))
