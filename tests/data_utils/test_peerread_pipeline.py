#!/usr/bin/env python3
"""
Complete end-to-end PeerRead pipeline test.

This script demonstrates:
1. Dataset downloading and caching
2. Agent setup with single LLM (manager only)
3. Paper retrieval and review generation
4. Review evaluation against ground truth
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, "src")

from pydantic_ai.usage import UsageLimits

from app.agents.agent_system import get_manager
from app.data_models.app_models import AppEnv, ChatConfig
from app.data_utils.datasets_peerread import (
    PeerReadDownloader,
    PeerReadLoader,
    load_peerread_config,
)
from app.llms.providers import get_api_key, get_provider_config


@pytest.mark.asyncio
async def test_complete_pipeline():
    """Run complete end-to-end pipeline test."""

    print("🚀 Starting PeerRead End-to-End Pipeline Test")
    print("=" * 60)

    # Step 1: Load configuration and setup
    print("\n📋 Step 1: Loading configuration...")
    try:
        config = load_peerread_config()
        print(
            f"""
            ✅ Config loaded: {len(config.venues)} venues, {len(config.splits)} splits
            """
        )
        print(f"   Cache directory: {config.cache_directory}")
        print(f"   Max papers per query: {config.max_papers_per_query}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return

    # Step 2: Download dataset sample
    print("\n📥 Step 2: Downloading specific papers...")
    try:
        downloader = PeerReadDownloader(config)

        # Download specific known papers
        known_papers = ["104", "123", "456"]  # Known to exist from tests
        downloaded_count = 0

        for paper_id in known_papers:
            paper_data = downloader.download_paper("acl_2017", "train", paper_id)
            if paper_data:
                downloaded_count += 1
                print(f"✅ Downloaded paper {paper_id}")

                # Cache the paper
                cache_path = Path(config.cache_directory) / "acl_2017" / "train"
                cache_path.mkdir(parents=True, exist_ok=True)

                with open(cache_path / f"{paper_id}.json", "w") as f:
                    json.dump(paper_data, f, indent=2)

        if downloaded_count > 0:
            print(f"✅ Downloaded {downloaded_count} papers")
        else:
            print("❌ No papers downloaded successfully")
            return

    except Exception as e:
        print(f"❌ Download error: {e}")
        return

    # Step 3: Load papers
    print("\n📚 Step 3: Loading papers...")
    try:
        loader = PeerReadLoader(config)
        papers = loader.load_papers("acl_2017", "train")

        if not papers:
            print("❌ No papers loaded")
            return

        print(f"✅ Loaded {len(papers)} papers")

        # Find a paper with reviews for testing
        test_paper = None
        for paper in papers[:3]:  # Check first 3 papers
            if len(paper.reviews) > 0:
                test_paper = paper
                break

        if not test_paper:
            print("❌ No papers with reviews found")
            return

        print(f"📄 Selected test paper: {test_paper.paper_id}")
        print(f"   Title: {test_paper.title[:80]}...")
        print(f"   Reviews: {len(test_paper.reviews)}")

    except Exception as e:
        print(f"❌ Loading error: {e}")
        return

    # Step 4: Setup agent system
    print("\n🤖 Step 4: Setting up agent system...")
    try:
        # Load chat configuration
        with open("src/app/config/config_chat.json") as f:
            chat_config_data = json.load(f)
        chat_config = ChatConfig.model_validate(chat_config_data)

        # Setup environment - using Ollama as default (available locally)
        provider = "ollama"
        env_config = AppEnv()

        # Get provider configuration
        provider_config = get_provider_config(provider, chat_config.providers)
        api_key = get_api_key(provider, env_config)

        if not api_key and provider != "ollama":
            print(f"❌ No API key found for {provider}")
            print(
                f"""
                   Set {provider.upper()}_API_KEY environment variable or use different
                provider
                """
            )
            return

        # Create manager agent (single LLM setup)
        manager = get_manager(
            provider=provider,
            provider_config=provider_config,
            api_key=api_key,
            prompts=chat_config.prompts,
            include_researcher=False,  # Single LLM - manager only
            include_analyst=False,
            include_synthesiser=False,
        )

        print(f"✅ Agent system initialized with {provider}")
        print("   Configuration: Manager only (single LLM)")

    except Exception as e:
        print(f"❌ Agent setup error: {e}")
        return

    # Step 5: Generate paper review
    print(f"\n✍️  Step 5: Generating review for paper {test_paper.paper_id}...")
    try:
        # Create query for paper review
        review_query = f"""
        Please review the following scientific paper comprehensively:
        
        Title: {test_paper.title}
        
        Abstract: {test_paper.abstract}
        
        Write a detailed peer review covering:
        1. Impact and significance of the work
        2. Technical substance and methodology
        3. Clarity and presentation quality
        4. Overall recommendation (accept/reject with reasoning)
        
        Be specific and constructive in your feedback.
        """

        # Set usage limits for the test
        usage_limits = UsageLimits(request_limit=5, total_tokens_limit=10000)

        # Run the agent
        result = await manager.run(user_prompt=review_query, usage=usage_limits)

        agent_review = str(result.output)
        print(f"✅ Review generated ({len(agent_review)} characters)")
        print(f"   Usage: {result.usage()}")
        print("\n📝 Generated Review:")
        print("-" * 40)
        print(agent_review[:500] + "..." if len(agent_review) > 500 else agent_review)
        print("-" * 40)

    except Exception as e:
        print(f"❌ Review generation error: {e}")
        return

    # Step 6: Evaluate review against ground truth
    print("\n📊 Step 6: Evaluating review against ground truth...")
    try:
        from app.evals.traditional_metrics import create_evaluation_result

        # Create evaluation result
        eval_result = create_evaluation_result(
            paper_id=test_paper.paper_id,
            agent_review=agent_review,
            ground_truth_reviews=test_paper.reviews,
        )

        print("✅ Evaluation completed")
        print(f"   Overall similarity: {eval_result.overall_similarity:.3f}")
        print(f"   Recommendation match: {eval_result.recommendation_match}")
        print("   Similarity scores:")
        for metric, score in eval_result.similarity_scores.items():
            print(f"     {metric}: {score:.3f}")

        print("\n📋 Ground Truth Summary:")
        print(f"   Number of reviews: {len(eval_result.ground_truth_reviews)}")
        for i, review in enumerate(eval_result.ground_truth_reviews[:2]):  # Show first 2
            print(f"   Review {i + 1} recommendation: {review.recommendation}")
            print(f"   Review {i + 1} excerpt: {review.comments[:100]}...")

    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return

    # Step 7: Agent-based evaluation (using tools)
    print("\n🔧 Step 7: Testing agent tools directly...")
    try:
        # Test the agent tools by asking it to use them
        tool_query = f"""
        Please demonstrate the PeerRead tools by:
        1. Getting paper {test_paper.paper_id} using get_peerread_paper
        2. Querying for papers from acl_2017 with at least 1 review using
        query_peerread_papers
        3. Evaluating a simple review using evaluate_paper_review
        
        For the evaluation, use this sample review text:
        "This paper presents interesting ideas but lacks sufficient experimental
        validation. The methodology is sound but the results are not convincing
        enough for acceptance."
        """

        tool_result = await manager.run(user_prompt=tool_query, usage=usage_limits)

        print("✅ Agent tool demonstration completed")
        print(f"   Usage: {tool_result.usage()}")
        print("\n🔧 Tool Usage Result:")
        print("-" * 40)
        tool_output = str(tool_result.output)
        print(tool_output[:800] + "..." if len(tool_output) > 800 else tool_output)
        print("-" * 40)

    except Exception as e:
        print(f"❌ Agent tool test error: {e}")
        return

    # Final summary
    print("\n🎉 Pipeline Test Complete!")
    print("=" * 60)
    print("✅ All steps completed successfully:")
    print("   1. Configuration loaded")
    print("   2. Dataset downloaded and cached")
    print("   3. Papers loaded from cache")
    print("   4. Agent system initialized")
    print("   5. Paper review generated")
    print("   6. Review evaluated against ground truth")
    print("   7. Agent tools tested")
    print("\n📈 Final Results:")
    print(f"   Paper ID: {test_paper.paper_id}")
    print(f"   Review similarity: {eval_result.overall_similarity:.3f}")
    print(f"   Recommendation match: {eval_result.recommendation_match}")
    print(f"   Total API usage: {result.usage()}")


if __name__ == "__main__":
    # Run the complete pipeline
    asyncio.run(test_complete_pipeline())
