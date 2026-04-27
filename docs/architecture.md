---
title: Agents-eval Architecture
description: Detailed architecture information for the Agents-eval Multi-Agent System (MAS) evaluation framework
created: 2025-08-31
updated: 2026-03-02
category: architecture
version: 3.9.0
validated_links: 2026-03-12
---
# Architecture

<!-- markdownlint-disable MD024 no-duplicate-heading -->

This document provides detailed architecture information for the Agents-eval Multi-Agent System (MAS) evaluation framework.

## System Overview

This is a Multi-Agent System (MAS) evaluation framework for assessing agentic AI systems using the **PeerRead dataset** for comprehensive agent performance measurement. The project uses **PydanticAI** as the core framework for agent orchestration and implements a three-tiered evaluation approach: traditional metrics, LLM-as-a-judge assessment, and graph-based complexity analysis.

**Primary Purpose**: Evaluate agent performance in generating academic paper reviews through multiple evaluation methodologies to produce composite performance scores.

## Entry Points

The framework exposes five execution entry points, each backed by a Makefile recipe:

| Entry Point | Makefile Recipe | Module | Purpose |
| --- | --- | --- | --- |
| **CLI** | `make app_cli ARGS="..."` | `src/run_cli.py` | Single-run evaluation via command line |
| **GUI** | `make app_gui` | `src/run_gui.py` | Streamlit interactive dashboard |
| **Sweep** | `make app_sweep ARGS="..."` | `src/run_sweep.py` | Automated benchmarking across compositions |
| **Batch Run** | `make app_batch_run ARGS="..."` | `scripts/batch_run.py` | Run `app_cli` across all agent compositions with error resilience |
| **Batch Eval** | `make app_batch_eval ARGS="..."` | `scripts/batch_eval.py` | Summarize existing runs and sweeps into a consolidated report |

Additional convenience recipes:

| Recipe | Purpose |
| --- | --- |
| `make app_quickstart` | Download sample data + evaluate smallest paper (one command) |
| `make app_profile` | Profile a CLI run with Scalene |
| `make app_clean_results` | Remove all sweep result files |
| `make app_clean_logs` | Remove accumulated agent evaluation logs |
| `make cc_run_solo PAPER_ID=…` | Shorthand for `--engine=cc` single-agent CC baseline |
| `make cc_run_teams PAPER_ID=…` | Shorthand for `--engine=cc --cc-teams` CC Agent Teams baseline |

### CLI (`run_cli.py`)

Lightweight wrapper with lazy imports. Parses `--engine={mas,cc}`, selects the execution path, runs `main()`, and optionally generates a report.

Key flags: `--paper-id`, `--chat-provider`, `--judge-provider`, `--engine`, `--cc-teams`, `--generate-report`, `--skip-eval`, `--include-researcher`, `--include-analyst`, `--include-synthesiser`, `--token-limit`.

### GUI (`run_gui.py`)

Streamlit multi-page app launched via `streamlit run`. Pages: Run Research App (execution + results), Settings (provider/model config), Evaluation Results (tier breakdown + baseline comparison), Agent Graph (Pyvis visualization), Trace Viewer (SQLite trace browser). Theme selection and session state persist across page navigations.

### Sweep (`run_sweep.py`)

