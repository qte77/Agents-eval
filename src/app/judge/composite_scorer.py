"""
Composite scoring system for three-tiered evaluation framework.

Integrates Traditional Metrics (Tier 1), LLM-as-Judge (Tier 2), and
Graph Analysis (Tier 3) into unified scoring system with recommendation mapping.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from app.data_models.evaluation_models import (
    CompositeResult,
    GraphTraceData,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.utils.log import logger

if TYPE_CHECKING:
    from app.judge.settings import JudgeSettings


class AgentMetrics(BaseModel):
    """Simple agent-level metrics for evaluation enhancement."""

    tool_selection_score: float = 0.7  # Default neutral score
    plan_coherence_score: float = 0.7  # Default neutral score
    coordination_score: float = 0.7  # Default neutral score

    def get_agent_composite_score(self) -> float:
        """Calculate simple weighted composite score for agent metrics."""
        weights = {
            "tool_selection": 0.35,
            "plan_coherence": 0.35,
            "coordination": 0.30,
        }
        return (
            self.tool_selection_score * weights["tool_selection"]
            + self.plan_coherence_score * weights["plan_coherence"]
            + self.coordination_score * weights["coordination"]
        )


class EvaluationResults(BaseModel):
    """Container for all three evaluation tier results."""

    tier1: Tier1Result | None = None
    tier2: Tier2Result | None = None
    tier3: Tier3Result | None = None

    def is_complete(self) -> bool:
        """Check if all required tiers have results."""
        return all([self.tier1, self.tier2, self.tier3])


class CompositeScorer:
    """
    Composite scoring system that integrates all three evaluation tiers.

    Implements the six-metric equal-weight formula:
    - time_taken (0.167)
    - task_success (0.167)
    - coordination_quality (0.167)
    - tool_efficiency (0.167)
    - planning_rationality (0.167)
    - output_similarity (0.167)

    Maps scores to recommendation categories with thresholds.
    """

    def __init__(
        self,
        settings: "JudgeSettings | None" = None,
    ):
        """Initialize composite scorer with configuration.

        Args:
            settings: JudgeSettings instance. If None, uses default JudgeSettings().
        """
        # Import here to avoid circular dependency
        if settings is None:
            from app.judge.settings import JudgeSettings

            settings = JudgeSettings()

        # Use JudgeSettings
        self.settings = settings

        # Equal-weight scoring across six composite metrics
        self.weights = {
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167,
            "tool_efficiency": 0.167,
            "planning_rationality": 0.167,
            "output_similarity": 0.167,
        }
        self.thresholds = {
            "accept": settings.composite_accept_threshold,
            "weak_accept": settings.composite_weak_accept_threshold,
            "weak_reject": settings.composite_weak_reject_threshold,
            "reject": 0.0,
        }
        self.recommendation_weights = {
            "accept": 1.0,
            "weak_accept": 0.7,
            "weak_reject": -0.7,
            "reject": -1.0,
        }

        logger.info(f"CompositeScorer initialized with JudgeSettings ({len(self.weights)} metrics)")

    def extract_metric_values(self, results: EvaluationResults) -> dict[str, float]:
        """Extract the six composite metrics from tier results.

        Args:
            results: Container with tier1, tier2, tier3 evaluation results

        Returns:
            Dictionary with normalized metric values (0.0 to 1.0)

        Raises:
            ValueError: If required tier results are missing
        """
        if not results.is_complete():
            missing_tiers = []
            if not results.tier1:
                missing_tiers.append("tier1")
            if not results.tier2:
                missing_tiers.append("tier2")
            if not results.tier3:
                missing_tiers.append("tier3")
            raise ValueError(f"Missing required tier results: {missing_tiers}")

        # Extract metrics following the sprint document specification
        # At this point, we know all tiers are non-None due to is_complete() check
        assert results.tier1 is not None, "tier1 should not be None after check"
        assert results.tier2 is not None, "tier2 should not be None after check"
        assert results.tier3 is not None, "tier3 should not be None after check"

        # Reason: Task 4.1 requires these exact 6 metrics with specific source mappings
        # Each metric maps to specific fields from evaluation tier results
        metrics = {
            # From Tier 1: Traditional metrics + execution performance
            # Reason: time_score is already normalized [0,1] where higher = better (faster)
            "time_taken": results.tier1.time_score,
            "task_success": results.tier1.task_success,  # binary completion flag
            "output_similarity": results.tier1.overall_score,  # weighted similarity
            # From Tier 2: LLM-as-Judge quality assessment - use specific metric
            "planning_rationality": results.tier2.planning_rationality,
            # From Tier 3: Graph-based coordination analysis
            "coordination_quality": results.tier3.coordination_centrality,  # centrality
            "tool_efficiency": results.tier3.tool_selection_accuracy,  # tool accuracy
        }

        # Validate all metrics are in valid range
        for metric_name, value in metrics.items():
            if not (0.0 <= value <= 1.0):
                logger.warning(f"Metric {metric_name} = {value:.3f} outside valid range [0.0, 1.0]")
                # Clamp to valid range
                metrics[metric_name] = max(0.0, min(1.0, value))

        logger.debug(f"Extracted metrics: {[(k, f'{v:.3f}') for k, v in metrics.items()]}")
        return metrics

    def calculate_composite_score(self, results: EvaluationResults) -> float:
        """Calculate weighted composite score from all evaluation tiers.

        Args:
            results: Container with tier1, tier2, tier3 evaluation results

        Returns:
            Composite score (0.0 to 1.0)

        Raises:
            ValueError: If required tier results are missing
        """
        metrics = self.extract_metric_values(results)

        # Apply weighted formula from configuration
        composite_score = sum(metrics[metric] * weight for metric, weight in self.weights.items())

        # Ensure score is in valid range
        composite_score = max(0.0, min(1.0, composite_score))

        logger.info(f"Composite score calculated: {composite_score:.3f}")
        contributions = [(m, f"{metrics[m] * self.weights[m]:.3f}") for m in self.weights.keys()]
        logger.debug(f"Metric contributions: {contributions}")

        return composite_score

    def map_to_recommendation(self, composite_score: float) -> str:
        """Map composite score to recommendation category.

        Args:
            composite_score: Composite score (0.0 to 1.0)

        Returns:
            Recommendation category: "accept", "weak_accept", "weak_reject", or "reject"
        """
        # Apply threshold mapping (descending order)
        if composite_score >= self.thresholds.get("accept", 0.8):
            return "accept"
        elif composite_score >= self.thresholds.get("weak_accept", 0.6):
            return "weak_accept"
        elif composite_score >= self.thresholds.get("weak_reject", 0.4):
            return "weak_reject"
        else:
            return "reject"

    def get_recommendation_weight(self, recommendation: str) -> float:
        """Get numerical weight for recommendation category.

        Args:
            recommendation: Recommendation category

        Returns:
            Numerical weight (-1.0 to 1.0)
        """
        return self.recommendation_weights.get(recommendation, 0.0)

    def _detect_single_agent_mode(self, trace_data: GraphTraceData) -> bool:
        """Detect if execution was single-agent (no multi-agent delegation).

        Single-agent mode is detected when:
        - coordination_events is empty (no delegation), OR
        - 0 or 1 unique agent IDs in tool_calls

        Args:
            trace_data: Graph trace data from agent execution

        Returns:
            True if single-agent mode, False if multi-agent coordination occurred
        """
        # Check coordination events first (most reliable signal)
        if trace_data.coordination_events:
            return False

        # Check unique agent IDs in tool_calls
        agent_ids = {call.get("agent_id") for call in trace_data.tool_calls if "agent_id" in call}
        unique_agent_count = len(agent_ids)

        # 0 or 1 unique agent = single-agent mode
        return unique_agent_count <= 1

    def evaluate_composite(self, results: EvaluationResults) -> CompositeResult:
        """Complete composite evaluation with score and recommendation.

        Args:
            results: Container with tier1, tier2, tier3 evaluation results

        Returns:
            CompositeResult with score, recommendation, and detailed metrics

        Raises:
            ValueError: If required tier results are missing
        """
        try:
            # Calculate composite score
            composite_score = self.calculate_composite_score(results)

            # Map to recommendation
            recommendation = self.map_to_recommendation(composite_score)
            recommendation_weight = self.get_recommendation_weight(recommendation)

            # Extract individual metrics for detailed analysis
            metrics = self.extract_metric_values(results)

            # Create result object
            # We know tiers are non-None since calculate_composite_score succeeded
            assert results.tier1 is not None
            assert results.tier2 is not None
            assert results.tier3 is not None

            # Get enabled tiers for metadata
            enabled_tiers = self.settings.get_enabled_tiers()

            # Reason: Store composite metric weights for transparency
            # These show how each metric contributes to final score
            composite_weights = self.weights.copy()

            result = CompositeResult(
                composite_score=composite_score,
                recommendation=recommendation,
                recommendation_weight=recommendation_weight,
                metric_scores=metrics,
                tier1_score=results.tier1.overall_score,
                tier2_score=results.tier2.overall_score,
                tier3_score=results.tier3.overall_score,
                evaluation_complete=results.is_complete(),
                weights_used=composite_weights,
                tiers_enabled=sorted(enabled_tiers),
            )

            logger.info(f"Composite evaluation complete: {composite_score:.3f} → {recommendation}")
            return result

        except Exception as e:
            logger.error(f"Composite evaluation failed: {e}")
            raise

    def get_scoring_summary(self) -> dict[str, Any]:
        """Get summary of scoring configuration for validation.

        Returns:
            Dictionary with configuration summary
        """
        return {
            "metrics_count": len(self.weights),
            "total_weight": sum(self.weights.values()),
            "weights": self.weights.copy(),
            "thresholds": self.thresholds.copy(),
            "recommendation_weights": self.recommendation_weights.copy(),
        }

    def _calculate_tool_score(self, tools_used: list[str]) -> float:
        """Calculate tool selection score based on usage count."""
        tool_count = len(tools_used)
        if tool_count == 0:
            return 0.3
        if tool_count > 5:
            return max(0.4, 0.8 - (tool_count - 5) * 0.1)
        return 0.8

    def _calculate_coherence_score(
        self, error_occurred: bool, output_length: int, execution_time: float
    ) -> float:
        """Calculate plan coherence score based on execution quality."""
        score = 0.7
        if error_occurred:
            score -= 0.4
        if output_length > 100:
            score += 0.1
        elif output_length < 20:
            score -= 0.2
        if execution_time > 30.0:
            score -= 0.2
        return max(0.0, min(1.0, score))

    def _calculate_coordination_score(self, delegation_count: int, output_length: int) -> float:
        """Calculate coordination score based on delegation and output quality."""
        score = 0.7
        if delegation_count > 0:
            if delegation_count <= 3:
                score += 0.2
            else:
                score -= (delegation_count - 3) * 0.1
        if output_length > 50:
            score += 0.1
        return max(0.0, min(1.0, score))

    def assess_agent_performance(
        self,
        execution_time: float,
        tools_used: list[str],
        delegation_count: int = 0,
        error_occurred: bool = False,
        output_length: int = 0,
    ) -> AgentMetrics:
        """Assess agent performance with simple rule-based metrics.

        Args:
            execution_time: Time taken for agent execution in seconds
            tools_used: List of tools used during execution
            delegation_count: Number of delegations made (for manager agents)
            error_occurred: Whether an error occurred during execution
            output_length: Length of output result in characters

        Returns:
            AgentMetrics with evaluated scores
        """
        tool_score = self._calculate_tool_score(tools_used)
        coherence_score = self._calculate_coherence_score(
            error_occurred, output_length, execution_time
        )
        coordination_score = self._calculate_coordination_score(delegation_count, output_length)

        agent_metrics = AgentMetrics(
            tool_selection_score=tool_score,
            plan_coherence_score=coherence_score,
            coordination_score=coordination_score,
        )

        logger.debug(
            f"Agent assessment: tool={tool_score:.3f}, coherence={coherence_score:.3f}, "
            f"coordination={coordination_score:.3f}"
        )
        return agent_metrics

    def _determine_excluded_metrics(
        self, single_agent_mode: bool, tier2_available: bool
    ) -> list[str]:
        """Determine which metrics to exclude based on execution mode.

        Args:
            single_agent_mode: Whether single-agent mode detected
            tier2_available: Whether Tier 2 results are available

        Returns:
            List of metric names to exclude from composite scoring
        """
        excluded_metrics: list[str] = []
        if single_agent_mode:
            excluded_metrics.append("coordination_quality")
            logger.info(
                "Single-agent mode detected - redistributing coordination_quality weight "
                "to remaining metrics"
            )

        if not tier2_available:
            excluded_metrics.append("planning_rationality")
            logger.warning(
                "Tier 2 (LLM-as-Judge) skipped - redistributing planning_rationality weight"
            )

        return excluded_metrics

    def _extract_tier1_metrics(
        self, tier1: Tier1Result, remaining_metrics: dict[str, float]
    ) -> dict[str, float]:
        """Extract Tier 1 metrics if they are not excluded."""
        metrics: dict[str, float] = {}
        if "time_taken" in remaining_metrics:
            metrics["time_taken"] = tier1.time_score
        if "task_success" in remaining_metrics:
            metrics["task_success"] = tier1.task_success
        if "output_similarity" in remaining_metrics:
            metrics["output_similarity"] = tier1.overall_score
        return metrics

    def _extract_tier3_metrics(
        self, tier3: Tier3Result, remaining_metrics: dict[str, float]
    ) -> dict[str, float]:
        """Extract Tier 3 metrics if they are not excluded."""
        metrics: dict[str, float] = {}
        if "coordination_quality" in remaining_metrics:
            metrics["coordination_quality"] = tier3.coordination_centrality
        if "tool_efficiency" in remaining_metrics:
            metrics["tool_efficiency"] = tier3.tool_selection_accuracy
        return metrics

    def _extract_metrics_with_exclusions(
        self, results: EvaluationResults, remaining_metrics: dict[str, float]
    ) -> dict[str, float]:
        """Extract metric values from tier results, excluding specified metrics.

        Args:
            results: Container with tier results
            remaining_metrics: Dictionary of metrics to include (not excluded)

        Returns:
            Dictionary mapping metric names to values
        """
        metrics: dict[str, float] = {}

        # Extract Tier 1 metrics
        if results.tier1:
            metrics.update(self._extract_tier1_metrics(results.tier1, remaining_metrics))

        # Extract Tier 2 metrics
        if results.tier2 and "planning_rationality" in remaining_metrics:
            metrics["planning_rationality"] = results.tier2.planning_rationality

        # Extract Tier 3 metrics
        if results.tier3:
            metrics.update(self._extract_tier3_metrics(results.tier3, remaining_metrics))

        return metrics

    def evaluate_composite_with_trace(
        self, results: EvaluationResults, trace_data: GraphTraceData
    ) -> CompositeResult:
        """Evaluate composite score with single-agent mode detection and weight redistribution.

        Detects single-agent runs from trace data and redistributes coordination_quality
        weight to remaining metrics. Also handles Tier 2 skip for compound redistribution.

        Args:
            results: Container with tier1, tier2, tier3 evaluation results
            trace_data: Graph trace data for single-agent detection

        Returns:
            CompositeResult with adjusted weights for single-agent mode
        """
        # Detect single-agent mode from trace data
        single_agent_mode = self._detect_single_agent_mode(trace_data)

        # Determine which metrics to exclude
        excluded_metrics = self._determine_excluded_metrics(
            single_agent_mode, tier2_available=results.tier2 is not None
        )

        # If no exclusions, use standard evaluation
        if not excluded_metrics:
            result = self.evaluate_composite(results)
            result.single_agent_mode = single_agent_mode
            return result

        # Build adjusted weights by redistributing to remaining metrics
        remaining_metrics = {k: v for k, v in self.weights.items() if k not in excluded_metrics}
        weight_per_remaining = (1.0 / len(remaining_metrics)) if remaining_metrics else 0.0
        adjusted_weights = {metric: weight_per_remaining for metric in remaining_metrics}

        # Extract metrics (only those not excluded)
        metrics = self._extract_metrics_with_exclusions(results, remaining_metrics)

        # Validate all required metrics are present
        missing_metrics = set(remaining_metrics.keys()) - set(metrics.keys())
        if missing_metrics:
            raise ValueError(f"Missing required metrics after exclusion: {missing_metrics}")

        # Calculate composite score with adjusted weights
        composite_score = sum(
            metrics[metric] * weight for metric, weight in adjusted_weights.items()
        )
        composite_score = max(0.0, min(1.0, composite_score))

        recommendation = self.map_to_recommendation(composite_score)
        recommendation_weight = self.get_recommendation_weight(recommendation)

        logger.info(
            f"Composite score with redistributed weights: {composite_score:.3f} "
            f"(excluded: {excluded_metrics})"
        )

        return CompositeResult(
            composite_score=composite_score,
            recommendation=recommendation,
            recommendation_weight=recommendation_weight,
            metric_scores=metrics,
            tier1_score=results.tier1.overall_score if results.tier1 else 0.0,
            tier2_score=results.tier2.overall_score if results.tier2 else None,
            tier3_score=results.tier3.overall_score if results.tier3 else 0.0,
            evaluation_complete=results.is_complete(),
            single_agent_mode=single_agent_mode,
            weights_used=adjusted_weights,
            tiers_enabled=sorted(self.settings.get_enabled_tiers()),
        )

    def evaluate_composite_with_optional_tier2(self, results: EvaluationResults) -> CompositeResult:
        """Evaluate composite score with optional Tier 2 (handles missing Tier 2).

        When Tier 2 is None, redistributes weights to Tier 1 and Tier 3.

        Args:
            results: Container with tier1, tier3, and optional tier2 results

        Returns:
            CompositeResult with adjusted weights when Tier 2 is missing
        """
        if results.tier2 is None:
            logger.warning(
                "Tier 2 (LLM-as-Judge) skipped - no valid provider available. "
                "Redistributing weights to Tier 1 + Tier 3."
            )
            # Redistribute Tier 2 metrics (planning_rationality: 0.167) to other metrics
            # Split evenly across remaining 5 metrics
            adjusted_weights = {
                "time_taken": 0.2,  # 0.167 + 0.033
                "task_success": 0.2,  # 0.167 + 0.033
                "coordination_quality": 0.2,  # 0.167 + 0.033
                "tool_efficiency": 0.2,  # 0.167 + 0.033
                "output_similarity": 0.2,  # 0.167 + 0.033
            }

            # Extract metrics from Tier 1 and Tier 3 only
            if not results.tier1 or not results.tier3:
                raise ValueError("Tier 1 and Tier 3 are required when Tier 2 is missing")

            metrics = {
                "time_taken": results.tier1.time_score,
                "task_success": results.tier1.task_success,
                "output_similarity": results.tier1.overall_score,
                "coordination_quality": results.tier3.coordination_centrality,
                "tool_efficiency": results.tier3.tool_selection_accuracy,
            }

            # Calculate composite score with adjusted weights
            composite_score = sum(
                metrics[metric] * weight for metric, weight in adjusted_weights.items()
            )
            composite_score = max(0.0, min(1.0, composite_score))

            recommendation = self.map_to_recommendation(composite_score)
            recommendation_weight = self.get_recommendation_weight(recommendation)

            return CompositeResult(
                composite_score=composite_score,
                recommendation=recommendation,
                recommendation_weight=recommendation_weight,
                metric_scores=metrics,
                tier1_score=results.tier1.overall_score,
                tier2_score=None,  # Tier 2 skipped
                tier3_score=results.tier3.overall_score,
                evaluation_complete=False,  # Not complete without Tier 2
                weights_used=adjusted_weights,
                tiers_enabled=sorted(self.settings.get_enabled_tiers()),
            )
        else:
            # All tiers available, use standard evaluation
            return self.evaluate_composite(results)
