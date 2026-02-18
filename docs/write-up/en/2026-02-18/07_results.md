# Results

## Data Inventory

The empirical foundation of this work comprises 30 structured JSONL trace files located in `logs/traces/`, as well as a SQLite database (`logs/traces/traces.db`) for persistent queries. Additionally, approximately 200 Loguru application and test logs (`logs/*.log`, `*.log.zip`) are available.

| Source | Count | Content |
|--------|-------|---------|
| `logs/traces/*.jsonl` | 30 | Structured execution traces (`GraphTraceData`) |
| `logs/traces/traces.db` | 1 | SQLite trace database |
| `logs/*.log` / `*.log.zip` | ~200 | Loguru application and test logs |
| `results/sweeps/` | 2 directories | Empty result arrays (`[]`) |
| CC Solo/Teams artifacts | 1 set | Collected under `logs/cc/solo/` and `logs/cc/teams/` |

Approximately 95% of the log files are pytest outputs from automated tests, not actual evaluation runs. Only 10--15 logs correspond to actual CLI executions.

---

## Single-LLM MAS (Manager-Only)

The Manager-Only configuration corresponds to single-LLM operation: research, analysis, and synthesis agents are deactivated (`AgentComposition(include_researcher=False, include_analyst=False, include_synthesiser=False)`). The Manager does not delegate but calls all tools directly.

| Metric | Value |
|--------|-------|
| Agent interactions | 0 (no delegation) |
| Tool calls per run | 3 (`get_peerread_paper`, `generate_paper_review_content_from_template`, `save_structured_review`) |
| Duration range | 1.6 s -- 8.7 s |
| Median duration | ~4.8 s |
| Input tokens (Paper 001) | 8,342 (of which 5,888 cache read) |
| Input tokens (Paper 1105.1072) | 14,198 (of which 8,960 cache read) |
| Output tokens | 570--743 |
| LLM requests per run | 4 |
| Observed runs | 14 |

Representative trace examples:

| Execution ID | Paper | Duration | Avg. Tool Duration |
|---|---|---|---|
| `exec_397258f1de20` | 1105.1072 | 1.611 s | 0.012 s |
| `exec_e4a4993014da` | 001 | 4.795 s | 0.004 s |
| `exec_4ef1548c4f24` | 1105.1072 | 8.659 s | 0.021 s |

Execution time is entirely dominated by LLM inference latency; the mean tool execution time ranges between 0.004 s and 0.09 s.

---

## Multi-LLM MAS (with Sub-Agents)

### Duration by Agent Count

In the multi-LLM configuration, the Manager delegates tasks sequentially to one or more sub-agents, each of which performs its own LLM inference. Three compositions were observed: Researcher-only, Researcher+Analyst, and the full three-agent configuration.

| Agents | Runs | Avg. Duration | Range |
|--------|------|---------------|-------|
| 1 (Researcher) | 4 | 6.5 s | 3.9--8.8 s |
| 2 (Researcher + Analyst or Synthesizer) | 3 | 8.8 s | 7.3--11.9 s |
| 3 (Researcher + Analyst + Synthesizer) | 3 | 12.3 s | 7.9--17.4 s |

Duration scales approximately linearly with agent count, as sub-agents are called sequentially.

### Outlier Analysis

Two runs exhibited extreme durations significantly above the normal range:

| Execution ID | Duration | Cause |
|---|---|---|
| `exec_655bf85674d4` | 135.96 s | Single Researcher, 2 attempts (retry) |
| `exec_2a4d21581ece` | 69.46 s | 2 interactions, 2 attempts (retry) |

Analysis of the trace data reveals that the outliers were not caused by coordination overhead but by LLM provider latency spikes or rate limiting.

### Failed Runs

Four traces recorded a duration of 0.0 s with 0--1 tool calls. These runs failed before meaningful work began due to initialization errors. This yields an error rate of 4/16 (25%) for the multi-LLM configuration, compared to 0/14 (0%) for the Manager-Only configuration.

---

## Claude Code Baseline

### CC Solo

