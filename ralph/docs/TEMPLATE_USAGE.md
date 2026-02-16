# Ralph Loop - Template Usage Guide

Quick reference for using Ralph Loop in your project.

## Initial Setup

```bash
# 1. Clone and customize (for template projects)
git clone <your-repo-url> && cd <your-repo>
ralph/scripts/setup_project.sh    # Interactive project customization

# 2. Install dependencies
make setup_dev                     # Python deps, tooling
make setup_sandbox                 # Sandbox deps (Linux/WSL2 only)
```

## Workflow

### Option A: Manual PRD

1. Edit `docs/PRD.md` with your requirements
2. Run Ralph:

   ```bash
   make ralph_prd_json                # PRD.md → prd.json
   make ralph_init                    # Validate environment
   make ralph_run MAX_ITERATIONS=25   # Start autonomous loop
   ```

### Option B: Assisted PRD (Interactive)

```bash
make ralph_userstory                   # Interactive Q&A → UserStory.md
make ralph_prd_md                      # UserStory.md → PRD.md
make ralph_prd_json                    # PRD.md → prd.json
make ralph_init                        # Validate environment
make ralph_run MAX_ITERATIONS=25       # Start autonomous loop
```

### Story Dependencies

In `docs/PRD.md` story breakdown, use `(depends: STORY-XXX)` syntax:

```markdown
- **Feature 2** → STORY-002: Create API, STORY-003: Integrate API (depends: STORY-002)
```

The parser generates `prd.json` with dependency tracking. Ralph skips stories with unmet dependencies until prerequisites complete.

### Phase-Specific PRD Management

**This project uses phase-specific PRDs:**

- `docs/GreenAgent-PRD.md` - Phase 1 (Green Agent benchmark)
- `docs/PurpleAgent-PRD.md` - Phase 2 (Purple Agent competition)

**Ralph expects `docs/PRD.md`:**

- `docs/PRD.md` is a **symlink** to the currently active phase
- `generate_prd_json.py` parses only `PRD.md` (no multi-file parsing needed)

**To switch phases:**

```bash
# Phase 1 (Green Agent benchmark)
cd docs && ln -sf GreenAgent-PRD.md PRD.md && cd ..

# Phase 2 (Purple Agent competition)
cd docs && ln -sf PurpleAgent-PRD.md PRD.md && cd ..

# Regenerate prd.json after switching
make ralph_prd_json
```

**Current active phase:** Phase 1 (`PRD.md` → `GreenAgent-PRD.md`)

### Monitoring

```bash
make ralph_status           # Show progress
make validate               # Run linters + tests
```

### Reset / Iterate

```bash
make ralph_clean            # Reset state (removes prd.json, progress.txt)
make ralph_reorganize NEW_PRD=docs/PRD-v2.md VERSION=2  # Archive and iterate
```

## Commands Reference

| Command | Description |
| --------- | ------------- |
| `make ralph_userstory` | Create `docs/UserStory.md` interactively |
| `make ralph_prd_md` | Generate `docs/PRD.md` from UserStory.md |
| `make ralph_prd_json` | Generate `ralph/docs/prd.json` from PRD.md |
| `make ralph_init` | Validate Ralph environment and dependencies |
| `make ralph_run MAX_ITERATIONS=N` | Run autonomous development (default: 25) |
| `make ralph_status` | Show progress from `ralph/docs/progress.txt` |
| `make ralph_clean` | Reset state (removes prd.json, progress.txt) |
| `make ralph_reorganize NEW_PRD=path VERSION=N` | Archive current PRD and start new iteration |
| `make validate` | Run quality checks (ruff, pyright, pytest) |

## Configuration

Environment variables (set in shell or pass to make):

```bash
# Model selection
RALPH_MODEL=sonnet make ralph_run     # sonnet (default), opus, haiku

# Iteration control
MAX_ITERATIONS=50 make ralph_run      # Override default (25)

# TDD enforcement
REQUIRE_REFACTOR=true make ralph_run  # Require [REFACTOR] commit (default: false)
```

## Directory Structure

```text
your-project/
├── .claude/                    # Claude Code configuration
│   ├── skills/                 # Agent capabilities
│   ├── rules/                  # Behavioral guidelines
│   └── settings.json           # Claude Code settings
├── docs/
│   ├── PRD.md                  # Product Requirements Document
│   └── UserStory.md            # User stories (optional)
├── ralph/
│   ├── CHANGELOG.md            # Ralph Loop version history
│   ├── README.md               # Methodology overview
│   ├── TEMPLATE_USAGE.md       # This file
│   ├── docs/
│   │   ├── LEARNINGS.md        # Patterns and lessons
│   │   ├── prd.json            # Parsed stories (gitignored)
│   │   ├── progress.txt        # Execution log (gitignored)
│   │   └── templates/          # Project templates
│   └── scripts/
│       ├── ralph.sh            # Main orchestration
│       ├── generate_prd_json.py
│       ├── init.sh
│       ├── setup_project.sh
│       └── lib/common.sh
├── src/                        # Source code
├── tests/                      # Tests
├── logs/ralph/                 # Execution logs (gitignored)
└── Makefile                    # Build automation
```

## Files Created by Ralph

Ralph creates and manages these files during execution:

- `ralph/docs/prd.json` - Parsed story tracking with status and content hashes
- `ralph/docs/progress.txt` - Iteration log with timestamps and notes
- `logs/ralph/YYYY-MM-DD_HH:MM:SS.log` - Detailed execution logs

## TDD Workflow

Ralph enforces Test-Driven Development with commit markers:

1. **RED Phase**: Write failing tests
   - Commit message must include `[RED]` marker
   - Tests should fail before implementation

2. **GREEN Phase**: Implement features
   - Commit message must include `[GREEN]` marker
   - All tests must pass after implementation

3. **REFACTOR Phase** (optional): Clean up code
   - Commit message must include `[REFACTOR]` or `[BLUE]` marker
   - Controlled by `REQUIRE_REFACTOR` environment variable (default: false)

Ralph verifies commits are made chronologically in the correct order.

## Troubleshooting

**Ralph skips stories:**

- Check dependencies in `prd.json` - stories with unmet `depends_on` are skipped
- Verify `passes: false` in prd.json for stories you want executed

**TDD verification fails:**

- Ensure commit messages have correct markers: `[RED]`, `[GREEN]`, `[REFACTOR]`
- Commits must be in chronological order (RED before GREEN)
- Check `logs/ralph/` for detailed error messages

**Quality checks fail:**

- Run `make validate` manually to see specific errors
- Fix linting: `make lint_fix`
- Fix type errors: check `pyright` output

**Reset and retry:**

```bash
make ralph_clean          # Clear state
make ralph_prd_json       # Regenerate from PRD.md
make ralph_run            # Start fresh
```
