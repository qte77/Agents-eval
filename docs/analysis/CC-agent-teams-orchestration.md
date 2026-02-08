---
title: CC Agent Teams Orchestration
source: https://code.claude.com/docs/en/agent-teams
purpose: Analysis of Claude Code Agent Teams feature for multi-session orchestration, assessing fit for parallel code review, cross-layer implementation, and adversarial debugging within Agents-eval.
created: 2026-02-08
updated: 2026-02-08
---

**Status**: Experimental (disabled by default)

## What Agent Teams Offer

A built-in Claude Code feature for coordinating multiple independent CC sessions
with:

- **Lead/teammate hierarchy** with shared task list and mailbox messaging
- **Inter-agent communication** — teammates can message each other directly
- **Parallel execution** — each teammate has its own context window
- **Task dependency management** with automatic unblocking
- **Quality gates** via `TeammateIdle` and `TaskCompleted` hooks
- **Delegate mode** — restricts lead to coordination only
- **Plan approval** — teammates must get lead sign-off before implementing

### How It Works

- One session acts as team lead, spawns teammates, coordinates work
- Each teammate is a full independent Claude Code instance
- Shared task list with pending/in-progress/completed states and dependency tracking
- Teammates load project context (CLAUDE.md, MCP servers, skills) automatically
- Lead's conversation history does NOT carry over to teammates
- Display modes: in-process (single terminal) or split panes (tmux/iTerm2)

### Configuration

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Agent Teams vs Subagents (Task tool)

| Aspect | Subagents | Agent Teams |
| -------- | ----------- | ------------- |
| Context | Own window; results return to caller | Own window; fully independent |
| Communication | Report back to main agent only | Teammates message each other directly |
| Coordination | Main agent manages all work | Shared task list with self-coordination |
| Best for | Focused tasks where only the result matters | Complex work requiring discussion and collaboration |
| Token cost | Lower: results summarized back | Higher: each teammate is a separate instance |

## Relevance to This Project

### High Relevance Areas

| Use Case | Fit | Rationale |
| -------- | --- | --------- |
| Parallel code review (security + performance + coverage) | Strong | Existing `reviewing-code` skill; agent teams let 3 reviewers run simultaneously with different lenses |
| Cross-layer feature implementation (backend + tests) | Strong | Enforces role separation (architect/developer/reviewer) that AGENTS.md mandates |
| Research + competing hypotheses debugging | Strong | Adversarial debate pattern addresses anchoring bias in single-agent investigation |

### Overlaps with Current Setup

- **Subagents (Task tool)**: Already used for focused, fire-and-forget work. Agent
  teams replace these only when inter-agent communication is needed.
- **Ralph loop**: Autonomous sequential execution. Agent teams are parallel. These
  are complementary, not competing.
- **Skills**: Teammates load CLAUDE.md + skills automatically, so existing skills
  work without modification.

## Key Limitations

1. **No session resumption** — in-process teammates are lost on `/resume`. Problem
   for long-running Ralph-style workflows.
2. **Task status can lag** — teammates sometimes don't mark tasks complete, blocking
   dependents. Requires manual intervention.
3. **No nested teams** — teammates can't spawn their own teams, limiting depth of
   orchestration.
4. **One team per session** — can't run multiple independent teams concurrently.
5. **Permissions set at spawn** — can't give architect teammates read-only and
   developer teammates write access separately at spawn time.
6. **Significantly higher token cost** — each teammate is a separate Claude instance.
7. **Experimental, disabled by default** — not stable enough for production workflows.
8. **Split panes require tmux or iTerm2** — not supported in VS Code integrated
   terminal.

## Simple Mode — Single CC Session

For most day-to-day development on Agents-eval, a single CC session with skills
handles the full workflow sequentially: research → design → implement → test →
review.

### When to Use

- **Prompt engineering** — iterating on agent prompts in `config_chat.json` where
  each change needs evaluation feedback before the next
- **Pipeline debugging** — tracing a failure through `evaluation_pipeline.py` where
  full conversation context of prior steps is essential
- **Individual tier improvement** — tuning a single tier's metrics (e.g., Tier 1
  traditional metrics or Tier 2 LLM-as-Judge prompts)
