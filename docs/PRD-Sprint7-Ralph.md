---
title: Product Requirements Document: Agents-eval Sprint 7
version: 1.0
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 6 delivered: benchmarking infrastructure, CC baseline completion, security hardening (CVE mitigations, input sanitization, log scrubbing), test quality improvements.

**Sprint 7 Focus**: Documentation alignment, example modernization, test suite refinement.

**Development Approach**: TDD workflow (RED → GREEN → REFACTOR). All code changes require tests first. Use `testing-python` skill for test creation, `implementing-python` for implementation. Run `make validate` before completing any story.

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
- Keep: `src/examples/__init__.py` (Python module structure)

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

##### 2.3 CC Baseline Comparison Example

**Acceptance Criteria**:
- [ ] `cc_baseline_comparison.py` demonstrates `CCTraceAdapter` usage
- [ ] Prerequisites documented: collected artifacts via `scripts/collect-cc-traces/collect-cc-*.sh`
- [ ] Shows: loading CC artifacts, comparing MAS vs CC results
- [ ] Test verifies adapter integration (mock artifact loading)

**Technical Requirements**:
- File: `src/examples/cc_baseline_comparison.py` (~100 lines)
- Imports: `CCTraceAdapter`, `baseline_comparison.compare()`

**Files**:
- `src/examples/cc_baseline_comparison.py` (new)
- `tests/examples/test_cc_baseline_comparison.py` (new)

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
  - CC baseline completion (artifact collection scripts, adapter path fixes, paper extraction)
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
  | **Sprint 6** | Delivered | Benchmarking infrastructure, CC baseline completion, security hardening, test quality | [PRD Sprint 6](PRD-Sprint6-Ralph.md) |
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

##### 7.1 Remove Orphaned Tests

**Acceptance Criteria**:
- [ ] `tests/cc_otel/` directory deleted (module removed Sprint 6 STORY-006)
- [ ] No remaining references to cc_otel tests
- [ ] `make test_all` passes

**Technical Requirements**:
- Delete: `tests/cc_otel/test_cc_otel_config.py`, `tests/cc_otel/test_cc_otel_instrumentation.py`

**Files**:
- `tests/cc_otel/` (delete directory)

##### 7.2 Consolidate Duplicate Tests

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

##### 7.3 Remove Implementation-Detail Tests

**Acceptance Criteria**:
- [ ] Plugin implementation tests removed from `test_plugin_*.py` files
- [ ] Deleted: isinstance checks, property existence tests, default constant verifications
- [ ] Kept: behavioral tests (evaluate returns correct structure, error handling)
- [ ] `make coverage_all` shows no reduction in critical module coverage

**Technical Requirements**:
- Review and edit:
  - `tests/judge/test_plugin_llm_judge.py` — remove property/isinstance tests
  - `tests/judge/test_plugin_traditional.py` — remove property/isinstance tests
  - `tests/judge/test_plugin_graph.py` — remove property/isinstance tests
- Keep: tests verifying `evaluate()` behavior, error handling, data flow

**Files**:
- `tests/judge/test_plugin_llm_judge.py` (edit)
- `tests/judge/test_plugin_traditional.py` (edit)
- `tests/judge/test_plugin_graph.py` (edit)

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

## Non-Functional Requirements

- All examples run successfully with minimal setup (API key in `.env`)
- Documentation updates must not break existing links (verified via markdownlint)
- PlantUML diagrams render without errors using project scripts
- Test refactoring maintains or improves coverage percentages
- No new pip dependencies

## Out of Scope

- Rewriting evaluation pipeline
- Adding new evaluation metrics
- GUI redesign or new Streamlit pages
- Test framework migration (pytest/Hypothesis stays)
- Comprehensive docstring coverage for all modules
- Updating UserStory.md
- Sprint 6 feature implementation (assumes delivered)
- BDD scenario tests (pytest with arrange/act/assert is sufficient)
- Live CC OTel trace piping to Phoenix — CC exports metrics/logs only, not trace spans (upstream limitation: anthropics/claude-code#9584, #2090). Artifact collection via `claude -p --output-format json` + `CCTraceAdapter` remains the evaluation approach. Revisit if Anthropic ships `OTEL_TRACES_EXPORTER` support.
- Enabling CC OTel metrics in `.claude/settings.json` — supplementary cost/token data only, does not feed evaluation pipeline metrics. Enable manually if Phoenix cost dashboard desired.

---

## Notes for Ralph Loop

**Priority Order:**
- **P0**: STORY-001 (remove examples), STORY-002 (create examples)
- **P1**: STORY-003 (README), STORY-004 (roadmap), STORY-005 (architecture)
- **P2**: STORY-006 (diagrams)
- **P3**: STORY-007 (test refactoring)

**Dependencies:**
- STORY-002 depends on STORY-001 (clean slate before building)
- STORY-006 should follow STORY-005 (diagrams illustrate text)
- STORY-007 independent (can run parallel with docs)

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (7 stories total):

- **Feature 1 (Remove Outdated Examples)** → STORY-001: Delete Sprint 1-era examples and generic PydanticAI tutorials
- **Feature 2 (Create Modern Examples)** → STORY-002: Build evaluation/settings/CC examples with tests and README (depends: STORY-001)
- **Feature 3 (Update README)** → STORY-003: Reflect Sprint 6 deliverables, version 4.0.0, new examples
- **Feature 4 (Update Roadmap)** → STORY-004: Mark Sprint 6 delivered, add Sprint 7 row
- **Feature 5 (Update Architecture)** → STORY-005: Add benchmarking/security sections, correct CC OTel analysis doc, update status
- **Feature 6 (Update Diagrams)** → STORY-006: Create sweep diagram, update workflow with security (depends: STORY-005)
- **Feature 7 (Test Refactoring)** → STORY-007: Delete cc_otel tests, consolidate composite tests, remove implementation tests, add BDD template
