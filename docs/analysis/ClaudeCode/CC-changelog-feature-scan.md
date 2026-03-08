---
title: CC Changelog Feature Scan
source: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md, https://claudelog.com/claude-code-changelog/
purpose: Identify actionable CC features from recent releases (v2.1.0–2.1.71) not yet covered by existing analysis docs.
created: 2026-03-07
---

**Status**: Research (informational — feeds into adoption plan)

## Scan Scope

Cross-referenced CHANGELOG.md (v2.1.0–2.1.71, Jan–Mar 2026) against 18 analysis docs in this directory. Features below are **not yet covered** and potentially relevant to Agents-eval workflows.

## High Relevance (directly applicable)

<!-- markdownlint-disable MD013 -->

### `/loop` Command + Cron Scheduling (v2.1.71)

Run prompts or slash commands at recurring intervals: `/loop 5m check the deploy`. Cron scheduling enables recurring prompts within a session without manual resubmission. ([source][changelog], [source][claudelog])

**Relevance**: Could supplement Ralph monitoring — periodic `make ralph_status` checks from a separate CC session. Lighter-weight than full loop orchestration. Also useful for periodic `make quick_validate` during long interactive sessions.

### Structured Outputs for `-p` Mode (v2.1.22)

`claude -p` now supports structured output schemas, not just `--output-format json`. ([source][changelog])

**Relevance**: Ralph uses `claude -p --output-format json`. Structured outputs could enforce story result schemas (pass/fail/error + commit hashes) directly in the CLI invocation, reducing parsing brittleness in `ralph.sh`.

### `includeGitInstructions` Setting (v2.1.69)

New `includeGitInstructions` setting and `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` env var remove built-in commit/PR workflow instructions from context. ([source][changelog])

**Relevance**: Ralph's headless mode doesn't need git workflow instructions. Disabling saves context tokens — aligns with memory system analysis (context noise reduction). Set `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` in Ralph's environment.

### Project Configs Shared Across Git Worktrees (v2.1.63)

`.claude/` project configuration files now automatically shared across worktrees of the same repo. ([source][changelog])

**Relevance**: Directly addresses Ralph worktree workflow — skills, agents, rules, and settings no longer need duplication or symlinking in worktree directories.

### HTTP Hooks (v2.1.63)

JSON POST/receive on hook events. See [CC-hooks-system-analysis.md](CC-hooks-system-analysis.md) for full hooks reference.

### Agent Worktree Isolation (`isolation: worktree`) (v2.1.50)

Spawn subagents in isolated git worktrees via `Agent(isolation: "worktree")`. Worktree auto-cleaned if agent makes no changes; path and branch returned if changes exist. ([source][changelog])

**Relevance**: Native CC support for what Ralph's `ralph-in-worktree.sh` does manually. Could simplify worktree-based parallel story execution — each teammate gets an isolated worktree without bash scaffolding.

### `Setup` Hook Event (v2.1.10)

One-time repo maintenance on session start. See [CC-hooks-system-analysis.md](CC-hooks-system-analysis.md).

### Task Tool Metrics (v2.1.30)

Task completions now include metrics: tokens consumed, tool uses, and duration. ([source][changelog])

**Relevance**: Direct cost/performance tracking per agent teams task. Feeds into CC baseline collection and evaluation pipeline. Supplements CC Analytics API research (Tier 2).

### TeammateIdle + TaskCompleted Hook Events (v2.1.33)

Agent Teams lifecycle hooks. See [CC-hooks-system-analysis.md](CC-hooks-system-analysis.md).

### Memory Frontmatter for Agents (v2.1.33)

Agents can have persistent memory storage via frontmatter configuration. ([source][changelog])

**Relevance**: Agent definitions in `.claude/agents/` could maintain state across sessions. Useful for agents that accumulate domain knowledge (e.g., code-reviewer learning project patterns).

## Medium Relevance (useful, not urgent)

### `/simplify` and `/batch` Bundled Commands (v2.1.63)

New built-in slash commands. `/simplify` for code simplification, `/batch` for batch operations. ([source][changelog])

**Relevance**: `/simplify` could be useful post-implementation for cleanup (similar to De-Sloppify pass concept in Ralph research). `/batch` for multi-file operations.

### `--from-pr` Flag (v2.1.27)

Resume sessions linked to a specific PR. Sessions auto-link to PRs created via `gh pr create`. ([source][changelog])

**Relevance**: Could resume Ralph sprint work by PR reference instead of session ID. Useful for long-running sprint branches.

### `/claude-api` Skill (v2.1.69)

Built-in skill for building applications with Claude API and Anthropic SDK. ([source][changelog])

**Relevance**: Project uses PydanticAI with Anthropic API. Skill could assist with API integration tasks, model configuration, and SDK patterns.

### LSP Tool for Code Intelligence (v2.0.74)

Go-to-definition, find-references, hover information via Language Server Protocol. ([source][changelog])

**Relevance**: Better code navigation for large codebase exploration. Passive improvement — no configuration needed.

### Plugin Hot Reload (`/reload-plugins`) (v2.1.69)

Activate pending plugin changes without session restart. ([source][changelog])

**Relevance**: Only relevant if plugins adopted (currently Tier 3). Reduces friction for plugin development.

### `ConfigChange` Hook Event (v2.1.49)

Hook fires when CC configuration changes — useful for security auditing. ([source][changelog])

**Relevance**: Track configuration drift. Low priority unless security auditing of CC config becomes a concern.

## Already Covered by Existing Research

| Feature | Covered In |
| ------- | ---------- |
| Remote Control (`claude remote-control`) | [CC-remote-control-analysis.md](CC-remote-control-analysis.md) |
| Agent Teams (TeamCreate, Task tools) | [CC-agent-teams-orchestration.md](CC-agent-teams-orchestration.md) |
| Fast mode (Opus 4.6) | [CC-fast-mode-analysis.md](CC-fast-mode-analysis.md) |
| Auto memory + CLAUDE.md hierarchy | [CC-memory-system-analysis.md](CC-memory-system-analysis.md) |
| Cloud sessions (`claude --remote`) | [CC-cloud-sessions-analysis.md](CC-cloud-sessions-analysis.md) |
| Skills (auto-discovery, SKILL.md) | [CC-skills-adoption-analysis.md](CC-skills-adoption-analysis.md) |
| Plugins + Cowork | [CC-cowork-plugins-enterprise-analysis.md](CC-cowork-plugins-enterprise-analysis.md) |
| Chrome extension | [CC-chrome-extension-analysis.md](CC-chrome-extension-analysis.md) |
| Hooks system (all events) | [CC-hooks-system-analysis.md](CC-hooks-system-analysis.md) |
| Opus 4.6 + 1M context | [CC-extended-context-analysis.md](CC-extended-context-analysis.md) |
| Task system with dependencies | Already in use |

<!-- markdownlint-enable MD013 -->

## References

- [CC CHANGELOG.md][changelog]
- [claudelog.com changelog][claudelog]

[changelog]: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
[claudelog]: https://claudelog.com/claude-code-changelog/
