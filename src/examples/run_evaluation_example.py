"""
Example: Running the Three-Tiered Evaluation System End-to-End

This example demonstrates how to run the evaluation framework implemented
in Day 2 of Sprint 1 to evaluate agent-generated academic paper reviews.
"""

import asyncio

# Import our evaluation components
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.evals.llm_judge import evaluate_single_llm_judge
from app.evals.trace_processors import get_trace_collector
from app.evals.traditional_metrics import evaluate_single_traditional


async def run_evaluation_example():
    """
    Example of running a complete evaluation on a sample paper review.

    This demonstrates the complete Day 2 evaluation pipeline:
    1. Traditional Metrics (Tier 1) - Text similarity and execution metrics
    2. LLM-as-Judge (Tier 2) - Quality assessment using language models
    3. Trace Collection - For future graph analysis (Day 3)
    """
    print("=== Three-Tiered Evaluation System Demo ===\n")

    # Sample data for demonstration
    sample_paper = """
    This paper presents a novel approach to transformer-based language models
    for scientific text generation. The methodology involves fine-tuning 
    pre-trained models on domain-specific datasets with comprehensive 
    evaluation across multiple benchmarks. The authors demonstrate significant
    improvements in coherence and factual accuracy compared to baseline methods.
    The experimental setup includes rigorous ablation studies and statistical
    significance testing across diverse scientific domains.
    """

    agent_generated_review = """
    The paper demonstrates solid technical methodology with clear experimental
    design and comprehensive evaluation. The transformer-based approach shows
    promise for scientific text generation. However, the evaluation could be 
    more comprehensive in terms of human evaluation metrics. The writing 
    clarity is good but could be improved in the methodology section. 
    I recommend acceptance with minor revisions to address the evaluation
    limitations and improve presentation clarity.
    """

    reference_reviews = [
        """
        Strong technical contribution with comprehensive experimental validation.
        The methodology is sound and the results are convincing. Minor issues
        with presentation that should be addressed before publication.
        """,
        """
        Good work on transformer applications to scientific domains. The 
        evaluation is thorough and the results support the claims. Some
        concerns about generalizability that could be addressed.
        """,
    ]

    # Simulated execution trace for demonstration
    execution_trace = {
        "agent_interactions": [
            {
                "from": "Manager",
                "to": "Researcher",
                "type": "task_request",
                "timestamp": 1.0,
            },
            {
                "from": "Researcher",
                "to": "Analyst",
                "type": "data_transfer",
                "timestamp": 2.5,
            },
            {
                "from": "Analyst",
                "to": "Synthesizer",
                "type": "result_delivery",
                "timestamp": 4.0,
            },
        ],
        "tool_calls": [
            {
                "tool_name": "paper_retrieval",
                "timestamp": 1.5,
                "success": True,
                "duration": 0.3,
            },
            {
                "tool_name": "duckduckgo_search",
                "timestamp": 2.0,
                "success": True,
                "duration": 1.2,
            },
            {
                "tool_name": "review_synthesis",
                "timestamp": 3.5,
                "success": True,
                "duration": 0.8,
            },
        ],
        "coordination_events": [
            {
                "coordination_type": "delegation",
                "target_agents": ["Researcher"],
                "timestamp": 1.0,
            }
        ],
    }

    print("1. TIER 1: Traditional Metrics Evaluation")
    print("-" * 50)

    # Run Tier 1: Traditional Metrics
    tier1_result = evaluate_single_traditional(
        agent_output=agent_generated_review,
        reference_texts=reference_reviews,
        config={"confidence_threshold": 0.8},
    )

    print(f"Cosine Similarity: {tier1_result.cosine_score:.3f}")
    print(f"Jaccard Similarity: {tier1_result.jaccard_score:.3f}")
    print(f"Semantic Similarity: {tier1_result.semantic_score:.3f}")
    print(f"Execution Time: {tier1_result.execution_time:.3f}s")
    print(f"Task Success: {tier1_result.task_success}")
    print(f"Overall Tier 1 Score: {tier1_result.overall_score:.3f}")
    print()

    print("2. TIER 2: LLM-as-Judge Evaluation")
    print("-" * 50)

    # Run Tier 2: LLM-as-Judge (with GitHub model config)
    llm_config = {
        "tier2_llm_judge": {
            "provider": "github",
            "model": "gpt-4o-mini",
            "fallback_provider": "openai",
            "fallback_model": "gpt-4o-mini",
            "timeout_seconds": 30.0,
            "weights": {
                "technical_accuracy": 0.4,
                "constructiveness": 0.3,
                "planning_rationality": 0.3,
            },
        }
    }

    try:
        tier2_result = await evaluate_single_llm_judge(
            paper=sample_paper,
            review=agent_generated_review,
            execution_trace=execution_trace,
            config=llm_config,
        )

        print(f"Technical Accuracy: {tier2_result.technical_accuracy:.3f}")
        print(f"Constructiveness: {tier2_result.constructiveness:.3f}")
        print(f"Planning Rationality: {tier2_result.planning_rationality:.3f}")
        print(f"Model Used: {tier2_result.model_used}")
        print(
            f"API Cost: ${tier2_result.api_cost:.4f}"
            if tier2_result.api_cost
            else "API Cost: $0.0000"
        )
        print(f"Fallback Used: {tier2_result.fallback_used}")
        print(f"Overall Tier 2 Score: {tier2_result.overall_score:.3f}")
        print()

    except Exception as e:
        print(f"LLM Judge evaluation failed (expected without API keys): {e}")
        print("Using fallback evaluation...")
        tier2_result = None
        print()

    print("3. TRACE COLLECTION: Observability Infrastructure")
    print("-" * 50)

    # Initialize trace collection for future graph analysis (Day 3)
    trace_collector = get_trace_collector(
        config={"observability": {"trace_collection": True}}
    )

    # Demonstrate trace collection
    execution_id = "demo_evaluation_001"
    trace_collector.start_execution(execution_id)

    # Log sample interactions
    trace_collector.log_agent_interaction(
        from_agent="Manager",
        to_agent="Researcher",
        interaction_type="task_request",
        data={"task": "Analyze paper quality"},
    )

    trace_collector.log_tool_call(
        agent_id="Researcher",
        tool_name="paper_analysis",
        success=True,
        duration=1.2,
        context="Technical methodology assessment",
    )

    trace_collector.log_coordination_event(
        manager_agent="Manager",
        event_type="delegation",
        target_agents=["Researcher", "Analyst"],
        data={"priority": "high"},
    )

    # End trace collection
    processed_trace = trace_collector.end_execution()

    if processed_trace:
        print(f"Execution ID: {processed_trace.execution_id}")
        print(f"Duration: {processed_trace.performance_metrics['total_duration']:.3f}s")
        print(
            f"Agent Interactions: "
            f"{processed_trace.performance_metrics['agent_interactions']}"
        )
        print(f"Tool Calls: {processed_trace.performance_metrics['tool_calls']}")
        print("Trace data collected successfully for Day 3 graph analysis")
    else:
        print("Trace collection completed (data stored in ./logs/traces/)")

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    # Calculate composite score (simplified version)
    if tier2_result:
        composite_score = (
            tier1_result.overall_score * 0.4
            + tier2_result.overall_score * 0.4
            + 0.8 * 0.2  # Placeholder for Tier 3 graph analysis
        )
    else:
        composite_score = tier1_result.overall_score

    print(f"Final Composite Score: {composite_score:.3f}")

    # Determine recommendation
    if composite_score >= 0.8:
        recommendation = "Accept"
    elif composite_score >= 0.6:
        recommendation = "Weak Accept"
    elif composite_score >= 0.4:
        recommendation = "Weak Reject"
    else:
        recommendation = "Reject"

    print(f"Recommendation: {recommendation}")
    print(f"Confidence: {min(composite_score, 1.0):.3f}")

    return {
        "tier1_result": tier1_result,
        "tier2_result": tier2_result,
        "composite_score": composite_score,
        "recommendation": recommendation,
        "trace_collected": processed_trace is not None,
    }


