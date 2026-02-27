---
title: Product Requirements Document - Agents-eval Sprint 12
description: Sprint 12 — CC teams mode bug fixes, scoring system fixes, and output directory restructuring. Fix engine_type misclassification, team artifact parsing, 5 evaluation scoring bugs, and consolidate all run artifacts into per-run directories.
version: 4.3.0
created: 2026-02-25
updated: 2026-02-27
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

**Sprint 12 goal**: Fix CC teams mode classification and evaluation wiring. CC teams runs are misclassified as `cc_solo` because (1) the JSONL stream parser looks for event types (`TeamCreate`, `Task`) that CC never emits — real team events use `type=system, subtype=task_started`, and (2) `engine_type` is inferred from parsed artifacts instead of the user's explicit mode selection. This causes downstream evaluation failures: Tier 3 graph analysis is skipped, coordination/tool metrics default to 0, and the results JSON reports the wrong engine.

Additionally, the composite scoring system has 5 bugs producing misleading evaluation results: (1) `time_taken` is always ~0.999 because `_execute_tier1` passes two near-identical timestamps instead of actual agent execution duration, (2) Tier 3 returns all-zeros for empty trace data instead of triggering fallback, (3) `evaluate_composite_with_trace` (single-agent weight redistribution) exists but is never called from production code, (4) `semantic_score` duplicates `cosine_score` because BERTScore is disabled and the fallback delegates to the same cosine function, (5) `task_success` is binary 0/1 with a harsh 0.8 threshold providing no gradient for generative tasks.

### Current State

| Area | Status | Gap |
| --- | --- | --- |
| CC teams engine_type | Broken | `engine_type` set to `"cc_solo"` even when CC teams mode is selected (`app.py:262`) |
| JSONL stream team event parsing | Broken | `_TEAM_EVENT_TYPES` expects `{"TeamCreate", "Task"}` but CC emits `{"type": "system", "subtype": "task_started"}` (`cc_engine.py:34`) |
| CC teams evaluation scores | Degraded | Tier 3 N/A, `coordination_quality=0`, `tool_efficiency=0` because graph trace has no team artifacts |
| `cc_teams` flag passthrough | Missing | `cc_teams` boolean consumed in CLI/GUI, never forwarded to `main()` or `_run_cc_engine_path()` |
| Tier 3 empty-trace handling | Broken | Empty `tool_calls` + `agent_interactions` returns all-zero `Tier3Result` (not `None`), bypassing fallback (`graph_analysis.py:224-269`) |
| Single-agent weight redistribution | Dead code | `evaluate_composite_with_trace` never called from production pipeline (`evaluation_pipeline.py:279-303`) |
| `time_taken` metric | Broken | Always ~0.999 — `_execute_tier1` passes two `time.time()` calls microseconds apart (`evaluation_pipeline.py:161,173`) |
| `semantic_score` duplication | Bug | `compute_semantic_similarity` delegates to `compute_cosine_similarity` — cosine gets 0.7 effective weight in Tier 1 formula (`traditional_metrics.py:232`) |
| `task_success` binary cliff | Design flaw | Returns 0.0 or 1.0 at 0.8 threshold — no gradient for generative tasks (`traditional_metrics.py:278`) |
| Output directory structure | Poor UX | All streams, traces, reviews, reports dumped flat in separate dirs — no per-run grouping, inconsistent timestamps, no cross-artifact linking (`config_app.py:16-22`) |

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop and CC Agent Teams enforce this order.**

Full references: `docs/best-practices/tdd-best-practices.md`, `docs/best-practices/testing-strategy.md`, `.claude/skills/testing-python/SKILL.md`.

### TDD Workflow (Mandatory for all features)

Every feature follows the Red-Green-Refactor cycle. Invoke `testing-python` skill for RED phase, `implementing-python` skill for GREEN phase.

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists. Use Arrange-Act-Assert (AAA) structure. Name tests `test_{module}_{component}_{behavior}`.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality beyond what tests require.
3. **REFACTOR**: Clean up while keeping tests green. Run `make quick_validate` (teammate) or `make validate` (lead/wave boundary) before marking complete.

### Test Tool Selection

| Tool | Use for | NOT for |
|------|---------|--------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation. See `testing-strategy.md` "Patterns to Remove" for anti-patterns.

### Mandatory Practices

- **Mock external dependencies** (HTTP, LLM providers, file systems, subprocess) using `@patch` with `spec=RealClass`. Never call real APIs in unit tests. Bare `MagicMock()` silently accepts any attribute — use `spec=` to constrain to the real interface.
- **Test behavior, not implementation** -- test observable outcomes (return values, side effects, error messages), not internal structure.
- **Use `tmp_path` fixture** for all test filesystem operations. Never use `tempfile.mkdtemp()` or hardcoded paths (see AGENT_LEARNINGS "Test Filesystem Isolation").
- **Google-style docstrings** for every new file, function, class, and method.
- **`# Reason:` comments** for non-obvious logic.
- **`# S12-F{N}:` change comments** for non-trivial code changes.
- **`make validate` MUST pass** before any story is marked complete. No exceptions.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (all features) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |

### Quality Gates (Per Story and Per Wave)

**Teammate (per story)**:

- [ ] Tests written FIRST (RED phase) using `testing-python` skill
- [ ] Tests fail for the right reason before implementation begins
- [ ] Minimal implementation passes all tests (GREEN phase)
- [ ] `make quick_validate` passes (lint + type check + complexity + duplication)

**Lead (per wave boundary)**:

