"""
LLM-as-Judge implementation for Tier 2 evaluation.

Provides quality assessment using existing PydanticAI infrastructure
with cost optimization and fallback mechanisms.
"""

import asyncio
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent

from app.data_models.evaluation_models import Tier2Result
from app.evals.traditional_metrics import TraditionalMetricsEngine
from app.utils.log import logger


class TechnicalAccuracyAssessment(BaseModel):
    """Structured LLM assessment of technical accuracy."""

    factual_correctness: float  # 1-5 scale
    methodology_understanding: float  # 1-5 scale
    domain_knowledge: float  # 1-5 scale
    explanation: str


class ConstructivenessAssessment(BaseModel):
    """Structured LLM assessment of review constructiveness."""

    actionable_feedback: float  # 1-5 scale
    balanced_critique: float  # 1-5 scale
    improvement_guidance: float  # 1-5 scale
    explanation: str


class PlanningRationalityAssessment(BaseModel):
    """Structured LLM assessment of planning quality."""

    logical_flow: float  # 1-5 scale
    decision_quality: float  # 1-5 scale
    resource_efficiency: float  # 1-5 scale
    explanation: str


class LLMJudgeEngine:
    """LLM-as-Judge evaluation engine with fallback mechanisms.

    Provides quality assessment through structured prompts and cost-optimized
    model usage with graceful degradation to traditional metrics on failures.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize LLM judge with configuration.

        Args:
            config: Configuration dictionary from config_eval.json
        """
        self.config = config
        self.fallback_engine = TraditionalMetricsEngine()

        # Extract LLM judge configuration
        llm_config = config.get("tier2_llm_judge", {})

        # Cost-optimized model selection
        self.default_model = llm_config.get("model", "gpt-4o-mini")
        self.max_retries = llm_config.get("max_retries", 2)
        self.timeout = llm_config.get("timeout_seconds", 30.0)
        self.paper_excerpt_length = llm_config.get("paper_excerpt_length", 2000)
        self.cost_budget = llm_config.get("cost_budget_usd", 0.05)

    async def assess_technical_accuracy(self, paper: str, review: str) -> float:
        """Assess technical accuracy of review against paper.

        Args:
            paper: Paper content (truncated for API efficiency)
            review: Agent-generated review

        Returns:
            Normalized technical accuracy score (0.0-1.0)
        """
        try:
            # Truncate paper content for cost efficiency
            paper_excerpt = (
                paper[: self.paper_excerpt_length]
                if len(paper) > self.paper_excerpt_length
                else paper
            )

            prompt = f"""Evaluate the technical accuracy of this academic review (1-5 scale):
            
Paper Excerpt: {paper_excerpt}

Review: {review}

Rate each aspect (1=poor, 5=excellent):
1. Factual Correctness: Are claims supported by the paper?
2. Methodology Understanding: Does reviewer grasp the approach?
3. Domain Knowledge: Appropriate technical terminology?

Provide scores and brief explanation."""

            agent = Agent(self.default_model)
            result = await asyncio.wait_for(
                agent.run(prompt, output_type=TechnicalAccuracyAssessment),
                timeout=self.timeout,
            )

            # Calculate weighted score and normalize to 0-1
            weighted_score = (
                result.factual_correctness * 0.5
                + result.methodology_understanding * 0.3
                + result.domain_knowledge * 0.2
            ) / 5.0

            return min(1.0, max(0.0, weighted_score))

        except Exception as e:
            logger.warning(f"Technical accuracy assessment failed: {e}")
            # Fallback to semantic similarity
            return self.fallback_engine.compute_semantic_similarity(paper, review)

    async def assess_constructiveness(self, review: str) -> float:
        """Assess constructiveness and helpfulness of review.

        Args:
            review: Agent-generated review text

        Returns:
            Normalized constructiveness score (0.0-1.0)
        """
        try:
            prompt = f"""Evaluate the constructiveness of this academic review (1-5 scale):
            
Review: {review}

Rate each aspect (1=poor, 5=excellent):
1. Actionable Feedback: Specific, implementable suggestions?
2. Balanced Critique: Both strengths and weaknesses noted?
3. Improvement Guidance: Clear direction for authors?

Provide scores and brief explanation."""

            agent = Agent(self.default_model)

            result = await asyncio.wait_for(
                agent.run(prompt, output_type=ConstructivenessAssessment),
                timeout=self.timeout,
            )

            # Equal weighting for constructiveness aspects
            average_score = (
                result.actionable_feedback
                + result.balanced_critique
                + result.improvement_guidance
            ) / 15.0  # Normalize to 0-1

            return min(1.0, max(0.0, average_score))

        except Exception as e:
            logger.warning(f"Constructiveness assessment failed: {e}")
            # Simple fallback: check for key constructive phrases
            return self._fallback_constructiveness_check(review)

    async def assess_planning_rationality(
        self, execution_trace: dict[str, Any]
    ) -> float:
        """Assess quality of agent planning and decision-making.

        Args:
            execution_trace: Agent execution trace data

        Returns:
            Normalized planning rationality score (0.0-1.0)
        """
        try:
            # Extract planning summary from trace
            planning_summary = self._extract_planning_decisions(execution_trace)

            prompt = f"""Evaluate the planning rationality of this agent execution (1-5 scale):
            
Execution Summary: {planning_summary}

Rate each aspect (1=poor, 5=excellent):
1. Logical Flow: Coherent step progression?
2. Decision Quality: Appropriate choices made?  
3. Resource Efficiency: Optimal tool/agent usage?

Provide scores and brief explanation."""

            agent = Agent(self.default_model)

            result = await asyncio.wait_for(
                agent.run(prompt, output_type=PlanningRationalityAssessment),
                timeout=self.timeout,
            )

            # Weight decision quality most heavily
            weighted_score = (
                result.logical_flow * 0.3
                + result.decision_quality * 0.5
                + result.resource_efficiency * 0.2
            ) / 5.0

            return min(1.0, max(0.0, weighted_score))

        except Exception as e:
            logger.warning(f"Planning rationality assessment failed: {e}")
            # Simple fallback based on trace structure
            return self._fallback_planning_check(execution_trace)

    async def evaluate_llm_judge(
        self, paper: str, review: str, execution_trace: dict[str, Any]
    ) -> Tier2Result:
        """Complete LLM-as-Judge evaluation with error handling.

        Args:
            paper: Full paper content
            review: Agent-generated review
            execution_trace: Agent execution data

        Returns:
            Tier2Result with all LLM judge assessments
        """
        fallback_used = False
        api_cost = 0.0

        try:
            # Run assessments concurrently for efficiency
            technical_task = self.assess_technical_accuracy(paper, review)
            constructiveness_task = self.assess_constructiveness(review)
            planning_task = self.assess_planning_rationality(execution_trace)

            (
                technical_score,
                constructiveness_score,
                planning_score,
            ) = await asyncio.gather(
                technical_task,
                constructiveness_task,
                planning_task,
                return_exceptions=True,
            )

            # Handle individual assessment failures
            if isinstance(technical_score, Exception):
                logger.warning(f"Technical assessment failed: {technical_score}")
                technical_score = self.fallback_engine.compute_semantic_similarity(
                    paper, review
                )
                fallback_used = True

            if isinstance(constructiveness_score, Exception):
                logger.warning(
                    f"Constructiveness assessment failed: {constructiveness_score}"
                )
                constructiveness_score = self._fallback_constructiveness_check(review)
                fallback_used = True

            if isinstance(planning_score, Exception):
                logger.warning(f"Planning assessment failed: {planning_score}")
                planning_score = self._fallback_planning_check(execution_trace)
                fallback_used = True

            # Estimate API cost (approximate for gpt-4o-mini)
            total_tokens = len(paper) / 4 + len(review) / 4 + 500  # Rough estimate
            api_cost = (total_tokens / 1000) * 0.0001  # $0.0001 per 1K tokens

            # Calculate overall LLM judge score
            weights = self.config.get("tier2_llm_judge", {}).get(
                "weights",
                {
                    "technical_accuracy": 0.4,
                    "constructiveness": 0.3,
                    "planning_rationality": 0.3,
                },
            )

            overall_score = (
                technical_score * weights.get("technical_accuracy", 0.4)
                + constructiveness_score * weights.get("constructiveness", 0.3)
                + planning_score * weights.get("planning_rationality", 0.3)
            )

            return Tier2Result(
                technical_accuracy=technical_score,
                constructiveness=constructiveness_score,
                clarity=constructiveness_score,  # Use constructiveness as proxy
                planning_rationality=planning_score,
                overall_score=overall_score,
                model_used=self.default_model,
                api_cost=api_cost,
                fallback_used=fallback_used,
            )

        except Exception as e:
            logger.error(f"Complete LLM judge evaluation failed: {e}")
            # Full fallback to traditional metrics
            return self._complete_fallback(paper, review, execution_trace)

    def _extract_planning_decisions(self, execution_trace: dict[str, Any]) -> str:
        """Extract key planning decisions from execution trace.

        Args:
            execution_trace: Agent execution trace data

        Returns:
            String summary of planning decisions
        """
        try:
            decisions = execution_trace.get("agent_interactions", [])
            tool_calls = execution_trace.get("tool_calls", [])

            summary = f"Agents involved: {len(decisions)} interactions, "
            summary += f"Tools used: {len(tool_calls)} calls"

            # Extract key decision points
            if decisions:
                decision_types = [
                    d.get("type", "unknown") for d in decisions[:5]
                ]  # First 5
                summary += f", Decision types: {', '.join(set(decision_types))}"

            return summary[:500]  # Limit length for API efficiency

        except Exception:
            return "Limited trace data available"

    def _fallback_constructiveness_check(self, review: str) -> float:
        """Simple fallback for constructiveness assessment.

        Args:
            review: Review text to analyze

        Returns:
            Heuristic constructiveness score (0.0-1.0)
        """
        constructive_phrases = [
            "suggest",
            "recommend",
            "could improve",
            "might consider",
            "strength",
            "weakness",
            "clear",
            "unclear",
            "future work",
            "however",
            "although",
            "while",
            "despite",
            "potential",
        ]

        review_lower = review.lower()
        matches = sum(1 for phrase in constructive_phrases if phrase in review_lower)

        return min(1.0, matches / len(constructive_phrases))

    def _fallback_planning_check(self, execution_trace: dict[str, Any]) -> float:
        """Simple fallback for planning rationality.

        Args:
            execution_trace: Agent execution trace data

        Returns:
            Heuristic planning score (0.0-1.0)
        """
        try:
            interactions = len(execution_trace.get("agent_interactions", []))
            tool_calls = len(execution_trace.get("tool_calls", []))

            # Simple heuristic: moderate activity indicates good planning
            # Too few = insufficient planning, too many = inefficient
            total_activity = interactions + tool_calls

            if total_activity <= 2:
                activity_score = total_activity / 2.0  # Scale up low activity
            elif total_activity <= 10:
                activity_score = 1.0  # Optimal range
            else:
                activity_score = max(
                    0.5, 1.0 - (total_activity - 10) * 0.05
                )  # Diminishing returns

            return min(1.0, max(0.0, activity_score))

        except Exception:
            return 0.5  # Neutral score when trace unavailable

    def _complete_fallback(
        self, paper: str, review: str, execution_trace: dict[str, Any]
    ) -> Tier2Result:
        """Complete fallback when all LLM assessments fail.

        Args:
            paper: Paper content
            review: Generated review
            execution_trace: Agent execution data

        Returns:
            Tier2Result using fallback mechanisms only
        """
        # Use traditional metrics as fallback
        semantic_score = self.fallback_engine.compute_semantic_similarity(paper, review)
        constructiveness_score = self._fallback_constructiveness_check(review)
        planning_score = self._fallback_planning_check(execution_trace)

        overall_score = (semantic_score + constructiveness_score + planning_score) / 3.0

        return Tier2Result(
            technical_accuracy=semantic_score,
            constructiveness=constructiveness_score,
            clarity=constructiveness_score,
            planning_rationality=planning_score,
            overall_score=overall_score,
            model_used="fallback_traditional",
            api_cost=0.0,
            fallback_used=True,
        )


async def evaluate_single_llm_judge(
    paper: str,
    review: str,
    execution_trace: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> Tier2Result:
    """Convenience function for single LLM judge evaluation.

    Args:
        paper: Paper content
        review: Generated review text
        execution_trace: Optional execution trace data
        config: Optional configuration override

    Returns:
        Tier2Result with LLM judge assessments

    Example:
        >>> result = await evaluate_single_llm_judge(
        ...     paper="This paper presents...",
        ...     review="The work demonstrates...",
        ...     execution_trace=trace_data,
        ... )
        >>> print(f"Overall score: {result.overall_score:.3f}")
    """
    config = config or {}
    execution_trace = execution_trace or {}

    engine = LLMJudgeEngine(config)
    return await engine.evaluate_llm_judge(paper, review, execution_trace)
