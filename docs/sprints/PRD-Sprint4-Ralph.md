---
title: Product Requirements Document: Agents-eval Sprint 4
version: 2.0.0
created: 2026-02-15
updated: 2026-02-15
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 3 is complete: plugin architecture, GUI wiring, test alignment, optional weave, and trace quality fixes are all shipped.

Sprint 4 has two goals:

1. **Operational resilience** -- graceful degradation for Logfire trace export failures, thread-safe Tier 3 timeout handling, Tier 2 judge fallback validation, and completing test infrastructure alignment.
2. **CC baseline comparison** -- compare Claude Code against the PydanticAI MAS in two modes: **solo** (single CC instance, no orchestration) and **teams** (CC Agent Teams with delegation). Both modes run with full internal tool, plugin, and MCP access -- the same capabilities available to the PydanticAI agents. Artifacts from both modes are parsed into `GraphTraceData` and evaluated through the same three-tier pipeline, enabling a three-way comparison: PydanticAI MAS vs CC solo vs CC teams.

---

## Functional Requirements

### Sprint 4: Operational Resilience & CC Baseline Comparison

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Graceful Logfire Trace Export Failures

**Description**: Suppress noisy exception stack traces when Logfire/OTLP trace export fails due to connection errors (e.g., Opik service not running on localhost:6006). Currently, both span and metrics export print full ConnectionRefusedError stack traces to stderr multiple times during execution and at shutdown, cluttering logs during normal operation when tracing is unavailable. Affects both CLI (`make run_cli`) and GUI (`make run_gui`) equally.

**Acceptance Criteria**:

- [ ] Logfire initialization catches connection errors and logs single warning message
- [ ] Failed span exports do not print stack traces to stderr during agent runs
- [ ] Failed metrics exports do not print stack traces to stderr at shutdown
- [ ] When OTLP endpoint is unreachable, log one warning at initialization (not per-export)
- [ ] App continues normal operation when Logfire endpoint unavailable (both CLI and GUI)
- [ ] When Opik service is running, traces and metrics export successfully (no regression)
- [ ] Suppression works for both `/v1/traces/v1/traces` (spans) and `/v1/traces/v1/metrics` (metrics) endpoints
- [ ] Tests: Hypothesis property tests for retry/backoff behavior bounds
- [ ] Tests: inline-snapshot for warning message format
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Add connection check in `LogfireInstrumentationManager._initialize_logfire()` (`src/app/agents/logfire_instrumentation.py:50-71`)
- Catch `requests.exceptions.ConnectionError` during initialization
- Set `self.config.enabled = False` when OTLP endpoint unreachable
- Log single warning: "Logfire tracing unavailable: {endpoint} unreachable (spans and metrics export disabled)"
- Configure OTLP span exporter with retry backoff to minimize per-span error noise
- Configure OTLP metrics exporter with retry backoff to minimize per-metric error noise
- Ensure existing `try/except` at line 69-71 handles initialization failures
- Suppress OpenTelemetry SDK export errors when endpoint connection fails (both span and metrics exporters)

**Files**:

- `src/app/agents/logfire_instrumentation.py`
- `tests/agents/test_logfire_instrumentation.py` (new)

---

#### Feature 2: Thread-Safe Graph Analysis Timeout Handling

**Description**: Replace Python `signal`-based timeouts in Tier 3 graph analysis with thread-safe alternatives. Currently, `_with_timeout()` fails with "signal only works in main thread" when called from Streamlit (non-main thread), causing `path_convergence` metric to return 0.0 fallback.

**Acceptance Criteria**:

