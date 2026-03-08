---
title: CC Hooks System Analysis
source: https://code.claude.com/docs/en/hooks
purpose: Analysis of Claude Code hooks system for automation, quality gates, and Ralph loop integration.
created: 2026-03-07
---

**Status**: Generally available (v2.0.41+, extensively evolved through v2.1.71)

## What Hooks Are

Shell commands that execute in response to CC lifecycle events. Configured in
`.claude/settings.json` (project) or `~/.claude/settings.json` (user). Hooks
run locally, outside the sandbox, with full system access.

## Hook Events

<!-- markdownlint-disable MD013 -->

| Event | Trigger | Since | Key Use Cases |
| ----- | ------- | ----- | ------------- |
| `PreToolUse` | Before any tool executes | v2.0.41 | Approval/denial gates, context injection via `additionalContext` (v2.1.9), input modification via `updatedInput` (v2.1.0) |
| `PostToolUse` | After any tool completes | v2.0.41 | Logging, trace collection, quality checks |
| `Stop` | Before session ends | v2.0.41 | Cleanup, final validation, re-prompting (Ralph Wiggum pattern) |
| `SessionStart` | Session begins | v2.0.43 | Repo maintenance, env setup; deferred for ~500ms faster startup (v2.1.47) |
| `Setup` | Repo initialization | v2.1.13 | One-time repo maintenance tasks |
| `PermissionRequest` | User prompted for permission | v2.0.45 | Automatic approval/denial policies (v2.0.54: processes 'always allow') |
| `SubagentStart` | Subagent spawns | v2.0.43 | Subagent monitoring, `agent_id` and `agent_transcript_path` in stop fields (v2.0.42) |
| `TeammateIdle` | Agent Teams teammate becomes idle | v2.1.33 | Work redistribution, progress tracking |
| `TaskCompleted` | Agent Teams task finishes | v2.1.33 | Dependency unblocking, aggregation triggers |
| `WorktreeCreate` | Git worktree created | v2.1.50 | Environment setup for isolated agents |
| `WorktreeRemove` | Git worktree removed | v2.1.50 | Cleanup after agent completes |

<!-- markdownlint-enable MD013 -->

## Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "echo 'checking bash command'",
        "once": true
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "command": "/path/to/trace-collector.sh"
      }
    ],
    "Stop": [
      {
        "command": "make validate"
      }
    ]
  }
}
```

### Key Configuration Fields

| Field | Description | Since |
| ----- | ----------- | ----- |
| `matcher` | Tool name filter (`*` for all, specific tool name) | v2.0.41 |
| `command` | Shell command to execute | v2.0.41 |
| `once` | Execute only once per session | v2.1.0 |
| `model` | Custom model for hook evaluation | v2.0.41 |
| `tool_use_id` | Available in hook input | v2.0.45 |

### Hook Return Values

Hooks can return JSON to influence CC behavior:

- **`additionalContext`**: Inject context into the agent's next turn (PreToolUse, v2.1.9)
- **`updatedInput`**: Modify tool input with ask decision (PreToolUse, v2.1.0)
- **Approval/denial**: PermissionRequest hooks can auto-approve or auto-deny (v2.0.45)

### HTTP Hooks (v2.1.63+)

Hooks support JSON POST/receive for external service integration. Enables
webhook-style automation without local scripts.

### Agent Frontmatter Hooks (v2.1.0)

Agent definitions (`.claude/agents/`) can include hooks in their frontmatter:
PreToolUse, PostToolUse, Stop. These are scoped to the agent's execution only.

## Relevance to This Project

| Use Case | Fit | Rationale |
| -------- | --- | --------- |
| **Ralph trace collection** | Strong | `PostToolUse` hook sends tool events to Phoenix OTLP; replaces manual artifact parsing |
| **Quality gates in Ralph** | Strong | `Stop` hook runs `make validate` before marking story passed |
| **Permission automation** | Medium | `PermissionRequest` auto-approves known-safe operations for `claude -p` runs |
| **Agent Teams monitoring** | Medium | `TeammateIdle` / `TaskCompleted` hooks track parallel story progress |
| **CC baseline collection** | Weak | Hooks run in interactive sessions; `claude -p` has limited hook support |

### Current Usage in Project

The project currently uses hooks indirectly through:

- Agent frontmatter hooks in `.claude/agents/` definitions
- `<user-prompt-submit-hook>` feedback in interactive sessions
- No dedicated hook scripts in the repository yet

### Potential Integration

```json
{
  "hooks": {
    "Stop": [
      {
        "command": "make quick_validate",
        "once": true
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "command": "ralph/scripts/lib/trace-hook.sh"
      }
    ]
  }
}
```

**Recommendation**: Adopt `Stop` hook for validation gates first (low risk,
high value). Defer `PostToolUse` trace collection until OTel upstream
limitation ([#9584](https://github.com/anthropics/claude-code/issues/9584)) is
resolved or artifact-based collection proves insufficient.

## References

- [CC Hooks docs](https://code.claude.com/docs/en/hooks)
- [CC Settings docs](https://code.claude.com/docs/en/settings)
- [CC Agent Teams docs](https://code.claude.com/docs/en/agent-teams) (TeammateIdle, TaskCompleted hooks)
- [CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md) (project-specific teams analysis)
- [CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md) (Ralph Wiggum Stop hook pattern)
