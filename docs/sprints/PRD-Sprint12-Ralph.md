---
title: Product Requirements Document - Agents-eval Sprint 12
description: Sprint 12 — CC teams mode bug fixes. Fix engine_type misclassification and team artifact parsing for CC teams execution.
version: 4.3.0
created: 2026-02-25
updated: 2026-02-25
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

**Sprint 12 goal**: Fix CC teams mode classification and evaluation wiring. CC teams runs are misclassified as `cc_solo` because (1) the JSONL stream parser looks for event types (`TeamCreate`, `Task`) that CC never emits — real team events use `type=system, subtype=task_started`, and (2) `engine_type` is inferred from parsed artifacts instead of the user's explicit mode selection. This causes downstream evaluation failures: Tier 3 graph analysis is skipped, coordination/tool metrics default to 0, and the results JSON reports the wrong engine.

### Current State

| Area | Status | Gap |
| --- | --- | --- |
| CC teams engine_type | Broken | `engine_type` set to `"cc_solo"` even when CC teams mode is selected (`app.py:262`) |
| JSONL stream team event parsing | Broken | `_TEAM_EVENT_TYPES` expects `{"TeamCreate", "Task"}` but CC emits `{"type": "system", "subtype": "task_started"}` (`cc_engine.py:34`) |
| CC teams evaluation scores | Degraded | Tier 3 N/A, `coordination_quality=0`, `tool_efficiency=0` because graph trace has no team artifacts |
| `cc_teams` flag passthrough | Missing | `cc_teams` boolean consumed in CLI/GUI, never forwarded to `main()` or `_run_cc_engine_path()` |

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

## Non-Functional Requirements

- No new external dependencies
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S12-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).

## Out of Scope

- CC-specific Tier 3 graph metrics (delegation fan-out, task completion rate, teammate utilization) — requires separate design
- Richer CC stream event parsing (tool use events, assistant messages) — only task lifecycle events needed for now
- GUI Sweep Page — deferred from Sprint 11
- `create_llm_model()` registry pattern refactor — deferred from Sprint 11

---

## Notes for Ralph Loop

### Priority Order

- **P0 (bug fix)**: STORY-001 (stream event parsing — root cause), STORY-002 (cc_teams flag passthrough — enables correct engine_type)

### Story Breakdown (2 stories total):

- **Feature 1** → STORY-001: Fix CC teams stream event parsing
  Update `_apply_event` to capture `task_started`/`task_completed` system events as team artifacts. Remove stale `_TEAM_EVENT_TYPES` constant. TDD: update existing `parse_stream_json` tests to use real CC event format, add new tests for task lifecycle events. Files: `src/app/engines/cc_engine.py`, `tests/engines/test_cc_engine.py`.

- **Feature 2** → STORY-002: Pass `cc_teams` flag through to `engine_type` assignment (depends: STORY-001)
  Add `cc_teams` param to `main()` and `_run_cc_engine_path()`. Wire from CLI and GUI. Change `engine_type` to use flag instead of `team_artifacts` inference. TDD: update `test_cc_engine_wiring.py` tests. Files: `src/app/app.py`, `src/run_cli.py`, `src/gui/pages/run_app.py`, `tests/cli/test_cc_engine_wiring.py`.

### Notes for CC Agent Teams

Reference: `docs/analysis/CC-agent-teams-orchestration.md`

#### Teammate Definitions

| Teammate | Role | Model | Permissions | TDD Responsibility |
|----------|------|-------|-------------|-------------------|
| Lead | Coordination, wave gates, `make validate` | sonnet | delegate mode | Runs full validation at wave boundaries |
| teammate-1 | Developer (src/ + tests/) | opus | acceptEdits | `testing-python` (RED) → `implementing-python` (GREEN) → `make quick_validate` |

#### File-Conflict Dependencies

| Story | Logical Dep | Shared File / Reason |
|---|---|---|
| STORY-002 | STORY-001 | `cc_engine.py` (STORY-001 changes event parsing that STORY-002's tests depend on) |

#### Orchestration Waves

```text
Wave 0 (P0 bug fixes — sequential due to shared cc_engine.py):
  teammate-1: STORY-001 (F1 stream event parsing fix) → STORY-002 (F2 cc_teams flag passthrough)
  gate: lead runs `make validate`
```

#### Quality Gate Workflow

1. **Teammate completes story**: runs `make quick_validate`, marks task completed via `TaskUpdate`
2. **Teammate picks next story**: checks `TaskList` for unblocked pending tasks, claims via `TaskUpdate` with `owner`
3. **Wave boundary**: when all stories in a wave are completed, lead runs `make validate` (full suite)
4. **Lead advances**: if `make validate` passes, lead confirms sprint complete; if it fails, lead assigns fix tasks
5. **Shutdown**: after Wave 0, lead sends `shutdown_request` to all teammates, then `TeamDelete`
