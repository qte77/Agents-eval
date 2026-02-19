# Troubleshooting Guide

This document provides guidance for common issues encountered during evaluation and development.

## Table of Contents

- [Tier 2 Authentication Failures](#tier-2-authentication-failures)

## Tier 2 Authentication Failures

### Symptoms

When running evaluations with Tier 2 (LLM-as-Judge) enabled, you may see:

- Warning logs: `"Auth failure detected - using neutral fallback score"`
- Tier 2 metrics return neutral scores (0.5)
- `Tier2Result.fallback_used` is `True`
- Lower composite scores due to neutral Tier 2 contributions

### Causes

Authentication failures occur when:

1. **Missing API keys**: Primary provider (`tier2_provider`) has no API key configured
2. **Invalid API keys**: Configured API key is expired or incorrect
3. **No fallback provider**: Both primary and fallback providers lack valid API keys

### Resolution

#### 1. Check API Key Configuration

Verify environment variables are set correctly:

```bash
# For OpenAI (default primary provider)
echo $OPENAI_API_KEY

# For GitHub (common fallback)
echo $GITHUB_API_KEY

# For other providers (Cerebras, Groq, etc.)
echo $CEREBRAS_API_KEY
echo $GROQ_API_KEY
```

#### 2. Configure Fallback Provider

Update `JudgeSettings` to specify a fallback provider:

```python
from app.judge.settings import JudgeSettings

settings = JudgeSettings(
    tier2_provider="openai",
    tier2_model="gpt-4o-mini",
    tier2_fallback_provider="github",  # Fallback when primary fails
    tier2_fallback_model="gpt-4o-mini",
)
```

#### 3. Provider Fallback Chain

The evaluation engine follows this fallback chain:

1. **Primary provider** (`tier2_provider`) - checked first
2. **Fallback provider** (`tier2_fallback_provider`) - used if primary unavailable
3. **Neutral scores** (0.5) - returned when all providers unavailable

#### 4. Verify Provider Selection

Use the `select_available_provider()` method to check which provider will be used:

```python
from app.data_models.app_models import AppEnv
from app.judge.llm_evaluation_managers import LLMJudgeEngine

engine = LLMJudgeEngine(settings)
env_config = AppEnv()  # Loads from environment

selected = engine.select_available_provider(env_config)
if selected is None:
    print("No providers available - Tier 2 will use neutral fallback scores")
else:
    provider, model = selected
    print(f"Using provider: {provider}/{model}")
```

### Expected Behavior

#### When Auth Fails

- **Individual assessments** return neutral score (0.5)
  - `technical_accuracy`: 0.5
  - `constructiveness`: 0.5
  - `planning_rationality`: 0.5
- **`fallback_used` flag** set to `True`
- **`model_used` field** shows configured provider (not "fallback_traditional")
- **Composite scoring** redistributes weights to Tier 1 + Tier 3

#### When Auth Succeeds

- **Full LLM-based scores** (0.0-1.0 range based on assessment)
- **`fallback_used` flag** set to `False`
- **Normal composite scoring** with all three tiers

### Disabling Tier 2

If you don't have access to LLM providers, disable Tier 2 entirely:

```python
settings = JudgeSettings(
    tier1_enabled=True,
    tier2_enabled=False,  # Skip LLM-as-Judge
    tier3_enabled=True,
)
```

This avoids auth failure warnings and redistributes weights to Tier 1 + Tier 3 automatically.

### Logging

Enable debug logging to see provider selection details:

```python
import logging
logging.getLogger("app.judge.llm_evaluation_managers").setLevel(logging.DEBUG)
```

You'll see logs like:

- `"Using primary provider: openai/gpt-4o-mini"`
- `"Primary provider unavailable, using fallback: github/gpt-4o-mini"`
- `"Neither primary nor fallback providers have valid API keys"`
