---
title: Claude Code Skills Adoption - Implementation Summary
description: Implementation summary of adopting Claude Code Skills for modular agent capabilities, including format analysis and ecosystem context.
category: analysis
created: 2026-01-11
updated: 2026-03-07
version: 2.0.0
status: completed
---

**Date**: 2026-01-11
**Status**: Completed
**Branch**: feat-evals

## Summary

Adopted Claude Code Skills as the modular capability pattern for this project.
Skills follow the [Agent Skills open standard][agentskills-spec] (originated by
Anthropic, now adopted by 30+ agent products) and are extended by Claude Code
with additional frontmatter fields.

Ralph Loop adoption is documented separately in [ralph/README.md](../../../ralph/README.md).

## Skills Created (Initial Adoption)

| Skill | Location | Purpose |
| ----- | -------- | ------- |
| `designing-backend` | `.claude/skills/designing-backend/SKILL.md` | Backend architecture planning |
| `implementing-python` | `.claude/skills/implementing-python/SKILL.md` | Python code implementation |
| `reviewing-code` | `.claude/skills/reviewing-code/SKILL.md` | Code quality review |
| `generating-prd` | `.claude/skills/generating-prd/SKILL.md` | PRD.md → prd.json conversion |

Since initial adoption, the project has grown to 16 skills. Run
`ls .claude/skills/` for the current list.

**Key Features**:

- Progressive disclosure architecture (name+description → full body → resources)
- Third-person descriptions with explicit triggers for auto-discovery
- References to @AGENTS.md, @CONTRIBUTING.md for compliance
- Under 500 lines per SKILL.md

## Skills Auto-Discovery

Skills are auto-discovered by Claude Code. Trigger by:

- Requesting backend design → `designing-backend` activates
- Asking to implement Python → `implementing-python` activates
- Requesting code review → `reviewing-code` activates
- Converting PRD to JSON → `generating-prd` activates

## Design Decision: Skills vs Agents

Kept both systems:

- `.claude/agents/` — Existing subagent definitions (9 total)
- `.claude/skills/` — Claude Code Skills (16 total)
- **Rationale**: Incremental adoption; Skills complement Agents with progressive
  disclosure and auto-discovery. Agents define subagent roles for Task tool
  invocations; Skills define modular capabilities triggered by task context.

## SKILL.md Format: Open Standard vs Claude Code Extensions

The SKILL.md format has two layers:

### 1. Agent Skills Open Standard (agentskills.io)

Cross-platform specification adopted by Claude Code, GitHub Copilot, Cursor,
Gemini CLI, OpenAI Codex, Roo Code, and others.

| Field | Required | Description |
| ----- | -------- | ----------- |
| `name` | Yes | Lowercase + hyphens, max 64 chars, must match directory |
| `description` | Yes | Max 1024 chars; what it does and when to use |
| `license` | No | SPDX identifier |
| `compatibility` | No | Environment requirements, max 500 chars |
| `metadata` | No | Arbitrary key-value map |
| `allowed-tools` | No | Space-delimited pre-approved tools (experimental) |

### 2. Claude Code Extensions (top-level frontmatter)

CC extends the standard with additional fields documented at
[code.claude.com/docs/en/skills][cc-skills]:

| Field | Description |
| ----- | ----------- |
| `argument-hint` | Shown during autocomplete, e.g. `[issue-number]` |
| `disable-model-invocation` | `true` = only user can invoke via `/` |
| `user-invocable` | `false` = hidden from `/` menu |
| `model` | Model override when skill is active |
| `context` | `fork` = run in isolated subagent context |
| `agent` | Subagent type when `context: fork` (e.g. `Explore`) |
| `hooks` | Skill lifecycle hooks |

CC-specific features not in the open standard:

- `$ARGUMENTS`, `$0`, `$1` string substitutions
- `` !`shell command` `` dynamic context injection
- `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}` variables

### VSCode Validation Warning (Known Bug)

The Claude Code VSCode extension validates SKILL.md frontmatter against a
**stale snapshot** of the agentskills.io schema. It only recognizes:
`argument-hint`, `compatibility`, `description`, `disable-model-invocation`,
`license`, `metadata`, `name`, `user-invocable`.

Fields like `allowed-tools`, `model`, `context`, `agent` trigger false-positive
warnings. This is a [known upstream bug][cc-schema-bug] (issues #23329, #25380,
#25795 — all closed as duplicates of a tracked fix).

**Current project workaround**: CC-specific fields are nested under `metadata:`
to avoid the warning. This is valid per the agentskills.io spec (metadata is a
free-form map) but means CC may not interpret them as first-class directives.
Monitor the upstream fix; when shipped, move these fields to top-level.

## Ecosystem Context

The Agent Skills standard has achieved broad cross-industry adoption:

| Source | Type | Relationship |
| ------ | ---- | ------------ |
| [agentskills.io][agentskills-spec] | Open specification | Base standard; originated by Anthropic |
| [code.claude.com/docs/en/skills][cc-skills] | CC documentation | Extends standard with CC-specific fields |
| [skills.sh][skills-sh] | Marketplace/registry | Distribution layer; `npx skills add owner/repo` |
| [Microsoft Agent Framework][ms-skills] | SDK integration | Implements spec via `FileAgentSkillsProvider`; adds code-defined skills |
| [HashiCorp Agent Skills][hashi-skills] | Domain skill library | Terraform/Packer skills in SKILL.md format |
| [anthropics/skills][gh-skills] | Reference skills | Official Anthropic skill examples |

**Key distinction** (from HashiCorp): "MCP is the 'pipe' connecting data to AI;
Agent Skills are the 'textbooks' of knowledge." These are complementary, not
competing patterns.

## Settings Configuration

Updated `.claude/settings.json` for Skills adoption:

- Added Skills tool permission
- Enabled skill script execution paths

## References

[agentskills-spec]: https://agentskills.io/specification
[cc-skills]: https://code.claude.com/docs/en/skills
[cc-sdk-skills]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
[gh-skills]: https://github.com/anthropics/skills/tree/main/skills
[skills-sh]: https://skills.sh/
[ms-skills]: https://learn.microsoft.com/en-us/agent-framework/agents/skills
[hashi-skills]: https://www.hashicorp.com/en/blog/introducing-hashicorp-agent-skills
[cc-schema-bug]: https://github.com/anthropics/claude-code/issues/25795
