---
name: generating-prd
description: Generates prd.json task tracking file from PRD.md requirements document. Use when initializing Ralph loop or when the user asks to convert PRD to JSON format for autonomous execution.
---

# PRD to JSON Conversion

**MANDATORY**: Always apply @core-principles skill first - User Experience, KISS, DRY, YAGNI, root-cause thinking.

Parses `docs/PRD.md` and generates `docs/ralph/prd.json` for Ralph loop task tracking.

## Purpose

The Ralph loop requires a structured JSON file to track task completion. This skill extracts implementation stories from PRD.md and creates the required prd.json format.

## Workflow

1. **Read `docs/PRD.md`** to extract functional requirements
2. **Identify atomic stories** - tasks that fit in single context window
3. **Generate `docs/ralph/prd.json`** with proper schema
4. **Validate JSON** format before saving

## PRD.json Schema

```json
{
  "project": "Agents-eval",
  "source": "docs/PRD.md",
  "generated": "YYYY-MM-DD HH:MM:SS",
  "stories": [
    {
      "id": "STORY-001",
      "title": "Brief story title",
      "description": "What needs to be implemented",
      "acceptance": ["Criteria 1", "Criteria 2"],
      "files": ["expected/file/paths.py"],
      "passes": false,
      "completed_at": null
    }
  ]
}
```

## Story Extraction Rules

**Atomic Stories**: Each story must complete within single context window

- Single feature addition (100-300 lines)
- Single bug fix
- Single refactoring task
- Single test suite addition

**From PRD.md Extract**:

- Functional requirements → stories
- API endpoints → implementation stories
- CLI commands → feature stories
- Evaluation metrics → metric implementation stories

**Story Attributes**:

- `id`: Unique identifier (STORY-XXX format)
- `title`: Brief 3-7 word description
- `description`: What to implement (1-2 sentences)
- `acceptance`: Testable completion criteria
- `files`: Expected files to modify/create
- `passes`: Boolean (false initially)
- `completed_at`: Timestamp when marked passing

## Validation Rules

Before saving prd.json:

- [ ] All required fields present for each story
- [ ] IDs are unique
- [ ] All stories have `passes: false` initially
- [ ] Acceptance criteria are specific and testable
- [ ] File paths match project structure

## Example Conversion

**From PRD.md**:

```markdown
## Functional Requirements
### CLI
- Command Line Interface:
  - Environment setup commands: make setup_dev
```

**To prd.json**:

```json
{
  "stories": [
    {
      "id": "STORY-001",
      "title": "Add make setup_dev command",
      "description": "Create Makefile recipe for development environment setup",
      "acceptance": [
        "Makefile contains setup_dev recipe",
        "Recipe installs all dev dependencies",
        "Recipe passes validation checks"
      ],
      "files": ["Makefile"],
      "passes": false,
      "completed_at": null
    }
  ]
}
```

## Usage

To generate prd.json:

```bash
# Run this skill to parse PRD.md
# Output will be saved to docs/ralph/prd.json
```

Ralph loop will then use this file to track task completion.

## References

- See `docs/PRD.md` for source requirements
- See `.claude/scripts/ralph/ralph.sh` for how prd.json is consumed
- See @AGENTS.md for task granularity guidelines
