---
title: Product Requirements Document: Agents-eval Sprint 5
version: 1.0.0
created: 2026-02-15
updated: 2026-02-15
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 4 delivered operational resilience (Logfire, graph timeouts, test alignment) and CC baseline comparison infrastructure.

Sprint 5 addresses runtime bugs, GUI enhancements, architectural improvements, code quality review, and technical debt cleanup across 17 stories:

1. **Core Runtime Fixes (Features 1-4)**: Judge provider fallback, token limit configurability, single-agent score fairness, PeerRead validation resilience
2. **GUI Enhancements (Features 6-9)**: Background execution, debug log panel, results tab wiring, editable settings
3. **Architecture & Reliability (Features 12-13, 16)**: OTLP endpoint fix, graph analysis accuracy, PeerRead tool delegation for multi-agent coordination
4. **Code Quality & Cleanup (Features 10-11, 14-15, 17)**: Security review (OWASP MAESTRO), test suite audit, wandb import guard, API key debug logging, duplicate AppEnv deletion
5. **Documentation (Feature 5)**: Comprehensive updates reflecting all Sprint 5 changes

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop enforces this order.**

### TDD Workflow (Mandatory for Features 1-4, 6-9, 12-17)

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality.
3. **REFACTOR**: Clean up while keeping tests green. Run `make validate` before marking complete.

### Test Tool Selection (per `docs/best-practices/testing-strategy.md`)

| Tool | Use for | NOT for |
|------|---------|---------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation.

### Core Principles (per `.claude/rules/core-principles.md`)

- **KISS**: Simplest solution that passes tests. Clear > clever.
- **DRY**: Reuse existing patterns (`pydantic-settings`, `select_available_provider()`, session state). Don't rebuild.
- **YAGNI**: Implement only what acceptance criteria require. No speculative features.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (1-4, 6-9, 12-17) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Review (10) | `reviewing-code` + `securing-mas` |
| Audit (11) | `testing-python` (for rewrites) |
| Documentation (5) | None (manual edits) |

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Wire Tier 2 Judge Provider Fallback

**Description**: The `LLMJudgeEngine.select_available_provider()` method exists but is never called. When `tier2_provider=openai` and no `OPENAI_API_KEY` is set, all three Tier 2 metrics fail with 401 and fall back to neutral 0.5 scores. Wire the existing fallback chain so the judge validates API key availability before attempting LLM calls, and add a `tier2_provider=auto` mode that inherits the agent system's active provider.

**Acceptance Criteria**:

- [ ] `LLMJudgeEngine` calls `select_available_provider()` before creating judge agents
- [ ] When primary provider API key is missing, fallback provider is used automatically
- [ ] When both providers are unavailable, Tier 2 is skipped with a single warning (no 401 errors, no neutral 0.5 fallback scores)
- [ ] When Tier 2 is skipped, its 3 metrics (`technical_accuracy`, `constructiveness`, `planning_rationality`) are excluded from composite scoring and their weights redistributed to Tier 1 and Tier 3 metrics
- [ ] Compound redistribution: When both Tier 2 skipped AND single-agent mode (STORY-003), composite scorer must handle both conditions (skip 3 Tier 2 metrics + skip `coordination_quality`, redistribute remaining weights)
- [ ] New `tier2_provider=auto` mode inherits the agent system's active `chat_provider`
- [ ] `EvaluationPipeline` accepts optional `chat_provider` parameter to pass through to judge
- [ ] `_run_evaluation_if_enabled()` in `app.py` passes `chat_provider` to the pipeline
- [ ] Existing `JUDGE_TIER2_PROVIDER` env var override continues to work
- [ ] Tests: Hypothesis property tests for provider selection invariants (fallback only when primary unavailable)
- [ ] Tests: inline-snapshot for log messages during fallback
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `LLMJudgeEngine.__init__()` (`llm_evaluation_managers.py:35`): store `env_config` parameter
- In `LLMJudgeEngine.create_judge_agent()` (`llm_evaluation_managers.py:110`): call `select_available_provider(self.env_config)` to resolve provider/model before creating agent
- If `select_available_provider()` returns `None`, skip Tier 2 evaluation (return neutral fallback)
- Add `tier2_provider: str = Field(default="auto")` option to `JudgeSettings` -- when `"auto"`, use the `chat_provider` passed from the agent system
- Update `EvaluationPipeline.__init__()` to accept optional `chat_provider: str | None` and pass it to `LLMJudgeEngine`
- Update `_run_evaluation_if_enabled()` in `app.py` to forward `chat_provider` from the agent run
- Update `create_simple_model()` in `models.py` to support Cerebras provider (reuse existing `create_llm_model()` provider logic)

**Files**:

- `src/app/judge/llm_evaluation_managers.py`
- `src/app/judge/evaluation_pipeline.py`
- `src/app/judge/settings.py`
- `src/app/app.py`
- `src/app/llms/models.py`
- `tests/judge/test_llm_evaluation_managers.py` (update)

---

#### Feature 2: Configurable Agent Token Limits

**Description**: The Cerebras provider has `usage_limits: 60000` in `config_chat.json`, but the `gpt-oss-120b` model consumed 75,954 tokens (74,714 input + 1,240 output) during a GUI run, causing `UsageLimitExceeded`. The high input token count was amplified by PeerRead tool returning 23 papers plus structured output validation retries. Add CLI and GUI overrides for `total_tokens_limit` so users can adjust without editing `config_chat.json`.