- **Focused single-file changes** — adding a new data model, fixing a utility
  function, writing tests for one module
- **Test writing** — creating or updating tests where you need to reference the
  implementation and test file together

### How It Works in Practice

1. Use `researching-codebase` skill to gather context in isolation
2. Use `designing-backend` skill if architectural decisions are needed
3. Use `implementing-python` skill for code changes
4. Use `testing-python` skill for test coverage
5. Use `reviewing-code` skill for quality validation
6. Run `make validate` to confirm everything passes

### Advantages

- Full conversation context retained across all phases — no information lost
  between research, implementation, and testing
- Lower token cost — one session vs multiple independent instances
- Real-time user feedback loop — user can steer direction at each step
- Skills load automatically and enforce AGENTS.md compliance

### Limitations

- Sequential execution — can't work on multiple files simultaneously
- Single perspective — no adversarial review or competing approaches
- Context window pressure on large tasks — may need `compacting-context` skill

## Agent Teams Mode — Researcher Team for Review Generation

For work that benefits from parallel execution or multiple perspectives, Agent
Teams maps naturally to this project's multi-agent review generation architecture.

### Mapping to Project Architecture

| Agent Teams Role | Project Equivalent | Responsibility |
| ---------------- | ------------------ | -------------- |
| Lead | Manager agent | Orchestrates work, defines tasks, reviews results |
| Teammate A | Researcher track | Paper analysis, data extraction, prompt development |
| Teammate B | Analyst track | Evaluation metrics, scoring pipeline, statistical analysis |
| Teammate C | Synthesizer track | Review generation quality, output formatting, integration |

### Concrete Use Cases

**Parallel pipeline component development** — three teammates work on different
tiers simultaneously:

- Teammate 1: improves Tier 1 traditional metrics (BLEU, ROUGE) in
  `evaluation_pipeline.py`
- Teammate 2: refines Tier 2 LLM-as-Judge prompts and scoring rubrics
- Teammate 3: develops Tier 3 graph analysis using NetworkX integration
- Lead: coordinates dependencies, ensures changes don't conflict

**Parallel code review with different lenses:**

- Security reviewer examines `agent_system.py` for prompt injection, API key
  handling, and input validation
- Quality reviewer examines `evaluation_pipeline.py` for error handling,
  performance bottlenecks, and code clarity
- Coverage reviewer examines `tests/` for gaps, edge cases, and mock strategy
- Lead: aggregates findings into a single prioritized action list

**Adversarial prompt testing** — teammates generate reviews with different agent
configurations and compare quality:

- Teammate 1: runs review generation with current prompts from `config_chat.json`
- Teammate 2: runs same papers with modified temperature/system prompt variations
- Teammate 3: evaluates both outputs through the three-tier pipeline
- Lead: compares results, identifies which configuration produces higher-quality
  reviews

### When to Use Over Simple Mode

- Work spans 3+ files with independent changes that don't block each other
- Multiple review perspectives are needed (security + performance + coverage)
- Comparing competing approaches where single-session anchoring bias is a risk
- Large refactoring where parallel testing of different components saves time

### Practical Setup

```bash
# Enable agent teams
# In .claude/settings.json or .claude/settings.local.json:
# "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }

# Start a team session — lead spawns teammates with specific roles
# Use delegate mode to prevent lead from implementing directly
# Pre-approve common operations (make validate, pytest) to reduce prompts
```

## Benchmarking PydanticAI MAS Against CC-Style Orchestration Baselines

The PydanticAI multi-agent system (Manager → Researcher → Analyst → Synthesizer)
is the project's primary approach for generating paper reviews. To measure how
well this architecture performs, two comparison baselines modeled after CC
orchestration patterns can be implemented **within `src/`** using PydanticAI
itself. This keeps the entire benchmark automated, batchable, and evaluated
through the same three-tier pipeline.

### Why Compare

The PydanticAI MAS makes specific architectural choices: tool-based delegation,
sequential workflow with an approval loop, structured Pydantic outputs, and
multi-model support. Comparing against simpler and differently-structured
baselines reveals whether these choices actually improve review quality, or
whether simpler orchestration produces equivalent results at lower cost.

