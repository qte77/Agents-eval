---
title: Product Requirements Document - Agents-eval Sprint 10
description: "Sprint 10: 6 features — CC engine GUI wiring, PydanticAI API migration, GUI layout refactor, data layer robustness, dispatch chain refactor, source inspection test rewrites."
version: 1.0.0
created: 2026-02-21
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

**Prerequisite**: Sprint 9 (9 features — correctness, security, quick wins) must be completed before Sprint 10 begins. Sprint 9 deletes `orchestration.py` dead code and resolves security/accuracy findings that Sprint 10 features depend on. See [PRD-Sprint9-Ralph.md](PRD-Sprint9-Ralph.md).

---

## Development Methodology

Same TDD workflow and mandatory practices as Sprint 9. See [PRD-Sprint9-Ralph.md](PRD-Sprint9-Ralph.md#development-methodology) for the complete methodology section.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->
<!-- PARSER REQUIREMENT: No compound sub-features — one heading per story -->
<!-- PARSER REQUIREMENT: Flatten AC items — no indented sub-items under a checkbox -->
<!-- PARSER REQUIREMENT: Each sub-feature MUST have its own **Files**: section -->

#### Feature 1: Wire CC Engine to GUI Execution Path

**Dependency**: Depends on Sprint 9 Feature 1 (`orchestration.py` deleted).

**Description**: The "Claude Code" radio button in `run_app.py` sets `engine="cc"` and passes it to `app.main()`, but `main()` only logs the value and unconditionally runs the MAS PydanticAI pipeline. The CLI (`run_cli.py:126-138`) correctly branches to `cc_engine.run_cc_solo`/`run_cc_teams` — the GUI must do the same.

**Acceptance Criteria**:

- [ ] AC1: Selecting "Claude Code" in the GUI radio button invokes `cc_engine.run_cc_solo()` (or `run_cc_teams()` if teams enabled) instead of the MAS pipeline
- [ ] AC2: CC engine results are stored in session state and available to Evaluation Results and Agent Graph pages
- [ ] AC3: MAS-specific controls (sub-agents, provider, token limit) remain hidden when CC engine is selected (existing behavior preserved)
- [ ] AC4: Error handling for missing `claude` CLI binary shows user-friendly message in GUI
- [ ] AC5: All existing MAS tests continue to pass; new tests cover the CC GUI path
- [ ] AC6: `run_cc_teams` respects `timeout` parameter — process is killed after timeout expires (Review F13)

**Technical Requirements**:

- Add CC engine branch in `_execute_query_background()` or `app.main()` mirroring `run_cli.py:126-138` logic
- Handle subprocess execution within Streamlit's threading model (background thread already exists)
- Wire CC results back through `_prepare_result_dict()` to populate `execution_graph` and `composite_result` in session state
- Fix `run_cc_teams` timeout: `subprocess.Popen` does not accept `timeout` — use `proc.wait(timeout=timeout)` or `threading.Timer` to enforce the deadline (`cc_engine.py:236-256`)
- Mock `subprocess.run` in tests — never call real `claude` CLI

**Files**:

- `src/gui/pages/run_app.py` (edit — CC branch in `_execute_query_background`)
- `src/app/app.py` (edit — CC branch in `main()` or delegate to caller)
- `src/app/engines/cc_engine.py` (edit — enforce timeout in `run_cc_teams`)
- `tests/test_gui/test_session_state_wiring.py` (edit — CC engine path tests)

---

#### Feature 2: PydanticAI API Migration — `manager.run()`, `RunContext`, and Private Attribute Access

**Dependency**: Depends on Sprint 9 Feature 1 (`orchestration.py` deleted) and Feature 1 of this sprint.

**Description**: `agent_system.py:543-551` uses the deprecated `manager.run()` PydanticAI API with 3 FIXME markers and broad `type: ignore` directives (`reportDeprecated`, `reportUnknownArgumentType`, `reportCallOverload`, `call-overload`). The `result.usage()` call also requires `type: ignore`. Additionally, `RunContext` may be deprecated in the installed PydanticAI version (Review F6), and `_model_name` private attribute access at `agent_system.py:537` should use the public `model_name` API (Review F23). Migrate all three patterns in one pass.

**Acceptance Criteria**:

- [ ] AC1: `manager.run()` replaced with current PydanticAI API (non-deprecated call)
- [ ] AC2: All `type: ignore` comments on lines 548 and 551 removed — pyright passes cleanly
- [ ] AC3: All 3 FIXME comments (lines 543-544, 550) removed
- [ ] AC4: Agent execution produces identical results (same `execution_id`, same `result.output`)
- [ ] AC5: `RunContext` verified against installed PydanticAI version; updated to current name (e.g., `AgentRunContext`) if deprecated (Review F6)
- [ ] AC6: `_model_name` private attribute access replaced with public `model_name` API (Review F23)
- [ ] AC7: `make validate` passes with no new type errors or test failures

**Technical Requirements**:

- Research current PydanticAI `Agent.run()` signature and migrate `mgr_cfg` dict unpacking accordingly
- Verify `result.usage()` return type is properly typed after migration
- Verify `RunContext` deprecation status: `python -c "from pydantic_ai import RunContext; print(RunContext)"`. If deprecated, update all tool function signatures in `agent_system.py` and `peerread_tools.py` (note: `orchestration.py` is deleted by Sprint 9 Feature 1)
- Replace `getattr(manager, "model")._model_name` with `getattr(manager, "model").model_name` (public attribute) with fallback to `"unknown"`
- Preserve `trace_collector` start/end calls and error handling structure
- Mock PydanticAI agent in tests — never call real LLM providers

**Files**:

- `src/app/agents/agent_system.py` (edit — lines 537-551, migrate `manager.run()`, fix `_model_name`, check `RunContext`)
- `src/app/tools/peerread_tools.py` (edit — update `RunContext` import if deprecated)
- `tests/agents/test_agent_system.py` (edit — update/add tests for migrated call)

---

#### Feature 3: GUI Layout Refactor — Sidebar Tabs and Page Separation

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

#### Feature 4: Data Layer Robustness — Narrow Exceptions + Contradictory Log

**Description**: Two data layer findings: (1) `_validate_papers()` and `load_papers()` use `except Exception` covering all failure modes — `KeyError`, `ValidationError`, and `OSError` all land in the same handler (Review F9), (2) `_validate_download_results` logs "continuing" then immediately raises, contradicting the log message (Review F17).

**Acceptance Criteria**:

- [ ] AC1: `_validate_papers()` separates `KeyError`/`ValidationError` (expected data quality) from `OSError`/`JSONDecodeError` (infrastructure failures) — infrastructure failures are re-raised (Review F9)
- [ ] AC2: `load_papers()` exception handling similarly narrowed (Review F9)
- [ ] AC3: `_validate_download_results` either removes the misleading "continuing" warning or makes the raise conditional (only raise if ALL downloads failed) (Review F17)
- [ ] AC4: `Exception` replaced with `RuntimeError` or custom exception in `_validate_download_results` (Review F17)
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- F9: Split exception handlers: `except (KeyError, ValidationError) as e: logger.warning(...)` + `except (OSError, JSONDecodeError) as e: raise`
- F17: Either `logger.warning("Some downloads failed, continuing with partial data")` without raise (if partial success is acceptable), or remove the warning and just raise

**Files**:

- `src/app/data_utils/datasets_peerread.py` (edit — lines 109-112, 734, 793-795)
- `tests/data_utils/test_datasets_peerread.py` (edit — test narrowed exception paths)

---

#### Feature 5: Dispatch Chain Registry Refactor in `datasets_peerread.py`

**Dependency**: Depends on Feature 4 (shared file: `datasets_peerread.py`).

**Description**: Four methods (`_construct_url`, `_extract_paper_id_from_filename`, `_get_cache_filename`, `_save_file_data`) each independently dispatch on the same three `data_type` values (`"reviews"`, `"parsed_pdfs"`, `"pdfs"`) via `if/elif/else` chains. This is the pattern documented in AGENT_LEARNINGS.md as "Repeated Dispatch Chains Inflate File Complexity" (Review F10).

**Acceptance Criteria**:

- [ ] AC1: A `DATA_TYPE_SPECS` registry dict replaces all four dispatch chains
- [ ] AC2: Adding a new data type requires only a dict entry, not changes to four methods
- [ ] AC3: Invalid `data_type` values are caught at entry with a descriptive error
- [ ] AC4: All existing download and validation tests pass unchanged
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- Define `@dataclass class DataTypeSpec` with fields: `url_suffix`, `filename_pattern`, `cache_prefix`, `is_json`, `save_handler`
- Create `DATA_TYPE_SPECS: dict[str, DataTypeSpec]` with entries for `"reviews"`, `"parsed_pdfs"`, `"pdfs"`
- Replace each `if/elif/else` chain with `spec = DATA_TYPE_SPECS[data_type]` lookup
- Validate `data_type` once at `download_venue_split` entry point

**Files**:

- `src/app/data_utils/datasets_peerread.py` (edit — lines 245-254, 272-278, 416-424, 439-444)
- `tests/data_utils/test_datasets_peerread.py` (edit — test registry lookup and invalid data_type)

---

#### Feature 6: Replace `inspect.getsource` Tests with Behavioral Tests

**Description**: Six test files use `inspect.getsource(module)` then assert string presence (e.g., `'engine != "cc"' in source`). This pattern breaks on code reformatting, passes if the string appears anywhere in source, and couples tests to implementation rather than behavior. Identified as a top-3 anti-pattern by prevalence in the tests parallel review (H5, H6, M14, M15 — ~20 occurrences across 6 files).

**Acceptance Criteria**:

- [ ] AC1: `tests/utils/test_weave_optional.py` — `inspect.getsource` replaced with behavioral test: import module with weave absent, verify `op()` is a callable no-op decorator (tests-review H5)
- [ ] AC2: `tests/gui/test_story012_a11y_fixes.py` — all 11 `inspect.getsource` occurrences replaced with Streamlit mock-based assertions (tests-review H6)
- [ ] AC3: `tests/gui/test_story013_ux_fixes.py` — source inspection replaced with behavioral widget assertions (tests-review H6)
- [ ] AC4: `tests/gui/test_story010_gui_report.py` — 2 source inspections replaced with output assertions (tests-review H6)
- [ ] AC5: `tests/cli/test_cc_engine_wiring.py` — 4 source inspections removed; behavioral tests already exist alongside (tests-review H6, M15)
- [ ] AC6: `tests/gui/test_prompts_integration.py` — source file read + string assertion replaced with render function mock test (tests-review M14)
- [ ] AC7: Zero occurrences of `inspect.getsource` remain in `tests/` directory
- [ ] AC8: `make validate` passes with no regressions

**Technical Requirements**:

- Replace source-level string assertions with behavioral tests: call the function with relevant inputs and assert outputs
- For UI tests, verify widgets called via Streamlit mocks instead of inspecting source
- For CLI tests, remove redundant source inspections where behavioral `parse_args` tests already cover the logic
- Run `grep -r "inspect.getsource" tests/` to verify zero remaining occurrences

**Files**:

- `tests/utils/test_weave_optional.py` (edit)
- `tests/gui/test_story012_a11y_fixes.py` (edit)
- `tests/gui/test_story013_ux_fixes.py` (edit)
- `tests/gui/test_story010_gui_report.py` (edit)
- `tests/cli/test_cc_engine_wiring.py` (edit)
- `tests/gui/test_prompts_integration.py` (edit)

---

## Non-Functional Requirements

- Report generation latency target: < 5s for rule-based suggestions, < 30s for LLM-assisted
- No new external dependencies without PRD validation
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S10-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).

