---
title: Product Requirements Document: Agents-eval Sprint 3
version: 3.4.0
created: 2026-02-15
updated: 2026-02-15
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 3 restructures the evaluation pipeline into a plugin architecture (`EvaluatorPlugin` + `PluginRegistry` → `JudgeAgent`), adds model-aware content truncation for provider rate limits, and introduces a standalone CC OTel observability plugin. All Sprint 2 features (settings migration, eval wiring, trace capture, graph-vs-text comparison, Logfire+Phoenix tracing, Streamlit dashboard) are prerequisites.

---

## Functional Requirements

### Sprint 3: Plugin Architecture and Infrastructure

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 5: Model-Aware Content Truncation

**Description**: Implement token-limit-aware content truncation to prevent 413 errors when paper content exceeds provider rate limits (e.g., GitHub Models free tier enforces 8,000 token request limit for `gpt-4.1`, despite the model supporting 1M tokens natively).

**Acceptance Criteria**:

- [ ] `CommonSettings` includes per-provider `max_content_length` defaults
- [ ] `generate_paper_review_content_from_template` truncates `paper_content_for_template` to `max_content_length` before formatting into template
- [ ] Truncation preserves abstract (always included) and truncates body with `[TRUNCATED]` marker
- [ ] Warning logged when truncation occurs with original vs truncated size
- [ ] `make validate` passes

**Technical Requirements**:

- Add per-provider max_content_length to `CommonSettings`
- Truncation logic in `generate_paper_review_content_from_template`
- Preserve abstract section, truncate body content

**Files**:

- `src/app/agents/peerread_tools.py`
- `src/app/common/settings.py`

---

#### Feature 6: EvaluatorPlugin Base and Registry

**Description**: Create `EvaluatorPlugin` ABC and `PluginRegistry` for typed, tier-ordered plugin execution.

**Acceptance Criteria**:

- [ ] `EvaluatorPlugin` ABC with name/tier/evaluate/get_context_for_next_tier
- [ ] `PluginRegistry` for registration and tier-ordered execution
- [ ] Typed Pydantic models at all plugin boundaries
- [ ] Structured error results from plugins

**Technical Requirements**:

- ABC defines plugin interface: `name`, `tier`, `evaluate()`, `get_context_for_next_tier()`
- Registry manages plugin lifecycle and tier-ordered execution
- All data contracts use Pydantic models

**Files**:

- `src/app/judge/plugins/base.py`
- `src/app/judge/plugins/__init__.py`

---

#### Feature 7: TraditionalMetricsPlugin Wrapper

**Description**: Wrap existing `TraditionalMetricsEngine` as an `EvaluatorPlugin`.

**Acceptance Criteria**:

- [ ] TraditionalMetricsPlugin wrapping existing engine
- [ ] All existing Tier 1 engine tests pass unchanged
- [ ] Per-plugin configurable timeout

**Technical Requirements**:

- Adapter pattern: delegate to existing `TraditionalMetricsEngine`
- Expose via `EvaluatorPlugin` interface
- Configurable timeout from `JudgeSettings`

**Files**:

- `src/app/judge/plugins/traditional.py`

---

#### Feature 8: LLMJudgePlugin Wrapper

**Description**: Wrap existing `LLMJudgeEngine` as an `EvaluatorPlugin` with opt-in Tier 1 context enrichment.

**Acceptance Criteria**:

- [ ] LLMJudgePlugin with opt-in Tier 1 context enrichment
- [ ] All existing Tier 2 engine tests pass unchanged
- [ ] Per-plugin configurable timeout

**Technical Requirements**:

- Adapter pattern: delegate to existing `LLMJudgeEngine`
- Accept optional Tier 1 context via `get_context_for_next_tier()`
- Configurable timeout from `JudgeSettings`

**Files**:

- `src/app/judge/plugins/llm_judge.py`

---

#### Feature 9: GraphEvaluatorPlugin Wrapper

**Description**: Wrap existing `GraphAnalysisEngine` as an `EvaluatorPlugin`.

**Acceptance Criteria**:

- [ ] GraphEvaluatorPlugin wrapping existing engine
- [ ] All existing Tier 3 engine tests pass unchanged
- [ ] Per-plugin configurable timeout

**Technical Requirements**:

- Adapter pattern: delegate to existing `GraphAnalysisEngine`
- Expose via `EvaluatorPlugin` interface
- Configurable timeout from `JudgeSettings`

**Files**:

- `src/app/judge/plugins/graph_metrics.py`

---

#### Feature 10: Plugin-Driven Pipeline

**Description**: Replace `EvaluationPipeline` with `JudgeAgent` using `PluginRegistry` for tier-ordered plugin execution.

