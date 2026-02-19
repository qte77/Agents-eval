# Test Suite Audit — 2026-02-17

**Scope**: All 83 test files under `tests/`
**Goal**: Identify tests that should be kept, removed, refactored, or replaced — focusing on behavioral (TDD/BDD) value
**Principle**: Tests verify *behavior* (what code does), not *implementation* (how it does it)
**Constraint**: Implementation code is NOT modified. Findings become next-sprint stories.

---

## Summary Statistics

| Domain | Files | Tests | Keep | Remove | Refactor | Delete File |
|--------|-------|-------|------|--------|----------|-------------|
| `tests/judge/` | 16 | ~156 | 135 | 15 | 7 | 0 |
| `tests/evals/` + `benchmark*/` | 13 | ~110 | 98 | 12 | 0 | 0 |
| `tests/agents/` + `tools/` + `llms/` + `data_*/` | 14 | ~100 | 73 | 17 | 10 | 0 |
| `tests/security/` | 5 | ~70 | 70 | 0 | 0 | 0 |
| `tests/utils/` | 7 | ~45 | 43 | 2 | 0 | 0 |
| `tests/app/` | 5 | ~40 | 37 | 0 | 3 | 0 |
| `tests/gui/` + `test_gui/` | 11 | ~55 | 44 | 11 | 0 | 0 |
| `tests/common/` | 1 | 3 | 3 | 0 | 0 | 0 |
| `tests/cleanup/` | 1 | 11 | 11 | 0 | 0 | 0 |
| `tests/docs/` | 1 | 4 | 4 | 0 | 0 | 0 |
| `tests/scripts/` | 1 | 5 | 4 | 1 | 0 | 0 |
| `tests/integration/` | 3 | ~30 | 30 | 0 | 0 | 0 |
| `tests/metrics/` | 1 | 3 | 3 | 0 | 0 | 0 |
| `tests/` (root) | 3 | 9 | 9 | 0 | 0 | 0 |
| **Total** | **83** | **~641** | **~564** | **~58** | **~20** | **0** |

**Overall health: GOOD.** ~88% of tests have clear behavioral value. ~9% should be removed, ~3% refactored.

---

## Files with Zero Issues (Exemplary)

These are reference-quality test files:

- `tests/judge/test_trace_data_quality.py` — property + snapshot, tests STORY-013 bug fix
- `tests/judge/test_composite_scorer_single_agent.py` — Hypothesis property + snapshot
- `tests/judge/test_graph_builder.py` — behavioral + property + snapshot
- `tests/judge/test_graph_analysis_tier3.py` — bug-fix verification + property tests
- `tests/judge/test_baseline_comparison.py` — symmetry property + snapshot
- `tests/judge/test_cc_trace_adapter.py` — adapter + property + compatibility tests
- `tests/evals/test_composite_scoring_scenarios.py` — scenario-based policy tests
- `tests/evals/test_composite_scoring_edge_cases.py` — edge case behavioral tests
- `tests/evals/test_evaluation_pipeline.py` — tier orchestration behavioral tests
- `tests/security/` (all 5 files) — MAESTRO security controls with Hypothesis
- `tests/data_utils/test_datasets_peerread.py` — comprehensive with Hypothesis + snapshot
- `tests/metrics/test_metrics_output_similarity.py` — invariants + snapshot

---

## Domain-by-Domain Findings

### 1. `tests/judge/` — MOSTLY GOOD

**DELETE (1 file, 5 tests)**:

- `test_trace_store.py` — All 5 tests are unimplemented placeholders for `TraceStore`. `test_audit_refactoring_verification.py` already verifies the correct behavioral tests remain (`TestTraceStoreThreadSafety`, `TestTraceStoreContextManager`). This file is dead code.

**REFACTOR (2 files, 7 tests)**:

- `test_trace_storage_logging.py` (3 tests) — Mocks `logger.info` and checks message text. Should test state changes (trace file exists at path) instead of log calls.
- `test_trace_skip_warning.py` (4 tests) — Same anti-pattern: mocks `logger.warning`. Should test skip conditions via return values or observable state.