## Out of Scope

**Deferred test review findings (MEDIUM/LOW from tests-parallel-review-2026-02-21.md):**

- `assert isinstance()` replacements with behavioral assertions (H4, M1-M3) — ~30+ occurrences across 12 files
- Subdirectory `conftest.py` creation for `tests/agents/`, `tests/tools/`, `tests/evals/`, `tests/judge/` (M5, M6)
- `@pytest.mark.parametrize` additions for provider tests and recommendation tests (M7, M8)
- `hasattr()` replacements with behavioral tests (M4)
- Weak assertion strengthening in `test_suggestion_engine.py` and `test_report_generator.py` (M18, L5)
- Hardcoded relative path fix in `test_peerread_tools_error_handling.py` (H8)
- `tempfile` → `tmp_path` in integration tests (L7, L8)
- `@pytest.mark.slow` markers on performance baselines (L10)

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

---

## Notes for Ralph Loop

### Priority Order

- **P1 (feature)**: STORY-010 (CC engine GUI), STORY-011 (PydanticAI migration)
- **P2 (feature)**: STORY-012 (GUI layout)
- **P3 (refactoring)**: STORY-013 (data layer), STORY-014 (dispatch chain)
- **P4 (test quality)**: STORY-015 (source inspection)

### Notes for CC Agent Teams

