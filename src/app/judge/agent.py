"""
JudgeAgent orchestrator for tier-ordered evaluation.

Replaces EvaluationPipeline with plugin-based architecture using
PluginRegistry for modular, extensible evaluation execution.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from app.data_models.evaluation_models import CompositeResult, GraphTraceData
from app.evals.settings import JudgeSettings
from app.judge.composite_scorer import CompositeScorer, EvaluationResults
from app.judge.performance_monitor import PerformanceMonitor
from app.judge.plugins import (
    GraphEvaluatorPlugin,
    LLMJudgePlugin,
    PluginRegistry,
    TraditionalMetricsPlugin,
)
from app.judge.trace_store import TraceStore
from app.utils.log import logger


class JudgeAgent:
    """
    Plugin-based evaluation orchestrator replacing EvaluationPipeline.

    Uses PluginRegistry for tier-ordered execution with context passing
    between tiers. Maintains backward compatibility with EvaluationPipeline
    interface while providing cleaner plugin architecture.

    Attributes:
        settings: JudgeSettings configuration
        registry: PluginRegistry for plugin management
        trace_store: TraceStore for execution traces
        composite_scorer: CompositeScorer for final scoring
        performance_monitor: PerformanceMonitor for metrics
    """

    def __init__(self, settings: JudgeSettings | None = None) -> None:
        """Initialize JudgeAgent with settings and plugins.

        Args:
            settings: JudgeSettings instance. If None, uses default JudgeSettings().
        """
        if settings is None:
            settings = JudgeSettings()

        self.settings = settings
        self.performance_monitor = PerformanceMonitor(settings.get_performance_targets())
        self.composite_scorer = CompositeScorer(settings=settings)
        self.trace_store = TraceStore()
        self.registry = PluginRegistry()

        # Register plugins for all tiers
        self._register_plugins()

        enabled_tiers = sorted(settings.get_enabled_tiers())
        logger.info(
            f"JudgeAgent initialized with {len(self.registry.list_plugins())} plugins, "
            f"enabled tiers: {enabled_tiers}"
        )

    def _register_plugins(self) -> None:
        """Register all evaluation plugins."""
        # Tier 1: Traditional Metrics
        tier1_timeout = self.settings.tier1_max_seconds
        self.registry.register(TraditionalMetricsPlugin(timeout_seconds=tier1_timeout))

        # Tier 2: LLM-as-Judge
        tier2_timeout = self.settings.tier2_max_seconds
        self.registry.register(LLMJudgePlugin(timeout_seconds=tier2_timeout))

        # Tier 3: Graph Analysis
        tier3_timeout = self.settings.tier3_max_seconds
        self.registry.register(GraphEvaluatorPlugin(timeout_seconds=tier3_timeout))

        logger.debug("Registered 3 evaluation plugins (Tier 1, 2, 3)")

    @property
    def enabled_tiers(self) -> set[int]:
        """Get enabled tiers (backward compatibility).

        Returns:
            Set of enabled tier numbers
        """
        return self.settings.get_enabled_tiers()

    @property
    def performance_targets(self) -> dict[str, float]:
        """Get performance targets (backward compatibility).

        Returns:
            Dictionary of performance targets
        """
        return self.settings.get_performance_targets()

    async def evaluate_comprehensive(
        self,
        paper: str,
        review: str,
        execution_trace: GraphTraceData | dict[str, Any] | None = None,
        reference_reviews: list[str] | None = None,
    ) -> CompositeResult:
        """Execute comprehensive three-tier evaluation using plugins.

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
        pipeline_start = time.time()
        logger.info("Starting JudgeAgent comprehensive evaluation")

        # Reset performance stats
        self.performance_monitor.reset_stats()

        try:
            # Execute tiers using plugin registry
            results = await self._execute_tiers(
                paper=paper,
                review=review,
                execution_trace=execution_trace,
                reference_reviews=reference_reviews,
            )

            # Generate composite score
            if results.is_complete():
                composite_result = self.composite_scorer.evaluate_composite(results)
            else:
                # Use fallback evaluation for incomplete results
                composite_result = self.composite_scorer.evaluate_composite_with_optional_tier2(
                    results
                )

            # Finalize monitoring
            total_time = time.time() - pipeline_start
            self.performance_monitor.finalize_execution(total_time)

            execution_stats = self.performance_monitor.get_execution_stats()
            performance_summary = self.performance_monitor.get_performance_summary()

            logger.info(
                f"JudgeAgent completed in {total_time:.2f}s, "
                f"tiers executed: {execution_stats['tiers_executed']}, "
                f"composite score: {composite_result.composite_score:.3f}, "
                f"performance: {performance_summary}"
            )

            return composite_result

        except Exception as e:
            total_time = time.time() - pipeline_start
            error_type = type(e).__name__
            logger.error(
                f"JudgeAgent evaluation failed after {total_time:.2f}s with {error_type}: {e}"
            )

            # Record failure
            self.performance_monitor.record_tier_failure(0, "critical_error", total_time, str(e))
            self.performance_monitor.finalize_execution(total_time)

            raise

    async def _execute_tiers(
        self,
        paper: str,
        review: str,
        execution_trace: GraphTraceData | dict[str, Any] | None,
        reference_reviews: list[str] | None,
    ) -> EvaluationResults:
        """Execute all enabled tiers with timeout and error handling.

        Args:
            paper: Paper content
            review: Review text
            execution_trace: Optional trace data
            reference_reviews: Optional reference reviews

        Returns:
            EvaluationResults with tier results
        """
        # Convert execution_trace to dict if needed
        trace_dict: dict[str, Any] | None = None
        if execution_trace is not None:
            if isinstance(execution_trace, GraphTraceData):
                trace_dict = execution_trace.model_dump()
            else:
                trace_dict = execution_trace

        # Execute Tier 1
        tier1_result = None
        if self.settings.is_tier_enabled(1):
            tier1_result = await self._execute_tier1(paper, review, reference_reviews)

        # Execute Tier 2
        tier2_result = None
        if self.settings.is_tier_enabled(2):
            tier2_result = await self._execute_tier2(paper, review, trace_dict)

        # Execute Tier 3
        tier3_result = None
        if self.settings.is_tier_enabled(3):
            tier3_result = await self._execute_tier3(trace_dict)

        return EvaluationResults(tier1=tier1_result, tier2=tier2_result, tier3=tier3_result)

    async def _execute_tier1(
        self, paper: str, review: str, reference_reviews: list[str] | None
    ) -> Any:
        """Execute Tier 1 evaluation with timeout."""
        timeout = self.settings.tier1_max_seconds
        start_time = time.time()

        try:
            logger.info("Executing Tier 1: Traditional Metrics")

            # Create input data for plugin
            from pydantic import BaseModel

            class Tier1Input(BaseModel):
                agent_output: str
                reference_texts: list[str]
                start_time: float
                end_time: float

            input_data = Tier1Input(
                agent_output=review,
                reference_texts=reference_reviews or [""],
                start_time=start_time,
                end_time=time.time(),
            )

            plugin = self.registry.get_plugin("traditional_metrics")
            if plugin is None:
                raise ValueError("Traditional metrics plugin not found")

            result = await asyncio.wait_for(
                asyncio.to_thread(plugin.evaluate, input_data), timeout=timeout
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(1, execution_time)
            logger.info(f"Tier 1 completed in {execution_time:.2f}s")

            # Store trace
            self.trace_store.add_trace("tier1_result", result.model_dump())

            return result

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 timeout after {timeout}s"
            logger.error(error_msg)
            self.performance_monitor.record_tier_failure(1, "timeout", execution_time, error_msg)
            return None
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tier 1 failed: {e}"
            logger.error(error_msg)
            self.performance_monitor.record_tier_failure(1, "error", execution_time, str(e))
            return None

    async def _execute_tier2(
        self, paper: str, review: str, execution_trace: dict[str, Any] | None
    ) -> Any:
        """Execute Tier 2 evaluation with timeout."""
        timeout = self.settings.tier2_max_seconds
        start_time = time.time()

        try:
            logger.info("Executing Tier 2: LLM-as-Judge")

            # Create input data for plugin
            from pydantic import BaseModel

            class Tier2Input(BaseModel):
                paper: str
                review: str
                execution_trace: dict[str, Any]

            input_data = Tier2Input(
                paper=paper, review=review, execution_trace=execution_trace or {}
            )

            plugin = self.registry.get_plugin("llm_judge")
            if plugin is None:
                raise ValueError("LLM judge plugin not found")

            # Get context from Tier 1 if available
            tier1_trace = self.trace_store.get_trace("tier1_result")
            context = {"tier1": tier1_trace} if tier1_trace else None

            result = await asyncio.wait_for(
                asyncio.to_thread(plugin.evaluate, input_data, context), timeout=timeout
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(2, execution_time)
            logger.info(f"Tier 2 completed in {execution_time:.2f}s")

            # Store trace
            self.trace_store.add_trace("tier2_result", result.model_dump())

            return result

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 2 timeout after {timeout}s"
            logger.error(error_msg)
            self.performance_monitor.record_tier_failure(2, "timeout", execution_time, error_msg)
            return None
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tier 2 failed: {e}"
            logger.error(error_msg)
            self.performance_monitor.record_tier_failure(2, "error", execution_time, str(e))
            return None

    async def _execute_tier3(self, execution_trace: dict[str, Any] | None) -> Any:
        """Execute Tier 3 evaluation with timeout."""
        timeout = self.settings.tier3_max_seconds
        start_time = time.time()

        try:
            logger.info("Executing Tier 3: Graph Analysis")

            # Create trace data
            if execution_trace:
                trace_data = GraphTraceData(
                    execution_id=execution_trace.get("execution_id", "judge_exec"),
                    agent_interactions=execution_trace.get("agent_interactions", []),
                    tool_calls=execution_trace.get("tool_calls", []),
                    timing_data=execution_trace.get("timing_data", {}),
                    coordination_events=execution_trace.get("coordination_events", []),
                )
            else:
                trace_data = GraphTraceData(
                    execution_id="judge_minimal",
                    agent_interactions=[],
                    tool_calls=[],
                    timing_data={},
                    coordination_events=[],
                )

            # Create input for plugin
            from pydantic import BaseModel

            class Tier3Input(BaseModel):
                trace_data: GraphTraceData

            input_data = Tier3Input(trace_data=trace_data)

            plugin = self.registry.get_plugin("graph_metrics")
            if plugin is None:
                raise ValueError("Graph metrics plugin not found")

            result = await asyncio.wait_for(
                asyncio.to_thread(plugin.evaluate, input_data), timeout=timeout
            )

            execution_time = time.time() - start_time
            self.performance_monitor.record_tier_execution(3, execution_time)
            logger.info(f"Tier 3 completed in {execution_time:.2f}s")

            # Store trace
            self.trace_store.add_trace("tier3_result", result.model_dump())

            return result

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tier 3 timeout after {timeout}s"
            logger.error(error_msg)
            self.performance_monitor.record_tier_failure(3, "timeout", execution_time, error_msg)
            return None
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tier 3 failed: {e}"
            logger.error(error_msg)
            self.performance_monitor.record_tier_failure(3, "error", execution_time, str(e))
            return None

    def get_execution_stats(self) -> dict[str, Any]:
        """Get execution statistics (backward compatibility).

        Returns:
            Dictionary with execution statistics
        """
        return self.performance_monitor.get_execution_stats()
