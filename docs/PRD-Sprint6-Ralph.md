---
title: Product Requirements Document: Agents-eval Sprint 6
version: 1.0.0
created: 2026-02-16
updated: 2026-02-16
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 5 delivered runtime fixes, GUI enhancements, architectural improvements, code quality review (OWASP MAESTRO), and test suite audit across 17 stories.

Sprint 6 focuses on **benchmarking infrastructure**, **baseline completion**, and **tool access refinement** across 7 stories:

1. **Cleanup (Features 1-2)**: Remove Opik entirely, fix Phoenix Docker recipe
2. **Benchmarking (Features 3-4)**: Complete CC baseline end-to-end, build MAS composition sweep
3. **Tool Access (Features 5-6)**: Conditional review tool placement, enable review tools by default
4. **GUI Fix (Feature 7)**: Fix empty Agent Interaction Graph tab

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop enforces this order.**

### TDD Workflow (Mandatory for all features)

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality.
3. **REFACTOR**: Clean up while keeping tests green. Run `make validate` before marking complete.

### Test Tool Selection (per `docs/best-practices/testing-strategy.md`)

| Tool | Use for | NOT for |
|------|---------|---------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation.

### Core Principles (per `.claude/rules/core-principles.md`)

- **KISS**: Simplest solution that passes tests. Clear > clever.
- **DRY**: Reuse existing patterns (`CompositeResult`, `EvaluationPipeline`, `CCTraceAdapter`). Don't rebuild.
- **YAGNI**: Implement only what acceptance criteria require. No speculative features.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (1-7) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Codebase research | `researching-codebase` (before implementation) |

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Remove Opik Entirely

**Description**: Remove all Opik-related code, configuration, Docker infrastructure, Makefile targets, documentation, and tests from the project. Opik was replaced by Logfire + Phoenix in Sprint 4. Deprecated stubs (`opik_instrumentation.py`, `OpikConfig`) and the full Docker stack (`docker-compose.opik.yaml`, 11 services) remain as dead code. This cleanup removes ~800 lines of unused code and configuration.

**Acceptance Criteria**:

- [ ] `src/app/agents/opik_instrumentation.py` deleted
- [ ] `OpikConfig` class removed from `src/app/utils/load_configs.py`
- [ ] `docker-compose.opik.yaml` deleted
- [ ] Makefile targets removed: `setup_opik`, `setup_opik_env`, `start_opik`, `stop_opik`, `clean_opik`, `status_opik`
- [ ] `.env.example` Opik variables removed (`OPIK_URL_OVERRIDE`, `OPIK_WORKSPACE`, `OPIK_PROJECT_NAME`)
- [ ] `.gitignore` Opik entries removed (`opik/`, `.opik_install_reported`)
- [ ] `docs/howtos/opik-setup-usage-integration.md` deleted
- [ ] Stale Opik docstrings in `src/app/judge/graph_analysis.py` (lines 423, 506) updated to reference Phoenix
- [ ] Test stubs deleted: `tests/evals/test_opik_removal.py`, `tests/integration/test_opik_integration.py`, `tests/evals/test_opik_metrics.py`
- [ ] `CONTRIBUTING.md` Opik references removed (make commands, setup instructions)
- [ ] No remaining imports or references to `opik` in `src/app/` (verified via grep)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Delete files: `src/app/agents/opik_instrumentation.py`, `docker-compose.opik.yaml`, `docs/howtos/opik-setup-usage-integration.md`
- Delete test files: `tests/evals/test_opik_removal.py`, `tests/integration/test_opik_integration.py`, `tests/evals/test_opik_metrics.py`
- In `src/app/utils/load_configs.py`: delete `OpikConfig` class (lines 63-93), keep `LogfireConfig`
- In `Makefile`: delete lines 308-359 (all opik targets), remove `setup_opik` from `setup_devc_full` and `setup_devc_ollama_full`
- In `src/app/judge/graph_analysis.py`: replace "Opik integration" references with "Phoenix" in docstrings at lines 423 and 506
- In `.env.example`: remove lines 22-24 (Opik env vars)
- In `.gitignore`: remove `opik/` and `.opik_install_reported` entries
- In `CONTRIBUTING.md`: remove Opik make commands from command reference table and setup instructions
- Verify cleanup: `grep -ri opik src/app/` returns no matches

**Files**:

- `src/app/agents/opik_instrumentation.py` (delete)
- `src/app/utils/load_configs.py` (edit)
- `src/app/judge/graph_analysis.py` (edit)
- `docker-compose.opik.yaml` (delete)
- `Makefile` (edit)
- `.env.example` (edit)
- `.gitignore` (edit)
- `CONTRIBUTING.md` (edit)
- `docs/howtos/opik-setup-usage-integration.md` (delete)
- `tests/evals/test_opik_removal.py` (delete)
- `tests/integration/test_opik_integration.py` (delete)
- `tests/evals/test_opik_metrics.py` (delete)

---

#### Feature 2: Fix Phoenix Docker Recipe

**Description**: The current `make start_phoenix` recipe has three problems: (1) no volume mount — trace data is lost on `docker rm`, (2) missing gRPC port 4317 — only HTTP OTLP on 6006 is exposed, (3) no restart policy — container dies on devcontainer restart (exit code 255) and doesn't come back. Additionally, `make start_phoenix` fails with "container name already in use" when a stopped container exists. Fix all four issues.

**Acceptance Criteria**:

- [ ] `make start_phoenix` persists trace data across container restarts via Docker volume `phoenix_data`
- [ ] Both OTLP endpoints exposed: HTTP on port 6006, gRPC on port 4317
- [ ] Container auto-restarts after devcontainer restart (`--restart unless-stopped`)
- [ ] `make start_phoenix` succeeds even when a stopped `phoenix-tracing` container exists (removes old container first)
- [ ] `make stop_phoenix` stops container but preserves volume data
- [ ] `make status_phoenix` shows container status and both port mappings
- [ ] Phoenix UI accessible at `http://localhost:6006` after `make start_phoenix`
- [ ] OTLP traces received on both `http://localhost:6006/v1/traces` (HTTP) and `localhost:4317` (gRPC)
- [ ] Logfire SDK (`logfire_instrumentation.py`) continues to export traces successfully via HTTP endpoint
- [ ] Tests: pytest test for Makefile recipe validation (recipe contains required flags)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Update `start_phoenix` recipe in `Makefile`:
  ```makefile
  start_phoenix:
  	docker rm -f $(PHOENIX_CONTAINER_NAME) 2>/dev/null || true
  	docker run -d --name $(PHOENIX_CONTAINER_NAME) \
  		--restart unless-stopped \
  		-p $(PHOENIX_PORT):$(PHOENIX_PORT) \
  		-p 4317:4317 \
  		-v phoenix_data:/mnt/data \
  		-e PHOENIX_WORKING_DIR=/mnt/data \
  		$(PHOENIX_IMAGE)
  ```
- Update `stop_phoenix` to only stop (not remove) so volume persists
- Update `status_phoenix` to show both port mappings
- Add `PHOENIX_GRPC_PORT := 4317` variable alongside existing `PHOENIX_PORT`
- Phoenix does NOT support `/v1/metrics` — keep `OTEL_METRICS_EXPORTER=none` in `logfire_instrumentation.py:70` as-is

**Files**:

- `Makefile`

---

#### Feature 3: Complete CC Baseline End-to-End

**Description**: The CC baseline infrastructure (trace adapter, comparison engine, CLI wiring) was built in Sprint 4 but has never been validated against real Claude Code artifacts. Four gaps prevent end-to-end operation: (1) teams mode path mismatch — adapter expects `tasks/` as child of teams dir, but CC stores tasks at `~/.claude/tasks/{team-name}/` (sibling), (2) no artifact collection scripts — CC doesn't natively export in the adapter-expected format, (3) paper/review extraction is placeholder — `evaluation_runner.py` passes empty strings, making Tier 1 scores meaningless, (4) orphaned `src/app/cc_otel/` module that is never called and solves the wrong problem (application-level instrumentation vs infrastructure-level env vars).

##### 3.1 Fix CCTraceAdapter Path Handling

**Acceptance Criteria**:

- [ ] Teams mode adapter accepts separate `teams_dir` and `tasks_dir` parameters (or auto-discovers `tasks/` as sibling)
- [ ] Adapter works with real `~/.claude/teams/{name}/` + `~/.claude/tasks/{name}/` directory layout
- [ ] Backward compatible: still works if `tasks/` is a subdirectory of teams dir
- [ ] CLI `--cc-teams-dir` accepts teams directory; tasks directory auto-discovered or specified separately
- [ ] Tests: pytest tests with both directory layouts (sibling and child)
- [ ] `make validate` passes