**Acceptance Criteria**:

- [ ] CLI: `--token-limit N` flag overrides `usage_limits` from `config_chat.json`
- [ ] GUI: Token limit input field in settings sidebar (pre-populated from `config_chat.json`)
- [ ] When flag/field is not set, existing `config_chat.json` value is used (no regression)
- [ ] `AGENT_TOKEN_LIMIT` environment variable override (lowest priority after CLI/GUI)
- [ ] Validation: minimum 1000, maximum 1000000
- [ ] Tests: Hypothesis property tests for limit bounds and override priority
- [ ] Tests: inline-snapshot for CLI help text
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Add `--token-limit` argument to CLI entry point in `src/app/main.py`
- Pass override through `main()` in `app.py` to `setup_agent_env()` in `agent_system.py`
- In `setup_agent_env()` (`agent_system.py:633-638`): use CLI override if provided, else `config_chat.json` value, else env var
- Add token limit input to GUI settings sidebar in `src/gui/pages/settings.py`
- Pass GUI value through to `render_app()` in `src/gui/pages/run_app.py`

**Files**:

- `src/app/main.py`
- `src/app/app.py`
- `src/app/agents/agent_system.py`
- `src/gui/pages/settings.py`
- `src/gui/pages/run_app.py`
- `tests/app/test_cli_token_limit.py` (new)

---

#### Feature 3: Single-Agent Composite Score Weight Redistribution

**Description**: The composite scorer uses equal weights (0.167 each) across 6 metrics. For single-agent runs (no multi-agent delegation), `coordination_quality` is structurally 0.0 (mapped from `coordination_centrality` in Tier 3 graph analysis), causing a guaranteed 0.167 deduction. The scorer should detect single-agent runs and redistribute `coordination_quality` weight to the remaining 5 metrics.

**Acceptance Criteria**:

- [ ] Detect single-agent runs from `GraphTraceData` (0 or 1 unique agent IDs, empty `coordination_events`)
- [ ] When single-agent detected, redistribute `coordination_quality` weight (0.167) equally across remaining 5 metrics
- [ ] Multi-agent runs continue using all 6 metrics with equal weights (no regression)
- [ ] `CompositeResult` includes `single_agent_mode: bool` flag for transparency
- [ ] Compound redistribution: When both Tier 2 skipped (STORY-001) AND single-agent mode, composite scorer must handle both conditions (see STORY-001 for interaction)
- [ ] Log message when weight redistribution occurs
- [ ] Tests: Hypothesis property tests for weight sum invariant (always sums to ~1.0)
- [ ] Tests: inline-snapshot for metric weights in single-agent vs multi-agent mode
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Add `is_single_agent(execution_trace: GraphTraceData | None) -> bool` helper in `composite_scorer.py`
- In `CompositeScorer.calculate_composite_score()` (`composite_scorer.py:167`): check agent count and adjust weights
- Adjusted weights for single-agent: each of the 5 remaining metrics gets `1.0 / 5.0 = 0.200`
- Add `single_agent_mode: bool = False` field to `CompositeResult` model in `evaluation_models.py`
- Set flag in `evaluate_composite()` before returning result

**Files**:

- `src/app/judge/composite_scorer.py`
- `src/app/data_models/evaluation_models.py`
- `tests/judge/test_composite_scorer.py` (update)

---

#### Feature 4: PeerRead Dataset Validation Resilience

**Description**: Six papers (304-308, 330) fail validation with `KeyError: 'IMPACT'` at `datasets_peerread.py:724` because they lack the `IMPACT` field. These papers are silently skipped, reducing dataset coverage. The `IMPACT` field should be treated as optional with a sensible default instead of causing validation failure.

**Acceptance Criteria**:

- [ ] Papers with missing `IMPACT` field are validated successfully with `IMPACT` defaulting to `None` or `"UNKNOWN"`
- [ ] Papers with missing other optional fields (`histories`, `comments`) also handled gracefully
- [ ] Existing papers with valid `IMPACT` field are unaffected (no regression)
- [ ] Log debug message when optional field is missing (not warning)
- [ ] Tests: Hypothesis property tests for paper validation with arbitrary missing optional fields
- [ ] Tests: inline-snapshot for validated paper with missing IMPACT
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `_validate_papers()` (`datasets_peerread.py:~700-727`): use `paper_data.get("IMPACT", None)` instead of direct key access
- Update `PeerReadPaper` Pydantic model to make `IMPACT` field `Optional[str] = None`
- Review other fields in validation loop for similar missing-key risks (`histories`, `comments`, `SUBSTANCE`, `APPROPRIATENESS`)
- Use `.get()` with defaults for all optional paper metadata fields

**Files**:

- `src/app/data_utils/datasets_peerread.py`
- `src/app/data_models/peerread_models.py` (update PeerReadPaper model)
- `tests/data_utils/test_datasets_peerread.py` (update)

---

#### Feature 5: Documentation and Diagram Updates

**Description**: Update project documentation and architecture diagrams to reflect Sprint 5 changes: judge provider fallback, configurable token limits, single-agent score redistribution, and PeerRead validation resilience. Add Sprint 5 to the roadmap and update architecture decision records where applicable.

**Acceptance Criteria**:

- [ ] `README.md`: Version badge updated, Sprint 5 referenced in status section
- [ ] `docs/roadmap.md`: Sprint 5 row added to roadmap table with status "Active" and link to `PRD-Sprint5-Ralph.md`
- [ ] `docs/architecture.md`: Composite Scoring section updated to document single-agent weight redistribution behavior
- [ ] `docs/architecture.md`: Tier 2 LLM-as-Judge section updated to document provider fallback chain and `auto` mode
- [ ] `docs/architecture.md`: Implementation Status section updated with Sprint 5 entry
- [ ] `docs/arch_vis/`: Update relevant PlantUML diagrams if evaluation pipeline flow changed (e.g., provider selection step in Tier 2)
- [ ] CHANGELOG.md updated
- [ ] Stale "Opik integration" docstrings in `graph_analysis.py` (lines 423, 506) updated to reference Phoenix
- [ ] No broken internal links introduced

**Technical Requirements**:

- Update `docs/roadmap.md` roadmap table: add Sprint 5 row, update Sprint 4 status to "Delivered"
- Update `docs/architecture.md` Composite Scoring System section (`line ~180-200`) to note weight redistribution for single-agent runs
- Update `docs/architecture.md` LLM-as-a-Judge section (`line ~124-139`) to document `tier2_provider=auto` and fallback chain
- Update `docs/architecture.md` Development Timeline section (`line ~297-304`) with Sprint 5 entry
- Review `docs/arch_vis/mas-enhanced-workflow.plantuml` and `docs/arch_vis/metrics-eval-sweep.plantuml` for accuracy against new evaluation flow
- Update `README.md` version badge if project version incremented

**Files**:

- `README.md`
- `docs/roadmap.md`
- `docs/architecture.md`
- `docs/arch_vis/mas-enhanced-workflow.plantuml` (if applicable)
- `docs/arch_vis/metrics-eval-sweep.plantuml` (if applicable)
- `CHANGELOG.md`

---

#### Feature 6: Background Execution with Tab Navigation

**Description**: When a user navigates away from the App tab during query execution, the run aborts because Streamlit re-runs the script on page change. The execution result is also lost because it is not persisted to session state. The app should run queries in the background and persist results so users can navigate freely and return to see completed output.

**Acceptance Criteria**:

- [ ] Query execution continues when user navigates to another tab (Settings, Evaluation Results, etc.)
- [ ] User can return to App tab and see the result after execution completes
- [ ] A progress indicator (spinner or status) shows while execution is in progress
- [ ] If execution is in progress when returning to App tab, spinner is displayed
- [ ] Execution result (`CompositeResult`, agent output) stored in `st.session_state`
- [ ] Error state stored in session state and displayed when user returns
- [ ] Tests: pytest unit tests for session state transitions (idle → running → completed/error)
- [ ] Tests: inline-snapshot for session state keys after execution
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Use `st.session_state` to persist execution state: `running`, `result`, `error`, `execution_id`
- Run `main()` via `st.fragment` (Streamlit 1.33+) or `threading.Thread` with callback that writes result to session state on completion. Note: `st.session_state` is not thread-safe -- use `st.fragment` if available, otherwise synchronize writes
- In `render_app()` (`run_app.py:108`): check session state for existing result before starting new execution
- Add `st.spinner("Running evaluation...")` or `st.status()` container around execution
- Store `CompositeResult` in `st.session_state["evaluation_result"]` for cross-tab access

**Files**:

- `src/gui/pages/run_app.py`
- `src/run_gui.py`
- `tests/test_gui/test_run_app.py` (update)

---

#### Feature 7: Debug Log Panel in App Tab

**Description**: Add an expandable panel in the App tab that displays real-time pipeline log output (evaluation metrics, tier results, errors) that currently only appears in the terminal. Users should see the same diagnostic information visible in the CLI without needing terminal access.

**Acceptance Criteria**:

- [ ] Expandable/collapsible "Debug Log" section at the bottom of the App tab
- [ ] Captures loguru output from `app.*` modules during execution
- [ ] Displays log entries with timestamp, level, and message (formatted, not raw)
- [ ] Log panel updates after execution completes (not required to be real-time streaming)
- [ ] Collapsed by default to keep UI clean
- [ ] Log entries color-coded by level: INFO (default), WARNING (yellow), ERROR (red)
- [ ] Tests: pytest unit tests for log capture sink (filters `app.*` modules, clears buffer)
- [ ] Tests: inline-snapshot for log panel HTML structure
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Add a custom loguru sink that captures log records to a list during execution
- Store captured logs in `st.session_state["debug_logs"]`
- In `render_app()`: add `st.expander("Debug Log", expanded=False)` after result display
- Inside expander, render each log entry using `st.text()` or `st.code()` with level formatting
- Sink should filter to `app.*` module logs only (exclude Streamlit internals)
- Clear log buffer at start of each new execution

**Files**:

- `src/gui/pages/run_app.py`
- `src/gui/utils/log_capture.py` (new)
- `tests/test_gui/test_log_capture.py` (new)

---

#### Feature 8: Wire Evaluation Results and Agent Graph Tabs to Real Data

**Description**: The "Evaluation Results" and "Agent Graph" tabs have full rendering implementations but are called with `None` data from `run_gui.py` (lines 100, 103). After a query execution in the App tab, both pages should display actual results from the completed run instead of showing placeholder messages.

**Acceptance Criteria**:

- [ ] After App tab execution completes, navigating to "Evaluation Results" displays the actual `CompositeResult`
- [ ] After App tab execution completes, navigating to "Agent Graph" displays the actual interaction graph from `GraphTraceData`
- [ ] Both pages show informational message when no execution has been run yet (existing behavior preserved)
- [ ] Evaluation Results page displays: composite score, tier scores, metric comparison chart, recommendation
- [ ] Agent Graph page displays: interactive Pyvis network with agent and tool nodes
- [ ] Data persists across tab navigation within the same session
- [ ] Tests: Hypothesis property tests for session state data integrity across page switches
- [ ] Tests: inline-snapshot for evaluation page render with real CompositeResult
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Store `CompositeResult` in `st.session_state["evaluation_result"]` after evaluation pipeline completes (from Feature 6)
- Build `nx.DiGraph` from `GraphTraceData` and store in `st.session_state["agent_graph"]`
- In `run_gui.py`: pass `st.session_state.get("evaluation_result")` to `render_evaluation()` instead of `None`
- In `run_gui.py`: pass `st.session_state.get("agent_graph")` to `render_agent_graph()` instead of `None`
- Graph construction: reuse existing `GraphTraceData` → `nx.DiGraph` conversion from `graph_analysis.py`

**Files**:

- `src/run_gui.py`
- `src/gui/pages/run_app.py`
- `src/gui/pages/evaluation.py` (minor -- verify data flow)
- `src/gui/pages/agent_graph.py` (minor -- verify data flow)
- `tests/test_gui/test_evaluation_page.py` (update)
- `tests/test_gui/test_agent_graph_page.py` (update)

---

#### Feature 9: Editable Settings Page

**Description**: The Settings page (`src/gui/pages/settings.py`) currently displays `JudgeSettings` and `AppEnv` values as read-only text. Only the "Agent Configuration" section (provider selector, agent toggles) in the App tab sidebar is interactive. All displayed settings should be editable via the GUI and applied to the current session.

**Acceptance Criteria**:

- [ ] `JudgeSettings` fields editable: `tiers_enabled`, `tier2_provider`, `tier2_model`, `tier2_fallback_provider`, `tier2_fallback_model`, timeout values
- [ ] `JudgeSettings` composite thresholds editable: `composite_accept_threshold`, `composite_weak_accept_threshold`, `composite_weak_reject_threshold`
- [ ] Observability settings editable: `logfire_enabled`, `phoenix_endpoint`, `trace_collection`
- [ ] Changed settings applied to the current session (stored in `st.session_state`)
- [ ] "Reset to Defaults" button restores original `JudgeSettings()` defaults
- [ ] Settings changes take effect on next App tab execution (no restart required)
- [ ] Input validation matches pydantic field constraints (e.g., `gt=0, le=300` for timeouts)
- [ ] Tests: Hypothesis property tests for settings value bounds
- [ ] Tests: inline-snapshot for settings page widget structure
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Replace `st.text()` / `st.json()` display-only rendering with appropriate input widgets:
  - `st.multiselect()` for `tiers_enabled`
  - `st.selectbox()` for `tier2_provider` (options from known providers list)
  - `st.text_input()` for model names
  - `st.number_input()` for timeouts and thresholds (with min/max from Field constraints)
  - `st.toggle()` for boolean fields (`logfire_enabled`, `trace_collection`)
- Store modified settings in `st.session_state["judge_settings"]` as `JudgeSettings` instance
- In `run_app.py`: use `st.session_state.get("judge_settings", JudgeSettings())` when creating `EvaluationPipeline`
- Add "Reset to Defaults" button that clears settings from session state

**Files**:

- `src/gui/pages/settings.py`
- `src/gui/pages/run_app.py` (read settings from session state)
- `tests/test_gui/test_settings_page.py` (update)

---

#### Feature 10: Code Quality and Security Review

**Description**: Comprehensive code quality and security audit of the entire codebase using the `reviewing-code` and `securing-mas` Claude Code skills, supported by Context7 MCP for up-to-date library documentation and Exa MCP for security advisory lookups. The review applies the OWASP MAESTRO 7-layer security framework documented in `docs/best-practices/mas-security.md` and produces actionable findings with fix recommendations.

**Acceptance Criteria**:

- [ ] Code quality review completed using `reviewing-code` skill across all `src/app/` modules
- [ ] Security review completed using `securing-mas` skill applying OWASP MAESTRO 7-layer framework
- [ ] MAESTRO Layer 1 (Model): Prompt injection risks assessed in agent system prompts and tool outputs
- [ ] MAESTRO Layer 2 (Agent Logic): Input validation and type safety verified across agent factories, evaluation managers
- [ ] MAESTRO Layer 3 (Integration): External service failure handling reviewed (LLM providers, PeerRead API, OTLP export)
- [ ] MAESTRO Layer 4 (Monitoring): Log injection risks and sensitive data in traces checked
- [ ] MAESTRO Layer 5 (Execution): Resource exhaustion risks reviewed (token limits, timeouts, thread pools)
- [ ] MAESTRO Layer 6 (Environment): Secret management verified (API keys in `.env`, no hardcoded credentials)
- [ ] MAESTRO Layer 7 (Orchestration): Agent delegation and tool registration security reviewed
- [ ] Context7 MCP used to verify current best practices for PydanticAI, Logfire, and Streamlit security patterns
- [ ] Exa MCP used to check for known CVEs in project dependencies
- [ ] Review findings documented in `docs/reviews/sprint5-code-review.md`
- [ ] Critical and high findings fixed in code; medium/low findings documented as future work
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Use `reviewing-code` skill for quality review: code complexity, duplication, naming, error handling, docstring completeness
- Use `securing-mas` skill for security review: apply each MAESTRO layer checklist against relevant modules
- Use Context7 MCP (`mcp__plugin_context7_context7__query-docs`) to verify security patterns for:
  - `/pydantic/pydantic-ai` -- agent security, tool validation
  - `/pydantic/logfire` -- trace data sensitivity
  - `/websites/streamlit_io` -- session state security, XSS prevention
