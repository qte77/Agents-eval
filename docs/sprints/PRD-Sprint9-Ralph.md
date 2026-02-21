---
title: Product Requirements Document - Agents-eval Sprint 9
description: "Sprint 9: 9 features — dead code deletion, format string sanitization, PDF size guard, API key env cleanup, security hardening, judge accuracy, AgentConfig typing, type safety + quick fixes, test suite quality sweep."
version: 1.4.0
created: 2026-02-19
updated: 2026-02-21
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 7 delivered: documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

Sprint 8 features (8 features, 14 stories) have been fully implemented: tool bug fix (`get_paper_content`), API key/model cleanup, CC engine consolidation with teams support, graph attribute alignment, dead code removal (`pydantic_ai_stream`), report generation (CLI + GUI + suggestion engine), judge settings dropdowns, and GUI a11y/UX fixes.

**Sprint 9/10 split**: Sprint 9 focuses on correctness, security, and quick wins (9 features). Feature work (CC engine GUI wiring, PydanticAI API migration, GUI layout refactor) and refactoring (data layer, dispatch chain) deferred to Sprint 10. Original Features 1, 2, 4, 11, 12 moved to Sprint 10.

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

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->
<!-- PARSER REQUIREMENT: No compound sub-features — one heading per story -->
<!-- PARSER REQUIREMENT: Flatten AC items — no indented sub-items under a checkbox -->
<!-- PARSER REQUIREMENT: Each sub-feature MUST have its own **Files**: section -->

#### Feature 1: Delete `orchestration.py` Dead Code Module

**Dependency**: P0 blocker — execute first. Unblocks Features 2, 4, 5, 6, 8 in Sprint 9 and Feature 2 in Sprint 10.

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

#### Feature 2: Sanitize `paper_full_content` in Review Template Format Call

**Dependency**: Depends on Feature 1 (shared file: `peerread_tools.py` via Feature 5 chain).

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

#### Feature 3: Add PDF File Size Guard Before MarkItDown Extraction

**Dependency**: Depends on Feature 2 (shared file: `peerread_tools.py`).

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

#### Feature 4: Remove API Keys from `os.environ` — Pass via Provider Constructors

**Dependency**: Depends on Feature 1 (shared file: `agent_system.py`).

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

#### Feature 5: Security Hardening — SSRF Documentation, Phoenix Validation, Tool Registration Guard

**Dependency**: Depends on Feature 3 (shared file: `peerread_tools.py`) and Feature 4 (shared file: `agent_system.py`).

**Description**: Three LOW-effort security findings from the review bundled together: (1) DuckDuckGo search tool bypasses the SSRF allowlist — needs explicit documentation (Review F4), (2) Phoenix endpoint is configurable via env var but not validated before `requests.head()` probe (Review F14), (3) No idempotency guard on PeerRead tool registration — calling twice crashes (Review F16).

**Acceptance Criteria**:
- [ ] AC1: Code comment in `agent_system.py` at `duckduckgo_search_tool()` usage documents that this tool bypasses `validate_url()` SSRF protection (Review F4)
- [ ] AC2: Phoenix endpoint (`JUDGE_PHOENIX_ENDPOINT`) validated at configuration time — must be `localhost` or explicitly trusted host (Review F14)
- [ ] AC3: `add_peerread_tools_to_agent()` is idempotent — calling twice on the same agent does not crash (Review F16)
- [ ] AC4: `make validate` passes with no regressions
- [ ] AC5: `TestAgentRoleBasedToolAssignment` tests use `Agent(TestModel())` — bare `try/except ValueError` pattern removed (tests-review C2)

**Technical Requirements**:
- F4: Add inline comment at `agent_system.py:402` documenting the SSRF bypass
- F14: Add URL format check in `logfire_instrumentation.py` before `requests.head()` — validate against allowed prefixes (`http://localhost`, `https://`)
- F16: Check `agent._function_toolset.tools` for existing tool names before registration, or catch `UserError` and skip
- C2: Replace `try/except ValueError` in `TestAgentRoleBasedToolAssignment` (3 tests at lines 26-57) with `Agent(TestModel())` pattern

**Files**:
- `src/app/agents/agent_system.py` (edit — SSRF comment at line 402, tool registration guard at lines 423-431)
- `src/app/agents/logfire_instrumentation.py` (edit — validate phoenix endpoint at line 81)
- `src/app/tools/peerread_tools.py` (edit — idempotency guard in `add_peerread_tools_to_agent`)
- `tests/security/test_tool_registration.py` (edit — test idempotent registration, fix C2 false-pass)