**REMOVE (4 files, 8 tests)**:

- `test_judge_agent.py`: `test_judge_agent_has_same_interface_as_pipeline` (hasattr), `test_evaluation_pipeline_re_export_works` (import shim test)
- `test_llm_evaluation_managers.py`: `test_auto_mode_with_no_chat_provider_uses_default` (no assertion), `test_tier2_provider_env_var_override_still_works` (env var override = Pydantic framework behavior)
- `test_plugin_base.py`: `test_registry_duplicate_plugin_names_raises_error` (not critical path)
- `test_plugin_graph.py`, `test_plugin_llm_judge.py`, `test_plugin_traditional.py`: `test_existing_engine_tests_still_pass` (placeholder, no assertions — 3 tests)
- `test_evaluation_runner.py`: `test_logs_skip_when_no_ground_truth` (tests log message text, not behavior)

**COVERAGE GAPS**:

1. No integration smoke test hitting real LLM API (even one `@pytest.mark.integration` test)
2. `test_graph_builder.py` has no malformed trace data tests (missing keys, wrong types)
3. No test for complete pipeline failure (all tiers None)

---

### 2. `tests/evals/` + `tests/benchmark*/` — GOOD

**SIMPLIFY (3 files, remove ~12 tests)**:

- `test_judge_settings.py` (lines 20–71): Tests `BaseSettings` env var parsing and Pydantic validation — this is framework behavior, not our code. Remove `TestJudgeSettingsDefaults` and `TestJudgeSettingsValidation` classes. Keep `TestJudgeSettingsEnvOverrides` and helper method tests.
- `test_sweep_config.py` (lines 23–142): Tests Pydantic model construction and default values. Remove these, keep `test_generates_8_compositions`, `test_all_combinations_unique`, `test_includes_all_agents_*`.
- `test_sweep_analysis.py` (line 125–146): `test_composition_stats_creation` tests Pydantic model construction. Remove.
- `test_sweep_runner.py` (lines 59–62): `test_sweep_runner_initialization` tests constructor field assignment. Remove.

**PRODUCTION BUG (1 test needs enabling)**:

- `test_traditional_metrics.py` (lines 706–741): Skipped property test discovered `cosine_score` can be `1.0000000000000002` (floating-point precision). The test is *correct* — the production code needs clamping. Fix is: clamp scores to `[0.0, 1.0]` in `traditional_metrics.py`, then enable the test. This is a next-sprint item.

**COVERAGE GAPS**: None. Strong behavioral coverage including fallback policies, scoring edge cases, and integration flows.

---

### 3. `tests/agents/` + `tests/tools/` + `tests/llms/` + `tests/data_*/` — GOOD WITH ISSUES

**REMOVE (3 files, ~17 tests)**:

- `test_trace_collection_integration.py` (7 tests): `hasattr`-only checks without behavioral assertion — `test_agent_interaction_logged_on_delegation`, `test_tool_call_logging_during_delegation`, `test_delegation_logs_interaction_with_timing`, and 4 similar.
- `test_agent_system.py` (8 tests): Empty stubs (`"tested at integration level"`), tests for PydanticAI exception construction (library behavior, not our code), `TestAgentCreation` (empty, logfire side effects).
- `test_agent_factories.py` (2 empty classes): `TestEvaluationAgentCreation` and `TestSimpleAgentCreation` — explicitly commented out due to logfire side effects.

**REFACTOR (2 files, ~10 tests)**:

- `test_trace_collection_integration.py`: 1 test checks only `call_count >= 1` — should assert trace data content.
- `test_agent_system.py`: 2 tests check `mock.called` without verifying arguments — should verify delegation semantics.
- `test_agent_factories.py`: 4 tests verify only `isinstance(agent, Agent)` — should verify agent configuration (tools, model, system prompt).

**COVERAGE GAPS**:

1. Agent delegation logic: tools registered but actual delegation calls with correct arguments not verified
2. Agent prompt configuration not testable due to logfire instrumentation side effects — document this limitation
3. Trace data content validation: tests verify logging happens but not trace data structure

---

### 4. `tests/security/` — EXCELLENT, KEEP ALL

All 5 files are exemplary. Parametrized attacks + Hypothesis properties. Each maps to a MAESTRO layer:

- `test_ssrf_prevention.py` — IP blocking, scheme enforcement, IDN homograph attacks (Hypothesis)
- `test_prompt_injection.py` — XML wrapping, length limits, format string injection (Hypothesis)
- `test_sensitive_data_filtering.py` — API key / password / token redaction (Hypothesis)
- `test_input_size_limits.py` — Pydantic field constraints for DoS prevention (Hypothesis)
- `test_tool_registration.py` — Tool scope validation, isolation between agents

**Minor issue** in `test_tool_registration.py`:

- `test_peerread_tools_registration_succeeds` only checks `hasattr(agent, "_function_toolset")` — not a real registration check. Relies on PydanticAI internals but no better alternative exists. KEEP with note.
- `test_tool_registration_logged` (line 168) has no assertion — it's a best-practice test. REMOVE.

---

### 5. `tests/utils/` — MOSTLY GOOD

**REMOVE (2 tests)**:

- `test_log_scrubbing.py`: `TestLoguruIntegration.test_loguru_sink_configured_with_filter` (lines 169–179) — checks `hasattr(log, "logger")`, no actual filtering behavior tested.
- `test_log_scrubbing.py`: `test_setup_llm_environment_uses_debug_level` (lines 185–196) — inspects source code (`inspect.getsource`) to check for `logger.debug`. This tests implementation text, not behavior.

**KEEP ALL OTHERS**:

- `test_url_validation.py` — behavioral + Hypothesis. Excellent.
- `test_prompt_sanitization.py` — behavioral + Hypothesis. Good duplicate of security tests but at lower level.
- `test_weave_optional.py` — behavioral guard tests for wandb/weave import.
- `test_logfire_config.py` — single test, behavioral (custom values flow through).
- `test_login.py` — behavioral (wandb skip, error reporting env var, user override respected).
- `test_load_settings.py` — AST-based structural tests verifying dead code removal.

**Redundancy note**: `tests/utils/test_prompt_sanitization.py` and `tests/security/test_prompt_injection.py` cover the same `sanitize_*` functions. The security file is more thorough. The utils file adds useful boundary condition tests not in the security file. Keep both — different focus.

---

### 6. `tests/app/` — KEEP ALL, MINOR ISSUES

**KEEP ALL**:

- `test_app.py` — behavioral: graph built/not built based on execution_id
- `test_evaluation_wiring.py` — behavioral: skip_eval flag, ground truth handling, Hypothesis property + snapshot
- `test_cli_token_limit.py` — behavioral: priority order CLI > env > config. BUT: lines 131–144 contain trivial property tests that just assert `limit < 1000` / `limit > 1000000` (tautologies — no production code called). **REMOVE these 3 pseudo-property tests**.
- `test_cli_baseline.py` — behavioral: CC solo/teams dirs, 3-way comparison, snapshot output
- `test_logfire_initialization.py` — behavioral: init when enabled, skip when disabled, graceful degradation. BUT: `test_logfire_initialization_uses_judge_settings` (line 56) only checks `hasattr(settings, "logfire_enabled")` — **REMOVE**.

---

### 7. `tests/gui/` + `tests/test_gui/` — NEEDS CLEANUP

**REMOVE (Pydantic framework tests in `test_settings_integration.py`)**:

- `test_common_settings_instantiation` — tests default field values (Pydantic behavior)
- `test_judge_settings_instantiation` — same, tests default field values
- These should be in `test_common_settings.py` and `test_judge_settings.py` if anywhere, but reviewer-evals already flagged those as framework tests too.

**KEEP**:

