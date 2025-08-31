"""
LLM evaluation management and orchestration.

This module provides managers for orchestrating LLM-based evaluations,
handling provider selection, fallback mechanisms, and cost optimization
for evaluation tasks.
"""

import asyncio
from typing import Any

from pydantic_ai import Agent

from app.agents.agent_factories import create_evaluation_agent
from app.data_models.evaluation_models import (
    ConstructivenessAssessment,
    PlanningRationalityAssessment,
    TechnicalAccuracyAssessment,
    Tier2Result,
)
from app.evals.traditional_metrics import TraditionalMetricsEngine
from app.utils.log import logger


class LLMJudgeEngine:
    """Manager for LLM-based evaluation with provider flexibility and fallbacks."""

    def __init__(self, config: dict[str, Any]):
        """Initialize evaluation LLM manager with configuration."""
        self.config = config
        self.fallback_engine = TraditionalMetricsEngine()

        # Extract LLM configuration
        llm_config = config.get("tier2_llm_judge", {})

        # Provider and model settings
        self.provider = llm_config.get("provider", "openai")
        self.model = llm_config.get("model", "gpt-4o-mini")
        self.fallback_provider = llm_config.get("fallback_provider", "github")
        self.fallback_model = llm_config.get("fallback_model", "gpt-4o-mini")

        # Performance settings
        self.timeout = llm_config.get("timeout_seconds", 30.0)
        self.max_retries = llm_config.get("max_retries", 2)
        self.paper_excerpt_length = llm_config.get("paper_excerpt_length", 2000)
        self.cost_budget = llm_config.get("cost_budget_usd", 0.05)

        # Evaluation weights
        self.weights = llm_config.get(
            "weights",
            {
                "technical_accuracy": 0.4,
                "constructiveness": 0.3,
                "planning_rationality": 0.3,
            },
        )

    async def create_judge_agent(
        self, assessment_type: str, use_fallback: bool = False
    ) -> Agent:
        """
        Create an LLM judge agent for specific assessment type.

        Args:
            assessment_type: Type of assessment ("technical_accuracy", etc.)
            use_fallback: Whether to use fallback provider

        Returns:
            Configured Agent for evaluation
        """
        if use_fallback:
            provider = self.fallback_provider
            model = self.fallback_model
            logger.info(f"Using fallback provider: {provider}/{model}")
        else:
            provider = self.provider
            model = self.model

        return create_evaluation_agent(
            provider=provider, model_name=model, assessment_type=assessment_type
        )

    async def assess_technical_accuracy(self, paper: str, review: str) -> float:
        """Assess technical accuracy of review against paper."""
        try:
            # Truncate paper content for cost efficiency
            paper_excerpt = (
                paper[: self.paper_excerpt_length]
                if len(paper) > self.paper_excerpt_length
                else paper
            )

            prompt = f"""Evaluate technical accuracy of this review (1-5 scale):
            
Paper Excerpt: {paper_excerpt}

Review: {review}

Rate each aspect (1=poor, 5=excellent):
1. Factual Correctness: Are claims supported by the paper?
2. Methodology Understanding: Does reviewer grasp the approach?
3. Domain Knowledge: Appropriate technical terminology?

Provide scores and brief explanation."""

            agent = await self.create_judge_agent("technical_accuracy")
            result = await asyncio.wait_for(
                agent.run(prompt, output_type=TechnicalAccuracyAssessment),
                timeout=self.timeout,
            )

            # Calculate weighted score and normalize to 0-1
            weighted_score = (
                result.output.factual_correctness * 0.5
                + result.output.methodology_understanding * 0.3
                + result.output.domain_knowledge * 0.2
            ) / 5.0

            return min(1.0, max(0.0, weighted_score))

        except Exception as e:
            logger.warning(f"Technical accuracy assessment failed: {e}")
            # Fallback to semantic similarity
            return self.fallback_engine.compute_semantic_similarity(paper, review)

    async def assess_constructiveness(self, review: str) -> float:
        """Assess constructiveness and helpfulness of review."""
        try:
            prompt = f"""Evaluate constructiveness of this review (1-5 scale):
            
Review: {review}

Rate each aspect (1=poor, 5=excellent):
1. Actionable Feedback: Specific, implementable suggestions?
2. Balanced Critique: Both strengths and weaknesses noted?
3. Improvement Guidance: Clear direction for authors?

Provide scores and brief explanation."""

            agent = await self.create_judge_agent("constructiveness")
            result = await asyncio.wait_for(
                agent.run(prompt, output_type=ConstructivenessAssessment),
                timeout=self.timeout,
            )

            # Equal weighting for constructiveness aspects
            average_score = (
                result.output.actionable_feedback
                + result.output.balanced_critique
                + result.output.improvement_guidance
            ) / 15.0  # Normalize to 0-1

            return min(1.0, max(0.0, average_score))

        except Exception as e:
            logger.warning(f"Constructiveness assessment failed: {e}")
            # Simple fallback: check for key constructive phrases
            return self._fallback_constructiveness_check(review)

    async def assess_planning_rationality(
        self, execution_trace: dict[str, Any]
    ) -> float:
        """Assess quality of agent planning and decision-making."""
        try:
            # Extract planning summary from trace
            planning_summary = self._extract_planning_decisions(execution_trace)

            prompt = f"""Evaluate planning rationality of this execution (1-5 scale):
            
Execution Summary: {planning_summary}

Rate each aspect (1=poor, 5=excellent):
1. Logical Flow: Coherent step progression?
2. Decision Quality: Appropriate choices made?
3. Resource Efficiency: Optimal tool/agent usage?

Provide scores and brief explanation."""

            agent = await self.create_judge_agent("planning_rationality")
            result = await asyncio.wait_for(
                agent.run(prompt, output_type=PlanningRationalityAssessment),
                timeout=self.timeout,
            )

            # Weight decision quality most heavily
            weighted_score = (
                result.output.logical_flow * 0.3
                + result.output.decision_quality * 0.5
                + result.output.resource_efficiency * 0.2
            ) / 5.0

            return min(1.0, max(0.0, weighted_score))

        except Exception as e:
            logger.warning(f"Planning rationality assessment failed: {e}")
            # Simple fallback based on trace structure
            return self._fallback_planning_check(execution_trace)

    async def evaluate_comprehensive(
        self, paper: str, review: str, execution_trace: dict[str, Any]
    ) -> Tier2Result:
        """Run comprehensive LLM-based evaluation."""
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

            # Handle individual assessment failures with proper type casting
            if isinstance(technical_score, Exception):
                logger.warning(f"Technical assessment failed: {technical_score}")
                technical_score = float(
                    self.fallback_engine.compute_semantic_similarity(paper, review)
                )
                fallback_used = True

            if isinstance(constructiveness_score, Exception):
                logger.warning(
                    f"Constructiveness assessment failed: {constructiveness_score}"
                )
                constructiveness_score = float(
                    self._fallback_constructiveness_check(review)
                )
                fallback_used = True

            if isinstance(planning_score, Exception):
                logger.warning(f"Planning assessment failed: {planning_score}")
                planning_score = float(self._fallback_planning_check(execution_trace))
                fallback_used = True

            # Estimate API cost (approximate)
            total_tokens = len(paper) / 4 + len(review) / 4 + 500  # Rough estimate
            api_cost = (total_tokens / 1000) * 0.0001  # $0.0001 per 1K tokens

            # Calculate overall LLM judge score
            overall_score = (
                technical_score * self.weights.get("technical_accuracy", 0.4)
                + constructiveness_score * self.weights.get("constructiveness", 0.3)
                + planning_score * self.weights.get("planning_rationality", 0.3)
            )

            return Tier2Result(
                technical_accuracy=technical_score,
                constructiveness=constructiveness_score,
                clarity=constructiveness_score,  # Use constructiveness as proxy
                planning_rationality=planning_score,
                overall_score=overall_score,
                model_used=f"{self.provider}/{self.model}",
                api_cost=api_cost,
                fallback_used=fallback_used,
            )

        except Exception as e:
            logger.error(f"Complete LLM judge evaluation failed: {e}")
            # Full fallback to traditional metrics
            return self._complete_fallback(paper, review, execution_trace)

    def _extract_planning_decisions(self, execution_trace: dict[str, Any]) -> str:
        """Extract key planning decisions from execution trace."""
        try:
            decisions = execution_trace.get("agent_interactions", [])
            tool_calls = execution_trace.get("tool_calls", [])

            summary = f"Agents involved: {len(decisions)} interactions, "
            summary += f"Tools used: {len(tool_calls)} calls"

            # Extract key decision points
            if decisions:
                decision_types = [d.get("type", "unknown") for d in decisions[:5]]
                summary += f", Decision types: {', '.join(set(decision_types))}"

            return summary[:500]  # Limit length for API efficiency

        except Exception:
            return "Limited trace data available"

    def _fallback_constructiveness_check(self, review: str) -> float:
        """Simple fallback for constructiveness assessment."""
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
        """Simple fallback for planning rationality."""
        try:
            interactions = len(execution_trace.get("agent_interactions", []))
            tool_calls = len(execution_trace.get("tool_calls", []))

            # Simple heuristic: moderate activity indicates good planning
            total_activity = interactions + tool_calls

            if total_activity <= 2:
                activity_score = total_activity / 2.0
            elif total_activity <= 10:
                activity_score = 1.0  # Optimal range
            else:
                activity_score = max(0.5, 1.0 - (total_activity - 10) * 0.05)

            return min(1.0, max(0.0, activity_score))

        except Exception:
            return 0.5  # Neutral score when trace unavailable

    def _complete_fallback(
        self, paper: str, review: str, execution_trace: dict[str, Any]
    ) -> Tier2Result:
        """Complete fallback when all LLM assessments fail."""
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