---

#### Feature 6: Judge Pipeline Accuracy — Clarity Field, Silent Stub, Sentiment Heuristic, Cosine Clamp

**Dependency**: Depends on Feature 1.

**Description**: Four judge pipeline findings bundled together: (1) `clarity` field in `Tier2Result` always receives the `constructiveness` score, never independently assessed (Review F8), (2) `_extract_planning_decisions` silently returns a stub string on any exception with no logging (Review F18), (3) Recommendation matching uses naive `"good" in text` heuristic that misclassifies negations (Review F19), (4) Cosine score can exceed 1.0 due to floating-point precision, causing Pydantic validation errors (tests-review C1).

**Acceptance Criteria**:
- [ ] AC1: `Tier2Result.clarity` either has a dedicated `assess_clarity` method or the field is removed from the model (Review F8)
- [ ] AC2: `_extract_planning_decisions` logs errors at debug level and narrows exception types to `(AttributeError, KeyError, TypeError)` (Review F18)
- [ ] AC3: Recommendation matching uses the structured `GeneratedReview.recommendation` integer score instead of text sentiment, or is explicitly documented as an approximation (Review F19)
- [ ] AC4: `make validate` passes with no regressions
- [ ] AC5: Cosine score clamped to `min(1.0, score)` before `Tier1Result` construction — un-skip `test_tier1_result_scores_always_valid` property test (tests-review C1)

**Technical Requirements**:
- F8: Design decision needed — either implement `assess_clarity` mirroring `assess_constructiveness`, or remove `clarity` from `Tier2Result` and all callers. Removing is lower effort and more honest.
- F18: Add `logger.debug(f"_extract_planning_decisions failed: {e}", exc_info=True)` and narrow `except Exception` to `except (AttributeError, KeyError, TypeError)`
- F19: Replace `"good" in agent_review.lower()` with `review_result.recommendation` score comparison if `ReviewGenerationResult` is available in the call context
- C1: Clamp `cosine_score = min(1.0, cosine_score)` in `traditional_metrics.py`. Un-skip `@pytest.mark.skip` property test at `test_traditional_metrics.py:706`

**Files**:
- `src/app/judge/llm_evaluation_managers.py` (edit — lines 428-429, 456-457, 529)
- `src/app/data_models/evaluation_models.py` (edit — remove `clarity` field from `Tier2Result` if chosen)
- `src/app/judge/traditional_metrics.py` (edit — lines 582-591 fix sentiment heuristic, clamp cosine score)
- `tests/judge/test_llm_evaluation_managers.py` (edit — tests for clarity and stub return)
- `tests/judge/test_traditional_metrics.py` (edit — test recommendation matching, un-skip property test)

---

#### Feature 7: Add Proper Type Annotation to `AgentConfig.tools` Field

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

#### Feature 8: Type Safety + Quick Fixes

**Dependency**: Depends on Feature 1 and Feature 6 (shared file: `traditional_metrics.py`).

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

#### Feature 9: Test Suite Quality Sweep

**Description**: Bundled HIGH-priority test quality findings from the tests parallel review (`docs/reviews/tests-parallel-review-2026-02-21.md`). Addresses unspec'd mocks, missing asyncio markers, incorrect thread-safety test, duplicate test files, dead test code, and `sys.path.insert` hacks across the test suite.

