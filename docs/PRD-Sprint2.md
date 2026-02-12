---
title: Product Requirements Document
version: 3.4.0
created: 2025-09-01
updated: 2026-02-12
---

# Product Requirements Document: Agents-eval

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 2 focuses on connecting generation and evaluation: capturing real agent execution graphs, running evaluation automatically after review generation, and producing a comparative summary of graph-based coordination metrics vs conventional text similarity metrics. All evaluation tiers are fully implemented (157 tests); the gap is wiring them into the generation flow with real trace data.

---

## Functional Requirements

### Sprint 2: Graph vs Text Evaluation Pipeline

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Migrate EvaluationConfig to Pydantic Settings

**Description**: Replace JSON-based `EvaluationConfig` (`config_eval.json`) with `JudgeSettings(BaseSettings)` using `JUDGE_` env prefix. Defaults in code, overridable via `.env` or env vars. Follows same pattern as existing `CommonSettings` (`EVAL_` prefix).

**Acceptance Criteria**:

- [ ] `JudgeSettings(BaseSettings)` with `JUDGE_` env prefix replaces `EvaluationConfig`
- [ ] Typed defaults in code: tier weights, timeouts, model selection, enabled tiers
- [ ] `EvaluationPipeline` uses `JudgeSettings` instead of loading `config_eval.json`
- [ ] Existing evaluation tests pass with settings-based config
- [ ] Timeout fields use bounded validators (gt=0, le=300)
- [ ] Time tracking pattern standardized across all tiers
- [ ] Existing test fixtures updated: pipeline uses JudgeSettings, JSON fixtures removed
- [ ] `make validate` passes

**Technical Requirements**:

- Create `src/app/evals/settings.py` with `JudgeSettings(BaseSettings)` (model_config with `JUDGE_` prefix, `.env` file)
- Defaults mirror current `config_eval.json` values (tier1_max_seconds=1.0, tier2_max_seconds=10.0, etc.)
- Update `EvaluationPipeline.__init__()` to accept `JudgeSettings` instead of `config_path`
- Keep `config_eval.json` temporarily but it is no longer loaded at runtime
- Reuse pattern from `src/app/common/settings.py`

**Files**:

- `src/app/evals/settings.py` (new — `JudgeSettings`)
- `src/app/evals/evaluation_config.py` (deprecate, replace usages)
- `src/app/evals/evaluation_pipeline.py` (use `JudgeSettings`)
- `src/app/evals/composite_scorer.py` (use `JudgeSettings` for weights)

---

#### Feature 2: Wire Evaluation After Review Generation

**Description**: Connect `run_manager()` output to `EvaluationPipeline.evaluate_comprehensive()`. Add `--skip-eval` CLI flag.

**Acceptance Criteria**:

- [ ] After `run_manager()` completes, `EvaluationPipeline` runs automatically
- [ ] `--skip-eval` CLI flag disables evaluation
- [ ] Graceful skip when no ground-truth reviews available
- [ ] `make validate` passes

**Technical Requirements**:

- Import `EvaluationPipeline` in `app.py`, call after line 134
- Pipeline uses `JudgeSettings` from Feature 1
- Add `--skip-eval` to `parse_args()` in `run_cli.py`

**Files**:

- `src/app/app.py`
- `src/run_cli.py`

---

#### Feature 3: Capture GraphTraceData During MAS Execution

**Description**: Wire `TraceCollector` into agent orchestration so `GraphTraceData` is populated from real agent runs.

**Acceptance Criteria**:

- [ ] Agent-to-agent delegations logged via `trace_collector.log_agent_interaction()`
- [ ] Tool calls logged via `trace_collector.log_tool_call()`
- [ ] Timing data captured for each delegation step
- [ ] `GraphTraceData` passed to `evaluate_comprehensive()` with real data
- [ ] `GraphTraceData` constructed via `model_validate()` instead of manual `.get()` extraction
- [ ] `make validate` passes

**Technical Requirements**:

- Initialize `TraceCollector` in `run_manager()` or `setup_agent_env()`
- Instrument delegation calls in `agent_system.py`
- Pass populated `GraphTraceData` from `app.py` to pipeline

**Files**:

- `src/app/agents/agent_system.py`
- `src/app/agents/orchestration.py`
- `src/app/app.py`

---

#### Feature 4: Graph vs Text Metric Comparison Output

**Description**: Log comparative summary showing Tier 1 (text) vs Tier 3 (graph) scores after evaluation.

**Acceptance Criteria**:

- [ ] Log shows Tier 1 overall score vs Tier 3 overall score
- [ ] Individual graph metrics displayed (path_convergence, tool_selection_accuracy, communication_overhead, coordination_centrality, task_distribution_balance)
- [ ] Individual text metrics displayed (cosine_score, jaccard_score, semantic_score)
- [ ] Composite score shows per-tier contribution
- [ ] `make validate` passes

