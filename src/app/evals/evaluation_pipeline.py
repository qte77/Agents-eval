"""
Three-tier evaluation pipeline orchestrator.

Coordinates Traditional Metrics (Tier 1), LLM-as-Judge (Tier 2), and
Graph Analysis (Tier 3) into unified evaluation workflow with performance
monitoring and graceful degradation.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from app.data_models.evaluation_models import (
    CompositeResult,
    GraphTraceData,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.evals.composite_scorer import CompositeScorer, EvaluationResults
from app.evals.graph_analysis import GraphAnalysisEngine
from app.evals.llm_evaluation_managers import LLMJudgeEngine
from app.evals.traditional_metrics import TraditionalMetricsEngine
from app.utils.log import logger


class EvaluationPipeline:
    """
    Unified evaluation pipeline orchestrator for three-tier assessment.

    Coordinates execution of Traditional Metrics → LLM-as-Judge → Graph Analysis
    with configurable tier enabling, performance monitoring, and fallback strategies.
    """

    # Type hints for class attributes
    config: dict[str, Any]
    config_path: Path
    system_config: dict[str, Any]
    enabled_tiers: set[int]
    performance_targets: dict[str, int | float]
    fallback_strategy: str
    execution_stats: dict[str, float | list[int] | bool]

    def __init__(self, config_path: str | Path | None = None):
        """Initialize evaluation pipeline with configuration.

        Args:
            config_path: Path to config_eval.json file. If None, uses default location.

        Raises:
            FileNotFoundError: If configuration file not found
            ValueError: If configuration is invalid
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config_eval.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Extract pipeline configuration
        self.system_config = self.config.get("evaluation_system", {})
        self.enabled_tiers = set(self.system_config.get("tiers_enabled", [1, 2, 3]))
        self.performance_targets = self.system_config.get("performance_targets", {})
        self.fallback_strategy = self.config.get("composite_scoring", {}).get(
            "fallback_strategy", "tier1_only"
        )

        # Initialize engines
        self.traditional_engine = TraditionalMetricsEngine()
        self.llm_engine = LLMJudgeEngine(self.config)
        self.graph_engine = GraphAnalysisEngine(self.config)
        self.composite_scorer = CompositeScorer(config_path)

        # Performance tracking
        self.execution_stats: dict[str, float | list[int] | bool] = {
            "tier1_time": 0.0,
            "tier2_time": 0.0,
            "tier3_time": 0.0,
            "total_time": 0.0,
            "tiers_executed": [],
            "fallback_used": False,
        }

        logger.info(
            f"EvaluationPipeline initialized with tiers: {sorted(self.enabled_tiers)}"
        )

    def _load_config(self) -> dict[str, Any]:
        """Load evaluation configuration from JSON file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file not found
            json.JSONDecodeError: If invalid JSON
        """
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            logger.debug(f"Loaded pipeline configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Pipeline configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in pipeline configuration: {e}")
            raise

    async def _execute_tier1(
        self, paper: str, review: str, reference_reviews: list[str] | None = None
    ) -> tuple[Tier1Result | None, float]:
        """Execute Traditional Metrics evaluation (Tier 1).

        Args:
            paper: Paper content text
            review: Generated review text
            reference_reviews: Optional list of ground truth reviews for similarity

        Returns:
            Tuple of (Tier1Result or None, execution_time)
        """
        if 1 not in self.enabled_tiers:
            logger.debug("Tier 1 disabled, skipping traditional metrics")
            return None, 0.0

        timeout = self.performance_targets.get("tier1_max_seconds", 1.0)
        start_time = time.time()

        try:
            logger.info("Executing Tier 1: Traditional Metrics")
            start_evaluation = time.time()

            # Use reference reviews or default to empty list for similarity comparison
            ref_reviews = reference_reviews or [""]  # Fallback for missing ground truth

            result = await asyncio.wait_for(
                asyncio.create_task(
                    asyncio.to_thread(
                        self.traditional_engine.evaluate_traditional_metrics,
                        review,  # agent_output
                        ref_reviews,  # reference_texts
                        start_evaluation,  # start_time
                        time.time(),  # end_time (will be updated in method)
                        self.config.get("tier1_traditional", {}),  # config
                    )
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            logger.info(f"Tier 1 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            logger.error(f"Tier 1 timeout after {timeout}s")
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tier 1 failed: {e}")
            return None, execution_time

    async def _execute_tier2(
        self, paper: str, review: str, execution_trace: dict[str, Any] | None = None
    ) -> tuple[Tier2Result | None, float]:
        """Execute LLM-as-Judge evaluation (Tier 2).

        Args:
            paper: Paper content text
            review: Generated review text
            execution_trace: Optional execution trace data

        Returns:
            Tuple of (Tier2Result or None, execution_time)
        """
        if 2 not in self.enabled_tiers:
            logger.debug("Tier 2 disabled, skipping LLM judge")
            return None, 0.0

        timeout = self.performance_targets.get("tier2_max_seconds", 10.0)
        start_time = time.time()

        try:
            logger.info("Executing Tier 2: LLM-as-Judge")
            result = await asyncio.wait_for(
                self.llm_engine.evaluate_comprehensive(
                    paper, review, execution_trace or {}
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            logger.info(f"Tier 2 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            logger.error(f"Tier 2 timeout after {timeout}s")
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tier 2 failed: {e}")
            return None, execution_time

    async def _execute_tier3(
        self, execution_trace: dict[str, Any] | None = None
    ) -> tuple[Tier3Result | None, float]:
        """Execute Graph Analysis evaluation (Tier 3).

        Args:
            execution_trace: Optional execution trace data for graph construction

        Returns:
            Tuple of (Tier3Result or None, execution_time)
        """
        if 3 not in self.enabled_tiers:
            logger.debug("Tier 3 disabled, skipping graph analysis")
            return None, 0.0

        timeout = self.performance_targets.get("tier3_max_seconds", 15.0)
        start_time = time.time()

        try:
            logger.info("Executing Tier 3: Graph Analysis")

            # Convert execution trace to GraphTraceData if available
            if execution_trace:
                trace_data = GraphTraceData(
                    execution_id=execution_trace.get("execution_id", "pipeline_exec"),
                    agent_interactions=execution_trace.get("agent_interactions", []),
                    tool_calls=execution_trace.get("tool_calls", []),
                    timing_data=execution_trace.get("timing_data", {}),
                    coordination_events=execution_trace.get("coordination_events", []),
                )
            else:
                # Create minimal trace data for basic analysis
                trace_data = GraphTraceData(
                    execution_id="pipeline_minimal",
                    agent_interactions=[],
                    tool_calls=[],
                    timing_data={},
                    coordination_events=[],
                )

            result = await asyncio.wait_for(
                asyncio.create_task(
                    asyncio.to_thread(
                        self.graph_engine.evaluate_graph_metrics, trace_data
                    )
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            logger.info(f"Tier 3 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            logger.error(f"Tier 3 timeout after {timeout}s")
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tier 3 failed: {e}")
            return None, execution_time

    def _apply_fallback_strategy(self, results: EvaluationResults) -> EvaluationResults:
        """Apply fallback strategy when tiers fail.

        Args:
            results: Partial evaluation results

        Returns:
            EvaluationResults with fallback applied
        """
        if self.fallback_strategy == "tier1_only" and results.tier1:
            logger.info("Applying tier1_only fallback strategy")
            # Create minimal results for missing tiers to enable composite scoring
            if not results.tier2:
                results.tier2 = Tier2Result(
                    technical_accuracy=0.5,
                    constructiveness=0.5,
                    clarity=0.5,
                    planning_rationality=0.5,
                    overall_score=0.5,
                    model_used="fallback",
                    api_cost=0.0,
                    fallback_used=True,
                )
            if not results.tier3:
                results.tier3 = Tier3Result(
                    path_convergence=0.5,
                    tool_selection_accuracy=0.5,
                    communication_overhead=0.5,
                    coordination_centrality=0.5,
                    task_distribution_balance=0.5,
                    overall_score=0.5,
                    graph_complexity=1,
                )
            self.execution_stats["fallback_used"] = True

        return results

    async def evaluate_comprehensive(
        self,
        paper: str,
        review: str,
        execution_trace: dict[str, Any] | None = None,
        reference_reviews: list[str] | None = None,
    ) -> CompositeResult:
        """Execute comprehensive three-tier evaluation pipeline.

        Args:
            paper: Paper content text for evaluation
            review: Generated review text to assess
            execution_trace: Optional execution trace for graph analysis
            reference_reviews: Optional list of ground truth reviews for similarity

        Returns:
            CompositeResult with scores from all applicable tiers

        Raises:
            ValueError: If critical evaluation components fail
        """
        pipeline_start = time.time()
        logger.info("Starting comprehensive three-tier evaluation pipeline")

        # Reset execution stats
        self.execution_stats = {
            "tier1_time": 0.0,
            "tier2_time": 0.0,
            "tier3_time": 0.0,
            "total_time": 0.0,
            "tiers_executed": [],
            "fallback_used": False,
        }

        try:
            # Execute all enabled tiers
            tier1_result, tier1_time = await self._execute_tier1(
                paper, review, reference_reviews
            )
            tier2_result, tier2_time = await self._execute_tier2(
                paper, review, execution_trace
            )
            tier3_result, tier3_time = await self._execute_tier3(execution_trace)

            # Track execution statistics
            self.execution_stats["tier1_time"] = tier1_time
            self.execution_stats["tier2_time"] = tier2_time
            self.execution_stats["tier3_time"] = tier3_time

            tiers_executed = self.execution_stats["tiers_executed"]
            if tier1_result and isinstance(tiers_executed, list):
                tiers_executed.append(1)
            if tier2_result and isinstance(tiers_executed, list):
                tiers_executed.append(2)
            if tier3_result and isinstance(tiers_executed, list):
                tiers_executed.append(3)

            # Assemble results
            results = EvaluationResults(
                tier1=tier1_result,
                tier2=tier2_result,
                tier3=tier3_result,
            )

            # Apply fallback strategy if needed
            if not results.is_complete():
                results = self._apply_fallback_strategy(results)

            # Generate composite score
            if results.is_complete():
                composite_result = self.composite_scorer.evaluate_composite(results)
            else:
                raise ValueError(
                    "Cannot generate composite score: insufficient tier results"
                )

            # Record total execution time
            total_time = time.time() - pipeline_start
            self.execution_stats["total_time"] = total_time

            # Check performance targets
            max_total_time = self.performance_targets.get("total_max_seconds", 25.0)
            if total_time > max_total_time:
                logger.warning(
                    f"Pipeline exceeded time target: {total_time:.2f}s > "
                    f"{max_total_time}s"
                )

            logger.info(
                f"Pipeline completed in {total_time:.2f}s, "
                f"tiers executed: {self.execution_stats['tiers_executed']}, "
                f"composite score: {composite_result.composite_score:.3f}"
            )

            return composite_result

        except Exception as e:
            total_time = time.time() - pipeline_start
            self.execution_stats["total_time"] = total_time
            logger.error(f"Pipeline evaluation failed after {total_time:.2f}s: {e}")
            raise

    def get_execution_stats(self) -> dict[str, Any]:
        """Get detailed execution statistics from last pipeline run.

        Returns:
            Dictionary with timing and execution details
        """
        return self.execution_stats.copy()

    def get_pipeline_summary(self) -> dict[str, Any]:
        """Get pipeline configuration summary.

        Returns:
            Dictionary with pipeline configuration details
        """
        return {
            "enabled_tiers": sorted(self.enabled_tiers),
            "performance_targets": self.performance_targets.copy(),
            "fallback_strategy": self.fallback_strategy,
            "config_path": str(self.config_path),
        }
