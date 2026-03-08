---
title: CC Model & Provider Configuration
source: https://code.claude.com/docs/en/settings#environment-variables, https://openrouter.ai/docs/guides/guides/coding-agents/claude-code-integration
purpose: Reference for configuring CC with alternative models, endpoints, API keys, and third-party providers (OpenRouter, Bedrock, Vertex, Foundry).
created: 2026-03-07
---

**Status**: Reference (actionable configuration guide)

## Model Selection

<!-- markdownlint-disable MD013 -->

| Variable | Purpose | Example |
| -------- | ------- | ------- |
| `ANTHROPIC_MODEL` | Primary model override | `claude-sonnet-4-6` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Override Haiku-class model | Custom model ID |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Override Sonnet-class model | Custom model ID |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Override Opus-class model | Custom model ID |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents/teammates | Custom model ID |
| `CLAUDE_CODE_EFFORT_LEVEL` | Reasoning effort (Opus 4.6, Sonnet 4.6) | `low`, `medium`, `high` |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | Disable adaptive reasoning | `1` |

All variables can also be set in `settings.json` under the `env` key. ([source][cc-settings])

<!-- markdownlint-enable MD013 -->

## API Key & Endpoint

<!-- markdownlint-disable MD013 -->

| Variable | Purpose | Example |
| -------- | ------- | ------- |
| `ANTHROPIC_API_KEY` | API key (sent as `X-Api-Key` header) | `sk-ant-...` |
| `ANTHROPIC_AUTH_TOKEN` | Custom `Authorization` header value (auto-prefixed with `Bearer `) | OpenRouter key |
| `ANTHROPIC_BASE_URL` | Override API endpoint | `https://openrouter.ai/api` |
| `ANTHROPIC_CUSTOM_HEADERS` | Extra headers (newline-separated `Name: Value`) | Custom routing headers |

<!-- markdownlint-enable MD013 -->

## Provider Configuration

### Anthropic API (default)

No extra config needed. Set `ANTHROPIC_API_KEY` or use `/login`. ([source][cc-settings])

### OpenRouter

Routes requests through OpenRouter for provider failover, budget controls, and usage analytics. OpenRouter implements an "Anthropic Skin" compatible with the Messages API — no local proxy needed. ([source][openrouter])

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="<openrouter-api-key>"
export ANTHROPIC_API_KEY=""  # must be explicitly empty
```

Or in `.claude/settings.local.json` (project-level, git-ignored):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_AUTH_TOKEN": "<openrouter-api-key>",
    "ANTHROPIC_API_KEY": ""
  }
}
```

**Key caveats** ([source][openrouter]):

- CC compatibility guaranteed only with Anthropic first-party provider on OpenRouter
- Run `/logout` first to clear existing Anthropic credentials
- Standard `.env` files are NOT read by CC — use shell profile or `settings.local.json`
- Prompts not logged unless explicitly enabled in OpenRouter account settings

**Benefits**: Provider failover during Anthropic outages, centralized team budget controls, real-time cost monitoring via Activity Dashboard. ([source][openrouter])

### AWS Bedrock

```bash
export CLAUDE_CODE_USE_BEDROCK=true
# Optional: export AWS_BEARER_TOKEN_BEDROCK="<api-key>"
# For LLM gateways: export CLAUDE_CODE_SKIP_BEDROCK_AUTH=true
```

([source][cc-settings])

### Google Vertex AI

```bash
export CLAUDE_CODE_USE_VERTEX=true
# For LLM gateways: export CLAUDE_CODE_SKIP_VERTEX_AUTH=true
```

([source][cc-settings])

### Microsoft Azure Foundry

```bash
export CLAUDE_CODE_USE_FOUNDRY=true
export ANTHROPIC_FOUNDRY_BASE_URL="https://my-resource.services.ai.azure.com/anthropic"
# Or: export ANTHROPIC_FOUNDRY_RESOURCE="my-resource"
# Optional: export ANTHROPIC_FOUNDRY_API_KEY="<api-key>"
# For LLM gateways: export CLAUDE_CODE_SKIP_FOUNDRY_AUTH=true
```

([source][cc-settings])

### LLM Gateway Notes

When routing through third-party gateways, additionally set ([source][cc-settings]):

- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` — disable Anthropic-specific `anthropic-beta` headers
- `CLAUDE_CODE_SKIP_*_AUTH=true` — skip native provider auth (Bedrock/Vertex/Foundry)

## Output & Context Tuning

<!-- markdownlint-disable MD013 -->

| Variable | Purpose | Default |
| -------- | ------- | ------- |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens | 32,000 (max 64,000) |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | Token limit for file reads | Default |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Disable 1M context window (see [extended context analysis](CC-extended-context-analysis.md)) | `1` to disable |

([source][cc-settings])

<!-- markdownlint-enable MD013 -->

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Aspect | Fit | Rationale |
| ------ | --- | --------- |
| Model override for Ralph (`ANTHROPIC_MODEL`) | Strong | Ralph's `RALPH_MODEL` maps to CC model; direct env var control per run |
| Subagent model (`CLAUDE_CODE_SUBAGENT_MODEL`) | Strong | Control cost by routing teammates/subagents to cheaper models |
| OpenRouter for failover | Moderate | Useful if Anthropic API has availability issues during long Ralph runs |
| OpenRouter for budget controls | Moderate | Team cost management for shared CC usage |
| Bedrock/Vertex/Foundry | Weak | Not currently using cloud provider APIs for CC |
| Effort level tuning | Strong | `CLAUDE_CODE_EFFORT_LEVEL=medium` for routine tasks saves tokens |

<!-- markdownlint-enable MD013 -->

### Decision Rule

**Model and effort variables are immediately useful** for optimizing Ralph runs (cost vs quality trade-offs). OpenRouter is a Tier 2 research spike if Anthropic API reliability becomes an issue or team budget controls are needed. Cloud providers (Bedrock/Vertex/Foundry) are not relevant until the project runs on cloud infrastructure.

## References

- [CC Settings — Environment Variables][cc-settings]
- [OpenRouter — Claude Code Integration][openrouter]

[cc-settings]: https://code.claude.com/docs/en/settings#environment-variables
[openrouter]: https://openrouter.ai/docs/guides/guides/coding-agents/claude-code-integration
