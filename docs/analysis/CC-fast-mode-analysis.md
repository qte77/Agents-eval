---
title: CC Fast Mode Analysis
source: https://code.claude.com/docs/en/fast-mode
purpose: Analysis of Claude Code Fast Mode for potential adoption within Agents-eval workflows.
created: 2026-02-17
---

**Status**: Research preview (pricing and availability may change)

## What Fast Mode Is

A high-speed API configuration for Opus 4.6 — **same model, same quality, 2.5x faster output tokens**. Toggle with `/fast` in CLI or VS Code. Not a different model or reduced reasoning — purely an infrastructure-level latency optimization at higher per-token cost.

### Pricing

<!-- markdownlint-disable MD013 -->

| Mode | Input (MTok) | Output (MTok) |
| ---- | ------------ | ------------- |
| Fast mode Opus 4.6 (<200K context) | $30 | $150 |
| Fast mode Opus 4.6 (>200K context) | $60 | $225 |
| Standard Opus 4.6 | Lower | Lower |

<!-- markdownlint-enable MD013 -->

Compatible with the 1M token extended context window.

### Configuration

```json
{ "fastMode": true }
```

Or toggle per-session: `/fast` (persists across sessions). CLI flag: `--fast`.

### Key Mechanics

- Enabling mid-conversation pays full uncached input price for entire context (enable at session start for cost efficiency)
- Separate rate limits from standard Opus 4.6; auto-fallback to standard on limit hit
- Extra usage only — not included in subscription rate limits
- Not available on Bedrock, Vertex AI, or Azure Foundry
- Teams/Enterprise: admin must explicitly enable

### Fast Mode vs Effort Level

| Setting | Effect |
| ------- | ------ |
| Fast mode | Same quality, lower latency, higher cost |
| Lower effort | Less thinking, faster, potentially lower quality on complex tasks |

Combinable: fast mode + lower effort for maximum speed on simple tasks.

## Relevance to This Project

| Workflow | Fit | Rationale |
| -------- | --- | --------- |
| Interactive development (debugging, iteration) | Strong | Latency reduction directly improves developer flow |
| Ralph loop (`claude -p`) | Weak | Autonomous execution — developer not waiting; cost matters more |
| Ralph teams mode (`TEAMS=true`) | Weak | Same as above; parallel stories multiply the cost further |
| Writeup generation (`make writeup`) | Weak | Batch/autonomous; no interactive waiting |
| CC baseline collection (`cc_run_solo`, `cc_run_teams`) | Neutral | Faster collection but 2x+ cost; only worth it under time pressure |

### Decision Rule

**Enable fast mode for interactive sessions where latency breaks flow. Disable for autonomous/headless invocations (`claude -p`) where cost efficiency matters.**

### Potential Integration

If adopted, fast mode could be passed through Makefile recipes:

```makefile
# Example (NOT implemented — YAGNI until measured need)
FAST_MODE ?= false
ralph_run:
    $(if $(filter true,$(FAST_MODE)),--fast)
```

**Recommendation**: Do not integrate yet. Fast mode is a research preview with unstable pricing. The project's primary CC usage (`claude -p` in Ralph and baselines) is autonomous — the 2.5x speed gain doesn't justify 2x+ cost increase when no human is waiting. Revisit if:

1. Pricing stabilizes and drops
2. Ralph loop becomes interactive (unlikely by design)
3. Time-boxed evaluation runs need faster turnaround

## References

- [CC Fast Mode docs][cc-fast]
- [CC Model Configuration][cc-model]
- [CC Cost Management][cc-costs]

[cc-fast]: https://code.claude.com/docs/en/fast-mode
[cc-model]: https://code.claude.com/docs/en/model-config
[cc-costs]: https://code.claude.com/docs/en/costs
