---
title: Product Requirements Document: Agents-eval Sprint 6
description: Benchmarking infrastructure, CC baseline completion, tool access refinement, security hardening (CVE mitigations, input sanitization, log scrubbing), and test quality improvements for the Agents-eval MAS evaluation framework.
version: 1.2.0
created: 2026-02-16
updated: 2026-02-16
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 5 delivered runtime fixes, GUI enhancements, architectural improvements, code quality review (OWASP MAESTRO), and test suite audit across 17 stories.

Sprint 6 focuses on **benchmarking infrastructure**, **baseline completion**, **tool access refinement**, **security hardening**, and **test quality** across 15 stories:

1. **Cleanup (Features 1-2, 6)**: Remove Opik entirely, fix Phoenix Docker recipe, delete orphaned cc_otel module
2. **CC Baseline (Features 3-5)**: Fix adapter path handling, create collection scripts, wire paper extraction
3. **Benchmarking (Feature 7)**: Build MAS composition sweep infrastructure
4. **Tool Access (Features 8-9)**: Conditional review tool placement, enable review tools by default
5. **Security Hardening (Features 10-13)**: CVE mitigations, prompt input sanitization, log/trace scrubbing, security test suite
6. **Test Quality (Features 14-15)**: Increase coverage on critical modules, execute test audit refactoring
7. **Quick Win (bundled with Feature 2)**: Fix empty Agent Interaction Graph (one-line change)

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop enforces this order.**

### TDD Workflow (Mandatory for all features)

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality.
3. **REFACTOR**: Clean up while keeping tests green. Run `make validate` before marking complete.

### Test Tool Selection

| Tool | Use for | NOT for |
|------|---------|---------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation.

### Mandatory Practices

- **Mock external dependencies** (HTTP, LLM providers, file systems, subprocess) using `@patch`. Never call real APIs in unit tests.
- **Test behavior, not implementation** — test observable outcomes (return values, side effects, error messages), not internal structure (isinstance checks, property existence, default constants).
- **Google-style docstrings** for every new file, function, class, and method. Auto-generated documentation depends on this.
- **`# Reason:` comments** for non-obvious logic (e.g., regex patterns, XML delimiter choices, fallback order).

### Core Principles

- **KISS**: Simplest solution that passes tests. Clear > clever.
- **DRY**: Reuse existing patterns (`CompositeResult`, `EvaluationPipeline`, `CCTraceAdapter`). Don't rebuild.
- **YAGNI**: Implement only what acceptance criteria require. No speculative features.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (1-12, 14) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Security tests (13) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Test refactoring (15) | `testing-python` (for validation after deletions) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |

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
- [ ] Test stubs deleted: `tests/integration/test_opik_integration.py`, `tests/evals/test_opik_metrics.py`
- [ ] `CONTRIBUTING.md` Opik references removed (make commands, setup instructions)
- [ ] No remaining imports or references to `opik` in `src/app/` (verified via grep)
- [ ] `docs/analysis/CC-agent-teams-orchestration.md` all Opik references (13 occurrences, verified via grep) updated to reflect Phoenix/Logfire
- [ ] Keep `load_configs.py` with `LogfireConfig` intact (4 active consumers: `agent_system.py`, `logfire_instrumentation.py`, and 2 test files)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Delete files: `src/app/agents/opik_instrumentation.py`, `docker-compose.opik.yaml`, `docs/howtos/opik-setup-usage-integration.md`
- Delete test files: `tests/integration/test_opik_integration.py`, `tests/evals/test_opik_metrics.py`
- In `src/app/utils/load_configs.py`: delete `OpikConfig` class (the DEPRECATED class), keep `LogfireConfig`
- In `Makefile`: delete all opik targets (`setup_opik`, `setup_opik_env`, `start_opik`, `stop_opik`, `clean_opik`, `status_opik`), remove `setup_opik` from `setup_devc_full` and `setup_devc_ollama_full`
- In `.env.example`: remove Opik env vars (`OPIK_URL_OVERRIDE`, `OPIK_WORKSPACE`, `OPIK_PROJECT_NAME`)
- In `.gitignore`: remove `opik/` and `.opik_install_reported` entries
- In `CONTRIBUTING.md`: remove Opik make commands from command reference table and setup instructions
- Verify cleanup: `grep -ri opik src/app/` returns no matches

**Files**:

- `src/app/agents/opik_instrumentation.py` (delete)
- `src/app/utils/load_configs.py` (edit — remove OpikConfig, keep LogfireConfig)
- `docker-compose.opik.yaml` (delete)
- `Makefile` (edit)
- `.env.example` (edit)
- `.gitignore` (edit)
- `CONTRIBUTING.md` (edit)
- `docs/howtos/opik-setup-usage-integration.md` (delete)
- `tests/integration/test_opik_integration.py` (delete)
- `tests/evals/test_opik_metrics.py` (delete)
- `docs/analysis/CC-agent-teams-orchestration.md` (edit — update 13 Opik references)

---

#### Feature 2: Fix Phoenix Docker Recipe + Agent Graph Fix (P0 Quick Win Bundle)

**Description**: The current `make start_phoenix` recipe has three problems: (1) no volume mount — trace data is lost on `docker rm`, (2) missing gRPC port 4317 — only HTTP OTLP on 6006 is exposed, (3) no restart policy — container dies on devcontainer restart (exit code 255) and doesn't come back. Additionally, `make start_phoenix` fails with "container name already in use" when a stopped container exists. Fix all four issues.