- [ ] `make validate` passes (lint + type check + full test suite)
- [ ] No regressions in existing tests
- [ ] All story ACs verified before advancing to next wave

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->
<!-- PARSER REQUIREMENT: No compound sub-features — one heading per story -->
<!-- PARSER REQUIREMENT: Flatten AC items — no indented sub-items under a checkbox -->
<!-- PARSER REQUIREMENT: Each sub-feature MUST have its own **Files**: section -->

#### Feature 1: Fix CC Teams Stream Event Parsing

**Description**: The JSONL stream parser (`parse_stream_json` via `_apply_event`) checks for `"type": "TeamCreate"` and `"type": "Task"` events via the `_TEAM_EVENT_TYPES` set (`cc_engine.py:34`). However, CC's actual stream-json output uses `"type": "system"` with `"subtype": "task_started"` (and `"task_type": "local_agent"`) for team sub-agent events. The parser never matches real team events, so `team_artifacts` is always empty in production.

Observed in the CC teams JSONL stream (`cc_teams_66a8e8d4-..._.jsonl`):

```json
{"type":"system","subtype":"task_started","task_id":"a0310d0243dc18105","description":"Explore paper review codebase","task_type":"local_agent","session_id":"66a8e8d4-..."}
{"type":"system","subtype":"task_started","task_id":"a99881260fa015660","description":"Technical soundness review","task_type":"local_agent","session_id":"66a8e8d4-..."}
```

These events have `"type": "system"`, not `"TeamCreate"` or `"Task"`, so `_apply_event` line 157 (`elif event_type in _TEAM_EVENT_TYPES`) never fires.

**Acceptance Criteria**:

- [ ] AC1: `_apply_event` captures `"type": "system", "subtype": "task_started"` events as team artifacts
- [ ] AC2: `_apply_event` captures `"type": "system", "subtype": "task_completed"` events as team artifacts
- [ ] AC3: `_TEAM_EVENT_TYPES` is removed or updated to reflect actual CC stream event types
- [ ] AC4: Existing `"type": "system", "subtype": "init"` handling is not broken (init events must NOT be captured as team artifacts)
- [ ] AC5: `parse_stream_json` returns populated `team_artifacts` when given a real CC teams stream
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- Update `_apply_event()` in `cc_engine.py` to detect team events by `type == "system"` AND `subtype in {"task_started", "task_completed"}` instead of checking `_TEAM_EVENT_TYPES`
- Remove or repurpose `_TEAM_EVENT_TYPES` constant — the old values (`"TeamCreate"`, `"Task"`) do not appear in real CC output
- Keep the existing `init` event handler (`type == "system" and subtype == "init"`) — it must take priority over the new team artifact handler
- Order of checks in `_apply_event`: (1) init event, (2) result event, (3) team task events

**Files**:

- `src/app/engines/cc_engine.py` (edit -- update `_apply_event`, remove/update `_TEAM_EVENT_TYPES`)
- `tests/engines/test_cc_engine.py` (edit -- update `parse_stream_json` tests to use real event format, add tests for `task_started`/`task_completed` capture)

---

#### Feature 2: Pass `cc_teams` Flag Through to `engine_type` Assignment

**Description**: `engine_type` is set at `app.py:262` based on whether `cc_result.team_artifacts` is non-empty: `"cc_teams" if cc_result.team_artifacts else "cc_solo"`. This is fragile — if CC runs in teams mode but emits no parseable team events (Bug 1, or a short run), `engine_type` is wrong. The user's explicit `cc_teams` flag is the source of truth for mode selection but is consumed in CLI (`run_cli.py:115`) and GUI (`run_app.py:331`) and never forwarded to `main()` or `_run_cc_engine_path()`.

**Acceptance Criteria**:

- [ ] AC1: `main()` accepts a `cc_teams: bool = False` parameter
- [ ] AC2: `_run_cc_engine_path()` accepts a `cc_teams: bool` parameter
- [ ] AC3: `engine_type` is set from `cc_teams` flag: `"cc_teams" if cc_teams else "cc_solo"` (not from `team_artifacts`)
- [ ] AC4: CLI (`run_cli.py`) passes `cc_teams` to `main()`
- [ ] AC5: GUI (`run_app.py:_execute_query_background`) passes `cc_teams` to `main()`
- [ ] AC6: When `cc_teams=True` and `team_artifacts` is empty, `engine_type` is still `"cc_teams"`
- [ ] AC7: When `cc_teams=False`, `engine_type` is `"cc_solo"` regardless of `team_artifacts` content
- [ ] AC8: `make validate` passes with no regressions

**Technical Requirements**:

- Add `cc_teams: bool = False` parameter to `main()` signature (`app.py:334`)
- Add `cc_teams: bool` parameter to `_run_cc_engine_path()` signature (`app.py:218`)
- Change `app.py:262` from `"cc_teams" if cc_result.team_artifacts else "cc_solo"` to `"cc_teams" if cc_teams else "cc_solo"`
- CLI fix (`run_cli.py:149`): pass `cc_teams=cc_teams` to `main()` call
- GUI fix (`run_app.py:334`): pass `cc_teams=cc_teams` to `main()` call
- Forward `cc_teams` from `main()` to `_run_cc_engine_path()` at the CC branch call site

**Files**:

- `src/app/app.py` (edit -- add `cc_teams` param to `main()` and `_run_cc_engine_path()`, fix `engine_type` assignment)
- `src/run_cli.py` (edit -- pass `cc_teams` to `main()`)
- `src/gui/pages/run_app.py` (edit -- pass `cc_teams` to `main()`)
- `tests/cli/test_cc_engine_wiring.py` (edit -- update `engine_type` tests to use `cc_teams` flag instead of `team_artifacts` inference)

---

#### Feature 3: Skip Tier 3 for Empty Trace Data