- **Team Structure**: Lead + 2 teammates max

#### File-Conflict Dependencies

| Stories sharing files | Shared file | Resolution |
|---|---|---|
| STORY-010, STORY-011 | `agent_system.py` | STORY-010→STORY-011 (sequential) |
| STORY-013, STORY-014 | `datasets_peerread.py` | STORY-013→STORY-014 (sequential) |

#### Orchestration Waves

```text
Wave 1 (independent): STORY-012 (F3 GUI layout), STORY-015 (F6 source inspection)
Wave 2 (after Sprint 9): STORY-010 (F1 CC engine), STORY-013 (F4 data layer)
Wave 3 (after Wave 2): STORY-011 (F2 PydanticAI, after STORY-010), STORY-014 (F5 dispatch, after STORY-013)
```

- **Quality Gates**: Teammate runs `make quick_validate`; lead runs `make validate` after each wave
- **Teammate Prompt Template**: Sprint 8 pattern with TDD `[RED]`/`[GREEN]` commit markers

Story Breakdown - Phase 1 (6 stories total):

- **Feature 1** → STORY-010: Wire CC engine to GUI execution path (depends: Sprint 9 STORY-001)
  Wire CC engine branch in `_execute_query_background()` or `app.main()` mirroring `run_cli.py:126-138` logic. Fix `run_cc_teams` timeout enforcement. Files: `src/gui/pages/run_app.py`, `src/app/app.py`, `src/app/engines/cc_engine.py`, `tests/test_gui/test_session_state_wiring.py`.