**Files**:

- `src/app/judge/cc_trace_adapter.py`
- `tests/judge/test_cc_trace_adapter.py`
- `src/run_cli.py` (add `--cc-teams-tasks-dir` optional flag)

##### 3.2 Create CC Artifact Collection Scripts

**Acceptance Criteria**:

- [ ] `scripts/collect-cc-solo.sh` captures CC solo session data into adapter-expected format (`metadata.json` + `tool_calls.jsonl`)
- [ ] `scripts/collect-cc-teams.sh` copies `~/.claude/teams/{name}/` + `~/.claude/tasks/{name}/` into single adapter-compatible directory
- [ ] Both scripts accept team/session name as argument
- [ ] Both scripts validate output directory structure matches adapter expectations
- [ ] README in `scripts/` documents usage

**Files**:

- `scripts/collect-cc-solo.sh` (new)
- `scripts/collect-cc-teams.sh` (new)

##### 3.3 Wire Paper and Review Extraction

**Acceptance Criteria**:

- [ ] `evaluation_runner.py` extracts actual paper content and generated review from manager run result
- [ ] Tier 1 metrics (text similarity) produce meaningful scores instead of near-zero from empty strings
- [ ] CC baseline evaluations receive the same paper content for fair comparison
- [ ] Tests: pytest test verifying non-empty paper/review passed to pipeline
- [ ] `make validate` passes

**Files**:

- `src/app/judge/evaluation_runner.py`
- `src/app/app.py`

##### 3.4 Delete Orphaned cc_otel Module

**Acceptance Criteria**:

- [ ] `src/app/cc_otel/` directory deleted (including `__init__.py`, `config.py`)
- [ ] `tests/cc_otel/` directory deleted (including `test_cc_otel_config.py`, `test_cc_otel_instrumentation.py`)
- [ ] No remaining imports of `app.cc_otel` in codebase
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Files**:

- `src/app/cc_otel/` (delete entire directory)
- `tests/cc_otel/` (delete entire directory)

---

#### Feature 4: MAS Composition Sweep Infrastructure

**Description**: Build automated benchmarking infrastructure to run the PydanticAI MAS evaluation pipeline across all agent composition variations (8 combinations of researcher/analyst/synthesiser toggles) and optionally include pre-collected CC baseline artifacts. Each composition runs multiple repetitions on the same paper(s) for statistical significance. Results are aggregated with mean/stddev per metric per composition and output as both JSON (machine-readable) and Markdown (human-readable).

**Acceptance Criteria**:

- [ ] `SweepConfig` Pydantic model defines: compositions, repetitions, paper_numbers, output_dir, cc artifact paths
- [ ] Sweep runner executes N repetitions x M compositions x P papers through existing `main()` pipeline
- [ ] Each run produces a `CompositeResult` stored in structured JSON output
- [ ] If CC artifact directories provided, CC baselines evaluated and included in comparison
- [ ] Analysis module calculates per-composition statistics: mean, stddev, min, max for all 6 composite metrics
- [ ] Markdown summary table generated with compositions as rows, metrics as columns, mean +/- stddev values
- [ ] CLI entry point: `python src/run_sweep.py --config sweep_config.json` or `python src/run_sweep.py --paper-numbers 1,2,3 --repetitions 3`
- [ ] `make sweep` Makefile target wrapping CLI with sensible defaults
- [ ] Sweep results saved to `results/sweeps/{timestamp}/` with `results.json` + `summary.md`
- [ ] Reuses existing `EvaluationPipeline`, `CompositeScorer`, `baseline_comparison.compare()` — no new evaluation logic
- [ ] Tests: pytest tests for sweep config validation, composition generation, results aggregation
- [ ] Tests: Hypothesis property tests for statistical calculations (mean/stddev bounds)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- `src/app/benchmark/sweep_config.py` (~50 lines): `SweepConfig` Pydantic model
  - `compositions: list[dict[str, bool]]` — defaults to all 8 combinations via `generate_all_compositions()`
  - `repetitions: int = 3` — runs per composition per paper
  - `paper_numbers: list[str]` — PeerRead paper IDs
  - `chat_provider: str` — provider for all runs
  - `cc_solo_dir: Path | None` — pre-collected CC solo artifacts
  - `cc_teams_dir: Path | None` — pre-collected CC teams artifacts
  - `output_dir: Path = Path("results/sweeps")`