- [ ] Graph analysis timeout handling works in both main and non-main threads
- [ ] `path_convergence` calculation succeeds in Streamlit GUI (no signal error)
- [ ] CLI evaluation continues to work with timeouts (no regression)
- [ ] Timeout mechanism uses `concurrent.futures.ThreadPoolExecutor` with timeout parameter
- [ ] Graceful fallback when timeout occurs (return 0.3, log warning)
- [ ] Tests: Hypothesis property tests for timeout bounds (0.0 <= fallback <= 0.5)
- [ ] Tests: inline-snapshot for timeout error result structure
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Replace `signal`-based `_with_timeout()` in `src/app/judge/graph_analysis.py:348`
- Implement thread-safe timeout using `concurrent.futures.ThreadPoolExecutor`:

  ```python
  from concurrent.futures import ThreadPoolExecutor, TimeoutError

  def _with_timeout(func, *args, timeout=5.0):
      with ThreadPoolExecutor(max_workers=1) as executor:
          future = executor.submit(func, *args)
          return future.result(timeout=timeout)
  ```

- Update `_calculate_path_convergence()` exception handler (line 342) to catch `concurrent.futures.TimeoutError`
- Maintain existing fallback values: disconnected graph -> 0.2, timeout -> 0.3
- Preserve debug logging for timeout events

**Files**:

- `src/app/judge/graph_analysis.py`
- `tests/evals/test_graph_analysis.py` (update timeout tests)

---

#### Feature 3: Tier 2 Judge Provider Fallback Validation

**Description**: End-to-end validation that judge provider fallback works correctly. This is a testing and documentation task to confirm existing implementation handles missing API keys gracefully.

**Acceptance Criteria**:

- [ ] Integration test: Run evaluation with `tier2_provider=openai` and no `OPENAI_API_KEY` set
- [ ] Verify fallback to `tier2_fallback_provider` occurs (check logs)
- [ ] Verify Tier 2 metrics use neutral fallback scores (0.5) when all providers unavailable
- [ ] Verify composite score redistributes weights when Tier 2 is skipped
- [ ] Verify `Tier2Result` includes fallback metadata flag
- [ ] Update `docs/best-practices/troubleshooting.md` with Tier 2 auth failure guidance
- [ ] Tests: inline-snapshot for Tier2Result with fallback metadata
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Create integration test in `tests/evals/test_llm_evaluation_managers_integration.py`
- Test scenarios:
  1. Valid primary provider -> Tier 2 succeeds
  2. Invalid primary + valid fallback -> fallback succeeds
  3. Both providers unavailable -> neutral scores, Tier 2 skipped
- Add troubleshooting section to `docs/best-practices/troubleshooting.md`:
  - Symptom: "status_code: 401, model_name: gpt-4o-mini"
  - Cause: Missing OPENAI_API_KEY when tier2_provider=openai
  - Solution: Set valid API key or configure tier2_fallback_provider
- Document expected behavior when Tier 2 is skipped (weight redistribution)

**Files**:

- `tests/evals/test_llm_evaluation_managers_integration.py` (new)
- `docs/best-practices/troubleshooting.md` (new)

---

#### Feature 4: Complete Test Suite Alignment

**Description**: Refactor remaining test suite to use hypothesis (property-based testing) and inline-snapshot (regression testing), completing the test infrastructure alignment. No production code changes. Covers integration tests, benchmarks, GUI tests, and data utilities not yet converted. Explicitly excludes BDD/Gherkin (pytest-bdd).

**Acceptance Criteria**:

- [ ] Property-based tests using `@given` for data validation (PeerRead dataset schemas, model invariants)
- [ ] Property-based tests for integration test invariants (API responses, file I/O operations)
- [ ] Property-based tests for GUI state management (session state updates, widget interactions)
- [ ] Snapshot tests using `snapshot()` for integration test outputs (trace data, evaluation results)
- [ ] Snapshot tests for GUI page rendering outputs (Streamlit component structures)
- [ ] Snapshot tests for benchmark result structures
- [ ] Remove low-value tests (trivial assertions, field existence checks per testing-strategy.md)
- [ ] All existing test coverage maintained or improved
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated
- [ ] Add `from hypothesis import given, strategies as st` imports to relevant test files
- [ ] Add `from inline_snapshot import snapshot` imports to relevant test files
- [ ] Convert data validation tests to property tests with invariants (schemas always valid)
- [ ] Convert integration test outputs to snapshot tests
- [ ] Document usage patterns in test files for future reference
- [ ] NO pytest-bdd, NO Gherkin, NO BDD methodology (use TDD with hypothesis for properties)

