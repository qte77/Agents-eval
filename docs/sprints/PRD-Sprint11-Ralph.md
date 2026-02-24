---
title: Product Requirements Document - Agents-eval Sprint 11
description: "Sprint 11: Observability, UX polish, and test quality — end-of-run artifact summary, GUI layout refactor, test hardening, data layer cleanup."
version: 4.2.0
created: 2026-02-24
updated: 2026-02-24
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

**Sprint 11 goal**: Observability and UX polish. After Sprint 10 established E2E parity across execution modes, Sprint 11 focuses on making the system easier to operate and maintain. The primary gap is that CLI runs produce artifacts (logs, traces, reviews, reports) scattered across multiple directories with no summary — operators must grep logs or know the codebase to find outputs. Secondary goals: GUI sidebar layout refactor (deferred since Sprint 8), test quality improvements from the Sprint 10 test review, and data layer cleanup.

### Current State

| Area | Status | Gap |
| --- | --- | --- |
| Artifact discoverability | Artifacts written to 5+ directories, no summary | Operator must know paths or grep logs |
| GUI layout | All settings on single page, no sidebar tabs | `run_gui.py:43` TODO since Sprint 8 |
| Test quality | `assert isinstance()` anti-pattern in ~30 occurrences | Couples tests to types, not behavior |
| Test organization | Flat `conftest.py` at `tests/` root only | Shared fixtures duplicated across subdirectories |
| Data layer | Dispatch chain repeated 4x in `datasets_peerread.py` | Inflates complexity score (12 CC points) |

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop enforces this order.**

### TDD Workflow (Mandatory for all features)

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality.
3. **REFACTOR**: Clean up while keeping tests green. Run `make validate` before marking complete.

### Test Tool Selection

| Tool | Use for | NOT for |
|------|---------|--------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation.

### Mandatory Practices

- **Mock external dependencies** (HTTP, LLM providers, file systems, subprocess) using `@patch`. Never call real APIs in unit tests.
- **Test behavior, not implementation** -- test observable outcomes (return values, side effects, error messages), not internal structure.
- **Google-style docstrings** for every new file, function, class, and method.
- **`# Reason:` comments** for non-obvious logic.
- **`make validate` MUST pass** before any story is marked complete. No exceptions.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (all features) | `testing-python` (RED) -> `implementing-python` (GREEN) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |
| Design phase | `researching-codebase` -> `designing-backend` |

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->
<!-- PARSER REQUIREMENT: No compound sub-features — one heading per story -->
<!-- PARSER REQUIREMENT: Flatten AC items — no indented sub-items under a checkbox -->
<!-- PARSER REQUIREMENT: Each sub-feature MUST have its own **Files**: section -->

#### Feature 1: End-of-Run Artifact Path Summary

**Description**: CLI runs produce artifacts across multiple directories (logs, traces, reviews, reports) with no consolidated output. Operators must know the codebase or grep logs to find where outputs landed. Add a lightweight artifact registry that components register paths into during execution, and print a summary block at the end of each CLI run listing all artifacts written and their paths.

Artifacts written during a run (identified via codebase analysis):

| # | Artifact | Default Path | Conditional On |
|---|----------|-------------|----------------|
| 1 | Log files (`.log`, `.zip`) | `logs/Agent_evals/{time}.log` | Always (on import) |
| 2 | Trace JSONL | `logs/Agent_evals/traces/trace_{id}_{ts}.jsonl` | `trace_collection=True` + events present |
| 3 | Trace SQLite DB | `logs/Agent_evals/traces/traces.db` | `trace_collection=True` |
| 4 | MAS review JSON | `results/MAS_reviews/{paper_id}_{ts}.json` | `--enable-review-tools` + tool called |
| 5 | Structured review JSON | `results/MAS_reviews/{paper_id}_{ts}_structured.json` | Same as #4 |
| 6 | Markdown report | `results/reports/{ts}.md` | `--generate-report` flag |
| 7 | Sweep results JSON | `{output_dir}/results.json` | Sweep mode |
| 8 | Sweep summary MD | `{output_dir}/summary.md` | Sweep mode |

**Acceptance Criteria**:

- [ ] AC1: An `ArtifactRegistry` singleton exists with `register(label: str, path: Path)` and `summary() -> list[tuple[str, Path]]` methods
- [ ] AC2: Each component that writes to disk registers its output path via `ArtifactRegistry.register()` — log setup, trace collector, review persistence, report generator, sweep runner
- [ ] AC3: At the end of every CLI run (`run_cli.py`), a summary block is printed to stdout listing all artifacts written during the run, grouped by category
- [ ] AC4: When no artifacts were written (e.g., `--skip-eval` with no report), the summary prints "No artifacts written"
- [ ] AC5: Artifact paths are printed as absolute paths so they can be copy-pasted into shell commands
- [ ] AC6: The summary is also logged via loguru at INFO level for inclusion in log files
- [ ] AC7: Sweep mode (`run_sweep.py`) also prints the artifact summary at the end of the sweep
- [ ] AC8: Existing tests continue to pass — registration is a no-op side effect that doesn't change return values
- [ ] AC9: New tests verify registry behavior: register, summary, reset, empty state
- [ ] AC10: `make validate` passes with no regressions

