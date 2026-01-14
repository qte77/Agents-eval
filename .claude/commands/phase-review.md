---
title: Phase Completion Review
name: phase-review
description: Review phase completion, update documentation, suggest improvements following KISS/DRY principles.
argument-hint: [sprint-name] (optional, e.g., "2025-08_Sprint2_SoC_SRP")
tools: Read, Edit, Write, Grep, Glob, Bash
---

I'll review the completed phase and update sprint documentation.

## Step 1: Gather Metrics

**Git analysis:**

- `git diff --stat` - Files changed, LOC delta
- `git log --oneline` - Commits since last review

**Validation:**

- `make validate` - Check ruff, pyright, pytest status

**KISS/DRY check:**

- Identify overcomplication or unnecessary abstractions
- Find duplicate code that can be consolidated
- Verify focus on core objectives

## Step 2: Phase Review Document

Create: `docs/sprints/assessment/PHASE_REVIEW_{YYYY-MM-DD}_Sprint{Name}.md`

**Required sections:**

1. **Time & Effort** - Estimate vs actual, blockers
2. **Impact** - User features, developer changes, breaking changes
3. **Technical Debt** - Created, resolved, net change
4. **Testing** - Coverage %, test status
5. **Metrics** - LOC, validation results
6. **Next Steps** - Actions for next sprint

## Step 3: Update Documentation

**ALWAYS update:**

1. `docs/sprints/YYYY-MM_Sprint#_Name.md` - Mark completed tasks [x], add results
2. `docs/roadmap.md` - Update sprint status (✅ Complete, 🚧 In Progress, 📋 Planned)
3. `CHANGELOG.md` - Add changes (Added, Changed, Fixed, Security, etc.)
4. `docs/arch/ADR-XXX.md` - If significant architecture decision made

**ONLY update if features are DONE:**

1. `docs/PRD.md` - Mark completed features [x] ONLY when fully implemented and validated

**Validate:** `make validate` must pass before completion.

## Step 4: Strategic Suggestions

**Forgotten?**

- Testing, error handling, logging
- Documentation (docstrings, README)
- Security (input validation, secrets)

**Add?**

- Missing PRD features
- UX improvements, error messages

**Delete?**

- Unused code, dead imports
- Debug print statements, TODOs

**Enhance?**

- Performance (async, caching)
- DRY violations, type safety
- Test coverage gaps

Let me begin the review now.
