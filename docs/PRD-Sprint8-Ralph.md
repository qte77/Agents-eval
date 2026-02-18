---
title: Product Requirements Document - Agents-eval Sprint 8
description: PeerRead tool fix, API key sentinel removal, CC engine consolidation, graph alignment, streaming check, report generation.
version: 0.3
created: 2026-02-17
updated: 2026-02-18
status: draft
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 7 delivered: documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

**Sprint 8 Focus**: Fix sweep-crashing tool bug, remove API key sentinel, consolidate CC engine logic, graph attribute alignment, streaming decision, report generation.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Replace `read_paper_pdf_tool` with `get_paper_content` Using Parsed JSON Fallback Chain

**Description**: `read_paper_pdf_tool` is exposed directly to the LLM and requires a local filesystem path as input. The LLM has no way to discover valid paths, leading to hallucinated URLs (e.g., `https://arxiv.org/pdf/1105.1072`) that crash the agent with `FileNotFoundError`. The correct content-loading logic already exists internally in `_load_paper_content_with_fallback()` (parsed JSON → raw PDF → abstract), but it's private — only called from `generate_paper_review_content_from_template`. Meanwhile, `get_peerread_paper` returns only title/abstract/reviews, no body text, so the LLM naturally reaches for `read_paper_pdf_tool` to get full paper content.

**Root cause**: The LLM needs full paper content but only has a raw-PDF-by-path tool with no way to supply a valid path. The parsed JSON data (primary content source) is not accessible via any tool.

**Acceptance Criteria**:
- [ ] `read_paper_pdf_tool` removed from agent tool registration (no longer LLM-callable)
- [ ] New tool `get_paper_content(paper_id: str) -> str` registered on the same agent (researcher or manager)
- [ ] `get_paper_content` internally calls `_load_paper_content_with_fallback()` fallback chain: parsed JSON → raw PDF → abstract
- [ ] Tool docstring clearly states: returns full paper text from local PeerRead dataset, requires `paper_id` (not a file path or URL)
- [ ] `read_paper_pdf()` function retained as internal helper (used by fallback chain), just not exposed as a tool
- [ ] `read_paper_pdf()` rejects URLs with a descriptive return instead of `FileNotFoundError` (defensive guard)
- [ ] Sweep with `--paper-id=1105.1072` no longer crashes with `FileNotFoundError`
- [ ] `make validate` passes

**Technical Requirements**:
- Remove `@agent.tool` decorator from `read_paper_pdf_tool` in `add_peerread_tools_to_agent()`
- Add new `@agent.tool get_paper_content(ctx, paper_id)` that instantiates `PeerReadLoader`, calls `_load_paper_content_with_fallback(ctx, loader, paper_id, abstract)` where `abstract` is obtained from `loader.get_paper_by_id(paper_id).abstract`
- Add URL guard in `read_paper_pdf()`: if `pdf_path` starts with `http`, return error string instead of raising
- `_load_paper_content_with_fallback` already handles all three tiers — no changes needed there
- Update tool trace logging (`trace_collector.log_tool_call`) for the new tool name

**Files**:
- `src/app/tools/peerread_tools.py` (edit — replace `read_paper_pdf_tool` with `get_paper_content`, add URL guard)
- `tests/tools/test_peerread_tools.py` (edit — update tool registration tests, add `get_paper_content` test)

---

#### Feature 2: Remove `"not-required"` API Key Sentinel from `create_llm_model`

**Description**: `create_llm_model()` in `models.py` uses `api_key or "not-required"` at 5 call sites (lines 78, 87, 98, 119, 128). This prevents the OpenAI SDK from falling back to environment variables (`OPENAI_API_KEY`, `GITHUB_TOKEN`, etc.) because the SDK receives a non-empty string and uses it as-is. Sprint 8 commit `9e14931` fixed this in `create_simple_model()` (judge path) by passing `api_key` directly. The same fix is needed in `create_llm_model()` for the main agent creation path.

**Note**: Line 70 (`ollama` provider) legitimately uses `"not-required"` as a literal — Ollama doesn't need auth. This should remain hardcoded.

**Acceptance Criteria**:
- [ ] `create_llm_model()` passes `api_key` directly to `OpenAIProvider` for all providers except `ollama` (5 sites: lines 78, 87, 98, 119, 128)
- [ ] Ollama provider retains `api_key="not-required"` (no auth needed)
- [ ] When `api_key=None`, OpenAI SDK falls back to `OPENAI_API_KEY` env var (verified by test)
- [ ] Existing tests pass — no behavioral change when API key is provided explicitly
- [ ] `make validate` passes

**Technical Requirements**:
- Replace `api_key=api_key or "not-required"` with `api_key=api_key` at 5 call sites
- Add test: `create_llm_model(provider="openai", ..., api_key=None)` results in `OpenAIProvider(api_key=None)`, not `"not-required"`

**Files**:
- `src/app/llms/models.py` (edit — 5 lines)
- `tests/llms/test_models.py` (edit — add sentinel removal test)

---

#### Feature 3: Extract CC Engine Logic into `src/app/engines/cc_engine.py`

**Description**: CC (Claude Code) engine logic is scattered across `run_cli.py`, `sweep_runner.py`, and `run_app.py` with duplicated subprocess invocation, inconsistent error handling, and incomplete wiring. The `subprocess.run(["claude", "-p", ...])` pattern is copy-pasted between CLI and sweep. The GUI accepts the engine selection but silently ignores it (`engine` parameter never reaches `main()`). `_run_cc_baselines()` in `sweep_runner.py` invokes CC but does not feed results into evaluation. `CCTraceAdapter` (the artifact parser) is not connected to any subprocess invocation path.