CLI for automated benchmarking. Accepts `--config <json>` for file-based configuration or individual flags. See [Benchmarking Infrastructure](#benchmarking-infrastructure-sprint-6) for full details.

### Batch Run (`batch_run.py`)

Runs `make app_cli` for each of the 8 agent compositions (2^3 from researcher/analyst/synthesiser toggles) for one or more papers. Catches and continues past errors (422, timeouts, UsageLimitExceeded). Supports parallel execution via `--parallel N` and composition filtering via `--compositions`.

Key flags: `--paper-ids`, `--chat-provider`, `--engine`, `--parallel`, `--compositions`, `--output`, `--verbose`.

### Batch Eval (`batch_eval.py`)

Reads `evaluation.json` from each run directory and `results.json` from each sweep directory, then writes a consolidated Markdown summary to `_Agents-eval/output/summary.md`. Supports `--runs-only` and `--sweeps-only` filters. Summary includes per-run scores (composite, T1/T2/T3, recommendation), aggregate statistics, and per-sweep mean/stddev.

## Data Flow

### Agent Execution Flow

1. PeerRead paper input → Manager Agent (with large context window models)
2. Optional: Manager delegates to Researcher Agent (with DuckDuckGo search)
3. Optional: Researcher results → Analyst Agent for validation
4. Optional: Validated data → Synthesizer Agent for review generation
5. Generated review → Comprehensive evaluation pipeline

### Evaluation Pipeline Flow

1. **Tier 1 — Traditional Metrics**: Text similarity (TF-IDF cosine, Jaccard, BERTScore/Levenshtein), execution time measurement
2. **Tier 2 — LLM-as-a-Judge**: Review quality assessment, agentic execution analysis
3. **Tier 3 — Graph-Based Analysis**: Tool call complexity, agent interaction mapping
4. **Composite Scoring**: Final score calculation using formula: (Agentic Results / Execution Time / Graph Complexity)

### Tier Result Data Flow and Persistence

Individual tier results are in-memory during pipeline execution. Per-run `evaluation.json` persistence writes the final `CompositeResult` to disk (see [Output Structure](#output-structure-sprint-13)).

1. **Tier execution** (`evaluation_pipeline.py`): Each tier runs and returns a typed result object (`Tier1Result`, `Tier2Result`, `Tier3Result`).
2. **Assembly**: Results are packed into an `EvaluationResults` dataclass (with fallback fill-in if tiers are missing).
3. **Composite scoring**: `CompositeScorer` combines tier results into a single `CompositeResult` — this is the only object returned to callers.

### `CompositeResult` consumers:

| Consumer | Location | Purpose |
| --- | --- | --- |
| `run_evaluation_if_enabled()` | `evaluation_runner.py` | Main entry point, returns up to `app.py` |
| `SweepRunner._run_single_evaluation()` | `sweep_runner.py` | Collects into `self.results` for batch analysis |
| `_render_report_section()` | `run_app.py` | Renders in Streamlit GUI |
| `generate_report()` | `report_generator.py` | Generates Markdown report |
| `compare()` | `baseline_comparison.py` | Diffs two `CompositeResult` objects |

**What is preserved:** Individual tier scores (`tier1_score`, `tier2_score`, `tier3_score`) and the full `metric_scores` breakdown are fields on `CompositeResult`. The per-tier `Tier1Result`/`Tier2Result`/`Tier3Result` objects are consumed by the composite scorer and not persisted separately.

**Persistence paths:** Per-run `evaluation.json`, Markdown report via `report_generator.py`, sweep `results.json` via `SweepRunner`, logger output (`_log_metric_comparison`). See [Output Structure](#output-structure-sprint-13) for the per-run directory layout.

### Three-Tier Validation Strategy

**Core Principle:** Tiers validate and enhance each other for robust evaluation.

| Tier | Role | Focus |
| ------ | ------ | ------- |
| Tier 1 (Traditional) | Baseline | Fast, objective text similarity |
| Tier 2 (LLM-Judge) | Semantic | Quality assessment via LLM |
| Tier 3 (Graph) | Behavioral | Coordination patterns from execution traces |

### Validation Logic:

- **All 3 tiers agree** → High confidence in MAS quality
- **Tier 3 good, Tier 1/2 fail** → Good coordination, poor output quality
- **Tier 1/2 good, Tier 3 fail** → Good output, inefficient coordination

### Design Goals:

- **Graph (Tier 3)**: Rich analysis from execution traces — project's differentiator
- **Traditional (Tier 1)**: Lightweight metrics only
- **LLM-Judge (Tier 2)**: Single LLM call, structured output

## Evaluation Framework Architecture

### Large Context Model Integration

The evaluation framework is built around large context window models capable of processing full PeerRead papers with automatic selection based on paper token count and intelligent fallback to document chunking for smaller context models.

**Model Selection**: Configurable per provider via `--chat-provider` and `--judge-provider`. See [Large Language Models](landscape/landscape-agent-frameworks-infrastructure.md#2-large-language-models) for model comparisons, context limits, and integration approaches.

### Evaluation Components

Result models: `src/app/data_models/evaluation_models.py`

#### Tier 1 — Traditional Metrics (`Tier1Result`)

**Location**: `src/app/judge/plugins/traditional.py`

| Metric | Range | Description |
| --- | --- | --- |
| `cosine_score` | 0–1 | TF-IDF cosine similarity vs ground truth |
| `jaccard_score` | 0–1 | Word-level Jaccard similarity |
| `semantic_score` | 0–1 | Levenshtein-based sequence similarity (BERTScore optional, currently disabled) |
| `execution_time` | ≥0 | Raw wall-clock seconds |
| `time_score` | 0–1 | Normalized time score |
| `task_success` | 0–1 | Continuous: `min(1.0, similarity / threshold)` |

#### Tier 2 — LLM-as-a-Judge (`Tier2Result`)

**Location**: `src/app/judge/plugins/llm_judge.py`

| Metric | Range | Description |
| --- | --- | --- |
| `technical_accuracy` | 0–1 | Factual and methodological correctness |
| `constructiveness` | 0–1 | Actionable feedback quality |
| `planning_rationality` | 0–1 | Decision-making and reasoning quality |

Also captures `model_used`, `api_cost`, and `fallback_used`.

#### Tier 3 — Graph Analysis (`Tier3Result`)

**Location**: `src/app/judge/plugins/graph_metrics.py`

Post-execution behavioral analysis: trace data → NetworkX graphs → retrospective evaluation.

| Metric | Range | Description |
| --- | --- | --- |
| `path_convergence` | 0–1 | Tool usage path efficiency |
| `tool_selection_accuracy` | 0–1 | Correct tool choice ratio |
| `coordination_centrality` | 0–1 | Agent coordination quality (graph centrality) |
| `task_distribution_balance` | 0–1 | Work distribution evenness across agents |
| `graph_complexity` | ≥0 | Node count in interaction graph |

#### Composite Scoring System

**Location**: `src/app/judge/composite_scorer.py`

The composite scorer maps tier result fields to six abstract metrics, each weighted 0.167 (equal):

| Composite Metric | Source Field | Tier |
| --- | --- | --- |
| `output_similarity` | `Tier1Result.overall_score` (weighted similarity) | 1 |
| `time_taken` | `Tier1Result.time_score` | 1 |
| `task_success` | `Tier1Result.task_success` | 1 |
| `planning_rationality` | `Tier2Result.planning_rationality` | 2 |
| `tool_efficiency` | `Tier3Result.tool_selection_accuracy` | 3 |
| `coordination_quality` | `Tier3Result.coordination_centrality` | 3 |

**Adaptive Weight Redistribution**:

- **Single-Agent Mode Detection**: Automatically detects single-agent runs from `GraphTraceData` (0-1 unique agent IDs, empty `coordination_events`)
- **Weight Redistribution**: When single-agent mode is detected, the `coordination_quality` metric (0.167 weight) is excluded and its weight is redistributed equally across the remaining 5 metrics (0.20 each)
- **Transparency**: `CompositeResult` includes `single_agent_mode: bool` flag to indicate when redistribution occurred
- **Compound Redistribution**: When both Tier 2 is skipped (no valid provider) AND single-agent mode is detected, weights are redistributed across the remaining available metrics to always sum to ~1.0
- **Tier Input Guards**: Tier 1 is skipped when review text is empty (non-paper queries) or no usable reference reviews are available (PeerRead cache empty). When Tier 1 is skipped and Tier 2+3 are available, composite uses T2+T3 with equal weight redistribution. When only Tier 1 is available (Tier 2 and 3 both unavailable), composite is capped at `composite_weak_reject_threshold` (default 0.4) with `evaluation_complete=False` — a single-tier result cannot score above the weak_reject boundary.

## Benchmarking Infrastructure (Sprint 6)

The benchmarking pipeline enables systematic comparison of MAS compositions with statistical rigor.

### Architecture

```text
SweepConfig → SweepRunner → (compositions × papers × repetitions) → SweepAnalyzer → output files
```bash

- **`SweepConfig`** (`src/app/benchmark/sweep_config.py`): Declares sweep parameters — agent compositions (2³ = 8 default), paper IDs, repetitions per combination, provider settings
- **`SweepRunner`** (`src/app/benchmark/sweep_runner.py`): Executes the sweep matrix, calls `evaluation_pipeline.evaluate_comprehensive()` for each cell, aggregates raw results
- **`SweepAnalyzer`** (`src/app/benchmark/sweep_analysis.py`): Computes mean, stddev, min, max per metric per composition across repetitions

### SweepConfig Fields

| Field | Type | Default | Purpose |
| --- | --- | --- | --- |
| `compositions` | `list[AgentComposition]` | required | Which MAS compositions to test |
| `repetitions` | `int` | required | Runs per composition per paper |
| `paper_ids` | `list[str]` | required | PeerRead paper IDs (e.g. `"1105.1072"`) |
| `output_dir` | `Path` | required | Sweep output directory |
| `chat_provider` | `str` | `CHAT_DEFAULT_PROVIDER` | LLM provider for MAS agents |
| `engine` | `str` | `"mas"` | `"mas"` or `"cc"` |
| `cc_teams` | `bool` | `False` | CC solo vs CC Agent Teams |
| `judge_provider` | `str` | `"auto"` | Tier 2 judge provider |
| `judge_model` | `str\|None` | `None` | Tier 2 judge model override |
| `retry_delay_seconds` | `float` | `5.0` | Backoff seed for 429 retries |
| `cc_artifact_dirs` | `list[Path]\|None` | `None` | Pre-collected CC artifacts (skip re-running) |

### Agent Compositions

`generate_all_compositions()` produces the full 2³ = 8 Cartesian product of `{researcher, analyst, synthesiser}` toggles:

| Name | Researcher | Analyst | Synthesiser |
| --- | --- | --- | --- |
| `manager-only` | - | - | - |
| `researcher` | yes | - | - |
| `analyst` | - | yes | - |
| `synthesiser` | - | - | yes |
| `researcher+analyst` | yes | yes | - |
| `researcher+synthesiser` | yes | - | yes |
| `analyst+synthesiser` | - | yes | yes |
| `researcher+analyst+synthesiser` | yes | yes | yes |

### Engine Modes in Sweep Context

The `engine` field is a single string, not a list. Each mode differs in execution:

- **`engine="mas"`**: Runs MAS evaluations only (compositions × papers × repetitions). No CC invoked.
- **`engine="cc", cc_teams=False`**: Runs MAS evaluations **and** CC solo baselines. CC solo loops over papers only (no composition loop), calls `run_cc_solo()`.
- **`engine="cc", cc_teams=True`**: Runs MAS evaluations **and** CC teams baselines. Calls `run_cc_teams()` per paper.

To compare all three engines on the same papers, run **three separate sweeps**:

```bash
# MAS only (all 8 compositions)
make app_sweep ARGS="--engine mas --all-compositions --paper-ids 1105.1072 --chat-provider cerebras --judge-provider cerebras"

# MAS + CC solo baseline
make app_sweep ARGS="--engine cc --paper-ids 1105.1072 --chat-provider cerebras --judge-provider cerebras"

# MAS + CC teams baseline
make app_sweep ARGS="--engine cc --cc-teams --paper-ids 1105.1072 --chat-provider cerebras --judge-provider cerebras"
```

### Sweep CLI Reference (`run_sweep.py`)

| Flag | Default | Description |
| --- | --- | --- |
| `--config <path>` | — | JSON config file (overrides individual flags) |
| `--paper-ids <csv>` | required | Comma-separated paper IDs |
| `--repetitions <n>` | `3` | Repetitions per composition |
| `--all-compositions` | off | Use all 8 agent compositions |
| `--chat-provider <name>` | `CHAT_DEFAULT_PROVIDER` | LLM provider for MAS agents |
| `--judge-provider <name>` | `"auto"` | Tier 2 judge provider |
| `--judge-model <name>` | per JudgeSettings | Tier 2 judge model |
| `--engine {mas,cc}` | `"mas"` | Execution engine |
| `--cc-teams` | off | Use CC Agent Teams mode |
| `--output-dir <path>` | `output/sweeps/<timestamp>` | Output directory |

### Execution Flow

`SweepRunner.run()` executes in this order:

1. `_validate_prerequisites()` — if `engine="cc"`, checks `claude` CLI is on PATH
2. `_run_mas_evaluations()` — **always runs**: loops compositions × papers × repetitions, writes incremental `results.json` after each success
3. `_run_cc_baselines()` — **only when `engine="cc"`**: loops papers, calls `run_cc_solo` or `run_cc_teams`, feeds CCResult through evaluation pipeline
4. `_save_results()` — writes final `results.json` + `summary.md`

Rate-limit resilience: on HTTP 429, retries with exponential backoff (seed: `retry_delay_seconds`). Incremental `results.json` persistence ensures partial results survive failures.

### CC Headless Integration

The CC path feeds Claude Code agent artifacts into the same evaluation pipeline as MAS:

```text
Solo:  claude -p "prompt" --output-format json        → CCResult → extract_cc_review_text → evaluate_comprehensive
Teams: claude -p "prompt" --output-format stream-json  → Popen JSONL stream → CCResult → cc_result_to_graph_trace → evaluate_comprehensive
```text

`check_cc_available()` (`src/app/engines/cc_engine.py`) wraps `shutil.which("claude")` for fail-fast validation. Teams mode sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and parses `init`, `result`, `TeamCreate`, and `Task` events from the live JSONL stream via `Popen`, since CC teams artifacts (`~/.claude/teams/`, `~/.claude/tasks/`) are ephemeral in print mode (see AGENT_LEARNINGS.md).

Sprint 10 added full pipeline parity: `extract_cc_review_text()` feeds review text to `evaluate_comprehensive()` via the `review_text` parameter on `run_evaluation_if_enabled()`. `cc_result_to_graph_trace()` builds `GraphTraceData` from team events for graph visualization. `CompositeResult.engine_type` is set to `"cc_solo"` or `"cc_teams"` after evaluation.

#### CC Teams Trace Data Flow

The JSONL stream from `claude -p --output-format stream-json` is consumed live from stdout. The raw stream is persisted to the per-run directory (see [Output Structure](#output-structure-sprint-13)).

```text
Popen(stdout=PIPE)
  → iter(proc.stdout)
    → parse_stream_json()
      → _parse_jsonl_line()     — skips blank/malformed lines
      → _apply_event()          — dispatches by event type:
          type=system,subtype=init  → execution_id
          type=result               → output_data (duration, cost, turns, review text)
          type=TeamCreate           → team_artifacts[] → coordination_events in GraphTraceData
          type=Task                 → team_artifacts[] → agent_interactions in GraphTraceData
    → CCResult
      → cc_result_to_graph_trace()  — maps team_artifacts to GraphTraceData
        → agent_interactions  (from Task events)
        → coordination_events (from TeamCreate events)
```

**Stream filter**: `_apply_event` captures `type=system, subtype=task_started/task_completed` events as team artifacts. The stale `_TEAM_EVENT_TYPES` constant was removed. Tier 3 graph analysis produces 0 nodes/0 edges when CC handles the task without spawning a team (triggers Tier 1-only fallback via adaptive weight redistribution).

**Team spawning is not guaranteed**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` enables the capability but CC autonomously decides whether to create a team based on task complexity. Simple queries may be solved solo even in teams mode. The default prompt template uses `"Use a team of agents."` phrasing to increase the likelihood of team creation, but it is ultimately CC's decision.

## Output Structure (Sprint 13)

All runtime data lives under a single `_Agents-eval/` root directory, kept outside the source tree via the leading underscore. `RunContext` (`src/app/utils/run_context.py`) owns per-run directory creation and routes MAS vs CC runs into separate subdirectories.

### Directory Layout

```text
_Agents-eval/
  datasets/
    peerread/             ← downloaded PeerRead corpus cache
  logs/
    {time}.log            ← Loguru rotating log files (not per-run)
  output/
    runs/
      mas/                              ← {ts} = YYYYMMDD_HHMMSS, {id} = exec_id first 8 chars
        {ts}_{engine}_{paper}_{id}/
          metadata.json   ← engine_type, paper_id, exec_id, start_time, cli_args
          trace.json      ← MAS execution trace (TraceCollector)
          review.json     ← generated review (ReviewPersistence + GeneratedReview)
          evaluation.json ← CompositeResult (when evaluation enabled)
          report.md       ← evaluation report (when --generate-report)
          agent_graph.json ← nx.DiGraph node-link serialization (when graph available)
          agent_graph.png  ← static graph render (when graph available)
      cc/
        {ts}_cc_solo_{paper}_{id}/
          metadata.json
          stream.json     ← raw JSON from claude -p
          evaluation.json
          report.md
          agent_graph.json
          agent_graph.png
        {ts}_cc_teams_{paper}_{id}/
          metadata.json
          stream.jsonl    ← JSONL teed from Popen stdout
          evaluation.json
          report.md
          agent_graph.json
          agent_graph.png
      traces.db           ← shared SQLite trace index (across all runs)
    sweeps/
      {YYYYMMDD_HHMMSS}/
        results.json      ← raw per-evaluation scores (composition × paper × repetition)
        summary.md        ← Markdown table with mean/stddev per metric per composition
    reports/
      {timestamp}.md      ← standalone reports (CLI --generate-report without run)
```text

### Output Decision Tree

```text
CLI/GUI invocation
  │
  ├─ ALWAYS: _Agents-eval/logs/{time}.log  (Loguru, module import)
  │
  ├─ RunContext.create() → _Agents-eval/output/runs/{mas|cc}/{ts}_{engine}_{paper}_{id}/
  │    └─ WRITES: metadata.json
  │
  ├─ CC solo path  → runs/cc/{ts}_cc_solo_{paper}_{id}/
  │    └─ WRITES: stream.json    (raw JSON from claude -p)
  │
  ├─ CC teams path → runs/cc/{ts}_cc_teams_{paper}_{id}/
  │    └─ WRITES: stream.jsonl   (JSONL teed from Popen stdout)
  │
  ├─ MAS path      → runs/mas/{ts}_{engine}_{paper}_{id}/
  │    ├─ WRITES: review.json    (ReviewPersistence + GeneratedReview)
  │    └─ WRITES: trace.json     (TraceCollector)
  │
  ├─ evaluation enabled (skip_eval=False)
  │    └─ WRITES: evaluation.json (CompositeResult)
  │
  ├─ graph available (graph is not None)
  │    ├─ WRITES: agent_graph.json (nx.DiGraph node-link data)
  │    └─ WRITES: agent_graph.png  (static matplotlib render)
  │
  └─ --generate-report
       └─ WRITES: report.md

Sweep invocation (run_sweep.py)
  │
  ├─ ALWAYS: _Agents-eval/logs/{time}.log
  │
  └─ SweepRunner.run() → _Agents-eval/output/sweeps/{ts}/
       ├─ WRITES: results.json   (incremental, after each evaluation)
       └─ WRITES: summary.md     (at sweep end)
```

### Path Configuration

All output paths derive from `_OUTPUT_BASE` in `src/app/config/config_app.py`:

| Constant | Value | Purpose |
| --- | --- | --- |
| `_OUTPUT_BASE` | `"_Agents-eval"` | Root for all runtime data |
| `DATASETS_PATH` | `"_Agents-eval/datasets"` | Downloaded dataset cache |
| `LOGS_PATH` | `"_Agents-eval/logs"` | Loguru rotating logs |
| `OUTPUT_PATH` | `"_Agents-eval/output"` | Run, sweep, and report artifacts |
| `RUNS_PATH` | `"_Agents-eval/output/runs"` | All per-run directories |
| `MAS_RUNS_PATH` | `"_Agents-eval/output/runs/mas"` | MAS engine run outputs |
| `CC_RUNS_PATH` | `"_Agents-eval/output/runs/cc"` | CC engine run outputs |

Paths are resolved relative to the project root via `resolve_project_path()` in `src/app/utils/paths.py`. Directories are created lazily with `mkdir(parents=True, exist_ok=True)`.

### RunContext Routing

`RunContext` is a module-level singleton (`get_active_run_context()` / `set_active_run_context()`) that bridges writers to the per-run directory:

- **`RunContext.create()`** routes to `runs/mas/` or `runs/cc/` based on `engine_type.startswith("cc")`.
- **Path properties** standardize filenames per engine: `stream_path` (`.json` for MAS, `.jsonl` for CC), `trace_path` (`trace.json`), `review_path`, `evaluation_path`, `report_path`.
- **`TraceCollector._store_trace()`** writes to `run_ctx.trace_path` when active, otherwise falls back to flat `{RUNS_PATH}/trace_{id}_{ts}.json`. Also writes to `traces.db` (SQLite) for structured queries.
- **`ReviewPersistence.save_review()`** writes to `run_dir/review.json` when active, otherwise falls back to `{MAS_RUNS_PATH}/{paper}_{ts}.json`.
- **`review.json` schema**: Contains `paper_id`, `timestamp`, `review` (PeerRead format), and optionally `structured_review` (validated `GeneratedReview` dict) and `model_info`.

### Timestamp Format

All output filenames use a unified timestamp format: `%Y%m%d_%H%M%S` (e.g., `20260227_143000`).

## Observability & Data Persistence

### Persistence Paths Reference

| Path | Writer | Format | Runtime Reader | Purpose |
| --- | --- | --- | --- | --- |
| `_Agents-eval/output/runs/traces.db` | `TraceCollector._store_trace` | SQLite | `TraceCollector.load_trace` (Tier 3) | Source of truth for graph-based evaluation |
| `{run_dir}/trace.json` | `TraceCollector._store_trace` | JSON | None (offline) | Per-run trace snapshot for manual inspection |
| `{run_dir}/review.json` | `ReviewPersistence` | JSON | None (offline) | Generated review with PeerRead format |
| `{run_dir}/evaluation.json` | `EvaluationPipeline` | JSON | None (offline) | CompositeResult serialized after evaluation |
| `{run_dir}/report.md` | `ReportGenerator` | Markdown | None (offline) | Human-readable evaluation report |
| `{run_dir}/agent_graph.json` | `graph_export.export_graph_json` | JSON | None (offline) | nx.DiGraph node-link serialization for offline analysis |
| `{run_dir}/agent_graph.png` | `graph_export.export_graph_png` | PNG | None (offline) | Static matplotlib render of agent interaction graph |
| `{run_dir}/metadata.json` | `RunContext` | JSON | None (offline) | Run configuration and timing metadata |
| `{run_dir}/stream.jsonl` | `cc_engine.py` (`_tee_stream` / `_persist_solo_stream`) | JSONL | None (offline) | CC engine raw stream capture |
| `_Agents-eval/datasets/peerread/` | `PeerReadDownloader` | Mixed | `datasets_peerread.load_paper` (Tier 1/2) | Ground truth reviews and paper content |
| `_Agents-eval/logs/{time}.log` | Loguru | Text | None (offline) | Rotating application logs |
| `_Agents-eval/output/sweeps/{ts}/results.json` | `SweepRunner` | JSON | None (offline) | Incremental sweep results |
| `_Agents-eval/output/sweeps/{ts}/summary.md` | `SweepRunner` | Markdown | None (offline) | Sweep summary report |

### Runtime vs Offline Readers

Only two persistence paths have runtime consumers in the evaluation pipeline:

- **`traces.db`** — read by `TraceCollector.load_trace()` during Tier 3 graph-based evaluation
- **`datasets/peerread/`** — read by `datasets_peerread.load_paper()` for ground truth in Tier 1/2

All other per-run files (`metadata.json`, `stream.*`, `review.json`, `evaluation.json`, `report.md`, `agent_graph.json`, `agent_graph.png`) are write-once, read-never at runtime. They exist for offline inspection, debugging, and audit trails.

### Phoenix / OTel vs TraceCollector

These are independent observability channels with no pipeline dependency between them:

| Aspect | TraceCollector | Phoenix / OTel |
| --- | --- | --- |
| Transport | Direct SQLite writes | OTLP gRPC via Logfire |
| Data | Agent interactions, tool calls, coordination events | Metrics and logs only (no distributed trace spans — see AGENT_LEARNINGS.md) |
| Consumer | Tier 3 evaluation (`composite_scorer.py`) | Phoenix dashboard (port 6006) |
| Dependency | Required for evaluation | Optional, supplementary |

### Trace Viewer (GUI)

The **Trace Viewer** Streamlit page (`src/gui/pages/trace_viewer.py`) provides read-only SQLite access to `traces.db`. It shows an executions overview table with drill-down to individual trace events. Uses Python's built-in `sqlite3` module — no additional dependencies.

### Agent Graph Pipeline (Trace → NetworkX → Pyvis)

The Agent Graph page renders an interactive visualization of agent interactions and tool usage from execution traces. The pipeline has three stages: trace persistence, graph construction, and rendering.

#### Stage 1: Trace Persistence

During MAS execution, `TraceCollector` (`src/app/judge/trace_processors.py`) records agent events (interactions, tool calls, coordination) and writes them to two stores:

- **`{run_dir}/trace.json`** — per-run JSON snapshot for offline inspection
- **`traces.db`** (SQLite, shared across runs) — structured store with `trace_executions` and `trace_events` tables, used as source of truth for runtime graph construction

For CC engines, `cc_result_to_graph_trace()` (`src/app/engines/cc_engine.py:255`) builds `GraphTraceData` directly from the JSONL stream's `TeamCreate` and `Task` events — no SQLite round-trip.

```text
MAS path:   TraceCollector.complete_trace() → _store_trace() → traces.db + trace.json
CC path:    CCResult.team_artifacts → cc_result_to_graph_trace() → GraphTraceData (in-memory)
```yaml

#### Stage 2: NetworkX Graph Construction

`GraphTraceData` (`src/app/data_models/evaluation_models.py:183`) is the intermediate model with three lists: `agent_interactions`, `tool_calls`, and `coordination_events`.

`build_interaction_graph()` (`src/app/judge/graph_builder.py:16`) converts `GraphTraceData` into an `nx.DiGraph`:

- **Agent nodes**: Created from `agent_interactions[].from`/`to` fields. Attributes: `type="agent"`, `label=<name>.capitalize()`.
- **Tool nodes**: Created from `tool_calls[].tool_name`. Attributes: `type="tool"`, `label=<tool_name>.replace("_"," ").title()`.
- **Edges**: Agent→Agent edges carry `interaction=<type>`. Agent→Tool edges carry `interaction="tool_call"`, `success=<bool>`.

The two engine paths converge at graph construction:

```text
MAS:  TraceCollector.load_trace(execution_id) → GraphTraceData → build_interaction_graph() → nx.DiGraph
CC:   cc_result_to_graph_trace(cc_result)      → GraphTraceData → build_interaction_graph() → nx.DiGraph
```

Both paths are called from `app.py`: `_run_mas_engine_path()` (line 375) and `_extract_cc_artifacts()` (line 245). The resulting `nx.DiGraph` is returned in the `main()` result dict as `{"graph": graph}`.

#### Stage 3: Pyvis Rendering (GUI)

The GUI stores the graph in Streamlit session state (`run_app.py:284`):

```python
st.session_state.execution_graph = result.get("graph")
```text

When the user navigates to the Agent Graph page, `render_agent_graph()` (`src/gui/pages/agent_graph.py:44`) converts the `nx.DiGraph` into an interactive HTML visualization using Pyvis:

1. Creates a `Network(directed=True)` with Barnes-Hut physics (gravitational constant, spring layout, 200 stabilization iterations)
2. Iterates graph nodes — agents rendered as themed circles (`shape="dot"`, `size=25`), tools as themed boxes (`shape="box"`, `size=20`). Colors sourced from the active GUI theme via `get_graph_node_colors()`
3. Iterates graph edges — directed arrows with interaction type as hover tooltip
4. Writes to a temporary HTML file via `net.save_graph()`, injects an accessibility `<title>` element, renders via `streamlit.components.html()`, then deletes the temp file
5. Displays graph statistics (node/edge counts) and an accessible text summary

```text
nx.DiGraph → Pyvis Network → temp .html → streamlit.components.html() → interactive browser widget
```

**Persistence**: After graph construction, `export_graph_json()` and `export_graph_png()` (`src/app/judge/graph_export.py`) write the `nx.DiGraph` to the per-run output directory as `agent_graph.json` (node-link format) and `agent_graph.png` (static matplotlib render). Both artifacts are registered with `ArtifactRegistry`.

### ArtifactRegistry

In-memory singleton (`src/app/utils/artifact_registry.py`) that tracks all file paths written during a run. Components call `register(label, path)` as they write artifacts. At run end, `summary()` produces a human-readable list of all outputs. Not persisted — exists only for end-of-run CLI/GUI display.

## Report Generation (Sprint 8)

Post-evaluation report generation synthesizes tier scores into actionable Markdown reports.

### Architecture

```text
CompositeResult → SuggestionEngine → [Suggestion, ...] → ReportGenerator → Markdown report
```python

- **`SuggestionEngine`** (`src/app/reports/suggestion_engine.py`): Iterates `metric_scores`, compares each against tier thresholds from `JudgeSettings` (accept=0.8, weak_accept=0.6, weak_reject=0.4). Assigns severity (critical/warning/info). Optional LLM enrichment via judge provider with rule-based fallback.
- **`ReportGenerator`** (`src/app/reports/report_generator.py`): Produces structured Markdown: executive summary, per-tier breakdown, weakness identification, actionable suggestions from the engine.
- **`Suggestion`** (`src/app/data_models/report_models.py`): Pydantic model with `severity`, `metric_name`, `tier`, `score`, `threshold`, `message`.

### Entry Points

- **CLI**: `--generate-report` flag on `run_cli.py` (requires evaluation, incompatible with `--skip-eval`). Output: `{run_dir}/report.md` (see [Output Structure](#output-structure-sprint-13))
- **GUI**: "Generate Report" button on App page, enabled after evaluation completes. Inline Markdown display with download option.

## Security Framework (Sprint 6)

The security hardening sprint applied the OWASP MAESTRO 7-layer model (Model, Agent Logic, Integration, Monitoring, Execution, Orchestration) to the evaluation framework.

### Key Mitigations

- **SSRF prevention**: URL validation with domain allowlisting (`src/app/utils/url_validation.py`). Allowlist derived from actual `validate_url()` call sites, not conceptual dependencies.
- **Input sanitization**: Prompt injection resistance via length limits and XML delimiter wrapping before LLM calls
- **Log scrubbing**: Sensitive data filtering (API keys, tokens, passwords) before trace export (`src/app/utils/log_scrubbing.py`)
- **Path sanitization**: `_sanitize_path_component()` in `run_context.py` strips path traversal sequences from `paper_id` and `engine_type` before directory creation
- **Input size limits**: DoS prevention through maximum payload sizes at system boundaries

### CVE Status

See [security-advisories.md](security-advisories.md) for all known advisories and their mitigation status. All Sprint 6 CVEs were either already mitigated by existing version pins or patched during this sprint.

### References

- Security tests: `tests/security/` (SSRF, prompt injection, sensitive data filtering)
- MAESTRO review findings: `docs/reviews/sprint5-code-review.md`
- Design principles: [best-practices/mas-security.md](archive/best-practices/mas-security.md)

## Implementation Status

**Detailed Timeline**: See [roadmap.md](roadmap.md) for comprehensive sprint history, dependencies, and development phases.

### Previous Implementation (Sprint 13 - Delivered)

**Sprint 13 Scope**: GUI audit remediation and theming system.

- **Accessibility Fixes** (STORY-001–004): Consolidated ARIA live regions via single `st.markdown()` calls, agent graph text summary with `st.caption()` and `<title>`, debug log `role="log"` landmark with `aria-label`, validation warning placement near Run button.
- **Theming System** (STORY-006–007, STORY-011): `THEMES` dict with 3 curated themes (Expanse Dark, Nord Light, Tokyo Night), integrated with Streamlit's built-in Settings menu for theme switching, graph font color and background color integration with active theme.
- **UX Improvements** (STORY-005, STORY-008–010, STORY-012): Report caching via `session_state["generated_report"]` with Clear Results button, home page onboarding steps, UI string consolidation in `src/gui/config/text.py`, navigation label consistency, type-aware output rendering in `render_output()`.

### Previous Implementation (Sprint 12 - Delivered)

**Sprint 12 Scope**: CC teams mode bug fixes, scoring system fixes, and output directory restructuring.

- **CC Teams Stream Event Parsing** (STORY-001): Fixed `_apply_event` to capture `type=system, subtype=task_started/task_completed` events as team artifacts. Removed stale `_TEAM_EVENT_TYPES` constant.
- **CC Teams Flag Passthrough** (STORY-002): Wired `cc_teams` boolean from CLI/GUI through `main()` to `engine_type` assignment. Replaced `team_artifacts` inference with explicit flag.
- **Tier 3 Empty-Trace Skip** (STORY-003): Returns `None` from `_execute_tier3` when trace data is empty, triggering Tier 1-only fallback (see [Adaptive Weight Redistribution](#composite-scoring-system)).
- **Composite Scoring Trace Awareness** (STORY-004): Wired `evaluate_composite_with_trace` into production pipeline for single-agent weight redistribution.
- **Execution Timestamp Propagation** (STORY-005): Captures wall-clock timestamps around subprocess/agent execution and propagates to `_execute_tier1` for accurate `time_taken` metric.
- **Semantic Score Deduplication** (STORY-006): Changed `compute_semantic_similarity` to use BERTScore F1 (`distilbert-base-uncased`) with Levenshtein fallback, replacing cosine (which duplicated `cosine_score`). BERTScore re-enabled after sentencepiece build issues resolved (Sprint 13).
- **Continuous Task Success** (STORY-007): Replaced binary 0/1 `task_success` with proportional `min(1.0, similarity/threshold)`.
- **Unified Output Directories** (STORY-008–010): `RunContext` consolidates all run artifacts into `output/runs/{ts}_{engine}_{paper}_{id}/`, sweeps into `output/sweeps/{ts}/`. See [Output Structure](#output-structure-sprint-13).

### Previous Implementation (Sprint 11 - Delivered)

**Sprint 11 Scope**: Observability, UX polish, test quality, and code health.

- **End-of-Run Artifact Summary** (STORY-001): `ArtifactRegistry` singleton in `src/app/utils/artifact_registry.py` with thread-safe `register()`, `summary()`, and `reset()`. Six components register artifact paths (log setup, trace collector, review persistence, report generator, sweep runner, CC stream persistence). CLI and sweep print summary at end of run.
- **GUI Sidebar Tabs** (STORY-002): Streamlit layout refactored with sidebar navigation separating Run, Settings, Evaluation, and Agent Graph into distinct pages. Tab selection persists across reruns. `run_gui.py:43` TODO removed.
- **CC Engine Empty Query Fix** (STORY-006): `build_cc_query()` in `cc_engine.py` generates default prompt from `paper_id` when query is empty. `DEFAULT_REVIEW_PROMPT_TEMPLATE` constant shared between CC and MAS paths (DRY). Teams mode prepends `"Use a team of agents."`.
- **CC JSONL Stream Persistence** (STORY-007): Raw JSONL stream teed during CC execution. Solo writes JSON, teams writes JSONL incrementally (crash-safe). Files registered with `ArtifactRegistry`. Later migrated to per-run directories.
- **Search Tool HTTP Resilience** (STORY-010): `resilient_tool_wrapper` catches HTTP 403/429 from DuckDuckGo, returning descriptive error string to agent instead of crashing. Tavily is a declared dependency (`pydantic-ai-slim[tavily]`) with `TAVILY_API_KEY` in `AppEnv`, ready to wire as a fallback search tool but not yet registered on the researcher agent.
- **Sub-Agent Validation Fix** (STORY-011): `_validate_model_return()` accepts `Any` input, tries `model_validate_json()` for string inputs (fixes non-OpenAI providers returning JSON strings instead of model instances). `str()` wrapping removed from call sites.
- **Query Persistence Fix** (STORY-008): `key` parameter added to free-form query `text_input` widgets for Streamlit session state persistence.
- **Test Quality** (STORY-003, STORY-004): `assert isinstance()` replaced with behavioral assertions across 12 test files. Subdirectory `conftest.py` files added to `tests/agents/`, `tests/judge/`, `tests/tools/`, `tests/evals/` with shared fixtures.
- **Data Layer Refactor** (STORY-005): `DATA_TYPE_SPECS` registry replaces 4 dispatch chains in `datasets_peerread.py`. Single validation point for `data_type`.
- **Config Consolidation** (STORY-009): `LogfireConfig` and `PeerReadConfig` moved to `src/app/config/`.
- **Examples Modernization** (STORY-012): 5 new examples (MAS single-agent, MAS multi-agent, CC solo, CC teams, sweep benchmark) added. README updated with all 8 examples.

### Previous Implementation (Sprint 10 - Substantially Delivered)

**Sprint 10 Scope**: E2E CLI/GUI parity for CC engine, graph visualization, test quality.

- **CC Evaluation Pipeline Parity** (STORY-010): `main()` decomposes into `_run_cc_engine_path()` and `_run_mas_engine_path()`. CC branch calls `extract_cc_review_text()` and `cc_result_to_graph_trace()`, then feeds both into `evaluate_comprehensive()`. `CompositeResult.engine_type` set to `"cc_solo"` or `"cc_teams"`. `_load_reference_reviews(paper_id)` loads ground-truth for all modes (was hardcoded `None`).
- **Graph Visualization Polish** (STORY-011): `render_agent_graph()` accepts `composite_result` for mode-specific empty-state messages (solo/teams/MAS). Tier 3 informational label on Evaluation page when engine is CC.
- **inspect.getsource Removal** (STORY-015): 7 occurrences of `inspect.getsource` in tests replaced with behavioral assertions. Zero remaining.
- **Reference Reviews from PeerRead**: `_load_reference_reviews(paper_id)` loads ground-truth reviews via `PeerReadLoader`, replacing hardcoded `None`.
- **Process Group Kill**: CC teams subprocess uses `start_new_session=True` with `os.killpg()` on timeout to cleanly terminate teammate child processes. Test fix: `os.killpg`/`os.getpgid` mocked in timeout test to prevent real SIGTERM to container process group.
- **GUI CC Execution**: `_execute_query_background()` calls `run_cc_solo()`/`run_cc_teams()` when CC engine selected, passing `cc_result` to `main()`.

### Sprint 9 Key Deliverables (Delivered)

- Dead code deletion, format string sanitization, PDF size guard, API key env cleanup, security hardening, judge accuracy, AgentConfig typing, type safety fixes, test suite quality sweep

**Sprint 8 Key Deliverables** (Delivered):

- Tool bug fix, API key/model cleanup, CC engine consolidation, graph alignment, dead code removal, report generation, judge settings UX, GUI a11y/UX

**Sprint 7 Key Deliverables** (Delivered):

- Unified provider configuration (`--chat-provider`, `--judge-provider`, `--judge-model`)
- `--engine=mas|cc` flag for CLI and sweep (replaces `--cc-baseline`)
- Sweep rate-limit resilience (retry with backoff, incremental result persistence)
- GUI: real-time debug log streaming, paper selection dropdown, editable settings
- `_handle_model_http_error` fix: re-raise instead of `SystemExit(1)` on HTTP 429

**Sprint 6 Key Deliverables** (Delivered):

- **Benchmarking Infrastructure**:
  - MAS composition sweep (`SweepRunner`): 8 agent compositions × N papers × N repetitions
  - Statistical analysis (`SweepAnalyzer`): mean, stddev, min, max per composition
  - Sweep CLI (`run_sweep.py`) with `--chat-provider`, `--paper-ids`, `--repetitions`, `--all-compositions`
  - Results output: `results.json` (raw) + `summary.md` (Markdown table)

- **CC Baseline Completion**:
  - `CCTraceAdapter` for parsing Claude Code artifacts from headless invocation
  - Live JSONL stream parsing (teams artifacts are ephemeral in print mode — see [CC Headless Integration](#cc-headless-integration))

- **Security Hardening**:
  - SSRF prevention: URL validation with domain allowlisting
  - Prompt injection resistance: length limits, XML delimiter wrapping
  - Sensitive data filtering in logs and traces (API keys, tokens)
  - Input size limits for DoS prevention

- **Test Quality**:
  - Security tests in `tests/security/` (SSRF, prompt injection, data scrubbing)
  - Test filesystem isolation via `tmp_path`

**Sprint 5 Key Improvements** (Delivered):

- **Runtime Fixes**:
  - Tier 2 judge provider fallback with automatic API key validation
  - Configurable agent token limits via CLI (`--token-limit`), GUI, and env var
  - PeerRead dataset validation resilience for optional fields (IMPACT, SUBSTANCE)
  - OTLP endpoint double-path bug fix for Phoenix trace export

- **GUI Enhancements**:
  - Background query execution with tab navigation resilience
  - Debug log panel in App tab with real-time capture
  - Evaluation Results and Agent Graph tabs wired to live data
  - Editable settings page with session-scoped persistence

- **Architecture Improvements**:
  - Single-agent composite score weight redistribution (adaptive scoring)
  - PeerRead tools moved from manager to researcher agent (separation of concerns)
  - Tier 3 tool accuracy accumulation bug fixes
  - Dead code removal (duplicate AppEnv class, commented agentops code)

- **Code Quality**:
  - OWASP MAESTRO 7-layer security review (Model, Agent Logic, Integration, Monitoring, Execution, Environment, Orchestration)
  - Test suite refactoring to remove implementation-detail tests (595 → 564 tests, no behavioral coverage loss)
  - Debug logging for empty API keys in provider resolution

### Previous Implementation (Sprint 4 Complete)

The three-tiered evaluation framework is fully operational with plugin architecture:

**✅ Tier 1 - Traditional Metrics** (`src/app/judge/plugins/traditional.py`):

- Cosine similarity using TF-IDF vectorization
- Jaccard similarity with enhanced textdistance support
- Semantic similarity via BERTScore F1 (Levenshtein fallback)
- Execution time measurement and normalization
- Task success assessment with configurable thresholds

**✅ Tier 2 - LLM-as-a-Judge** (`src/app/judge/plugins/llm_judge.py`):

- Quality assessment using configurable judge provider (default: auto-inherits chat provider)
- Planning rationality evaluation
- Technical accuracy scoring
- Cost-budgeted evaluation with retry mechanisms
- **Provider Fallback Chain** (Sprint 5): Automatically selects available LLM provider by validating API key availability before attempting calls
  - Primary provider validation → Fallback provider if primary unavailable → Skip Tier 2 entirely if both unavailable
  - `tier2_provider=auto` mode inherits the agent system's active `chat_provider` for consistency. When `chat_model` is not set, uses `PROVIDER_REGISTRY.default_model` for the resolved provider (e.g. `gpt-oss-120b` for Cerebras) instead of the generic `tier2_model` default
  - When Tier 2 is skipped, its 3 metrics (`technical_accuracy`, `constructiveness`, `planning_rationality`) are excluded from composite scoring and weights redistributed to Tier 1 and Tier 3
  - Prevents 401 authentication errors and neutral 0.5 fallback scores when providers are unavailable

**✅ Tier 3 - Graph Analysis** (`src/app/judge/plugins/graph_metrics.py`):

- NetworkX-based behavioral pattern analysis from execution traces
- Agent coordination quality measurement
- Tool usage effectiveness evaluation
- Performance bottleneck detection

**✅ Composite Scoring** (`src/app/judge/composite_scorer.py`):

- Six-metric weighted formula implementation
- Recommendation mapping (accept/weak_accept/weak_reject/reject)
- Configuration-driven weights from `JudgeSettings`

**✅ Evaluation Pipeline** (`src/app/judge/evaluation_pipeline.py`):

- End-to-end evaluation orchestration (active production path via `run_evaluation_if_enabled()`)
- Performance monitoring and error handling
- Fallback strategies and timeout management

**`JudgeAgent`** (`src/app/judge/agent.py`): Alternative plugin-based orchestrator. Exported from `judge.__init__` but not used in any production path (CLI, GUI, sweep). Candidate for removal.

### Plugin Architecture (Sprint 3 - Delivered)

**Design Principles**: See [best-practices/mas-design-principles.md](archive/best-practices/mas-design-principles.md) for 12-Factor Agents, Anthropic Harnesses, and PydanticAI integration patterns.

**Security Framework**: See [best-practices/mas-security.md](archive/best-practices/mas-security.md) for OWASP MAESTRO 7-layer security model.
See [analysis/ai-security-governance-frameworks.md](archive/analysis/ai-security-governance-frameworks.md) for cross-framework analysis (MAESTRO, MITRE ATLAS, NIST AI RMF, ISO 42001/23894).

#### EvaluatorPlugin Interface

All evaluation engines (Traditional, LLM-Judge, Graph) implement the typed `EvaluatorPlugin` abstract base class:

```python
class EvaluatorPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def tier(self) -> int: ...

    @abstractmethod
    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel: ...

    @abstractmethod
    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]: ...
```

#### PluginRegistry

Central registry for plugin discovery and tier-ordered execution. Plugins register at import time and are executed in tier order (1 → 2 → 3) with typed context passing between tiers.

#### JudgeSettings Configuration

Replaces `EvaluationConfig` JSON with `pydantic-settings` BaseSettings class using `JUDGE_` environment variable prefix:

```python
class JudgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JUDGE_")

    tier1_max_seconds: float = 1.0
    tier2_max_seconds: float = 10.0
    total_max_seconds: float = 120.0
    tier2_provider: str = "auto"
    tier2_model: str = "gpt-4o-mini"
    # ... 30+ settings covering per-tier config, thresholds, tracing, observability
```text

#### Typed Context Passing

Each plugin's `get_context_for_next_tier()` returns a `dict[str, Any]` context consumed by the next tier's `evaluate(input_data, context)` method. Input/output boundaries use Pydantic models; inter-tier context uses dicts for flexibility.

### Development Timeline

- **Sprint 1**: Three-tiered evaluation framework -- Delivered
- **Sprint 2**: Eval wiring, trace capture, Logfire+Phoenix, Streamlit dashboard -- Delivered
- **Sprint 3**: Plugin architecture, GUI wiring, test alignment, optional weave, trace quality -- Delivered
- **Sprint 4**: Operational resilience, Claude Code baseline comparison (solo + teams) -- Delivered
- **Sprint 5**: Runtime fixes, GUI enhancements, architecture improvements, code quality review -- Delivered
- **Sprint 6**: Benchmarking infrastructure, CC baseline completion, security hardening, test quality -- Delivered
- **Sprint 7**: Documentation, examples, test refactoring, GUI improvements, unified providers, CC engine -- Delivered
- **Sprint 8**: Tool bug fix, API key/model cleanup, CC engine consolidation, graph alignment, report generation, GUI a11y/UX -- Delivered
- **Sprint 9**: Correctness & security hardening — dead code, format string sanitization, PDF guard, API key cleanup, judge accuracy, type safety, test quality -- Delivered
- **Sprint 10**: E2E CLI/GUI parity for CC engine (pipeline parity, review text wiring, engine_type, GUI CC execution), graph visualization polish (mode-specific messages, Tier 3 informational label), test quality (inspect.getsource removal, reference reviews) -- Substantially Delivered (STORY-012/013/014 not started)
- **Sprint 11**: Observability and UX polish — artifact summary (ArtifactRegistry), GUI sidebar tabs, CC engine fixes (empty query, stream persistence), search tool resilience, sub-agent validation fix, test quality (isinstance→behavioral, conftest consolidation), data layer refactor, config consolidation, examples modernization -- Delivered
- **Sprint 12**: CC teams mode bug fixes (stream event parsing, cc_teams flag passthrough), scoring system fixes (Tier 3 empty-trace, composite trace awareness, time_taken timestamps, semantic dedup, continuous task_success), per-run output directories (RunContext, writer migration, evaluation.json persistence) -- Delivered
- **Sprint 13**: GUI audit remediation & theming — accessibility (ARIA live regions, landmarks, graph alt text), theming system (3 themes, selector widget, graph color integration), UX improvements (onboarding, validation, report caching, navigation, string consolidation, type-aware output) -- Delivered

For sprint details and candidate metrics backlog, see [roadmap.md](roadmap.md).

## Key Dependencies

The system relies on several key technology categories for implementation and evaluation.

**Core Technologies**: See [Agent Frameworks](landscape/landscape-agent-frameworks-infrastructure.md#1-agent-frameworks) for PydanticAI agent orchestration details, [Graph Analysis & Network Tools](landscape/landscape-evaluation-data-resources.md#6-graph-analysis-network-tools) for NetworkX complexity analysis capabilities, and [Large Language Models](landscape/landscape-agent-frameworks-infrastructure.md#2-large-language-models) for LLM integration approaches.

**Evaluation Tools**: See [Traditional Metrics Libraries](landscape/landscape-evaluation-data-resources.md#7-traditional-metrics-libraries) for NLTK and Rouge-Score implementation details and feasibility assessments.

**Development Infrastructure**: See [Development Infrastructure](landscape/landscape-agent-frameworks-infrastructure.md#development-infrastructure) for uv, Streamlit, Ruff, and pyright integration approaches and alternatives.

## Agents

### Manager Agent

- **Description**: Oversees research and analysis tasks, coordinating the efforts of the research, analysis, and synthesizer agents to provide comprehensive answers to user queries. Delegates tasks and ensures the accuracy of the information.
- **Responsibilities**:
  - Coordinates the research, analysis, and synthesis agents.
  - Delegates research tasks to the Research Agent.
  - Delegates analysis tasks to the Analyst Agent.
  - Delegates synthesis tasks to the Synthesizer Agent.
  - Ensures the accuracy of the information.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Researcher Agent

- **Description**: Gathers and analyzes data relevant to a given topic, utilizing search tools to collect data and verifying the accuracy of assumptions, facts, and conclusions.
- **Responsibilities**:
  - Gathers and analyzes data relevant to the topic.
  - Uses search tools to collect data.
  - Checks the accuracy of assumptions, facts, and conclusions.
- **Tools**:
  - [DuckDuckGo Search Tool](https://ai.pydantic.dev/common-tools/#duckduckgo-search-tool)
  - `get_paper_content(paper_id)` — retrieves full paper text from local PeerRead dataset via parsed JSON → raw PDF → abstract fallback chain (Sprint 8, replaces `read_paper_pdf_tool`)
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Analyst Agent

- **Description**: Checks the accuracy of assumptions, facts, and conclusions in the provided data, providing relevant feedback and ensuring data integrity.
- **Responsibilities**:
  - Checks the accuracy of assumptions, facts, and conclusions.
  - Provides relevant feedback if the result is not approved.
  - Ensures data integrity.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Synthesizer Agent

- **Description**: Outputs a well-formatted scientific report using the data provided, maintaining the original facts, conclusions, and sources.
- **Responsibilities**:
  - Outputs a well-formatted scientific report using the provided data.
  - Maintains the original facts, conclusions, and sources.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Critic Agent (Proposed - Unscheduled)

- **Description**: Dedicated skeptical reviewer that participates in all agent interactions to reduce hallucinations and compounding errors. Based on Stanford Virtual Lab research showing critic agents significantly improve output quality.
- **Responsibilities**:
  - Challenge assumptions in Researcher outputs
  - Question methodology in Analyst assessments
  - Flag potential hallucinations in Synthesizer reports
  - Provide conservative feedback to reduce errors
  - Participate in both group coordination and individual agent assessments
- **Location**: Planned for `src/app/agents/critic_agent.py` or extension of `agent_system.py`
- **Research Basis**: Stanford's Virtual Lab demonstrated that dedicated critic agents reduce compounding errors in multi-agent systems

## Decision Log

This section documents architectural decisions made during system development to provide context, rationale, and alternatives considered.

### Decision Format

Each architectural decision includes:

- **Date**: When the decision was made
- **Decision**: What was decided
- **Context**: Why this decision was needed
- **Alternatives**: What other options were considered
- **Rationale**: Why this option was chosen
- **Status**: Active/Superseded/Deprecated

### Architectural Decisions Records

#### ADR-001: PydanticAI as Agent Framework

- **Date**: 2025-03-01
- **Decision**: Use PydanticAI for multi-agent orchestration
- **Context**: Need type-safe, production-ready agent framework
- **Alternatives**: LangChain, AutoGen, CrewAI, custom implementation
- **Rationale**: Type safety, async support, Pydantic validation, lightweight architecture
- **Status**: Active

#### ADR-002: PeerRead Dataset Integration

- **Date**: 2025-08-01
- **Decision**: Use PeerRead scientific paper review dataset as primary evaluation benchmark
- **Context**: Need standardized, academic-quality evaluation dataset
- **Alternatives**: Custom dataset, multiple datasets, synthetic data
- **Rationale**: Established academic benchmark, complex reasoning tasks, real-world data quality
- **Status**: Active

#### ADR-003: Three-Tiered Evaluation Framework

- **Date**: 2025-08-23
- **Decision**: Implement Traditional Metrics → LLM-as-a-Judge → Graph Analysis evaluation pipeline
- **Context**: Need comprehensive agent evaluation beyond simple metrics
- **Alternatives**: Single-tier evaluation, two-tier approach, external evaluation only
- **Rationale**: Provides complementary evaluation dimensions (quantitative, qualitative, behavioral) while maintaining modularity
- **Status**: Active

#### ADR-004: Post-Execution Graph Analysis

- **Date**: 2025-08-25
- **Decision**: Analyze agent behavior through post-execution trace processing rather than real-time monitoring
- **Context**: Need to evaluate coordination patterns without affecting agent performance
- **Alternatives**: Real-time graph construction, embedded monitoring, manual analysis
- **Rationale**: Avoids performance overhead, enables comprehensive analysis, preserves agent autonomy
- **Status**: Active

#### ADR-005: Plugin-Based Evaluation Architecture

- **Date**: 2026-02-09
- **Decision**: Wrap existing evaluation engines in `EvaluatorPlugin` interface with `PluginRegistry` for tier-ordered execution
- **Context**: Need extensibility without modifying core pipeline code; enable new metrics without breaking existing functionality
- **Alternatives**: Direct engine refactoring, new parallel pipeline, microservices architecture
- **Rationale**: Pure adapter pattern preserves existing engines; 12-Factor #4/#10/#12 (backing services, dev/prod parity, stateless processes); MAESTRO Agent Logic Layer typed interfaces
- **Status**: Active

#### ADR-006: pydantic-settings Migration

- **Date**: 2026-02-09
- **Decision**: Replace JSON config files with `BaseSettings` classes (`JudgeSettings`, `CommonSettings`) using environment variables
- **Context**: Need 12-Factor #3 (config in env) compliance; eliminate JSON parsing overhead; enable per-environment configuration
- **Alternatives**: Keep JSON, YAML config, TOML config, mixed approach
- **Rationale**: Type-safe config with Pydantic validation; environment variable support; JSON fallback during transition; aligns with 12-Factor app principles
- **Status**: Active

#### ADR-007: Optional Container-Based Deployment

- **Date**: 2026-02-09
- **Decision**: Support both local (default) and containerized (optional) deployment modes for MAS orchestrator and judge components
- **Context**: Future need for distributed evaluation, parallel judge execution, production isolation, and scalable infrastructure; current single-machine execution sufficient but architecture should enable growth
- **Alternatives**:
  - Local-only - simple but doesn't scale
  - Container-only - production-ready but development friction
  - Hybrid (chosen) - local default, containers optional
  - Microservices - over-engineered for current scale
- **Rationale**:
  - Local execution remains default (zero friction for development)
  - Containers optional (opt-in for production/CI/CD scenarios)
  - API-first communication (FastAPI Feature 10 enables inter-container communication)
  - Stateless judge design (plugin architecture naturally supports containerization)
  - 12-Factor #6 compliance (execute as stateless processes)
  - Parallel evaluation via multiple judge replicas per tier
- **Implementation**:
  - Phase 1: Document pattern only, no implementation
  - Phase 2: Docker images, compose files, deployment docs
  - Prerequisite: FastAPI API stability
- **Status**: Proposed (deferred, unscheduled)

#### ADR-008: CC Baseline Engine — subprocess vs SDK

- **Date**: 2026-02-17
- **Decision**: Keep `subprocess.run([claude, "-p"])` for Sprint 7 STORY-013; evaluate SDK migration for Sprint 8
- **Context**: `--engine=cc` invokes Claude Code headless to compare CC's agentic approach against PydanticAI MAS. Three implementation options exist.
- **Alternatives**:
  - `subprocess.run([claude, "-p"])` (Sprint 7) — full CC tool use, external CLI dependency, correct agentic semantics
  - `anthropic` SDK (`messages.create`) — pure Python, no CLI, but **no tool use** — reduces CC to a raw LLM call, not a valid agentic baseline
  - `claude-agent-sdk` — wraps CLI in Python package, full CC tools, bundles CLI (~100MB), proprietary license
- **Rationale**:
  - The CC baseline measures **orchestration approach** (CC agents vs PydanticAI agents), not model quality
  - CC solo used 19 tool calls (Task, Bash, Glob, Grep, Read) — removing tools changes what's being measured
  - `subprocess.run` is the simplest correct approach (KISS); `shutil.which("claude")` provides fail-fast validation
  - `anthropic` SDK is valid as a **separate** `--engine=claude-api` mode for model-vs-model comparison, not as a CC replacement
  - `claude-agent-sdk` is a valid Sprint 8 refinement if subprocess proves brittle
- **Status**: Active (subprocess). Sprint 8 PRD confirmed: SDK migration removed from scope, subprocess retained per this ADR

## Agentic System Architecture

**PlantUML Source**: [arch_vis/MAS-C4-Overview.plantuml](arch_vis/MAS-C4-Overview.plantuml) | [arch_vis/MAS-C4-Detailed.plantuml](arch_vis/MAS-C4-Detailed.plantuml)

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show MAS Overview</summary>
  <img src="../assets/images/MAS-C4-Overview-dark.png#gh-dark-mode-only" alt="MAS Architecture Overview" title="MAS Architecture Overview" width="80%" />
  <img src="../assets/images/MAS-C4-Overview-light.png#gh-light-mode-only" alt="MAS Architecture Overview" title="MAS Architecture Overview" width="80%" />
</details>
<details>
  <summary>Show MAS Detailed</summary>
  <img src="../assets/images/MAS-C4-Detailed-dark.png#gh-dark-mode-only" alt="MAS Architecture Detailed" title="MAS Architecture Detailed" width="80%" />
  <img src="../assets/images/MAS-C4-Detailed-light.png#gh-light-mode-only" alt="MAS Architecture Detailed" title="MAS Architecture Detailed" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

## Review Workflow

**PlantUML Source**: [arch_vis/MAS-Review-Workflow.plantuml](arch_vis/MAS-Review-Workflow.plantuml)

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show Review Workflow</summary>
  <img src="../assets/images/MAS-Review-Workflow-dark.png#gh-light-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
  <img src="../assets/images/MAS-Review-Workflow-light.png#gh-dark-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

## Diagram Generation

All architecture diagrams are generated from PlantUML source files in the `arch_vis/` directory. For rendering instructions and PlantUML setup, see [arch_vis/README.md](arch_vis/README.md).
