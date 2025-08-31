"""
Data models for three-tiered evaluation system.

This module provides Pydantic models for the comprehensive evaluation framework
that assesses multi-agent systems on PeerRead scientific paper review generation.
"""

from typing import Any

from pydantic import BaseModel, Field


class TechnicalAccuracyAssessment(BaseModel):
    """LLM assessment of technical accuracy."""

    factual_correctness: float = Field(
        ge=1.0, le=5.0, description="Factual correctness score"
    )
    methodology_understanding: float = Field(
        ge=1.0, le=5.0, description="Methodology understanding score"
    )
    domain_knowledge: float = Field(
        ge=1.0, le=5.0, description="Domain knowledge score"
    )
    explanation: str = Field(description="Explanation of the assessment")


class ConstructivenessAssessment(BaseModel):
    """LLM assessment of constructiveness."""

    actionable_feedback: float = Field(
        ge=1.0, le=5.0, description="Actionable feedback score"
    )
    balanced_critique: float = Field(
        ge=1.0, le=5.0, description="Balanced critique score"
    )
    improvement_guidance: float = Field(
        ge=1.0, le=5.0, description="Improvement guidance score"
    )
    explanation: str = Field(description="Explanation of the assessment")


class PlanningRationalityAssessment(BaseModel):
    """LLM assessment of planning rationality."""

    logical_flow: float = Field(ge=1.0, le=5.0, description="Logical flow score")
    decision_quality: float = Field(
        ge=1.0, le=5.0, description="Decision quality score"
    )
    resource_efficiency: float = Field(
        ge=1.0, le=5.0, description="Resource efficiency score"
    )
    explanation: str = Field(description="Explanation of the assessment")


class Tier1Result(BaseModel):
    """Traditional metrics evaluation result.

    Contains text similarity metrics, execution performance, and task success
    indicators using lightweight computational approaches.
    """

    cosine_score: float = Field(ge=0.0, le=1.0, description="TF-IDF cosine similarity")
    jaccard_score: float = Field(
        ge=0.0, le=1.0, description="Word-level Jaccard similarity"
    )
    semantic_score: float = Field(
        ge=0.0, le=1.0, description="BERT-based semantic similarity"
    )
    execution_time: float = Field(ge=0.0, description="Raw execution time in seconds")
    time_score: float = Field(ge=0.0, le=1.0, description="Normalized time score")
    task_success: float = Field(description="Binary success indicator (0.0 or 1.0)")
    overall_score: float = Field(
        ge=0.0, le=1.0, description="Weighted traditional metrics score"
    )


class Tier2Result(BaseModel):
    """LLM-as-Judge evaluation result.

    Contains quality assessments from large language model evaluation including
    technical accuracy, constructiveness, and planning rationality.
    """

    technical_accuracy: float = Field(
        ge=0.0, le=1.0, description="Technical accuracy score"
    )
    constructiveness: float = Field(
        ge=0.0, le=1.0, description="Constructiveness score"
    )
    clarity: float = Field(ge=0.0, le=1.0, description="Clarity and coherence score")
    planning_rationality: float = Field(
        ge=0.0, le=1.0, description="Planning quality score"
    )
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted LLM judge score")
    model_used: str = Field(description="LLM model used for evaluation")
    api_cost: float | None = Field(description="Estimated API cost in USD")
    fallback_used: bool = Field(default=False, description="Whether fallback was used")


class Tier3Result(BaseModel):
    """Graph-based analysis result.

    Contains metrics derived from analyzing agent coordination patterns,
    tool usage efficiency, and communication overhead using NetworkX.
    """

    path_convergence: float = Field(ge=0.0, le=1.0, description="Tool usage efficiency")
    tool_selection_accuracy: float = Field(
        ge=0.0, le=1.0, description="Tool choice accuracy"
    )
    communication_overhead: float = Field(
        ge=0.0, le=1.0, description="Communication efficiency"
    )
    coordination_centrality: float = Field(
        ge=0.0, le=1.0, description="Coordination quality"
    )
    task_distribution_balance: float = Field(
        ge=0.0, le=1.0, description="Load balancing"
    )
    overall_score: float = Field(
        ge=0.0, le=1.0, description="Weighted graph analysis score"
    )
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
    timing_data: dict[str, Any] = Field(
        description="Execution timestamps", default_factory=dict
    )
    coordination_events: list[dict[str, Any]] = Field(
        description="Manager delegation patterns", default_factory=list
    )


