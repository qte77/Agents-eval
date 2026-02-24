"""MAS multi-agent example: full 4-agent delegation via app.main().

Purpose:
    Demonstrates the full MAS execution mode where the manager agent
    delegates tasks to all three sub-agents: researcher, analyst, and
    synthesiser. All include_* flags are True, enabling the complete
    multi-agent review workflow.

Prerequisites:
    - API key for the default LLM provider set in .env (e.g. OPENAI_API_KEY)
    - PeerRead sample dataset downloaded (run `make app_quickstart` or
      `make setup_dataset` to fetch samples).

Expected output:
    A ReviewGenerationResult from the full 4-agent pipeline (manager +
    researcher + analyst + synthesiser) for paper '1105.1072'. The composite
    evaluation score and recommendation are printed to stdout.

Usage:
    uv run python src/examples/mas_multi_agent.py
"""

import asyncio
from typing import Any

from app.app import main
from app.utils.log import logger

# Paper ID used for all MAS examples (available in the PeerRead sample dataset)
_PAPER_ID = "1105.1072"


async def run_example() -> dict[str, Any] | None:
    """Run the MAS pipeline in full multi-agent mode (4 agents).

    Uses app.main() with all include_* flags set to True so that the manager
    delegates research, analysis, and synthesis to specialist sub-agents.
    The researcher agent is equipped with DuckDuckGo search and PeerRead tools.

    Returns:
        Dictionary with 'composite_result' and 'graph' keys, or None if the
        run fails (e.g. missing dataset, API key not set).
    """
    logger.info(f"Starting MAS multi-agent example for paper {_PAPER_ID}")

    result = await main(
        paper_id=_PAPER_ID,
        include_researcher=True,
        include_analyst=True,
        include_synthesiser=True,
        enable_review_tools=True,
        skip_eval=False,
    )

    if result is not None:
        composite = result.get("composite_result")
        if composite is not None:
            logger.info(
                f"MAS multi-agent complete — score: {composite.composite_score:.3f}, "
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
