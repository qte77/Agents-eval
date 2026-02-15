---
title: Product Requirements Document: Agents-eval Sprint 3
version: 3.9.0
created: 2026-02-15
updated: 2026-02-15
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 3 adds judge provider fallback for Tier 2 evaluation, restructures the evaluation pipeline into a plugin architecture (`EvaluatorPlugin` + `PluginRegistry` → `JudgeAgent`), adds model-aware content truncation for provider rate limits, introduces a standalone CC OTel observability plugin, aligns the test suite with documented testing strategy (hypothesis for property-based tests, inline-snapshot for regression tests), and wires the Streamlit GUI to display actual pydantic-settings defaults, makes weave observability optional, fixes trace data quality for Tier 3 graph analysis, and adds GUI controls for provider and sub-agent configuration. All Sprint 2 features (settings migration, eval wiring, trace capture, graph-vs-text comparison, Logfire+Phoenix tracing, Streamlit dashboard) are prerequisites.

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

#### Feature 6: Judge Provider Fallback

**Description**: Make the Tier 2 LLM-as-Judge evaluation provider configurable and resilient. Currently hardcoded to `openai/gpt-4o-mini`, causing 401 errors when no `OPENAI_API_KEY` is set. The judge should validate API key availability at startup and fall back to an available provider or skip Tier 2 gracefully.

**Acceptance Criteria**:

- [ ] Judge provider validates API key availability before attempting evaluation
- [ ] When configured provider's API key is missing, falls back to `tier2_fallback_provider`/`tier2_fallback_model`
- [ ] When no valid judge provider is available, Tier 2 is skipped with a warning (not scored 0.0)
- [ ] Composite score adjusts weights when Tier 2 is skipped (redistribute to Tier 1 + Tier 3)
- [ ] `JudgeSettings.tier2_provider` and `tier2_model` overridable via `JUDGE_TIER2_PROVIDER` / `JUDGE_TIER2_MODEL` env vars (already exists, ensure it works end-to-end)
- [ ] Fallback heuristic scores capped at 0.5 (neutral) when LLM assessment fails due to auth/provider errors
- [ ] Tier2Result includes metadata flag indicating whether fallback was used
- [ ] CompositeScorer logs warning when using fallback-derived scores
- [ ] Tests: Hypothesis property tests for fallback score bounds (0.0 ≤ fallback ≤ 0.5)
- [ ] Tests: inline-snapshot for Tier2Result structure with fallback metadata
- [ ] `make validate` passes

**Technical Requirements**:

- Add API key availability check in `LLMJudgeEngine` initialization
- Implement provider fallback chain: configured → fallback → skip
- Update `CompositeScorer` to handle missing Tier 2 (weight redistribution)
- Log clear warning when Tier 2 is skipped due to missing provider
- Fix `_fallback_planning_check()` in `llm_evaluation_managers.py:356-357` — cap fallback scores at 0.5 instead of 1.0 for "optimal range"
- Distinguish auth failures (401) from timeouts in fallback scoring

**Files**:

- `src/app/evals/llm_evaluation_managers.py` (provider validation + fallback)
- `src/app/evals/composite_scorer.py` (weight redistribution when tier skipped)
- `src/app/evals/settings.py` (ensure fallback settings work)

---

#### Feature 7: EvaluatorPlugin Base and Registry

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

#### Feature 8: TraditionalMetricsPlugin Wrapper

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

#### Feature 9: LLMJudgePlugin Wrapper

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

#### Feature 10: GraphEvaluatorPlugin Wrapper

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

#### Feature 11: Plugin-Driven Pipeline

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

#### Feature 12: Migration Cleanup

**Description**: Remove backward-compatibility shims, update all imports, delete deprecated JSON config.

**Acceptance Criteria**:

- [ ] All imports use `judge.`, `common.` paths
- [ ] No re-export shims remain
- [ ] `config/config_eval.json` removed
- [ ] Remove or implement commented-out `error_handling_context()` FIXME notes in `agent_system.py` (lines 443, 514, 583)
- [ ] Delete duplicate `src/app/agents/peerread_tools.py` (canonical: `src/app/tools/peerread_tools.py`, imported at `agent_system.py:63`)
- [ ] CHANGELOG.md updated
- [ ] `make validate` passes, no dead code