**Technical Requirements**:

- Apply hypothesis for property-based testing to:
  - Data validation: PeerRead dataset schemas, model serialization
  - Integration tests: API responses, trace data outputs
  - GUI tests: Session state updates, widget value bounds
- Apply inline-snapshot for regression testing to:
  - Integration test outputs: evaluation pipeline results, trace data structures
  - GUI rendering: Streamlit page component outputs
  - Benchmark results: performance metric structures
- Remove trivial tests per testing-strategy.md guidelines:
  - Field existence checks (Pydantic models already validate)
  - Simple getter/setter tests
  - Tests that duplicate type checker validation
- Maintain coverage thresholds (no reduction in coverage percentage)
- Document patterns for future test authoring

**Priority Test Areas** (from testing-strategy.md):

- **CRITICAL**: Data validation (PeerRead dataset schemas, trace data formats)
- **CRITICAL**: Integration test invariants (end-to-end evaluation flows)
- **HIGH**: GUI state management (session state persistence, provider selection)
- **HIGH**: Serialization (integration test result structures)
- **MEDIUM**: Benchmark output validation (performance metric consistency)

**Files**:

- `tests/app/test_evaluation_wiring.py` (snapshot for evaluation outputs)
- `tests/benchmarks/test_performance_baselines.py` (snapshot for benchmark results)
- `tests/data_utils/test_datasets_peerread.py` (property tests for schemas)
- `tests/evals/test_opik_metrics.py` (property tests for metric bounds)
- `tests/integration/test_enhanced_peerread_integration.py` (snapshot for integration outputs)
- `tests/integration/test_opik_integration.py` (snapshot for trace outputs)
- `tests/integration/test_peerread_integration.py` (property tests + snapshots)
- `tests/integration/test_peerread_real_dataset_validation.py` (property tests for real data)
- `tests/metrics/test_metrics_output_similarity.py` (property tests for similarity bounds)
- `tests/test_gui/test_agent_graph_page.py` (snapshot for GUI components)
- `tests/test_gui/test_evaluation_page.py` (snapshot for GUI outputs)
- `tests/test_gui/test_sidebar_phoenix.py` (snapshot for sidebar structure)

---

#### Feature 5: CC Trace Adapter

**Description**: Parse Claude Code artifacts into `GraphTraceData` format in two modes so CC runs can be evaluated through the same three-tier pipeline used for PydanticAI MAS runs. Both modes assume CC has full internal tool, plugin, and MCP access (the same capabilities as the PydanticAI agents).

- **Solo mode**: Parse a CC session export directory containing conversation history and tool-call logs from a single CC instance (no orchestration). Produces a single-agent `GraphTraceData` with `tool_calls` and `timing_data` but minimal `agent_interactions` and no `coordination_events`.
- **Teams mode**: Parse CC Agent Teams artifacts (`~/.claude/teams/`, `~/.claude/tasks/`) from a multi-agent CC run with delegation. Produces a multi-agent `GraphTraceData` with full `agent_interactions`, `tool_calls`, `timing_data`, and `coordination_events`.

**Acceptance Criteria**:

- [ ] Output `GraphTraceData` instance passes existing Tier 3 graph analysis without modification in both modes
- [ ] Auto-detect mode from directory structure (presence of `config.json` with `members` array indicates teams; otherwise solo)
- [ ] Graceful error handling when CC artifact directories are missing or malformed
- [ ] Tests: Hypothesis property tests for data mapping invariants (all fields populated, timestamps ordered) in both modes
- [ ] Tests: inline-snapshot for `GraphTraceData` output structure from sample CC artifacts (one solo, one teams)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

