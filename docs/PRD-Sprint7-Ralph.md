---
title: Product Requirements Document - Agents-eval Sprint 7
description: Documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, and Claude Code engine option for the Agents-eval MAS evaluation framework.
version: 1.2
created: 2026-02-17
updated: 2026-02-17
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 6 delivered: benchmarking infrastructure, CC comparison engine infrastructure, security hardening (CVE mitigations, input sanitization, log scrubbing), test quality improvements.

**Sprint 7 Focus**: Documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

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
- **Test behavior, not implementation** — test observable outcomes (return values, side effects, error messages), not internal structure (isinstance checks, property existence, default constants).
- **Google-style docstrings** for every new file, function, class, and method. Auto-generated documentation depends on this.
- **`# Reason:` comments** for non-obvious logic (e.g., regex patterns, XML delimiter choices, fallback order).
- **`make validate` MUST pass** before any story is marked complete. No exceptions.

### Core Principles

- **KISS**: Simplest solution that passes tests. Clear > clever.
- **DRY**: Reuse existing patterns (`CompositeResult`, `EvaluationPipeline`, `CCTraceAdapter`). Don't rebuild.
- **YAGNI**: Implement only what acceptance criteria require. No speculative features.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (1-6, 8-14) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Test refactoring (7) | `testing-python` (for validation after changes) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Remove Outdated Examples

**Description**: `src/examples/` contains Sprint 1-era code using deprecated APIs and generic PydanticAI tutorials without project context. Remove all outdated examples to eliminate confusion and maintenance burden.

**Acceptance Criteria**:
- [ ] Delete evaluation examples: `run_evaluation_example.py`, `run_evaluation_example_simple.py` (use deprecated dict-based `execution_trace` API)
- [ ] Delete generic agent examples: `run_simple_agent_no_tools.py`, `run_simple_agent_system.py`, `run_simple_agent_tools.py` (PydanticAI tutorials, no project value)
- [ ] Delete supporting files: `src/examples/utils/` directory, `config.json`
- [ ] No remaining imports of deleted files (verified via `grep -r "from examples" src/`)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:
- Delete files: `run_evaluation_example.py`, `run_evaluation_example_simple.py`, `run_simple_agent_no_tools.py`, `run_simple_agent_system.py`, `run_simple_agent_tools.py`
- Delete directory: `src/examples/utils/` (contains 5 files)
- Delete config: `src/examples/config.json`
- Note: `src/examples/__init__.py` does not currently exist — create it only if needed by Feature 2 examples

**Files**:
- `src/examples/run_evaluation_example.py` (delete)
- `src/examples/run_evaluation_example_simple.py` (delete)
- `src/examples/run_simple_agent_no_tools.py` (delete)
- `src/examples/run_simple_agent_system.py` (delete)
- `src/examples/run_simple_agent_tools.py` (delete)
- `src/examples/utils/` (delete directory)
- `src/examples/config.json` (delete)

---

#### Feature 2: Create Modern Examples

**Description**: Replace outdated examples with minimal, self-contained demonstrations of Sprint 5-6 features using current APIs.

##### 2.1 Basic Evaluation Example

**Acceptance Criteria**:
- [ ] `basic_evaluation.py` demonstrates plugin-based evaluation with realistic paper/review data
- [ ] Uses current imports: `EvaluationPipeline`, `GraphTraceData`, `PeerReadPaper`
- [ ] Includes docstring: purpose, prerequisites, expected output
- [ ] Runs successfully with API key in `.env`
- [ ] Test verifies example runs without errors (mock external dependencies)

**Technical Requirements**:
- File: `src/examples/basic_evaluation.py` (~80 lines)
- Demonstrates: Tier 1-3 evaluation with synthetic `GraphTraceData`
- Mock strategy: Mock provider for Tier 2 LLM calls

**Files**:
- `src/examples/basic_evaluation.py` (new)
- `tests/examples/test_basic_evaluation.py` (new)

##### 2.2 Judge Settings Customization Example

**Acceptance Criteria**:
- [ ] `judge_settings_customization.py` shows `JudgeSettings` configuration
- [ ] Demonstrates: environment variable override, programmatic settings modification
- [ ] Shows: timeout adjustment, tier weight customization, provider selection
- [ ] Test verifies settings modifications work correctly

**Technical Requirements**:
- File: `src/examples/judge_settings_customization.py` (~60 lines)
- Imports: `JudgeSettings`, `EvaluationPipeline`

**Files**:
- `src/examples/judge_settings_customization.py` (new)
- `tests/examples/test_judge_settings_customization.py` (new)

##### 2.3 Engine Comparison Example

**Acceptance Criteria**:
- [ ] `engine_comparison.py` demonstrates comparing MAS results against CC results using `CCTraceAdapter`
- [ ] Prerequisites documented: collected CC artifacts via `scripts/collect-cc-traces/collect-cc-*.sh`
- [ ] Shows: loading CC artifacts, comparing multi-LLM MAS vs single-LLM MAS vs CC (optional) evaluation scores
- [ ] Test verifies adapter integration (mock artifact loading)

**Technical Requirements**:
- File: `src/examples/engine_comparison.py` (~100 lines)
- Imports: `CCTraceAdapter`, evaluation pipeline comparison utilities
- Clarifies comparison model: single-LLM MAS is the baseline; multi-LLM compositions and CC are compared against it

**Files**:
- `src/examples/engine_comparison.py` (new)
- `tests/examples/test_engine_comparison.py` (new)

##### 2.4 Examples Documentation

**Acceptance Criteria**:
- [ ] `src/examples/README.md` documents all examples with usage instructions
- [ ] Lists prerequisites: API keys, sample data requirements
- [ ] Integration guide: how examples relate to main CLI/GUI
- [ ] All examples use actual project imports (no external utility modules)
- [ ] `make validate` passes

**Technical Requirements**:
- File: `src/examples/README.md` (~40 lines)
- Lists: all 3 examples with one-line descriptions, prerequisites, integration points

**Files**:
- `src/examples/README.md` (new)

---

#### Feature 3: Update README for Sprint 6 Reality

**Description**: `README.md` shows version 3.3.0 (Sprint 5) but doesn't reflect Sprint 6 deliverables. Update status, feature list, and versions to match current implementation.

**Acceptance Criteria**:
- [ ] Version badge updated to 4.0.0
- [ ] "Current Release" section lists Sprint 6: benchmarking sweep, CC scripts, security fixes, test improvements
- [ ] "Next" section updated to Sprint 7 scope
- [ ] Quick Start commands verified working (review tools enabled by default)
- [ ] Examples section references `src/examples/README.md` instead of deleted files
- [ ] All referenced files/commands exist and work
- [ ] No broken links (verified via `make run_markdownlint`)
- [ ] CHANGELOG.md updated

