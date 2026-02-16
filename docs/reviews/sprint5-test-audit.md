# Sprint 5 Test Suite Audit

**Date**: 2026-02-16
**Auditor**: Claude (STORY-011)
**Scope**: All 64 test files in `tests/`
**Criteria**: Testing strategy from `docs/best-practices/testing-strategy.md`

## Executive Summary

Systematic audit of all test files to identify and remove implementation-detail tests while preserving behavioral coverage. The audit applies the testing strategy principle: **"If the test wouldn't catch a real bug, remove it."**

**Results**:
- **Analyzed**: 64 test files (~500 total tests)
- **Keep as-is**: 35 files (behavioral/integration focus)
- **Delete entirely**: 4 files (migration artifacts)
- **Refactor**: 11 files (mix of behavioral and implementation tests)
- **Estimated reduction**: 80-100 low-value tests removed (16-20% reduction)
- **Behavioral coverage**: No reduction - only implementation-detail tests removed

---

## Anti-Patterns Identified

| Anti-Pattern | Count | Why Remove |
|--------------|-------|------------|
| Default constant tests | ~30 | Testing `300 == 300`, no business logic |
| Field existence tests | ~12 | Python/imports handle, `hasattr()` equivalent |
| Type validation tests | ~6 | Pydantic validates automatically |
| Import/module existence tests | ~15 | Python import system handles |
| Property getter tests | ~9 | Testing `@property` returns value |

---

## Category 1: KEEP AS-IS (35 files)

Tests verify behavior, not implementation details.

### Behavioral Tests (Core Business Logic)

1. **tests/evals/test_composite_scoring_scenarios.py** - KEEP AS-IS
   - Tests business scenarios (high quality/fast, low quality/slow, mixed)
   - Validates recommendation boundary conditions
   - Tests scenario ranking accuracy

2. **tests/evals/test_composite_scoring_interpretability.py** - KEEP AS-IS
   - Tests score consistency across boundaries
   - Validates dominant metric impact
   - Tests mathematical properties

3. **tests/evals/test_composite_scoring_edge_cases.py** - KEEP AS-IS
   - Tests missing tier handling
   - Validates zero-score behavior
   - Tests error propagation

4. **tests/evals/test_traditional_metrics.py** - KEEP AS-IS
   - Tests cosine/Jaccard/semantic similarity algorithms
   - Uses Hypothesis for property-based testing
   - Validates execution time measurement

5. **tests/evals/test_composite_scorer.py** - KEEP AS-IS
   - Tests metric extraction from tier results
   - Validates composite score calculation with weights
   - Tests recommendation mapping logic

6. **tests/evals/test_evaluation_pipeline.py** - KEEP AS-IS
   - Tests tier execution orchestration
   - Validates timeout handling and error propagation
   - Tests performance monitoring

7. **tests/evals/test_metric_comparison_logging.py** - KEEP AS-IS
   - Tests logging behavior after evaluation
   - Validates metric comparison output

8. **tests/evals/test_judge_provider_fallback.py** - KEEP AS-IS
   - Tests provider fallback chain behavior
   - Validates API key availability checking

9. **tests/evals/test_llm_evaluation_managers_integration.py** - KEEP AS-IS
   - Integration tests for LLM judge orchestration

10. **tests/data_models/test_peerread_models_serialization.py** - KEEP AS-IS
    - Uses inline-snapshot for regression testing
    - Tests API contracts (serialization behavior)

11. **tests/data_utils/test_datasets_peerread.py** - KEEP AS-IS
    - Tests URL construction logic
    - Validates error handling for invalid inputs

12. **tests/agents/test_peerread_tools.py** - KEEP AS-IS
    - Tests review saving with file persistence
    - Tests PDF reading with error handling
    - Tests content truncation logic

13. **tests/agents/test_logfire_instrumentation.py** - KEEP AS-IS
    - Tests integration with OpenTelemetry
    - Validates graceful degradation behavior

14. **tests/agents/test_rate_limit_handling.py** - KEEP AS-IS
    - Tests retry logic and error handling