### Baseline Definitions

All three approaches are implemented in Python using PydanticAI and run from
`src/`. The CC-style baselines replicate the orchestration patterns of CC Single
Session and CC Agent Teams, but as programmatic agents — not actual CC sessions.

#### Primary: PydanticAI MAS (current)

The existing system in `src/app/agents/`:

- Manager delegates to sub-agents via `@manager_agent.tool` decorators
  (`agent_system.py:127-183`)
- Sequential: research → analysis → (approval loop) → synthesis
- Structured outputs enforced by Pydantic models (`ResearchResult`,
  `AnalysisResult`, `ResearchSummary`)
- Token tracking via `RunContext.usage`, observability via Opik
- Configurable models per role via `config_chat.json` and `AgentFactory`

```python
# Current flow — manager delegates via tools
@manager_agent.tool
async def delegate_research(ctx: RunContext[None], query: str) -> ResearchResult:
    result = await research_agent.run(query, usage=ctx.usage)
    return result.output

@manager_agent.tool
async def delegate_analysis(ctx: RunContext[None], query: str) -> AnalysisResult:
    result = await analysis_agent.run(query, usage=ctx.usage)
    return result.output

@manager_agent.tool
async def delegate_synthesis(ctx: RunContext[None], query: str) -> ResearchSummary:
    result = await synthesis_agent.run(query, usage=ctx.usage)
    return result.output
```

#### Baseline 1: Single-Agent (CC Single Session pattern)

Simulates what a single CC session does — one agent receives the full paper and
generates a complete review in a single pass. No delegation, no sub-agents, no
approval loop. This isolates the value of multi-agent orchestration by removing
it entirely.

```python
from pydantic_ai import Agent

from app.data_models.peerread_models import GeneratedReview

# Single agent — full paper in, structured review out
single_agent = Agent(
    model=model,
    output_type=GeneratedReview,
    system_prompt=(
        "You are a scientific paper reviewer. Read the paper and produce a "
        "structured review covering summary, strengths, weaknesses, questions, "
        "and an overall recommendation."
    ),
)

async def run_single_baseline(paper_content: str) -> GeneratedReview:
    """CC Single Session equivalent — one agent, one pass."""
    result = await single_agent.run(paper_content)
    return result.output
```

This baseline reuses the same `GeneratedReview` output type as the MAS, so
Tier 1 metrics compare like-for-like. Tier 3 traces are minimal (single agent,
no delegation graph).

#### Baseline 2: Parallel Independent Agents (CC Agent Teams pattern)

