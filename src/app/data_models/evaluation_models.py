"""
Data models for three-tiered evaluation system.

This module provides Pydantic models for the comprehensive evaluation framework
that assesses multi-agent systems on PeerRead scientific paper review generation.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.data_models.peerread_models import PeerReadReview


class TechnicalAccuracyAssessment(BaseModel):
    """LLM assessment of technical accuracy."""

    factual_correctness: float = Field(ge=1.0, le=5.0, description="Factual correctness score")
    methodology_understanding: float = Field(
        ge=1.0, le=5.0, description="Methodology understanding score"
    )
    domain_knowledge: float = Field(ge=1.0, le=5.0, description="Domain knowledge score")
    explanation: str = Field(description="Explanation of the assessment")


class ConstructivenessAssessment(BaseModel):
    """LLM assessment of constructiveness."""

    actionable_feedback: float = Field(ge=1.0, le=5.0, description="Actionable feedback score")
    balanced_critique: float = Field(ge=1.0, le=5.0, description="Balanced critique score")
    improvement_guidance: float = Field(ge=1.0, le=5.0, description="Improvement guidance score")
    explanation: str = Field(description="Explanation of the assessment")


class PlanningRationalityAssessment(BaseModel):
    """LLM assessment of planning rationality."""

    logical_flow: float = Field(ge=1.0, le=5.0, description="Logical flow score")
    decision_quality: float = Field(ge=1.0, le=5.0, description="Decision quality score")
    resource_efficiency: float = Field(ge=1.0, le=5.0, description="Resource efficiency score")
    explanation: str = Field(description="Explanation of the assessment")


class Tier1Result(BaseModel):
    """Traditional metrics evaluation result.

    Contains text similarity metrics, execution performance, and task success
    indicators using lightweight computational approaches.
    """

    cosine_score: float = Field(ge=0.0, le=1.0, description="TF-IDF cosine similarity")
    jaccard_score: float = Field(ge=0.0, le=1.0, description="Word-level Jaccard similarity")
    semantic_score: float = Field(ge=0.0, le=1.0, description="BERT-based semantic similarity")
    execution_time: float = Field(ge=0.0, description="Raw execution time in seconds")
    time_score: float = Field(ge=0.0, le=1.0, description="Normalized time score")
    task_success: float = Field(description="Binary success indicator (0.0 or 1.0)")
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted traditional metrics score")


class Tier2Result(BaseModel):
    """LLM-as-Judge evaluation result.

    Contains quality assessments from large language model evaluation including
    technical accuracy, constructiveness, and planning rationality.
    """

    technical_accuracy: float = Field(ge=0.0, le=1.0, description="Technical accuracy score")
    constructiveness: float = Field(ge=0.0, le=1.0, description="Constructiveness score")
    planning_rationality: float = Field(ge=0.0, le=1.0, description="Planning quality score")
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted LLM judge score")
    model_used: str = Field(description="LLM model used for evaluation")
    api_cost: float | None = Field(
        default=None, description="Estimated API cost in USD; None when cost is unavailable"
    )
    fallback_used: bool = Field(default=False, description="Whether fallback was used")


class Tier3Result(BaseModel):
    """Graph-based analysis result.

    Contains metrics derived from analyzing agent coordination patterns,
    tool usage efficiency using NetworkX.
    """

    path_convergence: float = Field(ge=0.0, le=1.0, description="Tool usage efficiency")
    tool_selection_accuracy: float = Field(ge=0.0, le=1.0, description="Tool choice accuracy")
    coordination_centrality: float = Field(ge=0.0, le=1.0, description="Coordination quality")
    task_distribution_balance: float = Field(ge=0.0, le=1.0, description="Load balancing")
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted graph analysis score")
    graph_complexity: int = Field(description="Number of nodes in interaction graph")


class CompositeEvaluationResult(BaseModel):
    """Complete three-tier evaluation result.

    Aggregates all evaluation tiers into a single comprehensive assessment
    with composite scoring and recommendation generation.
    """

    paper_id: str = Field(description="Evaluated paper identifier")
    agent_review: str = Field(description="Generated review text")

    tier1_results: Tier1Result
    tier2_results: Tier2Result | None = None
    tier3_results: Tier3Result | None = None

    composite_score: float = Field(ge=0.0, le=1.0, description="Final weighted score")
    recommendation: str = Field(description="accept/weak_accept/weak_reject/reject")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in evaluation")

    # Performance metrics
    tier1_duration: float = Field(description="Tier 1 execution time")
    tier2_duration: float | None = None
    tier3_duration: float | None = None
    total_duration: float = Field(description="Total evaluation time")

    # Metadata
    timestamp: str = Field(description="ISO 8601 evaluation timestamp")
    config_version: str = Field(description="Configuration version used")


class CompositeResult(BaseModel):
    """Result of composite scoring across all three evaluation tiers.

    Integrates Traditional Metrics, LLM-as-Judge, and Graph Analysis
    into unified scoring system with recommendation mapping.
    """

    composite_score: float = Field(
        ge=0.0, le=1.0, description="Weighted composite score across all tiers"
    )
    recommendation: str = Field(
        description="Recommendation category: accept, weak_accept, weak_reject, reject"
    )
    recommendation_weight: float = Field(
        ge=-1.0, le=1.0, description="Numerical weight for recommendation (-1.0 to 1.0)"
    )

    # Individual metric contributions
    metric_scores: dict[str, float] = Field(
        description="Individual metric values used in composite calculation"
    )

    # Tier-level scores
    tier1_score: float = Field(ge=0.0, le=1.0, description="Traditional metrics overall score")
    tier2_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="LLM-as-Judge overall score (None if skipped)"
    )
    tier3_score: float = Field(ge=0.0, le=1.0, description="Graph analysis overall score")

    # Evaluation metadata
    evaluation_complete: bool = Field(description="Whether all required tiers completed")
    single_agent_mode: bool = Field(
        default=False,
        description="Whether single-agent mode weight redistribution was applied",
    )
    timestamp: str = Field(description="ISO 8601 evaluation timestamp", default="")
    config_version: str = Field(description="Configuration version used", default="1.0.0")
    weights_used: dict[str, float] | None = Field(
        description="Tier weights used in composite calculation", default=None
    )
    tiers_enabled: list[int] | None = Field(
        description="List of enabled tier numbers", default=None
    )

    agent_assessment_scores: dict[str, float] | None = Field(
        description="Optional agent-level assessment scores", default=None
    )


class GraphTraceData(BaseModel):
    """Trace data structure for graph-based analysis.

    Captures execution traces from agent interactions, tool usage,
    and coordination patterns for NetworkX graph construction.
    """

    execution_id: str = Field(description="Unique execution identifier")
    agent_interactions: list[dict[str, Any]] = Field(
        description="Agent-to-agent communications", default_factory=list
    )
    tool_calls: list[dict[str, Any]] = Field(
        description="Tool usage sequence", default_factory=list
    )
    timing_data: dict[str, Any] = Field(description="Execution timestamps", default_factory=dict)
    coordination_events: list[dict[str, Any]] = Field(
        description="Manager delegation patterns", default_factory=list
    )

    @classmethod
    def from_trace_dict(
        cls, trace: dict[str, Any] | None, fallback_id: str = "minimal"
    ) -> "GraphTraceData":
        """Create GraphTraceData from an execution trace dict, with safe defaults.

        Args:
            trace: Raw execution trace dict, or None for a minimal empty instance.
            fallback_id: Execution ID to use when trace is None.

        Returns:
            GraphTraceData populated from dict or with empty defaults.
        """
        if trace:
            return cls(
                execution_id=trace.get("execution_id", fallback_id),
                agent_interactions=trace.get("agent_interactions", []),
                tool_calls=trace.get("tool_calls", []),
                timing_data=trace.get("timing_data", {}),
                coordination_events=trace.get("coordination_events", []),
            )
        return cls(execution_id=fallback_id)


class PeerReadEvalResult(BaseModel):
    """Result of evaluating agent review against PeerRead ground truth."""

    paper_id: str = Field(description="Paper being evaluated")
    agent_review: str = Field(description="Review generated by agent")
    ground_truth_reviews: list[PeerReadReview] = Field(
        description="Original peer reviews from dataset"
    )
    similarity_scores: dict[str, float] = Field(
        description="Similarity metrics (semantic, cosine, jaccard)"
    )
    overall_similarity: float = Field(description="Weighted overall similarity score (0-1)")
    recommendation_match: bool = Field(
        description="Whether agent recommendation matches ground truth"
    )