- `test_settings_integration.py`: `test_render_settings_accepts_*` (behavioral), `test_settings_values_are_customizable` (behavioral)
- `test_session_state.py` — snapshot + behavioral, tests defaults structure and provider registry membership
- `test_prompts_integration.py` — tests that dead code (`PROMPTS_DEFAULT`) was removed. Valid cleanup verification.
- `test_gui/test_settings_page.py` — behavioral UI tests with mocked Streamlit
- `test_gui/test_session_state_wiring.py` — behavioral: CompositeResult flow through session state + Hypothesis + snapshot

**COVERAGE GAP**: No behavioral tests for GUI error states (what happens when evaluation fails mid-render).

---

### 8. `tests/common/` — KEEP ALL

`test_common_settings.py` has 3 tests, all behavioral: env var override, `.env` file loading, env overrides code defaults. Already cleaned up per `test_audit_refactoring_verification.py`.

---

### 9. `tests/cleanup/` — KEEP ALL (Verification Tests)

`test_opik_removal.py` — 11 tests verifying Opik code, Docker, Makefile targets, env vars, docs, imports were all removed. This is a legitimate pattern: tests that verify intentional deletions stay deleted.

---

### 10. `tests/docs/` — REMOVE

`test_sprint5_review.py` — 4 tests checking that `docs/reviews/sprint5-code-review.md` exists and contains certain section headers. This is testing documentation, not code behavior.

- `test_sprint5_review_document_exists` — file existence check
- `test_sprint5_review_has_required_sections` — content contains "Layer 1", etc.
- `test_sprint5_review_documents_findings` — contains "CRITICAL" or "HIGH"
- `test_sprint5_review_includes_fixes` — contains "Fix:" or "Recommendation:"

These fail silently if the document is updated and sections renamed. **DELETE the entire file** — sprint review documentation completeness is a human process, not a test concern.

---

### 11. `tests/scripts/` — MOSTLY GOOD

`test_collect_cc_scripts.py` — tests shell scripts via `subprocess.run`. Behavioral (exit codes, file creation, JSON validity).

**REMOVE (1 test)**:

- `test_validation_failure_returns_exit_code_1` (line 107 in TestCollectCCSolo) — explicitly `pytest.skip`ped with comment "hard to trigger without breaking jq dependency". Should be deleted, not skipped.

---

### 12. `tests/integration/` — KEEP ALL

All 3 integration test files test real PeerRead dataset formats and evaluation pipeline compatibility. Appropriate use of `@pytest.mark.integration` / skip patterns for CI. No implementation detail testing.

---

### 13. `tests/metrics/` — KEEP ALL

`test_metrics_output_similarity.py` — 3 tests: behavioral similarity check, Hypothesis bounds property, snapshot regression. Exemplary.

---

### 14. Root test files — KEEP ALL

- `tests/conftest.py` — adds `src/` to `sys.path`. Essential.
- `tests/test_cc_otel_cleanup.py` — verifies `cc_otel` module deletion (same pattern as `test_opik_removal.py`). Keep.
- `tests/test_audit_refactoring_verification.py` — verifies this sprint's test audit changes were applied correctly. Keep through the next sprint, then delete once findings are validated and stable.

---

## Anti-Patterns Found (Cross-Cutting)

### 1. Logger-mocking anti-pattern (7 tests)

**Files**: `test_trace_storage_logging.py`, `test_trace_skip_warning.py`
**Issue**: Mock `logger.warning` / `logger.info` and assert on message text. Brittle (text changes break tests) and tests implementation not behavior.
**Fix**: Test observable state or return values. For storage: assert file exists. For skip: assert return value is None/empty.

### 2. `hasattr`-only checks (8 tests)

**Files**: `test_trace_collection_integration.py`, `test_tool_registration.py`, `test_judge_agent.py`
**Issue**: `assert hasattr(obj, "method")` — only checks interface existence, catches nothing useful.
**Fix**: Call the method and assert the result.

### 3. Pydantic framework tests (12 tests)

