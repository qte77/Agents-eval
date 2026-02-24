"""MAS single-agent example: manager-only mode via app.main().

Purpose:
    Demonstrates the minimal MAS execution mode where the manager agent
    handles the entire review workflow without delegating to sub-agents
    (researcher, analyst, synthesiser). All include_* flags are False.

Prerequisites:
    - API key for the default LLM provider set in .env (e.g. OPENAI_API_KEY)
    - PeerRead sample dataset downloaded (run `make app_quickstart` or
      `make setup_dataset` to fetch samples).

Expected output:
    A ReviewGenerationResult or ResearchResult from the manager agent with
    a structured peer review for paper '1105.1072'. The result is printed to
    stdout after the evaluation pipeline completes.

Usage:
    uv run python src/examples/mas_single_agent.py
"""

import asyncio
from typing import Any

from app.app import main
from app.utils.log import logger

# Paper ID used for all MAS examples (available in the PeerRead sample dataset)
_PAPER_ID = "1105.1072"


async def run_example() -> dict[str, Any] | None:
    """Run the MAS pipeline in manager-only (single-agent) mode.

    Uses app.main() with all include_* flags set to False so that the manager
    agent processes the full review workflow without delegation to sub-agents.
    Tier 2 (LLM judge) is skipped to avoid requiring a second API key.

    Returns:
        Dictionary with 'composite_result' and 'graph' keys, or None if the
        run fails (e.g. missing dataset, API key not set).
    """
    logger.info(f"Starting MAS single-agent example for paper {_PAPER_ID}")

    result = await main(
        paper_id=_PAPER_ID,
        include_researcher=False,
        include_analyst=False,
        include_synthesiser=False,
        enable_review_tools=True,
        skip_eval=False,
    )

    if result is not None:
        composite = result.get("composite_result")
        if composite is not None:
            logger.info(
                f"MAS single-agent complete — score: {composite.composite_score:.3f}, "
                f"recommendation: {composite.recommendation}"
            )
    return result


if __name__ == "__main__":
    output = asyncio.run(run_example())
    if output is not None:
        composite = output.get("composite_result")
        if composite is not None:
            print(f"Composite score  : {composite.composite_score:.3f}")
            print(f"Recommendation   : {composite.recommendation}")
            print(f"Tiers enabled    : {composite.tiers_enabled}")
        else:
            print("Run completed — no composite result produced (eval may be skipped).")
    else:
        print("Run completed — no result returned (download-only or error).")
