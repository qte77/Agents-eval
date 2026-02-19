"""Basic evaluation example using the three-tier EvaluationPipeline.

Purpose:
    Demonstrates the plugin-based evaluation system with realistic paper/review
    data. Shows how to construct a GraphTraceData trace, configure a pipeline,
    and interpret the resulting CompositeResult.

Prerequisites:
    - API key for the Tier 2 LLM provider set in .env (e.g. OPENAI_API_KEY)
      or run with tiers_enabled=[1, 3] to skip LLM calls entirely.
    - No dataset download required: uses synthetic data.

Expected output:
    Composite score in [0.0, 1.0] and a recommendation string such as
    "accept", "weak_accept", "weak_reject", or "reject".

Usage:
    uv run python src/examples/basic_evaluation.py
"""

import asyncio

from app.data_models.evaluation_models import CompositeResult, GraphTraceData
from app.data_models.peerread_models import PeerReadPaper, PeerReadReview
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.settings import JudgeSettings
from app.utils.log import logger


def _make_synthetic_paper() -> PeerReadPaper:
    """Build a minimal synthetic PeerReadPaper for the example."""
    review = PeerReadReview(
        comments=(
            "The paper presents a novel attention mechanism with strong empirical results. "
            "The ablation study is thorough and the writing is clear. "
            "Minor concern: related work section could be expanded."
        ),
        recommendation="accept",
        reviewer_confidence="4",
        soundness_correctness="4",
        originality="4",
        clarity="5",
    )
    return PeerReadPaper(
        paper_id="example-001",
        title="Efficient Attention for Long-Context Transformers",
        abstract=(
            "We propose a linear-complexity attention mechanism that achieves "
            "competitive results on standard NLP benchmarks while reducing "
            "memory usage by 60% compared to full self-attention."
        ),
        reviews=[review],
    )


def _make_synthetic_trace() -> GraphTraceData:
    """Build a minimal GraphTraceData representing a 3-agent MAS execution."""
    return GraphTraceData(
        execution_id="example-run-001",
        agent_interactions=[
            {"from": "orchestrator", "to": "researcher", "message": "Analyze paper claims"},
            {"from": "researcher", "to": "analyst", "message": "Pass domain findings"},
            {"from": "analyst", "to": "synthesiser", "message": "Draft review sections"},
            {"from": "synthesiser", "to": "orchestrator", "message": "Submit final review"},
        ],
        tool_calls=[
            {"tool": "search_arxiv", "agent": "researcher", "success": True, "duration_s": 1.2},
            {"tool": "extract_claims", "agent": "analyst", "success": True, "duration_s": 0.8},
            {"tool": "write_review", "agent": "synthesiser", "success": True, "duration_s": 2.1},
        ],
        timing_data={
            "start": "2026-01-01T10:00:00Z",
            "end": "2026-01-01T10:00:08Z",
            "total_seconds": 8.0,
        },
        coordination_events=[
            {"type": "delegation", "from": "orchestrator", "to": "researcher"},
            {"type": "delegation", "from": "orchestrator", "to": "analyst"},
        ],
    )


async def run_example() -> CompositeResult:
    """Run a complete three-tier evaluation with synthetic data.

    Tier 1 (Traditional Metrics) and Tier 3 (Graph Analysis) run locally.
    Tier 2 (LLM-as-Judge) requires an API key; set tiers_enabled=[1, 3]
    in JudgeSettings to skip it without an API key.

    Returns:
        CompositeResult with composite_score and recommendation.
    """
    paper = _make_synthetic_paper()
    trace = _make_synthetic_trace()

    # Configure pipeline — disable Tier 2 to skip LLM calls for the example
    settings = JudgeSettings(tiers_enabled=[1, 3])
    pipeline = EvaluationPipeline(settings=settings)

    # Compose a plausible agent-generated review from the paper data
    agent_review = (
        f"Review of: {paper.title}\n\n"
        "This paper introduces an efficient attention mechanism for transformers. "
        "The empirical evaluation is solid with clear ablations. "
        "The memory reduction claims are well-supported. "
        "Recommended for acceptance pending minor revisions to the related work section."
    )

    result = await pipeline.evaluate_comprehensive(
        paper=paper.abstract,
        review=agent_review,
        execution_trace=trace,
        reference_reviews=[r.comments for r in paper.reviews if r.comments],
    )

    logger.info(
        f"Evaluation complete — score: {result.composite_score:.3f}, "
        f"recommendation: {result.recommendation}"
    )
    return result


if __name__ == "__main__":
    result = asyncio.run(run_example())
    print(f"Composite score : {result.composite_score:.3f}")
    print(f"Recommendation  : {result.recommendation}")
    print(f"Tiers enabled   : {result.tiers_enabled}")