class EvaluationConfig(BaseModel):
    """Configuration model for evaluation system.

    Defines performance targets, weights, thresholds, and behavioral
    parameters for the three-tiered evaluation framework.
    """

    version: str = Field(description="Configuration version")

    # Performance targets
    tier1_max_seconds: float = Field(
        default=1.0, description="Tier 1 performance target"
    )
    tier2_max_seconds: float = Field(
        default=10.0, description="Tier 2 performance target"
    )
    tier3_max_seconds: float = Field(
        default=15.0, description="Tier 3 performance target"
    )
    total_max_seconds: float = Field(default=25.0, description="Total pipeline target")

    # Traditional metrics configuration
    similarity_metrics: list[str] = Field(
        default=["cosine", "jaccard", "semantic"],
        description="Enabled similarity metrics",
    )
    confidence_threshold: float = Field(
        default=0.8, description="Task success threshold"
    )
    bertscore_model: str = Field(
        default="distilbert-base-uncased", description="BERTScore model name"
    )

    # LLM judge configuration
    llm_model: str = Field(default="gpt-4o-mini", description="LLM judge model")
    llm_timeout: float = Field(default=30.0, description="LLM request timeout")
    llm_max_retries: int = Field(default=2, description="Maximum retry attempts")

    # Composite scoring weights
    composite_weights: dict[str, float] = Field(
        default={
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167,
            "tool_efficiency": 0.167,
            "planning_rational": 0.167,
            "output_similarity": 0.167,
        },
        description="Composite scoring weights",
    )

    # Recommendation thresholds
    recommendation_thresholds: dict[str, float] = Field(
        default={"accept": 0.8, "weak_accept": 0.6, "weak_reject": 0.4, "reject": 0.0},
        description="Score thresholds for recommendations",
    )


class EvaluationRequest(BaseModel):
    """Request structure for evaluation pipeline.

    Encapsulates all required data for running a complete
    three-tiered evaluation on a single paper.
    """

    paper_id: str = Field(description="Unique paper identifier")
    paper_content: str = Field(description="Full paper text content")
    agent_review: str = Field(description="Agent-generated review")
    reference_reviews: list[str] = Field(description="Ground truth reviews")
    execution_trace: GraphTraceData | None = None
    tiers_enabled: list[int] = Field(
        default=[1, 2, 3], description="Which tiers to run"
    )
    config_override: dict[str, Any] | None = None


class BatchEvaluationResult(BaseModel):
    """Result structure for batch evaluation operations.

    Contains aggregated results from multiple paper evaluations
    with performance statistics and summary metrics.
    """

    results: list[CompositeEvaluationResult] = Field(
        description="Individual evaluation results"
    )
    batch_id: str = Field(description="Batch execution identifier")
    total_papers: int = Field(description="Number of papers evaluated")
    successful_evaluations: int = Field(description="Number of successful evaluations")
    failed_evaluations: int = Field(description="Number of failed evaluations")

    # Performance statistics
    average_duration: float = Field(description="Average evaluation time per paper")
    total_duration: float = Field(description="Total batch processing time")
    average_composite_score: float = Field(
        description="Average composite score across batch"
    )

    # Summary statistics
    recommendation_distribution: dict[str, int] = Field(
        description="Count of each recommendation type", default_factory=dict
    )

    timestamp: str = Field(description="Batch completion timestamp")
    config_version: str = Field(description="Configuration version used")
