"""Sweep runner for MAS composition benchmarking.

This module orchestrates multiple evaluation runs across different agent
compositions and optionally invokes Claude Code in headless mode for baseline
comparison.
"""

import asyncio
import json
import shutil
import subprocess
from typing import Any

from pydantic_ai.exceptions import ModelHTTPError

from app.app import main
from app.benchmark.sweep_analysis import SweepAnalyzer, generate_markdown_summary
from app.benchmark.sweep_config import AgentComposition, SweepConfig
from app.data_models.evaluation_models import CompositeResult
from app.judge.settings import JudgeSettings
from app.utils.log import logger

_MAX_RETRIES = 3


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

    def _build_judge_settings(self) -> JudgeSettings | None:
        """Build JudgeSettings from sweep config if judge args are configured.

        Returns:
            JudgeSettings with configured provider/model, or None to use defaults.
        """
        if self.config.judge_provider != "auto" or self.config.judge_model is not None:
            kwargs: dict[str, Any] = {"tier2_provider": self.config.judge_provider}
            if self.config.judge_model is not None:
                kwargs["tier2_model"] = self.config.judge_model
            return JudgeSettings(**kwargs)
        return None

    async def _run_single_evaluation(
        self, composition: AgentComposition, paper_id: str, repetition: int
    ) -> CompositeResult | None:
        """Run a single evaluation with specified composition, retrying on rate limits.

        Retries up to _MAX_RETRIES times on HTTP 429 errors with exponential backoff
        starting at retry_delay_seconds. After max retries, logs error and returns None.

        Args:
            composition: Agent composition to test.
            paper_id: Paper ID to evaluate (string, supports arxiv IDs like '1105.1072').
            repetition: Repetition number (for logging).

        Returns:
            CompositeResult if successful, None if evaluation failed.
        """
        logger.info(
            f"Running composition={composition.get_name()}, "
            f"paper={paper_id}, repetition={repetition}"
        )

        judge_settings = self._build_judge_settings()

        for attempt in range(_MAX_RETRIES + 1):
            try:
                # Run evaluation through main() with specified composition
                result = await main(
                    chat_provider=self.config.chat_provider,
                    query=f"Evaluate paper {paper_id}",
                    paper_id=paper_id,
                    include_researcher=composition.include_researcher,
                    include_analyst=composition.include_analyst,
                    include_synthesiser=composition.include_synthesiser,
                    enable_review_tools=True,
                    skip_eval=False,
                    judge_settings=judge_settings,
                )

                # Reason: main() returns dict with 'composite_result' key, not CompositeResult directly
                if isinstance(result, dict) and "composite_result" in result:
                    return result["composite_result"]

                logger.warning(f"Evaluation returned unexpected format: {type(result).__name__}")
                return None

            except ModelHTTPError as e:
                if e.status_code == 429 and attempt < _MAX_RETRIES:
                    delay = self.config.retry_delay_seconds * (2**attempt)
                    logger.warning(
                        f"Rate limit hit for composition={composition.get_name()}, "
                        f"paper={paper_id} (attempt {attempt + 1}/{_MAX_RETRIES + 1}). "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Rate limit exhausted for composition={composition.get_name()}, "
                        f"paper={paper_id}: {e}"
                    )
                    return None

            except Exception as e:
                logger.error(
                    f"Evaluation failed for composition={composition.get_name()}, "
                    f"paper={paper_id}: {e}"
                )
                return None

        return None

    async def _invoke_cc_comparison(self, paper_id: str) -> tuple[str, dict[str, Any]] | None:
        """Invoke Claude Code in headless mode for baseline comparison.

        Args:
            paper_id: Paper ID to evaluate (string, supports arxiv IDs).

        Returns:
            Tuple of (execution_id, result_data) if successful, None otherwise.

        Raises:
            RuntimeError: If claude CLI not found, subprocess fails, or times out.
            ValueError: If CC output is not valid JSON.
        """
        # Check if claude CLI is available
        claude_path = shutil.which("claude")
        if not claude_path:
            raise RuntimeError("claude CLI not found. Install Claude Code or use --engine=mas.")

        prompt = f"Review paper {paper_id} from the PeerRead dataset"

        try:
            result = subprocess.run(
                [claude_path, "-p", prompt, "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"CC failed: {result.stderr}")

            try:
                output_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise ValueError(f"CC output not valid JSON: {e}") from e

            execution_id = output_data.get("execution_id", "unknown")

            logger.info(f"CC comparison completed: execution_id={execution_id}")
            return (execution_id, output_data)

        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"CC timed out after {e.timeout}s") from e

    async def _validate_prerequisites(self) -> None:
        """Validate sweep prerequisites."""
        if self.config.engine == "cc" and not shutil.which("claude"):
            raise RuntimeError(
                "engine=cc requires claude CLI. Install Claude Code or use --engine=mas."
            )

    async def _run_mas_evaluations(self) -> None:
        """Run MAS evaluations for all compositions, papers, and repetitions.

        Writes partial results.json after each successful evaluation for crash resilience.
        """
        for composition in self.config.compositions:
            for paper_id in self.config.paper_ids:
                for repetition in range(self.config.repetitions):
                    result = await self._run_single_evaluation(composition, paper_id, repetition)
                    if result:
                        self.results.append((composition, result))
                        await self._save_results_json()

    async def _run_cc_baselines(self) -> None:
        """Run CC comparison evaluations if engine=cc."""
        if self.config.engine != "cc":
            return

        for paper_id in self.config.paper_ids:
            cc_result = await self._invoke_cc_comparison(paper_id)
            if cc_result:
                logger.info(f"CC comparison completed for paper {paper_id}")
                # CC evaluation integration would go here
                # For now, just log that CC was invoked

    async def run(self) -> list[tuple[AgentComposition, CompositeResult]]:
        """Execute the full sweep across all compositions and repetitions.

        Returns:
            list[tuple[AgentComposition, CompositeResult]]: All evaluation results.

        Raises:
            RuntimeError: If engine=cc but claude CLI not found.
        """
        await self._validate_prerequisites()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        await self._run_mas_evaluations()
        await self._run_cc_baselines()
        await self._save_results()
        return self.results

    async def _save_results_json(self) -> None:
        """Save sweep results to results.json only (incremental write).

        Used for crash-resilient incremental persistence after each evaluation.
        """
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

    async def _save_results(self) -> None:
        """Save sweep results to both results.json and summary.md."""
        await self._save_results_json()

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