Simulates CC Agent Teams — multiple independent agents run in parallel with
separate contexts, then a coordinator merges their outputs. Each agent sees only
the paper (no access to other agents' outputs during generation), mirroring how
CC teammates each get their own context window.

```python
import asyncio

from pydantic import BaseModel
from pydantic_ai import Agent

from app.data_models.peerread_models import GeneratedReview


class ResearchFindings(BaseModel):
    """Researcher teammate output."""
    key_claims: list[str]
    methodology_summary: str
    related_work: list[str]


class AnalystAssessment(BaseModel):
    """Analyst teammate output."""
    strengths: list[str]
    weaknesses: list[str]
    validity_concerns: list[str]


# Independent agents — no shared context during generation
researcher = Agent(
    model=model,
    output_type=ResearchFindings,
    system_prompt="Extract key claims, methodology, and related work from the paper.",
)
analyst = Agent(
    model=model,
    output_type=AnalystAssessment,
    system_prompt="Evaluate strengths, weaknesses, and validity of the paper.",
)
synthesizer = Agent(
    model=model,
    output_type=GeneratedReview,
    system_prompt=(
        "Combine the research findings and analyst assessment into a "
        "structured review."
    ),
)


async def run_teams_baseline(paper_content: str) -> GeneratedReview:
    """CC Agent Teams equivalent — parallel agents, then synthesis."""
    # Teammates run in parallel (like CC Agent Teams independent sessions)
    research_task = researcher.run(paper_content)
    analysis_task = analyst.run(paper_content)
    research_result, analysis_result = await asyncio.gather(
        research_task, analysis_task, return_exceptions=True,
    )

    # Handle failures — fall back to empty findings
    findings = (
        research_result.output
        if not isinstance(research_result, Exception)
        else ResearchFindings(key_claims=[], methodology_summary="", related_work=[])
    )
    assessment = (
        analysis_result.output
        if not isinstance(analysis_result, Exception)
        else AnalystAssessment(strengths=[], weaknesses=[], validity_concerns=[])
    )

    # Synthesizer merges (like CC lead aggregating teammate results)
    synthesis_input = (
        f"Research findings:\n{findings.model_dump_json()}\n\n"
        f"Analyst assessment:\n{assessment.model_dump_json()}\n\n"
        f"Paper:\n{paper_content}"
    )
    result = await synthesizer.run(synthesis_input)
    return result.output
```

Key differences from the PydanticAI MAS:

- **No approval loop** — analyst output goes straight to synthesis without the
  manager deciding whether to re-trigger research
- **Parallel execution** — researcher and analyst run concurrently via
  `asyncio.gather`, not sequentially via tool calls
- **No shared context** — each agent sees only the paper, not each other's
  intermediate output (until the synthesis step)
- **Coordinator is an agent, not an LLM-driven manager** — the synthesis step
  is deterministic (always runs after gather), not decided by the manager LLM

### Running the Benchmark From `src/`

All three approaches produce a `GeneratedReview` and can be scored through
`evaluation_pipeline.evaluate_comprehensive()`. The benchmark orchestration
fits into the existing `orchestration.py` patterns:

```python
from app.agents.agent_system import run_manager
from app.agents.orchestration import AgentOrchestrator
from app.evals.evaluation_pipeline import EvaluationPipeline
from app.tools.peerread_tools import query_peerread_papers


async def run_benchmark(papers: list, pipeline: EvaluationPipeline):
    """Run all three approaches against the same papers and compare scores."""
    orchestrator = AgentOrchestrator()

    for paper in papers:
        orchestrator.log_step("benchmark_paper", {"id": paper.paper_id})

        # Approach A: PydanticAI MAS
        mas_review = await run_manager(query=paper.content, ...)
        mas_score = await pipeline.evaluate_comprehensive(
            paper, mas_review, paper.reference_reviews,
        )

        # Baseline 1: Single-agent (CC Single pattern)
        single_review = await run_single_baseline(paper.content)
        single_score = await pipeline.evaluate_comprehensive(
            paper, single_review, paper.reference_reviews,
        )

        # Baseline 2: Parallel agents (CC Agent Teams pattern)
        teams_review = await run_teams_baseline(paper.content)
        teams_score = await pipeline.evaluate_comprehensive(
            paper, teams_review, paper.reference_reviews,
        )

        orchestrator.log_step("benchmark_scores", {
            "paper_id": paper.paper_id,
            "mas": mas_score,
            "single": single_score,
            "teams": teams_score,
        })
```

### What Each Tier Measures in the Benchmark

| Tier | What It Reveals About the MAS |
| ---- | ----------------------------- |
| **Tier 1** — Traditional metrics | Does multi-agent delegation produce reviews that are closer to reference reviews than a single-pass agent? |
| **Tier 2** — LLM-as-Judge | Does the analyst approval loop improve technical accuracy and constructiveness vs no validation (single) or parallel-only validation (teams)? |
| **Tier 3** — Graph analysis | How much coordination overhead does the delegation chain add? Is the MAS's path convergence efficient or wasteful compared to simpler topologies? |

### Expected Results

| Dimension | PydanticAI MAS | Single-Agent Baseline | Parallel-Agents Baseline |
| --------- | ------------- | -------------------- | ------------------------ |
| **Tier 1 score** | Highest — approval loop refines output before synthesis | Lower — no refinement step | Medium — parallel inputs to synthesizer |
| **Tier 2 score** | Highest — analyst validates before synthesis | Lower — single-pass, no validation | Comparable — independent analyst assessment |
| **Tier 3 score** | Full graph data — delegation chain is traceable | Minimal — single node, no graph | Medium — parallel edges, gather node |
| **Token cost** | Baseline (1x) | Lowest (~0.5x, one agent pass) | Higher (~1.5x, parallel + synthesis) |
| **Latency** | Highest — sequential delegation chain | Lowest — single pass | Medium — parallel phase + synthesis phase |

**Hypothesis**: the MAS's approval loop (analyst can reject and re-trigger
research) is the key differentiator for Tier 2 scores. If the single-agent
baseline achieves comparable Tier 2 scores, the multi-agent overhead is not
justified for the review generation task. If the parallel baseline matches MAS
on Tier 2 but at lower latency, the sequential delegation pattern should be
reconsidered in favor of parallel-then-merge.