**Technical Requirements**:

- Update all source and test imports from `evals.` to `judge.` paths
- Remove re-export shim from Feature 11
- Delete deprecated `config/config_eval.json`
- Resolve `error_handling_context()` FIXMEs: either implement as a context manager or delete the comments (current try/except at line 520 is adequate)

**Files**:

- All source and test files (import updates)
- `CHANGELOG.md`
- `src/app/agents/agent_system.py`

---

#### Feature 13: CC OTel Observability Plugin

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

#### Feature 14: Wire GUI to Actual Settings

**Description**: Connect Streamlit GUI to load and display actual default values from `CommonSettings` and `JudgeSettings` pydantic-settings classes. Remove hardcoded `PROMPTS_DEFAULT` fallback and load prompts directly from `ChatConfig`. Follows DRY principle (single source of truth) and KISS principle (simple display, no persistence).

**Acceptance Criteria**:

- [ ] Settings page displays `CommonSettings` fields (log_level, enable_logfire, max_content_length)
- [ ] Settings page displays key `JudgeSettings` fields (tier timeouts, composite thresholds, enabled tiers)
- [ ] Prompts page loads from `ChatConfig.prompts` without hardcoded fallback
- [ ] GUI instantiates `CommonSettings()` and `JudgeSettings()` on startup
- [ ] Displayed values match actual pydantic-settings defaults
- [ ] Remove hardcoded `PROMPTS_DEFAULT` from `gui/config/config.py`
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Instantiate `CommonSettings()` and `JudgeSettings()` in `src/run_gui.py`
- Pass settings instances to `render_settings()`
- Update `render_settings()` to display CommonSettings and key JudgeSettings fields
- Update `render_prompts()` to use `ChatConfig.prompts` directly (remove fallback)
- Delete `PROMPTS_DEFAULT` constant from `gui/config/config.py`
- Read-only display (no save functionality per YAGNI principle)
- Use Streamlit expanders to organize settings by category

**Key Settings to Display** (JudgeSettings):

- Tiers: `tiers_enabled`, `tier1_max_seconds`, `tier2_max_seconds`, `tier3_max_seconds`
- Composite: `composite_accept_threshold`, `composite_weak_accept_threshold`
- Tier 2: `tier2_provider`, `tier2_model`, `tier2_cost_budget_usd`
- Observability: `trace_collection`, `logfire_enabled`, `phoenix_endpoint`

**Out of Scope** (per YAGNI):

- Saving edited settings back to .env file (read-only display only)
- Full CRUD for all 50+ JudgeSettings fields (show key 12-15 fields only)
- Settings validation/editing (display actual values only)

**Files**:

- `src/run_gui.py` (instantiate CommonSettings, JudgeSettings)
- `src/gui/pages/settings.py` (render CommonSettings, key JudgeSettings)
- `src/gui/pages/prompts.py` (remove hardcoded fallback)
- `src/gui/config/config.py` (delete PROMPTS_DEFAULT)

---

#### Feature 15: Test Infrastructure Alignment

**Description**: Refactor existing tests to use hypothesis (property-based testing) and inline-snapshot (regression testing), aligning test suite with documented testing-strategy.md practices. No production code changes. Explicitly excludes BDD/Gherkin (pytest-bdd).

**Acceptance Criteria**:

- [ ] Property-based tests using `@given` for math formulas (score bounds, composite calculations)
- [ ] Property-based tests for input validation (arbitrary text handling)
- [ ] Property-based tests for serialization (model dumps always valid)
- [ ] Snapshot tests using `snapshot()` for Pydantic `.model_dump()` outputs
- [ ] Snapshot tests for complex nested result structures
- [ ] Snapshot tests for GraphTraceData transformations
- [ ] Remove low-value tests (trivial assertions, field existence checks per testing-strategy.md)
- [ ] All existing test coverage maintained or improved
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Add `from hypothesis import given, strategies as st` imports
- Add `from inline_snapshot import snapshot` imports
- Convert score calculation tests to property tests with invariants (0.0 ≤ score ≤ 1.0)
- Convert model serialization tests to snapshot tests
- Document usage patterns in test files for future reference
- NO pytest-bdd, NO Gherkin, NO BDD methodology (use TDD with hypothesis for properties)

