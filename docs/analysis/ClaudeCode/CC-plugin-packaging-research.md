---
title: CC Plugin Packaging Research
source: https://platform.claude.com/docs/en/agent-sdk/plugins, https://code.claude.com/docs/en/plugins
purpose: Evaluate packaging project skills, agents, and rules as a CC Plugin — including the AGENTS.md refactor plan as a plugin-based integration.
created: 2026-03-07
---

**Status**: Research (informational — not implementation requirements)

## Context

The AGENTS.md refactor plan (completed, deleted) proposed 3 minimal edits to integrate Skills/Ralph awareness into AGENTS.md. This research evaluates whether that integration — and the broader project configuration — would benefit from being packaged as a CC Plugin instead of remaining as repo-local files.

## What CC Plugins Are

Plugins are portable directory bundles that extend Claude Code with commands, agents, skills, hooks, and MCP servers ([source][sdk-plugins]). They work across Cowork and the Claude Agent SDK.

### Plugin Structure

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required: manifest
├── commands/                 # Custom slash commands
│   └── custom-cmd.md
├── agents/                   # Custom subagents
│   └── specialist.md
├── skills/                   # Agent Skills (SKILL.md)
│   └── my-skill/
│       └── SKILL.md
├── hooks/                    # Event handlers
│   └── hooks.json
└── .mcp.json                # MCP server definitions
```

([source][sdk-plugins])

### Loading Plugins

```python
# Agent SDK (Python)
async for message in query(
    prompt="Hello",
    options={
        "plugins": [
            {"type": "local", "path": "./my-plugin"},
        ]
    },
):
    pass
```

```bash
# CLI — install from marketplace or local
/plugin install my-plugin@marketplace
# Or reference by path in settings
```

([source][sdk-plugins])

### Key Mechanics

- Commands namespaced: `plugin-name:command-name` ([source][sdk-plugins])
- Plugins discovered via `.claude-plugin/plugin.json` manifest ([source][sdk-plugins])
- CLI-installed plugins stored in `~/.claude/plugins/` ([source][sdk-plugins])
- Plugins loaded at session init; appear in system init message ([source][sdk-plugins])
- Skills within plugins follow standard SKILL.md format with progressive disclosure ([source][skill-dev])

## Current Project Structure vs Plugin Structure

<!-- markdownlint-disable MD013 -->

| Project Component | Current Location | Plugin Equivalent | Notes |
| ----------------- | ---------------- | ----------------- | ----- |
| Skills | `.claude/skills/` (4 skills) | `plugin/skills/` | Direct mapping — SKILL.md format identical |
| Agents | `.claude/agents/` (9 agents) | `plugin/agents/` | Direct mapping — .md format identical |
| Rules | `.claude/rules/` (2 rules) | No plugin equivalent | Rules are repo-local only; not portable via plugins |
| CLAUDE.md | `./CLAUDE.md` → `@AGENTS.md` | No plugin equivalent | Project instructions are repo-local |
| Hooks | `.claude/settings.json` hooks | `plugin/hooks/hooks.json` | Can be ported to plugin hooks format |
| MCP servers | `.claude/settings.json` mcpServers | `plugin/.mcp.json` | Can be ported to plugin MCP config |
| Ralph scripts | `ralph/scripts/` | `plugin/commands/` | Could expose as slash commands |

<!-- markdownlint-enable MD013 -->

## AGENTS.md Refactor: Plugin vs Direct Edit

The refactor plan (completed, deleted) proposed 3 edits totaling ~16 lines:

1. Add "Claude Code Infrastructure" section referencing Skills/Ralph
2. Update subagent section header to note Skills complement
3. Add core-principles post-task review to Quick Reference

### Option A: Direct Edit (Current Plan)

- **Effort**: 15 minutes, 3 edits to AGENTS.md
- **Scope**: Project-local only
- **Maintenance**: Edit AGENTS.md directly when adding new skills/agents
- **Portability**: None — tied to this repo

### Option B: Plugin Packaging

Package project skills, agents, and ralph commands as a plugin:

```text
agents-eval-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── ralph-init.md        # /agents-eval:ralph-init
│   ├── ralph-run.md         # /agents-eval:ralph-run
│   └── ralph-status.md      # /agents-eval:ralph-status
├── agents/
│   ├── backend-architect.md
│   ├── python-developer.md
│   ├── code-reviewer.md
│   └── ...                  # all 9 agents
├── skills/
│   ├── designing-backend/SKILL.md
│   ├── implementing-python/SKILL.md
│   ├── reviewing-code/SKILL.md
│   └── generating-prd/SKILL.md
└── hooks/
    └── hooks.json           # quality gates
