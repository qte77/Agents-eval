"""
Judge settings module using pydantic-settings.

This module implements evaluation configuration following 12-Factor #3 (Config) principles:
- Defaults in code (version-controlled)
- Environment variable overrides via JUDGE_ prefix
- .env file support for local development
"""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JudgeSettings(BaseSettings):
    """
    Judge settings for the evaluation pipeline.

    Configuration follows 12-Factor #3 principles with typed defaults in code
    and environment variable overrides using the JUDGE_ prefix.
    Replaces JSON-based EvaluationConfig with pydantic-settings.

    Attributes:
        tiers_enabled: List of enabled evaluation tiers (1=Traditional, 2=LLM, 3=Graph)
        tier1_max_seconds: Tier 1 timeout (Traditional Metrics)
        tier2_max_seconds: Tier 2 timeout (LLM-as-Judge)
        tier3_max_seconds: Tier 3 timeout (Graph Analysis)
        total_max_seconds: Total pipeline timeout
        tier1_similarity_metrics: Similarity metrics for Tier 1
        tier1_confidence_threshold: Confidence threshold for Tier 1
        tier1_bertscore_model: BERTScore model name
        tier1_tfidf_max_features: Max features for TF-IDF
        tier2_model: LLM model for Tier 2 evaluation
        tier2_max_retries: Max retry attempts for LLM calls
        tier2_timeout_seconds: Request timeout for LLM calls
        tier2_cost_budget_usd: Cost budget for LLM evaluation
        tier2_paper_excerpt_length: Paper excerpt length for LLM context
        tier3_min_nodes: Minimum nodes for graph analysis
        tier3_centrality_measures: Centrality measures for graph analysis
        tier3_max_nodes: Maximum nodes for graph analysis
        tier3_max_edges: Maximum edges for graph analysis
        tier3_operation_timeout: Operation timeout for graph operations
        fallback_strategy: Fallback strategy when tiers fail
        trace_collection: Enable trace collection
        opik_enabled: Enable Opik tracing
        performance_logging: Enable performance logging
    """

    # Tiers configuration
    tiers_enabled: list[int] = Field(default=[1, 2, 3])

    # Performance targets (with validation)
    tier1_max_seconds: float = Field(default=1.0, gt=0, le=300)
    tier2_max_seconds: float = Field(default=10.0, gt=0, le=300)
    tier3_max_seconds: float = Field(default=15.0, gt=0, le=300)
    total_max_seconds: float = Field(default=25.0, gt=0, le=300)

    # Tier 1: Traditional Metrics
    tier1_similarity_metrics: list[str] = Field(default=["cosine", "jaccard", "semantic"])
    tier1_confidence_threshold: float = Field(default=0.8)
    tier1_bertscore_model: str = Field(default="distilbert-base-uncased")
    tier1_tfidf_max_features: int = Field(default=5000)

    # Tier 2: LLM-as-Judge
    tier2_model: str = Field(default="gpt-4o-mini")
    tier2_max_retries: int = Field(default=2)
    tier2_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    tier2_cost_budget_usd: float = Field(default=0.05)
    tier2_paper_excerpt_length: int = Field(default=2000)

    # Tier 3: Graph Analysis
    tier3_min_nodes: int = Field(default=2, gt=0)
    tier3_centrality_measures: list[str] = Field(
        default=["betweenness", "closeness", "degree"]
    )
    tier3_max_nodes: int = Field(default=1000, gt=0)
    tier3_max_edges: int = Field(default=5000, gt=0)
    tier3_operation_timeout: float = Field(default=10.0, gt=0, le=300)

    # Composite scoring
    fallback_strategy: str = Field(default="tier1_only")

    # Observability
    trace_collection: bool = Field(default=True)
    opik_enabled: bool = Field(default=True)
    performance_logging: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="JUDGE_", env_file=".env", env_file_encoding="utf-8"
    )

    def get_enabled_tiers(self) -> set[int]:
        """
        Get enabled tiers as a set.

        Returns:
            Set of enabled tier numbers for backward compatibility
        """
        return set(self.tiers_enabled)

    def is_tier_enabled(self, tier: int) -> bool:
        """
        Check if a specific tier is enabled.

        Args:
            tier: Tier number to check (1, 2, or 3)

        Returns:
            True if tier is enabled
        """
        return tier in self.tiers_enabled

    def get_performance_targets(self) -> dict[str, float]:
        """
        Get performance targets as dictionary.

        Returns:
            Dictionary of performance targets for backward compatibility
        """
        return {
            "tier1_max_seconds": self.tier1_max_seconds,
            "tier2_max_seconds": self.tier2_max_seconds,
            "tier3_max_seconds": self.tier3_max_seconds,
            "total_max_seconds": self.total_max_seconds,
        }

    def get_tier1_config(self) -> dict[str, Any]:
        """
        Get Tier 1 configuration as dictionary.

        Returns:
            Tier 1 configuration for engine initialization
        """
        return {
            "similarity_metrics": self.tier1_similarity_metrics,
            "confidence_threshold": self.tier1_confidence_threshold,
            "bertscore_model": self.tier1_bertscore_model,
            "tfidf_max_features": self.tier1_tfidf_max_features,
        }

    def get_tier2_config(self) -> dict[str, Any]:
        """
        Get Tier 2 configuration as dictionary.

        Returns:
            Tier 2 configuration for engine initialization
        """
        return {
            "model": self.tier2_model,
            "max_retries": self.tier2_max_retries,
            "timeout_seconds": self.tier2_timeout_seconds,
            "cost_budget_usd": self.tier2_cost_budget_usd,
            "paper_excerpt_length": self.tier2_paper_excerpt_length,
        }

    def get_tier3_config(self) -> dict[str, Any]:
        """
        Get Tier 3 configuration as dictionary.

        Returns:
            Tier 3 configuration for engine initialization
        """
        return {
            "min_nodes_for_analysis": self.tier3_min_nodes,
            "centrality_measures": self.tier3_centrality_measures,
            "max_nodes": self.tier3_max_nodes,
            "max_edges": self.tier3_max_edges,
            "operation_timeout_seconds": self.tier3_operation_timeout,
        }