**Description**: When `GraphTraceData` has empty `tool_calls` and empty `agent_interactions` (e.g., CC solo runs with no trace artifacts), `evaluate_graph_metrics` returns an all-zero `Tier3Result`. This non-None result bypasses the fallback strategy (`_apply_fallback_strategy`), silently penalizing the composite score by 0.334 (two metrics × 0.167 weight). The fix: return `None` from `_execute_tier3` when trace data is empty, triggering the existing `tier1_only` fallback which creates neutral 0.5 scores.

**Acceptance Criteria**:

- [ ] AC1: `_execute_tier3` returns `(None, 0.0)` when `GraphTraceData` has empty `tool_calls` AND empty `agent_interactions`
- [ ] AC2: A log message at INFO level is emitted when Tier 3 is skipped due to empty trace
- [ ] AC3: `performance_monitor.record_tier_execution(3, 0.0)` is called for the skip case
- [ ] AC4: Existing Tier 3 behavior is unchanged when trace data has tool_calls or agent_interactions
- [ ] AC5: The `tier1_only` fallback strategy creates neutral Tier 3 result (0.5 scores) when Tier 3 returns None
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- In `_execute_tier3` (`evaluation_pipeline.py:323`), after `trace_data = self._create_trace_data(execution_trace)`, add early return guard checking `not trace_data.tool_calls and not trace_data.agent_interactions`
- Record tier execution with 0.0 time before returning to keep performance stats consistent
- The existing `_apply_fallback_strategy` (`evaluation_pipeline.py:369`) already handles `results.tier3 is None` by creating a `Tier3Result` with 0.5 scores — no changes needed there

**Files**:

- `src/app/judge/evaluation_pipeline.py` (edit -- add empty-trace early return in `_execute_tier3`)
- `tests/evals/test_evaluation_pipeline.py` (edit -- add test for empty-trace skip behavior)

---

#### Feature 4: Wire `evaluate_composite_with_trace` into Production Pipeline

**Description**: `CompositeScorer.evaluate_composite_with_trace` detects single-agent mode from `GraphTraceData` and redistributes `coordination_quality` weight to remaining metrics. However, it is never called from production code — `_generate_composite_score` only calls `evaluate_composite` or `evaluate_composite_with_optional_tier2`. This means CC solo runs (and any single-agent execution) never benefit from weight redistribution, and `coordination_quality=0` silently penalizes the composite score.

**Acceptance Criteria**:

- [ ] AC1: `_generate_composite_score` accepts an optional `trace_data: GraphTraceData | None` parameter
- [ ] AC2: When `trace_data` is provided and `results.is_complete()`, `evaluate_composite_with_trace` is called
- [ ] AC3: When `trace_data` is None, existing routing to `evaluate_composite` / `evaluate_composite_with_optional_tier2` is preserved
- [ ] AC4: `evaluate_comprehensive` retains the `GraphTraceData` object and passes it to `_generate_composite_score`
- [ ] AC5: CC solo runs with empty `agent_interactions` trigger single-agent detection and weight redistribution
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- In `evaluate_comprehensive` (`evaluation_pipeline.py:476`), retain a `GraphTraceData` reference when converting `execution_trace` to dict — currently the object is discarded after conversion
- Add `trace_data: GraphTraceData | None = None` parameter to `_generate_composite_score` (`evaluation_pipeline.py:279`)
- New routing: if `trace_data is not None and results.is_complete()` → call `self.composite_scorer.evaluate_composite_with_trace(results, trace_data)`; otherwise fall through to existing logic
- `evaluate_composite_with_trace` already handles both single-agent and multi-agent cases internally (`composite_scorer.py:456-517`)

**Files**:

- `src/app/judge/evaluation_pipeline.py` (edit -- update `_generate_composite_score` signature and routing, update `evaluate_comprehensive` to retain and pass trace data)
- `tests/evals/test_evaluation_pipeline.py` (edit -- add test for trace-aware composite scoring path)
- `tests/evals/test_composite_scorer.py` (edit -- add integration test for trace-aware path)

---

#### Feature 5: Propagate Actual Execution Timestamps to `time_taken` Metric

**Description**: `time_taken` is always ~0.999 because `_execute_tier1` captures `start_evaluation = time.time()` and immediately passes `time.time()` as `end_time` — both timestamps are microseconds apart. The `measure_execution_time` formula `exp(-duration)` then returns `exp(~0) ≈ 0.999`. The actual agent execution (e.g., CC solo ran for 158 seconds) is never measured or propagated. The fix: capture wall-clock timestamps around the subprocess/agent execution and propagate them through the pipeline to `_execute_tier1`.

**Acceptance Criteria**:

- [ ] AC1: `CCResult` has `start_time: float` and `end_time: float` fields
- [ ] AC2: `run_cc_solo` captures `time.time()` before and after `subprocess.run()` and stores on `CCResult`
- [ ] AC3: `run_cc_teams` captures `time.time()` before and after `Popen` block and stores on `CCResult`
- [ ] AC4: `run_evaluation_if_enabled` accepts `execution_start_time: float = 0.0` and `execution_end_time: float = 0.0`
- [ ] AC5: `evaluate_comprehensive` accepts and forwards `execution_start_time`/`execution_end_time` to `_execute_tier1`
- [ ] AC6: `_execute_tier1` uses external timestamps when non-zero, falls back to `time.time()` when zero
- [ ] AC7: MAS engine path captures timing around `run_manager()` and passes to evaluation
- [ ] AC8: CC engine path extracts `cc_result.start_time`/`cc_result.end_time` and passes to evaluation
- [ ] AC9: `make validate` passes with no regressions

**Technical Requirements**:

- Add `start_time: float = Field(default=0.0)` and `end_time: float = Field(default=0.0)` to `CCResult` (`cc_engine.py:67-87`)
- Wrap `subprocess.run()` in `run_cc_solo` (`cc_engine.py:~380`) with `time.time()` before/after
- Wrap `Popen` block in `run_cc_teams` (`cc_engine.py:~440`) with `time.time()` before/after; set `start_time`/`end_time` on `CCResult` after construction
- Add `execution_start_time: float = 0.0` and `execution_end_time: float = 0.0` to `run_evaluation_if_enabled` (`evaluation_runner.py:115`); forward to `pipeline.evaluate_comprehensive`
- Add same params to `evaluate_comprehensive` (`evaluation_pipeline.py:476`) and `_execute_tier1` (`evaluation_pipeline.py:138`)
- In `_execute_tier1`, replace `start_evaluation = time.time()` / `time.time()` with external timestamps when non-zero
- In `_run_cc_engine_path` (`app.py:218`): pass `cc_result.start_time`/`cc_result.end_time`
- In `_run_mas_engine_path` (`app.py:266`): wrap `run_manager()` with `time.time()` before/after

**Files**:

- `src/app/engines/cc_engine.py` (edit -- add timing fields to `CCResult`, capture in `run_cc_solo`/`run_cc_teams`)
- `src/app/app.py` (edit -- capture and pass timing from both engine paths)
- `src/app/judge/evaluation_runner.py` (edit -- add timing params, forward to pipeline)
- `src/app/judge/evaluation_pipeline.py` (edit -- accept and use external timestamps in `evaluate_comprehensive` and `_execute_tier1`)
- `tests/evals/test_evaluation_pipeline.py` (edit -- add test for timestamp propagation)
- `tests/judge/test_evaluation_runner.py` (edit -- add timing params to call sites, add forward-propagation test)
- `tests/engines/test_cc_engine.py` (edit -- verify `CCResult` timing fields populated)

---

#### Feature 6: Deduplicate `semantic_score` from `cosine_score`

**Description**: `compute_semantic_similarity` (`traditional_metrics.py:218`) delegates to `compute_cosine_similarity` because BERTScore is disabled due to build issues. This means `semantic_score == cosine_score` always, giving cosine 0.7 effective weight in the Tier 1 formula (`0.4 × semantic + 0.3 × cosine`) while Jaccard gets only 0.2. The fix: use Levenshtein similarity (already available via `textdistance` in `pyproject.toml`, with `compute_levenshtein_similarity` already implemented in the same class) as the semantic fallback. This provides a distinct character-level sequence similarity signal.

**Acceptance Criteria**:

- [ ] AC1: `compute_semantic_similarity` delegates to `compute_levenshtein_similarity` instead of `compute_cosine_similarity`
- [ ] AC2: `semantic_score` and `cosine_score` produce different values for non-identical texts
- [ ] AC3: `semantic_score` returns 1.0 for identical texts and 0.0 for empty-vs-nonempty texts
- [ ] AC4: `Tier1Result.semantic_score` field description updated to reflect Levenshtein-based calculation
- [ ] AC5: No new dependencies added — uses existing `textdistance` library
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- In `compute_semantic_similarity` (`traditional_metrics.py:218`), change `return self.compute_cosine_similarity(text1, text2)` to `return self.compute_levenshtein_similarity(text1, text2)`
- Update the method's docstring and log message to say "Levenshtein" not "cosine similarity fallback"
- In `evaluation_models.py`, update `Tier1Result.semantic_score` field description from "BERT-based" to "Levenshtein-based sequence similarity (BERTScore disabled)"
- `compute_levenshtein_similarity` already exists at `traditional_metrics.py:190` with its own fallback chain

**Files**:

- `src/app/judge/traditional_metrics.py` (edit -- change `compute_semantic_similarity` delegation)
- `src/app/data_models/evaluation_models.py` (edit -- update `semantic_score` field description)
- `tests/evals/test_traditional_metrics.py` (edit -- update semantic similarity tests; remove any assertions that `semantic == cosine`)

---

#### Feature 7: Replace Binary `task_success` with Continuous Score

**Description**: `assess_task_success` (`traditional_metrics.py:256`) returns exactly 1.0 or 0.0 based on whether weighted similarity meets the 0.8 threshold. For generative review tasks where typical text similarity ranges 0.3–0.6, this almost always returns 0.0, providing zero useful signal in the composite score. The fix: use proportional credit `min(1.0, similarity / threshold)` which gives linear gradient below threshold and full credit at/above threshold.

**Acceptance Criteria**:

- [ ] AC1: `assess_task_success` returns continuous float in `[0.0, 1.0]` instead of binary `{0.0, 1.0}`
- [ ] AC2: When weighted similarity >= threshold, returns 1.0
- [ ] AC3: When weighted similarity < threshold, returns `weighted_similarity / threshold` (proportional credit)
- [ ] AC4: When weighted similarity is 0.0, returns 0.0
- [ ] AC5: When threshold is 0.0, returns 0.0 (avoid division by zero)
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- In `assess_task_success` (`traditional_metrics.py:256`), replace `return 1.0 if overall_similarity >= threshold else 0.0` with `return min(1.0, overall_similarity / threshold) if threshold > 0.0 else 0.0`
- Update the method's docstring to document continuous scoring behavior
- No config changes — the 0.8 threshold still represents "full credit" target; the change is in how sub-threshold scores are handled

**Files**:

- `src/app/judge/traditional_metrics.py` (edit -- change `assess_task_success` return logic)
- `tests/evals/test_traditional_metrics.py` (edit -- update tests from binary assertions to continuous range checks)

---

#### Feature 8: Consolidate Run Artifacts into Per-Run Directories

