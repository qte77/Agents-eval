---
title: Phase Plan Implementation
name: phase-implement
description: Execute implementation plan following KISS/DRY/Python best practices with laser-focused goal orientation
argument-hint: [ralph] 
tools: Read, Edit, Write, Grep, Glob, Bash
---

Implement the plan following first-principles.

**Plan input (auto-detect in order):**

1. Latest plan file in `/home/vscode/.claude/plans/`
2. `docs/ralph/prd.json` (for Ralph autonomous execution)
3. Conversation context (from earlier `/phase-exec-planner` output)

If none found, prompt user for plan source.

**MANDATORY:**

- **KISS**: Simplest solution, no over-engineering, lowest complexity possible
- **DRY**: Reuse existing patterns and implementation, no duplication
- **Python Standards**: Follow @docs/best-practices/python-best-practices.md
- **Project Compliance**: Follow @AGENTS.md and @CONTRIBUTING.md
- **Reuse**: Leverage existing components/patterns/utilities from `src/app/`
- **Scope**: Do NOT change/update/modify/extend code not related to the task
- **Laser-focused**: Only necessary functionality, goal-oriented execution
- **First Principles**: Break down into core concepts

**Apply skills:**

- @core-principles (MANDATORY for all tasks)
- @implementing-python (Python coding standards)

**Validation:**

Before marking complete:

```bash
make validate
```

Must pass: ruff formatting, ruff linting, pyright type checking, pytest tests.

**Ralph Loop (Autonomous Execution):**

If `docs/ralph/prd.json` detected OR if "ralph" parameter provided run: `make ralph ITERATIONS=N`

See `/phase-exec-planner` with "ralph" parameter for prd.json generation.

**Execute now:**

- **Manual**: Read plan → Implement tasks → Run `make validate` after each
- **Ralph**: Automatically runs if `docs/ralph/prd.json` detected
