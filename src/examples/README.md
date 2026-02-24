# Examples

Self-contained demonstrations of Agents-eval Sprint 5-11 features using current APIs.

## Examples

### `basic_evaluation.py` — Three-tier evaluation with synthetic data

Demonstrates the `EvaluationPipeline` with realistic paper/review data.

**What it shows:**

- Constructing `GraphTraceData` for a 3-agent MAS execution
- Running Tier 1 (Traditional Metrics) + Tier 3 (Graph Analysis)
- Interpreting `CompositeResult` (score, recommendation, tier breakdown)

**Usage:**

```bash
uv run python src/examples/basic_evaluation.py
```

**Prerequisites:** None for Tier 1 + Tier 3. Add `OPENAI_API_KEY` to `.env` and set
`tiers_enabled=[1, 2, 3]` to also run Tier 2 (LLM-as-Judge).

---

### `judge_settings_customization.py` — JudgeSettings configuration patterns

Demonstrates how to configure the evaluation pipeline via `JudgeSettings`.

**What it shows:**

- Environment variable overrides (`JUDGE_` prefix, e.g. `JUDGE_TIER2_PROVIDER=anthropic`)
- Timeout adjustment for slow/fast environments
- Tier selection (e.g. disable Tier 2 to skip LLM calls)
- Provider switching (OpenAI → Anthropic → GitHub)
- Composite score threshold customization

**Usage:**

```bash
uv run python src/examples/judge_settings_customization.py
```

**Prerequisites:** None — JudgeSettings is pure Pydantic, no API key required.

---

### `engine_comparison.py` — MAS vs Claude Code comparison

Demonstrates comparing evaluation scores between MAS and Claude Code engines.

**What it shows:**

- Multi-LLM MAS evaluation (synthetic 3-agent trace)
- Single-LLM MAS baseline evaluation
- Loading CC artifacts via `CCTraceAdapter` (optional, requires prior collection)
- Side-by-side score comparison

**Usage:**

```bash
uv run python src/examples/engine_comparison.py
```

**Prerequisites:**

For MAS-only comparison: None (uses synthetic traces).

For CC comparison, collect artifacts first:

```bash
# Solo mode
bash scripts/collect-cc-traces/collect-cc-solo.sh

# Teams mode
bash scripts/collect-cc-traces/collect-cc-teams.sh
```

Artifacts are read from `~/.claude/teams/<run-name>/` (teams) or the path you
specify. Set the `cc_artifacts_dir` variable in the script if your path differs.

---

### `mas_single_agent.py` — MAS manager-only mode

Demonstrates the minimal MAS execution mode where only the manager agent runs
(no sub-agents). All `include_*` flags are `False`.

**What it shows:**

- Running `app.main()` in manager-only (single-agent) mode
- How to set `include_researcher=False`, `include_analyst=False`, `include_synthesiser=False`
- Interpreting `CompositeResult` from the single-agent run

**Usage:**

```bash
uv run python src/examples/mas_single_agent.py
```

**Prerequisites:** API key for the default LLM provider in `.env`. PeerRead sample
dataset downloaded (`make setup_dataset`).

---

### `mas_multi_agent.py` — MAS full 4-agent delegation

Demonstrates the full MAS execution mode with manager delegating to all three
sub-agents: researcher, analyst, and synthesiser.

**What it shows:**

- Running `app.main()` with all `include_*` flags set to `True`
- Full 4-agent delegation workflow (manager → researcher → analyst → synthesiser)
- Composite score comparison vs. single-agent mode

**Usage:**

```bash
uv run python src/examples/mas_multi_agent.py
```

**Prerequisites:** API key for the default LLM provider in `.env`. PeerRead sample
dataset downloaded (`make setup_dataset`).

---

### `cc_solo.py` — Claude Code solo (headless) mode

Demonstrates running Claude Code in solo headless mode via `run_cc_solo()` with
a `check_cc_available()` guard and `build_cc_query()` for query construction.

**What it shows:**

- Checking CC availability with `check_cc_available()`
- Building a query with `build_cc_query()`
- Invoking `run_cc_solo()` and inspecting the `CCResult`
- Graceful handling when `claude` CLI is not on PATH

**Usage:**

```bash
uv run python src/examples/cc_solo.py
```

**Prerequisites:** Claude Code CLI installed (`claude --version`) and authenticated
(`claude` interactive session). No LLM API keys required.

---

### `cc_teams.py` — Claude Code agent-teams mode

Demonstrates running Claude Code in agent-teams orchestration mode via
`run_cc_teams()`, which sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

**What it shows:**

- Building a teams-mode query with `build_cc_query(cc_teams=True)`
- Invoking `run_cc_teams()` and inspecting `TeamCreate`/`Task` events in `CCResult`
- How team artifacts are captured from the live JSONL stream
- Graceful handling when `claude` CLI is not on PATH

**Usage:**

```bash
uv run python src/examples/cc_teams.py
```

**Prerequisites:** Claude Code CLI installed (`claude --version`) and authenticated.
Teams mode requires Claude Max or API subscription with agent teams enabled.

---

### `sweep_benchmark.py` — Composition sweep benchmark

Demonstrates running a multi-composition sweep using `SweepRunner` and
`SweepConfig`. Evaluates 3 compositions on 1 paper with 1 repetition.

**What it shows:**

- Configuring `SweepConfig` with multiple `AgentComposition` instances
- Running `SweepRunner.run()` across all compositions
- Using a temporary directory for `output_dir` (auto-cleaned up)
- Comparing composite scores across compositions

**Usage:**

```bash
uv run python src/examples/sweep_benchmark.py
```

**Prerequisites:** API key for the default LLM provider in `.env`. PeerRead sample
dataset downloaded (`make setup_dataset`). Runs 3 LLM calls (one per composition).

---

## Integration with CLI and GUI

These examples use the same `EvaluationPipeline`, `JudgeSettings`, `CCTraceAdapter`,
`SweepRunner`, and `app.main()` as the main application.

| Example topic | CLI equivalent | GUI page |
|---|---|---|
| Run evaluation | `make app_cli ARGS="--paper-id=123"` | App → Run |
| Settings customization | `JUDGE_TIER2_PROVIDER=anthropic make app_cli ...` | App → Settings |
| Engine comparison | `make app_sweep ARGS="--engine=cc"` | App → Run (engine selector) |
| MAS single-agent | `make app_cli ARGS="--paper-id=1105.1072"` | App → Run |
| MAS multi-agent | `make app_cli ARGS="--paper-id=1105.1072 --researcher --analyst --synthesiser"` | App → Run |
| CC solo | `make app_cli ARGS="--engine=cc --paper-id=1105.1072"` | App → Run |
| CC teams | `make app_cli ARGS="--engine=cc --cc-teams --paper-id=1105.1072"` | App → Run |
| Sweep benchmark | `make app_sweep ARGS="--paper-id=1105.1072 --repetitions=1"` | App → Sweep |

For full usage, see the [main README](../../README.md) and the
[CLI reference](../../CONTRIBUTING.md).