**Bundled Quick Win**: The Agent Interaction Graph tab in the GUI shows "No agent interaction data available" even when trace data exists because graph building is coupled to evaluation success (`app.py:267` only builds graph when `composite_result` is not None). Fix: change conditional graph building to unconditional when `execution_id` exists (one-line change).

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
- [ ] **Quick Win**: Agent Interaction Graph renders when trace data exists, regardless of evaluation success (change `app.py:267` from conditional to unconditional)
- [ ] **Quick Win**: Graph renders correctly after `--skip-eval` runs and after failed evaluation
- [ ] Tests: pytest test verifying `_build_graph_from_trace()` is called when `execution_id` exists and `composite_result` is None
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

- `Makefile` (edit)
- `src/app/app.py` (edit — quick win graph fix at line 267)
- `tests/infra/test_makefile_recipes.py` (new — Makefile recipe validation)
- `tests/app/test_app.py` (update — graph fix behavior test; mock `_build_graph_from_trace`)

---

#### Feature 3: Fix CCTraceAdapter Path Handling

**Description**: The CC baseline infrastructure was built in Sprint 4 but has a teams mode path mismatch — adapter expects `tasks/` as child of teams dir, but CC stores tasks at `~/.claude/tasks/{team-name}/` (sibling of `~/.claude/teams/`). Fix the adapter to support both layouts.

**Acceptance Criteria**:

- [ ] Teams mode adapter accepts separate `teams_dir` and `tasks_dir` parameters (or auto-discovers `tasks/` as sibling)
- [ ] Adapter works with real `~/.claude/teams/{name}/` + `~/.claude/tasks/{name}/` directory layout
- [ ] Backward compatible: still works if `tasks/` is a subdirectory of teams dir
- [ ] CLI `--cc-teams-dir` accepts teams directory; tasks directory auto-discovered or specified separately
- [ ] Tests: pytest tests with both directory layouts (sibling and child)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `CCTraceAdapter.__init__()`: accept optional `tasks_dir: Path | None` parameter alongside existing `teams_dir`
- When `tasks_dir` is None: auto-discover by checking `teams_dir.parent / "tasks" / teams_dir.name` (sibling layout), then `teams_dir / "tasks"` (child layout)
- In `src/run_cli.py`: add `--cc-teams-tasks-dir` optional flag that maps to `tasks_dir` parameter
- Preserve existing behavior when `tasks/` is a child directory (backward compatible)

**Files**:

- `src/app/judge/cc_trace_adapter.py` (edit)
- `tests/judge/test_cc_trace_adapter.py` (update)
- `src/run_cli.py` (edit — add `--cc-teams-tasks-dir` optional flag)

---

#### Feature 4: Create CC Artifact Collection Scripts

**Description**: CC doesn't natively export artifacts in the format expected by `CCTraceAdapter`. Create bash scripts to collect solo session and teams mode artifacts into adapter-compatible directory structures.

**Acceptance Criteria**:

- [ ] `scripts/collect-cc-solo.sh` captures CC solo session data into adapter-expected format (`metadata.json` + `tool_calls.jsonl`)
- [ ] `scripts/collect-cc-teams.sh` copies `~/.claude/teams/{name}/` + `~/.claude/tasks/{name}/` into single adapter-compatible directory
- [ ] Both scripts accept named parameters: `--name <session/team-name>` and `--output-dir <path>` (required)
- [ ] Both scripts validate output directory structure matches adapter expectations
- [ ] Exit code 0 on success, exit code 1 on validation failure (missing source dirs, malformed artifacts), exit code 2 on usage error (missing required params)
- [ ] README in `scripts/` documents usage, examples, and exit codes
- [ ] Tests: pytest tests invoking scripts via `subprocess.run()`, verifying exit codes and output directory structure
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- `scripts/collect-cc-solo.sh`: parse `--name` and `--output-dir` args, locate CC session data in `~/.claude/projects/` or user-specified path, create `metadata.json` (session name, timestamp, model) and `tool_calls.jsonl` (one JSON object per tool call) in output dir
- `scripts/collect-cc-teams.sh`: parse `--name` and `--output-dir` args, copy `~/.claude/teams/{name}/config.json` and `~/.claude/tasks/{name}/*.json` into output dir preserving structure
- Both scripts: validate output structure matches `CCTraceAdapter` expectations (required files exist, valid JSON), exit 1 on validation failure, exit 2 on usage error
- Use `set -euo pipefail` for strict error handling in both scripts

**Files**:

- `scripts/collect-cc-solo.sh` (new)
- `scripts/collect-cc-teams.sh` (new)
- `scripts/README.md` (new)
- `tests/scripts/test_collect_cc_scripts.py` (new)

---

#### Feature 5: Wire Paper and Review Extraction

**Description**: `evaluation_runner.py:101-106` passes empty strings for `paper=""` and `review=""` to `evaluate_comprehensive()`, making Tier 1 text similarity scores meaningless (near-zero). The manager run result contains both paper ID and generated review, but `run_manager()` only returns the `execution_id` string — discarding `result.output`. Fix: return the result object alongside execution_id, extract the review text and paper content, and pass them to the evaluation pipeline.