**Description**: Currently, run artifacts are scattered across 4 flat directories (`logs/Agent_evals/cc_streams/`, `logs/Agent_evals/traces/`, `results/MAS_reviews/`, `results/reports/`) with inconsistent naming and no per-run grouping. After 20+ runs, finding all artifacts for a single run requires cross-referencing execution IDs across directories. Filenames sort poorly because execution ID (hex hash) precedes the timestamp. Timestamp formats vary across writers (3 different formats). The fix: introduce an `output/` directory with `runs/` and `sweeps/` subdirectories, a unified timestamp format, a `RunContext` that tracks the current run's output path, and a `metadata.json` file that makes each run self-describing. Remove legacy path constants and all code writing to the old locations.

**Current state (6 writers, 4 directories, 3 timestamp formats)**:

| Writer | Current path | Filename pattern | Timestamp format |
|--------|-------------|-----------------|------------------|
| `cc_engine.py:334` | `logs/Agent_evals/cc_streams/` | `cc_solo_{exec_id}_{ts}.json` | `%Y%m%dT%H%M%S` |
| `cc_engine.py:431` | `logs/Agent_evals/cc_streams/` | `cc_teams_{exec_id}_{ts}.jsonl` | `%Y%m%dT%H%M%S` |
| `trace_processors.py:320` | `logs/Agent_evals/traces/` | `trace_{exec_id}_{ts}.jsonl` | `%Y-%m-%dT%H-%M-%SZ` |
| `review_persistence.py:38` | `results/MAS_reviews/` | `{paper_id}_{ts}.json` | `%Y-%m-%dT%H-%M-%SZ` |
| `run_cli.py:164` | `results/reports/` | `{ts}.md` | `%Y%m%dT%H%M%S` |
| `sweep_runner.py:228` | `results/sweeps/{ts}/` | `results.json`, `summary.md` | `%Y%m%d_%H%M%S` |

**Target state (unified output directory)**:

```
output/
  runs/
    {YYYYMMDD_HHMMSS}_{engine}_{paper_id}_{exec_id_8}/
      metadata.json       ← engine_type, paper_id, exec_id, timestamps, CLI args
      stream.json         ← CC solo output (if CC solo)
      stream.jsonl        ← CC teams output (if CC teams)
      trace.jsonl         ← MAS trace (if MAS)
      review.json         ← MAS review (if MAS)
      evaluation.json     ← pipeline results (currently in-memory only)
      report.md           ← evaluation report (if --generate-report)
    traces.db             ← shared SQLite trace index (across all runs)
  sweeps/
    {YYYYMMDD_HHMMSS}/
      results.json        ← raw per-evaluation scores
      summary.md          ← Markdown statistical summary
```

This feature is split into 3 stories to manage scope:

- **STORY-008**: `RunContext` + `metadata.json` + path constants — foundational infrastructure
- **STORY-009**: Migrate all 6 writers to use `RunContext` — the actual file moves
- **STORY-010**: Persist evaluation results to `evaluation.json` — new capability enabled by per-run dirs

---

##### Feature 8a: Introduce `RunContext` and Per-Run Directory Infrastructure (STORY-008)

**Description**: Create a `RunContext` dataclass that owns the per-run output directory. It is created at the start of each `main()` invocation with the run's engine type, paper ID, and execution ID. It creates `output/runs/{YYYYMMDD_HHMMSS}_{engine}_{paper_id}_{exec_id_8}/`, writes `metadata.json`, and exposes path helpers (`stream_path`, `trace_path`, `review_path`, `report_path`, `evaluation_path`). Replace legacy path constants in `config_app.py` with single `OUTPUT_PATH`. Adopt unified timestamp format `%Y%m%dT%H%M%S` everywhere.

**Acceptance Criteria**:

- [ ] AC1: `RunContext` dataclass exists with fields: `engine_type`, `paper_id`, `execution_id`, `start_time`, `run_dir` (Path)
- [ ] AC2: `RunContext.create(engine_type, paper_id, execution_id)` creates the directory `output/runs/{YYYYMMDD_HHMMSS}_{engine}_{paper_id}_{exec_id_8}/` and writes `metadata.json`
- [ ] AC3: `metadata.json` contains: `engine_type`, `paper_id`, `execution_id`, `start_time` (ISO), `cli_args` (optional dict)
- [ ] AC4: Path helpers return correct filenames: `stream_path` → `stream.json`/`stream.jsonl` (based on engine_type), `trace_path` → `trace.jsonl`, `review_path` → `review.json`, `report_path` → `report.md`, `evaluation_path` → `evaluation.json`
- [ ] AC5: `OUTPUT_PATH = "output"` constant added to `config_app.py`
- [ ] AC6: Legacy constants `CC_STREAMS_PATH`, `MAS_REVIEWS_PATH`, `RESULTS_PATH` removed from `config_app.py`
- [ ] AC7: `LOGS_PATH` (Loguru logs) and `LOGS_BASE_PATH` remain unchanged — application logs are not per-run
- [ ] AC8: `JudgeSettings.trace_storage_path` default changed from `logs/Agent_evals/traces` to `output/runs` (fallback when `run_dir` is None)
- [ ] AC9: `main()` creates `RunContext` after engine execution completes (once `execution_id` is known) and passes it to evaluation and writer paths
- [ ] AC10: `output/` added to `.gitignore` (`results/` entry kept for existing artifacts)
- [ ] AC11: `make validate` passes with no regressions

**Technical Requirements**:

- New file `src/app/utils/run_context.py` with `RunContext` dataclass (Pydantic model)
- `RunContext.create()` classmethod: generates `run_dir` name from `datetime.now().strftime("%Y%m%dT%H%M%S")`, `engine_type`, `paper_id`, `execution_id[:8]`; calls `mkdir(parents=True)` under `output/runs/`; writes `metadata.json` via `model_dump_json()`
- Update `config_app.py`: add `OUTPUT_PATH = "output"`, remove `CC_STREAMS_PATH`, `MAS_REVIEWS_PATH`, `RESULTS_PATH`
- Update `app.py:main()`: create `RunContext` after engine type is known, pass to `_run_cc_engine_path()` and `_run_mas_engine_path()`
- For CC paths: `RunContext` is created after `run_cc_solo`/`run_cc_teams` returns (execution_id only known after CC runs). The stream file is written to a temp location first, then moved into the run dir. This matches the existing pattern where cc_teams renames the stream file after extracting session_id.
- `ArtifactRegistry` calls updated to register paths from `RunContext`
- GUI evaluation page `default_traces_dir` (`evaluation.py:320`) updated to `"output/runs/"`

**Files**:

- `src/app/utils/run_context.py` (new -- `RunContext` dataclass with path helpers and metadata writer)
- `src/app/config/config_app.py` (edit -- add `OUTPUT_PATH`, remove `CC_STREAMS_PATH`, `MAS_REVIEWS_PATH`, `RESULTS_PATH`)
- `src/app/config/judge_settings.py` (edit -- remove `trace_storage_path` default or point to `OUTPUT_PATH`)
- `src/app/app.py` (edit -- create `RunContext` in `main()`, pass to engine/eval paths)
- `src/gui/pages/evaluation.py` (edit -- update `default_traces_dir`)
- `.gitignore` (edit -- add `output/`, keep `results/`)
- `tests/utils/test_run_context.py` (new -- test directory creation, metadata.json content, path helpers)

---

##### Feature 8b: Migrate All Writers to Per-Run Directories (STORY-009, depends: STORY-008)

**Description**: Update all 6 file writers to use `RunContext` path helpers instead of constructing paths from legacy constants. Each writer receives `RunContext` (or `run_dir: Path`) and writes to the run directory. Remove timestamp generation from individual writers — `RunContext` owns the timestamp. Remove `CC_STREAMS_PATH` usage from `cc_engine.py`, `LOGS_BASE_PATH/traces` from `trace_processors.py`, `MAS_REVIEWS_PATH` from `review_persistence.py`, and hardcoded `results/reports` from `run_cli.py`.

**Acceptance Criteria**:

- [ ] AC1: `run_cc_solo` writes stream to `run_context.stream_path` instead of `cc_streams/cc_solo_{exec_id}_{ts}.json`
- [ ] AC2: `run_cc_teams` writes stream to `run_context.stream_path` instead of `cc_streams/cc_teams_{exec_id}_{ts}.jsonl`
- [ ] AC3: `TraceCollector._store_trace()` writes to `run_context.trace_path` instead of `traces/trace_{exec_id}_{ts}.jsonl`
- [ ] AC4: `ReviewPersistence.save_review()` writes to `run_context.review_path` instead of `MAS_reviews/{paper_id}_{ts}.json`
- [ ] AC5: CLI report save writes to `run_context.report_path` instead of `results/reports/{ts}.md`
- [ ] AC6: `traces.db` SQLite database writes to `output/runs/traces.db` (shared across runs, not per-run)
- [ ] AC7: `review_loader.py` deleted — dead code (no imports in `src/`, no tests), references removed `MAS_REVIEWS_PATH`
- [ ] AC8: No code references `CC_STREAMS_PATH`, `MAS_REVIEWS_PATH`, `RESULTS_PATH`, or `LOGS_BASE_PATH/traces` for file writes
- [ ] AC9: `ArtifactRegistry` entries point to new per-run paths
- [ ] AC10: Sweep runner default `output_dir` changed from `results/sweeps/{ts}` to `output/sweeps/{ts}`
- [ ] AC11: `--output-dir` CLI override on `run_sweep.py` still works
- [ ] AC12: `make validate` passes with no regressions

**Technical Requirements**:

- `cc_engine.py`: `run_cc_solo()` and `run_cc_teams()` accept `run_dir: Path` parameter; write stream to `run_dir / "stream.json"` (solo) or `run_dir / "stream.jsonl"` (teams); remove `CC_STREAMS_PATH` import and local timestamp generation
- `trace_processors.py`: `TraceCollector.__init__()` accepts optional `run_dir: Path`; `_store_trace()` writes to `run_dir / "trace.jsonl"` when set; `traces.db` moves to `resolve_project_path(OUTPUT_PATH) / "runs" / "traces.db"` (shared index)
- `review_persistence.py`: `ReviewPersistence.__init__()` accepts optional `run_dir: Path`; `save_review()` writes to `run_dir / "review.json"` when set; remove `MAS_REVIEWS_PATH` import
- `run_cli.py`: report save uses `run_context.report_path` instead of constructing `Path("results") / "reports" / f"{timestamp}.md"`
- `sweep_runner.py`: remove `RESULTS_PATH` import (no default `output_dir` here — `SweepConfig.output_dir` is a required field)
- `run_sweep.py`: change default `output_dir` from `f"results/sweeps/{ts}"` to `f"output/sweeps/{ts}"` (`run_sweep.py:150` owns the default); update `--output-dir` argparse default if hardcoded
- `app.py`: pass `RunContext` (or `run_dir`) to CC engine functions and trace/review components
- All writers: remove individual `strftime()` calls — `RunContext` directory name carries the timestamp

**Files**:

