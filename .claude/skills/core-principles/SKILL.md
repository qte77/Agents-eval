---
name: core-principles
description: Project core principles that MUST be applied to ALL tasks. Use this skill for every task to ensure User Experience, KISS, DRY, YAGNI, and rigorous first-principles thinking.
---

# Core Principles

**MANDATORY for ALL tasks.** These principles override all other guidance when conflicts arise.

## User-Centric Principles

1. **User Experience, User Joy, User Success**

   - Every decision optimizes for user value
   - Prioritize clarity and usability
   - Eliminate friction and confusion

## Code Quality Principles

1. **KISS (Keep It Simple, Stupid)**

   - Simplest solution that works
   - No unnecessary abstraction
   - Clear > clever

2. **DRY (Don't Repeat Yourself)**

   - Single source of truth
   - Reuse existing code/docs
   - Reference, don't duplicate

3. **YAGNI (You Aren't Gonna Need It)**

   - Implement only what's requested
   - No speculative features
   - No "future-proofing"

## Execution Principles

1. **Concise and On-Point**

   - Minimal code/text for task
   - No verbose explanations
   - Direct implementation

2. **Reuse and Generalize**

   - Use existing patterns
   - Leverage existing dependencies
   - Extend, don't rebuild

3. **Focused Changes**

   - Touch only task-related code
   - No unrelated "improvements"
   - No scope creep

4. **Prevent Incoherence**

   - Spot inconsistencies
   - Maintain alignment
   - Validate against existing patterns

## Decision Principles

1. **Rigor and Sufficiency**

   - Research thoroughly
   - Think critically
   - Decide with evidence

2. **High-Impact Quick Wins**

    - Prioritize must-do tasks
    - Focus on high value
    - Ship fast, iterate

3. **Actionable and Concrete**

    - Specific deliverables
    - Clear steps
    - Measurable outcomes

4. **Root-Cause and First-Principles**

    - Understand the "why"
    - Question assumptions
    - Solve root problems

## Before Starting Any Task

Ask:

- [ ] Does this serve user value?
- [ ] Is this the simplest approach?
- [ ] Am I duplicating existing work?
- [ ] Do I actually need this?
- [ ] Am I touching only relevant code?
- [ ] Have I checked for inconsistencies?
- [ ] What's the root cause I'm solving?
- [ ] Is this a high-impact quick win?

## Post-Task Review

Before finishing, ask yourself:

- **Did we forget anything?** - Check requirements thoroughly
- **Beneficial enhancements or quick wins?** - Identify opportunities
- **Something to delete?** - Remove obsolete/unnecessary code

**IMPORTANT**: Do NOT alter files based on this review. Only output suggestions to the user.

Let the user decide on additional changes.

## When in Doubt

**STOP. Ask the user.**

Don't assume, don't over-engineer, don't add complexity.
