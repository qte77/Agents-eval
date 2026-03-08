---
title: CC Feature Adoption Plan
purpose: Consolidated adoption plan synthesizing all CC feature research into prioritized, actionable items for the Agents-eval project.
created: 2026-03-07
---

## Summary

This plan synthesizes CC feature analysis documents into a prioritized adoption roadmap. Each item is grounded in a specific analysis doc, has a clear trigger condition, and maps to a concrete project workflow.

**Principle**: Adopt only what solves a real measured problem. Research is informational; adoption requires validation against PRD.md scope ([AGENTS.md](../../../AGENTS.md)).

## Adoption Tiers

### Tier 1 — Adopt Now (zero cost, immediate value)

<!-- markdownlint-disable MD013 -->

- [ ] **Remote Control for Ralph monitoring**: Run `claude remote-control --name "Ralph"` before interactive sessions. [CC-remote-control-analysis.md](CC-remote-control-analysis.md)
- [ ] **Path-scoped rules**: Add `paths:` frontmatter to `.claude/rules/` files. [CC-memory-system-analysis.md](CC-memory-system-analysis.md)
- [ ] **Auto memory / AGENT_LEARNINGS.md dedup**: Run `/memory` audit; reconcile stale entries. [CC-memory-system-analysis.md](CC-memory-system-analysis.md)
- [ ] **llms.txt bookmark**: Add `platform.claude.com/llms.txt` and `code.claude.com/docs/llms.txt` as reference indexes. [CC-llms-txt-analysis.md](CC-llms-txt-analysis.md)
- [ ] **Fix `ralph_status` recipe**: Change `.passes == true` to `.status == "passed"` in Makefile. [CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md)
- [ ] **Disable git instructions for Ralph**: Set `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` in Ralph's env. [CC-changelog-feature-scan.md](CC-changelog-feature-scan.md)
- [ ] **`Setup` hook for env validation**: Add `Setup` hook event to auto-run `make setup_dev` on session start. [CC-changelog-feature-scan.md](CC-changelog-feature-scan.md)
- [ ] **Effort level tuning**: Set `CLAUDE_CODE_EFFORT_LEVEL=medium` for routine tasks; `high` for complex work. [CC-model-provider-configuration.md](CC-model-provider-configuration.md)
- [ ] **Subagent model override**: Set `CLAUDE_CODE_SUBAGENT_MODEL` to route subagents to cheaper models. [CC-model-provider-configuration.md](CC-model-provider-configuration.md)

#### Tier 1 — Done

- [x] **Apply AGENTS.md refactor plan**: 3 direct edits applied. Refactor plan deleted. [CC-plugin-packaging-research.md](CC-plugin-packaging-research.md)
- [x] **Fix AGENTS.md Ralph path**: Updated `.claude/scripts/ralph/` → `ralph/scripts/` and state tracking paths. [CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md)

<!-- markdownlint-enable MD013 -->

### Tier 2 — Research Spike (high potential, needs validation)

<!-- markdownlint-disable MD013 -->

| Item | Action | Effort | Trigger | Source |
| ---- | ------ | ------ | ------- | ------ |
| **Batch Processing API** | Evaluate `platform.claude.com/docs/en/build-with-claude/batch-processing` for tier 2 LLM judge calls. Run one eval batch, measure cost vs current approach | 2-4 hrs spike | Next eval run where cost is a concern | [CC-llms-txt-analysis.md](CC-llms-txt-analysis.md) |
| **CC Analytics API** | Evaluate `platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api` for programmatic cost tracking of CC baseline runs | 2-4 hrs spike | Manual cost tracking becomes tedious | [CC-llms-txt-analysis.md](CC-llms-txt-analysis.md) |
| **Cloud Sessions for parallel baselines** | Test `claude --remote "prompt"` for running N baseline tasks in parallel on cloud VMs | 4 hrs spike | Local machine can't handle parallel CC runs | [CC-cloud-sessions-analysis.md](CC-cloud-sessions-analysis.md) |
| **Structured outputs for `-p` mode** | Evaluate structured output schemas for Ralph's `claude -p` invocations — enforce story result schema (pass/fail/error + commit hashes) | 2 hrs spike | Ralph output parsing is brittle or needs schema validation | [CC-changelog-feature-scan.md](CC-changelog-feature-scan.md) |
| **`/loop` command for monitoring** | Test `/loop 5m make ralph_status` for periodic monitoring during interactive sessions | 1 hr spike | Next interactive Ralph session | [CC-changelog-feature-scan.md](CC-changelog-feature-scan.md) |
| **HTTP hooks for status notifications** | Evaluate HTTP hooks to push Ralph status events (story pass/fail) to Slack or dashboard | 2 hrs spike | Manual monitoring becomes tedious | [CC-changelog-feature-scan.md](CC-changelog-feature-scan.md) |
| **OpenRouter for failover + budget** | Route CC through OpenRouter for provider failover and team budget controls. Set `ANTHROPIC_BASE_URL=https://openrouter.ai/api` | 2 hrs spike | Anthropic API reliability issues or team cost management needed | [CC-model-provider-configuration.md](CC-model-provider-configuration.md) |

