---
title: Product Requirements Document - Agents-eval Sprint 9
description: "Sprint 9: 4 features — CC engine GUI wiring, deprecated manager.run() fix, AgentConfig typing, GUI layout refactor."
version: 0.3.0
created: 2026-02-19
updated: 2026-02-21
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 7 delivered: documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

Sprint 8 features (8 features, 14 stories) have been fully implemented: tool bug fix (`get_paper_content`), API key/model cleanup, CC engine consolidation with teams support, graph attribute alignment, dead code removal (`pydantic_ai_stream`), report generation (CLI + GUI + suggestion engine), judge settings dropdowns, and GUI a11y/UX fixes.

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop enforces this order.**

### TDD Workflow (Mandatory for all features)

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality.
3. **REFACTOR**: Clean up while keeping tests green. Run `make validate` before marking complete.

### Test Tool Selection

| Tool | Use for | NOT for |
|------|---------|------------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation.

### Mandatory Practices

- **Mock external dependencies** (HTTP, LLM providers, file systems, subprocess) using `@patch`. Never call real APIs in unit tests.
- **Test behavior, not implementation** — test observable outcomes (return values, side effects, error messages), not internal structure.
- **Google-style docstrings** for every new file, function, class, and method.
- **`# Reason:` comments** for non-obvious logic.
- **`make validate` MUST pass** before any story is marked complete. No exceptions.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (all features) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |
| Design phase | `researching-codebase` → `designing-backend` |

---

## Non-Functional Requirements

- Report generation latency target: < 5s for rule-based suggestions, < 30s for LLM-assisted
- No new external dependencies without PRD validation
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S9-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).

## Features

### Feature 1: Wire CC Engine to GUI Execution Path

**Description**: The "Claude Code" radio button in `run_app.py` sets `engine="cc"` and passes it to `app.main()`, but `main()` only logs the value and unconditionally runs the MAS PydanticAI pipeline. The CLI (`run_cli.py:126-138`) correctly branches to `cc_engine.run_cc_solo`/`run_cc_teams` — the GUI must do the same.

**Acceptance Criteria**:

- [ ] AC1: Selecting "Claude Code" in the GUI radio button invokes `cc_engine.run_cc_solo()` (or `run_cc_teams()` if teams enabled) instead of the MAS pipeline
- [ ] AC2: CC engine results are stored in session state and available to Evaluation Results and Agent Graph pages
- [ ] AC3: MAS-specific controls (sub-agents, provider, token limit) remain hidden when CC engine is selected (existing behavior preserved)
- [ ] AC4: Error handling for missing `claude` CLI binary shows user-friendly message in GUI
- [ ] AC5: All existing MAS tests continue to pass; new tests cover the CC GUI path

**Technical Requirements**:

- Add CC engine branch in `_execute_query_background()` or `app.main()` mirroring `run_cli.py:126-138` logic
- Handle subprocess execution within Streamlit's threading model (background thread already exists)
- Wire CC results back through `_prepare_result_dict()` to populate `execution_graph` and `composite_result` in session state
- Mock `subprocess.run` in tests — never call real `claude` CLI

**Files**:

- `src/gui/pages/run_app.py` (edit — CC branch in `_execute_query_background`)
- `src/app/app.py` (edit — CC branch in `main()` or delegate to caller)
- `tests/test_gui/test_session_state_wiring.py` (edit — CC engine path tests)

---

### Feature 2: Fix Deprecated `manager.run()` Call and Type Suppressions

**Description**: `agent_system.py:543-551` uses the deprecated `manager.run()` PydanticAI API with 3 FIXME markers and broad `type: ignore` directives (`reportDeprecated`, `reportUnknownArgumentType`, `reportCallOverload`, `call-overload`). The `result.usage()` call also requires `type: ignore`. Migrate to the current PydanticAI `Agent.run()` API to remove all suppressions.

**Acceptance Criteria**:

- [ ] AC1: `manager.run()` replaced with current PydanticAI API (non-deprecated call)
- [ ] AC2: All `type: ignore` comments on lines 548 and 551 removed — pyright passes cleanly
- [ ] AC3: All 3 FIXME comments (lines 543-544, 550) removed
- [ ] AC4: Agent execution produces identical results (same `execution_id`, same `result.output`)
- [ ] AC5: `make validate` passes with no new type errors or test failures

**Technical Requirements**:

- Research current PydanticAI `Agent.run()` signature and migrate `mgr_cfg` dict unpacking accordingly
- Verify `result.usage()` return type is properly typed after migration
- Preserve `trace_collector` start/end calls and error handling structure
- Mock PydanticAI agent in tests — never call real LLM providers

**Files**:

- `src/app/agents/agent_system.py` (edit — lines 538-551, migrate `manager.run()` call)
- `tests/agents/test_agent_system.py` (edit — update/add tests for migrated call)

