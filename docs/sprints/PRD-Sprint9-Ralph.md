---
title: Product Requirements Document - Agents-eval Sprint 9
description: "Sprint 9: 13 features — CC engine GUI wiring, PydanticAI API migration, AgentConfig typing, GUI layout refactor, dead code deletion, format string sanitization, PDF size guard, API key env cleanup, security hardening, judge accuracy, data layer robustness, dispatch chain refactor, type safety + quick fixes."
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

### Feature 2: PydanticAI API Migration — `manager.run()`, `RunContext`, and Private Attribute Access

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
- Verify `RunContext` deprecation status: `python -c "from pydantic_ai import RunContext; print(RunContext)"`. If deprecated, update all tool function signatures in `agent_system.py` and `peerread_tools.py` (note: `orchestration.py` is deleted by Feature 5)
- Replace `getattr(manager, "model")._model_name` with `getattr(manager, "model").model_name` (public attribute) with fallback to `"unknown"`
- Preserve `trace_collector` start/end calls and error handling structure
- Mock PydanticAI agent in tests — never call real LLM providers

**Files**:

- `src/app/agents/agent_system.py` (edit — lines 537-551, migrate `manager.run()`, fix `_model_name`, check `RunContext`)
- `src/app/tools/peerread_tools.py` (edit — update `RunContext` import if deprecated)
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

### Feature 5: Delete `orchestration.py` Dead Code Module

**Dependency**: Execute before Features 2 and 13 — both reference files/patterns that this deletion eliminates.

**Description**: `src/app/agents/orchestration.py` (~317 lines) defines `EvaluationOrchestrator`, `PeerReviewOrchestrator`, `DelegationOrchestrator`, and workflow functions — none of which are imported or used anywhere in the codebase. Stub methods simulate work with `asyncio.sleep()`. The `_validate_model_return` function silently returns a default-constructed model on validation failure, masking errors. Flagged independently by both security and integration reviewers (Review F5). YAGNI per AGENTS.md.

**Acceptance Criteria**:

- [ ] AC1: `src/app/agents/orchestration.py` deleted
- [ ] AC2: No imports of `orchestration` remain in `src/` or `tests/`
- [ ] AC3: `make validate` passes — no import errors, no test failures
- [ ] AC4: Any tests that imported `orchestration.py` are deleted or updated

**Technical Requirements**:

- Grep for `orchestration` imports across `src/` and `tests/` before deletion
- Delete the module and any orphaned test files
- Verify no runtime references via `make test`

**Files**:

- `src/app/agents/orchestration.py` (delete)
- `tests/agents/test_orchestration.py` (delete if exists)

---

### Feature 6: Sanitize `paper_full_content` in Review Template Format Call

**Description**: In `_load_and_format_template()` (`peerread_tools.py:359`), `paper_title` and `paper_abstract` are sanitized via `sanitize_paper_title()` / `sanitize_paper_abstract()`, but `paper_full_content` (raw PDF body, potentially megabytes of adversary-controlled text) is passed to `.format()` without sanitization. Malicious PDF content containing Python `str.format()` placeholders like `{tone}`, `{review_focus}`, or `{0.__class__}` could execute format string injection (Review F3, MAESTRO L1).

**Acceptance Criteria**:

- [ ] AC1: `paper_full_content` is sanitized before being passed to `.format()` — curly braces escaped or `sanitize_for_prompt()` applied
- [ ] AC2: Existing review generation produces identical output for benign inputs
- [ ] AC3: A test verifies that `{malicious_placeholder}` in paper content is neutralized
- [ ] AC4: `make validate` passes with no regressions

**Technical Requirements**:

- Apply `sanitize_for_prompt()` to `truncated_content` before `.format()`, OR escape `{` → `{{` and `}` → `}}` in paper_full_content, OR migrate the entire template to `string.Template.safe_substitute()`
- Add security test covering format string injection via paper content

**Files**:

- `src/app/tools/peerread_tools.py` (edit — sanitize `paper_full_content` in `_load_and_format_template`)
- `tests/security/test_prompt_injection.py` (edit — add format string injection test for paper content)

---

### Feature 7: Add PDF File Size Guard Before MarkItDown Extraction