- Use Exa MCP (`mcp__exa__web_search_exa`) to search for CVEs and security advisories for project dependencies
- Claude Code agent orchestration: spawn parallel review agents per MAESTRO layer for efficiency
- Priority modules for review:
  - `src/app/agents/agent_system.py` -- agent orchestration, prompt handling
  - `src/app/llms/providers.py` -- API key management
  - `src/app/llms/models.py` -- model creation, provider routing
  - `src/app/judge/llm_evaluation_managers.py` -- LLM judge calls
  - `src/app/judge/evaluation_pipeline.py` -- pipeline orchestration
  - `src/gui/pages/run_app.py` -- user input handling
  - `src/app/data_utils/datasets_peerread.py` -- external data ingestion

**Files**:

- `docs/reviews/sprint5-code-review.md` (new)
- `src/app/` (all modules subject to review -- fixes applied in place)

**Ralph Loop Note**: This is a review task, not an implementation task. Ralph should invoke the `reviewing-code` and `securing-mas` skills to produce findings, fix critical/high issues in code, and write the review document. The primary deliverable is `docs/reviews/sprint5-code-review.md`.

---

#### Feature 11: Test Suite Audit and Behavioral Refactoring

**Description**: Systematic audit of all 56 test files against the testing strategy (`docs/best-practices/testing-strategy.md`). Tests that only verify implementation details (field existence, type checks, default values, import availability) are deleted or replaced with behavioral tests. Tests that verify actual behavior (business logic, error handling, integration contracts) are kept and improved. The goal is a leaner, higher-signal test suite where every test catches real bugs.

**Acceptance Criteria**:

- [ ] Every test file in `tests/` audited against testing strategy criteria
- [ ] Tests that only verify implementation details identified and removed (see anti-patterns below)
- [ ] Tests that verify actual behavior kept and improved where needed
- [ ] No reduction in behavioral coverage -- only implementation-detail tests removed
- [ ] Remaining tests use appropriate tooling: pytest for logic, Hypothesis for properties, inline-snapshot for structure
- [ ] Audit findings documented in `docs/reviews/sprint5-test-audit.md` with per-file decisions (keep/delete/refactor)
- [ ] `make validate` passes after refactoring
- [ ] `make test_all` passes with no regressions in behavioral coverage
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- **Anti-patterns to remove** (from `docs/best-practices/testing-strategy.md`):
  - Import/existence tests: `test_module_exists()`, `test_class_importable()`
  - Field existence tests: `test_model_has_field_x()`, `hasattr()` checks
  - Default constant tests: `assert DEFAULT_VALUE == 300`
  - Type-only checks: `assert isinstance(result, dict)` (pyright handles this)
  - Over-granular tests: 8 separate tests for one Pydantic model's fields
  - Library behavior tests: testing Pydantic validation, `os.environ` reads, framework internals
  - Trivial assertions: `x is not None`, `callable(func)`

- **Behavioral tests to keep/improve**:
  - Business logic: composite scoring calculations, metric extraction, weight redistribution
  - Error handling: provider fallback chains, timeout behavior, missing data graceful degradation
  - Integration contracts: evaluation pipeline end-to-end, trace data flow, GUI session state
  - Edge cases with real impact: empty inputs, boundary values, concurrent access

- **Per-directory audit priorities**:
  - `tests/evals/` (14 files) -- HIGH: core evaluation logic, likely contains both good behavioral tests and implementation-detail tests
  - `tests/judge/` (10 files) -- HIGH: judge pipeline, plugin system
  - `tests/integration/` (5 files) -- MEDIUM: integration contracts, may have over-mocked tests
  - `tests/test_gui/` (5 files) -- MEDIUM: GUI behavior, may test Streamlit internals
  - `tests/agents/` (3 files) -- MEDIUM: agent wiring
  - `tests/data_models/`, `tests/data_utils/`, `tests/common/`, `tests/utils/` -- LOW: data validation, likely candidates for cleanup
  - `tests/cc_otel/` (2 files) -- DELETE: Phoenix replaced Opik, cc_otel tests are obsolete
  - `test_migration_cleanup.py` -- DELETE: Sprint 4 migration complete, cleanup file no longer needed

- **Decision rule**: If a test wouldn't catch a real bug introduced by a code change, remove it.

**Files**:

- `tests/` (all 56 test files subject to audit)
- `docs/reviews/sprint5-test-audit.md` (new -- per-file audit decisions)

**Ralph Loop Note**: This is an audit-and-refactor task. Ralph should read each test file, apply the decision rule against the anti-pattern list, delete or rewrite failing tests, and document per-file decisions in `docs/reviews/sprint5-test-audit.md`. Run `make test_all` after each batch of changes.

---

#### Feature 12: Fix OTLP Endpoint Double-Path Bug

**Description**: The Logfire instrumentation sets `OTEL_EXPORTER_OTLP_ENDPOINT` to `http://localhost:6006/v1/traces` (`logfire_instrumentation.py:59`). Per the OTEL spec, the SDK auto-appends signal-specific paths to this base endpoint, producing `http://localhost:6006/v1/traces/v1/traces` for spans and `http://localhost:6006/v1/traces/v1/metrics` for metrics -- both return HTTP 405 from Phoenix. All trace export silently fails despite the agent instrumentation working correctly.