- `src/app/engines/cc_engine.py` (edit -- accept `run_dir`, write stream to run dir, remove `CC_STREAMS_PATH`)
- `src/app/judge/trace_processors.py` (edit -- accept `run_dir`, write trace to run dir, move `traces.db`)
- `src/app/data_utils/review_persistence.py` (edit -- accept `run_dir`, write review to run dir, remove `MAS_REVIEWS_PATH`)
- `src/app/data_utils/review_loader.py` (delete -- dead code, no imports in src/, no tests)
- `src/run_cli.py` (edit -- use `run_context.report_path` for report save)
- `src/app/app.py` (edit -- plumb `RunContext` to all writers)
- `src/app/benchmark/sweep_runner.py` (edit -- change default `output_dir` to `output/sweeps/`)
- `src/run_sweep.py` (edit -- update default `--output-dir` if hardcoded)
- `tests/engines/test_cc_engine.py` (edit -- update stream write tests to use `run_dir`)
- `tests/judge/test_trace_processors.py` (edit -- update trace write tests)
- `tests/data_utils/test_review_persistence.py` (edit -- update review write tests)

---

##### Feature 8c: Persist Evaluation Results to `evaluation.json` (STORY-010, depends: STORY-009)

**Description**: Evaluation pipeline results are currently returned in-memory and never written to disk (except indirectly via sweep `results.json`). With per-run directories, write the composite evaluation result to `run_dir/evaluation.json` after `evaluate_comprehensive` completes. This makes each run fully self-contained: stream/trace + review + evaluation + report all in one directory.

**Acceptance Criteria**:

- [ ] AC1: `evaluation.json` is written to `run_context.evaluation_path` after `evaluate_comprehensive` returns
- [ ] AC2: `evaluation.json` contains the full `CompositeResult` (tier1, tier2, tier3, composite scores)
- [ ] AC3: `evaluation.json` is only written when evaluation actually ran (not when `skip_eval=True`)
- [ ] AC4: `ArtifactRegistry` registers `evaluation.json` as `"Evaluation"` artifact
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- In `run_evaluation_if_enabled` (`evaluation_runner.py`), after pipeline returns results, write `result_dict` to `run_context.evaluation_path` via `json.dumps()` with `indent=2`
- Guard: only write if `run_context` is provided and results are non-None
- Register artifact path in `ArtifactRegistry`

**Files**:

- `src/app/judge/evaluation_runner.py` (edit -- write `evaluation.json` after pipeline completes)
- `tests/judge/test_evaluation_runner.py` (edit -- verify `evaluation.json` written with correct content)

---

## Non-Functional Requirements

- No new external dependencies
- **Scoring changes**: Features 3–7 change evaluation score behavior. Existing score comparisons against historical runs will not be directly comparable after these changes.
- **Output directory migration**: Feature 8 consolidates all output under `output/` and removes legacy paths (`logs/Agent_evals/cc_streams/`, `logs/Agent_evals/traces/`, `results/`). Existing artifacts in those directories are not migrated. No backward compatibility layer.
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S12-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).

## Out of Scope

- CC-specific Tier 3 graph metrics (delegation fan-out, task completion rate, teammate utilization) — requires separate design
- Richer CC stream event parsing (tool use events, assistant messages) — only task lifecycle events needed for now
- GUI Sweep Page — deferred from Sprint 11
- `create_llm_model()` registry pattern refactor — deferred from Sprint 11
- BERTScore re-enablement — blocked by build issues, Levenshtein sufficient for deduplication

---

## Notes for Ralph Loop

### Priority Order

- **P0 (bug fix)**: STORY-001 (stream event parsing — root cause), STORY-002 (cc_teams flag passthrough — enables correct engine_type)
- **P1 (scoring fix)**: STORY-003 → STORY-004 (Tier 3 fallback + single-agent redistribution), STORY-005 (time_taken timestamps), STORY-006 (semantic dedup), STORY-007 (task_success continuous)
- **P2 (UX)**: STORY-008 → STORY-009 → STORY-010 (per-run output directories)

### Story Breakdown (10 stories total)

- **Feature 1** → STORY-001: Fix CC teams stream event parsing
  Update `_apply_event` to capture `task_started`/`task_completed` system events as team artifacts. Remove stale `_TEAM_EVENT_TYPES` constant. TDD: update existing `parse_stream_json` tests to use real CC event format, add new tests for task lifecycle events. Files: `src/app/engines/cc_engine.py`, `tests/engines/test_cc_engine.py`.

- **Feature 2** → STORY-002: Pass `cc_teams` flag through to `engine_type` assignment (depends: STORY-001)
  Add `cc_teams` param to `main()` and `_run_cc_engine_path()`. Wire from CLI and GUI. Change `engine_type` to use flag instead of `team_artifacts` inference. TDD: update `test_cc_engine_wiring.py` tests. Files: `src/app/app.py`, `src/run_cli.py`, `src/gui/pages/run_app.py`, `tests/cli/test_cc_engine_wiring.py`.

- **Feature 3** → STORY-003: Skip Tier 3 for empty trace data
  Add early return in `_execute_tier3` when trace has no tool_calls or agent_interactions. Triggers existing fallback (neutral 0.5 scores). Files: `src/app/judge/evaluation_pipeline.py`, `tests/evals/test_evaluation_pipeline.py`.

- **Feature 4** → STORY-004: Wire `evaluate_composite_with_trace` into production (depends: STORY-003)
  Update `_generate_composite_score` to accept trace data and route to `evaluate_composite_with_trace` for single-agent detection. Retain `GraphTraceData` ref in `evaluate_comprehensive`. Files: `src/app/judge/evaluation_pipeline.py`, `tests/evals/test_evaluation_pipeline.py`, `tests/evals/test_composite_scorer.py`.

