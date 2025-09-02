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
    execution_stats: dict[str, Any]

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

        # Enhanced performance tracking
        self.execution_stats: dict[str, Any] = {
            "tier1_time": 0.0,
            "tier2_time": 0.0,
            "tier3_time": 0.0,
            "total_time": 0.0,
            "tiers_executed": [],
            "fallback_used": False,
            "tier_failures": [],
            "performance_warnings": [],
            "bottlenecks_detected": [],
        }

        logger.info(
            f"EvaluationPipeline initialized with tiers: {sorted(self.enabled_tiers)}, "
            f"fallback_strategy: {self.fallback_strategy}, "
            f"config: {self.config_path}"
        )

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate pipeline configuration structure and values.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid
        """
        required_sections = ["evaluation_system", "composite_scoring"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate enabled tiers
        tiers = config.get("evaluation_system", {}).get("tiers_enabled", [])
        if not isinstance(tiers, list) or not all(
            isinstance(t, int) and 1 <= t <= 3 for t in tiers
        ):
            raise ValueError("tiers_enabled must be a list of integers between 1 and 3")

        # Validate performance targets
        perf_targets = config.get("evaluation_system", {}).get(
            "performance_targets", {}
        )
        if perf_targets:
            for key, value in perf_targets.items():
                if not isinstance(value, int | float) or value <= 0:
                    raise ValueError(
                        f"Performance target {key} must be a positive number"
                    )

        logger.debug("Configuration validation passed")

    def _record_tier_failure(
        self, tier: int, failure_type: str, execution_time: float, error_msg: str
    ) -> None:
        """Record tier failure details for monitoring and analysis.

        Args:
            tier: Tier number that failed
            failure_type: Type of failure (timeout, error)
            execution_time: Time spent before failure
            error_msg: Error message
        """
        if "tier_failures" not in self.execution_stats:
            self.execution_stats["tier_failures"] = []

        failure_record = {
            "tier": tier,
            "failure_type": failure_type,
            "execution_time": execution_time,
            "error_msg": error_msg,
            "timestamp": time.time(),
        }

        if isinstance(self.execution_stats["tier_failures"], list):
            self.execution_stats["tier_failures"].append(failure_record)

        logger.debug(
            f"Recorded tier {tier} failure: {failure_type} after {execution_time:.2f}s"
        )

    def _load_config(self) -> dict[str, Any]:
        """Load evaluation configuration from JSON file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file not found
            json.JSONDecodeError: If invalid JSON
            ValueError: If configuration validation fails
        """
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            logger.debug(f"Loaded pipeline configuration from {self.config_path}")

            # Enhanced configuration validation
            self._validate_config(config)
            return config
        except FileNotFoundError as e:
            error_msg = f"Pipeline configuration file not found: {self.config_path}"
            logger.error(
                f"{error_msg}. Please ensure config file exists and is accessible."
            )
            raise FileNotFoundError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in pipeline configuration: {e}"
            logger.error(
                f"{error_msg}. Check file syntax at line "
                f"{e.lineno if hasattr(e, 'lineno') else 'unknown'}."
            )
            raise json.JSONDecodeError(error_msg, e.doc, e.pos) from e
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
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
            error_msg = (
                f"Tier 1 timeout after {timeout}s (traditional metrics evaluation)"
            )
            logger.error(
                f"{error_msg}. Consider increasing tier1_max_seconds in config."
            )
            # Reason: Record timeout details for performance analysis
            self._record_tier_failure(1, "timeout", execution_time, error_msg)
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 failed with {type(e).__name__}: {e}"
            logger.error(
                f"{error_msg}. Paper length: {len(paper)}, Review length: {len(review)}"
            )
            # Reason: Record error details for debugging and monitoring
            self._record_tier_failure(1, "error", execution_time, str(e))
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
            error_msg = f"Tier 2 timeout after {timeout}s (LLM-as-Judge evaluation)"
            logger.error(
                f"{error_msg}. Consider increasing tier2_max_seconds or "
                f"check LLM service availability."
            )
            # Reason: Record timeout details for performance analysis
            self._record_tier_failure(2, "timeout", execution_time, error_msg)
            return None, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            error_msg = f"Tier 2 failed with {error_type}: {e}"
            logger.error(
                f"{error_msg}. Paper length: {len(paper)}, Review length: {len(review)}"
            )
            # Add specific guidance based on error type
            if "rate limit" in str(e).lower():
                logger.error(
                    "Rate limit exceeded - consider adjusting request frequency"
                )
            elif "authentication" in str(e).lower():
                logger.error("Authentication failed - check API keys and configuration")
            elif "connection" in str(e).lower():
                logger.error(
                    "Connection failed - check network connectivity and "
                    "service availability"
                )
            # Reason: Record error details for debugging and monitoring
            self._record_tier_failure(2, "error", execution_time, str(e))
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
            error_msg = f"Tier 3 timeout after {timeout}s (Graph analysis evaluation)"
            logger.error(
                f"{error_msg}. Consider increasing tier3_max_seconds or "
                f"simplifying trace data."
            )
            # Reason: Record timeout details for performance analysis
            self._record_tier_failure(3, "timeout", execution_time, error_msg)
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
            # Reason: Record error details for debugging and monitoring
            self._record_tier_failure(3, "error", execution_time, str(e))
            return None, execution_time

    def _apply_fallback_strategy(self, results: EvaluationResults) -> EvaluationResults:
        """Apply fallback strategy when tiers fail.

        Args:
            results: Partial evaluation results

        Returns:
            EvaluationResults with fallback applied
        """
        fallback_applied = False

        if self.fallback_strategy == "tier1_only" and results.tier1:
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
                self.execution_stats["fallback_used"] = True
                self.execution_stats["fallback_details"] = {
                    "strategy": self.fallback_strategy,
                    "tier1_available": bool(results.tier1),
                    "tier2_fallback": not bool(results.tier2),
                    "tier3_fallback": not bool(results.tier3),
                }
                logger.info(
                    f"Fallback strategy applied successfully. Details: "
                    f"{self.execution_stats['fallback_details']}"
                )

        elif not results.tier1:
            logger.warning(
                f"Cannot apply fallback strategy '{self.fallback_strategy}' - "
                f"Tier 1 results unavailable"
            )

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

        # Reset execution stats with enhanced tracking
        self.execution_stats = {
            "tier1_time": 0.0,
            "tier2_time": 0.0,
            "tier3_time": 0.0,
            "total_time": 0.0,
            "tiers_executed": [],
            "fallback_used": False,
            "tier_failures": [],
            "performance_warnings": [],
            "bottlenecks_detected": [],
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

            # Enhanced performance analysis and bottleneck detection
            self._analyze_performance(total_time)

            # Check performance targets with detailed warnings
            max_total_time = self.performance_targets.get("total_max_seconds", 25.0)
            if total_time > max_total_time:
                warning_msg = (
                    f"Pipeline exceeded time target: {total_time:.2f}s > "
                    f"{max_total_time}s"
                )
                logger.warning(warning_msg)
                self._record_performance_warning(
                    "total_time_exceeded", warning_msg, total_time
                )

            # Enhanced completion logging with performance insights
            performance_summary = self._get_performance_summary()
            logger.info(
                f"Pipeline completed in {total_time:.2f}s, "
                f"tiers executed: {self.execution_stats['tiers_executed']}, "
                f"composite score: {composite_result.composite_score:.3f}, "
                f"performance: {performance_summary}"
            )

            return composite_result

        except Exception as e:
            total_time = time.time() - pipeline_start
            self.execution_stats["total_time"] = total_time
            error_type = type(e).__name__
            logger.error(
                f"Pipeline evaluation failed after {total_time:.2f}s with "
                f"{error_type}: {e}"
            )

            # Record pipeline-level failure for monitoring
            if "tier_failures" not in self.execution_stats:
                self.execution_stats["tier_failures"] = []

            if isinstance(self.execution_stats["tier_failures"], list):
                self.execution_stats["tier_failures"].append(
                    {
                        "tier": "pipeline",
                        "failure_type": "critical_error",
                        "execution_time": total_time,
                        "error_msg": str(e),
                        "error_type": error_type,
                        "timestamp": time.time(),
                    }
                )

            raise

    def get_execution_stats(self) -> dict[str, Any]:
        """Get detailed execution statistics from last pipeline run.

        Returns:
            Dictionary with timing and execution details including performance analysis
        """
        stats = self.execution_stats.copy()

        # Add derived performance metrics
        if stats["total_time"] > 0:
            stats["tier_time_percentages"] = {
                "tier1": (stats["tier1_time"] / stats["total_time"]) * 100,
                "tier2": (stats["tier2_time"] / stats["total_time"]) * 100,
                "tier3": (stats["tier3_time"] / stats["total_time"]) * 100,
            }

        return stats

    def _analyze_performance(self, total_time: float) -> None:
        """Analyze pipeline performance and detect bottlenecks.

        Args:
            total_time: Total pipeline execution time
        """
        tier_times = {
            "tier1": self.execution_stats["tier1_time"],
            "tier2": self.execution_stats["tier2_time"],
            "tier3": self.execution_stats["tier3_time"],
        }

        # Identify bottlenecks (tiers taking >40% of total time)
        bottleneck_threshold = total_time * 0.4
        bottlenecks = []

        for tier, time_taken in tier_times.items():
            if time_taken > bottleneck_threshold and time_taken > 0:
                bottlenecks.append(
                    {
                        "tier": tier,
                        "time": time_taken,
                        "percentage": (time_taken / total_time) * 100,
                    }
                )

        if bottlenecks:
            self.execution_stats["bottlenecks_detected"] = bottlenecks
            for bottleneck in bottlenecks:
                logger.warning(
                    f"Performance bottleneck detected: {bottleneck['tier']} took "
                    f"{bottleneck['time']:.2f}s "
                    f"({bottleneck['percentage']:.1f}% of total time)"
                )

        # Check individual tier targets
        for tier_num in range(1, 4):
            tier_key = f"tier{tier_num}"
            target_key = f"tier{tier_num}_max_seconds"

            if target_key in self.performance_targets and tier_times[tier_key] > 0:
                target_time = self.performance_targets[target_key]
                actual_time = tier_times[tier_key]

                if actual_time > target_time:
                    warning_msg = (
                        f"Tier {tier_num} exceeded target: {actual_time:.2f}s > "
                        f"{target_time}s"
                    )
                    self._record_performance_warning(
                        f"tier{tier_num}_time_exceeded", warning_msg, actual_time
                    )

    def _record_performance_warning(
        self, warning_type: str, message: str, value: float
    ) -> None:
        """Record performance warning for monitoring.

        Args:
            warning_type: Type of warning
            message: Warning message
            value: Associated numeric value
        """
        warning_record = {
            "type": warning_type,
            "message": message,
            "value": value,
            "timestamp": time.time(),
        }

        if isinstance(self.execution_stats["performance_warnings"], list):
            self.execution_stats["performance_warnings"].append(warning_record)

    def _get_performance_summary(self) -> str:
        """Get concise performance summary.

        Returns:
            Performance summary string
        """
        bottlenecks = len(self.execution_stats.get("bottlenecks_detected", []))
        warnings = len(self.execution_stats.get("performance_warnings", []))
        failures = len(self.execution_stats.get("tier_failures", []))

        return f"bottlenecks={bottlenecks}, warnings={warnings}, failures={failures}"

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
