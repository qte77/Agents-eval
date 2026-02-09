---
title: Production Agent Patterns - Gap Analysis
description: Gap analysis of PydanticAI and Anthropic production patterns against our evaluation pipeline
created: 2026-02-09
category: analysis
version: 1.0.0
---

Gap analysis of three production agentic system sources against
our evaluation pipeline, with scope decisions for Sprint 2+.

## Sources

1. [Building Agentic Applications](https://pydantic.dev/articles/building-agentic-application)
   (PydanticAI)
2. [The Logs I Never Read](https://pydantic.dev/articles/the-logs-i-never-read)
   (Pydantic/Logfire)
3. [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
   (Anthropic)

## Gap Matrix

| Principle | Source | Status | Decision |
| --- | --- | --- | --- |
| Framework-based approach | PydanticAI | ✅ Done | PydanticAI stays |
| Type-safe structured outputs | PydanticAI | ✅ Done | Enhance via plugin |
| Layered deployment | PydanticAI | ⚠️ CLI only | Sprint 2: FastAPI+MCP |
| VCR-based testing | PydanticAI | ❌ Missing | Deferred: @patch ok |
| Model settings for determinism | PydanticAI | ⚠️ Partial | Sprint 2: expose |
| Structured queryable logs | Logfire | ⚠️ loguru | Opik primary |
| AI-queryable observability | Logfire | ❌ Missing | Sprint 3: MCP |
| Incremental boundaries | Anthropic | ✅ Done | Ralph loop |
| State management | Anthropic | ✅ Done | prd.json + git |
| Checkpointing | Anthropic | ✅ Done | Git commits |
| Error recovery | Anthropic | ✅ Done | git revert |
| Human-in-the-loop | Anthropic | ✅ Done | Ralph approval |

## Scope Decisions

### Sprint 2: FastAPI + MCP (Feature 10)

Multi-channel access prevents rearchitecture later:

- **CLI** - Developer-facing (exists)
- **Streamlit UI** - Interactive exploration (exists, no redesign)
- **FastAPI REST** - CI/CD integration (new)
- **MCP Server** - AI-to-AI workflows (new)

### Opik Primary, Logfire Optional

Opik already covers agent tracing, LLM tracking, cost monitoring,
evaluation metrics. Logfire adds incremental value (app-level logs,
HTTP tracing) but creates hard dependency on Pydantic ecosystem.
Keep optional/fallback.

### Deferred: VCR + Browser E2E

**VCR**: @patch mocking works for current test suite. VCR adds
dependency without proportional benefit.

**Browser E2E**: Streamlit UI is secondary interface. API E2E tests
via pytest + httpx provide sufficient coverage. Playwright/Selenium
deferred to Sprint 4+.

## Sprint 3+ Candidates

| Priority | Feature | Prerequisite |
| --- | --- | --- |
| High | Container-based deployment | Feature 10 (FastAPI) stable |
| Medium | MCP observability server | Opik trace API access |
| Medium | Logfire integration | Optional, alongside Opik |
| Low | VCR testing | None |
| Low | Browser E2E tests | Streamlit UI importance increases |

## Key Findings

1. **Ralph loop already matches Anthropic best practices** - documented
   in `ralph/README.md`
2. **Deployment flexibility is the primary gap** - addressed by
   Feature 10 (FastAPI + MCP)
3. **Observability is sufficient** - Opik covers needs; Logfire is
   incremental
4. **Testing is appropriate** - E2E integration tests (not browser)
   added to Sprint 2
