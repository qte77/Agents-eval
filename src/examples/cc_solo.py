"""CC solo example: run Claude Code in headless solo mode.

Purpose:
    Demonstrates how to invoke the Claude Code CLI in solo (single-agent)
    headless mode using run_cc_solo(). Includes a check_cc_available() guard
    that prints a helpful message if the 'claude' CLI is not installed.

Prerequisites:
    - Claude Code CLI installed and available on PATH (check with `claude --version`).
    - Authenticated Claude Code session (run `claude` interactively once to log in).
    - No LLM API keys required: CC uses its own authenticated session.

Expected output:
    A CCResult with execution_id and output_data from the CC JSON response.
    The review text extracted from the result is printed to stdout.
    If 'claude' is not on PATH, a helpful installation message is printed
    and the example exits without error.

Usage:
    uv run python src/examples/cc_solo.py
"""

import asyncio

from app.engines.cc_engine import CCResult, build_cc_query, check_cc_available, run_cc_solo
from app.utils.log import logger

# Paper ID for the CC solo review example
_PAPER_ID = "1105.1072"

# Timeout for the CC subprocess (seconds)
_TIMEOUT_SECONDS = 300


async def run_example() -> CCResult | None:
    """Run Claude Code in solo headless mode for paper review.

    Checks CC availability first. If 'claude' CLI is missing, prints an
    installation hint and returns None. Otherwise builds a non-empty query
    using build_cc_query() and invokes run_cc_solo() with a timeout.

    Returns:
        CCResult with execution_id and output_data, or None if CC unavailable.
    """
    if not check_cc_available():
        print(
            "Claude Code CLI not found on PATH.\n"
            "Install it from https://claude.ai/code and authenticate with `claude`.\n"
            "Skipping CC solo example."
        )
        return None

    query = build_cc_query("", paper_id=_PAPER_ID, cc_teams=False)
    logger.info(f"CC solo: query={query!r}")

    result = run_cc_solo(query, timeout=_TIMEOUT_SECONDS)

    logger.info(
        f"CC solo completed — execution_id={result.execution_id}, "
        f"output_keys={list(result.output_data.keys())}"
    )
    return result


if __name__ == "__main__":
    output = asyncio.run(run_example())
    if output is not None:
        review_text = output.output_data.get("result", "")
        print(f"Execution ID     : {output.execution_id}")
        print(f"Output keys      : {list(output.output_data.keys())}")
        if review_text:
            # Print first 500 chars of review to keep output manageable
            print(f"Review preview   : {review_text[:500]}")
