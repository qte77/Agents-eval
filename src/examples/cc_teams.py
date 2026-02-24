"""CC teams example: run Claude Code in agent-teams orchestration mode.

Purpose:
    Demonstrates how to invoke Claude Code in teams mode using run_cc_teams().
    Teams mode sets CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 so CC can spawn
    teammate agents for parallel task execution. Includes a check_cc_available()
    guard that prints a helpful message if 'claude' is not on PATH.

Prerequisites:
    - Claude Code CLI installed and available on PATH (check with `claude --version`).
    - Authenticated Claude Code session (run `claude` interactively once to log in).
    - No LLM API keys required: CC uses its own authenticated session.

Expected output:
    A CCResult with team_artifacts populated from the JSONL stream events.
    The number of TeamCreate and Task events is printed to stdout.
    If 'claude' is not on PATH, a helpful installation message is printed
    and the example exits without error.

Usage:
    uv run python src/examples/cc_teams.py
"""

import asyncio

from app.engines.cc_engine import CCResult, build_cc_query, check_cc_available, run_cc_teams
from app.utils.log import logger

# Paper ID for the CC teams review example
_PAPER_ID = "1105.1072"

# Timeout for the CC subprocess (seconds); teams mode needs more time than solo
_TIMEOUT_SECONDS = 600


async def run_example() -> CCResult | None:
    """Run Claude Code in agent-teams orchestration mode for paper review.

    Checks CC availability first. If 'claude' CLI is missing, prints an
    installation hint and returns None. Otherwise builds a teams-mode query
    using build_cc_query(cc_teams=True) and invokes run_cc_teams() which
    sets the CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 environment variable.

    Returns:
        CCResult with team_artifacts from stream events, or None if CC unavailable.
    """
    if not check_cc_available():
        print(
            "Claude Code CLI not found on PATH.\n"
            "Install it from https://claude.ai/code and authenticate with `claude`.\n"
            "Skipping CC teams example."
        )
        return None

    # cc_teams=True prepends "Use a team of agents." to encourage CC to spawn teammates
    query = build_cc_query("", paper_id=_PAPER_ID, cc_teams=True)
    logger.info(f"CC teams: query={query!r}")

    result = run_cc_teams(query, timeout=_TIMEOUT_SECONDS)

    team_creates = sum(1 for e in result.team_artifacts if e.get("type") == "TeamCreate")
    tasks = sum(1 for e in result.team_artifacts if e.get("type") == "Task")
    logger.info(
        f"CC teams completed — execution_id={result.execution_id}, "
        f"TeamCreate={team_creates}, Task={tasks}"
    )
    return result


if __name__ == "__main__":
    output = asyncio.run(run_example())
    if output is not None:
        team_creates = sum(1 for e in output.team_artifacts if e.get("type") == "TeamCreate")
        tasks = sum(1 for e in output.team_artifacts if e.get("type") == "Task")
        print(f"Execution ID     : {output.execution_id}")
        print(f"Team artifacts   : {len(output.team_artifacts)} total events")
        print(f"  TeamCreate     : {team_creates}")
        print(f"  Task           : {tasks}")
        print(f"Output keys      : {list(output.output_data.keys())}")
