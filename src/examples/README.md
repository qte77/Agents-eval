# Examples

Self-contained demonstrations of Agents-eval Sprint 5-6 features using current APIs.

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

## Integration with CLI and GUI

These examples use the same `EvaluationPipeline`, `JudgeSettings`, and
`CCTraceAdapter` as the main application.

| Example topic | CLI equivalent | GUI page |
|---|---|---|
| Run evaluation | `make app_cli ARGS="--paper-id=123"` | App → Run |
| Settings customization | `JUDGE_TIER2_PROVIDER=anthropic make app_cli ...` | App → Settings |
| Engine comparison | `make app_sweep ARGS="--engine=cc"` | App → Run (engine selector) |

For full usage, see the [main README](../../README.md) and the
[CLI reference](../../CONTRIBUTING.md).