### Key Files for Implementation

| File | Role in Benchmark |
| ---- | ----------------- |
| `agent_system.py` | Primary MAS — `run_manager()` entry point |
| `orchestration.py` | `AgentOrchestrator` for benchmark logging, `parallel_workflow` for teams baseline |
| `agent_factories.py` | `AgentFactory` creates agents for baselines with same model config |
| `evaluation_pipeline.py` | `evaluate_comprehensive()` scores all three approaches identically |
| `peerread_models.py` | `GeneratedReview` — shared output type across all approaches |
| `peerread_tools.py` | `query_peerread_papers` — selects test set |
| `config_chat.json` | System prompts — MAS uses role-specific prompts, baselines use review-focused prompts |
| `config_eval.json` | Tier weights and fallback strategy for fair scoring |

## Tracing & Observability for the Benchmark

### The Observability Gap

The PydanticAI MAS has full Opik tracing — agent delegation
calls, tier execution metadata, and timing — via `track()`
wrappers in `opik_instrumentation.py` and
`evaluation_pipeline.py`. The CC-style baselines need
equivalent observability. Three approaches exist; OTel is
the best fit because the infrastructure is already in place.

### Approach 1 (Recommended): CC OTel → Opik

**Why this fits:**

1. **Already configured** — `.claude/settings.json` has
   three OTEL env vars (lines 9-11), currently disabled:

   ```json
   "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "",
   "OTEL_EXPORTER_OTLP_PROTOCOL": "",
   "OTEL_LOGS_EXPORTER": ""
   ```

2. **Richest data** — CC's OTel export includes:
   - **Metrics**: `claude_code.token.usage`
     (input/output/cache), `claude_code.cost.usage` (USD),
     `claude_code.session.count`,
     `claude_code.active_time.total`
   - **Events/Logs**: `claude_code.tool_result`
     (tool_name, success, duration_ms),
     `claude_code.api_request`
     (model, cost_usd, tokens, duration_ms),
     `claude_code.api_error`, `claude_code.tool_decision`

3. **Reuses existing Opik ClickHouse** — the OTel Collector
   forwards to the same ClickHouse instance Opik uses

#### Settings Changes Required

**Current vars to enable** (in `.claude/settings.json`):

- `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL`:
  `""` → `"grpc"` — metrics export protocol
- `OTEL_EXPORTER_OTLP_PROTOCOL`:
  `""` → `"grpc"` — general OTLP protocol
- `OTEL_LOGS_EXPORTER`:
  `""` → `"otlp"` — logs/events exporter type

**New vars to add:**

- `CLAUDE_CODE_ENABLE_TELEMETRY`: `"1"`
  — master switch (required before OTEL vars work)
- `OTEL_METRICS_EXPORTER`: `"otlp"`
  — metrics exporter type
- `OTEL_EXPORTER_OTLP_ENDPOINT`:
  `"http://localhost:4317"` — OTel Collector gRPC

**Optional tuning:**

- `OTEL_LOG_TOOL_DETAILS`: `"1"`
  — include MCP/tool/skill names
- `OTEL_LOG_USER_PROMPTS`: `"1"`
  — include prompt content (off by default)
- `OTEL_RESOURCE_ATTRIBUTES`:
  `"project=peerread-benchmark"` — Opik filter tag
- `OTEL_METRIC_EXPORT_INTERVAL`: `"10000"`
  — 10s intervals for testing (default 60s)

