# Changelog

All notable changes to Ralph Loop will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- **Story Status Enum**: Replaced binary `passes: bool` with `status: str` enum (`"pending"` | `"in_progress"` | `"passed"` | `"failed"`) across prd.json schema, shell scripts, and templates — enables observable story state and distinguishes not-started from running from failed
- **Wave Field in prd.json**: `wave: int` (1-indexed BFS level) computed by `compute_waves()` in `generate_prd_json.py` — makes dependency execution plan visible in prd.json without runtime computation
- **Sprint 9 Archive**: `ralph/docs/archive/sprint9/` with completed prd.json and progress.txt (all 9 stories passed)

### Removed

- **Duplicate `verify_teammate_stories`**: Deleted stale copy in `ralph.sh` that shadowed `lib/teams.sh` authoritative version — stale copy ignored `$3` (DELEGATED_TEAMMATES), using `get_unblocked_stories` instead which could pick up Wave N+1 stories never delegated

### Fixed

- **Worktree Directory Guard**: `ralph-in-worktree.sh` checks `[ -d "$WORKTREE_DIR" ]` alongside branch grep to prevent false positive when main checkout matches branch name in `git worktree list --porcelain` output
- **Teammate Verification**: `verify_teammate_stories()` in `ralph.sh` — after primary story passes in teams mode, runs TDD commit check + scoped quality checks (ruff, complexity, tests) on each wave-peer story and marks them `"passed"` or `"failed"`
- **Legacy Schema Guard**: `validate_environment()` detects old `passes` field without `status` and exits with migration instructions
- **`-X ours` Merge Blind Spot**: Documented in README.md and LEARNINGS.md — files added exclusively by the other branch are auto-merged as clean additions, not conflicts; must `git rm` after merge
- **Sprint 8 Archive**: `ralph/docs/archive/sprint8/` with completed `prd.json` and `progress.txt`
- **Scoped Ruff Checks**: `run_ruff_scoped()` in teams mode — only lint story files from prd.json, preventing cross-story lint false positives
- **Scoped Test Execution**: `run_tests_scoped()` in teams mode — only run story's test files from prd.json
- **Wave Checkpoint Validation**: `run_wave_checkpoint()` — full `make validate` at wave boundaries in teams mode to catch cross-story breakage
- **Impact Scan Prompt**: Agent instruction in `prompt.md` to grep test tree for consumers before implementing renames
- **Pycache Cleanup**: `clean_test_pycache()` — removes `__pycache__` dirs and `.pyc` files under `tests/` before test runs
- **Known Failure Mode #6**: Incomplete PRD file lists causing stale tests (Sprint 8 post-mortem)
- **Worktree Launcher**: `ralph-in-worktree.sh` + `make ralph_worktree` — create branch, setup git worktree, print `cd` path
- **Worktree Runner**: `make ralph_run_worktree` — create worktree + run Ralph in it (same args as `ralph_run`)
- **Worktree Workflow Docs**: README "Git Worktree Workflow" section — setup, sibling directory layout, `.venv` symlink, key practices, sandbox note
- **PRD Parser Constraints**: Documented 4 parser gotchas in `LEARNINGS.md` (table) and `prd.md.template` (inline comments)
- **Merge Strategy**: Squash merge pattern and conflict prevention rule in `LEARNINGS.md`
- **Wave Terminology**: Defined "wave" (dependency graph frontier) in `ralph.sh` and `README.md`
- **Sprint 8 prd.json**: 14 stories with file-conflict peer deps for teams mode (Wave 4a/4b/4c)
- **CC Agent Teams as alternative orchestrator**: PRD dual-mode support (Ralph loop + CC Teams), file-conflict dependencies, orchestration waves, teammate prompt template
- **Known Failure Mode #5**: File-conflict dependencies not tracked in `get_unblocked_stories`
- **Agent Activity Monitor**: Heartbeat now tails agent log output at 30s intervals with `[CC]` (magenta) prefix for agent activity and red for agent errors (`common.sh`: `log_cc`, `log_cc_error`)
- **Quality Retry Context**: Failed quality gate name is passed to the agent prompt on retry via `RETRY_CONTEXT_FILE`, so the agent knows what to fix
- **PRD Parser**: Parser for structured PRD.md files with automatic prd.json generation
- **TDD Workflow**: Optional REFACTOR phase with RED/GREEN/REFACTOR commit markers and chronological verification
- **Template System**: Comprehensive templates for progress.txt and prd.json with parser-compatible structure
- **Documentation**: README.md with Ralph Loop overview, extended functionality guide, and usage examples
- **Project Templates**: Interactive setup script with auto-detection of git repo, author, and Python version

### Changed