##### 5.1 Teams Mode

**Acceptance Criteria**:

- [ ] Adapter reads CC team config from `config.json` and extracts `execution_id` from team name
- [ ] Adapter parses `inboxes/*.json` messages into `agent_interactions` list
- [ ] Adapter parses `tasks/*.json` completions into `tool_calls` list (task completions as proxy)
- [ ] Adapter derives `timing_data` from first/last timestamps across all artifacts
- [ ] Adapter extracts `coordination_events` from task assignments and blocked-by relationships

##### 5.2 Solo Mode

**Acceptance Criteria**:

- [ ] Adapter reads CC session export directory and extracts `execution_id` from session metadata
- [ ] Adapter parses tool-call entries from session logs into `tool_calls` list
- [ ] Adapter derives `timing_data` from session start/end timestamps
- [ ] `agent_interactions` is empty or contains only user-agent exchanges
- [ ] `coordination_events` is empty (single agent, no delegation)

**Technical Requirements**:

- Create `CCTraceAdapter` class that accepts a CC artifacts directory path and auto-detects mode
- **Teams mode** data mapping from CC artifacts to `GraphTraceData`:

  | GraphTraceData field | CC source | Mapping |
  | --- | --- | --- |
  | `execution_id` | `config.json` team name | Direct |
  | `agent_interactions` | `inboxes/*.json` messages | `{"from": sender, "to": recipient, "type": msg_type, "timestamp": ts}` |
  | `tool_calls` | `tasks/*.json` completions | `{"agent_id": owner, "tool_name": subject, "success": completed, "duration": derived}` |
  | `timing_data` | First/last timestamps | `{"start_time": min, "end_time": max, "total_duration": delta}` |
  | `coordination_events` | `tasks/*.json` assignments + blocks | `{"coordination_type": "task_delegation", "manager_agent": lead, "target_agents": [owner]}` |

- **Solo mode** data mapping:

  | GraphTraceData field | CC source | Mapping |
  | --- | --- | --- |
  | `execution_id` | Session directory name or metadata | Direct |
  | `agent_interactions` | None (single agent) | Empty list |
  | `tool_calls` | Session tool-call log entries | `{"agent_id": "cc-solo", "tool_name": tool_name, "success": bool, "duration": derived}` |
  | `timing_data` | Session start/end timestamps | `{"start_time": min, "end_time": max, "total_duration": delta}` |
  | `coordination_events` | None (single agent) | Empty list |

- Post-hoc parsing of CC artifacts (not live OTel) -- CC Agent Teams do not store tool-level traces, so task completions serve as proxy for `tool_calls` in teams mode
- Validate parsed data against existing `GraphTraceData` Pydantic model
- Return empty/default `GraphTraceData` when artifacts directory is invalid (log warning, do not raise)

**Files**:

- `src/app/judge/cc_trace_adapter.py` (new)
- `tests/judge/test_cc_trace_adapter.py` (new)

---

#### Feature 6: Baseline Comparison Engine

**Description**: New `BaselineComparison` Pydantic model and comparison logic to diff `CompositeResult` instances across three systems: PydanticAI MAS, CC solo (no orchestration), and CC teams (with orchestration). The pairwise `compare()` function diffs any two `CompositeResult` instances; a `compare_all()` convenience function produces all three pairwise comparisons at once. Reuses existing `CompositeResult` model and `CompositeScorer.extract_metric_values()`.

**Acceptance Criteria**:

- [ ] `BaselineComparison` Pydantic model with fields: `label_a`, `label_b`, `result_a`, `result_b`, `metric_deltas`, `tier_deltas`, `summary`
- [ ] `compare(result_a, result_b, label_a, label_b)` accepts two `CompositeResult` instances and returns `BaselineComparison`
- [ ] `compare_all(pydantic_result, cc_solo_result, cc_teams_result)` returns list of 3 `BaselineComparison` (PydanticAI vs CC-solo, PydanticAI vs CC-teams, CC-solo vs CC-teams)
- [ ] `compare_all()` accepts `None` for any result and skips comparisons involving that result
- [ ] `metric_deltas` contains per-metric delta for all 6 composite metrics
- [ ] `tier_deltas` contains tier-level score differences (Tier 1, Tier 2, Tier 3)
- [ ] `summary` is a human-readable comparison string (e.g., "PydanticAI scored +0.12 higher on technical_accuracy vs CC-solo")
- [ ] Handles missing tiers gracefully (one system has Tier 2, other does not)
- [ ] Tests: Hypothesis property tests for delta symmetry (swap inputs -> negated deltas)
- [ ] Tests: inline-snapshot for `BaselineComparison` model dump structure
- [ ] Tests: inline-snapshot for `compare_all()` output with one None result
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Create `BaselineComparison` Pydantic model:
  - `label_a: str` -- human label for first system (e.g., "PydanticAI MAS")
  - `label_b: str` -- human label for second system (e.g., "CC-solo")
  - `result_a: CompositeResult` -- first system evaluation
  - `result_b: CompositeResult` -- second system evaluation
  - `metric_deltas: dict[str, float]` -- per-metric delta (6 composite metrics)
  - `tier_deltas: dict[str, float]` -- tier-level score differences
  - `summary: str` -- human-readable comparison
- Create `compare(result_a: CompositeResult, result_b: CompositeResult, label_a: str, label_b: str) -> BaselineComparison` function
- Create `compare_all(pydantic_result: CompositeResult | None, cc_solo_result: CompositeResult | None, cc_teams_result: CompositeResult | None) -> list[BaselineComparison]` convenience function
- Reuse `CompositeScorer.extract_metric_values()` (`src/app/judge/composite_scorer.py:164`) to extract per-metric values from each result
- Compute deltas as `value_a - value_b` for each metric
- Generate summary string listing metrics where delta exceeds 0.05 threshold

**Files**:

- `src/app/judge/baseline_comparison.py` (new)
- `src/app/data_models/evaluation_models.py` (add `BaselineComparison` model)
- `tests/judge/test_baseline_comparison.py` (new)

---

#### Feature 7: CLI & GUI Baseline Integration

**Description**: Wire the CC trace adapter and baseline comparison engine into the existing CLI and GUI so users can run side-by-side evaluations. Supports two CC baseline modes: solo (single CC instance, no orchestration) and teams (CC Agent Teams with delegation). Both modes assume CC had full internal tool, plugin, and MCP access during the run being evaluated.

**Acceptance Criteria**:

- [ ] CLI: `--cc-solo-dir PATH` flag accepts path to CC solo session export directory
- [ ] CLI: `--cc-teams-dir PATH` flag accepts path to CC Agent Teams artifacts directory
- [ ] CLI: Both flags can be provided together for three-way comparison (PydanticAI vs CC-solo vs CC-teams)
- [ ] CLI: Adapter auto-detects mode per directory; flags override auto-detection
- [ ] CLI: Baseline comparison(s) printed to console after standard evaluation output
- [ ] GUI: Baseline comparison view on evaluation results page (side-by-side metrics display)
- [ ] GUI: Separate directory inputs for CC solo and CC teams artifacts
- [ ] GUI: Three-way comparison table when both CC baselines are provided
- [ ] Both CLI and GUI skip baseline comparison when no CC artifacts provided (no regression)
- [ ] Tests: inline-snapshot for CLI output with single baseline and three-way comparison
- [ ] Tests: Hypothesis property tests for GUI state management with baseline data
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- CLI: Add `--cc-solo-dir` and `--cc-teams-dir` arguments to CLI entry point
- CLI: For each provided directory, call `CCTraceAdapter(path).parse()` to get CC `GraphTraceData`, then run through `evaluate_comprehensive()` pipeline
- CLI: Call `compare_all()` with available results (pass `None` for missing baselines) and print each `BaselineComparison.summary`
- GUI: Add baseline section to evaluation results page using existing Streamlit patterns
- GUI: Display `metric_deltas` as side-by-side bar chart and `summary` as text for each pairwise comparison
- All traces go through the same evaluation pipeline (`evaluate_comprehensive()`)
- Reuse existing GUI evaluation page patterns (`src/gui/pages/evaluation.py`)

