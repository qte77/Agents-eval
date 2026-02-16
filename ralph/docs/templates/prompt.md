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
- **Status updates**: Output a one-line status message at each step marked with **STATUS** below

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

### Before starting: Read relevant files

- Read ALL files listed in the story's `files` array from prd.json
- Understand existing patterns before writing any code
- **STATUS**: Output "Reading story files for STORY-XXX"

### RED: Write failing tests

- **STATUS**: Output "Starting RED phase: writing tests for ..."
- Read story acceptance criteria, write FAILING tests
  - Run tests — they MUST fail (code doesn't exist yet)
  - **STATUS**: Output "RED tests failing as expected. Committing."
  - **STOP AND COMMIT NOW**: `git add tests/ && git commit -m "test(STORY-XXX): add failing tests [RED]"`
  - Do NOT proceed to GREEN until this commit is made

### GREEN: Minimal implementation

- **STATUS**: Output "Starting GREEN phase: implementing ..."
- Implement MINIMAL code to pass tests
  - Run tests — they MUST pass now
  - **STATUS**: Output "Tests passing. Committing GREEN."
  - **STOP AND COMMIT NOW**: `git add src/ && git commit -m "feat(STORY-XXX): implement to pass tests [GREEN]"`
  - Do NOT proceed to REFACTOR until this commit is made

### REFACTOR: Fix remaining issues and clean up

- **STATUS**: Output "Starting REFACTOR phase"
- Fix any remaining test failures or edge cases from GREEN phase
- Improve code structure while keeping tests passing
  - Use focused checks: `make ruff`, `make type_check`, `uv run pytest <test-file>`
  - Do NOT run `make validate` — Ralph handles full validation after your work
  - **COMMIT**: `git add . && git commit -m "refactor(STORY-XXX): fix edge cases [REFACTOR]"`

**CRITICAL**: The Ralph loop counts your commits and checks for `[RED]` and
`[GREEN]` markers. If these commits are missing, ALL your work will be reset
and you must start over.

**Retry after quality failure**: If Ralph retries your story after quality checks
failed, your prior `[RED]` and `[GREEN]` commits still exist. You only need a
`[REFACTOR]` commit to fix the remaining issues — do NOT recreate `[RED]` or
`[GREEN]`. Check git log to confirm they exist before deciding your approach.

## Quality Gates

Ralph runs quality checks automatically after your work completes.
Use focused checks during development to catch issues early:

```bash
make ruff          # Format and lint src
make type_check    # Static type checking
uv run pytest <test-file>  # Run specific tests
```

Do NOT run `make validate` — it lints all test files including pre-existing
issues outside your story scope. Ralph's validation is story-scoped.

**Note on pre-existing test failures:** The Ralph loop captures a baseline of
failing tests before your story starts. Pre-existing failures unrelated to your
story are handled by the baseline comparison and will not block your progress.
Focus only on making YOUR story's tests pass. Do not attempt to fix unrelated
failing tests.

## Reminder: Commit Discipline

Your work is verified by checking git history. Before finishing, confirm:

- [ ] `[RED]` commit exists (tests committed before implementation)
- [ ] `[GREEN]` commit exists (implementation committed after tests pass)
- [ ] Commits are separate (not bundled into one)

## Current Story Details

(Will be appended by ralph.sh for each iteration)