- **`update_story_status()`**: Accepts enum values (`"pending"`, `"in_progress"`, `"passed"`, `"failed"`) instead of `"true"`/`"false"` — sets `.status` field, sets `completed_at` only on `"passed"`
- **Story Lifecycle**: Main loop marks story `"in_progress"` at start, `"passed"` on success, `"failed"` on max retries (was only `"true"` on success)
- **`_backfill_existing_stories()`**: Migrates legacy `passes: bool` → `status: str` and adds `wave: 0` for existing prd.json files
- **prd.json Template**: `"passes": false` → `"status": "pending"`, added `"wave": 1`
- **init.sh**: `.passes == true` → `.status == "passed"` in prd.json status display
- **init.sh**: `initialize_progress()` and `check_prd_json()` substitute `{{PROJECT}}` placeholder from `RALPH_PROJECT` env var or git repo name (was hardcoded project name)
- **LEARNINGS.md**: Condensed from 114 to ~55 lines, added frontmatter, replaced verbose prose with actionable table and checklists
- **PRD-Sprint8**: Flattened AC sub-items, added sub-feature Files sections, merged compound sub-features, added file-conflict peer deps
- **Documentation Structure**: Reorganized ralph/ directory structure and moved TEMPLATE_USAGE.md to ralph root
- **Skill System**: Relocated commands to skills structure (`.claude/skills/`)
- **Default Configuration**: Increased max iterations to 25, set REQUIRE_REFACTOR to false by default
- **State Files**: Consolidated Ralph script utilities and simplified story processing
- **PRD Format**: Updated to v3.0 with A2A protocol and AgentBeats competition details

### Removed

- **`reorganize_prd.sh`**: Deleted stale PRD reorganization script leaked from old `main` during squash merge

### Fixed

- **PRD Parser Compliance**: Removed 45 blank lines between section headers (`**Acceptance Criteria**:`, `**Technical Requirements**:`, `**Files**:`) and first list items across Sprint 9 (27) and Sprint 10 (18) — parser was producing `AC: 0, files: 0` for every story
- **PRD Template Conformance**: Both Sprint 9/10 PRDs — nested `#### File-Conflict Dependencies` inside `### Notes for CC Agent Teams`, replaced inline `- **Orchestration Waves**:` bullet with `####` heading, removed duplicate `### Story Breakdown` heading, moved `## Non-Functional Requirements` after `## Functional Requirements`
- **STORY-009 Wave Conflict**: Moved STORY-009 from Wave 1 to Wave 4 (undeclared file conflict with STORY-006 on `test_llm_evaluation_managers.py`); updated file-conflict table to STORY-NNN notation with new conflict row
- **Pytest Collection ERRORs**: `compare_test_failures` and `capture_test_baseline` now detect `ERROR` lines in addition to `FAILED` lines — collection errors no longer invisible to baseline comparison
- **Missing ruff_tests in Baseline**: Solo mode baseline pipeline now runs `make ruff` + `make ruff_tests` (previously only `make ruff`)
- **Killed Pytest Detection**: Exit 137/143 (OOM/SIGTERM) now returns hard failure with retry context — no longer treated as valid test result with partial output
- **CC Monitor Log Nesting**: Replace `tail -5` with byte offset tracking (`wc -c`) so monitor reads only new log content per 30s cycle, preventing `[CC] [INFO] [CC] [INFO] ...` chains
- **Worktree VIRTUAL_ENV Mismatch**: Launch `ralph.sh` via `env -u VIRTUAL_ENV` so uv discovers `.venv` via symlink without devcontainer mismatch warnings; capture `SOURCE_VENV=$PWD` before `cd` (replaces `git rev-parse`)
- **Worktree Phantom chmod**: Replace `make_executable()` with `check_executable()` in `init.sh` — warn instead of writing, preventing phantom permission changes on read-only worktree filesystems
- **CC Monitor Log Dedup**: Strip inner log-level prefix from CC agent output before wrapping with `log_cc*`
- **Scoped Reset**: TDD failure cleanup now only removes story-created untracked files instead of `git clean -fd` which nuked all untracked files
- **REFACTOR Marker Fallback**: `check_tdd_commits` detects conventional `refactor(` prefix when `[REFACTOR]` bracket marker is missing
- **Quality Retry TDD Skip**: Retries after quality failure skip TDD verification (prior RED+GREEN already verified), preventing false rejections
- **Prompt Marker Emphasis**: Added explicit `[REFACTOR]` commit example to retry section of `prompt.md`
- **Error Handling**: Improved error handling when staging state files in Ralph script
- **Type Safety**: Fixed type errors and lint issues for strict type checking
- **Parser Flexibility**: Made Story Breakdown section parsing phase-agnostic
- **Code Formatting**: Applied PEP 8 compliance to generate_prd_json.py