**Files**: `test_judge_settings.py`, `test_sweep_config.py`, `test_sweep_analysis.py`, `test_settings_integration.py`
**Issue**: Tests that `BaseSettings` loads from env vars or that Pydantic validates types. These test the library, not our code.
**Fix**: Remove. Keep env-override tests only when they test *our* configuration logic (e.g., what happens at thresholds, not that the env var mechanism works).

### 4. Empty test classes (2 classes)

**Files**: `test_agent_factories.py`
**Issue**: `TestEvaluationAgentCreation` and `TestSimpleAgentCreation` have no test methods — commented out due to logfire side effects.
**Fix**: Delete the empty classes. Document the limitation in `AGENT_LEARNINGS.md`.

### 5. Source-code inspection tests (2 tests)

**Files**: `test_log_scrubbing.py`, `test_cli_baseline.py`
**Issue**: `inspect.getsource(fn)` to check for `"logger.debug"` or specific flag strings. Tests implementation text.
**Fix**: For logging level: test observable behavior (no INFO log appears, DEBUG log appears with appropriate level). For flag: keep the `parse_args` test which actually calls the function.

### 6. Tautological property tests (3 tests)

**File**: `test_cli_token_limit.py`
**Issue**: Property tests that assert `limit < 1000` on inputs constrained to `max_value=999` — the assertion is always true and no production code is exercised.
**Fix**: Remove. Replace with actual validation tests calling `setup_agent_env` with out-of-range values.

---

## Tests to DELETE (Entire Files)

| File | Reason |
|------|--------|
| `tests/docs/test_sprint5_review.py` | Tests documentation content, not code behavior |

---

## Tests to REMOVE (Individual Tests)

| File | Test(s) | Reason |
|------|---------|--------|
| `tests/judge/test_judge_agent.py` | `test_judge_agent_has_same_interface_as_pipeline`, `test_evaluation_pipeline_re_export_works` | hasattr / import shim |
| `tests/judge/test_llm_evaluation_managers.py` | `test_auto_mode_with_no_chat_provider_uses_default`, `test_tier2_provider_env_var_override_still_works` | No assertion / framework behavior |
| `tests/judge/test_plugin_base.py` | `test_registry_duplicate_plugin_names_raises_error` | Not critical behavior |
| `tests/judge/test_plugin_graph.py` | `test_existing_engine_tests_still_pass` | Placeholder, no assertions |
| `tests/judge/test_plugin_llm_judge.py` | `test_existing_engine_tests_still_pass` | Placeholder, no assertions |
| `tests/judge/test_plugin_traditional.py` | `test_existing_engine_tests_still_pass` | Placeholder, no assertions |
| `tests/judge/test_evaluation_runner.py` | `test_logs_skip_when_no_ground_truth` | Tests log message text |
| `tests/evals/test_judge_settings.py` | `TestJudgeSettingsDefaults` class (lines 20-36), `TestJudgeSettingsValidation` class (lines 38-71) | Pydantic framework |
| `tests/evals/test_sweep_config.py` | Lines 23–142 (Pydantic model construction and default tests) | Pydantic framework |
| `tests/evals/test_sweep_analysis.py` | `test_composition_stats_creation` | Pydantic model construction |
| `tests/benchmark/test_sweep_runner.py` | `test_sweep_runner_initialization` | Trivial constructor field check |
| `tests/agents/test_trace_collection_integration.py` | 7 hasattr-only tests | No behavioral assertion |
| `tests/agents/test_agent_system.py` | 8 tests (empty stubs, library behavior) | No behavioral value |
| `tests/agents/test_agent_factories.py` | `TestEvaluationAgentCreation`, `TestSimpleAgentCreation` classes | Empty (no test methods) |
| `tests/utils/test_log_scrubbing.py` | `test_loguru_sink_configured_with_filter`, `test_setup_llm_environment_uses_debug_level` | hasattr / source inspection |
| `tests/security/test_tool_registration.py` | `test_tool_registration_logged` | No assertion |
| `tests/app/test_cli_token_limit.py` | `test_valid_token_limits_accepted`, `test_token_limit_below_minimum_rejected`, `test_token_limit_above_maximum_rejected` | Tautological assertions |
| `tests/app/test_logfire_initialization.py` | `test_logfire_initialization_uses_judge_settings` | hasattr check only |
| `tests/gui/test_settings_integration.py` | `test_common_settings_instantiation`, `test_judge_settings_instantiation` | Pydantic framework defaults |
| `tests/scripts/test_collect_cc_scripts.py` | `test_validation_failure_returns_exit_code_1` (TestCollectCCSolo) | Permanently skipped |

