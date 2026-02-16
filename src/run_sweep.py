"""CLI entry point for MAS composition sweep.

Run automated benchmarking across multiple agent compositions with
statistical analysis of results.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from app.benchmark import AgentComposition, SweepConfig, generate_all_compositions, run_sweep
from app.utils.log import logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run MAS composition sweep with configurable parameters"
    )

    # Config file option
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to sweep configuration JSON file",
    )

    # Individual parameter options (override config file)
    parser.add_argument(
        "--paper-numbers",
        type=str,
        help="Comma-separated list of paper IDs (e.g., '1,2,3')",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=3,
        help="Number of repetitions per composition (default: 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for results (default: results/sweeps/<timestamp>)",
    )
    parser.add_argument(
        "--all-compositions",
        action="store_true",
        help="Use all 2^3=8 agent compositions (default)",
    )
    parser.add_argument(
        "--cc-baseline",
        action="store_true",
        help="Enable Claude Code baseline comparison",
    )

    return parser.parse_args()


async def main_async() -> int:
    """Async main entry point.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    args = parse_args()

    try:
        # Load config from file if provided
        if args.config:
            if not args.config.exists():
                logger.error(f"Config file not found: {args.config}")
                return 1

            with open(args.config) as f:
                config_data = json.load(f)

            # Convert compositions from dicts to AgentComposition objects
            compositions = [
                AgentComposition(**comp) for comp in config_data.get("compositions", [])
            ]

            config = SweepConfig(
                compositions=compositions,
                repetitions=config_data["repetitions"],
                paper_numbers=config_data["paper_numbers"],
                output_dir=Path(config_data["output_dir"]),
                cc_baseline_enabled=config_data.get("cc_baseline_enabled", False),
            )

        # Build config from CLI arguments
        else:
            # Parse paper numbers
            if not args.paper_numbers:
                logger.error("--paper-numbers required when not using --config")
                return 1

            paper_numbers = [int(p.strip()) for p in args.paper_numbers.split(",")]

            # Generate compositions
            if args.all_compositions:
                compositions = generate_all_compositions()
            else:
                # Default: single composition with all agents enabled
                compositions = [
                    AgentComposition(
                        include_researcher=True,
                        include_analyst=True,
                        include_synthesiser=True,
                    )
                ]

            # Set output directory
            if args.output_dir:
                output_dir = args.output_dir
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path(f"results/sweeps/{timestamp}")

            config = SweepConfig(
                compositions=compositions,
                repetitions=args.repetitions,
                paper_numbers=paper_numbers,
                output_dir=output_dir,
                cc_baseline_enabled=args.cc_baseline,
            )

        # Run sweep
        logger.info(f"Starting sweep with {len(config.compositions)} compositions")
        logger.info(f"Papers: {config.paper_numbers}")
        logger.info(f"Repetitions: {config.repetitions}")
        logger.info(f"Output: {config.output_dir}")

        results = await run_sweep(config)

        logger.info(f"Sweep completed with {len(results)} total evaluations")
        logger.info(f"Results saved to {config.output_dir}")

        return 0

    except Exception as e:
        logger.error(f"Sweep failed: {e}", exc_info=True)
        return 1


def main() -> int:
    """Synchronous main entry point.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