**Acceptance Criteria**:

- [ ] `run_manager()` returns both `execution_id` and the manager result output (change return type from `str` to `tuple[str, Any]`)
- [ ] `evaluation_runner.py` receives `ReviewGenerationResult.review.comments` as the generated review text
- [ ] Paper content loaded via `PeerReadLoader.load_parsed_pdf_content(paper_id)` using `ReviewGenerationResult.paper_id`
- [ ] Fallback: if parsed PDF unavailable, use `PeerReadPaper.abstract` as paper content
- [ ] Tier 1 metrics (cosine, jaccard, semantic similarity) produce non-zero scores with real content
- [ ] CC baseline evaluations receive the same paper content (loaded by paper_id) for fair comparison
- [ ] When review tools are disabled (no `ReviewGenerationResult`), gracefully pass empty strings (current behavior preserved)
- [ ] Tests: pytest test verifying non-empty paper/review passed to pipeline
- [ ] Tests: pytest test for fallback when parsed PDF is unavailable
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- In `agent_system.py:510`: change `run_manager()` return from `str` to `tuple[str, Any]`, return `(execution_id, result.output)`
- In `app.py:112`: destructure return: `execution_id, manager_output = await run_manager(...)`
- In `app.py:256`: pass `manager_output` to `_run_evaluation_if_enabled()`
- In `evaluation_runner.py:101-106`: extract fields:
  - `review_text = manager_output.review.comments` (from `ReviewGenerationResult`)
  - `paper_id = manager_output.paper_id`
  - `paper_content = PeerReadLoader(...).load_parsed_pdf_content(paper_id)` with abstract fallback
- Pass extracted strings to `pipeline.evaluate_comprehensive(paper=paper_content, review=review_text, ...)`
- Mock strategy: mock `run_manager()` return value, mock `PeerReadLoader.load_parsed_pdf_content()` for unit tests

**Files**:

- `src/app/agents/agent_system.py` (change `run_manager()` return type)
- `src/app/app.py` (destructure return, pass to evaluation)
- `src/app/judge/evaluation_runner.py` (extract content from result)
- `tests/judge/test_evaluation_runner.py` (update)

---

#### Feature 6: Delete Orphaned cc_otel Module

**Description**: `src/app/cc_otel/` is an orphaned module containing `CCOtelConfig` — a Pydantic settings model for configuring Claude Code's OpenTelemetry environment variables from Python. This approach is fundamentally wrong: CC tracing is configured via infrastructure-level env vars (set in shell or `.claude/settings.json`), not application code. The module has no consumers — no imports of `app.cc_otel` exist anywhere in the codebase. The correct approach for CC baseline comparison is headless invocation via `claude -p` (Feature 7) with post-hoc artifact collection. This is independent of Opik removal (Feature 1) — cc_otel was for Claude Code OTel configuration, not Opik.

**Acceptance Criteria**:

- [ ] `src/app/cc_otel/` directory deleted (including `__init__.py`, `config.py`)
- [ ] `tests/cc_otel/` directory deleted (including `test_cc_otel_config.py`, `test_cc_otel_instrumentation.py`)
- [ ] No remaining imports of `app.cc_otel` in codebase (verified via grep)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Delete `src/app/cc_otel/` directory entirely (2 files: `__init__.py`, `config.py`)
- Delete `tests/cc_otel/` directory entirely (2 files: `test_cc_otel_config.py`, `test_cc_otel_instrumentation.py`)
- Verify cleanup: `grep -ri cc_otel src/app/` and `grep -ri cc_otel tests/` return no matches

**Files**:

- `src/app/cc_otel/` (delete entire directory)
- `tests/cc_otel/` (delete entire directory)

---

#### Feature 7: MAS Composition Sweep Infrastructure

**Description**: Build automated benchmarking infrastructure to run the PydanticAI MAS evaluation pipeline across configurable agent composition variations and optionally invoke Claude Code in headless mode (`claude -p`) for CC baseline comparison. The default composition set is all 8 combinations of `include_researcher` / `include_analyst` / `include_synthesiser` toggles (2^3 = 8), but both the number of compositions and the agent toggles within each composition are configurable. Each composition runs a configurable number of repetitions on the same paper(s) for statistical significance. Results are aggregated with mean/stddev per metric per composition and output as both JSON (machine-readable) and Markdown (human-readable).

**Acceptance Criteria**:

