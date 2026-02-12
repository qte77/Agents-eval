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
from app.evals.evaluation_config import EvaluationConfig
from app.evals.graph_analysis import GraphAnalysisEngine
from app.evals.llm_evaluation_managers import LLMJudgeEngine
from app.evals.performance_monitor import PerformanceMonitor
from app.evals.settings import JudgeSettings
from app.evals.traditional_metrics import TraditionalMetricsEngine
from app.utils.load_configs import OpikConfig
from app.utils.log import logger

# Set up Opik imports with fallback
OPIK_AVAILABLE: bool = False
track = None  # type: ignore

try:
    from opik import track  # type: ignore

    OPIK_AVAILABLE = True  # type: ignore
except ImportError:
    # Fallback when opik is not available
    def track(**kwargs: Any) -> Any:  # type: ignore
        """No-op decorator fallback."""

        def decorator(func: Any) -> Any:
            return func

        return decorator


class EvaluationPipeline:
    """
    Streamlined evaluation pipeline orchestrator for three-tier assessment.

    Coordinates execution of Traditional Metrics → LLM-as-Judge → Graph Analysis
    with configurable tier enabling and graceful degradation. Uses modular
    components for configuration management and performance monitoring.
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        settings: JudgeSettings | None = None,
    ):
        """Initialize evaluation pipeline with configuration.

        Args:
            config_path: (Deprecated) Path to config_eval.json file. If None, uses default location.
            settings: JudgeSettings instance. If provided, takes precedence over config_path.

        Raises:
            FileNotFoundError: If configuration file not found (legacy mode)
            ValueError: If configuration is invalid
        """
        # Prefer JudgeSettings over legacy config_path
        if settings is not None:
            self.settings = settings
            self.config_manager = None  # No longer needed
            self.performance_monitor = PerformanceMonitor(settings.get_performance_targets())

            # Initialize Opik configuration from settings
            # Reason: OpikConfig needs dict structure, convert from settings
            config_dict = {
                "observability": {
                    "opik_enabled": settings.opik_enabled,
                    "trace_collection": settings.trace_collection,
                    "performance_logging": settings.performance_logging,
                }
            }
            self.opik_config = OpikConfig.from_config(config_dict)

            # Initialize engines with settings-based config
            tier2_config = settings.get_tier2_config()
            tier3_config = settings.get_tier3_config()

            self.traditional_engine = TraditionalMetricsEngine()
            self.llm_engine = LLMJudgeEngine(tier2_config)
            self.graph_engine = GraphAnalysisEngine(tier3_config)
            self.composite_scorer = CompositeScorer(settings=settings)

            enabled_tiers = sorted(settings.get_enabled_tiers())
            fallback_strategy = settings.fallback_strategy
            logger.info(
                f"EvaluationPipeline initialized with JudgeSettings: tiers={enabled_tiers}, "
                f"fallback_strategy={fallback_strategy}"
            )
        else:
            # Legacy path: use EvaluationConfig (deprecated)
            self.settings = None
            self.config_manager = EvaluationConfig(config_path)
            self.performance_monitor = PerformanceMonitor(
                self.config_manager.get_performance_targets()
            )

            # Initialize Opik configuration
            config_dict = self.config_manager.get_full_config()
            self.opik_config = OpikConfig.from_config(config_dict)

            # Initialize engines with configuration
            self.traditional_engine = TraditionalMetricsEngine()
            self.llm_engine = LLMJudgeEngine(config_dict)
            self.graph_engine = GraphAnalysisEngine(config_dict)
            self.composite_scorer = CompositeScorer(self.config_manager.config_path)

            enabled_tiers = sorted(self.config_manager.get_enabled_tiers())
            fallback_strategy = self.fallback_strategy
            logger.info(
                f"EvaluationPipeline initialized with tiers: {enabled_tiers}, "
                f"fallback_strategy: {fallback_strategy}, "
                f"config: {self.config_manager.config_path}"
            )

        # Pre-configure Opik decorator for performance optimization
        self._opik_decorator_enabled = OPIK_AVAILABLE and self.opik_config.enabled

    @property
    def enabled_tiers(self) -> set[int]:
        """Get enabled tiers (backward compatibility property).

        Returns:
            Set of enabled tier numbers
        """
        if self.settings is not None:
            return self.settings.get_enabled_tiers()
        assert self.config_manager is not None
        return self.config_manager.get_enabled_tiers()

    @property
    def performance_targets(self) -> dict[str, float]:
        """Get performance targets (backward compatibility property).

        Returns:
            Dictionary of performance targets
        """
        if self.settings is not None:
            return self.settings.get_performance_targets()
        assert self.config_manager is not None
        return self.config_manager.get_performance_targets()

    @property
    def fallback_strategy(self) -> str:
        """Get fallback strategy (backward compatibility property).

        Returns:
            Fallback strategy name
        """
        if self.settings is not None:
            return self.settings.fallback_strategy
        assert self.config_manager is not None
        return self.config_manager.get_fallback_strategy()

    @property
    def config_path(self) -> Path | None:
        """Get configuration path (backward compatibility property).

        Returns:
            Path to configuration file (None if using JudgeSettings)
        """
        if self.settings is not None:
            return None
        assert self.config_manager is not None
        return self.config_manager.config_path

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
        if self.settings is not None:
            return self.settings.is_tier_enabled(tier)
        assert self.config_manager is not None
        return self.config_manager.is_tier_enabled(tier)

    def _get_tier_config(self, tier: int) -> dict[str, Any]:
        """Get tier-specific configuration (internal helper).

        Args:
            tier: Tier number (1, 2, or 3)

        Returns:
            Tier configuration dictionary
        """
        if self.settings is not None:
            if tier == 1:
                return self.settings.get_tier1_config()
            elif tier == 2:
                return self.settings.get_tier2_config()
            else:  # tier == 3
                return self.settings.get_tier3_config()
        else:
            assert self.config_manager is not None
            if tier == 1:
                return self.config_manager.get_tier1_config()
            elif tier == 2:
                return self.config_manager.get_tier2_config()
            else:  # tier == 3
                return self.config_manager.get_tier3_config()

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
            tier1_config = self._get_tier_config(1)

            result = await asyncio.wait_for(
                asyncio.create_task(
                    asyncio.to_thread(
                        self.traditional_engine.evaluate_traditional_metrics,
                        review,  # agent_output
                        ref_reviews,  # reference_texts
                        start_evaluation,  # start_time
                        time.time(),  # end_time (will be updated in method)
                        tier1_config,  # config
                    )
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(1, execution_time)
            self._record_opik_metadata(1, execution_time, result)
            logger.info(f"Tier 1 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 timeout after {timeout}s (traditional metrics evaluation)"
            logger.error(f"{error_msg}. Consider increasing tier1_max_seconds in config.")
            self.performance_monitor.record_tier_failure(1, "timeout", execution_time, error_msg)
            self._record_opik_metadata(1, execution_time, error=error_msg)
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 failed with {type(e).__name__}: {e}"
            logger.error(f"{error_msg}. Paper length: {len(paper)}, Review length: {len(review)}")
            self.performance_monitor.record_tier_failure(1, "error", execution_time, str(e))
            self._record_opik_metadata(1, execution_time, error=error_msg)
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
            self._record_opik_metadata(2, execution_time, result)
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
            self._record_opik_metadata(2, execution_time, error=error_msg)
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
            self._record_opik_metadata(2, execution_time, error=error_msg)
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
                    asyncio.to_thread(self.graph_engine.evaluate_graph_metrics, trace_data)
                ),
                timeout=timeout,
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(3, execution_time)
            self._record_opik_metadata(3, execution_time, result)
            logger.info(f"Tier 3 completed in {execution_time:.2f}s")
            return result, execution_time

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 3 timeout after {timeout}s (Graph analysis evaluation)"
            logger.error(
                f"{error_msg}. Consider increasing tier3_max_seconds or simplifying trace data."
            )
            self.performance_monitor.record_tier_failure(3, "timeout", execution_time, error_msg)
            self._record_opik_metadata(3, execution_time, error=error_msg)
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            trace_size = len(str(execution_trace)) if execution_trace else 0
            error_msg = f"Tier 3 failed with {error_type}: {e}"
            logger.error(f"{error_msg}. Trace data size: {trace_size} chars")
            # Add specific guidance for common graph analysis issues
            if "memory" in str(e).lower():
                logger.error("Memory error - consider reducing trace data complexity")
            elif "networkx" in str(e).lower():
                logger.error("Graph construction error - check trace data format")
            self.performance_monitor.record_tier_failure(3, "error", execution_time, str(e))
            self._record_opik_metadata(3, execution_time, error=error_msg)
            return None, execution_time

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

    def _apply_opik_decorator(self, func: Any) -> Any:
        """Apply Opik tracking decorator if available and enabled."""
        if self._opik_decorator_enabled:
            return track(
                name="evaluation_pipeline_comprehensive",
                tags=["evaluation", "three-tier", "pipeline"],
            )(func)
        return func

    def _record_opik_metadata(
        self, tier: int, execution_time: float, result: Any = None, error: str | None = None
    ):
        """Record tier execution metadata for Opik tracing."""
        if not self._opik_decorator_enabled:
            return

        # Reason: Opik metadata recording is handled by the @track decorator
        # This method serves as a placeholder for future enhanced metadata collection
        try:
            metadata: dict[str, Any] = {
                f"tier{tier}_execution_time": float(execution_time),
                f"tier{tier}_success": bool(error is None),
                "enabled_tiers": list(self.enabled_tiers),
            }
            if error:
                metadata[f"tier{tier}_error"] = str(error)
            if result:
                metadata[f"tier{tier}_result_type"] = str(type(result).__name__)

            logger.debug(f"Opik metadata for tier {tier}: {metadata}")
        except Exception as e:
            logger.debug(f"Failed to record Opik metadata: {e}")

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
        # Apply Opik decorator dynamically
        decorated_func = self._apply_opik_decorator(self._evaluate_comprehensive_impl)
        return await decorated_func(paper, review, execution_trace, reference_reviews)

    async def _evaluate_comprehensive_impl(
        self,
        paper: str,
        review: str,
        execution_trace: dict[str, Any] | None = None,
        reference_reviews: list[str] | None = None,
    ) -> CompositeResult:
        """Implementation of comprehensive evaluation pipeline."""
        pipeline_start = time.time()
        logger.info("Starting comprehensive three-tier evaluation pipeline")

        # Reset execution stats for new evaluation
        self.performance_monitor.reset_stats()

        try:
            # Execute all enabled tiers
            tier1_result, _ = await self._execute_tier1(paper, review, reference_reviews)
            tier2_result, _ = await self._execute_tier2(paper, review, execution_trace)
            tier3_result, _ = await self._execute_tier3(execution_trace)

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
        if self.settings is not None:
            return {
                "config_path": None,
                "enabled_tiers": sorted(self.settings.get_enabled_tiers()),
                "fallback_strategy": self.settings.fallback_strategy,
                "performance_targets": self.settings.get_performance_targets(),
                "has_tier1_config": True,
                "has_tier2_config": True,
                "has_tier3_config": True,
            }
        assert self.config_manager is not None
        return self.config_manager.get_config_summary()
