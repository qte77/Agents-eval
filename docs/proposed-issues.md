# Proposed Issues for Agents-eval

Create these 3 issues on qte77/Agents-eval.

---

## Issue 1: feat: extract graph analysis engine as reusable cc-meta observability skill

### Goal

Make Agents-eval's graph analysis engine available as a cc-plugins skill so any CC session can evaluate multi-agent coordination quality post-execution.

### Reasoning

Tier 3 graph analysis ([src/app/judge/graph_analysis.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/graph_analysis.py)) computes coordination_centrality, tool_selection_accuracy, task_distribution_balance, and path_convergence via NetworkX. Currently locked inside the eval pipeline. External projects (e.g., [disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) — 1.3k stars, 26 open issues) capture events but have no evaluation layer. Our [polyforge-orchestrator](https://github.com/qte77/polyforge-orchestrator) runs parallel agents via `cc-parallel.sh` with no post-execution quality metrics.

Extracting the graph engine as a skill in [cc-plugins](https://github.com/qte77/claude-code-plugins) (`plugins/cc-meta/skills/observing-agent-behavior/`) would make it available to any project that installs the plugin.

### Suggested Solution

1. Extract `GraphAnalysisEngine` + `GraphTraceData` + `TraceCollector` into standalone module
2. Create `plugins/cc-meta/skills/observing-agent-behavior/SKILL.md` that:
   - Reads CC session transcripts (`~/.claude/projects/<path>/<uuid>.jsonl`)
   - Parses tool calls, subagent spawns, team events into `GraphTraceData`
   - Runs graph analysis (NetworkX) and outputs structured metrics
   - Optionally feeds results into `ai-agents-research/docs/learnings/` via compound writeback
3. Adapter interface: accept both Agents-eval trace format and raw CC JSONL

Key files:
- [src/app/judge/graph_analysis.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/graph_analysis.py)
- [src/app/judge/trace_processors.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/trace_processors.py)
- [src/app/judge/composite_scorer.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/composite_scorer.py)

---

## Issue 2: feat: add behavioral drift detection across sessions

### Goal

Detect agent behavioral drift by comparing graph metrics across multiple execution sessions over time.

### Reasoning

Agents-eval currently evaluates single execution runs via the 3-tier pipeline ([src/app/judge/evaluation_pipeline.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/evaluation_pipeline.py)). No temporal comparison — each run is scored independently. [TraceCollector](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/trace_processors.py) stores all traces in `traces.db` (SQLite), but nothing reads historical traces to detect trends.

This gap is mirrored externally: [disler/claude-code-hooks-multi-agent-observability#34](https://github.com/disler/claude-code-hooks-multi-agent-observability/issues/34) requests exactly this. Our [learnings-ralphy](https://github.com/qte77/learnings-ralphy) runs weekly — drift detection would tell us whether agent quality is improving or degrading.

### Suggested Solution

1. Add `DriftAnalyzer` to `src/app/judge/` that:
   - Loads N most recent traces from `traces.db` for a given engine type
   - Computes per-session graph metrics (reusing `GraphAnalysisEngine`)
   - Calculates drift velocity: rate of change in coordination_centrality, tool_selection_accuracy
   - Flags anomalies: sessions deviating >2σ from rolling mean
2. Output: drift report with session-over-session comparison, trend direction, anomaly flags
3. CLI: optional `--drift` flag runs drift analysis after evaluation
4. Feed into [ai-agents-research/docs/learnings/](https://github.com/qte77/ai-agents-research/tree/main/docs/learnings) for compound learning

Key dependencies:
- [src/app/judge/trace_processors.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/trace_processors.py) — `TraceCollector.load_trace()`
- [src/app/judge/graph_analysis.py](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/graph_analysis.py) — `GraphAnalysisEngine.evaluate_graph_metrics()`

---

## Issue 3: feat: add CC session JSONL parser for TraceCollector

### Goal

Enable Agents-eval to evaluate Claude Code sessions directly from CC's native JSONL transcript format.

### Reasoning

[TraceCollector](https://github.com/qte77/Agents-eval/blob/main/src/app/judge/trace_processors.py) only accepts events from Agents-eval's PydanticAI agents. CC sessions produce rich JSONL at `~/.claude/projects/<path>/<uuid>.jsonl` with tool calls, subagent spawns, team events — can't be ingested.

[cc_engine.py](https://github.com/qte77/Agents-eval/blob/main/src/app/engines/cc_engine.py) parses CC output during live execution but has no offline parser for existing session files.

A JSONL parser would let us:
- Evaluate any past CC session post-hoc
- Feed [polyforge-orchestrator](https://github.com/qte77/polyforge-orchestrator) parallel results into graph analysis
- Support the proposed [cc-meta observability skill](https://github.com/qte77/claude-code-plugins)

### Suggested Solution

1. Add `CCSessionParser` to `src/app/judge/` that:
   - Reads `<uuid>.jsonl` (schema in [cc-entry-types.md](https://github.com/qte77/claude-code-plugins/blob/main/plugins/cc-meta/skills/synthesizing-cc-bigpicture/references/cc-entry-types.md))
   - Maps CC entries to `GraphTraceData`:
     - `assistant` + tool_use → `tool_calls`
     - `queue-operation` → `agent_interactions` (subagent spawns)
     - Team events → `coordination_events`
   - Handles subagent transcripts in `<uuid>/subagents/`
2. `CCSessionParser.to_graph_trace_data()` → feeds into `GraphAnalysisEngine`
3. CLI: `agents-eval --from-session ~/.claude/projects/<path>/<uuid>.jsonl`

Key references:
- [src/app/engines/cc_engine.py](https://github.com/qte77/Agents-eval/blob/main/src/app/engines/cc_engine.py)
- [CC entry types](https://github.com/qte77/claude-code-plugins/blob/main/plugins/cc-meta/skills/synthesizing-cc-bigpicture/references/cc-entry-types.md)