**Description**: `peerread_tools.py:68-72` calls `MarkItDown().convert(pdf_file)` without checking file size. Content truncation exists after extraction (via `_truncate_paper_content`), but the extraction itself is unbounded. A malicious or corrupt PDF could exhaust memory. This finding has been unresolved since Sprint 5 (Sprint 5 Finding 18, Review F7, MAESTRO L5).

**Acceptance Criteria**:

- [ ] AC1: PDF file size is checked before calling `MarkItDown().convert()`
- [ ] AC2: Files exceeding the configured maximum (default 50MB) raise `ValueError` with a descriptive message
- [ ] AC3: The size limit is configurable (constant or parameter), not hardcoded inline
- [ ] AC4: A test verifies that oversized PDFs are rejected before extraction
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- Add `pdf_file.stat().st_size` check before `md_converter.convert(pdf_file)`
- Define `MAX_PDF_SIZE_BYTES` constant (default 50 * 1024 * 1024)
- Raise `ValueError` with file size and limit in the message

**Files**:

- `src/app/tools/peerread_tools.py` (edit — add size guard before `MarkItDown().convert()`)
- `tests/tools/test_peerread_tools.py` (edit — add test for oversized PDF rejection)

---

### Feature 8: Remove API Keys from `os.environ` — Pass via Provider Constructors

**Description**: `setup_llm_environment()` in `providers.py:66-80` writes API keys to `os.environ`, exposing them to child processes, crash reporters, and debug dumps. This has been the only HIGH-severity finding deferred across two consecutive review cycles (Sprint 5 Finding 10, Review F1). Most providers already accept keys via constructor in `models.py` — the `os.environ` path is redundant for all except Google/Gemini which relies on environment variable lookup.

**Acceptance Criteria**:

- [ ] AC1: `setup_llm_environment()` no longer writes API keys to `os.environ`
- [ ] AC2: All LLM providers (OpenAI, Anthropic, Google, OpenRouter, Cerebras, GitHub, Ollama) still authenticate successfully
- [ ] AC3: The `setup_llm_environment()` call in `agent_system.py:675` is removed or replaced with direct constructor injection
- [ ] AC4: For Google/Gemini: API key is passed via constructor parameter or set in a scoped context (not left in `os.environ` permanently)
- [ ] AC5: No API keys appear in `os.environ` after agent setup (verifiable via test)
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- Audit `src/app/llms/models.py` to confirm which providers already accept keys via constructor (most do — `OpenAIChatModel`, `AnthropicModel`, etc.)
- For Google/Gemini: check if `GoogleModel` accepts an `api_key` constructor parameter. If not, set env var before construction and unset immediately after
- Remove `setup_llm_environment` import and call from `agent_system.py:63,675`
- Delete or deprecate `setup_llm_environment()` in `providers.py`
- Mock provider constructors in tests — never call real LLM APIs

**Files**:

- `src/app/llms/providers.py` (edit — remove or deprecate `setup_llm_environment`)
- `src/app/agents/agent_system.py` (edit — remove call at line 675, pass keys via constructors)
- `src/app/llms/models.py` (edit — ensure all providers receive keys via constructor)
- `tests/agents/test_agent_system.py` (edit — verify no `os.environ` key leakage)
- `tests/llms/test_providers.py` (edit — test provider key injection without env vars)

---

### Feature 9: Security Hardening — SSRF Documentation, Phoenix Validation, Tool Registration Guard

**Description**: Three LOW-effort security findings from the review bundled together: (1) DuckDuckGo search tool bypasses the SSRF allowlist — needs explicit documentation (Review F4), (2) Phoenix endpoint is configurable via env var but not validated before `requests.head()` probe (Review F14), (3) No idempotency guard on PeerRead tool registration — calling twice crashes (Review F16).

**Acceptance Criteria**:

- [ ] AC1: Code comment in `agent_system.py` at `duckduckgo_search_tool()` usage documents that this tool bypasses `validate_url()` SSRF protection (Review F4)
- [ ] AC2: Phoenix endpoint (`JUDGE_PHOENIX_ENDPOINT`) validated at configuration time — must be `localhost` or explicitly trusted host (Review F14)
- [ ] AC3: `add_peerread_tools_to_agent()` is idempotent — calling twice on the same agent does not crash (Review F16)
- [ ] AC4: `make validate` passes with no regressions

