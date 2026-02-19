"""
Judge settings module using pydantic-settings.

This module implements evaluation configuration following 12-Factor #3 (Config) principles:
- Defaults in code (version-controlled)
- Environment variable overrides via JUDGE_ prefix
- .env file support for local development
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JudgeSettings(BaseSettings):
    """
    Judge settings for the evaluation pipeline.

    Configuration follows 12-Factor #3 principles with typed defaults in code
    and environment variable overrides using the JUDGE_ prefix.
    Uses pydantic-settings for typed, environment-driven configuration.

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
        tier2_provider: LLM provider for Tier 2 evaluation
        tier2_model: LLM model for Tier 2 evaluation
        tier2_fallback_provider: Fallback LLM provider
        tier2_fallback_model: Fallback LLM model
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
        composite_accept_threshold: Score threshold for "accept" recommendation
        composite_weak_accept_threshold: Score threshold for "weak_accept"
        composite_weak_reject_threshold: Score threshold for "weak_reject"
        trace_collection: Enable trace collection
        trace_storage_path: Directory for trace file storage
        logfire_enabled: Enable Logfire tracing
        logfire_send_to_cloud: Send traces to Logfire cloud (requires LOGFIRE_TOKEN)
        phoenix_endpoint: Phoenix local trace viewer endpoint
        logfire_service_name: Service name for tracing
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
    tier2_provider: str = Field(default="auto")
    tier2_model: str = Field(default="gpt-4o-mini")
    tier2_fallback_provider: str = Field(default="github")
    tier2_fallback_model: str = Field(default="gpt-4o-mini")
    tier2_max_retries: int = Field(default=2)
    tier2_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    tier2_cost_budget_usd: float = Field(default=0.05)
    tier2_paper_excerpt_length: int = Field(default=2000)

    # Tier 3: Graph Analysis
    tier3_min_nodes: int = Field(default=2, gt=0)
    tier3_centrality_measures: list[str] = Field(default=["betweenness", "closeness", "degree"])
    tier3_max_nodes: int = Field(default=1000, gt=0)
    tier3_max_edges: int = Field(default=5000, gt=0)
    tier3_operation_timeout: float = Field(default=10.0, gt=0, le=300)

    # Composite scoring
    fallback_strategy: str = Field(default="tier1_only")
    composite_accept_threshold: float = Field(default=0.8, ge=0, le=1)
    composite_weak_accept_threshold: float = Field(default=0.6, ge=0, le=1)
    composite_weak_reject_threshold: float = Field(default=0.4, ge=0, le=1)

    # Observability
    trace_collection: bool = Field(default=True)
    trace_storage_path: str = Field(default="./logs/Agent_evals/traces/")
    logfire_enabled: bool = Field(default=True)
    logfire_send_to_cloud: bool = Field(default=False)
    phoenix_endpoint: str = Field(default="http://localhost:6006")
    logfire_service_name: str = Field(default="peerread-evaluation")
    performance_logging: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="JUDGE_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
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
