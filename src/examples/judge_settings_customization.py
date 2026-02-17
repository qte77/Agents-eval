"""JudgeSettings customization example.

Purpose:
    Demonstrates how to configure the evaluation pipeline via JudgeSettings:
    - Environment variable overrides (JUDGE_ prefix)
    - Programmatic settings modification
    - Timeout adjustment, tier selection, provider configuration

Prerequisites:
    None — JudgeSettings is pure Python/Pydantic, no API keys required.

Environment variable override pattern:
    All settings can be overridden via JUDGE_<FIELD_NAME> in .env or shell:

        JUDGE_TIER2_PROVIDER=anthropic
        JUDGE_TIER1_MAX_SECONDS=2.0
        JUDGE_TIERS_ENABLED=[1,3]

    Pydantic-settings reads these automatically when JudgeSettings() is created.

Usage:
    uv run python src/examples/judge_settings_customization.py
"""

from app.judge.settings import JudgeSettings
from app.utils.log import logger


def example_timeout_adjustment() -> JudgeSettings:
    """Adjust tier timeouts for slower or faster environments.

    Returns:
        JudgeSettings with increased timeouts suitable for larger models.
    """
    settings = JudgeSettings(
        tier1_max_seconds=2.0,   # allow more time for BERTScore on long abstracts
        tier2_max_seconds=30.0,  # allow slow LLM providers
        tier3_max_seconds=20.0,  # allow larger graphs
        total_max_seconds=60.0,
    )
    logger.info(
        f"Timeouts — T1: {settings.tier1_max_seconds}s, "
        f"T2: {settings.tier2_max_seconds}s, "
        f"T3: {settings.tier3_max_seconds}s"
    )
    return settings


def example_tier_selection() -> JudgeSettings:
    """Enable only Tier 1 and Tier 3 (no LLM calls, no API key needed).

    Returns:
        JudgeSettings with Tier 2 disabled.
    """
    settings = JudgeSettings(tiers_enabled=[1, 3])
    enabled = settings.get_enabled_tiers()
    logger.info(f"Enabled tiers: {sorted(enabled)}")
    assert not settings.is_tier_enabled(2), "Tier 2 should be disabled"
    return settings


def example_provider_selection() -> JudgeSettings:
    """Switch the Tier 2 LLM judge to a specific provider.

    Returns:
        JudgeSettings configured for Anthropic as Tier 2 provider.
    """
    settings = JudgeSettings(
        tier2_provider="anthropic",
        tier2_model="claude-haiku-4-5",
        tier2_fallback_provider="openai",
    )
    logger.info(
        f"Tier 2 provider: {settings.tier2_provider} / {settings.tier2_model}, "
        f"fallback: {settings.tier2_fallback_provider}"
    )
    return settings


def example_composite_thresholds() -> JudgeSettings:
    """Adjust composite score thresholds for stricter evaluation.

    Returns:
        JudgeSettings with raised acceptance thresholds.
    """
    settings = JudgeSettings(
        composite_accept_threshold=0.85,       # raise bar for "accept"
        composite_weak_accept_threshold=0.65,  # raise bar for "weak_accept"
        composite_weak_reject_threshold=0.35,  # lower bar for "weak_reject"
        fallback_strategy="tier1_only",
    )
    logger.info(
        f"Thresholds — accept: {settings.composite_accept_threshold}, "
        f"weak_accept: {settings.composite_weak_accept_threshold}, "
        f"weak_reject: {settings.composite_weak_reject_threshold}"
    )
    return settings


if __name__ == "__main__":
    print("=== Timeout adjustment ===")
    s1 = example_timeout_adjustment()
    print(f"  tier2_max_seconds: {s1.tier2_max_seconds}")

    print("\n=== Tier selection ===")
    s2 = example_tier_selection()
    print(f"  enabled tiers: {sorted(s2.get_enabled_tiers())}")

    print("\n=== Provider selection ===")
    s3 = example_provider_selection()
    print(f"  tier2_provider: {s3.tier2_provider}")

    print("\n=== Composite thresholds ===")
    s4 = example_composite_thresholds()
    print(f"  composite_accept_threshold: {s4.composite_accept_threshold}")