**Acceptance Criteria**:

- [ ] Traces from agent runs appear in the Phoenix UI at `http://localhost:6006`
- [ ] No HTTP 405 errors in logs for `/v1/traces/v1/traces` or `/v1/traces/v1/metrics` paths
- [ ] `OTEL_EXPORTER_OTLP_ENDPOINT` set to base URL only (`http://localhost:6006`), not the signal-specific path
- [ ] Existing `PHOENIX_ENDPOINT` env var and `phoenix_endpoint` config field continue to work
- [ ] Tests: pytest unit test for endpoint construction logic (base URL without signal path)
- [ ] Tests: inline-snapshot for the constructed OTLP endpoint value
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `LogfireInstrumentation._configure_phoenix()` (`logfire_instrumentation.py:59`): set `OTEL_EXPORTER_OTLP_ENDPOINT` to `self.config.phoenix_endpoint` (base URL) instead of appending `/v1/traces`
- Update connectivity check at line 65: `requests.head()` should probe the base URL (e.g., `http://localhost:6006`), not the double-path URL
- Alternative: use `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (signal-specific variable, not auto-appended by SDK) if base endpoint conflicts with other signal exporters
- Remove any 405 suppression workarounds that are no longer needed after the fix

**Files**:

- `src/app/agents/logfire_instrumentation.py`
- `tests/agents/test_logfire_instrumentation.py` (update)

---

#### Feature 13: Fix Tier 3 Graph Analysis Tool Accuracy and Dead Metric

**Description**: Two issues in `graph_analysis.py` affect Tier 3 scoring accuracy. First, `add_node` at line 171 overwrites `success_rate` each time a tool is called, so only the last call's outcome survives -- if a tool succeeds 9 times and fails once (last), `success_rate=0.0`. The same overwrite applies to `add_edge` at line 173 for agent-tool edge weights. Second, `communication_overhead` is computed and stored in `Tier3Result` but never included in `overall_score` (lines 392-397), making it a dead metric that inflates the model without contributing to scoring.

**Acceptance Criteria**:

- [ ] Tool `success_rate` accumulates across all calls (e.g., 9/10 successes = 0.9), not just the last call
- [ ] Agent-tool edge `weight` accumulates or averages across repeated calls, not overwritten
- [ ] `communication_overhead` either contributes to `overall_score` or is removed from `Tier3Result`
- [ ] If `communication_overhead` is included in scoring, weights are rebalanced to sum to 1.0
- [ ] Existing multi-tool and single-tool scenarios produce correct `tool_selection_accuracy`
- [ ] Tests: Hypothesis property tests for tool accuracy with repeated calls (success_rate in [0.0, 1.0])
- [ ] Tests: inline-snapshot for Tier3Result with known tool call sequences
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `analyze_tool_usage()` (`graph_analysis.py:165-173`): track call count and success count per tool node, compute `success_rate` as `successes / total_calls` after the loop
- For edge weights: accumulate call count per agent-tool pair, average or sum weights
- For `communication_overhead`: decide include-or-remove. If removed, delete from `Tier3Result` model in `evaluation_models.py` and any downstream references. If included, rebalance `self.weights` to sum to 1.0 across 5 metrics.

**Files**:

- `src/app/judge/graph_analysis.py`
- `src/app/data_models/evaluation_models.py` (if `communication_overhead` removed)
- `tests/judge/test_graph_analysis.py` (update)

---

#### Feature 14: Guard Wandb Import and Disable Crash Telemetry

**Description**: `login.py:9` has an unconditional `from wandb import login as wandb_login` at module level. If the optional `wandb` package is not installed, the entire `login.py` module fails to import, breaking the application. Additionally, wandb sends crash telemetry to Sentry by default with no opt-out. The weave import at line 44 is already guarded inside the function body -- the wandb import should follow the same pattern.

**Acceptance Criteria**:

- [ ] Application starts successfully when `wandb` is not installed (no `ImportError`)
- [ ] When `wandb` is installed and `WANDB_API_KEY` is set, login and weave init work as before
- [ ] When `wandb` is not installed, `login()` skips wandb/weave initialization with a debug log
- [ ] `WANDB_ERROR_REPORTING` defaults to `"false"` (respects user override if already set)
- [ ] Dead agentops commented code removed from `login.py`: commented import at line 7 (`# from agentops import init as agentops_init`) and commented code block at lines 30-37
- [ ] Tests: pytest unit test for login with wandb unavailable (mock ImportError)
- [ ] Tests: inline-snapshot for log output when wandb is missing
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Replace unconditional `from wandb import login as wandb_login` (line 9) with guarded import:
  ```python
  try:
      from wandb import login as wandb_login
      _wandb_available = True
  except ImportError:
      _wandb_available = False
  ```
- Add `os.environ.setdefault("WANDB_ERROR_REPORTING", "false")` before the wandb import
- In `login()`: guard `wandb_login()` and `weave_init()` calls with `if _wandb_available`
- Log `logger.debug("wandb not installed, skipping wandb/weave initialization")` when unavailable

**Files**:

- `src/app/utils/login.py`
- `tests/utils/test_login.py` (new or update)

---

#### Feature 15: Debug Logging for Empty API Keys

