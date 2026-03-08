---
title: CC Extended Context Window (1M) Analysis
source: https://code.claude.com/docs/en/model-config#extended-context
purpose: Analysis of 1M token extended context window for cost planning and Ralph loop usage.
created: 2026-03-07
---

**Status**: Beta (features, pricing, and availability may change)

## What It Is

Opus 4.6 and Sonnet 4.6 support a 1 million token context window, up from
the standard 200K. This enables long sessions with large codebases without
hitting context limits or triggering auto-compaction.

## Availability

<!-- markdownlint-disable MD013 -->

| Account Type | 1M Access | Billing |
| ------------ | --------- | ------- |
| API / pay-as-you-go | Full access | Long-context pricing above 200K |
| Pro, Max, Teams, Enterprise | Requires [extra usage](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) enabled | Tokens above 200K billed as extra usage |

<!-- markdownlint-enable MD013 -->

## Pricing Model

Selecting a 1M model does **not** immediately change billing. The session
uses standard rates until context exceeds 200K tokens. Beyond 200K:

- Requests charged at
  [long-context pricing](https://platform.claude.com/docs/en/about-claude/pricing#long-context-pricing)
- Dedicated
  [rate limits](https://platform.claude.com/docs/en/api/rate-limits#long-context-rate-limits)
  apply
- For subscribers, billed as extra usage (not subscription)

### Interaction with Fast Mode

Fast mode pricing splits at the same 200K boundary — see pricing table in
[CC-fast-mode-analysis.md](CC-fast-mode-analysis.md#pricing). The 1M window
extends the upper-tier pricing zone from 200K to 1M tokens. Fast mode is
compatible with the full 1M context (confirmed v2.1.50).

## Configuration

### Enable

The 1M option appears in `/model` picker if the account supports it. Use
the `[1m]` suffix with model aliases or full model names:

```bash
# Alias
/model sonnet[1m]

# Full model name
/model claude-sonnet-4-6[1m]
```

The `sonnet[1m]` alias is a top-level model alias in CC.

### Disable

```bash
CLAUDE_CODE_DISABLE_1M_CONTEXT=1
```

Removes 1M model variants from the model picker entirely. Set in
`settings.json` env section or shell environment.

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Workflow | Fit | Rationale |
| -------- | --- | --------- |
| Interactive development | Strong | Large codebase exploration without compaction; avoids context rot mid-session |
| Ralph loop (`claude -p`) | Weak | Each story starts fresh with clean context; rarely approaches 200K. Extra cost unjustified. |
| Ralph teams mode | Weak | Each teammate has its own context window; same fresh-start pattern as solo mode |
| CC baseline collection | Neutral | Longer runs may benefit, but cost scales with context; only if evaluation requires deep multi-file analysis in a single pass |
| Code review sessions | Medium | Multi-file reviews with large diffs can benefit from sustained context |

<!-- markdownlint-enable MD013 -->

### Decision Rule

**Use 1M context for interactive sessions exploring large codebases or
reviewing large diffs. Avoid for autonomous/headless invocations where
fresh context per iteration is the design pattern.**

### Cost Awareness

The 200K threshold is the key cost boundary. Monitor context usage via
`/cost` or the status line (`context_window.used/remaining_percentage`).
For Ralph runs, `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` prevents accidental
long-context charges.

## References

- [CC Model Configuration — Extended context](https://code.claude.com/docs/en/model-config#extended-context)
- [CC Costs](https://code.claude.com/docs/en/costs)
- [Long-context pricing](https://platform.claude.com/docs/en/about-claude/pricing#long-context-pricing)
- [Long-context rate limits](https://platform.claude.com/docs/en/api/rate-limits#long-context-rate-limits)
- [CC-fast-mode-analysis.md](CC-fast-mode-analysis.md) — fast mode pricing tiers
- [CC-model-provider-configuration.md](CC-model-provider-configuration.md) — model env vars
