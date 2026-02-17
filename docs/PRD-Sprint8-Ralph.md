---
title: Product Requirements Document - Agents-eval Sprint 8
description: Report generation (CLI + GUI), graph attribute alignment, security hardening (MAESTRO), code quality improvements, and deferred fixes.
version: 0.1
created: 2026-02-17
updated: 2026-02-17
status: draft
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 7 delivered: documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

**Sprint 8 Focus**: Report generation with actionable suggestions, graph attribute alignment, security hardening, code quality improvements.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Report Generation in CLI and GUI

**Description**: After evaluation completes, users should be able to generate a structured report that summarizes evaluation results and suggests improvements. The report synthesizes Tier 1/2/3 scores, highlights weaknesses (low-scoring dimensions), and proposes actionable content suggestions (e.g., "Tier 1 BLEU score low — review lacks specific technical terminology from the paper abstract"). Available via `--generate-report` in CLI and a "Generate Report" button in the GUI.

##### 1.1 CLI Report Generation

**Acceptance Criteria**:
- [ ] `run_cli.py` accepts `--generate-report` flag (requires evaluation to have run, incompatible with `--skip-eval`)
- [ ] Report includes: executive summary, per-tier score breakdown, identified weaknesses, actionable suggestions
- [ ] Suggestions are grounded in evaluation data (reference specific metric scores and thresholds)
- [ ] Report output as Markdown file in `--output-dir` (default: `results/reports/<timestamp>.md`)
- [ ] `make validate` passes

**Technical Requirements**:
- TBD — requires design phase to determine report structure, suggestion generation approach (rule-based vs LLM-assisted), and integration with `CompositeResult`

**Files**:
- `src/run_cli.py` (edit — add `--generate-report` flag)
- `src/app/reports/` (new — report generation module)
- TBD

##### 1.2 GUI Report Generation

**Acceptance Criteria**:
- [ ] "Generate Report" button on App page, enabled after evaluation completes
- [ ] Report displayed inline (Markdown rendered via `st.markdown`) with download option
- [ ] Same report content as CLI (shared generation logic)
- [ ] `make validate` passes

**Technical Requirements**:
- TBD — reuse CLI report generation module, render in Streamlit

**Files**:
- `src/gui/pages/run_app.py` (edit — add report button and display)
- TBD

##### 1.3 Report Content and Suggestion Engine

**Acceptance Criteria**:
- [ ] Suggestions are specific and actionable (not generic "improve quality")
- [ ] Each suggestion references the metric/tier that triggered it
- [ ] Severity levels: critical (score < threshold), warning (below average), info (improvement opportunity)
- [ ] Optional LLM-assisted suggestions (uses judge provider) for richer content recommendations
- [ ] Rule-based fallback when LLM is unavailable or `--no-llm-suggestions` is set

**Technical Requirements**:
- TBD — requires research into what makes suggestions actionable for the PeerRead evaluation context

**Files**:
- `src/app/reports/` (new — suggestion engine)
- TBD

---

#### Feature 2: Graph Node Attribute Alignment

**Description**: `graph_analysis.py:export_trace_to_networkx()` uses `type` as node attribute, while `agent_graph.py:render_agent_graph()` expects `node_type`. Direct callers of `export_trace_to_networkx()` get wrong visual node types. Sprint 7 avoided this by routing through `build_interaction_graph()`, but the latent mismatch should be fixed.

**Acceptance Criteria**:
- [ ] Unified node attribute name across graph export and rendering
- [ ] All callers of `export_trace_to_networkx()` produce correct visual node types
- [ ] `make validate` passes

**Technical Requirements**:
- TBD — choose canonical attribute name, update both sides

**Files**:
- `src/app/judge/graph_analysis.py` (edit)
- `src/gui/pages/agent_graph.py` (edit)

---

#### Feature 3: Security Hardening (MAESTRO Deferred Items)

**Description**: Address MAESTRO security findings deferred from Sprint 5-6.

##### 3.1 Centralized Tool Registry with Module Allowlist (MAESTRO L7.2)

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 3.2 Plugin Tier Validation at Registration (MAESTRO L7.1)

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 3.3 Error Message Sanitization

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 3.4 Configuration Path Traversal Protection

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

---

#### Feature 4: Code Quality Improvements

**Description**: Address accumulated code quality debt from Sprint 5-7.

##### 4.1 GraphTraceData Construction Simplification

**Description**: Replace manual `.get()` chains with `model_validate()`.

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 4.2 Timeout Bounds Enforcement

**Description**: Add min/max limits on user-configurable timeouts.

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 4.3 Hardcoded Settings Audit

**Description**: Migrate module-level constants to Pydantic BaseSettings (continuation of Sprint 7 Feature 10).

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 4.4 Time Tracking Consistency Across Tiers

**Description**: Standardize timing pattern across evaluation tiers.

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

---

#### Feature 5: Test Improvements