<!-- markdownlint-enable MD013 -->

### Tier 3 — Monitor (not yet actionable, revisit on trigger)

<!-- markdownlint-disable MD013 -->

| Item | Current Blocker | Trigger to Revisit | Source |
| ---- | --------------- | ------------------ | ------ |
| **Fast mode for Ralph loop** | 2x+ cost increase; autonomous execution doesn't benefit from latency reduction | Pricing drops or Ralph becomes interactive | [CC-fast-mode-analysis.md](CC-fast-mode-analysis.md) |
| **Omnara cloud sandbox failover** | Startup risk (pivoted once); no E2E encryption; CC Remote Control may be sufficient | Ralph runs regularly stall because laptop sleeps — measured, not assumed | [CC-remote-access-landscape.md](CC-remote-access-landscape.md) |
| **Cloud Sessions for Ralph loop** | No local MCP servers or persistent state in cloud VMs; setup script complexity | Cloud sessions support custom images or MCP forwarding | [CC-cloud-sessions-analysis.md](CC-cloud-sessions-analysis.md) |
| **Cowork Plugins for eval distribution** | Enterprise deployment feature; no team consumers yet | Eval framework needs distribution to non-developer stakeholders | [CC-cowork-plugins-enterprise-analysis.md](CC-cowork-plugins-enterprise-analysis.md) |
| **Agent Teams as core infra** | No session resumption; task status lag; no nested teams; experimental | Limitations resolved upstream; reliability proven over multiple sprints | [CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md) |
| **Agent SDK as PydanticAI alternative** | Working PydanticAI MAS with Logfire/Phoenix observability already in place | PydanticAI becomes a bottleneck or Agent SDK offers unique capabilities | [CC-llms-txt-analysis.md](CC-llms-txt-analysis.md) |
| **Chrome extension for browser automation** | Project is API/CLI-driven; no browser interaction surface | Evaluation workflows require web UI interaction | [CC-chrome-extension-analysis.md](CC-chrome-extension-analysis.md) |

<!-- markdownlint-enable MD013 -->

## Path-Scoped Rules Implementation

Highest ROI Tier 1 item. Current state: 2 rules files, both loaded unconditionally every session.

**Proposed changes:**

```markdown
# .claude/rules/context-management.md (keep unconditional — applies everywhere)
# No changes needed
```

```markdown
# .claude/rules/core-principles.md (keep unconditional — applies everywhere)
# No changes needed
```

```markdown
# .claude/rules/agent-patterns.md (NEW — path-scoped)
---
paths:
  - "src/app/agents/**/*.py"
  - ".claude/agents/*.md"
  - ".claude/skills/**/*.md"
---
# Agent Implementation Rules
- Use PydanticAI agent patterns from agent_system.py
- Follow delegation chain: Manager → Researcher → Analyst → Synthesizer
- Use Pydantic models from data_models/ for all agent I/O
```

```markdown
# .claude/rules/testing.md (NEW — path-scoped)
---
paths:
  - "tests/**/*.py"
---
# Testing Rules
- Mock external dependencies (HTTP, file systems, APIs)
- Use pytest with arrange/act/assert structure
- Mirror src/app/ structure in tests/
- Use tmp_path for filesystem isolation
```

## Decision Log