**Priority Test Areas** (from testing-strategy.md):

- **CRITICAL**: Math formulas (composite scoring, normalization bounds)
- **CRITICAL**: Loop termination (evaluation pipeline timeouts)
- **HIGH**: Input validation (arbitrary paper/review text)
- **HIGH**: Serialization (Tier1/2/3 result model dumps)
- **MEDIUM**: Invariants (tier weight sums, score aggregation)

**Files**:

- `tests/evals/test_composite_scorer.py` (score bounds properties)
- `tests/evals/test_traditional_metrics.py` (similarity score properties)
- `tests/data_models/test_peerread_models_serialization.py` (snapshot tests)
- `tests/evals/test_evaluation_pipeline.py` (result structure snapshots)
- `tests/evals/test_llm_evaluation_managers.py` (fallback property tests)
- `tests/evals/test_graph_analysis.py` (graph metric properties)
- Other test files as needed (~10-15 files total)

---

#### Feature 16: Optional Weave Integration

**Description**: Make weave dependency optional. Only import/init when `WANDB_API_KEY` is configured. Eliminates warning noise for users who don't use Weights & Biases.

**Acceptance Criteria**:

- [ ] `weave` moved from required to optional dependency group in `pyproject.toml`
- [ ] `login.py` conditionally imports weave only when `WANDB_API_KEY` is present
- [ ] `app.py` provides no-op `@op()` decorator fallback when weave unavailable
- [ ] No warning messages emitted when `WANDB_API_KEY` not set
- [ ] Existing weave tracing works unchanged when `WANDB_API_KEY` IS set
- [ ] Tests use Hypothesis for import guard property tests (weave present vs absent)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Move `weave>=0.52.28` to optional group in `pyproject.toml`
- `try/except ImportError` guard in `app.py`: `op = lambda: lambda f: f`
- Conditional import in `login.py` — only import weave inside the `if is_api_key:` block

**Files**:

- `pyproject.toml`
- `src/app/utils/login.py`
- `src/app/app.py`

---

#### Feature 17: Trace Data Quality & Manager Tool Tracing

**Description**: Fix trace data transformation bugs, add trace logging to PeerRead tools, initialize Logfire instrumentation, and improve trace storage logging.

**Acceptance Criteria**:

- [ ] Fix: `_process_events()` includes `agent_id` in tool_call dicts (`trace_processors.py:268-269`)
- [ ] Fix: `_parse_trace_events()` includes `agent_id` in tool_call dicts (`trace_processors.py:376-377`)
- [ ] Tier 3 graph analysis succeeds with `--include-researcher` traces (no "missing agent_id" error)
- [ ] PeerRead tools log trace events via `trace_collector.log_tool_call()` (all 6 tools)
- [ ] `initialize_logfire_instrumentation_from_settings()` called at startup when `logfire_enabled=True`
- [ ] `_store_trace()` logs full storage path (JSONL + SQLite) at least once per execution
- [ ] Manager-only runs produce non-empty trace data
- [ ] Tests: Hypothesis property tests for trace event schema invariants (agent_id always present)
- [ ] Tests: inline-snapshot for GraphTraceData transformation output structure
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `_process_events()` line 269: add `"agent_id": event.agent_id` to tool_call dict
- In `_parse_trace_events()` line 377: add `"agent_id": agent_id` to tool_call dict
- Add `trace_collector.log_tool_call()` to 6 PeerRead tools in `src/app/tools/peerread_tools.py` following delegation tool pattern (`time.perf_counter()` timing, success/failure)
- Call `initialize_logfire_instrumentation_from_settings()` in `src/app/app.py` after settings load
- Extend log message at `trace_processors.py:352-358` to include `self.storage_path`
- Use `JudgeSettings.logfire_enabled` as authoritative setting for Logfire initialization (not `CommonSettings.enable_logfire`)

**Files**:

- `src/app/evals/trace_processors.py` (agent_id fix + path logging)
- `src/app/tools/peerread_tools.py` (trace logging for 6 tools)
- `src/app/app.py` (Logfire init call)