**Acceptance Criteria**:
- [ ] AC1: All `MagicMock()`/`Mock()` in `tests/` use `spec=ClassName` — covers `tests/agents/test_rate_limit_handling.py`, `tests/agents/test_trace_collection_integration.py`, `tests/judge/test_evaluation_runner.py`, `tests/judge/test_llm_evaluation_managers.py`, `tests/judge/test_graph_analysis.py`, `tests/evals/test_evaluation_pipeline.py`, `tests/app/test_cli_baseline.py`, `tests/app/test_app.py`, `tests/app/test_cli_token_limit.py`, `tests/gui/test_story013_ux_fixes.py`, `tests/gui/test_story007_gui_polish.py`, `tests/benchmark/test_sweep_runner.py`, `tests/agents/test_logfire_instrumentation.py`, `tests/judge/test_trace_skip_warning.py`, `tests/evals/test_metric_comparison_logging.py` (tests-review H1-H3, H13, M11)
- [ ] AC2: Async tests in `test_judge_agent.py` have `@pytest.mark.asyncio` + mock LLM calls (tests-review H10)
- [ ] AC3: Thread-safety test in `test_trace_store.py` uses `threading.Lock` around counter increments + final assertions on counter values (tests-review H9)
- [ ] AC4: Shared async fixture extracted in `test_metric_comparison_logging.py` — four tests share setup, each contains only its unique assertion (tests-review H11)
- [ ] AC5: `test_agent_factories_coverage.py` merged into `test_agent_factories.py`, coverage file deleted (tests-review H12)
- [ ] AC6: Empty `TestCompositeScorer` class deleted from `test_composite_scorer.py` (tests-review M9)
- [ ] AC7: `sys.path.insert` removed from `tests/integration/test_peerread_integration.py`, `tests/integration/test_enhanced_peerread_integration.py`, `tests/integration/test_peerread_real_dataset_validation.py`, `tests/benchmarks/test_performance_baselines.py` (tests-review M13)
- [ ] AC8: Stub test with `pass` body deleted from `test_peerread_tools.py:312` (tests-review H7)
- [ ] AC9: `test_datasets_peerread_coverage.py` merged into `test_datasets_peerread.py`, coverage file deleted (tests-review L6)
- [ ] AC10: `make validate` passes

**Technical Requirements**:
- AC1: Grep for `MagicMock()` and `Mock()` without `spec=` across all listed files. Add `spec=ClassName` for each mock target (e.g., `spec=Agent`, `spec=TraceCollector`, `spec=AgentRunResult`, `spec=EvaluationPipeline`, `spec=requests.models.Response`). Use `spec_set=` where stricter enforcement is appropriate.
- AC2: Add `@pytest.mark.asyncio` to all `async def test_*` methods in `test_judge_agent.py`. Add proper mocking for `JudgeAgent.evaluate_comprehensive` to prevent real LLM calls.
- AC3: Add `threading.Lock` in `test_trace_store.py` around `write_count[0] += 1` increments. Add `assert write_count[0] == expected_writes` at end of test.
- AC4: Extract `@pytest_asyncio.fixture` in `test_metric_comparison_logging.py` with shared mock setup (~40 lines). Each test function receives the fixture and asserts only its unique condition.
- AC5: Move unique tests from `test_agent_factories_coverage.py` into `test_agent_factories.py`. Delete `tests/agents/test_agent_factories_coverage.py`.
- AC6: Delete the empty `class TestCompositeScorer:` at `test_composite_scorer.py:75-76`.
- AC7: Remove `sys.path.insert(0, ...)` from all 4 files. Root `conftest.py` already handles path setup.
- AC8: Delete the stub `test_generate_review_template_with_truncation` at `test_peerread_tools.py:312-316`.
- AC9: Move unique tests from `test_datasets_peerread_coverage.py` into `test_datasets_peerread.py`. Delete `tests/data_utils/test_datasets_peerread_coverage.py`.

**Files**:
- `tests/agents/test_rate_limit_handling.py` (edit — add spec= to mocks)
- `tests/agents/test_trace_collection_integration.py` (edit — add spec= to mocks)
- `tests/agents/test_logfire_instrumentation.py` (edit — add spec= to mocks)
- `tests/agents/test_peerread_tools.py` (edit — delete stub test at line 312)
- `tests/agents/test_agent_factories.py` (edit — merge content from coverage file)
- `tests/agents/test_agent_factories_coverage.py` (delete)
- `tests/judge/test_evaluation_runner.py` (edit — add spec= to mocks)
- `tests/judge/test_llm_evaluation_managers.py` (edit — add spec= to mocks)
- `tests/judge/test_graph_analysis.py` (edit — add spec= to mocks)
- `tests/judge/test_judge_agent.py` (edit — add asyncio markers + mock LLM)
- `tests/judge/test_trace_store.py` (edit — fix thread-safety test)
- `tests/judge/test_trace_skip_warning.py` (edit — add spec= to logger mock)
- `tests/evals/test_evaluation_pipeline.py` (edit — add spec= to mocks)
- `tests/evals/test_metric_comparison_logging.py` (edit — extract shared fixture, add spec=)
- `tests/evals/test_composite_scorer.py` (edit — delete empty class)
- `tests/app/test_cli_baseline.py` (edit — add spec= to mocks)
- `tests/app/test_app.py` (edit — add spec= to mocks)
- `tests/app/test_cli_token_limit.py` (edit — add spec= to mocks)
- `tests/gui/test_story013_ux_fixes.py` (edit — add spec= to mocks)
- `tests/gui/test_story007_gui_polish.py` (edit — add spec= to mocks)
- `tests/benchmark/test_sweep_runner.py` (edit — add spec= to mocks)
- `tests/integration/test_peerread_integration.py` (edit — remove sys.path.insert)
- `tests/integration/test_enhanced_peerread_integration.py` (edit — remove sys.path.insert)
- `tests/integration/test_peerread_real_dataset_validation.py` (edit — remove sys.path.insert)
- `tests/benchmarks/test_performance_baselines.py` (edit — remove sys.path.insert)
- `tests/data_utils/test_datasets_peerread.py` (edit — merge content from coverage file)
- `tests/data_utils/test_datasets_peerread_coverage.py` (delete)