**Technical Requirements**:

- Add `ArtifactRegistry` class in `src/app/utils/artifact_registry.py` — singleton with thread-safe `register()`, `summary()`, and `reset()` methods. Use module-level `_global_registry` pattern (same as `get_trace_collector()` in `trace_processors.py`)
- Registration points (add `artifact_registry.register()` calls):
  - `src/app/utils/log.py` — register the log file path after `logger.add()`
  - `src/app/judge/trace_processors.py:_store_trace()` — register JSONL file path after write
  - `src/app/data_utils/review_persistence.py:save_review()` — register review file path after write
  - `src/app/tools/peerread_tools.py:save_structured_review` — register structured review path after write
  - `src/app/reports/report_generator.py:save_report()` — register report path after write
  - `src/app/benchmark/sweep_runner.py:_save_results_json()` — register results.json path after write
  - `src/app/benchmark/sweep_runner.py:_save_results()` — register summary.md path after write
- Summary printer in `src/run_cli.py` — call `get_artifact_registry().summary()` after `main()` returns, format and print
- Summary printer in `src/app/benchmark/sweep_runner.py:run()` — print after sweep completes
- Do NOT register the SQLite DB path (it's a persistent store, not a per-run artifact)
- Do NOT register PeerRead dataset cache (download-only mode, not a run artifact)

**Files**:

- `src/app/utils/artifact_registry.py` (new -- `ArtifactRegistry` singleton)
- `src/app/utils/log.py` (edit -- register log path)
- `src/app/judge/trace_processors.py` (edit -- register trace JSONL path)
- `src/app/data_utils/review_persistence.py` (edit -- register review path)
- `src/app/tools/peerread_tools.py` (edit -- register structured review path)
- `src/app/reports/report_generator.py` (edit -- register report path)
- `src/app/benchmark/sweep_runner.py` (edit -- register sweep result paths, print summary)
- `src/run_cli.py` (edit -- print artifact summary after main() returns)
- `tests/utils/test_artifact_registry.py` (new -- registry unit tests)

---

#### Feature 2: GUI Layout Refactor -- Sidebar Tabs

**Description**: The GUI currently renders all settings on a single page with no sidebar navigation. The `run_gui.py:43` TODO ("create sidebar tabs, move settings to page") has been deferred since Sprint 8. Refactor the Streamlit layout to use sidebar tabs separating Run, Settings, Evaluation Results, and Agent Graph into distinct navigation sections. This improves discoverability and reduces visual clutter.

**Acceptance Criteria**:

- [ ] AC1: Sidebar contains navigation tabs for: Run, Settings, Evaluation, Agent Graph
- [ ] AC2: Settings page is accessible via its own sidebar tab (not inline on the Run page)
- [ ] AC3: Run page shows only execution controls (provider, engine, paper, query, run button)
- [ ] AC4: Tab selection persists across Streamlit reruns within a session
- [ ] AC5: All existing GUI functionality works unchanged after layout refactor
- [ ] AC6: The TODO comment at `run_gui.py:43` is removed
- [ ] AC7: `make validate` passes with no regressions

**Technical Requirements**:

- Use `st.sidebar` with `st.radio` or `st.selectbox` for tab navigation (Streamlit's native `st.tabs` is for inline tabs, not sidebar navigation)
- Move settings rendering from inline position to a dedicated conditional block
- Preserve session state across tab switches — settings values must not reset
- Keep page module structure (`src/gui/pages/`) unchanged — refactor is in `run_gui.py` layout orchestration only

**Files**:

- `src/run_gui.py` (edit -- sidebar navigation, remove TODO comment)
- `src/gui/pages/run_app.py` (edit -- extract run-only controls from settings)
- `tests/gui/test_sidebar_navigation.py` (new -- tab rendering and persistence)

---

#### Feature 3: Replace `assert isinstance` Tests with Behavioral Assertions

**Description**: ~30 occurrences of `assert isinstance(obj, Type)` across 12 test files (identified as H4, M1-M3 in the Sprint 10 tests review). These assertions verify type identity rather than behavior — they pass even if the object has wrong values, missing fields, or broken methods. Replace with assertions on observable behavior: return values, field access, method outputs.

**Acceptance Criteria**:

- [ ] AC1: All `assert isinstance()` occurrences in `tests/agents/` replaced with behavioral assertions
- [ ] AC2: All `assert isinstance()` occurrences in `tests/judge/` replaced with behavioral assertions
- [ ] AC3: All `assert isinstance()` occurrences in `tests/data_models/` replaced with behavioral assertions
- [ ] AC4: All `assert isinstance()` occurrences in `tests/reports/` replaced with behavioral assertions
- [ ] AC5: Remaining `assert isinstance()` in other test directories replaced or explicitly justified with `# Reason:` comment
- [ ] AC6: Zero unjustified `assert isinstance()` occurrences remain in `tests/`
- [ ] AC7: Hardcoded relative path in `test_peerread_tools_error_handling.py` replaced with `tmp_path` fixture (H8 from Sprint 10 test review)
- [ ] AC8: `make validate` passes with no regressions

**Technical Requirements**:

- Replace pattern: `assert isinstance(result, CompositeResult)` -> `assert result.composite_score >= 0.0` (test a real field)
- Replace pattern: `assert isinstance(items, list)` -> `assert len(items) >= 0` or assert on element content
- Preserve test intent — if the test was checking "function returns correct type", replace with "function returns object with expected properties"
- Some `isinstance` checks may be justified (e.g., testing polymorphic return types) — keep those with `# Reason:` comment
- H8 fix: replace hardcoded path string with `tmp_path` fixture to avoid Bandit B108 and disk pollution (see AGENT_LEARNINGS "Test Filesystem Isolation" pattern)

**Files**:

- `tests/agents/test_agent_system.py` (edit)
- `tests/judge/test_evaluation_pipeline.py` (edit)
- `tests/judge/test_composite_scorer.py` (edit)
- `tests/data_models/test_evaluation_models.py` (edit)
- `tests/data_models/test_app_models.py` (edit)
- `tests/reports/test_report_generator.py` (edit)
- `tests/reports/test_suggestion_engine.py` (edit)
- `tests/tools/test_peerread_tools_error_handling.py` (edit -- H8 hardcoded path fix)
- Additional test files as identified by `grep -r "assert isinstance" tests/`

---

#### Feature 4: Test Organization -- Subdirectory `conftest.py` Files

**Description**: Test fixtures are either duplicated across test files or centralized in the root `tests/conftest.py`. Subdirectories like `tests/agents/`, `tests/judge/`, `tests/tools/`, and `tests/evals/` lack their own `conftest.py`, forcing tests to recreate common fixtures locally. Add subdirectory-level conftest files to share domain-specific fixtures (identified as M5, M6 in Sprint 10 tests review).

**Acceptance Criteria**:

- [ ] AC1: `tests/agents/conftest.py` exists with shared agent test fixtures (mock agent, mock run context)
- [ ] AC2: `tests/judge/conftest.py` exists with shared evaluation fixtures (sample CompositeResult, sample EvaluationResults, mock pipeline)
- [ ] AC3: `tests/tools/conftest.py` exists with shared tool test fixtures (mock PeerRead config, mock loader)
- [ ] AC4: `tests/evals/conftest.py` exists with shared evaluation engine fixtures
- [ ] AC5: Duplicate fixture definitions removed from individual test files in favor of conftest imports
- [ ] AC6: All `tempfile.mkdtemp()` / `tempfile.NamedTemporaryFile()` usages in integration tests replaced with pytest `tmp_path` fixture (L7, L8 from Sprint 10 test review)
- [ ] AC7: No test behavior changes — all tests produce identical results
- [ ] AC8: `make validate` passes with no regressions

**Technical Requirements**:

- Identify duplicate fixtures by searching for identical `@pytest.fixture` definitions across test files in each subdirectory
- Move shared fixtures to subdirectory `conftest.py` — pytest auto-discovers these
- Keep test-specific one-off fixtures in their respective test files
- Do not move fixtures that are only used by a single test file

**Files**:

- `tests/agents/conftest.py` (new)
- `tests/judge/conftest.py` (new)
- `tests/tools/conftest.py` (new)
- `tests/evals/conftest.py` (new)
- Various test files in each subdirectory (edit -- remove duplicate fixtures)

---

#### Feature 5: Data Layer -- Dispatch Chain Registry Refactor

**Description**: `datasets_peerread.py` has 4 methods each with `if/elif/else` chains dispatching on `data_type` ("reviews"/"parsed_pdfs"/"pdfs"). Each chain adds 3 cognitive complexity points = 12 total from one repeated pattern. Replace with a `DATA_TYPE_SPECS` registry dict for single-lookup dispatch. Identified as Review F10 in Sprint 10, deferred for scope reasons.

**Acceptance Criteria**:

- [ ] AC1: A `DATA_TYPE_SPECS` dict maps each `data_type` string to its type-specific configuration (file extension, parser, URL path component)
- [ ] AC2: All 4 dispatch chains in `datasets_peerread.py` replaced with registry lookups
- [ ] AC3: Invalid `data_type` values raise `ValueError` at a single validation point instead of falling through to `else` branches
- [ ] AC4: Module cognitive complexity reduced (target: net -8 CC points or more)
- [ ] AC5: All existing `tests/data_utils/test_datasets_peerread.py` tests pass unchanged
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- Define `DATA_TYPE_SPECS: dict[str, DataTypeSpec]` at module level with a simple dataclass or TypedDict for the spec
- Validate `data_type` once at method entry, not per-branch
- Keep the public method signatures unchanged — this is an internal refactor
- Run `make complexity` before and after to measure CC reduction

**Files**:

- `src/app/data_utils/datasets_peerread.py` (edit -- add registry, replace dispatch chains)
- `tests/data_utils/test_datasets_peerread.py` (edit -- add test for invalid data_type ValueError)

---

#### Feature 6: CC Engine Empty Query Fix -- Shared Query Builder

**Description**: When `--engine=cc` is used with `--paper-id` but no `--query`, the CC engine receives an empty string and crashes with `"Input must be provided either through stdin or as a prompt argument when using --print"`. The MAS engine avoids this because `app.py:_prepare_query()` auto-generates a default prompt from `paper_id` — but the CC path in both CLI (`run_cli.py`) and GUI (`run_app.py`) bypasses `_prepare_query()` and passes the raw empty query directly to `run_cc_solo()`/`run_cc_teams()`. Add a shared `build_cc_query()` function in `cc_engine.py` that both CLI and GUI call before invoking the CC subprocess.

**Acceptance Criteria**:

- [ ] AC1: `make app_cli ARGS="--paper-id=1105.1072 --engine=cc"` no longer crashes with empty query error
- [ ] AC2: A `build_cc_query(query, paper_id)` function exists in `cc_engine.py` that returns a non-empty prompt when `paper_id` is provided
- [ ] AC3: The default prompt template for solo mode matches `app.py:_prepare_query()` — `"Generate a structured peer review for paper '{paper_id}'."`
- [ ] AC3a: The default prompt template for teams mode (`--cc-teams`) prepends `"Use a team of agents."` — `"Use a team of agents. Generate a structured peer review for paper '{paper_id}'."` to increase likelihood of CC spawning teammates
- [ ] AC4: When both `query` and `paper_id` are empty, `build_cc_query()` raises `ValueError` with a clear message
- [ ] AC5: CLI (`run_cli.py`) calls `build_cc_query()` before `run_cc_solo()`/`run_cc_teams()`
- [ ] AC6: GUI (`run_app.py:_prepare_cc_result`) calls `build_cc_query()` before `run_cc_solo()`/`run_cc_teams()`, receiving `paper_id` from `_execute_query_background()`
- [ ] AC7: Explicit `--query` still takes precedence over auto-generated prompt
- [ ] AC8: `make validate` passes with no regressions

**Technical Requirements**:

- Add `DEFAULT_REVIEW_PROMPT_TEMPLATE = "Generate a structured peer review for paper '{paper_id}'."` as a constant in `src/app/config/config_app.py`. Both `build_cc_query()` and `app.py:_prepare_query()` reference this constant instead of duplicating the string (DRY).
- Add `build_cc_query(query: str, paper_id: str | None = None, cc_teams: bool = False) -> str` in `src/app/engines/cc_engine.py`. When `cc_teams=True` and no explicit query, prepend `"Use a team of agents."` to the generated prompt.
- Update `app.py:_prepare_query()` to use `DEFAULT_REVIEW_PROMPT_TEMPLATE` from `config_app.py` instead of its hardcoded `default_tmpl` string.
- CLI fix: `run_cli.py:138` — replace `query = args.get("query", "")` with `build_cc_query(args.get("query", ""), args.get("paper_id"))`
- GUI fix: `run_app.py:_prepare_cc_result()` — add `paper_id` parameter, call `build_cc_query()` before dispatch
- GUI fix: `run_app.py:_execute_query_background()` line 318 — pass `paper_id` to `_prepare_cc_result()`

**Files**:

- `src/app/config/config_app.py` (edit -- add `DEFAULT_REVIEW_PROMPT_TEMPLATE` constant)
- `src/app/engines/cc_engine.py` (edit -- add `build_cc_query()`, use shared constant)
- `src/app/app.py` (edit -- use `DEFAULT_REVIEW_PROMPT_TEMPLATE` in `_prepare_query()`)
- `src/run_cli.py` (edit -- use `build_cc_query()` before CC dispatch)
- `src/gui/pages/run_app.py` (edit -- pass `paper_id` through to `_prepare_cc_result()`, use `build_cc_query()`)
- `tests/engines/test_cc_engine_query.py` (new -- unit tests for `build_cc_query()` three branches)

---

#### Feature 7: Persist CC JSONL Stream to Disk

**Description**: The CC teams JSONL stream (`--output-format stream-json`) is consumed live from stdout via `parse_stream_json()` and discarded after parsing. If the process crashes, or if post-hoc analysis is needed, the raw stream data is lost. Persist the raw JSONL stream to `{LOGS_BASE_PATH}/cc_streams/` during execution, consistent with how MAS traces are stored under `{LOGS_BASE_PATH}/traces/`. Solo mode (`--output-format json`) should also persist its raw JSON response for parity.

Existing trace storage already uses `LOGS_BASE_PATH` (`logs/Agent_evals`) via `JudgeSettings.trace_storage_path`. CC stream persistence should follow the same pattern.

**Acceptance Criteria**:

- [ ] AC1: CC teams mode writes raw JSONL stream to `{LOGS_BASE_PATH}/cc_streams/cc_teams_{execution_id}_{timestamp}.jsonl` during execution
- [ ] AC2: CC solo mode writes raw JSON response to `{LOGS_BASE_PATH}/cc_streams/cc_solo_{execution_id}_{timestamp}.json` after completion
- [ ] AC3: Stream persistence uses `LOGS_BASE_PATH` from `config_app.py`, not a hardcoded path
- [ ] AC4: Stream is written incrementally (line-by-line tee) during teams execution, not buffered until process exit — partial data is preserved if the process crashes or times out
- [ ] AC5: `parse_stream_json()` behavior is unchanged — persistence is a side effect, not a replacement for live parsing
- [ ] AC6: Persisted files are registered with `ArtifactRegistry` (Feature 1) when both features are implemented
- [ ] AC7: `make validate` passes with no regressions

**Technical Requirements**:

- Add `CC_STREAMS_PATH = f"{LOGS_BASE_PATH}/cc_streams"` to `src/app/config/config_app.py`
- In `run_cc_teams()`: wrap `proc.stdout` iterator with a tee that writes each line to the JSONL file before yielding to `parse_stream_json()`
- In `run_cc_solo()`: write `proc.stdout` (raw JSON) to file after successful parse
- Create output directory lazily (`Path.mkdir(parents=True, exist_ok=True)`) on first write
- Use `execution_id` from parsed result for filename; fall back to timestamp-only if `execution_id` is `"unknown"`

**Files**:

- `src/app/config/config_app.py` (edit -- add `CC_STREAMS_PATH`)
- `src/app/engines/cc_engine.py` (edit -- tee stream to disk in `run_cc_teams()`, write response in `run_cc_solo()`)
- `tests/engines/test_cc_stream_persistence.py` (new -- verify file creation, incremental write, content matches parsed result)

---

#### Feature 8: App Page Free-Form Query Persistence Fix

**Description**: The free-form query `text_input` on the App page (`run_app.py:602`) has no Streamlit `key` parameter. When the user types a query, navigates to another page (Settings, Evaluation, etc.), and returns to App, the query field is empty. All other App page widgets (engine radio, input mode radio, paper selection, CC Teams checkbox) have explicit keys and persist correctly. The fallback query input at `run_app.py:426` (shown when no papers are downloaded) has the same issue.

**Acceptance Criteria**:

- [ ] AC1: Free-form query text persists when navigating away from App page and returning
- [ ] AC2: Fallback query input (no papers available) also persists across page navigation
- [ ] AC3: No widget key conflicts with existing keys on the App or Settings pages
- [ ] AC4: `make validate` passes with no regressions

**Technical Requirements**:

- `run_app.py:602`: Add `key="freeform_query"` to `text_input(RUN_APP_QUERY_PLACEHOLDER)`
- `run_app.py:426`: Add `key="freeform_query_fallback"` to `text_input(RUN_APP_QUERY_PLACEHOLDER)`
- No other changes needed — Streamlit auto-persists widget values when a `key` is provided

**Files**:

- `src/gui/pages/run_app.py` (edit -- add `key` to two `text_input` calls)

---

#### Feature 9: Move Remaining Config Models to `src/app/config/`

**Description**: `LogfireConfig` and `PeerReadConfig` are config-shaped `BaseModel` subclasses living outside `src/app/config/`. Sprint 11 already consolidated `JudgeSettings`, `CommonSettings`, and `AppEnv` into `config/`. Move these two to complete the consolidation. Same mechanical pattern: move class, update imports, delete if source file becomes empty.

**Acceptance Criteria**:

- [ ] AC1: `LogfireConfig` lives in `src/app/config/logfire_config.py`
- [ ] AC2: `PeerReadConfig` lives in `src/app/config/peerread_config.py`
- [ ] AC3: All import sites (src + tests) updated to new paths
- [ ] AC4: `src/app/config/__init__.py` exports both classes
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- Move `LogfireConfig` from `src/app/utils/load_configs.py:63` to `src/app/config/logfire_config.py` (new). Keep `load_config()` in `load_configs.py`, update its import.
- Move `PeerReadConfig` from `src/app/data_models/peerread_models.py:114` to `src/app/config/peerread_config.py` (new). Update import in `peerread_models.py` if other models reference it, otherwise just update external import sites.
- Update `src/app/config/__init__.py` exports.

**Files**:

- `src/app/config/logfire_config.py` (new -- receives `LogfireConfig`)
- `src/app/config/peerread_config.py` (new -- receives `PeerReadConfig`)
- `src/app/utils/load_configs.py` (edit -- remove class, update import)
- `src/app/data_models/peerread_models.py` (edit -- remove class, update import)
- `src/app/config/__init__.py` (edit -- add exports)
- `src/app/data_utils/datasets_peerread.py` (edit -- update import)
- `tests/agents/test_logfire_instrumentation.py` (edit -- update import)
- `tests/utils/test_logfire_config.py` (edit -- update import)
- `tests/agents/test_peerread_tools.py` (edit -- update import)
- `tests/data_utils/test_datasets_peerread.py` (edit -- update import)
- `tests/integration/test_peerread_real_dataset_validation.py` (edit -- update import)

---

#### Feature 10: Search Tool HTTP Error Resilience

**Description**: The Researcher agent uses `duckduckgo_search_tool()` from PydanticAI, backed by the `ddgs 9.10.0` library. This library routes searches through third-party backends (Mojeek, Brave) that frequently block automated requests with HTTP 403 (Forbidden) and HTTP 429 (Too Many Requests). When the search tool raises an `HTTPError`, the exception propagates uncaught through PydanticAI agent execution up to `app.py:410`, which wraps it as `"Aborting app"` and crashes the entire run. The review can still be generated without web search results — the search is supplementary, not required.

The `ddgs` library cycles through Mojeek (403) and Brave (429) — both block automated requests. The fix wraps the search tool so HTTP errors return a message to the agent instead of crashing the app. The agent then generates the review using paper content alone, which is the expected graceful degradation.

Observed errors:

- `HTTPError('HTTP 403 Forbidden for URL: https://www.mojeek.com/search?q=...')`
- `HTTPError('HTTP 429 Too Many Requests for URL: https://search.brave.com/search?q=...')`

**Acceptance Criteria**:

- [ ] AC1: HTTP 403/429 errors from either search tool do not crash the app
- [ ] AC2: When a search tool fails, the agent receives a descriptive error message (e.g., `"Web search unavailable: HTTP 403. Proceed with available information."`) instead of an unhandled exception
- [ ] AC3: A warning is logged at `logger.warning` level when search fails, including the HTTP status code and URL
- [ ] AC4: The review is still generated using paper content and agent knowledge when search is unavailable
- [ ] AC6: The resilient wrapper applies to both DuckDuckGo and Tavily tools — same error-catching pattern for both
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- Create a generic `resilient_tool_wrapper` that takes any PydanticAI tool and catches `HTTPError` (and broader `Exception` for network failures), returning an error string to the agent instead of raising. PydanticAI tools can return strings — the agent treats them as tool output and adapts.
- Apply the wrapper to both `duckduckgo_search_tool()` and `tavily_search_tool()` — same pattern, no duplication.
- Register both wrapped tools: `tools=[wrapped_ddg_tool, wrapped_tavily_tool]`. The agent sees both and can fall back between them. Requires `TAVILY_API_KEY` env var (already configured).
- No dedicated test file — the wrapper is a trivial try/except (~5 lines). Validation is manual: run `make app_cli ARGS="--paper-id=1105.1072"` and confirm the review completes without crashing.

**Files**:

- `src/app/agents/agent_system.py` (edit -- wrap `duckduckgo_search_tool()` with error-catching wrapper, add `tavily_search_tool()`)

---

#### Feature 11: Sub-Agent Result Validation JSON Parsing Fix

**Description**: When OpenAI-compatible providers (Cerebras, Groq, etc.) fail to return structured output, PydanticAI's `result.output` is a plain string instead of a Pydantic model instance. The fallback path in `_validate_model_return()` calls `str(result.output)` and passes the result to `model_validate()`. This produces a Python repr string (e.g., `"insights=['User requests...'] approval=True"`) which is neither valid JSON nor a dict — `model_validate()` rejects it with `Input should be a valid dictionary or instance of ResearchSummary`. The error repeats on every sub-agent delegation (synthesis, analysis), causing the entire run to fail.

Observed errors (Cerebras `gpt-oss-120b`):

```text
Invalid pydantic data model format: 1 validation error for ResearchSummary
  Input should be a valid dictionary or instance of ResearchSummary [type=model_type,
  input_value="insights=['User requests...ctions.'] approval=True", input_type=str]
```

**Acceptance Criteria**:

- [ ] AC1: `_validate_model_return()` attempts `model_validate_json()` first when `result.output` is a string, falling back to `model_validate()` for dict/model inputs
- [ ] AC2: When the string is valid JSON (e.g., `'{"insights": [], "approval": false}'`), the model is successfully parsed
- [ ] AC3: When the string is not valid JSON (Python repr), the error message includes the actual string content to aid debugging
- [ ] AC4: The delegation tools (`delegate_research`, `delegate_analysis`, `delegate_synthesis`) pass `result.output` directly to `_validate_model_return()` instead of wrapping in `str()`
- [ ] AC5: When `result.output` is already the correct Pydantic type, it is returned directly (existing behavior preserved)
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- Change `_validate_model_return()` signature from `result_output: str` to `result_output: Any` to accept string, dict, or model instances
- Inside `_validate_model_return()`: if input is `str`, try `result_model.model_validate_json(result_output)` first; if that raises `ValidationError`, re-raise with clear context. If input is dict or model, use `result_model.model_validate(result_output)` as before.
- Remove `str()` wrapping at call sites (lines 185, 212, 239) — pass `result.output` directly
- No new dependencies — `model_validate_json()` is built into Pydantic `BaseModel`

**Files**:

- `src/app/agents/agent_system.py` (edit -- fix `_validate_model_return` and call sites)
- `tests/agents/test_agent_system.py` (edit -- add tests for JSON string parsing and error cases)

---

## Non-Functional Requirements

- No new external dependencies without PRD validation
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S11-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).

## Out of Scope

**Deferred from Sprint 10 (not aligned with Sprint 11 observability/polish goal):**

- GUI Sweep Page -- full sweep GUI with progress indicators, multi-select papers, composition toggles. Needs design work.
- CC-specific Tier 3 graph metrics (delegation fan-out, task completion rate, teammate utilization)
- `create_llm_model()` registry pattern refactor -- the if/elif chain is fine for 19 providers
- Provider health checks or connectivity validation
- `--judge-provider` CLI validation

**Deferred test review findings (LOW priority from tests-parallel-review-2026-02-21.md):**

- `@pytest.mark.parametrize` additions for provider tests and recommendation tests (M7, M8)
- `hasattr()` replacements with behavioral tests (M4)
- Weak assertion strengthening in `test_suggestion_engine.py` and `test_report_generator.py` (M18, L5)
- `@pytest.mark.slow` markers on performance baselines (L10)

**Picked up from Sprint 10 deferrals into Sprint 11:**

- Hardcoded relative path fix in `test_peerread_tools_error_handling.py` (H8) → F3/STORY-018
- `tempfile` -> `tmp_path` in integration tests (L7, L8) → F4/STORY-019

**Deferred to future sprint (TBD acceptance criteria, low urgency):**

- Centralized Tool Registry with Module Allowlist (MAESTRO L7.2) -- architectural, needs design
- Plugin Tier Validation at Registration (MAESTRO L7.1) -- architectural, needs design
- Error Message Sanitization (MAESTRO) -- TBD acceptance criteria
- Configuration Path Traversal Protection (MAESTRO) -- TBD acceptance criteria
- GraphTraceData Construction Simplification (`model_validate()`) -- TBD acceptance criteria
- Timeout Bounds Enforcement -- low urgency
- Hardcoded Settings Audit -- continuation of Sprint 7 (partially addressed by F9/STORY-024)
- BDD Scenario Tests for Evaluation Pipeline -- useful but not blocking

---

## Notes for Ralph Loop

### Priority Order

- **P0 (bug fix)**: STORY-021 (CC engine empty query fix), STORY-023 (App page query persistence fix), STORY-025 (search tool HTTP error resilience -- blocks MAS runs), STORY-026 (sub-agent result validation fix -- blocks non-OpenAI providers)
- **P1 (observability)**: STORY-016 (artifact summary -- new capability, standalone), STORY-022 (CC stream persistence -- trace data for post-hoc analysis)
- **P2 (UX)**: STORY-017 (GUI sidebar refactor -- user-facing improvement)
- **P3 (code health)**: STORY-018 (isinstance replacements), STORY-019 (conftest consolidation), STORY-020 (dispatch refactor), STORY-024 (config model consolidation)

### File-Conflict Dependencies

| Story | Logical Dep | Shared File | Reason |
| --- | --- | --- | --- |
| STORY-021 | none | `cc_engine.py`, `run_cli.py`, `run_app.py` | Bug fix, touches run_app.py (coordinate with STORY-017) |
| STORY-022 | STORY-021 | `cc_engine.py`, `config_app.py` | Stream persistence depends on query fix; shares cc_engine.py with STORY-021 |
| STORY-023 | none | `run_app.py` | Trivial fix, coordinate with STORY-017 and STORY-021 (all touch run_app.py) |
| STORY-017 | STORY-021 | `run_gui.py`, `run_app.py` | GUI refactor should apply after run_app.py query fix |
| STORY-018 | none | various test files | Test-only changes, no src/ conflicts |
| STORY-019 | STORY-018 | test files in same subdirectories | Conftest extraction should happen after isinstance cleanup to avoid moving fixtures that get rewritten |
| STORY-020 | none | `datasets_peerread.py` | Standalone src/ refactor |
| STORY-024 | none | `load_configs.py`, `peerread_models.py`, `config/__init__.py` | Standalone config consolidation, no src/ conflicts with other stories |
| STORY-025 | none | `agent_system.py` | Standalone fix, no file conflicts with other stories |
| STORY-026 | none | `agent_system.py` | Shares file with STORY-025 but different functions; coordinate in same wave |

### Orchestration Waves

```text
Wave 0 (bug fixes, fast):
  teammate-1: STORY-021 (F6 CC engine empty query fix)
  teammate-2: STORY-023 (F8 App page query persistence -- trivial, 2 lines) then STORY-025 (F10 search tool resilience) then STORY-026 (F11 result validation fix -- same file as STORY-025)

Wave 1 (independent, no file conflicts -- after Wave 0):
  teammate-1: STORY-016 (F1 artifact summary) then STORY-022 (F7 CC stream persistence, depends: STORY-021)
  teammate-2: STORY-017 (F2 GUI sidebar refactor, depends: STORY-021 for run_app.py)

Wave 2 (after Wave 1):
  teammate-1: STORY-018 (F3 isinstance replacements) then STORY-019 (F4 conftest, depends: STORY-018)
  teammate-2: STORY-020 (F5 dispatch refactor) then STORY-024 (F9 config model consolidation)
```

- **Quality Gates**: Teammate runs `make quick_validate`; lead runs `make validate` after each wave

### Story Breakdown (11 stories total)

- **Feature 6** -> STORY-021: CC engine empty query fix
  Add `build_cc_query()` in `cc_engine.py`. Wire into CLI (`run_cli.py`) and GUI (`run_app.py:_prepare_cc_result`). Files: `src/app/engines/cc_engine.py`, `src/run_cli.py`, `src/gui/pages/run_app.py`, `tests/engines/test_cc_engine_query.py` (new).

- **Feature 7** -> STORY-022: Persist CC JSONL stream to disk (depends: STORY-021)
  Tee raw JSONL stream to `{LOGS_BASE_PATH}/cc_streams/` during CC execution. Solo writes JSON, teams writes JSONL incrementally. Files: `src/app/config/config_app.py`, `src/app/engines/cc_engine.py`, `tests/engines/test_cc_stream_persistence.py` (new).

- **Feature 8** -> STORY-023: App page free-form query persistence fix
  Add `key` parameter to two `text_input` calls in `run_app.py`. Files: `src/gui/pages/run_app.py`.

- **Feature 1** -> STORY-016: End-of-run artifact path summary
  New `ArtifactRegistry` singleton. Register paths in 7 components. Print summary in CLI and sweep. Files: `src/app/utils/artifact_registry.py` (new), `src/app/utils/log.py`, `src/app/judge/trace_processors.py`, `src/app/data_utils/review_persistence.py`, `src/app/tools/peerread_tools.py`, `src/app/reports/report_generator.py`, `src/app/benchmark/sweep_runner.py`, `src/run_cli.py`, `tests/utils/test_artifact_registry.py` (new).

- **Feature 2** -> STORY-017: GUI layout refactor -- sidebar tabs
  Add sidebar navigation to `run_gui.py`. Separate Run and Settings into distinct tabs. Remove `run_gui.py:43` TODO. Files: `src/run_gui.py`, `src/gui/pages/run_app.py`, `tests/gui/test_sidebar_navigation.py` (new).

- **Feature 3** -> STORY-018: Replace `assert isinstance` tests with behavioral assertions
  ~30 occurrences across 12 test files. Replace type checks with field/method assertions. Files: `tests/agents/test_agent_system.py`, `tests/judge/test_evaluation_pipeline.py`, `tests/judge/test_composite_scorer.py`, `tests/data_models/test_evaluation_models.py`, `tests/data_models/test_app_models.py`, `tests/reports/test_report_generator.py`, `tests/reports/test_suggestion_engine.py`, + others.

- **Feature 4** -> STORY-019: Test organization -- subdirectory conftest.py files (depends: STORY-018)
  Add `conftest.py` to `tests/agents/`, `tests/judge/`, `tests/tools/`, `tests/evals/`. Deduplicate shared fixtures.

- **Feature 5** -> STORY-020: Data layer -- dispatch chain registry refactor
  Replace 4 dispatch chains in `datasets_peerread.py` with `DATA_TYPE_SPECS` registry. Target -8 CC points. Files: `src/app/data_utils/datasets_peerread.py`, `tests/data_utils/test_datasets_peerread.py`.

- **Feature 9** -> STORY-024: Move remaining config models to `src/app/config/`
  Move `LogfireConfig` from `utils/load_configs.py` and `PeerReadConfig` from `data_models/peerread_models.py` into `config/`. Update imports in 5 src files + 5 test files. Files: `src/app/config/logfire_config.py` (new), `src/app/config/peerread_config.py` (new), `src/app/utils/load_configs.py`, `src/app/data_models/peerread_models.py`, `src/app/config/__init__.py`, `src/app/data_utils/datasets_peerread.py`, + 5 test files.

- **Feature 10** -> STORY-025: Search tool HTTP error resilience
  Wrap `duckduckgo_search_tool()` with error-catching wrapper that returns descriptive string on HTTP 403/429 instead of crashing the app. Add `tavily_search_tool()` as secondary search tool (requires `TAVILY_API_KEY`). No dedicated test file — trivial wrapper, manual validation. Files: `src/app/agents/agent_system.py`.

- **Feature 11** -> STORY-026: Sub-agent result validation JSON parsing fix
  Fix `_validate_model_return()` to try `model_validate_json()` for string inputs instead of `model_validate(str(...))`. Remove `str()` wrapping at 3 call sites. Fixes Cerebras/Groq providers returning string instead of structured output. Files: `src/app/agents/agent_system.py`, `tests/agents/test_agent_system.py`.