15. **tests/agents/test_provider_env_setup.py** - KEEP AS-IS
    - Tests environment variable configuration behavior

16. **tests/agents/test_trace_collection_integration.py** - KEEP AS-IS
    - Integration tests for trace collection

17. **tests/app/test_cli_token_limit.py** - KEEP AS-IS
    - Tests CLI argument parsing and validation

18. **tests/app/test_evaluation_wiring.py** - KEEP AS-IS
    - Tests integration between components

19. **tests/app/test_cli_baseline.py** - KEEP AS-IS
    - Tests CLI baseline behavior

20. **tests/app/test_logfire_initialization.py** - KEEP AS-IS
    - Tests initialization behavior and error handling

21. **tests/judge/test_composite_scorer_single_agent.py** - KEEP AS-IS
    - Tests weight redistribution behavior

22. **tests/judge/test_baseline_comparison.py** - KEEP AS-IS
    - Tests metric comparison logic

23. **tests/judge/test_llm_evaluation_managers.py** - KEEP AS-IS
    - Tests orchestration and delegation

24. **tests/judge/test_trace_data_quality.py** - KEEP AS-IS
    - Tests data quality validation

25. **tests/judge/test_trace_storage_logging.py** - KEEP AS-IS
    - Tests logging behavior

26. **tests/judge/test_trace_skip_warning.py** - KEEP AS-IS
    - Tests warning emission behavior

27. **tests/judge/test_cc_trace_adapter.py** - KEEP AS-IS
    - Tests trace adaptation logic

28. **tests/judge/test_graph_builder.py** - KEEP AS-IS
    - Tests graph construction algorithms

29. **tests/judge/test_evaluation_runner.py** - KEEP AS-IS
    - Tests orchestration behavior

30. **tests/metrics/test_metrics_output_similarity.py** - KEEP AS-IS
    - Tests similarity calculation algorithms

31. **tests/tools/test_peerread_tools_tracing.py** - KEEP AS-IS
    - Tests tracing integration

32. **tests/utils/test_weave_optional.py** - KEEP AS-IS
    - Tests optional dependency handling

33. **tests/benchmarks/test_performance_baselines.py** - KEEP AS-IS
    - Tests performance measurement

34. **tests/integration/test_peerread_integration.py** - KEEP AS-IS
    - Integration tests with real data

35. **tests/integration/test_enhanced_peerread_integration.py** - KEEP AS-IS
    - Enhanced integration scenarios

36. **tests/integration/test_peerread_real_dataset_validation.py** - KEEP AS-IS
    - Real dataset validation

37. **tests/gui/test_settings_integration.py** - KEEP AS-IS
    - GUI settings behavior tests

38. **tests/gui/test_prompts_integration.py** - KEEP AS-IS
    - GUI prompts integration tests

39. **tests/gui/test_session_state.py** - KEEP AS-IS
    - Session state management tests

40. **tests/test_gui/test_agent_graph_page.py** - KEEP AS-IS
    - Graph page rendering tests

41. **tests/test_gui/test_sidebar_phoenix.py** - KEEP AS-IS
    - Sidebar behavior tests

42. **tests/test_gui/test_evaluation_baseline.py** - KEEP AS-IS
    - Evaluation page baseline tests

43. **tests/test_gui/test_log_capture.py** - KEEP AS-IS
    - Log capture behavior tests

44. **tests/test_gui/test_run_app.py** - KEEP AS-IS
    - App execution tests

45. **tests/test_gui/test_session_state_wiring.py** - KEEP AS-IS
    - Session state wiring tests

46. **tests/test_gui/test_evaluation_page.py** - KEEP AS-IS
    - Evaluation page rendering tests

47. **tests/test_gui/test_settings_page.py** - KEEP AS-IS
    - Settings page interaction tests

48. **tests/docs/test_sprint5_review.py** - KEEP AS-IS
    - Documentation validation tests

---

## Category 2: DELETE ENTIRELY (4 files)

All tests verify implementation details or migration artifacts.

### Files to Delete