---

## Tests to REFACTOR

| File | Tests | Current Issue | Target Behavior |
|------|-------|---------------|-----------------|
| `tests/judge/test_trace_storage_logging.py` | All 3 | Mock `logger.info`, check text | Assert trace data persisted / retrievable |
| `tests/judge/test_trace_skip_warning.py` | All 4 | Mock `logger.warning`, check text | Assert skip conditions produce no trace / empty result |
| `tests/agents/test_trace_collection_integration.py` | 1 (`call_count >= 1`) | No argument verification | Assert trace data content is correct |
| `tests/agents/test_agent_system.py` | 2 (`mock.called`) | No delegation argument check | Assert delegation called with correct agent IDs |
| `tests/agents/test_agent_factories.py` | 4 (`isinstance` only) | No config verification | Assert agent has expected tools / model |

---

## Coverage Gaps (Next Sprint Stories)

### HIGH Priority

1. **Floating-point precision in traditional metrics** — `cosine_score` can exceed `1.0` (e.g., `1.0000000000000002`). Hypothesis test in `test_traditional_metrics.py` (lines 706–741) correctly identifies this. Fix: clamp scores in `traditional_metrics.py`. Enable the skipped test.

2. **Agent delegation argument verification** — `tests/agents/` verifies tools are registered but not that delegation calls pass correct arguments. Add tests for actual `log_agent_interaction` call arguments.

3. **Trace data content validation** — Storage tests verify trace operations happen but not the data structure/content stored.

### MEDIUM Priority

1. **Complete pipeline failure** — No test for all tiers returning None (catastrophic failure path).

2. **Malformed trace data in graph_builder** — `test_graph_builder.py` covers valid inputs; no tests for missing keys / wrong types.

3. **GUI error states** — No tests for what happens when evaluation fails mid-render in Streamlit pages.

4. **Token limit validation** — `test_cli_token_limit.py` has tautological tests instead of real boundary validation calls through `setup_agent_env`.

---

## Patterns Worth Keeping (Recommendations)

The following patterns appear consistently in the best test files and should be the standard:

1. **Hypothesis property tests** — Used well in judge/, evals/, security/, data_utils/. Prefer `@given` over manually parameterized edge cases.
2. **`inline-snapshot`** — Used for regression detection throughout. Catches structural changes without maintaining large expected dicts by hand.
3. **Mock only external dependencies** — e.g., mock HTTP calls, file systems, LLM APIs. Do NOT mock our own code's internals.
4. **Scenario-based tests** — `test_composite_scoring_scenarios.py` is the model: test policies and recommendations, not arithmetic.
5. **Cleanup verification tests** — `test_opik_removal.py`, `test_cc_otel_cleanup.py` pattern is valid for ensuring deliberate deletions stay deleted.

---

## Implementation Guidance for Next Sprint

**Net change**: Remove ~58 low-value tests, refactor ~20 tests = ~78 changes total.

**Safe ordering** (avoids coverage valleys):

1. Refactor logger-mocking tests FIRST (replace with behavioral equivalents before removing)
2. Remove tautological / empty / placeholder tests
3. Remove Pydantic framework tests
4. Fix floating-point bug in `traditional_metrics.py`, enable skipped property test
5. Add missing coverage (delegation args, trace content, pipeline failure)

**Estimated outcome**: ~564 tests remaining after cleanup, with higher signal density and zero dead-weight assertions.