**Description**: When `get_api_key()` returns `False` for a provider whose key exists in `.env` but resolves to empty string at runtime, there is no diagnostic log. This makes transient `.env` loading issues (CWD mismatch, env var unset between runs) hard to diagnose. Add a debug log when a key is expected (provider registered with `env_key`) but the value is empty.

**Acceptance Criteria**:

- [ ] `get_api_key()` logs a debug message when a registered provider's key resolves to empty string
- [ ] Debug message includes the `env_key` name (e.g., `GITHUB_API_KEY`) for diagnosis
- [ ] No log emitted for providers without API keys (e.g., Ollama)
- [ ] No log emitted when key is correctly loaded
- [ ] Tests: pytest unit test for empty-key debug log scenario
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `get_api_key()` (`providers.py:42`): add `logger.debug(f"API key '{provider_metadata.env_key}' is empty for provider '{provider}'")` in the else branch
- No new settings fields, no behavioral change -- debug logging only

**Files**:

- `src/app/llms/providers.py`
- `tests/llms/test_providers.py` (update)

---

#### Feature 16: Move PeerRead Tools from Manager to Researcher Agent

**Description**: The manager agent receives both delegation tools (`researcher()`, `analyst()`, `synthesiser()`) and PeerRead tools (`get_peerread_paper`, `generate_paper_review_content_from_template`, `save_structured_review`) via `add_peerread_tools_to_manager()` at `agent_system.py:411`. Sub-agents get minimal tools: researcher has only `duckduckgo_search_tool()`, analyst and synthesiser have none. Models take the path of least resistance -- the manager uses PeerRead tools directly instead of delegating, resulting in zero multi-agent coordination. Moving PeerRead tools to the researcher enforces separation of concerns: manager coordinates, researcher executes.

**Acceptance Criteria**:

- [ ] PeerRead tools (`get_peerread_paper`, `generate_paper_review_content_from_template`, `save_structured_review`) registered on the researcher agent, not the manager
- [ ] Manager agent retains only delegation tools (`researcher()`, `analyst()`, `synthesiser()`)
- [ ] Researcher agent has PeerRead tools plus `duckduckgo_search_tool()`
- [ ] Manager delegates to researcher for PeerRead operations (verified via `GraphTraceData` showing delegation events)
- [ ] Tier 3 graph analysis produces non-zero `coordination_centrality` and `communication_overhead` in multi-agent runs
- [ ] Single-agent fallback still works if researcher is disabled via agent toggles
- [ ] Existing CLI and GUI behavior produces correct review output (no regression in review quality)
- [ ] Tests: pytest unit test for tool registration (researcher has PeerRead tools, manager does not)
- [ ] Tests: Hypothesis property tests for delegation invariant (manager never calls PeerRead tools directly)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Rename `add_peerread_tools_to_manager()` to `add_peerread_tools_to_researcher()` in `peerread_tools.py`
- In `_create_manager()` (`agent_system.py:410-411`): remove `add_peerread_tools_to_manager(manager)` call
- In researcher agent creation block (`agent_system.py:~370-380`): add PeerRead tools alongside `duckduckgo_search_tool()`
- Update researcher system prompt to include PeerRead tool usage instructions (currently only on manager prompt)
- If researcher is `None` (disabled), fall back to adding PeerRead tools to manager to preserve single-agent operation

**Files**:

- `src/app/agents/agent_system.py`
- `src/app/tools/peerread_tools.py`
- `tests/agents/test_agent_system.py` (update)

---

#### Feature 17: Delete Duplicate AppEnv and Dead Code in load_settings.py

**Description**: `src/app/utils/load_settings.py` contains a duplicate `AppEnv` class (lines 22-49) that diverges from the canonical `AppEnv` in `src/app/data_models/app_models.py` (lines 219-249). The duplicate is missing `ANTHROPIC_API_KEY`, `CEREBRAS_API_KEY`, `OPENAI_API_KEY`, and uses `LOGFIRE_TOKEN` instead of `LOGFIRE_API_KEY`. It also eagerly instantiates `chat_config = AppEnv()` at module level (line 52), which runs on import. Only one consumer exists: `datasets_peerread.py:23`. The duplicate class and module-level instance should be deleted; `load_config()` can remain since it loads `ChatConfig` from JSON.

**Acceptance Criteria**:

- [ ] Duplicate `AppEnv` class removed from `load_settings.py`
- [ ] Module-level `chat_config = AppEnv()` instance removed from `load_settings.py`
- [ ] `datasets_peerread.py` import updated to use canonical `AppEnv` from `app.data_models.app_models`
- [ ] `load_config()` function retained in `load_settings.py` ONLY if still used for JSON config loading; if `load_config()` is unused (grep/search confirms no consumers), delete entire `load_settings.py` module
- [ ] No import errors or runtime failures after removal
- [ ] Tests: pytest unit test verifying single `AppEnv` source of truth
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Delete `class AppEnv` (lines 22-49) and `chat_config = AppEnv()` (line 52) from `load_settings.py`
- In `datasets_peerread.py:23`: change `from app.utils.load_settings import chat_config` to `from app.data_models.app_models import AppEnv` and instantiate where needed (or pass as parameter)
- Verify no other files import from `load_settings.AppEnv` (grep confirmed: only `datasets_peerread.py`)

**Files**:

- `src/app/utils/load_settings.py`
- `src/app/data_utils/datasets_peerread.py`
- `tests/data_utils/test_datasets_peerread.py` (update if affected)

