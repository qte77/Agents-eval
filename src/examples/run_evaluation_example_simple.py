"""
Example: Simple Three-Tiered Evaluation System Demo

This simplified example demonstrates the new evaluation pipeline
without trying to access individual tier results.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.evals.evaluation_pipeline import EvaluationPipeline


async def run_simple_evaluation():
    """Simple example using the new evaluation pipeline."""

    print("=== Simple Three-Tier Evaluation Demo ===\n")

    # Sample data
    sample_paper = """
    This paper presents a novel approach to transformer-based language models
    for scientific text generation. The methodology involves fine-tuning 
    pre-trained models on domain-specific datasets with comprehensive 
    evaluation across multiple benchmarks.
    """

    agent_review = """
    The paper demonstrates solid technical methodology with clear experimental
    design. The transformer-based approach shows promise for scientific text
    generation. I recommend acceptance with minor revisions.
    """

    reference_reviews = [
        "Strong technical contribution with comprehensive validation.",
        "Good work on transformer applications to scientific domains.",
    ]

    execution_trace = {
        "agent_interactions": [
            {
                "from": "Manager",
                "to": "Researcher",
                "type": "task_request",
                "timestamp": 1.0,
            }
        ],
        "tool_calls": [
            {
                "tool_name": "paper_analysis",
                "timestamp": 1.5,
                "success": True,
                "duration": 0.8,
            }
        ],
        "coordination_events": [
            {
                "coordination_type": "delegation",
                "target_agents": ["Researcher"],
                "timestamp": 1.0,
            }
        ],
    }

    try:
        print("Initializing evaluation pipeline...")
        pipeline = EvaluationPipeline()

        print("Running comprehensive evaluation...")
        result = await pipeline.evaluate_comprehensive(
            paper=sample_paper,
            review=agent_review,
            execution_trace=execution_trace,
            reference_reviews=reference_reviews,
        )

        print("\n" + "=" * 40)
        print("EVALUATION RESULTS")
        print("=" * 40)
        print(f"Final Score: {result.composite_score:.3f}")
        print(f"Recommendation: {result.recommendation}")
        print(f"Recommendation Weight: {result.recommendation_weight:.3f}")

        # Performance metrics
        stats = pipeline.get_execution_stats()
        print("Performance:")
        print(f"  Total Time: {stats['total_time']:.3f}s")
        print(f"  Tiers Executed: {stats['tiers_executed']}")
        print(f"  Fallback Used: {stats['fallback_used']}")

        return result

    except Exception as e:
        print(f"Evaluation failed: {e}")
        print("This is expected without proper API keys configured.")
        return None


if __name__ == "__main__":
    result = asyncio.run(run_simple_evaluation())
    if result:
        print("Evaluation completed successfully!")
    else:
        print("Evaluation failed (expected without API setup)")
