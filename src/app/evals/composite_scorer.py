"""
Composite scoring system for three-tiered evaluation framework.

Integrates Traditional Metrics (Tier 1), LLM-as-Judge (Tier 2), and
Graph Analysis (Tier 3) into unified scoring system with recommendation mapping.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from app.data_models.evaluation_models import (
    CompositeResult,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.utils.log import logger

if TYPE_CHECKING:
    from app.evals.settings import JudgeSettings


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

    Implements the six-metric weighted formula from config_eval.json:
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
            from app.evals.settings import JudgeSettings

            settings = JudgeSettings()

        # Use JudgeSettings
        self.settings = settings
        self.config_path = None
        self.config = None

        # Hardcoded defaults from config_eval.json (will be moved to JudgeSettings later)
        # Reason: Keep settings minimal for now, hardcode composite config
        self.weights = {
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167,
            "tool_efficiency": 0.167,
            "planning_rationality": 0.167,
            "output_similarity": 0.167,
        }
        self.thresholds = {
            "accept": 0.8,
            "weak_accept": 0.6,
            "weak_reject": 0.4,
            "reject": 0.0,
        }
        self.recommendation_weights = {
            "accept": 1.0,
            "weak_accept": 0.7,
            "weak_reject": -0.7,
            "reject": -1.0,
        }
        self.composite_config = {
            "metrics_and_weights": self.weights,
            "recommendation_thresholds": self.thresholds,
            "recommendation_weights": self.recommendation_weights,
        }

        logger.info(
            f"CompositeScorer initialized with JudgeSettings ({len(self.weights)} metrics)"
        )

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
            "time_taken": self._normalize_time_score(
                results.tier1.time_score
            ),  # normalized execution time
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

    def _normalize_time_score(self, time_score: float) -> float:
        """Normalize time score using 1/(1+log(time)) formula.

        Args:
            time_score: Raw time score from Tier 1

        Returns:
            Normalized time score (0.0 to 1.0, higher is better)
        """
        import math

        if time_score <= 0:
            return 1.0  # Perfect score for zero time

        # Apply logarithmic normalization - better performance = higher score
        normalized = 1.0 / (1.0 + math.log(1.0 + time_score))
        return max(0.0, min(1.0, normalized))

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

            result = CompositeResult(
                composite_score=composite_score,
                recommendation=recommendation,
                recommendation_weight=recommendation_weight,
                metric_scores=metrics,
                tier1_score=results.tier1.overall_score,
                tier2_score=results.tier2.overall_score,
                tier3_score=results.tier3.overall_score,
                evaluation_complete=results.is_complete(),
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
        # Tool Selection Score (0.0-1.0)
        tool_score = 0.8  # Default good score
        if len(tools_used) == 0:
            tool_score = 0.3  # No tools used
        elif len(tools_used) > 5:
            tool_score = max(0.4, 0.8 - (len(tools_used) - 5) * 0.1)  # Over-tooling penalty

        # Plan Coherence Score (0.0-1.0)
        coherence_score = 0.7  # Default neutral
        if error_occurred:
            coherence_score -= 0.4  # Major penalty for errors
        if output_length > 100:
            coherence_score += 0.1  # Reward substantive output
        elif output_length < 20:
            coherence_score -= 0.2  # Penalize minimal output
        if execution_time > 30.0:  # Very long execution
            coherence_score -= 0.2  # Penalize slow execution

        # Coordination Score (0.0-1.0)
        coordination_score = 0.7  # Default neutral
        if delegation_count > 0:  # Agent delegated tasks
            if delegation_count <= 3:
                coordination_score += 0.2  # Reward appropriate delegation
            else:
                coordination_score -= (delegation_count - 3) * 0.1  # Over-delegation penalty
        if output_length > 50:  # Substantive response
            coordination_score += 0.1

        # Ensure all scores are within bounds
        tool_score = max(0.0, min(1.0, tool_score))
        coherence_score = max(0.0, min(1.0, coherence_score))
        coordination_score = max(0.0, min(1.0, coordination_score))

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