- **Feature 5** → STORY-005: Propagate actual execution timestamps to `time_taken` (depends: STORY-004)
  Add timing to `CCResult`, capture around subprocess in `run_cc_solo`/`run_cc_teams`, propagate through `evaluation_runner` → `evaluation_pipeline` → `_execute_tier1`. Files: `src/app/engines/cc_engine.py`, `src/app/app.py`, `src/app/judge/evaluation_runner.py`, `src/app/judge/evaluation_pipeline.py`, tests.

- **Feature 6** → STORY-006: Deduplicate `semantic_score` from `cosine_score`
  Change `compute_semantic_similarity` to use Levenshtein instead of cosine. Uses existing `textdistance` library. Files: `src/app/judge/traditional_metrics.py`, `src/app/data_models/evaluation_models.py`, `tests/evals/test_traditional_metrics.py`.

- **Feature 7** → STORY-007: Replace binary `task_success` with continuous score
  Change `assess_task_success` from `0/1` to `min(1.0, similarity/threshold)`. Files: `src/app/judge/traditional_metrics.py`, `tests/evals/test_traditional_metrics.py`.

- **Feature 8a** → STORY-008: Introduce `RunContext` and per-run directory infrastructure
  Create `RunContext` dataclass with path helpers, `metadata.json` writer, unified timestamp. Add `OUTPUT_PATH`, remove `CC_STREAMS_PATH`/`MAS_REVIEWS_PATH`/`RESULTS_PATH`. Create in `main()`. Files: `src/app/utils/run_context.py` (new), `src/app/config/config_app.py`, `src/app/config/judge_settings.py`, `src/app/app.py`, `src/gui/pages/evaluation.py`, `tests/utils/test_run_context.py` (new).

- **Feature 8b** → STORY-009: Migrate all writers to per-run directories (depends: STORY-008, STORY-005)
  Update `cc_engine.py`, `trace_processors.py`, `review_persistence.py`, `run_cli.py`, `sweep_runner.py` to write via `RunContext`/`OUTPUT_PATH` paths. Delete dead `review_loader.py`. Remove legacy path constants usage. Files: `src/app/engines/cc_engine.py`, `src/app/judge/trace_processors.py`, `src/app/data_utils/review_persistence.py`, `src/app/data_utils/review_loader.py` (delete), `src/run_cli.py`, `src/app/benchmark/sweep_runner.py`, `src/app/app.py`, tests.

- **Feature 8c** → STORY-010: Persist evaluation results to `evaluation.json` (depends: STORY-009)
  Write `CompositeResult` to `run_dir/evaluation.json` after pipeline completes. Files: `src/app/judge/evaluation_runner.py`, `tests/judge/test_evaluation_runner.py`.

### Notes for CC Agent Teams

Reference: `docs/analysis/CC-agent-teams-orchestration.md`

#### Teammate Definitions

| Teammate | Role | Model | Permissions | TDD Responsibility |
| --- | --- | --- | --- | --- |
| Lead | Coordination, wave gates, `make validate` | sonnet | delegate mode | Runs full validation at wave boundaries |
| teammate-1 | Developer (src/ + tests/) | opus | acceptEdits | `testing-python` (RED) → `implementing-python` (GREEN) → `make quick_validate` |
| teammate-2 | Developer (traditional_metrics + tests) | opus | acceptEdits | `testing-python` (RED) → `implementing-python` (GREEN) → `make quick_validate` |

#### File-Conflict Dependencies

| Story | Logical Dep | Shared File / Reason |
| --- | --- | --- |
| STORY-002 | STORY-001 | `cc_engine.py` (STORY-001 changes event parsing that STORY-002's tests depend on) |
| STORY-004 | STORY-003 | `evaluation_pipeline.py` (STORY-003 changes `_execute_tier3`; STORY-004 changes `_generate_composite_score` in same file) |
| STORY-005 | STORY-004 | `evaluation_pipeline.py` (STORY-005 adds timestamp params to methods STORY-004 modified) |
| STORY-009 | STORY-008 | All writer files (STORY-009 uses `RunContext` from STORY-008) |
| STORY-009 | STORY-005 | `cc_engine.py`, `app.py` (STORY-005 adds timing fields that STORY-009's writer migration must preserve) |
| STORY-010 | STORY-009 | `evaluation_runner.py` (STORY-010 adds `evaluation.json` write after STORY-009 plumbs `RunContext`) |

#### Orchestration Waves

```text
Wave 0 (P0 bug fixes — sequential due to shared cc_engine.py):
  teammate-1: STORY-001 (F1 stream event parsing fix) → STORY-002 (F2 cc_teams flag passthrough)
  gate: lead runs `make validate`

Wave 1 (P1 scoring fixes — sequential on evaluation_pipeline.py, parallel on traditional_metrics.py):
  teammate-1: STORY-003 (F3 Tier 3 empty-trace skip) → STORY-004 (F4 wire composite_with_trace) → STORY-005 (F5 timestamp propagation)
  teammate-2: STORY-006 (F6 semantic dedup) → STORY-007 (F7 task_success continuous)
  gate: lead runs `make validate`

Wave 2 (P2 output restructuring — sequential, touches many files):
  teammate-1: STORY-008 (F8a RunContext infrastructure) → STORY-009 (F8b migrate writers) → STORY-010 (F8c evaluation.json)
  gate: lead runs `make validate`
```

#### Quality Gate Workflow

1. **Teammate completes story**: runs `make quick_validate`, marks task completed via `TaskUpdate`
2. **Teammate picks next story**: checks `TaskList` for unblocked pending tasks, claims via `TaskUpdate` with `owner`
3. **Wave boundary**: when all stories in a wave are completed, lead runs `make validate` (full suite)
4. **Lead advances**: if `make validate` passes, lead confirms sprint complete; if it fails, lead assigns fix tasks
5. **Shutdown**: after Wave 2, lead sends `shutdown_request` to all teammates, then `TeamDelete`
