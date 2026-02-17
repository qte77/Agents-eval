---
title: CC Agent Teams Orchestration
source: https://code.claude.com/docs/en/agent-teams
purpose: Analysis of Claude Code Agent Teams for parallel code review, cross-layer implementation, and adversarial debugging within Agents-eval.
created: 2026-02-08
updated: 2026-02-12
test_run: 2026-02-11 (parallel code review with 3 teammates)
---

**Status**: Experimental (disabled by default)

## What Agent Teams Offer

Coordinates multiple independent CC sessions with:

- **Lead/teammate hierarchy** with shared task list and mailbox messaging
- **Inter-agent communication** — direct teammate-to-teammate messaging
- **Parallel execution** — each teammate has its own context window
- **Task dependency management** with automatic unblocking
- **Quality gates** via `TeammateIdle` and `TaskCompleted` hooks
- **Delegate mode** — restricts lead to coordination only
- **Plan approval** — teammates must get lead sign-off before implementing

### How It Works

- Lead spawns teammates, coordinates work; each teammate is a full CC instance
- Shared task list (pending/in-progress/completed) with dependency tracking
- Teammates load project context (CLAUDE.md, MCP servers, skills) automatically
- Lead's conversation history does NOT carry over to teammates
- Display: in-process (single terminal) or split panes (tmux/iTerm2)

### Configuration

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

### Delegate Mode

Restricts lead to coordination-only (spawn, assign, synthesize). Blocks direct implementation.

**Use when**: Lead keeps implementing instead of delegating; 3+ teammates. **Skip when**: Task is already pure coordination; small teams.

### Agent Teams vs Subagents (Task tool)

<!-- markdownlint-disable MD013 -->

| Aspect | Subagents | Agent Teams |
| -------- | ----------- | ------------- |
| Context | Own window; results return to caller | Own window; fully independent |
| Communication | Report back to main agent only | Teammates message each other directly |
| Coordination | Main agent manages all work | Shared task list with self-coordination |
| Best for | Focused tasks where only the result matters | Complex work requiring discussion and collaboration |
| Token cost | Lower: results summarized back | Higher: each teammate is a separate instance |

<!-- markdownlint-enable MD013 -->

## Relevance to This Project

| Use Case | Fit | Rationale |
| -------- | --- | --------- |
| Parallel code review (security + performance + coverage) | Strong | 3 reviewers run simultaneously with different lenses |
| Cross-layer feature implementation (backend + tests) | Strong | Enforces role separation (architect/developer/reviewer) |
| Research + competing hypotheses debugging | Strong | Adversarial debate addresses anchoring bias |

**Overlaps**: Subagents for fire-and-forget work (replace only when inter-agent communication needed). Ralph loop is sequential (complementary, not competing). Skills load automatically in teammates.

## Key Limitations

1. **No session resumption** — teammates lost on `/resume`
2. **Task status can lag** — teammates sometimes don't mark tasks complete
3. **No nested teams** — teammates can't spawn their own teams
4. **One team per session**
5. **Permissions set at spawn** — can't differentiate read-only vs write per teammate
6. **Linear token cost** — each teammate is a separate Claude instance
7. **Experimental, disabled by default**
8. **Split panes require tmux or iTerm2**

## When to Use Each Mode

**Single CC Session**: Sequential workflows, prompt engineering, pipeline debugging, single-file changes, test writing. Full context retention, lower cost.

**Agent Teams**: 3+ independent files, multiple review perspectives, competing approaches, large refactoring. See [parallel review test](../reviews/evaluation-pipeline-parallel-review-2026-02-11.md).

## Benchmarking PydanticAI MAS vs CC-Style Baselines

Compare MAS (Manager -> Researcher -> Analyst -> Synthesizer) against simpler patterns using same three-tier evaluation pipeline.

**Baselines** (all PydanticAI within `src/`):

