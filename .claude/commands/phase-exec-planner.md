---
title: Phase Execution Planner
name: phase-exec-planner
description: Extract phase from sprint plan, gather context, plan for implementing the phase
argument-hint: <phase-id> <sprint-path> [ralph] (e.g., "2I docs/sprints/2025-08_Sprint2_SoC_SRP.md ralph")
---

Execute implementation phase planning with first-principles thinking.

**Arguments:**

- Phase ID (e.g., "2I" or sprint section identifier)
- Sprint plan path (e.g., `docs/sprints/YYYY-MM_Sprint#_Name.md`)
- ralph (optional) - If provided, generate `docs/ralph/prd.json` for autonomous execution

**Planning approach:**

Use Task tool with Plan subagent:

```text
Plan implementation for phase {{arg1}} from {{arg2}}.

**MANDATORY:**

- **KISS**: Simplest solution, no over-engineering, lowest complexity possible
- **DRY**: Reuse existing patterns and implementation, no duplication
- **Python Standards**: Follow @docs/best-practices/python-best-practices.md
- **Project Compliance**: Follow @AGENTS.md and @CONTRIBUTING.md
- **Laser-focused**: Only modify in-scope files, only necessary code/functionality
- **Goal-oriented**: Deliver working functionality without detours
- **First Principles**: Break down into core concepts

Extract phase context, analyze existing patterns, create focused implementation plan.

**Do NOT implement** - planning only.
```

**Plan subagent will:**

1. Analyze sprint document for phase tasks
2. Create detailed implementation plan
3. Save to `/home/vscode/.claude/plans/{filename}.md`

## If "ralph" parameter provided

Generate `docs/ralph/prd.json` for autonomous execution:

1. Read {{arg2}} (sprint document) and extract phase {{arg1}} tasks
2. Convert each task to story format:
   - id: "story-{n}"
   - title: Task summary
   - description: Full task description
   - acceptance_criteria: Success criteria list
   - expected_files: Files to be modified/created
   - passes: false
   - completed_at: null
3. Write JSON to `docs/ralph/prd.json`:

```json
{
  "version": "1.0.0",
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "source": "{{arg2}} phase {{arg1}}",
  "stories": [...]
}
```

**Output:** "Generated prd.json with N stories. Run: `make ralph ITERATIONS=N`"

**Key references:**

- Apply @core-principles skill (KISS, DRY, YAGNI)
- Follow @implementing-python skill for Python standards
- Reference @designing-backend if architecture decisions needed
- Use @reviewing-code after implementation

**Output:**

- Without "ralph" parameter: Detailed implementation plan (manual execution)
- With "ralph" parameter: Plan + `docs/ralph/prd.json` (autonomous execution via `make ralph`)