---

## Non-Functional Requirements

- Report generation latency target: < 5s for rule-based suggestions, < 30s for LLM-assisted
- No new external dependencies without PRD validation
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S9-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).
- Sprint 9 focuses on correctness, security, and quick wins. Feature work (GUI, API migration) deferred to Sprint 10.

---

## Out of Scope

**Deferred to Sprint 10 (see [PRD-Sprint10-Ralph.md](PRD-Sprint10-Ralph.md)):**

- Feature 1: Wire CC Engine to GUI Execution Path
- Feature 2: PydanticAI API Migration
- Feature 3: GUI Layout Refactor — Sidebar Tabs
- Feature 4: Data Layer Robustness — Narrow Exceptions
- Feature 5: Dispatch Chain Registry Refactor
- Feature 6: Replace `inspect.getsource` Tests with Behavioral Tests

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
- ~~Unify API Key Resolution Across Agent and Judge Paths~~ — **Promoted to Feature 4** (Review F1, HIGH — deferred for 2 sprints)
- ~~CC engine SDK migration~~ — **Removed.** Keeping `subprocess.run([claude, "-p"])` per ADR-008.

**Deferred test review findings (MEDIUM/LOW from tests-parallel-review-2026-02-21.md):**

- `assert isinstance()` replacements with behavioral assertions (H4, M1-M3) — ~30+ occurrences across 12 files
- Subdirectory `conftest.py` creation for `tests/agents/`, `tests/tools/`, `tests/evals/`, `tests/judge/` (M5, M6)
- `@pytest.mark.parametrize` additions for provider tests and recommendation tests (M7, M8)
- `hasattr()` replacements with behavioral tests (M4)
- Weak assertion strengthening in `test_suggestion_engine.py` and `test_report_generator.py` (M18, L5)
- Hardcoded relative path fix in `test_peerread_tools_error_handling.py` (H8)
- `tempfile` → `tmp_path` in integration tests (L7, L8)
- `@pytest.mark.slow` markers on performance baselines (L10)

**All src-parallel-review-2026-02-21 findings promoted to Sprint 9 features.** Review F11 (unsafe dict access in `sweep_runner.py`) is addressed by Feature 8's TypedDict approach.

**Already completed (Sprint 8, all 14 stories delivered):**

- Feature 1: `read_paper_pdf_tool` → `get_paper_content` with parsed JSON fallback chain
- Feature 2: `"not-required"` sentinel removal + judge auto-mode model inheritance
- Feature 3: CC engine consolidation (`cc_engine.py`) with solo + teams support
- Feature 4: Graph node attribute alignment (`node_type` → `type`)
- Feature 5: Dead `pydantic_ai_stream` parameter removal
- Feature 6: Report generation (CLI `--generate-report`, GUI button, suggestion engine)
- Feature 7: Judge settings free-text → populated dropdowns
- Feature 8: GUI a11y/UX fixes (WCAG, environment URL, run ID, baseline validation)

---

## Notes for Ralph Loop

### Priority Order

- **P0 (blocker)**: STORY-001 (delete dead code — unblocks F2-F6, F8)
- **P1 (security)**: STORY-002, STORY-003, STORY-004, STORY-005
- **P2 (correctness)**: STORY-006, STORY-008
- **P3 (quick wins)**: STORY-007
- **P4 (test quality)**: STORY-009

### Notes for CC Agent Teams

- **Team Structure**: Lead + 3 teammates max

#### File-Conflict Dependencies