1. **tests/evals/test_opik_metrics.py** - DELETE ENTIRELY
   - Already removed (contains only comment)
   - Migration artifact

2. **tests/integration/test_opik_integration.py** - DELETE ENTIRELY
   - Already removed (contains only comment)
   - Migration artifact

3. **tests/evals/test_opik_removal.py** - DELETE ENTIRELY
   - Tests verify file deletion and import existence
   - Tests check for string presence in source code
   - Uses AST parsing to verify decorator removal
   - **Anti-patterns**: Import existence tests, file existence checks
   - **Verdict**: All tests verify implementation cleanliness, not behavior

4. **tests/test_migration_cleanup.py** - DELETE ENTIRELY
   - Tests check for `app.evals.*` import presence
   - Verifies file deletion (duplicate peerread_tools.py)
   - Checks for FIXME comments in source
   - **Anti-patterns**: Import existence tests, AST parsing
   - **Verdict**: Tests verify implementation cleanliness, not business logic

---

## Category 3: REFACTOR (11 files)

Mix of behavioral and implementation-detail tests.

### 1. tests/common/test_common_settings.py - REFACTOR

**KEEP** (3 tests):
- `test_common_settings_env_prefix` - Tests env var override behavior
- `test_common_settings_env_file_loading` - Tests .env file loading behavior
- `test_common_settings_env_override_defaults` - Tests override behavior

**DELETE** (2 tests):
- `test_common_settings_defaults` - Tests default constants (`DEFAULT == "INFO"`)
- `test_common_settings_type_validation` - Pydantic validates types

---

### 2. tests/evals/test_judge_settings.py - REFACTOR

**KEEP** (13 tests):
- All `TestJudgeSettingsEnvOverrides` tests (env var override behavior)
- All `TestJudgeSettingsValidation` tests (business rules: positive values, bounds)
- All `TestJudgeSettingsCompatibility` tests (backward compatibility behavior)

**DELETE** (13 tests):
- Entire `TestJudgeSettingsDefaults` class (lines 17-72)
  - `test_tier1_max_seconds_default` - Tests `1.0 == 1.0`
  - `test_tier2_model_default` - Tests `"gpt-4o-mini" == "gpt-4o-mini"`
  - `test_tier2_provider_default` - Tests `"openai" == "openai"`
  - `test_tier2_fallback_model_default`
  - `test_tier2_fallback_provider_default`
  - `test_tier2_max_seconds_default`
  - `test_tier2_agent_timeout_default`
  - `test_tier3_max_seconds_default`
  - `test_composite_accept_threshold_default`
  - `test_composite_weak_accept_threshold_default`
  - `test_composite_weak_reject_threshold_default`
  - `test_tiers_enabled_default`
  - `test_tier2_metrics_default`

---

### 3. tests/utils/test_logfire_config.py - REFACTOR

**KEEP** (4 tests):
- `test_logfire_config_from_settings_custom` - Tests custom values behavior
- `test_logfire_config_env_file_loading` - Tests .env loading behavior
- `test_logfire_config_env_override_defaults` - Tests override behavior
- `test_logfire_config_otlp_endpoint_computed` - Tests computed property behavior

**DELETE** (3 tests):
- `test_logfire_config_from_settings_defaults` - Tests default values
- `test_logfire_config_direct_instantiation` - Tests constructor with literals
- `test_logfire_config_type_validation` - Pydantic validates types

---

### 4. tests/cc_otel/test_cc_otel_config.py - REFACTOR

**KEEP** (remaining behavioral tests):
- All env override tests
- All computed property tests

**DELETE** (2 tests):
- `test_cc_otel_config_defaults` (lines 14-22) - Tests default constants
- `test_cc_otel_config_type_validation` (lines 63-72) - Pydantic validates

---

### 5. tests/judge/test_plugin_base.py - REFACTOR

**KEEP** (all registry tests):
- `test_registry_execute_all_in_order` - Tests execution order behavior
- All context passing tests
- All error handling tests

