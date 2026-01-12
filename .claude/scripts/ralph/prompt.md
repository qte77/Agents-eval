# Ralph Loop - Iteration Prompt

You are executing a single story from the Ralph autonomous development loop.

## Critical Rules (Apply FIRST)

- **MANDATORY**: Apply @core-principles skill - User Experience, KISS, DRY, YAGNI, root-cause thinking
- **MANDATORY**: Read and follow `AGENTS.md` compliance requirements
- **One story only**: Complete the current story, don't start others
- **Atomic changes**: Keep changes focused and minimal
- **Quality first**: All changes must pass `make validate`
- **No scope creep**: Implement exactly what the story requires

## Your Task

1. **Read `docs/ralph/prd.json`** to understand the current story
2. **Implement the story** following acceptance criteria exactly
3. **Create/update tests** for the implemented functionality
4. **Ensure `make validate` passes** before completing

## Workflow

1. Read current story details from prd.json
2. Study existing code patterns in `src/app/`
3. Implement minimal solution matching acceptance criteria
4. Create focused tests in `tests/`
5. Run `make validate` and fix any issues
6. Verify all acceptance criteria are met

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
