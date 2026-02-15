"""
Streamlined three-tier evaluation pipeline orchestrator.

Coordinates Traditional Metrics (Tier 1), LLM-as-Judge (Tier 2), and
Graph Analysis (Tier 3) into unified evaluation workflow with graceful
degradation. Uses modular components for configuration and monitoring.
"""

import asyncio
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
from app.evals.performance_monitor import PerformanceMonitor
from app.evals.settings import JudgeSettings
from app.evals.traditional_metrics import TraditionalMetricsEngine
from app.utils.log import logger


class EvaluationPipeline:
    """
    Streamlined evaluation pipeline orchestrator for three-tier assessment.

    Coordinates execution of Traditional Metrics → LLM-as-Judge → Graph Analysis
    with configurable tier enabling and graceful degradation. Uses modular
    components for configuration management and performance monitoring.
    """

    def __init__(
        self,
        settings: JudgeSettings | None = None,
    ):
        """Initialize evaluation pipeline with configuration.

        Args:
            settings: JudgeSettings instance. If None, uses default JudgeSettings().

        Raises:
            ValueError: If configuration is invalid
        """
        # Use provided settings or create default
        if settings is None:
            settings = JudgeSettings()

        self.settings = settings
        self.performance_monitor = PerformanceMonitor(settings.get_performance_targets())

        # Initialize engines with settings
        self.traditional_engine = TraditionalMetricsEngine()
        self.llm_engine = LLMJudgeEngine(settings)
        self.graph_engine = GraphAnalysisEngine(settings)
        self.composite_scorer = CompositeScorer(settings=settings)

        enabled_tiers = sorted(settings.get_enabled_tiers())
        fallback_strategy = settings.fallback_strategy
        logger.info(
            f"EvaluationPipeline initialized with JudgeSettings: tiers={enabled_tiers}, "
            f"fallback_strategy={fallback_strategy}"
        )

    @property
    def enabled_tiers(self) -> set[int]:
        """Get enabled tiers (backward compatibility property).

        Returns:
            Set of enabled tier numbers
        """
        return self.settings.get_enabled_tiers()

    @property
    def performance_targets(self) -> dict[str, float]:
        """Get performance targets (backward compatibility property).

        Returns:
            Dictionary of performance targets
        """
        return self.settings.get_performance_targets()

    @property
    def fallback_strategy(self) -> str:
        """Get fallback strategy (backward compatibility property).

        Returns:
            Fallback strategy name
        """
        return self.settings.fallback_strategy

    @property
    def config_path(self) -> Path | None:
        """Get configuration path (backward compatibility property).

        Returns:
            Always None (settings-based configuration only)
        """
        return None

    @property
    def execution_stats(self) -> dict[str, Any]:
        """Get execution statistics (backward compatibility property).

        Returns:
            Dictionary with execution statistics
        """
        return self.performance_monitor.get_execution_stats()

    def _is_tier_enabled(self, tier: int) -> bool:
        """Check if tier is enabled (internal helper).

        Args:
            tier: Tier number to check

        Returns:
            True if tier is enabled
        """
        return self.settings.is_tier_enabled(tier)

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
        if not self._is_tier_enabled(1):
            logger.debug("Tier 1 disabled, skipping traditional metrics")
            return None, 0.0

        performance_targets = self.performance_targets
        timeout = performance_targets.get("tier1_max_seconds", 1.0)
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
                        self.settings,  # settings
                    )
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(1, execution_time)
            logger.info(f"Tier 1 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 timeout after {timeout}s (traditional metrics evaluation)"
            logger.error(f"{error_msg}. Consider increasing tier1_max_seconds in config.")
            self.performance_monitor.record_tier_failure(1, "timeout", execution_time, error_msg)
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 failed with {type(e).__name__}: {e}"
            logger.error(f"{error_msg}. Paper length: {len(paper)}, Review length: {len(review)}")
            self.performance_monitor.record_tier_failure(1, "error", execution_time, str(e))
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
        if not self._is_tier_enabled(2):
            logger.debug("Tier 2 disabled, skipping LLM judge")
            return None, 0.0

        performance_targets = self.performance_targets
        timeout = performance_targets.get("tier2_max_seconds", 10.0)
        start_time = time.time()

        try:
            logger.info("Executing Tier 2: LLM-as-Judge")
            result = await asyncio.wait_for(
                self.llm_engine.evaluate_comprehensive(paper, review, execution_trace or {}),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(2, execution_time)
            logger.info(f"Tier 2 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 2 timeout after {timeout}s (LLM-as-Judge evaluation)"
            logger.error(
                f"{error_msg}. Consider increasing tier2_max_seconds or check "
                "LLM service availability."
            )
            self.performance_monitor.record_tier_failure(2, "timeout", execution_time, error_msg)
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            error_msg = f"Tier 2 failed with {error_type}: {e}"
            logger.error(f"{error_msg}. Paper length: {len(paper)}, Review length: {len(review)}")
            # Add specific guidance based on error type
            if "rate limit" in str(e).lower():
                logger.error("Rate limit exceeded - consider adjusting request frequency")
            elif "authentication" in str(e).lower():
                logger.error("Authentication failed - check API keys and configuration")
            elif "connection" in str(e).lower():
                logger.error(
                    "Connection failed - check network connectivity and service availability"
                )
            self.performance_monitor.record_tier_failure(2, "error", execution_time, str(e))
            return None, execution_time

    def _create_trace_data(self, execution_trace: dict[str, Any] | None) -> GraphTraceData:
        """Convert execution trace to GraphTraceData."""
        if execution_trace:
            return GraphTraceData(
                execution_id=execution_trace.get("execution_id", "pipeline_exec"),
                agent_interactions=execution_trace.get("agent_interactions", []),
                tool_calls=execution_trace.get("tool_calls", []),
                timing_data=execution_trace.get("timing_data", {}),
                coordination_events=execution_trace.get("coordination_events", []),
            )
        return GraphTraceData(
            execution_id="pipeline_minimal",
            agent_interactions=[],
            tool_calls=[],
            timing_data={},
            coordination_events=[],
        )

    def _handle_tier3_error(
        self, e: Exception, execution_trace: dict[str, Any] | None, start_time: float
    ) -> tuple[None, float]:
        """Handle Tier 3 execution errors with specific guidance."""
        execution_time = time.time() - start_time
        error_type = type(e).__name__
        trace_size = len(str(execution_trace)) if execution_trace else 0
        error_msg = f"Tier 3 failed with {error_type}: {e}"
        logger.error(f"{error_msg}. Trace data size: {trace_size} chars")

        if "memory" in str(e).lower():
            logger.error("Memory error - consider reducing trace data complexity")
        elif "networkx" in str(e).lower():
            logger.error("Graph construction error - check trace data format")

        self.performance_monitor.record_tier_failure(3, "error", execution_time, str(e))
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
        if not self._is_tier_enabled(3):
            logger.debug("Tier 3 disabled, skipping graph analysis")
            return None, 0.0

        performance_targets = self.performance_targets
        timeout = performance_targets.get("tier3_max_seconds", 15.0)
        start_time = time.time()

        try:
            logger.info("Executing Tier 3: Graph Analysis")
            trace_data = self._create_trace_data(execution_trace)

            result = await asyncio.wait_for(
                asyncio.create_task(
                    asyncio.to_thread(self.graph_engine.evaluate_graph_metrics, trace_data)
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(3, execution_time)
            logger.info(f"Tier 3 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 3 timeout after {timeout}s (Graph analysis evaluation)"
            logger.error(
                f"{error_msg}. Consider increasing tier3_max_seconds or simplifying trace data."
            )
            self.performance_monitor.record_tier_failure(3, "timeout", execution_time, error_msg)
            return None, execution_time
        except Exception as e:
            return self._handle_tier3_error(e, execution_trace, start_time)

    def _apply_fallback_strategy(self, results: EvaluationResults) -> EvaluationResults:
        """Apply fallback strategy when tiers fail.

        Args:
            results: Partial evaluation results

        Returns:
            EvaluationResults with fallback applied
        """
        fallback_strategy = self.fallback_strategy
        fallback_applied = False

        if fallback_strategy == "tier1_only" and results.tier1:
            logger.info(
                "Applying tier1_only fallback strategy - creating fallback "
                "results for missing tiers"
            )

            # Create fallback results for missing tiers to enable composite scoring
            if not results.tier2:
                logger.debug("Creating fallback Tier 2 result")
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
                fallback_applied = True

            if not results.tier3:
                logger.debug("Creating fallback Tier 3 result")
                results.tier3 = Tier3Result(
                    path_convergence=0.5,
                    tool_selection_accuracy=0.5,
                    communication_overhead=0.5,
                    coordination_centrality=0.5,
                    task_distribution_balance=0.5,
                    overall_score=0.5,
                    graph_complexity=1,
                )
                fallback_applied = True

            if fallback_applied:
                self.performance_monitor.record_fallback_usage(True)
                logger.info(f"Fallback strategy '{fallback_strategy}' applied successfully.")

        elif not results.tier1:
            logger.warning(
                f"Cannot apply fallback strategy '{fallback_strategy}' - Tier 1 results unavailable"
            )

        return results

    def _log_metric_comparison(
        self, results: EvaluationResults, composite_result: CompositeResult
    ) -> None:
        """Log comparative summary of Tier 1 (text) vs Tier 3 (graph) metrics.

        Args:
            results: EvaluationResults containing tier1 and tier3 results
            composite_result: CompositeResult with composite scoring information
        """
        logger.info("=" * 60)
        logger.info("Evaluation Metrics Comparison Summary")
        logger.info("=" * 60)

        # Log overall tier scores comparison
        tier1_score = composite_result.tier1_score
        tier3_score = composite_result.tier3_score
        logger.info(f"Tier 1 (Text Metrics) overall score: {tier1_score:.3f}")
        logger.info(f"Tier 3 (Graph Analysis) overall score: {tier3_score:.3f}")
        logger.info("")

        # Log individual text metrics from Tier 1
        if results.tier1:
            logger.info("Text Metrics (Tier 1):")
            logger.info(f"  cosine_score: {results.tier1.cosine_score:.3f}")
            logger.info(f"  jaccard_score: {results.tier1.jaccard_score:.3f}")
            logger.info(f"  semantic_score: {results.tier1.semantic_score:.3f}")
            logger.info("")

        # Log individual graph metrics from Tier 3
        if results.tier3:
            logger.info("Graph Metrics (Tier 3):")
            logger.info(f"  path_convergence: {results.tier3.path_convergence:.3f}")
            logger.info(f"  tool_selection_accuracy: {results.tier3.tool_selection_accuracy:.3f}")
            logger.info(f"  communication_overhead: {results.tier3.communication_overhead:.3f}")
            logger.info(f"  coordination_centrality: {results.tier3.coordination_centrality:.3f}")
            logger.info(
                f"  task_distribution_balance: {results.tier3.task_distribution_balance:.3f}"
            )
            logger.info("")

        # Log composite score with tier contributions
        logger.info("Composite Score Summary:")
        logger.info(f"  Final composite score: {composite_result.composite_score:.3f}")
        logger.info(f"  Recommendation: {composite_result.recommendation}")

        # Show metric weights used in composite calculation
        if hasattr(composite_result, "weights_used") and composite_result.weights_used:
            logger.info("  Metric weights used:")
            for metric, weight in composite_result.weights_used.items():
                logger.info(f"    {metric}: {weight:.3f}")

        logger.info("=" * 60)

    async def evaluate_comprehensive(
        self,
        paper: str,
        review: str,
        execution_trace: GraphTraceData | dict[str, Any] | None = None,
        reference_reviews: list[str] | None = None,
    ) -> CompositeResult:
        """Execute comprehensive three-tier evaluation pipeline.

        Args:
            paper: Paper content text for evaluation
            review: Generated review text to assess
            execution_trace: Optional execution trace (GraphTraceData or dict) for graph analysis
            reference_reviews: Optional list of ground truth reviews for similarity

        Returns:
            CompositeResult with scores from all applicable tiers

        Raises:
            ValueError: If critical evaluation components fail
        """
        # Convert GraphTraceData to dict if needed
        trace_dict: dict[str, Any] | None = None
        if execution_trace is not None:
            if isinstance(execution_trace, GraphTraceData):
                trace_dict = execution_trace.model_dump()
            else:
                trace_dict = execution_trace

        # Execute comprehensive evaluation pipeline
        pipeline_start = time.time()
        logger.info("Starting comprehensive three-tier evaluation pipeline")

        # Reset execution stats for new evaluation
        self.performance_monitor.reset_stats()

        try:
            # Execute all enabled tiers
            tier1_result, _ = await self._execute_tier1(paper, review, reference_reviews)
            tier2_result, _ = await self._execute_tier2(paper, review, trace_dict)
            tier3_result, _ = await self._execute_tier3(trace_dict)

            # Execution times are already tracked by performance_monitor in tier methods

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
                raise ValueError("Cannot generate composite score: insufficient tier results")

            # Finalize performance monitoring
            total_time = time.time() - pipeline_start
            self.performance_monitor.finalize_execution(total_time)

            # Get execution statistics and performance summary
            execution_stats = self.performance_monitor.get_execution_stats()
            performance_summary = self.performance_monitor.get_performance_summary()

            logger.info(
                f"Pipeline completed in {total_time:.2f}s, "
                f"tiers executed: {execution_stats['tiers_executed']}, "
                f"composite score: {composite_result.composite_score:.3f}, "
                f"performance: {performance_summary}"
            )

            # Log metric comparison summary
            self._log_metric_comparison(results, composite_result)

            return composite_result

        except Exception as e:
            total_time = time.time() - pipeline_start
            error_type = type(e).__name__
            logger.error(
                f"Pipeline evaluation failed after {total_time:.2f}s with {error_type}: {e}"
            )

            # Record pipeline-level failure for monitoring
            # Note: Using tier 0 for pipeline-level failures
            self.performance_monitor.record_tier_failure(0, "critical_error", total_time, str(e))
            self.performance_monitor.finalize_execution(total_time)

            raise

    def get_execution_stats(self) -> dict[str, Any]:
        """Get detailed execution statistics from last pipeline run.

        Returns:
            Dictionary with timing and execution details including performance analysis
        """
        return self.performance_monitor.get_execution_stats()

    def get_pipeline_summary(self) -> dict[str, Any]:
        """Get pipeline configuration summary.

        Returns:
            Dictionary with pipeline configuration details
        """
        return {
            "config_path": None,
            "enabled_tiers": sorted(self.settings.get_enabled_tiers()),
            "fallback_strategy": self.settings.fallback_strategy,
            "performance_targets": self.settings.get_performance_targets(),
            "has_tier1_config": True,
            "has_tier2_config": True,
            "has_tier3_config": True,
        }