- `src/app/benchmark/sweep_runner.py` (~150 lines): orchestration loop
  - `run_sweep(config: SweepConfig) -> SweepResults` — main entry
  - Calls `main()` from `app.py` for each composition x paper x repetition
  - Collects `CompositeResult` per run
  - Evaluates CC artifacts once (same result across compositions)
- `src/app/benchmark/sweep_analysis.py` (~100 lines): statistics and reporting
  - `analyze(results: SweepResults) -> SweepSummary` — per-composition stats
  - `generate_markdown_report(summary: SweepSummary) -> str` — table output
- `src/run_sweep.py` (~50 lines): CLI argument parsing, loads config, calls runner
- `Makefile`: add `sweep` target

**Files**:

- `src/app/benchmark/__init__.py` (new)
- `src/app/benchmark/sweep_config.py` (new)
- `src/app/benchmark/sweep_runner.py` (new)
- `src/app/benchmark/sweep_analysis.py` (new)
- `src/run_sweep.py` (new)
- `Makefile` (edit)
- `tests/benchmark/test_sweep_config.py` (new)
- `tests/benchmark/test_sweep_analysis.py` (new)

---

#### Feature 5: Review Tools Conditional Access

**Description**: Sprint 5 STORY-016 moved PeerRead base tools from manager to researcher. However, review tools (`generate_paper_review_content_from_template`, `save_paper_review`, `save_structured_review`) are still added unconditionally to the manager via `conditionally_add_review_tools()`. When a researcher agent is present, review tools should be placed on the researcher (alongside base PeerRead tools and DuckDuckGo). When no researcher is present (single-agent mode), review tools should fall back to the manager so single-agent review generation continues to work.

**Acceptance Criteria**:

- [ ] When `include_researcher=True`: review tools registered on researcher agent, not manager
- [ ] When `include_researcher=False`: review tools registered on manager agent (single-agent fallback)
- [ ] Manager retains only delegation tools (`researcher()`, `analyst()`, `synthesiser()`) in multi-agent mode
- [ ] Researcher has: PeerRead base tools + review tools + `duckduckgo_search_tool()` in multi-agent mode
- [ ] Single-agent mode produces correct review output (no regression)
- [ ] Multi-agent mode delegates PeerRead + review operations to researcher (verified via trace data)
- [ ] Tests: pytest tests for tool registration (which agent has which tools) in both modes
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `src/app/agents/agent_system.py`:
  - `conditionally_add_review_tools()` (line 462): add `researcher` parameter
  - When `researcher is not None` and `enable=True`: add review tools to researcher
  - When `researcher is None` and `enable=True`: add review tools to manager (fallback)
  - Pass `researcher` from `get_manager()` scope into `conditionally_add_review_tools()`
- In `src/app/tools/peerread_tools.py`:
  - Rename `add_peerread_review_tools_to_manager()` to `add_peerread_review_tools()` (agent-agnostic name)
  - Function signature already accepts `Agent[None, BaseModel]` — no parameter change needed

**Files**:

- `src/app/agents/agent_system.py`
- `src/app/tools/peerread_tools.py`
- `tests/agents/test_agent_system.py` (update)

---

#### Feature 6: Enable Review Tools by Default

**Description**: Review tools (`--enable-review-tools`) currently default to `False`, requiring explicit opt-in for review generation. Since the primary use case of this project is PeerRead paper review evaluation, review tools should be enabled by default. Users who want to run general queries without review tools can opt out via `--no-review-tools`.

**Acceptance Criteria**:

- [ ] `enable_review_tools` defaults to `True` in `main()` signature (`app.py`)
- [ ] CLI: `--no-review-tools` flag disables review tools (replaces opt-in with opt-out)
- [ ] CLI: `--enable-review-tools` flag kept for backward compatibility (no-op since default is True)
- [ ] GUI: Review tools checkbox in settings defaults to checked
- [ ] Auto-enable logic from `_prepare_query()` still works (no regression when `--paper-number` provided)
- [ ] Tests: pytest tests for default-on behavior and opt-out flag
- [ ] Tests: inline-snapshot for CLI help text showing new flag
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `src/app/app.py:203`: change `enable_review_tools: bool = False` to `enable_review_tools: bool = True`
- In `src/run_cli.py`: add `--no-review-tools` flag that sets `enable_review_tools=False`
- Keep `--enable-review-tools` for backward compatibility (already True by default, becomes no-op)
- In `src/app/app.py:94`: adjust OR logic — `_prepare_query()` auto-enable no longer needed since default is True, but keep for explicitness