1. **PydanticAI MAS** (current): Sequential delegation with approval loop, Pydantic models, token tracking, Logfire/Phoenix observability
2. **Single-Agent**: One agent, one pass, no delegation — tests value of multi-agent orchestration
3. **Parallel-Agents**: Independent agents via `asyncio.gather`, coordinator merges — tests parallel vs sequential

**Evaluation**: All produce `GeneratedReview` -> scored via `evaluation_pipeline.evaluate_comprehensive()`

| Tier | Measures |
| ---- | -------- |
| 1 | Multi-agent vs single-pass quality |
| 2 | Approval loop value (validation vs no validation) |
| 3 | Coordination overhead (delegation chain efficiency) |

**Hypothesis**: Approval loop is key for Tier 2 quality. If single-agent matches, multi-agent overhead unjustified. If parallel matches at lower latency, reconsider sequential.

**Key Files**: `agent_system.py`, `orchestration.py`, `evaluation_pipeline.py`, `peerread_models.py`, `config_chat.json`, `config_eval.json`

## Tracing & Observability

**Gap**: PydanticAI MAS has Logfire/Phoenix tracing; CC baselines need equivalent.

### Approach Comparison

<!-- markdownlint-disable MD013 -->

| Dimension | OTel -> Phoenix (recommended) | Hooks -> Phoenix | Langfuse |
| --------- | ----------------------------- | ---------------- | -------- |
| Same Phoenix instance | Yes | Yes | No |
| Token/cost tracking | Yes | No | Yes |
| Tool-level traces | Yes | Yes | Yes |
| LLM-call traces | Yes | No | Yes |
| Setup complexity | Medium (Collector) | Low (script) | Low (npm) |
| Unified dashboard | Yes | Yes | No |
| In settings.json | Yes (vars exist) | No | No |

<!-- markdownlint-enable MD013 -->

### OTel -> Phoenix (Recommended)

Already partially configured in `.claude/settings.json` (currently disabled). Richest data, reuses existing Phoenix OTLP endpoint.

**Full enabled config** (`settings.json` env section):

```json
{
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
    "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "grpc"
}
```

**Optional**: `OTEL_LOG_TOOL_DETAILS`: `"1"`, `OTEL_LOG_USER_PROMPTS`: `"1"`, `OTEL_RESOURCE_ATTRIBUTES`: `"project=peerread-benchmark"`, `OTEL_METRIC_EXPORT_INTERVAL`: `"10000"` (10s for testing)

**Infrastructure**: Phoenix container already accepts OTLP on `:4317` (gRPC) and `:6006` (HTTP). No additional infrastructure needed.

### Hooks -> Phoenix (Fallback)

`PostToolUse` hook script sending traces to Phoenix OTLP endpoint. Lower setup (single script), coarser data (tool-level only, no token/cost). Sufficient for coarse Tier 3 execution graphs.

### Langfuse (Last Resort)

Official CC integration. Turnkey setup but splits observability across two platforms. Use only if OTel approach proves insufficient.

### Integration Points

Plugs into existing stack: `LogfireConfig` in `load_configs.py`, Logfire instrumentation in `logfire_instrumentation.py`, Phoenix Docker container via `make start_phoenix`.

CC OTel is infrastructure-level (env vars + Phoenix endpoint), separate from application-level PydanticAI Logfire. Enable/disable without touching `src/app/agents/`.

### References

- [CC Monitoring/OTel docs][cc-mon] — env var reference, metrics/events
- [CC Settings docs][cc-set] — `CLAUDE_CODE_ENABLE_TELEMETRY`
- [CC ROI Measurement Guide][cc-roi] — Docker Compose, Prometheus/OTel setups
- [CC on Bedrock monitoring][cc-bed]
- [OTel exporter spec][otel-spec]
- [Langfuse CC integration][langfuse]
- [Phoenix Arize docs][phoenix-docs]

[cc-mon]: https://code.claude.com/docs/en/monitoring-usage
[cc-set]: https://code.claude.com/docs/en/settings
[cc-roi]: https://github.com/anthropics/claude-code-monitoring-guide
[cc-bed]: https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/MONITORING.md
[otel-spec]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md
[langfuse]: https://langfuse.com/integrations/other/claude-code
[phoenix-docs]: https://docs.arize.com/phoenix

