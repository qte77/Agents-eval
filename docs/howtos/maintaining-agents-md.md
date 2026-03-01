---
title: Strategy for Maintaining Agent Governance Files
description: Guidelines for keeping AGENTS.md, AGENT_LEARNINGS.md, and AGENT_REQUESTS.md synchronized with codebase changes for effective AI agent operation
date: 2026-03-01
category: maintenance
version: 1.1.0
---

This document outlines a strategy to ensure the agent governance files remain synchronized with the state of the codebase, preventing them from becoming outdated. Accurate governance files are critical for safe, effective AI agent operation.

**Agent governance files:**

| File | Purpose | Authority |
|------|---------|-----------|
| `AGENTS.md` | Behavioral rules, role boundaries, compliance requirements | Behavioral authority |
| `AGENT_LEARNINGS.md` | Accumulated patterns, solutions, architectural insights | Living knowledge base |
| `AGENT_REQUESTS.md` | Active escalations requiring human input | Escalation queue |
| `CONTRIBUTING.md` | Technical workflows, commands, coding standards | Technical authority |

The strategy combines process integration, automation, and collaborative habits.

## 1. Process & Workflow Integration

Integrate documentation updates into the core development workflow, making them a required and explicit step.

### Pull Request Checklist

Modify the project's PR template to include a mandatory checklist item that forces a review of governance files:

```markdown
- [ ] I have reviewed `AGENTS.md` and confirmed my changes are reflected
- [ ] New patterns or solutions are documented in `AGENT_LEARNINGS.md`
- [ ] Resolved requests are removed from `AGENT_REQUESTS.md`
```

> **Note**: `.github/pull_request_template.md` does not yet exist in this project. Adding it is a recommended improvement.

### Agent Responsibility

- **AGENTS.md**: Agent must update when introducing new patterns, changing role boundaries, or altering compliance rules.
- **AGENT_LEARNINGS.md**: Agent must add a concise entry for every new pattern discovered — including failed approaches, solutions to recurring issues, and architectural decisions. Format: Context / Problem / Solution / Example / References.
- **AGENT_REQUESTS.md**: Agent must add an entry when blocked, when user input is required, or when a conflict cannot be resolved autonomously. Entry must be removed once resolved.
- **CONTRIBUTING.md**: Agent must update the command reference or coding patterns sections when the project tooling changes.

### Commit Message Convention

Reference governance files in commit messages when a change addresses or updates them:

```bash
# Example
git commit -m "fix(agent): resolve import path (refs AGENT_LEARNINGS.md module-naming)"
```

## 2. Automation & Tooling

Build automated checks to catch desynchronization before it gets merged.

### CI/CD Validation

The `make validate` pipeline can be extended to check for governance inconsistencies:

- **Check for `FIXME`/`TODO`**: New `FIXME`/`TODO` items in code should have a corresponding entry in `AGENT_REQUESTS.md`.
- **Validate file paths**: Parse governance files for referenced paths (e.g., `src/app/`) and assert those files still exist.
- **Keyword synchronization**: If a commit removes a `NotImplementedError`, check whether `AGENTS.md` or `AGENT_LEARNINGS.md` still references it.

### Ralph Autonomous Loop

The Ralph loop (`ralph/scripts/ralph.sh`) is the primary autonomous task execution mechanism. It reads sprint state from `ralph/docs/prd.json` and logs learnings to `ralph/docs/progress.txt`. When Ralph completes or fails a story, governance files should be updated as part of story completion criteria:

```bash
make ralph_init        # Initialize state for a new sprint
make ralph ITERATIONS=N  # Run autonomous loop
```

Post-sprint: ensure `AGENT_LEARNINGS.md` reflects any new patterns discovered during Ralph execution. The Ralph-specific learnings log in `ralph/docs/LEARNINGS.md` is a source for promoting patterns to the project-level `AGENT_LEARNINGS.md`.

### Claude Code Skills

CC Skills (via `.claude/` plugin mechanism) enforce governance compliance automatically. Skills load AGENTS.md rules at invocation. When adding new skills or modifying existing ones, ensure they reference the current AGENTS.md document structure.

Available skills are registered via Claude Code plugins (see `~/.claude/plugins/`). The `.claude/skills/` directory in the project is reserved for project-local skill overrides.

## 3. Cultural & Collaborative Habits

Foster a culture where documentation is treated with the same importance as code.

### Treat Governance Files as Code

The most important principle: governance files should be reviewed in every PR, and an inaccurate file should be treated as a bug that can block a merge. A wrong rule is worse than a missing rule.

### Shared Ownership

The entire team — human and AI agents — is responsible for accuracy. If anyone spots an inconsistency, they should be empowered to fix it immediately.

### Regular Reviews

At the start of each sprint:

1. Review `AGENT_REQUESTS.md` — resolve or reprioritize active requests
2. Scan `AGENT_LEARNINGS.md` — promote Ralph-discovered patterns, remove outdated entries
3. Validate `AGENTS.md` role boundaries still match the current architecture
4. Confirm `CONTRIBUTING.md` command reference matches the current `Makefile`

### Maintenance Priority Order

When updating governance files, use this priority order to prevent information hierarchy conflicts:

1. `AGENTS.md` — behavioral rules first (highest impact)
2. `CONTRIBUTING.md` — technical standards second
3. `AGENT_LEARNINGS.md` — patterns third (high-value, low-risk)
4. `AGENT_REQUESTS.md` — escalations last (time-sensitive, not structural)
