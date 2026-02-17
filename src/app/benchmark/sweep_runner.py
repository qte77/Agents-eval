"""Sweep runner for MAS composition benchmarking.

This module orchestrates multiple evaluation runs across different agent
compositions and optionally invokes Claude Code in headless mode for baseline
comparison.
"""

import json
import shutil
import subprocess
from typing import Any

from app.app import main
from app.benchmark.sweep_analysis import SweepAnalyzer, generate_markdown_summary
from app.benchmark.sweep_config import AgentComposition, SweepConfig
from app.data_models.evaluation_models import CompositeResult
from app.utils.log import logger


class SweepRunner:
    """Runner for composition sweep experiments.

    Executes the MAS evaluation pipeline across multiple compositions with
    repetitions for statistical significance.
    """

    def __init__(self, config: SweepConfig):
        """Initialize sweep runner with configuration.

        Args:
            config: Sweep configuration defining compositions, repetitions, papers.
        """
        self.config = config
        self.results: list[tuple[AgentComposition, CompositeResult]] = []

    async def _run_single_evaluation(
        self, composition: AgentComposition, paper_number: int, repetition: int
    ) -> CompositeResult | None:
        """Run a single evaluation with specified composition.

        Args:
            composition: Agent composition to test.
            paper_number: Paper ID to evaluate.
            repetition: Repetition number (for logging).

        Returns:
            CompositeResult if successful, None if evaluation failed.
        """
        logger.info(
            f"Running composition={composition.get_name()}, "
            f"paper={paper_number}, repetition={repetition}"
        )

        try:
            # Run evaluation through main() with specified composition
            result = await main(
                chat_provider=self.config.chat_provider,
                query=f"Evaluate paper {paper_number}",
                paper_number=str(paper_number),
                include_researcher=composition.include_researcher,
                include_analyst=composition.include_analyst,
                include_synthesiser=composition.include_synthesiser,
                enable_review_tools=True,
                skip_eval=False,
            )

            # Reason: main() returns dict with 'composite_result' key, not CompositeResult directly
            if isinstance(result, dict) and "composite_result" in result:
                return result["composite_result"]

            logger.warning(f"Evaluation returned unexpected format: {type(result).__name__}")
            return None

        except Exception as e:
            logger.error(
                f"Evaluation failed for composition={composition.get_name()}, "
                f"paper={paper_number}: {e}"
            )
            return None

    async def _invoke_cc_baseline(self, paper_number: int) -> tuple[str, dict[str, Any]] | None:
        """Invoke Claude Code in headless mode for baseline comparison.

        Args:
            paper_number: Paper ID to evaluate.

        Returns:
            Tuple of (execution_id, result_data) if successful, None otherwise.
        """
        # Check if claude CLI is available
        claude_path = shutil.which("claude")
        if not claude_path:
            raise RuntimeError(
                "claude CLI not found. Install Claude Code or disable cc_baseline_enabled."
            )

        prompt = f"Review paper {paper_number} from the PeerRead dataset"

        try:
            result = subprocess.run(
                [claude_path, "-p", prompt, "--output-format", "json"],
                capture_output=True,
                text=True,
                check=True,
                timeout=600,  # 10 minute timeout
            )

            output_data = json.loads(result.stdout)
            execution_id = output_data.get("execution_id", "unknown")

            logger.info(f"CC baseline completed: execution_id={execution_id}")
            return (execution_id, output_data)

        except subprocess.CalledProcessError as e:
            logger.error(f"CC baseline invocation failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CC output: {e}")
            return None
        except subprocess.TimeoutExpired:
            logger.error("CC baseline timed out after 10 minutes")
            return None

    async def _validate_prerequisites(self) -> None:
        """Validate sweep prerequisites."""
        if self.config.cc_baseline_enabled and not shutil.which("claude"):
            raise RuntimeError(
                "CC baseline enabled but claude CLI not found. "
                "Install Claude Code or set cc_baseline_enabled=False."
            )

    async def _run_mas_evaluations(self) -> None:
        """Run MAS evaluations for all compositions, papers, and repetitions."""
        for composition in self.config.compositions:
            for paper_number in self.config.paper_numbers:
                for repetition in range(self.config.repetitions):
                    result = await self._run_single_evaluation(
                        composition, paper_number, repetition
                    )
                    if result:
                        self.results.append((composition, result))

    async def _run_cc_baselines(self) -> None:
        """Run CC baseline evaluations if enabled."""
        if not self.config.cc_baseline_enabled:
            return

        for paper_number in self.config.paper_numbers:
            cc_result = await self._invoke_cc_baseline(paper_number)
            if cc_result:
                logger.info(f"CC baseline completed for paper {paper_number}")
                # CC evaluation integration would go here
                # For now, just log that CC was invoked

    async def run(self) -> list[tuple[AgentComposition, CompositeResult]]:
        """Execute the full sweep across all compositions and repetitions.

        Returns:
            list[tuple[AgentComposition, CompositeResult]]: All evaluation results.

        Raises:
            RuntimeError: If cc_baseline_enabled but claude CLI not found.
        """
        await self._validate_prerequisites()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        await self._run_mas_evaluations()
        await self._run_cc_baselines()
        await self._save_results()
        return self.results

    async def _save_results(self) -> None:
        """Save sweep results to JSON and Markdown files."""
        # Save raw results as JSON
        results_file = self.config.output_dir / "results.json"
        json_data = [
            {
                "composition": {
                    "include_researcher": comp.include_researcher,
                    "include_analyst": comp.include_analyst,
                    "include_synthesiser": comp.include_synthesiser,
                },
                "result": result.model_dump(),
            }
            for comp, result in self.results
        ]

        with open(results_file, "w") as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"Saved raw results to {results_file}")

        # Generate and save statistical summary
        analyzer = SweepAnalyzer(self.results)
        stats = analyzer.analyze()
        markdown = generate_markdown_summary(stats)

        summary_file = self.config.output_dir / "summary.md"
        with open(summary_file, "w") as f:
            f.write(markdown)

        logger.info(f"Saved summary to {summary_file}")


async def run_sweep(config: SweepConfig) -> list[tuple[AgentComposition, CompositeResult]]:
    """Convenience function to run a sweep with given configuration.

    Args:
        config: Sweep configuration.

    Returns:
        list[tuple[AgentComposition, CompositeResult]]: All evaluation results.
    """
    runner = SweepRunner(config)
    return await runner.run()
