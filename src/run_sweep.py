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
        "--paper-ids",
        type=str,
        help="Comma-separated list of paper IDs (e.g., '1,2,3' or '1105.1072')",
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
        "--chat-provider",
        type=str,
        choices=list(PROVIDER_REGISTRY.keys()),
        default=CHAT_DEFAULT_PROVIDER,
        help=f"LLM provider to use for MAS agents (default: {CHAT_DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--judge-provider",
        type=str,
        default="auto",
        help="LLM provider for Tier 2 judge (default: auto, inherits --chat-provider)",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default=None,
        help="LLM model for Tier 2 judge (default: uses JudgeSettings default)",
    )
    parser.add_argument(
        "--engine",
        type=str,
        choices=["mas", "cc"],
        default="mas",
        help="Execution engine: 'mas' for MAS pipeline (default), 'cc' for Claude Code headless",
    )

    return parser.parse_args()


def _load_config_from_file(config_path: Path) -> SweepConfig | None:
    """Load sweep config from JSON file.

    Supports both new ('paper_ids', 'chat_provider') and legacy ('paper_numbers', 'provider') keys.
    Legacy keys are accepted with a deprecation log for backward compatibility.
    """
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return None

    with open(config_path) as f:
        config_data = json.load(f)

    compositions = [AgentComposition(**comp) for comp in config_data.get("compositions", [])]

    # Backward compat: accept 'paper_numbers' (old) or 'paper_ids' (new)
    if "paper_ids" in config_data:
        paper_ids = [str(p) for p in config_data["paper_ids"]]
    elif "paper_numbers" in config_data:
        logger.warning("Config key 'paper_numbers' is deprecated, use 'paper_ids' instead")
        paper_ids = [str(p) for p in config_data["paper_numbers"]]
    else:
        logger.error("Config file missing required key 'paper_ids'")
        return None

    # Backward compat: accept 'provider' (old) or 'chat_provider' (new)
    if "chat_provider" in config_data:
        chat_provider = config_data["chat_provider"]
    elif "provider" in config_data:
        logger.warning("Config key 'provider' is deprecated, use 'chat_provider' instead")
        chat_provider = config_data["provider"]
    else:
        chat_provider = CHAT_DEFAULT_PROVIDER

    return SweepConfig(
        compositions=compositions,
        repetitions=config_data["repetitions"],
        paper_ids=paper_ids,
        output_dir=Path(config_data["output_dir"]),
        chat_provider=chat_provider,
        engine=config_data.get("engine", "mas"),
        judge_provider=config_data.get("judge_provider", "auto"),
        judge_model=config_data.get("judge_model"),
    )


def _build_config_from_args(args: argparse.Namespace) -> SweepConfig | None:
    """Build sweep config from CLI arguments."""
    if not args.paper_ids:
        logger.error("--paper-ids required when not using --config")
        return None

    paper_ids = [p.strip() for p in args.paper_ids.split(",")]

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
        paper_ids=paper_ids,
        output_dir=output_dir,
        chat_provider=args.chat_provider,
        engine=args.engine,
        judge_provider=args.judge_provider,
        judge_model=args.judge_model,
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
        logger.info(f"Papers: {config.paper_ids}")
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