**Files**:

- `src/app/app.py`
- `src/app/evals/evaluation_pipeline.py` (optional enhancement)

---

### Sprint 3: Plugin Architecture and Infrastructure (Deferred)

#### Feature 5: Model-Aware Content Truncation

**Description**: Implement token-limit-aware content truncation to prevent 413 errors when paper content exceeds provider rate limits (e.g., GitHub Models free tier enforces 8,000 token request limit for `gpt-4.1`, despite the model supporting 1M tokens natively).

**Acceptance Criteria**:

- [ ] `CommonSettings` includes per-provider `max_content_length` defaults
- [ ] `generate_paper_review_content_from_template` truncates `paper_content_for_template` to `max_content_length` before formatting into template
- [ ] Truncation preserves abstract (always included) and truncates body with `[TRUNCATED]` marker
- [ ] Warning logged when truncation occurs with original vs truncated size
- [ ] `make validate` passes

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

**Files**:

- `src/app/judge/plugins/traditional.py`

---

#### Feature 8: LLMJudgePlugin Wrapper

**Description**: Wrap existing `LLMJudgeEngine` as an `EvaluatorPlugin` with opt-in Tier 1 context enrichment.

**Acceptance Criteria**:

- [ ] LLMJudgePlugin with opt-in Tier 1 context enrichment
- [ ] All existing Tier 2 engine tests pass unchanged
- [ ] Per-plugin configurable timeout

**Files**:

- `src/app/judge/plugins/llm_judge.py`

---

#### Feature 9: GraphEvaluatorPlugin Wrapper

**Description**: Wrap existing `GraphAnalysisEngine` as an `EvaluatorPlugin`.

**Acceptance Criteria**:

- [ ] GraphEvaluatorPlugin wrapping existing engine
- [ ] All existing Tier 3 engine tests pass unchanged
- [ ] Per-plugin configurable timeout

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

**Files**: All source and test files (import updates), `CHANGELOG.md`

---

#### Feature 12: CC OTel Observability Plugin

**Description**: Standalone CC telemetry plugin using OTel → Opik pipeline. Enables CC session tracing alongside PydanticAI Opik instrumentation.

**Acceptance Criteria**:

- [ ] `src/app/cc_otel/` module with config + enable/disable API
- [ ] `CCOtelConfig` with env var export
- [ ] OTel Collector service added to `docker-compose.opik.yaml`
- [ ] Separate from existing `opik_instrumentation.py`
- [ ] Graceful degradation when OTel unavailable
- [ ] `make validate` passes

**Files**:

- `src/app/cc_otel/__init__.py`
- `src/app/cc_otel/config.py`
- `docker-compose.opik.yaml`

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
- Streamlit UI redesign (existing UI stays as-is)
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead)
- HuggingFace `datasets` library (use GitHub API downloader instead)
- Google Gemini SDK (`google-genai`) — use OpenAI-spec compatible providers only
- VCR-based network mocking (use @patch for unit tests)
- Browser-based E2E tests (Playwright/Selenium deferred)
- CC-style evaluation baselines (deferred beyond Sprint 3)
- E2E integration tests and multi-channel deployment (deferred beyond Sprint 3)

---

## Notes for Ralph Loop

Story Breakdown - Sprint 2 (4 stories total):

- **Feature 1 (Settings Migration)** → STORY-001: Migrate EvaluationConfig to JudgeSettings pydantic-settings
- **Feature 2 (Wire Evaluation)** → STORY-002: Wire evaluate_comprehensive after run_manager (depends: STORY-001)
- **Feature 3 (Trace Capture)** → STORY-003: Capture GraphTraceData during MAS execution (depends: STORY-002)
- **Feature 4 (Comparison Output)** → STORY-004: Add graph vs text metric comparison logging (depends: STORY-003)

Story Breakdown - Sprint 3 (8 stories total):

- **Feature 5 (Content Truncation)** → STORY-005: Model-aware content truncation
- **Feature 6 (Plugin Base)** → STORY-006: EvaluatorPlugin base and registry (depends: STORY-004)
- **Feature 7 (Traditional Adapter)** → STORY-007: TraditionalMetricsPlugin wrapper (depends: STORY-006)
- **Feature 8 (LLM Judge Adapter)** → STORY-008: LLMJudgePlugin wrapper (depends: STORY-006)
- **Feature 9 (Graph Adapter)** → STORY-009: GraphEvaluatorPlugin wrapper (depends: STORY-006)
- **Feature 10 (Plugin Pipeline)** → STORY-010: JudgeAgent replaces EvaluationPipeline (depends: STORY-007, STORY-008, STORY-009)
- **Feature 11 (Migration Cleanup)** → STORY-011: Remove shims and update imports (depends: STORY-010)
- **Feature 12 (CC OTel)** → STORY-012: CC OTel observability plugin (depends: STORY-010)