---

### Feature 3: Add Proper Type Annotation to `AgentConfig.tools` Field

**Description**: `app_models.py:105-106` has a FIXME noting that `tools: list[Any]` should be `list[Callable[..., Awaitable[Any]]]`. The `Any` type bypasses static analysis and allows invalid tool registrations to pass silently. The correct type is known but was deferred due to Pydantic schema generation issues with callable types.

**Acceptance Criteria**:

- [ ] AC1: `tools` field uses `list[Callable[..., Awaitable[Any]]]` (or narrower type if feasible)
- [ ] AC2: FIXME comment on line 105 removed
- [ ] AC3: Pydantic schema generation still works (no `PydanticSchemaGenerationError`)
- [ ] AC4: All existing agent creation paths pass type checking with the new annotation
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- May require adding `Callable` to `arbitrary_types_allowed` or using a Pydantic `TypeAdapter`/custom validator
- Verify all call sites that populate `tools` pass the correct callable types
- If `Callable[..., Awaitable[Any]]` causes schema generation errors, use `Annotated` with a custom `BeforeValidator` or `SkipValidation`

**Files**:

- `src/app/data_models/app_models.py` (edit — line 105-106, fix type annotation)
- `tests/data_models/test_app_models.py` (edit — add test for tools field type validation)

---

### Feature 4: GUI Layout Refactor — Sidebar Tabs and Page Separation

**Description**: `run_gui.py:43-44` has a TODO to restructure the GUI layout: create sidebar tabs, move settings to its own page, set `README.md` as the home page, and separate prompts into a dedicated page. Currently all pages are rendered inline without tab-based navigation.

**Acceptance Criteria**:

- [ ] AC1: Sidebar uses `st.tabs` or equivalent navigation for page switching
- [ ] AC2: Settings renders as a standalone page accessible from sidebar (not inline)
- [ ] AC3: Home page displays project README.md content
- [ ] AC4: Prompts renders as a standalone page accessible from sidebar (not inline)
- [ ] AC5: All existing page functionality (Run App, Evaluation Results, Agent Graph) preserved
- [ ] AC6: TODO comment on lines 43-44 removed
- [ ] AC7: `make validate` passes with no regressions

**Technical Requirements**:

- Use Streamlit's `st.navigation` / `st.Page` (Streamlit 1.36+) or `st.sidebar` radio/selectbox pattern matching existing codebase conventions
- Preserve session state across page switches (existing `get_session_state_defaults()` must still work)
- Load README.md via `pathlib.Path` read — no external fetch
- Mock file reads in tests

**Files**:

- `src/run_gui.py` (edit — replace inline rendering with tab/page navigation)
- `src/gui/pages/home.py` (edit — render README.md content)
- `tests/test_gui/test_gui_navigation.py` (new — sidebar navigation and page rendering tests)

---

## Out of Scope

**Deferred to future sprint (TBD acceptance criteria, low urgency):**

- Centralized Tool Registry with Module Allowlist (MAESTRO L7.2) — architectural, needs design
- Plugin Tier Validation at Registration (MAESTRO L7.1) — architectural, needs design
- Error Message Sanitization (MAESTRO) — TBD acceptance criteria
- Configuration Path Traversal Protection (MAESTRO) — TBD acceptance criteria
- GraphTraceData Construction Simplification (`model_validate()`) — TBD acceptance criteria
- Timeout Bounds Enforcement — low urgency
- Hardcoded Settings Audit — continuation of Sprint 7
- Time Tracking Consistency Across Tiers — low urgency
- BDD Scenario Tests for Evaluation Pipeline — useful but not blocking
- Tier 1 Reference Comparison Fix — requires ground-truth review integration
- Cerebras Structured Output Validation Retries — provider-specific edge case
- PlantUML Diagram Audit — cosmetic, no user impact
- Unify API Key Resolution Across Agent and Judge Paths — partially addressed by Feature 2 auto-mode fix; full unification deferred
- ~~CC engine SDK migration~~ — **Removed.** Keeping `subprocess.run([claude, "-p"])` per ADR-008.

**Already completed (Sprint 8, all 14 stories delivered):**

- Feature 1: `read_paper_pdf_tool` → `get_paper_content` with parsed JSON fallback chain
- Feature 2: `"not-required"` sentinel removal + judge auto-mode model inheritance
- Feature 3: CC engine consolidation (`cc_engine.py`) with solo + teams support
- Feature 4: Graph node attribute alignment (`node_type` → `type`)
- Feature 5: Dead `pydantic_ai_stream` parameter removal
- Feature 6: Report generation (CLI `--generate-report`, GUI button, suggestion engine)
- Feature 7: Judge settings free-text → populated dropdowns
- Feature 8: GUI a11y/UX fixes (WCAG, environment URL, run ID, baseline validation)