**Technical Requirements**:
- Update version badge to 4.0.0
- Update "Current Release":
  ```markdown
  **Current Release**: Version 4.0.0 - Sprint 6 (Delivered)
  - Benchmarking infrastructure (MAS composition sweep with statistical analysis)
  - CC comparison engine (artifact collection scripts, adapter path fixes, paper extraction)
  - Security hardening (CVE mitigations, prompt sanitization, log/trace scrubbing)
  - Test quality (coverage 27%→60% on 5 critical modules, test audit execution)
  ```
- Replace examples references: `See [src/examples/README.md](src/examples/README.md)`

**Files**:
- `README.md` (edit)

---

#### Feature 4: Update Roadmap for Sprint 6 Completion

**Description**: `docs/roadmap.md` shows Sprint 6 as "Planned" — update to "Delivered" with Sprint 7 row added.

**Acceptance Criteria**:
- [ ] Sprint 6 row: status "Delivered", reference `PRD-Sprint6-Ralph.md`
- [ ] Sprint 7 row added: status "In Progress", reference `PRD-Sprint7-Ralph.md`
- [ ] Table chronology maintained (Sprint 1-6 delivered, Sprint 7 current)
- [ ] All PRD links valid
- [ ] CHANGELOG.md updated

**Technical Requirements**:
- Update table:
  ```markdown
  | **Sprint 6** | Delivered | Benchmarking infrastructure, CC comparison engine, security hardening, test quality | [PRD Sprint 6](PRD-Sprint6-Ralph.md) |
  | **Sprint 7** | In Progress | Documentation alignment, example modernization, test suite refinement | [PRD Sprint 7](PRD-Sprint7-Ralph.md) |
  ```

**Files**:
- `docs/roadmap.md` (edit)

---

#### Feature 5: Update Architecture Doc for Sprint 5-6 Features

**Description**: `docs/architecture.md` doesn't include Sprint 6 features. Add sections for benchmarking and security, update implementation status.

##### 5.1 Benchmarking Infrastructure Section

**Acceptance Criteria**:
- [ ] New section "Benchmarking Infrastructure (Sprint 6)" describes sweep architecture
- [ ] Documents: `SweepConfig`, `SweepRunner`, `SweepAnalysis` modules
- [ ] Explains: composition variations (2^3 default), CC headless integration, statistical aggregation

**Technical Requirements**:
- Section content (~30 lines):
  - Architecture: config → runner → (compositions × papers × repetitions) → analysis
  - CC integration: `claude -p` headless invocation
  - Output: `results.json` + `summary.md` with mean/stddev per metric

**Files**:
- `docs/architecture.md` (edit)

##### 5.2 Security Framework Section

**Acceptance Criteria**:
- [ ] New section "Security Framework (Sprint 6)" references MAESTRO review
- [ ] Documents: CVE mitigations, input sanitization layers, log scrubbing patterns
- [ ] References `SECURITY.md` for known advisories

**Technical Requirements**:
- Section content (~40 lines):
  - MAESTRO 7-layer coverage
  - CVE mitigations: URL allowlist (SSRF), scikit-learn upgrade (CVE-2024-5206)
  - Input sanitization: truncation (500/5000/50000 char limits) + XML delimiters
  - Log scrubbing: Logfire/Loguru pattern filtering (api_key, secret, token patterns)

**Files**:
- `docs/architecture.md` (edit)

##### 5.3 CC OTel Tracing Limitations and Analysis Doc Correction

**Description**: `docs/analysis/CC-agent-teams-orchestration.md` recommends "OTel → Phoenix" as the primary CC tracing approach and labels it "Recommended." Research confirms this is **partially misleading**: Claude Code's OTel support exports **metrics and logs only — not trace spans** (GitHub issues anthropics/claude-code#9584, #2090, both unresolved). The analysis doc's comparison table implies full tracing parity with PydanticAI Logfire, which is incorrect. The artifact-based approach (`claude -p --output-format json` → `collect-cc-*.sh` → `CCTraceAdapter`) remains the only viable method for obtaining tool-call-level data needed by Tier 3 graph analysis.