| Stories sharing files | Shared file | Resolution |
|---|---|---|
| STORY-001, STORY-002, STORY-003, STORY-005 | `peerread_tools.py` | STORY-001→002→003→005 |
| STORY-001, STORY-004, STORY-005 | `agent_system.py` | STORY-001→004→005 |
| STORY-006, STORY-008 | `traditional_metrics.py` | STORY-006→008 |
| STORY-006, STORY-009 | `test_llm_evaluation_managers.py` | STORY-006→009 |

#### Orchestration Waves

```text
Wave 1 (independent): STORY-001 (F1 dead code), STORY-007 (F7 typing)
Wave 2 (after STORY-001): STORY-002 (F2 format sanitize), STORY-006 (F6 judge accuracy)
Wave 3 (after Wave 2): STORY-003 (F3 PDF guard), STORY-004 (F4 API keys), STORY-008 (F8 type fixes)
Wave 4 (after Wave 3): STORY-005 (F5 security bundle), STORY-009 (F9 test quality sweep)
```

- **Quality Gates**: Teammate runs `make quick_validate`; lead runs `make validate` after each wave
- **Teammate Prompt Template**: Sprint 8 pattern with TDD `[RED]`/`[GREEN]` commit markers

Story Breakdown - Phase 1 (9 stories total):

- **Feature 1** → STORY-001: Delete orchestration.py dead code module
  Delete `src/app/agents/orchestration.py` (~317 lines) and any test files importing it. Files: `src/app/agents/orchestration.py`, `tests/agents/test_orchestration.py`.

- **Feature 2** → STORY-002: Sanitize paper_full_content format string (depends: STORY-001)
  Sanitize `paper_full_content` before `.format()` in `_load_and_format_template()`. Files: `src/app/tools/peerread_tools.py`, `tests/security/test_prompt_injection.py`.

- **Feature 3** → STORY-003: Add PDF file size guard (depends: STORY-002 [file: peerread_tools.py])
  Add `pdf_file.stat().st_size` check before `MarkItDown().convert()`. Files: `src/app/tools/peerread_tools.py`, `tests/tools/test_peerread_tools.py`.

- **Feature 4** → STORY-004: Remove API keys from os.environ (depends: STORY-001 [file: agent_system.py])
  Stop writing API keys to `os.environ`, pass via provider constructors. Files: `src/app/llms/providers.py`, `src/app/agents/agent_system.py`, `src/app/llms/models.py`, `tests/agents/test_agent_system.py`, `tests/llms/test_providers.py`.

- **Feature 5** → STORY-005: Security hardening bundle (depends: STORY-003 [file: peerread_tools.py], STORY-004 [file: agent_system.py])
  SSRF documentation, Phoenix validation, tool registration guard, security test false-pass fix. Files: `src/app/agents/agent_system.py`, `src/app/agents/logfire_instrumentation.py`, `src/app/tools/peerread_tools.py`, `tests/security/test_tool_registration.py`.

- **Feature 6** → STORY-006: Judge pipeline accuracy fixes (depends: STORY-001)
  Fix clarity field, silent stub, sentiment heuristic, cosine score clamp. Files: `src/app/judge/llm_evaluation_managers.py`, `src/app/data_models/evaluation_models.py`, `src/app/judge/traditional_metrics.py`, `tests/judge/test_llm_evaluation_managers.py`, `tests/judge/test_traditional_metrics.py`.

- **Feature 7** → STORY-007: Add type annotation to AgentConfig.tools field
  Change `tools: list[Any]` to `list[Callable[..., Awaitable[Any]]]`. Files: `src/app/data_models/app_models.py`, `tests/data_models/test_app_models.py`.

- **Feature 8** → STORY-008: Type safety + quick fixes (depends: STORY-001, STORY-006 [file: traditional_metrics.py])
  Seven LOW-effort type fixes bundled. Files: `src/app/benchmark/sweep_runner.py`, `src/app/engines/cc_engine.py`, `src/app/app.py`, `src/app/utils/load_configs.py`, `src/app/tools/peerread_tools.py`, `src/app/judge/traditional_metrics.py`, `src/app/judge/baseline_comparison.py`, `src/run_sweep.py`, `tests/judge/test_traditional_metrics.py`, `tests/judge/test_baseline_comparison.py`.

- **Feature 9** → STORY-009: Test suite quality sweep
  Add `spec=` to MagicMock, fix asyncio markers, fix thread-safety test, merge duplicate files, delete dead code. Files: 25 test files (edit), 2 test files (delete). See Feature 9 Files section for complete list.
