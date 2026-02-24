"""Sweep benchmark example: SweepRunner with SweepConfig.

Purpose:
    Demonstrates how to configure and run a composition sweep using
    SweepRunner and SweepConfig. A sweep evaluates multiple agent
    compositions across one or more papers and repetitions for
    statistical comparison of results.

Prerequisites:
    - API key for the default LLM provider set in .env (e.g. OPENAI_API_KEY)
    - PeerRead sample dataset downloaded (run `make app_quickstart` or
      `make setup_dataset` to fetch samples).

Expected output:
    SweepRunner executes each composition (manager-only, researcher-only,
    full 3-agent) on paper '1105.1072' for 1 repetition and prints a
    summary table of composite scores per composition. Output is written
    to a temporary directory that is removed after the example completes.

Usage:
    uv run python src/examples/sweep_benchmark.py
"""

import asyncio
import tempfile
from pathlib import Path

from app.benchmark.sweep_config import AgentComposition, SweepConfig
from app.benchmark.sweep_runner import SweepRunner
from app.data_models.evaluation_models import CompositeResult
from app.utils.log import logger


def _build_sweep_config(output_dir: Path) -> SweepConfig:
    """Build a minimal SweepConfig for the example.

    Uses 3 compositions, 1 paper, and 1 repetition to keep runtime short.

    Args:
        output_dir: Temporary directory for sweep result files.

    Returns:
        SweepConfig ready for SweepRunner.
    """
    compositions = [
        # Manager-only (single-agent baseline)
        AgentComposition(
            include_researcher=False,
            include_analyst=False,
            include_synthesiser=False,
        ),
        # Manager + researcher (2-agent)
        AgentComposition(
            include_researcher=True,
            include_analyst=False,
            include_synthesiser=False,
        ),
        # Full 3-agent delegation
        AgentComposition(
            include_researcher=True,
            include_analyst=True,
            include_synthesiser=True,
        ),
    ]

    return SweepConfig(
        compositions=compositions,
        repetitions=1,
        paper_ids=["1105.1072"],
        output_dir=output_dir,
    )


async def run_example() -> list[tuple[AgentComposition, CompositeResult]]:
    """Run the sweep benchmark with 3 compositions, 1 paper, 1 repetition.

    Results are written to a temporary directory that is cleaned up after
    the example completes.

    Returns:
        List of (AgentComposition, CompositeResult) tuples from the sweep.
    """
    with tempfile.TemporaryDirectory(prefix="sweep_example_") as tmp_dir:
        output_dir = Path(tmp_dir)
        config = _build_sweep_config(output_dir)
        runner = SweepRunner(config)

        logger.info(
            f"Starting sweep: {len(config.compositions)} compositions, "
            f"{config.repetitions} repetition(s), paper_ids={config.paper_ids}"
        )

        await runner.run()

        logger.info(f"Sweep complete — {len(runner.results)} result(s)")
        # Snapshot results before temp dir cleanup
        results = list(runner.results)

    return results


if __name__ == "__main__":
    results = asyncio.run(run_example())
    print(f"\n=== Sweep Results ({len(results)} runs) ===")
    for composition, result in results:
        name = composition.get_name()
        if hasattr(result, "composite_score"):
            print(
                f"  {name:30s}  score={result.composite_score:.3f}  "  # type: ignore[union-attr]
                f"rec={result.recommendation}"  # type: ignore[union-attr]
            )
        else:
            print(f"  {name:30s}  (no result)")