**Acceptance Criteria**:
- [ ] `docs/analysis/CC-agent-teams-orchestration.md` updated: OTel approach table corrected to show metrics/logs only, no trace spans
- [ ] Approach table adds "Trace spans" row showing: OTel (No — upstream limitation), Hooks (No), Artifact collection (Yes — via CCTraceAdapter)
- [ ] Recommendation section updated: artifact collection is primary for evaluation; OTel is supplementary for cost/token dashboards
- [ ] `.claude/settings.json` OTel vars annotated: currently disabled, enables cost/token metrics only when active
- [ ] Upstream limitation documented with references (GitHub #9584, #2090)
- [ ] `AGENT_LEARNINGS.md` updated with CC OTel limitation finding

**Technical Requirements**:
- In `docs/analysis/CC-agent-teams-orchestration.md`:
  - Update comparison table: add "Trace spans (tool calls, LLM spans)" row — No for OTel, No for Hooks, Yes for Artifact+CCTraceAdapter
  - Change recommendation from "OTel → Phoenix (Recommended)" to "Artifact Collection (Recommended for evaluation), OTel (Supplementary for cost metrics)"
  - Add upstream limitation note: CC exports OTel metrics (`cost_usd`, `input_tokens`, `output_tokens`, `duration_ms`) and log events, but NOT trace spans — feature requested in anthropics/claude-code#9584 (closed as dup of #2090, auto-closed by inactivity bot, not resolved)
  - Document what CC OTel log events actually contain (sample JSON from #2090)
- In `AGENT_LEARNINGS.md`: add "CC OTel Metrics vs Traces" pattern

**Files**:
- `docs/analysis/CC-agent-teams-orchestration.md` (edit — correct OTel approach table and recommendation)
- `AGENT_LEARNINGS.md` (edit — add CC OTel limitation pattern)

##### 5.4 Implementation Status Update

**Acceptance Criteria**:
- [ ] "Current Implementation" updated to Sprint 6 deliverables
- [ ] Timeline shows Sprint 6 delivered, Sprint 7 in progress
- [ ] All code references valid (files exist at mentioned paths)
- [ ] CHANGELOG.md updated

**Technical Requirements**:
- Update "Current Implementation (Sprint 6 - Delivered)":
  - Benchmarking sweep with `make sweep`
  - CC artifact collection via `scripts/collect-cc-traces/collect-cc-*.sh`
  - Security controls active (URL validation, prompt sanitization, log scrubbing)
  - Test quality: 5 critical modules at 60%+ coverage

**Files**:
- `docs/architecture.md` (edit)

---

#### Feature 6: Update Architecture Diagrams

**Description**: PlantUML diagrams don't reflect Sprint 6 changes. Update workflow diagrams with benchmarking pipeline and security boundaries.

##### 6.1 Benchmarking Sweep Diagram

**Acceptance Criteria**:
- [ ] New diagram: `metrics-eval-sweep.plantuml` shows benchmarking workflow
- [ ] Workflow: SweepConfig → SweepRunner → (compositions × papers × repetitions) → SweepAnalysis → output files
- [ ] Includes optional CC headless path: `claude -p` → artifacts → CCTraceAdapter → evaluation
- [ ] Renders without errors, PNGs generated (light/dark themes)

**Technical Requirements**:
- File: `docs/arch_vis/metrics-eval-sweep.plantuml` (~80 lines)
- Style: activity diagram or sequence diagram
- Generate: `./scripts/writeup/generate-plantuml-png.sh docs/arch_vis/metrics-eval-sweep.plantuml`

**Files**:
- `docs/arch_vis/metrics-eval-sweep.plantuml` (new)
- `assets/images/metrics-eval-sweep-light.png` (generated)
- `assets/images/metrics-eval-sweep-dark.png` (generated)

##### 6.2 Review Workflow Security Update

**Acceptance Criteria**:
- [ ] Updated diagram: `MAS-Review-Workflow.plantuml` includes security boundaries
- [ ] Shows: URL validation checkpoints, prompt sanitization before LLM calls, log scrubbing before trace export
- [ ] Annotations for MAESTRO layers
- [ ] Re-generated PNGs (light/dark themes)

**Technical Requirements**:
- Edit existing file, add security checkpoints as annotations or separate swimlanes
- MAESTRO layer labels at boundaries

**Files**:
- `docs/arch_vis/MAS-Review-Workflow.plantuml` (edit)
- `assets/images/MAS-Review-Workflow-light.png` (re-generated)
- `assets/images/MAS-Review-Workflow-dark.png` (re-generated)

##### 6.3 Diagram Documentation

**Acceptance Criteria**:
- [ ] `docs/arch_vis/README.md` updated with new diagram descriptions
- [ ] Diagrams referenced in `docs/architecture.md` and `README.md`
- [ ] All PlantUML sources render without errors
- [ ] CHANGELOG.md updated

**Files**:
- `docs/arch_vis/README.md` (edit)

---

#### Feature 7: Test Suite Strategic Refactoring

**Description**: Execute strategic test refactoring aligned with TDD principles — remove tests that don't prevent regressions, consolidate duplicates, ensure BDD structure.

##### 7.1 Consolidate Duplicate Tests

**Acceptance Criteria**:
- [ ] Composite scoring tests merged: 3 files → 1 (`test_composite_scorer.py`)
- [ ] Test organization: `TestBasicScoring`, `TestWeightRedistribution`, `TestEdgeCases` classes
- [ ] Original files deleted after merge
- [ ] Coverage maintained (no behavioral test loss)
- [ ] `make test_all` passes

**Technical Requirements**:
- Merge into `tests/evals/test_composite_scorer.py`:
  - `test_composite_scoring_scenarios.py`
  - `test_composite_scoring_interpretability.py`
  - `test_composite_scoring_edge_cases.py`
- Delete originals after merge

**Files**:
- `tests/evals/test_composite_scorer.py` (edit — consolidate)
- `tests/evals/test_composite_scoring_scenarios.py` (delete)
- `tests/evals/test_composite_scoring_interpretability.py` (delete)
- `tests/evals/test_composite_scoring_edge_cases.py` (delete)

##### 7.2 Remove Remaining Implementation-Detail Tests

**Description**: Sprint 6 STORY-015 (Test Audit Execution) deleted ~55 implementation-detail tests from 9 files. These three plugin test files were in scope but may retain residual isinstance/property tests that survived the audit. This sub-feature completes the cleanup for plugin test files specifically.

**Acceptance Criteria**:
- [ ] Plugin implementation tests removed from `test_plugin_*.py` files (any isinstance checks, property existence tests, default constant verifications remaining after Sprint 6 audit)
- [ ] Kept: behavioral tests (evaluate returns correct structure, error handling)
- [ ] `make coverage_all` shows no reduction in critical module coverage
- [ ] If no implementation-detail tests remain (Sprint 6 fully cleaned these), mark as verified-complete with no changes

**Technical Requirements**:
- Review and edit (verify Sprint 6 audit completeness, remove any residual):
  - `tests/judge/test_plugin_llm_judge.py` — remove property/isinstance tests if any remain
  - `tests/judge/test_plugin_traditional.py` — remove property/isinstance tests if any remain
  - `tests/judge/test_plugin_graph.py` — remove property/isinstance tests if any remain
- Keep: tests verifying `evaluate()` behavior, error handling, data flow

**Files**:
- `tests/judge/test_plugin_llm_judge.py` (edit)
- `tests/judge/test_plugin_traditional.py` (edit)
- `tests/judge/test_plugin_graph.py` (edit)

##### 7.3 FIXME Cleanup: Dead Code and Broken Test

**Acceptance Criteria**:
- [ ] Remove commented-out `error_handling_context` code blocks in `agent_system.py:459,518` and `orchestration.py:263` (3 FIXME markers with dead code)
- [ ] Fix `test_download_success_mocked` in `test_datasets_peerread.py:35` (FIXME: AttributeError on module)
- [ ] `make validate` passes

**Files**:
- `src/app/agents/agent_system.py` (edit — remove commented-out FIXME blocks)
- `src/app/agents/orchestration.py` (edit — remove commented-out FIXME block)
- `tests/data_utils/test_datasets_peerread.py` (edit — fix broken test)

##### 7.4 Add BDD Structure Documentation

**Acceptance Criteria**:
- [ ] Test structure template added to `tests/conftest.py`
- [ ] All remaining tests follow BDD: arrange/act/assert with comments
- [ ] Test docstrings added explaining: purpose, setup, expected behavior
- [ ] Mock strategy documented in test file headers
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:
- Add to `tests/conftest.py`:
  ```python
  # BDD Test Structure Template:
  # def test_behavior_under_condition():
  #     """Test that X happens when Y condition.
  #
  #     Setup: Create minimal fixtures
  #     Action: Invoke behavior
  #     Assert: Verify outcome
  #     """
  #     # Arrange
  #     ...
  #     # Act
  #     ...
  #     # Assert
  #     ...
  ```

**Files**:
- `tests/conftest.py` (edit)

---

#### Feature 8: Real-Time Debug Log in GUI App Page

**Description**: The App page debug log (`st.expander("Debug Log")`) currently collects log entries via `LogCapture` during agent execution but only renders them after completion (in the `finally` block). During execution the panel shows stale content. Replace the post-hoc rendering with a real-time streaming approach so users can monitor agent progress as it happens.

**Acceptance Criteria**:
- [ ] Debug log panel updates with new entries while agent execution is in progress
- [ ] Log entries appear within ~1 second of being emitted by `app.*` modules
- [ ] Color-coded level formatting (existing `format_logs_as_html` behavior) preserved
- [ ] Panel auto-scrolls to latest entry during streaming
- [ ] After execution completes, full log remains visible (no truncation)
- [ ] No performance degradation: Streamlit reruns kept to minimum (use `st.fragment` or container-based approach)
- [ ] Test verifies log entries are captured and rendered incrementally (mock execution with timed log emissions)
- [ ] Streamlit >= 1.33 confirmed in `pyproject.toml` (required for `st.fragment`)
- [ ] PeerRead debug log noise reduced: `_create_review_from_dict` aggregates missing optional fields into one line per review instead of one line per field (e.g., `"Paper 306: 9 optional fields missing (IMPACT, SUBSTANCE, ...), using UNKNOWN"`)
- [ ] Fix `st.text()` rendering raw Markdown: `run_app.py:235-238` uses `text()` (plain monospace) for strings containing `**bold**` markdown — replace with `st.markdown()` so formatting renders correctly. Audit other `st.text()` calls in GUI pages for same issue.
- [ ] `make validate` passes

**Technical Requirements**:
- **Prerequisite — background thread execution**: Streamlit cannot update UI while Python is blocked on `await main(...)`. Execution must move to `threading.Thread` so the render loop stays free. See AGENT_LEARNINGS.md "Streamlit Background Execution Strategy" for the established pattern (`threading.Thread` + synchronized session state writes for page-level survival)
- **Log noise fix**: In `datasets_peerread.py:_create_review_from_dict`, collect missing field names into a list, then emit a single `logger.debug(f"Paper {paper_id}: {len(missing)} optional fields missing ({', '.join(missing)}), using UNKNOWN")` instead of per-field logging
- Modify `LogCapture` to support a polling interface (e.g., `get_new_logs_since(index)` returning only entries added since last read). `LogCapture._buffer` is written from the worker thread, read from the Streamlit thread — use `threading.Lock` for safe access
- Use `st.fragment` (Streamlit 1.33+) with a polling loop (`time.sleep(1)` + `st.rerun()` scoped to the fragment) to re-render the log panel independently of the main page
- Preserve existing `_capture_execution_logs` for final state persistence (session survives page navigation)
- See **`_execute_query_background` Signature Convergence** in Notes for Ralph Loop — Features 8, 9, and 10 all modify this function

**Files**:
- `src/gui/utils/log_capture.py` (edit — add incremental read support)
- `src/gui/pages/run_app.py` (edit — streaming log render during execution)
- `src/app/data_utils/datasets_peerread.py` (edit — aggregate missing-field debug logs)
- `tests/gui/test_realtime_debug_log.py` (new)

---

#### Feature 9: Paper Selection Mode in GUI App Page

**Description**: The App page currently only offers a free-text query input. Users should be able to choose between free-form text input and selecting a pre-downloaded PeerRead paper from a dropdown — mirroring the CLI `--paper-id` flag. When a paper is selected, its abstract is displayed for confirmation before running.

##### 9.1 Input Mode Toggle

**Acceptance Criteria**:
- [ ] Radio button or toggle: "Free-form query" vs "Select a paper"
- [ ] Free-form mode: existing text input field (unchanged behavior)
- [ ] Paper mode: dropdown replaces text input; optional query override text field shown below (pre-filled with default review template, editable)
- [ ] Switching modes preserves state (query text survives toggle back)
- [ ] `paper_id` is passed to `main()` when in paper mode (enables `enable_review_tools=True` and evaluation pipeline)

**Technical Requirements**:
- Add `st.radio` with options `["Free-form query", "Select a paper"]`
- Store selection in `st.session_state.input_mode`
- When paper mode: pass `paper_id` to `_execute_query_background` → `main(paper_id=...)`. If user also provides a custom query, pass both (mirrors CLI behavior where `--paper-id` + query are independent)
- When free-form mode: pass `query` only (existing behavior, `paper_id=None`)
- `_execute_query_background` signature must add `paper_id: str | None = None` parameter (see **Signature Convergence** in Notes for Ralph Loop)

##### 9.2 Paper Dropdown with Available Papers

**Acceptance Criteria**:
- [ ] Dropdown lists all locally downloaded PeerRead papers
- [ ] `PeerReadReview` model coerces int review scores to str (fixes validation errors that silently drop papers with numeric `SOUNDNESS_CORRECTNESS`, `RECOMMENDATION`, etc. fields)
- [ ] Each option displays: paper ID and title (e.g., `"42 — Attention Is All You Need"`)
- [ ] Papers loaded via `PeerReadLoader.load_papers()` across configured venues/splits
- [ ] If no papers are downloaded, show: `"No papers downloaded yet. Use the Downloads page to fetch the PeerRead dataset."` with a button linking to the Downloads tab
- [ ] Selecting a paper stores `paper_id` in session state

**Technical Requirements**:
- **Review score coercion**: In `peerread_models.py`, add `BeforeValidator(str)` to numeric review fields (`SOUNDNESS_CORRECTNESS`, `ORIGINALITY`, `RECOMMENDATION`, `CLARITY`, `REVIEWER_CONFIDENCE`, `IMPACT`, `SUBSTANCE`) so int values from raw PeerRead JSON are coerced to str instead of failing validation
- Use `PeerReadLoader` to enumerate available papers: iterate `load_papers(venue, split)` for all configured venues/splits, collect `(paper_id, title)` pairs
- Cache paper list in `st.session_state.available_papers` (refresh on page load or via button)
- `st.selectbox` with `format_func` to display `f"{paper.paper_id} — {paper.title}"`
- Handle `FileNotFoundError` from `load_papers()` gracefully (dataset not downloaded yet)

##### 9.3 Abstract Preview on Paper Selection

**Acceptance Criteria**:
- [ ] When a paper is selected in the dropdown, its abstract is displayed below
- [ ] Abstract shown in a styled container (e.g., `st.info` or `st.markdown` with blockquote)
- [ ] Abstract updates immediately on dropdown selection change
- [ ] No abstract shown when in free-form mode or no paper selected

**Technical Requirements**:
- Read `paper.abstract` from the selected `PeerReadPaper` object (already loaded for dropdown)
- Display via `st.markdown(f"> {abstract}")` or `st.info(abstract)` below the dropdown
- No additional data loading needed — abstract is a field on `PeerReadPaper`

**Files**:
- `src/gui/pages/run_app.py` (edit — input mode toggle, paper dropdown, abstract preview)
- `src/app/data_models/peerread_models.py` (edit — add int→str coercion on review score fields)
- `tests/gui/test_paper_selection.py` (new — test dropdown population, paper_id passthrough, abstract display)

---

#### Feature 10: Editable Common Settings with Tooltips in GUI Settings Page

**Description**: The Settings page displays `CommonSettings` (log level, enable logfire, max content length) as read-only text. Make these editable with session state persistence and add tooltip descriptions (question-mark icon) for each setting explaining what it controls.

##### 10.1 Editable Common Settings Fields

**Acceptance Criteria**:
- [ ] Log Level: dropdown with options `["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]`
- [ ] Enable Logfire: checkbox (boolean toggle)
- [ ] Max Content Length: number input with min=1000, max=100000, step=1000
- [ ] Edited values stored in session state with `common_` prefix (e.g., `common_log_level`)
- [ ] Edited values passed to application execution (override `CommonSettings` defaults)
- [ ] Reset to Defaults button also resets common settings to `CommonSettings()` defaults
- [ ] `make validate` passes

**Technical Requirements**:
- Replace `st.text(f"Log Level: {common_settings.log_level}")` with `st.selectbox`
- Replace `st.text(f"Enable Logfire: ...")` with `st.checkbox`
- Replace `st.text(f"Max Content Length: ...")` with `st.number_input`
- Store overrides in session state with `common_` prefix; in the App page, build a `_build_common_settings_from_session()` helper (mirrors existing `_build_judge_settings_from_session()` pattern)
- **Runtime application** (three distinct mechanisms — do not conflate):
  - `log_level` → call `logger.remove()`/`logger.add()` with new level before execution
  - `max_content_length` → pass as a dedicated `max_content_length: int | None` kwarg to `main()` (distinct from `token_limit` which controls agent token budget, not content truncation); `main()` must thread it through to `_truncate_paper_content()` in `peerread_tools.py`
  - `enable_logfire` → gate `logfire.configure()` call (see Logfire consolidation below)
  - Note: `CommonSettings` is instantiated once at module level in `run_gui.py:48` — session state overrides must be applied at execution time, not by mutating the module-level instance
- `_execute_query_background` signature must also receive `common_*` overrides (see **Signature Convergence** in Notes for Ralph Loop)
- **Logfire setting consolidation**: `CommonSettings.enable_logfire` and `JudgeSettings.logfire_enabled` control overlapping behavior. Consolidate to a single `logfire_enabled` in `JudgeSettings` (which already has the setting) and deprecate `CommonSettings.enable_logfire`. Tooltip should explain: "Enables Logfire instrumentation for both logging transport and evaluation observability"
- Update `_render_reset_button` to also clear `common_*` session state keys

**Files**:
- `src/gui/pages/settings.py` (edit — replace read-only display with editable widgets)
- `src/gui/pages/run_app.py` (edit — read `common_*` session state and apply overrides before execution)

##### 10.2 Tooltip Descriptions for All Settings

**Acceptance Criteria**:
- [ ] Each setting field has a help icon (question mark) that shows a description on hover
- [ ] Tooltips are concise (1-2 sentences) and explain: what the setting controls, valid values, and effect
- [ ] Tooltips applied to both Common Settings and existing Judge Settings fields
- [ ] Streamlit native `help` parameter used (available on `st.selectbox`, `st.checkbox`, `st.number_input`, `st.text_input`, `st.slider`)

**Technical Requirements**:
- Use Streamlit's built-in `help` parameter on input widgets: `st.selectbox("Log Level", ..., help="Controls verbosity...")`
- Tooltip text for Common Settings:
  - Log Level: `"Controls logging verbosity for app.* modules. DEBUG shows all messages, ERROR shows only errors. Env var: EVAL_LOG_LEVEL"`
  - Enable Logfire: `"Enables Logfire observability transport for loguru logs. Requires Logfire credentials. Env var: EVAL_ENABLE_LOGFIRE"`
  - Max Content Length: `"Maximum character length for paper content passed to LLM agents. Longer papers are truncated. Env var: EVAL_MAX_CONTENT_LENGTH"`
- Add `help` parameter to existing Judge Settings widgets (tier timeouts, composite thresholds, Tier 2 model fields)
- `make validate` passes (covered by Feature 10.1 AC)
- CHANGELOG.md updated (covered by Feature 10.1 AC)

**Files**:
- `src/gui/pages/settings.py` (edit — add `help=` parameter to all input widgets)
- `tests/gui/test_editable_common_settings.py` (new — test widget rendering, session state persistence, reset behavior)

---

#### Feature 11: Unified Provider Configuration for MAS and Judge

**Description**: The MAS chat provider and judge (Tier 2) provider are currently configured through different mechanisms with inconsistent naming. The judge defaults to `"openai"` regardless of the MAS provider. Unify provider configuration so the judge defaults to the MAS provider, both can be independently overridden, and naming is consistent across CLI, sweep, and GUI.

**Current state**:
- `run_cli.py`: `--chat-provider` (MAS only; no judge override)
- `run_sweep.py`: `--provider` (MAS only; inconsistent name; no judge override)
- `JudgeSettings.tier2_provider` defaults to `"openai"` — independent from MAS provider
- `"auto"` special value already exists in `LLMJudgeEngine` to inherit MAS provider, but is not the default

##### 11.1 Judge Defaults to MAS Chat Provider

**⚠️ Breaking change**: Users relying on the previous default (`openai/gpt-4o-mini` with `OPENAI_API_KEY`) will silently switch to their MAS provider (default: `github/gpt-4o-mini`) after this change. Same model family, different API endpoint and billing. To retain previous behavior, set `JUDGE_TIER2_PROVIDER=openai` explicitly.

**Acceptance Criteria**:
- [ ] `JudgeSettings.tier2_provider` default changed from `"openai"` to `"auto"`
- [ ] When `tier2_provider="auto"`, judge inherits the MAS `chat_provider` at runtime (existing `LLMJudgeEngine` logic — no new code required)
- [ ] `JUDGE_TIER2_PROVIDER` env var still overrides the default
- [ ] Migration log emitted at startup when `"auto"` resolves to a different provider than `"openai"`: `logger.info("Judge provider: auto → {resolved}")`
- [ ] Existing tests updated to reflect new default
- [ ] Fallback chain in `llm_evaluation_managers.py:112` fixed: when `tier2_provider="auto"`, fallback uses resolved MAS provider instead of hardcoded `openai→github` (fixes FIXME Sprint5-STORY-001)
- [ ] `make validate` passes

**Technical Requirements**:
- Edit `src/app/judge/settings.py` line 74: `tier2_provider: str = Field(default="auto")`
- Fix `_get_fallback_provider()` in `llm_evaluation_managers.py`: use resolved `chat_provider` when `tier2_provider="auto"` instead of hardcoded `"openai"` → `"github"` chain
- No changes to `LLMJudgeEngine` — the `"auto"` path already exists
- `tier2_fallback_provider` default remains `"github"` (unchanged)

**Files**:
- `src/app/judge/settings.py` (edit — change `tier2_provider` default to `"auto"`)
- `src/app/judge/llm_evaluation_managers.py` (edit — fix fallback chain to respect resolved provider)
- `tests/judge/` (edit — update any tests asserting `tier2_provider == "openai"`)

##### 11.2 Consistent Naming: `--chat-provider`, `--judge-provider`, and `--paper-ids`

**Acceptance Criteria**:
- [ ] `run_cli.py`: `--paper-number` renamed to `--paper-id` (accepts string IDs like `"1105.1072"`); existing `--chat-provider` unchanged; new `--judge-provider` and `--judge-model` args added
- [ ] `run_sweep.py`: `--paper-numbers` renamed to `--paper-ids` (accepts comma-separated string IDs, no `int()` cast); `--provider` renamed to `--chat-provider` for consistency; new `--judge-provider` and `--judge-model` args added
- [ ] `SweepConfig.paper_numbers: list[int]` renamed to `paper_ids: list[str]` (fixes crash on arxiv IDs like `"1105.1072"` that cannot be cast to int)
- [ ] `SweepRunner` method signatures updated: `paper_id: str` replaces `paper_number: int`
- [ ] `main()` parameter renamed: `paper_id: str | None` replaces `paper_number: str | None`
- [ ] `SweepConfig` adds `judge_provider: str` and `judge_model: str | None` fields
- [ ] JSON sweep config accepts `"chat_provider"` key (rename from `"provider"` for consistency) and `"paper_ids"` (rename from `"paper_numbers"`)
- [ ] Both args documented in `--help` output for both entry points
- [ ] `make sweep ARGS="--help"` shows all new args (Makefile `$(ARGS)` passthrough already exists — no Makefile change needed)
- [ ] `make validate` passes

**Note — partial implementation already staged**: `run_sweep.py` and `SweepConfig` already have `--provider`/`chat_provider` staged. STORY-012 must build on top: rename `--provider` → `--chat-provider`, add `--judge-provider`/`--judge-model`. Do not treat staged code as complete.

**Technical Requirements**:
- `run_cli.py`: rename `--paper-number` → `--paper-id`; add `--judge-provider` with `choices=["auto"] + list(PROVIDER_REGISTRY.keys())` and `--judge-model`; construct `JudgeSettings(tier2_provider=judge_provider, tier2_model=judge_model)` when provided and pass as `judge_settings=` to `main()`
- `run_sweep.py`: rename `--paper-numbers` → `--paper-ids` (remove `int()` cast, keep as `str`); rename `--provider` → `--chat-provider` (keep `dest="chat_provider"`); add `--judge-provider` and `--judge-model`
- `SweepConfig`: rename `paper_numbers: list[int]` → `paper_ids: list[str]`; add `judge_provider: str = Field(default="auto")` and `judge_model: str | None = Field(default=None)`; `SweepRunner._run_single_evaluation()` must build `JudgeSettings` from these fields
- `SweepRunner`: rename `paper_number: int` → `paper_id: str` in `_run_single_evaluation()` and `_invoke_cc_baseline()` signatures; remove `str(paper_number)` cast when calling `main()`. Note: `_invoke_cc_baseline()` → `_invoke_cc_comparison()` rename is handled by STORY-013 (Feature 12.1) which rewrites this method
- `main()` in `app.py`: rename parameter `paper_number` → `paper_id`; update all internal references
- `evaluation_runner.py`: rename `paper_number` → `paper_id` in `run_evaluation_if_enabled()` signature
- JSON config key renames: `"provider"` → `"chat_provider"`, `"paper_numbers"` → `"paper_ids"` (backward-compat read of old keys with deprecation log)
- GUI judge provider: already covered by Feature 10.1 — no separate GUI story needed

**Files**:
- `src/run_cli.py` (edit — rename `--paper-number` → `--paper-id`, add `--judge-provider`, `--judge-model`)
- `src/run_sweep.py` (edit — rename `--paper-numbers` → `--paper-ids`, `--provider` → `--chat-provider`, add `--judge-provider`, `--judge-model`)
- `src/app/app.py` (edit — rename `paper_number` → `paper_id` in `main()` and `_prepare_query()`)
- `src/app/judge/evaluation_runner.py` (edit — rename `paper_number` → `paper_id`)
- `src/app/benchmark/sweep_config.py` (edit — rename `paper_numbers` → `paper_ids` with `list[str]`, add `judge_provider`, `judge_model`)
- `src/app/benchmark/sweep_runner.py` (edit — rename params, remove int cast, thread `judge_provider`/`judge_model`)
- `tests/benchmark/test_sweep_config.py` (edit — new fields)
- `tests/benchmark/test_sweep_runner.py` (edit — judge_settings passthrough)
- `tests/cli/test_run_cli.py` (edit or new — `--judge-provider` arg parsing)

---

#### Feature 12: Claude Code as Comparison Engine

**Description**: The benchmarking model uses **single-LLM MAS as the baseline** — one provider for all agents. Multi-LLM MAS compositions (varying providers per agent) are compared against this baseline. CC (Claude Code) is an **optional comparison engine** — single LLM with a different orchestration model — not a baseline. The CC headless execution path (`claude -p`, artifact collection via `CCTraceAdapter`) already exists in `main()` via `cc_solo_dir`/`cc_teams_dir`/`cc_teams_tasks_dir` params and `--cc-baseline` in the sweep. However it is not a first-class selectable option. Add an `--engine` flag so users can choose between MAS (PydanticAI agents) and CC as the execution engine across CLI, sweep, and GUI.

**Current state**:
- `main()` has `cc_solo_dir`, `cc_teams_dir`, `cc_teams_tasks_dir` — used to load pre-collected CC artifacts
- `run_sweep.py` has `--cc-baseline` flag (misnomer — CC is a comparison, not a baseline; loads artifacts from default paths)
- No CLI flag to run CC headless inline (invoke `claude -p` and capture output)
- No GUI option to switch engine

**Comparison model**:
- **Baseline**: Single-LLM MAS (one provider for all 4 agents) — the reference point
- **Multi-LLM MAS**: Compositions with mixed providers per agent — compared against single-LLM baseline
- **CC (optional)**: Claude Code headless — single LLM, different orchestration — compared against both MAS variants

##### 12.1 `--engine` Flag in CLI and Sweep

**⚠️ Breaking change**: `--cc-baseline` flag removed from `run_sweep.py` and `cc_baseline_enabled` removed from `SweepConfig` (CC is a comparison engine, not a baseline). Users of `--cc-baseline` must switch to `--engine=cc`. This was an internal CLI with no stable contract, but existing sweep configs referencing `cc_baseline_enabled` will need updating.

**Acceptance Criteria**:
- [ ] `run_cli.py` accepts `--engine=mas` (default) or `--engine=cc`
- [ ] `run_sweep.py` accepts `--engine=mas` (default) or `--engine=cc`; `--cc-baseline` removed (replaced by `--engine=cc`)
- [ ] `--engine=mas`: existing MAS execution path (unchanged)
- [ ] `--engine=cc`: invokes CC headless (`claude -p "..."`) via `subprocess.run()`, collects artifacts, passes artifact dirs to `main(cc_solo_dir=..., cc_teams_dir=..., cc_teams_tasks_dir=...)` for evaluation
- [ ] `--engine=cc` with `claude` CLI not found: raises clear error at arg-parse time (`shutil.which("claude")` check)
- [ ] `--engine=cc` subprocess failure handling: non-zero exit code raises `RuntimeError` with stderr content; `subprocess.TimeoutExpired` caught and re-raised with context; malformed JSON output from `claude -p --output-format json` raises `ValueError` with parsing details
- [ ] `--engine` documented in `--help` output for both entry points
- [ ] Mutual exclusivity enforced: `--engine=cc` with MAS-specific flags (e.g., `--include-researcher`) raises a clear error
- [ ] `make validate` passes
- [ ] Sweep rate-limit resilience: `SweepRunner._run_single_evaluation()` retries on HTTP 429 / rate-limit errors with exponential backoff (max 3 retries, initial delay from `SweepConfig.retry_delay_seconds`). After max retries, logs error and continues to next evaluation (does not abort sweep)
- [ ] Incremental result persistence: `SweepRunner` writes partial `results.json` after each successful evaluation, so a crash or kill mid-sweep preserves completed results

**Technical Requirements**:
- `run_cli.py`: add `--engine` with `choices=["mas", "cc"]`, `default="mas"`. When `cc`: check `shutil.which("claude")` at arg-parse time and fail fast; invoke `claude -p "{query}" --output-format json` via `subprocess.run(timeout=300)`; store artifacts under `--output-dir` (not `tempfile`) so CLI users can inspect them after the run
- `run_sweep.py`: same `--engine` flag; `SweepConfig` adds `engine: str = Field(default="mas")`; sweep CC artifacts stored under `config.output_dir / "cc_artifacts" / f"{paper_id}_{repetition}"` and cleaned up after all repetitions (high volume)
- Delete `--cc-baseline` from `run_sweep.py` and `cc_baseline_enabled` from `SweepConfig` (replaced entirely by `--engine=cc`). Rename `_invoke_cc_baseline()` → `_invoke_cc_comparison()` in `SweepRunner`
- Subprocess error handling: wrap `subprocess.run()` in try/except — catch `TimeoutExpired` (re-raise with context), check `returncode != 0` (raise `RuntimeError` with stderr), parse JSON output with `json.loads()` in try/except `JSONDecodeError` (raise `ValueError` with raw output snippet)
- Reuse existing `CCTraceAdapter` for artifact parsing — no new adapter code
- **Rate-limit error propagation fix** (prerequisite for retry): `_handle_model_http_error()` in `agent_system.py:478` currently calls `raise SystemExit(1)` on HTTP 429 — this kills the process and bypasses all caller error handling (`SystemExit` inherits `BaseException`, not `Exception`). Change to `raise error` (re-raise `ModelHTTPError`) so callers decide recovery policy. Update `run_manager()` to catch `ModelHTTPError` with status 429 and raise `SystemExit(1)` there (preserves CLI behavior). This moves the process-exit decision from the utility function to the caller.
- Rate-limit retry: in `_run_single_evaluation()`, catch `SystemExit` and `ModelHTTPError` (both needed during transition), retry with exponential backoff (`retry_delay_seconds * 2^attempt`), max 3 attempts. `SweepConfig` adds `retry_delay_seconds: float = Field(default=5.0)`. After exhausting retries, return `None` (skip this evaluation, don't abort the sweep)
- Incremental persistence: split `_save_results()` into `_save_results_json()` (writes only `results.json` — cheap, called after each successful `self.results.append(...)`) and `_save_results()` (writes both `results.json` and `summary.md` via `SweepAnalyzer` — called once at the end). Running statistical analysis after every single evaluation is wasteful and produces meaningless 1-sample summaries mid-sweep

**Files**:
- `src/run_cli.py` (edit — add `--engine` flag)
- `src/run_sweep.py` (edit — add `--engine` flag, remove `--cc-baseline`)
- `src/app/benchmark/sweep_config.py` (edit — add `engine` field, remove `cc_baseline_enabled`)
- `src/app/benchmark/sweep_runner.py` (edit — branch on `engine`, remove cc_baseline path, add retry + incremental save)
- `src/app/agents/agent_system.py` (edit — `_handle_model_http_error` re-raises instead of `SystemExit`)
- `tests/cli/test_run_cli_engine.py` (new — `--engine` arg parsing, CC unavailable error)
- `tests/benchmark/test_sweep_runner.py` (edit — engine branching, remove cc_baseline tests, retry behavior)

##### 12.2 Engine Selector in GUI

**Acceptance Criteria**:
- [ ] Engine selector placed on **App page** (not Settings): radio with `["MAS (PydanticAI)", "Claude Code"]` — engine choice is per-run, not persistent config; it directly controls which controls are visible on the same page
- [ ] When CC selected: MAS-specific agent toggles (Researcher, Analyst, Synthesiser) are hidden or disabled with a note
- [ ] When CC selected: CC availability warning shown if `claude` CLI not found
- [ ] Engine selection stored in `st.session_state.engine`
- [ ] App page passes `engine` to execution; when `cc`, invokes CC headless path (same subprocess approach as 12.1)
- [ ] CC orchestration graph visualized on Agent Graph page after CC execution completes: `CCTraceAdapter.parse()` → `GraphTraceData` → `build_interaction_graph()` → `render_agent_graph()` (existing pyvis pipeline)
- [ ] CC `coordination_events` populated from teams mode `inboxes/*.json` messages (currently a stub returning `[]`)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:
- Engine selector on App page: `st.radio("Execution Engine", ["MAS (PydanticAI)", "Claude Code"], help="...")`
- CC availability: compute once via `st.session_state.setdefault("cc_available", shutil.which("claude") is not None)` — do not call `shutil.which()` on every re-render; display `st.warning(...)` when `not st.session_state.cc_available`
- Disable MAS agent toggles with `st.checkbox(..., disabled=(engine == "cc"))` when CC selected
- App page execution: same subprocess + artifact path pattern as 12.1
- CC graph visualization: after CC execution, parse artifacts via `CCTraceAdapter.parse()` → store `GraphTraceData` in session state → Agent Graph page renders via existing `build_interaction_graph()` → `render_agent_graph()` path (pyvis). No new visualization library needed.
- Fix `CCTraceAdapter._extract_coordination_events()` stub: populate `coordination_events` from teams `inboxes/*.json` (messages already loaded into `agent_interactions` — extract delegation/coordination events as a subset)

**Files**:
- `src/gui/pages/run_app.py` (edit — engine selector, CC availability cache, branch execution, store CC graph data)
- `src/app/judge/cc_trace_adapter.py` (edit — populate `coordination_events` from inbox messages)
- `tests/gui/test_engine_selector.py` (new)

---

## Non-Functional Requirements

- All examples run successfully with minimal setup (API key in `.env`)
- Documentation updates must not break existing links (verified via markdownlint)
- PlantUML diagrams render without errors using project scripts
- Test refactoring maintains or improves coverage percentages
- No new pip dependencies
- Streamlit >= 1.33 required (for `st.fragment` in Feature 8) — verify pinned version in `pyproject.toml`

## Out of Scope

- Rewriting evaluation pipeline
- Adding new evaluation metrics
- New Streamlit pages or full GUI redesigns (Features 8-10 enhance existing pages only)
- Test framework migration (pytest/Hypothesis stays)
- Comprehensive docstring coverage for all modules
- Sprint 6 feature implementation (assumes delivered)
- Live CC OTel trace piping to Phoenix — CC exports metrics/logs only, not trace spans (upstream limitation: anthropics/claude-code#9584, #2090). Artifact collection via `claude -p --output-format json` + `CCTraceAdapter` remains the evaluation approach. Revisit if Anthropic ships `OTEL_TRACES_EXPORTER` support.
- Enabling CC OTel metrics in `.claude/settings.json` — supplementary cost/token data only, does not feed evaluation pipeline metrics. Enable manually if Phoenix cost dashboard desired.

- Align `type` vs `node_type` node attribute between `graph_analysis.py:export_trace_to_networkx()` and `agent_graph.py:render_agent_graph()` — latent mismatch; Sprint 7 avoids it by routing through `build_interaction_graph()`, but direct callers of `export_trace_to_networkx()` get wrong visual node types. Sprint 8.

**Deferred from Sprint 6 "Out of Scope → Sprint 7+" (explicitly deferred to Sprint 8+):**

- Centralized tool registry with module allowlist (MAESTRO L7.2) — architectural improvement, lower priority than current feature work
- Plugin tier validation at registration (MAESTRO L7.1) — prevents tier mismatch, deferred pending plugin system stabilization
- Error message sanitization / information leakage prevention — low-risk given log scrubbing already active (Sprint 6 Feature 12)
- GraphTraceData construction simplification (replace manual `.get()` with `model_validate()`) — code quality improvement, no user impact
- Timeout bounds enforcement (min/max limits on user-configurable timeouts) — low risk, current validation via Pydantic Field constraints is sufficient
- Configuration path traversal protection (validate config paths against allowlist) — low risk in current deployment (local-only CLI/GUI)
- BDD scenario tests for evaluation pipeline (end-to-end user workflow tests) — deferred; pytest with arrange/act/assert is sufficient for Sprint 7
- Time tracking consistency across tiers (standardize timing pattern) — cosmetic improvement, no functional impact
- Hardcoded settings audit (module-level constants → Pydantic BaseSettings) — deferred pending Feature 10 completion, which addresses the highest-value settings first

**Deferred from Sprint 5 "Out of Scope" (explicitly deferred to Sprint 8+):**

- Tier 1 reference comparison fix (all-1.0 self-comparison scores) — requires ground-truth review integration, separate feature
- Cerebras-specific prompt optimization for structured output validation retries — provider-specific, low priority

---

## Notes for Ralph Loop

**Priority Order:**
- **P0**: STORY-001 (remove examples), STORY-002 (create examples)
- **P1**: STORY-003 (README), STORY-004 (roadmap), STORY-005 (architecture)
- **P1**: STORY-011 (judge defaults), STORY-012 (provider naming + args)
- **P1**: STORY-008 (real-time debug log), STORY-009 (paper selection), STORY-010 (editable settings)
- **P1**: STORY-013 (CC engine CLI/sweep), STORY-013b (sweep resilience), STORY-014 (CC engine GUI)
- **P2**: STORY-006 (diagrams)
- **P3**: STORY-007 (test refactoring)

**Dependencies:**
- STORY-002 depends on STORY-001 (clean slate before building)
- STORY-006 should follow STORY-005 (diagrams illustrate text)
- STORY-007 independent (can run parallel with docs)
- STORY-008, STORY-009, STORY-010 independent of each other (can run parallel)
- STORY-012 depends on STORY-011 (rename args after default is settled)
- STORY-013 independent of STORY-011/012 (engine selection orthogonal to provider config)
- STORY-013b depends on STORY-013 (resilience layered on top of engine selection)
- STORY-007 and STORY-013b both edit `agent_system.py` (different functions: STORY-007 removes FIXME dead code at lines 459/518, STORY-013b changes `_handle_model_http_error` at line 478 — no conflict, but coordinate if running in parallel)
- STORY-014 depends on STORY-013 (GUI reuses CLI engine logic)

**`_execute_query_background` Signature Convergence:**
Features 8, 9, and 10 all modify `_execute_query_background()` in `src/gui/pages/run_app.py`. Coordinate signature changes to avoid merge conflicts:
- Feature 8 adds threading/streaming support (return type, callback pattern)
- Feature 9 adds `paper_id: str | None = None`
- Feature 10 adds `common_*` override kwargs (`log_level`, `max_content_length`, `logfire_enabled`)
- Feature 12.2 adds `engine: str = "mas"` (branches execution path)
Recommended approach: implement Feature 8's signature first (includes threading refactor), then Features 9 and 10 add parameters on top. If executing in parallel, agree on final signature upfront.

**Mandatory Practices:** See Development Methodology section above. TDD workflow, `make validate`, mocking, behavioral testing, and docstrings are non-negotiable for all stories.

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (15 stories total):

- **Feature 1 (Remove Outdated Examples)** → STORY-001: Delete Sprint 1-era examples and generic PydanticAI tutorials
- **Feature 2 (Create Modern Examples)** → STORY-002: Build evaluation, settings, and engine comparison examples with tests and README (depends: STORY-001)
- **Feature 3 (Update README)** → STORY-003: Reflect Sprint 6 deliverables, version 4.0.0, new examples
- **Feature 4 (Update Roadmap)** → STORY-004: Mark Sprint 6 delivered, add Sprint 7 row
- **Feature 5 (Update Architecture)** → STORY-005: Add benchmarking/security sections, correct CC OTel analysis doc, update status
- **Feature 6 (Update Diagrams)** → STORY-006: Create sweep diagram, update workflow with security (depends: STORY-005)
- **Feature 7 (Test Refactoring)** → STORY-007: Consolidate composite tests, remove residual implementation-detail tests, clean up FIXME dead code, fix broken peerread test, add BDD template
- **Feature 8 (Real-Time Debug Log)** → STORY-008: Stream debug log entries during agent execution instead of post-completion dump
- **Feature 9 (Paper Selection Mode)** → STORY-009: Add paper dropdown with ID/title display and abstract preview alongside free-form input
- **Feature 10 (Editable Common Settings)** → STORY-010: Make log level, logfire, max content length editable with tooltip descriptions
- **Feature 11.1 (Judge Default Provider)** → STORY-011: Change `tier2_provider` default to `"auto"` to inherit MAS chat provider, fix fallback chain hardcoded provider bug
- **Feature 11.2 (Consistent Naming + Args)** → STORY-012: Rename `--paper-number(s)` → `--paper-id(s)` with `str` type (fixes arxiv ID crash), rename sweep `--provider` → `--chat-provider`, add `--judge-provider`/`--judge-model`, rename `paper_number` → `paper_id` across `main()`/sweep/runner (depends: STORY-011)
- **Feature 12.1 (CC Comparison Engine CLI/Sweep)** → STORY-013: Add `--engine=mas|cc` flag, remove `--cc-baseline`, rename `_invoke_cc_baseline` → `_invoke_cc_comparison`, subprocess error handling
- **Feature 12.1 (Sweep Resilience)** → STORY-013b: Rate-limit retry with backoff, `SystemExit` → re-raise fix, incremental result persistence (depends: STORY-013)
- **Feature 12.2 (CC Comparison Engine GUI)** → STORY-014: Add engine selector to GUI, CC orchestration graph, CC availability check, disable MAS-specific controls (depends: STORY-013)