```

- **Effort**: 2-4 hours to create plugin manifest + restructure
- **Scope**: Portable across projects and teams
- **Maintenance**: Plugin version management; separate from repo
- **Portability**: High — reusable in other evaluation projects

### Option C: Hybrid (Recommended)

Keep AGENTS.md + rules as repo-local (they're project-specific). Apply the 3 direct edits from the refactor plan. Separately evaluate plugin packaging only for components that would benefit from cross-project reuse.

<!-- markdownlint-disable MD013 -->

| Component | Keep Repo-Local | Package as Plugin | Rationale |
| --------- | --------------- | ----------------- | --------- |
| AGENTS.md / CONTRIBUTING.md | Yes | No | Project-specific behavioral rules |
| `.claude/rules/` | Yes | No | Project-specific context rules |
| `.claude/skills/` | Yes | Future | Skills are project-tailored; plugin only if reusing across projects |
| `.claude/agents/` | Yes | Future | Agent definitions reference project-specific patterns |
| Ralph commands | Yes | Future | Ralph is project-infrastructure; plugin if standardizing across repos |
| MCP config | Yes | No | Project-specific server endpoints |

<!-- markdownlint-enable MD013 -->

## Plugin Packaging: When It Makes Sense

Based on external research on plugin adoption patterns:

**Package as plugin when** ([source][skill-dev], [source][plugin-structure]):

- Skills/agents are **domain-generic** (e.g., "code-reviewer" applicable to any Python project)
- Multiple repos need the **same configuration** (e.g., org-wide security review agent)
- You want **versioned distribution** via marketplace or private GitHub repo
- The Agent SDK is used for **programmatic agent orchestration** beyond CLI

**Keep repo-local when** ([source][cc-mem]):

- Configuration references **project-specific paths, patterns, or conventions**
- CLAUDE.md / rules contain **behavioral rules tied to this codebase**
- Skills reference **project-specific files** (e.g., `agent_system.py`, `evaluation_pipeline.py`)
- No cross-project reuse demand exists

## Actionable Recommendation

### Immediate (Tier 1)

**Apply the 3 direct edits from the refactor plan (completed).** This is the minimal, KISS approach:

1. Add Claude Code Infrastructure section to AGENTS.md
2. Update Agent Role Boundaries header with Skills note
3. Add core-principles post-task review to Quick Reference

Fix the path reference from `.claude/scripts/ralph/` to `ralph/scripts/` while editing (gap identified in [CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md)).

### Future (Tier 3 — triggered by cross-project reuse)

**If the project spawns sibling evaluation repos**, extract domain-generic skills into a plugin:

```json
{
  "name": "eval-framework-skills",
  "version": "1.0.0",
  "description": "Evaluation framework skills for MAS research",
  "skills": ["reviewing-code", "testing-python", "designing-backend"]
}
```

This is YAGNI until a second project needs these skills.

## References

- [Agent SDK Plugins docs][sdk-plugins] — plugin loading and structure
- [CC Plugins docs][cc-plugins] — full plugin development guide
- [CC Plugins reference][cc-plugins-ref] — technical specs and schemas
- [Plugin Structure skill][plugin-structure] — community plugin scaffolding guide
- [Skill Development skill][skill-dev] — SKILL.md authoring best practices
- [CC Memory docs][cc-mem] — CLAUDE.md and rules (repo-local patterns)
- AGENTS.md refactor plan (completed, deleted)

[sdk-plugins]: https://platform.claude.com/docs/en/agent-sdk/plugins
[cc-plugins]: https://code.claude.com/docs/en/plugins
[cc-plugins-ref]: https://code.claude.com/docs/en/plugins-reference
[plugin-structure]: https://claude-plugins.dev/skills/@anthropics/claude-plugins-official/plugin-structure
[skill-dev]: https://lobehub.com/skills/sjnims-plugin-dev-skill-development
[cc-mem]: https://code.claude.com/docs/en/memory