- [ ] `SweepConfig` Pydantic model defines: compositions (variable length), repetitions, paper_numbers, output_dir, cc options
- [ ] Compositions are configurable: user can specify any subset of agent toggle combinations, not hardcoded to 8
- [ ] Default `generate_all_compositions()` produces all 2^3 = 8 combinations as a convenience
- [ ] Sweep runner executes N repetitions x M compositions x P papers through existing `main()` pipeline
- [ ] Each run produces a `CompositeResult` stored in structured JSON output
- [ ] If `cc_baseline_enabled=True`: sweep invokes `claude -p` in headless mode with the same paper review prompt used by the MAS, collects artifacts, and evaluates via `CCTraceAdapter`
- [ ] CC headless invocation uses `--output-format json` for structured parsing of results
- [ ] When `cc_baseline_enabled=True` and `claude` CLI not found (`shutil.which("claude")` returns None), sweep exits with clear error message
- [ ] If pre-collected CC artifact directories provided instead, those are evaluated without re-running CC
- [ ] Analysis module calculates per-composition statistics: mean, stddev, min, max for all 6 composite metrics
- [ ] Markdown summary table generated with compositions as rows, metrics as columns, mean +/- stddev values
- [ ] CLI entry point: `python src/run_sweep.py --config sweep_config.json` or `python src/run_sweep.py --paper-numbers 1,2,3 --repetitions 3`
- [ ] `make sweep` Makefile target wrapping CLI with sensible defaults
- [ ] Sweep results saved to `results/sweeps/{timestamp}/` with `results.json` + `summary.md`
- [ ] `.gitignore` includes `results/sweeps/` to prevent committing large JSON result files
- [ ] Reuses existing `EvaluationPipeline`, `CompositeScorer`, `baseline_comparison.compare()` — no new evaluation logic
- [ ] Tests: pytest tests for sweep config validation, composition generation, results aggregation, runner error handling
- [ ] Tests: pytest tests for sweep runner (mock `main()` and `subprocess.run()`, verify result collection and CC invocation)
- [ ] Tests: Hypothesis property tests for statistical calculations (mean/stddev bounds)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- `src/app/benchmark/sweep_config.py` (~70 lines): `SweepConfig` Pydantic model
  - `compositions: list[AgentComposition]` — defaults to all 8 combinations via `generate_all_compositions()`
  - `AgentComposition` model: `{"include_researcher": bool, "include_analyst": bool, "include_synthesiser": bool}`
  - `repetitions: int = 3` — runs per composition per paper
  - `paper_numbers: list[str]` — PeerRead paper IDs
  - `chat_provider: str` — provider for all MAS runs
  - `cc_baseline_enabled: bool = False` — when True, invoke CC headless per paper
  - `cc_solo_dir: Path | None` — pre-collected CC solo artifacts (alternative to live CC runs)
  - `cc_teams_dir: Path | None` — pre-collected CC teams artifacts
  - `output_dir: Path = Path("results/sweeps")`
  - `generate_all_compositions() -> list[AgentComposition]` — produces all 2^3 = 8 toggle combinations
- `src/app/benchmark/sweep_runner.py` (~180 lines): orchestration loop
  - `run_sweep(config: SweepConfig) -> SweepResults` — main entry
  - Calls `main()` from `app.py` for each composition x paper x repetition
  - Collects `CompositeResult` per run
  - When `cc_baseline_enabled`: invokes `claude -p "Generate a structured peer review for paper '{paper_number}'" --output-format json` via `subprocess.run()`, collects output to temp dir, parses via `CCTraceAdapter`
  - When pre-collected CC artifact dirs provided: evaluates once (same result across compositions)
- `src/app/benchmark/sweep_analysis.py` (~100 lines): statistics and reporting
  - `analyze(results: SweepResults) -> SweepSummary` — per-composition stats
  - `generate_markdown_report(summary: SweepSummary) -> str` — table output
- `src/run_sweep.py` (~50 lines): CLI argument parsing, loads config, calls runner
- `Makefile`: add `sweep` target
- `CONTRIBUTING.md`: add `make sweep` to command reference table
- Mock strategy: mock `app.main()` to return synthetic `CompositeResult`, mock `subprocess.run()` for CC headless invocation, mock filesystem for output dir creation

**Files**:

- `src/app/benchmark/__init__.py` (new)
- `src/app/benchmark/sweep_config.py` (new)
- `src/app/benchmark/sweep_runner.py` (new)
- `src/app/benchmark/sweep_analysis.py` (new)
- `src/run_sweep.py` (new)
- `Makefile` (edit)
- `.gitignore` (edit - add results/sweeps/)
- `CONTRIBUTING.md` (edit — add `make sweep` to command reference table)
- `tests/benchmark/test_sweep_config.py` (new)
- `tests/benchmark/test_sweep_runner.py` (new — mock `main()` and `subprocess.run()`)
- `tests/benchmark/test_sweep_analysis.py` (new)

---

#### Feature 8: Review Tools Conditional Access

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
- Mock strategy: mock PydanticAI `Agent` to verify tool registration lists without LLM calls

**Files**:

- `src/app/agents/agent_system.py`
- `src/app/tools/peerread_tools.py`
- `tests/agents/test_agent_system.py` (update)

---

#### Feature 9: Enable Review Tools by Default

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

#### Feature 10: CVE Mitigations (SSRF URL Allowlist)

**Description**: The Sprint 5 MAESTRO security review (Finding CVE-1, `docs/reviews/sprint5-code-review.md`) identified CVE-2026-25580, a CRITICAL PydanticAI SSRF vulnerability allowing information disclosure via malicious URLs in message history. Agent tools that process URLs (PeerRead dataset downloads, DuckDuckGo search) need domain-allowlist validation to prevent SSRF attacks against internal services. CVE-2026-25640 (Stored XSS in PydanticAI web UI) does not affect this project since we don't use `clai web` or `Agent.to_web()` — document this as a known advisory. CVE-2024-5206 (scikit-learn) is already mitigated by `scikit-learn>=1.8.0` in `pyproject.toml`.

**Acceptance Criteria**:

- [ ] `validate_url()` function enforces HTTPS-only and domain allowlist for all external requests
- [ ] Allowlist includes: `raw.githubusercontent.com`, `arxiv.org`, `api.openai.com`, `api.anthropic.com`, `api.cerebras.ai`
- [ ] PeerRead dataset download URLs validated before `httpx.Client.get()` in `datasets_peerread.py`
- [ ] URLs in agent tool responses validated before any HTTP requests
- [ ] Blocked URLs raise `ValueError` with domain name (no URL echoing to prevent log injection)
- [ ] CVE-2026-25640 documented in `SECURITY.md` advisory section (project does not use affected features)
- [ ] Tests: pytest tests for URL validation (allowed domains, blocked domains, non-HTTPS, internal IPs)
- [ ] Tests: Hypothesis property tests for URL parsing edge cases (unicode domains, IP addresses, port variations)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Create `src/app/utils/url_validation.py` (~30 lines):

  ```python
  ALLOWED_DOMAINS = frozenset({
      "raw.githubusercontent.com", "arxiv.org",
      "api.openai.com", "api.anthropic.com", "api.cerebras.ai",
  })

  def validate_url(url: str) -> str:
      parsed = urlparse(url)
      if parsed.scheme != "https":
          raise ValueError("Only HTTPS URLs allowed")
      if parsed.netloc not in ALLOWED_DOMAINS:
          raise ValueError(f"URL domain not allowed: {parsed.netloc}")
      return url
  ```

- In `datasets_peerread.py`: call `validate_url()` before `client.get(url)` in download functions
- Create `SECURITY.md` with known advisory for CVE-2026-25640 (XSS — not applicable) and CVE-2026-25580 (SSRF — mitigated by URL allowlist)

**Files**:

- `src/app/utils/url_validation.py` (new)
- `src/app/data_utils/datasets_peerread.py` (edit — add URL validation before downloads)
- `SECURITY.md` (new — known advisories)
- `tests/utils/test_url_validation.py` (new)

---

#### Feature 11: LLM Prompt Input Sanitization

**Description**: The Sprint 5 MAESTRO review (Finding L1.1, HIGH) and parallel pipeline review (Item 1, CRITICAL) both identified unsanitized user input flowing into LLM prompts. `llm_evaluation_managers.py:177-188` interpolates `paper_excerpt` and `review` via f-strings. `peerread_tools.py:295` uses `.format()` with `paper_title` and `paper_abstract` from the PeerRead dataset. Malicious paper content could inject prompt instructions or trigger unintended LLM behavior. Add length-limited structured inputs and XML delimiter wrapping.

**Acceptance Criteria**:

- [ ] Paper titles truncated to 500 chars, abstracts to 5000 chars, review text to 50000 chars before prompt insertion
- [ ] User-controlled content wrapped in XML delimiters (`<paper_content>...</paper_content>`) in LLM judge prompts to separate instructions from data
- [ ] `peerread_tools.py` template formatting uses `string.Template.safe_substitute()` instead of `str.format()` to prevent format string injection
- [ ] Truncation happens at the sanitization boundary (before prompt construction), not ad-hoc per call site
- [ ] Existing prompt behavior unchanged for well-formed inputs (no regression in evaluation quality)
- [ ] Tests: pytest tests for truncation at boundary lengths
- [ ] Tests: pytest tests for format string injection attempts (e.g., `{__import__}` in paper title)
- [ ] Tests: Hypothesis property tests — for all strings, output length <= max_length + delimiter overhead, and output always contains XML delimiters
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Create `src/app/utils/prompt_sanitization.py` (~40 lines):
  - `sanitize_for_prompt(text: str, max_length: int, label: str) -> str` — truncates and wraps in `<{label}>...</{label}>`
  - `sanitize_paper_title(title: str) -> str` — max 500 chars
  - `sanitize_paper_abstract(abstract: str) -> str` — max 5000 chars
  - `sanitize_review_text(review: str) -> str` — max 50000 chars
- In `llm_evaluation_managers.py:177-188`: replace raw f-string interpolation with sanitized inputs
- In `peerread_tools.py:295`: replace `.format()` with `string.Template.safe_substitute()`
- Sanitization module is reusable for any future LLM prompt construction

**Files**:

- `src/app/utils/prompt_sanitization.py` (new)
- `src/app/judge/llm_evaluation_managers.py` (edit — use sanitized inputs in prompts)
- `src/app/tools/peerread_tools.py` (edit — use safe_substitute for template formatting)
- `tests/utils/test_prompt_sanitization.py` (new)

---

#### Feature 12: Log and Trace Data Scrubbing

**Description**: The Sprint 5 MAESTRO review identified three related data leakage risks: (1) no Logfire scrubbing patterns configured (Finding L4.2, HIGH), so trace data exported to Phoenix contains unredacted API keys and user content; (2) no Loguru log filtering (Finding L4.1, MEDIUM), so exception traces may contain local variables with API key values; (3) `setup_llm_environment()` in `providers.py:80` logs env var names at INFO level. Add scrubbing patterns to both Logfire (trace export) and Loguru (file/console logging).

**Acceptance Criteria**:

- [ ] Logfire configured with scrubbing patterns for: `password`, `passwd`, `secret`, `auth`, `credential`, `api[._-]?key`, `token`, `jwt`
- [ ] Loguru file sink filters sensitive patterns from log messages before writing
- [ ] `setup_llm_environment()` logs at DEBUG level instead of INFO (reduces exposure surface)
- [ ] Exception traces from Loguru do not contain raw API key values (local variable scrubbing)
- [ ] Trace data exported to Phoenix via OTLP has sensitive fields redacted
- [ ] Existing logging behavior preserved for non-sensitive messages (no over-scrubbing)
- [ ] Tests: pytest tests for Loguru filter (sensitive patterns redacted, normal messages pass through)
- [ ] Tests: pytest tests for Logfire scrubbing configuration (patterns applied)
- [ ] Tests: Hypothesis property tests — for all messages containing any SENSITIVE_PATTERNS match, output contains `[REDACTED]`
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Create `src/app/utils/log_scrubbing.py` (~40 lines):
  - `SENSITIVE_PATTERNS: list[str]` — shared pattern list for both Loguru and Logfire
  - `scrub_log_record(record: dict) -> dict` — Loguru filter function
  - `get_logfire_scrubbing_patterns() -> list[str]` — returns patterns for Logfire configuration
- In `src/app/utils/log.py`: add `filter=scrub_log_record` to the Loguru file sink
- In `src/app/common/log.py`: consolidate with `utils/log.py` — replace duplicate loguru config with re-export: `from app.utils.log import logger` (DRY fix — both files are near-identical, but only `utils/log.py` will have scrubbing)
- In `src/app/agents/logfire_instrumentation.py`: pass `scrubbing_patterns` to `logfire.configure()`
- In `src/app/llms/providers.py:80`: change `logger.info(f"Set environment variable: {env_var}")` to `logger.debug(...)`

**Files**:

- `src/app/utils/log_scrubbing.py` (new)
- `src/app/utils/log.py` (edit — add scrubbing filter to file sink)
- `src/app/common/log.py` (edit — replace with re-export from `utils/log.py`)
- `src/app/agents/logfire_instrumentation.py` (edit — configure Logfire scrubbing patterns)
- `src/app/llms/providers.py` (edit — downgrade log level for env var setup)
- `tests/utils/test_log_scrubbing.py` (new)

---

#### Feature 13: Security Test Suite

**Description**: The Sprint 5 MAESTRO review (Recommendations, Priority 4) explicitly tagged "Add comprehensive security test suite" for Sprint 6. Zero security-focused tests currently exist. Create `tests/security/` with tests validating the security controls added by Features 10-12 and testing additional attack vectors identified in the review: plugin input size limits, tool registration scope, and prompt injection scenarios.

**Acceptance Criteria**:

- [ ] `tests/security/test_ssrf_prevention.py` — SSRF attack vectors: internal IPs blocked, non-HTTPS blocked, AWS metadata endpoint, localhost, IDN homograph attacks
- [ ] `tests/security/test_prompt_injection.py` — injection attempts in paper titles/abstracts rejected or sanitized
- [ ] `tests/security/test_sensitive_data_filtering.py` — API key patterns filtered from logs and traces, Bearer tokens redacted
- [ ] `tests/security/test_input_size_limits.py` — oversized inputs to plugin adapters rejected (DoS prevention)
- [ ] `tests/security/test_tool_registration.py` — tools only registered from expected modules (no runtime injection)
- [ ] All security tests use pytest with clear arrange/act/assert structure
- [ ] Hypothesis property tests for input boundary fuzzing (oversized strings, unicode edge cases)
- [ ] Security tests run as part of `make test_all` (no separate security test suite command needed)
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Create `tests/security/__init__.py`
- Create `tests/security/test_ssrf_prevention.py` — test `validate_url()` from Feature 10 with: allowed domains, blocked domains, HTTP (non-HTTPS), `169.254.169.254` (AWS metadata), `localhost`, `0.0.0.0`, unicode domain IDN homograph attacks
- Create `tests/security/test_prompt_injection.py` — test `sanitize_for_prompt()` from Feature 11 with: `"Ignore previous instructions"` payloads, format string attempts (`{__import__}`), oversized inputs, null bytes
- Create `tests/security/test_sensitive_data_filtering.py` — test `scrub_log_record()` from Feature 12 with: messages containing `api_key=sk-...`, `password=secret`, `Bearer token` patterns
- Create `tests/security/test_input_size_limits.py` — test plugin `evaluate()` with oversized `agent_output` (>100KB) and `reference_texts` (>10 items)
- Create `tests/security/test_tool_registration.py` — verify agent tool lists match expected registrations per agent role

**Files**:

- `tests/security/__init__.py` (new)
- `tests/security/test_ssrf_prevention.py` (new)
- `tests/security/test_prompt_injection.py` (new)
- `tests/security/test_sensitive_data_filtering.py` (new)
- `tests/security/test_input_size_limits.py` (new)
- `tests/security/test_tool_registration.py` (new)

---

#### Feature 14: Increase Coverage for Critical Modules

**Description**: The Sprint 5 MAESTRO review (Recommendations, Priority 5) identified five modules with critically low test coverage that handle core data loading, agent tools, and orchestration. These modules have high regression risk and are frequently modified across sprints. Add targeted behavioral tests to increase coverage before the test audit (Feature 15) removes low-value tests elsewhere.

**Acceptance Criteria**:

- [ ] `datasets_peerread.py`: 27% -> 60% — tests for download error handling, URL construction, paper validation with missing fields, retry logic
- [ ] `peerread_tools.py`: 22% -> 60% — tests for tool registration, PDF extraction error handling, content truncation, template loading
- [ ] `llms/models.py`: 24% -> 50% — tests for model creation with different providers, error handling for unsupported models
- [ ] `agent_factories.py`: 39% -> 60% — tests for agent creation with various toggle combinations, system prompt construction
- [ ] `agent_system.py`: 47% -> 60% — tests for delegation flow, usage limit enforcement, single-agent fallback
- [ ] All new tests verify behavior (error handling, data flow, edge cases), not implementation details
- [ ] Coverage measured via `make coverage_all` before and after
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Tests go in existing test directories (mirror `src/app/` structure):
  - `tests/data_utils/test_datasets_peerread.py` (update — add download error, validation tests)
  - `tests/agents/test_peerread_tools.py` (update — add PDF extraction, truncation tests)
  - `tests/llms/test_models.py` (new or update — model creation tests)
  - `tests/agents/test_agent_factories.py` (new or update — agent creation tests)
  - `tests/agents/test_agent_system.py` (update — delegation and limit tests)
- Mock external dependencies (HTTP, file system, LLM providers) — test logic, not network
- Use Hypothesis for property tests on data validation (arbitrary missing fields, boundary values)

**Files**:

- `tests/data_utils/test_datasets_peerread.py` (update)
- `tests/agents/test_peerread_tools.py` (update)
- `tests/llms/test_models.py` (new or update)
- `tests/agents/test_agent_factories.py` (new or update)
- `tests/agents/test_agent_system.py` (update)

---

#### Feature 15: Execute Test Audit Refactoring

**Description**: Sprint 5 STORY-011 produced `docs/reviews/sprint5-test-audit.md` — a detailed per-file audit with explicit keep/delete/refactor decisions for all test files. The audit was completed but the actual refactoring (deleting ~55 implementation-detail tests from 9 files) was not executed. This story executes the audit plan. Note: `test_migration_cleanup.py` is already deleted, and `tests/cc_otel/` is deleted by Feature 6 (cc_otel removal).

**Acceptance Criteria**:

- [ ] `tests/evals/test_judge_settings.py`: `TestJudgeSettingsDefaults` class deleted (13 tests verifying default constants)
- [ ] `tests/common/test_common_settings.py`: 2 implementation-detail tests deleted (`test_common_settings_defaults`, `test_common_settings_type_validation`)
- [ ] `tests/utils/test_logfire_config.py`: 3 tests deleted (`test_logfire_config_from_settings_defaults`, `test_logfire_config_direct_instantiation`, `test_logfire_config_type_validation`)
- [ ] `tests/judge/test_plugin_base.py`: `TestEvaluatorPluginABC` class deleted (4 property-existence tests)
- [ ] `tests/judge/test_trace_store.py`: basic CRUD and metadata-tracking tests deleted (tests dict-like behavior assumed by Python)
- [ ] `tests/judge/test_plugin_llm_judge.py`: 3 tests deleted (isinstance check, name property, tier property)
- [ ] `tests/judge/test_plugin_traditional.py`: 3 tests deleted (isinstance check, name property, tier property)
- [ ] `tests/judge/test_plugin_graph.py`: 3 tests deleted (isinstance check, name property, tier property)
- [ ] `tests/evals/test_graph_analysis.py`: review for field-existence or type-check tests; delete any found (skip if none exist)
- [ ] No reduction in behavioral test coverage — only implementation-detail tests removed
- [ ] `make test_all` passes with all remaining tests green
- [ ] `make validate` passes
- [ ] CHANGELOG.md updated

**Technical Requirements**:

- Follow execution plan in `docs/reviews/sprint5-test-audit.md` exactly (Phase 2: Delete Implementation-Detail Tests)
- Delete tests by removing specific test functions or classes, not entire files (files contain mix of keep and delete tests)
- Run `make test_all` after each file modification to catch regressions immediately
- Expected net reduction: ~55 tests from 9 files

**Files**:

- `tests/evals/test_judge_settings.py` (edit)
- `tests/common/test_common_settings.py` (edit)
- `tests/utils/test_logfire_config.py` (edit)
- `tests/judge/test_plugin_base.py` (edit)
- `tests/judge/test_trace_store.py` (edit)
- `tests/judge/test_plugin_llm_judge.py` (edit)
- `tests/judge/test_plugin_traditional.py` (edit)
- `tests/judge/test_plugin_graph.py` (edit)
- `tests/evals/test_graph_analysis.py` (edit — if applicable)

---

## Non-Functional Requirements

- All sweep runs must complete within provider rate limits (no concurrent API calls within a single sweep iteration)
- Phoenix Docker container must survive devcontainer restarts without trace data loss
- Sweep results must be deterministic given same paper content and provider (modulo LLM non-determinism)
- No new pip dependencies — reuse existing `networkx`, `pydantic`, `arize-phoenix`, `logfire`

## Out of Scope