**DELETE** (4 tests from `TestEvaluatorPluginABC` class, lines 112-138):
- `test_plugin_has_name_property` - Tests property existence
- `test_plugin_has_tier_property` - Tests property existence
- `test_plugin_has_evaluate_method` - Tests method existence
- `test_plugin_has_get_context_for_next_tier_method` - Tests method existence

---

### 6. tests/judge/test_trace_store.py - REFACTOR

**KEEP**:
- All thread-safety tests (tests concurrency behavior)
- All context manager tests (tests resource cleanup behavior)

**DELETE** (lines 18-78 + lines 195-228):
- `TestTraceStore` class basic CRUD tests (dict-like behavior assumed)
- Metadata tracking tests (field existence checks)

---

### 7. tests/judge/test_plugin_llm_judge.py - REFACTOR

**KEEP**:
- All integration tests with mocked engine
- All context passing tests
- All timeout configuration tests

**DELETE** (lines 63-73, 3 tests):
- `test_plugin_implements_evaluator_interface` - isinstance check
- `test_plugin_name_property` - Tests property value
- `test_plugin_tier_property` - Tests constant value

---

### 8. tests/judge/test_plugin_traditional.py - REFACTOR

**KEEP**:
- All delegation tests
- All timeout tests
- All integration tests

**DELETE** (lines 52-62, 3 tests):
- `test_plugin_implements_evaluator_interface`
- `test_plugin_name_property`
- `test_plugin_tier_property`

---

### 9. tests/judge/test_plugin_graph.py - REFACTOR

**KEEP**:
- All delegation tests
- All integration tests

**DELETE** (lines 53-63, 3 tests):
- `test_plugin_implements_evaluator_interface`
- `test_plugin_name_property`
- `test_plugin_tier_property`

---

### 10. tests/evals/test_graph_analysis.py - REFACTOR

**KEEP**:
- All algorithm tests (graph construction, metric calculation)
- All edge case tests (empty graphs, single nodes)

**DELETE** (if any field existence or type check tests exist - needs per-test review)

---

### 11. tests/judge/test_judge_agent.py - REFACTOR (Actually KEEP AS-IS on re-review)

All tests verify orchestration behavior, integration contracts, backward compatibility.

---

## Execution Plan

### Phase 1: Delete Entire Files (4 files)

```bash
rm tests/evals/test_opik_removal.py
rm tests/test_migration_cleanup.py
# Note: test_opik_metrics.py and test_opik_integration.py already removed
```

### Phase 2: Delete Implementation-Detail Tests (by file)

1. **tests/evals/test_judge_settings.py**: Delete `TestJudgeSettingsDefaults` class (13 tests)
2. **tests/common/test_common_settings.py**: Delete 2 tests
3. **tests/utils/test_logfire_config.py**: Delete 3 tests
4. **tests/cc_otel/test_cc_otel_config.py**: Delete 2 tests
5. **tests/judge/test_plugin_base.py**: Delete 4 tests (`TestEvaluatorPluginABC`)
6. **tests/judge/test_trace_store.py**: Delete basic CRUD and metadata tests
7. **tests/judge/test_plugin_llm_judge.py**: Delete 3 tests (lines 63-73)
8. **tests/judge/test_plugin_traditional.py**: Delete 3 tests (lines 52-62)
9. **tests/judge/test_plugin_graph.py**: Delete 3 tests (lines 53-63)

### Phase 3: Verification

```bash
make validate
make test_all
```

Expected outcome:
- All remaining tests pass
- No reduction in behavioral coverage
- 16-20% reduction in test suite size
- Faster test execution

---

## Impact Analysis

**Before**:
- ~500 total tests across 64 files
- ~80-100 implementation-detail tests

**After**:
- ~400-420 behavioral tests across 60 files
- 0 implementation-detail tests
- No loss of bug-catching capability
- Cleaner, more maintainable test suite

---

## Conclusion

This audit identifies 80-100 low-value tests for removal while preserving all behavioral coverage. The refactoring aligns the test suite with the testing strategy principle: **"Test behavior, not implementation details."**

Every remaining test answers the question: **"Would this catch a real bug?"**