**Description**: Address testing gaps deferred from Sprint 7.

##### 5.1 BDD Scenario Tests for Evaluation Pipeline

**Description**: End-to-end user workflow tests using pytest.

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

##### 5.2 Tier 1 Reference Comparison Fix

**Description**: Fix all-1.0 self-comparison scores. Requires ground-truth review integration.

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

---

#### Feature 6: Provider-Specific Optimizations

**Description**: Address provider-specific issues deferred from Sprint 5.

##### 6.1 Cerebras Structured Output Validation Retries

**Description**: Optimize prompt/retry strategy for Cerebras provider structured output failures.

**Acceptance Criteria**:
- [ ] TBD

**Files**:
- TBD

---

#### Feature 7: PydanticAI Structured Output Streaming

**Description**: `run_manager()` raises `NotImplementedError` when `pydantic_ai_stream=True` because PydanticAI's `run_stream()` only supports `output_type=str`, not structured `BaseModel` outputs. Check if upstream PydanticAI has resolved this limitation; if so, enable streaming. If not, remove the dead code path and the `pydantic_ai_stream` parameter.

**Acceptance Criteria**:
- [ ] Check PydanticAI `run_stream()` structured output support status (upstream)
- [ ] If supported: enable streaming for structured output in `run_manager()`, remove `NotImplementedError`
- [ ] If not supported: delete dead code block (`agent_system.py:525-536`), remove `pydantic_ai_stream` parameter from `run_manager()` signature and all callers
- [ ] Update `AGENT_REQUESTS.md` entry (close or revise)
- [ ] `make validate` passes

**Files**:
- `src/app/agents/agent_system.py` (edit)

---

#### Feature 8: PlantUML Diagram Audit

**Description**: Review all PlantUML diagrams in `docs/arch_vis/` for necessity, accuracy, and coherence. Sprint 7 updated content but did not audit whether each diagram is still needed, whether overlapping diagrams should be consolidated, or whether naming/titles are consistent.

##### 8.1 Necessity Review

**Acceptance Criteria**:
- [ ] Each diagram in `docs/arch_vis/` justified as serving a distinct purpose (architecture, workflow, journey, landscape) — or marked for deletion/consolidation
- [ ] Overlapping diagrams identified (e.g., `mas-workflow` vs `mas-enhanced-workflow` vs `MAS-Review-Workflow` all depict agent interaction sequences) — consolidate or document why each is needed
- [ ] `AI-agent-landscape-visualization.puml` assessed: still useful as informational snapshot or stale enough to remove?

##### 8.2 Accuracy Review

**Acceptance Criteria**:
- [ ] Each diagram verified against current source code (Sprint 7 state): components, data flows, participants, and relationships match implementation
- [ ] C4 diagrams (`MAS-C4-Overview`, `MAS-C4-Detailed`) verified against `architecture.md` — no containers missing or stale
- [ ] Sequence diagrams verified against actual call chains in `agent_system.py`, `sweep_runner.py`, `evaluation_pipeline.py`

##### 8.3 Coherence Review

**Acceptance Criteria**:
- [ ] File names match diagram titles (e.g., `mas-workflow.plantuml` title is "MAS Workflow - Agent Interactions and Tool Usage" — do these align?)
- [ ] Naming convention consistent across files: some use `PascalCase` (`MAS-C4-Overview`), others `kebab-case` (`mas-workflow`) — standardize
- [ ] Diagram titles are concise and accurately describe content (not aspirational)
- [ ] Cross-references between diagrams and docs verified (architecture.md, README.md diagram links)

**Files**:
- `docs/arch_vis/*.plantuml` (audit, potentially edit/delete/consolidate)
- `docs/arch_vis/*.puml` (audit)
- `assets/images/` (sync after any changes)
- `docs/architecture.md` (edit — update diagram references if names change)
- `README.md` (edit — update diagram references if names change)

---

## Non-Functional Requirements

- TBD (pending Sprint 7 completion and Feature 1 design phase)

## Out of Scope

- TBD (pending Sprint 8 scoping)

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (TBD stories total):

**Carried forward from Sprint 7 Out of Scope:**
- Feature 2 (graph alignment) — Sprint 7 line 768
- Feature 3.1-3.4 (MAESTRO) — Sprint 6 deferred
- Feature 4.1-4.4 (code quality) — Sprint 6-7 deferred
- Feature 5.1 (BDD tests) — Sprint 7 deferred
- Feature 5.2 (Tier 1 fix) — Sprint 5 deferred
- Feature 6.1 (Cerebras) — Sprint 5 deferred

**New in Sprint 8:**
- Feature 1 (report generation) — new requirement
- Feature 7 (structured output streaming) — AGENT_REQUESTS.md open item
- Feature 8 (PlantUML audit) — necessity, accuracy, coherence review

Story breakdown TBD after Sprint 7 completion and Feature 1 design phase.