| Decision | Rationale | Date |
| -------- | --------- | ---- |
| Adopt CC Remote Control over Omnara/CloudCLI | Free, native, zero-setup; sufficient for monitoring. Omnara adds complexity and security risk for a feature gap (offline continuation) that hasn't been measured as a real problem | 2026-03-07 |
| Skip fast mode for autonomous runs | 2.5x speed doesn't justify 2x+ cost when no human is waiting ([CC-fast-mode-analysis.md](CC-fast-mode-analysis.md)) | 2026-03-07 |
| Keep Skills over Plugins | Project is developer-local; Plugins are for enterprise distribution. Skills already provide modular capability pattern needed ([CC-cowork-plugins-enterprise-analysis.md](CC-cowork-plugins-enterprise-analysis.md)) | 2026-03-07 |
| Agent Teams for reviews only, not core infra | Useful for parallel code reviews and competing hypotheses. Too unreliable (no resumption, task lag) for replacing Ralph loop or subagent architecture ([CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md)) | 2026-03-07 |
| OTel supplementary, artifacts primary for CC eval | CC OTel exports metrics/logs only — no trace spans (upstream limitation). Artifact collection via `CCTraceAdapter` is primary for evaluation ([CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md)) | 2026-03-07 |
| Batch Processing API as priority research | 50% cost reduction on async workloads directly applicable to tier 2 LLM judge calls ([CC-llms-txt-analysis.md](CC-llms-txt-analysis.md)) | 2026-03-07 |
| Apply AGENTS.md refactor as direct edits, not plugin | Project-specific rules stay repo-local; plugin packaging is YAGNI until cross-project reuse demand exists ([CC-plugin-packaging-research.md](CC-plugin-packaging-research.md)) | 2026-03-07 |
| Fix `ralph_status` + AGENTS.md path ref | Broken functionality — `ralph_status` uses legacy `.passes` field; AGENTS.md references wrong path ([CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md)) | 2026-03-07 |
| Skip Chrome extension | Browser automation for web-based knowledge work; project is API/CLI-driven with no browser interaction ([CC-chrome-extension-analysis.md](CC-chrome-extension-analysis.md)) | 2026-03-07 |

## Source Documents

| Document | Topic | Status |
| -------- | ----- | ------ |
| [CC-fast-mode-analysis.md](CC-fast-mode-analysis.md) | Fast mode pricing, mechanics, fit | Tier 3 — monitor |
| [CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md) | Agent Teams, OTel, observability | Partial adopt (reviews) |
| [CC-skills-adoption-analysis.md](CC-skills-adoption-analysis.md) | Skills adoption and format analysis | Completed |
| [CC-remote-control-analysis.md](CC-remote-control-analysis.md) | Remote Control mechanics, fit | Tier 1 — adopt now |
| [CC-cloud-sessions-analysis.md](CC-cloud-sessions-analysis.md) | Cloud sessions, setup scripts, network | Tier 2/3 — research spike |
| [CC-memory-system-analysis.md](CC-memory-system-analysis.md) | CLAUDE.md, auto memory, rules | Tier 1 — optimize |
| [CC-cowork-plugins-enterprise-analysis.md](CC-cowork-plugins-enterprise-analysis.md) | Cowork, plugins, enterprise | Tier 3 — monitor |
| [CC-llms-txt-analysis.md](CC-llms-txt-analysis.md) | Platform docs surface area | Tier 1 (ref) + Tier 2 (batch/analytics) |
| [CC-remote-access-landscape.md](CC-remote-access-landscape.md) | Omnara, CloudCLI, DIY alternatives | Tier 3 — monitor |
| [CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md) | Ralph loop gaps, external patterns, enhancements | Tier 1 (bugs) + Tier 2 (robustness) |
| [CC-plugin-packaging-research.md](CC-plugin-packaging-research.md) | Plugin packaging vs repo-local, AGENTS.md refactor | Tier 1 (direct edit) + Tier 3 (plugin) |
| [CC-chrome-extension-analysis.md](CC-chrome-extension-analysis.md) | Chrome browser automation extension | Tier 3 — monitor |
| [CC-changelog-feature-scan.md](CC-changelog-feature-scan.md) | Changelog scan (v2.1.0–2.1.71) | Tier 1 + Tier 2 |
| [CC-model-provider-configuration.md](CC-model-provider-configuration.md) | Model, endpoint, API key, provider config | Tier 1 (effort/subagent) + Tier 2 (OpenRouter) |
| [CC-sandboxing-analysis.md](CC-sandboxing-analysis.md) | Sandboxing, security model, project config | Adopted (enabled) |
| [CC-llms-txt-analysis.md](CC-llms-txt-analysis.md) | llms.txt spec, Anthropic implementations, project template | Adopted (workflows) |

Ralph-specific bugs, enhancements, and deferred items also tracked in [ralph/TODO.md](../../../ralph/TODO.md).
