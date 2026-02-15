---
title: Product Requirements Document: Agents-eval Sprint 2
version: 3.4.0
created: 2025-09-01
updated: 2026-02-12
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset for scientific paper review assessment. The system generates reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through a three-tier engine: Tier 1 (traditional text metrics), Tier 2 (LLM-as-Judge), and Tier 3 (graph analysis).

Sprint 2 focuses on connecting generation and evaluation: capturing real agent execution graphs, running evaluation automatically after review generation, and producing a comparative summary of graph-based coordination metrics vs conventional text similarity metrics. All evaluation tiers are fully implemented (157 tests); the gap is wiring them into the generation flow with real trace data.

---

## Functional Requirements

### Sprint 2: Graph vs Text Evaluation Pipeline

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Migrate EvaluationConfig to Pydantic Settings

**Description**: Replace JSON-based `EvaluationConfig` (`config_eval.json`) with `JudgeSettings(BaseSettings)` using `JUDGE_` env prefix. Defaults in code, overridable via `.env` or env vars. Follows same pattern as existing `CommonSettings` (`EVAL_` prefix).

**Acceptance Criteria**:

- [ ] `JudgeSettings(BaseSettings)` with `JUDGE_` env prefix replaces `EvaluationConfig`
- [ ] Typed defaults in code: tier weights, timeouts, model selection, enabled tiers
- [ ] `EvaluationPipeline` uses `JudgeSettings` instead of loading `config_eval.json`
- [ ] Existing evaluation tests pass with settings-based config
- [ ] Timeout fields use bounded validators (gt=0, le=300)
- [ ] Time tracking pattern standardized across all tiers
- [ ] Existing test fixtures updated: pipeline uses JudgeSettings, JSON fixtures removed
- [ ] `make validate` passes

**Technical Requirements**:

- Create `src/app/evals/settings.py` with `JudgeSettings(BaseSettings)` (model_config with `JUDGE_` prefix, `.env` file)
- Defaults mirror current `config_eval.json` values (tier1_max_seconds=1.0, tier2_max_seconds=10.0, etc.)
- Update `EvaluationPipeline.__init__()` to accept `JudgeSettings` instead of `config_path`
- Keep `config_eval.json` temporarily but it is no longer loaded at runtime
- Reuse pattern from `src/app/common/settings.py`

**Files**:

- `src/app/evals/settings.py` (new — `JudgeSettings`)
- `src/app/evals/evaluation_config.py` (deprecate, replace usages)
- `src/app/evals/evaluation_pipeline.py` (use `JudgeSettings`)
- `src/app/evals/composite_scorer.py` (use `JudgeSettings` for weights)

---

#### Feature 2: Wire Evaluation After Review Generation

**Description**: Connect `run_manager()` output to `EvaluationPipeline.evaluate_comprehensive()`. Add `--skip-eval` CLI flag.

**Acceptance Criteria**:

- [ ] After `run_manager()` completes, `EvaluationPipeline` runs automatically
- [ ] `--skip-eval` CLI flag disables evaluation
- [ ] Graceful skip when no ground-truth reviews available
- [ ] `make validate` passes

**Technical Requirements**:

- Import `EvaluationPipeline` in `app.py`, call after line 134
- Pipeline uses `JudgeSettings` from Feature 1
- Add `--skip-eval` to `parse_args()` in `run_cli.py`

**Files**:

- `src/app/app.py`
- `src/run_cli.py`

---

#### Feature 3: Capture GraphTraceData During MAS Execution

**Description**: Wire `TraceCollector` into agent orchestration so `GraphTraceData` is populated from real agent runs.

**Acceptance Criteria**:

- [ ] Agent-to-agent delegations logged via `trace_collector.log_agent_interaction()`
- [ ] Tool calls logged via `trace_collector.log_tool_call()`
- [ ] Timing data captured for each delegation step
- [ ] `GraphTraceData` passed to `evaluate_comprehensive()` with real data
- [ ] `GraphTraceData` constructed via `model_validate()` instead of manual `.get()` extraction
- [ ] `make validate` passes

**Technical Requirements**:

- Initialize `TraceCollector` in `run_manager()` or `setup_agent_env()`
- Instrument delegation calls in `agent_system.py`
- Pass populated `GraphTraceData` from `app.py` to pipeline

**Files**:

- `src/app/agents/agent_system.py`
- `src/app/agents/orchestration.py`
- `src/app/app.py`

---

#### Feature 4: Graph vs Text Metric Comparison Output

**Description**: Log comparative summary showing Tier 1 (text) vs Tier 3 (graph) scores after evaluation.

**Acceptance Criteria**:

- [ ] Log shows Tier 1 overall score vs Tier 3 overall score
- [ ] Individual graph metrics displayed (path_convergence, tool_selection_accuracy, communication_overhead, coordination_centrality, task_distribution_balance)
- [ ] Individual text metrics displayed (cosine_score, jaccard_score, semantic_score)
- [ ] Composite score shows per-tier contribution
- [ ] `make validate` passes

**Files**:

- `src/app/app.py`
- `src/app/evals/evaluation_pipeline.py` (optional enhancement)

---

#### Feature 4b: Migrate Opik to Logfire + Phoenix Local Tracing

**Description**: Replace Opik tracing integration (11 Docker containers, ~155s startup) with Logfire SDK + Arize Phoenix. `logfire.instrument_pydantic_ai()` auto-instruments all PydanticAI agents natively, eliminating manual `OpikInstrumentationManager`, `@track` decorators, and `get_opik_decorator()` wrappers. Phoenix receives traces via OTLP and provides a local web UI — all via `pip install` with zero Docker dependencies.

**Acceptance Criteria**:

- [ ] `pyproject.toml` replaces `opik>=1.8.0` with `arize-phoenix` and `openinference-instrumentation-pydantic-ai`
- [ ] `JudgeSettings` replaces `opik_*` fields with `logfire_enabled`, `logfire_send_to_cloud`, `phoenix_endpoint`, `logfire_service_name`
- [ ] `LogfireConfig` replaces `OpikConfig` in `load_configs.py`
- [ ] `logfire_instrumentation.py` replaces `opik_instrumentation.py` using `logfire.instrument_pydantic_ai()` auto-instrumentation
- [ ] `agent_system.py` removes manual `@opik_decorator` wrappers from delegation tools
- [ ] `evaluation_pipeline.py` removes Opik import block and `_apply_opik_decorator()`/`_record_opik_metadata()` methods
- [ ] `CommonSettings.enable_opik` renamed to `enable_logfire`
- [ ] Makefile adds `start_phoenix`, `stop_phoenix`, `status_phoenix` targets (Opik targets kept as legacy)
- [ ] `.env.example` replaces `OPIK_*` vars with `JUDGE_PHOENIX_*` / `JUDGE_LOGFIRE_*` vars
- [ ] `make validate` passes

**Technical Requirements**:

- Keep `docker-compose.opik.yaml` as optional legacy (not deleted)
- Keep `TraceCollector` (`trace_processors.py`) unchanged — independent local SQLite/JSONL system
- Logfire auto-instrumentation replaces all manual decorator wiring
- Graceful degradation when Phoenix is not running

**Files**:

- `pyproject.toml`
- `src/app/evals/settings.py`
- `src/app/utils/load_configs.py`
- `src/app/agents/opik_instrumentation.py` (delete)
- `src/app/agents/logfire_instrumentation.py` (new)
- `src/app/agents/agent_system.py`
- `src/app/evals/evaluation_pipeline.py`
- `src/app/common/settings.py`
- `.env.example`
- `Makefile`
- `tests/evals/test_judge_settings.py`
- `tests/common/test_common_settings.py`

---

#### Feature 4c: Streamlit Evaluation Dashboard + Agent Graph Visualization

**Description**: Add two new Streamlit pages: an Evaluation Results dashboard displaying Tier 1/2/3 scores with graph vs text metric comparison, and an Agent Graph page rendering the NetworkX delegation graph interactively via Pyvis. Phoenix (localhost:6006) is cross-linked from the sidebar for deep trace inspection.

**Acceptance Criteria**:

- [ ] "Evaluation Results" page displays Tier 1/2/3 scores from `CompositeResult`
- [ ] Bar chart compares graph metrics vs text metrics (Tier 1 vs Tier 3)
- [ ] Individual metric scores displayed in table format
- [ ] "Agent Graph" page renders `export_trace_to_networkx()` output as interactive Pyvis graph
- [ ] Agent nodes and tool nodes visually distinguished (color/shape)
- [ ] Sidebar includes Phoenix link with status indicator
- [ ] Pages render gracefully with empty/mock data when evaluation hasn't run
- [ ] `pyvis` added to gui dependency group in `pyproject.toml`
- [ ] `make validate` passes

**Technical Requirements**:

- Use `graph_analysis.export_trace_to_networkx()` (line 426) for graph data
- Use `CompositeResult` / `Tier1Result` / `Tier3Result` models for evaluation data
- Pyvis `Network.from_nx(graph)` → HTML → `st.components.v1.html()`
- Cross-link to Phoenix at `http://localhost:6006` (not embed)
- Follow existing GUI patterns in `src/gui/`

**Files**:

- `src/gui/pages/evaluation.py` (new)
- `src/gui/pages/agent_graph.py` (new)
- `src/gui/config/config.py` (add pages to PAGES list)
- `src/gui/components/sidebar.py` (add Phoenix link)
- `src/run_gui.py` (route new pages)
- `pyproject.toml` (add pyvis to gui group)

---

## Non-Functional Requirements

- **Maintainability:**
  - Use modular design patterns for easy updates and maintenance.
  - Implement logging and error handling for debugging and monitoring.
- **Performance:**
  - Ensure low latency in evaluation pipeline execution.
  - Optimize for memory usage during graph analysis.
- **Documentation:**
  - Comprehensive documentation for setup, usage, and testing.
  - Docstrings for all new functions and classes (Google style format).

## Out of Scope

- A2A protocol migration (PydanticAI stays)
- Agent system restructuring (`src/app/agents/` unchanged except trace instrumentation)
- Streamlit UI redesign (existing UI stays as-is)
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead)
- HuggingFace `datasets` library (use GitHub API downloader instead)
- Google Gemini SDK (`google-genai`) — use OpenAI-spec compatible providers only
- VCR-based network mocking (use @patch for unit tests)
- Browser-based E2E tests (Playwright/Selenium deferred)
- CC-style evaluation baselines (deferred)
- E2E integration tests and multi-channel deployment (deferred)

---

## Notes for Ralph Loop

Story Breakdown - Sprint 2 (6 stories total):

- **Feature 1 (Settings Migration)** → STORY-001: Migrate EvaluationConfig to JudgeSettings pydantic-settings
- **Feature 2 (Wire Evaluation)** → STORY-002: Wire evaluate_comprehensive after run_manager (depends: STORY-001)
- **Feature 3 (Trace Capture)** → STORY-003: Capture GraphTraceData during MAS execution (depends: STORY-002)
- **Feature 4 (Comparison Output)** → STORY-004: Add graph vs text metric comparison logging (depends: STORY-003)
- **Feature 4b (Opik → Logfire Migration)** → STORY-005: Migrate Opik to Logfire + Phoenix local tracing (depends: STORY-001)
- **Feature 4c (Streamlit Dashboard)** → STORY-006: Streamlit evaluation dashboard + agent graph visualization (depends: STORY-005)