## Recommendation

**Useful but premature as core infrastructure.**

**Adopt now**: Parallel code reviews, multi-angle research, competing hypotheses debugging. Low-risk, high-value, clear boundaries.

**Wait on**: Replacing Ralph loop or subagent architecture. Limitations (no resumption, task lag, no nested teams) make it unreliable.

**When ready**: Enable in `settings.json`, start with review/research tasks, pre-approve common operations, use delegate mode for 3+ teammates.

## Trace & Communication Storage

Agent Teams artifacts stored under `~/.claude/`:

```text
~/.claude/
├── teams/
│   └── {team-name}/
│       ├── config.json              # Team metadata and member roster
│       └── inboxes/
│           ├── {agent-1}.json       # Mailbox for agent 1
│           ├── {agent-2}.json       # Mailbox for agent 2
│           └── {agent-n}.json       # Mailbox for agent n
├── tasks/
│   └── {team-name}/
│       ├── 1.json                   # Task 1 metadata
│       ├── 2.json                   # Task 2 metadata
│       └── n.json                   # Task n metadata
└── transcripts/                     # Full teammate session logs (if enabled)
    └── {session-id}.jsonl
```

### 1. Team Configuration

**Location**: `~/.claude/teams/{team-name}/config.json`

Contains complete team orchestration metadata:

```json
{
  "name": "parallel-code-review",
  "description": "Parallel review of evaluation_pipeline.py...",
  "createdAt": 1770854157287,
  "leadAgentId": "team-lead@parallel-code-review",
  "leadSessionId": "e41ee506-14e0-49c7-b933-de43cac57810",
  "members": [
    {
      "agentId": "security-reviewer@parallel-code-review",
      "name": "security-reviewer",
      "agentType": "general-purpose",
      "model": "claude-opus-4-6",
      "prompt": "MANDATORY: Read AGENTS.md first...",
      "color": "blue",
      "planModeRequired": false,
      "joinedAt": 1770854199673,
      "tmuxPaneId": "in-process",
      "cwd": "/workspaces/Agents-eval",
      "backendType": "in-process"
    }
    // ... other members
  ]
}
```

**Key fields**:

- `members[]`: Complete roster with prompts, models, colors, join timestamps
- `model`: Shows which model each teammate uses (Opus 4.6 for teammates, Sonnet 4.5 for lead)
- `prompt`: Full prompt given to each teammate at spawn time
- `backendType`: Execution mode (`in-process` vs split panes)

### 2. Inter-Agent Messages (Mailboxes)

**Location**: `~/.claude/teams/{team-name}/inboxes/{agent-name}.json`

Each agent has its own mailbox file containing all messages received:

```json
[
  {
    "from": "quality-reviewer",
    "text": "## Quality Review Findings: evaluation_pipeline.py\n\n...",
    "summary": "Quality review findings for evaluation_pipeline.py",
    "timestamp": "2026-02-11T23:57:29.518Z",
    "color": "green",
    "read": true
  },
  {
    "from": "security-reviewer",
    "text": "# Security Review: evaluation_pipeline.py\n\n...",
    "summary": "Security review findings for evaluation_pipeline.py",
    "timestamp": "2026-02-11T23:57:55.822Z",
    "color": "blue",
    "read": true
  }
]
```

**Message types captured**:

- **Review findings**: Full markdown-formatted reports
- **Idle notifications**: JSON structured `{"type":"idle_notification",...}`
- **Task assignments**: JSON structured `{"type":"task_assignment",...}`
- **Peer DM summaries**: Brief snippets when teammates message each other

**Practical example from test run**:

- `team-lead.json`: Received 3 complete review reports + idle notifications
- `security-reviewer.json`: Received task assignments from lead
- `quality-reviewer.json`: Received task assignments from lead
- `coverage-reviewer.json`: Received task assignments from lead

