---
name: compacting-context
description: Compacts verbose context into structured summary. Use after pollution sources (searches, logs, JSON) or at phase milestones.
compatibility: Designed for Claude Code
metadata:
  argument-hint: [compaction-name]
  context: fork
  agent: Explore
  model: sonnet
  allowed-tools: Read, Grep, Glob
---

# Context Compaction (ACE-FCA)

Distills verbose outputs into structured summaries following ACE-FCA principles.

## When to Use

Per `.claude/rules/context-management.md`:
- After verbose tool output (logs, JSON, search results)
- After completing a phase or milestone

## Workflow

1. **Identify noise** - What pollution sources need compacting?
2. **Extract signal** - Correct + Complete info only
3. **Structure output** - Use template format below

## Output Template

```markdown
# Compaction: {{name}}

## Trajectory
<!-- Research status → Planning status → Implementation status -->

## Key Files
<!-- files touched with purpose -->

## Completed
<!-- done items -->

## Blockers
<!-- blocking issues (empty if none) -->

## Findings
<!-- key discoveries, distilled outputs from logs/JSON/tests -->
```

## Quality Check

- Correct > Complete > Minimal
- No raw dumps, only structured summaries
- Enough to continue, no more
- Update working plan with compaction output (don't orphan it)