Full enabled config:

```json
"env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
    "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "grpc"
}
```

#### Infrastructure Addition

- Add an OTel Collector container to
  `docker-compose.opik.yaml` (or separate compose)
- Collector config: receive OTLP on `:4317`,
  export to Opik ClickHouse on `:8123`

### Approach 2: CC Hooks → Opik Manual Traces

A Python hook script for `PostToolUse` that calls
`opik.trace()` directly.

- Lower setup — single script in `.claude/hooks/`
- Coarser data — tool-level only, no token/cost
- No OTel Collector dependency
- Sufficient for coarse Tier 3 execution graphs

```python
#!/usr/bin/env python3
"""CC PostToolUse hook — logs tool calls to Opik."""
import json
import sys

from opik import Opik

client = Opik(project_name="cc-benchmark")
hook_event = json.loads(sys.stdin.read())

client.trace(
    name=f"cc_tool_{hook_event.get('tool_name', 'unknown')}",
    input={"tool_input": hook_event.get("tool_input", "")},
    output={
        "tool_output": hook_event.get("tool_output", ""),
    },
    metadata={
        "session_id": hook_event.get("session_id", ""),
        "source": "cc-hook",
    },
)
```

### Approach 3: Langfuse for CC + Opik for PydanticAI

Fallback — Langfuse has an official CC integration and
community tooling (`claude-langfuse-monitor`).

- Turnkey setup, richest CC-specific features
- Splits observability across two platforms
- Use only if OTel approach proves insufficient

### Comparison

<!-- markdownlint-disable MD013 -->

| Dimension | OTel → Opik (rec.) | Hooks → Opik | Langfuse |
| --------- | ------------------ | ------------ | -------- |
| Same Opik instance | Yes | Yes | No |
| Token/cost tracking | Yes | No | Yes |
| Tool-level traces | Yes | Yes | Yes |
| LLM-call traces | Yes | No | Yes |
| Agent Teams | Session-level | Start/Stop hooks | Official |
| Setup complexity | Medium (Collector) | Low (script) | Low (npm) |
| Unified dashboard | Yes | Yes | No |
| In settings.json | Yes (vars exist) | No | No |

<!-- markdownlint-enable MD013 -->

### Integration with Existing Opik Setup

The OTel approach plugs into the existing stack:

- `OpikConfig` in `load_configs.py:60`
  — url, workspace, project, batch settings
- `track()` wrappers in `opik_instrumentation.py:76`
- `_record_opik_metadata()` in
  `evaluation_pipeline.py:389`
- Docker stack in `docker-compose.opik.yaml`
  (11 containers, ClickHouse backend)
- Opik frontend at `:5173` for side-by-side
  trace comparison of MAS vs baselines

### Standalone CC OTel Plugin

CC telemetry is infrastructure-level (env vars + OTel
Collector), not application-level (Python decorators).
It should be enableable/disableable without touching
`src/app/agents/` or the PydanticAI Opik setup.

Proposed structure:

```text
src/app/
├── agents/
│   └── opik_instrumentation.py  ← existing (untouched)
│
└── cc_otel/                     ← standalone plugin
    ├── __init__.py              ← enable/disable/is_enabled
    ├── config.py                ← CCOtelConfig
    ├── collector.py             ← OTel Collector lifecycle
    ├── hooks.py                 ← optional: Approach 2 fallback
    └── README.md                ← setup + env var reference
```

Key design points:

1. **Separate from PydanticAI Opik** — existing `track()`
   wrappers and `OpikConfig` stay untouched
2. **Python-first** — config, collector lifecycle, and
   hook logic are all Python
3. **Enable/disable programmatically** —
   `cc_otel.enable()` sets env vars,
   `cc_otel.disable()` clears them
4. **Composable** — collector attaches to existing
   Opik ClickHouse or runs standalone
5. **Graceful degradation** — `CC_OTEL_AVAILABLE` flag,
   try/except import, no-op when unavailable

`CCOtelConfig` example:

```python
from dataclasses import dataclass, field


@dataclass
class CCOtelConfig:
    """Configuration for CC OpenTelemetry tracing."""

    enabled: bool = False
    endpoint: str = "http://localhost:4317"
    protocol: str = "grpc"
    metrics_exporter: str = "otlp"
    logs_exporter: str = "otlp"
    log_tool_details: bool = True
    log_user_prompts: bool = False
    export_interval_ms: int = 60000
    resource_attributes: dict[str, str] = field(
        default_factory=lambda: {
            "project": "peerread-benchmark",
        }
    )

    def to_env_vars(self) -> dict[str, str]:
        """Export as env vars for settings.json."""
        env = {
            "CLAUDE_CODE_ENABLE_TELEMETRY": (
                "1" if self.enabled else "0"
            ),
            "OTEL_METRICS_EXPORTER": (
                self.metrics_exporter
            ),
            "OTEL_LOGS_EXPORTER": self.logs_exporter,
            "OTEL_EXPORTER_OTLP_PROTOCOL": self.protocol,
            "OTEL_EXPORTER_OTLP_ENDPOINT": self.endpoint,
            "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": (
                self.protocol
            ),
        }
        if self.log_tool_details:
            env["OTEL_LOG_TOOL_DETAILS"] = "1"
        if self.log_user_prompts:
            env["OTEL_LOG_USER_PROMPTS"] = "1"
        if self.resource_attributes:
            attrs = ",".join(
                f"{k}={v}"
                for k, v in self.resource_attributes.items()
            )
            env["OTEL_RESOURCE_ATTRIBUTES"] = attrs
        return env
```

Public API:

```python
import os

from app.cc_otel.config import CCOtelConfig


def enable(config: CCOtelConfig | None = None) -> None:
    """Activate CC OTel telemetry via env vars."""
    cfg = config or CCOtelConfig(enabled=True)
    for key, value in cfg.to_env_vars().items():
        os.environ[key] = value


def disable() -> None:
    """Deactivate CC OTel telemetry."""
    os.environ["CLAUDE_CODE_ENABLE_TELEMETRY"] = "0"


def is_enabled() -> bool:
    """Check if CC telemetry is active."""
    return os.environ.get(
        "CLAUDE_CODE_ENABLE_TELEMETRY",
    ) == "1"
```

### References

- [CC Monitoring/OTel docs][cc-mon]
  — OTEL env var reference, metrics/events
- [CC Settings docs][cc-set]
  — env section, `CLAUDE_CODE_ENABLE_TELEMETRY`
- [CC ROI Measurement Guide][cc-roi]
  — Docker Compose, Prometheus/OTel setups
- [CC on Bedrock monitoring][cc-bed]
- [OTel exporter spec][otel-spec]
- [Langfuse CC integration][langfuse]
  — Approach 3 reference
- [Opik Anthropic integration][opik-anth]
  — `track_anthropic` wrapper

[cc-mon]: https://code.claude.com/docs/en/monitoring-usage
[cc-set]: https://code.claude.com/docs/en/settings
[cc-roi]: https://github.com/anthropics/claude-code-monitoring-guide
[cc-bed]: https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md
[otel-spec]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md
[langfuse]: https://langfuse.com/integrations/other/claude-code
[opik-anth]: https://www.comet.com/docs/opik/integrations/anthropic

## Recommendation

**Useful but premature to adopt as core infrastructure.**

### Adopt Now For

- Parallel code reviews (multi-lens: security, performance, coverage)
- Multi-angle research tasks
- Debugging sessions with competing hypotheses

These are low-risk, high-value use cases with clear boundaries.

### Wait On

- Replacing Ralph loop or subagent architecture
- Autonomous multi-step development workflows

The limitations (no resumption, task lag, no nested teams) make it unreliable for
these use cases.

### When Ready

- Add `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: "1"` to `settings.json` env
- Start with research/review tasks before attempting implementation tasks
- Pre-approve common operations in permissions to reduce teammate prompt friction
- Use delegate mode to prevent lead from implementing instead of coordinating

The feature aligns well with existing role separation (architect/developer/reviewer)
and could enforce those boundaries more naturally than prompt-based subagent
instructions. But the experimental status means it should supplement, not replace,
the current Task tool + skills approach.