**Technical Requirements**:

- F4: Add inline comment at `agent_system.py:402` documenting the SSRF bypass
- F14: Add URL format check in `logfire_instrumentation.py` before `requests.head()` — validate against allowed prefixes (`http://localhost`, `https://`)
- F16: Check `agent._function_toolset.tools` for existing tool names before registration, or catch `UserError` and skip

**Files**:

- `src/app/agents/agent_system.py` (edit — SSRF comment at line 402, tool registration guard at lines 423-431)
- `src/app/agents/logfire_instrumentation.py` (edit — validate phoenix endpoint at line 81)
- `src/app/tools/peerread_tools.py` (edit — idempotency guard in `add_peerread_tools_to_agent`)
- `tests/security/test_tool_registration.py` (edit — test idempotent registration)

---

### Feature 10: Judge Pipeline Accuracy — Clarity Field, Silent Stub, Sentiment Heuristic

**Description**: Three judge pipeline findings bundled together: (1) `clarity` field in `Tier2Result` always receives the `constructiveness` score, never independently assessed (Review F8), (2) `_extract_planning_decisions` silently returns a stub string on any exception with no logging (Review F18), (3) Recommendation matching uses naive `"good" in text` heuristic that misclassifies negations (Review F19).

**Acceptance Criteria**:

- [ ] AC1: `Tier2Result.clarity` either has a dedicated `assess_clarity` method or the field is removed from the model (Review F8)
- [ ] AC2: `_extract_planning_decisions` logs errors at debug level and narrows exception types to `(AttributeError, KeyError, TypeError)` (Review F18)
- [ ] AC3: Recommendation matching uses the structured `GeneratedReview.recommendation` integer score instead of text sentiment, or is explicitly documented as an approximation (Review F19)
- [ ] AC4: `make validate` passes with no regressions

**Technical Requirements**:

- F8: Design decision needed — either implement `assess_clarity` mirroring `assess_constructiveness`, or remove `clarity` from `Tier2Result` and all callers. Removing is lower effort and more honest.
- F18: Add `logger.debug(f"_extract_planning_decisions failed: {e}", exc_info=True)` and narrow `except Exception` to `except (AttributeError, KeyError, TypeError)`
- F19: Replace `"good" in agent_review.lower()` with `review_result.recommendation` score comparison if `ReviewGenerationResult` is available in the call context

**Files**:

- `src/app/judge/llm_evaluation_managers.py` (edit — lines 428-429, 456-457, 529)
- `src/app/data_models/evaluation_models.py` (edit — remove `clarity` field from `Tier2Result` if chosen)
- `src/app/judge/traditional_metrics.py` (edit — lines 582-591, fix sentiment heuristic)
- `tests/judge/test_llm_evaluation_managers.py` (edit — tests for clarity and stub return)
- `tests/judge/test_traditional_metrics.py` (edit — test recommendation matching)

---

### Feature 11: Data Layer Robustness — Narrow Exceptions + Contradictory Log

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

### Feature 12: Dispatch Chain Registry Refactor in `datasets_peerread.py`

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

### Feature 13: Type Safety + Quick Fixes

**Description**: Seven LOW-effort fixes bundled together: two FIXABLE type suppressions from the type audit plus five one-liner fixes from the review. (1) `sweep_runner.py:104` type suppression via TypedDict return (Review F11), (2) `cc_engine.py:78` type suppression via cast (Review type audit), (3) `load_config()` returns `BaseModel` instead of generic `T` (Review F12), (4) `model_info` hardcoded as `"GPT-4o via PydanticAI"` (Review F15), (5) Artificial `time.sleep(0.001)` inflates timing data (Review F21), (6) `ZeroDivisionError` on empty `metric_deltas` (Review F22), (7) Missing `.get()` default for `repetitions` (Review F24).

**Acceptance Criteria**:

- [ ] AC1: `sweep_runner.py:104` — `# type: ignore[return-value]` removed by typing `_prepare_result_dict` return as `TypedDict` with `composite_result: CompositeResult | None` (Review F11)
- [ ] AC2: `cc_engine.py:78` — `# type: ignore[no-any-return]` removed by adding `cast(dict[str, Any] | None, ...)` around `json.loads()` (Review type audit)
- [ ] AC3: `load_config()` is generic — returns `T` where `T: BaseModel`, eliminating cast and `# type: ignore` at `app.py:90` (Review F12)
- [ ] AC4: `model_info` in `ReviewGenerationResult` derived from actual model name, not hardcoded string (Review F15)
- [ ] AC5: `time.sleep(0.001)` removed from `evaluate_single_traditional` (Review F21)
- [ ] AC6: `baseline_comparison.compare()` handles empty `metric_deltas` without `ZeroDivisionError` (Review F22)
- [ ] AC7: `run_sweep.py` uses `config_data.get("repetitions", 3)` or validates via `SweepConfig.model_validate()` (Review F24)
- [ ] AC8: `make validate` passes — pyright clean on all changed files with no new suppressions

**Technical Requirements**:

- F11: Type `_prepare_result_dict` return as a `TypedDict` with `composite_result: CompositeResult | None` (preferred), or add explicit `cast()` at `sweep_runner.py:104`
- Type audit: Add `cast(dict[str, Any] | None, json.loads(stripped))` at `cc_engine.py:78`, or assign to a typed variable
- F12: Change `def load_config(config_path, data_model: type[BaseModel]) -> BaseModel` to `def load_config[T: BaseModel](config_path, data_model: type[T]) -> T` in `load_configs.py:29`
- F15: Pass actual model name through tool context or agent attribute to `ReviewGenerationResult` construction at `peerread_tools.py:507`
- F21: Remove `time.sleep(0.001)` at `traditional_metrics.py:488-490` — `measure_execution_time` already clamps minimum
- F22: Add `if not metric_deltas: return BaselineComparisonSummary(...)` guard at `baseline_comparison.py:87`
- F24: Replace `config_data["repetitions"]` with `config_data.get("repetitions", 3)` at `run_sweep.py:118`

**Files**:

- `src/app/benchmark/sweep_runner.py` (edit — line 104, remove type suppression)
- `src/app/engines/cc_engine.py` (edit — line 78, remove type suppression)
- `src/app/app.py` (edit — type `_prepare_result_dict` return, remove cast at line 90)
- `src/app/utils/load_configs.py` (edit — make `load_config` generic)
- `src/app/tools/peerread_tools.py` (edit — derive `model_info` from actual model at line 507)
- `src/app/judge/traditional_metrics.py` (edit — remove `time.sleep` at line 488)
- `src/app/judge/baseline_comparison.py` (edit — guard empty dict at line 87)
- `src/run_sweep.py` (edit — `.get()` default at line 118)
- `tests/judge/test_traditional_metrics.py` (edit — verify no artificial sleep)
- `tests/judge/test_baseline_comparison.py` (edit — test empty metric_deltas)

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
- ~~Unify API Key Resolution Across Agent and Judge Paths~~ — **Promoted to Feature 8** (Review F1, HIGH — deferred for 2 sprints)
- ~~CC engine SDK migration~~ — **Removed.** Keeping `subprocess.run([claude, "-p"])` per ADR-008.

**All src-parallel-review-2026-02-21 findings promoted to Sprint 9 features.** Review F11 (unsafe dict access in `sweep_runner.py`) is addressed by Feature 13's TypedDict approach.

**Already completed (Sprint 8, all 14 stories delivered):**

- Feature 1: `read_paper_pdf_tool` → `get_paper_content` with parsed JSON fallback chain
- Feature 2: `"not-required"` sentinel removal + judge auto-mode model inheritance
- Feature 3: CC engine consolidation (`cc_engine.py`) with solo + teams support
- Feature 4: Graph node attribute alignment (`node_type` → `type`)
- Feature 5: Dead `pydantic_ai_stream` parameter removal
- Feature 6: Report generation (CLI `--generate-report`, GUI button, suggestion engine)
- Feature 7: Judge settings free-text → populated dropdowns
- Feature 8: GUI a11y/UX fixes (WCAG, environment URL, run ID, baseline validation)