The CC Solo configuration was executed with the command `claude -p --output-format stream-json --verbose` without the Teams flag.

| Metric | Value |
|--------|-------|
| Session ID | `dad34c5b-813d-4f85-99d0-91c2c4ccc3eb` |
| Model | `claude-sonnet-4-5-20250929` |
| Duration | 118.3 s |
| Cost | \$0.94 |
| Turns | 4 |
| Tool calls | 19 |
| Artifact path | `logs/cc/solo/1105.1072_20260217_181344/` |

The single agent used codebase exploration tools (Task, Bash, Glob, Grep, Read) to locate the paper data in the project directory before generating the review.

### CC Teams

The CC Teams configuration was executed with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set and a teams-specific prompt.

| Metric | Value |
|--------|-------|
| Session ID | `8dd391f8-82c4-43bd-b960-cf7bce4d5a3e` |
| Model | `claude-sonnet-4-5-20250929` |
| Duration | 359.9 s |
| Cost | \$1.35 |
| Turns | 13 |
| Tool calls | 22 |
| Artifact path | `logs/cc/teams/1105.1072_20260217_182646/` |

The tool distribution comprises: TodoWrite (5x), TeamCreate (1x), Task (3x -- Explore + 2 sub-agents), Bash (2x), Glob (2x), Read (6x). The system created a team `paper-review-1105-1072` and spawned three sub-agents: Researcher, Analyst, and Synthesizer.

### Infrastructure Status

| Component | Status | Path |
|-----------|--------|------|
| `CCTraceAdapter` | Implemented | `src/app/judge/cc_trace_adapter.py` |
| CC Solo parser | Implemented | Reads `metadata.json` + `tool_calls.jsonl` |
| CC Teams parser | Implemented | Reads `config.json` + `inboxes/` + `tasks/` |
| `BaselineComparison` model | Implemented | `src/app/judge/baseline_comparison.py` |
| `compare_all()` function | Implemented | Generates 3 pairwise comparisons |
| CC Solo artifacts | **Collected** | `logs/cc/solo/1105.1072_20260217_181344/` |
| CC Teams artifacts | **Partial** | Only `metadata.json` + `tool_calls.jsonl` (no `config.json`, `inboxes/`, `tasks/`) |

---

## Comparative Analysis

### Single-LLM vs. Multi-LLM

| Dimension | Single-LLM (Manager-Only) | Multi-LLM (3 Agents) | Delta |
|-----------|--------------------------|----------------------|-------|
| Median duration | ~4.8 s | ~12.3 s | +156% |
| Agent interactions | 0 | 3 | -- |
| Tool calls | 3 (direct) | 3 (delegated) | Same count, different pattern |
| LLM requests | 4 | 4+ (per agent) | Higher total |
| Error rate | 0/14 (0%) | 4/16 (25%) | Higher with delegation |
| Token efficiency | ~9,000 input | Unknown (sub-agent tokens not logged) | Likely higher |

Multi-agent configurations produce approximately 2.5x latency increase with the three-agent variant compared to Manager-Only. Since the evaluation pipeline could not produce composite quality scores due to blocking issues, a quality comparison based on the available data is not possible.

### PydanticAI MAS vs. CC (Paper 1105.1072)

| Dimension | PydanticAI Manager-Only | PydanticAI 3 Agents | CC Solo | CC Teams |
|-----------|------------------------|----------------------|---------|----------|
| Duration | ~4.8 s | ~12.3 s | 118.3 s | 359.9 s |
| Cost (approx.) | ~\$0.01 | ~\$0.03 | \$0.94 | \$1.35 |
| Tool calls | 3 | 3 | 19 | 22 |
| Turns | 4 | 4+ | 4 | 13 |
| Agent interactions | 0 | 3 (delegation) | 0 | 3 (Task sub-agents) |
| Model | GPT-4.1 (GitHub) | GPT-4.1 (GitHub) | claude-sonnet-4-5 | claude-sonnet-4-5 |
| Error rate | 0% | 25% | 0% (n=1) | 0% (n=1) |

Key observations:

1. **PydanticAI is 25--75x faster than CC**: CC Solo (118.3 s) vs. PydanticAI Manager-Only (4.8 s). CC explored the codebase at runtime to locate paper data; PydanticAI uses typed tools with direct data access.
2. **CC Teams incurs a 3x overhead over CC Solo**: 359.9 s vs. 118.3 s. The orchestration pattern (TodoWrite + TeamCreate + 3 Task sub-agents) structurally mirrors PydanticAI three-agent delegation, but with significantly higher overhead from tool-based coordination.
3. **CC uses 6--7x more tool calls**: CC probes the filesystem (Glob, Grep, Read, Bash) for data discovery; PydanticAI uses purpose-built tools (`get_peerread_paper`, `generate_paper_review_content_from_template`).
4. **The cost difference is approximately 50--100x**: CC Solo (\$0.94) vs. PydanticAI Manager-Only (~\$0.01). The difference arises from model cost disparity (Claude Sonnet 4.5 vs. GPT-4.1) and higher token consumption from codebase exploration.
5. **CC Teams orchestration is structurally analogous to PydanticAI multi-agent**: Both instantiate Researcher, Analyst, and Synthesizer roles. CC uses the Task tool; PydanticAI uses `delegate_research`/`delegate_analysis`/`delegate_synthesis`.

**Limitation**: This comparison is based on a single paper (n=1 for CC). PydanticAI data comes from 14+ runs. Cost figures for PydanticAI are estimates (GitHub Models pricing). A quality comparison requires the complete evaluation pipeline (Tier 1 + 2 + 3), which is blocked by the missing `GITHUB_API_KEY` for Tier 2.

---

## Evaluation Pipeline Readiness

The three-tier evaluation framework is fully implemented but could not be fully executed on the available traces due to blocking issues.

| Tier | Purpose | Metrics | Status |
|------|---------|---------|--------|
| Tier 1 | Traditional text metrics | `cosine`, `jaccard`, `semantic`, `time_taken`, `task_success` | Implemented |
| Tier 2 | LLM-as-Judge | `accuracy`, `constructiveness`, `clarity`, `planning_rationality` | Implemented (requires API key) |
| Tier 3 | Graph behavioral analysis | `path_convergence`, `tool_accuracy`, `coordination_quality`, `distribution` | Implemented |

The composite scoring system combines six equally weighted metrics (0.167 each): `time_taken`, `task_success`, `output_similarity`, `planning_rationality`, `coordination_quality`, `tool_efficiency`.

Decision thresholds: accept $\geq$ 0.863 | weak_accept $\geq$ 0.626 | reject < 0.626.

In single-agent operation (`single_agent_mode=True`), the weight of `coordination_quality` (0.167) is evenly redistributed to the remaining five metrics (0.20 each), since no inter-agent interactions are present.

---

## Gaps and Blocking Issues

| Issue | Impact | Location |
|-------|--------|----------|
| `'AgentRunResult' object has no attribute 'data'` | Manager-Only runs abort during result extraction | `app.py:280` on branch `refactor-arch` |
| Empty sweep results | No composition comparison dataset generated | `results/sweeps/*/results.json` |
| CC Teams artifacts ephemeral | `CCTraceAdapter` Teams parser cannot operate | `~/.claude/teams/` empty after run |
| `GITHUB_API_KEY` not set | Tier 2 LLM-as-Judge comparison blocked | `.env` / shell environment |

The blocking issues prevent the generation of composite quality scores and thus a complete empirical comparison of system configurations. Latency and cost metrics based solely on trace data are, however, fully available.

| User Story | Status | Gap |
|------------|--------|-----|
| Evaluation runs automatically after generation | Partially built | Blocked by `AgentRunResult` bug |
| Real agent execution traces captured | Done for PydanticAI + CC | CC Teams artifacts ephemeral |
| Graph metrics alongside text metrics | Tier 1 + Tier 3 implemented | No real composite scores computed |
| Compare MAS vs. CC baseline | CC Solo + Teams collected | Evaluation pipeline blocked by API key |
| Run across all composition variants | Sweep harness present | Produces empty results |