---

## Non-Functional Requirements

- **Maintainability:**
  - Use existing configuration patterns (pydantic-settings, env prefix overrides)
  - No new dependencies required
- **Performance:**
  - Provider selection adds negligible overhead (single API key check per evaluation)
  - Weight redistribution is a simple arithmetic operation
  - GUI background execution must not block Streamlit's event loop
- **Backward Compatibility:**
  - All fixes are additive; existing `JUDGE_TIER2_PROVIDER=openai` and `config_chat.json` values continue working
  - Default behavior changes only where current defaults produce errors (401 auth failures, silent paper skipping)
  - CLI behavior unchanged by GUI features
- **Testing** (per `docs/best-practices/testing-strategy.md`):
  - **TDD mandatory**: RED (failing test) → GREEN (minimal implementation) → REFACTOR for all implementation stories
  - Use **pytest** as primary TDD tool for unit tests with Arrange-Act-Assert structure
  - Use **Hypothesis** (`@given`) for property-based tests: provider selection invariants, weight sum invariants, token limit bounds, paper validation with missing fields, settings value bounds
  - Use **inline-snapshot** (`snapshot()`) for regression tests: log messages, model dumps, CLI help text, GUI component structures
  - **Decision rule**: Test behavior, not implementation. If a test wouldn't catch a real bug, don't write it.

## Out of Scope

- Tier 1 reference comparison fix (all-1.0 self-comparison scores -- requires ground-truth review integration, separate feature)
- Automatic PeerRead dataset download when splits are missing (existing error message with instructions is sufficient)
- Custom composite weight configuration via CLI/GUI (equal-weight is the defined scoring model)
- Tier 2 cost tracking or budget enforcement (existing `tier2_cost_budget_usd` is informational only)
- Cerebras-specific prompt optimization for structured output validation retries
- Real-time log streaming in GUI (logs displayed after execution completes)
- Persisting modified settings to `.env` or `config_chat.json` (session-only changes)
- Adding new tests for untested modules (audit scope is refactoring existing tests only)
- Penetration testing or runtime exploit validation (static review only)

---

## Notes for Ralph Loop

### Story Priority Tiers for Ralph

Ralph should prioritize stories in the following order to maximize value delivery:

- **P0 (Quick Wins - 1-line fixes)**: STORY-012 (OTLP endpoint), STORY-014 (wandb import guard), STORY-015 (API key debug log), STORY-017 (duplicate AppEnv)
- **P1 (Core Bugs)**: STORY-001 (judge provider fallback), STORY-003 (single-agent score fairness), STORY-004 (PeerRead validation), STORY-013 (graph analysis accuracy)
- **P2 (GUI Features)**: STORY-002 (token limits), STORY-006 (background execution), STORY-007 (debug log panel), STORY-008 (wire results tabs), STORY-009 (editable settings)
- **P3 (Architecture)**: STORY-016 (PeerRead tool delegation)
- **P4 (Meta-Tasks)**: STORY-010 (code review), STORY-011 (test audit)
- **P5 (Documentation - Blocked)**: STORY-005 (depends on all other stories)

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Sprint 5 (17 stories total):

- **Feature 1 (Judge Provider Fallback)** → STORY-001: Wire Tier 2 judge provider fallback and auto-inherit agent provider
- **Feature 2 (Token Limits)** → STORY-002: Configurable agent token limits via CLI, GUI, and env var
- **Feature 3 (Score Fairness)** → STORY-003: Single-agent composite score weight redistribution
- **Feature 4 (PeerRead Validation)** → STORY-004: PeerRead dataset validation resilience for optional fields
- **Feature 5 (Documentation Updates)** → STORY-005: Update documentation and diagrams for Sprint 5 (depends: STORY-001, STORY-002, STORY-003, STORY-004, STORY-006, STORY-007, STORY-008, STORY-009, STORY-010, STORY-011, STORY-012, STORY-013, STORY-014, STORY-015, STORY-016, STORY-017)
- **Feature 6 (Background Execution)** → STORY-006: Background query execution with tab navigation resilience
- **Feature 7 (Debug Log Panel)** → STORY-007: Debug log panel in App tab (depends: STORY-006)
- **Feature 8 (Wire Results Tabs)** → STORY-008: Wire Evaluation Results and Agent Graph tabs to real data (depends: STORY-006)
- **Feature 9 (Editable Settings)** → STORY-009: Editable settings page with session-scoped persistence (depends: STORY-001)
- **Feature 10 (Code Review)** → STORY-010: Code quality and OWASP MAESTRO security review
- **Feature 11 (Test Audit)** → STORY-011: Test suite audit and behavioral refactoring
- **Feature 12 (OTLP Endpoint Fix)** → STORY-012: Fix OTLP endpoint double-path bug in Logfire instrumentation
- **Feature 13 (Graph Analysis Fixes)** → STORY-013: Fix Tier 3 tool accuracy overwrite and dead communication_overhead metric
- **Feature 14 (Wandb Import Guard)** → STORY-014: Guard wandb import and disable crash telemetry default
- **Feature 15 (API Key Debug Log)** → STORY-015: Debug logging for empty API keys in provider resolution
- **Feature 16 (PeerRead Tool Delegation)** → STORY-016: Move PeerRead tools from manager to researcher agent
- **Feature 17 (Delete Duplicate AppEnv)** → STORY-017: Delete duplicate AppEnv class and dead code in load_settings.py
