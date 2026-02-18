# Ralph Loop - Iteration Prompt

You are executing a single story from the Ralph autonomous development loop.

## Critical Rules (Apply FIRST)

- **Core Principles**: Auto-applied via rules - KISS, DRY, YAGNI, user-centric
- **MANDATORY**: Read and follow `AGENTS.md` compliance requirements
- **One story only**: Complete the current story, don't start others
- **Atomic changes**: Keep changes focused and minimal
- **Quality first**: All changes must pass `make validate`
- **No scope creep**: Implement exactly what the story requires

## Your Task

Follow TDD workflow below. Tests MUST be written FIRST.

## Workflow (TDD - MANDATORY)

**RED → GREEN → REFACTOR cycle:**

### RED: Write failing tests FIRST

- Read story from prd.json, write FAILING tests for acceptance criteria
  - Create test file in `tests/` (e.g., `tests/test_messenger.py`)
  - Write tests that verify each acceptance criterion
  - Run tests - they MUST fail (code doesn't exist yet)
  - **COMMIT TESTS FIRST**: `git add tests/ && git commit -m "test(STORY-XXX): add failing tests [RED]"`

### GREEN: Minimal implementation

- Study patterns in `src/`, implement MINIMAL code to pass tests
  - Create/modify implementation file (e.g., `src/agentbeats/messenger.py`)
  - Write simplest code that makes tests pass
  - Run tests - they MUST pass now
  - **COMMIT IMPLEMENTATION**: `git add src/ && git commit -m "feat(STORY-XXX): implement to pass tests [GREEN]"`

### REFACTOR: Clean up

- Clean up code while keeping tests passing
  - Remove duplication (DRY)
  - Simplify logic (KISS)
  - Ensure `make validate` passes
  - **COMMIT REFACTORINGS** (if any): `git add . && git commit -m "refactor(STORY-XXX): cleanup [REFACTOR]"`

**Final step**: Verify all acceptance criteria met

**CRITICAL**: Tests MUST be committed BEFORE implementation. This ensures verifiable TDD compliance and provides audit trail for agent evaluation.

## Available Skills

You have access to these skills:

- `designing-backend` - For architecture decisions
- `implementing-python` - For Python code implementation
- `reviewing-code` - For self-review before completion

Use skills appropriately based on task requirements.

## Quality Gates

Before marking the story complete:

```bash
make validate
```

Must pass:

- [ ] Code formatting (ruff)
- [ ] Type checking (pyright)
- [ ] All tests (pytest)

## Current Story Details

(Will be appended by ralph.sh for each iteration)
