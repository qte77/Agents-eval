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
from app.config.config_app import CHAT_DEFAULT_PROVIDER
from app.data_models.app_models import PROVIDER_REGISTRY
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
        "--provider",
        type=str,
        choices=list(PROVIDER_REGISTRY.keys()),
        default=CHAT_DEFAULT_PROVIDER,
        help=f"LLM provider to use (default: {CHAT_DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--cc-baseline",
        action="store_true",
        help="Enable Claude Code baseline comparison",
    )

    return parser.parse_args()


def _load_config_from_file(config_path: Path) -> SweepConfig | None:
    """Load sweep config from JSON file."""
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return None

    with open(config_path) as f:
        config_data = json.load(f)

    compositions = [AgentComposition(**comp) for comp in config_data.get("compositions", [])]

    return SweepConfig(
        compositions=compositions,
        repetitions=config_data["repetitions"],
        paper_numbers=config_data["paper_numbers"],
        output_dir=Path(config_data["output_dir"]),
        chat_provider=config_data.get("provider", CHAT_DEFAULT_PROVIDER),
        cc_baseline_enabled=config_data.get("cc_baseline_enabled", False),
    )


def _build_config_from_args(args: argparse.Namespace) -> SweepConfig | None:
    """Build sweep config from CLI arguments."""
    if not args.paper_numbers:
        logger.error("--paper-numbers required when not using --config")
        return None

    paper_numbers = [int(p.strip()) for p in args.paper_numbers.split(",")]

    compositions = (
        generate_all_compositions()
        if args.all_compositions
        else [
            AgentComposition(
                include_researcher=True,
                include_analyst=True,
                include_synthesiser=True,
            )
        ]
    )

    output_dir = args.output_dir or Path(
        f"results/sweeps/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    return SweepConfig(
        compositions=compositions,
        repetitions=args.repetitions,
        paper_numbers=paper_numbers,
        output_dir=output_dir,
        chat_provider=args.provider,
        cc_baseline_enabled=args.cc_baseline,
    )


async def main_async() -> int:
    """Async main entry point.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    args = parse_args()

    try:
        config = (
            _load_config_from_file(args.config) if args.config else _build_config_from_args(args)
        )

        if config is None:
            return 1

        # Run sweep
        logger.info(f"Starting sweep with {len(config.compositions)} compositions")
        logger.info(f"Provider: {config.chat_provider}")
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
