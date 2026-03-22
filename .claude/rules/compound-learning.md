# Compound Learning

Prevent repeated mistakes by systematically promoting learnings.

## Before Solving a Problem

Check AGENT_LEARNINGS.md for prior art. If a matching pattern exists, apply it.

## Promotion Path

1. **1st occurrence** — fix inline, move on
2. **2nd occurrence** — add to AGENT_LEARNINGS.md (pattern + solution)
3. **3rd occurrence** — promote to `.claude/rules/` (always-loaded, prevents recurrence)
4. **Recurring workflow** — extract to `.claude/skills/` (reusable capability)

## When Promoting (step 3)

- Verify the root cause is the same across occurrences
- Write the rule as a constraint ("do X", "never Y"), not a narrative
- Reference the AGENT_LEARNINGS.md entry being promoted
- Remove or link the original entry to avoid duplication
