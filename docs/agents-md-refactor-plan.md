# AGENTS.md Refactor Plan - Minimal Skills/Ralph Integration

**Date**: 2026-01-11
**Principle**: KISS, DRY, YAGNI - Add awareness, no duplication

## Root Cause

AGENTS.md written before Skills/Ralph infrastructure existed:
- No reference to `.claude/skills/`
- No reference to Ralph autonomous execution
- Skills reference AGENTS.md (one-way), should be bidirectional

## Solution: 3 Minimal Changes

### 1. Add Claude Code Infrastructure Section (After "External References")

**Insert after line 12:**

```markdown
## Claude Code Infrastructure

**Skills** (`.claude/skills/`): Modular capabilities with progressive disclosure
- `core-principles` - MANDATORY for all tasks (KISS, DRY, YAGNI, verification)
- `designing-backend`, `implementing-python`, `reviewing-code`, `generating-prd`
- See individual SKILL.md files for usage triggers and instructions

**Ralph Loop** (`.claude/scripts/ralph/`): Autonomous task execution system
- `make ralph_init` - Initialize environment and state files
- `make ralph ITERATIONS=N` - Run autonomous development loop
- State tracking: `docs/ralph/prd.json` (tasks), `docs/ralph/progress.txt` (learnings)
- See `docs/CC-skills-Ralph-adoption-plan.md` for complete documentation

**Integration**: Skills enforce AGENTS.md compliance. Ralph executes stories from PRD.md using Skills.
```

**Lines added**: ~14
**Impact**: Users/agents aware of new infrastructure
**Duplication**: None (just pointers)

### 2. Update Subagent Section Header (Line 100)

**Change from:**
```markdown
## Subagent Role Boundaries
```

**Change to:**
```markdown
## Agent Role Boundaries

**Note**: This section defines subagent behavior for Task tool invocations. Claude Code Skills (`.claude/skills/`) complement these with progressive disclosure and auto-discovery.
```

**Lines changed**: 3
**Impact**: Clarifies relationship between subagents and Skills
**Duplication**: None

### 3. Update Agent Quick Reference Post-Task (Line 225-231)

**Change from:**
```markdown
**Post-Task:**

- Run `make validate` - must pass all checks
- Update CHANGELOG.md for non-trivial changes
- Document new patterns in AGENT_LEARNINGS.md (concise, laser-focused, streamlined)
- Escalate to AGENT_REQUESTS.md if blocked
```

**Change to:**
```markdown
**Post-Task:**

- Run `make validate` - must pass all checks (code tasks only)
- Apply core-principles post-task review: Did we forget anything? Beneficial enhancements? Something to delete?
- Update CHANGELOG.md for non-trivial changes
- Document new patterns in AGENT_LEARNINGS.md (concise, laser-focused, streamlined)
- Escalate to AGENT_REQUESTS.md if blocked
```

**Lines changed**: 2
**Impact**: Integrates core-principles skill workflow
**Duplication**: References skill, doesn't duplicate

## Total Changes

- **Lines added**: ~16
- **Lines modified**: ~5
- **Sections added**: 1
- **Sections modified**: 2

## What NOT To Do (YAGNI)

❌ Move subagent definitions to Skills (they're still used)
❌ Restructure existing content
❌ Duplicate Skills documentation in AGENTS.md
❌ Add extensive Ralph documentation (already in separate file)
❌ Change mandatory compliance requirements (still valid)

## Verification

After changes:
- [ ] AGENTS.md mentions `.claude/skills/` infrastructure
- [ ] AGENTS.md mentions Ralph loop
- [ ] Bidirectional awareness: AGENTS.md ↔ Skills
- [ ] No content duplication
- [ ] Total additions <20 lines

## Benefits

✅ Users discover Skills infrastructure
✅ Users discover Ralph autonomous execution
✅ Bidirectional documentation (AGENTS.md ↔ Skills)
✅ No duplication (DRY)
✅ Minimal changes (KISS)
✅ High-impact quick win

---

**Implementation**: 3 precise edits, <20 lines total, no restructuring