**Files**:

- `src/app/app.py`
- `src/run_cli.py`
- `tests/app/test_cli_baseline.py` (update)

---

#### Feature 7: Fix Agent Interaction Graph in GUI

**Description**: The "Agent Interaction Graph" tab in the Streamlit GUI shows "No agent interaction data available" even when a NetworkX graph has been created from trace data. The root cause is that graph building is coupled to evaluation success: `app.py:267` only builds the graph when `composite_result` is not None. If evaluation is skipped (`--skip-eval`) or fails, no graph is rendered despite trace data being available. The graph should be built whenever trace data exists, independent of evaluation outcome.

**Acceptance Criteria**:

- [ ] Agent Interaction Graph renders when trace data exists, regardless of evaluation success/failure
- [ ] Graph renders correctly after `--skip-eval` runs (evaluation skipped but traces collected)
- [ ] Graph renders correctly after failed evaluation (Tier 2 provider unavailable, etc.)
- [ ] Graph shows agent nodes, tool nodes, and delegation edges from `GraphTraceData`
- [ ] Empty graph state only shown when no trace data exists (no execution has run)
- [ ] Existing evaluation flow unchanged (graph still available when evaluation succeeds)
- [ ] Tests: pytest test verifying graph built from trace data without evaluation
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `src/app/app.py:267`: decouple graph building from `composite_result`
  - Current: `graph = _build_graph_from_trace(execution_id) if composite_result else None`
  - Fix: `graph = _build_graph_from_trace(execution_id)` (always attempt when execution_id exists)
- In `src/app/judge/evaluation_runner.py:23-47`: `build_graph_from_trace()` already handles None execution_id and missing traces gracefully — no changes needed
- Verify `src/gui/pages/agent_graph.py` renders correctly when graph has nodes but no evaluation result
- Verify `src/gui/pages/run_app.py:197` stores graph in session state correctly

**Files**:

- `src/app/app.py`
- `tests/app/test_app.py` (update)

---

## Non-Functional Requirements

- All sweep runs must complete within provider rate limits (no concurrent API calls within a single sweep iteration)
- Phoenix Docker container must survive devcontainer restarts without trace data loss
- Sweep results must be deterministic given same paper content and provider (modulo LLM non-determinism)
- No new pip dependencies — reuse existing `networkx`, `pydantic`, `arize-phoenix`, `logfire`

## Out of Scope

- Automated CC run triggering (CC sessions remain manual; only artifact collection and evaluation are automated)
- CC OTel env var configuration in `.claude/settings.json` (infrastructure-level, not application code)
- Phoenix cloud deployment or authentication setup
- Sweep visualization dashboard (Markdown tables are sufficient for Sprint 6)
- Heterogeneous model support in sweep (all agents use same LLM per composition)
- GUI integration for sweep (CLI-only for Sprint 6)

---

## Notes for Ralph Loop

**Priority Order:**

- **P0 (Quick Wins)**: STORY-001 (Opik removal), STORY-002 (Phoenix recipe), STORY-007 (graph fix)
- **P1 (CC Baseline)**: STORY-003 (CC baseline completion)
- **P2 (Tool Access)**: STORY-005 (conditional access), STORY-006 (default enabled)
- **P3 (Benchmarking)**: STORY-004 (sweep infrastructure)

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (7 stories total):

- **Feature 1 (Remove Opik)** → STORY-001: Remove all Opik code, config, Docker, docs, and tests
- **Feature 2 (Phoenix Recipe)** → STORY-002: Fix Phoenix Docker recipe with volume, ports, restart policy
- **Feature 3 (CC Baseline)** → STORY-003: Complete CC baseline end-to-end (adapter fix, collection scripts, paper extraction, delete cc_otel) (depends: STORY-001)
- **Feature 4 (Composition Sweep)** → STORY-004: Build MAS composition sweep infrastructure with statistical analysis (depends: STORY-003)
- **Feature 5 (Review Tools Conditional)** → STORY-005: Move review tools to researcher when present, manager when single-agent
- **Feature 6 (Review Tools Default)** → STORY-006: Enable review tools by default with opt-out flag (depends: STORY-005)
- **Feature 7 (Agent Graph Fix)** → STORY-007: Fix empty Agent Interaction Graph in GUI by decoupling from evaluation