- CC Agent Teams mode invocation from sweep (only CC solo headless mode via `claude -p`; teams requires manual setup)
- CC OTel env var configuration in `.claude/settings.json` (infrastructure-level, not application code)
- Phoenix cloud deployment or authentication setup
- Sweep visualization dashboard (Markdown tables are sufficient for Sprint 6)
- Heterogeneous model support in sweep (all agents use same LLM per composition)
- GUI integration for sweep (CLI-only for Sprint 6)
- Centralized tool registry with module allowlist (architecture improvement — Sprint 7+, per MAESTRO review L7.2)
- Plugin tier validation at registration (prevents tier mismatch — Sprint 7+, per MAESTRO review L7.1)
- Immutable trace storage / audit trail signing (low priority — Sprint 7+, per MAESTRO review L4.3)
- Complete docstring coverage for `llms/` and `data_utils/` modules (Sprint 7+, per MAESTRO review CQ.1)
- Removing API keys from `os.environ` entirely (PydanticAI requires env vars for provider auth — would need upstream changes)
- Performance bottleneck remediation automation (auto-adjusting timeouts from historical data — Sprint 7+, per parallel review Item 3)
- Additional evaluation fallback strategies beyond `tier1_only` (Sprint 7+, per parallel review Item 5)
- Error message sanitization / information leakage prevention (sanitize error metadata sizes — Sprint 7+, per parallel review Item 2)
- GraphTraceData construction simplification (replace manual `.get()` with `model_validate()` — Sprint 7+, per parallel review Item 8)
- Timeout bounds enforcement (min/max limits on user-configurable timeouts — Sprint 7+, per parallel review Item 9)
- Configuration path traversal protection (validate config paths against allowlist — Sprint 7+, per parallel review Item 10)
- BDD scenario tests for evaluation pipeline (end-to-end user workflow tests — Sprint 7+, per parallel review Item 12)
- Time tracking consistency across tiers (standardize timing pattern — Sprint 7+, per parallel review Item 7)

---

## Notes for Ralph Loop

**Priority Order:**

- **P0 (Quick Wins)**: STORY-001 (Opik removal), STORY-002 (Phoenix recipe + graph fix), STORY-006 (cc_otel deletion)
- **P1 (Security Hardening)**: STORY-010 (CVE mitigations), STORY-011 (input sanitization), STORY-012 (log scrubbing)
- **P1 (CC Baseline)**: STORY-003 (adapter paths), STORY-004 (collection scripts), STORY-005 (paper extraction)
- **P2 (Tool Access)**: STORY-008 (conditional access), STORY-009 (default enabled)
- **P2 (Test Quality)**: STORY-014 (coverage improvements), STORY-015 (audit execution)
- **P3 (Security Verification)**: STORY-013 (security test suite)
- **P3 (Benchmarking)**: STORY-007 (sweep infrastructure)

**Split Option for STORY-007:** If sweep implementation exceeds single-story scope, split into STORY-007a (config + runner) and STORY-007b (analysis + CLI + Makefile). Both remain P3.

**File Conflict Notes:**

- `peerread_tools.py`: touched by STORY-008 (review tools) and STORY-011 (input sanitization) — different functions, no code conflict, but avoid parallel execution
- `logfire_instrumentation.py`: touched by STORY-012 (log scrubbing) only — no conflict
- `agent_system.py`: touched by STORY-005 (paper extraction) and STORY-008 (review tools) — different functions, avoid parallel execution

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (15 stories total):

- **Feature 1 (Remove Opik)** → STORY-001: Remove all Opik code, config, Docker, docs, and tests
- **Feature 2 (Phoenix Recipe)** → STORY-002: Fix Phoenix Docker recipe with volume, ports, restart policy + Agent graph fix (one-line change bundled as P0 quick win)
- **Feature 3 (CC Adapter Paths)** → STORY-003: Fix CCTraceAdapter path handling for sibling teams/tasks directories
- **Feature 4 (CC Collection Scripts)** → STORY-004: Create CC artifact collection scripts (depends: STORY-003)
- **Feature 5 (Paper Extraction)** → STORY-005: Wire paper and review extraction in evaluation runner
- **Feature 6 (Delete cc_otel)** → STORY-006: Delete orphaned cc_otel module (independent of Opik)
- **Feature 7 (Composition Sweep)** → STORY-007: Build MAS composition sweep infrastructure with statistical analysis (depends: STORY-003, STORY-004, STORY-005)
- **Feature 8 (Review Tools Conditional)** → STORY-008: Move review tools to researcher when present, manager when single-agent (note: shares `agent_system.py` with STORY-005 — different functions, no dependency, but avoid parallel execution)
- **Feature 9 (Review Tools Default)** → STORY-009: Enable review tools by default with opt-out flag (depends: STORY-008)
- **Feature 10 (CVE Mitigations)** → STORY-010: Add SSRF URL allowlist and document known CVE advisories
- **Feature 11 (Input Sanitization)** → STORY-011: Add prompt input sanitization with length limits and XML delimiters (note: shares `peerread_tools.py` with STORY-008 — different functions, avoid parallel execution)
- **Feature 12 (Log Scrubbing)** → STORY-012: Configure Logfire scrubbing patterns and Loguru sensitive data filter
- **Feature 13 (Security Tests)** → STORY-013: Create security test suite in `tests/security/` (depends: STORY-010, STORY-011, STORY-012)
- **Feature 14 (Coverage Improvements)** → STORY-014: Increase test coverage for 5 critical low-coverage modules
- **Feature 15 (Test Audit Execution)** → STORY-015: Execute Sprint 5 test audit refactoring plan — delete ~55 implementation-detail tests (depends: STORY-014, STORY-006)