**Current state:**
- `run_cli.py:169-214` — subprocess invocation + engine dispatch (30 lines inline)
- `sweep_runner.py:143-232` — duplicate subprocess invocation + stub baseline loop
- `run_app.py:471-532` — engine selector UI, but `engine` param silently dropped in `_execute_query_background()`
- `cc_trace_adapter.py` — artifact parser, only called from `evaluation_runner.py` baseline comparisons (not from subprocess paths)

**Acceptance Criteria**:
- [ ] New module `src/app/engines/cc_engine.py` with:
  - `check_cc_available() -> bool` — `shutil.which("claude")` (replaces 3 inline checks)
  - `run_cc_headless(query: str, timeout: int = 600) -> CCResult` — subprocess invocation with error handling (replaces 2 duplicate implementations)
  - `CCResult` Pydantic model: `session_dir`, `output_data`, `execution_id`
- [ ] `run_cli.py` CC branch delegates to `cc_engine.run_cc_headless()` — no inline subprocess code
- [ ] `sweep_runner.py._invoke_cc_comparison()` delegates to `cc_engine.run_cc_headless()` — no inline subprocess code
- [ ] `run_app.py._execute_query_background()` passes `engine` to `main()` when `engine == "cc"` (currently silently dropped)
- [ ] `_run_cc_baselines()` wires CC results through `CCTraceAdapter` → evaluation (not a stub)
- [ ] `src/app/engines/__init__.py` created
- [ ] `make validate` passes

**Technical Requirements**:
- Extract `subprocess.run(["claude", "-p", ...])` into single `run_cc_headless()` function
- Error handling consolidated: `RuntimeError` for non-zero exit, `ValueError` for JSON parse failure, `RuntimeError` for timeout
- `check_cc_available()` replaces `shutil.which("claude")` in `run_cli.py:170`, `sweep_runner.py:189`, `run_app.py:471`
- Wire `CCTraceAdapter` into the subprocess result flow: `run_cc_headless()` → `CCResult.session_dir` → `CCTraceAdapter(session_dir).parse()` → `GraphTraceData`

**Files**:
- `src/app/engines/__init__.py` (new)
- `src/app/engines/cc_engine.py` (new — extracted CC logic)
- `src/run_cli.py` (edit — delegate to `cc_engine`)
- `src/app/benchmark/sweep_runner.py` (edit — delegate to `cc_engine`, wire adapter)
- `src/gui/pages/run_app.py` (edit — pass `engine` through, wire CC path)
- `tests/engines/test_cc_engine.py` (new — subprocess mock tests)

---

#### Feature 4: Graph Node Attribute Alignment

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

#### Feature 5: PydanticAI Structured Output Streaming

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

#### Feature 6: Report Generation in CLI and GUI

**Description**: After evaluation completes, users should be able to generate a structured report that summarizes evaluation results and suggests improvements. The report synthesizes Tier 1/2/3 scores, highlights weaknesses (low-scoring dimensions), and proposes actionable content suggestions (e.g., "Tier 1 BLEU score low — review lacks specific technical terminology from the paper abstract"). Available via `--generate-report` in CLI and a "Generate Report" button in the GUI.

##### 6.1 CLI Report Generation

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

##### 6.2 GUI Report Generation

**Acceptance Criteria**:
- [ ] "Generate Report" button on App page, enabled after evaluation completes
- [ ] Report displayed inline (Markdown rendered via `st.markdown`) with download option
- [ ] Same report content as CLI (shared generation logic)
- [ ] `make validate` passes

**Files**:
- `src/gui/pages/run_app.py` (edit — add report button and display)
- TBD

##### 6.3 Report Content and Suggestion Engine

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

## Non-Functional Requirements

- Report generation (Feature 6) latency target: < 5s for rule-based suggestions, < 30s for LLM-assisted
- No new external dependencies for Features 1-5

## Out of Scope

**Deferred to Sprint 9 (TBD acceptance criteria, low urgency):**
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
- Unify API Key Resolution Across Agent and Judge Paths — YAGNI after Feature 2 removes sentinel
- ~~CC engine SDK migration~~ — **Removed.** Keeping `subprocess.run([claude, "-p"])` per ADR-008.

**Already completed (Sprint 8 pre-work, commits a5ac5c9→9e14931→9329fc3):**
- Legacy config key removal (`paper_numbers`, `provider`) from `run_sweep.py`
- Judge API key forwarding: `_resolve_provider_key` → `select_available_provider` → `create_judge_agent`
- `"not-required"` sentinel removed from `create_simple_model()` — `None` lets SDK use env vars

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (TBD stories total):

**Sprint 8 scope (in priority order):**
- Feature 1 (replace `read_paper_pdf_tool` with `get_paper_content`) — fixes sweep crash
- Feature 2 (remove `"not-required"` from `create_llm_model`) — small fix, 5 call sites
- Feature 3 (extract CC engine into `cc_engine.py`) — consolidate scattered subprocess logic, fix GUI silent drop
- Feature 4 (graph alignment) — small fix, 2 files
- Feature 5 (structured output streaming) — binary check, AGENT_REQUESTS.md item
- Feature 6 (report generation) — flagship feature, needs design phase first

Story breakdown TBD after Feature 6 design phase.
