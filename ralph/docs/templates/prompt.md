# Ralph Loop - Iteration Prompt

You are executing a single story from the Ralph autonomous development loop.

## CRITICAL: Separate Git Commits Per Phase

You MUST make **separate git commits** for each workflow phase. This is
verified automatically — the Ralph loop will **reject your work and reset
everything** if commits are missing or bundled.

**Required commits (minimum 2):**

1. `git add tests/ && git commit -m "test(STORY-XXX): ... [RED]"` — after writing failing tests
2. `git add src/ && git commit -m "feat(STORY-XXX): ... [GREEN]"` — after passing implementation
3. `git add . && git commit -m "refactor(STORY-XXX): ... [REFACTOR]"` — after cleanup (optional)

**DO NOT** bundle all work into a single commit.
**DO NOT** skip commits and describe what you "would have committed."
**DO NOT** ask for git permission — you already have it.

## Critical Rules (Apply FIRST)

- **MANDATORY**: Read and follow project compliance requirements
- **One story only**: Complete the current story, don't start others
- **Atomic changes**: Keep changes focused and minimal
- **Quality first**: All changes must pass `make validate`
- **No scope creep**: Implement exactly what the story requires

## References

- `docs/best-practices/python-best-practices.md` — Python development
- `docs/best-practices/tdd-best-practices.md` — TDD methodology

## Available Skills

Relevant skills for story implementation (others may also be available):

- `testing-python` — Test writing (TDD/BDD)
- `implementing-python` — Code implementation
- `designing-backend` — Architecture decisions
- `reviewing-code` — Self-review before completion

Use skills appropriately based on task requirements.

## Your Task

Follow the project's testing best practices. Tests MUST be written and
**committed** FIRST.

## Workflow

### RED: Write failing tests

- Read story acceptance criteria, write FAILING tests
  - Run tests — they MUST fail (code doesn't exist yet)
  - **STOP AND COMMIT NOW**: `git add tests/ && git commit -m "test(STORY-XXX): add failing tests [RED]"`
  - Do NOT proceed to GREEN until this commit is made

### GREEN: Minimal implementation

- Implement MINIMAL code to pass tests
  - Run tests — they MUST pass now
  - **STOP AND COMMIT NOW**: `git add src/ && git commit -m "feat(STORY-XXX): implement to pass tests [GREEN]"`
  - Do NOT proceed to REFACTOR until this commit is made

### REFACTOR: Clean up

- Clean up while keeping tests passing
  - Ensure `make validate` passes
  - **COMMIT REFACTORINGS** (if any): `git add . && git commit -m "refactor(STORY-XXX): cleanup [REFACTOR]"`

**CRITICAL**: The Ralph loop counts your commits and checks for `[RED]` and
`[GREEN]` markers. If these commits are missing, ALL your work will be reset
and you must start over.

## Quality Gates

Before marking the story complete:

```bash
make validate
```

All checks (formatting, type checking, tests) must pass.

## Reminder: Commit Discipline

Your work is verified by checking git history. Before finishing, confirm:

- [ ] `[RED]` commit exists (tests committed before implementation)
- [ ] `[GREEN]` commit exists (implementation committed after tests pass)
- [ ] Commits are separate (not bundled into one)

## Current Story Details

(Will be appended by ralph.sh for each iteration)