def run_traditional_metrics_only_example():
    """
    Simplified example running only Tier 1 traditional metrics.

    This is useful when you want to quickly test the basic evaluation
    without needing API keys or complex setup.
    """
    print("=== Traditional Metrics Only Demo ===\n")

    agent_review = "This paper shows good methodology and clear results."
    reference_reviews = ["The work demonstrates solid approach and findings."]

    result = evaluate_single_traditional(
        agent_output=agent_review, reference_texts=reference_reviews
    )

    print(f"Cosine Similarity: {result.cosine_score:.3f}")
    print(f"Jaccard Similarity: {result.jaccard_score:.3f}")
    print(f"Overall Score: {result.overall_score:.3f}")
    print(f"Task Success: {'✓' if result.task_success else '✗'}")

    return result


if __name__ == "__main__":
    print("Choose evaluation mode:")
    print("1. Full three-tier evaluation (requires API setup)")
    print("2. Traditional metrics only (no API required)")

    try:
        choice = input("Enter choice (1 or 2): ").strip()
    except EOFError:
        choice = "1"
        print("1")  # Show the default choice

    if choice == "1":
        # Run full evaluation
        result = asyncio.run(run_evaluation_example())
        print("\nFull evaluation completed!")

    elif choice == "2":
        # Run traditional metrics only
        result = run_traditional_metrics_only_example()
        print("\nTraditional metrics evaluation completed!")

    else:
        print("Invalid choice. Running traditional metrics only...")
        result = run_traditional_metrics_only_example()
