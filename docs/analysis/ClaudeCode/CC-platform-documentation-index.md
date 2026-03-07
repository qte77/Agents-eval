---
title: Claude Platform Documentation Index (llms.txt) Analysis
source: https://platform.claude.com/llms.txt
purpose: Catalog of Anthropic's developer documentation surface area for reference when researching API capabilities, Agent SDK features, and CC integration patterns.
created: 2026-03-07
---

**Status**: Stable (651 English pages; 11 language versions)

## What llms.txt Is

A structured index file at `platform.claude.com/llms.txt` listing all Anthropic developer documentation URLs ([source][llms-txt]). Designed for LLM consumption — provides a machine-readable map of the documentation surface. Full content available at `platform.claude.com/llms-full.txt` ([source][llms-full]).

### Documentation Surface Area

| Section | Pages | Key Topics |
| ------- | ----- | ---------- |
| Getting Started | 3 | Intro, quickstart, features overview |
| Models | 5 | Overview, selection guide, Claude 4.6 changes, migration, deprecations |
| Core API | 4 | Messages API, streaming, token counting, stop reasons |
| Prompt Engineering | 3 | Overview, best practices, console tools |
| Vision & Multimodal | 3 | Vision, PDF support, Files API |
| Reasoning | 2 | Extended thinking, adaptive thinking |
| Output & Structured Data | 2 | Structured outputs, citations |
| Performance & Cost | 5 | Batch processing, prompt caching, compaction, fast mode, latency |
| Tool Use | 10 | Overview, implementation, bash, code execution, computer use, memory, text editor, search |
| Agent SDK | 20+ | Overview, Python/TypeScript SDKs, custom tools, MCP, plugins, skills, hooks, sessions |
| Agent Skills | 4 | Overview, quickstart, best practices, enterprise |
| MCP | 2 | MCP connector, remote MCP servers |
| Quality & Safety | 7 | Evals, hallucinations, consistency, jailbreaks, prompt leak, refusals |
| Admin & Data | 6 | Data residency, ZDR, admin API, usage/cost API, CC analytics, workspaces |
| API Reference | 40+ | Messages, batches, completions, models, files, skills, admin |
| Client SDKs | 9 | Python, TypeScript, C#, Go, Java, PHP, Ruby, OpenAI compat |

### Key URLs for This Project

<!-- markdownlint-disable MD013 -->

| Category | URL | Why It Matters |
| -------- | --- | -------------- |
| Agent SDK Overview | `platform.claude.com/docs/en/agent-sdk/overview` | Foundation for understanding CC internals and Agent SDK as alternative |
| Agent SDK Plugins | `platform.claude.com/docs/en/agent-sdk/plugins` | Plugin architecture for portable agent bundles |
| Agent SDK Skills | `platform.claude.com/docs/en/agent-sdk/skills` | Skills API for programmatic skill management |
| Agent SDK Subagents | `platform.claude.com/docs/en/agent-sdk/subagents` | Subagent architecture reference |
| Agent SDK Hooks | `platform.claude.com/docs/en/agent-sdk/hooks` | Hook system for execution control |
| Agent SDK Cost Tracking | `platform.claude.com/docs/en/agent-sdk/cost-tracking` | Cost/usage monitoring patterns |
| Agent SDK CC Features | `platform.claude.com/docs/en/agent-sdk/claude-code-features` | CC-specific SDK features |
| Fast Mode | `platform.claude.com/docs/en/build-with-claude/fast-mode` | API-level fast mode (complements CC fast mode) |
| Batch Processing | `platform.claude.com/docs/en/build-with-claude/batch-processing` | 50% cost reduction for async workloads |
| Structured Outputs | `platform.claude.com/docs/en/build-with-claude/structured-outputs` | JSON schema enforcement (relevant to PydanticAI integration) |
| CC Analytics API | `platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api` | Programmatic CC usage data |
| Eval Tool | `platform.claude.com/docs/en/test-and-evaluate/eval-tool` | Anthropic's evaluation tooling |

<!-- markdownlint-enable MD013 -->

### Multi-Language SDK Coverage

API endpoints available in 10 languages: CLI, C#, Go, Java, Kotlin, PHP, Python, Ruby, Terraform, TypeScript ([source][llms-txt]).

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Documentation Area | Fit | Rationale |
| ------------------ | --- | --------- |
| Agent SDK | Strong | Alternative/complement to PydanticAI for agent orchestration; understanding CC internals |
| Batch Processing | Strong | 50% cost reduction for evaluation runs — could batch tier 2 LLM judge calls |
| CC Analytics API | Strong | Programmatic cost/usage data for CC baseline evaluation |
| Structured Outputs | Moderate | Already using PydanticAI structured outputs; API-level reference useful for debugging |
| Eval Tool | Moderate | Anthropic's eval approach — compare with our three-tier pipeline |
| Skills API | Moderate | Programmatic skill management if adopting Cowork plugins |
| Fast Mode (API) | Weak | Already analyzed in CC-fast-mode-analysis.md; API-level doc adds detail |
| Admin API | Weak | Enterprise administration — not relevant for research project |

<!-- markdownlint-enable MD013 -->

### Decision Rule

**Use llms.txt as a reference index when researching specific Anthropic API capabilities. Most immediately actionable: Batch Processing for cost reduction, CC Analytics API for evaluation data, Agent SDK for understanding CC architecture.**

### Priority Research Queue

1. **Batch Processing** — Evaluate for tier 2 LLM judge calls (50% cost savings)
2. **CC Analytics API** — Programmatic alternative to manual cost tracking
3. **Agent SDK Subagents** — Compare with PydanticAI delegation patterns
4. **Eval Tool** — Compare Anthropic's evaluation approach with our three-tier pipeline

**Recommendation**: Bookmark `platform.claude.com/llms.txt` as the canonical reference index. Use `llms-full.txt` for comprehensive content when Context7 MCP is unavailable. Prioritize researching Batch Processing and CC Analytics API for immediate cost/data benefits.

## References

- [Platform llms.txt][llms-txt]
- [Platform llms-full.txt][llms-full]
- [CC Documentation Index][cc-llms]

[llms-txt]: https://platform.claude.com/llms.txt
[llms-full]: https://platform.claude.com/llms-full.txt
[cc-llms]: https://code.claude.com/docs/llms.txt