### 3. Task Tracking

**Location**: `~/.claude/tasks/{team-name}/{task-id}.json`

Each task is tracked in its own JSON file:

```json
{
  "id": "1",
  "subject": "Security review of evaluation_pipeline.py",
  "description": "Review src/app/evals/evaluation_pipeline.py for...",
  "activeForm": "Reviewing security vulnerabilities",
  "owner": "security-reviewer",
  "status": "completed",
  "blocks": ["4"],
  "blockedBy": []
}
```

**Key behaviors**: File locking prevents race conditions on task claiming. Teammates inherit lead's permissions. Context is fully isolated per teammate.

### Test Results (2026-02-11)

3-teammate parallel code review of `evaluation_pipeline.py`:

- **Team**: Lead (Sonnet 4.5) + security/quality/coverage reviewers (Opus 4.6 each)
- **Execution**: ~26 seconds for 3 complete reviews (quality 23:57:29, coverage +6s, security +20s)
- **Dependencies**: Tasks 1-3 ran in parallel; task 4 (aggregation) waited for all 3
- **Output**: Full review content preserved in mailboxes (19k+ chars each)
- **Report**: [evaluation-pipeline-parallel-review-2026-02-11.md](../reviews/evaluation-pipeline-parallel-review-2026-02-11.md)

### Phoenix/Logfire Correlation

- **Application traces** (PydanticAI MAS): Phoenix OTLP endpoint (`:6006` HTTP, `:4317` gRPC), Logfire SDK, `LogfireConfig`
- **Agent Teams traces** (CC orchestration): `~/.claude/teams/` + `~/.claude/tasks/`, file-based JSON
- **Unified approach**: Phoenix/Logfire for application-level, CC traces for orchestration-level, aggregated findings to `docs/reviews/`, cross-reference by timestamps

### Sources

<!-- markdownlint-disable MD013 -->

| Source | Author | Key Content |
| ------ | ------ | ----------- |
| [Official CC Agent Teams docs][cc-teams-docs] | Anthropic | Architecture, task lists, mailbox, storage |
| [Agent Teams Announcement][anthropic-teams] | Anthropic | Feature announcement |
| [Claude Code Swarms][addy-swarms] | Addy Osmani | Swarm patterns, competing hypotheses |
| [Setup and Use Guide][medium-setup] | D. Sobaloju | Practical examples, troubleshooting |
| [Agent Orchestration Analysis][linkedin-trace] | Sigrid Jin | `~/.claude/teams` structure analysis |
| [Agent Teams Guide][claudefast] | Community | Multi-session orchestration guide |
| [Porting to OpenCode][dev-opencode] | Uenyioha | Architecture comparison |
| [Aura Frog Guide][aura-frog] | Community | Structured workflow integration |
| [C Compiler with 16 Agents][compiler-case] | Anthropic/Register | 2,000 sessions, 100k-line compiler |

<!-- markdownlint-enable MD013 -->

[cc-teams-docs]: https://code.claude.com/docs/en/agent-teams
[anthropic-teams]: https://www.anthropic.com/engineering/building-c-compiler
[addy-swarms]: https://addyosmani.com/blog/claude-code-agent-teams/
[medium-setup]: https://darasoba.medium.com/how-to-set-up-and-use-claude-code-agent-teams-and-actually-get-great-results-9a34f8648f6d
[linkedin-trace]: https://www.linkedin.com/pulse/how-claude-code-orchestrate-team-agents-sigrid-jin--msedc
[claudefast]: https://claudefa.st/blog/guide/agents/agent-teams
[dev-opencode]: https://dev.to/uenyioha/porting-claude-codes-agent-teams-to-opencode-4hol
[aura-frog]: https://github.com/nguyenthienthanh/aura-frog/blob/main/aura-frog/docs/AGENT_TEAMS_GUIDE.md
[compiler-case]: https://www.theregister.com/2026/02/09/claude_opus_46_compiler/