**Files**:

- `src/app/app.py` (add `--cc-solo-dir` and `--cc-teams-dir` CLI flags)
- `src/gui/pages/evaluation.py` (add baseline comparison view)
- `tests/app/test_cli_baseline.py` (new)
- `tests/test_gui/test_evaluation_baseline.py` (new)

---

## Non-Functional Requirements

- **Maintainability:**
  - Use modular design patterns for easy updates and maintenance.
  - Implement logging and error handling for debugging and monitoring.
  - Graceful degradation when external services unavailable.
- **Performance:**
  - Timeout mechanisms must not introduce significant latency overhead.
  - Thread-safe implementations should minimize thread pool creation overhead.
  - CC trace adapter must parse typical team artifacts (< 50 files) in under 2 seconds.
- **Documentation:**
  - Comprehensive troubleshooting guide for common operational issues.
  - Docstrings for all new functions and classes (Google style format).
- **Testing:**
  - All new features must include tests per `docs/best-practices/testing-strategy.md`
  - Use **Hypothesis** (`@given`) for property-based tests: timeout bounds, retry behavior, score fallbacks, data mapping invariants, delta symmetry
  - Use **inline-snapshot** (`snapshot()`) for regression tests: warning messages, error result structures, trace adapter output, comparison model dumps
  - Use **pytest** for standard unit/integration tests with Arrange-Act-Assert structure
  - Tool selection: pytest for **logic**, Hypothesis for **properties**, inline-snapshot for **structure**

## Out of Scope

- Opik service auto-start on GUI launch (user must manually run `make start_opik`)
- Custom OTLP exporter implementation (use standard OpenTelemetry libraries)
- Tier 3 graph analysis performance optimization (timeout mechanism only)
- Alternative tracing backends (Phoenix/Logfire only)
- Persistent retry queues for failed trace exports (in-memory only)
- Gemini provider compatibility (`agent_system.py:610` FIXME -- deferred to future sprint)
- HuggingFace provider implementation (deferred to future sprint)
- Streaming with Pydantic model outputs (`agent_system.py:522` -- deferred to future sprint)
- CC OpenTelemetry live telemetry (post-hoc artifact parsing only)
- OTel Collector Docker deployment for CC traces
- CC native span creation or instrumentation
- A2A (Agent-to-Agent) protocol integration
- Provisioning CC tool/plugin/MCP access (assumed pre-configured by the user before the CC run)

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Sprint 4 (7 stories total):

- **Feature 1 (Logfire Export)** → STORY-001: Graceful Logfire trace export failures
- **Feature 2 (Graph Timeout)** → STORY-002: Thread-safe graph analysis timeout handling
- **Feature 3 (Judge Fallback Validation)** → STORY-003: Tier 2 judge provider fallback validation
- **Feature 4 (Complete Test Alignment)** → STORY-004: Complete test suite alignment with hypothesis and inline-snapshot
- **Feature 5 (CC Trace Adapter)** → STORY-005: CC trace adapter for solo and teams artifacts
- **Feature 6 (Baseline Comparison)** → STORY-006: Baseline comparison engine for CompositeResult diffing
- **Feature 7 (CLI & GUI Baseline)** → STORY-007: CLI and GUI baseline integration (depends: STORY-002, STORY-005, STORY-006)