**Acceptance Criteria**:

- [ ] JudgeAgent replaces EvaluationPipeline using PluginRegistry
- [ ] Explicit tier execution order in code
- [ ] Context flows Tier 1 → Tier 2 → Tier 3
- [ ] TraceStore with thread-safe storage
- [ ] Graceful degradation preserved
- [ ] Re-export shim for EvaluationPipeline

**Technical Requirements**:

- `JudgeAgent` orchestrates plugins via `PluginRegistry`
- Tier context passed forward via `get_context_for_next_tier()`
- `TraceStore` provides thread-safe trace storage
- Backward-compatible `EvaluationPipeline` re-export shim

**Files**:

- `src/app/judge/agent.py`
- `src/app/judge/trace_store.py`
- `src/app/judge/composite_scorer.py`
- `src/app/judge/performance_monitor.py`

---

#### Feature 11: Migration Cleanup

**Description**: Remove backward-compatibility shims, update all imports, delete deprecated JSON config.

**Acceptance Criteria**:

- [ ] All imports use `judge.`, `common.` paths
- [ ] No re-export shims remain
- [ ] `config/config_eval.json` removed
- [ ] CHANGELOG.md updated
- [ ] `make validate` passes, no dead code

**Technical Requirements**:

- Update all source and test imports from `evals.` to `judge.` paths
- Remove re-export shim from Feature 10
- Delete deprecated `config/config_eval.json`

**Files**: All source and test files (import updates), `CHANGELOG.md`

---

#### Feature 12: CC OTel Observability Plugin

**Description**: Standalone CC telemetry plugin using OTel → Logfire + Phoenix pipeline. Enables CC session tracing alongside PydanticAI Logfire auto-instrumentation.

**Acceptance Criteria**:

- [ ] `src/app/cc_otel/` module with config + enable/disable API
- [ ] `CCOtelConfig` with env var export
- [ ] OTel traces routed to Phoenix via OTLP endpoint
- [ ] Separate from existing `logfire_instrumentation.py`
- [ ] Graceful degradation when OTel unavailable
- [ ] `make validate` passes

**Technical Requirements**:

- Standalone module at `src/app/cc_otel/`
- `CCOtelConfig` using pydantic-settings pattern
- OTLP exporter sends to Phoenix endpoint
- Independent from `logfire_instrumentation.py` (no coupling)

**Files**:

- `src/app/cc_otel/__init__.py`
- `src/app/cc_otel/config.py`
- `Makefile` (phoenix targets)

---

## Non-Functional Requirements

- **Maintainability:**
  - Use modular design patterns for easy updates and maintenance.
  - Implement logging and error handling for debugging and monitoring.
- **Performance:**
  - Ensure low latency in evaluation pipeline execution.
  - Optimize for memory usage during graph analysis.
- **Documentation:**
  - Comprehensive documentation for setup, usage, and testing.
  - Docstrings for all new functions and classes (Google style format).

## Out of Scope

- A2A protocol migration (PydanticAI stays)
- Agent system restructuring (`src/app/agents/` unchanged except trace instrumentation)
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead)
- HuggingFace `datasets` library (use GitHub API downloader instead)
- Google Gemini SDK (`google-genai`) — use OpenAI-spec compatible providers only
- VCR-based network mocking (use @patch for unit tests)
- Browser-based E2E tests (Playwright/Selenium deferred)
- CC-style evaluation baselines (deferred beyond Sprint 3)
- E2E integration tests and multi-channel deployment (deferred beyond Sprint 3)

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Sprint 3 (8 stories total):

- **Feature 5 (Content Truncation)** → STORY-007: Model-aware content truncation
- **Feature 6 (Plugin Base)** → STORY-008: EvaluatorPlugin base and registry (depends: STORY-004)
- **Feature 7 (Traditional Adapter)** → STORY-009: TraditionalMetricsPlugin wrapper (depends: STORY-008)
- **Feature 8 (LLM Judge Adapter)** → STORY-010: LLMJudgePlugin wrapper (depends: STORY-008)
- **Feature 9 (Graph Adapter)** → STORY-011: GraphEvaluatorPlugin wrapper (depends: STORY-008)
- **Feature 10 (Plugin Pipeline)** → STORY-012: JudgeAgent replaces EvaluationPipeline (depends: STORY-009, STORY-010, STORY-011)
- **Feature 11 (Migration Cleanup)** → STORY-013: Remove shims and update imports (depends: STORY-012)
- **Feature 12 (CC OTel)** → STORY-014: CC OTel observability plugin (depends: STORY-012)