- **Feature 2** → STORY-011: PydanticAI API migration (depends: Sprint 9 STORY-001, STORY-010)
  Migrate `manager.run()` to current PydanticAI API, fix `RunContext`, replace `_model_name` with public API. Files: `src/app/agents/agent_system.py`, `src/app/tools/peerread_tools.py`, `tests/agents/test_agent_system.py`.

- **Feature 3** → STORY-012: GUI layout refactor — sidebar tabs
  Create sidebar tab navigation, move settings to own page, `README.md` as home page, prompts as dedicated page. Files: `src/run_gui.py`, `src/gui/pages/home.py`, `tests/test_gui/test_gui_navigation.py`.

- **Feature 4** → STORY-013: Data layer robustness — narrow exceptions
  Split `except Exception` into specific handlers, fix contradictory log-then-raise in `_validate_download_results`. Files: `src/app/data_utils/datasets_peerread.py`, `tests/data_utils/test_datasets_peerread.py`.

- **Feature 5** → STORY-014: Dispatch chain registry refactor (depends: STORY-013 [file: datasets_peerread.py])
  Replace 4 dispatch chains with `DATA_TYPE_SPECS` registry dict. Validate `data_type` once at entry point. Files: `src/app/data_utils/datasets_peerread.py`, `tests/data_utils/test_datasets_peerread.py`.

- **Feature 6** → STORY-015: Replace inspect.getsource tests with behavioral tests
  Rewrite ~20 `inspect.getsource` assertions across 6 test files with behavioral tests using function calls and mock assertions. Files: `tests/utils/test_weave_optional.py`, `tests/gui/test_story012_a11y_fixes.py`, `tests/gui/test_story013_ux_fixes.py`, `tests/gui/test_story010_gui_report.py`, `tests/cli/test_cc_engine_wiring.py`, `tests/gui/test_prompts_integration.py`.