**Note**: `src/app/agents/peerread_tools.py` appears to be a duplicate of `src/app/tools/peerread_tools.py`. Canonical import is `app.tools.peerread_tools` (used at `agent_system.py:63`).

---

#### Feature 18: GUI Agent & Provider Configuration

**Description**: Expose provider selection and sub-agent toggles in the Streamlit GUI with session state persistence. Currently CLI-only (`--chat-provider`, `--include-researcher/analyst/synthesiser`).

**Acceptance Criteria**:

- [ ] Settings page displays provider selectbox with all providers from `PROVIDER_REGISTRY`
- [ ] Settings page displays checkboxes for include_researcher, include_analyst, include_synthesiser
- [ ] Selections persist across page navigation via `st.session_state`
- [ ] Run App page passes all flags to `main()` from session state
- [ ] Default provider matches `CHAT_DEFAULT_PROVIDER`
- [ ] Tests: inline-snapshot for session state defaults structure
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Settings page: provider selectbox keyed to `st.session_state`, agent checkboxes
- Run App page: read from session state, pass to `main(chat_provider=..., include_researcher=..., ...)`
- `run_gui.py`: initialize session state defaults on startup
- Import `PROVIDER_REGISTRY` from `app.data_models.app_models` for provider list

**Files**:

- `src/gui/pages/settings.py`
- `src/gui/pages/run_app.py`
- `src/run_gui.py`

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
- **Testing:**
  - All new features must include tests per `docs/best-practices/testing-strategy.md`
  - Use **Hypothesis** (`@given`) for property-based tests: score bounds, input validation, serialization invariants
  - Use **inline-snapshot** (`snapshot()`) for regression tests: Pydantic model dumps, complex result structures
  - Use **pytest** for standard unit/integration tests with Arrange-Act-Assert structure
  - Tool selection: pytest for **logic**, Hypothesis for **properties**, inline-snapshot for **structure**
  - NO pytest-bdd / Gherkin (already in Out of Scope)

## Out of Scope

- A2A protocol migration (PydanticAI stays)
- Agent system restructuring (`src/app/agents/` unchanged except trace instrumentation)
- Streaming with Pydantic model outputs (`agent_system.py:522` `NotImplementedError` — PydanticAI supports `stream_struct()`/`agent.iter()` but integration deferred)
- Gemini provider compatibility (`agent_system.py:610` FIXME — `ModelRequest` iteration and `MALFORMED_FUNCTION_CALL` literal errors)
- HuggingFace provider implementation (falls through to generic OpenAI-compatible path, no dedicated handling needed yet)
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
Story Breakdown - Sprint 3 (14 stories total):

- **Feature 5 (Content Truncation)** → STORY-001: Model-aware content truncation
- **Feature 6 (Judge Fallback)** → STORY-002: Judge provider fallback for Tier 2
- **Feature 7 (Plugin Base)** → STORY-003: EvaluatorPlugin base and registry
- **Feature 8 (Traditional Adapter)** → STORY-004: TraditionalMetricsPlugin wrapper (depends: STORY-003)
- **Feature 9 (LLM Judge Adapter)** → STORY-005: LLMJudgePlugin wrapper (depends: STORY-003)
- **Feature 10 (Graph Adapter)** → STORY-006: GraphEvaluatorPlugin wrapper (depends: STORY-003)
- **Feature 11 (Plugin Pipeline)** → STORY-007: JudgeAgent replaces EvaluationPipeline (depends: STORY-004, STORY-005, STORY-006)
- **Feature 12 (Migration Cleanup)** → STORY-008: Remove shims and update imports (depends: STORY-007)
- **Feature 13 (CC OTel)** → STORY-009: CC OTel observability plugin (depends: STORY-007)
- **Feature 14 (GUI Settings Wiring)** → STORY-010: Wire GUI to actual settings (depends: STORY-008)
- **Feature 15 (Test Refactoring)** → STORY-011: Test infrastructure alignment (depends: STORY-008)
- **Feature 16 (Optional Weave)** → STORY-012: Make weave dependency optional
- **Feature 17 (Trace Quality)** → STORY-013: Trace data quality fixes + manager tool tracing
- **Feature 18 (GUI Config)** → STORY-014: GUI agent & provider configuration (depends: STORY-010)
