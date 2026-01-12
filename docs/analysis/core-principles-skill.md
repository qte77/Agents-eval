---
title: Core Principles Skill - Implementation Summary
created: 2026-01-11
updated: 2026-01-11
---

## What Was Created

**New Foundational Skill**: `.claude/skills/core-principles/SKILL.md`

This skill encodes the project's core principles and MUST be applied to ALL tasks.

## Core Principles (From Skill)

1. **User Experience, User Joy, User Success**
2. **KISS** (Keep It Simple, Stupid)
3. **DRY** (Don't Repeat Yourself)
4. **YAGNI** (You Aren't Gonna Need It)
5. **Concise and On-Point**
6. **Reuse and Generalize**
7. **Focused Changes**
8. **Prevent Incoherence**
9. **Rigor and Sufficiency**
10. **High-Impact Quick Wins**
11. **Actionable and Concrete**
12. **Root-Cause and First-Principles**

## Integration

**All skills now reference core-principles:**

- ✅ designing-backend
- ✅ implementing-python
- ✅ reviewing-code
- ✅ generating-prd

**Ralph prompt updated:**

- ✅ Iteration prompt now applies core-principles FIRST

## Usage

The skill is automatically discovered by Claude Code. It triggers when:

- Starting any task
- Making design decisions
- Writing code
- Reviewing code
- Converting requirements

**Key phrase in all skills:**
> **MANDATORY**: Always apply @core-principles skill first

## Before/After Checklist

The skill provides a pre-task checklist:

- [ ] Does this serve user value?
- [ ] Is this the simplest approach?
- [ ] Am I duplicating existing work?
- [ ] Do I actually need this?
- [ ] Am I touching only relevant code?
- [ ] Have I checked for inconsistencies?
- [ ] What's the root cause I'm solving?
- [ ] Is this a high-impact quick win?

## Impact

This ensures:

- No over-engineering
- No unnecessary complexity
- Focus on user value
- Rigorous decision-making
- Quick, high-impact delivery
